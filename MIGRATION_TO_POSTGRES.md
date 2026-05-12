# Migração SQLite → Postgres (Supabase)

Documento técnico de referência para a Etapa 4 do TCC.
Versão: 1 · Base: `database.py` v2 (atual).

---

## 1. Decisão arquitetural

**Dual-backend via `DATABASE_URL`.** O mesmo código suporta SQLite (dev local, PC do Leonardo) e Postgres (Supabase, prod). A escolha é runtime, baseada em variável de ambiente.

```
DATABASE_URL não definida ou começa com "sqlite://"  → SQLite local (pcp_vo_nena.db)
DATABASE_URL começa com "postgres://" ou "postgresql://"  → Postgres (Supabase)
```

**Por que dual e não migração total para Postgres:**
- Dev local sem internet continua funcionando (importante: Leonardo pode codar de casa).
- Backup do SQLite local serve como cópia paralela do Postgres (defesa em profundidade).
- Streamlit Cloud sempre lê via `DATABASE_URL` em secrets, sem ambiguidade.

**Trade-off aceito:** uma fina camada de adaptação (wrapper de conexão + tradução `?` ↔ `%s`). Custa ~80 linhas; evita reescrever todo `database.py`.

**Alternativa descartada — SQLAlchemy Core:** abstrairia o dialeto, mas obrigaria reescrita completa de `database.py` e introduziria ORM-like overhead. Over-engineering para o tamanho atual do projeto (~700 linhas).

---

## 2. Mapa de diferenças (SQLite → Postgres)

### 2.1. Tipos de dados (CREATE TABLE)

| SQLite (atual) | Postgres (alvo) | Observação |
|---|---|---|
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY` | SQL-standard (PG 10+). Alternativa legacy: `SERIAL PRIMARY KEY`. |
| `TEXT` | `TEXT` | Idêntico. |
| `INTEGER DEFAULT 0` | `INTEGER DEFAULT 0` | Idêntico. |
| `data TEXT NOT NULL` (datas como string `'2026-05-11'`) | `data TEXT NOT NULL` | **Manter TEXT na migração inicial.** Refatorar para `DATE` é trabalho separado, fora de escopo da Etapa 4. |
| `UNIQUE(data, sabor)` | `UNIQUE(data, sabor)` | Idêntico. |

### 2.2. Placeholders de query

| SQLite | Postgres (psycopg) |
|---|---|
| `?` posicional | `%s` posicional (sempre `%s`, mesmo para int/text) |

**Impacto no código atual:** todas as ~30 chamadas `c.execute("... ?", params)` precisam virar `%s` quando rodando em Postgres. Estratégia: wrapper que faz `sql.replace("?", "%s")` antes de executar.

**Cuidado:** se algum SQL tiver `?` literal dentro de string (ex.: `LIKE '?abc'`), o replace quebra. Auditei `database.py` — **não há ocorrências**, todos os `?` são placeholders.

### 2.3. UPSERT

| SQLite | Postgres |
|---|---|
| `INSERT ... ON CONFLICT(col) DO UPDATE SET col=excluded.col` | **Idêntico.** Sintaxe PG ≥ 9.5 é a mesma. |

**Boa notícia:** zero mudanças nas funções `_upsert_por_sabor`, `salvar_folha_completa`, `upsert_pm_balas_doces`.

### 2.4. Introspecção de schema (migrações suaves)

`database.py` faz várias migrações suaves do tipo "se a coluna X não existe, ADD COLUMN" usando `PRAGMA table_info`. Postgres não tem PRAGMA.

| SQLite (atual) | Postgres (alvo) |
|---|---|
| `PRAGMA table_info(tabela)` | `SELECT column_name FROM information_schema.columns WHERE table_name='tabela'` |
| `ALTER TABLE t ADD COLUMN x INTEGER DEFAULT 0` (após check manual) | `ALTER TABLE t ADD COLUMN IF NOT EXISTS x INTEGER DEFAULT 0` (PG ≥ 9.6 — atômico, sem check) |

**Simplificação possível:** em Postgres podemos usar `ADD COLUMN IF NOT EXISTS` direto, eliminando o check manual. Em SQLite, **não** existe `IF NOT EXISTS` em `ADD COLUMN` (até versão 3.35; SQLite 3.35+ tem mas distribuições antigas não), então mantemos o check.

Solução pragmática: função helper `_add_column_if_missing(c, tabela, coluna, tipo)` que internamente faz o método correto para cada backend.

### 2.5. Cursor / row factory

| SQLite | Postgres (psycopg 3 — recomendado) | Postgres (psycopg2 — legacy) |
|---|---|---|
| `conn.row_factory = sqlite3.Row` | `conn = psycopg.connect(url, row_factory=dict_row)` | `cur = conn.cursor(cursor_factory=RealDictCursor)` |

Acesso por chave (`row["data"]`, `row["sabor"]`) funciona em todos os três. Código atual **não precisa mudar**, só o setup da conexão.

**Recomendação:** **psycopg 3** (`pip install psycopg[binary]`). Razões:
- Mantido ativamente, sucessor do psycopg2.
- `row_factory` na conexão é mais limpo (afeta todos os cursors automaticamente).
- Suporte nativo a async (irrelevante agora, útil futuro).

### 2.6. Backup do banco

| SQLite (atual) | Postgres (alvo) |
|---|---|
| `shutil.copy2(DB_PATH, bak)` (`_backup_db`) | Não aplicável: Supabase faz backup automático. Para backup manual: `pg_dump` via CLI. |

**Decisão:** caminho de migração v1→v2 (`_migrate_v1_to_v2` + `_backup_db`) só roda em SQLite. Em Postgres começamos clean: schema v2 puro, sem código de migração v1. Razão: nunca houve banco v1 em Postgres.

### 2.7. Conexão

| SQLite | Postgres |
|---|---|
| `sqlite3.connect(DB_PATH)` (arquivo local) | `psycopg.connect(DATABASE_URL)` (rede + auth) |
| Latência: μs (arquivo local) | Latência: 50-200 ms (rede para Supabase) |

**Implicação:** abrir/fechar conexão em toda chamada (padrão atual: `conn = get_conn(); ...; conn.close()`) é **OK em SQLite, ruim em Postgres** com Supabase. Cada `get_conn()` paga TCP+TLS handshake.

**Soluções (em ordem de simplicidade):**
1. **`psycopg.connect` com pool**: usar `psycopg_pool.ConnectionPool` (pool de 2-5 conexões reaproveitadas). Mínimo de mudança no código.
2. **Manter conexão global**: arriscado em ambiente multi-thread; Streamlit faz threads sob o capô.
3. **Supabase pooler (PgBouncer)**: a própria Supabase oferece pooler em porta separada (`...?pgbouncer=true`). **Recomendado.** É o caminho oficial para apps stateless como Streamlit.

**Recomendação:** usar URL do **pooler do Supabase** + manter o padrão atual de abrir/fechar conexão. Pooler resolve a latência sem mudar código.

---

## 3. Estratégia de implementação

### 3.1. Topologia do código alvo

```
database.py
├── get_conn()              ← decide backend pela DATABASE_URL
├── _is_postgres()          ← helper
├── _placeholder()          ← retorna '?' ou '%s'
├── _add_column_if_missing  ← compatível com ambos
├── init_db()               ← roda DDL apropriado
│   ├── em SQLite: caminho v1→v2 + ensure_v2 + seeds
│   └── em Postgres: ensure_v2 + seeds (sem v1)
├── _ensure_v2_schema(c)    ← DDL parametrizada pelo backend
└── (resto inalterado, exceto strings com '?')
```

### 3.2. Padrão de execução

Helper único `execute(c, sql, params)` que:
1. Detecta backend via flag global.
2. Se Postgres, faz `sql.replace("?", "%s")`.
3. Chama `c.execute(sql, params)`.

Tudo no `database.py` passa por esse helper. ~30 chamadas atualizadas.

### 3.3. Variável de ambiente e secrets

| Onde | Como |
|---|---|
| Dev local | `DATABASE_URL` não definida → SQLite local. Sem mudança no fluxo atual. |
| Streamlit Cloud | Adicionar em **Settings → Secrets** (TOML): `DATABASE_URL = "postgresql://..."` |
| Acesso via código | `os.environ.get("DATABASE_URL", "")` |

⚠️ **Nunca commitar `DATABASE_URL` no Git.** Adicionar `.streamlit/secrets.toml` ao `.gitignore`.

---

## 4. Checklist de execução

Em ordem dependencial:

- [x] **1.** `requirements.txt` adicionar `psycopg[binary]>=3.2,<4.0` e `psycopg-pool>=3.2,<4.0`. ✅ feito sessão 2 (12/05/2026).
- [ ] **2.** Criar projeto no Supabase (Leonardo). **← bloqueador atual**
- [ ] **3.** Copiar URL do **pooler** (porta 6543) — não a URL direta (porta 5432).
- [ ] **4.** Adicionar `DATABASE_URL` no `.streamlit/secrets.toml` local + `.gitignore` (template já em `.streamlit/secrets.toml.example`).
- [x] **5.** Refatorar `database.py`: ✅ feito 12/05/2026.
  - [x] Helpers `_sql()`, `_table_columns()`, `_id_pk()` adicionados.
  - [x] `get_conn()` bifurcado por `IS_POSTGRES` (import lazy do psycopg).
  - [x] DDL parametrizada (`INTEGER PRIMARY KEY AUTOINCREMENT` ↔ `INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY`).
  - [x] Todas as chamadas com `?` placeholder roteadas por `_sql()` (~30 ocorrências).
  - [x] `PRAGMA table_info` substituído por `_table_columns()` (usa `information_schema` em PG).
  - [x] `ORDER BY rowid` → `ORDER BY id` (PG não tem rowid).
  - [x] Subquery `FROM (UNION …)` ganhou alias `AS u` (exigência PG; SQLite ignora).
  - [x] `SELECT COUNT(*)` → `SELECT COUNT(*) AS n` + `.fetchone()["n"]` (psycopg `dict_row` não aceita índice posicional).
  - [x] Migração v1→v2 e `_backup_db()` gated por `not IS_POSTGRES` (PG nunca teve v1).
  - [x] Smoke test SQLite: `init_db()` + `list_datas_folha()` + `calcular_cortados()` + `calcular_viradas_pvirar()` — todos OK.
- [ ] **6.** Adicionar bootstrap em `lancamento.py` e `painel.py` para Streamlit Cloud ler `DATABASE_URL` de `st.secrets` e expor como env var (Streamlit Cloud NÃO expõe secrets como env vars automaticamente):
    ```python
    import os
    import streamlit as st
    if "DATABASE_URL" in st.secrets and not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
    import database as db
    ```
    Deixar para fazer depois que Leonardo terminar o input do 12/05 (evita hot-reload no meio).
- [ ] **7.** Testar `init_db()` apontando para Postgres vazio (cria schema + seeds).
- [x] **8.** Script `migrar_dados_sqlite_para_postgres.py` criado (sessão 2). ✅
  - [x] Lê todas as tabelas do `pcp_vo_nena.db`.
  - [x] Insere em Postgres via `salvar_folha_completa` para cada data.
  - [x] Verifica contagem por tabela antes/depois.
  - [x] `contar()` corrigido para acesso por chave (`["n"]` em vez de `[0]`) — compatível com dict_row do psycopg.
- [ ] **9.** Rodar migração contra Postgres de **teste** primeiro.
- [ ] **10.** Validar abrindo `lancamento.py` apontando para Postgres — checar 12 folhas (estado atual em 12/05/2026).
- [ ] **11.** Configurar Streamlit Cloud (repo Git + secrets).
- [ ] **12.** Deploy + smoke test.

---

## 5. Riscos e mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Latência Supabase deixa UI lenta | Média | Médio | Usar pooler. Se persistir, agrupar reads em menos queries. |
| `?` literal dentro de string SQL quebra com replace | Baixa | Alto | Auditei — não existe. Adicionar teste de regressão. |
| Encoding (acentos: `CAFÉ`, `LIMÃO`) | Baixa | Médio | Postgres é UTF-8 nativo. SQLite atual já está UTF-8. Verificar `client_encoding=UTF8`. |
| Auto-increment IDs diferem entre SQLite e Postgres na migração | Baixa | Baixo | IDs internos não são referenciados externamente. Aceitar renumeração. |
| Free tier Supabase (500 MB) acaba | Baixa | Médio | 11 folhas ocupam ~136 KB. Margem para ~30 mil folhas. Sem risco em horizonte do TCC. |
| Free tier Streamlit Cloud (1 GB RAM) trava com cache de plotly | Média | Médio | Limitar `@st.cache_data` com TTL curto. |
| Secret vaza no Git | Média | **Alto** | `.gitignore` + revisar `git status` antes de cada commit. Se vazar: revogar URL no Supabase imediatamente. |

---

## 6. O que NÃO está no escopo desta migração

- Refatorar `data TEXT` → `DATE` (refactor separado, baixa prioridade).
- Adicionar índices além das constraints UNIQUE existentes (otimizar quando houver lentidão real).
- Mudar `cnt_doces_displays` e outros campos legados (decisão de UX, não de migração).
- Implementar autenticação multi-usuário (será adicionada como camada Streamlit Auth depois do deploy básico).

---

## 7. Próximos passos imediatos (após este doc)

**Atualizado em 12/05/2026 — após refatoração de `database.py`.**

1. ~~`requirements.txt` com `psycopg`~~ → feito.
2. ~~Refatorar `database.py` em branch separado~~ → feito direto no main (refatoração hot-reload-safe: sem `DATABASE_URL`, comportamento idêntico ao SQLite atual; smoke testado).
3. **Leonardo cria projeto Supabase** + copia URL do pooler (porta 6543). Não compartilhar no chat — colar em `.streamlit/secrets.toml` local.
4. Bootstrap de `lancamento.py` / `painel.py` para Streamlit Cloud (ver passo 6 da checklist). Deixar para depois do input do 12/05.
5. Testar `init_db()` apontando para Postgres vazio (`$env:DATABASE_URL = "postgresql://..."; python -c "import database; database.init_db()"`).
6. Rodar `migrar_dados_sqlite_para_postgres.py --dry-run` e depois sem `--dry-run`.
7. Configurar Streamlit Cloud + deploy.

**Estimativa restante:** 1 sessão de 1-2 h para teste + deploy. Pré-requisito: projeto Supabase criado (~30 min de Leonardo).

---

## 8. Estado da refatoração (12/05/2026)

### O que está pronto
- `database.py` é dual-backend; backend escolhido em `import` time via `DATABASE_URL`.
- `migrar_dados_sqlite_para_postgres.py` pronto para rodar (depende de Supabase + env var).
- `requirements.txt`, `.gitignore`, `.streamlit/secrets.toml.example` configurados.

### O que falta
- Bootstrap em `lancamento.py` / `painel.py` (3 linhas no topo cada).
- Projeto Supabase criado + URL do pooler.
- Testes contra Postgres real (init_db, salvar/ler folha, migração das 12 folhas).
- Repo Git + Streamlit Cloud + secrets.

### Comprovação de não-regressão SQLite
Smoke test rodado em 12/05/2026 com `DATABASE_URL` vazia:

```
IS_POSTGRES = False
Total folhas: 12
calcular_cortados: 6 sabores
calcular_viradas_pvirar: 6 sabores
pm_balas_doces: cnt_pm=22, bala_cortadas=220
```

Caminho SQLite preserva 100% do comportamento anterior. Hot-reload do Streamlit pegando o novo `database.py` é seguro.
