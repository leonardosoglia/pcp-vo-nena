# CLAUDE.md — PCP Vó Nena

## 1. Identidade e contexto

**Projeto:** Dashboard de PCP — Doces Vó Nena (confeitaria industrial, São Paulo-SP).
**Dev:** Leonardo Sóglia, graduando em Eng. de Produção UFCG (Campina Grande-PB), residindo em SP para estágio + TCC simultâneos.
**Objetivo TCC:** substituir folhas de papel do chão de fábrica por sistema digital com visualização, alertas e futura sugestão automática de corte.
**Defesa prevista:** ~18/07/2026 (aprox.). Escrita do TCC começa 05/06/2026 (aprox.).

---

## 2. Stack técnico

- **App:** Python 3.14 + Streamlit (multi-page, entry `lancamento.py` + `pages/1_Painel.py`).
- **Dados:** pandas + Supabase Postgres em produção · SQLite local (`pcp_vo_nena.db`) em dev (fallback automático sem `DATABASE_URL`).
- **Driver PG:** psycopg 3 (`psycopg[binary]>=3.2`) + URL do pooler Supabase (porta **6543**, não 5432).
- **Deploy alvo:** Streamlit Community Cloud (free) + Supabase free tier (500 MB, ~30 k folhas de margem).
- **Cache:** `@st.cache_data` via `cached_db.py` (TTL 60s folhas, 1h refs). Invalidação manual após save/delete.
- **Extras:** openpyxl (xlsx), plotly (viz), python-docx (relatórios TCC).

Subir local (um único app multi-page; o Painel aparece no sidebar):
```powershell
streamlit run lancamento.py --server.port=8502
```

---

## 3. Arquivos principais

| Arquivo | Função |
|---------|--------|
| `database.py` | Schema v2, dual-backend SQLite/PG, toda lógica de dados — **puro, sem Streamlit** |
| `cached_db.py` | Wrappers `@st.cache_data` sobre `database.py` + `invalidar_folha()`. Tudo que é UI importa daqui |
| `lancamento.py` | Entry point Streamlit: formulário diário da folha (multi-page) |
| `pages/1_Painel.py` | Página Painel: abas Eraldo · Joel · Gil · Leonília · Estoque · Análise |
| `analise.py` | KPIs, heatmaps, anomalias — importada pela aba Análise |
| `exportar.py` | Gera XLSX por folha (chamado pelo menu ⋮) |
| `inserir_historico.py` | Script one-shot de inserção em massa (já rodou) |
| `migrar_dados_sqlite_para_postgres.py` | ETL idempotente SQLite → Supabase (pré-requisito: `DATABASE_URL`) — importa só `database.py`, sem Streamlit |
| `MIGRATION_TO_POSTGRES.md` | Checklist técnico da Etapa 4 (atualizado em 12/05) |

Dados físicos em `folhas-semanais/` (organizado por `YYYY-MM_mês/semana_DD-DD_MM_a_DD-DD_MM_YYYY/`).

---

## 4. Regras de negócio essenciais

### Produtos e tamanhos
- **Cocada:** T, L, B, C, P, Z — em 45g, Mini (30g/27g p/ Z), Pet, Potes 260g/605g. **Zero não tem 45g.**
- **Palha:** T, L, CH, CK, LIM — 50g (só T/L/CH) e Pet 160g (todos os 5).
- **PM (Pão de Mel):** 1 bolo = 70 und. Campo "Amanhã" na folha = PM apenas.
- **Bala DL:** `ord_balas` em TACHOS (1 tacho = 30 balas).

### Conversões-chave
- 1 tacho cocada = 8 band (Z = 3) · band 45g = 100 und · Mini = 150 · Pet = 30 · Pet-Z = 60 · ≈ 7 kg/band
- **`joel_pet` = BANDEJAS** (diferente das outras colunas do papelzinho que são unidades) → converte × 30 (× 60 p/ Z) em `calcular_cortados()`.
- 1 display palha 50g = 10 palhas (4T + 4L + 2CH).

### Lead times
- Cocada: **3 dias** (tacho → virar → virada → corte). Potes: **1 dia**. Palha: **3 dias**.

### Calendário de corte (Eraldo)
- Seg/Qua/Qui → 45g · Ter/Sex → Mini + Pet (juntos).

### Parâmetros base 45g (und/dia — ajustável pelo Eraldo)
| Sabor | Seg | Ter | Qua | Qui | Sex |
|-------|-----|-----|-----|-----|-----|
| T | 5200 | 4400 | 5200 | 6800 | 5600 |
| L | 2600 | 2200 | 2600 | 3400 | 2800 |
| B/C/P | 1300 | 1100 | 1300 | 1700 | 1400 |

Mini fixo: T=L=500, B/C/P=300, **Z Mini = L45g do dia** (dinâmico). Pet fixo: T=220, L=180, B/C/P=90, Z=300. P/Virar ideal (band): T=70, L=35, B/C/P=22, Z=18.

### Cronologia do dia
7h equipe inicia · 7h–10h Leonardo conta estoque · ~10h folha pronta · Eraldo define ordens.
**Cortados① às 9h já inclui o que Gil cortou desde 7h** — não é snapshot do início do dia.

### Embalagem (2 etapas)
1. Popô: plástico individual. 2. Leonília: cinta de papel (~3000 und/dia, prioridade 45g > Mini).

### Folhas = SNAPSHOTS independentes
Chave `(data, sabor)`. Não acumulativas. Derivados **não persistem** (Cortados②③, Viradas②, P/Virar② recalculados ao exibir).

---

## 5. Pessoas e papéis

| Pessoa | Função |
|--------|--------|
| **Eraldo** | Gestor PCP; define ordens, ajusta parâmetros, decide proporção embalagem |
| **Leonardo** | Dev/estagiário; conta estoque (~7h–10h), alimenta sistema |
| **Sr. Joel** | Encarregado de produção; preenche papelzinho diário (5 col × 6 sabores); também PM e Balas |
| **Leonília** | Encarregada de embalagem cinta |
| **Gil** | Encarregado de corte |
| **Maria** | Produz palha (~2 dias/sem) |
| **Popô** | 1ª etapa embalagem (plástico) + corte de balas |

---

## 6. Decisões arquiteturais consolidadas (não revisitar)

- **Dual-backend:** `DATABASE_URL` vazia → SQLite (dev). `postgresql://...` → Postgres. `IS_POSTGRES` computado em import time.
- **`_sql(q)`:** troca `?` → `%s` só em PG. Auditado: nenhum `?` literal em SQL.
- **`_table_columns(c, t)`:** `PRAGMA table_info` (SQLite) ↔ `information_schema` (PG).
- **`_id_pk()`:** `INTEGER PRIMARY KEY AUTOINCREMENT` ↔ `INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY`.
- **Pooler Supabase porta 6543** (PgBouncer). Evita TCP+TLS handshake por chamada. Não usar porta 5432.
- **`salvar_folha_completa()`:** 4 tabelas em 1 transação atômica; rollback total em falha. UPSERT via `ON CONFLICT DO UPDATE` — idêntico em SQLite ≥ 3.24 e PG ≥ 9.5.
- **Fidelidade ao papel antes de automação.** Sistema faz exatamente o que o papel faz, na mesma unidade. Conversões = referência visual, não cálculo que substitui input.
- **Migração v1→v2 SQLite-only:** `_backup_db()` e `_migrate_v1_to_v2()` gated por `not IS_POSTGRES`.
- **Renderização inversa em `lancamento.py`:** coluna Joel renderiza antes da coluna oficial pra alimentar derivados em tempo real.
- **Bootstrap Streamlit Cloud:** topo de `lancamento.py` / `painel.py` propaga `st.secrets["DATABASE_URL"]` para `os.environ` antes de `import database` (Streamlit Cloud não faz isso automaticamente). Implementado em 12/05/2026.
- **`prepare_threshold=None` no psycopg.connect:** PgBouncer transaction mode (porta 6543) multiplexa transações em conexões backend compartilhadas; psycopg 3 cria prepared statements com nomes determinísticos (`_pg3_N`) que colidem ao reutilizar uma conexão backend que já tem o mesmo nome. Solução: desabilitar prepared statements automáticos. Custo desprezível pra workload baixa-frequência do PCP. Implementado em 12/05/2026 após `DuplicatePreparedStatement` na 1ª migração. Vira parágrafo no TCC.
- **Camada de cache separada (`cached_db.py`):** decorators `@st.cache_data` ficam num módulo wrapper, NÃO em `database.py`. Razão: scripts CLI (migração, smoke tests) importam `database.py` direto e não dependem de Streamlit. Toda UI importa de `cached_db.py`. TTL folhas = 60s · TTL refs = 1h. Invalidação manual via `invalidar_folha()` após save/delete. Implementado em 13/05/2026.
- **Multi-page Streamlit (`pages/` directory):** consolidação de `lancamento.py` + `painel.py` em um único app deployado, navegação automática no sidebar. `lancamento.py` continua sendo o entry point no Streamlit Cloud; `painel.py` foi deletado da raiz, conteúdo migrado pra `pages/1_Painel.py`. Vantagens: 1 link só pro Eraldo, 1 slot do free tier (em vez de 2), cache compartilhado entre páginas, mesmo deploy/secrets/versão. Implementado em 13/05/2026.

---

## 7. Pontos de atenção

- **Asteriscos `*` no papelzinho:** qty já enviada à embalagem → duplica em Cortados②. Solução atual: aviso ℹ️ + obs. Feature futura (Fase 1.5): checkbox por célula.
- **Encoding cp1252:** emojis em `print()` de scripts Python no Windows quebram. Sempre usar `$env:PYTHONIOENCODING="utf-8"`.
- **Campos legados:** `obs_joel`, `obs_gil`, `obs_leonilia`, `cnt_doces_displays` existem no schema, não exibidos separados na UI.
- **Secrets fora do Git:** `.streamlit/secrets.toml` no `.gitignore`. Se vazar, revogar URL Supabase imediatamente.
- **Mini de Z:** coluna "30g" do papelzinho = 27g/tablete. Registrado em `joel_mini`. Normal.

---

## 8. Estado atual (13/05/2026)

**Etapa 4 concluída.** App no ar em produção.

- 13 folhas no Postgres do Supabase (`folha_cocada=78`, `folha_palha=65`, `papelzinho_joel=54`, `folha_pm_balas_doces=13`). Paridade total com SQLite local (mantido como fallback/backup).
- Projeto Supabase: organização `doces-vo-nena`, projeto `pcp-vo-nena`, região `sa-east-1`, Postgres 17.6, pooler transaction porta 6543. Status Healthy. Compute NANO (free tier), 4/60 conns, 18% disco, 48% RAM.
- Bootstrap `st.secrets → os.environ` aplicado em `lancamento.py` e `painel.py`.
- `database.py:get_conn()` com `prepare_threshold=None` (correção do `DuplicatePreparedStatement`).
- Repositório GitHub: `github.com/leonardosoglia/pcp-vo-nena` (privado), branch `main`, commit `1b29f03`.
- App público no Streamlit Community Cloud: **`https://pcp-vo-nena.streamlit.app`** (deploy de `lancamento.py`, Python 3.14).
- Backup pré-migração: `pcp_vo_nena.db.bak.20260512_161629` (136 KB).
- Janela de manutenção do pooler Supabase em `sa-east-1`: **13-14/05/2026** (banner anunciou no dashboard).

**13/05/2026 (sessão tarde):**
- ✅ Erro `psycopg.errors.InternalError_` **resolveu sozinho** — era a janela de manutenção do pooler `sa-east-1` (13-14/05). App estabilizou.
- ✅ Cache adicionado (`cached_db.py`) — reduz latência percebida no app em produção.
- ✅ Multi-page consolidado: `painel.py` migrado para `pages/1_Painel.py`. `lancamento.py` continua entry point.
- ⏳ Pendente commit + push (Leonardo preenchendo folha de 13/05 em produção; evitar redeploy no meio).

---

## 9. Próximos passos imediatos

1. Leonardo termina input da folha de 13/05 em produção.
2. Commit + push das mudanças locais (cache + multi-page) → Streamlit Cloud redeploya automaticamente.
3. Apagar os 2 apps antigos `painel-vonena` no dashboard Streamlit Cloud (libera slots, free tier permite 3 apps).
4. Voltar o repo `pcp-vo-nena` para **privado** no GitHub (foi público temporariamente pra desbloquear o deploy inicial).
5. Validar com Eraldo na fábrica: mandar link `pcp-vo-nena.streamlit.app`. Pedir feedback de UX e regras de negócio.
6. Migração do `estoque` do SQLite local pra Postgres — o script só toca as 4 tabelas de folha. Verificar se há dados além do seed.
7. **22-29/05:** Etapa 5 (polimento visual, KPIs comparativos, exportação PDF).
8. **05/06:** início da escrita do TCC.
9. **~18/07:** defesa.

---

## 10. Dúvidas em aberto (entrevista futura com Eraldo)

- Frequência exata de produção de PM.
- Existe papelzinho separado para Bala/PM? Qual formato?
- Dias exatos de corte de palha (Maria).
- Quem produz Doces (Eraldo pergunta a quem diretamente?).
- Capacidade típica de Joel em tachos/dia.
- Como funcionam encomendas de cliente (afetam o parâmetro do dia?).

---

## 11. Como me ajudar bem

- **Postura:** especialista técnico em PCP + software. Não simplificar. Defender decisões com argumentos (vai pro TCC). Antecipar 2-3 jogadas.
- **Código:** sempre completo, sem `# resto do código aqui`. Pedaços menores e validáveis antes do próximo.
- **Tom:** informal, PT-BR, direto. Sem sumário do que acabei de fazer no final da resposta.
- **Antes de programar:** identificar inconsistências com o fluxo real da fábrica.
- **Unidades explícitas:** und · bandejas · tachos — nunca misturar.
- **TCC:** quando fizer decisão arquitetural, explicar o porquê (vira capítulo).

---

## 12. Históricos das sessões anteriores

- `historico_sessoes/sessao1_completa.md` — sessão principal, ~1700 entradas (~18.900 linhas).
- `historico_sessoes/sessao2_completa.md` — sessão curta pós-travamento (~180 entradas, ~3.200 linhas).

**Não ler na íntegra automaticamente** — custo de contexto muito alto. Consultar só se faltar informação específica que não consta neste CLAUDE.md.
