# Handoff — Integração com o SIGE Cloud

> **⚠ PARCIALMENTE SUPERADO (28/05/2026).** A fonte atual da integração SIGE é:
> - `CADERNO.md` Bloco 6 — API confirmada, endpoints, decisão de arquitetura (modelo B).
> - `sige_cloud_api.py` — cliente HTTP read-only já implementado.
> - `suprimentos_sigee/03_solicitar_credenciais_api.md` — como pedir credenciais.
> - Aba "Importar do SIGE" em `pages/3_Suprimentos.py` — upload de planilha (plano B sem API).
>
> Este arquivo mantém o histórico da exploração de 21/05 (ainda útil pra entender
> o catálogo do SIGE e as categorias). O que mudou: a API EXISTE (era "não sei se
> existe" aqui) e a decisão é read-only.

> Documento de apoio. Ler depois do `HANDOFF_COMPLETO.md`.
> Atualizado em 21/05/2026 com a exploração real do SIGE Cloud.

---

## Objetivo

Trazer a lista de **insumos** (matéria-prima, embalagens, potes, cintas, displays)
do SIGE Cloud — o ERP da Doces Vó Nena — pra a tabela `insumos` do nosso sistema,
sem digitar tudo à mão. Isso destrava a Etapa C (cadastro de insumos) do roadmap.

---

## O que descobrimos do SIGE Cloud (sessão 21/05/2026)

O SIGE Cloud fica em `app.sigecloud.com.br`. O Leonardo tem acesso (conta do Eraldo).
**O Claude NÃO acessa** — conta privada. O Leonardo é a ponte: clica, manda print,
o Claude orienta.

### Estrutura relevante
- **Estoque → Produtos** — o cadastro de produtos. Tem busca e "Busca Avançada".
- **Estoque → Produtos → menu "Mais Ações" → "Importar/Exportar"** — **existe
  exportação.** É o caminho pra tirar os dados (Excel/CSV). ✅
- **Estoque → Categorias de Produtos** — as categorias cadastradas.
- O menu lateral ainda tem **Relatórios** (com sub-relatório de Estoque) e
  **Downloads** — alternativas se a exportação direta não servir.

### O catálogo é GRANDE
O cadastro de Produtos tem MUITO mais itens que os insumos da fábrica (ao buscar
"açúcar" aparecem vários: Caravelas, Arcolor, Mix Confeiteiro, Refinado...).
**Não exportar o catálogo inteiro** — filtrar primeiro.

### Categorias de Produtos (as 9 existentes)
| Categoria | Serve pro módulo de Suprimentos? |
|---|---|
| PRODUÇÃO | **Provavelmente sim** — ingredientes das receitas (a confirmar) |
| EMBALAGEM | **Sim** — embalagens (plástico, cinta, pote, display) |
| PRODUTOS DE USO FABRICA | **Talvez** — conteúdo desconhecido; perguntar ao Leonardo |
| ATIVO | Não — produtos de venda / ativos |
| PRODUTOS LOJA | Não — produtos da loja |
| VENDAS LOJAS | Não |
| PRODUTO INATIVO | Não — desativados |
| Despesas Fixas | Não — despesas, não produtos físicos |
| Confraternizações / Alimentação / Outros | Não |

---

## Plano — onde paramos e o próximo passo

### Próximo passo concreto (retomar aqui)
1. Pedir ao Leonardo: na tela **Estoque → Produtos**, usar **"Busca Avançada"** e
   filtrar por **Categoria = PRODUÇÃO**. Mandar print. Confirmar que são mesmo os
   ingredientes das receitas (coco ralado, açúcar cristal, leite condensado, etc).
2. Idem pra **EMBALAGEM** e perguntar/checar **PRODUTOS DE USO FABRICA**.
3. Com as categorias certas identificadas, exportar (via "Importar/Exportar")
   apenas essas categorias — gera um arquivo Excel/CSV pequeno e limpo.
4. O Leonardo salva o arquivo numa pasta acessível e diz o caminho ao Claude.
5. Claude lê o arquivo, vê as colunas reais, e cria **`importar_csv_sigee.py`** —
   script que mapeia as colunas do SIGE → tabela `insumos` (campos: codigo, nome,
   categoria, unidade, estoque_atual, estoque_minimo, fornecedor, custo_unitario,
   lead_time). Detecta insert vs update por código. Tem dry-run.
6. Leonardo roda o script localmente uma vez; valida no Supabase / na página
   Suprimentos.

### Mapa de colunas (a confirmar quando vir o arquivo exportado)
A tela de Produtos do SIGE mostrava: Tipo · Código Sistema · Código · Nome · Marca
· Fornecedor · Preço. O arquivo exportado provavelmente tem essas + outras
(unidade, saldo de estoque). Ajustar o mapeamento ao ver o arquivo real.

---

## Caminhos alternativos (se a exportação não servir)

- **Relatórios → Estoque** — relatórios de estoque costumam ter botão de exportar
  pra Excel/PDF. Um relatório de "posição de estoque" listaria só produtos com
  saldo (= o que a fábrica realmente usa).
- **API do SIGE** — não investigada. O menu tem "Central de Integrações" — pode
  ter API. Só investigar se a exportação manual não bastar (a exportação manual já
  resolve a Etapa C; API seria pra sincronização contínua, fase futura).
- **Cadastro manual** — se o SIGE for bagunçado demais, o Leonardo (que conhece a
  fábrica) lista os ~15-20 insumos reais e cadastramos direto. Plano C.

---

## Pendências pra destravar 100%
- [ ] Confirmar quais categorias do SIGE contêm os insumos da produção.
- [ ] Exportar o arquivo e recebê-lo.
- [ ] Receitas: dependem do Eraldo responder o questionário `02_suprimentos.docx`.

---

*Atualizado 21/05/2026. Quando os insumos entrarem e as receitas forem cadastradas,
o módulo de Suprimentos passa a calcular sozinho o que falta comprar (MRP simplificado).*
