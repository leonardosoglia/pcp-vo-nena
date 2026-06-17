# Fichas técnicas para o SIGE — grandezas por receita/tacho

> **Doces Vó Nena · 14/06/2026 (atualizado 17/06: + Cocada Assada na Cumbuca).**
> Geradas a partir do nosso BOM cruzado com o de-para SIGE
> ([`suprimentos_sigee/de_para_sige.md`](../suprimentos_sigee/de_para_sige.md)).
> Servem para **cadastrar as fichas técnicas no SIGE** (fonte única — decisão da
> Gestão, 17/06) e para montar a **OP de teste**. Arquitetura em
> [`ARQUITETURA_SIGE.md`](ARQUITETURA_SIGE.md).

A coluna **Código SIGE** já traz o código do insumo no ERP — é só transcrever.
Quantidades na **unidade da receita** (kg/L/und); ao cadastrar no SIGE, ajuste
para a unidade que o ERP usa no insumo, se for diferente.

---

## Roteiro da OP de teste (manual, no SIGE)

A entrada da OP é **manual** (decisão da Gestão) — o nosso sistema só lê. Sugestão
de teste para entender as grandezas e validar o ciclo:

1. **Cadastrar a ficha técnica** de **1 produto** no SIGE (ex.: Cocada Tradicional),
   usando a tabela abaixo (insumos + quantidades + rendimento esperado).
2. **Gerar uma OP de teste** (ex.: 10 receitas) e observar:
   - o SIGE **explode** os insumos e mostra a quantidade separada?
   - os insumos ficam **pré-reservados** (somem da necessidade de compra)?
   - aparece a **baixa por lote** na retirada?
3. **Finalizar a OP** com um rendimento (ex.: rendeu 60 bandejas) e ver onde o
   **rendimento real** e o **descarte** ficam registrados.
4. Depois, o nosso PCP **lê a OP de volta** pela API (`pesquisar_ordens_producao`)
   e a gente confirma os campos reais de rendimento/lote — fechando a análise.

---

## Fichas técnicas


## Cocadas (por tacho)

### Cocada Tradicional
**Rendimento:** 1 tacho → 8 bandejas (≈ 800 und de 45 g · ≈ 44 kg)

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite in natura | `01021` | 19 | L |
| Açúcar cristal | `409000200` | 8 | kg |
| Coco ralado | `008` | 5 | kg |
| Sal | `344` | 0.015 | kg |
| Sorbato (anti-mofo) | `29.08.07.01` | 0.07 | kg |

### Cocada Leite Condensado
**Rendimento:** 1 tacho → 8 bandejas (≈ 800 und de 45 g · ≈ 44 kg)

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite in natura | `01021` | 19 | L |
| Açúcar cristal | `409000200` | 8 | kg |
| Coco ralado | `008` | 10 | kg |
| Leite condensado | `000000000000012332` | 15 | kg |
| Sal | `344` | 0.015 | kg |
| Sorbato (anti-mofo) | `29.08.07.01` | 0.07 | kg |

### Cocada Brigadeiro
**Rendimento:** 1 tacho → 8 bandejas (≈ 800 und de 45 g · ≈ 44 kg)

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite in natura | `01021` | 19 | L |
| Açúcar cristal | `409000200` | 8 | kg |
| Coco ralado | `008` | 5 | kg |
| Achocolatado / Cacau (Brigadeiro) | `82143` | 0.5 | kg |
| Sal | `344` | 0.015 | kg |
| Sorbato (anti-mofo) | `29.08.07.01` | 0.07 | kg |

### Cocada Café
**Rendimento:** 1 tacho → 8 bandejas (≈ 800 und de 45 g · ≈ 44 kg)

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite in natura | `01021` | 19 | L |
| Açúcar cristal | `409000200` | 8 | kg |
| Coco ralado | `008` | 5 | kg |
| Café (sachê 40 g) | `409000174` | 5 | und |
| Sal | `344` | 0.015 | kg |
| Sorbato (anti-mofo) | `29.08.07.01` | 0.07 | kg |

### Cocada Pé de Moça
**Rendimento:** 1 tacho → 8 bandejas (≈ 800 und de 45 g · ≈ 44 kg)

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite in natura | `01021` | 19 | L |
| Açúcar cristal | `409000200` | 8 | kg |
| Amendoim | `649` | 2.5 | kg |
| Sal | `344` | 0.015 | kg |
| Sorbato (anti-mofo) | `29.08.07.01` | 0.07 | kg |

### Cocada Zero
**Rendimento:** 1 tacho → 3 bandejas (Mini 27 g)

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite in natura | `01021` | 26 | L |
| Coco ralado | `008` | 6 | kg |
| Adoçante Lowçucar Culinária c/ Stevia | `409000415` | 2 | kg |
| Eritritol | `409000463` | 2 | kg |
| Xilitol | `XILITOL` | 1 | kg |
| Sal | `344` | 0.015 | kg |
| Sorbato (anti-mofo) | `29.08.07.01` | 0.07 | kg |


## Cocada Assada (por lote de 30 cumbucas)

### Cocada Assada na Cumbuca
**Rendimento:** 1 lote → 30 cumbucas de 145 g (assada no forno)

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite condensado | `000000000000012332` | 3 | kg |
| Coco ralado | `008` | 2 | kg |
| Ovo | `291` | 12 | und |
| Açúcar cristal | `409000200` | 0.5 | kg |
| Leite in natura | `01021` | 0.15 | L |
| Sal | `344` | 0.005 | kg |
| Sorbato (anti-mofo) | `29.08.07.01` | 0.06 | kg |


## Palhas (por bandeja)

### Palha Tradicional (Chocolate)
**Rendimento:** 1 receita → 1 bandeja

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite condensado | `000000000000012332` | 3.82 | kg |
| Manteiga sem sal | `5620` | 0.07 | kg |
| Creme de leite | `560074` | 0.13 | kg |
| Açúcar de confeiteiro | `409001130` | 0.4 | kg |
| Biscoito maisena | `740226` | 1.25 | kg |
| Chocolate meio amargo | `409000228` | 0.75 | kg |
| Etiqueta de palha | `⚠ a cadastrar no SIGE` | 100 | und |

### Palha Leite em Pó (Ninho)
**Rendimento:** 1 receita → 1 bandeja

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite condensado | `000000000000012332` | 4.465 | kg |
| Manteiga sem sal | `5620` | 0.11 | kg |
| Creme de leite | `560074` | 0.13 | kg |
| Açúcar de confeiteiro | `409001130` | 0.3 | kg |
| Biscoito maisena | `740226` | 1.3 | kg |
| Leite Ninho (em pó) | `560077` | 0.27 | kg |
| Etiqueta de palha | `⚠ a cadastrar no SIGE` | 100 | und |

### Palha Churros
**Rendimento:** 1 receita → 1 bandeja

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite condensado | `000000000000012332` | 3.72 | kg |
| Manteiga sem sal | `5620` | 0.07 | kg |
| Creme de leite | `560074` | 0.13 | kg |
| Açúcar de confeiteiro | `409001130` | 0.4 | kg |
| Biscoito maisena | `740226` | 1.3 | kg |
| Doce de leite | `409000198` | 1 | kg |
| Canela em pó | `5769` | 0.064 | kg |
| Etiqueta de palha | `⚠ a cadastrar no SIGE` | 100 | und |

### Palha Cookies
**Rendimento:** 1 receita → 1 bandeja

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite condensado | `000000000000012332` | 4.465 | kg |
| Manteiga sem sal | `5620` | 0.11 | kg |
| Creme de leite | `560074` | 0.13 | kg |
| Açúcar de confeiteiro | `409001130` | 0.3 | kg |
| Biscoito maisena | `740226` | 0.3 | kg |
| Leite Ninho (em pó) | `560077` | 0.27 | kg |
| Biscoito Negresco | `409000207` | 1.1 | kg |
| Etiqueta de palha | `⚠ a cadastrar no SIGE` | 100 | und |

### Palha Limão
**Rendimento:** 1 receita → 1 bandeja

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Leite condensado | `000000000000012332` | 4.5 | kg |
| Manteiga sem sal | `5620` | 0.11 | kg |
| Creme de leite | `560074` | 0.13 | kg |
| Açúcar de confeiteiro | `409001130` | 0.4 | kg |
| Biscoito maisena | `740226` | 1.25 | kg |
| Limão taiti | `1805` | 5 | und |
| Etiqueta de palha | `⚠ a cadastrar no SIGE` | 100 | und |


## Pão de Mel (por bolo)

### Pão de Mel
**Rendimento:** 1 bolo → 70 unidades (7 displays de 10)

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Farinha de trigo | `409000150` | 0.36 | kg |
| Açúcar mascavo | `⚠ a cadastrar no SIGE` | 0.34 | kg |
| Cacau em pó (Pão de Mel) | `82143` | 0.16 | kg |
| Leite in natura | `01021` | 0.23 | L |
| Canela em pó | `5769` | 0.003 | kg |
| Cravo em pó | `⚠ a cadastrar no SIGE` | 0.003 | kg |
| Mel | `02` | 0.189 | kg |
| Essência de mel | `⚠ a cadastrar no SIGE` | 0.003 | kg |
| Palmiste (gordura vegetal) | `OLEO DE PALMISTE TAUA` | 0.22 | kg |
| Sorbato (anti-mofo) | `29.08.07.01` | 0.01 | kg |
| Amaciante | `⚠ a cadastrar no SIGE` | 0.02 | kg |
| Bicarbonato (sódio) | `26818` | 0.011 | kg |
| Fermento em pó | `409000330` | 0.014 | kg |


## Bala de Doce de Leite (por tacho)

### Bala de Doce de Leite
**Rendimento:** 1 tacho → 30 balas

| Insumo | Código SIGE | Qtd / receita | Unidade |
|---|---|---:|---|
| Açúcar cristal | `409000200` | 8.5 | kg |
| Leite in natura | `01021` | 28 | L |
| Bicarbonato (sódio) | `26818` | 0.035 | kg |
| Palmiste (gordura vegetal) | `OLEO DE PALMISTE TAUA` | 0.9 | kg |
| Sal | `344` | 0.005 | kg |
| Sorbato (anti-mofo) | `29.08.07.01` | 0.01 | kg |


---

## Pendente — falta receita

### Docinhos  ⚠
Não há receita de **docinhos** no nosso BOM. Para gerar a ficha técnica, preciso
das grandezas por receita: quais insumos, quanto de cada, e o rendimento (quantas
unidades por receita). Mesma estrutura das fichas acima.

> Outros produtos vistos no catálogo do SIGE que **também não têm receita** no
> nosso sistema (caso entrem no escopo): linha de **morango**, **coberturas**,
> **biscoitos amanteigados**, **bala de gengibre**.

---

## Observações para o cadastro

- **Insumos `⚠ a cadastrar no SIGE`** (açúcar mascavo, essência de mel, cravo em
  pó, amaciante): precisam ser criados no ERP antes de a ficha ficar completa.
- **Cocadas — a "mistura" do tacho:** o **sal** (15 g = 1 colher) e o **sorbato**
  (70 g) listados em cada cocada são a *mistura*, dissolvidos em ~500 ml do leite.
  Esses 500 ml **já estão dentro** do leite total (19 L nas cocadas T/L/B/C/P;
  26 L na Zero) — **não somam por cima**.
- **Cocada Assada na Cumbuca** (adicionada 17/06): o **ovo** usa o cadastro
  `OVOS BRANCOS GRANDES (30 OVOS)` (cód. `291`) — confirmar se é esse mesmo.
  O **casco/cumbuca** (recipiente) e a **embalagem** **não entram na ficha** (não
  estão cadastrados no SIGE) — a ficha cobre só a massa.
- **Rendimentos** marcados em bandejas/unidades são os que conhecemos com
  segurança; os valores em **kg são aproximados** e devem ser confirmados na OP de
  teste (é exatamente o "rendeu 60 / devia render 70" que a Gestão quer medir).
- **1 receita = 1 tacho** (cocada/bala) ou **1 bandeja** (palha) ou **1 bolo** (PM)
  — confirme se o SIGE usa "receita" com o mesmo significado.
