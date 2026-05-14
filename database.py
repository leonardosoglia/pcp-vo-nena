"""
database.py — PCP Vó Nena (schema v2, backend dual SQLite/Postgres)

Reflete fielmente a folha de produção física da Doces Vó Nena.

Tabelas principais (uma por bloco do papel):
    folha_cocada            — quadros 1, 2, 4, 5, 6, 7 da folha oficial (cocada)
    folha_palha             — quadros equivalentes para palha (5 sabores)
    papelzinho_joel         — 5 colunas do papelzinho diário do Joel (T, L, B, C, P, Z)
    folha_pm_balas_doces    — PM/Balas/Doces — contagens + ordens

Tabelas de referência (não mudam dia a dia):
    metas_45g                  — base semanal de unidades 45g
    metas_mini_pet             — referência Mini/Pet por sabor
    metas_potes                — referência potes
    parametros_pvirar_ideal    — bandejas P/Virar ideais por sabor
    conversoes                 — tabela de conversões (1 tacho = 8 band etc.)
    estoque                    — estoque atual + segurança + alerta

Cálculos derivados (NÃO persistem — calculados ao exibir):
    Cortados ②(45g)  = cort1_45g  + emb_45g  + papelzinho_joel.joel_45g
    Cortados ②(Mini) = cort1_mini + emb_mini + joel_mini
    Cortados ②(Pet)  = cort1_pet  + emb_pet  + joel_pet
    Cortados ③       = ② − param_real_*
    Viradas ②        = joel_v − (ord_corte_45g + ord_corte_mini + ord_corte_pet)
    P/Virar ②        = joel_pv + Viradas ②

Migração v1 → v2 (automática quando init_db detecta schema antigo):
    1. Backup do .db em .bak.YYYYMMDD_HHMMSS  (apenas SQLite — não há v1 em Postgres)
    2. Renomeia tabelas antigas → _v1_legacy
    3. Cria tabelas v2 vazias
    4. Copia dados das _v1_legacy com mapeamento de colunas
    5. Drop _v1_legacy (banco já tem backup em arquivo)

Backend dual (Etapa 4 — TCC):
    Sem DATABASE_URL no ambiente   → SQLite local (pcp_vo_nena.db). Padrão de dev.
    DATABASE_URL = "postgresql://…" → Postgres (Supabase) via psycopg 3.
    Detecção runtime; consumo externo (lancamento.py / painel.py) não precisa mudar.

Princípio: dados na unidade do papel (sem conversão automática). Cálculos derivados
ficam na camada de apresentação (lancamento.py / painel.py).
"""
import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "pcp_vo_nena.db")

# ── Backend detection ─────────────────────────────────────────────────────────
# Opt-in: sem DATABASE_URL no ambiente, comportamento é idêntico ao SQLite original.
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
# Heroku-style postgres:// é deprecated em vários drivers; normaliza p/ postgresql://.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]
IS_POSTGRES = DATABASE_URL.startswith("postgresql://")


# ── Catálogos fixos do domínio ─────────────────────────────────────────────────
SABORES_COCADA = ["TRADICIONAL", "LEITE CONDENSADO", "BRIGADEIRO", "CAFÉ", "PÉ DE MOÇA", "ZERO"]
SIGLA_COCADA = {"TRADICIONAL": "T", "LEITE CONDENSADO": "L", "BRIGADEIRO": "B",
                "CAFÉ": "C", "PÉ DE MOÇA": "P", "ZERO": "Z"}

SABORES_PALHA = ["TRADICIONAL", "LEITE EM PÓ", "CHURROS", "COOKIES", "LIMÃO"]
SIGLA_PALHA = {"TRADICIONAL": "T", "LEITE EM PÓ": "L", "CHURROS": "CH",
               "COOKIES": "CK", "LIMÃO": "LIM"}

# Palha 50g existe apenas em T, L, CH (Cookies e Limão só vêm em Pet)
SABORES_PALHA_50G = ["TRADICIONAL", "LEITE EM PÓ", "CHURROS"]


# ════════════════════════════════════════════════════════════════════════════════
# CONEXÃO E HELPERS DE COMPATIBILIDADE
# ════════════════════════════════════════════════════════════════════════════════
import atexit

# Pool de conexões Postgres (criado preguiçosamente na 1ª chamada de get_conn).
# Razão: cada psycopg.connect() faz TCP+TLS handshake (~1.5-2 s na ligação Brasil-Brasil).
# Manter conexões abertas e reutilizá-las reduz a latência percebida em 20-30×.
# Thread-safe (Streamlit roda em multi-thread sob o capô).
_postgres_pool = None


def _close_pool():
    """Fecha pool ordenadamente no shutdown do processo (evita warning de thread)."""
    global _postgres_pool
    if _postgres_pool is not None:
        try:
            _postgres_pool.close()
        except Exception:
            pass
        _postgres_pool = None


atexit.register(_close_pool)


def _get_pool():
    """Inicializa o pool Postgres na primeira chamada (lazy). Thread-safe."""
    global _postgres_pool
    if _postgres_pool is None:
        from psycopg_pool import ConnectionPool
        from psycopg.rows import dict_row
        _postgres_pool = ConnectionPool(
            DATABASE_URL,
            min_size=2,  # 2 conexões prontas no startup (suporta queries paralelas)
            max_size=5,
            kwargs={
                "row_factory": dict_row,
                # prepare_threshold=None: PgBouncer transaction mode (porta 6543) não
                # rastreia state per-conexão backend; sem esse flag, prepared statements
                # com nomes determinísticos colidem.
                "prepare_threshold": None,
            },
            # Mantém conexões abertas indefinidamente — não derrubar por idle.
            max_idle=600,
            open=True,
        )
        # Pre-warm: aguarda min_size conexões serem abertas ANTES de retornar.
        # Sem isso, a primeira query paga TCP+TLS handshake (~1.5 s).
        # Com isso, o handshake é pago no import time (paralelo a outras inicializações).
        try:
            _postgres_pool.wait(timeout=10.0)
        except Exception:
            # Se wait falhar (timeout, rede ruim), segue mesmo assim — primeira
            # query vai disparar a conexão sob demanda.
            pass
    return _postgres_pool


# Pre-warm: se já estamos em Postgres no momento do import, inicia o pool agora.
# Faz com que o cold start do app (Streamlit Cloud acordando) pague o handshake
# em paralelo a outras inicializações, em vez de pagar na 1ª requisição do usuário.
if IS_POSTGRES:
    try:
        _get_pool()
    except Exception:
        # Falha de pre-warm não bloqueia o app — fallback lazy na 1ª chamada de get_conn.
        pass


class _PooledConnWrapper:
    """Wrapper sobre conexão do pool: `.close()` devolve ao pool em vez de fechar.

    Garante compatibilidade com o resto do código (que faz conn.close() no fim).
    Sem isso, cada close() destruiria a conexão e o pool não serviria pra nada.
    """
    __slots__ = ("_conn", "_pool", "_returned")

    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool
        self._returned = False

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        if not self._returned:
            try:
                # Rollback transações implícitas antes de devolver pro pool.
                # Em SELECTs (caminho mais comum) é no-op; em UPSERTs o commit
                # explícito já foi chamado antes. Silencia warnings do pool.
                try:
                    self._conn.rollback()
                except Exception:
                    pass
                self._pool.putconn(self._conn)
            finally:
                self._returned = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            try:
                self._conn.rollback()
            except Exception:
                pass
        else:
            try:
                self._conn.commit()
            except Exception:
                pass
        self.close()


def get_conn():
    """Abre conexão de acordo com o backend ativo.

    SQLite: sqlite3 padrão, row_factory=Row (acesso por chave string e por índice int).
    Postgres: conexão tirada de um pool global de até 5 conexões reutilizáveis (psycopg 3
    com row_factory=dict_row). A primeira chamada inicializa o pool (lazy).
    Ambos expõem .execute(), .cursor(), .commit(), .rollback(), .close().
    Em Postgres, .close() devolve a conexão ao pool em vez de destruí-la.
    """
    if IS_POSTGRES:
        pool = _get_pool()
        conn = pool.getconn()
        return _PooledConnWrapper(conn, pool)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_folha_completa(data: str) -> dict:
    """Carrega TODOS os blocos da folha de uma data em paralelo (Postgres) ou
    sequencial (SQLite). Reduz o tempo total de 4× round trip → 1× round trip.

    Retorna dict com chaves: 'cocada', 'palha', 'papelzinho', 'pmbd'.

    Otimização crítica para latência Atlântico Supabase × Streamlit Cloud:
    cada query individual leva ~30-50 ms quente; 4 sequenciais = 120-200 ms.
    Executadas em paralelo com pool de 5 conexões → ~30-50 ms total.

    SQLite não é thread-safe por default (cada conexão amarrada à thread que
    a criou). Roda sequencial no caminho local, sem perda — SQLite é μs.
    """
    if IS_POSTGRES:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as ex:
            f_cocada = ex.submit(get_folha_cocada, data)
            f_palha  = ex.submit(get_folha_palha, data)
            f_papel  = ex.submit(get_papelzinho_joel, data)
            f_pmbd   = ex.submit(get_pm_balas_doces, data)
            return {
                "cocada":     f_cocada.result(),
                "palha":      f_palha.result(),
                "papelzinho": f_papel.result(),
                "pmbd":       f_pmbd.result(),
            }
    # SQLite: sequencial (microssegundos cada)
    return {
        "cocada":     get_folha_cocada(data),
        "palha":      get_folha_palha(data),
        "papelzinho": get_papelzinho_joel(data),
        "pmbd":       get_pm_balas_doces(data),
    }


def _sql(query: str) -> str:
    """Adapta placeholders entre backends: '?' (SQLite) ↔ '%s' (psycopg).

    Auditoria do código: nenhuma string SQL em database.py contém '?' literal
    fora de placeholder posicional. Replace global é seguro.
    """
    return query.replace("?", "%s") if IS_POSTGRES else query


def _table_columns(c, tabela: str):
    """Nomes das colunas de uma tabela — wrapper compatível com ambos os backends."""
    if IS_POSTGRES:
        rows = c.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s",
            (tabela,),
        ).fetchall()
        return [r["column_name"] for r in rows]
    return [r[1] for r in c.execute(f"PRAGMA table_info({tabela})").fetchall()]


def _id_pk() -> str:
    """Cláusula PK auto-incremental por backend (sintaxe usada no CREATE TABLE)."""
    return "INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY" if IS_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"


# ════════════════════════════════════════════════════════════════════════════════
# INIT — detecta versão e migra se necessário
# ════════════════════════════════════════════════════════════════════════════════
def init_db():
    """Idempotente: cria schema v2 se não existir; migra v1 → v2 só em SQLite."""
    conn = get_conn()
    c = conn.cursor()

    # Migração v1→v2 só faz sentido em SQLite (nunca houve schema v1 em Postgres).
    if not IS_POSTGRES and _is_schema_v1(c):
        _backup_db()
        _migrate_v1_to_v2(conn)

    _ensure_v2_schema(c)
    _seed_referencias(c)
    conn.commit()
    conn.close()


def _is_schema_v1(c) -> bool:
    """v1 tem coluna `cort_45g_meta` em folha_cocada — sinal claro de schema antigo.
    Chamada apenas no caminho SQLite (gated por IS_POSTGRES em init_db)."""
    try:
        cols = [r[1] for r in c.execute("PRAGMA table_info(folha_cocada)").fetchall()]
        return "cort_45g_meta" in cols
    except sqlite3.Error:
        return False


def _backup_db():
    """Backup .db local antes da migração v1→v2. SQLite-only."""
    if not os.path.exists(DB_PATH):
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{DB_PATH}.bak.{ts}"
    shutil.copy2(DB_PATH, bak)


def _migrate_v1_to_v2(conn):
    """Renomeia tabelas v1, cria v2, copia dados com mapeamento, dropa v1. SQLite-only.

    Mapeamento de colunas (folha_cocada):
        cort_45g            → cort1_45g           (CORTADOS ① — em unidades)
        cort_mini           → cort1_mini
        cort_pet            → cort1_pet
        corte_meta_45g      → ord_corte_45g       (ordem do Eraldo, em bandejas)
        corte_meta_mini     → ord_corte_mini
        corte_meta_pet      → ord_corte_pet
        prod_bandejas       → ord_prod_band
        prod_virada         → ord_prod_virada
        prod_potes_260g     → ord_prod_potes_260g
        prod_potes_605g     → ord_prod_potes_605g
        embalagem_45g       → ord_emb_45g
        embalagem_mini      → ord_emb_mini
        amanha              → amanha_obs

    Dropados (não tinham input ou eram derivados):
        cort_45g_meta, viradas_1, viradas_2, viradas_palha,
        pvirar_1, pvirar_2, pvirar_meta,
        corte_real_45g, corte_real_mini, corte_real_pet
    """
    c = conn.cursor()
    c.execute("ALTER TABLE folha_cocada RENAME TO folha_cocada_v1_legacy")
    c.execute("ALTER TABLE folha_palha RENAME TO folha_palha_v1_legacy")
    c.execute("ALTER TABLE folha_pm_balas_doces RENAME TO folha_pm_balas_doces_v1_legacy")

    _ensure_v2_schema(c)

    c.execute("""
        INSERT INTO folha_cocada
            (data, sabor,
             emb_45g, emb_mini, emb_pet, emb_potes_260g, emb_potes_605g,
             cort1_45g, cort1_mini, cort1_pet,
             ord_corte_45g, ord_corte_mini, ord_corte_pet,
             ord_prod_band, ord_prod_virada,
             ord_prod_potes_260g, ord_prod_potes_605g,
             ord_emb_45g, ord_emb_mini,
             param_real_45g, amanha_obs)
        SELECT
             data, sabor,
             emb_45g, emb_mini, emb_pet, emb_potes_260g, emb_potes_605g,
             cort_45g, cort_mini, cort_pet,
             corte_meta_45g, corte_meta_mini, corte_meta_pet,
             prod_bandejas, prod_virada,
             prod_potes_260g, prod_potes_605g,
             embalagem_45g, embalagem_mini,
             0, COALESCE(amanha, '')
        FROM folha_cocada_v1_legacy
    """)

    c.execute("""
        INSERT INTO folha_palha
            (data, sabor, emb_50g, emb_pet,
             ord_corte_50g, ord_corte_pet, ord_prod_band)
        SELECT
             data, sabor, emb_50g, emb_pet,
             corte_meta_50g, corte_meta_pet, prod_bandejas
        FROM folha_palha_v1_legacy
    """)

    c.execute("""
        INSERT INTO folha_pm_balas_doces
            (data, cnt_pm, cnt_balas, cnt_doces_displays,
             ord_pm, ord_balas, ord_amanha_obs, obs)
        SELECT
             data, pm_qtd, balas_qtd, doces_displays,
             pm_amanha, balas_amanha, '', COALESCE(obs, '')
        FROM folha_pm_balas_doces_v1_legacy
    """)

    c.execute("DROP TABLE folha_cocada_v1_legacy")
    c.execute("DROP TABLE folha_palha_v1_legacy")
    c.execute("DROP TABLE folha_pm_balas_doces_v1_legacy")


# ════════════════════════════════════════════════════════════════════════════════
# SCHEMA v2
# ════════════════════════════════════════════════════════════════════════════════
def _ensure_v2_schema(c):
    pk = _id_pk()

    # ── Folha oficial (cocada) ─────────────────────────────────────────────────
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS folha_cocada (
            id   {pk},
            data TEXT NOT NULL,
            sabor TEXT NOT NULL,
            -- EMBALADOS — produto acabado em estoque (input Leonardo)
            emb_45g            INTEGER DEFAULT 0,   -- unidades
            emb_mini           INTEGER DEFAULT 0,   -- unidades
            emb_pet            INTEGER DEFAULT 0,   -- unidades
            emb_potes_260g     INTEGER DEFAULT 0,   -- unidades
            emb_potes_605g     INTEGER DEFAULT 0,   -- unidades
            -- CORTADOS ① — bandejas cortadas hoje, lado da embalagem (input Leonardo)
            cort1_45g          INTEGER DEFAULT 0,   -- UNIDADES (confirmado com fórmula do Excel)
            cort1_mini         INTEGER DEFAULT 0,
            cort1_pet          INTEGER DEFAULT 0,
            -- ORDENS DO ERALDO
            ord_corte_45g      INTEGER DEFAULT 0,   -- bandejas a cortar
            ord_corte_mini     INTEGER DEFAULT 0,
            ord_corte_pet      INTEGER DEFAULT 0,
            ord_prod_band      INTEGER DEFAULT 0,   -- bandejas a produzir (múltiplo de 8; Z múltiplo de 3)
            ord_prod_virada    INTEGER DEFAULT 0,   -- bandejas
            ord_prod_potes_260g INTEGER DEFAULT 0,  -- unidades de potes
            ord_prod_potes_605g INTEGER DEFAULT 0,
            ord_emb_45g        INTEGER DEFAULT 0,   -- unidades a embalar
            ord_emb_mini       INTEGER DEFAULT 0,
            -- PARÂMETRO REAL DO DIA — base + ajuste do Eraldo, já aplicado (unidades)
            -- 45g: base muda por dia da semana (tabela metas_45g)
            -- Mini/Pet: base é fixa por sabor (tabela metas_mini_pet); Z mini é dinâmico
            param_real_45g     INTEGER DEFAULT 0,
            param_real_mini    INTEGER DEFAULT 0,
            param_real_pet     INTEGER DEFAULT 0,
            -- TEXTO LIVRE
            amanha_obs         TEXT DEFAULT '',
            UNIQUE(data, sabor)
        )
    """)
    # Migração suave: adiciona param_real_mini/pet a bancos existentes
    cols_fc = _table_columns(c, "folha_cocada")
    for col_novo in ("param_real_mini", "param_real_pet"):
        if col_novo not in cols_fc:
            c.execute(f"ALTER TABLE folha_cocada ADD COLUMN {col_novo} INTEGER DEFAULT 0")

    # ── Folha oficial (palha) ──────────────────────────────────────────────────
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS folha_palha (
            id   {pk},
            data TEXT NOT NULL,
            sabor TEXT NOT NULL,
            emb_50g            INTEGER DEFAULT 0,   -- unidades
            emb_pet            INTEGER DEFAULT 0,   -- unidades
            cont_band_palha    INTEGER DEFAULT 0,   -- col D do quadro Viradas (Leonardo conta)
            cont_band_pos_corte INTEGER DEFAULT 0,  -- após abater corte (opcional)
            ord_corte_50g      INTEGER DEFAULT 0,   -- bandejas
            ord_corte_pet      INTEGER DEFAULT 0,   -- bandejas
            ord_prod_band      INTEGER DEFAULT 0,   -- bandejas
            UNIQUE(data, sabor)
        )
    """)

    # ── Papelzinho do Joel (5 colunas, 6 sabores) ──────────────────────────────
    # Z não tem 45g (célula vazia → 0). Mini do Z é 27g, registrado em joel_mini.
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS papelzinho_joel (
            id   {pk},
            data TEXT NOT NULL,
            sabor TEXT NOT NULL,
            joel_45g  INTEGER DEFAULT 0,   -- unidades
            joel_mini INTEGER DEFAULT 0,   -- unidades (coluna "30g" do papel)
            joel_pet  INTEGER DEFAULT 0,   -- BANDEJAS (rendimento 30 und/band; Z=60)
            joel_pv   INTEGER DEFAULT 0,   -- bandejas para virar
            joel_v    INTEGER DEFAULT 0,   -- bandejas viradas
            UNIQUE(data, sabor)
        )
    """)

    # ── PM, Balas, Doces ──────────────────────────────────────────────────────
    # PM = Pão de Mel · Balas · Doces — produtos independentes da cocada/palha.
    # Unidades:
    #   ord_balas: em TACHOS (1 tacho = 30 balas). Ex: "3" = 3 tachos = 90 balas.
    #   ord_pm:    quantidade de Pão de Mel a produzir no dia.
    #   cnt_doces_displays: contagem do dia (normalmente vazio na folha).
    c.execute("""
        CREATE TABLE IF NOT EXISTS folha_pm_balas_doces (
            data TEXT PRIMARY KEY,
            cnt_pm              INTEGER DEFAULT 0,   -- contagem PM hoje (top folha)
            cnt_balas           INTEGER DEFAULT 0,
            cnt_doces_displays  INTEGER DEFAULT 0,
            ord_pm              INTEGER DEFAULT 0,   -- ordem PM do dia (linha 36 folha)
            ord_balas           INTEGER DEFAULT 0,   -- em TACHOS (1 tacho = 30 balas)
            ord_amanha_obs      TEXT DEFAULT '',     -- lembrete livre p/ produção de amanhã
            obs                 TEXT DEFAULT '',     -- avisos gerais do dia (Eraldo → equipe)
            obs_joel            TEXT DEFAULT '',     -- orientações p/ Sr. Joel (produção)
            obs_gil             TEXT DEFAULT '',     -- orientações p/ Gil (corte)
            obs_leonilia        TEXT DEFAULT ''      -- orientações p/ Leonília (embalagem)
        )
    """)
    # Migrações suaves: adiciona colunas em bancos existentes (idempotente em ambos os backends).
    cols_pbd = _table_columns(c, "folha_pm_balas_doces")
    for col_novo in ("obs_joel", "obs_gil", "obs_leonilia"):
        if col_novo not in cols_pbd:
            c.execute(f"ALTER TABLE folha_pm_balas_doces ADD COLUMN {col_novo} TEXT DEFAULT ''")
    # Migração suave: cnt_displays_palha (contagem manual de displays de palha 50g do dia)
    if "cnt_displays_palha" not in cols_pbd:
        c.execute("ALTER TABLE folha_pm_balas_doces ADD COLUMN cnt_displays_palha INTEGER DEFAULT 0")
    # Migração suave: Bala de doce de leite (papelzinho separado contado pelo Joel)
    if "bala_p_cortar" not in cols_pbd:
        c.execute("ALTER TABLE folha_pm_balas_doces ADD COLUMN bala_p_cortar INTEGER DEFAULT 0")
    if "bala_cortadas" not in cols_pbd:
        c.execute("ALTER TABLE folha_pm_balas_doces ADD COLUMN bala_cortadas INTEGER DEFAULT 0")
    # Migração suave: PM inacabado em unidades + bolos (1 bolo = 70 und de PM)
    if "pm_inacabado_und" not in cols_pbd:
        c.execute("ALTER TABLE folha_pm_balas_doces ADD COLUMN pm_inacabado_und INTEGER DEFAULT 0")
    if "pm_bolos" not in cols_pbd:
        c.execute("ALTER TABLE folha_pm_balas_doces ADD COLUMN pm_bolos INTEGER DEFAULT 0")
    # Migração suave: Cocada Assada (ASS — produto independente)
    if "cocada_assada_und" not in cols_pbd:
        c.execute("ALTER TABLE folha_pm_balas_doces ADD COLUMN cocada_assada_und INTEGER DEFAULT 0")

    # ── Tabelas de referência (parâmetros) ─────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS metas_45g (
            sabor TEXT PRIMARY KEY,
            segunda INTEGER, terca INTEGER, quarta INTEGER, quinta INTEGER, sexta INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS metas_mini_pet (
            sabor TEXT PRIMARY KEY,
            mini TEXT,
            pet INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS metas_potes (
            sabor TEXT PRIMARY KEY,
            potes_260g INTEGER, potes_605g INTEGER, ref_bandejas INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS parametros_pvirar_ideal (
            sabor TEXT PRIMARY KEY,
            band INTEGER NOT NULL
        )
    """)
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS conversoes (
            id {pk},
            descricao TEXT,
            rende TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id_produto TEXT PRIMARY KEY,
            stock_real INTEGER DEFAULT 0,
            stock_seguranca INTEGER DEFAULT 0,
            alerta TEXT DEFAULT ''
        )
    """)


# ════════════════════════════════════════════════════════════════════════════════
# SEEDS — apenas tabelas de referência. Folhas do dia nascem do lancamento.py.
# ════════════════════════════════════════════════════════════════════════════════
def _seed_referencias(c):
    # COUNT(*) AS n + acesso por chave: psycopg dict_row não aceita índice posicional.
    if c.execute("SELECT COUNT(*) AS n FROM metas_45g").fetchone()["n"] == 0:
        c.executemany(_sql("INSERT INTO metas_45g VALUES (?,?,?,?,?,?)"), [
            ("TRADICIONAL",      5200, 4400, 5200, 6800, 5600),
            ("LEITE CONDENSADO", 2600, 2200, 2600, 3400, 2800),
            ("BRIGADEIRO",       1300, 1100, 1300, 1700, 1400),
            ("CAFÉ",             1300, 1100, 1300, 1700, 1400),
            ("PÉ DE MOÇA",       1300, 1100, 1300, 1700, 1400),
        ])

    if c.execute("SELECT COUNT(*) AS n FROM metas_mini_pet").fetchone()["n"] == 0:
        c.executemany(_sql("INSERT INTO metas_mini_pet VALUES (?,?,?)"), [
            ("TRADICIONAL",      "500",          220),
            ("LEITE CONDENSADO", "500",          180),
            ("BRIGADEIRO",       "300",           90),
            ("CAFÉ",             "300",           90),
            ("PÉ DE MOÇA",       "300",           90),
            ("ZERO",             "= L 45g/dia",  300),
        ])

    if c.execute("SELECT COUNT(*) AS n FROM metas_potes").fetchone()["n"] == 0:
        c.executemany(_sql("INSERT INTO metas_potes VALUES (?,?,?,?)"), [
            ("TRADICIONAL",      50, 20, 70),
            ("LEITE CONDENSADO",  5, 20, 35),
            ("BRIGADEIRO",       20, 10, 22),
            ("CAFÉ",             15, 10, 22),
            ("PÉ DE MOÇA",       15, 10, 22),
            ("ZERO",             50, 20, 18),
        ])

    if c.execute("SELECT COUNT(*) AS n FROM parametros_pvirar_ideal").fetchone()["n"] == 0:
        # Valores extraídos do Excel oficial (área de parâmetros)
        c.executemany(_sql("INSERT INTO parametros_pvirar_ideal VALUES (?,?)"), [
            ("TRADICIONAL",      70),
            ("LEITE CONDENSADO", 35),
            ("BRIGADEIRO",       22),
            ("CAFÉ",             22),
            ("PÉ DE MOÇA",       22),
            ("ZERO",             18),
        ])

    if c.execute("SELECT COUNT(*) AS n FROM conversoes").fetchone()["n"] == 0:
        c.executemany(_sql("INSERT INTO conversoes (descricao, rende) VALUES (?,?)"), [
            ("1 Tacho",                 "8 Bandejas"),
            ("1 Tacho ZERO",            "3 Bandejas"),
            ("1 Bandeja 45g",           "100 unidades"),
            ("1 Bandeja Mini",          "150 unidades"),
            ("1 Bandeja Pet (normal)",   "30 unidades"),
            ("1 Bandeja Pet ZERO",       "60 unidades"),
            ("1 Bandeja",               "≈ 7 kg"),
        ])

    if c.execute("SELECT COUNT(*) AS n FROM estoque").fetchone()["n"] == 0:
        produtos = []
        for s in SABORES_COCADA:
            sig = SIGLA_COCADA[s]
            for tam, real, seg in [("45G", 1200, 800), ("MINI", 480, 400), ("PET", 90, 60)]:
                if s == "ZERO" and tam == "45G":
                    continue  # Zero não tem 45g
                alerta = "⚠️ GERAR ORDEM" if real < seg else "✅ OK"
                produtos.append((f"COC-{sig}-{tam}", real, seg, alerta))
        for s in SABORES_PALHA:
            sig = SIGLA_PALHA[s]
            for tam, real, seg in [("50G", 200, 150), ("PET", 100, 80)]:
                if tam == "50G" and s not in SABORES_PALHA_50G:
                    continue
                alerta = "⚠️ GERAR ORDEM" if real < seg else "✅ OK"
                produtos.append((f"PAL-{sig}-{tam}", real, seg, alerta))
        c.executemany(_sql("INSERT INTO estoque VALUES (?,?,?,?)"), produtos)


# ════════════════════════════════════════════════════════════════════════════════
# GETTERS — leem por data
# ════════════════════════════════════════════════════════════════════════════════
def get_folha_cocada(data):
    conn = get_conn()
    rows = conn.execute(
        _sql("SELECT * FROM folha_cocada WHERE data=? ORDER BY id"), (data,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_folha_palha(data):
    conn = get_conn()
    rows = conn.execute(
        _sql("SELECT * FROM folha_palha WHERE data=? ORDER BY id"), (data,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_papelzinho_joel(data):
    conn = get_conn()
    rows = conn.execute(
        _sql("SELECT * FROM papelzinho_joel WHERE data=? ORDER BY id"), (data,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pm_balas_doces(data):
    conn = get_conn()
    row = conn.execute(
        _sql("SELECT * FROM folha_pm_balas_doces WHERE data=?"), (data,)
    ).fetchone()
    conn.close()
    return dict(row) if row else {}


def get_estoque():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM estoque ORDER BY id_produto").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_metas_45g():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM metas_45g").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_metas_mini_pet():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM metas_mini_pet").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_metas_potes():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM metas_potes").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pvirar_ideal():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM parametros_pvirar_ideal").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_conversoes():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM conversoes").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_datas_folha():
    """Datas com qualquer dado registrado (qualquer tabela). Útil para histórico/auditoria.

    Subquery FROM (UNION ...) leva alias 'AS u' porque Postgres exige (SQLite ignora).
    ORDER BY id (em vez de rowid) — Postgres não expõe rowid.
    """
    conn = get_conn()
    rows = conn.execute("""
        SELECT DISTINCT data FROM (
            SELECT data FROM folha_cocada
            UNION SELECT data FROM folha_palha
            UNION SELECT data FROM papelzinho_joel
            UNION SELECT data FROM folha_pm_balas_doces
        ) AS u WHERE data IS NOT NULL ORDER BY data DESC
    """).fetchall()
    conn.close()
    return [r["data"] for r in rows]


# ════════════════════════════════════════════════════════════════════════════════
# UPSERTS — gravam (ou atualizam) por (data, sabor) ou (data)
# Apenas as colunas presentes em `fields` são tocadas.
# Sintaxe INSERT … ON CONFLICT … DO UPDATE SET … = excluded.X é idêntica em
# SQLite ≥ 3.24 e Postgres ≥ 9.5 — zero adaptação necessária.
# ════════════════════════════════════════════════════════════════════════════════
def _upsert_por_sabor(tabela, data, sabor, fields):
    if not fields:
        return
    cols = list(fields.keys())
    placeholders = ",".join("?" for _ in cols)
    insert_cols = "data, sabor, " + ", ".join(cols)
    update_set = ", ".join(f"{k}=excluded.{k}" for k in cols)
    conn = get_conn(); c = conn.cursor()
    c.execute(
        _sql(f"INSERT INTO {tabela} ({insert_cols}) VALUES (?, ?, {placeholders}) "
             f"ON CONFLICT(data, sabor) DO UPDATE SET {update_set}"),
        (data, sabor, *fields.values()),
    )
    conn.commit(); conn.close()


def upsert_folha_cocada(data, sabor, fields: dict):
    _upsert_por_sabor("folha_cocada", data, sabor, fields)


def upsert_folha_palha(data, sabor, fields: dict):
    _upsert_por_sabor("folha_palha", data, sabor, fields)


def upsert_papelzinho_joel(data, sabor, fields: dict):
    _upsert_por_sabor("papelzinho_joel", data, sabor, fields)


# ════════════════════════════════════════════════════════════════════════════════
# CÁLCULOS DERIVADOS — fórmulas do papel, recomputadas ao exibir (não persistem)
# ════════════════════════════════════════════════════════════════════════════════
def calcular_cortados(data):
    """Quadro CORTADOS (cocada) — ① ② ③ por sabor para 45g, Mini e Pet.

    ② = cort1 + emb + joel              (somatório fábrica)
    ③ = ② − param_real_*                 (diferença vs parâmetro do dia)

    Atenção Pet: joel_pet vem em BANDEJAS, então é convertido para unidades
    usando o rendimento (30 und/band ou 60 und/band para Z).
    """
    pj_by_sabor = {r["sabor"]: r for r in get_papelzinho_joel(data)}
    fc_by_sabor = {r["sabor"]: r for r in get_folha_cocada(data)}
    out = []
    for s in SABORES_COCADA:
        pj = pj_by_sabor.get(s, {})
        fc = fc_by_sabor.get(s, {})
        c1_45 = fc.get("cort1_45g", 0)
        c2_45 = c1_45 + fc.get("emb_45g", 0) + pj.get("joel_45g", 0)
        c3_45 = c2_45 - fc.get("param_real_45g", 0)
        c1_mi = fc.get("cort1_mini", 0)
        c2_mi = c1_mi + fc.get("emb_mini", 0) + pj.get("joel_mini", 0)
        c3_mi = c2_mi - fc.get("param_real_mini", 0)
        c1_pt = fc.get("cort1_pet", 0)
        rend_pet = 60 if s == "ZERO" else 30  # joel_pet está em bandejas
        joel_pet_und = (pj.get("joel_pet", 0) or 0) * rend_pet
        c2_pt = c1_pt + fc.get("emb_pet", 0) + joel_pet_und
        c3_pt = c2_pt - fc.get("param_real_pet", 0)
        out.append({
            "sabor":   s,
            "c1_45g":  c1_45, "c2_45g":  c2_45, "c3_45g":  c3_45,
            "c1_mini": c1_mi, "c2_mini": c2_mi, "c3_mini": c3_mi,
            "c1_pet":  c1_pt, "c2_pet":  c2_pt, "c3_pet":  c3_pt,
        })
    return out


def calcular_viradas_pvirar(data):
    """Quadros VIRADAS e P/VIRAR — ① puxa do papelzinho do Joel; ② é derivado.

    Viradas ②  = joel_v − (ord_corte_45g + ord_corte_mini + ord_corte_pet)
    P/Virar ②  = joel_pv + Viradas ②
    Meta P/Virar = parametros_pvirar_ideal.band (referência fixa por sabor)
    """
    pj_by_sabor = {r["sabor"]: r for r in get_papelzinho_joel(data)}
    fc_by_sabor = {r["sabor"]: r for r in get_folha_cocada(data)}
    pv_meta = {r["sabor"]: r["band"] for r in get_pvirar_ideal()}
    out = []
    for s in SABORES_COCADA:
        pj = pj_by_sabor.get(s, {})
        fc = fc_by_sabor.get(s, {})
        v1 = pj.get("joel_v", 0)
        ord_corte_total = (fc.get("ord_corte_45g", 0)
                           + fc.get("ord_corte_mini", 0)
                           + fc.get("ord_corte_pet", 0))
        v2 = v1 - ord_corte_total
        pv1 = pj.get("joel_pv", 0)
        pv2 = pv1 + v2
        out.append({
            "sabor": s,
            "vir1": v1, "vir2": v2,
            "pv1": pv1, "pv2": pv2,
            "pv_meta": pv_meta.get(s, 0),
        })
    return out


def salvar_folha_completa(
    data: str,
    *,
    folha_cocada_por_sabor: dict,    # {sabor: {emb_45g, cort1_45g, ...}}
    folha_palha_por_sabor: dict,     # {sabor: {emb_50g, cont_band_palha, ...}}
    papelzinho_por_sabor: dict,      # {sabor: {joel_45g, ...}}
    pm_balas_doces: dict,            # {cnt_pm, cnt_balas, ...}
):
    """Salva todos os blocos da folha de uma data em UMA transação atômica.

    Se qualquer INSERT falhar, faz rollback de tudo (banco volta ao estado anterior).
    Usa INSERT ... ON CONFLICT DO UPDATE — operação idempotente (pode ser repetida).
    """
    def _build_upsert_sql(table, key_cols, data_cols):
        all_cols = ", ".join(key_cols + data_cols)
        all_phs = ", ".join("?" for _ in (key_cols + data_cols))
        update_set = ", ".join(f"{k}=excluded.{k}" for k in data_cols)
        conflict = ", ".join(key_cols)
        return _sql(
            f"INSERT INTO {table} ({all_cols}) VALUES ({all_phs}) "
            f"ON CONFLICT({conflict}) DO UPDATE SET {update_set}"
        )

    conn = get_conn()
    try:
        c = conn.cursor()

        # folha_cocada — chave (data, sabor)
        for sabor, fields in folha_cocada_por_sabor.items():
            if not fields:
                continue
            cols = list(fields.keys())
            sql = _build_upsert_sql("folha_cocada", ["data", "sabor"], cols)
            c.execute(sql, (data, sabor, *fields.values()))

        # folha_palha — chave (data, sabor)
        for sabor, fields in folha_palha_por_sabor.items():
            if not fields:
                continue
            cols = list(fields.keys())
            sql = _build_upsert_sql("folha_palha", ["data", "sabor"], cols)
            c.execute(sql, (data, sabor, *fields.values()))

        # papelzinho_joel — chave (data, sabor)
        for sabor, fields in papelzinho_por_sabor.items():
            if not fields:
                continue
            cols = list(fields.keys())
            sql = _build_upsert_sql("papelzinho_joel", ["data", "sabor"], cols)
            c.execute(sql, (data, sabor, *fields.values()))

        # folha_pm_balas_doces — chave (data)
        if pm_balas_doces:
            cols = list(pm_balas_doces.keys())
            sql = _build_upsert_sql("folha_pm_balas_doces", ["data"], cols)
            c.execute(sql, (data, *pm_balas_doces.values()))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def excluir_folha(data: str):
    """Apaga TODOS os registros (cocada, palha, papelzinho, PM/balas/doces) de uma data.

    Operação destrutiva. Não há undo automático — o usuário deve confirmar antes na UI.
    Tabelas de referência (metas, parâmetros) não são afetadas.
    """
    conn = get_conn()
    try:
        c = conn.cursor()
        for tabela in ("folha_cocada", "folha_palha", "papelzinho_joel", "folha_pm_balas_doces"):
            c.execute(_sql(f"DELETE FROM {tabela} WHERE data = ?"), (data,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def duplicar_folha(data_origem: str, data_destino: str):
    """Copia TODOS os dados de uma folha para outra data.

    Se a data destino já tem dados, eles são sobrescritos (via salvar_folha_completa
    que faz INSERT ON CONFLICT UPDATE). Útil para criar folha de hoje a partir
    de um template (folha de ontem ou semana passada).
    """
    if data_origem == data_destino:
        return  # nada a fazer

    def _strip_keys(row, exclude=("id", "data", "sabor")):
        return {k: row[k] for k in row.keys() if k not in exclude}

    cocada = {r["sabor"]: _strip_keys(r) for r in get_folha_cocada(data_origem)}
    palha  = {r["sabor"]: _strip_keys(r) for r in get_folha_palha(data_origem)}
    papel  = {r["sabor"]: _strip_keys(r) for r in get_papelzinho_joel(data_origem)}

    pmbd_full = get_pm_balas_doces(data_origem) or {}
    pmbd = {k: v for k, v in pmbd_full.items() if k != "data"}

    salvar_folha_completa(
        data_destino,
        folha_cocada_por_sabor=cocada,
        folha_palha_por_sabor=palha,
        papelzinho_por_sabor=papel,
        pm_balas_doces=pmbd,
    )


def upsert_pm_balas_doces(data, fields: dict):
    if not fields:
        return
    cols = list(fields.keys())
    placeholders = ",".join("?" for _ in cols)
    insert_cols = "data, " + ", ".join(cols)
    update_set = ", ".join(f"{k}=excluded.{k}" for k in cols)
    conn = get_conn(); c = conn.cursor()
    c.execute(
        _sql(f"INSERT INTO folha_pm_balas_doces ({insert_cols}) VALUES (?, {placeholders}) "
             f"ON CONFLICT(data) DO UPDATE SET {update_set}"),
        (data, *fields.values()),
    )
    conn.commit(); conn.close()
