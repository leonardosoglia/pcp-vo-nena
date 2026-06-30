# 4 RESULTADOS

Este capítulo apresenta o sistema de Planejamento e Controle da Produção desenvolvido para a Doces Vó Nena e os resultados obtidos em cada uma de suas frentes. A exposição segue a própria ordem de construção do projeto — da mais antiga para a mais recente —, porque essa progressão é, ela própria, um resultado: o sistema não foi concebido de cima para baixo, mas cresceu em camadas, partindo da digitalização fiel da folha de papel e chegando à integração com o ERP da empresa e à análise de custo, margem, vendas e lucratividade. Cada seção descreve o que foi construído, as decisões de modelagem que sustentam a construção e os números observados no estudo de caso. Reservou-se a interpretação aprofundada e o confronto com a teoria para o Capítulo 5; aqui o foco é o relato dos fatos e dos artefatos produzidos.

Por transparência metodológica, registra-se desde já que o sistema foi desenvolvido pelo autor com o apoio do Claude Code, um assistente de programação baseado em inteligência artificial, usado como ferramenta de codificação sob sua condução e validação contínuas. As decisões de modelagem, as regras de negócio e a engenharia de produção subjacentes são de autoria do pesquisador, fruto da imersão no chão de fábrica durante o estágio.

O sistema está hospedado em produção (Hugging Face Spaces, via Docker), com banco de dados PostgreSQL na nuvem e integração somente leitura com o ERP SIGE Cloud. Ao longo do período de coleta, a fábrica passou por crescimento acelerado de demanda, o que ampliou o valor das ferramentas, mas também limitou o tamanho da amostra histórica disponível para validação — ponto retomado na discussão das limitações.

O Quadro 3 oferece uma visão geral dos módulos construídos e de seu estágio de validação; as seções seguintes detalham cada frente.

**Quadro 3 — Módulos do sistema: desenvolvimento e validação**

| Módulo | Desenvolvido | Validado |
|---|---|---|
| Folha digital e Painel | Sim | Sim — em uso diário na fábrica |
| Curva ABC de produção | Sim | Sim — corrigida por fluxo (Forrester) |
| Média móvel de metas | Sim | Parcial — série histórica curta |
| Sugestão de corte e produção — Palha | Sim | Sim — aderência de ~85% à decisão real |
| Sugestão de corte e produção — Cocada | Sim | Parcial — aderência de 50–70% |
| Suprimentos: BOM, MRP e auto-baixa | Sim | Sim — explosão e baixa idempotente; falta carga inicial de estoque |
| Integração SIGE (somente leitura) | Sim | Sim — ciclo ficha técnica → OP → leitura provado |
| Reconciliação de estoque | Sim | Parcial — depende da contagem física inicial |
| Custo de produção (custo por peso) | Sim | Sim — validação dupla com o ERP; cobertura de 64% |
| Margem por canal | Sim | Sim — com a ressalva da margem de material |
| Vendas — Curva ABC de demanda | Sim | Sim — dados reais lidos do SIGE |
| Lucratividade — contribuição por produto | Sim | Sim — cobertura de 64% da receita |
| Catálogo de produtos | Sim | Sim — 38 fichas cruzadas com o sistema |
| Assistente de IA (LLM) | Sim | Em validação — uso assistido e pontual |

Fonte: elaborado pelo autor (2026).

## 4.1 Camada 0 — Digitalização da folha de produção

O ponto de partida foi substituir a folha de produção em papel por um registro digital fiel. A regra que orientou toda essa primeira camada foi a fidelidade ao papel antes da automação: o sistema faz exatamente o que a folha faz, na mesma unidade (unidades, bandejas, tachos), sem que nenhuma conversão automática substitua o dado que a equipe efetivamente anota. Conversões aparecem como referência visual, nunca como cálculo que apaga o número original. Essa decisão foi deliberada — só se ganha a confiança da fábrica quando a tela espelha o documento que as pessoas já conhecem.

### 4.1.1 Modelo de dados

A folha física foi mapeada para um conjunto de entidades relacionais, materializadas no banco em tabelas principais (entre elas `folha_cocada`, `folha_palha`, `papelzinho_joel` e a folha de Pão de Mel e Bala) e em tabelas de referência (metas-base por sabor e dia, fatores de conversão, parâmetros de "Para Virar" ideal). Três decisões de modelagem estruturam essa camada e atravessam todo o restante do trabalho.

A primeira é a chave de registro `(data, sabor)`: cada folha é identificada pela combinação da data com o sabor, garantindo unicidade do lançamento diário. A segunda é o entendimento de que cada folha é um *snapshot* independente, não acumulativo: o registro de um dia descreve o estado daquele dia e não se soma automaticamente ao do dia anterior. A terceira é que os valores derivados não são persistidos: campos que resultam de cálculo (como os cortados de segunda e terceira leitura ou as viradas recalculadas) são reconstruídos no momento da exibição, a partir dos dados primários, evitando inconsistência entre o que foi digitado e o que foi computado. Essas três decisões, aparentemente técnicas, são na verdade a tradução fiel da natureza do documento de origem: a folha de papel também é um instantâneo do dia, preenchido à mão, do qual o gestor lê derivados de cabeça.

A distinção entre *snapshot* (estado em um instante) e quantidade acumulável já antecipa o princípio de estoque *versus* fluxo de Forrester (1961), que se torna central nas camadas analíticas (seções 4.2 e 4.5) e que será retomado na discussão do Capítulo 5.

Para além das tabelas da folha, o modelo de dados do sistema articula produção, receita e estoque de insumos. A Figura 5 o sintetiza em forma simplificada: a folha de produção e a receita (lista de materiais) combinam-se para calcular o consumo, que alimenta as movimentações de estoque e, por elas, atualiza o saldo de insumos.

**Figura 5 — Modelo de dados simplificado do sistema**

[[IMG: COLAR AQUI a Figura 5 — Modelo de dados simplificado (imagem gerada pelo autor)]]

Fonte: elaborado pelo autor (2026).

### 4.1.2 Formulário de lançamento e Painel

A interface de entrada — o formulário diário de lançamento — reproduz visualmente os quadros do papel, preservando a disposição que a equipe já memorizou. Um detalhe de implementação merece registro porque é determinado pela própria lógica da fábrica: a coluna alimentada pela Produção (o "papelzinho") é renderizada antes da coluna oficial, porque é ela que alimenta os derivados em tempo real — a ordem de renderização inverte a ordem de leitura para respeitar a dependência de cálculo. Enquanto o usuário preenche, os derivados (cortados de segunda e terceira passagem, viradas recalculadas) aparecem imediatamente, dando à equipe um retorno que o papel jamais ofereceu.

Complementando o lançamento, construiu-se o Painel da fábrica, que consolida a folha do dia em tabela e indicadores-chave, organizado por departamento (Gestão, Produção, Corte, Embalagem, Estoque) e com uma aba de análise. Essa separação por departamento — em vez de nomes próprios — foi uma escolha consciente de profissionalização: dá ao sistema cara de ERP industrial e facilita a expansão futura.

A Figura 6 apresenta o Painel da fábrica, que consolida a folha do dia em tabela e indicadores, organizado por departamento.

**Figura 6 — Painel (dashboard) da fábrica**

[[IMG: COLAR AQUI o print do Painel (dashboard) da fábrica — folha do dia consolidada em tabela e indicadores por departamento]]

Fonte: elaborado pelo autor (2026).

### 4.1.3 Resultado operacional

O resultado direto desta camada é a eliminação do papel como meio primário de registro e a passagem para um registro digital pesquisável, com cálculo automático dos derivados. O preenchimento de uma folha completa leva poucos minutos, e o dado fica imediatamente disponível para todas as camadas analíticas seguintes. Ao longo do estágio, acumularam-se 44 folhas registradas (40 completas), base sobre a qual rodam todas as análises a seguir.

## 4.2 Camada 1 — Visualização e análise

Sobre o dado digitalizado, construiu-se uma camada de análise que transforma o registro bruto em informação para decisão. São dois instrumentos principais: a Curva ABC de produção e a média móvel de calibração de metas, além de um módulo de diagnóstico automático que reúne achados clássicos.

### 4.2.1 Curva ABC de produção

A Curva ABC de produção aplica o princípio de Pareto, generalizado à gestão por Juran (JURAN, 1951), para ordenar os produtos por sua relevância no volume produzido, distinguindo os poucos itens que respondem pela maior parte da produção (classe A) da longa cauda de itens de baixa expressão individual (classe C).

A implementação dessa curva rendeu o primeiro resultado conceitualmente forte do trabalho. Uma versão inicial somava a quantidade *embalada* — uma variável de estoque, medida a cada dia — ao longo de várias folhas, produzindo um total sem significado físico. Ao reconhecer o erro à luz do princípio de Forrester (1961), corrigiu-se a curva para somar as ordens de corte — uma variável de fluxo, que pode legitimamente ser acumulada por período. Essa correção, aparentemente pequena, é a primeira manifestação concreta de um princípio teórico clássico orientando a engenharia do sistema, e reaparece em todas as análises posteriores. O ranking resultante confirma a concentração esperada: o sabor Tradicional domina o volume, seguido pelos demais sabores em ordem decrescente.

A Figura 7 apresenta a Curva ABC de produção na tela do sistema, com os sabores ordenados por participação no volume produzido e agrupados nas classes A, B e C.

**Figura 7 — Curva ABC de produção**

[[IMG: COLAR AQUI o print da Curva ABC de produção — sabores ordenados por participação no volume produzido (classes A, B e C)]]

Fonte: elaborado pelo autor (2026).

### 4.2.2 Média móvel — calibração de metas

O segundo instrumento é a calibração das metas-base por sabor e dia da semana. Métodos clássicos de previsão, em especial médias móveis (MAKRIDAKIS; WHEELWRIGHT; HYNDMAN, 1998), comparam o realizado recente com a meta-base e sinalizam desvios sistemáticos, permitindo recalibrar os parâmetros sem sobre-ajuste. A ferramenta confronta a meta-base de cada sabor com a média dos cortados recentes e organiza o resultado em um mapa de calor por sabor × dia da semana, propondo automaticamente uma recalibração das metas.

A Figura 8 apresenta o mapa de calor de calibração de metas, que confronta a meta-base com a média dos cortados recentes por sabor e dia da semana.

**Figura 8 — Mapa de calor de calibração de metas (média móvel)**

[[IMG: COLAR AQUI o print do mapa de calor de calibração de metas — meta-base × média dos cortados recentes, por sabor e dia da semana]]

Fonte: elaborado pelo autor (2026).

### 4.2.3 Diagnóstico automático e o cuidado com a amostra

Esses sinais foram reunidos em um módulo de diagnóstico que sintetiza achados recorrentes — desbalanceamentos aparentes entre sabores, episódios de tachos parciais e outros padrões. Um achado importante, porém, veio do confronto desse diagnóstico com a Gestão: um aparente desbalanceamento sistemático apontado pelo sistema não foi confirmado pela Gestão como problema real. A reinterpretação correta é que muitas das diferenças entre o parâmetro praticado e a meta-base não são erro a corrigir, mas antecipação de pedidos da semana seguinte — planejamento, e não desvio. Esse episódio é um resultado em si: alertou para o risco de viés de amostra pequena e reforçou a postura de tratar todos os sinais estatísticos como apoio à decisão humana, nunca como sentença. Esse ponto é retomado no Capítulo 5.

### 4.2.4 Avaliação estatística dos modelos

A avaliação dos modelos analíticos seguiu o que cada técnica efetivamente permite medir, com a cautela imposta pelo tamanho da amostra (seção 3.9). Dois registros importam.

Para a sugestão automática (seção 4.3), o indicador de desempenho é a aderência — a proporção de decisões em que a sugestão do sistema coincide com a decisão real da Gestão, por sabor, formato e dia da semana. É uma taxa de acerto direta, observada em torno de 85% para a palha e de 50% a 70% para a cocada, medida sobre os dias de corte do estágio. Por se apoiar em amostra reduzida, esses valores são apresentados como evidência do estudo de caso, e não como estimativa com intervalo de confiança formal.

Para a calibração por média móvel (seção 4.2.2), o erro mensurável é o desvio entre a meta-base e a média observada por sabor e dia da semana, expresso em termos absolutos e percentuais — um indicador da família do erro percentual médio (MAPE). É esse desvio que aciona a recomendação de recalibração; seu cálculo é direto a partir do histórico, mas sua interpretação exige a mesma cautela de série curta, pois um único dia atípico desloca sensivelmente a média.

Em síntese, o trabalho privilegia os indicadores que a natureza dos dados sustenta — aderência e desvio —, em vez de produzir números estatísticos sem lastro.

## 4.3 Camada 2 — Sugestão automática

A camada seguinte deixa de apenas descrever o passado e passa a sugerir quantidades de corte e produção, comparando suas recomendações com as decisões reais da Gestão. O objetivo nunca foi automatizar a decisão, mas oferecer um ponto de partida defensável; a métrica central, portanto, é a aderência entre a sugestão do sistema e o que a Gestão de fato decidiu.

### 4.3.1 Palha — MRP semanal

A palha tem ciclo semanal e estrutura de decisão mais limpa, o que a tornou o caso mais tratável. O algoritmo segue a lógica de um MRP simplificado (ORLICKY, 1975) combinada a uma política de reposição a estoque-alvo (*order-up-to*): o corte atende à necessidade líquida da semana, e a produção repõe o estoque-alvo de bandejas. A calibração incluiu um modo Normal e um modo Conservador, com limiares ajustados para os formatos de venda.

Na comparação com as decisões reais da Gestão ao longo do estágio, observou-se aderência de aproximadamente 85%. É um resultado expressivo para um caso de pequena empresa: na maioria das decisões, o sistema chegou ao mesmo número que a Gestão chegou pela experiência.

### 4.3.2 Cocada — sugestão diária multiformato

A cocada é estruturalmente mais difícil: a decisão é diária (não semanal), envolve múltiplos formatos a partir do mesmo tacho (tablete, mini, PET e potes) e está sujeita a restrições de capacidade e ao tratamento dos tachos parciais. Desenvolveu-se o sugeridor em versões sucessivas, cada uma incorporando mais da realidade do chão de fábrica: da diferença simples entre parâmetro e cortados, à inclusão dos potes, à priorização por capacidade (Tradicional antes de Leite Condensado, e estes antes dos demais) com a sobra do tacho parcial sendo encaminhada a potes e a viração calculada, e finalmente à incorporação de um painel histórico que usa a mediana das últimas folhas do mesmo dia da semana.

A aderência da cocada ficou entre 50% e 70% — abaixo da palha, como esperado. Esse intervalo não é uma falha, e sim um resultado honesto: ele mede exatamente o quanto da decisão da cocada é capturável por regras determinísticas e o quanto depende de julgamento contextual da Gestão (eventos da semana, encomendas, intuição) que a estrutura algorítmica não modela. Essa diferença de aderência entre palha (~85%) e cocada (50–70%) é discutida em profundidade no Capítulo 5, pois delimita com precisão a fronteira entre o que o PCP estruturado resolve e o que permanece como conhecimento tácito (NONAKA; TAKEUCHI, 1997).

## 4.4 Suprimentos — MRP simplificado e auto-baixa

A frente de Suprimentos fecha o ciclo de PCP ao ligar a produção planejada ao consumo de materiais, aplicando o MRP simplificado (ORLICKY, 1975) descrito na revisão.

### 4.4.1 Cadastro de insumos e lista de materiais (BOM)

Cadastraram-se as matérias-primas e embalagens da fábrica e, sobre elas, a lista de materiais (BOM) dos produtos, a partir das receitas oficiais e das entrevistas com a Gestão e a Produção. A decisão de modelagem mais importante aqui é que a BOM foi cadastrada por tacho (cocada e bala) ou por bandeja (palha), e não por formato de venda. A razão é de fidelidade ao processo: a fábrica não produz "um tablete de 45 g"; ela coze um tacho de cada sabor, do qual saem bandejas que depois são cortadas em vários formatos. Modelar a receita pela unidade real de produção é a única forma de o MRP refletir o que de fato acontece — e essa mesma escolha viabiliza, mais adiante, o método de custo por peso (seção 4.6). A mistura padrão é somada ao leite em cada receita de cocada, como na prática da fábrica.

### 4.4.2 Explosão de necessidades e baixa automática

Quando a folha do dia é salva, o sistema executa a explosão da BOM: multiplica as quantidades produzidas pelos coeficientes técnicos de cada insumo, gera a necessidade de matéria-prima e dá baixa automática no estoque de insumos. O confronto entre necessidade e estoque disponível sustenta a sugestão de compra. Durante o desenvolvimento, corrigiu-se um erro de unidade em que a palha era tratada como tacho quando a unidade correta de sua BOM é a bandeja — mais um caso, como o da Curva ABC, em que a disciplina de unidades explícitas (unidade, bandeja, tacho) evitou um cálculo silenciosamente errado.

A baixa automática é idempotente e reversível, de modo que reprocessar a mesma folha não duplica o consumo. Cabe um registro de honestidade que reaparece na integração com o ERP: a baixa automática sem uma carga inicial de estoque produz saldos negativos de insumo — sinal correto de que falta registrar a contagem inicial, e não erro de cálculo. Esse é o tipo de evidência que a reconciliação (seção 4.5) trata explicitamente.

## 4.5 Integração com o ERP SIGE (somente leitura) e reconciliação de estoque

A frente mais recente e mais ambiciosa do trabalho foi integrar o sistema de PCP ao ERP que a empresa já operava, o SIGE Cloud. Essa integração transformou o projeto: de uma digitalização da folha, ele passou a um PCP capaz de raciocinar sobre custo, margem, vendas e lucro com dados reais da empresa.

A Figura 9 representa esse fluxo entre o ERP e o PCP: de um lado o SIGE, com o ciclo de materiais (nota fiscal → estoque → Ordem de Produção → baixa → rendimento); de outro o PCP, que lê desse ciclo — custo, vendas, estoque e Ordem de Produção — para apoiar a decisão, sem nunca escrever no ERP.

**Figura 9 — Fluxo de integração entre o ERP (SIGE) e o PCP**

[[IMG: COLAR AQUI a Figura 9 — Fluxo ERP ↔ PCP (imagem gerada pelo autor)]]

Fonte: elaborado pelo autor (2026).

### 4.5.1 A Ordem de Produção como ponte e o modelo de contextos delimitados

No SIGE, o ciclo de materiais percorre etapas bem definidas: a nota fiscal eletrônica (NF-e/XML) dá entrada no estoque; a Ordem de Produção (OP) explode a ficha técnica do produto; o sistema faz a pré-reserva dos insumos, a baixa por lote e, ao final, registra o rendimento. A OP é a ponte entre o mundo contábil do ERP e o mundo operacional do chão de fábrica. O ponto defendido, validado com a Gestão, é que a decisão de produzir continua humana — tomada pela Gestão a partir de demanda, estoque e antecipação de pedidos —, e nenhum sistema a substitui.

Para organizar a relação entre os dois sistemas sem que um corrompesse o outro, adotou-se a noção de contextos delimitados (*bounded contexts*), do *Domain-Driven Design* (EVANS, 2009): o SIGE é a fonte da verdade contábil (custo, identidade do produto, saldo teórico) e o sistema de PCP é a fonte da verdade operacional (o que foi efetivamente produzido e cortado). Coerente com esse desenho, a integração é somente leitura: o PCP consome dados do SIGE — catálogo de produtos, custos, pedidos —, mas nunca escreve nele, preservando o ERP como registro oficial e evitando duplo comando sobre o estoque.

### 4.5.2 A linguagem da produção ≠ a linguagem do ERP

Conectar os dois mundos exigiu construir um mapa de equivalências (*de-para*) entre os itens, porque o mesmo produto recebe nomes diferentes em cada contexto. O exemplo emblemático é que o produto cadastrado no SIGE como "Cocada Cubos 160g" corresponde ao que o chão de fábrica chama de "PET". Sem esse mapa, qualquer cálculo de custo, demanda ou necessidade fica corrompido. Construir e manter o *de-para* dos insumos e dos produtos vendáveis revelou-se condição necessária — e não trivial — para a confiabilidade de tudo o que veio depois. Outro cuidado de modelagem associado foi identificar que o saldo de estoque, no SIGE da empresa, vive no cadastro operacional real de cada item, e não no cadastro "de produção" idealizado, que aparece zerado — uma sutileza que só a inspeção atenta dos dados revelou.

### 4.5.3 Reconciliação de estoque: teórico × físico

Sobre a integração, construiu-se a reconciliação de estoque: o confronto entre o saldo teórico (o que o SIGE diz que existe, pela soma de entradas e baixas) e o saldo físico (a contagem real). A divergência entre os dois é tratada explicitamente como ajuste de inventário — informação a registrar, e não erro a esconder. Essa reconciliação é a aplicação mais direta do princípio de Forrester (1961) em todo o projeto: modelou-se o produto acabado em três camadas, cada uma um reservatório (*stock*) distinto que não pode ser confundido nem somado com os demais — a prateleira (produto pronto para venda), o semiacabado (bandejas cortadas à espera de embalagem) e a produção em curso. Essa separação resolveu confusões persistentes em que quantidades de camadas diferentes eram tratadas como se fossem o mesmo número. A contagem física realizada todas as manhãs alimenta justamente esses reservatórios, e a reconciliação fecha o ciclo entre o que o ERP registra e o que a fábrica de fato tem.

A Figura 10 mostra essa reconciliação na tela do sistema, insumo a insumo.

**Figura 10 — Tela de Reconciliação de estoque (teórico × físico)**

[[IMG: COLAR AQUI o print da tela de Reconciliação de estoque — saldo teórico do SIGE × estoque do sistema, insumo a insumo, com a divergência (ajuste de inventário) destacada]]

Fonte: elaborado pelo autor (2026).

## 4.6 Custo de produção: BOM × custo de insumo e o método do custo por peso

Com o custo de cada insumo trazido do SIGE e a BOM cadastrada por tacho/bandeja, tornou-se possível calcular o custo de material de cada produto: a explosão da receita multiplica os coeficientes da BOM pelo custo unitário de cada insumo. Esse é o primeiro passo do chamado "ir além do ERP" — usar o dado contábil do SIGE para responder a uma pergunta operacional que o ERP, sozinho, não responde de forma confiável.

A dificuldade prática é que a fábrica vende muitos formatos do mesmo sabor (tablete 45 g, mini 30 g, PET de 100 a 160 g, potes de tamanhos variados), e mapear o custo formato a formato seria trabalhoso e frágil. A solução desenvolvida é o método do custo por peso, e ele se apoia em uma observação simples: o nome do produto no SIGE traz a gramatura (por exemplo, "Cocada Cubos 160g", "Cocada Zero 100g"). Tendo o custo por quilograma de cada sabor — obtido dividindo o custo da receita do tacho pela quantidade de quilogramas vendáveis que o tacho rende —, o custo de qualquer formato daquele sabor é simplesmente o custo por quilograma multiplicado pela gramatura do formato. Uma única referência por sabor passa a custear todo o portfólio daquele sabor.

O rendimento que ancora esse cálculo foi confirmado pela fábrica: o tacho normal rende 8 bandejas, o tacho Zero rende 3, e cada bandeja pesa 5,5 kg. Para fins de custo, considera-se a fração vendável da bandeja (parte do peso se perde como aparas e umidade no corte). É importante o registro de honestidade, mantido visível na própria tela: o ranking de quem custa mais é robusto, mas o valor absoluto escala com o rendimento adotado; por isso o rendimento foi confirmado diretamente com a Produção antes de fixar os números.

O impacto do método é direto e mensurável: ele elevou a cobertura de custo de 17% para 64% das vendas. Ou seja, antes do custo por peso, era possível atribuir custo de material a apenas 17% da receita (os poucos formatos mapeados manualmente); generalizando pelo peso, passou-se a custear 64% — essencialmente toda a cocada, mais o Pão de Mel. O restante (palha, bala e alguns itens sem receita completa) permanece marcado como "a confirmar", e a tela explicita essa cobertura parcial em vez de simular um número fechado.

## 4.7 Margem e a armadilha da margem de matéria-prima

De posse do custo de material e do preço de venda, o passo natural seria calcular a margem. Foi aqui que se documentou um dos achados mais relevantes do trabalho: a armadilha da margem de matéria-prima.

A margem de matéria-prima — preço de venda menos apenas o custo do material — é quase sempre alta: observaram-se valores entre 84% e 96%. À primeira vista, isso sugeriria que praticamente todo produto é altamente lucrativo. Mas essa leitura é falsa. A margem de material é alta porque, neste tipo de produto, a matéria-prima é uma fração pequena do preço final; o que ela não captura é o custo de conversão — mão de obra, energia, embalagem e demais despesas de transformar insumo em doce pronto e vendido. Margem de material não é lucro. Confundir as duas leva a priorizar os produtos errados, justamente o que esta análise busca evitar.

A consequência prática é que o sistema apresenta a margem de material com clareza, mas com a ressalva explícita de que ela não é lucratividade, e organiza a análise de margem também por canal de venda (atacado, varejo e quiosque), que têm estruturas de preço distintas. O custo de conversão não está disponível no SIGE e precisa ser levantado por fora — o que é tratado como achado, e não como falha do projeto, na seção 4.9 e no Capítulo 5.

## 4.8 Vendas reais — Curva ABC de demanda

A integração com o SIGE deu acesso a algo que, no início do projeto, só seria obtido por planilhas manuais: as vendas reais da empresa. O SIGE registra os pedidos e as operações de PDV com os produtos vendidos, o que permitiu construir uma tela de Vendas sem nenhuma planilha intermediária — o dado vem direto do ERP.

Sobre essas vendas, construiu-se a Curva ABC de demanda, ordenando os produtos por volume e por receita reais, com recortes por canal e por empresa. Os números do estudo de caso mostram um faturamento da ordem de R$ 400 a 530 mil por mês, com aproximadamente 32 produtos classe A respondendo pela maior parte da receita — confirmando a concentração de Pareto também na demanda. A análise revelou ainda particularidades operacionais úteis à Gestão, como a presença de itens de revenda no faturamento e uma parcela significativa de receita sem canal classificado, que aponta uma oportunidade de melhoria no próprio cadastro do ERP.

O ponto conceitual que essa curva prepara é decisivo: a ordenação por demanda não coincide com a ordenação por produção nem, sobretudo, com a ordenação por lucro. Vender muito não é o mesmo que lucrar muito — tese que a seção seguinte demonstra com números.

A Figura 11 apresenta a tela de Vendas, com a Curva ABC de demanda real lida do SIGE — receita e volume por produto, com recortes por canal e por empresa.

**Figura 11 — Tela de Vendas: Curva ABC de demanda real**

[[IMG: COLAR AQUI o print da tela de Vendas — Curva ABC de demanda real lida do SIGE: receita e volume por produto, com recortes por canal e por empresa (gráfico de Pareto e cartões-resumo)]]

Fonte: elaborado pelo autor (2026).

## 4.9 Lucratividade — contribuição por produto

A tela de Lucratividade é a síntese de tudo o que veio antes: cruza as vendas reais do SIGE com o custo de material calculado pelo método do custo por peso para apresentar a contribuição por produto — a receita de cada produto menos o custo do material que ele consome. Em vez de responder "o que vende mais", ela responde "o que mais contribui".

O resultado reordena o portfólio. O campeão de contribuição de material é a Cocada Cubos Tradicional 160 g, com cerca de R$ 31 mil por mês — um produto que combina volume alto com baixo custo de material. No extremo oposto, e este é o achado mais ilustrativo, está a cocada Zero: ela vende bem, mas é a mais cara de produzir — seu custo de material por quilograma é de cerca de R$ 25,79/kg, contra R$ 5,60/kg da Tradicional, ou seja, 4,6 vezes mais cara, em razão dos adoçantes especiais e do menor rendimento do tacho (3 bandejas em vez de 8). A consequência é direta: um produto pode liderar a curva de vendas e, ao mesmo tempo, ocupar posição muito inferior na curva de contribuição. A tela materializa essa diferença em quatro quadros — quem mais contribui, o custo por quilograma por sabor (com alerta para o Zero), uma matriz de giro × ticket e a comparação entre produção e venda.

Dois registros de honestidade científica acompanham essa tela e se mantêm visíveis para o usuário. O primeiro: a contribuição calculada é receita menos custo de matéria-prima, não lucro líquido — falta o custo de conversão, que não existe no SIGE e está sendo levantado à parte. O segundo: a cobertura é parcial — a tela cobre os 64% da receita com custo de material mapeado (toda a cocada, pelo método do peso, mais o Pão de Mel) e marca o restante como "a confirmar". Assim, o ranking de contribuição é robusto e já orienta decisão de mix; o que ainda não se tem é o lucro líquido absoluto, que dependeria da terceira camada de custo. Esse limite do ERP — entregar custo de insumo e receita, mas não o custo de conversão alocado à fábrica — é um dos resultados conceituais centrais do trabalho, retomado no Capítulo 5.

A Figura 12 apresenta o painel de Lucratividade, que organiza a contribuição por produto em quatro quadros.

**Figura 12 — Painel de Lucratividade: contribuição por produto**

[[IMG: COLAR AQUI o print do painel de Lucratividade — os quatro quadros: (1) Curva ABC por contribuição, (2) custo por quilo por sabor (com alerta da Zero), (3) matriz giro × ticket e (4) produção × venda por sabor]]

Fonte: elaborado pelo autor (2026).

## 4.10 Catálogo de produtos

A última frente foi consolidar um catálogo de produtos: foram preenchidas 38 fichas a partir da leitura das fotos dos itens comercializados (embalagens, gramaturas, sabores, formatos), cruzando cada uma com os dados do sistema e do SIGE. O cruzamento serviu de referência — distinguindo produção interna de revenda terceirizada e fixando as gramaturas que alimentam o método de custo por peso — e de validação, expondo e corrigindo inconsistências entre a linguagem da produção, o cadastro do ERP e a realidade física do produto (a mesma classe de problema que motivou o *de-para* da seção 4.5). É, assim, tanto entregável de gestão quanto salvaguarda de qualidade de dados para as análises de custo, margem e lucratividade.

## 4.11 Do papel ao sistema — comparação operacional

Além das frentes descritas, convém contrastar diretamente a operação antes (folha de papel) e depois (sistema), conforme o Quadro 4. O ganho mais relevante não está na velocidade de preencher a folha — que permanece de poucos minutos —, mas no que o sistema torna possível: localizar, calcular, consolidar e alertar, capacidades que o papel jamais ofereceu.

**Quadro 4 — Comparação operacional: do papel ao sistema**

| Tarefa | Antes (papel) | Depois (sistema) |
|---|---|---|
| Preencher a folha do dia | manual, com somas feitas à mão | formulário digital; cortados e viradas calculados automaticamente |
| Localizar uma folha ou informação anterior | busca física em pilhas e pastas | seleção por data, em segundos |
| Calcular a necessidade de insumos | inexistente ou cálculo manual demorado | automática (explosão da BOM: produção × receita − estoque) |
| Gerar a ordem de corte e de produção | decisão manual, sem apoio quantitativo | sugestão automática para ajuste da Gestão |
| Identificar estoque crítico | sem visão consolidada | alerta automático na tela inicial |
| Consolidar histórico e análise (ABC, médias móveis) | inviável no papel | automático, a partir do registro digital |
| Erros de soma e de transcrição | sujeitos a erro humano | eliminados nos cálculos derivados |

Fonte: elaborado pelo autor (2026).

Os contrastes do Quadro 4 são qualitativos, porém concretos e verificáveis. A quantificação precisa dos tempos (em segundos ou minutos por tarefa) pode ser aferida para a defesa, reforçando ainda mais a comparação.

## 4.12 Síntese dos resultados

O Quadro 5 sintetiza as frentes construídas, relacionando objetivo, resultado e impacto de cada uma.

**Quadro 5 — Síntese das frentes: objetivo, resultado e impacto**

| Frente | Objetivo | Resultado | Impacto |
|---|---|---|---|
| Digitalização da folha | substituir o papel por registro fiel | registro digital; derivados em tempo real | histórico pesquisável; base de todas as análises |
| Visualização e análise | transformar dado em informação | Curva ABC (fluxo) e média móvel | priorização e sinais para a Gestão |
| Sugestão automática | apoiar a decisão de corte e produção | aderência palha ~85%, cocada 50–70% | ponto de partida defensável; delimita o tácito |
| Suprimentos e MRP | ligar produção ao consumo de insumo | BOM por tacho/bandeja; baixa idempotente | necessidade de compra automática |
| Integração SIGE e reconciliação | usar custo e vendas reais do ERP | ciclo ficha → OP → leitura; reconciliação em 3 camadas | PCP integrado ao ERP; ajuste de inventário explícito |
| Custo de produção | custear todos os formatos | custo por peso; cobertura 17% → 64% | análise de margem em escala |
| Margem | medir a margem por produto e canal | margem de material 84–96% (≠ lucro) | evita priorizar o produto errado |
| Vendas reais | enxergar a demanda real | Curva ABC de demanda; ~R$ 400–530 mil/mês; ~32 classe A | decisão de mix com dado real |
| Lucratividade | saber quem mais contribui | campeão Cubos Tradicional ~R$ 31 mil/mês; Zero 4,6× mais cara | reordena o portfólio por contribuição |
| Catálogo de produtos | padronizar a identidade dos produtos | 38 fichas validadas | qualidade de dados para custo e margem |

Fonte: elaborado pelo autor (2026).

O fio que costura todas as frentes é a progressão em camadas anunciada no início: cada nova capacidade se apoia na anterior e a estende, e três princípios atravessam o conjunto — fidelidade ao processo real da fábrica, disciplina de unidades e o princípio de estoque *versus* fluxo de Forrester (1961). Os resultados aqui descritos — em especial a divergência entre as curvas ABC de produção, demanda e lucro, a armadilha da margem de matéria-prima e o limite do ERP quanto ao custo de conversão — são interpretados e confrontados com a literatura no Capítulo 5.
