# 1 INTRODUÇÃO

## 1.1 Contextualização

O Planejamento e Controle da Produção (PCP) é uma das funções centrais da
Engenharia de Produção, responsável por organizar quando produzir, quanto
produzir e com que recursos, garantindo o atendimento à demanda com o menor
custo possível (TUBINO, 2017; CORRÊA; CORRÊA, 2017). Em grandes indústrias,
sistemas integrados do tipo *Enterprise Resource Planning* (ERP) automatizam
essa função há décadas, integrando módulos de produção, suprimentos, vendas
e contabilidade em torno de uma base de dados única
(LAUDON; LAUDON, 2020).

Pequenas e médias indústrias (PMI), no entanto, frequentemente operam à
margem dessa automação. Por restrições de custo, complexidade ou ausência de
profissional dedicado à área, muitas pequenas fábricas mantêm o controle de
produção em registros manuscritos — folhas de papel, planilhas avulsas e a
memória dos gestores — o que dificulta a rastreabilidade, a análise histórica
e a tomada de decisão baseada em dados (SLACK; BRANDON-JONES; JOHNSTON, 2018).
Quando essas empresas finalmente adotam um ERP, é comum que o utilizem como
sistema de registro fiscal e contábil, sem que o módulo de produção converse
de fato com a operação do chão de fábrica — abrindo uma lacuna entre a
**verdade contábil** do sistema e a **verdade operacional** do dia a dia.

Esse cenário se aplica particularmente bem ao setor de alimentos artesanais
e semi-industriais brasileiro, no qual a produção combina receitas
tradicionais com escalas crescentes de comercialização. Nesses ambientes,
decisões críticas — quanto produzir de cada sabor, em que ordem cortar,
quando solicitar matéria-prima, quais produtos realmente dão lucro — são
tomadas com base na experiência acumulada dos gestores, e raramente sob apoio
sistemático de dados ou modelos de planejamento (MARTINS; LAUGENI, 2015).

## 1.2 Apresentação da empresa

A **Pequenas Mordidas Alimentos Eireli**, conhecida comercialmente como
**Doces Vó Nena**, é uma confeitaria industrial localizada em São Paulo (SP).
Produz cocadas, palhas italianas, pão de mel, balas de doce de leite e doces
finos, com distribuição em pontos de venda próprios (quiosques) e
fornecimento a clientes corporativos. A empresa utiliza o ERP **SIGE Cloud**
como sistema de registro do ciclo de materiais — entrada de notas fiscais,
estoque, ordens de produção e vendas.

A operação envolve cinco departamentos principais:

- **Gestão** — define ordens de produção, ajusta parâmetros, decide
  prioridades por sabor e por dia da semana.
- **Produção** — opera tachos e panelas de cocada e palha, vira massas e
  registra contagens matinais em folhas manuscritas.
- **Corte** — fatia bandejas em produtos finais (formatos 45g, Mini, Pet,
  potes de 260g e 605g).
- **Embalagem** — embala plástico individual e cintas de papel, em duas
  etapas distintas, com limite variável de capacidade diária.
- **Suprimentos** — controla matéria-prima, insumos auxiliares,
  embalagens e potes; faz compras junto a fornecedores.

A produção segue um fluxo de três estágios para a cocada — tacho, viração e
corte — com *lead time* total de aproximadamente três dias. A palha tem
fluxo mais simples (uma receita, uma panela, uma bandeja). O pão de mel e a
bala seguem rotinas próprias, com unidades de medida distintas (bolos e
tachos, respectivamente).

Antes do desenvolvimento descrito neste trabalho, todo o controle de
produção era feito em folhas de papel preenchidas manualmente a cada dia.
Cada folha continha quatro quadros principais — Embalados, Cortados,
Viradas e Pra Virar — mais o "Papelzinho do Joel", documento auxiliar de
contagem matinal feita pela Produção. Esses registros eram arquivados
fisicamente, sem agregação digital, o que inviabilizava análises de
tendência, comparações entre semanas e cálculos consolidados de produção.
Paralelamente, embora o ERP da empresa armazenasse vendas, custos de insumo
e estrutura de produtos, esses dados não eram explorados para apoiar as
decisões de produção: viviam no sistema fiscal, desconectados da folha de
chão de fábrica.

## 1.3 Problema

A operação descrita acima apresenta quatro limitações estruturais que
motivaram este trabalho:

**Primeiro, a falta de visibilidade histórica e em tempo real.** O sistema
em papel armazena os números do dia, mas não permite consultar facilmente
o que aconteceu há uma semana, um mês ou em períodos similares. Comparações
entre dias, sabores ou semanas exigiriam folhear dezenas de páginas, e
métricas agregadas (como total mensal por sabor) só seriam obtidas por
contagem manual demorada.

**Segundo, a ausência de cálculos automatizados de necessidade de
insumos.** Quando a Gestão define uma ordem de produção, a quantidade de
matéria-prima necessária — leite, açúcar, coco ralado, leite condensado,
embalagens — é estimada mentalmente ou por aproximação. Não há explosão
formal de necessidades pela lista de materiais (*Bill of Materials* — BOM),
o que aumenta o risco de faltas inesperadas e de compras superdimensionadas
(CHOPRA; MEINDL, 2016; ORLICKY, 1975).

**Terceiro, a dependência crítica do conhecimento tácito da Gestão.** As
decisões diárias — quantas bandejas cortar, em que sabor, com que prioridade
— concentram-se em uma única pessoa, com base em sua memória sobre pedidos
antecipados, sazonalidade e disponibilidade da equipe. Esse conhecimento
não está documentado nem sistematicamente capturado, tornando a operação
vulnerável a ausências do gestor e dificultando a transferência futura de
conhecimento (NONAKA; TAKEUCHI, 1997).

**Quarto, a desconexão entre o que se produz e o que efetivamente dá
lucro.** A empresa registra vendas e custos de insumo no ERP, mas não os
cruza com a produção para responder a perguntas estratégicas: qual produto
contribui mais para o resultado? Vender muito de um sabor significa lucrar
muito com ele? Qual é o custo real de produzir cada formato? Sem essa
leitura, o esforço de produção pode ser direcionado a itens de alto volume,
porém baixa contribuição — uma decisão invisível para quem só enxerga
quantidade, e não margem.

## 1.4 Justificativa

A digitalização do PCP e sua integração ao ERP em uma confeitaria industrial
de pequeno porte são justificadas por quatro frentes complementares.

**Operacional.** Substituir o papel por um sistema digital permite
preencher, consultar e exportar folhas em segundos, reduzindo o tempo de
operações administrativas e eliminando perdas físicas de registros.
Comparações entre dias, sabores e semanas tornam-se imediatas, e a
exportação para planilhas viabiliza análises adicionais externas.

**Estratégica.** A estruturação dos dados em base relacional, somada à
leitura dos dados já existentes no ERP, cria a base para a aplicação de
técnicas de Engenharia de Produção classicamente restritas a grandes
indústrias: Curva ABC de sabores, MRP simplificado para suprimentos, médias
móveis para calibração de metas (HOPP; SPEARMAN, 2008). Mais do que isso, ao trazer
para dentro do PCP o **custo de produção**, a **margem por canal**, as
**vendas reais** e a **contribuição por produto**, o sistema deixa de ser
apenas um registro do que se faz na fábrica e passa a apoiar a decisão de
**o que vale a pena fazer** — fechando a ponte, antes ausente, entre o chão
de fábrica e o resultado da empresa. Cada uma dessas técnicas, isoladamente,
agrega valor; em conjunto, transformam o controle do PCP de reativo para
proativo.

**Econômica e gerencial.** A análise de lucratividade desenvolvida revelou
distinções que não eram evidentes na operação cotidiana e que têm impacto
direto na gestão. A primeira é a chamada **armadilha da margem de
matéria-prima**: como o material é uma fração pequena do preço de venda, a
margem sobre matéria-prima é sempre alta (na faixa de 84% a 96%) — o que
**não** significa lucro, pois ignora o custo de conversão. A segunda é que
a **Curva ABC por contribuição difere da Curva ABC por volume e por
produção**: vender muito de um produto não equivale a lucrar muito com ele,
como evidenciado pelo caso da cocada Zero, que vende bem mas é a mais cara de
produzir (custo de material por quilo de R$ 25,79 contra R$ 5,60 da
Tradicional). Tornar essas distinções visíveis e quantificáveis é, por si
só, uma contribuição gerencial relevante para a empresa.

**Acadêmica.** A literatura nacional sobre PCP aplicado a micro e pequenas
indústrias é relativamente escassa quando comparada à literatura sobre
grandes manufaturas (RODRIGUES; FERONI, 2020; ANDRADE, 2007).
Documentar a implementação de um sistema de PCP em uma confeitaria
industrial — incluindo a integração *read-only* com o ERP, o método de
custeio por peso adaptado ao contexto artesanal-industrial e as distinções
analíticas de lucratividade — contribui com um caso de estudo replicável
para outras empresas do setor. O trabalho também aborda, com honestidade
científica, o **limite do ERP**: o sistema entrega o custo do insumo e a
estrutura do produto, mas não o custo de **conversão** (mão de obra, energia,
overhead) alocado à fábrica, que precisa ser levantado por fora — um achado,
não uma falha do projeto.

Por fim, a presença de um agente cognitivo baseado em Modelo de Linguagem de
Grande Porte (LLM) como camada complementar de apoio à decisão, descrita no
Capítulo 4, representa uma fronteira emergente da prática em PCP, ainda
pouco explorada na literatura acadêmica brasileira em Engenharia de
Produção (BROWN *et al.*, 2020). Cabe registrar, em transparência, que o
sistema descrito neste trabalho foi desenvolvido pelo autor com o apoio do
**Claude Code**, assistente de programação baseado em IA — recurso de
produtividade cuja adoção é, ela própria, parte do contexto contemporâneo de
desenvolvimento de software industrial.

## 1.5 Objetivos

### 1.5.1 Objetivo geral

Desenvolver e implementar um sistema digital de Planejamento e Controle da
Produção para a confeitaria industrial Doces Vó Nena, substituindo o
controle manual em papel, integrando-o de forma somente leitura ao ERP da
empresa (SIGE Cloud) e incorporando funcionalidades de visualização,
sugestão automática de produção, custeio, análise de margem e lucratividade,
além de apoio cognitivo à decisão.

### 1.5.2 Objetivos específicos

1. **Mapear** os processos produtivos atuais da empresa, identificando
   etapas, unidades de medida, prazos e gargalos.
2. **Modelar** o domínio de dados em base relacional, preservando a
   estrutura conceitual da folha de produção em papel.
3. **Implementar a digitalização** — formulário digital equivalente ao
   papel, com persistência em banco de dados relacional na nuvem.
4. **Implementar as funcionalidades de visualização e análise** — painel de
   acompanhamento, exportação de dados e análises descritivas: Curva ABC e
   média móvel de calibração de metas (MAKRIDAKIS; WHEELWRIGHT; HYNDMAN,
   1998).
5. **Implementar a sugestão automática** — algoritmos de sugestão de corte e
   produção para palha e cocada, calibrados contra decisões reais da Gestão.
6. **Implementar o módulo de Suprimentos** com MRP simplificado a partir da
   lista de materiais (BOM) e auto-baixa de insumos por produção.
7. **Integrar o sistema ao ERP SIGE Cloud** em modo somente leitura, usando
   a Ordem de Produção (OP) como ponte entre a verdade contábil do ERP e a
   verdade operacional do PCP, e implementar a reconciliação entre estoque
   teórico (sistema) e físico (contagem).
8. **Apurar o custo de produção** por meio do método de custeio por peso,
   cruzando a estrutura do produto com o custo de insumo trazido do ERP, e
   **analisar a margem** por canal de venda, evidenciando a armadilha da
   margem de matéria-prima.
9. **Construir o módulo de Vendas e Lucratividade** — Curva ABC de demanda
   real lida do ERP e análise de contribuição por produto, distinguindo o
   que se vende do que efetivamente contribui para o resultado.
10. **Avaliar a aderência** das sugestões automáticas às decisões reais da
    Gestão, identificando padrões e limites da modelagem determinística.
11. **Discutir** o papel de um agente conversacional baseado em LLM como
    camada de apoio cognitivo, capturando contexto não estruturado que
    complementa o modelo formal.

## 1.6 Estrutura do trabalho

Este Trabalho de Conclusão de Curso está organizado em seis capítulos.

**O Capítulo 2** apresenta a revisão de literatura, abordando os fundamentos
do PCP, os conceitos de MRP, BOM e Curva ABC, o princípio de estoque versus
fluxo (FORRESTER, 1961), os fundamentos de sistemas de informação e ERP
(LAUDON; LAUDON, 2020) e de custeio e margem de contribuição, além de uma
seção sobre aplicações recentes de aprendizado de máquina e LLMs em sistemas
industriais.

**O Capítulo 3** descreve a metodologia, incluindo o levantamento de
processos junto à empresa, a modelagem de dados, as escolhas tecnológicas
(arquitetura, banco de dados na nuvem, hospedagem, integração com o ERP) e o
método de validação adotado, caracterizando o trabalho como pesquisa
aplicada na forma de estudo de caso
(YIN, 2015;
GIL, 2017).

**O Capítulo 4** apresenta os resultados em blocos cumulativos. Os primeiros
tratam da digitalização da folha, das funcionalidades de visualização e
análise e dos algoritmos de sugestão automática de produção. Os blocos
seguintes — desenvolvidos a partir da integração com o ERP — apresentam a
reconciliação de estoque (teórico versus físico), a apuração do custo de
produção pelo método de custeio por peso, a análise de margem por canal, o
módulo de vendas (Curva ABC de demanda real) e a análise de lucratividade
por contribuição. Métricas quantitativas e qualitativas são apresentadas
para cada bloco.

**O Capítulo 5** discute criticamente os resultados, contrastando as
sugestões automáticas com as decisões reais da Gestão, distinguindo a Curva
ABC por lucro da Curva ABC por volume e por produção, examinando a armadilha
da margem de matéria-prima e o limite do ERP quanto ao custo de conversão, e
analisando o papel do agente conversacional como mediador entre modelo
formal e julgamento experiente.

**O Capítulo 6** conclui o trabalho, sumariza as contribuições, reconhece as
limitações e aponta trabalhos futuros — entre eles, o levantamento do custo
de conversão (a "terceira camada"), a evolução das sugestões automáticas
para escrita de Ordens de Produção no ERP e a aplicação dos princípios aqui
desenvolvidos em outras micro e pequenas indústrias do setor.

---
