# 3 METODOLOGIA

Este capítulo descreve o percurso metodológico adotado para conceber, desenvolver e validar o sistema digital de Planejamento e Controle da Produção (PCP) implantado na confeitaria Doces Vó Nena. O objetivo é tornar o trabalho replicável e auditável, deixando explícitas as decisões de pesquisa, as fontes de dados, as escolhas tecnológicas e os critérios de validação. Por se tratar de uma intervenção conduzida dentro de uma empresa real, durante o período de estágio supervisionado, a metodologia combina o rigor do método científico com a pragmática do desenvolvimento de software aplicado ao chão de fábrica.

O percurso metodológico organizou-se em sete fases sucessivas — do levantamento do processo às conclusões —, sintetizadas na Figura 2 e detalhadas nas seções seguintes.

**Figura 2 — Fluxograma metodológico da pesquisa**

[[IMG: COLAR AQUI a Figura 2 — Fluxograma metodológico da pesquisa (imagem gerada pelo autor)]]

Fonte: elaborado pelo autor (2026).

## 3.1 Classificação da pesquisa

Quanto à natureza, esta é uma pesquisa aplicada: não se buscou gerar conhecimento de uso geral, e sim resolver um problema concreto de gestão da produção em uma confeitaria semi-industrial específica, produzindo um artefato (o sistema de PCP) que pudesse ser efetivamente utilizado pela empresa.

Quanto aos objetivos, a pesquisa é descritiva-exploratória. É descritiva ao caracterizar o processo produtivo, os fluxos de informação e a estrutura de custos da fábrica; é exploratória ao investigar como conceitos clássicos de PCP, MRP e custeio podem ser instrumentalizados em um contexto de pequeno porte que, até então, operava integralmente em papel.

Quanto à abordagem, o estudo é quali-quantitativo. A dimensão qualitativa aparece no levantamento de processos por meio de entrevistas, na observação participante durante o estágio e na codificação do conhecimento tácito da Gestão e da Produção (NONAKA; TAKEUCHI, 1997). A dimensão quantitativa surge na modelagem dos dados de produção, no cálculo de custo e margem, na análise da curva ABC e na mensuração da aderência das sugestões automáticas às decisões reais.

Quanto aos procedimentos técnicos, adotou-se o estudo de caso único (YIN, 2015; GIL, 2017). O estudo de caso é adequado quando se investiga um fenômeno contemporâneo em profundidade, dentro de seu contexto real, sobre o qual o pesquisador tem pouco controle e cujas fronteiras com o contexto não são nitidamente definidas — exatamente a situação de implantar um sistema de PCP em uma fábrica em operação e em crescimento. O caráter de caso único se justifica pela natureza reveladora e longitudinal da intervenção: acompanhou-se a fábrica do papel ao sistema digital integrado ao ERP, ao longo de todo o período de estágio, o que permite descrever a transformação com riqueza de detalhe que um levantamento amostral amplo não alcançaria.

O universo da pesquisa é a operação de Planejamento e Controle da Produção da confeitaria Doces Vó Nena ao longo do período de estágio supervisionado (28 de abril a 26 de junho de 2026), e a unidade de análise é a própria confeitaria, tomada como caso único. Por se tratar de uma intervenção real e contínua, não se adotou amostragem probabilística, e sim uma amostra intencional dos registros mantidos no sistema: cerca de 40 folhas de produção completas (44 folhas registradas no total, a maior parte no período do estágio), os dias de corte do estágio utilizados como referência na validação, 38 fichas de produtos preenchidas a partir de fotos e o catálogo de aproximadamente 1.988 itens lido do ERP. A amostra cobre os produtos e as decisões mais relevantes da fábrica no período, embora limitada em extensão temporal — limitação retomada na seção 3.9.

As variáveis observadas organizam-se em quatro grupos. As operacionais descrevem o dia produtivo: produção e ordens de corte, de embalagem e de produção por sabor e formato (45 g, Mini, Pet, potes), estoques de produto acabado, semiacabado e insumos, e os parâmetros de meta do dia. As econômicas abrangem o custo de insumo importado do ERP, o custo de material por quilo e por produto, o preço de venda por canal, a margem de material e a contribuição. As de demanda correspondem às vendas reais por produto e por canal. As derivadas, calculadas pelo sistema, compreendem os cortados e as viradas, a necessidade de insumos (MRP), a classe na curva ABC, o escore de anomalia, o desvio em relação à média móvel e a aderência das sugestões automáticas à decisão real da Gestão. Complementarmente, registram-se variáveis qualitativas — as regras de decisão tácitas da Gestão e os eventos da semana —, que dão contexto às quantitativas.

O Quadro 2 consolida o delineamento metodológico, reunindo em um só lugar os elementos detalhados ao longo deste capítulo.

**Quadro 2 — Delineamento metodológico da pesquisa**

| Elemento | Definição no estudo |
|---|---|
| Natureza | Pesquisa aplicada |
| Objetivos | Descritiva-exploratória |
| Abordagem | Quali-quantitativa |
| Procedimento técnico | Estudo de caso único |
| Unidade de análise | Confeitaria Doces Vó Nena |
| Universo | Operação de PCP da fábrica no período do estágio (28/04 a 26/06/2026) |
| Amostra | 44 folhas registradas (40 completas); dias de corte do estágio como referência; 38 fichas de produto; catálogo de ~1.988 itens do ERP |
| Instrumentos | Observação participante; entrevistas semiestruturadas; questionários estruturados; análise documental; leitura de fotos; o próprio sistema como registro |
| Variáveis | Operacionais, econômicas, de demanda, derivadas e qualitativas (detalhadas no texto) |
| Análise dos dados | Qualitativa (codificação do conhecimento tácito) e quantitativa (custo, margem, contribuição, curva ABC, média móvel, aderência), com triangulação |

Fonte: elaborado pelo autor (2026).

## 3.2 Levantamento dos processos

A primeira etapa consistiu em compreender, em detalhe, como a fábrica planeja e controla a produção. Esse levantamento se apoiou em quatro fontes complementares.

A principal foi a imersão no chão de fábrica durante o estágio. A rotina do pesquisador como PCP — contar pela manhã o estoque de produto acabado, apoiar a definição das ordens de produção, de corte e de embalagem, e alimentar o sistema com os dados do dia — deu-lhe acesso de observador participante ao fluxo real, e não a uma versão idealizada dele. Foi essa convivência que revelou nuances que nenhum documento explicitava, como o fato de que a contagem de cortados das 9h já incorpora o que o Corte produziu desde as 7h, ou de que parte dos tachos é desviada para potes quando a ordem não fecha um número inteiro de bandejas.

A segunda fonte foi a análise dos documentos físicos que estruturavam o PCP em papel — a folha de produção e o chamado "papelzinho" diário. Esses documentos foram tratados como artefatos primários: cada coluna, sigla e unidade foi mapeada e questionada quanto ao seu significado operacional, pois seriam a base do modelo de dados.

A terceira fonte foram as entrevistas semiestruturadas com a Gestão e a Produção, conduzidas ao longo do estágio à medida que surgiam dúvidas. Esse formato permitiu seguir um roteiro mínimo de tópicos sem engessar a conversa, deixando espaço para que os entrevistados explicitassem regras de decisão que normalmente permanecem tácitas — frequência de produção do pão de mel, dias de corte da palha, capacidade típica em tachos por dia, critérios para encomendas de cliente.

A quarta fonte foram os questionários estruturados aplicados à Gestão e à Produção, registrados em `entrevistas/01_pcp_inicial.docx` e `entrevistas/02_suprimentos.docx`, que consolidaram parâmetros quantitativos (receitas por tacho, rendimentos, lead times, estoques-alvo). Como complemento, 38 fichas de produtos foram preenchidas a partir da leitura de fotos dos produtos e cruzadas com os registros do sistema, num procedimento de triangulação que confronta o dado declarado com a realidade física da fábrica.

O produto desse levantamento é o mapa do fluxo produtivo da fábrica, sintetizado na Figura 3, que percorre as cinco linhas de produção — cocada, pote, palha, pão de mel e bala — dos suprimentos ao estoque e à venda, com os respectivos tempos de processo.

**Figura 3 — Fluxo do processo produtivo da Doces Vó Nena**

[[IMG: COLAR AQUI a Figura 3 — Fluxo do processo produtivo (imagem gerada pelo autor)]]

Fonte: elaborado pelo autor (2026).

## 3.3 Modelagem de dados

O levantamento de processos foi traduzido em um modelo de dados relacional que serve de espinha dorsal do sistema. A diretriz central dessa etapa foi a fidelidade ao papel antes da automação: o sistema deveria, primeiro, fazer exatamente o que a folha de papel já fazia, na mesma unidade e com a mesma semântica, para só então acrescentar inteligência. Essa decisão reduz a resistência da equipe à mudança e garante que o modelo reflita o processo real, e não uma idealização do projetista.

O mapeamento conceitual converteu cada documento físico em entidades relacionais. A folha de produção deu origem às tabelas de folha por sabor; o papelzinho diário, à tabela de registros da Produção; o estoque de produto acabado e os derivados de corte e embalagem, às respectivas estruturas. Adotou-se a chave natural `(data, sabor)` para as folhas, tratando cada registro como um snapshot independente e não acumulativo — uma decisão que preserva a rastreabilidade histórica e evita os erros de agregação típicos de quem confunde estoque com fluxo, ponto retomado na validação dos algoritmos.

A modelagem evoluiu de forma incremental, do Schema v1 ao v2, à medida que novas regras de negócio eram descobertas e que o escopo crescia da digitalização da folha para os módulos de Suprimentos, custo, margem e vendas. Cada migração foi tratada de modo idempotente e versionado, preservando os dados já coletados.

Um cuidado específico de modelagem merece destaque por ter sido fonte recorrente de risco: a divergência entre a linguagem da produção e a linguagem do ERP. Um mesmo produto pode aparecer com nomes distintos no chão de fábrica e no SIGE — por exemplo, o que a Produção chama de "PET" corresponde, no cadastro do SIGE, a "Cocada Cubos 160g". Sem um mapeamento explícito (de-para) entre os dois vocabulários, qualquer cálculo de custo, margem ou consumo de insumo herdaria essa ambiguidade. Construir e manter esse de-para foi parte essencial da modelagem.

## 3.4 Arquitetura técnica e escolhas tecnológicas

As decisões tecnológicas foram orientadas por três restrições do contexto: a fábrica é de pequeno porte e sem orçamento para licenças; o sistema precisaria ser desenvolvido e mantido por uma única pessoa; e teria de rodar de forma confiável tanto em desenvolvimento local quanto em produção na nuvem.

A arquitetura resultante dessas restrições é apresentada na Figura 4, que organiza as camadas do sistema — usuários, interface, lógica de negócio e banco de dados — e a integração somente leitura com o ERP.

**Figura 4 — Arquitetura técnica do sistema**

[[IMG: COLAR AQUI a Figura 4 — Arquitetura do sistema (imagem gerada pelo autor)]]

Fonte: elaborado pelo autor (2026).

### 3.4.1 Stack de desenvolvimento

A linguagem escolhida foi Python, pela maturidade de seu ecossistema de dados e pela velocidade de prototipagem. A camada de dados usa pandas para manipulação tabular; a inteligência analítica usa scikit-learn (curva ABC, detecção de anomalias); e a visualização usa Plotly. A interface foi construída em Streamlit, um framework que permite transformar scripts Python em aplicações web multipágina sem exigir um time de front-end — decisão coerente com a restrição de desenvolvedor único, ainda que ao custo de menor flexibilidade de layout do que frameworks web tradicionais.

### 3.4.2 Persistência dual-backend (SQLite/Postgres)

A persistência foi projetada como dual-backend: em desenvolvimento local, o sistema usa um banco SQLite em arquivo, sem dependências externas; em produção, usa PostgreSQL hospedado no provedor de nuvem. A seleção do backend é automática e determinada por variável de ambiente — sem ela, cai-se em SQLite (fallback de desenvolvimento); com a URL de conexão, ativa-se o Postgres. Essa arquitetura, justificada em detalhe no capítulo de resultados, permite desenvolver e testar offline sem custo, mantendo paridade de schema com o ambiente produtivo. Toda a lógica de dados foi mantida em um módulo puro, sem dependência da camada de interface, o que viabiliza que scripts utilitários (migração, testes, cargas em lote) reutilizem a mesma base de código sem carregar o Streamlit.

### 3.4.3 Hospedagem e banco em nuvem

A aplicação está hospedada em Hugging Face Spaces, empacotada via Docker, e o banco Postgres roda na nuvem com conexão por pooler de transações. Tanto a aplicação quanto o banco foram posicionados na mesma região (us-east-1) para minimizar a latência de rede entre as duas camadas — um ajuste que reduziu de forma expressiva o tempo de resposta percebido. A opção por serviços de camada gratuita (free tier) atende à restrição orçamentária da fábrica sem comprometer a disponibilidade necessária ao uso diário.

### 3.4.4 Apoio de ferramenta de IA no desenvolvimento

Em transparência metodológica, registra-se que o sistema foi desenvolvido com o apoio do Claude Code, um assistente de programação baseado em modelos de linguagem (LLM). A ferramenta foi utilizada como apoio à codificação, à revisão e à documentação — na escrita de funções, na investigação de erros e na exploração da API do ERP —, sempre sob autoria, decisão e validação do autor. Todas as regras de negócio, escolhas arquiteturais e interpretações do processo produtivo foram definidas pelo autor a partir do levantamento na fábrica; a ferramenta acelerou a implementação, mas não substituiu o entendimento do domínio nem a validação com a Gestão. Esse uso é coerente com a literatura recente sobre o potencial dos LLMs em tarefas assistidas (BROWN *et al.*, 2020) e está aqui declarado para preservar a integridade científica do trabalho.

## 3.5 Camadas funcionais — visão geral

O sistema foi concebido em camadas funcionais sucessivas, cada uma agregando capacidade sobre a anterior. Essa organização não é apenas didática: reflete a estratégia de implantação adotada, em que cada camada só foi construída depois de a anterior estar validada e em uso, reduzindo risco e mantendo o sistema sempre útil à fábrica.

A Camada 0 é a digitalização do papel — o formulário diário de Lançamento e o Painel, que reproduzem fielmente a folha de produção e o papelzinho, persistindo os dados como snapshots independentes. A Camada 1 acrescenta visualização e análise sobre esses dados: a curva ABC da produção (PARETO/JURAN, ver capítulo 2) e a média móvel de calibração de metas (MAKRIDAKIS; WHEELWRIGHT; HYNDMAN, 1998). A Camada 2 é a sugestão automática de corte e produção, baseada nas regras de planejamento da palha e da cocada levantadas com a Gestão. A Camada 3, em caráter de proposta, prevê um agente cognitivo apoiado em LLM para diagnóstico e recomendação.

Sobre essas camadas operacionais foram ainda construídos os módulos de Suprimentos — insumos, lista de materiais (BOM), MRP simplificado (ORLICKY, 1975) e auto-baixa de consumo por produção — e a integração com o ERP, descritos nas seções seguintes por exigirem decisões metodológicas próprias.

## 3.6 Integração com o ERP (SIGE) em modo somente-leitura

A confeitaria utiliza o ERP SIGE Cloud para registrar o ciclo de materiais: a nota fiscal eletrônica (NF-e/XML) dá entrada no estoque; a Ordem de Produção (OP) explode a ficha técnica e gera a pré-reserva de insumos; a baixa ocorre por lote; e a OP é finalizada com o rendimento real. A integração entre o PCP e o ERP foi definida em conjunto com a Gestão a partir de uma decisão metodológica central: o PCP opera em modo somente-leitura (read-only) sobre o SIGE. O sistema lê do ERP, mas não escreve nele.

Essa fronteira foi modelada segundo a noção de contextos delimitados (*bounded contexts*) do *Domain-Driven Design* (EVANS, 2009): o SIGE é a fonte da verdade contábil (saldos, custos de insumo, cadastros fiscais), enquanto o PCP é a fonte da verdade operacional (a folha diária, os derivados de corte e embalagem, as sugestões de produção). A OP é a ponte entre os dois contextos. Crucialmente, a decisão de o quê e quanto produzir permanece humana — é tomada pela Gestão com base em estoque, semiacabado e demanda —, e nenhum sistema a substitui. O PCP apoia e instrumentaliza essa decisão; não a automatiza.

Como decorrência dessa separação, o sistema realiza a reconciliação de estoque entre o saldo teórico (registrado no SIGE) e o saldo físico (obtido na contagem diária). Quando há divergência, ela é tratada como ajuste de inventário, e não silenciada. Essa reconciliação aplica a distinção entre estoque e fluxo de Forrester (1961) em três camadas — prateleira, semiacabado e produção —, reconhecendo que o saldo correto de um produto depende de em qual camada do processo ele está sendo medido. Um achado relevante de modelagem foi que o saldo confiável muitas vezes vive no cadastro "operacional" do ERP, e não no cadastro idealizado, o que exigiu critério para escolher de qual registro extrair a quantidade.

## 3.7 Método de custeio por peso

Para custear os produtos, partiu-se da estrutura clássica: o custo de material de cada produto é o somatório dos insumos da sua lista de materiais (BOM) multiplicados pelo custo unitário de insumo trazido do SIGE. O obstáculo prático é que a fábrica produz dezenas de formatos (cubos, tabletes, potes, pet, mini) e nem todos têm ficha técnica detalhada cadastrada, o que deixaria a maior parte das vendas sem custo associado.

A solução metodológica foi o custeio por peso. A observação-chave é que o custo de material de uma cocada é essencialmente função do sabor (que determina os ingredientes) e do peso do produto, e não do formato. Como a gramatura costuma estar declarada no próprio nome do produto no SIGE (por exemplo, "Cocada Cubos 160g"), foi possível derivar um custo de material por quilo de cada sabor e, a partir dele, custear qualquer formato apenas multiplicando o custo/kg do sabor pela gramatura indicada no nome. Esse método elevou a cobertura de custeio de cerca de 17% para 64% das vendas, permitindo análise de margem e contribuição em escala antes inviável. As bases conceituais de custeio adotadas seguem a literatura de custos industriais (MARTINS, E., 2018; BORNIA, 2010).

É preciso registrar, com honestidade científica, o limite do método e do próprio ERP: o SIGE fornece o custo do insumo e a receita, mas não fornece o custo de conversão — mão de obra, energia e overhead alocados à fábrica. Esse custo precisa ser levantado por fora, constituindo a "terceira camada" do custeio, ainda não disponível na empresa. Não se trata de uma falha do projeto, e sim de um achado sobre o limite do sistema de informação existente: o custo de material por si só não é lucro, e tomá-lo como tal levaria à armadilha da margem de matéria-prima, em que a margem de material aparece sempre alta (na faixa de 84% a 96%) simplesmente porque o insumo é uma fração pequena do preço de venda. A análise de margem do trabalho, portanto, é apresentada como margem de material e não como lucro líquido, com essa ressalva sempre explícita.

## 3.8 Validação dos algoritmos e dos cálculos

A validação seguiu o princípio de confrontar o que o sistema produz com a realidade da fábrica, em duas frentes.

A primeira frente é a validação das sugestões automáticas da Camada 2. O método consistiu em comparar a sugestão gerada pelo sistema com a decisão real tomada pela Gestão para o mesmo dia, medindo a aderência por sabor, formato e dia da semana. A comparação tomou como referência os dias de corte registrados ao longo do estágio. O resultado dessa comparação é apresentado no capítulo 4: a aderência da sugestão de palha ficou em torno de 85%, enquanto a da cocada ficou entre 50% e 70% — diferença que o capítulo de discussão interpreta à luz da maior complexidade do planejamento da cocada (eventos da semana, antecipação de pedidos, restrições de não-acomodação).

A segunda frente é a validação dos dados e dos cálculos derivados. Os números de custo, margem, vendas e contribuição produzidos pelo sistema foram confrontados com a realidade física e com a percepção da Gestão. Por exemplo, o rendimento adotado nos cálculos — 8 bandejas por tacho (3 no caso da Zero), bandeja de 5,5 kg — foi confirmado diretamente com a fábrica, depois que uma checagem de consistência apontou que certos valores de rendimento extraídos do cadastro não fechavam fisicamente. Da mesma forma, os custos por quilo por sabor foram revisados quanto à sua plausibilidade (a Tradicional a cerca de R$ 5,60/kg e a Zero a R$ 25,79/kg, a mais cara por usar adoçantes especiais e ter menor rendimento), e a leitura das fotos dos 38 produtos serviu para validar o cadastro contra a realidade. Esse procedimento de triangulação — dado do sistema versus contagem física versus declaração da Gestão — é o que confere confiabilidade às análises do capítulo seguinte.

## 3.9 Limitações da metodologia

Algumas limitações precisam ser declaradas para o correto enquadramento dos resultados.

A primeira é o tamanho da amostra de folhas de produção coletadas no período (na ordem de 44 folhas registradas, 40 completas), o que recomenda cautela ao interpretar a curva ABC e as médias móveis, sensíveis a séries curtas. Padrões observados podem refletir viés de amostra pequena, e não tendência estrutural.

A segunda é o crescimento acentuado da fábrica durante a coleta: o volume de produção cresceu de forma expressiva ao longo de poucas semanas, o que torna o ambiente de estudo não estacionário e dificulta separar variação sazonal de variação de tendência.

A terceira é a natureza parcialmente não modelável das decisões da Gestão. Parte do planejamento incorpora informação que não chega ao sistema — encomendas de cliente, antecipação de pedidos da semana seguinte, eventos pontuais —, de modo que uma aderência inferior a 100% das sugestões não significa, necessariamente, erro do algoritmo, mas sim a presença de conhecimento tácito que o sistema ainda não captura (NONAKA; TAKEUCHI, 1997).

A quarta, já discutida na seção de custeio, é a ausência do custo de conversão, que impede o cálculo de lucro líquido por produto e restringe as análises ao nível da contribuição de material.

Por fim, como estudo de caso único, os resultados têm validade contextual forte para a empresa estudada, mas sua generalização deve ser feita por transferência analítica — pela aplicabilidade dos conceitos e do método a casos semelhantes —, e não por inferência estatística a uma população (YIN, 2015).
