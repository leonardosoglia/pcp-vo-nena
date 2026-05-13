# Handoff — Sessão 12-13/05/2026

Eu sou Leonardo Sóglia, estagiário na Doces Vó Nena, desenvolvendo o
**PCP Vó Nena** (Streamlit + Postgres) como projeto de estágio e TCC.

Esta sessão concluiu a **Etapa 4 (migração SQLite → Postgres + deploy
na nuvem)**. O app está no ar em produção, mas tem um erro pendente
de diagnóstico. A próxima sessão começa daqui.

**Antes de tudo**, lê o `CLAUDE.md` na íntegra — ele tem o contexto
de negócio, decisões arquiteturais consolidadas, regras de cocada/palha/
PM, pessoas, e o estado atual atualizado. Este arquivo é só o relato
da sessão pra você entender o caminho que percorremos.

---

## 1. O que foi feito nesta sessão (12-13/05)

### 1.1 Supabase configurado do zero
- Conta criada com GitHub OAuth (`bandroid289@gmail.com`).
- Organização `doces-vo-nena`, projeto `pcp-vo-nena`, região São Paulo (`sa-east-1`).
- Postgres 17.6, free tier, compute NANO.
- Senha do banco gerada via gerador automático do Supabase (sem chars especiais → sem URL-encoding).
- Senha guardada em `OneDrive/_secrets/supabase_pcp.txt` (Leonardo planeja migrar pra Bitwarden).
- URL do pooler transaction (porta 6543) salva em `.streamlit/secrets.toml` local.

### 1.2 Smoke test de conexão validado
- Script standalone (`smoke_test_conexao.py`, depois apagado) conectou no Supabase, rodou `SELECT 1` e confirmou Postgres 17.6 + sa-east-1 + pooler.

### 1.3 Bootstrap `st.secrets → os.environ` aplicado
- 6 linhas inseridas no topo de `lancamento.py` (entre linha 20 e 22) e `painel.py` (entre linha 9 e 10).
- Padrão: `if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets: os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]`.
- Preserva env var explícita (útil pra scripts CLI como `migrar_dados_sqlite_para_postgres.py`).

### 1.4 Schema criado no Supabase
- `python -c "import database; database.init_db()"` com `DATABASE_URL` setada via PowerShell.
- 10 tabelas criadas: 4 de folha (vazias inicialmente) + 6 de referência (populadas pelo `_seed_referencias`).

### 1.5 Migração SQLite → Postgres
- Backup pré-migração: `pcp_vo_nena.db.bak.20260512_161629` (136 KB, mantido).
- Dry-run identificou 13 datas (2026-04-02 → 2026-05-12).
- **1ª tentativa de migração real FALHOU** com `psycopg.errors.DuplicatePreparedStatement: prepared statement "_pg3_0" already exists`.
- **Causa:** PgBouncer transaction mode multiplexa transações em conexões backend; psycopg 3 nomeia prepared statements de forma determinística e colide ao reutilizar uma conexão backend.
- **Correção:** adicionado `prepare_threshold=None` em `database.py:get_conn()` no `psycopg.connect(...)`. 1 linha + comentário explicativo.
- **2ª tentativa OK:** 13 folhas migradas, paridade confirmada: `folha_cocada=78`, `folha_palha=65`, `papelzinho_joel=54`, `folha_pm_balas_doces=13`.
- **Tabela `estoque` NÃO foi migrada** — o script só toca as 4 tabelas de folha. Tem 25 linhas no Postgres (do seed) mas o SQLite local pode ter dados adicionais de contagens diárias. Verificar na próxima sessão.

### 1.6 Validação local
- `python -m streamlit run lancamento.py --server.port=8502` em background, health endpoint HTTP 200.
- Script ad-hoc validou stack `database.py → Postgres`: leu 13 datas, calculou derivados, retornou metas e conversões. Stack 100% funcional contra Postgres.

### 1.7 Git + GitHub
- `git init` + commit inicial `1b29f03` ("Estado inicial: dual-backend SQLite/Postgres pronto pra deploy").
- 16 arquivos comitados, 4826 linhas. Repositório criado em `github.com/leonardosoglia/pcp-vo-nena` (privado).
- `.gitignore` expandido pra cobrir `historico_sessoes/`, `.claude/`, `_tmp_*.py`, `smoke_test_*.py`, `_streamlit_*.txt`.
- Push HTTPS bem sucedido (Credential Manager Windows já tinha auth cacheada).
- Arquivo zumbi `.streamlit/smoke_test_conexao.py` (0 bytes, criado por um Out-File em path errado em sessão anterior) removido.

### 1.8 Deploy no Streamlit Community Cloud (saga longa)
- Vários travas até funcionar:
  - Streamlit não enxergava o repo privado `pcp-vo-nena` no dropdown — só listava `painel-vonena` e `2025.2-IAD-LEONARDO`.
  - Tentamos: revogar e reautorizar OAuth (2 entradas "Streamlit" e "Streamlit Community Cloud" em `github.com/settings/applications`), instalar GitHub App (404 — Streamlit não usa GitHub App tradicional), trocar de browser (Opera → Chrome, descartou hipótese de VPN), aguardar sync.
  - **Solução que funcionou:** tornar o repo **público temporariamente** no GitHub (Settings → Danger Zone → Change visibility → Make public). O Streamlit conseguiu clonar e deployar.
  - **Leonardo deve voltar o repo pra privado depois** (mesmo caminho, Make private). Streamlit Cloud continua servindo o app mesmo após a mudança.
- Configuração do app: Python 3.14, secrets coladas no Advanced settings (DATABASE_URL via TOML), Main file `lancamento.py`, App URL `pcp-vo-nena`.
- App público: **`https://pcp-vo-nena.streamlit.app`**.

### 1.9 Erro de runtime visível no app deployado
- App carrega, mostra a UI, lê dados do Postgres, mas em algum momento explode com:
  ```
  psycopg.errors.InternalError_: This app has encountered an error...
  File "/mount/src/pcp-vo-nena/lancamento.py", line 688, in <module>
      metas_dia = {r["sabor"]: r for r in get_metas_45g()}
  File "/mount/src/pcp-vo-nena/database.py", line 527, in get_metas_45g
      rows = conn.execute("SELECT * FROM metas_45g").fetchall()
  ```
- Mensagem real foi "redacted" pelo Streamlit Cloud — precisa do log completo via botão "Manage app" (canto inferior direito do app) pra ver o erro real.
- **Hipóteses:**
  - (a) Janela de manutenção do pooler Supabase em `sa-east-1` — banner do dashboard anunciou "Shared pooler maintenance May 13-14". Hoje é 13/05.
  - (b) Outro padrão de prepared statement não coberto por `prepare_threshold=None`.
  - (c) Algo específico do `get_metas_45g` (talvez query simples sem WHERE clause aciona algum caminho diferente no psycopg).
- **Leonardo concordou em ignorar o erro por enquanto** e abordar na próxima sessão.

---

## 2. Decisões tomadas nesta sessão (vão pro TCC)

1. **Pooler transaction (porta 6543) + `prepare_threshold=None`** em vez de session pooler (5432). Preserva a Decisão Arquitetural original do projeto. Justificativa: prepared statements colidem com PgBouncer transaction mode porque o pooler não rastreia state per-conexão backend; desabilitar prepared statements no psycopg evita a colisão sem custo perceptível pra workload de baixa frequência do PCP.
2. **`historico_sessoes/` gitignorado** — transcrições podem ter conteúdo sensível, repo é privado mas precaução faz sentido.
3. **`painel_claude.py` e `Painel_Fabrica.py` (vazio) mantidos no commit** — versões legadas, Leonardo decidirá se remove em commits futuros.
4. **Repo no GitHub privado** (mesmo Streamlit Community Cloud aceitar privado) — proteger decisões arquiteturais em validação até depois da defesa do TCC (~07/2026), depois tornar público pra portfólio.

---

## 3. Estado do app em produção (13/05/2026)

| Item | Status |
|------|--------|
| Supabase | ✅ Healthy, 13 folhas migradas, paridade total com SQLite local |
| GitHub | ✅ Repo `pcp-vo-nena` (privado), commit `1b29f03` |
| Streamlit Cloud | ⚠️ App no ar (`pcp-vo-nena.streamlit.app`) mas com erro psycopg pendente |
| App local (8501, 8502) | ✅ Funcional (usa SQLite por default se `DATABASE_URL` não setado) |
| Backup SQLite | ✅ `pcp_vo_nena.db.bak.20260512_161629` |
| 2 apps antigos `painel-vonena` | ⚠️ Ainda no dashboard Streamlit Cloud, ocupam slots, Leonardo vai deletar |

---

## 4. Pendências imediatas (próxima sessão começa por aqui)

### Bloqueador
1. **Diagnosticar `psycopg.InternalError_`** no app em produção:
   - Pedir Leonardo abrir `pcp-vo-nena.streamlit.app`, clicar "Manage app" (canto inferior direito), capturar o log completo.
   - Se for manutenção do pooler (janela 13-14/05), basta esperar passar e validar de novo.
   - Se for outro padrão de prepared statement, ajustar `database.py` (talvez explicit `PREPARE`/`DEALLOCATE` ou `cursor.execute(query, prepare=False)` em queries específicas).

### Limpeza
2. Apagar os 2 apps antigos `painel-vonena · painel_claude.py` e `painel-vonena · painel.py` no dashboard Streamlit Cloud (3 pontinhos → Delete app).
3. Voltar o repo `pcp-vo-nena` pra **privado** no GitHub (foi tornado público temporariamente pra desbloquear o deploy).

### Validação com fábrica
4. Mandar link `pcp-vo-nena.streamlit.app` pro Eraldo testar — só depois do erro psycopg resolvido. Pedir feedback de UX e regras de negócio.

### Decisão arquitetural pendente
5. **`painel.py` no Streamlit Cloud:** dois caminhos:
   - (a) Subir como segundo app (`painel-pcp-vo-nena.streamlit.app`), Streamlit Cloud free permite 3 apps.
   - (b) Consolidar `lancamento` + `painel` em estrutura multi-página (`pages/`), 1 app só, navegação por sidebar. Refactor ~30min.
   - Decisão depende de feedback do Eraldo sobre UX.

### Migração faltante
6. **Estoque:** o script de migração só copiou as 4 tabelas de folha. `estoque` no Postgres tem 25 linhas do seed inicial. Verificar se o SQLite local tem contagens diárias adicionais que precisam ir pra produção. Se sim, criar script complementar (pode reaproveitar padrão do `migrar_dados_sqlite_para_postgres.py`).

### Performance
7. Adicionar `@st.cache_data(ttl=60)` nas funções de leitura (`get_folha_cocada`, `get_papelzinho_joel`, `get_metas_45g`, `get_conversoes`, etc.). Reduz latência percebida no app em produção (~20-50ms por query × ~10-15 queries por folha = lento ao navegar entre datas).

---

## 5. Roadmap até a defesa

| Quando | O quê |
|--------|-------|
| **Próxima sessão** | Resolver psycopg, limpar apps antigos, voltar repo pra privado |
| **Esta semana** | Mostrar pro Eraldo, ajustar conforme feedback |
| **22-29/05/2026** | Etapa 5: polimento visual, KPIs comparativos, exportação PDF |
| **05/06/2026** | Início da escrita do TCC |
| **~18/07/2026** | Defesa |

---

## 6. Como me ajudar bem (lembrete pra próxima sessão)

- **Linguagem:** Leonardo é leigo em programação. Evitar jargão técnico ou explicar quando usar. Não usar "backend", "pooler", "OAuth", "deploy" etc. sem explicação curta.
- **Postura:** especialista técnico em PCP + software, mas didático. Defender decisões com argumentos (vai pro TCC).
- **Tom:** informal, PT-BR, direto. Sem sumário do que acabou de fazer no final da resposta.
- **Antes de programar:** identificar inconsistências com o fluxo real da fábrica.
- **Unidades explícitas:** und · bandejas · tachos — nunca misturar.
- **Pausar e perguntar:** Leonardo se cansa de copiar/colar comandos. Quando ele delegar autonomia, executar e parar SÓ se der erro real ou precisar de decisão. Mas quando ele pedir pra ir devagar, ir devagar de verdade.
