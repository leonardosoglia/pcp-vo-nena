# Requisitos da integração PCP ↔ SIGE — o que a Gestão pediu e o que confirmar

> **Doces Vó Nena · reuniões com a Gestão em 14/06/2026.**
> Fonte: `audios/docs/transcricao_reuniao_gestora.md`. Arquitetura em
> [`ARQUITETURA_SIGE.md`](ARQUITETURA_SIGE.md).

---

## 1. O que a Gestão pediu

- **Fechar a cadeia (ciclo de materiais) sem trabalho manual:** entrada de NF-e por
  XML abastece o estoque; a OP explode a ficha técnica, pré-reserva e baixa os
  insumos; a finalização registra o rendimento. *"Quanto mais automatizado, melhor."*
- **Acompanhar tudo por números**, reduzindo desperdício: se o número não é
  acompanhado, "o tanto que você fez se perdeu ali no meio".
- **Usar o rendimento como sinal de qualidade/processo:** planejou render 70,
  rendeu 60 → investigar (leite aguado, ponto, tempo de espera do lote).
- **Rastreabilidade por lote** na baixa dos insumos.
- **Que o Leonardo explore o módulo de produção (PCP) do SIGE** e avalie se
  funciona para a operação — a Gestão observou que hoje ele está **vazio** (sem
  cadastro de produtos, sem controle, sem base lançada).
- **Manter a decisão de produção com as pessoas** (Gestão + planejamento), não com
  o sistema.

---

## 2. Requisitos da integração (derivados)

1. **Somente leitura no SIGE** por padrão — o nosso PCP lê, não altera o ERP.
2. **A OP é o ponto de ligação** entre a decisão humana e o ciclo do SIGE.
3. **Ler do SIGE:** estoque, OPs (situação/produtos/lotes/datas), rendimento e
   custo — para planejar, analisar e reconciliar.
4. **Reconciliar** o estoque teórico do SIGE com a contagem física → divergência
   vira ajuste de inventário. *(implementado em `reconciliacao_sige.py`)*
5. **Ramo de escrita (entrada da OP) isolado e configurável**, desligado até a
   decisão da Gestão. Nunca escrever no SIGE nesta fase.
6. **Não duplicar** o controle de materiais: o SIGE é a fonte do ciclo de
   materiais; o nosso PCP é a camada de planejamento/análise.

---

## 3. Perguntas a confirmar com a Gestão

### (a) A OP entra no SIGE manual ou via nosso sistema (API)?
O nosso plano de produção (decidido pelas pessoas) precisa virar uma OP no SIGE.
Duas opções:
- **Manual** — uma pessoa lança a OP no SIGE a partir do nosso plano → integração
  segue 100% somente leitura. **(recomendado para começar)**
- **Via API** — o nosso sistema cadastra a OP (`POST /OrdensProducao/Cadastrar`) →
  seria o **único ponto de escrita**.
> **Impacto:** define se a integração permanece read-only. O ramo de escrita já
> está isolado e desligado no código, aguardando esta resposta.

### (b) As fichas técnicas (receitas) passam a ser fonte única no SIGE?
Hoje as receitas estão **no nosso sistema** (BOM da Etapa D) **e** precisam estar
no SIGE para a OP explodir os insumos.
- As fichas serão mantidas **no SIGE como fonte única**, e o nosso PCP só **lê**?
- Ou seguem **espelhadas** (cadastradas nos dois), com algum processo de
  sincronização?
> **Impacto:** evita receita divergente entre os dois sistemas. Recomenda-se fonte
> única no SIGE + leitura nossa, para não manter duas verdades.

### (c) O que a API do SIGE expõe de fato para leitura?
*(Já levantamos tecnicamente em 14/06 — confirmar com ela o uso operacional.)*
- **OPs:** ✅ `GET /OrdensProducao/Pesquisar` existe e responde (hoje **vazio** —
  módulo de produção sem dados ainda). **Quando começam a lançar OPs no SIGE?**
- **Lotes:** vêm **dentro da OP** (não há endpoint isolado). OK?
- **Rendimento:** sai da **avaliação/finalização** da OP — os campos exatos só dá
  pra validar na **1ª OP real**. Podemos cadastrar uma OP de teste?
- **Movimentações de estoque:** ❌ a API **não expõe** o histórico de
  movimentações (só o saldo atual e a gravação). **Isso é limitação aceitável**,
  ou há outro caminho (relatório/export) para auditar movimento por movimento?

### (d) Onde a contagem física é registrada e como entra o ajuste?
A reconciliação compara SIGE × físico. Precisamos definir:
- A **contagem física** (feita na fábrica, ~7h–10h) é registrada **no nosso PCP**
  (origem `contagem`/inventário) e/ou **no SIGE** (ajuste de estoque)?
- Quando há divergência, **quem lança o ajuste** e **em qual sistema** ele é a
  verdade?
> **Recomendação:** registrar a contagem no nosso PCP (vira a carga inicial real e
> zera os saldos negativos da auto-baixa); o ajuste no SIGE é lançado pela
> Suprimentos/estoquista, mantendo o ERP como verdade contábil.

---

## 4. Pergunta extra que surgiu no levantamento técnico

- **Qual depósito do SIGE é o da fábrica/matéria-prima?** Há 22 depósitos; o mais
  provável é **"FABRICA"** (e os da **PEQUENAS MORDIDAS**, a produtora) — os demais
  são lojas. Confirmar para a reconciliação ler o saldo do depósito certo.
- **Custos quebrados e cadastros duplicados** no SIGE (já mapeados no de-para):
  vale alinhar a limpeza com a Suprimentos (ver `suprimentos_sigee/de_para_sige.md`).
