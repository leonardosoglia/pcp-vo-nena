# 1 INTRODUÇÃO

---

Este relatório descreve as atividades desenvolvidas durante o Estágio
Supervisionado Obrigatório do curso de Engenharia de Produção da
Universidade Federal de Campina Grande, realizado na empresa Pequenas
Mordidas Alimentos Eireli — conhecida comercialmente como **Doces Vó
Nena** —, indústria de alimentos localizada em São Paulo (SP).

O estágio teve como foco a atuação no Planejamento e Controle da Produção
(PCP) diário da empresa e a estruturação desse processo. Na prática, atuei na
rotina operacional do PCP — o levantamento diário do estoque de produto
acabado e o apoio à definição das ordens de produção, corte de bandejas e
embalagem — e, em paralelo, desenvolvi um sistema digital que substituísse o
controle manual em folhas de papel utilizado pela empresa até então. Para
isso, foi necessário compreender as rotinas e as restrições dos departamentos
de Gestão, Produção, Corte, Embalagem e Suprimentos.

O setor de confeitaria semi-industrial combina receitas tradicionais com escalas crescentes de comercialização, o que torna o planejamento da produção um desafio particular: é preciso conciliar a natureza artesanal do produto com a previsibilidade exigida pela operação diária. Em empresas desse porte, esse planejamento costuma apoiar-se sobretudo na experiência da gestão, com pouco suporte sistemático de dados — exatamente a lacuna que este estágio buscou endereçar.

Ao longo do período do estágio, acompanhei o ciclo completo de produção e atuei diretamente na rotina de Planejamento e Controle da Produção, ao mesmo tempo em que desenvolvia, de forma incremental, o sistema digital que passou a sustentá-la. Este relatório descreve essa experiência, da imersão inicial no chão de fábrica aos resultados obtidos e às recomendações para a continuidade.

## 1.1 Objetivos do estágio

### 1.1.1 Objetivo geral

Aplicar os conhecimentos adquiridos no curso de Engenharia de Produção em
contexto industrial real, contribuindo com o desenvolvimento de um sistema
de PCP digital para uma confeitaria semi-industrial.

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
   automática e apoio à decisão.
6. Documentar processos, decisões arquiteturais e resultados, gerando
   subsídios para o Trabalho de Conclusão de Curso.

## 1.2 Justificativa pessoal e profissional

A escolha pela Doces Vó Nena como local de estágio foi motivada por três
fatores. Primeiro, a possibilidade de atuar em uma empresa em fase de
crescimento operacional, onde a sistematização de processos pode produzir
ganho mensurável em curto prazo. Segundo, a oportunidade de aplicar
conceitos clássicos de Engenharia de Produção — PCP, MRP, Curva ABC, BOM —
em escala adaptada à realidade de uma micro/pequena indústria, contexto
historicamente sub-explorado na literatura acadêmica nacional. Terceiro, o
alinhamento estratégico com o Trabalho de Conclusão de Curso, possibilitando
que estágio e TCC se desenvolvessem em paralelo e se retroalimentassem.

## 1.3 Estrutura do relatório

Este relatório está organizado em cinco seções, além desta introdução; ao final, apresentam-se as referências e uma lista de perguntas ao orientador.

A **Seção 2** apresenta a empresa concedente do estágio, descrevendo seu
setor, porte, produtos, fluxos produtivos e estrutura organizacional.

A **Seção 3** descreve a rotina diária de PCP em que atuei — o levantamento do
estoque de produto acabado, a consolidação da folha de produção do dia e o
apoio à definição das ordens de produção, corte de bandejas e embalagem.

A **Seção 4** apresenta os resultados obtidos e as contribuições do estágio
à empresa, incluindo métricas quantitativas (quando disponíveis) e
testemunhos qualitativos.

A **Seção 5** traz as considerações finais, incluindo aprendizados técnicos
e profissionais, dificuldades enfrentadas e recomendações para futuros
estagiários no mesmo contexto.

Anexos contendo declarações da empresa, capturas de tela do sistema
desenvolvido e documentação complementar finalizam o relatório.

---
