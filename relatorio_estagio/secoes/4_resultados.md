# 4 RESULTADOS E CONTRIBUIÇÕES

## 4.1 Sistema desenvolvido

O principal resultado do estágio é um sistema digital de Planejamento e Controle da Produção, em uso diário pela empresa. Em síntese, o sistema reúne:

- um aplicativo *web* com páginas para o lançamento da folha diária, painel de acompanhamento, sugestões automáticas de produção e análises;
- um banco de dados relacional que substitui o arquivo físico de folhas de papel, preservando todo o histórico;
- hospedagem em nuvem, com acesso pelo computador e pelo celular;
- a lista de materiais (receitas) cadastrada, base para o cálculo de necessidade de insumos.

[[IMG: Captura de tela do Painel do sistema, exibindo a folha de produção do dia]]

## 4.2 Indicadores

### 4.2.1 Cobertura funcional

Ao longo do período, o sistema passou a concentrar a operação de PCP da empresa. Os números de cobertura, no momento da redação deste relatório, são:

- 27 folhas de produção registradas no sistema;
- 6 sabores de cocada e 5 de palha, além de pão de mel e bala de doce de leite;
- 33 insumos cadastrados;
- 91 linhas de lista de materiais (receitas por produto).

### 4.2.2 Aderência das sugestões automáticas

As sugestões automáticas de corte e produção foram comparadas às decisões reais da Gestão ao longo do estágio:

- **Palha:** aderência de aproximadamente **85%** — o modelo semanal reproduz bem a decisão da Gestão;
- **Cocada:** aderência aproximada de **50% a 70%**, com limites conhecidos e documentados — a decisão da cocada envolve um componente cognitivo que o modelo determinístico não captura totalmente.

### 4.2.3 Tempo operacional

A digitalização eliminou o folhear de páginas arquivadas: consultas a folhas anteriores, que antes exigiam busca manual no arquivo físico, passaram a ser imediatas. Os cálculos derivados (cortados, viradas, pra virar), antes feitos manualmente, passaram a ser automáticos. A quantificação precisa do tempo economizado está em consolidação junto à Gestão.

## 4.3 Contribuições qualitativas

**Para a empresa.** Substituição do controle manual por um sistema digital de baixa fricção; visibilidade histórica e em tempo real do estado da produção; base de dados estruturada que viabiliza análises e futuras extensões.

**Para a Gestão.** Apoio à decisão diária por meio de sugestões automáticas e redução do tempo dedicado a tarefas administrativas.

**Para a equipe.** Comunicação mais clara das ordens do dia e possibilidade de consulta a qualquer hora pelo celular.

## 4.4 Aprendizados de Engenharia de Produção aplicados

Ao longo do estágio, conceitos estudados no curso foram aplicados em contexto real, adaptados ao porte da empresa: Planejamento e Controle da Produção, MRP simplificado a partir da lista de materiais, Curva ABC dos sabores, *lead time*, política de estoque-alvo (reposição) e o princípio de estoque *versus* fluxo na construção das análises. As ordens não-múltiplas da capacidade do tacho, que geram sobra de massa, foram modeladas como decisão intencional de aproveitamento (a sobra vira potes), e não como desperdício.

## 4.5 Contribuição acadêmica

O sistema desenvolvido durante o estágio é também objeto de estudo do Trabalho de Conclusão de Curso, sob a mesma orientação. As descobertas operacionais — em especial a documentação do fenômeno da não-acomodação (a Gestão solicita produção mesmo com a meta do dia atingida, para não ociosar a equipe) e a aplicação de uma camada de apoio à decisão baseada nos dados reais da fábrica — compõem a contribuição original do trabalho.
