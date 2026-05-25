# HANDOFF COMPLETO — Encerramento sessão 24/05/2026

> **Pra Claude da próxima sessão:** este é o documento MASTER. Ler INTEIRO antes
> de qualquer ação. Em seguida: `CLAUDE.md` (referência técnica + regras), `CADERNO.md`
> (diário do projeto — seções **1.A (palha)** e **1.B (cocada)** são CHAVE), e as
> memórias persistentes em `~/.claude/.../memory/MEMORY.md` (índice).

---

## 🔴 PRIMEIRA AÇÃO NA PRÓXIMA SESSÃO

Cumprimentar o Leonardo, confirmar que leu o handoff + CADERNO + memória, e **perguntar
onde ele quer continuar**. Não saia decidindo sozinho. Opções principais (ver seção 7):

1. Testar/iterar a v2 da calculadora da cocada (potes recém-adicionados — pode ter feedback).
2. Pegar as metas de **embalagem** com a Gestão (última peça das receitas/BOM).
3. Retomar a extração de insumos do **SIGE** (quando o acesso voltar — estava pausado).
4. v3 da cocada — modelar a absorção de sobra de tacho parcial → potes.
5. v3 da cocada — capacidade priorizando T > L quando o teto aperta.

---

## 1. SOBRE O LEONARDO (USUÁRIO) — LEIA COM ATENÇÃO

- **Eng. de Produção UFCG.** TCC defendendo ~18/07/2026. Escrita começa ~05/06.
- **NÃO programa.** Comunicar em linguagem simples, sem jargão de programação.
  Explicar pelo **efeito visível**, não pela implementação. Termos de PCP estão OK
  (tacho, bandeja, MRP, BOM, ord_prod, P/Virar, etc.).
- Trate-o como o **cliente sênior** e o **especialista de PCP da fábrica**.
  Você é o **programador avançado + engenheiro de produção sênior** da dupla.
- Ele lê tudo. Seja **honesto** sobre limitações ("essa parte ainda não modela X").
- Ele se preocupa muito com **persistir os dados** que manda (receitas, fotos,
  decisões da Gestão) — sempre gravar no CADERNO/memória e dizer onde salvou.
  Memória `feedback_persistir_dados.md`.
- **Nunca usar nomes próprios** (Eraldo, Joel, Gil, Leonília, Paulo, Maria, Mariana,
  Popô) em prose/código/UI/doc. Use departamentos: **Gestão, Produção, Corte,
  Embalagem, Suprimentos.** Memória `feedback_sem_nomes.md`. Decisão de 14/05,
  reforçada em 23/05.

---

## 2. O PROJETO EM 30 SEGUNDOS

PCP digital pra uma confeitaria industrial (**Pequenas Mordidas Alimentos Eireli /
Doces Vó Nena**, São Paulo). Substitui as folhas de papel do chão de fábrica por
sistema digital — com visualização, alertas, análises, e **progressivamente
automação** (Camada 2 — "sistema sugere, Gestão decide"). Stack: Streamlit +
Postgres (Supabase) + pandas. Hospedado em Hugging Face Spaces.

---

## 3. ESTADO ATUAL DO SISTEMA (24/05/2026)

### URLs
- **App em produção:** `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena`
- **Repositório:** `https://github.com/leonardosoglia/pcp-vo-nena` (privado)
- **Banco:** Supabase Postgres `pcp-vo-nena-us` (us-east-1)
- Remotes git locais: `origin` (GitHub) + `hf` (Hugging Face).

### 11 páginas no sistema
`lancamento.py` (folha do dia) ·  
`pages/1_Painel.py` · `2_Insights.py` · `3_Suprimentos.py` · `4_Curva_ABC.py` ·
`5_Anomalias_ML.py` · `6_Media_Movel.py` · `7_Assistente_IA.py` · `8_Equipe.py` ·
`9_Ajuda.py` · **`10_Sugestao_Palha.py`** (novo 23/05 — Camada 2 da palha) ·
**`11_Sugestao_Cocada.py`** (novo 24/05 — Camada 2 da cocada, v2 com potes).

### Git
- Branch `main`. **Várias mudanças desta sessão NÃO foram commitadas** — Leonardo
  precisa decidir quando commitar. Ver seção 4.

---

## 4. O QUE FOI FEITO NESTA SESSÃO LONGA (21-24/05/2026)

**Resumo:** receitas 100% coletadas, palha automation funcionando, cocada automation
v2 funcionando, padrões dos dados documentados, regras do "no nomes" reforçadas.

### Confirmações de receita (cocada, Bloco 5 do CADERNO)
- **Pé de Moça** NÃO leva coco ralado (única cocada sem coco — Gestão confirmou).
- **Adoçante Zero** = "Lowçucar Culinária com Stevia" (Stevia mesmo, não "servia").
- **Sabores de palha a ignorar:** morango e paçoca.
- **Palha = panela, NÃO tacho.** 1 receita (1 panela) = 1 bandeja. Implicação:
  o código atual trata palha como tacho (chave `palha_<sigla>_tacho` + ÷8 no MRP)
  — **ERRADO**, corrigir na Etapa D/E. Memória `project_palha_planejamento.md`.
- **PM não é tacho nem panela** — assado/montado, unidade = bolo (70 und = 7 displays).
- **Bala** = 1 tacho = 30 balas. Anti-mofo = **Sorbato** (mesmo da cocada).

### Palha (CADERNO seção 1.A + memória `project_palha_planejamento.md`)
- Algoritmo de planejamento semanal documentado (corte = necessidade líquida,
  produção = order-up-to). Exemplo real 18/05/2026.
- **Receitas (fichas técnicas)** dos 5 sabores ativos no Bloco 5 — kg por lote de
  100 palhas 50g (= 1 bandeja). T (chocolate meio amargo), L (Ninho), Churros,
  Cookies (Ninho com Negresco), Limão (limão taiti).
- **Rendimento confirmado:** 1 bandeja de palha = 80-90 palhas 50g (planejamento
  usa 80, o mínimo) ou ~30 Pets.
- **Calculadora `palha_planejamento.py` + `pages/10_Sugestao_Palha.py`** — Leonardo
  testou com 18/05 e 11/05, bateu muito perto.

### Cocada (CADERNO seção 1.B + análise de 17 folhas)
- **Padrões observados:** T domina (189 band, 2,4× L); a fábrica está **crescendo**
  (+55% comparando metade antiga vs recente); calendário de corte mais flexível
  que a regra teórica (45g todo dia útil, Mini concentra Qua/Ter/Sex, Pet em Ter/Sex);
  parâmetros base do CLAUDE.md confirmados.
- **Restrição de mão de obra** (capacidade da Produção) é o teto real — modelo MVP
  só alerta, não redistribui prioridade.
- **Estoque-alvo de potes** recebido completo (todos os sabores, 260g e 605g).
- **Calculadora `cocada_planejamento.py` + `pages/11_Sugestao_Cocada.py`** v2 —
  cobre corte (45g/Mini/Pet) + produção bandejas + tachos + **potes 260g/605g**.
  Pré-carregada com 11/05/2026 pra validação. Bandejas: corte e produção batem
  perto da Gestão real. Potes: subestima em dia de tacho parcial (sobra-pra-pote
  não modelada — fica pra v3).

### SIGE Cloud (insumos — pausado)
- Export `Produtos_1_ate_283.xlsx` baixado em `C:/Users/bandr/AppData/Local/Temp/`.
- 283 produtos de matéria-prima — **maioria dos insumos das receitas está lá**,
  mas com muita duplicação (8 leite condensado, 11 farinha de trigo etc.) e
  lixo (cenoura, óleo de soja, vassoura, BOPP). 3 ausentes em matéria-prima:
  açúcar mascavo, cravo em pó, essência de mel.
- **Próximo passo (quando acesso voltar):** Produtos → Busca Avançada → Gênero 01
  + "Somente Com Estoque" → printar (não exportar) → ~30-50 itens "vivos"
  → cruzar com export → cadastrar `insumos`. Detalhes no CADERNO + memória.

### Insights / UI (sessão 21/05)
- Página `2_Insights.py` limpa de "quadros de chat" (perguntas amarelas, falas
  do Gestão entre aspas, "melhoria futura"). Gráfico cortado consertado.
  Zoom travado em todos os gráficos do sistema. Bug do quadro "Tachos parciais"
  consertado (rótulos certos: 3 tachos cozidos, 6 → potes pra um pedido de 18).

### Memória + CADERNO atualizados
- Memórias novas: `project_palha_planejamento.md`, `feedback_persistir_dados.md`,
  `feedback_sem_nomes.md`.
- Memórias atualizadas (correções): `project_tachos_parciais_potes.md` (corrigida
  versão antiga errada), `project_receita_por_tacho.md` (palha-não-é-tacho),
  `project_ajustes_antecipacao.md` (③ não comanda produção).
- CADERNO: seção **1.A (palha)** e **1.B (cocada)** novas, Bloco 5 (receitas)
  com tabelas completas.

---

## 5. ROADMAP — onde estamos

| Etapa | O quê | Status |
|---|---|---|
| **A** — Renomeação departamentos | UI/variáveis usam departamentos | ✅ feito 14/05 |
| **B** — Modelo de Suprimentos | Schema BOM + página | ✅ feito 15/05 |
| **C** — Cadastro de insumos | Povoar tabela `insumos` via SIGE | 🟡 em andamento (pausado por acesso) |
| **D** — BOM cadastrada | Receitas no `bom_produto` | 🟡 receitas coletadas, falta cadastrar |
| **E** — Auto-baixa por produção | Folha salva → baixa insumo | 🔴 pendente |
| **F** — Alertas + sugestão de compra + Sigee | MRP completo | 🔴 pendente (parcial até defesa) |
| **Camada 2 palha** | Sugestão de corte/produção | ✅ MVP funcionando 23/05 |
| **Camada 2 cocada v2** | Corte + produção + potes | ✅ MVP funcionando 24/05 |
| **Camada 2 cocada v3** | + capacidade priorizada + sobra→potes + viração calculada | 🔴 próximo |

---

## 6. PRÓXIMOS PASSOS (priorizados — Leonardo escolhe)

### 🥇 Cocada v3 (continua a IA)
- **Capacidade priorizada:** quando total de tachos sugerido > teto, redistribuir
  por prioridade (T > L > demais).
- **Sobra de tacho parcial → potes:** quando `ord_prod_band` não é múltiplo de 8,
  cozinhar `ceil(band/8)` tachos e a sobra (`ceil(band/8)*8 − band`) vira potes.
  Já documentado em `project_tachos_parciais_potes.md`.
- **Viração calculada:** olhar 3 dias à frente (lead time tacho→virar→cortar)
  e sugerir `ord_prod_virada` específico.

### 🥈 Embalagem (última peça das receitas)
- A Gestão tem que passar **quanto de plástico/cinta/pote/display cada produto
  consome**. Falta a última tabela do questionário `02_suprimentos.docx`.

### 🥉 Retomar SIGE quando acesso voltar
- Produtos → Busca Avançada → Gênero 01 + "Somente Com Estoque" → printar (3-4 prints).
- Cruzar com o export salvo em Temp.
- Construir `importar_csv_sigee.py` ou inserir manual.
- Repetir pro Gênero 02 (Embalagem) e 07 (Material de Uso e Consumo).

### Em paralelo
- Cadastrar BOM no sistema (Etapa D) com as receitas que já estão no CADERNO.
- Bugs técnicos pendentes (correção de "palha como tacho" no código + `÷8` do
  MRP virar `ceil(band/8)` quando ligar auto-baixa na Etapa E).

### 🎓 Escrita do TCC — começa ~05/06/2026 (~12 dias)

---

## 7. ARQUIVOS-CHAVE

| Arquivo | O que é |
|---|---|
| `CLAUDE.md` | Referência técnica + regras invariáveis. **Sempre carregado.** |
| `CADERNO.md` | Diário do projeto. **Seções 1.A (palha) e 1.B (cocada) são centrais.** Bloco 5 tem todas as receitas. |
| `palha_planejamento.py` | Calculadora pura da palha. Validado contra 18/05 e 11/05. |
| `pages/10_Sugestao_Palha.py` | Página Streamlit da palha. |
| `cocada_planejamento.py` | Calculadora pura da cocada v2 (com potes). Validado contra 11/05. |
| `pages/11_Sugestao_Cocada.py` | Página Streamlit da cocada v2. |
| `database.py` | Schema + CRUD, dual SQLite/Postgres. |
| `cached_db.py` | Wrappers `@st.cache_data` sobre database. |
| `ui_theme.py` | Tema visual. Seletores `[data-testid="stMain"]`. |
| `lancamento.py` | Folha do dia (entry point Streamlit). |
| `entrevistas/02_suprimentos.docx` | Questionário (5 de 6 tabelas respondidas — falta só embalagens). |
| `HANDOFF_COMPLETO.md` | Este arquivo. |
| `HANDOFF_SIGEE.md` | Plano específico da integração SIGE. |
| `C:/Users/bandr/AppData/Local/Temp/Produtos_1_ate_283.xlsx` | Export do SIGE (matéria-prima). Não apagar. |

---

## 8. DECISÕES IMPORTANTES (RECENTES)

- **Departamentos sempre, nomes nunca** — UI, código, doc, prose. Memória `feedback_sem_nomes.md`.
- **Receita por tacho** (cocada). Receita por receita/panela = bandeja (palha). Memória `project_receita_por_tacho.md`.
- **Tacho parcial → potes** (cocada). Pedido de 18 band = 3 tachos cozidos, 18 viram bandeja, 6 viram pote. Memória `project_tachos_parciais_potes.md`.
- **Sistema sugere, Gestão decide.** Camada 2 nunca comanda automaticamente — sugere com transparência.
- **Persistir dados imediatamente** que o Leonardo mandar (receitas, entrevistas, fotos) no CADERNO + confirmar onde salvou. Memória `feedback_persistir_dados.md`.
- **Validar UI no DOM renderizado**, não no chute (preview local). Memória `feedback_validar_ui.md`.
- **Horizonte de corte e produção** (cocada): distribui a necessidade em N dias (3 pra corte, 5 pra produção). Aproxima o que a Gestão faz na prática (não fecha tudo de uma vez).

---

## 9. REGRAS INVARIÁVEIS

1. **PT-BR informal e direto.** Sem jargão de programação com o Leonardo.
2. Especialista técnico em PCP + software sênior. Defender decisões com argumentos.
3. **Gestão decide.** Sistema sugere/visualiza/alerta, nunca comanda.
4. Antes de codar: identificar inconsistências com o fluxo real da fábrica.
5. Código completo, sem placeholders. Pedaços validáveis antes do próximo.
6. Unidades explícitas: und · band · tachos · kg · L · displays · bolos.
7. **Estoque vs Fluxo (Forrester 1961):** nunca somar `emb_*` entre dias.
8. Memória persistente: salvar descobertas críticas em `~/.claude/.../memory/`.
9. Decisões arquiteturais explicam o porquê — viram capítulo do TCC.
10. Senha exposta em print → revogar imediatamente.
11. Zero emoji decorativo no sistema/app/código.
12. Validar mudança de UI no app renderizado antes de commitar.
13. **Sem nomes de pessoas** — sempre departamentos.
14. **Persistir dados que o Leonardo manda** imediatamente; confirmar onde foi salvo.

---

## 10. CRONOGRAMA TCC

| Data | O quê |
|---|---|
| 24/05 (hoje) | Sessão encerrada — Camada 2 cocada v2 funcionando, receitas completas |
| 25/05 – 04/06 | Cocada v3, embalagens, SIGE (quando acesso voltar), Etapas C/D/E |
| **~05/06** | **Início da escrita do TCC** |
| 05/06 – 25/06 | Capítulos 1-5 + coleta de métricas reais |
| 25/06 – 10/07 | Cap 6 + revisão + ensaios |
| **~18/07/2026** | **DEFESA** |

---

## 11. MEMÓRIA + DOCUMENTAÇÃO — onde está o quê

- **`CLAUDE.md`** — sempre carregado. Regras invariáveis, schema básico, conversões, calendário, decisões arquiteturais antigas.
- **`CADERNO.md`** — diário versionado no repo. Histórico de descobertas, entrevistas, achados das folhas, roadmap, **planejamento da palha (1.A)** e **da cocada (1.B)**, receitas completas (Bloco 5).
- **`~/.claude/.../memory/MEMORY.md`** — índice das memórias persistentes (sempre carregado pra Claude). Cada arquivo `.md` é um fato/preferência/contexto durável.
- **`HANDOFF_COMPLETO.md`** (este) — snapshot da sessão. Substituído a cada encerramento.
- **`HANDOFF_SIGEE.md`** — plano específico do SIGE (precisa de atualização — ainda fala em filtro por Categoria, mas o melhor é Gênero do Produto + "Somente Com Estoque").

---

## 12. TEXTO PRO LEONARDO ABRIR A PRÓXIMA SESSÃO

(Copia daqui pra baixo e cola na nova sessão.)

```
Oi, sessão nova do PCP Vó Nena.

Antes de QUALQUER ação, lê na ordem:
1. HANDOFF_COMPLETO.md (raiz do repo) — documento MASTER, é o snapshot
   da última sessão. Tem a "primeira ação" no topo.
2. CLAUDE.md — referência técnica + regras invariáveis (departamentos
   sempre, nunca nome de pessoa).
3. CADERNO.md — diário do projeto. Lê com atenção:
   - Bloco 5: todas as receitas (cocada, palha, PM, bala).
   - Seção 1.A: planejamento da PALHA (algoritmo + exemplo 18/05).
   - Seção 1.B: planejamento da COCADA (padrões dos dados + algoritmo +
     restrição de mão de obra + alvos de pote).
4. Memórias em ~/.claude/projects/.../memory/MEMORY.md (índice).

Depois me dá um resumo em ~8 linhas:
   (a) Quem sou eu e como você vai falar comigo.
   (b) Estado atual do sistema.
   (c) O que a sessão passada fez (palha v1, cocada v2, receitas completas).
   (d) Os 3 próximos passos prioritizados.

Me diz onde quer continuar (não decida sozinho). As opções principais
estão na seção 6 do handoff. Eu já testei a palha (bateu) e a cocada v1
(close). A v2 da cocada acabou de ganhar potes — eu posso testar agora
ou seguir pra outra frente.

Lembra: linguagem simples comigo, sem jargão de programação. Termos de
PCP estão OK. Sempre persiste o que eu te mandar no CADERNO e me diz
onde salvou. Sem nome de pessoa (sempre departamento). Você é meu
programador avançado e engenheiro de produção sênior.

Manda ver.
```

---

**Fim do handoff. Sessão encerrada em 24/05/2026.**  
*Próxima sessão retoma decidindo entre: cocada v3, embalagens, SIGE.*

— Claude Opus 4.7 (1M context)
