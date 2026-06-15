# De-Para SIGE ↔ Insumos do PCP (BOM)

> **Doces Vó Nena · 14/06/2026 · Leonardo (estágio)**
> Sucede e atualiza o `01_matches_para_mariana.md` (27/05). Diferença: agora a
> fonte é a **API do SIGE ao vivo** (1.988 produtos lidos read-only), com **saldo
> e custo reais** — não mais um export estático. Cada código foi **validado
> contra o cadastro real do ERP** (nenhum código inventado).
>
> **Para quê:** ligar cada insumo que o nosso sistema rastreia ao item certo do
> SIGE, pra trazer **custo** e **referência de estoque** — e assim resolver o
> estoque negativo de insumos. **O SIGE só é lido; nunca escrevemos nele.**

---

## Como ler a tabela

| Coluna | O que é |
|---|---|
| **Cód. SIGE** | O código do produto no ERP (é o que a ponte vai usar). |
| **Saldo** | Quanto o SIGE diz que tem hoje, **na unidade de compra** (caixa/fardo/pacote). |
| **Custo R$** | Preço de compra cadastrado (referência pro custo de produção / TCC). |
| **Fator → receita** | Quantos **kg/L/und** há em **1 unidade de compra** do SIGE. Ex.: "×10" = 1 caixa vale 10 kg. É o que converte o saldo do ERP pra unidade da nossa receita. |
| **Status** | ✅ pronto · 🟡 escolher entre 2+ cadastros · 🔢 falta confirmar a unidade · ❌ não existe no SIGE. |

### A regra de ouro que descobrimos (vai pro TCC)
O SIGE é um ERP usado há anos: o **mesmo insumo costuma ter 2+ cadastros** (um
"bonito" na categoria PRODUÇÃO e um "sujo" sem categoria). Quase sempre o saldo
real está no cadastro **sujo, com movimento** — não no bonito (que fica zerado).
**Regra:** entre dois cadastros do mesmo item, apontamos para o que **tem saldo**,
não para o mais bonito. (Foi assim que corrigimos leite condensado, amendoim,
biscoito maizena, xilitol e canela abaixo.)

---

## 1. ✅ Prontos — identidade e fator claros (6)

| Insumo (nosso) | Cód. SIGE | Produto no SIGE | Saldo | Custo R$ | Fator → receita |
|---|---|---|---:|---:|---|
| Leite in natura | `01021` | LEITE PAST INTEGRAL SERRAMAR | 3.290 | 4,70 | ×1 (já em L) |
| Açúcar confeiteiro | `409001130` | AÇÚCAR CONFEITEIRO GLAÇÚCAR 20×500 | 8 | 53,10 | ×10 (fardo = 10 kg) |
| Adoçante Stevia (Zero) | `409000415` | LOWÇUCAR CULINÁRIA C/ STEVIA 1000G | 78 | 23,10 | ×1 (pacote 1 kg) |
| Eritritol (Zero) | `409000463` | ERITRITOL CRISTAL 1 KG | 10 | 27,50 | ×1 (pacote 1 kg) |
| Bicarbonato | `26818` | BICARBONATO DE SÓDIO 1KG SICILIANO | 0 | 9,99 | ×1 (pacote 1 kg) |
| Fermento em pó | `409000330` | FERMENTO ROYAL 250G | 0 | 6,39 | ×0,25 (lata 250 g) |

*Obs.: bicarbonato e fermento têm saldo 0 no SIGE — a identidade está certa, mas a quantidade inicial virá da contagem física (ver §6).*

---

## 2. 🟡 Escolher o cadastro certo — há duplicatas (12)

> Em todos, **já apontei pro código que tem saldo** (regra de ouro). Falta a
> Suprimentos confirmar qual é o oficial.

| Insumo (nosso) | Cód. sugerido | Produto no SIGE | Saldo | Custo R$ | Fator | Confirmar |
|---|---|---|---:|---:|---|---|
| **Leite condensado** ⭐ | `…012332` | PIRACANJUBA BAG **4×5KG** | 40 | 239,20 | ×20 | É o 4×5kg (saldo real) ou o 2×5kg `560075` (cód. "bonito", saldo 0)? Saldo é em caixa ou kg? **Insumo de maior consumo da casa.** |
| Xilitol (Zero) | `XILITOL` | XILITOL CRYSTAL **25KG** | 2 | 810,00 | ×25 | Usam o fardo 25 kg (tem saldo) ou o pacote 1 kg `409000890` (saldo 0)? |
| Coco ralado | `008` | LEVE COCO FRESCO CONGELADO 2KG | 670 | 30,00 | ×2 | LEVE COCO 2 kg ou Vita Coco 1 kg (`01`, saldo 285)? |
| Amendoim | `649` | AMENDOIM GRANULADO **5KG** | 11 | 60,00 | ×5 | Pacote 5 kg (saldo real) ou saco 25 kg `409000125` (saldo 0)? |
| Achocolatado (Brigadeiro) | `82143` | CACAU EM PÓ 100% SICÃO 500G | 23 | 28,79 | ×0,5 | É cacau puro ou achocolatado tipo Nescau? **Mesmo cacau do Pão de Mel?** |
| Cacau em pó (Pão de Mel) | `82143` | CACAU EM PÓ 100% SICÃO 500G | 23 | 28,79 | ×0,5 | **É o mesmo `82143` do Brigadeiro** → risco de baixar 2× o mesmo estoque (ver §5). |
| Biscoito maizena | `740226` | MARILAN MAIZENA **300G** | 100 | 117,36 | ×0,30 | Pacote 300 g (saldo real) ou o 350g `409000184` (saldo −1, custo R$0,01 quebrado)? Saldo 100 é pacote ou caixa? |
| Biscoito Negresco | `409000207` | NEGRESCO RECHEADO 100G | 30 | 2,29 | ×0,10 | Pacote 100 g (saldo 30) ou caixa 66×100g `560078`? |
| Canela em pó | `5769` | CANELA KITANO 50G | −11 | 143,76 | a definir | Custo R$143,76 = é **caixa de potes**, não pote — então fator ≠ 0,05. Qual usam: `5769` ou `409000202`? |
| Farinha de trigo | `409000150` | FARINHA D. BENTA TIPO 1 1KG | 0 | 5,50 | ×1 | Avulso 1 kg ou fardo 10×1kg `1462` (saldo 10)? |
| Palmiste | `OLEO…TAUA` | ÓLEO DE PALMISTE TAUÁ 14,5KG | 9 | 400,00 | ×14,5 | Duplicata `PRD00066` (custo 268). Qual o ativo? Custo 400 vs 268? |
| Sal | `344` | SAL REFINADO LEBRE 1KG | 4 | 2,74 | ×1 | Marca fixa ou "o sal 1 kg que tiver"? (commodity, impacto $ irrelevante) |

---

## 3. 🔢 Identidade certa, falta a unidade do saldo (10)

> O item está achado, mas o nome não deixa claro se o saldo é contado por
> **caixa/fardo** ou por **unidade**. Isso muda o fator em 10–25× — perigoso.
> Uma pergunta só resolve: *"a baixa deste item no SIGE é por caixa/fardo ou por
> unidade individual?"*

| Insumo (nosso) | Cód. SIGE | Produto no SIGE | Saldo | Custo R$ | Fator provável | A confirmar |
|---|---|---|---:|---:|---|---|
| Creme de leite | `560074` | PIRACANJUBA 12×1,03KG | 254 | 161,64 | ×12,36 (caixa) ou ×1,03 (latinha) | 254 caixas = 3,1 t (irreal) → provável que conte latinha |
| Leite Ninho | `560077` | NINHO INTEGRAL SACHÊ | −8 | 29,76 | ? (peso do sachê) | Sachê de 750 g, 800 g? Nome não traz o peso |
| Manteiga sem sal | `5620` | MARGARINA AMÉLIA S/SAL 12×1,01KG | 1 | 150,01 | ×12,12 (caixa) | **Manteiga ou margarina?** (no SIGE só há margarina com saldo) |
| Doce de leite | `409000198` | DOCE DE LEITE FRIMESA 4,8KG | 1 | **0,01** ⚠ | ×4,8 | Custo quebrado — qual o real? Qual balde? |
| Açúcar cristal | `409000200` | AÇÚCAR CRISTAL 5KG | 0 | 21,90 | ×5 | Saldo 0 — **precisa carga inicial** (alto volume!) |
| Mel | `02` | MEL LITRO 1.450 GR | 76 | 29,50 | ×1,45 (litro→kg) | Conta por garrafa/litro ou já por kg? |
| Chocolate meio amargo | `409000228` | BARRA SICÃO MEIO AMARGO 2,1KG | 5 | 69,90 | ×2,1 (barra) | Barra 2,1 kg ou gotas a granel/kg? |
| Café (sachê) | `409000174` | CAFÉ SOLÚVEL SACHÊ **50G** | 0 | 5,16 | ×1 (por sachê) | Receita assume 40 g; SIGE tem 50 g |
| Limão taiti | `1805` | HF. LIMÃO TAITI | 0 | 5,60 | ? (und ou kg?) | Receita pede **unidades**; SIGE pode contar por kg (~6–8 limões/kg) |
| Sorbato (anti-mofo) | `29.08.07.01` | SORBATO POTÁSSIO KUNDA 25KG | 224 | 53,00 | ? (×25 ou ×1) | **224 caixas = 5,6 t (irreal)** → saldo provavelmente já em kg → fator ×1 |

---

## 4. ❌ Não existem no SIGE — a Suprimentos precisa cadastrar (5)

| Insumo (nosso) | Onde é usado | Ação |
|---|---|---|
| Açúcar mascavo | Pão de Mel | Cadastrar no SIGE (com peso da embalagem no nome) |
| Essência de mel | Pão de Mel | Cadastrar (ou é "aromatizante"?) |
| Cravo em pó | Pão de Mel | Cadastrar (ou vem num blend de especiarias?) |
| Amaciante | Pão de Mel | Cadastrar — confirmar o nome comercial (emulsificante / liga neutra / Emustab?) |
| Etiqueta de palha | Palha (todas) | No SIGE são **cintas por sabor** (Chocolate, Ninho, Churros…), não 1 item só. Decidir: desmembrar por sabor **ou** mapear numa cinta de referência. |

---

## 5. ⚠️ Produtos que a fábrica faz e o sistema NÃO modela

> Resposta direta à sua intuição ("talvez faltem insumos"): faltam porque
> faltam **produtos**. Achei matérias-primas no SIGE que nenhuma das nossas
> receitas (6 cocadas, 5 palhas, PM, bala) consome — sinal de produção paralela
> invisível ao MRP. **Esses produtos consomem os MESMOS insumos do BOM** (creme
> de leite, chocolate, farinha), então o MRP hoje **subestima** a necessidade.

| Produto não modelado | Pista no SIGE | Por que importa |
|---|---|---|
| **Cocada Assada / linha com ovo** | `OVO BRANCO 10UN` e `CX OVO BCO 60UN` (PRODUÇÃO) | Ovo é insumo ativo e **nada** no BOM usa ovo. A Assada (e ovos de Páscoa de colher) ficam sem baixa. |
| **Linha Morango** (cocada e palha) | `PÓ SOBREMESA MORANGO MAVALÉRIO` (PRODUÇÃO); SKUs morango com saldo negativo | Vendem de verdade, fora dos sabores T/L/B/C/P/Z e das 5 palhas. |
| **Coberturas (choco ao leite e branco)** | `CHOCO SICÃO AO LEITE 2,05KG`; `GENUINE BRANCO 2,1KG` | Entram em ovos de colher, biscoitos cobertos, fondue. BOM só tem meio amargo. |
| **Biscoitos amanteigados** (linha própria) | `Biscoito Amanteigado … KG` (PRODUÇÃO) | Família vendida por kg, sem nenhuma receita no sistema. |
| **Bala de gengibre** | vários `BALA GENGIBRE … 40G` | Produto diferente da bala de doce de leite; gengibre nem está no SIGE. |
| **Palha de Paçoca / de Leite em Pó** | `PALHA ITALIANA PAÇOCA`; `… LEITE EM PÓ BALDE` | 2 sabores de palha além dos 5 do BOM. |
| **Chocotone / bolos com ganache** | `CHOCOTONE TRUF GANACHE`; `BOLO … GANACHE` | Sazonais que consomem creme de leite/chocolate compartilhados. |

→ Sugestão: virar um **backlog de receitas a levantar** numa próxima entrevista. Prioridade: **morango e ovo** (volume e recorrência).

---

## 6. Decisão de arquitetura (importante — vai pro TCC)

**O saldo do SIGE NÃO entra como verdade absoluta.** Motivos: (a) o saldo do ERP
reflete nota fiscal, não o físico no chão; (b) existem **3 camadas de estoque**
(SIGE × nosso sistema × físico real) que divergem — o mesmo princípio
estoque‑vs‑fluxo (Forrester) já adotado no resto do projeto.

**Portanto a ponte vai usar o SIGE assim:**
- ✅ **Custo** e **identidade** do insumo → vêm do SIGE (confiável).
- ✅ **Carga inicial de quantidade** → vem da **1ª contagem física** sua (7h–10h), lançada como entrada/contagem_inicial. **Não** do saldo cego do SIGE.
- ✅ Importar automaticamente **só os itens ✅ CONFIRMADOS**; os 🟡/🔢 ficam manuais até a fábrica responder; os ❌ aguardam cadastro.
- 🚫 Nunca escrever de volta no SIGE (read-only — já decidido).

---

## 7. Perguntas pra levar à Suprimentos/Produção (priorizadas)

1. **Leite condensado** (o mais crítico): código oficial é o 2×5kg (`560075`) ou o 4×5kg (`…012332`, que tem o saldo)? O saldo é em caixas ou em kg?
2. **A baixa no SIGE é por caixa/fardo ou por unidade?** — vale pra creme de leite, ninho, manteiga, sorbato, biscoito maizena, canela, café. (Resolve 7 fatores de uma vez.)
3. **Manteiga ou margarina?** Na receita da palha, entra manteiga sem sal ou a margarina Amélia s/sal (`5620`)?
4. **Cacau do Brigadeiro = cacau do Pão de Mel?** Se for o mesmo (`82143`), como separar pra não baixar o estoque 2×?
5. **Açúcar cristal e amendoim:** qual a embalagem de compra (pacote vs fardo)? Precisam de contagem inicial (saldo 0/baixo).
6. **Cadastrar no SIGE:** açúcar mascavo, essência de mel, cravo em pó, amaciante (qual nome comercial?). Pedir que o cadastro **sempre tenha o peso no nome**.
7. **Custos quebrados** (doce de leite e biscoito maizena a R$0,01): quais os valores reais de compra?
8. **Produtos fora do BOM** (§5): a fábrica faz Cocada Assada, linha morango, biscoitos amanteigados, bala de gengibre? Receitas?

---

## 8. Resumo

- **33 insumos:** 6 prontos · 12 a escolher código · 10 a confirmar unidade · 5 a cadastrar.
- A ponte (`importar_sige_api.py`, a construir) vai importar **só os 6 prontos** primeiro; o resto destrava conforme a Suprimentos responde §7.
- **O que mudou desde 27/05:** açúcar cristal "ressuscitou" (estava dado como inativo); agora temos **saldo ao vivo** (não só custo); e a verificação corrigiu 6 escolhas de código que apontavam pra cadastros zerados.
