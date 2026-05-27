# 4 RESULTADOS E CONTRIBUIÇÕES

> Estrutura esboçada. Detalhar na semana 10–16/06 quando tivermos métricas
> mais consolidadas (mais semanas de uso real do sistema).

---

## 4.1 Sistema desenvolvido

`<<APRESENTAÇÃO RESUMIDA — pode reaproveitar do TCC capítulo 4, mas mais enxuto>>`

- 11 páginas funcionais no aplicativo Streamlit
- Banco de dados Postgres (Supabase, us-east-1)
- Hospedagem em Hugging Face Spaces
- Repositório versionado no GitHub
- BOM cadastrada (33 insumos + 91 linhas de receita)

## 4.2 Indicadores quantitativos

### 4.2.1 Tempo operacional
| Tarefa | Antes (papel) | Depois (sistema) |
|---|---|---|
| Lançamento da folha do dia | `<<X>>` min | `<<Y>>` min |
| Consulta de folha histórica | `<<X>>` min (folhear arquivo) | `<<Y>>` s (busca por data) |
| Geração de relatório mensal | `<<X>>` horas | `<<Y>>` min (automático) |

`<<MEDIR essas métricas com a Gestão antes de fechar o relatório>>`

### 4.2.2 Cobertura funcional
- `<<N>>` folhas registradas no sistema durante o estágio
- `<<N>>` sabores cadastrados (cocada × 6, palha × 5, PM, bala)
- `<<N>>` insumos cadastrados
- `<<N>>` linhas de Bill of Materials cadastradas

### 4.2.3 Acertividade das sugestões automáticas
- **Palha:** aderência de aproximadamente `<<%>>` contra decisões reais da Gestão
- **Cocada:** aderência de aproximadamente `<<%>>` (limites conhecidos)

## 4.3 Contribuições qualitativas

### 4.3.1 Para a empresa
- Substituição do controle manual por sistema digital com baixa fricção
- Visibilidade histórica e em tempo real do estado da produção
- Insights automáticos que antes exigiriam análise manual demorada
- Base de dados estruturada que viabiliza futuras extensões

### 4.3.2 Para a Gestão
- Redução do tempo dedicado a tarefas administrativas
- Suporte à decisão diária através de sugestões automáticas
- Apoio cognitivo via Assistente IA (em produção após configuração da API)

### 4.3.3 Para a equipe
- Comunicação mais clara das ordens diárias
- Possibilidade de consulta a qualquer hora pelo celular
- Histórico permanente das atividades

## 4.4 Aprendizados de Engenharia de Produção aplicada

Durante o estágio, conceitos estudados ao longo do curso foram aplicados
em contexto real, com adaptações ao porte da empresa:

- **Planejamento Mestre da Produção** — mapeado nas ordens diárias
- **MRP simplificado** — implementado via BOM cadastrada
- **Curva ABC** — aplicada aos sabores produzidos
- **Estoque vs Fluxo** (Forrester) — princípio aplicado em todas as métricas
- **Lead time** — modelado para cocada (3 dias) e palha (3 dias)
- **Order-up-to / base-stock** — usado na sugestão de produção da palha
- **Tachos parciais** — modelados como decisão intencional (sobra → pote)

## 4.5 Contribuição acadêmica

O sistema desenvolvido durante o estágio serve como objeto de estudo para
o Trabalho de Conclusão de Curso, sendo o mesmo orientador responsável
por ambos os trabalhos. As descobertas operacionais — em especial a
documentação do fenômeno da "não-acomodação" e a aplicação de um agente
conversacional baseado em LLM como camada de apoio cognitivo — são parte
da contribuição original do trabalho de TCC.

---

## Notas pra completar

- Medir métricas quantitativas COM A GESTÃO antes da entrega
- Pedir um depoimento curto da Gestão sobre o impacto percebido (carta?)
- Capturar prints comparativos: folha em papel × tela do sistema
