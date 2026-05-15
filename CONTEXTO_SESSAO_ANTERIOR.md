# Handoff — Sessão 15/05/2026 (sexta) — ATUALIZADO 15/05 fim do dia

> **Pra você que acabou de abrir uma nova sessão do Claude Code neste projeto:**
> Leia este arquivo INTEIRO antes de fazer qualquer coisa. Em seguida o `CLAUDE.md`
> (referência técnica). Em seguida o `CADERNO.md` (diário com descobertas, perguntas,
> roadmap). Só depois disso, responda ao Leonardo.
>
> **🆕 ATUALIZAÇÃO 15/05 fim do dia:** Eraldo respondeu PARTE do questionário (Blocos
> 1, 2, 3 + parte 5/6/7). Várias DESCOBERTAS CRÍTICAS recalibram o entendimento do
> projeto. Veja seção 3.5 abaixo, e CADERNO.md seção 1.0, antes de qualquer ação.

---

## TL;DR (1 minuto)

- **Estado:** app em produção (`pcp-vo-nena.streamlit.app`) com Etapas A + B feitas. Keepalive ativo. Suprimentos pronto pra receber cadastro.
- **O que falta da sessão anterior:** Leonardo levou ficha de entrevista (29 perguntas) pro Eraldo no questionário pendente. **Vai chegar respondida nesta sessão nova.**
- **Próxima grande virada decidida:** **migrar de Streamlit Cloud Free → Hugging Face Spaces** (16× mais RAM, não dorme, ainda grátis). Mas **com cuidado** — não destruir Streamlit Cloud até HF Spaces estar 100% validado.
- **Visão estratégica recalibrada (importante):** o coração do projeto é o **PCP de produção**, NÃO o controle de insumos. Suprimentos é **suporte/contexto**, não driver. Detalhe abaixo.
- **IA / ML:** Leonardo quer começar agora, ainda que de forma simples. Eu (Claude) preciso ser honesto sobre o que dá e o que não dá com poucos dados. Plano gradual abaixo.

---

## 1. Estado do projeto em 15/05/2026

### O que está rodando hoje em produção
- **App público:** `https://pcp-vo-nena.streamlit.app/`
- **Plataforma:** Streamlit Community Cloud Free + Supabase Postgres (sa-east-1)
- **Páginas:** Lançamento (home) · Painel · Insights · **Suprimentos (NOVO 15/05)**
- **Folhas no banco:** ~14 (mais novas: 11, 12, 13, 14, 15/05)
- **GitHub:** `leonardosoglia/pcp-vo-nena` (público temporariamente)

### Roadmap de Etapas (A-F)

| Etapa | O quê | Status |
|---|---|---|
| **A** | Renomeação por departamentos (Gestão / Produção / Corte / Embalagem) | ✅ 14/05 |
| **B** | Modelo de Suprimentos (3 tabelas + página + MRP simplificado) | ✅ 15/05 |
| **C** | Cadastro inicial de insumos | ⏳ Aguarda entrevista Eraldo |
| **D** | Cadastro de Receitas (BOM) | ⏳ Aguarda entrevista Eraldo |
| **E** | Auto-baixa por produção (Camada 1.5) | ⏳ Semana 22-29/05 |
| **F** | Alertas + sugestão de compra + Sigee Cloud | ⏳ Parcial até defesa |

**Cronograma TCC:**
- 18/05 - 21/05: receber questionário, cadastrar Etapas C/D, iniciar HF Spaces migration
- 22/05 - 29/05: Etapa E + Etapa 5 do TCC (polimento Camada 1)
- 30/05 - 04/06: consolidação
- **05/06:** começa escrita do TCC
- **~18/07:** defesa

---

## 2. O que rolou nesta sessão (15/05/2026)

Lista do que foi feito hoje (em ordem):

1. ✅ Resolvido erro `Oh no — Error running app` em produção (era repo privado bloqueando clone; voltou pra público).
2. ✅ Pool de conexões Postgres adicionado em `database.py` (`psycopg-pool`, min 2, max 5).
3. ✅ Pre-warm do pool no import time (mata cold start de TCP+TLS handshake).
4. ✅ `get_folha_completa()` com 4 queries paralelas (ThreadPoolExecutor) — substituiu chamadas separadas.
5. ✅ Cache TTL aumentado: folhas 60s → 5min, refs 1h → 24h.
6. ✅ `folha_existe()` otimizado: 4 queries → 0 (reusa cache de `list_datas_folha`).
7. ✅ Tema light forçado via `.streamlit/config.toml` (não usa mais dark do sistema).
8. ✅ `plotly_chart` com `displayModeBar=False` em todos os gráficos (resolve zoom acidental no celular).
9. ✅ `ZERO 45g` mascarado como "—" nas tabelas do Painel (produto não existe).
10. ✅ Conversão de bandeja corrigida no banco: 6 kg recém-tacho / 5,5 kg pronta-corte (era "≈ 7 kg" errado).
11. ✅ Limpeza profunda do PC do Leonardo: lixo Temp/Update/cache liberados (~5 GB), startups bloat removidos, plano de energia "Alto desempenho", **Autodesk completamente desinstalado** (~9 GB).
12. ✅ Identificadas peças que ele comprou: RAM 4GB DDR4 3200 (vai funcionar 100%, slot livre) + SSD Patriot 120GB SATA (notebook tem baia 2.5" porque é modelo bateria 35Wh).
13. ✅ **GitHub Actions keepalive** rodando: pinga app a cada 15 min em horário comercial (seg-sáb, 7h-19h BR). Resolve cold start sem custo.
14. ✅ **Etapa B — Suprimentos** criada e deployada: 3 tabelas + 4 abas + helpers + cache + smoke test contra Supabase.
15. ✅ Memórias persistentes salvas: `project_engrenagem_virada.md`, `project_pm_unidades.md`.

---

## 3. Clarificações IMPORTANTES de domínio (LEIA com atenção)

### 3.1 Insumos vs Estoque vs Produto Semiacabado

**Discussão de 15/05 que reposiciona o projeto:**

A fábrica trabalha com **3 categorias de "coisa medida"**, não 1:

| Categoria | O que é | Quem conta | Onde está no sistema |
|---|---|---|---|
| **Insumo** (matéria-prima) | Coco ralado, leite condensado, açúcar, mel, plástico, cinta... | Quase ninguém conta sistematicamente | **Suprimentos** (Etapa B — feito hoje) |
| **Produto semiacabado** | Bandejas cortadas mas não embaladas; massa virada esperando o corte | Leonardo, Joel — informalmente | Folha de Produção (campos `cort1_*`, `joel_pv`, `joel_v`) |
| **Produto acabado** (estoque) | Cocada embalada pronta pra venda; PM em display pronto | Leonardo (todo dia 7h-10h) | Folha de Produção (campos `emb_*`) |

**Insight crítico:** o **Eraldo NÃO produz olhando insumos.** Ele decide ordens olhando:
1. **Estoque acabado** (Embalados)
2. **Semiacabado** (Cortados ②, Viradas, P/Virar)
3. **Parâmetro do dia** (demanda esperada por dia da semana)
4. **Mão de obra disponível** (quem tá no chão de fábrica hoje)
5. **Pedidos de cliente** (encomendas pontuais)

Insumos entram como **CONTEXTO defensivo:** "preciso saber se vai faltar coco antes de ordenar 24 bandejas, mas o coco não é o GATILHO da ordem — o gatilho é a demanda."

**Implicação prática pro sistema:**
- O **coração** é a Folha de Produção + Painel + Insights (Camadas 0 + 1).
- Suprimentos é **suporte:** avisa sobre falta antes de virar problema.
- **NÃO** tornar Suprimentos o centro da experiência. Eraldo não vai abrir Suprimentos como primeira tela — abre Lançamento ou Painel.
- A página de "Necessidades do dia" da aba Suprimentos é **alerta passivo**, não fluxo principal.

### 3.2 Foco do projeto, na visão do Leonardo (palavras dele)

> *"Minha ideia principal é tornar esse PCP melhor, mais prático, economizar tempo com ele. (...) É interessante ter insights que sejam importantes e que agreguem, que mostre aquela visão diferenciada, mas, minha ideia principal é tornar esse PCP melhor."*

**Tradução pra próxima sessão:** priorize sempre que reduza tempo/erro no dia-a-dia do Eraldo. Insights, IA e Suprimentos só agregam SE forem práticos. Não criar feature complexa que ele não vai usar.

### 3.3 Conversão de bandeja corrigida hoje

| Estado da bandeja | Peso |
|---|---|
| Recém-saída do tacho (úmida) | **~6 kg** |
| Pronta pra corte (após viração + descanso) | **~5,5 kg** |

A conversão "≈ 7 kg" que estava na tabela era incorreta. Atualizado no banco hoje (init_db re-seed). Documentado em `CLAUDE.md` seção 4 (regras de negócio) e na memória persistente.

### 3.4 Engrenagem da Virada (`ord_prod_virada`)

Já documentado em memória persistente, mas vale repetir pra próxima sessão entender:

`ord_prod_virada` é **resposta corretiva** ao Viradas② baixo. Quando sobra pouco/nenhum estoque de bandejas viradas após o corte do dia, a Gestão pede pra virar X bandejas pra repor.

Exemplo 15/05: Leite Condensado V② = 1 → ord_prod_virada(L) = 15.

### 3.5 🆕 DESCOBERTAS DO QUESTIONÁRIO (15/05 fim do dia)

**Eraldo respondeu Blocos 1-3 + parte 5/6/7. Várias coisas recalibram o projeto.**

Detalhes completos: `CADERNO.md` seção 1.0 + 5 memórias persistentes em `~/.claude/projects/.../memory/`. Resumo:

#### Descoberta 1 — Ajustes da Gestão = ANTECIPAÇÃO de pedidos (não correção)
- A diferença entre `param_real_*` e o base da tabela `metas_45g` representa **pedidos futuros** distribuídos ao longo dos dias.
- Exemplo (15/05 quinta): base T=6800 → real T=8300 porque pedido cliente de +1500 distribuído na semana.
- **Implicação:** o "Insight Master" (③ negativo de T/L, positivo de PdM) **NÃO é fato confirmado**. Eraldo NÃO sente esse desbalanceamento. Pode ser viés de amostra pequena + sinal do próprio ajuste antecipado embutido no `param_real`.
- **Ação próxima sessão:** recalibrar texto da página Insights — "padrão DETECTADO, validar com mais dados" em vez de "desbalanceamento confirmado".
- Memória: `project_ajustes_antecipacao.md`

#### Descoberta 2 — Tachos parciais NÃO são desperdício (viram potes!)
- Quando Eraldo ordena `ord_prod_band = 18` (não-múltiplo de 8):
  - 16 bandejas → corte normal
  - 2 bandejas + sobra do 3º tacho → **potes 260g/605g**
- É **decisão intencional**, não erro.
- **Implicação:** Insight H1 (33% tachos parciais como "desperdício") está **errado conceitualmente**.
- **Ação próxima sessão:** remover/reformular H1 na página Insights. Pode virar "X% dos tachos foram aproveitados como potes — conversão de Y kg de cocada em Z potes".
- Memória: `project_tachos_parciais_potes.md`
- **Pendência:** Leonardo notou que 15/05 sobrou 36 kg de Pé de Moça mas só pediu 30 potes 260g (= 7,8 kg). Diferença não explicada. Vai perguntar ao Eraldo.

#### Descoberta 3 — RECEITA é por TACHO, não por formato (45g/Mini/Pet)
- Eraldo: *"A mesma receita que vai na tradicional 45g é a mesma que vai na mini, na pet, porque todas são tradicionais — só os formatos são diferentes."*
- **Implicação na Etapa B (Suprimentos):** as chaves de BOM precisam ser refatoradas:
  - Antes: `cocada_T_45g_band`, `cocada_T_Mini_band`, ...
  - Depois: **`cocada_T_tacho`** (única, por sabor)
- 1 tacho rende 8 bandejas (Z=3); divisão em formatos é decisão de corte/embalagem.
- **Receita Tradicional (1 tacho):**
  - 19 L leite in natura
  - 8 kg açúcar cristal
  - 4 kg coco ralado
  - 14 colheres de anti-mofo
  - 1 colher de sal
- **Variações por sabor (sobre Tradicional):**
  - L: substitui leite por 15 kg leite condensado *(confirmar — parece muito)*
  - C: + 5 sachês 40g café
  - B: + 500g cacau/brigadeiro
  - PdM: + amendoim (qtd pendente)
  - Z: substitui açúcar por adoçante zero (qtd pendente)
- **Ação próxima sessão:** atualizar `listar_produtos_possiveis()` em `database.py` (chaves por tacho) + ajustar página Suprimentos > Receitas (BOM) pra usar nova convenção.
- Memória: `project_receita_por_tacho.md`

#### Descoberta 4 — Mariana (pessoa nova) + Sigee Cloud tem insumos
- **Mariana** faz compras + controla estoque de insumos. Trabalha no escritório.
- **Sigee Cloud** tem: NF, Estoque, Vendas, NFE. NÃO faz PCP.
- **Insumos JÁ ESTÃO cadastrados no Sigee** — não precisamos digitar manualmente!
- **Plano de integração com Sigee** (memória `project_pessoa_mariana_e_sigee.md`):
  - **Opção A (rápida):** Mariana exporta CSV dos insumos do Sigee → script Python povoa nossa tabela `insumos`. Tempo: ~2h.
  - **Opção B (longo prazo):** API do Sigee — verificar se existe.
  - **Recomendação:** começar com A na próxima sessão pra destravar Etapas C+D.
- **Pendência:** Leonardo perguntar pra Mariana se ela consegue exportar CSV.

#### Descoberta 5 — Capacidade Embalagem é VARIÁVEL
- O threshold "3000 und/dia" da Leonília que o sistema usa em Insights NÃO é fixo.
- Varia conforme: quantas pessoas estão na embalagem + capacidade individual.
- Exemplo 15/05: só 1 rapaz embalando, capacidade reduzida → ordem reduzida (1800 und).
- **Ação próxima sessão:** considerar tornar o threshold do alerta H4 (sobrecarga embalagem) configurável. Ou esconder até ter mais dados de capacidade real.

#### Descoberta 6 — Detalhes operacionais (Bala/PM/ASS)
- **Papelzinho da Bala/PM:** existe, é separado. Eraldo confirmou.
- **Balas 15/05:** P/cortar 630 + Cortados 191 = subtotal 821 + Embalado 118 = total 939 balas
- **Pão de Mel 15/05:** 390 (provavelmente unidades; **REVISAR regra**: se cnt_pm está em DISPLAYS, deveria ser 39 displays; se em unidades, conflita com memória atual)
- **ASS (Cocada Assada):** produzido no dia, vai em campo `cocada_assada_und`
- **Ação próxima sessão:** revalidar regra do `cnt_pm` (unidades vs displays) com Leonardo.

#### Pendências reabertas (Leonardo vai responder depois)
- Bloco 4 inteiro (lista de insumos com fornecedor/lead time) — Mariana ajuda
- Receitas de Palha (Bloco 5)
- Quem produz Doces, frequência PM, dias palha (Bloco 7 — boa parte)
- Capacidade Joel em tachos/dia
- Mistério 36 kg PdM vs 30 potes
- Confirmar 15 kg leite condensado (parece muito)
- API do Sigee — Leonardo investiga

---

## 4. Pendências imediatas (bloqueadores ou esperando alguém)

### 4.1 ⏳ Questionário Eraldo (29 perguntas) — ESTÁ COM ELE
- Arquivo: `entrevistas/01_pcp_inicial.docx` (.pdf também)
- Status: respondendo no momento desta sessão (15/05 tarde)
- **Vai chegar respondido na próxima sessão.**
- Quando chegar, Leonardo vai mandar as respostas (transcrever no chat, ou commitar arquivo `entrevistas/01_pcp_inicial_respondido.md`)
- Próxima sessão: absorver respostas → cadastrar insumos (Etapa C) → cadastrar receitas/BOM (Etapa D) → atualizar `CADERNO.md` com aprendizados.

### 4.2 Folha de produção 15/05/2026 (sexta)
- Preenchida em `pcp-vo-nena.streamlit.app` (Leonardo testou ali mesmo)
- Dados no banco

### 4.3 Asteriscos no papelzinho
- Caso conhecido: às vezes Mini/Pet do papelzinho Joel já foi embalada antes da folha fechar → contagem dupla em Cortados②
- Solução atual: aviso visual + obs no campo
- Solução futura (Fase 1.5): checkbox por célula

### 4.4 Tabela `estoque` (legada)
- Tem 25 linhas de seed inicial
- Não foi migrada do SQLite local pro Postgres (script de migração só toca 4 tabelas de folha)
- Hoje: usada só pra alertas no sidebar do Painel
- Decidir destino: migrar de fato OU substituir pela nova lógica de Suprimentos

---

## 5. Plano para a próxima sessão (em ordem de prioridade)

### Prioridade 0 — Recalibrar Insights com descobertas do Eraldo (rápido, ~30 min)

Antes de migrar/cadastrar nada, ajustar a página `pages/2_Insights.py`:

1. **H1 (Tachos parciais)** — REMOVER ou REFORMULAR. Não é desperdício, é conversão pra potes.
2. **Insight Master (desbalanceamento T/L × P)** — atenuar texto. Em vez de "está faltando T", dizer "Sistema detectou padrão. Confirmar com Gestão se há motivo (ex: pedidos antecipados)."
3. **H4 (Sobrecarga Embalagem 3000)** — threshold variável; talvez esconder ou pedir input dinâmico.
4. **H5 (anomalia palha LP>T)** — manter (Eraldo aprovou).

### Prioridade 1 — Migração para Hugging Face Spaces

**Decisão:** Leonardo quer migrar. Motivo principal: HF Spaces tem **16 GB de RAM** (vs 1 GB Streamlit Cloud Free), não dorme, é gratuito.

**MAS Leonardo tem receio de perder o que já está funcionando.** Plano de migração com **rollback seguro**:

#### Estratégia: NÃO derrubar Streamlit Cloud até HF Spaces estar 100% validado.

| Fase | Ação | Risco se der errado |
|---|---|---|
| **1. Criar Space no HF** | Conta HF (login Google), criar Space novo apontando pro mesmo repo GitHub | Zero — Streamlit Cloud continua intocado |
| **2. Configurar secrets HF** | DATABASE_URL no painel HF (mesmo Supabase) | Zero |
| **3. Adicionar README.md com YAML header** | HF exige (sdk: streamlit, app_file: lancamento.py) | Pode quebrar se errar formato, mas é só editar |
| **4. Testar em paralelo** | Acessar `huggingface.co/spaces/leonardosoglia/pcp-vo-nena` por uma semana | Zero — Streamlit Cloud continua |
| **5. Comparar:** velocidade, estabilidade, custo de manutenção | Anotar prós/contras observados | Zero |
| **6. SE HF Spaces der certo → descomissionar Streamlit Cloud (deletar app + keepalive workflow)** | Trocar URL na ficha de entrevista + comunicação com Eraldo | Pode-se voltar Streamlit Cloud em ~30 min se precisar |
| **7. SE HF Spaces der problema → manter Streamlit Cloud, fechar Space** | Sem perda | Zero |

**Custo estimado de migração:** ~30-45 min de trabalho (setup + teste).

**O que NÃO muda:**
- Código Python (mesmo lancamento.py, pages/, etc.)
- Banco de dados (mesmo Supabase Postgres)
- Repo GitHub (mesmo)

**O que muda:**
- URL do app (`*.streamlit.app` → `huggingface.co/spaces/...`)
- Plataforma de hosting
- Como deployar (HF tem fluxo próprio)

### Prioridade 2 — Receber e absorver respostas do questionário Eraldo

Quando Leonardo mandar:

1. Ler todas as 29 respostas
2. Cadastrar insumos na aba 📦 Insumos (Etapa C) — provavelmente 30-50 itens
3. Cadastrar receitas (BOM) na aba 📋 Receitas (Etapa D) — provavelmente 20-30 produtos
4. Atualizar `CADERNO.md` (seção 3 → seção 1 e 2) com respostas
5. Atualizar `CLAUDE.md` com regras de negócio novas descobertas
6. Salvar memórias persistentes pra descobertas críticas
7. Conferir se o cálculo de Necessidades faz sentido com dados reais

### Prioridade 3 — Introdução gradual de IA / Machine Learning

Leonardo quer começar a usar IA. **Não posso prometer mágica.** Plano realista abaixo na seção 6.

### Prioridade 4 — Bugs conhecidos pra corrigir

| Bug | Reportado | Prioridade |
|---|---|---|
| Gráficos plotly quebram no celular ao tocar | 15/05 | ✅ Resolvido com `displayModeBar: False` |
| Tema dark forçado pelo sistema | 15/05 | ✅ Resolvido com config.toml |
| Cores escuras ilegíveis em dark mode | 15/05 | ✅ Resolvido (tema light forçado) |
| Necessidade visual de Viradas② + ord_prod_virada lado a lado | 15/05 | Pendente — UX melhoria pra próxima sessão |

---

## 6. Sobre IA e Machine Learning (visão honesta — LEIA)

Leonardo quer começar a usar IA. **Eu preciso ser honesto com ele:**

### ❌ O que IA / ML NÃO faz com 30 dias de dados:
- Previsão precisa de demanda (preciso 6+ meses)
- Otimização complexa (preciso modelar todas as restrições, custos, capacidades)
- "Entender" a empresa autonomamente
- Sugerir ordens com confiança alta

### ✅ O que IA / ML pode fazer JÁ com poucos dados:
- **Detecção de anomalias estatística** (Isolation Forest, Z-score) — melhora a regra "LP > T+30%" atual
- **Curva ABC de sabores** (clustering simples) — quem gira muito, médio, pouco
- **Projeção simples de demanda** (média móvel ponderada por dia da semana) — funciona razoável com 4 semanas de dados
- **Detecção de tendência** (slope da regressão linear) — vendas subindo/caindo

### 🤖 LLM (Claude API) como "assistente cognitivo" — pode usar AGORA:
- Adicionar botão "Pergunte ao Claude" no app
- Quando usuário aperta, sistema manda contexto (folha atual + métricas + descobertas do CADERNO) + pergunta pro Claude API
- Resposta volta em ~2-3 segundos
- Casos de uso:
  - "Por que o sistema está sugerindo cortar 20 bandejas de T hoje?"
  - "Onde estamos perdendo mais venda este mês?"
  - "Qual sabor tá com viés mais positivo?"
- **Custo:** R$ 0,01 a R$ 0,10 por consulta (Claude Haiku é barato)
- **Tempo de implementação:** ~3-4h. Pode ser feito antes do TCC e vira capítulo bonito.

### 🎓 Pro TCC:

Recomendação minha (Claude da próxima sessão deve seguir):
- **Capítulo 4 (Implementação):** descrever Camada 1 atual (regras heurísticas, detecção de anomalia LP>T)
- **Capítulo 4.5 ou seção dentro de 4 (IA Aplicada):** implementar 1-2 técnicas estatísticas/ML simples:
  - Detecção de anomalia com Isolation Forest
  - Projeção de demanda com média móvel + sazonalidade dia da semana
  - Botão "Pergunte ao Claude" no app
- **Capítulo 5 (Resultados):** mostrar que as técnicas detectaram anomalias reais e ajudaram nas decisões
- **Capítulo 6 (Trabalhos Futuros):** dizer que com 6+ meses de dados, modelos preditivos vão ficar muito melhores

### ❗ O que NÃO prometer ao Leonardo:
- "Sistema vai aprender sozinho" (vai aprender com dados — precisa tempo)
- "Vai prever exato o que produzir" (sugere, ele aprova/ajusta)
- "Vai eliminar trabalho do Eraldo" (vai amplificar a capacidade dele, não substituir)

---

## 7. Como funciona o sistema NA PRÁTICA (visão alinhada com Leonardo)

Pra próxima sessão entender a visão de uso real:

### Fluxo do dia típico (depois de tudo pronto):

1. **7h-10h:** Leonardo conta estoque (acabado + semiacabado) no chão de fábrica → digita no app
2. **~10h:** Eraldo abre o app no notebook/celular:
   - **Painel** mostra: Cortados ②③, Viradas, P/Virar, alertas
   - **Insights** mostra: padrão de excesso/falta semanal, anomalias
   - **Suprimentos > Necessidades** mostra: o que vai precisar comprar nos próximos dias
3. **~10h30:** Eraldo define ordens olhando: estoque + semiacabado + parâmetro + mão-de-obra + pedidos + (defensivamente) insumos
4. **Eraldo salva folha:**
   - (Etapa E futura) Sistema baixa automaticamente insumos consumidos
   - Painel atualiza pra cada departamento
5. **11h-18h:** cada departamento (Joel/Gil/Leonília/Maria) abre sua aba no celular, executa
6. **Fim do dia:** Eraldo confere o que foi produzido vs planejado, sistema mostra alertas pendentes

### O que importa:
- **Reduzir tempo gasto** preenchendo papel (de 18 min → 6 min)
- **Eliminar erros** de cálculo
- **Visibilidade histórica** instantânea (consulta em segundos vs procurar pasta por minutos)
- **Antecipar problemas** (insumo acabando, sabor sobrando crônico)

### O que NÃO importa (na visão do Leonardo):
- Sistema dirigir decisões — ele complementa, não substitui Eraldo
- Controle obsessivo de cada grama de insumo — Eraldo trabalha por estoque
- Features complexas que ninguém usa

---

## 8. Estrutura técnica resumida (pra orientação)

### Arquivos principais
- `database.py` — schema, CRUD, conexões. Backend dual SQLite/Postgres. Pool psycopg.
- `cached_db.py` — wrappers `@st.cache_data` (TTL folhas 5min / refs 24h / Suprimentos 5min). `invalidar_folha()` + `invalidar_suprimentos()` chamados após save/delete.
- `lancamento.py` — entry point Streamlit. Formulário diário da folha.
- `pages/1_Painel.py` — visualização por departamento.
- `pages/2_Insights.py` — diagnóstico operacional automático (6 hipóteses).
- `pages/3_Suprimentos.py` — **NOVO 15/05** — 4 abas (Insumos, BOM, Movimentações, Necessidades).
- `analise.py` — importado pela aba Análise do Painel. Curva ABC inicial.
- `.github/workflows/keepalive.yml` — anti cold-start.
- `.streamlit/config.toml` — tema light forçado + paleta Vó Nena.

### Banco Supabase (Postgres 17.6, sa-east-1)
**Tabelas de Folha:**
- `folha_cocada`, `folha_palha`, `papelzinho_joel`, `folha_pm_balas_doces`

**Tabelas de Referência:**
- `metas_45g`, `metas_mini_pet`, `metas_potes`, `parametros_pvirar_ideal`, `conversoes`, `estoque`

**Tabelas de Suprimentos (Etapa B, novas):**
- `insumos`, `bom_produto`, `movimentos_insumo`

### Constantes/helpers de domínio em `database.py`
- `SABORES_COCADA`, `SIGLA_COCADA` (T, L, B, C, P, Z)
- `SABORES_PALHA`, `SIGLA_PALHA` (T, L, CH, CK, LIM)
- `SABORES_PALHA_50G` (T, L, CH)
- `CATEGORIAS_INSUMO` (matéria-prima, embalagem, pote, cinta, display, outros)
- `UNIDADES_INSUMO`, `TIPOS_MOVIMENTO`, `ORIGENS_MOVIMENTO`
- `chave_produto_cocada(sabor, tamanho)` → `cocada_T_45g_band`
- `chave_produto_palha(sabor, tamanho)` → `palha_L_50g_band`
- `listar_produtos_possiveis()` → lista pra dropdown da UI BOM

---

## 9. Como me ajudar bem (postura — válido pra próxima sessão também)

**Pra próxima sessão Claude Code:**

- **Postura técnica:** especialista em PCP (Eng. de Produção) + software (Python sênior). Tom didático mas direto. Não simplifica prematuramente. Argumenta decisões.
- **Tom:** PT-BR informal mas profissional. Sem floreios.
- **Antes de codar:** **identifica inconsistências** com o fluxo real da fábrica. **Pergunta** se algo não bate.
- **Código:** sempre completo. Sem placeholders. Pedaços validáveis antes do próximo.
- **Unidades:** explícitas sempre (kg vs L vs und vs band vs tacho). Nunca misturar.
- **Decisões arquiteturais:** explica o **porquê** — vira capítulo do TCC.
- **Memória persistente:** salva descobertas importantes em `~/.claude/projects/.../memory/`. Atualiza `MEMORY.md` (índice).
- **CADERNO.md:** atualiza com cada conversa relevante (descobertas, perguntas, hipóteses).

**Sobre o Leonardo:**
- Estagiário Eng. Produção (UFCG P10)
- Reside em SP pro estágio + TCC
- Leigo em programação (mas absorvendo bem)
- Profundo conhecedor do domínio PCP/Vó Nena
- Tempo curto até defesa (~9 semanas)
- Quer construir algo IMPACTANTE pro TCC e pra fábrica

**Princípios:**
- **Fidelidade ao papel antes de automação.** Sistema espelha papel; depois automatiza.
- **Departamentos > nomes próprios** na UI (decidido 14/05).
- **PCP > Suprimentos > IA** (em ordem de prioridade da atenção).
- **Validação humana sempre** — sistema sugere, Eraldo decide.

---

## 10. Primeira ação da próxima sessão

Quando Leonardo abrir a sessão nova, **ele deve:**

1. Mandar mensagem inicial tipo *"continua de onde paramos"* ou similar
2. **Eventualmente:** mandar respostas do questionário Eraldo

Você (Claude) deve:

1. **Ler:**
   - Este arquivo (`CONTEXTO_SESSAO_ANTERIOR.md`) — onde paramos
   - `CLAUDE.md` — referência técnica
   - `CADERNO.md` — diário do projeto
   - Memórias persistentes em `~/.claude/projects/.../memory/`
2. **Resumir** pra ele em 5-7 linhas: "Estamos em X, próximo passo é Y, você tinha pendência Z."
3. **Perguntar:** "Você quer (a) começar a migração HF Spaces, (b) já tem o questionário pra processar, ou (c) outra prioridade?"
4. **Não tomar atitude antes do alinhamento.**

---

## 11. Resumo executivo das decisões pendentes

| Decisão | Status | Responsável |
|---|---|---|
| Migrar pra HF Spaces | ✅ Decidido (com rollback seguro) | Claude próxima sessão executa |
| Implementar Etapa C/D | ✅ Aguarda questionário | Leonardo + Claude próxima sessão |
| Implementar Etapa E (auto-baixa) | Programado pra 22-29/05 | Claude futuras sessões |
| Implementar IA (LLM "Pergunte ao Claude") | A discutir na próxima | Decisão conjunta |
| Voltar repo pra privado | Pendente — deixar público até HF Spaces validado | Leonardo |

---

**Fim do handoff. Sessão atual encerrada em 15/05/2026.**

*Boa sorte na próxima sessão. Quando o Eraldo te der as respostas, o projeto destrava.*
