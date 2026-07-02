# 5 CONSIDERAÇÕES FINAIS

## 5.1 Síntese do estágio

O estágio tinha como objetivo aplicar, em um contexto industrial real, os conhecimentos de Planejamento e Controle da Produção (PCP) adquiridos ao longo do curso, contribuindo com a estruturação do PCP de uma confeitaria de pequeno porte. Considero que esse objetivo foi alcançado. A operação que antes dependia de folhas de papel e da memória da Gestão passou a contar com um sistema digital em uso diário, com o histórico preservado, os cálculos automáticos e sugestões de produção. E o trabalho não parou na digitalização: ao longo do período, o sistema evoluiu para um PCP integrado ao ERP da empresa, passando a tratar custo de produção, margem por canal, vendas reais e contribuição por produto.

Mais do que entregar uma ferramenta, o estágio me permitiu compreender em profundidade como uma pequena indústria de alimentos realmente planeja e controla sua produção — e, a partir daí, adaptar a teoria a essa realidade. Foi essa ida e volta constante entre o que eu havia estudado e o que eu via no chão de fábrica que deu sentido a todo o trabalho.

## 5.2 A relação entre a teoria de Engenharia de Produção e a prática na fábrica

O ponto que mais me marcou no estágio foi perceber o quanto a teoria de Engenharia de Produção descreve, sim, o que acontece na fábrica — mas quase nunca na forma "limpa" dos livros. Os conceitos estão todos lá, vivos na operação; só não vêm rotulados.

O planejamento de necessidades de materiais (MRP), por exemplo, eu sempre tinha estudado como um procedimento formal: ordem de produção, lista de materiais, explosão das necessidades, comparação com o estoque (ORLICKY, 1975). Na Doces Vó Nena, esse raciocínio existia inteiro, mas acontecia de cabeça, na conversa da manhã entre mim e a Gestão. Meu trabalho, no fundo, foi escrever esse MRP que já existia de forma tácita — montar o cadastro de insumos, a lista de materiais por sabor e o cálculo automático do consumo do dia — sem mudar a lógica de quem já o fazia bem. A teoria me deu a estrutura para organizar o que a experiência da fábrica já sabia fazer.

A distinção entre **estoque e fluxo** foi outro caso em que a teoria me corrigiu na prática. Logo no início, ao montar a Curva ABC dos produtos, cometi o erro de somar estoques — que são fotografias de um instante — como se fossem fluxo ao longo do tempo. O conceito de variáveis de nível e de fluxo (FORRESTER, 1961) deixou claro por que aquilo estava errado e organizou toda a modelagem seguinte: a folha de produção passou a ser tratada como um retrato independente de cada dia, e não como um saldo que se acumula. Esse mesmo cuidado me ajudou depois a enxergar o produto em diferentes pontos — na prateleira, em processo e em produção — quando passei a reconciliar o estoque teórico do ERP com a minha contagem física.

A **Curva ABC** (princípio de Pareto, popularizado por Juran) (JURAN, 1951) também ganhou camadas que eu não tinha percebido na teoria. Na prática, descobri que a Curva ABC por **volume**, por **receita** e por **contribuição** não coincidem: vender muito não é a mesma coisa que lucrar muito. A cocada Zero, por exemplo, vende bem, mas é de longe a mais cara de produzir — cerca de R\$ 25,79 por quilo de material contra R\$ 5,60 da Tradicional. Sem cruzar venda com custo, a empresa olharia só o que sai mais e não o que efetivamente sustenta o resultado.

Foi também na prática que entendi os **limites** das ferramentas. O **lead time** da cocada (cerca de três dias entre o tacho e o corte) torna a produção de hoje uma aposta na demanda de dois a três dias à frente, o que aproxima o planejamento de um problema de previsão, e não de simples reposição. E a previsão tem seus limites: minhas sugestões automáticas alcançaram uma aderência de cerca de **85% na palha**, mas só de **50% a 70% na cocada**, porque a decisão da cocada carrega um julgamento da Gestão — sazonalidade, pedidos antecipados, eventos da semana — que uma regra fixa não captura por inteiro. Em vez de esconder essa diferença, registrei-a como um limite conhecido da ferramenta.

Por fim, a integração com o ERP me ensinou onde a teoria do sistema de informação encosta na realidade contábil da empresa. O ERP entrega o custo do insumo e a receita, mas **não** entrega o custo de **conversão** — mão de obra, energia, *overhead* — alocado a cada produto. Esse custo precisa ser levantado por fora. Demorei a aceitar que isso não era uma falha do meu trabalho, e sim um achado: há um limite no que o registro contábil consegue responder sobre o custo real de produzir, e reconhecê-lo com honestidade vale mais do que forçar um número que os dados não sustentam.

## 5.3 Aprendizados

### 5.3.1 Técnicos

No plano técnico, a vivência consolidou a aplicação prática de conceitos de PCP — MRP, lista de materiais, Curva ABC, *lead time*, estoque-alvo — e o desenvolvimento de um sistema de informação aplicado à manufatura, unindo modelagem de dados, automação de cálculos e análise. Desenvolvi o sistema de forma incremental, com o apoio do Claude Code, um assistente de programação baseado em Inteligência Artificial: ele me ajudou a escrever e revisar o código com mais rapidez, mas as decisões de o que construir e de como modelar a fábrica foram minhas, sempre a partir do que eu observava no chão de fábrica e do que levantava com a Gestão.

O aprendizado técnico que levo como mais importante é simples de enunciar e difícil de praticar: **um modelo só é útil quando é fiel ao processo real**. Cada conversão (tacho, bandeja, display), cada regra de negócio e cada nome do chão de fábrica precisou ser entendido antes de ser formalizado. Foi por isso que tive o cuidado de traduzir a linguagem da produção para a linguagem do ERP — o mesmo produto que a equipe chama de "Pet" aparece no ERP como "Cocada Cubos 160 g" —, mapeando essas equivalências uma a uma para que os dados conversassem sem erro.

### 5.3.2 Profissionais

No plano profissional, convivi com diferentes departamentos e perfis, o que me exigiu comunicar ideias técnicas a pessoas não familiarizadas com tecnologia, traduzindo-as sempre pelo efeito prático, e não pelo jargão. Aprendi a priorizar entregas conforme a necessidade real da operação — as funcionalidades do sistema foram surgindo na medida em que a fábrica precisava delas, não de um plano fechado de antemão —, a gerir expectativas e a documentar continuamente as decisões. Em um primeiro estágio, percebi que essas competências de comunicação e organização pesam tanto quanto o conhecimento técnico.

### 5.3.3 Pessoais

No plano pessoal, o estágio reforçou minha disposição para entender um problema a fundo antes de propor qualquer solução, e a importância de ouvir quem opera o processo no dia a dia. Passar as manhãs no estoque e junto às equipes me mostrou que boas soluções de engenharia nascem da observação atenta da realidade, e não apenas do modelo teórico. Também me ensinou a conviver com a incerteza: nem tudo na fábrica cabe em uma regra, e saber até onde a automação ajuda — e onde a decisão deve permanecer humana — foi um amadurecimento que levo para além do estágio.

## 5.4 Dificuldades enfrentadas

A primeira dificuldade foi a **complexidade do domínio**. A confeitaria tem uma terminologia própria, com unidades e conversões particulares (tachos, bandejas, displays, potes), e nada disso estava escrito: vivia na experiência da Gestão e da Produção. Levantar e documentar essas regras, por entrevistas e pela observação diária, foi um trabalho contínuo e às vezes lento, mas indispensável — sem ele, qualquer modelo sairia errado.

A segunda foi **traduzir a prática operacional, muitas vezes informal, em uma modelagem formal de dados**. Decisões que a fábrica tomava de forma fluida precisavam virar campos, regras e cálculos exatos, sem perder a fidelidade ao que realmente acontece. Foi nesse ponto que mais senti a tensão entre o rigor do sistema e a flexibilidade do chão de fábrica.

A terceira foi a **calibração das sugestões automáticas** contra as decisões reais da Gestão, especialmente na cocada, cuja decisão tem um forte componente de julgamento humano. Aceitar que uma aderência de 50% a 70% era um resultado honesto — e não um defeito a ser disfarçado — exigiu maturidade técnica.

A quarta foi o **crescimento acelerado da empresa** durante o período. A demanda aumentou ao longo do estágio, e parâmetros que eu havia fixado ficavam defasados rapidamente. A resposta foi deixar de confiar em valores fixos e passar a usar janelas móveis de referência, calibradas pelo histórico recente — uma lição prática sobre não tratar um número como verdade permanente.

Por fim, houve a dificuldade, mais discreta, de **não ter um modelo pronto para copiar**. Boa parte do que construí precisou ser pensado do zero para o porte e a realidade desta fábrica específica, o que tornou o estágio mais desafiador, porém muito mais formativo.

## 5.5 Recomendações

**Para a empresa.** Recomendo manter o uso e a calibração contínua do sistema; avançar na integração com o ERP, agora que a leitura está consolidada; estruturar, por fora do ERP, o levantamento do custo de conversão, que é hoje a principal lacuna para se chegar ao custo total e ao lucro real por produto; e organizar o treinamento de novos usuários, para que o sistema não dependa de uma única pessoa.

**Para futuros estagiários.** Recomendo imergir no chão de fábrica antes de modelar qualquer coisa; documentar diariamente as decisões e descobertas, registrando na hora os dados da operação para não perdê-los; e manter comunicação frequente tanto com a empresa quanto com o orientador.

**Para o curso.** Recomendo dar maior ênfase ao PCP aplicado a micro e pequenas indústrias e incentivar estágios nesse tipo de empresa — um contexto rico em aprendizado, em que o estudante toca em todas as etapas do PCP, e historicamente menos procurado do que o das grandes manufaturas.

## 5.6 Trabalhos futuros

O sistema continuará evoluindo após o término do estágio. As próximas frentes previstas são a consolidação da baixa automática de insumos por produção, o aprofundamento da integração com o ERP, a evolução das telas de vendas e lucratividade já iniciadas — que permitem analisar o giro dos produtos a partir da demanda real — e o levantamento do custo de conversão, para fechar a leitura do custo total. Em conjunto, essas etapas ampliam a camada de apoio à decisão construída sobre os dados da própria fábrica, sempre preservando a regra que orientou todo o projeto: o sistema organiza a informação e sugere, mas a decisão de quanto produzir permanece humana.

## 5.7 Encerramento

Encerro o estágio com a convicção de que ele cumpriu o que se propunha. Agradeço à Doces Vó Nena pela abertura em compartilhar sua operação e por confiar no desenvolvimento aqui descrito; à Gestão e às equipes de Produção, Corte e Embalagem, pela paciência em me explicar, tantas vezes, como a fábrica realmente funciona; e ao professor orientador, pelo acompanhamento ao longo de todo o período.

A experiência uniu, na prática, a minha formação em Engenharia de Produção e a realidade de uma pequena indústria de alimentos. Sai do estágio entendendo melhor o que aprendi na universidade, justamente porque precisei colocá-lo à prova diante de um processo real, com suas particularidades, suas pessoas e suas restrições. E deixo na empresa um sistema que seguirá em uso depois do meu término — talvez o sinal mais concreto de que o trabalho fez sentido.
