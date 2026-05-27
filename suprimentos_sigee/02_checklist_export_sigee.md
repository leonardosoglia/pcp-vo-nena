# Checklist — Exports do Sigee Cloud necessários

> Pra Leonardo levar pra Mariana. Curto. 3 arquivos pra exportar.

---

## Antes de começar

- [ ] Login no Sigee Cloud (`app.sigecloud.com.br`)
- [ ] Criar pasta no Drive/computador chamada `suprimentos_sigee_<DATA>`
- [ ] Onde achar as funções: **Estoque** (menu lateral)

---

## Arquivo 1 — Matérias-Primas (cadastro completo + saldos)

**Caminho:** Estoque → Produtos → Mais Ações → Importar/Exportar
**Filtro a aplicar:**
- Gênero do Produto = `01 – Matéria-Prima`
- Cadastro Inativo = NÃO (só ativos)

**Exportar como:** `MateriasPrimas_28_05_2026.xlsx` (ou data do dia)

**Colunas esperadas** (verificar se vêm todas):
- Nome
- Código
- Categoria
- Marca
- Fornecedor Padrão
- EstoqueUnidade (unidade de medida)
- PrecoCusto
- **EstoqueAtual** ⭐ — se essa coluna não vier, exportar Relatório de Posição (Arquivo 3)

---

## Arquivo 2 — Embalagens (potes, cintas, plásticos, etiquetas)

**Caminho:** mesmo do Arquivo 1
**Filtro:**
- Categoria = `EMBALAGEM`
- OU Gênero = `02 - Embalagem` (se existir)
- Cadastro Inativo = NÃO

**Exportar como:** `Embalagens_28_05_2026.xlsx`

---

## Arquivo 3 — Posição de estoque (saldos atuais)

**SÓ SE** o Arquivo 1 não trouxer a coluna de estoque atual.

**Caminho provável:** Relatórios → Estoque → Posição Atual / Saldo de Estoque
**Filtro:** Matérias-primas ativas
**Exportar como:** `Estoque_Atual_28_05_2026.xlsx`

---

## Onde colocar os arquivos

Salvar todos em:

```
C:\Users\bandr\OneDrive\Documentos\DISCIPLINAS\P10\Estágio\Novo projeto\suprimentos_sigee\
```

(Mesma pasta deste arquivo.)

---

## Outras coisas pra perguntar à Mariana

- [ ] **Achocolatado vs Cacau em pó** — qual é usado na Cocada Brigadeiro?
- [ ] **Açúcar cristal** está inativo no Sigee? Por quê?
- [ ] **Café** usado nas receitas — é sachê 40g ou almofada 500g?
- [ ] **Sal** — não cadastrado como matéria-prima. É comprado avulso?
- [ ] **Sorbato** — usa Kunda 25kg (R$ 53) ou Import 25kg (R$ 583)? Preços muito diferentes
- [ ] Para cada um dos 33 insumos: **estimar lead time** (1, 3, 7 dias?)
- [ ] Para cada um: **estimar estoque mínimo** (em unidades da própria matéria)

---

## Próximo passo após a Mariana entregar

Leonardo me avisa "Mariana entregou" + caminho dos arquivos. Eu:

1. Leio os 3 Excel
2. Atualizo a tabela de matches com os confirmados
3. Rodo o script `importar_csv_sigee.py` (que vou criar agora)
4. Atualizo os 33 insumos no banco com: estoque_atual, custo, fornecedor, lead_time, estoque_minimo
5. Te entrego o relatório de import (X criados, Y atualizados, Z erros)
6. Em seguida, **destravamos a Etapa E** (auto-baixa por produção)
