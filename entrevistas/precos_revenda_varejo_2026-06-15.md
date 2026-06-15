# Preços de venda — Doces Vó Nena (registrados 15/06/2026)

> Fonte: duas tabelas enviadas pelo Leonardo. Dados de negócio — base pra cálculo
> de margem (ver `margem_produto.py` / `custo_producao.py`).

## 1. ATACADO / revenda

Duas colunas: **SEM ST** (sem nota fiscal) · **COM ST** (com nota — embute o
imposto/substituição tributária, ~13% a mais).

| Produto | Sem ST (R$) | Com ST (R$) |
|---|---:|---:|
| Cocada 45g | 3,30 | 3,73 |
| Palhas 50g | 4,10 | 4,51 |
| Zero 27g | 2,90 | 3,28 |
| Doce de Leite 40g | 2,90 | — |
| Pão de Mel 60g | 5,40 | 5,94 |
| Cocada Assada | 11,50 | 13,01 |
| Bala Doce de Leite 400g | 21,00 | — |
| Pet Cocada Zero 100g | 11,40 | 12,90 |
| Pet Cocada 160g | 10,90 | 12,33 |
| Kit 02 Cocada | 8,70 | 9,84 |

## 2. VAREJO / quiosques, feiras, loja, barraquinhas

Duas colunas: **Preço Netinho** (cartão fidelidade) · **Preço Normal** (venda comum).

| Produto | Netinho (R$) | Normal (R$) |
|---|---:|---:|
| Mini 30g | 4,79 | 5,10 |
| 3x Mini 30g | 11,79 | 12,80 |
| Tablete 30g Zero | 6,39 | 6,90 |
| Palha 50g | 7,29 | 7,90 |
| 2x Palha 50g | 12,59 | 13,40 |
| Pão de Mel (quiosque) | 9,79 | 10,50 |
| Doce de Leite 40g (quiosques) | 6,39 | 6,79 |
| Doce de Leite Barra 400g | 31,90 | 34,60 |
| Pet 100g Cocada Zero | 18,90 | 20,60 |
| Pet 170g Cocada | 17,60 | 18,90 |
| Pet Palha 170g | 17,60 | 18,90 |
| Cocada Assada (quiosque) | 17,60 | 18,90 |
| Bala de Doce de Leite (quiosque) | 36,90 | 39,90 |
| Doce de Leite em Cubos | 17,60 | 18,90 |
| Bala de Coco | 17,60 | 18,90 |
| Bala de Coco Beijinho | 17,60 | 18,90 |
| Goiabada Cascão | 31,90 | 34,50 |
| Amanteigados | 17,60 | 18,90 |
| Casadinhos | 17,60 | 18,90 |
| Biju | 22,90 | 24,40 |
| Brownie 30g | 6,29 | 6,70 |
| Brownie 100g | 17,60 | 18,90 |
| Bolo Cenoura | 34,90 | 37,90 |
| Bolo Brownie | 34,90 | 37,90 |
| Bolo Cocada | 34,90 | 37,90 |
| Bolo Chocolate | 34,90 | 37,90 |
| Pote 260g Cocada | 28,39 | 30,90 |
| Pote 260g Zero | 34,90 | 36,90 |
| Pote 600g Cocada | 49,19 | 52,90 |
| Pote 600g Doce de Leite Ivone | 49,19 | 52,90 |
| Pote 600g Zero | 55,90 | 59,80 |
| Cx Pres c/ 02 Cocadas | 16,89 | 17,90 |
| Cx Pres c/ 04 Cocadas | 25,19 | 26,90 |
| Cx Pres c/ 06 Cocadas | 36,90 | 39,30 |
| Cx Pres c/ 08 Cocadas | 50,90 | 53,90 |
| Cx Pres Transp | 40,90 | 43,90 |
| Bombons Caixa | 68,29 | 72,80 |
| Bombons Palha | 36,90 | 39,90 |
| Lata de Bombom | 61,90 | 65,90 |
| Lata de Cocada | 48,29 | 51,90 |
| Lata de Lascas | 39,79 | 42,90 |
| Fondue | 51,90 | 55,90 |
| Cesta Grande | 45,10 | 48,00 |
| Cesta Pequena | 26,15 | 27,90 |
| Caixote | 52,70 | 56,50 |

## Observações
- **O atacado é ~metade do varejo** (ex.: Cocada 45g — atacado R$ 3,30 vs varejo R$ 6,99).
- **"Com ST" ≈ "Sem ST" + ~13%** (o imposto embutido).
- Vários produtos do varejo são **terceirizados/revenda** (Bala de Coco, Goiabada,
  Amanteigados, Brownie) — não entram no custo de produção da fábrica.
- Cocada 45g no varejo: usa-se R$ 6,99 (cadastro SIGE) — não consta explícito nesta
  tabela de quiosque; confirmar.
