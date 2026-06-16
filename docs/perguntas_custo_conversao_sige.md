# Perguntas — Custo de conversão e estrutura financeira (SIGE)

> Levantadas a partir da varredura completa (somente leitura) do SIGE em 15/06/2026.
> Objetivo: destravar o **custo total** e a **margem real** por produto. Hoje o
> sistema tem o custo da matéria-prima e a receita de venda, mas **não** o custo
> de conversão (mão de obra, energia, overhead) da produção.

## O diagnóstico (em uma frase)

O SIGE tem o **custo e a identidade do insumo** (preço de custo, NF-e) e tem a
**receita de venda**. O que ele **não** mostra de forma utilizável é o **custo de
conversão alocado à fábrica** — porque, na janela analisada, a folha de
pagamento, a energia e o overhead da produção **não aparecem lançados sob o CNPJ
industrial** (Soglia Indústria). Eles estão concentrados em outra empresa do
grupo e/ou roteados por outra via. Conclusão: o custo de conversão precisa entrar
por **levantamento/rateio externo** (contagem na fábrica), não por leitura direta
do ERP — e isso é uma decisão metodológica, não uma falha do sistema.

Sinais que sustentam o diagnóstico:
- A Soglia Indústria aparece com **zero folha de pagamento** na janela de 30 dias;
  o único salário lançado está na Pequenas Mordidas (~R$ 3,9 mil/mês — compatível
  com 1-2 pessoas, não com um chão de fábrica).
- **Duas das quatro empresas com venda** (Soglia Comércio e Soglia & Schneider)
  registram **só receita e nenhuma despesa**.
- "Energia elétrica da fábrica" aparece como ~R$ 70/mês — impossível para quem
  ferve tacho o dia inteiro.
- Os Boletos mostram a conta "Itaú Fábrica PM" — fábrica e Pequenas Mordidas
  **compartilham conta bancária**.

---

## Para o contador — prioridade 1 (destravam o custo)

1. **A folha de pagamento da equipe da fábrica** (Produção, Corte, Embalagem e
   auxiliares) está lançada em **qual CNPJ** e em **qual conta**? No SIGE, a Soglia
   Indústria aparece com folha zerada e só a Pequenas Mordidas tem salário — a PM
   é a empresa que paga a equipe toda?

2. O **custo de mão de obra, energia e aluguel da produção** está amarrado a algum
   **centro de custo** no SIGE (ex.: "Fábrica" / "Produção")? Qual o **nome exato**?
   (Preciso filtrar a despesa por centro de custo, não por empresa.)

3. **(Gestão + contador)** Existe **preço de transferência** entre os CNPJs? A
   Soglia Indústria fatura a produção para as empresas de varejo por um valor
   interno **antes** da venda no balcão? Se sim, **é esse o "custo de fábrica"** que
   eu deveria usar — não o preço de balcão.

## Para o contador — prioridade 2

4. O filtro de data dos relatórios financeiros é por **data de competência** ou de
   **vencimento**? (Decide se a folha mensal e as contas fixas aparecem ou somem da
   janela que eu leio.)

5. As **compras de matéria-prima** entram como **despesa do período** ou como
   **estoque/CMV** com baixa na venda? (Preciso saber para não contar a mesma
   compra duas vezes.)

6. **(Gestão)** A conta de **luz/água/gás da fábrica** está separada das lojas?

## Para a Gestão — prioridade 3

7. A fábrica usa **Ordem de Produção** no SIGE? O módulo de OP retorna **zero**
   registros. Sem OP com rendimento e baixa de insumo, o sistema nunca terá o
   **consumo e o rendimento reais do tacho** — confirma que isso hoje é só no papel
   / no nosso PCP?

8. Cada produto tem **preço diferente por canal** (revenda, PDV, atacado)? O SIGE
   lista 6 tabelas de preço; hoje uso 1 preço por produto. Qual tabela vale para
   cada tipo de cliente?

9. **(Contador)** Dá para exportar uma **DRE consolidada do grupo** (as empresas
   juntas) de um mês fechado — Receita, CMV, Despesa com pessoal, Resultado? Quero
   validar a leitura via API contra a contabilidade oficial.

---

## Atualização — após cavar mais o financeiro (15/06/2026)

A investigação mais funda **confirmou o teto** do que o SIGE oferece sobre custo:

- O SIGE **não usa centro de custo** — todos os lançamentos estão "sem centro".
  Não há como separar "custo de produção" dentro do financeiro como ele está hoje.
- Os lançamentos de despesa da fábrica são **só compras** (matéria-prima e
  embalagem, via nota de entrada). Não há mão de obra nem energia relevantes
  lançadas sob a fábrica.
- **Não há transferência bancária entre os CNPJs** registrada no período.

Perguntas adicionais que surgiram:

10. **(Contador)** A **folha de pagamento completa** da empresa é processada
    **dentro do SIGE** ou num sistema de folha **separado**? No SIGE só aparece
    ~R$ 4 mil de salário no mês — muito abaixo do real para a equipe da fábrica.

11. **(Gestão + contador)** A empresa estaria disposta a **marcar as despesas de
    produção a um centro de custo** ("Produção") no SIGE daqui pra frente? Isso
    permitiria o sistema calcular o custo de conversão automaticamente no futuro —
    é uma melhoria de processo simples e de alto retorno.

## Lembrete — disparidade ainda aberta (produção)

- **Rendimento do tacho:** quantas bandejas de 5,5 kg saem de **1 tacho** de cocada?
  O sistema assume 8 (≈ 44 kg), mas a receita entra com ~33 kg e o cozimento
  evapora água → a conta sugere ~4-5 bandejas. Isso **dobra** o custo por unidade.
