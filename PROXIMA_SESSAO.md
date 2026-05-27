# Próxima sessão — Etapa E (Auto-baixa de Insumos)

> Nota planejada em 28/05/2026. Foco da próxima sessão: implementar a
> baixa automática de insumos quando uma folha é salva.

---

## Contexto

A BOM (Bill of Materials) foi cadastrada na Etapa D: 33 insumos + 91 linhas
de receita cobrindo cocada × 6, palha × 5, PM e bala. Função
`calcular_necessidades_do_dia(data)` já existe em `database.py` e calcula
quanto de cada insumo a folha do dia consome.

**Falta:** transformar esse cálculo em **baixa real no estoque** quando
a folha é salva.

---

## O que precisa ser feito

### Backend

1. **Função `baixar_insumos_da_folha(data)`** em `database.py`
   - Lê a folha do dia (cocada, palha, PM, bala)
   - Pra cada ordem (`ord_prod_band`, `ord_pm`, `ord_balas`, etc.), calcula consumo via BOM
   - Registra `movimento_insumo` tipo `saida`, origem `producao`, ligado à data
   - Decrementa `estoque_atual` em `insumos`
   - Tudo numa transação atômica (rollback total em falha)

2. **Hook no `salvar_folha_completa`**
   - Após o save da folha, chamar `baixar_insumos_da_folha(data)`
   - Idempotente: se já houve baixa pra essa data, NÃO duplicar
     (registrar `origem_id = "folha_{data}"` e checar antes)

3. **Função `reverter_baixa_da_folha(data)`**
   - Útil se a folha for editada/excluída
   - Cria movimentos de `entrada` correspondentes (estorno)

### UI

4. **Página `pages/3_Suprimentos.py`** — aba "Movimentações"
   - Já existe parcialmente, só completar
   - Mostrar movimentos do dia com filtro por insumo, tipo, origem
   - Coluna "data de produção" linkando à folha

5. **Aviso no formulário de Lançamento**
   - Mostrar preview do consumo antes de salvar: "Esta folha vai consumir
     X kg de leite, Y kg de açúcar, etc."
   - Permitir cancelar se algum insumo ficar negativo

6. **Página Início** (Home)
   - Card "Insumos abaixo do mínimo" (depende de ter estoque_minimo cadastrado)

### Edge cases

- **BOM ausente** pra um produto — avisar mas não bloquear save da folha
- **Estoque negativo** — registrar consumo mas marcar alerta visual
- **Folha editada** — recalcular baixa (diferença entre nova e antiga)
- **Folha excluída** — estornar baixa

---

## Esforço estimado

| Item | Tempo |
|---|---|
| `baixar_insumos_da_folha` + idempotência | 1-2h |
| Hook no save + reverter | 1h |
| Página Suprimentos (movimentações) | 1h |
| Preview no Lançamento | 1h |
| Testes contra folhas existentes | 1h |
| **Total** | **5-6h (1 sessão longa)** |

---

## Antes de começar — preciso de você

Nada bloqueante. Posso atacar diretamente quando você voltar. Mas seria
útil saber:

1. Você quer **preview obrigatório** antes de salvar, ou baixa **automática silenciosa**?
2. Quando uma folha for **editada**, deve recalcular baixa ou só na primeira save?
3. Quer que eu **rode contra as 17 folhas históricas** pra ter o histórico de
   consumo populado, ou começamos do zero?

---

## Tarefas suas pra antes da próxima sessão

| | Ação | Tempo |
|---|---|---|
| ☐ | Ler `tcc/capitulos/1_introducao.md` e me devolver com correções | 20 min |
| ☐ | Ler `relatorio_estagio/secoes/1_introducao.md` e `2_empresa.md` | 15 min |
| ☐ | Conversar com orientador (2 decisões de escopo + template ABNT UFCG) | 1 reunião |
| ☐ | Pegar com Gestão/Mariana: CNPJ, endereço, datas/CH do estágio | 1 conversa |
| ☐ | No HF Spaces, clicar no botão "Cadastrar BOM completa" da página Admin Seed | 30 s |
| ☐ | (Semana que vem) Configurar `ANTHROPIC_API_KEY` no HF | 10 min |
| ☐ | (Opcional) Tirar fotos da fábrica pra anexos | quando der |

Quando voltar à sessão, é só dizer "vamos pra Etapa E" e eu retomo daqui.
