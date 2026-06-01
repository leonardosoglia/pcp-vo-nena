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
import math
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


# ── Suprimentos (módulo de insumos + BOM + movimentações) ────────────────────
# Categorias que um insumo pode ter. Lista controlada (não-extensível em runtime).
CATEGORIAS_INSUMO = [
    "materia_prima",  # coco, leite condensado, açúcar, mel, farinha, chocolate, café, etc.
    "embalagem",      # plástico individual (45g, Mini, Pet)
    "pote",           # pote 260g, pote 605g
    "cinta",          # cinta de papel (45g, Mini)
    "display",        # caixa de display palha 50g
    "outros",         # qualquer outro item consumível
]

# Unidades aceitas pra estoque/quantidade. Não é exclusivo — TEXT no banco —
# mas a UI usa essa lista pra selectbox.
UNIDADES_INSUMO = ["kg", "g", "L", "mL", "und", "cx", "m", "pacote"]

# Tipos de movimentação. 'entrada' soma ao estoque, 'saida' subtrai.
TIPOS_MOVIMENTO = ["entrada", "saida"]

# Origens prováveis de uma movimentação. Documenta de onde veio o lançamento.
ORIGENS_MOVIMENTO = [
    "compra",            # entrada vinda de NF de compra
    "producao_auto",     # saída automática quando uma folha é salva (Etapa E)
    "producao_manual",   # saída lançada manualmente pela Gestão
    "perda",             # saída por descarte (lote ruim, vencimento, queima)
    "ajuste",            # ajuste manual de inventário (contagem física diferente)
    "contagem_inicial",  # entrada do cadastro inicial do estoque
]


# ── Equipe (módulo de funcionários + capacidades + presença) ─────────────────
# Departamentos disponíveis pra cadastro de funcionário.
# Alinhado com a renomeação da Etapa A (14/05/2026): UI usa departamentos,
# não nomes pessoais. Aqui mantemos pra agrupar visualmente.
DEPARTAMENTOS_FUNCIONARIO = [
    "Gestão",
    "Produção",
    "Corte",
    "Embalagem",
    "Estoque/Contagem",
    "Suprimentos",
    "Auxiliar geral",
]

# Atividades padronizadas pra cadastro de capacidade. Lista controlada pra
# permitir consultas estruturadas pelo algoritmo de Sugestão de Ordem (Ideia 4
# Etapa C). Cada atividade tem uma unidade típica anotada nos comentários.
ATIVIDADES_CAPACIDADE = [
    # Cocada
    "corte_cocada_45g",      # band/dia (Gil, Paulo)
    "corte_cocada_mini",     # band/dia
    "corte_cocada_pet",      # band/dia
    "viracao_cocada",        # band/dia (Paulo, equipe Corte)
    "producao_cocada",       # tachos/dia (Joel)
    # Palha
    "corte_palha_50g",       # band/dia (Maria, talvez Gil)
    "corte_palha_pet",       # band/dia
    "producao_palha",        # tachos/dia (Maria)
    # Embalagem
    "embalagem_plastico",    # und/dia (Popô)
    "embalagem_cinta",       # und/dia (Leonília)
    # Outros produtos
    "producao_pm",           # bolos/dia
    "producao_bala",         # tachos/dia
    # Suporte
    "contagem_estoque",      # operações completas/dia (Leonardo, 1 normalmente)
]

# Tipos de evento/observação da semana (gap 2 da Camada 2 cocada).
# Cada tipo ganha um rótulo amigável na UI. 'observacao' é o default genérico.
TIPOS_EVENTO = [
    "equipe_reduzida",   # menos gente que o normal num dia
    "feriado",           # fábrica fechada ou meia-jornada
    "pedido_grande",     # encomenda fora da curva
    "manutencao",        # equipamento/limpeza pesada
    "observacao",        # anotação livre genérica
]


def chave_produto_cocada(sabor: str) -> str:
    """Chave canônica do produto cocada na tabela bom_produto.

    A receita é POR TACHO (uma produção inteira), NÃO por formato — descoberta
    da entrevista com a Gestão (15/05/2026): "a mesma receita da Tradicional 45g
    vai na Mini e na Pet, só os formatos são diferentes". O formato (45g/Mini/Pet)
    é decidido só no corte, depois — não afeta a receita.
    Ex: 'TRADICIONAL' → 'cocada_T_tacho' · 'ZERO' → 'cocada_Z_tacho'.
    """
    sigla = SIGLA_COCADA.get(sabor, sabor[:1])
    return f"cocada_{sigla}_tacho"


def chave_produto_palha(sabor: str) -> str:
    """Chave canônica do produto palha — uma receita por BANDEJA.

    Confirmado 22/05/2026 (CADERNO 1.A): a palha NÃO é feita em tacho, é em
    PANELA. Cada receita = 1 panela = 1 bandeja. A receita técnica das fichas
    é, portanto, 'por bandeja', não 'por tacho'.
    Ex: 'LEITE EM PÓ' → 'palha_L_band'.
    """
    sigla = SIGLA_PALHA.get(sabor, sabor[:3])
    return f"palha_{sigla}_band"


def listar_produtos_possiveis() -> list[dict]:
    """Produtos que podem ter receita (BOM) cadastrada.
    Cada item tem 'chave' (canônica), 'nome' (label pra UI) e 'grupo'.
    Cocada e palha: UMA receita por sabor (por tacho) — não por formato.
    """
    produtos = []
    for sabor in SABORES_COCADA:
        produtos.append({
            "chave": chave_produto_cocada(sabor),
            "nome": f"Cocada {sabor} (1 tacho)",
            "grupo": "Cocada",
        })
    for sabor in SABORES_PALHA:
        produtos.append({
            "chave": chave_produto_palha(sabor),
            "nome": f"Palha {sabor} (1 bandeja)",
            "grupo": "Palha",
        })
    produtos.extend([
        {"chave": "pm_bolo",     "nome": "Pão de Mel (1 bolo = 70 unidades)", "grupo": "PM/Balas/Doces"},
        {"chave": "bala_tacho",  "nome": "Bala de doce de leite (1 tacho = 30 balas)", "grupo": "PM/Balas/Doces"},
        {"chave": "doce_und",    "nome": "Doce de leite (1 unidade)", "grupo": "PM/Balas/Doces"},
    ])
    return produtos


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
            min_size=4,  # 4 conexões prontas — get_folha_completa dispara 4 queries paralelas
            max_size=8,  # margem pra picos sem precisar reabrir TCP+TLS
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

    # Migração suave: PESSOAS POR ÁREA + OBSERVAÇÃO DO DIA (feature 01/06/2026).
    # Contagem de quantas pessoas atuaram em cada área/atividade no dia (entender o
    # manejo de pessoal) + um campo livre de observações do dia — distinto de "obs"
    # (que são as Orientações da Gestão p/ a equipe). Tudo a nível de DATA.
    for _col_pes in (
        "pes_producao", "pes_corte_band", "pes_maq_emb", "pes_embalagem",
        "pes_palha", "pes_pm", "pes_bala", "pes_cocada_assada", "pes_virada",
    ):
        if _col_pes not in cols_pbd:
            c.execute(f"ALTER TABLE folha_pm_balas_doces ADD COLUMN {_col_pes} INTEGER DEFAULT 0")
    if "observacao_dia" not in cols_pbd:
        c.execute("ALTER TABLE folha_pm_balas_doces ADD COLUMN observacao_dia TEXT DEFAULT ''")

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

    # ════════════════════════════════════════════════════════════════════════
    # SUPRIMENTOS (Etapa B — 15/05/2026)
    # Modelo de insumos + receitas (BOM) + movimentações de estoque.
    # ════════════════════════════════════════════════════════════════════════
    # Catálogo de insumos (matéria-prima, embalagem, potes, cintas, etc).
    # estoque_atual usa REAL (float) pra suportar quantidades fracionárias
    # como 12.5 kg, 0.5 L, etc. Postgres usa DOUBLE PRECISION; SQLite mapeia REAL.
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS insumos (
            id {pk},
            codigo TEXT NOT NULL UNIQUE,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            unidade TEXT NOT NULL,
            estoque_atual REAL DEFAULT 0,
            estoque_minimo REAL DEFAULT 0,
            estoque_seguranca REAL DEFAULT 0,
            fornecedor TEXT DEFAULT '',
            lead_time_dias INTEGER DEFAULT 0,
            custo_unitario REAL DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            obs TEXT DEFAULT '',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # BOM (Bill of Materials) — receita de cada produto. Cada linha = 1 insumo
    # consumido pra produzir 1 unidade do produto (1 bandeja, 1 bolo, 1 tacho).
    # `produto_chave` segue convenção de listar_produtos_possiveis() em database.py.
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS bom_produto (
            id {pk},
            produto_chave TEXT NOT NULL,
            insumo_id INTEGER NOT NULL,
            quantidade REAL NOT NULL,
            unidade TEXT NOT NULL,
            obs TEXT DEFAULT '',
            UNIQUE(produto_chave, insumo_id)
        )
    """)

    # Movimentações de estoque (histórico). Rastreabilidade: toda mudança de
    # estoque_atual passa por aqui. estoque_atual em `insumos` é cache;
    # soma dos movimentos por insumo deve bater.
    # quantidade SEMPRE positiva — o sinal vem do `tipo` (entrada/saida).
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS movimentos_insumo (
            id {pk},
            data TEXT NOT NULL,
            insumo_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            quantidade REAL NOT NULL,
            origem TEXT DEFAULT '',
            referencia TEXT DEFAULT '',
            obs TEXT DEFAULT '',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ════════════════════════════════════════════════════════════════════════
    # EQUIPE — funcionários + capacidades + presença diária (Ideia 4 — 19/05/2026)
    # Fundação pra Sugestão Automática de Ordem do Dia. Inputs principais:
    # quem tá presente hoje × quanto cada um produz × quais atividades faz.
    # ════════════════════════════════════════════════════════════════════════
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id {pk},
            nome TEXT NOT NULL UNIQUE,
            departamento TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            observacao TEXT DEFAULT '',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Capacidades por atividade. Um funcionário pode ter várias linhas
    # (Gil corta 45g E corta Mini, com valores diferentes). UNIQUE(func,atividade)
    # garante 1 linha por par. valor_normal é o esperado; min/max delimitam
    # banda observada (pra futuro algoritmo de sugestão usar como restrição).
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS capacidades_funcionario (
            id {pk},
            funcionario_id INTEGER NOT NULL,
            atividade TEXT NOT NULL,
            valor_normal REAL NOT NULL,
            valor_min REAL DEFAULT 0,
            valor_max REAL DEFAULT 0,
            unidade TEXT DEFAULT '',
            observacao TEXT DEFAULT '',
            UNIQUE(funcionario_id, atividade)
        )
    """)

    # Presença diária. Input simples (presente/ausente por funcionário por data).
    # Usado pelo algoritmo de Sugestão pra calcular capacidade EFETIVA do dia.
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS presenca_diaria (
            id {pk},
            data TEXT NOT NULL,
            funcionario_id INTEGER NOT NULL,
            presente INTEGER DEFAULT 1,
            observacao TEXT DEFAULT '',
            UNIQUE(data, funcionario_id)
        )
    """)

    # Eventos / observações da semana (gap 2 da Camada 2 cocada — CADERNO 1.B).
    # Contexto que a Gestão conhece mas o sistema não deriva da folha: dia de
    # equipe reduzida, feriado, pedido grande, manutenção. Faz a Gestão adiantar
    # ou segurar corte/produção. Captura livre — a leitura é humana (e, no futuro,
    # entra como contexto pro assistente IA). Não dispara cálculo automático.
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS eventos_semana (
            id {pk},
            data TEXT NOT NULL,
            tipo TEXT DEFAULT 'observacao',
            descricao TEXT NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
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
            ("1 Bandeja 45g",                "100 unidades"),
            ("1 Bandeja Mini",               "150 unidades"),
            ("1 Bandeja Pet (normal)",        "30 unidades"),
            ("1 Bandeja Pet ZERO",            "60 unidades"),
            ("1 Bandeja recém-tacho",         "≈ 6 kg (úmida)"),
            ("1 Bandeja pronta p/ corte",     "≈ 5,5 kg (após viração + descanso)"),
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
    auto_baixa: bool = False,
) -> dict:
    """Salva todos os blocos da folha de uma data em UMA transação atômica.

    Se qualquer INSERT falhar, faz rollback de tudo (banco volta ao estado anterior).
    Usa INSERT ... ON CONFLICT DO UPDATE — operação idempotente (pode ser repetida).

    auto_baixa (Etapa E):
        Quando True, dispara `baixar_insumos_da_folha(data)` DEPOIS do commit
        da folha. A baixa roda na sua própria transação — se falhar, a folha
        permanece salva e a exceção é repropagada (chamador decide o que fazer).
        Default False pra preservar comportamento legado de scripts/testes que
        não querem mexer em estoque.

    Retorna dict:
        {'folha_salva': True, 'baixa': {...} | None}
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

    baixa_resultado = None
    if auto_baixa:
        # Conexão própria, transação separada. Se falhar, folha permanece salva.
        baixa_resultado = baixar_insumos_da_folha(data)

    return {"folha_salva": True, "baixa": baixa_resultado}


def excluir_folha(data: str, reverter_baixa: bool = True):
    """Apaga TODOS os registros (cocada, palha, papelzinho, PM/balas/doces) de uma data.

    Operação destrutiva. Não há undo automático — o usuário deve confirmar antes na UI.
    Tabelas de referência (metas, parâmetros) não são afetadas.

    reverter_baixa (Etapa E): por padrão True — se a folha excluída tinha baixa
    automática registrada, estorna os movimentos pra manter o estoque coerente.
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

    if reverter_baixa:
        # Transação separada; se não houver baixa, é no-op.
        reverter_baixa_da_folha(data)


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


# ════════════════════════════════════════════════════════════════════════════════
# SUPRIMENTOS — CRUD de insumos, receitas (BOM) e movimentações
# ════════════════════════════════════════════════════════════════════════════════

# ── Insumos (catálogo) ────────────────────────────────────────────────────────
def get_insumos(categoria: str | None = None, somente_ativos: bool = True) -> list[dict]:
    """Lista insumos cadastrados. Filtra por categoria se informado.
    `somente_ativos=True` esconde insumos desativados (ativo=0)."""
    conn = get_conn()
    sql = "SELECT * FROM insumos WHERE 1=1"
    params: list = []
    if somente_ativos:
        sql += " AND ativo = 1"
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
    sql += " ORDER BY categoria, nome"
    rows = conn.execute(_sql(sql), tuple(params)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_insumo(insumo_id: int) -> dict | None:
    """Busca um insumo pelo ID. Retorna None se não existe."""
    conn = get_conn()
    row = conn.execute(_sql("SELECT * FROM insumos WHERE id = ?"), (insumo_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_insumo_por_codigo(codigo: str) -> dict | None:
    """Busca insumo pelo código único (ex: 'INS-COCO-RALADO')."""
    conn = get_conn()
    row = conn.execute(_sql("SELECT * FROM insumos WHERE codigo = ?"), (codigo,)).fetchone()
    conn.close()
    return dict(row) if row else None


def criar_insumo(dados: dict) -> int:
    """Cria um insumo novo. Retorna o id gerado.

    Campos obrigatórios: codigo (único), nome, categoria, unidade.
    Opcionais: estoque_atual, estoque_minimo, estoque_seguranca, fornecedor,
               lead_time_dias, custo_unitario, obs.

    Se `estoque_atual` > 0, registra um movimento de origem 'contagem_inicial'
    pra manter coerência entre estoque_atual e soma de movimentos.
    """
    obrigatorios = ("codigo", "nome", "categoria", "unidade")
    for f in obrigatorios:
        if not dados.get(f):
            raise ValueError(f"Campo obrigatório ausente: {f}")
    if dados["categoria"] not in CATEGORIAS_INSUMO:
        raise ValueError(f"Categoria inválida: {dados['categoria']}. Use uma de {CATEGORIAS_INSUMO}.")

    cols_validas = [
        "codigo", "nome", "categoria", "unidade",
        "estoque_atual", "estoque_minimo", "estoque_seguranca",
        "fornecedor", "lead_time_dias", "custo_unitario",
        "ativo", "obs",
    ]
    fields = {k: v for k, v in dados.items() if k in cols_validas}
    cols = list(fields.keys())
    placeholders = ", ".join("?" for _ in cols)

    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute(
            _sql(f"INSERT INTO insumos ({', '.join(cols)}) VALUES ({placeholders})"),
            tuple(fields.values()),
        )
        # Pega o id inserido (compatível com ambos os backends)
        if IS_POSTGRES:
            insumo_id = c.execute(
                _sql("SELECT id FROM insumos WHERE codigo = ?"), (dados["codigo"],)
            ).fetchone()["id"]
        else:
            insumo_id = c.lastrowid

        # Se estoque inicial > 0, registra movimento de contagem inicial
        estoque_ini = float(dados.get("estoque_atual") or 0)
        if estoque_ini > 0:
            from datetime import date as _date
            c.execute(
                _sql("INSERT INTO movimentos_insumo (data, insumo_id, tipo, quantidade, origem, obs) "
                     "VALUES (?, ?, ?, ?, ?, ?)"),
                (_date.today().isoformat(), insumo_id, "entrada", estoque_ini,
                 "contagem_inicial", "Cadastro inicial do insumo"),
            )

        conn.commit()
        return insumo_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def atualizar_insumo(insumo_id: int, dados: dict):
    """Atualiza campos de um insumo. NÃO atualiza estoque_atual — pra mudar
    estoque, usar `registrar_movimento_insumo` (mantém rastreabilidade)."""
    if not dados:
        return
    cols_editaveis = [
        "nome", "categoria", "unidade", "estoque_minimo", "estoque_seguranca",
        "fornecedor", "lead_time_dias", "custo_unitario", "ativo", "obs",
    ]
    fields = {k: v for k, v in dados.items() if k in cols_editaveis}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
    set_clause += ", atualizado_em = CURRENT_TIMESTAMP"

    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute(
            _sql(f"UPDATE insumos SET {set_clause} WHERE id = ?"),
            (*fields.values(), insumo_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def excluir_insumo(insumo_id: int):
    """Marca insumo como inativo (não apaga — preserva histórico de movimentos).
    Pra apagar de verdade, fazer DELETE direto no banco (perigoso, perde refs)."""
    atualizar_insumo(insumo_id, {"ativo": 0})


# ── BOM (Receitas — Bill of Materials) ────────────────────────────────────────
def get_bom_produto(produto_chave: str) -> list[dict]:
    """Lista de insumos consumidos por 1 unidade do produto especificado.
    Cada linha vem com os dados do insumo JOINed (nome, unidade, etc)."""
    conn = get_conn()
    sql = """
        SELECT b.id, b.produto_chave, b.insumo_id, b.quantidade, b.unidade, b.obs,
               i.codigo, i.nome AS insumo_nome, i.categoria,
               i.unidade AS insumo_unidade, i.estoque_atual
        FROM bom_produto b
        INNER JOIN insumos i ON i.id = b.insumo_id
        WHERE b.produto_chave = ?
        ORDER BY i.categoria, i.nome
    """
    rows = conn.execute(_sql(sql), (produto_chave,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_bom_linha(produto_chave: str, insumo_id: int, quantidade: float,
                     unidade: str, obs: str = "") -> int:
    """Insere ou atualiza uma linha de receita.
    UNIQUE(produto_chave, insumo_id) garante que não há duplicata."""
    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute(
            _sql("INSERT INTO bom_produto (produto_chave, insumo_id, quantidade, unidade, obs) "
                 "VALUES (?, ?, ?, ?, ?) "
                 "ON CONFLICT(produto_chave, insumo_id) DO UPDATE SET "
                 "quantidade = excluded.quantidade, "
                 "unidade = excluded.unidade, "
                 "obs = excluded.obs"),
            (produto_chave, insumo_id, quantidade, unidade, obs),
        )
        conn.commit()
        # Retorna id da linha (pra ambos os backends)
        row = c.execute(
            _sql("SELECT id FROM bom_produto WHERE produto_chave = ? AND insumo_id = ?"),
            (produto_chave, insumo_id),
        ).fetchone()
        return row["id"] if row else 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def excluir_bom_linha(linha_id: int):
    """Remove uma linha específica de BOM."""
    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute(_sql("DELETE FROM bom_produto WHERE id = ?"), (linha_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Movimentações de estoque ──────────────────────────────────────────────────
def registrar_movimento_insumo(insumo_id: int, tipo: str, quantidade: float,
                                origem: str = "", referencia: str = "",
                                obs: str = "", data: str | None = None):
    """Registra uma movimentação e atualiza estoque_atual atomicamente.

    Args:
        insumo_id: FK pra tabela insumos.
        tipo: 'entrada' (soma) ou 'saida' (subtrai).
        quantidade: SEMPRE positiva (o sinal vem do tipo).
        origem: ver ORIGENS_MOVIMENTO (compra, perda, ajuste, etc).
        referencia: texto livre (NF, data folha, etc).
        obs: observação opcional.
        data: YYYY-MM-DD. Default = hoje.

    Atualiza estoque_atual em uma única transação atômica.
    """
    if tipo not in TIPOS_MOVIMENTO:
        raise ValueError(f"Tipo inválido: {tipo}. Use 'entrada' ou 'saida'.")
    if quantidade <= 0:
        raise ValueError("Quantidade deve ser positiva (o sinal vem do tipo).")
    if not data:
        from datetime import date as _date
        data = _date.today().isoformat()

    delta = quantidade if tipo == "entrada" else -quantidade

    conn = get_conn()
    try:
        c = conn.cursor()
        # 1. Insere movimentação
        c.execute(
            _sql("INSERT INTO movimentos_insumo "
                 "(data, insumo_id, tipo, quantidade, origem, referencia, obs) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?)"),
            (data, insumo_id, tipo, quantidade, origem, referencia, obs),
        )
        # 2. Atualiza cache de estoque_atual no insumo
        c.execute(
            _sql("UPDATE insumos SET estoque_atual = estoque_atual + ?, "
                 "atualizado_em = CURRENT_TIMESTAMP WHERE id = ?"),
            (delta, insumo_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_movimentos_insumo(insumo_id: int | None = None,
                           data_inicio: str | None = None,
                           data_fim: str | None = None,
                           tipo: str | None = None,
                           limite: int = 100) -> list[dict]:
    """Histórico de movimentações. Filtros opcionais.
    JOIN com insumos pra trazer nome + unidade."""
    conn = get_conn()
    sql = """
        SELECT m.id, m.data, m.insumo_id, m.tipo, m.quantidade,
               m.origem, m.referencia, m.obs, m.criado_em,
               i.codigo, i.nome AS insumo_nome, i.unidade AS insumo_unidade
        FROM movimentos_insumo m
        INNER JOIN insumos i ON i.id = m.insumo_id
        WHERE 1=1
    """
    params: list = []
    if insumo_id is not None:
        sql += " AND m.insumo_id = ?"
        params.append(insumo_id)
    if data_inicio:
        sql += " AND m.data >= ?"
        params.append(data_inicio)
    if data_fim:
        sql += " AND m.data <= ?"
        params.append(data_fim)
    if tipo:
        sql += " AND m.tipo = ?"
        params.append(tipo)
    sql += " ORDER BY m.data DESC, m.id DESC LIMIT ?"
    params.append(limite)

    rows = conn.execute(_sql(sql), tuple(params)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ════════════════════════════════════════════════════════════════════════════
# EQUIPE — CRUD de funcionários, capacidades e presença (Ideia 4 — Etapa A)
# ════════════════════════════════════════════════════════════════════════════
def get_funcionarios(somente_ativos: bool = True) -> list[dict]:
    """Lista funcionários cadastrados. Por padrão só ativos."""
    conn = get_conn()
    if somente_ativos:
        rows = conn.execute(
            _sql("SELECT * FROM funcionarios WHERE ativo = 1 ORDER BY departamento, nome")
        ).fetchall()
    else:
        rows = conn.execute(
            _sql("SELECT * FROM funcionarios ORDER BY ativo DESC, departamento, nome")
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_funcionario(funcionario_id: int) -> dict | None:
    """Busca 1 funcionário por id. Retorna None se não existir."""
    conn = get_conn()
    row = conn.execute(
        _sql("SELECT * FROM funcionarios WHERE id = ?"),
        (funcionario_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def criar_funcionario(nome: str, departamento: str,
                       observacao: str = "") -> int:
    """Cria novo funcionário. Retorna ID criado. Levanta erro se nome já existe."""
    if not nome or not nome.strip():
        raise ValueError("Nome do funcionário não pode ser vazio.")
    nome = nome.strip()

    conn = get_conn()
    try:
        c = conn.cursor()
        if IS_POSTGRES:
            row = c.execute(
                _sql("INSERT INTO funcionarios (nome, departamento, observacao) "
                     "VALUES (?, ?, ?) RETURNING id"),
                (nome, departamento, observacao),
            ).fetchone()
            new_id = row["id"]
        else:
            c.execute(
                "INSERT INTO funcionarios (nome, departamento, observacao) "
                "VALUES (?, ?, ?)",
                (nome, departamento, observacao),
            )
            new_id = c.lastrowid
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def atualizar_funcionario(funcionario_id: int, **campos):
    """Atualiza campos do funcionário. Campos aceitos: nome, departamento,
    ativo, observacao."""
    permitidos = {"nome", "departamento", "ativo", "observacao"}
    campos_validos = {k: v for k, v in campos.items() if k in permitidos}
    if not campos_validos:
        return

    set_clause = ", ".join(f"{k} = ?" for k in campos_validos)
    params = list(campos_validos.values()) + [funcionario_id]

    conn = get_conn()
    try:
        conn.execute(
            _sql(f"UPDATE funcionarios SET {set_clause} WHERE id = ?"),
            tuple(params),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def excluir_funcionario(funcionario_id: int):
    """Soft delete: marca ativo=0. Preserva histórico de capacidades/presença."""
    atualizar_funcionario(funcionario_id, ativo=0)


def get_capacidades_funcionario(funcionario_id: int) -> list[dict]:
    """Lista capacidades cadastradas pra um funcionário (todas atividades)."""
    conn = get_conn()
    rows = conn.execute(
        _sql("SELECT * FROM capacidades_funcionario "
             "WHERE funcionario_id = ? ORDER BY atividade"),
        (funcionario_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_capacidade(funcionario_id: int, atividade: str) -> dict | None:
    """Busca capacidade específica (1 funcionário × 1 atividade)."""
    conn = get_conn()
    row = conn.execute(
        _sql("SELECT * FROM capacidades_funcionario "
             "WHERE funcionario_id = ? AND atividade = ?"),
        (funcionario_id, atividade),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_capacidade(funcionario_id: int, atividade: str,
                       valor_normal: float,
                       valor_min: float = 0, valor_max: float = 0,
                       unidade: str = "", observacao: str = "") -> int:
    """Insere ou atualiza capacidade (funcionario, atividade). Idempotente.

    Retorna ID da linha."""
    if not atividade:
        raise ValueError("Atividade não pode ser vazia.")
    if valor_normal < 0:
        raise ValueError("valor_normal deve ser >= 0.")

    existente = get_capacidade(funcionario_id, atividade)
    conn = get_conn()
    try:
        if existente:
            conn.execute(
                _sql("UPDATE capacidades_funcionario SET "
                     "valor_normal = ?, valor_min = ?, valor_max = ?, "
                     "unidade = ?, observacao = ? "
                     "WHERE id = ?"),
                (valor_normal, valor_min, valor_max,
                 unidade, observacao, existente["id"]),
            )
            id_linha = existente["id"]
        else:
            c = conn.cursor()
            if IS_POSTGRES:
                row = c.execute(
                    _sql("INSERT INTO capacidades_funcionario "
                         "(funcionario_id, atividade, valor_normal, valor_min, "
                         "valor_max, unidade, observacao) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id"),
                    (funcionario_id, atividade, valor_normal,
                     valor_min, valor_max, unidade, observacao),
                ).fetchone()
                id_linha = row["id"]
            else:
                c.execute(
                    "INSERT INTO capacidades_funcionario "
                    "(funcionario_id, atividade, valor_normal, valor_min, "
                    "valor_max, unidade, observacao) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (funcionario_id, atividade, valor_normal,
                     valor_min, valor_max, unidade, observacao),
                )
                id_linha = c.lastrowid
        conn.commit()
        return id_linha
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def excluir_capacidade(capacidade_id: int):
    """Remove uma capacidade (hard delete — não tem histórico significativo)."""
    conn = get_conn()
    try:
        conn.execute(
            _sql("DELETE FROM capacidades_funcionario WHERE id = ?"),
            (capacidade_id,),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_capacidades_atividade(atividade: str,
                                somente_ativos: bool = True) -> list[dict]:
    """Lista quem pode fazer uma atividade, com capacidades. JOIN com funcionarios.

    Usado pelo algoritmo de Sugestão de Ordem (Etapa C) pra calcular
    capacidade efetiva do dia (depende de quem está presente)."""
    conn = get_conn()
    sql = """
        SELECT c.id AS cap_id, c.funcionario_id, c.atividade,
               c.valor_normal, c.valor_min, c.valor_max, c.unidade,
               c.observacao AS cap_obs,
               f.nome, f.departamento, f.ativo
        FROM capacidades_funcionario c
        INNER JOIN funcionarios f ON f.id = c.funcionario_id
        WHERE c.atividade = ?
    """
    params = [atividade]
    if somente_ativos:
        sql += " AND f.ativo = 1"
    sql += " ORDER BY c.valor_normal DESC"
    rows = conn.execute(_sql(sql), tuple(params)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_presenca_dia(data: str) -> list[dict]:
    """Lista presença registrada de TODOS os funcionários ativos em uma data.

    Pra funcionários ainda sem registro de presença na data, retorna entrada
    com presente=NULL (UI trata como 'não marcado ainda'). JOIN com funcionarios.
    """
    conn = get_conn()
    sql = """
        SELECT f.id AS funcionario_id, f.nome, f.departamento,
               p.id AS presenca_id, p.presente, p.observacao
        FROM funcionarios f
        LEFT JOIN presenca_diaria p
            ON p.funcionario_id = f.id AND p.data = ?
        WHERE f.ativo = 1
        ORDER BY f.departamento, f.nome
    """
    rows = conn.execute(_sql(sql), (data,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_presenca(data: str, funcionario_id: int,
                     presente: bool = True, observacao: str = "") -> int:
    """Registra/atualiza presença de 1 funcionário em 1 data. Idempotente."""
    conn = get_conn()
    try:
        existente = conn.execute(
            _sql("SELECT id FROM presenca_diaria "
                 "WHERE data = ? AND funcionario_id = ?"),
            (data, funcionario_id),
        ).fetchone()
        if existente:
            conn.execute(
                _sql("UPDATE presenca_diaria SET presente = ?, observacao = ? "
                     "WHERE id = ?"),
                (1 if presente else 0, observacao, existente["id"]),
            )
            id_linha = existente["id"]
        else:
            c = conn.cursor()
            if IS_POSTGRES:
                row = c.execute(
                    _sql("INSERT INTO presenca_diaria "
                         "(data, funcionario_id, presente, observacao) "
                         "VALUES (?, ?, ?, ?) RETURNING id"),
                    (data, funcionario_id, 1 if presente else 0, observacao),
                ).fetchone()
                id_linha = row["id"]
            else:
                c.execute(
                    "INSERT INTO presenca_diaria "
                    "(data, funcionario_id, presente, observacao) "
                    "VALUES (?, ?, ?, ?)",
                    (data, funcionario_id, 1 if presente else 0, observacao),
                )
                id_linha = c.lastrowid
        conn.commit()
        return id_linha
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_capacidade_efetiva_dia(data: str, atividade: str) -> dict:
    """Soma a capacidade total disponível pra uma atividade em uma data,
    considerando APENAS funcionários presentes (presente=1).

    Retorna dict:
        {atividade, total_normal, total_min, total_max,
         funcionarios_presentes: [...], funcionarios_ausentes: [...]}

    Se um funcionário com capacidade na atividade não tem registro de presença,
    é considerado AUSENTE (conservador).
    """
    conn = get_conn()
    sql = """
        SELECT c.valor_normal, c.valor_min, c.valor_max, c.unidade,
               f.id AS func_id, f.nome,
               COALESCE(p.presente, 0) AS presente
        FROM capacidades_funcionario c
        INNER JOIN funcionarios f ON f.id = c.funcionario_id
        LEFT JOIN presenca_diaria p
            ON p.funcionario_id = f.id AND p.data = ?
        WHERE c.atividade = ? AND f.ativo = 1
    """
    rows = conn.execute(_sql(sql), (data, atividade)).fetchall()
    conn.close()

    presentes = []
    ausentes = []
    total_normal = 0.0
    total_min = 0.0
    total_max = 0.0
    unidade = ""

    for r in rows:
        r = dict(r)
        if r["presente"]:
            presentes.append({"id": r["func_id"], "nome": r["nome"],
                              "valor": r["valor_normal"]})
            total_normal += float(r["valor_normal"] or 0)
            total_min += float(r["valor_min"] or 0)
            total_max += float(r["valor_max"] or 0)
            if not unidade:
                unidade = r["unidade"] or ""
        else:
            ausentes.append({"id": r["func_id"], "nome": r["nome"],
                             "valor": r["valor_normal"]})

    return {
        "atividade": atividade,
        "data": data,
        "total_normal": total_normal,
        "total_min": total_min,
        "total_max": total_max,
        "unidade": unidade,
        "funcionarios_presentes": presentes,
        "funcionarios_ausentes": ausentes,
        "n_presentes": len(presentes),
        "n_ausentes": len(ausentes),
    }


def calcular_necessidades_do_dia(data: str) -> list[dict]:
    """Cruza folha do dia × BOM × estoque atual.

    Pra cada produto da folha do dia (com ordem > 0), busca a BOM, calcula
    necessidade total de cada insumo, compara com estoque atual.

    Retorna lista de dicts:
        {insumo_id, insumo_nome, unidade, necessidade, estoque_atual,
         saldo (estoque - necessidade), status ('falta'/'ok'/'critico')}

    Versão SIMPLES desta Etapa B: trata apenas ord_prod_band da cocada e
    ord_prod_band da palha + ord_pm + ord_balas. Outros campos podem entrar
    em iterações futuras.
    """
    folha_c = get_folha_cocada(data)
    folha_p = get_folha_palha(data)
    pmbd    = get_pm_balas_doces(data) or {}

    # Acumula necessidade total por insumo
    necessidades: dict[int, dict] = {}

    def _adicionar_necessidade(produto_chave: str, qtd_produzir: float):
        """Pega a BOM do produto e soma a necessidade dos insumos."""
        if qtd_produzir <= 0:
            return
        bom = get_bom_produto(produto_chave)
        for linha in bom:
            iid = linha["insumo_id"]
            necessidades.setdefault(iid, {
                "insumo_id": iid,
                "insumo_nome": linha["insumo_nome"],
                "unidade": linha["insumo_unidade"],
                "estoque_atual": linha["estoque_atual"],
                "necessidade": 0.0,
            })
            necessidades[iid]["necessidade"] += linha["quantidade"] * qtd_produzir

    # Cocada — receita por TACHO INTEIRO. Pedidos não-múltiplos de 8 (Zero: 3)
    # cozinham um tacho parcial: ord 18 band → ceil(18/8)=3 tachos cozidos
    # (18 viram bandeja, 6 sobram pra potes). Logo, ingrediente consumido =
    # ceil(band/band_por_tacho) × receita. Usar divisão simples (band/8 = 2.25)
    # subestimava ingrediente em todo pedido não-múltiplo.
    # Ver memória project_tachos_parciais_potes + CADERNO Bloco 2.
    for r in folha_c:
        sabor = r["sabor"]
        band = r.get("ord_prod_band") or 0
        if band > 0:
            band_por_tacho = 3 if sabor == "ZERO" else 8
            tachos_cozidos = math.ceil(band / band_por_tacho)
            _adicionar_necessidade(chave_produto_cocada(sabor), tachos_cozidos)

    # Palha — receita É POR BANDEJA (1 panela = 1 bandeja), confirmado 22/05/2026
    # via CADERNO 1.A. Necessidade = receita_por_bandeja × ord_prod_band (1:1).
    for r in folha_p:
        sabor = r["sabor"]
        band = r.get("ord_prod_band") or 0
        if band > 0:
            _adicionar_necessidade(chave_produto_palha(sabor), band)

    # PM (ord_pm em bolos)
    _adicionar_necessidade("pm_bolo", pmbd.get("ord_pm") or 0)

    # Balas (ord_balas em tachos)
    _adicionar_necessidade("bala_tacho", pmbd.get("ord_balas") or 0)

    # Calcula saldo e status
    resultado = []
    for n in necessidades.values():
        saldo = n["estoque_atual"] - n["necessidade"]
        if saldo < 0:
            status = "falta"
        elif saldo < n["necessidade"] * 0.1:  # menos de 10% de folga
            status = "critico"
        else:
            status = "ok"
        n["saldo"] = saldo
        n["status"] = status
        resultado.append(n)

    # Ordena: faltas primeiro, depois críticos, depois OK
    ordem_status = {"falta": 0, "critico": 1, "ok": 2}
    resultado.sort(key=lambda x: (ordem_status[x["status"]], x["insumo_nome"]))
    return resultado


# ════════════════════════════════════════════════════════════════════════════
# ETAPA E — Auto-baixa de insumos por produção (lançada quando a folha é salva)
# ════════════════════════════════════════════════════════════════════════════
# Convenção de rastreabilidade pra movimentos automáticos gerados pelo hook:
#   origem      = 'producao_auto'
#   referencia  = f'folha_{data}'           ex: 'folha_2026-05-27'
#
# Idempotência total: rodar baixar_insumos_da_folha(d) N vezes deixa o estoque
# no mesmo estado que rodar 1 vez, porque a função SEMPRE reverte a baixa
# anterior do mesmo (origem, referencia) antes de criar a nova. Isso resolve
# também o caso "folha editada" — basta chamar de novo após salvar.
# ════════════════════════════════════════════════════════════════════════════

def _calcular_consumo_da_folha(data: str) -> tuple[list[dict], list[dict]]:
    """Versão "raw" do consumo da folha, sem comparar com estoque.

    Retorna (consumos, sem_bom):
        consumos: lista [{'insumo_id', 'insumo_nome', 'unidade', 'quantidade'}]
                  com a quantidade EXATA que vai ser baixada.
        sem_bom: lista [{'produto_chave', 'qtd_produzir'}] dos produtos da folha
                 que não têm BOM cadastrada (a Gestão produziu mas não conseguimos
                 calcular o consumo). Não bloqueia — só avisa.

    Reusa a lógica de calcular_necessidades_do_dia mas isola o "quanto baixar"
    do "compara com estoque" — separação útil pra reverter_baixa também.
    """
    folha_c = get_folha_cocada(data)
    folha_p = get_folha_palha(data)
    pmbd    = get_pm_balas_doces(data) or {}

    consumos: dict[int, dict] = {}
    sem_bom: list[dict] = []

    def _adicionar(produto_chave: str, qtd_produzir: float):
        if qtd_produzir <= 0:
            return
        bom = get_bom_produto(produto_chave)
        if not bom:
            sem_bom.append({"produto_chave": produto_chave, "qtd_produzir": qtd_produzir})
            return
        for linha in bom:
            iid = linha["insumo_id"]
            consumos.setdefault(iid, {
                "insumo_id": iid,
                "insumo_nome": linha["insumo_nome"],
                "unidade": linha["insumo_unidade"],
                "quantidade": 0.0,
            })
            consumos[iid]["quantidade"] += linha["quantidade"] * qtd_produzir

    # Cocada — receita por TACHO INTEIRO. Pedido não-múltiplo de 8 (Zero: 3)
    # cozinha tacho parcial: ord 18 band → ceil(18/8)=3 tachos. Ingrediente
    # consumido = ceil(band/band_por_tacho) × receita. Ver [[project_tachos_parciais_potes]].
    for r in folha_c:
        sabor = r["sabor"]
        band = r.get("ord_prod_band") or 0
        if band > 0:
            band_por_tacho = 3 if sabor == "ZERO" else 8
            tachos_cozidos = math.ceil(band / band_por_tacho)
            _adicionar(chave_produto_cocada(sabor), tachos_cozidos)

    # Palha — receita É POR BANDEJA (1 panela = 1 bandeja, CADERNO 1.A).
    for r in folha_p:
        sabor = r["sabor"]
        band = r.get("ord_prod_band") or 0
        if band > 0:
            _adicionar(chave_produto_palha(sabor), band)

    # PM (ord_pm em bolos), Bala (ord_balas em tachos).
    _adicionar("pm_bolo", pmbd.get("ord_pm") or 0)
    _adicionar("bala_tacho", pmbd.get("ord_balas") or 0)

    return list(consumos.values()), sem_bom


def consumo_previsto_da_folha(data: str) -> dict:
    """Calcula o consumo previsto pela folha do dia (sem aplicar baixa) e
    informa se já existe baixa anterior. Usado pela UI pra mostrar o preview
    antes da Gestão confirmar.

    Retorna:
        {
          'consumos': [{'insumo_id','insumo_nome','unidade','quantidade',
                        'estoque_atual','estoque_depois','status'}],
            (status: 'falta' se depois < 0, 'critico' se < 10% do consumo, 'ok' c.c.)
          'sem_bom': [{'produto_chave','qtd_produzir'}],
          'baixa_anterior': bool,         # True se já houve baixa pra essa data
          'movs_anteriores': int,         # quantos movimentos existem
          'data': data,
        }
    """
    consumos, sem_bom = _calcular_consumo_da_folha(data)

    # Anexa estoque atual + projeção pós-baixa pra cada consumo.
    if consumos:
        conn = get_conn()
        ids = [c["insumo_id"] for c in consumos]
        placeholders = ", ".join("?" for _ in ids)
        rows = conn.execute(
            _sql(f"SELECT id, estoque_atual FROM insumos WHERE id IN ({placeholders})"),
            tuple(ids),
        ).fetchall()
        conn.close()
        estoque_map = {r["id"]: r["estoque_atual"] for r in rows}
        for c in consumos:
            atual = estoque_map.get(c["insumo_id"], 0.0)
            depois = atual - c["quantidade"]
            c["estoque_atual"] = atual
            c["estoque_depois"] = depois
            if depois < 0:
                c["status"] = "falta"
            elif depois < c["quantidade"] * 0.1:
                c["status"] = "critico"
            else:
                c["status"] = "ok"

    # Detecta baixa anterior pra essa data.
    referencia = f"folha_{data}"
    conn = get_conn()
    row = conn.execute(
        _sql("SELECT COUNT(*) AS n FROM movimentos_insumo "
             "WHERE origem = ? AND referencia = ?"),
        ("producao_auto", referencia),
    ).fetchone()
    conn.close()
    movs_anteriores = row["n"] if row else 0

    return {
        "consumos": consumos,
        "sem_bom": sem_bom,
        "baixa_anterior": movs_anteriores > 0,
        "movs_anteriores": movs_anteriores,
        "data": data,
    }


def reverter_baixa_da_folha(data: str) -> dict:
    """Apaga movimentos auto-gerados (origem='producao_auto', referencia='folha_<data>')
    e re-soma as quantidades estornadas no estoque_atual dos insumos. Tudo numa
    transação atômica.

    Idempotente: se não houver baixa anterior pra essa data, retorna zeros sem fazer nada.

    Retorna: {'movimentos_estornados', 'quantidade_total_estornada', 'insumos_afetados'}.
    """
    referencia = f"folha_{data}"
    conn = get_conn()
    try:
        c = conn.cursor()

        # Pega os movimentos que serão estornados (precisa do delta pra repor no estoque).
        rows = c.execute(
            _sql("SELECT id, insumo_id, tipo, quantidade FROM movimentos_insumo "
                 "WHERE origem = ? AND referencia = ?"),
            ("producao_auto", referencia),
        ).fetchall()

        if not rows:
            return {
                "movimentos_estornados": 0,
                "quantidade_total_estornada": 0.0,
                "insumos_afetados": 0,
            }

        # Re-soma no estoque (estorno) e apaga os movimentos.
        # Agrupa por insumo pra fazer 1 UPDATE por insumo em vez de N.
        deltas_por_insumo: dict[int, float] = {}
        total_qtd = 0.0
        for r in rows:
            # SEMPRE foi saida (producao_auto só gera saida). Estorno = +quantidade.
            delta = r["quantidade"] if r["tipo"] == "saida" else -r["quantidade"]
            deltas_por_insumo[r["insumo_id"]] = deltas_por_insumo.get(r["insumo_id"], 0.0) + delta
            total_qtd += r["quantidade"]

        for insumo_id, delta in deltas_por_insumo.items():
            c.execute(
                _sql("UPDATE insumos SET estoque_atual = estoque_atual + ?, "
                     "atualizado_em = CURRENT_TIMESTAMP WHERE id = ?"),
                (delta, insumo_id),
            )

        c.execute(
            _sql("DELETE FROM movimentos_insumo WHERE origem = ? AND referencia = ?"),
            ("producao_auto", referencia),
        )

        conn.commit()
        return {
            "movimentos_estornados": len(rows),
            "quantidade_total_estornada": total_qtd,
            "insumos_afetados": len(deltas_por_insumo),
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def baixar_insumos_da_folha(data: str) -> dict:
    """Hook da Etapa E. Cruza folha × BOM × estoque e baixa o consumo automático
    pra cada insumo. Idempotente — reverte qualquer baixa anterior pra essa data
    antes de criar a nova (essencial pra suportar folha EDITADA).

    Não bloqueia se algum produto não tem BOM cadastrada — só lista em `sem_bom`.
    Não bloqueia se algum insumo vai ficar com estoque negativo — registra e
    lista em `alertas_negativos` pra UI mostrar. Decisão de pausar a baixa é
    do humano (Gestão), não do sistema.

    Tudo em transação atômica: se qualquer INSERT/UPDATE falhar, rollback total
    e levanta exceção.

    Retorna: dict com
        - 'data': str (ecoada)
        - 'estornados': int (quantos movs da baixa anterior foram apagados)
        - 'movimentos': [{'insumo_id','insumo_nome','unidade','quantidade',
                          'estoque_antes','estoque_depois'}]
        - 'sem_bom': [{'produto_chave','qtd_produzir'}] (produtos sem receita)
        - 'alertas_negativos': [insumo_id, ...] (insumos cujo estoque ficou <0)
    """
    referencia = f"folha_{data}"

    # 1) Estorno (transação própria, deixa o banco consistente antes da nova baixa).
    estorno = reverter_baixa_da_folha(data)

    # 2) Calcula consumo da folha atual.
    consumos, sem_bom = _calcular_consumo_da_folha(data)

    # Sem consumos pra baixar — só retorna info do estorno (folha pode ter ord_prod=0).
    if not consumos:
        return {
            "data": data,
            "estornados": estorno["movimentos_estornados"],
            "movimentos": [],
            "sem_bom": sem_bom,
            "alertas_negativos": [],
        }

    # 3) Registra movimentos saida + atualiza estoque, tudo em UMA transação.
    movimentos_resultado: list[dict] = []
    alertas_negativos: list[int] = []

    conn = get_conn()
    try:
        c = conn.cursor()

        # Pega estoque atual de todos os insumos envolvidos numa só query.
        ids_envolvidos = [c_["insumo_id"] for c_ in consumos]
        placeholders = ", ".join("?" for _ in ids_envolvidos)
        rows = c.execute(
            _sql(f"SELECT id, estoque_atual FROM insumos WHERE id IN ({placeholders})"),
            tuple(ids_envolvidos),
        ).fetchall()
        estoque_antes = {r["id"]: r["estoque_atual"] for r in rows}

        for consumo in consumos:
            iid = consumo["insumo_id"]
            qtd = consumo["quantidade"]

            # Insere movimento saida.
            c.execute(
                _sql("INSERT INTO movimentos_insumo "
                     "(data, insumo_id, tipo, quantidade, origem, referencia, obs) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?)"),
                (data, iid, "saida", qtd, "producao_auto", referencia,
                 "Baixa automática (folha salva)"),
            )
            # Decrementa estoque.
            c.execute(
                _sql("UPDATE insumos SET estoque_atual = estoque_atual - ?, "
                     "atualizado_em = CURRENT_TIMESTAMP WHERE id = ?"),
                (qtd, iid),
            )

            antes = estoque_antes.get(iid, 0.0)
            depois = antes - qtd
            if depois < 0:
                alertas_negativos.append(iid)

            movimentos_resultado.append({
                "insumo_id": iid,
                "insumo_nome": consumo["insumo_nome"],
                "unidade": consumo["unidade"],
                "quantidade": qtd,
                "estoque_antes": antes,
                "estoque_depois": depois,
            })

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {
        "data": data,
        "estornados": estorno["movimentos_estornados"],
        "movimentos": movimentos_resultado,
        "sem_bom": sem_bom,
        "alertas_negativos": alertas_negativos,
    }


# ════════════════════════════════════════════════════════════════════════════
# EVENTOS / OBSERVAÇÕES DA SEMANA (gap 2 da Camada 2 cocada — CADERNO 1.B)
# Captura livre de contexto que a Gestão conhece mas o sistema não deriva da
# folha. Leitura humana; futuramente entra como contexto pro assistente IA.
# ════════════════════════════════════════════════════════════════════════════
def criar_evento_semana(data: str, descricao: str, tipo: str = "observacao") -> int:
    """Registra um evento/observação. Retorna o id criado.
    `data` = dia que o evento afeta (YYYY-MM-DD). `descricao` obrigatória."""
    if not descricao or not descricao.strip():
        raise ValueError("Descrição do evento não pode ser vazia.")
    descricao = descricao.strip()
    if tipo not in TIPOS_EVENTO:
        tipo = "observacao"

    conn = get_conn()
    try:
        c = conn.cursor()
        if IS_POSTGRES:
            row = c.execute(
                _sql("INSERT INTO eventos_semana (data, tipo, descricao) "
                     "VALUES (?, ?, ?) RETURNING id"),
                (data, tipo, descricao),
            ).fetchone()
            new_id = row["id"]
        else:
            c.execute(
                "INSERT INTO eventos_semana (data, tipo, descricao) VALUES (?, ?, ?)",
                (data, tipo, descricao),
            )
            new_id = c.lastrowid
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_eventos_periodo(data_inicio: str, data_fim: str) -> list[dict]:
    """Eventos com data no intervalo [data_inicio, data_fim], ordenados por data.
    Genérico — qualquer página (cocada, palha, home) pode consumir."""
    conn = get_conn()
    rows = conn.execute(
        _sql("SELECT id, data, tipo, descricao, criado_em FROM eventos_semana "
             "WHERE data >= ? AND data <= ? ORDER BY data, id"),
        (data_inicio, data_fim),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def excluir_evento_semana(evento_id: int):
    """Remove um evento por id."""
    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute(_sql("DELETE FROM eventos_semana WHERE id = ?"), (evento_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
