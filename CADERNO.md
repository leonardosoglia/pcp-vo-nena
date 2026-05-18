# Caderno de Campo — PCP Vó Nena

> **Propósito:** ponto único pra consolidar o que descobrimos, o que precisamos perguntar, e o roadmap até a defesa do TCC (~18/07/2026).
>
> Não é doc técnico (esse é `CLAUDE.md`). É o **diário do projeto** — atualizado conforme avançamos. Hipóteses, validações, ideias soltas, perguntas pra Gestão/Produção/Corte/Embalagem — tudo entra aqui pra não se perder.

---

## 0.3 Migração para Hugging Face Spaces — 17/05/2026

**Plataforma de hospedagem trocada de Streamlit Community Cloud → Hugging Face Spaces.**

### Por quê

| Critério | Streamlit Cloud Free | HF Spaces Free |
|---|---|---|
| RAM | 1 GB | **16 GB** |
| CPU | ~1 vCPU compartilhado | 2 vCPU |
| Sleep | poucas horas | 48h |
| Versão Streamlit | qualquer | qualquer (via Docker) |
| Ecosistema ML/IA | nenhum | hub de modelos + datasets |

Razão estratégica: capacidade pra Fase 3 do ROADMAP_IA (LLM "Pergunte ao Claude") + portfólio público pro TCC.

### Como
- **`Dockerfile`** novo no repo (Python 3.13-slim, user uid 1000, streamlit headless 8501)
- **`README.md` YAML header** (`sdk: docker`, `app_port: 8501`, `colorFrom: red`, `colorTo: yellow`)
- **Git LFS** configurado pra `*.pdf`, `*.docx`, `*.xlsx` (HF rejeita binários inline)
- **2 remotes git:** `origin` (GitHub → Streamlit Cloud) e `hf` (Hugging Face)
- Streamlit Cloud **mantido no ar** durante validação paralela

### Problemas encontrados + lições
1. `sdk: streamlit` no HF tá deprecado — força versão 1.25.0 antiga. **Solução:** Docker SDK.
2. `colorFrom` só aceita 8 cores específicas (não tem `orange`). **Solução:** `red` + `colorTo: yellow`.
3. PDFs/DOCXs no histórico do git impediam push. **Solução:** Git LFS migrate import.
4. Force push da pasta principal sobrescreveu commits do worktree. **Lição:** sempre fetch antes de force push se trabalho está em múltiplas branches.

### Performance pós-migração
- Primeira observação do Leonardo: navegação entre datas ~1 min (anormal)
- **3 quick wins aplicados** (commit `3424897`):
  - TTL do cache: 5min → 30min
  - Pre-warm no startup (`@st.cache_resource` chamando `list_datas_folha`, `metas_45g`, etc.)
  - Pool psycopg `min_size 2→4`, `max_size 5→8`
- Validação pendente após rebuild do HF

### Adendo de IA / ML (palavras do Leonardo)

> *"Eu quero uma plataforma muito interessante, a fim de trazer essa visão diferencial pra ela crescer pra todas as partes. Essa coisa de IA quero muito. Inclusive se você tiver outras possibilidades, outras ferramentas, mesmo que seja pago, você me fala."*

Sinal verde pra Claude API (~R$1/mês uso típico), Supabase Pro se necessário, features pagas que agreguem.

### Insight crítico do Leonardo sobre Vendas — 17/05/2026

> *"A Curva ABC mostra o que é produzido, não o que é vendido. Leonília organiza pedidos por destino (quiosques, feiras...). A gente não tem essas informações."*

**Diagnóstico:** o módulo de **Vendas** é o **buraco central** que falta no sistema. Sem ele:
- Curva ABC mede produção, não venda real
- Não é possível medir perda de venda real (só perda de produção vs parâmetro)
- Insights de demanda ficam "às cegas"

**3 caminhos identificados:**
1. **Ficha pra Leonília** — como controla pedidos hoje (caderno? planilha? mental?)
2. **Sigee Cloud** — Mariana confirma se tem vendas por produto+data+cliente → CSV
3. **Módulo Pedidos no sistema** — tabelas `pedidos` + `pedido_item` (só se 1 e 2 falharem)

**Status:** **PRIORIZADO PRA DEPOIS DA FASE 1 ML**. Leonardo decidiu (17/05) focar em IA primeiro. Retomar após Detecção de Anomalia + Média Móvel.

**Pra próxima sessão:** quando começar trabalho com Vendas, atacar Caminhos 1+2 em paralelo. Caminho 3 é Plano B.

**Próximos passos imediatos:**
- ✅ **Fase 1 ML COMPLETA (17/05/2026)** — adiantada do prazo original (22-29/05):
  - Curva ABC (`pages/4_Curva_ABC.py`) — diagrama de Pareto + classificação 80/95
  - Detecção de Anomalia (`pages/5_Anomalias_ML.py`) — Isolation Forest com features de estoque + fluxo
  - Média Móvel (`pages/6_Media_Movel.py`) — comparativo base × observado por sabor × dia da semana
- **Fase 2 ML** (semana 22-29/05, ~10h): Detecção de tendência + projeção Prophet
- **Fase 3 LLM** (semana 29/05-12/06, ~4h): Botão "Pergunte ao Claude" (Claude Haiku 4.5 via API)
- **Módulo Vendas** (após Fase 3 ou paralelo): ficha pra Leonília + integração CSV Sigee — depende de respostas pendentes

**Correção crítica 17/05/2026 (insight do Leonardo):** Curva ABC inicialmente usava
`emb_*` (estoque snapshot) somado entre dias = erro estatístico clássico. Corrigido
para `ord_corte_*` (fluxo de bandejas — pode ser somado dia a dia). Detecção de
Anomalia também reforçada com features de fluxo. Princípio stock vs flow
(Forrester 1961) agora respeitado no sistema todo. Vai pro Cap 4 do TCC.

Detalhes em `ROADMAP_IA.md`.

---

## 0.5 Reposicionamento estratégico — 15/05/2026

**Após Etapa B estar pronta, Leonardo recalibrou a visão do projeto:**

> *"Nessa parte de insumos, eu não conto insumos, o que eu conto é o estoque e produto semiacabado e produto acabado. Na verdade o Eraldo não produz olhando insumos."*

A fábrica trabalha com **3 categorias de "coisa medida"**:

| Categoria | O que é | Onde no sistema |
|---|---|---|
| **Insumo** (matéria-prima) | Coco, leite condensado, plástico, cinta | Suprimentos (Etapa B feita 15/05) |
| **Produto semiacabado** | Bandejas cortadas mas não embaladas; massa virada | Folha (cort1_*, joel_pv, joel_v) |
| **Produto acabado** (estoque) | Cocada embalada pronta pra venda | Folha (emb_*) |

**Implicação:**
- O **coração** do sistema é a Folha + Painel + Insights (Camadas 0+1)
- Suprimentos é **suporte defensivo:** avisa sobre falta antes de virar problema
- Eraldo decide ordens olhando estoque + semiacabado + parâmetro + mão-de-obra + pedidos
- Insumos entra como CONTEXTO ("vou ter coco pra ordenar 24 bandejas?"), **não como driver**

**Pra próxima sessão:** priorize features que reduzam tempo/erro no fluxo principal do PCP. Insights e IA agregam **se forem práticos** — não criar feature complexa que ninguém vai usar.

---

## 0. Virada conceitual — 14/05/2026

**O projeto evoluiu de "PCP de produção" para "PCP completo de empresa".**

A diferença na prática:

| PCP só de produção (até 13/05) | PCP completo (a partir de 14/05) |
|---|---|
| Folha do dia → ordem de produção → fim | Folha do dia → ordem → **BOM** → necessidade de insumo → **almoxarifado/suprimentos** → sugestão de compra → fim |
| Sistema sabe **o que** produzir | Sistema sabe o que **e como** produzir (insumos disponíveis, quanto consome, quando comprar) |
| Camada 1 (visualização) está madura | Camada 1.5 (semi-automação real via auto-baixa de insumos) é o próximo salto |

**Conceitos aplicados (úteis pra revisão de literatura do TCC):**
- **MRP** (Material Requirements Planning): explosão de necessidades a partir da BOM.
- **BOM** (Bill of Materials): receita do produto — quanto de cada insumo é necessário.
- **Ponto de pedido** e **estoque de segurança**: gatilhos pra disparo de compra.
- **Lead time de compra**: tempo entre pedido ao fornecedor e chegada do insumo.
- **Curva ABC**: priorização por giro/valor (insumos críticos vs commodities).
- **JIT** (Just-In-Time): visão futura — pedir só o que vai precisar.

**Por que isso é fundamental:**
1. Hoje a fábrica trabalha "no feeling" pra reposição. Sistema vai antecipar.
2. Evita PARADAS por falta de insumo (pior pesadelo de chão de fábrica).
3. Vira capítulo brilhante do TCC ("Aplicação de MRP simplificado em confeitaria industrial").
4. Conecta com Sigee Cloud (ERP da empresa) — possível integração futura.

**Nome escolhido pro módulo:** **Suprimentos** (mais amplo que "Almoxarifado") — engloba matéria-prima, embalagens, potes, cintas, qualquer item consumível.

---

## 1.0 Respostas do Eraldo ao questionário (15/05/2026, parcial)

Leonardo levou ficha (`entrevistas/01_pcp_inicial.docx`) pro Eraldo. Eraldo respondeu Blocos 1-3 + parte do 5/6/7. Blocos completos virão depois.

### Bloco 1 — Insight Master (desbalanceamento)

**Q1 — Sente padrão de falta T/L e sobra Pé de Moça?**
> *"Na verdade eu não sei. Você sente que esses sabores Tradicional e Leite estão faltando, talvez porque eu fiz que para esses 2 sabores sejam produzidos em maior quantidade porque eles saem bastante. Aí talvez o sistema fechou que eu fizer muito eles estão faltando, mas não. Eu também não sinto pé de moça sobrando, ok, realmente talvez pareça sobrar por sempre ter ali no estoque acima, mas de momento isso não tem me incomodado. Talvez o recorte de poucos dias tenha te passado essa imagem de estar sobrando."*

**Eraldo NÃO confirma o desbalanceamento.** Hipótese: viés de amostra pequena (13 folhas). Recalibrar Insight Master pra: "Padrão DETECTADO, validar com mais dados."

**Q2 — Por que proporção T/L oscila tanto? Capacidade?**
> Não é capacidade. **São pedidos antecipados.** Eraldo aumenta `param_real` pra distribuir pedido futuro ao longo dos dias da semana.
>
> Exemplo (15/05, quinta):
> - Param base do dia: T=6800, L=3400, B=1700, C=1700, P=1700
> - Pedido pra próxima semana: T+1500, L+200, B+200, C+200, P+400
> - `param_real` do dia incorpora esse ajuste distribuído

→ **Memória persistente:** `project_ajustes_antecipacao.md`. Implicação: muitas das "anomalias" detectadas podem ser ajustes intencionais.

**Q3 — Pé de Moça que sobra vai pra onde?** *Não está sobrando hoje. (Mesma resposta da Q1)*

**Q4 — Demanda fixa de Pé de Moça?** *"Não tem!"*

**Regra confirmada:** T = 2×L; L = 2×B = 2×C = 2×P. Ou seja, **T : L : B : C : P = 4 : 2 : 1 : 1 : 1** (em 45g).

### Bloco 2 — Tachos parciais

**Q5 — Quando ordena tacho parcial (18 band), o que vai pra:**
> ✅ **"Vira potes do mesmo sabor"** (260g ou 605g)

→ **DESCOBERTA CRÍTICA:** tacho parcial NÃO é desperdício. É decisão intencional.

**Q6 — Tachos parciais por planejamento ou urgência?** *Planejamento normal — sobra do tacho vai pra potes.*

**Q7 — Sugestão de arredondamento útil?** *Não muito útil — o "parcial" já é intencional.*

→ **Memória persistente:** `project_tachos_parciais_potes.md`. **Recalibrar Insight H1.**

**Regras de peso confirmadas:**
- 1 bandeja recém-tacho: ~6 kg (úmida)
- 1 bandeja pronta pra corte (após viração+descanso): ~5,5 kg
- **500 g perdidos** "pela interferes, evaporação" (palavras do Eraldo)

### Bloco 3 — Anomalias palha + embalagem

**Q8 — Anomalia palha LP > T (04/05 e 06/05)?** *"Sim, me parece que nesses dias realmente foi maior."* — **Confirmado.** Eraldo gostou: *"é interessante que o sistema sempre entregue isso."* Manter detecção.

**Q9 — Em dias com >3000 und embalagem, o que acontece?**
> *"Às vezes tem mais pessoas na embalagem, ou existem pessoas com capacidade maior."*
> *"A capacidade de 3000 não é fixa, varia."*
> *"Hoje (15/05) só tinha um rapaz lá embalando, ordenado 1400 T 45g + 400 L 45g."*

→ **Capacidade Embalagem é VARIÁVEL.** Sistema não deveria usar threshold fixo de 3000.

**Q10 — Capacidade real?** Variável (depende de quantas pessoas + capacidade individual). No início tinha "uma menina que embalava pouco", depois um rapaz que embala mais.

### Bloco 5 — Receitas (BOM)

**Q17 — Receita de Cocada Tradicional (1 TACHO):**

| Insumo | Quantidade |
|---|---|
| Leite in natura | 19 L |
| Açúcar cristal | 8 kg |
| Coco ralado | 4 kg |
| Anti-mofo (aditivo) | 14 colheres de sopa |
| Sal | 1 colher |

**Q18 — Receita varia por formato (45g/Mini/Pet)?**
> *"Sim, a mesma receita que vai na tradicional 45g é a mesma que vai na mini, na pet, porque todas são tradicionais, só que os formatos são diferentes."*

→ **DESCOBERTA CRÍTICA:** receita é POR TACHO (sabor), não por formato. Reformular BOM. Memória: `project_receita_por_tacho.md`.

**Variações por sabor (sobre a receita Tradicional):**
- **Leite Condensado:** substitui leite por **15 kg de leite condensado** (atenção: muito! confirmar)
- **Café:** + 5 sachês de 40g de café (200g total)
- **Brigadeiro:** + 500g de cacau/brigadeiro
- **Pé de Moça:** + amendoim (quantidade pendente)
- **Zero:** substitui açúcar cristal por adoçante zero (quantidade pendente)

**Q19 — Receitas de Palha?** *Pendente, Leonardo ainda não sabe.*

### Bloco 6 — Sigee Cloud

**Quem faz compras / controla insumos:** **Mariana** (pessoa nova mapeada).

**Sigee Cloud tem:** Estoque, Vendas, NF, NFE. **NÃO tem PCP.**

**Insumos JÁ ESTÃO cadastrados no Sigee** — não precisamos digitar manualmente.

**API do Sigee:** Eraldo não sabe se existe. **Pendência crítica.**

→ **Memória persistente:** `project_pessoa_mariana_e_sigee.md`.

### Bloco 7 — Operação geral

**Q25 — Papelzinho Bala/PM existe?** Sim — *"é pra contar quantas balas nós temos na empresa."*

**Balas hoje (15/05):**
- Para cortar: 630
- Cortados (semiacabado): 191
- Subtotal: 821
- Embalado/acabado: 118
- Total na fábrica: 939

**Pão de Mel hoje:** 390 (provavelmente unidades; revisar regra `cnt_pm` em DISPLAYS vs unidades).

**Cocada Assada (ASS):** quantidade produzida no dia.

**Demais perguntas do Bloco 7:** pendentes.

### Pendências reabertas (Leonardo vai perguntar depois)

- Lista de insumos completa (Bloco 4)
- Estoque mínimo / fornecedor / lead time por insumo
- Quem produz Doces, frequência PM, dias palha
- Capacidade Joel em tachos/dia
- Mistério dos 36 kg de Pé de Moça vs 30 potes
- Confirmar 15 kg leite condensado (parece muito)
- API do Sigee
- Receitas de Palha

---

## 1. INSIGHT MASTER — Desbalanceamento sistemático na produção (13/05/2026)

**⚠️ RECALIBRAR (15/05):** O Eraldo NÃO confirma o desbalanceamento. Pode ser viés da amostra pequena (13 folhas) + ajustes de pedidos antecipados embutidos no `param_real`. Manter detecção como **sinal pra investigar**, NÃO como "fato confirmado".



Análise das **13 folhas** registradas entre 02/04/2026 e 12/05/2026 (9 com parâmetro real preenchido) revelou padrão consistente que **explica perda de venda + encalhe simultâneos**.

### 1.1 Os números

| Sabor / Tamanho | ③ médio (und/dia) | ③ acumulada (9 dias) | Interpretação |
|---|---:|---:|---|
| **TRADICIONAL 45g** | **−272** | **−2.444** | Faltou estoque crônicamente |
| **LEITE CONDENSADO 45g** | −231 | −2.081 | Faltou estoque crônicamente |
| **ZERO Mini** | −454 | −4.084 | Faltou Zero crônicamente |
| BRIGADEIRO 45g | +110 | +992 | Sobrou |
| **PÉ DE MOÇA 45g** | **+392** | **+3.528** | **Sobra crônica — risco encalhe/validade** |
| TRADICIONAL Mini | +148 | +1.334 | Sobrou |

### 1.2 Razão T/L observada × esperada

A regra do Eraldo: **T = 2×L = 4×B/C/P** (45g em und).

Realidade nas 11 folhas com EMBALADOS preenchido:
- T/L esperado: 2.00 · **observado: 0.77 a 3.33** (variação enorme)
- T/(B+C+P) esperado: 1.33 · **observado: 0.63 a 1.34**

### 1.3 Diagnóstico

A produção simultaneamente:
- **Perde venda** (T, L, Zero em déficit)
- **Encalha estoque** (Pé de Moça em excesso)

Isso é o "pior dos dois mundos" em PCP. Hipóteses pra investigar:
- Eraldo subestima demanda de T/L?
- Equipe é mais rápida em produzir sabores secundários (B/C/P) e prioriza eles?
- Há demanda específica de cliente em Pé de Moça não capturada no parâmetro?
- Erros de contagem (asteriscos no papelzinho) mascaram o problema?

### 1.4 Por que isso é ouro pro TCC

É exatamente o tipo de achado que **justifica academicamente o sistema**: o sistema digital revelou um padrão operacional invisível no papel. Vira o **achado principal do capítulo 5 (Resultados)**.

---

## 2. Outros achados das 13 folhas (13/05/2026)

### 2.1 Capacidade ociosa de tacho

**33% das ordens de produção saíram com tacho parcial** (9 de 27 ordens com `ord_prod_band > 0`).

| Data | Sabor | Bandejas ordenadas | Tachos cheios | Sobra |
|---|---|---:|---:|---:|
| 04/05 | TRADICIONAL | 20 | 2 | 4 band soltas |
| 04/05 | ZERO | 2 | 0 | 2 band soltas |
| 05/05 | TRADICIONAL | 28 | 3 | 4 band soltas |
| 05/05 | ZERO | 2 | 0 | 2 band soltas |
| 07/05 | LEITE CONDENSADO | 7 | 0 | 7 band soltas |
| 11/05 | TRADICIONAL | 18 | 2 | 2 band soltas |
| 11/05 | ZERO | 2 | 0 | 2 band soltas |
| 12/05 | BRIGADEIRO | 7 | 0 | 7 band soltas |
| 12/05 | ZERO | 5 | 1 | 2 band soltas |

**Interpretação:** quando Eraldo ordena 7 bandejas em vez de 8 (ou 18 em vez de 16/24), o tacho sai parcial → ingrediente extra precisa ir pra outro produto, ou é descartado, ou alguém complementa. Não sabemos.

### 2.2 Anomalias palha (Leite em Pó > Tradicional + 30%)

**2 anomalias detectadas** nas 13 folhas pela regra atual da Camada 1:
- **04/05/2026:** T=4 band, L=12 band → razão L/T = 3.00
- **06/05/2026:** T=4 band, L=14 band → razão L/T = 3.50

Validar com Eraldo: tinha pedido específico de Leite em Pó esses dias?

### 2.3 Sobrecarga de embalagem

**2 de 13 folhas** tiveram ordem total de embalagem > 3000 und (capacidade aproximada da Leonília):
- 04/05: 3.114 und
- 05/05: 3.200 und

Pequeno excesso. Pergunta: nesses dias, Leonília ficou até tarde, ou outro funcionário ajudou?

### 2.4 Lead time real — INCONCLUSIVO

Só 3 pares de dias com gap de 3 dias úteis disponíveis. Várias folhas históricas têm só Embalados preenchido (cascas das datas 23/04, 28/04, etc.), o que impede a correlação P/Virar(d) → Cortados①(d+3). **Precisa de série de 3+ dias consecutivos completos pra validar.** Coletar nas próximas semanas.

---

## 3. Perguntas pendentes — em ordem de prioridade

### 3.1 Pra Gestão (entrevista presencial)

#### Sobre o INSIGHT MASTER (urgente — fundamento do capítulo 5)
1. Você sente que falta Tradicional/Leite Condensado e sobra Pé de Moça?
2. Por que a proporção T/L observada varia tanto (0.77 a 3.33) vs esperado 2.0?
3. Pé de Moça que sobra vai pra onde? Pote? Vencimento? Doação?
4. Existe demanda específica de cliente em Pé de Moça que não está no parâmetro?

#### Sobre tachos parciais (H1)
5. Quando produz 18 band de Tradicional em vez de 16 ou 24, o ingrediente extra:
   - (a) vira potes do mesmo sabor?
   - (b) é guardado pra próximo tacho?
   - (c) é descartado?
6. Tachos parciais acontecem por necessidade (urgência de cliente) ou por planejamento?

#### Sobre embalagem (H4)
7. Em dias com > 3.000 und embaladas, Leonília fica até tarde ou outro ajuda?
8. Qual o custo de hora extra? (Pra estimar perda real)

#### Sobre anomalias palha (H5)
9. Nos dias 04/05 e 06/05, teve encomenda específica de Leite em Pó?
10. Ou foi erro de digitação/lançamento?

#### Pendentes do CLAUDE.md (sessão 1)
11. Frequência exata de produção de PM (dias da semana?)
12. Existe papelzinho separado pra Bala/PM? Qual formato?
13. Dias exatos de corte de palha (Maria — confirmar Seg/Ter + Qui/Sex?)
14. Quem produz Doces? Eraldo pergunta a quem diretamente?
15. Capacidade típica do Joel em tachos/dia?
16. Como funcionam encomendas de cliente? Afetam o parâmetro do dia?

### 3.2 Pra Produção
17. Quando recebe ordem de 18 band, complementa pra 24 por iniciativa, ou produz exatos 18?
18. Quanto tempo leva pra "trocar de sabor" (set-up entre Tradicional → Brigadeiro)?

### 3.3 Pra Embalagem
19. Capacidade real: ~3.000 und/dia confirmada? Tem dias melhores/piores?
20. Quando sobra cortado mas não embalado, fica onde? Validade?

### 3.4 Pra Corte / Embalagem (operacional)
21. Cortados ③ persistentemente positivo: vocês "param de cortar" quando vêem que tá sobrando, ou seguem a ordem do Eraldo?
22. Asterisco no papelzinho (qty já enviada à embalagem): com que frequência acontece?

---

## 4. Ideias e oportunidades de redução de custo / desperdício

### 4.1 Já implementáveis (rodam nos dados atuais)
- **Curva ABC de sabores** (giro alto/médio/baixo) — orientar produção/estoque
- **Análise de Cortados ③ histórico** — ranking de sabores com excesso/falta
- **Alerta de tacho parcial** — sistema avisa "ordem 18 band; arredondar pra 16 (poupar 2) ou 24 (produzir mais 6)?"
- **Painel pro celular** — Eraldo consulta a qualquer hora na fábrica

### 4.2 Precisam de coleta adicional
- **Tracking de "perda real"** (campo `perdas_und` por folha) — quantas und foram descartadas/devolvidas
- **Validade próxima** (rastrear data de cada lote) — alertar antes do vencimento
- **Setup time entre sabores** — quanto tempo o Joel leva pra trocar entre tachos
- **Hora extra por dia** — pra calcular custo direto do gargalo de embalagem

### 4.3 Camada 2 (sugestão automática, pós-TCC)
- Algoritmo `ordem ≈ teto((parâmetro − ②) / rendimento)` já documentado
- Calibração com 3+ semanas de dados
- "Eraldo, o sistema sugere cortar X de 45g hoje. Concorda?" → ele aprova/ajusta → sistema aprende

### 4.4 Camada 3 (pós-TCC)
- Integração com Sigee Cloud (ERP)
- OEE básico (disponibilidade × performance × qualidade) — vira métrica padrão de Eng. Produção
- Baixa automática de insumos
- Cumbucas (parte dura do coco) — investigar se hoje é desperdício ou tem destino

---

## 5. Roadmap até a defesa (~18/07/2026)

### Etapas A-F (detalhamento da virada conceitual da seção 0)

| Etapa | O quê | Tempo | Status / quando |
|---|---|---|---|
| **A — Renomeação** | UI/variáveis: nomes próprios → departamentos (Gestão, Produção, Corte, Embalagem, Suprimentos). Mantém retrocompat no banco. | 2h | ✅ **Feito 14/05/2026** |
| **B — Modelo de Suprimentos** | ✅ **Feito 15/05/2026.** Schema novo (3 tabelas), CRUD completo, página com 4 abas, helpers `chave_produto_*`, função `calcular_necessidades_do_dia(data)` (MRP simplificado). Smoke test passou contra Supabase. Pronto pra cadastro real após entrevista. | 4h | ✅ 15/05/2026 |
| **C — Cadastro inicial de insumos** | Lista de matérias-primas + estoque atual + mínimo + fornecedor. Depende de entrevista com Gestão. | manual | Esta semana |
| **D — BOM (receitas)** | Pra cada produto, quanto consome de cada insumo. Pergunta-chave pra Produção/Gestão. | entrevista | Esta semana |
| **E — Auto-baixa por produção** | Quando folha é salva, sistema calcula consumo e baixa do almoxarifado. Sai da pura visualização — Camada 1.5. | 6-8h | 22-29/05 (Etapa 5 do TCC) |
| **F — Alertas + sugestão de compra + Sigee** | "Vai faltar X em Y dias", "Comprar Z". Importação de dados do Sigee Cloud. | 10h+ | Parcial até a defesa, completo pós-TCC |

### Semana atual (13-15/05)
- ✅ Cache + multi-page deploy
- ✅ **Página `pages/2_Insights.py`** criada e deployada — diagnóstico operacional automático com os 6 achados visualmente. Acessível em `pcp-vo-nena.streamlit.app/Insights` (no celular ou desktop).
- ✅ **Etapa A — Renomeação por departamento** (14/05)
- 🔄 Validar app em produção pós-redeploy (cache, multi-page, página Insights, renomeação)
- ➡️ Marcar entrevista presencial com a Gestão (1h, ficha em `entrevistas/01_pcp_inicial.md`)
- ➡️ Começar Etapa B — modelo de Suprimentos no banco

### 16-22/05 — Validação na fábrica
- Apresentar Relatório de Insights pro Eraldo
- Coletar respostas das perguntas pendentes
- Cronometrar 3-5x "preencher folha no sistema" (métrica #1 do cap. 5)
- Observar 1 dia completo: como Eraldo usa o app? Onde trava? Onde brilha?

### 22-29/05 — Etapa 5 (polimento Camada 1)
- Curva ABC de sabores
- Gráficos comparativos (semana atual × semana anterior)
- Alerta de tacho parcial integrado ao formulário
- Exportação PDF da folha pro arquivo físico (se Eraldo quiser manter paralelo)
- Painel mobile-friendly

### 29/05-04/06 — Consolidação
- Migração da tabela `estoque` SQLite → Postgres (se houver dados além do seed)
- Tratamento dos asteriscos `*` no papelzinho (Fase 1.5)
- Refatoração de qualquer débito técnico crítico
- Finalizar coleta de métricas Fase 1

### 05/06 em diante — Escrita do TCC
- Capítulo 1 — Introdução
- Capítulo 2 — Revisão de literatura (PCP, MRP, OEE, KPIs)
- Capítulo 3 — Metodologia
- Capítulo 4 — Implementação (sistema, decisões arquiteturais)
- **Capítulo 5 — Resultados** (Insight Master + métricas Fase 1 + casos do Eraldo)
- Capítulo 6 — Conclusão + trabalhos futuros (Camadas 2-4)

### ~18/07/2026 — Defesa

---

## 6. Convenções deste arquivo

- **Atualizar conforme avança.** Achado novo? Adiciona na seção 1 ou 2.
- **Perguntas respondidas viram descobertas.** Quando Eraldo responder uma pergunta da seção 3, move pra seção 1 ou 2 com a resposta.
- **Hipóteses sem confirmação ficam marcadas.** Use `[HIPÓTESE]` no início do parágrafo até virar fato confirmado.
- **Datas absolutas sempre.** "Próxima semana" rota, "16-22/05" não.
- **Sem dados? Diz.** "Não medido", "inconclusivo", "amostra pequena" — não inventa número.
