# 🚨 HANDOFF COMPLETO — Sessão 19/05/2026

> **Pra Claude da próxima sessão:** este é o documento MASTER de transferência.
> Leia INTEIRO antes de qualquer ação. Depois `CLAUDE.md`, `CADERNO.md`,
> `HANDOFF_SIGEE.md`, memórias persistentes.
> Sessão atual encerrou em 19/05/2026 ~15:30 BRT com **3 problemas críticos
> de design pendentes** + transferência pendente pro Sigee Cloud.

---

## 🔴 PROBLEMAS PENDENTES — PRIMEIRA AÇÃO DA PRÓXIMA SESSÃO

Leonardo escreveu textualmente:

> *"o design la não ficou legal. os emojis eram pra ter saido. as cores brancas
> ali no sidebar a esquerda tao se misturando com a fonte branca tambem, arruma
> tudo isso meu deusss."*

### Problema 1 — Design "não ficou legal"
**O que está errado:** mesmo após aplicar `ui_theme.py` (fonte Inter + paleta clean), o visual não convenceu. Razão provável: o tema Inter foi aplicado, mas o `<style>` antigo de cada página ainda tem prioridade em alguns pontos (especificidade CSS).

**Diagnóstico técnico:**
- `ui_theme.py` injeta CSS com `aplicar_tema()` — OK
- Páginas têm CSS legacy que ficou após a substituição (classes como `.insight-card-master`, `.didatica`, gradientes)
- O CSS legacy foi mapeado pelo tema novo COM `!important` em vários lugares, mas alguns elementos podem estar passando

**Solução pra próxima sessão:**
1. Abrir o app no HF, dar F12 → Inspector
2. Identificar quais elementos ainda estão com cores/fontes erradas
3. Adicionar regras `!important` no `ui_theme.py` ou remover CSS legacy de cada página
4. **Alternativa radical:** apagar TODO CSS antigo de cada página, deixar SÓ o `aplicar_tema()`

### Problema 2 — Emojis "eram pra ter saído"
**O que foi feito:** script removeu emojis APENAS dos `st.title()`. Headers internos (`st.header()`), métricas (`st.metric()`) e botões ainda têm emojis.

**Solução pra próxima sessão:**
1. Rodar script Python análogo ao desta sessão, mas que pegue:
   - `st.header("...")`
   - `st.subheader("...")`
   - `st.metric("emoji texto", ...)`
   - `st.button("emoji texto", ...)`
   - Texto em `st.markdown` com emojis decorativos
2. Manter APENAS emojis com função semântica clara (✅ OK, ⚠️ aviso, ❌ erro)
3. Banir emojis decorativos (📊, 📈, 🎯, 🔍, etc.)

### Problema 3 — Sidebar com texto branco sobre fundo branco
**O que está errado:** no print do Leonardo, vejo "Adicionar nova folha" como botão **branco com texto branco** na sidebar. Está ilegível.

**Causa:**
- Tema novo (`ui_theme.py`) define sidebar com `background-color: #1F2937` (escuro)
- Mas algum botão específico (provavelmente `+ Adicionar nova folha` em `lancamento.py`) tem CSS legacy que sobrescreve com `background: #FFFFFF` ou semelhante
- Resultado: botão branco + texto branco (definido no tema escuro) = invisível

**Diagnóstico:** olhar o CSS legacy do `lancamento.py` linhas ~100-200 (antes da substituição). Provavelmente havia regras pra botões específicos (`stPopover`, `[data-testid="stButton"]` com cor vermelha) que foram perdidas na refatoração ou estão conflitando.

**Solução pra próxima sessão:**
1. Inspecionar via F12 o botão ilegível
2. Identificar a classe/data-testid
3. No `ui_theme.py`, adicionar regra específica pra sidebar:
   ```css
   section[data-testid="stSidebar"] button {
       background-color: #C05621 !important;
       color: #FFFFFF !important;
   }
   ```

### Problema 4 (menor) — Folha PM/Balas voltou a mostrar "0"
**O que foi feito hoje:** o regex pra `value=None` quebrava somas (TypeError `int + NoneType`). Revertido nos 14 number_inputs diretos. **Só os campos da cocada/palha** (que usam helper `num_input_compact`) têm UX vazia.

**Solução pra próxima sessão:**
- Substituir os 14 number_inputs diretos pelo helper `num_input_compact`, OU
- Trocar `st.number_input` por `st.text_input` com regex de validação numérica
- Garantir que setas do teclado movem entre células (não incrementam valor)

### Problema 5 (menor) — Setas do teclado incrementam valor
- Limitação Streamlit nativa
- Pra resolver: trocar `st.number_input` por `st.text_input` com `int(valor or 0)` no salvamento
- Bastante trabalho — fazer com cautela

---

## 📋 ESTADO ATUAL DO SISTEMA (19/05/2026)

### URLs em produção
- **App principal:** `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena`
- **App backup:** `https://pcp-vo-nena.streamlit.app` (pausar em ~1 semana)
- **Repo:** `https://github.com/leonardosoglia/pcp-vo-nena` (público)

### Bancos
- **Atual em uso:** Supabase `pcp-vo-nena-us` (us-east-1) — migrado 19/05, latência -97%
- **Antigo (manter pausado):** Supabase `pcp-vo-nena` (sa-east-1) — backup vivo

### Páginas (10 no total)
1. **Lançamento** (`lancamento.py`) — entry point
2. **Painel** (`pages/1_Painel.py`)
3. **Insights** (`pages/2_Insights.py`) — regras hardcoded
4. **Suprimentos** (`pages/3_Suprimentos.py`) — schema pronto, aguarda Sigee
5. **Curva ABC** (`pages/4_Curva_ABC.py`) — Fase 1 ML
6. **Anomalias ML** (`pages/5_Anomalias_ML.py`) — Isolation Forest + botão "Explicar via IA"
7. **Calibração de Metas** (`pages/6_Media_Movel.py`) — Média Móvel
8. **Assistente IA** (`pages/7_Assistente_IA.py`) — Claude Q&A (não ativado)
9. **Equipe** (`pages/8_Equipe.py`) — funcionários + capacidades + presença
10. **Ajuda** (`pages/9_Ajuda.py`) — central de documentação/glossário/FAQ

### Tema visual
- `ui_theme.py` centraliza CSS via `aplicar_tema()`
- Fonte: Inter (Google Fonts)
- Paleta: branco/cinza neutros + laranja Vó Nena (#C05621) apenas em accents
- Status: **NÃO está perfeito** (ver Problemas 1, 2, 3 acima)

### Features de IA implementadas (não ativadas)
1. **Pergunte ao Claude** — página dedicada (Assistente IA)
2. **Explicação de Anomalia via Claude** — botão em Anomalias ML
3. Ambas requerem `ANTHROPIC_API_KEY` no HF Spaces
4. Custo estimado: R$5-15/mês uso típico
5. Leonardo decidiu **não ativar agora** (custo)

---

## 🗓️ TUDO QUE FOI FEITO NESTE PROJETO (HISTÓRICO)

### Antes desta sessão (12/05 – 18/05)
- **12-13/05:** Etapa 4 — deploy Postgres/Supabase + Streamlit Cloud
- **14/05:** Etapa A — renomeação por departamento (Gestão/Produção/Corte/Embalagem)
- **15/05:** Etapa B — schema Suprimentos + página com 4 abas
  - Tabelas: `insumos`, `bom_produto`, `movimentos_insumo`
  - MRP simplificado: folha × BOM × estoque → necessidade
- **15/05:** Entrevista parcial Eraldo (Blocos 1-3 + parte 5/6/7)
- **17/05:** Migração Streamlit Cloud → HF Spaces via Docker
- **17/05:** Insights recalibrado com respostas Eraldo
- **17/05:** Fase 1 ML completa — Curva ABC, Detecção Anomalia, Média Móvel
- **18/05:** Correção stock vs flow (insight Leonardo + Forrester 1961)
- **18/05:** Quick wins de performance (cache 30min, pre-warm, pool maior)

### Esta sessão (19/05)
- **Manhã:** Migração Supabase sa-east-1 → us-east-1 (latência -97%)
- **Manhã:** Reset de senha do banco (segurança)
- **Tarde:** Fase 3 LLM — código entregue mas NÃO ativado
- **Tarde:** Ideia 2 — Explicação de anomalia via Claude (botão na pg Anomalias)
- **Tarde:** Ideia 4 Etapa A — Cadastro de funcionários + capacidades + presença
- **Tarde:** 2 bugs corrigidos (KeyError Media Movel + Anomalias ML)
- **Tarde:** Página `Ajuda` criada — central de docs
- **Tarde:** Enxugamento de páginas ML (textos longos → captions curtas)
- **Final do dia:** Tema Inter aplicado + emojis reduzidos (PARCIAL) + folha vazia
- **Final do dia:** Bug TypeError corrigido (revertido value=None nos 14 diretos)
- **Final do dia:** `HANDOFF_SIGEE.md` criado pro próximo módulo (Sigee Cloud)

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
- `8a31e35` — **fix: TypeError soma bala_p_cortar + bala_cortadas** ⚠️ último

### Memórias persistentes criadas
- `project_migracao_hf_spaces.md`
- `project_fase1_ml_completa.md`
- `project_handoff_sigee.md`

---

## 🎯 PRÓXIMA SESSÃO — ORDEM DE AÇÃO RECOMENDADA

### Fase 1 — Corrigir design (URGENTE, ~2h)
1. **Inspect F12** no app HF, identificar elementos quebrados
2. **Sidebar:** consertar botão "+ Adicionar nova folha" (branco com branco)
3. **Remover TODOS os emojis decorativos** (manter só semânticos ✅⚠️❌)
4. **Validar visual** com Leonardo via prints

### Fase 2 — Integração Sigee Cloud (~5h)
Seguir o **`HANDOFF_SIGEE.md`** detalhadamente:
1. Investigação (Leonardo manda prints do Sigee)
2. Caminho A: importar_csv_sigee.py
3. Investigar API em paralelo

### Fase 3 — Refinamentos pendentes
- Folha: trocar `st.number_input` por `st.text_input` (setas funcionam)
- Pausar Supabase antigo (sa-east-1)
- Deletar app Streamlit Cloud + desabilitar GitHub Actions keepalive
- Deprecation warnings `use_container_width`

### Fase 4 — Continuar roadmap
- Ideia 4 Etapa B (input presença no Lançamento)
- Ideia 4 Etapa C (algoritmo Sugestão de Ordem)
- Eventualmente ativar Claude API (se Leonardo decidir gastar R$5-15/mês)

---

## 📂 ARQUIVOS-CHAVE DO PROJETO

### Documentação técnica (ler nesta ordem)
1. **`HANDOFF_COMPLETO.md`** — este arquivo (mais novo)
2. **`HANDOFF_SIGEE.md`** — plano de integração Sigee
3. **`CLAUDE.md`** — referência técnica permanente
4. **`CADERNO.md`** — diário do projeto, com descobertas
5. **`ROADMAP_IA.md`** — visão IA em 3 fases
6. **`HUGGINGFACE_SETUP.md`** — guia de deploy
7. **`CONTEXTO_SESSAO_ANTERIOR.md`** — handoff genérico antigo

### Código
- **`database.py`** — schema + CRUD, backend dual SQLite/Postgres
- **`cached_db.py`** — wrappers @st.cache_data sobre database.py
- **`ui_theme.py`** — tema visual centralizado (Inter font, paleta clean)
- **`claude_assistant.py`** — Claude API integration (Q&A + explicação anomalia)
- **`lancamento.py`** — entry point, formulário da folha
- **`pages/`** — 9 páginas Streamlit
- **`migrar_postgres_para_postgres.py`** — script de migração entre Supabases
- **`Dockerfile`** — receita do container HF Spaces

### Configs
- **`.streamlit/config.toml`** — paleta base + theme=light
- **`requirements.txt`** — Python deps (streamlit, pandas, plotly, psycopg, scikit-learn, anthropic, numpy)
- **`.gitattributes`** — Git LFS pra PDFs/DOCXs/XLSXs
- **`.github/workflows/keepalive.yml`** — anti cold start (desabilitar quando pausar Streamlit Cloud)

---

## 🔑 CREDENCIAIS E ACESSOS (nunca no chat, sempre no Notepad privado do Leonardo)

### Supabase
- **Conta:** `bandroid289@gmail.com`
- **Projeto ATIVO:** `pcp-vo-nena-us` (us-east-1)
- **Projeto LEGACY (pausar):** `pcp-vo-nena` (sa-east-1)
- **DATABASE_URL:** secret no HF Spaces + Streamlit Cloud (mesma URL)

### Hugging Face
- **Conta:** `leonardosoglia` (login Google)
- **Space:** `huggingface.co/spaces/leonardosoglia/pcp-vo-nena`
- **Settings > Variables and secrets:** `DATABASE_URL` configurada

### GitHub
- **Conta:** `leonardosoglia`
- **Repo:** `github.com/leonardosoglia/pcp-vo-nena` (público)
- **Branch:** `main`
- **Remotes locais:**
  - `origin` → GitHub
  - `hf` → Hugging Face

### Anthropic (NÃO ativada)
- Leonardo NÃO criou créditos
- Código pronto pra ativar: `claude_assistant.py` + `pages/7_Assistente_IA.py`
- Pra ativar: criar conta `console.anthropic.com`, gerar API key, configurar `ANTHROPIC_API_KEY` no HF

### Sigee Cloud (próxima sessão investigar)
- Mariana tem acesso (compras + estoque insumos)
- Eraldo tem acesso
- API existe? — desconhecido
- Detalhes em `HANDOFF_SIGEE.md`

---

## ⚠️ REGRAS PARA A PRÓXIMA SESSÃO

1. **PT-BR informal direto.** Sem floreios, sem "como posso ajudar".
2. **Especialista técnico em PCP + software sênior.** Defender decisões com argumentos.
3. **Eraldo decide.** Sistema sugere/visualiza/alerta. Nunca comanda.
4. **Antes de codar:** identificar inconsistências com fluxo real da fábrica.
5. **Código completo, sem placeholders.**
6. **Unidades explícitas:** und · band · tachos · kg · L · displays · bolos.
7. **Estoque vs Fluxo (Forrester 1961):** nunca somar `emb_*` entre dias.
8. **Memória persistente:** salvar descobertas críticas em `~/.claude/.../memory/`.
9. **TCC sempre em mente:** decisões viram capítulos. Cita referências (Pareto, Juran, Forrester, Liu/Ting/Zhou, Heizer/Render, Wheelwright/Hyndman).
10. **Senhas em prints:** revogar imediatamente, criar nova.
11. **Sem emojis decorativos.** Site profissional, não brincadeira.

---

## 🎯 PRIMEIRA MENSAGEM DA PRÓXIMA SESSÃO

Quando Leonardo abrir sessão nova, **ele vai mandar algo como:**

> *"Continua de onde paramos. Lê HANDOFF_COMPLETO.md primeiro."*

**Você (Claude) deve:**

1. Ler **este arquivo INTEIRO** primeiro
2. Ler `HANDOFF_SIGEE.md` (próximo módulo Sigee)
3. Ler `CLAUDE.md` (referência técnica)
4. Ler memórias persistentes (`project_handoff_sigee.md`, etc.)
5. **Resumir em 5-7 linhas:** estado + 3 problemas urgentes (design, emojis, sidebar) + próximo passo proposto
6. **Perguntar:** *"Vamos começar consertando o design (problemas 1-3) ou direto pra Sigee Cloud?"*
7. **NÃO TOMAR ATITUDE antes do alinhamento.**

---

## 📊 CRONOGRAMA TCC (referência)

- **19/05** (hoje) — Sessão atual encerrada
- **20-29/05** — Sigee integration + Etapa C (cadastro insumos) + Design fix
- **29/05-04/06** — Etapa D (BOM) + Etapa E (auto-baixa por produção)
- **05/06** — **Início escrita TCC** (Caps 1-2)
- **05/06-12/06** — Caps 3-4 + Ideia 4 Etapa C (algoritmo Sugestão Ordem)
- **12-25/06** — Cap 5 (Resultados) com métricas reais
- **25/06-10/07** — Cap 6 + revisão + ensaios defesa
- **~18/07/2026** — **DEFESA**

---

**Boa sorte na próxima sessão. Quando o design ficar certo + Sigee integrar, o projeto destrava DE NOVO.**

— Claude Opus 4.7, sessão 19/05/2026
