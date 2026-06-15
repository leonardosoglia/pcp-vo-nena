# Arquitetura da integração PCP ↔ SIGE Cloud

> **Doces Vó Nena · definido com a Gestão (reuniões 14/06/2026).**
> Base: `audios/docs/transcricao_reuniao_gestora.md`. Decisões confirmadas por Leonardo.
> Documento de referência do projeto (vira capítulo do TCC).

---

## 0. Princípio que orienta tudo: a decisão de produção é HUMANA

**Nenhum sistema decide o que produzir** — nem o SIGE, nem o nosso PCP. Quem
define o que cortar, produzir e embalar a cada dia são **as pessoas responsáveis
(a Gestão, responsável pela produção, em conjunto com o planejamento/PCP)**,
olhando a realidade do dia: capacidade instalada, equipe disponível e demanda.

O nosso PCP **apoia** essa decisão com sugestões, parâmetros e dados; a **palavra
final é das pessoas**. Esse princípio ("o sistema sugere, a gestão decide") é o
mesmo que guia o projeto inteiro e não muda com a integração.

---

## 1. Papéis: quem é fonte da verdade de quê

| | **SIGE Cloud (ERP)** | **Nosso PCP (Streamlit/Supabase)** |
|---|---|---|
| É a verdade de… | **Ciclo de materiais** (contábil/fiscal): estoque por NF-e, fichas técnicas, ordens de produção, lotes, rendimento. | **Operação do chão de fábrica**: folha diária, parâmetros, sugestões de corte/produção, análises, contagem física. |
| Origem do dado | Nota fiscal (XML) e lançamentos da OP. | Registro diário do que acontece na produção. |
| Papel na integração | **Sistema de registro** do ciclo de materiais. | **Camada de planejamento e análise** que lê o SIGE. |

A integração **não duplica** o controle de materiais no nosso sistema — ela
**lê** o que o SIGE já controla e usa isso para planejar, analisar e reconciliar.

---

## 2. O SIGE como sistema de registro do ciclo de materiais

Fluxo que a Gestão descreveu (e que o SIGE executa):

1. **Entrada por NF-e (XML).** A nota fiscal de compra entra pelo XML e **abastece
   o estoque** automaticamente (ex.: 10 kg de coco entram pelo XML da nota).
2. **Fichas técnicas (receitas) ficam no SIGE.** Cada produto tem sua ficha
   (BOM) cadastrada lá.
3. **Ordem de Produção (OP) explode a ficha.** Ao gerar a OP (ex.: 10 receitas de
   cocada tradicional), o SIGE calcula e **separa os insumos** (coco, leite, etc.).
4. **Pré-reserva.** Os insumos da OP ficam **pré-reservados** no estoque — somem
   da necessidade de compra (não aparecem mais para comprar).
5. **Baixa por lote.** O estoquista, ao retirar, **confirma a baixa dos lotes** —
   isso dá **rastreabilidade** do produto por lote.
6. **Finalização com rendimento real.** Ao finalizar a OP, registra-se o
   **rendimento** efetivo. Exemplo dado pela Gestão: planejou-se render 70,
   rendeu 60 → **há um erro** (leite com mais água, ponto não atingido, lote
   esquecido tempo demais). O desvio de rendimento vira sinal de problema.

Esse ciclo **fecha a cadeia** (compra → produção → baixa → rendimento) **sem
preenchimento manual**, o que reduz desperdício e dá números para acompanhar.

---

## 3. A Ordem de Produção é o ponto de ligação

```
   PESSOAS decidem a produção           SIGE roda o ciclo                NOSSO PCP
   (Gestão + planejamento,        ┌────────────────────────────┐     (lê de volta)
    olhando a realidade do dia)   │ OP explode a ficha técnica  │
            │                     │ → pré-reserva insumos       │   • planeja
            │   vira uma          │ → baixa por lote (rastreio) │   • analisa
            └─────  OP  ────────► │ → finaliza c/ rendimento    │ ──► • reconcilia
                                  │ → estoque atualizado        │     (SIGE × físico)
                                  └────────────────────────────┘
```

A **OP é a peça que liga os dois mundos**: a decisão humana de produzir vira uma
OP no SIGE; o SIGE roda o ciclo de materiais; e o **nosso PCP lê de volta** (OPs,
reservas, baixas, lotes, rendimento e estoque) para **planejar, analisar e
reconciliar**.

---

## 4. Princípio SOMENTE LEITURA (e o único ponto de escrita, ainda pendente)

A integração é **somente leitura** no SIGE: o nosso PCP **lê**, mas **não altera
nada** no ERP. Isso preserva o controle do ciclo de materiais inteiramente com a
empresa e evita conflito de escrita.

**A única exceção possível — e que está EM ABERTO — é COMO a OP entra no SIGE:**

- **(a) OP lançada manualmente** por uma pessoa, a partir do plano do nosso PCP →
  mantém a integração 100% read-only. *(caminho conservador)*
- **(b) OP escrita pelo nosso sistema via API** (`POST /OrdensProducao/Cadastrar`)
  → seria o **único ponto de escrita** do sistema no SIGE.

> **Decisão pendente com a Gestão.** Até ela ser tomada, o ramo de escrita fica
> **isolado e desligado** no código (`sige_cloud_api.cadastrar_ordem_producao` /
> `finalizar_ordem_producao`: bloqueadas por `SIGE_PERMITIR_ESCRITA` **e** com
> `NotImplementedError`). **Nada é escrito no SIGE.**

---

## 5. O que o nosso PCP lê do SIGE — e para quê

| Lemos do SIGE | Para quê |
|---|---|
| **Cadastro de produtos** (custo, fornecedor, identidade) | Custo de produção; ligar insumo ao ERP. *(já implementado — de-para + importação de custo)* |
| **Saldo de estoque** | Reconciliação contra a contagem física; insumo da necessidade de compra. |
| **Ordens de produção** (situação, produtos, lotes, datas, responsáveis) | Acompanhar a produção planejada/em curso; base do planejamento. |
| **Rendimento / avaliação da OP** | Análise de rendimento (planejado × produzido × descarte) → detectar problema de processo. |
| **Lotes** (dentro da OP) | Rastreabilidade. |

**Reconciliação** (já implementada, `reconciliacao_sige.py`): cruza o estoque
**teórico do SIGE** com o estoque do **nosso sistema / contagem física**, item a
item, e aponta a divergência. Essa diferença é o gatilho do **ajuste de
inventário** e da investigação (sumiço, perda, baixa não lançada). Respeita o
princípio das **3 camadas de estoque** (SIGE contábil × nosso sistema × físico
real — Forrester/stock-vs-flow, já adotado no projeto).

---

## 6. O que a API do SIGE expõe hoje (fatos técnicos, confirmados em 14/06/2026)

**Leitura disponível (e já no nosso cliente `sige_cloud_api.py`):**
- `GET /Produtos/GetAll` e `/Produtos/Pesquisar` — catálogo, custo, saldo, fornecedor.
- `GET /Estoque/BuscarQuantidades` — saldo por depósito.
- `GET /Depositos/GetTodosDepositos` — 22 depósitos (o da fábrica é **"FABRICA"**; há os da **PEQUENAS MORDIDAS**, a produtora).
- `GET /Empresas/GetTodasEmpresas` — 5 empresas (multi-CNPJ; 1 credencial cobre todas).
- `GET /OrdensProducao/Pesquisar` — ordens de produção (situação, produtos, lote, datas). **Hoje devolve 0** — o módulo de produção do SIGE ainda está vazio (confirmado pela Gestão). Fica pronto pra quando começarem a lançar OPs.
- `GET /OrdensProducao/BuscarCheckListQualidade` — checklist de qualidade da OP.

**Escrita (bloqueada — modelo read-only):** `Produtos/Criar|Atualizar`,
`ProdutosEstoque/Salvar`, `OrdensProducao/Cadastrar|Finalizar`.

**Limitações confirmadas (viram pergunta/decisão):**
- **Não há endpoint de leitura do histórico de movimentações de estoque** (só o
  saldo atual e a gravação de movimento). Rastreabilidade de movimento depende da OP.
- **Não há endpoint de lotes isolado** — lotes vêm **dentro da OP**.
- **Rendimento** sai da avaliação/finalização da OP; os campos exatos só serão
  validados na **1ª OP real** (hoje não há OPs para inspecionar).

---

## 7. Estado e próximos passos

- ✅ Leitura de produtos/custo + de-para + importação de custo (feito).
- ✅ Cliente estendido: depósitos, empresas, OPs, checklist (read-only).
- ✅ Reconciliação estoque SIGE × nosso sistema (feito, `reconciliacao_sige.py`).
- ⏳ **Carga inicial de estoque** via contagem física → torna a reconciliação real.
- ⏳ **Análise de rendimento** de OP → aguarda a 1ª OP no SIGE.
- ❓ **Decisão da OP** (manual × API) → ver `docs/requisitos_gestora_sige.md`.

**Regra firme desta fase: a integração é SOMENTE LEITURA até a Gestão decidir o
caminho da OP. O ramo de escrita está isolado e não implementado.**
