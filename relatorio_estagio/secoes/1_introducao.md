# 1 INTRODUÇÃO

---

Este relatório descreve as atividades que desenvolvi durante o Estágio
Supervisionado Obrigatório do curso de Engenharia de Produção da
Universidade Federal de Campina Grande (UFCG), na Unidade Acadêmica de
Engenharia de Produção (UAEP). O estágio foi realizado na empresa
**Pequenas Mordidas Alimentos Eireli** — conhecida comercialmente como
**Doces Vó Nena** —, indústria de alimentos do setor de confeitaria
semi-industrial localizada em São Paulo (SP), no período de **28 de abril
a 26 de junho de 2026**, totalizando **240 horas**. As atividades foram
acompanhadas, na empresa, pelo supervisor Eraldo, sócio-gerente
responsável pela Gestão da produção, e, na universidade, pelo orientador
Prof. Kegenaldo (UFCG-UAEP).

Cheguei à empresa para atuar no **Planejamento e Controle da Produção
(PCP)** do dia a dia e, a partir dessa vivência, ajudar a estruturar esse
processo. Propus-me, em conjunto com a Gestão, a substituir o controle
manual em folhas de papel — utilizado pela empresa até então para
registrar o que era produzido, cortado e embalado — por um sistema digital
que tornasse esses dados mais confiáveis, visíveis e úteis para a tomada
de decisão. Na prática, atuei nas duas frentes ao mesmo tempo: participei
da **rotina operacional do PCP** e, em paralelo, **desenvolvi o sistema**
que passou a apoiá-la.

Como apoio ao PCP, minha rotina partia do levantamento diário do estoque
de produto acabado, feito logo na primeira parte da manhã, e seguia para o
apoio à definição das ordens de produção, ao corte das bandejas e à
embalagem. Para isso, foi necessário conviver com o chão de fábrica e
entender as rotinas e restrições de cada departamento — **Gestão**,
**Produção**, **Corte**, **Embalagem** e **Suprimentos** —, conversando
com as pessoas responsáveis por cada etapa e registrando como o trabalho
realmente acontece, antes de tentar digitalizá-lo.

O setor de confeitaria semi-industrial combina receitas tradicionais com
escalas crescentes de comercialização, o que torna o planejamento da
produção um desafio particular: é preciso conciliar a natureza artesanal
do produto com a previsibilidade exigida pela operação diária. Em empresas
desse porte, esse planejamento costuma apoiar-se sobretudo na experiência
da gestão, com pouco suporte sistemático de dados (RODRIGUES; FERONI,
2020) — exatamente a lacuna que este estágio buscou endereçar. O sistema
que desenvolvi foi crescendo de forma incremental: começou apenas
digitalizando a folha de produção e, ao longo do estágio, evoluiu para um
PCP mais completo, integrado ao ERP da empresa — uma evolução cujo
detalhamento técnico é objeto do meu Trabalho de Conclusão de Curso, e que
neste relatório registro apenas como apoio à rotina operacional.

É importante registrar, com transparência, que **desenvolvi o sistema com
o apoio do Claude Code**, um assistente de programação baseado em
inteligência artificial. As decisões de modelagem, de regras de negócio e
de prioridade do projeto foram minhas e da Gestão; a ferramenta acelerou a
parte de programação e me permitiu cobrir, no tempo do estágio, um escopo
que dificilmente seria viável de outra forma. Ao final do período, o
sistema estava no ar, em uso, com banco de dados na nuvem e integração de
leitura com o ERP da empresa.

Ao longo do estágio, portanto, acompanhei o ciclo completo de produção e
atuei diretamente na rotina de Planejamento e Controle da Produção, ao
mesmo tempo em que construía o sistema digital que passou a sustentá-la.
Este relatório descreve essa experiência, da imersão inicial no chão de
fábrica aos resultados obtidos e às recomendações para a continuidade.

## 1.1 Objetivos do estágio

### 1.1.1 Objetivo geral

Aplicar os conhecimentos adquiridos no curso de Engenharia de Produção em
contexto industrial real, contribuindo para a estruturação do Planejamento
e Controle da Produção de uma confeitaria semi-industrial por meio do
desenvolvimento de um sistema digital de apoio à decisão.

### 1.1.2 Objetivos específicos

1. Vivenciar o cotidiano de uma indústria de alimentos de pequeno porte,
   compreendendo as rotinas, restrições e dinâmicas de cada departamento.
2. Mapear os processos produtivos atuais da empresa e identificar pontos
   passíveis de melhoria.
3. Modelar conceitualmente o domínio de dados de produção, preservando a
   estrutura conceitual da folha de produção em papel.
4. Desenvolver, em colaboração com a Gestão da empresa, um sistema digital
   capaz de substituir o controle em papel sem ruptura operacional.
5. Implementar funcionalidades incrementais de análise de dados, sugestão
   automática de corte e produção e apoio à decisão.
6. Integrar o sistema, em modo somente leitura, ao ERP da empresa,
   preservando-o como registro oficial.
7. Documentar os processos, as receitas, os produtos e as decisões da
   operação, organizando o conhecimento da fábrica que antes era tácito.

## 1.2 Justificativa pessoal e profissional

A escolha pela Doces Vó Nena como local de estágio foi motivada por três
fatores. Primeiro, a possibilidade de atuar em uma empresa em fase de
crescimento operacional, onde a sistematização de processos pode produzir
ganho mensurável em curto prazo. Segundo, a oportunidade de aplicar
conceitos clássicos de Engenharia de Produção — PCP, MRP, Curva ABC, lista
de materiais — em escala adaptada à realidade de uma micro/pequena
indústria, contexto historicamente pouco explorado na literatura acadêmica
nacional. Terceiro, o alinhamento estratégico com o Trabalho de Conclusão
de Curso, possibilitando que estágio e TCC se desenvolvessem em paralelo e
se retroalimentassem.

## 1.3 Estrutura do relatório

Este relatório está organizado em cinco seções, além desta introdução; ao
final, apresentam-se as referências e uma lista de perguntas ao orientador.

A **Seção 2** apresenta a empresa concedente do estágio, descrevendo seu
setor, porte, produtos, fluxos produtivos e estrutura organizacional.

A **Seção 3** descreve a rotina diária de PCP em que atuei — a contagem do
estoque (produto acabado e em processo), a lista dos produtos fabricados, e
a definição das ordens de produção, corte de bandejas, embalagem e alocação
da equipe — e, em paralelo, o desenvolvimento do sistema digital de apoio.

A **Seção 4** apresenta as contribuições operacionais do estágio à empresa.

A **Seção 5** traz as considerações finais, incluindo aprendizados técnicos
e profissionais, dificuldades enfrentadas e recomendações para futuros
estagiários no mesmo contexto.

Anexos contendo declarações da empresa, capturas de tela do sistema
desenvolvido e documentação complementar finalizam o relatório.

---
