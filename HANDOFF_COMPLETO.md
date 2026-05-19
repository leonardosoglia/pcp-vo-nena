# HANDOFF COMPLETO — Encerramento sessão 19/05/2026 ~16h30

> **Pra Claude da próxima sessão:** este é o documento MASTER definitivo.
> Ler INTEIRO antes de qualquer ação. Em seguida: `CLAUDE.md`, `HANDOFF_SIGEE.md`,
> `CADERNO.md`, memórias persistentes em `~/.claude/projects/.../memory/`.
> Sessão atual encerrou após várias iterações de design + 391 emojis removidos.

---

## 🔴 PRIMEIRA AÇÃO NA PRÓXIMA SESSÃO

**ANTES de qualquer outra coisa** o Leonardo quer:

### Diminuir AINDA MAIS os tamanhos de fonte

Mesmo após reduzir de 28px → 18px (h1), 22px → 14px (h2), etc., o Leonardo
ainda acha **grande demais**. Pista no print do dia 19/05 às 16:13 — "TRADICIONAL"
quebrando em 2 linhas no quadro Embalados, "LEITE CONDENSADO" também.

**Plano de ação:**
1. Abrir `ui_theme.py` no raiz do projeto
2. Reduzir mais 1-2 pontos em cada nível:
   - h1: 18px → **15-16px**
   - h2: 14px → **12-13px**
   - h3: 12px → **11px**
   - body: 12px → **11px**
   - caption: 11px → **10-11px**
   - métrica valor: 16px → **14-15px**
3. **Reduzir altura das células do quadro Embalados** (responsável por
   quebrar "TRADICIONAL" em 2 linhas). O CSS de `[data-testid="metric-container"]`
   pode ser reaproveitado, ou criar regras específicas pra os inputs do quadro Embalados.
4. **Largura das colunas** do quadro Embalados — provavelmente a coluna "Sabor"
   está estreita demais. Verificar `lancamento.py` no bloco `Embalados — Cocada`
   e ajustar as proporções `st.columns([...])`.
5. **Validar com Leonardo** antes de continuar pra outras tarefas. Mandar
   screenshot do app rebuildado depois do ajuste.

**Princípio:** o Leonardo já reclamou 3 vezes da fonte grande. Não cometer
o mesmo erro de só ajustar 1-2px. Fazer reducao real (~30-40%) + verificar
o quadro Embalados especificamente.

---

## 1. ESTADO ATUAL DO SISTEMA (final da sessão 19/05)

### URLs em produção
- **Principal:** `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena` (Docker)
- **Backup:** `https://pcp-vo-nena.streamlit.app` (pausar próxima semana)
- **Repo:** `https://github.com/leonardosoglia/pcp-vo-nena` (público)

### Bancos
- **Ativo:** Supabase `pcp-vo-nena-us` (us-east-1) — latência ~5ms
- **Backup pausável:** Supabase `pcp-vo-nena` (sa-east-1) — fallback de emergência

### 10 Páginas no sistema
| # | Arquivo | Função |
|---|---|---|
| 1 | `lancamento.py` | Entry point — formulário da folha do dia |
| 2 | `pages/1_Painel.py` | Visualização por departamento |
| 3 | `pages/2_Insights.py` | Diagnóstico operacional (regras hardcoded) |
| 4 | `pages/3_Suprimentos.py` | Insumos + BOM + necessidades (aguarda Sigee) |
| 5 | `pages/4_Curva_ABC.py` | Pareto dos produtos |
| 6 | `pages/5_Anomalias_ML.py` | Isolation Forest + botão "Explicar via IA" |
| 7 | `pages/6_Media_Movel.py` | Comparativo meta × realidade |
| 8 | `pages/7_Assistente_IA.py` | Claude Q&A (não ativado) |
| 9 | `pages/8_Equipe.py` | Funcionários + capacidades + presença |
| 10 | `pages/9_Ajuda.py` | Central de documentação |

### Tema visual atual (refatorado nesta sessão)
- **Fonte:** Inter (Google Fonts)
- **Paleta:** sistema profissional (Linear/Vercel/Stripe-like)
  - Sidebar dark slate-900 (#0F172A)
  - Conteúdo claro (#FFFFFF / #FAFAFA)
  - Brand orange #C05621 apenas em accents (botões primários, links, item ativo)
  - Status: success/warning/danger/info com bg sutil + border-left 4px
- **Tipografia atual** (Leonardo acha grande, REDUZIR mais):
  - h1: 18px / h2: 14px / h3: 12px / body: 12px / caption: 11px / métrica: 16px
- **CSS centralizado em `ui_theme.py`** — cada página chama `aplicar_tema()`
- **391 emojis decorativos removidos** dos 10 arquivos Streamlit
- **Sidebar** com items 12px, padding 5/10, botões laranja brand consistentes

### Features de IA (código pronto, NÃO ativadas)
1. **Pergunte ao Claude** (página dedicada)
2. **Explicação de Anomalia** (botão na página Anomalias ML)
3. Ambas requerem `ANTHROPIC_API_KEY` secret no HF Spaces
4. Custo: ~R$5-15/mês uso típico
5. Leonardo decidiu **não ativar agora** por questão de custo

### Animação de salvamento (NÃO REMOVER)
Adicionada no `lancamento.py:1187-1196`. Quando salva folha:
- `st.toast()` no canto com check verde
- `st.success()` inline confirmando
- `st.balloons()` REMOVIDO (festivo demais)

---

## 2. HISTÓRICO COMPLETO DO PROJETO

### Sessões anteriores (12-18/05)
- **12-13/05:** Etapa 4 — Deploy Postgres/Supabase + Streamlit Cloud
- **14/05:** Etapa A — Renomeação por departamento (Gestão / Produção / Corte / Embalagem)
- **15/05:** Etapa B — Schema Suprimentos (tabelas `insumos`, `bom_produto`, `movimentos_insumo`) + página com 4 abas
- **15/05:** Entrevista parcial Eraldo (Blocos 1-3 + parte 5/6/7)
  - Descobertas críticas: ajustes são pedidos antecipados; tachos parciais viram potes; receita é por tacho; capacidade variável da embalagem
- **17/05:** Migração Streamlit Cloud → HF Spaces via Docker
- **17/05:** Insights recalibrado com respostas do Eraldo
- **17/05:** Fase 1 ML completa — Curva ABC + Anomalia ML + Média Móvel
- **18/05:** Correção stock vs flow (Forrester 1961) — insight crítico do Leonardo
- **18/05:** Quick wins de performance (cache 30min, pre-warm, pool maior)

### Sessão atual (19/05)
1. **Manhã:** Migração Supabase sa-east-1 → us-east-1 (latência -97%)
2. **Manhã:** Reset de senha do banco (segurança após vazamento em prints)
3. **Tarde:** Fase 3 LLM — código entregue, não ativado
4. **Tarde:** Ideia 2 — Explicação de anomalia via Claude
5. **Tarde:** Ideia 4 Etapa A — Cadastro funcionários + capacidades + presença
6. **Tarde:** 2 bugs corrigidos (KeyError Media Movel + Anomalias ML expander)
7. **Tarde:** Página `Ajuda` criada (central de docs)
8. **Tarde:** Enxugamento das páginas ML (textos longos → captions curtas)
9. **Tarde:** Bug TypeError corrigido (`bala_p_cortar + bala_cortadas`)
10. **Tarde/Noite:** Refatoração FINAL do tema:
    - `ui_theme.py` completamente reescrito (sistema de design profissional)
    - 391 emojis decorativos removidos
    - Sidebar dark consistente
    - Compatibilidade backward com classes legacy
    - Contraste WCAG validado
11. **Noite:** Iterações de ajuste de fonte (h1 28→22→18, h2 22→17→14...)
    — **AINDA GRANDE, próxima sessão reduz mais**
12. **Noite:** Animação de salvamento (`st.toast` + `st.success`, removeu `st.balloons`)

### Commits desta sessão 19/05 (em ordem)
- `0446786` — feat(insights): recalibrar com respostas Eraldo
- `f32ef70` — feat(deploy): preparar migração HF Spaces
- `3a5af81` — docs: roadmap IA em 3 fases
- `0324efb` — config: Git LFS pra PDFs/DOCXs
- `678d6ad` — fix YAML header HF
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
- `6e66c93` — ux(refatoracao): tema profissional + 391 emojis removidos
- `0188b2c` — ux: reduzir fontes (1ª vez)
- `b7e1f6f` — ux: compactar tudo + animação salvar
- **(próximo commit)** — handoff final

### Memórias persistentes salvas
- `project_migracao_hf_spaces.md`
- `project_fase1_ml_completa.md`
- `project_handoff_sigee.md`
- `project_etapa4_deploy.md`
- `project_departamentos_e_mrp.md`
- `project_pm_unidades.md`
- `project_engrenagem_virada.md`
- `project_reposicionamento_insumos.md`
- `project_ajustes_antecipacao.md`
- `project_tachos_parciais_potes.md`
- `project_receita_por_tacho.md`
- `project_pessoa_mariana_e_sigee.md`

Verificar `~/.claude/projects/C--Users-bandr-OneDrive-Documentos-DISCIPLINAS-P10-Est-gio-Novo-projeto/memory/MEMORY.md` (índice).

---

## 3. PRÓXIMOS PASSOS (priorizados)

### 🥇 PRIORIDADE 0 — Fix de tipografia (PRIMEIRA AÇÃO próxima sessão)

Detalhado no topo deste documento. Reduzir fontes mais 30%, ajustar células
do quadro Embalados pra não quebrar "TRADICIONAL"/"LEITE CONDENSADO" em 2 linhas.

### 🥈 PRIORIDADE 1 — Integração Sigee Cloud

Seguir o **`HANDOFF_SIGEE.md`** (separate file). Resumo:

1. **Investigação inicial** (Leonardo + Claude): print do painel Sigee, ver se tem aba "API" ou "Integrações"
2. **Caminho A (CSV manual)** — Mariana exporta lista de insumos do Sigee, criamos `importar_csv_sigee.py`
3. **Caminho B (API REST)** — se Sigee tiver, criar cliente em Python
4. **Recomendação:** começar por A, investigar B em paralelo

**Pré-requisitos:**
- Mariana topa exportar CSV? (Leonardo pergunta)
- API do Sigee existe? (investigar)
- Bloco 4 questionário Eraldo (lista de insumos com fornecedor/lead time)

### 🥉 PRIORIDADE 2 — Refinamentos pendentes

| Item | Esforço | Impacto |
|---|---|---|
| Folha PM/Balas: trocar `st.number_input` por `st.text_input` (vazio em vez de 0 + setas movem entre células) | 2h | Médio |
| Pausar Supabase antigo (sa-east-1) | 5 min | Limpeza |
| Deletar app Streamlit Cloud + desabilitar GitHub Actions keepalive | 10 min | Limpeza |
| Substituir `use_container_width=True` por `width="stretch"` (~10 ocorrências, deprecation) | 30 min | Limpeza |
| Page_icon vazio em algumas páginas (pós-emoji removal) | 10 min | Cosmético |

### Continuação roadmap

| Item | Pré-requisito | Fase |
|---|---|---|
| Etapa C — Cadastro de insumos | Mariana CSV ou Sigee API | Pós-Sigee |
| Etapa D — BOM (receitas) | Eraldo confirmar receitas (Bloco 5) | Pós-C |
| Etapa E — Auto-baixa por produção | BOM cadastrada | Pós-D |
| Ideia 4 Etapa B — Input presença no Lançamento | Etapa A (já feita) | Independente |
| Ideia 4 Etapa C — Algoritmo Sugestão de Ordem | Etapa B + capacidades reais | Após entrevista capacidades |
| Ideia 4 Etapa D — Claude explica sugestão | Etapa C | Após C |
| Ideia 3 — Predição de falta de insumo | BOM + lead time | Após D |
| Fase 2 ML — Regressão + Prophet + Tendência | 8+ semanas de dados | Junho |

### 🎓 Escrita do TCC (a partir de 05/06)

- **Cap 1 — Introdução**
- **Cap 2 — Revisão de literatura** (Pareto, Juran, Forrester, MRP, OEE, Isolation Forest, LLMs)
- **Cap 3 — Metodologia** (stack, decisões arquiteturais, dual-backend)
- **Cap 4 — Implementação** (Camadas 0, 1, 1.5, 2)
- **Cap 5 — Resultados** (métricas reais, anomalias detectadas, decisões apoiadas)
- **Cap 6 — Conclusão + trabalhos futuros**

---

## 4. PROBLEMAS CONHECIDOS / LIMITAÇÕES

### Tipografia AINDA GRANDE (URGENTE)
Cobertura no item PRIORIDADE 0 acima. Leonardo já reclamou 3x.

### Folha PM/Balas mostra "0" em vez de vazio
Razão: regex anterior aplicou `value=None` em number_inputs cuja variável era
usada em somas (`bala_p_cortar + bala_cortadas`). Reverti pra evitar TypeError.
**Solução próxima:** trocar `st.number_input` → `st.text_input` com validação.

### Setas do teclado incrementam valor (em vez de mover entre células)
Limitação Streamlit nativo. Solução junto com PM/Balas (text_input).

### Deprecation warnings `use_container_width`
~10 ocorrências. Trocar por `width="stretch"`.

### Quadro Embalados com colunas estreitas
"TRADICIONAL"/"LEITE CONDENSADO" quebrando em 2 linhas. Ajustar proporções de
`st.columns([...])` em `lancamento.py` bloco "Embalados — Cocada".

### page_icon vazio em várias páginas
Após remoção de emojis, alguns `page_icon=""` ficaram vazios. Streamlit aceita
mas mostra favicon default. Cosmético.

### Sidebar "Adicionar nova folha" pode estar invisível em alguns rebuilds
Já corrigido na refatoração final, mas validar visualmente após rebuild novo.

---

## 5. ARQUIVOS-CHAVE

### Documentação (ler nesta ordem)
1. **`HANDOFF_COMPLETO.md`** ← ESTE arquivo
2. **`HANDOFF_SIGEE.md`** — plano integração Sigee
3. **`CLAUDE.md`** — referência técnica permanente
4. **`CADERNO.md`** — diário do projeto
5. **`ROADMAP_IA.md`** — visão IA em 3 fases
6. **`HUGGINGFACE_SETUP.md`** — guia de deploy

### Código principal
| Arquivo | O que faz |
|---|---|
| `database.py` | Schema + CRUD (backend dual SQLite/Postgres) |
| `cached_db.py` | Wrappers `@st.cache_data` sobre `database.py` |
| `ui_theme.py` | Tema visual centralizado — **EDITAR PRIMEIRO próxima sessão** |
| `claude_assistant.py` | Claude API integration (Q&A + explicação anomalia) |
| `lancamento.py` | Entry point — formulário da folha (com animação salvar) |
| `pages/1_Painel.py` ... `pages/9_Ajuda.py` | 9 páginas Streamlit |
| `migrar_postgres_para_postgres.py` | Migração entre Supabases |
| `Dockerfile` | Receita do container HF Spaces |

### Configs
- `.streamlit/config.toml` — paleta base
- `requirements.txt` — Python deps
- `.gitattributes` — Git LFS

---

## 6. CREDENCIAIS (sempre no Notepad privado do Leonardo, nunca no chat)

### Supabase
- Conta: `bandroid289@gmail.com`
- Projeto ATIVO: `pcp-vo-nena-us` (us-east-1)
- Projeto LEGACY: `pcp-vo-nena` (sa-east-1)

### Hugging Face
- Conta: `leonardosoglia` (login Google)
- Space: `huggingface.co/spaces/leonardosoglia/pcp-vo-nena`
- Secret configurado: `DATABASE_URL`

### GitHub
- Conta: `leonardosoglia`
- Repo: `github.com/leonardosoglia/pcp-vo-nena` (público)
- Remotes locais: `origin` (GitHub), `hf` (Hugging Face)

### Anthropic (NÃO ativada)
- Sem créditos
- Código pronto: `claude_assistant.py` + `pages/7_Assistente_IA.py`
- Ativar: criar conta `console.anthropic.com`, gerar API key, configurar `ANTHROPIC_API_KEY` no HF

### Sigee Cloud (próxima sessão investigar)
- Mariana tem acesso (compras + estoque insumos)
- Eraldo tem acesso
- API existe? — DESCONHECIDO, investigar

---

## 7. COMANDOS DE DEPLOY

### Atualizar produção
```powershell
cd "C:\Users\bandr\OneDrive\Documentos\DISCIPLINAS\P10\Estágio\Novo projeto"

# Empurra pra GitHub (Streamlit Cloud rebuilda automaticamente)
git push origin HEAD:main

# Empurra pra HF Spaces (rebuilda em ~3-5 min)
git push hf HEAD:main
```

### Acessar logs do HF
URL: `huggingface.co/spaces/leonardosoglia/pcp-vo-nena/logs`

### Restart manual do HF
Dashboard do Space → 3 pontos → "Restart Space"

---

## 8. REGRAS INVARIÁVEIS PARA TODAS AS SESSÕES

1. **PT-BR informal direto.** Sem floreios, sem "como posso ajudar".
2. **Especialista técnico em PCP + software sênior.** Defender decisões com argumentos.
3. **Eraldo decide.** Sistema sugere/visualiza/alerta, NUNCA comanda.
4. **Antes de codar:** identificar inconsistências com fluxo real da fábrica.
5. **Código completo, sem placeholders.**
6. **Unidades explícitas:** und · band · tachos · kg · L · displays · bolos.
7. **Estoque vs Fluxo (Forrester 1961):** nunca somar `emb_*` entre dias. Usar `ord_corte_*`/`ord_emb_*`.
8. **Memória persistente:** salvar descobertas críticas em `~/.claude/.../memory/`.
9. **TCC sempre em mente:** decisões viram capítulos. Citar referências.
10. **Senhas em prints:** revogar imediatamente, criar nova.
11. **Zero emoji decorativo.** Sistema profissional.
12. **Animação ao salvar folha (NÃO REMOVER):** `st.toast` + `st.success` em `lancamento.py:1187+`.

---

## 9. CRONOGRAMA TCC

| Data | O quê |
|---|---|
| 19/05 (hoje) | Sessão encerrada |
| 20-29/05 | Fix design + integração Sigee + Etapa C |
| 29/05-04/06 | Etapa D (BOM) + Etapa E (auto-baixa) |
| **05/06** | **Início da escrita do TCC** |
| 05/06-12/06 | Caps 1-4 + Ideia 4 Etapa C (algoritmo Sugestão) |
| 12-25/06 | Cap 5 (Resultados) com métricas reais |
| 25/06-10/07 | Cap 6 + revisão + ensaios defesa |
| **~18/07/2026** | **DEFESA** |

---

## 10. PRIMEIRA AÇÃO DA PRÓXIMA SESSÃO (resumo)

Quando Leonardo abrir sessão nova, **você (Claude) deve:**

1. **Ler `HANDOFF_COMPLETO.md` INTEIRO** (este arquivo)
2. **Ler `HANDOFF_SIGEE.md`** (plano Sigee detalhado)
3. **Ler `CLAUDE.md`** (referência técnica)
4. **Ler `CADERNO.md`** (diário)
5. **Ler memórias persistentes** (`MEMORY.md` é o índice)
6. **Resumir em 5-7 linhas:** estado + os 3 problemas principais (fontes grandes, folha PM 0, setas teclado) + próximo passo
7. **PERGUNTAR antes de mexer:** *"Posso começar reduzindo as fontes do `ui_theme.py` agora? Ou prefere abrir outro tópico primeiro?"*
8. **Não tomar atitude antes do alinhamento.**

---

## TEXTO INICIAL PRA COPIAR NA PRÓXIMA SESSÃO

```
Oi, sessão nova do PCP Vó Nena.

Antes de QUALQUER ação, lê na ordem:

1. HANDOFF_COMPLETO.md (raiz do repo) — documento MASTER. Tem TUDO:
   estado atual, histórico, próximos passos priorizados, primeira ação
   urgente (fonte ainda grande), regras invariáveis, cronograma TCC.

2. HANDOFF_SIGEE.md — plano detalhado de integração com Sigee Cloud.

3. CLAUDE.md — referência técnica permanente.

4. CADERNO.md — diário do projeto.

5. Memórias persistentes em ~/.claude/projects/.../memory/ — abre
   MEMORY.md (índice) e lê as mais recentes.

Depois de ler tudo, me dá um resumo em ~7 linhas:
   (a) Estado atual do sistema
   (b) O problema URGENTE da fonte (que ficou grande mesmo após 2 reduções)
   (c) Outros problemas pendentes (folha PM mostra 0, setas teclado, etc)
   (d) Status da integração Sigee Cloud (pendente)

Aí me pergunta: "Posso começar reduzindo as fontes do ui_theme.py agora
(prioridade 0 do handoff)? Quanto você quer reduzir — manter compacto
profissional, ou ainda mais radical?"

NÃO tome atitude antes desse alinhamento. NÃO faça nada além de ler e
me perguntar.

Manda ver.
```

---

**Boa sorte na próxima sessão. Quando fonte ficar compacta + Sigee integrar, o projeto destrava.**

— Claude Opus 4.7 max mode, sessão 19/05/2026 ~16h30 BRT
