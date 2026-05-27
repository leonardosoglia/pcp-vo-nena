# HANDOFF COMPLETO — Estado do projeto em 27/05/2026

> **Pra Claude da próxima sessão:** este é o documento MASTER, atualizado em
> **27/05/2026 às 15h47**. Ler INTEIRO antes de qualquer ação. Em seguida:
> `INVENTARIO_PENDENCIAS.md` (50 pendências), `CLAUDE.md` (regras),
> `CADERNO.md` (diário), `PROXIMA_SESSAO.md` (plano da Etapa E) e memórias
> em `~/.claude/.../memory/MEMORY.md` (índice).
>
> **TODOS os números, datas e nomes de arquivos abaixo foram conferidos
> contra o sistema real em 27/05/2026.**

---

## 🔴 PRIMEIRA AÇÃO NA PRÓXIMA SESSÃO

1. **Cumprimentar o Leonardo** e confirmar que leu este handoff.
2. **Ler `INVENTARIO_PENDENCIAS.md`** — varredura sistemática de 50
   pendências. Foi criado em 27/05 depois que o Leonardo apontou que a
   Claude da sessão anterior esqueceu coisas que estavam documentadas.
3. **Perguntar onde o Leonardo quer continuar** — NÃO sair decidindo
   sozinho. Opções principais na seção 6.

---

## 1. SOBRE O LEONARDO (USUÁRIO)

- **Engenharia de Produção UFCG.** TCC defendendo ~18/07/2026. Escrita
  começa ~05/06/2026.
- **NÃO programa.** Linguagem simples, sem jargão de programação. Termos
  de PCP estão OK (tacho, bandeja, MRP, BOM, ord_prod, P/Virar, etc).
- **Cliente sênior + especialista de PCP da fábrica.** Você é o
  **programador avançado + engenheiro sênior de Engenharia de Produção**
  da dupla.
- **NUNCA usar nomes próprios** (Eraldo, Joel, Gil, Leonília, Paulo,
  Maria, Mariana, Popô) em prose/código/UI/doc. Use departamentos:
  **Gestão, Produção, Corte, Embalagem, Suprimentos**.
- **Persistir dados** que ele manda imediatamente no CADERNO + confirmar
  onde foi salvo.
- Ele lê tudo. Seja honesto sobre limitações.

---

## 2. O PROJETO EM 30 SEGUNDOS

PCP digital para **Pequenas Mordidas Alimentos Eireli / Doces Vó Nena**,
confeitaria semi-industrial em São Paulo. Substitui folhas de papel por
sistema digital — com visualização, alertas, análises, sugestão
automática ("sistema sugere, Gestão decide") e camada cognitiva via LLM.

**Stack:** Streamlit + Postgres (Supabase) + pandas + scikit-learn +
Plotly + Anthropic SDK (Claude). Hospedado em Hugging Face Spaces.

---

## 3. ESTADO ATUAL DO SISTEMA (27/05/2026 — verificado)

### URLs
- **App em produção:** `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena`
- **Repositório:** `https://github.com/leonardosoglia/pcp-vo-nena` (privado)
- **Banco de produção:** Supabase Postgres `pcp-vo-nena-us` (região us-east-1)
- **Remotes git locais:** `origin` (GitHub) + `hf` (Hugging Face)

### Banco — atenção dupla configuração
- `.streamlit/secrets.toml` LOCAL aponta para **banco antigo sa-east-1**
  (pausado mas funcional pra leitura/escrita). Pendência crítica #3.
- `DATABASE_URL` do HF Spaces aponta para **banco de produção us-east-1**
  (onde a Gestão lança as folhas em produção).

### Navegação atual (via `st.navigation` em `app.py`)
```
[Início]                              ← home.py (página padrão)

Operação do dia
├── Lançamento                        ← lancamento.py
└── Painel                            ← pages/1_Painel.py

Sugestão
├── Palha                             ← pages/10_Sugestao_Palha.py
└── Cocada                            ← pages/11_Sugestao_Cocada.py

Análises
├── Insights                          ← pages/2_Insights.py
├── Curva ABC                         ← pages/4_Curva_ABC.py
├── Anomalias ML                      ← pages/5_Anomalias_ML.py
└── Média Móvel                       ← pages/6_Media_Movel.py

Cadastros
├── Suprimentos                       ← pages/3_Suprimentos.py
└── Equipe                            ← pages/8_Equipe.py

Suporte
├── Assistente IA                     ← pages/7_Assistente_IA.py
└── Ajuda                             ← pages/9_Ajuda.py

Admin
└── Cadastrar BOM (setup)             ← pages/0_Admin_Seed.py
```

**Entry point:** `app.py` (substituiu `lancamento.py` em 26/05). Dockerfile
e config do HF apontam para `app.py`.

### Dados cadastrados no banco LOCAL (sa-east-1)
- 33 insumos cadastrados (via `seed_bom_completa.py`)
- **15** desses 33 com custo + fornecedor atualizados do Sigee (27/05)
- 91 linhas de BOM (Bill of Materials) — 12 produtos (6 cocadas + 5 palhas + PM + bala)

### Dados no banco de produção (us-east-1)
- 17+ folhas de produção lançadas pela Gestão (de 02/04 a 25/05+)
- **Insumos e BOM ainda NÃO cadastrados** — pendência crítica #1 (botão
  Admin Seed do HF não foi clicado pelo Leonardo ainda)

### Git
- Branch: `main`
- Último commit: `068a446 fix(handoff): corrigir data — hoje é 27/05/2026`
- **Tudo commitado e pushed** para origin (GitHub) e hf (Hugging Face)

---

## 4. O QUE FOI FEITO RECENTEMENTE

Histórico verificado contra `git log`. Duas sessões longas:

### Sessão 26/05/2026 (Frentes A-D + 3 melhorias IA + Etapa D + cocada v4)

**Cocada v4 — duas sugestões lado a lado**
- 26/05 12:41 — `fix(cocada)`: inclui joel_45g/mini/pet do papelzinho no cálculo
- 26/05 14:37 — `feat(cocada)`: painel de contexto histórico v4 (últimas N folhas do mesmo dia da semana)
- 26/05 15:08 — `feat(cocada)`: v4.1 duas sugestões lado a lado — Conservadora (fórmula) vs Histórica (mediana)
- **Status atual:** v4 **pausada** pelo Leonardo (achou "embolada e fora da realidade"). Próxima abordagem: NÃO copiar a palha — pensar na lógica própria da cocada.

**Etapa D — BOM cadastrada**
- 26/05 15:29 — `feat(suprimentos)`: cadastro completo via `pages/0_Admin_Seed.py`
- Criou `seed_bom_completa.py` com 33 insumos + 91 linhas de BOM
- Bug corrigido: `palha_<sigla>_tacho` → `palha_<sigla>_band` (palha é por bandeja, não tacho)
- Rodou no banco LOCAL. **Falta clicar no botão do HF** pra rodar em produção.

**4 Frentes de UX (A-D)**
- 26/05 16:13 — **Frente A**: `app.py` novo entry com `st.navigation`, `home.py` com saudação e atalhos
- 26/05 16:17 — **Frente B**: Meta × Realidade trocou `ord_emb_45g` por `Cortados²` (= emb + cort1 + joel_45g) em `pages/6_Media_Movel.py`
- 26/05 16:21 — **Frente C**: system prompt do Assistente IA atualizado (sem nomes, calendário flexível, Cortados² central, não-acomodação)
- 26/05 16:24 — **Frente D**: navegação de folhas saiu do sidebar e foi pra topo da página em `lancamento.py`

**3 melhorias do Assistente IA**
- 26/05 16:55 — `feat(ia)`: streaming (st.write_stream) + sugestões contextuais (4-6 perguntas baseadas no estado da folha) + slash commands (`/resumo`, `/anomalias`, `/comparar`, `/sugerir`, `/faltas`, `/historico`)

### Sessão 27/05/2026 (HOJE — IA Tool Use + calibração palha + TCC + Sigee + handoff)

**Modelo Opus 4 adicionado**
- 27/05 11:14 — `feat(ia)`: Claude Opus 4 no seletor (Haiku $, Sonnet $$, Opus $$$). Estimar_custo atualizado com pricing dos 3.

**Tool Use no Assistente IA (4ª melhoria)**
- 27/05 12:10 — `feat(ia)`: Tool use — `assistant_tools.py` com 7 ferramentas (`buscar_folha`, `listar_folhas_no_periodo`, `comparar_dia_da_semana`, `metricas_agregadas`, `info_meta_base_cocada_45g`, `info_alvos_estoque`, `calcular_cortados2`). `perguntar_com_tools()` em `claude_assistant.py` com loop agentic manual. Toggle "Modo profundo" na página.

**Calibração palha conservadora (50g)**
- 27/05 12:18 — `calibrar(palha)`: piso de 60 unidades líquidas. Folha real 27/05 mostrou T 50g líquido=56 und → Gestão decidiu 0 band → antes sistema arredondava pra 1, agora arredonda pra 0. Constante `PISO_LIQUIDO_50G_CONSERVADOR = 60`.

**TCC — estrutura ABNT + Capítulo 1 esboço**
- 27/05 12:40 — `docs(tcc)`: pasta `tcc/` com README, capa, resumo, 6 capítulos estruturados, Cap 1 (Introdução) esboçado integralmente (~6 págs ABNT). Cronograma de 8 semanas até defesa.

**Pesquisa web de referências bibliográficas**
- 27/05 14:03 — `docs(tcc)`: análise dos 3 PDFs do orientador (PUC-MG 2019, UnB 2014, ETEC 2021) + 7 buscas web identificando 18 trabalhos brasileiros relevantes. Princípio: pesquisar web ANTES de escrever cada capítulo. Pasta `tcc/referencias_externas/`.

**Relatório de Estágio — estrutura + Seções 1-2 esboço**
- 27/05 14:13 — `docs(relatorio-estagio)`: pasta `relatorio_estagio/` com identificação, capa, 5 seções. Seção 1 (Introdução) e Seção 2 (Caracterização da empresa) esboçadas (~6 págs ABNT total).

**Etapa C — Integração Sigee (acesso voltou hoje)**
- 27/05 14:46 — `feat(sigee)`: 3 entregáveis criados:
  - `suprimentos_sigee/01_matches_para_mariana.md` — planilha de 33 matches pra Mariana revisar
  - `suprimentos_sigee/02_checklist_export_sigee.md` — lista de exports faltantes
  - `importar_csv_sigee.py` — script idempotente, busca robusta (case-insensitive + whitespace)
- 27/05 15:06 — `data(sigee)`: import aplicado no banco LOCAL — **15 dos 33 insumos atualizados** com custo + fornecedor reais do Sigee.
  - 12 matches diretos resolvidos
  - 10 matches múltiplos pendentes (Mariana escolhe entre opções)
  - 8 sem match no Sigee (açúcar cristal, mascavo, achocolatado, essência mel, cravo, amaciante, sal, etiqueta palha)

**INVENTARIO_PENDENCIAS.md**
- 27/05 15:11 — Criado após Leonardo apontar que a Claude esqueceu do "esperando acesso ao Sigee voltar". 50 itens em 5 categorias. Leitura obrigatória em toda sessão nova.

**Handoff atualizado**
- 27/05 15:35 — primeira versão (tinha erros de data)
- 27/05 15:41 — `fix(handoff)`: corrigida data 28/05 → 27/05 em 8 lugares (3 arquivos)
- **Este arquivo** — segunda reescrita com fact-check completo

---

## 5. ROADMAP — onde estamos

| Etapa | O quê | Status (27/05/2026) |
|---|---|---|
| **A** — Renomeação departamentos | UI/variáveis usam departamentos | ✅ feito 14/05/2026 |
| **B** — Modelo de Suprimentos | Schema BOM + página | ✅ feito 15/05/2026 |
| **C** — Cadastro de insumos | Povoar `insumos` via Sigee | 🟡 **15/33 atualizados HOJE no banco local.** Falta: 10 matches múltiplos (Mariana confirma), 8 cadastros faltantes, estoque atual (relatório separado do Sigee), aplicar no banco de produção. |
| **D** — BOM cadastrada | Receitas no `bom_produto` | 🟡 **Rodou no banco LOCAL** (33 insumos + 91 linhas). **Falta clicar no botão da Admin Seed do HF** pra rodar em produção. 30 segundos. |
| **E** — Auto-baixa por produção | Folha salva → baixa insumo | ✅ **Implementada 27/05 (sessão 3).** `baixar_insumos_da_folha` + `reverter_baixa_da_folha` + `consumo_previsto_da_folha` em `database.py`. Hook opcional em `salvar_folha_completa(auto_baixa=False)`. UI: preview obrigatório no Lançamento, aba Movimentações ampliada (filtro de origem + top 5), card de alertas na Home, `baixar_historico.py` pra popular movimentos. Smoke test passou contra SQLite local; 245 movimentos populados no banco antigo (sa-east-1). Aguarda Etapa D rodar no banco us-east-1. |
| **F** — Alertas + sugestão compra + Sigee | MRP completo | 🔴 Pós-Etapa E |
| **Camada 2 palha** | Sugestão de corte/produção | ✅ MVP + conservadora calibrada (piso 60 und no 50g, validado 27/05) |
| **Camada 2 cocada v3** | Capacidade priorizada + sobra→pote + viração | ✅ Implementada |
| **Camada 2 cocada v4** | Outra abordagem (não copiar palha) | ⏸ **Pausada** pelo Leonardo em 26/05 |
| **Camada 3 — IA** | Assistente cognitivo com 4 features | ✅ Streaming, sugestões, slash, tool use. **Aguarda ANTHROPIC_API_KEY** ser configurada no HF. |

---

## 6. PRÓXIMOS PASSOS (Leonardo escolhe)

### 🥇 Etapa E — Auto-baixa de insumos
- Ler `PROXIMA_SESSAO.md` que detalha a implementação
- Hook em `salvar_folha_completa` chama `baixar_insumos_da_folha(data)`
- Idempotente (não duplica se rodar 2×), com `reverter_baixa_da_folha` pra estornos
- ~5-6h de trabalho. Funciona mesmo sem estoque atual cadastrado (registra movimentos negativos; ajustes de inventário corrigem depois).

### 🥈 Etapa D no banco de produção
- Leonardo precisa abrir o HF Spaces → sidebar → Admin → "Cadastrar BOM (setup)"
- Clica no botão "Cadastrar BOM completa" — cadastra 33 insumos + 91 linhas BOM no banco us-east-1
- 30 segundos. Idempotente (se rodar 2×, não duplica).

### 🥉 TCC Cap 2 — Revisão de Literatura
- Antes: nova pesquisa web focada (CAPES, SciELO, Spell BR)
- Esboço estrutural já existe em `tcc/capitulos/2_revisao_literatura.md`
- Referências por capítulo em `tcc/referencias_externas/03_referencias_por_capitulo.md`
- Lista de buscas pendentes em `tcc/referencias_externas/04_busca_pendente.md`

### 🏆 Embalagens (última peça da BOM)
- Gestão preencher última tabela do questionário `entrevistas/02_suprimentos.docx`
- Bloqueada por ação humana (não código)
- Quando vier: cadastrar plástico/cinta/pote/display no `bom_produto`

### Em paralelo (sem ir à fábrica)
- TCC Cap 2 (eu escrevo)
- Relatório Seção 3 (Atividades) — preciso cronograma exato do Leonardo
- Cocada v4 reformulada (se ele quiser retomar com outra abordagem)

---

## 7. ARQUIVOS-CHAVE (verificados em 27/05/2026)

### Documentação
| Arquivo | Linhas | Função |
|---|---|---|
| `HANDOFF_COMPLETO.md` | este | Snapshot da sessão (este arquivo) |
| `INVENTARIO_PENDENCIAS.md` | 142 | **50 pendências em 5 categorias — LEITURA OBRIGATÓRIA** |
| `PROXIMA_SESSAO.md` | 101 | Plano detalhado da Etapa E (Auto-baixa) |
| `CLAUDE.md` | 219 | Regras invariáveis + referência técnica |
| `CADERNO.md` | 760 | Diário do projeto (Bloco 5 = receitas, 1.A = palha, 1.B = cocada) |
| `HANDOFF_SIGEE.md` | 95 | Plano da integração Sigee (DESATUALIZADO — diz que acesso tá pausado, mas voltou 27/05) |

### Código principal
| Arquivo | Linhas | Função |
|---|---|---|
| `app.py` | 72 | Entry point com `st.navigation` |
| `home.py` | 146 | Página Início |
| `lancamento.py` | 1237 | Página Lançamento (navegação de folhas no topo) |
| `database.py` | 1886 | Schema + CRUD, dual SQLite/Postgres |
| `cached_db.py` | 334 | Wrappers `@st.cache_data` |
| `palha_planejamento.py` | 203 | Calculadora palha (Normal + Conservadora c/ piso 60) |
| `cocada_planejamento.py` | 371 | Calculadora cocada v3 |
| `claude_assistant.py` | 930 | LLM helper (streaming + tools + slash + prompt caching) |
| `assistant_tools.py` | 419 | 7 ferramentas que o Claude pode chamar |
| `seed_bom_completa.py` | 317 | Cadastra 33 insumos + 91 linhas BOM |
| `importar_csv_sigee.py` | 274 | Import Sigee → tabela insumos |

### Páginas Streamlit (12 ao todo)
```
pages/0_Admin_Seed.py            ← Cadastrar BOM (setup)
pages/1_Painel.py                ← Painel
pages/2_Insights.py              ← Insights
pages/3_Suprimentos.py           ← Suprimentos
pages/4_Curva_ABC.py             ← Curva ABC
pages/5_Anomalias_ML.py          ← Anomalias ML
pages/6_Media_Movel.py           ← Média Móvel (corrigida pra usar Cortados²)
pages/7_Assistente_IA.py         ← Assistente IA (com 4 melhorias)
pages/8_Equipe.py                ← Equipe
pages/9_Ajuda.py                 ← Ajuda
pages/10_Sugestao_Palha.py       ← Sugestão Palha
pages/11_Sugestao_Cocada.py      ← Sugestão Cocada
```

### Documentos acadêmicos
```
tcc/                                  (6 itens)
├── README.md                         (cronograma)
├── 00_capa.md
├── 04_resumo.md
├── capitulos/                        (6 capítulos)
│   ├── 1_introducao.md               ✅ esboço completo (~6 págs)
│   ├── 2_revisao_literatura.md       🟡 estrutural
│   ├── 3_metodologia.md              🟡 estrutural
│   ├── 4_resultados.md               🟡 estrutural
│   ├── 5_discussao.md                🟡 estrutural
│   └── 6_conclusao.md                🟡 estrutural
├── referencias_externas/             (5 arquivos)
│   ├── README.md                     (princípio metodológico)
│   ├── 01_pdfs_professor.md          (análise dos 3 PDFs)
│   ├── 02_busca_web_resultados.md    (18 trabalhos identificados)
│   ├── 03_referencias_por_capitulo.md
│   └── 04_busca_pendente.md
└── anexos/                           (vazio)

relatorio_estagio/                    (5 itens)
├── README.md
├── 00_capa.md
├── 01_identificacao.md
├── secoes/                           (5 seções)
│   ├── 1_introducao.md               ✅ esboço completo
│   ├── 2_empresa.md                  ✅ esboço completo
│   ├── 3_atividades.md               🟡 estrutural
│   ├── 4_resultados.md               🟡 estrutural
│   └── 5_consideracoes.md            🟡 estrutural
└── anexos/                           (vazio)
```

### Material da integração Sigee
```
suprimentos_sigee/
├── 01_matches_para_mariana.md           (planilha pra revisar)
├── 02_checklist_export_sigee.md         (lista de exports)
└── MateriasPrimas_27_05_2026.xlsx       (export Sigee de hoje — 259 itens)
```

---

## 8. PENDÊNCIAS CRÍTICAS (resumo — detalhes completos em `INVENTARIO_PENDENCIAS.md`)

| # | Pendência | Bloqueia |
|---|---|---|
| 1 | Etapa D no banco de produção (botão Admin Seed HF) | Etapa E em produção |
| 2 | Etapa C — Sigee completar (10 matches Mariana + 8 cadastros + estoque atual) | Etapa E útil |
| 3 | `.streamlit/secrets.toml` aponta pro banco antigo (sa-east-1) | Validações locais batem com produção |
| 4 | Embalagem — última peça das receitas (BOM) | BOM 100% |
| 5 | Etapa E — Auto-baixa | MRP completo |

Mais 45 pendências em 4 outras categorias (importantes, nice-to-have, documentação, técnicas) — ver `INVENTARIO_PENDENCIAS.md`.

---

## 9. REGRAS INVARIÁVEIS

1. **PT-BR informal e direto.** Sem jargão de programação com Leonardo.
2. **Persona:** programador avançado + engenheiro sênior de Eng. de Produção.
3. **Gestão decide.** Sistema sugere/visualiza/alerta, nunca comanda.
4. Antes de codar: identificar inconsistências com o fluxo real da fábrica.
5. Código completo, sem placeholders. Pedaços validáveis antes do próximo.
6. Unidades explícitas: und · band · tachos · kg · L · displays · bolos.
7. **Estoque vs Fluxo (Forrester 1961):** nunca somar `emb_*` entre dias.
8. Memória persistente: salvar descobertas em `~/.claude/.../memory/`.
9. Decisões arquiteturais explicam o porquê — viram capítulo do TCC.
10. Senha exposta em print → revogar imediatamente.
11. **Zero emoji decorativo** no sistema/app/código.
12. Validar UI no DOM renderizado antes de commitar.
13. **Sem nomes de pessoas** — sempre departamentos (Gestão, Produção, Corte, Embalagem, Suprimentos).
14. **Persistir dados** que Leonardo manda imediatamente; confirmar onde salvou.
15. **Ler `INVENTARIO_PENDENCIAS.md` no início de cada sessão.**
16. **Sempre conferir a data atual** (system reminder) — não inventar.

---

## 10. CRONOGRAMA TCC

| Data | O quê |
|---|---|
| 26-27/05/2026 | Sessões longas — IA polida, TCC iniciado, Sigee parcial, inventário |
| 28/05 a 04/06/2026 | Leonardo: visitar fábrica (Mariana + Gestão). Eu: Etapa E + TCC Cap 2 |
| **~05/06/2026** | **Início oficial da escrita do TCC** |
| 05/06 a 25/06/2026 | Capítulos 1-5 + métricas reais |
| 25/06 a 10/07/2026 | Capítulo 6 + revisão + ensaios |
| **~18/07/2026** | **DEFESA** |

---

## 11. MEMÓRIA + DOCUMENTAÇÃO — onde está o quê

- **`CLAUDE.md`** — regras invariáveis (sempre carregado pelo Claude Code)
- **`CADERNO.md`** — diário versionado (descobertas, entrevistas, receitas)
- **`INVENTARIO_PENDENCIAS.md`** — 50 pendências (leitura obrigatória)
- **`HANDOFF_COMPLETO.md`** (este) — snapshot da sessão
- **`HANDOFF_SIGEE.md`** — plano Sigee (DESATUALIZADO — atualizar quando puder)
- **`PROXIMA_SESSAO.md`** — plano detalhado da Etapa E
- **`tcc/`** + **`relatorio_estagio/`** — documentos acadêmicos
- **`suprimentos_sigee/`** — material da integração Sigee
- **`~/.claude/.../memory/MEMORY.md`** — índice das memórias persistentes

---

## 12. TEXTO PRO LEONARDO ABRIR A PRÓXIMA SESSÃO

(Copia daqui pra baixo e cola na nova sessão do Claude Code.)

```
Oi, sessão nova do PCP Vó Nena. A sessão anterior fechou em 27/05/2026.

Antes de QUALQUER ação, lê na ordem:

1. HANDOFF_COMPLETO.md (raiz do repo) — documento MASTER. É o snapshot
   da última sessão. Tem a "primeira ação" no topo.

2. INVENTARIO_PENDENCIAS.md (raiz do repo) — LEITURA OBRIGATÓRIA.
   Lista de 50 pendências em 5 categorias. Foi criado pq na sessão
   anterior você esqueceu coisas que estavam documentadas. Não esquece.

3. CLAUDE.md — regras invariáveis (departamentos sempre, nunca nome
   de pessoa; sem emojis decorativos; PT-BR direto). Persona: você é
   meu programador avançado e engenheiro sênior de Engenharia de
   Produção.

4. CADERNO.md — diário do projeto. Lê com atenção:
   - Bloco 5: todas as receitas (cocada, palha, PM, bala)
   - Seção 1.A: planejamento da PALHA
   - Seção 1.B: planejamento da COCADA + gaps de modelagem

5. PROXIMA_SESSAO.md — plano detalhado da Etapa E (Auto-baixa) se
   for esse o caminho que escolhermos.

6. Memórias em ~/.claude/projects/.../memory/MEMORY.md (índice).

Depois me dá um resumo em ~10 linhas:
   (a) Quem sou eu e como você vai falar comigo.
   (b) Estado atual do sistema (URLs, banco, navegação).
   (c) O que as sessões anteriores fizeram (resumo das 12 frentes
       cobertas em 26-27/05).
   (d) Quais são as 5 pendências CRÍTICAS (do inventário).
   (e) Os 3 próximos passos prioritizados.

Me diz onde quer continuar (não decida sozinho). Opções principais:
- Etapa E (Auto-baixa de insumos) — desbloqueada se eu rodar Admin Seed
  no HF antes
- TCC Cap 2 (Revisão de Literatura) — antes faz nova busca web
- Sigee completo — quando eu trouxer respostas da Mariana
- Embalagens — quando Gestão preencher a última tabela do questionário
- Continuar polindo o que já tem

Lembra das regras:
- Linguagem simples comigo, sem jargão de programação. Termos de PCP ok.
- Sempre persiste o que eu te mandar no CADERNO + diz onde salvou.
- Sem nome de pessoa (sempre departamento: Gestão, Produção, Corte,
  Embalagem, Suprimentos).
- Persona: programador avançado + engenheiro sênior de Engenharia de
  Produção.
- Confere a data atual sempre que mencionar data num documento.

Eu fiquei de fazer essas coisas entre as sessões (se já fiz, te aviso):
- Levar a planilha de matches do Sigee pra Mariana revisar
  (suprimentos_sigee/01_matches_para_mariana.md)
- Pegar com Mariana os exports de Embalagens + Posição de Estoque
- Conversar com orientador (2 decisões de escopo + template ABNT UFCG)
- Pegar CNPJ, endereço, datas/CH do estágio
- Configurar ANTHROPIC_API_KEY no HF (quando tiver grana)
- Clicar no botão "Cadastrar BOM completa" na Admin Seed do HF (30 seg)
- Ler os esboços (tcc/capitulos/1_introducao.md e
  relatorio_estagio/secoes/1_introducao.md + 2_empresa.md)

Manda ver.
```

---

**Fim do handoff. Sessão encerrada em 27/05/2026 às 15h47.**
*Próxima sessão retoma decidindo entre: Etapa E, TCC Cap 2, Sigee completo,
Embalagens ou polimento.*

— Claude Opus 4.7 (1M context)
