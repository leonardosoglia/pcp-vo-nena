# HANDOFF COMPLETO — Encerramento sessão 19/05/2026

> **Pra Claude da próxima sessão:** este é o documento MASTER de transferência.
> Ler INTEIRO antes de qualquer ação. Em seguida: `CLAUDE.md`, `HANDOFF_SIGEE.md`,
> `CADERNO.md` e memórias persistentes em `~/.claude/projects/.../memory/`.

---

## 1. ESTADO ATUAL (final desta sessão)

### URLs
- **Produção:** `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena`
- **Backup:** `https://pcp-vo-nena.streamlit.app` (pausar próxima semana)
- **Repo:** `https://github.com/leonardosoglia/pcp-vo-nena`

### Bancos
- **Ativo:** Supabase `pcp-vo-nena-us` (us-east-1) — latência ~5ms
- **Backup (manter pausado):** Supabase `pcp-vo-nena` (sa-east-1) — fallback

### Páginas (10)
1. **Lançamento** (`lancamento.py`) — entry point, formulário da folha
2. **Painel** (`pages/1_Painel.py`) — visualização por departamento
3. **Insights** (`pages/2_Insights.py`) — diagnóstico com regras hardcoded
4. **Suprimentos** (`pages/3_Suprimentos.py`) — schema pronto, aguarda Sigee
5. **Curva ABC** (`pages/4_Curva_ABC.py`) — Pareto dos produtos
6. **Anomalias ML** (`pages/5_Anomalias_ML.py`) — Isolation Forest + botão "Explicar via IA"
7. **Calibração de Metas** (`pages/6_Media_Movel.py`) — Média Móvel
8. **Assistente IA** (`pages/7_Assistente_IA.py`) — Claude Q&A (sem ANTHROPIC_API_KEY ativada)
9. **Equipe** (`pages/8_Equipe.py`) — funcionários + capacidades + presença
10. **Ajuda** (`pages/9_Ajuda.py`) — central de documentação/glossário/FAQ

### Tema visual (refatorado nesta sessão final)
- **Fonte:** Inter (Google Fonts)
- **Paleta:** sistema profissional baseado em design systems modernos (Linear, Vercel)
  - Sidebar dark slate-900 (#0F172A)
  - Conteúdo claro (#FFFFFF / #FAFAFA)
  - Brand orange #C05621 apenas em accents (botões primários, links, item ativo)
  - Status: success/warning/danger/info com bg sutil + border-left 4px
- **Tipografia hierárquica:** h1 28px / h2 22px / h3 17px / body 14px / caption 13px
- **CSS centralizado em `ui_theme.py`** — cada página chama `aplicar_tema()`
- **Compatibilidade backward:** classes legacy (`.insight-card-*`, `.didatica`,
  `.anomaly-card`, etc.) mapeadas pro novo tema com contraste correto
- **391 emojis decorativos removidos** de strings em todos os arquivos Streamlit
- **Sidebar:** botões laranja brand, popovers slate-700 → brand on hover, navegação
  com border-left brand no item ativo

### Features de IA (não ativadas)
1. **Pergunte ao Claude** (pages/7_Assistente_IA.py)
2. **Explicação de Anomalia** (botão em pages/5_Anomalias_ML.py)
3. Ambas requerem `ANTHROPIC_API_KEY` secret no HF Spaces
4. Custo estimado: R$5-15/mês uso típico
5. Leonardo decidiu não ativar agora

---

## 2. HISTÓRICO COMPLETO DO PROJETO

### Sessões anteriores (12-18/05)
- **12-13/05:** Etapa 4 — deploy Postgres/Supabase + Streamlit Cloud
- **14/05:** Etapa A — renomeação por departamento
- **15/05:** Etapa B — schema Suprimentos + página com 4 abas
- **15/05:** Entrevista parcial Eraldo (Blocos 1-3 + parte 5/6/7)
- **17/05:** Migração Streamlit Cloud → HF Spaces via Docker
- **17/05:** Insights recalibrado com respostas Eraldo
- **17/05:** Fase 1 ML completa — Curva ABC + Anomalia ML + Média Móvel
- **18/05:** Correção stock vs flow (Forrester 1961)
- **18/05:** Quick wins de performance (cache, pre-warm, pool)

### Sessão atual (19/05)
1. Migração Supabase sa-east-1 → us-east-1 (latência -97%)
2. Reset de senha do banco (segurança após vazamento em prints)
3. Fase 3 LLM — código entregue, não ativado
4. Ideia 2 — Explicação de anomalia via Claude
5. Ideia 4 Etapa A — Cadastro funcionários + capacidades + presença
6. 2 bugs corrigidos (KeyError Media Movel + Anomalias ML expander)
7. Página `Ajuda` criada (central de docs)
8. Enxugamento das páginas ML (textos longos → captions curtas)
9. Bug TypeError corrigido (`bala_p_cortar + bala_cortadas`)
10. **REFATORAÇÃO FINAL DO TEMA:**
    - `ui_theme.py` completamente reescrito (sistema de design profissional)
    - 391 emojis decorativos removidos
    - Sidebar dark consistente com hierarquia clara
    - Compatibilidade backward com classes legacy
    - Contraste WCAG validado

### Commits desta sessão (em ordem)
- `0446786` — feat(insights): recalibrar com respostas Eraldo
- `f32ef70` — feat(deploy): preparar migração HF Spaces
- `3a5af81` — docs: roadmap IA em 3 fases
- `0324efb` — config: Git LFS pra PDFs/DOCXs
- `678d6ad` — fix YAML header
- `3424897` — perf: 3 quick wins
- `e1f3341` — feat: Curva ABC
- `4d1f41e` — feat: Anomalias ML
- `cc096ad` — fix: estoque vs fluxo (Forrester)
- `015c14b` — feat: Média Móvel + Fase 1 completa
- `5b11a1d` — docs: CADERNO atualizado
- `4e2cb09` — feat(ia): código Pergunte ao Claude
- `0129f1f` — feat(ia): explicação anomalia via LLM
- `8c6febd` — feat(equipe): cadastro funcionários + capacidades + presença
- `61daec7` — fix(secrets) + ux polimento legendas
- `1d5c417` — fix: KeyError + enxugar páginas + criar Ajuda
- `14551a2` — ux(visual): tema Inter + folha vazia + handoff Sigee
- `8a31e35` — fix: TypeError soma bala_p_cortar
- `eb1b857` — docs: HANDOFF_COMPLETO.md
- **(commit pendente)** — refatoração final do tema + remoção total de emojis

### Memórias persistentes
- `project_migracao_hf_spaces.md`
- `project_fase1_ml_completa.md`
- `project_handoff_sigee.md`

---

## 3. PRÓXIMOS PASSOS (ordem recomendada)

### Fase 1 — Validar visual + ajustes finos (~30 min)
1. Leonardo abre HF Spaces após rebuild
2. Confere visualmente todas as 10 páginas
3. Se algo ainda parece estranho: F12 → inspecionar → reportar com print
4. Possíveis ajustes finos:
   - Tamanhos de fonte
   - Espaçamento
   - Cores específicas de algum elemento

### Fase 2 — Integração Sigee Cloud (~5h)
Seguir o **`HANDOFF_SIGEE.md`** detalhadamente:
1. Investigação inicial (Leonardo traz prints do Sigee)
2. Caminho A: criar `importar_csv_sigee.py`
3. Investigar API em paralelo
4. Decidir caminho definitivo

### Fase 3 — Refinamentos pendentes
- Folha PM/Balas: trocar `st.number_input` por `st.text_input` (campos vazios consistentes + setas movem entre células)
- Pausar Supabase antigo (sa-east-1)
- Deletar app Streamlit Cloud + desabilitar GitHub Actions keepalive
- Substituir `use_container_width=True` por `width="stretch"` (deprecation)

### Fase 4 — Continuação do roadmap
- Ideia 4 Etapa B (input presença no Lançamento)
- Ideia 4 Etapa C (algoritmo Sugestão de Ordem)
- Ativar Claude API (se Leonardo decidir)

---

## 4. ARQUIVOS-CHAVE

### Documentação (ler nesta ordem)
1. **`HANDOFF_COMPLETO.md`** ← este arquivo (mais novo)
2. **`HANDOFF_SIGEE.md`** — plano integração Sigee
3. **`CLAUDE.md`** — referência técnica permanente
4. **`CADERNO.md`** — diário do projeto
5. **`ROADMAP_IA.md`** — visão IA em 3 fases
6. **`HUGGINGFACE_SETUP.md`** — guia de deploy

### Código
- **`database.py`** — schema + CRUD, backend dual SQLite/Postgres
- **`cached_db.py`** — wrappers @st.cache_data
- **`ui_theme.py`** — tema visual centralizado (NOVO/refatorado nesta sessão)
- **`claude_assistant.py`** — Claude API integration
- **`lancamento.py`** — entry point, formulário da folha
- **`pages/`** — 9 páginas Streamlit
- **`migrar_postgres_para_postgres.py`** — script de migração Supabase
- **`Dockerfile`** — receita do container HF Spaces

### Configs
- **`.streamlit/config.toml`** — paleta base + theme=light
- **`requirements.txt`** — Python deps
- **`.gitattributes`** — Git LFS

---

## 5. CREDENCIAIS (no Notepad privado do Leonardo, nunca no chat)

### Supabase
- Conta: `bandroid289@gmail.com`
- Projeto ATIVO: `pcp-vo-nena-us` (us-east-1)
- Projeto LEGACY: `pcp-vo-nena` (sa-east-1)

### Hugging Face
- Conta: `leonardosoglia` (login Google)
- Space: `huggingface.co/spaces/leonardosoglia/pcp-vo-nena`
- Secret: `DATABASE_URL` configurada

### GitHub
- Conta: `leonardosoglia`
- Repo: `github.com/leonardosoglia/pcp-vo-nena` (público)
- Branches/remotes locais: `origin` → GitHub, `hf` → Hugging Face

### Anthropic (NÃO ativada)
- Sem créditos
- Código pronto: `claude_assistant.py` + `pages/7_Assistente_IA.py`

### Sigee Cloud (próxima sessão investigar)
- Mariana tem acesso (compras + estoque insumos)
- API existe? — DESCONHECIDO. Investigar.

---

## 6. REGRAS PARA A PRÓXIMA SESSÃO

1. **PT-BR informal direto.** Sem floreios, sem "como posso ajudar".
2. **Especialista técnico em PCP + software sênior.** Defender decisões.
3. **Eraldo decide.** Sistema sugere/visualiza/alerta, nunca comanda.
4. **Antes de codar:** identificar inconsistências com fluxo real da fábrica.
5. **Código completo, sem placeholders.**
6. **Unidades explícitas:** und · band · tachos · kg · L · displays · bolos.
7. **Estoque vs Fluxo (Forrester 1961):** nunca somar `emb_*` entre dias.
8. **Memória persistente:** salvar descobertas críticas em `~/.claude/.../memory/`.
9. **TCC sempre em mente:** decisões viram capítulos. Citar referências (Pareto, Juran, Forrester, Liu/Ting/Zhou, Heizer/Render, Wheelwright/Hyndman, Brown et al).
10. **Senhas em prints:** revogar imediatamente.
11. **Zero emoji decorativo.** Sistema profissional, não brincadeira.

---

## 7. CRONOGRAMA TCC

- **19/05** (hoje) — Sessão atual encerrada
- **20-29/05** — Sigee integration + Etapa C (cadastro insumos)
- **29/05-04/06** — Etapa D (BOM) + Etapa E (auto-baixa)
- **05/06** — **Início escrita TCC**
- **05/06-12/06** — Caps 1-4 + Ideia 4 Etapa C
- **12-25/06** — Cap 5 (Resultados)
- **25/06-10/07** — Cap 6 + revisão + ensaios
- **~18/07/2026** — DEFESA

---

## 8. PROBLEMAS CONHECIDOS / LIMITAÇÕES

### Folha PM/Balas mostra "0" em vez de vazio
Razão: regex anterior aplicou `value=None` em number_inputs cuja variável era usada em somas (`bala_p_cortar + bala_cortadas`). Reverti pra evitar TypeError. Próxima sessão: trocar `st.number_input` por `st.text_input` com validação.

### Setas do teclado incrementam valor (em vez de mover entre células)
Limitação Streamlit nativo. Pra resolver: usar `st.text_input` + parser numérico.

### Deprecation warnings `use_container_width`
~10 ocorrências em `st.plotly_chart(... use_container_width=True)` e `st.dataframe`. Trocar por `width="stretch"`.

### page_icon vazio em algumas páginas
Após remoção de emojis, alguns `page_icon=""` ficaram vazios. Streamlit aceita mas mostra favicon default. Não bloqueia, só estético.

---

## 9. PRIMEIRA AÇÃO DA PRÓXIMA SESSÃO

Quando Leonardo abrir sessão, **vai mandar texto pronto** (ver fim deste documento).

**Você (Claude) deve:**

1. Ler **este arquivo INTEIRO**
2. Ler `HANDOFF_SIGEE.md` (plano detalhado Sigee)
3. Ler `CLAUDE.md` (referência técnica)
4. Ler `CADERNO.md` (diário)
5. Ler memórias persistentes
6. **Resumir em 5-7 linhas** estado atual
7. **Perguntar:** *"Vamos validar o visual primeiro ou direto pra Sigee Cloud?"*
8. **NÃO TOMAR ATITUDE antes do alinhamento.**

---

**Boa sorte. Quando Sigee integrar + design ficar redondo, o projeto destrava.**

— Claude Opus 4.7 max mode, sessão 19/05/2026 ~16h BRT
