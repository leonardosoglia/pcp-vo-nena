# HANDOFF COMPLETO — Encerramento sessão 27-28/05/2026

> **Pra Claude da próxima sessão:** este é o documento MASTER. Ler INTEIRO
> antes de qualquer ação. Em seguida: `INVENTARIO_PENDENCIAS.md` (lista
> completa de 50 pendências), `CLAUDE.md` (regras), `CADERNO.md` (diário)
> e memórias em `~/.claude/.../memory/MEMORY.md` (índice).

---

## 🔴 PRIMEIRA AÇÃO NA PRÓXIMA SESSÃO

1. **Cumprimentar o Leonardo** e confirmar que leu este handoff.
2. **Ler `INVENTARIO_PENDENCIAS.md`** — varredura sistemática de pendências
   (50 itens em 5 categorias). Foi criado nesta sessão depois que o Leonardo
   apontou que eu (Claude anterior) esqueci coisas documentadas nos handoffs.
3. **Perguntar onde o Leonardo quer continuar** — não saia decidindo sozinho.
   Opções principais estão na seção 6.

---

## 1. SOBRE O LEONARDO (USUÁRIO)

- **Eng. de Produção UFCG.** TCC defendendo ~18/07/2026. Escrita começa ~05/06.
- **NÃO programa.** Linguagem simples, sem jargão de programação. Termos de
  PCP ok (tacho, bandeja, MRP, BOM, ord_prod, P/Virar, etc).
- **Cliente sênior** + **especialista PCP da fábrica**. Você é o **programador
  avançado + engenheiro de produção sênior**.
- **NUNCA usar nomes próprios** (Eraldo, Joel, Gil, Leonília, Paulo, Maria,
  Mariana, Popô) em prose/código/UI/doc. Use departamentos: **Gestão,
  Produção, Corte, Embalagem, Suprimentos**.
- **Persistir dados** que ele manda imediatamente no CADERNO + confirmar onde
  salvou.
- Ele lê tudo. Seja honesto sobre limitações.

---

## 2. O PROJETO EM 30 SEGUNDOS

PCP digital pra **Pequenas Mordidas Alimentos Eireli / Doces Vó Nena**,
confeitaria semi-industrial em São Paulo. Substitui folhas de papel por
sistema digital — visualização, alertas, análises, sugestão automática
("sistema sugere, Gestão decide") e camada cognitiva via LLM.

Stack: Streamlit + Postgres (Supabase us-east-1) + pandas + scikit-learn +
Plotly + Anthropic SDK (Claude). Hospedado em Hugging Face Spaces.

---

## 3. ESTADO ATUAL DO SISTEMA (28/05/2026)

### URLs
- **App em produção:** `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena`
- **Repositório:** `https://github.com/leonardosoglia/pcp-vo-nena` (privado)
- **Banco de produção:** Supabase Postgres `pcp-vo-nena-us` (us-east-1)
- Remotes git locais: `origin` (GitHub) + `hf` (Hugging Face)

### Navegação atual (sidebar via `st.navigation`)

```
[Início]  ← home.py (página padrão de abertura)

Operação do dia
├── Lançamento  ← lancamento.py
└── Painel       ← pages/1_Painel.py

Sugestão
├── Palha   ← pages/10_Sugestao_Palha.py
└── Cocada  ← pages/11_Sugestao_Cocada.py

Análises
├── Insights      ← pages/2_Insights.py
├── Curva ABC     ← pages/4_Curva_ABC.py
├── Anomalias ML  ← pages/5_Anomalias_ML.py
└── Média Móvel   ← pages/6_Media_Movel.py

Cadastros
├── Suprimentos  ← pages/3_Suprimentos.py
└── Equipe       ← pages/8_Equipe.py

Suporte
├── Assistente IA  ← pages/7_Assistente_IA.py
└── Ajuda          ← pages/9_Ajuda.py

Admin
└── Cadastrar BOM (setup)  ← pages/0_Admin_Seed.py
```

Entry point: `app.py` (substituiu `lancamento.py` na sessão de 27/05).

### Git

Tudo commitado e pushed. Último commit: `INVENTARIO_PENDENCIAS.md` criado.

---

## 4. O QUE FOI FEITO NESTA SESSÃO LONGA (27-28/05/2026)

### A — Reorganização da navegação (Frente A)
- `app.py` novo entry com `st.navigation` — sidebar custom em grupos
- `home.py` página Início (saudação, status, atalhos)
- Dockerfile atualizado pra apontar pra `app.py`

### B — Correção Meta × Realidade (Frente B)
- `pages/6_Media_Movel.py` trocou `ord_emb_45g` por `Cortados²` (= emb + cort1 + joel_45g)
- Mapa de calor parou de ficar todo vermelho falso
- Caption atualizada explicando a fórmula

### C — Assistente IA polido (Frente C)
- System prompt atualizado: SEM nomes, calendário flexível, Cortados² central,
  não-acomodação documentada, BOM cadastrada, crescimento da fábrica
- `_resumir_folha` agora calcula e exibe Cortados² + déficit vs param

### D — Lançamento limpo (Frente D)
- Navegação de folhas movida do sidebar pra topo da página
- 3 colunas compactas: Abrir/criar folha, Folhas anteriores, Data atual editando
- Sidebar agora mostra só a navegação do `st.navigation`

### E — Assistente IA com 4 melhorias
1. **Streaming** — texto chegando token a token (`StreamingResposta` + `st.write_stream`)
2. **Sugestões contextuais** — quando data é selecionada, gera 4-6 perguntas relevantes
3. **Slash commands** — `/resumo`, `/anomalias`, `/comparar`, `/sugerir`, `/faltas`, `/historico`
4. **Tool use** — toggle "Modo profundo" — Claude consulta banco via 7 ferramentas:
   `buscar_folha`, `listar_folhas_no_periodo`, `comparar_dia_da_semana`,
   `metricas_agregadas`, `info_meta_base_cocada_45g`, `info_alvos_estoque`,
   `calcular_cortados2`

### F — Modelo Opus 4 adicionado
- Seletor de modelo: Haiku 4.5 ($), Sonnet 4.6 ($$), Opus 4 ($$$)
- `estimar_custo` atualizado com pricing dos 3
- Tooltip explicando quando usar cada um

### G — Calibração palha conservadora (50g)
- Folha real de 27/05 mostrou T 50g liq=56 und → Gestão decidiu 0 band
- Antes: round(56/80) = 1 (errado)
- Agora: piso de 60 und líquidas — se líquido < 60, devolve 0
- Constante `PISO_LIQUIDO_50G_CONSERVADOR = 60` em `palha_planejamento.py`

### H — TCC: estrutura completa + Cap 1 esboço
- Pasta `tcc/` com README + 5 capítulos (1 esboçado, 2-6 estruturados)
- `capitulos/1_introducao.md` esboço completo (~6 págs ABNT)
- `04_resumo.md`, `00_capa.md` com placeholders
- Decisões pendentes: incluir LLM no escopo? mencionar Vó Nena pelo nome?

### I — Pesquisa web de referências bibliográficas
- Pasta `tcc/referencias_externas/` com 5 arquivos
- 3 PDFs do orientador analisados (PUC-MG 2019, UnB 2014, ETEC 2021)
- 18 trabalhos brasileiros identificados em 6 temas
- Princípio adotado: **pesquisar web ANTES de escrever cada capítulo**
- Conclusão: literatura BR sobre PCP digital em PMI de alimentos é escassa
  (reforça justificativa do TCC)

### J — Relatório de Estágio: estrutura + Seções 1-2 esboço
- Pasta `relatorio_estagio/` com README + 5 seções
- Seção 1 (Introdução) e 2 (Caracterização da empresa) esboçadas
- Identificação, capa, anexos com placeholders

### K — Etapa C — Integração Sigee (acesso voltou hoje 27/05)
- Leonardo retomou acesso ao Sigee Cloud
- Export filtrado: 259 matérias-primas ativas (vs 283 antes)
- Cruzamento com nossos 33 insumos:
  - **15 matches confirmados** — atualizados no banco LOCAL (custo + fornecedor)
  - **10 múltiplos** — Mariana escolhe entre opções
  - **8 sem match** — incluindo CRÍTICOS (açúcar cristal, sal, etiqueta palha)
- 3 entregáveis prontos:
  - `suprimentos_sigee/01_matches_para_mariana.md` — pra Mariana revisar
  - `suprimentos_sigee/02_checklist_export_sigee.md` — lista de exports
  - `importar_csv_sigee.py` — script idempotente, testado, funcional

### L — INVENTARIO_PENDENCIAS.md
- Criado depois que Leonardo apontou que eu esqueci do "esperando Sigee"
- Varredura sistemática de 50 pendências em 5 categorias
- Documento de leitura obrigatória no início de cada sessão

---

## 5. ROADMAP — onde estamos

| Etapa | O quê | Status |
|---|---|---|
| **A** — Renomeação departamentos | UI/variáveis usam departamentos | ✅ feito 14/05 |
| **B** — Modelo de Suprimentos | Schema BOM + página | ✅ feito 15/05 |
| **C** — Cadastro de insumos | Povoar `insumos` via Sigee | 🟡 **15/33 hoje (banco local)**. Falta: 10 matches Mariana + 8 cadastros + estoque atual + aplicar no banco de produção. |
| **D** — BOM cadastrada | Receitas no `bom_produto` | 🟡 **Rodou no banco LOCAL. Falta clicar no botão Admin Seed do HF** pra rodar em produção. |
| **E** — Auto-baixa por produção | Folha salva → baixa insumo | 🔴 Planejada (`PROXIMA_SESSAO.md`), 5-6h. Bloqueada por D + C. |
| **F** — Alertas + sugestão compra + Sigee | MRP completo | 🔴 Pós-Etapa E |
| **Camada 2 palha** | Sugestão de corte/produção | ✅ MVP + conservadora calibrada |
| **Camada 2 cocada v3** | Capacidade + sobra→pote + viração | ✅ |
| **Camada 2 cocada v4** | Outra abordagem (não copia palha) | ⏸ **Pausada** pelo Leonardo (26/05) |

---

## 6. PRÓXIMOS PASSOS (Leonardo escolhe)

### 🥇 Etapa E — Auto-baixa de insumos
- Ler `PROXIMA_SESSAO.md` que detalha a implementação
- Hook em `salvar_folha_completa` chama `baixar_insumos_da_folha(data)`
- Idempotente, com reverter pra estornos
- 5-6h de trabalho. Pode funcionar mesmo sem estoque atual cadastrado
  (registra movimentos negativos; ajustes de inventário corrigem depois)

### 🥈 Etapa D no banco de produção
- Leonardo precisa clicar 1 botão na página Admin Seed do HF
- Cadastra 33 insumos + 91 linhas de BOM no banco us-east-1
- 30 segundos

### 🥉 Embalagens (última peça da BOM)
- Gestão preencher última tabela do questionário `02_suprimentos.docx`
- Quanto de plástico/cinta/pote/display por produto
- Bloqueada por ação humana (não código)

### 🏆 TCC Cap 2 — Revisão de Literatura
- Antes: nova pesquisa web focada (CAPES, SciELO, Spell)
- Esboço estrutural já existe em `tcc/capitulos/2_revisao_literatura.md`
- Referências mapeadas em `tcc/referencias_externas/03_referencias_por_capitulo.md`

### Em paralelo (sem ir à fábrica)
- TCC Cap 2 (eu escrevo)
- Relatório Seção 3 (Atividades) — precisa cronograma exato do Leonardo

---

## 7. ARQUIVOS-CHAVE

| Arquivo | O que é |
|---|---|
| `HANDOFF_COMPLETO.md` | Este — snapshot da sessão |
| **`INVENTARIO_PENDENCIAS.md`** | **Lista completa de 50 pendências — LEITURA OBRIGATÓRIA no início de cada sessão** |
| `PROXIMA_SESSAO.md` | Plano detalhado da Etapa E (Auto-baixa) |
| `CLAUDE.md` | Regras invariáveis + referência técnica |
| `CADERNO.md` | Diário do projeto |
| `HANDOFF_SIGEE.md` | Plano da integração Sigee (precisa atualização — feito hoje) |
| `app.py` | Entry point Streamlit com st.navigation |
| `home.py` | Página Início |
| `lancamento.py` | Página Lançamento (com navegação de folhas no topo) |
| `palha_planejamento.py` | Calculadora palha (Normal + Conservadora com piso 60) |
| `cocada_planejamento.py` | Calculadora cocada v3 |
| `pages/10_Sugestao_Palha.py`, `pages/11_Sugestao_Cocada.py` | Páginas de sugestão |
| `claude_assistant.py` | LLM helper (streaming, tools, slash commands) |
| `assistant_tools.py` | 7 tools que o Claude pode chamar |
| `pages/7_Assistente_IA.py` | Página do Assistente |
| `seed_bom_completa.py` | Cadastra 33 insumos + 91 linhas BOM |
| `pages/0_Admin_Seed.py` | Botão "Cadastrar BOM" |
| `importar_csv_sigee.py` | Import Sigee → insumos |
| `suprimentos_sigee/01_matches_para_mariana.md` | Planilha pra Mariana revisar |
| `suprimentos_sigee/02_checklist_export_sigee.md` | Lista de exports pendentes |
| `suprimentos_sigee/MateriasPrimas_27_05_2026.xlsx` | Export do Sigee de hoje (259 itens) |
| `tcc/` | TCC ABNT — estrutura + Cap 1 esboço |
| `tcc/referencias_externas/` | Análise dos 3 PDFs do orientador + pesquisa web |
| `relatorio_estagio/` | Relatório de estágio — estrutura + Seções 1-2 |

---

## 8. PENDÊNCIAS CRÍTICAS (resumo — detalhes em INVENTARIO_PENDENCIAS.md)

| # | Pendência | Bloqueia |
|---|---|---|
| 1 | Etapa D no banco de produção (botão Admin Seed HF) | Etapa E |
| 2 | Etapa C — Sigee completar (10 matches + 8 cadastros + estoque atual) | Etapa E útil |
| 3 | `.streamlit/secrets.toml` aponta pro banco antigo (sa-east-1) | Validações locais |
| 4 | Embalagem — última peça das receitas (BOM) | BOM 100% |
| 5 | Etapa E — Auto-baixa | MRP completo |

E mais 45 itens em 4 categorias (importantes, nice-to-have, documentação, técnicas).

---

## 9. REGRAS INVARIÁVEIS

1. **PT-BR informal e direto.** Sem jargão de programação.
2. Especialista PCP + software sênior. Defender decisões.
3. **Gestão decide.** Sistema sugere/visualiza/alerta, nunca comanda.
4. Antes de codar: identificar inconsistências com fluxo real.
5. Código completo. Pedaços validáveis antes do próximo.
6. Unidades explícitas: und · band · tachos · kg · L · displays · bolos.
7. **Estoque vs Fluxo (Forrester 1961):** nunca somar `emb_*` entre dias.
8. Memória persistente: salvar descobertas em `~/.claude/.../memory/`.
9. Decisões arquiteturais explicam o porquê — viram capítulo do TCC.
10. Senha exposta em print → revogar imediatamente.
11. **Zero emoji decorativo** no sistema/app/código.
12. Validar UI no DOM renderizado antes de commitar.
13. **Sem nomes de pessoas** — sempre departamentos.
14. **Persistir dados** que Leonardo manda imediatamente; confirmar onde salvou.
15. **NOVO:** Ler `INVENTARIO_PENDENCIAS.md` no início de cada sessão.

---

## 10. CRONOGRAMA TCC

| Data | O quê |
|---|---|
| 28/05 (hoje) | Sessão encerrada — Sigee parcial, melhorias IA, TCC iniciado, inventário |
| 29/05–04/06 | Leonardo: visita à fábrica (Mariana + Gestão). Eu: Etapa E + TCC Cap 2 |
| **~05/06** | **Início oficial da escrita do TCC** |
| 05/06–25/06 | Caps 1-5 + métricas reais |
| 25/06–10/07 | Cap 6 + revisão + ensaios |
| **~18/07/2026** | **DEFESA** |

---

## 11. MEMÓRIA + DOCUMENTAÇÃO — onde está o quê

- **`CLAUDE.md`** — regras invariáveis (sempre carregado pra Claude)
- **`CADERNO.md`** — diário versionado (descobertas, entrevistas, receitas)
- **`INVENTARIO_PENDENCIAS.md`** — lista de 50 pendências (lê toda sessão)
- **`HANDOFF_COMPLETO.md`** (este) — snapshot da sessão
- **`HANDOFF_SIGEE.md`** — plano Sigee (precisa atualização)
- **`PROXIMA_SESSAO.md`** — plano da Etapa E
- **`tcc/`** + **`relatorio_estagio/`** — documentos acadêmicos
- **`suprimentos_sigee/`** — material da integração Sigee
- **`~/.claude/.../memory/MEMORY.md`** — índice das memórias persistentes

---

## 12. TEXTO PRO LEONARDO ABRIR A PRÓXIMA SESSÃO

(Copia daqui pra baixo e cola na nova sessão.)

```
Oi, sessão nova do PCP Vó Nena. A sessão anterior fechou em 28/05/2026.

Antes de QUALQUER ação, lê na ordem:

1. HANDOFF_COMPLETO.md (raiz do repo) — documento MASTER. É o snapshot
   da última sessão. Tem a "primeira ação" no topo.

2. INVENTARIO_PENDENCIAS.md (raiz do repo) — LEITURA OBRIGATÓRIA.
   Lista de 50 pendências em 5 categorias. Foi criado pq na sessão
   anterior você esqueceu coisas que estavam documentadas. Não esquece
   essa parte.

3. CLAUDE.md — regras invariáveis (departamentos sempre, nunca nome
   de pessoa; sem emojis decorativos; PT-BR direto).

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
   (c) O que a sessão anterior fez (resumo das 12 frentes — A a L).
   (d) Quais são as 5 pendências CRÍTICAS (do inventário).
   (e) Os 3 próximos passos prioritizados.

Me diz onde quer continuar (não decida sozinho). Opções principais:
- Etapa E (Auto-baixa de insumos) — bloqueada por Etapa D no HF
- TCC Cap 2 (Revisão de Literatura) — antes faz nova busca web
- Sigee completo — quando eu trouxer respostas da Mariana
- Embalagens — quando Gestão preencher
- Continuar polindo o que já tem

Lembra das regras:
- Linguagem simples comigo, sem jargão de programação. Termos de PCP ok.
- Sempre persiste o que eu te mandar no CADERNO + diz onde salvou.
- Sem nome de pessoa (sempre departamento: Gestão, Produção, Corte,
  Embalagem, Suprimentos).
- Você é meu programador avançado e engenheiro de produção sênior.

Eu fiquei de fazer essas coisas entre as sessões (se já fiz, te aviso):
- Levar a planilha de matches do Sigee pra Mariana revisar
- Pegar com Mariana os exports de Embalagens + Posição de Estoque
- Conversar com orientador (2 decisões de escopo + template ABNT UFCG)
- Pegar CNPJ, endereço, datas/CH do estágio
- Configurar ANTHROPIC_API_KEY no HF (quando tiver grana)
- Clicar no botão "Cadastrar BOM completa" na Admin Seed do HF (30 seg)

Manda ver.
```

---

**Fim do handoff. Sessão encerrada em 28/05/2026.**
*Próxima sessão retoma decidindo entre: Etapa E, TCC Cap 2, Sigee completo,
ou continuar polindo.*

— Claude Opus 4.7 (1M context)
