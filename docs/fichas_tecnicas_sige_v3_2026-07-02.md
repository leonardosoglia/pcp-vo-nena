# Guia de cadastro das fichas no SIGE — v2 (03/07/2026, com conversao de unidade)

> **1 unidade da ficha = 1 TACHO** (cocada/bala) / bandeja (palha) / bolo (PM).
> **Coluna `Consumo (digitar)`** = o numero que vai no campo Consumo da Composicao.
> **Coluna `Custo compra (conferir)`** = o que o SIGE mostra ao adicionar o insumo.
> **REGRA DE OURO:** se o custo que aparecer bater com a coluna, a unidade esta certa.
> Se vier diferente, o cadastro esta em outra embalagem — me chama.

## PRIMEIRO: corrigir a Cocada Tradicional (ja no SIGE)

| Trocar | Remover | Adicionar (buscar) | Consumo | Confere custo |
|---|---|---|---:|---|
| Acucar | o refinado que esta la (1292) | **`7566`** Alto Alegre | **0,8** | R$46 (fardo 10kg) |
| Sorbato | Kunda `29080701` | **`7908089414222`** Wanglong | **0,07** | R$24,89 (por kg) |
> Se o custo do acucar vier ~R$4,60 (e nao R$46), o cadastro e por kg -> ai digite **8**, nao 0,8.

## Cocada Tradicional
*1 tacho -> 8 bandejas · JA NO SIGE - corrigir acucar+sorbato*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite in natura | `01021` | 19.5 | R$4.70 | por L |
| Açúcar cristal | `7566` | 0.8 | R$46.00 | emb. 10 kg |
| Coco ralado | `008` | 2.5 | R$30.00 | emb. 2 kg |
| Sal | `344` | 0.015 | R$2.74 | por kg |
| Sorbato (anti-mofo) | `7908089414222` | 0.07 | R$24.89 | por kg |

## Cocada Leite Condensado
*1 tacho -> 8 bandejas · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite in natura | `01021` | 19.5 | R$4.70 | por L |
| Açúcar cristal | `7566` | 0.8 | R$46.00 | emb. 10 kg |
| Coco ralado | `008` | 5 | R$30.00 | emb. 2 kg |
| Leite condensado | `000000000000012332` | 0.75 | R$239.20 | emb. 20 kg |
| Sal | `344` | 0.015 | R$2.74 | por kg |
| Sorbato (anti-mofo) | `7908089414222` | 0.07 | R$24.89 | por kg |

## Cocada Brigadeiro
*1 tacho -> 8 bandejas · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite in natura | `01021` | 19.5 | R$4.70 | por L |
| Açúcar cristal | `7566` | 0.8 | R$46.00 | emb. 10 kg |
| Coco ralado | `008` | 2.5 | R$30.00 | emb. 2 kg |
| Achocolatado / Cacau (Brigadeiro) | `82143` | 1 | R$28.79 | emb. 0.5 kg |
| Sal | `344` | 0.015 | R$2.74 | por kg |
| Sorbato (anti-mofo) | `7908089414222` | 0.07 | R$24.89 | por kg |

## Cocada Cafe
*1 tacho -> 8 bandejas · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite in natura | `01021` | 19.5 | R$4.70 | por L |
| Açúcar cristal | `7566` | 0.8 | R$46.00 | emb. 10 kg |
| Coco ralado | `008` | 2.5 | R$30.00 | emb. 2 kg |
| Café (sachê 40 g) | `000000000012610012` | 0.208333 | R$130.04 | emb. 24 und |
| Sal | `344` | 0.015 | R$2.74 | por kg |
| Sorbato (anti-mofo) | `7908089414222` | 0.07 | R$24.89 | por kg |

## Cocada Pe de Moca
*1 tacho -> 8 bandejas · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite in natura | `01021` | 19.5 | R$4.70 | por L |
| Açúcar cristal | `7566` | 0.8 | R$46.00 | emb. 10 kg |
| Amendoim | `649` | 0.5 | R$60.00 | emb. 5 kg |
| Sal | `344` | 0.015 | R$2.74 | por kg |
| Sorbato (anti-mofo) | `7908089414222` | 0.07 | R$24.89 | por kg |

## Cocada Zero
*1 tacho -> 3 bandejas · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite in natura | `01021` | 26.5 | R$4.70 | por L |
| Coco ralado | `008` | 3 | R$30.00 | emb. 2 kg |
| Adoçante Lowçucar Culinária c/ Stevia | `409000415` | 2 | R$23.10 | por kg |
| Eritritol | `409000463` | 2 | R$27.50 | por kg |
| Xilitol | `XILITOL` | 0.04 | R$810.00 | emb. 25 kg |
| Sal | `344` | 0.015 | R$2.74 | por kg |
| Sorbato (anti-mofo) | `7908089414222` | 0.07 | R$24.89 | por kg |

## Bala de Doce de Leite
*1 tacho -> 30 balas · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Açúcar cristal | `7566` | 0.85 | R$46.00 | emb. 10 kg |
| Leite in natura | `01021` | 28 | R$4.70 | por L |
| Bicarbonato (sódio) | `26818` | 0.035 | R$9.99 | por kg |
| Palmiste (gordura vegetal) | `OLEO DE PALMISTE TAUA` | 0.062069 | R$400.00 | emb. 14.5 kg |
| Sal | `344` | 0.005 | R$2.74 | por kg |
| Sorbato (anti-mofo) | `7908089414222` | 0.01 | R$24.89 | por kg |

## Cocada Assada na Cumbuca
*1 lote -> 30 cumbucas · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite condensado | `000000000000012332` | 0.15 | R$239.20 | emb. 20 kg |
| Coco ralado | `008` | 1 | R$30.00 | emb. 2 kg |
| Ovo | `409000334` | 0.6 | R$13.99 | emb. 20 und |
| Açúcar cristal | `7566` | 0.05 | R$46.00 | emb. 10 kg |
| Leite in natura | `01021` | 0.15 | R$4.70 | por L |
| Sal | `344` | 0.005 | R$2.74 | por kg |
| Sorbato (anti-mofo) | `7908089414222` | 0.06 | R$24.89 | por kg |

## Palha Tradicional (Chocolate)
*1 receita -> 1 bandeja · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite condensado | `000000000000012332` | 0.191 | R$239.20 | emb. 20 kg |
| Manteiga sem sal | `5620` | 0.00577558 | R$150.01 | emb. 12.12 kg |
| Creme de leite | `6943` | 0.13? | R$213.72 | CONFIRMAR unidade |
| Açúcar de confeiteiro | `409001130` | 0.04 | R$53.10 | emb. 10 kg |
| Biscoito maisena | `740226` | 1.25? | R$117.36 | CONFIRMAR unidade |
| Chocolate meio amargo | `409000228` | 0.357143 | R$69.90 | emb. 2.1 kg |
| Etiqueta de palha | **⚠ criar** | CRIAR | — | — |

## Palha Leite em Po (Ninho)
*1 receita -> 1 bandeja · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite condensado | `000000000000012332` | 0.22325 | R$239.20 | emb. 20 kg |
| Manteiga sem sal | `5620` | 0.00907591 | R$150.01 | emb. 12.12 kg |
| Creme de leite | `6943` | 0.13? | R$213.72 | CONFIRMAR unidade |
| Açúcar de confeiteiro | `409001130` | 0.03 | R$53.10 | emb. 10 kg |
| Biscoito maisena | `740226` | 1.3? | R$117.36 | CONFIRMAR unidade |
| Leite Ninho (em pó) | `560077` | 0.27? | R$29.76 | CONFIRMAR unidade |
| Etiqueta de palha | **⚠ criar** | CRIAR | — | — |

## Palha Churros
*1 receita -> 1 bandeja · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite condensado | `000000000000012332` | 0.186 | R$239.20 | emb. 20 kg |
| Manteiga sem sal | `5620` | 0.00577558 | R$150.01 | emb. 12.12 kg |
| Creme de leite | `6943` | 0.13? | R$213.72 | CONFIRMAR unidade |
| Açúcar de confeiteiro | `409001130` | 0.04 | R$53.10 | emb. 10 kg |
| Biscoito maisena | `740226` | 1.3? | R$117.36 | CONFIRMAR unidade |
| Doce de leite | `409000198` | 0.208333 | R$0.01 | emb. 4.8 kg |
| Canela em pó | `5769` | 0.064? | R$143.76 | CONFIRMAR unidade |
| Etiqueta de palha | **⚠ criar** | CRIAR | — | — |

## Palha Cookies
*1 receita -> 1 bandeja · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite condensado | `000000000000012332` | 0.22325 | R$239.20 | emb. 20 kg |
| Manteiga sem sal | `5620` | 0.00907591 | R$150.01 | emb. 12.12 kg |
| Creme de leite | `6943` | 0.13? | R$213.72 | CONFIRMAR unidade |
| Açúcar de confeiteiro | `409001130` | 0.03 | R$53.10 | emb. 10 kg |
| Biscoito maisena | `740226` | 0.3? | R$117.36 | CONFIRMAR unidade |
| Leite Ninho (em pó) | `560077` | 0.27? | R$29.76 | CONFIRMAR unidade |
| Biscoito Negresco | `83726` | 1.1? | R$10.14 | CONFIRMAR unidade |
| Etiqueta de palha | **⚠ criar** | CRIAR | — | — |

## Palha Limao
*1 receita -> 1 bandeja · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Leite condensado | `000000000000012332` | 0.225 | R$239.20 | emb. 20 kg |
| Manteiga sem sal | `5620` | 0.00907591 | R$150.01 | emb. 12.12 kg |
| Creme de leite | `6943` | 0.13? | R$213.72 | CONFIRMAR unidade |
| Açúcar de confeiteiro | `409001130` | 0.04 | R$53.10 | emb. 10 kg |
| Biscoito maisena | `740226` | 1.25? | R$117.36 | CONFIRMAR unidade |
| Limão taiti | `1805` | 5? | R$5.60 | CONFIRMAR unidade |
| Etiqueta de palha | **⚠ criar** | CRIAR | — | — |

## Pao de Mel
*1 bolo -> 70 und (7 displays) · cadastrar*

| Insumo | Codigo | Consumo (digitar) | Custo compra (conferir) | Base |
|---|---|---:|---|---|
| Farinha de trigo | `1462` | 0.36? | R$4.99 | CONFIRMAR unidade |
| Açúcar mascavo | `7908089414219` | 0.34 | R$9.90 | por kg |
| Cacau em pó (Pão de Mel) | `82143` | 0.32 | R$28.79 | emb. 0.5 kg |
| Leite in natura | `01021` | 0.23 | R$4.70 | por L |
| Canela em pó | `5769` | 0.003? | R$143.76 | CONFIRMAR unidade |
| Cravo em pó | **⚠ criar** | CRIAR | — | — |
| Mel | `02` | 0.130345 | R$29.50 | emb. 1.45 kg |
| Essência de mel | **⚠ criar** | CRIAR | — | — |
| Palmiste (gordura vegetal) | `OLEO DE PALMISTE TAUA` | 0.0151724 | R$400.00 | emb. 14.5 kg |
| Sorbato (anti-mofo) | `7908089414222` | 0.01 | R$24.89 | por kg |
| Amaciante | **⚠ criar** | CRIAR | — | — |
| Bicarbonato (sódio) | `26818` | 0.011 | R$9.99 | por kg |
| Fermento em pó | `409000330` | 0.056 | R$6.39 | emb. 0.25 kg |
