# 2 REVISÃO DE LITERATURA

## 2.1 Planejamento e Controle da Produção: fundamentos

O Planejamento e Controle da Produção (PCP) é a função que articula *o que*
produzir, *quanto*, *quando* e *com quais recursos*, traduzindo as decisões
estratégicas da empresa em ordens executáveis no chão de fábrica (TUBINO, 2017).
A literatura clássica organiza essa função em três horizontes hierárquicos: o
**estratégico** (longo prazo, capacidade instalada), o **tático** (médio prazo,
plano agregado de produção) e o **operacional** (curto prazo, programação e
sequenciamento diário) — distinção desenvolvida por Slack, Brandon-Jones e Johnston
(2018) e por Corrêa e Corrêa (2017).

Entre as atribuições operacionais do PCP, três são centrais para este trabalho:
**programar** (definir as quantidades por período), **sequenciar** (ordenar a
execução respeitando restrições de capacidade) e **controlar** (comparar o
realizado com o planejado e realimentar o ciclo). Hopp e Spearman (2008), em
*Factory Physics*, formalizam a relação entre estoque, tempo de fluxo e
capacidade — base conceitual para o tratamento de estoque *versus* fluxo
discutido na seção 2.5.

No caso estudado, o PCP opera hoje em nível operacional e de forma manual (folhas
de papel preenchidas diariamente). O sistema desenvolvido digitaliza esse nível
e, progressivamente, adiciona apoio tático (sugestão de corte e produção,
calibração de parâmetros). Esta seção fundamenta o vocabulário que estrutura todo
o sistema.

## 2.2 Pequenas indústrias e a digitalização do PCP

As micro e pequenas indústrias (MPI) brasileiras caracterizam-se por estrutura
enxuta, decisão centralizada no proprietário e forte presença de **conhecimento
tácito** — saber operacional que reside nas pessoas e raramente está formalizado
em documentos ou sistemas (NONAKA; TAKEUCHI, 1997). Essa informalidade é
funcional enquanto a escala é pequena, mas torna-se gargalo quando a empresa
cresce: a decisão fica dependente de indivíduos e difícil de auditar ou escalar.

A adoção de sistemas ERP em pequena escala enfrenta barreiras conhecidas — custo
de licença, complexidade de implantação e baixa aderência ao processo real da
empresa (LAUDON; LAUDON, 2020). A literatura brasileira recente registra diversas
experiências de estruturação do PCP em pequenas empresas, inclusive do setor
alimentício: estudos de caso em empresas alimentícias de pequeno porte
(RODRIGUES; FERONI, 2020) e modelos estruturados de
melhoria de PCP para PMEs baseados em DMAIC (tese de doutorado, USP, 2019) mostram que
ganhos relevantes são possíveis **sem** adoção de ERP completo, por meio de
formalização de processos e ferramentas simples.

Particularmente relevante é o trabalho de implantação de PCP em uma **pequena
empresa produtora de doces** (BERALDO, L. *et al.*), pela proximidade de
contexto com o caso aqui estudado. A revisão desses trabalhos posiciona a
contribuição deste TCC: em vez de adaptar um ERP genérico, **constrói-se um
sistema sob medida** que espelha a folha de papel existente e evolui em camadas.

## 2.3 MRP e Lista de Materiais (BOM)

O *Material Requirements Planning* (MRP), formalizado por Orlicky (1975),
é a técnica que calcula as necessidades de materiais a partir de três entradas:
o **plano mestre de produção** (o que e quanto produzir), a **lista de materiais**
(BOM — *Bill of Materials*, que decompõe cada produto em seus componentes) e a
**posição de estoque** (o que já se tem). A "explosão" da BOM multiplica a
quantidade a produzir pelos coeficientes técnicos de cada insumo, gerando a
necessidade bruta; descontando o estoque disponível, obtém-se a necessidade
líquida — e, com ela, sugestões de compra e produção.

Conceitos correlatos consolidam o planejamento de materiais: **lote econômico**
(equilíbrio entre custo de pedido e de manutenção), **ponto de pedido** (nível de
estoque que dispara reposição considerando o *lead time*) e **estoque de
segurança** (proteção contra variabilidade de demanda e suprimento)
(CHOPRA; MEINDL, 2016). Em pequenas empresas, costuma-se aplicar um **MRP
simplificado**, sem a sofisticação dos sistemas comerciais — abordagem
documentada em estudos brasileiros, como o uso de MRP em panificadoras
(CONGRESSO DE ENGENHARIA DE PRODUÇÃO DA REGIÃO SUL, 2014).

Este trabalho aplica MRP simplificado de forma fiel ao chão de fábrica: a BOM é
cadastrada **por tacho/bandeja** (a unidade real de produção), e a explosão de
necessidades roda quando a folha do dia é salva, gerando a baixa automática de
insumos. A receita por tacho — e não por formato de venda — é uma decisão de
modelagem derivada da entrevista com a Gestão, detalhada no Capítulo 4.

## 2.4 Curva ABC e priorização por giro

A Curva ABC aplica o **princípio de Pareto** (a regra dos 80/20, derivada das
observações de Vilfredo Pareto sobre concentração) à gestão de estoques:
tipicamente, uma minoria de itens (classe A) responde pela maior parte do valor
ou do volume movimentado, enquanto a maioria (classe C) tem baixa relevância
individual (TUBINO, 2017; SLACK *et al.*, 2018). A classificação orienta o esforço
de controle — itens A merecem acompanhamento rigoroso; itens C, gestão simples.

A aplicação em indústrias de alimentos é amplamente documentada na literatura
brasileira: estudos de caso em indústrias e micro empresas do setor alimentício
relatam classificações que concentram poucos itens na classe A e a maioria na
classe C (repositório UFC; trabalhos publicados na ABEPRO/ENEGEP e no *Brazilian
Journal of Development*, 2021). Esses trabalhos confirmam a utilidade da
ferramenta para priorização, mas em geral a aplicam sobre **valor financeiro**
de itens em estoque.

A contribuição deste trabalho na seção de resultados é uma **correção conceitual**
nesse uso: classificar a produção por **fluxo** (bandejas cortadas, somáveis ao
longo do tempo) em vez de por **estoque** (quantidade embalada num instante, que
não pode ser somada entre dias) — distinção desenvolvida na seção 2.5. Essa
correção evita um erro estatístico comum em aplicações ingênuas da Curva ABC.

## 2.5 Estoque versus Fluxo (princípio de Forrester)

A distinção entre variáveis de **estoque** (*stock*) e de **fluxo** (*flow*) é
um princípio fundamental da dinâmica de sistemas, formalizado por Forrester
(1961) em *Industrial Dynamics*. Uma variável de estoque representa uma
**quantidade acumulada em um instante** (o nível de um reservatório); uma de
fluxo representa uma **taxa por período** (o que entra ou sai por unidade de
tempo). A confusão entre as duas leva a erros analíticos — em especial, **somar
snapshots de estoque ao longo do tempo**, operação que não tem significado físico.

Esse princípio teve consequência direta no desenvolvimento do sistema. Uma versão
inicial da Curva ABC somava a quantidade *embalada* (uma variável de estoque,
medida a cada dia) ao longo de várias folhas, produzindo um total sem sentido. A
correção foi passar a somar as **ordens de corte** (uma variável de fluxo, que
pode legitimamente ser acumulada por período). O mesmo cuidado foi aplicado à
detecção de anomalias e à média móvel. Trata-se de um caso concreto em que um
conceito teórico clássico corrigiu um erro de implementação — material rico para
a discussão do Capítulo 4.

## 2.6 Aprendizado de máquina aplicado a operações industriais

Técnicas de aprendizado de máquina vêm sendo incorporadas a operações
industriais no contexto da Indústria 4.0, sobretudo para **detecção de
anomalias** e **manutenção preditiva**, diante do volume crescente de dados de
processo. O algoritmo **Isolation Forest**, proposto por Liu, Ting e Zhou (2008),
é um método não supervisionado que isola observações atípicas com baixo custo
computacional — adequado a contextos onde rótulos de "anomalia" são caros ou
inexistentes. Aplicações industriais recentes relatam desempenho competitivo do
método em ambientes ruidosos e de alta dimensionalidade (ex.: detecção de
anomalias em aperto de parafusos industriais, MDPI *Computers*, 2022).

Para o ajuste contínuo de parâmetros de produção, **médias móveis** e métodos
clássicos de previsão (MAKRIDAKIS; WHEELWRIGHT; HYNDMAN, 1998) oferecem uma base simples e
interpretável: comparar o realizado recente com a meta-base permite sinalizar
desvios sistemáticos e recalibrar parâmetros sem sobre-ajuste.

O sistema deste trabalho aplica ambos: Isolation Forest para apontar dias
atípicos de produção (sinal para investigação, não veredito) e média móvel para
sugerir recalibração das metas por sabor e dia da semana. O princípio de
estoque/fluxo (2.5) é respeitado na engenharia de atributos — os modelos operam
sobre variáveis de fluxo, não sobre snapshots de estoque.

## 2.7 Modelos de Linguagem de Grande Porte (LLM) em ambientes industriais

Os Modelos de Linguagem de Grande Porte (LLM) ganharam capacidade de
generalização *few-shot* a partir do trabalho de Brown *et al.* (2020),
*Language Models are Few-Shot Learners*. Mais recentemente, a literatura discute
o uso de LLMs não apenas como geradores de texto, mas como **agentes** capazes de
chamar ferramentas, consultar dados e apoiar decisões — inclusive em manufatura
(revisões recentes em periódicos de engenharia, 2025, examinam centenas de
trabalhos sobre LLMs em manufatura inteligente e Indústria 5.0).

Dois aspectos práticos são relevantes para este trabalho. O **prompt caching**
reduz custo e latência ao reaproveitar o contexto fixo entre chamadas; o **tool
use** (uso de ferramentas) permite que o modelo consulte o estado real do sistema
em vez de "alucinar" números. Ambos foram empregados na camada cognitiva
implementada, viabilizando custo compatível com uma pequena empresa.

A posição defendida é que o LLM ocupa um papel **complementar**, não substituto:
ele capta o **contexto livre** (eventos da semana, intuição da Gestão, pedidos
antecipados) que a estrutura algorítmica não modela — exatamente o "gap" entre o
que o MRP clássico resolve e o que a decisão experiente faz. Trabalhos em
português sobre LLM em indústria ainda são escassos, o que reforça o caráter
exploratório desta contribuição.

## 2.8 Síntese

A revisão mostra que cada camada do sistema desenvolvido se apoia em um corpo
teórico consolidado:

| Bloco teórico | Seção | Sustenta no sistema |
|---|---|---|
| Fundamentos de PCP | 2.1 | Vocabulário e hierarquia de decisão |
| PCP em pequenas indústrias | 2.2 | Justificativa do sistema sob medida (vs. ERP) |
| MRP e BOM | 2.3 | Suprimentos: baixa automática de insumos |
| Curva ABC | 2.4 | Priorização por giro de produção |
| Estoque vs. fluxo | 2.5 | Correção conceitual transversal (ABC, ML) |
| Aprendizado de máquina | 2.6 | Anomalias e calibração de metas |
| LLM e agentes | 2.7 | Camada cognitiva complementar |

O fio condutor é a **progressão em camadas**: da digitalização fiel do papel
(Camada 0), passando pela análise (Camada 1) e pela sugestão semi-automática
(Camada 2), até a camada cognitiva (Camada 3). A literatura clássica de PCP, MRP
e Curva ABC sustenta as camadas estruturadas; a literatura de ML e LLM sustenta as
camadas adaptativa e cognitiva; e o princípio de Forrester atravessa todas,
garantindo rigor estatístico. Essa articulação fundamenta a metodologia
(Capítulo 3) e a leitura dos resultados (Capítulo 4).
