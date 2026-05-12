# CLAUDE.md — PCP Vó Nena

## 1. Identidade e contexto

**Projeto:** Dashboard de PCP — Doces Vó Nena (confeitaria industrial, São Paulo-SP).
**Dev:** Leonardo Sóglia, graduando em Eng. de Produção UFCG (Campina Grande-PB), residindo em SP para estágio + TCC simultâneos.
**Objetivo TCC:** substituir folhas de papel do chão de fábrica por sistema digital com visualização, alertas e futura sugestão automática de corte.
**Defesa prevista:** ~18/07/2026 (aprox.). Escrita do TCC começa 05/06/2026 (aprox.).

---

## 2. Stack técnico

- **App:** Python 3.14 + Streamlit — porta 8502 (`lancamento.py`), 8501 (`painel.py`).
- **Dados:** pandas + SQLite local (`pcp_vo_nena.db`) → migração iminente para Supabase Postgres.
- **Driver PG:** psycopg 3 (`psycopg[binary]>=3.2`) + URL do pooler Supabase (porta **6543**, não 5432).
- **Deploy alvo:** Streamlit Community Cloud (free) + Supabase free tier (500 MB, ~30 k folhas de margem).
- **Extras:** openpyxl (xlsx), plotly (viz), python-docx (relatórios TCC).

Subir local:
```powershell
streamlit run lancamento.py --server.port=8502
streamlit run painel.py     --server.port=8501
```

---

## 3. Arquivos principais

| Arquivo | Função |
|---------|--------|
| `database.py` | Schema v2, dual-backend SQLite/PG, toda lógica de dados |
| `lancamento.py` | Formulário diário da folha (porta 8502) |
| `painel.py` | Abas Eraldo · Joel · Gil · Leonília · Estoque · Análise (porta 8501) |
| `analise.py` | KPIs, heatmaps, anomalias — importada pelo painel |
| `exportar.py` | Gera XLSX por folha (chamado pelo menu ⋮) |
| `inserir_historico.py` | Script one-shot de inserção em massa (já rodou) |
| `migrar_dados_sqlite_para_postgres.py` | ETL idempotente SQLite → Supabase (pré-requisito: `DATABASE_URL`) |
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
- **Bootstrap Streamlit Cloud (PENDENTE):** `lancamento.py` / `painel.py` precisam de 3 linhas no topo pra expor `st.secrets["DATABASE_URL"]` como env var (Streamlit Cloud **não** faz isso automaticamente).

---

## 7. Pontos de atenção

- **Asteriscos `*` no papelzinho:** qty já enviada à embalagem → duplica em Cortados②. Solução atual: aviso ℹ️ + obs. Feature futura (Fase 1.5): checkbox por célula.
- **Encoding cp1252:** emojis em `print()` de scripts Python no Windows quebram. Sempre usar `$env:PYTHONIOENCODING="utf-8"`.
- **Campos legados:** `obs_joel`, `obs_gil`, `obs_leonilia`, `cnt_doces_displays` existem no schema, não exibidos separados na UI.
- **Secrets fora do Git:** `.streamlit/secrets.toml` no `.gitignore`. Se vazar, revogar URL Supabase imediatamente.
- **Mini de Z:** coluna "30g" do papelzinho = 27g/tablete. Registrado em `joel_mini`. Normal.

---

## 8. Estado atual (12/05/2026)

- 12 folhas no banco (`pcp_vo_nena.db`, 139 KB).
- `database.py` refatorado para dual-backend. Smoke test SQLite OK (12 folhas, cálculos derivados OK).
- `migrar_dados_sqlite_para_postgres.py` pronto (idempotente, `--dry-run`).
- **Etapa 4 em andamento — bloqueador: criar projeto Supabase + URL do pooler.**
- Checklist detalhado em `MIGRATION_TO_POSTGRES.md`.

---

## 9. Próximos passos imediatos

1. Leonardo termina input do 12/05 em `lancamento.py`.
2. Leonardo cria projeto Supabase → URL pooler porta 6543 → `.streamlit/secrets.toml` local (não no chat).
3. Adicionar bootstrap de `DATABASE_URL` em `lancamento.py` / `painel.py`.
4. `python -c "import database; database.init_db()"` com `DATABASE_URL` setada → cria schema no Postgres.
5. `python migrar_dados_sqlite_para_postgres.py --dry-run` → confirmar datas → rodar sem `--dry-run`.
6. Deploy: Streamlit Cloud + secrets + smoke test.
7. **22-29/05:** Etapa 5 (polimento visual, KPIs comparativos, exportação PDF).
8. **05/06:** início da escrita do TCC.

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
