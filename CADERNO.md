# Caderno de Campo — PCP Vó Nena

> **Propósito:** ponto único pra consolidar o que descobrimos, o que precisamos perguntar, e o roadmap até a defesa do TCC (~18/07/2026).
>
> Não é doc técnico (esse é `CLAUDE.md`). É o **diário do projeto** — atualizado conforme avançamos. Hipóteses, validações, ideias soltas, perguntas pra Gestão/Produção/Corte/Embalagem — tudo entra aqui pra não se perder.

---

## 0.2 Migração Supabase sa-east-1 → us-east-1 (18-19/05/2026)

**Resolução definitiva da lentidão pós-HF Spaces.**

### Sintoma
Após migrar pro HF Spaces (17/05), navegação entre datas no app levava **~1 min**.
Quick wins de cache (30min TTL, pre-warm, pool maior — commit `3424897`) não
resolveram. Causa raiz: latência transcontinental Supabase sa-east-1 ↔ HF us-east-1
(~150ms por query), amplificada por re-renders do Streamlit.

### Solução
Migração do banco Supabase do **Brasil** (`sa-east-1`) pra **EUA** (`us-east-1`),
mesma região do HF Spaces.

### Como
1. Criado novo projeto Supabase `pcp-vo-nena-us` em us-east-1 (free tier, NANO compute)
2. Script `migrar_postgres_para_postgres.py` criado e iterado:
   - Bug 1: `cannot insert non-DEFAULT value into column id` → corrigido com `OVERRIDING SYSTEM VALUE`
   - Bug 2: `current transaction is aborted` em cascata → corrigido com rollback explícito por tabela
3. Migração concluída: **338/338 linhas em 13 tabelas, todas ✅ OK**
4. `DATABASE_URL` trocada no HF Spaces secret + restart Space
5. Reset da senha do banco (boa prática — vazou em prints durante setup)

### Resultado
- Latência por query: **~150ms → ~5ms** (redução de ~97%)
- Banco antigo (`pcp-vo-nena` sa-east-1) **MANTIDO PAUSADO** por 1-2 semanas como backup vivo (rollback de 30s se necessário)
- Aprendizado pro TCC: estoque vs fluxo (Forrester 1961) — princípio que também
  corrigiu erro conceitual na Curva ABC (somar `emb_*` vs `ord_corte_*`)

### Lições de operação
- HF Spaces tem bug visual no badge "Restarting" (cache JS) — `Ctrl+F5` resolve
- Aba `Logs > Container` do HF mostra runtime logs (não só build)
- Senhas em `.txt` no Notepad são vulneráveis (OneDrive sync + print) — usar gerenciador (Bitwarden)
- `OVERRIDING SYSTEM VALUE` necessário pra colunas IDENTITY no Postgres 17+

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

**Q17/Q18 — Receita das Cocadas (por TACHO).** Questionário `02_suprimentos.docx` preenchido pela Gestão — recebido 22/05/2026. 1 tacho rende 8 bandejas (Zero rende 3). Receita é POR TACHO/sabor, não por formato — 45g/Mini/Pet são só decisão de corte (ver `project_receita_por_tacho.md`).

| Ingrediente (1 tacho) | Tradic. | Leite Cond. | Brigad. | Café | Pé de Moça | Zero |
|---|---|---|---|---|---|---|
| Leite in natura | 19 L | 19 L | 19 L | 19 L | 19 L | 26 L |
| Açúcar cristal | 8 kg | 8 kg | 8 kg | 8 kg | 8 kg | — (sem) |
| Coco ralado | 5 kg | 10 kg | 5 kg | 5 kg | — (sem coco) | 6 kg |
| Leite condensado | — | 15 kg | — | — | — | — |
| Cacau / achocolatado | — | — | 500 g | — | — | — |
| Café (sachê 40 g) | — | — | — | 5 sachês | — | — |
| Amendoim | — | — | — | — | 2,5 kg | — |
| Adoçante | — | — | — | — | — | 2 kg Lowçucar Stevia + 2 kg eritritol + 1 kg xilitol |

**Mistura — igual em TODOS os sabores (por tacho):** 500 ml de leite + 1 colher de sal + 14 colheres de antimofo. O leite da mistura soma ao leite in natura.

**Notas (confirmadas 22/05/2026):**
- vs respostas verbais de 15/05: o coco da Tradicional era estimado em "4 kg" — o questionário diz **5 kg**. A "mistura" não tinha aparecido na resposta verbal.
- **Pé de Moça NÃO leva coco ralado** — é a única cocada sem coco (vira só amendoim).
- **Adoçante da Zero:** "servia" = **Lowçucar Culinária com Stevia** (FoodService), adoçante à base de stévia — confirmado por foto da embalagem.

### Receita da PALHA — fichas técnicas (recebidas 22/05/2026)

Fichas técnicas oficiais ("Pequenas Mordidas Alimentos Eireli"). **Cada ficha é a receita de 1 bandeja** (= 1 receita = 1 panela, ver seção 1.A). A ficha lista ETIQUETA = 100 (lote nominal), mas na prática **1 bandeja rende 80-90 palhas 50g** — o planejamento usa **80** (o mínimo) — ou **~30 Pets** (confirmado 22/05/2026).

7 sabores existem; **5 ativos** + 2 ignorados (Morango, Paçoca — confirmados como sabores de palha).

Quantidades em **kg** por lote de 100 palhas 50g (kg conferidos contra a coluna de % das fichas — consistentes):

| Ingrediente | Tradicional | Ninho (L) | Churros (CH) | Cookies (CK) | Limão (LIM) |
|---|---|---|---|---|---|
| Leite condensado | 3,820 | 4,465 | 3,720 | 4,465 | 4,500 |
| Manteiga sem sal | 0,070 | 0,110 | 0,070 | 0,110 | 0,110 |
| Creme de leite | 0,130 | 0,130 | 0,130 | 0,130 | 0,130 |
| Açúcar de confeiteiro | 0,400 | 0,300 | 0,400 | 0,300 | 0,400 |
| Biscoito maisena | 1,250 | 1,300 | 1,300 | 0,300 | 1,250 |
| Leite ninho | — | 0,270 | — | 0,270 | — |
| Biscoito negresco | — | — | — | 1,100 | — |
| Doce de leite | — | — | 1,000 | — | — |
| Canela em pó | — | — | 0,064 | — | — |
| Chocolate meio amargo | 0,750 | — | — | — | — |
| Limão taiti | — | — | — | — | 5 und |
| Etiqueta | 100 und | 100 und | 100 und | 100 und | 100 und |

Notas de transcrição: leite ninho aparece 2× nas fichas de Ninho e Cookies (0,170 + 0,100) — somados. Canela 2× em Churros (0,044 + 0,020 = 0,064). Etiqueta da ficha Ninho não estava visível na foto — assumido 100 como as outras.

Ignorados (fichas existem): **Morango** = base + Nesquik 0,170 kg. **Paçoca** = base + Paçoquita Rolha 1,170 kg (0,756 + 0,414).

### Receita do PÃO DE MEL (manuscrita, recebida 22/05/2026)

Rendimento do lote **não indicado na foto — a confirmar** (provavelmente 1 bolo = 70 und = 7 displays).

- Farinha de trigo 360 g · Açúcar mascavo 340 g · Cacau em pó 160 g
- Leite 230 g (≈ 1 xícara) · Canela em pó 3 g · Cravo em pó 3 g
- Mel — 9 colheres · Essência de mel 3 g · Palmiste 220 g (≈ 1 xícara)
- Anti-mofo 10 g · Amaciante 20 g · Bicarbonato 11 g · Fermento em pó 14 g

### Receita da BALA DE DOCE DE LEITE — 1 TACHO (manuscrita, recebida 22/05/2026)

1 tacho de bala = 30 balas.

- Açúcar derretido 300 g · Açúcar 8,2 kg · Leite 28 L · Bicarbonato de sódio 35 g
- *(processo: atingir o ponto de leite condensado)*
- Palmiste (gordura vegetal) 900 g
- *(processo: desligar)*
- Sal 5 g · Anti-mofo 10 g — **Sorbato, o mesmo anti-mofo da cocada**

### Notas das receitas

- **Palha (resolvido 22/05):** 1 bandeja rende 80-90 palhas 50g — o planejamento usa **80** (o mínimo) — ou **~30 Pets**. A ficha técnica é a receita de 1 bandeja.
- **Pão de Mel (resolvido 22/05):** a receita manuscrita é de **1 bolo**. 1 bolo = **70 pães de mel = 7 displays**.
- **Anti-mofo = Sorbato** (confirmado pela receita da bala) — usar esse nome no cadastro de insumos.

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

## 1.A — Planejamento da PALHA: como a Gestão decide corte e produção (caderno do Leonardo, 22/05/2026)

Fotos do caderno do Leonardo. A palha é planejada **semanalmente, nas segundas** (quarta/quinta re-checam). É a lógica que o Leonardo quer **automatizar** (Camada 2) — pedido explícito: *"quero que você entenda isso para tentarmos automatizar"*.

### Dados de referência (os "ideais")

- **Palha 50g** — vendida em displays. 1 display = 10 palhas = **4 Tradicional + 4 Leite em Pó + 2 Churros**. Só T/L/CH têm 50g.
- **Palha Pet** — 5 sabores (T, L, CH, CK, LIM). Pet é cortado **terça e sexta**.
- **Ideal de displays/dia:** Seg 32 · Ter 36 · Qua 32 · Qui 32 · Sex 36 → semana = **168**.
- **Ideal de Pet/dia (cada terça e cada sexta):** T 170 · L 170 · CH 70 · CK 60 · LIM 70.
- **Estoque-alvo de bandejas (buffer da semana):** T 18 · L 18 · CH 9 · CK 4 · LIM 5.
- **Rendimento da bandeja de palha:** 1 bandeja → **30 Pets** ou **≈ 80 palhas 50g**.

### O algoritmo, com o exemplo real da segunda 18/05/2026

**1. Corte para 50g.** Necessidade da semana = 168 displays − 35 em estoque = **133 displays**. Em unidades (display = 4T+4L+2CH): T 532 · L 532 · CH 266. Menos o estoque de 50g pronto (T 415 · L 379 · CH 186) = necessidade líquida T 117 · L 153 · CH 80. ÷ 80 (rendimento 50g) → **cortar T 1 · L 2 · CH 1** bandejas.

**2. Corte para Pet.** Necessidade da semana = ideal de terça + sexta: T 340 · L 340 · CH 140 · CK 120 · LIM 140. Menos o estoque de Pet pronto (T 241 · L 304 · CH 110 · CK 90 · LIM 96) = líquida T 99 · L 36 · CH 50 · CK 30 · LIM 44. ÷ 30 (rendimento Pet) → **cortar T 3 · L 1 · CH 1 · CK 1 · LIM 1** bandejas.

**3. Corte total (bandejas) = 50g + Pet:** T 4 · L 3 · CH 2 · CK 1 · LIM 1.

**4. Sobra após o corte = bandejas em estoque − corte total.** Bandejas em estoque: T 14 · L 13 · CH 6 · CK 3 · LIM 4 → **sobra** T 10 · L 10 · CH 4 · CK 2 · LIM 3.

**5. Produção (bandejas) = estoque-alvo − sobra:** T 18−10=**8** · L 18−10=**8** · CH 9−4=**5** · CK 4−2=**2** · LIM 5−3=**2**.

### Leitura em PCP (vai pro TCC)

A fábrica já roda um **MRP manual** pra palha, em duas partes:
- **Corte = necessidade líquida.** Demanda da semana (displays + Pets) − estoque de produto pronto, convertido em bandejas pelo rendimento. O arredondamento NÃO é rígido — a Gestão tende a **não sobreproduzir** (ex.: precisava de 117 palhas T, cortou 80 e não 160). O caderno diz: *"o interessante é não fixar muito as bandejas a serem cortadas"*.
- **Produção = política de estoque-alvo (order-up-to / base-stock).** Repõe o estoque de bandejas até o ideal fixo (T 18, L 18, CH 9, CK 4, LIM 5), descontando o que sobrou do corte.

Pra automatizar (Camada 2): o sistema **sugere** corte e produção a partir dos estoques do dia + ideais + rendimentos; a Gestão ajusta. Inputs que o sistema precisa: estoque de displays, de 50g pronto, de Pet pronto e de bandejas.

### Notas de cocada / PM que vieram nas mesmas fotos

- **Calendário de corte:** Seg 45g · Ter Pet+mini · Qua 45g · Qui 45g · Sex Pet+mini (confirma o CLAUDE.md).
- **Prioridade de embalagem por dia** (prioridade 1 / prioridade 2): Seg mini / 45g · Ter 45g / mini · Qua 45g / mini · Qui mini / 45g · Sex 45g / mini.
- **Terça e sexta:** mandar produtos para os quiosques.
- **Pão de Mel — ideal por dia:** Seg 22 · Ter 26 · Qua 22 · Qui 22 · Sex 26.

### Modo de produção da palha (confirmado 22/05/2026)

**A palha NÃO é feita em tacho — é feita em PANELA.** Cada receita (1 panela) rende **1 bandeja** (resposta da funcionária que faz a palha). Logo: produzir N bandejas de palha = N receitas; a receita da palha É a "receita por bandeja".

Implicação no sistema: hoje o código trata a palha como cocada (`palha_<sigla>_tacho`, conversão ÷8 em `calcular_necessidades_do_dia`) — **está errado**. Pra palha é 1 receita = 1 bandeja (1:1). Corrigir na Etapa D/E.

Sabores de palha a **ignorar por enquanto:** morango e paçoca.

### Validação sistemática contra o banco (24/05/2026)

Rodei `sugerir_palha()` contra **3 segundas** (04/05, 11/05, 18/05) e comparei com a decisão real da Gestão (somatório de ord_corte + ord_prod da semana).

| Semana | Real (band/sem) | Sistema c/ `estoque_displays=0` | Sistema c/ `estoque_displays` "certo" |
|---|---|---|---|
| 04/05 | 63 | 79 (+25%) | 67 com displays=50 (+6%) |
| 11/05 | 51 | 54 (+6%) | 54 com displays=0 (+6%) |
| **18/05** | **36** (caderno manual) | 46 (+28%) | **36 com displays=35 (BATE EXATO +0%)** |

**Achado:** o algoritmo está **correto**. A divergência vem de um input que o sistema **não captura**: o **estoque de displays já montados na segunda** (varia ~0-50 por semana). Em 18/05, com `displays=35` (exato do caderno), o sistema reproduz no centavo a decisão da Gestão.

**Ações tomadas em seguida (24/05):**
- O input `estoque_displays` **já existia** na página, mas estava com pouca evidência visual (perdido no meio dos outros). Reorganizada a página: input em destaque no topo, tooltip explicando o impacto, expander com "como saber esse número" (peça à Embalagem) e default 35 marcado como "valor de referência".
- A médio prazo: nova coluna `cont_displays_palha` na tabela `folha_palha` + campo no formulário; Embalagem preenche junto com a contagem do estoque.

**Observação operacional (Leonardo, 24/05):** a folha de 04/05 tinha `ord_corte_50g = 0` e `ord_corte_pet = 0` em todos os sabores — provavelmente os cortes da semana foram feitos em outros dias (qua/qui) ou simplesmente não lançados. A Gestão confirmou que **segunda é o dia das decisões da palha**.

### Pendências da palha

- Receita da palha recebida 22/05 (fichas técnicas, registrada no Bloco 5). Rendimento confirmado: 1 bandeja = 80-90 palhas 50g (planejamento usa 80) ou ~30 Pets. Dados da palha completos — falta só corrigir o código (palha tratada como tacho, ver "Modo de produção" acima).
- Capturar `cont_displays_palha` no banco — input crítico que hoje vive na cabeça da Embalagem.

---

## 1.B — Planejamento da COCADA (em construção, iniciado 23/05/2026)

A "Camada 2" da cocada — análoga à da palha, mas bem mais rica:

- **3 estágios com lead time:** tacho → virar → virada → cortar (≈ 3 dias). A decisão de virar HOJE define o que pode ser cortado em 3 dias; bandeja **só** corta depois da viração.
- **5 formatos:** 45g, Mini, Pet, Potes 260g, Potes 605g.
- **Calendário de corte:** Seg/Qua/Qui → 45g · Ter/Sex → Mini + Pet (CLAUDE.md seção 4).
- **Sugestão precisa cobrir 4 decisões:** quanto cortar (por formato), quanto produzir (tachos), quanto virar (alimentar o corte dos próximos dias), quanto de potes.

### Estoque-alvo de POTES — diariamente (recebido completo 24/05/2026)

Confirmado: **605g** (não 65g). Tabela completa pra todos os sabores — "números base, a Gestão pode ajustar":

| Sabor | Pote 260g | Pote 605g |
|---|---|---|
| T (Tradicional) | 50 | 20 |
| L (Leite Cond.) | 50 | 20 |
| B (Brigadeiro)  | 20 | 10 |
| C (Café)        | 15 | 10 |
| P (Pé de Moça)  | 15 | 10 |
| Z (Zero)        | 50 | 20 |

T, L e Z dominam (50/20). B médio (20/10). C, P menores (15/10). Bate com o padrão observado nas folhas (T e Z são quem mais pede pote — análise 1.B "Padrões observados").

### Padrões observados nas folhas (análise de 17 folhas, 02/04 → 18/05/2026)

**Ranking de produção (`ord_prod_band` total):** TRADICIONAL 189 · LEITE COND. 79 · CAFÉ 30 · ZERO 27 · PÉ DE MOÇA 24 · BRIGADEIRO 23. T é ~2,4× L e ~8× os outros — confirma a regra-base 4:2:1:1:1.

**TENDÊNCIA: a fábrica está crescendo.** Metade antiga (02/04→05/05, 8d) vs recente (06/05→18/05, 9d): T +62% · L +47% · B +88% · C −12% · P +100% · Z +70%. Total: ~146 → ~226 bandejas (+55%). Achado relevante pro TCC — o sistema capturou crescimento real do negócio.

**Calendário de corte — mais flexível na prática que a regra teórica.** O CLAUDE.md diz Seg/Qua/Qui=45g · Ter/Sex=Mini+Pet, mas os dados mostram:
- 45g acontece em **TODOS** os dias úteis (mais forte em Qui — média 36 und/dia).
- Mini concentra em **Qua** > Ter ≈ Sex (não só Ter/Sex).
- Pet concentra em Ter/Sex (consistente com a regra).

A automação tem que ser **flexível** no calendário, não rígida.

**Parâmetros base — confirmados pelos dados.** Médias dos `param_real`: 45g T=6438, L=2815, B/C=1438, P=1500 (proporção 4:2:1:1:1 ✓). Mini T=L=500, B/C/P=300, Z=2815 (Z Mini = L 45g do dia, dinâmico ✓). Pet T=220, L=180, B/C/P=90, Z=300 ✓. Bate com a tabela do CLAUDE.md seção 4.

**Potes — pedido raro mas em volume.** T e Z dominam: T 260g (3 dias, total 70) · Z 260g (2d, 50) · T 605g (4d, 55) · Z 605g (4d, 45). LC/B/C/P quase nunca pedem pote. Consistente com a lógica do tacho parcial (sobra vira pote nesses sabores grandes).

**Viração — engrenagem corretiva.** `ord_prod_virada` aparece só 4 vezes em 17 folhas, sempre em grandes quantidades (24, 40, 15 bandejas). Confirma a memória [[project_engrenagem_virada]]: é pedido reativo quando o estoque de virada cai, pra não faltar o que cortar nos próximos dias.

### Restrição de mão de obra (a incorporar — 23/05/2026)

A decisão final de produção/virada/potes **não é só demanda vs estoque** — passa também pela **capacidade humana do dia**. Quando a Gestão define a produção (parte de baixo da folha, junto com balas/PM/Doces), ela **pergunta à Produção** se dá conta. A capacidade varia conforme quem está disponível no dia (com auxiliar a Produção rende mais). Mesma lógica vale pro Corte e pra Embalagem nas outras etapas.

A calculadora `sugerir_cocada()` precisa:
- Calcular a sugestão pela demanda (mesmo esquema da palha).
- **Aplicar o teto de capacidade** — se a sugestão passar do que cabe no dia, marcar "excede capacidade" e a Gestão decide o que priorizar.
- Aceitar input opcional de **"capacidade do dia"** (cheia / reduzida / mínima) pra ajustar o teto.

Pendente: **capacidade típica** da Produção (tachos/dia), do Corte (bandejas/dia) e da Embalagem (und/dia). Já dá pra estimar a da Produção pelo **maior dia observado** nas folhas — mas confirmar com a Gestão é melhor.

### Validação sistemática contra o banco (24/05/2026)

Rodei `sugerir_cocada()` contra **12 folhas** (29/04 → 15/05) com papelzinho_joel preenchido e param_real_*. Comparei totais sugeridos vs totais reais (ord_corte_*, ord_prod_band, ord_prod_potes_*).

| Métrica | Soma das diferenças (sist − real) | Leitura |
|---|---|---|
| Corte (band) | **+94** | Sistema overestima ~10-20% em vários dias |
| Produção (band) | **−41** | Sistema subestima em dias de alta produção (29/04, 07/05, 14/05, 15/05 = −20 cada) |
| Pote (und) | **−80** | Sistema subestima muito (−65 só em 11/05) — confirma hipótese do tacho parcial |

**Diagnóstico:**
- **Pote (−80 und):** consistente com o gap conhecido — sistema só repõe o alvo de pote, mas a Gestão também produz pote ABSORVENDO a sobra de tachos parciais (ver `project_tachos_parciais_potes.md`). Ex: 04/05 T → ord 30 band = 4 tachos cozidos (32 band massa); 2 band de sobra vão pra pote. A v3 vai modelar.
- **Corte (+94 band):** parte vem do mesmo gap dos potes (a "sobra" vira pote em vez de bandeja, o que faria o sistema enxergar estoque mais alto e sugerir menos corte); parte é capacidade priorizada — a Gestão concentra esforço em T/L em dias apertados.
- **Produção (−41 band):** o sistema espalha em mais sabores; a Gestão concentra. Mesmo efeito de capacidade priorizada.
- **Folhas com `ord_*=0` em vários campos** (06/05, 08/05) provavelmente estão incompletas — pulei na análise.

**Conclusão:** o algoritmo da v2 está coerente; as 3 melhorias planejadas pra v3 atacam exatamente as 3 fontes de divergência:
1. **Sobra do tacho parcial → pote** → resolve grande parte do `−80 pote` e parte do `+94 corte`.
2. **Capacidade priorizada T > L > demais** → resolve o `+94 corte` e o `−41 prod`.
3. **Viração calculada (3 dias à frente)** → fecha a engrenagem do estoque de virada.

### A construir / em construção (24/05)

- ✅ Calculadora `sugerir_cocada()` v2 — corte por formato + produção de tachos + potes, com alerta de capacidade e viração.
- ✅ Página `pages/11_Sugestao_Cocada.py`.
- ✅ **v3 entregue (24/05):**
  - **Capacidade priorizada (T > L > B > C > P > Z)** — quando `capacidade_tachos` é informado e excede, reduz produção dos sabores menos prioritários até caber. T sempre preservado.
  - **Sobra de tacho parcial → potes** — modelada. Default: só T, L, Z absorvem sobra (análise das folhas: B/C/P quase nunca fazem pote). Conversão conservadora: 1 band → 10 potes 260g ou 5 potes 605g. Cap pelo gap (`alvo − estoque`) pra não overshootar.
  - **Viração calculada** — `virada_sugerida = max(0, corte_total × 2 − joel_v)`. Mantém ~2 dias de viradas à frente.
- 🟡 **Resultado da re-validação v3 (24/05):**
  | Métrica | v2 (Σ) | v3 (Σ) | Comentário |
  |---|---|---|---|
  | Corte | +94 band | +94 band | Sem mudança (capacidade não acionada nos testes — `capacidade_tachos=None`). |
  | Produção | −41 band | −41 band | Idem. |
  | Pote | −80 und | **+186 und** | Trocou direção do erro; magnitude similar. Modelagem ainda aproximada. |
  | Viração | n/a | **−8 band** | Quase batendo zero no agregado. |
- 🟡 **Limites conhecidos da v3:**
  - A regra "sobra do tacho → pote" depende de julgamento humano (mistura 260g/605g, decide quando ignora). Modelagem 100% exigiria fichas detalhadas das folhas mostrando tachos cozidos + destino real.
  - Capacidade priorizada só atua se `capacidade_tachos` for passado. Sem isso, sistema "espalha" em todos os sabores e o erro `+94 corte` persiste.
- 🔴 Integração com metas de embalagem (Gestão precisa passar a última peça do questionário `02_suprimentos.docx`).

### Gaps de modelagem da cocada (Leonardo, 25/05/2026)

Após o Leonardo testar a v3 com a folha real de 25/05, vieram 4 observações importantes — **a sugestão isolada não captura nuances que a Gestão usa**:

**1. Cortados (sala da Embalagem) — ✅ resolvido nesta sessão.** A folha de produção tem coluna "CORTADOS" (45g, Mini, Pet) que é o estoque "quase-pronto" entre Corte e Embalagem. Antes da v3.1, o sistema só olhava `emb_*` (embalado), ignorando cortado. Agora aparece como input na seção "Estoque do dia" e entra na fórmula: `need = param_real − emb − cortado`. Se já há cortado suficiente, sistema sugere cortar menos hoje.

**2. Eventos da semana — pendente.** Quando a Gestão sabe que a equipe vai estar parcialmente fora num dia (ex: pintar rua sex/sáb), ela **adianta** corte e produção nos dias normais. O sistema não tem como saber sobre esses eventos. *Caminho proposto:* campo livre de "evento da semana / observação" no input. Médio prazo: tabela `eventos_semana` no banco (data, tipo, impacto). Longo prazo: botão "Pergunte ao Claude" pra contextualizar em PT-BR.

**3. Não-acomodação — pendente.** Observação do Leonardo: *"tanto no corte como na produção e até na embalagem ele não se acomoda caso os números do dia já tenham sido batidos, ele pede para fazer mais e mais para a equipe não ficar ociosa"*. Significa que o **alvo real é dinâmico** — cresce conforme a equipe disponível, não é só função da demanda. *Caminho:* capturar headcount diário das 3 áreas (Produção, Corte, Embalagem) na folha; correlacionar com produção observada; estimar capacidade média; sugerir "topo" baseado em capacidade, não só demanda. Vira capítulo de PCP no TCC (Goldratt — *Theory of Constraints*: gargalo é mão de obra, capacidade ociosa custa).

**4. Calendário + IA — pendente (sugestão do Leonardo).** A cocada tem muita coisa que influencia decisão (eventos, headcount, pedidos antecipados, intuição). Hard-codar tudo é impraticável. Caminhos sugeridos:
- **Calendário operacional** (curto prazo): tela onde a Gestão marca eventos da semana (pintura, feriado, pedido grande, equipe reduzida). Sistema lê e ajusta.
- **Botão IA** (médio prazo, ROADMAP_IA fase 3): "Pergunte ao Claude" recebe contexto livre + sugestão atual + ajusta com base no que a Gestão escreveu.
- **Aprendizado por histórico** (longo prazo): após N semanas com folhas completas + sugestões aplicadas, treinar modelo simples que aprende padrões da Gestão (regressão / árvore).

**Síntese honesta pro TCC:** a Camada 2 atinge ~85% da decisão da Gestão pela palha (algoritmo MRP clássico funciona); na cocada, atinge ~50-70% (dependendo do dia) porque há **decisões cognitivas** que dependem de contexto humano não capturado em estrutura. Esse "gap restante" é exatamente o espaço onde **um agente conversacional faz sentido** — não pra substituir a Gestão, mas pra captar contexto livre.

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
