# Ficha de Entrevista — PCP Vó Nena

**Data:** ____ / ____ / 2026
**Entrevistado:** Eraldo (responsável da Gestão)
**Entrevistador:** Leonardo Sóglia
**Duração estimada:** 60 minutos
**Local:** ____________________________

---

## Objetivo

Validar achados do sistema (Insights iniciais) e coletar informações para construção do módulo de **Suprimentos** (insumos, embalagens, receitas).

Sistema acessível em: `https://pcp-vo-nena.streamlit.app`
Página de Insights: `https://pcp-vo-nena.streamlit.app/Insights`

Antes da reunião: abrir a página de Insights no celular pra acompanhar conforme as perguntas.

---

## BLOCO 1 — Achado principal (Insight Master)

> **Contexto pra apresentar:**
> Analisei as 13 folhas registradas. O sistema descobriu que **alguns sabores faltam consistentemente** (Tradicional e Leite Condensado em 45g) e **outros sobram** (Pé de Moça 45g). A regra que você ensinou — Tradicional = 2× Leite Condensado = 4× B/C/P — não está sendo respeitada na prática. A razão T/L observada variou de 0.77 a 3.33, quando o esperado era 2.0.

**1.** Você sente esse padrão? Tradicional/Leite Condensado faltando e Pé de Moça sobrando?

> Resposta: __________________________________________________________________
>
> ________________________________________________________________________

**2.** Por que a proporção Tradicional/Leite Condensado oscila tanto? É limite de capacidade da Produção? Decisão consciente?

> Resposta: __________________________________________________________________
>
> ________________________________________________________________________

**3.** Pé de Moça que sobra na 45g — vai pra onde? Pote? Vencimento? Doação? Outra coisa?

> Resposta: __________________________________________________________________
>
> ________________________________________________________________________

**4.** Tem demanda fixa de cliente que justifique produzir mais Pé de Moça que a regra manda? Quanto? Em quais dias?

> Resposta: __________________________________________________________________
>
> ________________________________________________________________________

---

## BLOCO 2 — Tachos parciais

> **Contexto:** o sistema viu que **33% das ordens de produção** saíram com tacho parcial (bandejas que não completam tacho de 8, ou de 3 no caso do Zero).

**5.** Quando você ordena 18 bandejas de Tradicional em vez de 16 ou 24, o ingrediente extra:

- ( ) Vira potes do mesmo sabor
- ( ) É guardado pra próximo tacho
- ( ) É descartado
- ( ) Outro: ______________________________________________________________

**6.** Tachos parciais acontecem por necessidade (urgência de cliente) ou por planejamento mesmo?

> Resposta: __________________________________________________________________
>
> ________________________________________________________________________

**7.** Sistema sugerir arredondamento (ex: "18 = 2 tachos + 2 sobras. Sugere 16 ou 24?") seria útil ou atrapalha o controle?

> Resposta: __________________________________________________________________

---

## BLOCO 3 — Anomalias palha e embalagem

**8.** Nos dias 04/05 e 06/05 o sistema detectou Leite em Pó com produção bem maior que Tradicional. Foi encomenda específica de cliente ou erro de lançamento?

> Resposta: __________________________________________________________________

**9.** Em dias com >3000 unidades de embalagem (Leonília sobrecarregada), o que acontece? Hora extra? Outro ajuda?

> Resposta: __________________________________________________________________

**10.** A capacidade da Embalagem é mesmo ~3000 und/dia? Tem dias melhores/piores?

> Resposta: __________________________________________________________________

---

## BLOCO 4 — Insumos e Suprimentos (cadastro inicial)

> **Contexto pra apresentar:**
> Próximo passo do sistema é controlar matéria-prima e insumos. Sistema vai saber quanto de cada coisa é consumido por bandeja, alertar quando estiver acabando, sugerir compras. Precisa cadastrar a lista inicial.

**11.** **Lista de insumos principais** (marca os que usam e adiciona o que falta):

Cocada:
- ( ) Coco ralado — fornecedor: ____________ — lead time: ___ dias
- ( ) Leite condensado — fornecedor: ____________ — lead time: ___ dias
- ( ) Leite em pó — fornecedor: ____________ — lead time: ___ dias
- ( ) Açúcar refinado — fornecedor: ____________ — lead time: ___ dias
- ( ) Açúcar cristal — fornecedor: ____________ — lead time: ___ dias
- ( ) Chocolate em pó / cacau — fornecedor: ____________
- ( ) Café — fornecedor: ____________
- ( ) Outros: ____________________________________________________________

Palha:
- ( ) Glucose — fornecedor: ____________
- ( ) Manteiga / gordura vegetal — fornecedor: ____________
- ( ) Saborizante Churros — fornecedor: ____________
- ( ) Saborizante Cookies — fornecedor: ____________
- ( ) Saborizante Limão — fornecedor: ____________
- ( ) Outros: ____________________________________________________________

Pão de Mel / Balas / Doces:
- ( ) Mel — fornecedor: ____________
- ( ) Farinha — fornecedor: ____________
- ( ) Cobertura de chocolate — fornecedor: ____________
- ( ) Outros: ____________________________________________________________

Embalagens:
- ( ) Plástico individual (cocada 45g) — fornecedor: ____________
- ( ) Plástico individual (Mini) — fornecedor: ____________
- ( ) Plástico Pet — fornecedor: ____________
- ( ) Cinta de papel 45g — fornecedor: ____________
- ( ) Cinta de papel Mini — fornecedor: ____________
- ( ) Pote 260g — fornecedor: ____________
- ( ) Pote 605g — fornecedor: ____________
- ( ) Display palha 50g (caixa) — fornecedor: ____________
- ( ) Outros: ____________________________________________________________

**12.** Quem controla o estoque de insumos hoje? Está no Sigee Cloud? Em planilha? Memória?

> Resposta: __________________________________________________________________

**13.** Estoque mínimo de cada insumo (quanto deveria ter sempre disponível) está definido? Ou compra "quando vê que tá faltando"?

> Resposta: __________________________________________________________________

**14.** Quem faz as compras? Eraldo? Outra pessoa? Tem orçamento mensal?

> Resposta: __________________________________________________________________

---

## BLOCO 5 — Receitas (BOM — Bill of Materials)

> **Contexto:** pra cada produto, o sistema precisa saber **quanto de cada insumo** consome. Ex: 1 bandeja de cocada T 45g = X kg de coco ralado + Y litros de leite condensado + Z gramas de açúcar.

**15.** Tem caderno ou planilha com as receitas exatas? Ou está só na memória do Sr. Joel?

> Resposta: __________________________________________________________________

**16.** A receita varia por sabor (T vs L vs B/C/P)? Por tamanho (45g vs Mini vs Pet)?

> Resposta: __________________________________________________________________

**17.** Pode listar a receita aproximada de **1 bandeja de cocada Tradicional 45g**?

| Insumo | Quantidade | Unidade |
|---|---|---|
| Coco ralado | ______ | ( ) kg ( ) g |
| Leite condensado | ______ | ( ) L ( ) g |
| Açúcar | ______ | ( ) kg ( ) g |
| Outro: ___________ | ______ | __________ |
| Outro: ___________ | ______ | __________ |

**18.** Mesma receita pra Mini? Pra Pet? Pra Zero?

> Resposta: __________________________________________________________________

**19.** Algum insumo é **compartilhado** entre cocada e palha? Entre sabores diferentes?

> Resposta: __________________________________________________________________

---

## BLOCO 6 — Sigee Cloud (integração futura)

**20.** Vocês usam o Sigee Cloud hoje? Quais módulos? (Vendas, NFE, Estoque, Fiscal...)

> Resposta: __________________________________________________________________

**21.** Os insumos estão cadastrados no Sigee? Estoque atualizado lá?

> Resposta: __________________________________________________________________

**22.** Você tem credencial de admin? É possível exportar lista de produtos/insumos em Excel/CSV?

> Resposta: __________________________________________________________________

**23.** Sabe se o Sigee tem API (forma do nosso sistema conversar direto com ele)?

> Resposta: __________________________________________________________________

---

## BLOCO 7 — Operação geral (perguntas pendentes do handoff anterior)

**24.** Frequência exata de produção de PM (Pão de Mel) — dias da semana específicos?

> Resposta: __________________________________________________________________

**25.** Existe papelzinho separado pra Bala e PM? Qual formato?

> Resposta: __________________________________________________________________

**26.** Dias de corte de palha (Maria) — confirma Seg/Ter + Qui/Sex?

> Resposta: __________________________________________________________________

**27.** Quem produz os Doces (pequenos doces de leite)? Quando produzem?

> Resposta: __________________________________________________________________

**28.** Capacidade típica do Sr. Joel em tachos/dia?

> Resposta: __________________________________________________________________

**29.** Como funcionam encomendas de cliente? Entram no parâmetro do dia ou são tratadas à parte?

> Resposta: __________________________________________________________________

---

## Espaço pra anotações livres

(Observações do entrevistado que não couberam nas perguntas, ideias dele, preocupações, etc.)

________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________

---

## Pós-entrevista (Leonardo preenche depois)

**Hora de início:** _____ : _____  •  **Hora de fim:** _____ : _____

**Principais aprendizados (3-5 pontos):**

1. _____________________________________________________________________
2. _____________________________________________________________________
3. _____________________________________________________________________
4. _____________________________________________________________________
5. _____________________________________________________________________

**Próximos passos identificados:**

- ( ) ___________________________________________________________________
- ( ) ___________________________________________________________________
- ( ) ___________________________________________________________________

**Disposição da Gestão pra usar o sistema:**

( ) Animada · ( ) Curiosa · ( ) Cautelosa · ( ) Resistente · ( ) Outro: ___________

---

*Após a entrevista: anotar respostas digitalmente no `CADERNO.md` (seção 1 — Descobertas).*
