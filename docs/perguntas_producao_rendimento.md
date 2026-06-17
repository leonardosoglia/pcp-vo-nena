# Perguntas de produção — rendimento e conversões

> Para a Produção / Gestão (e o que o Leonardo sabe do chão de fábrica).
> Cada resposta destrava o cálculo de **custo por unidade** e a **Curva ABC por
> lucro**. Atualizar com as respostas assim que chegarem.

## 1. Rendimento do tacho de cocada — PRIORIDADE (firma 60% dos números)

O custo por unidade depende de **quanto sai de um tacho**. Hoje o sistema assume
**8 bandejas por tacho** (Zero = 3), com a bandeja pronta pra cortar pesando
**~5,5 kg**. Mas a receita entra com ~33 kg de ingredientes e o cozimento evapora
água — então 8 × 5,5 = 44 kg parece impossível; a conta sugere ~4-5 bandejas.

- **1 tacho de cocada tradicional rende quantas bandejas?** (8 mesmo, ou menos?)
- **1 tacho de cocada Zero rende quantas bandejas?** (hoje assumo 3)
- _(Se for mais fácil responder assim:)_ **quantos quilos de cocada pronta saem
  de 1 tacho?**

> Impacto: se for ~4-5 em vez de 8, o custo por unidade ~dobra. O **ranking** dos
> produtos não muda, mas o valor em reais sim.

## 2. Bala de doce de leite — maior venda sem custo (~R$ 19 mil/mês)

Já sei o custo de material de **1 tacho de bala**. Falta a conversão:

- **1 tacho de bala rende quantos pacotes de 400 g?** (ou: **quantos quilos de
  bala** saem de 1 tacho?)
- A unidade "1 tacho = 30 balas" que eu tenho — o que é essa "bala" exatamente
  (uma bala pequena? um pacote?).

## 3. Palha — ~R$ 32 mil/mês sem custo

- **1 bandeja (ou 1 tacho) de palha rende quantos pacotes de 170 g?** Quantos kg?
- _(Obs.: a receita da palha ainda está sem alguns insumos — creme/manteiga/
  maizena. Mesmo com a conversão, o custo da palha sai parcial até confirmarmos
  esses insumos no de-para.)_

## 4. Produtos sem receita — para depois

Vendem bem mas não temos a ficha (BOM): **Doce de Leite Cremoso 700 g** (~R$ 10
mil/mês) e **Cocada Assada na Cumbuca 145 g** (~R$ 9 mil/mês). Quando puder, passar
a receita deles para entrarem no custo.

---

## Respostas — CONFIRMADAS pela fábrica (15/06/2026)

### Cocada — rendimento e formatos
- **Tradicional, Leite Condensado, Brigadeiro, Café, Pé de Moça: 8 bandejas/tacho.**
- **Zero: 3 bandejas/tacho.** Bandeja = **5,5 kg** em todos os sabores.
- (A dúvida do "4-5 bandejas" foi **descartada**: é 8 mesmo. Os custos da tela
  estão corretos, não dobram.)
- **Formatos** em que a bandeja é cortada:
  - **Tablete 45 g** (todos os sabores normais)
  - **Mini 30 g** (normais) · **Mini 27 g** (Zero)
  - **PET = pedaços pequenos num pote plástico:** **160 g** (Leite Cond., Brigadeiro,
    Café, Pé de Moça), **150 g** (Tradicional), **100 g** (Zero).

### Bala (Bala de Doce de Leite)
- **1 tacho = 30 balas · cada bala = 400 g.** Custo de material ≈ R$ 6,47/bala.
- É um doce próprio (não revenda): cremosa por dentro, casca fina crocante por
  fora; embrulhada em papel filme + pano + cinta. Tem fotos no banco de fotos.

### Palha
- **1 bandeja de palha = 30 PETs (potes) de 160 g** cada (= 4,8 kg/bandeja).
- Também vendida em **display (caixa)**: 4 tradicionais + 4 leite em pó + 2 churros,
  cada palha do display pesa **50 g** (display = 10 palhas = 500 g).
- **Receitas** (Tradicional=chocolate, Leite em Pó=Ninho, Churros, Cookies, Limão):
  **já estão no BOM do projeto** (`seed_bom_completa.py`); as fotos das fichas
  técnicas (Pequenas Mordidas) confirmam. Os outros sabores (morango, paçoca) =
  desconsiderar por ora. _Custo da palha ainda sai PARCIAL_ até confirmarmos o
  custo de creme de leite / manteiga / biscoito maisena no de-para (§7).

### Pão de Mel
- Receita já no BOM (`pm_bolo`). Foto da receita manuscrita confere
  (farinha 360 g, mascavo 340 g, cacau 160 g, leite 230 g, palmiste 220 g, mel
  9 colheres, canela/cravo/essência 3 g, antimofo 10 g, amaciante 20 g,
  bicarbonato 11 g, fermento 14 g).

### Cocada Assada na Cumbuca 145 g — recebida 17/06/2026 (massa completa; casco fora)
- Receita **por lote de 30 cumbucas**, assada em vasilhas: 12 ovos (só a gema; clara
  descartada), 3 kg leite condensado, **2 kg coco ralado**, 500 g açúcar, 150 ml leite,
  60 g sorbato, 5 g sal. (O coco era o furo do rótulo — resolvido: 2 kg.)
- **Cumbuca** (casco do coco): comprada vazia, lote de 300; **150–160 descartadas/lote**
  (aproveitamento ~47–50 %). **Deixada FORA do custo por enquanto** (sem dado de custo; não
  está cadastrada no SIGE) → custo da assada sai **subestimado** até o casco entrar.
- Etiqueta da cocada assada no SIGE = R$0,18/un (embalagem).
- Detalhe completo no `CADERNO.md` → Bloco 5.

### Pendente
- **Banco de fotos** (`entrevistas/fotos_produtos/`): Leonardo pediu uma leitura de
  todas as fotos dos produtos comercializados (preencher os `descricao.md`).
- Produtos sem receita no BOM: **Doce de Leite Cremoso 700 g** (e os terceirizados:
  bala de coco, goiabada, doce de leite cubos/barra). **Cocada Assada 145 g** = recebida
  parcialmente (faltam coco + custo da cumbuca, acima).
