# 1 INTRODUÇÃO

> **Esboço inicial — 27/05/2026.** Texto em PT-BR acadêmico, citações
> autor-data (ABNT). Procure `<<PREENCHER>>` pra pontos que precisam de
> decisão sua ou do orientador. Revise o tom — escrevi pra ser revisado,
> não pra ser final.

---

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
e a tomada de decisão baseada em dados (SLACK; CHAMBERS; JOHNSTON, 2018).

Esse cenário se aplica particularmente bem ao setor de alimentos artesanais
e semi-industriais brasileiro, no qual a produção combina receitas
tradicionais com escalas crescentes de comercialização. Nesses ambientes,
decisões críticas — quanto produzir de cada sabor, em que ordem cortar,
quando solicitar matéria-prima — são tomadas com base na experiência
acumulada dos gestores, e raramente sob apoio sistemático de dados ou
modelos de planejamento (MARTINS; LAUGENI, 2015).

## 1.2 Apresentação da empresa

A **Pequenas Mordidas Alimentos Eireli**, conhecida comercialmente como
**Doces Vó Nena**, é uma confeitaria industrial localizada em São Paulo (SP).
Produz cocadas, palhas italianas, pão de mel, balas de doce de leite e doces
finos, com distribuição em pontos de venda próprios (quiosques) e
fornecimento a clientes corporativos.

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

## 1.3 Problema

A operação descrita acima apresenta três limitações estruturais que
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
(CHOPRA; MEINDL, 2016).

**Terceiro, a dependência crítica do conhecimento tácito da Gestão.** As
decisões diárias — quantas bandejas cortar, em que sabor, com que prioridade
— concentram-se em uma única pessoa, com base em sua memória sobre pedidos
antecipados, sazonalidade e disponibilidade da equipe. Esse conhecimento
não está documentado nem sistematicamente capturado, tornando a operação
vulnerável a ausências do gestor e dificultando a transferência futura de
conhecimento (NONAKA; TAKEUCHI, 1997).

## 1.4 Justificativa

A digitalização do PCP em uma confeitaria industrial de pequeno porte é
justificada por três frentes complementares.

**Operacional.** Substituir o papel por um sistema digital permite
preencher, consultar e exportar folhas em segundos, reduzindo o tempo de
operações administrativas e eliminando perdas físicas de registros.
Comparações entre dias, sabores e semanas tornam-se imediatas, e a
exportação para planilhas viabiliza análises adicionais externas.

**Estratégica.** A estruturação dos dados em base relacional cria a base
para a aplicação de técnicas de Engenharia de Produção classicamente
restritas a grandes indústrias: Curva ABC de sabores, MRP simplificado para
suprimentos, médias móveis para calibração de metas, detecção de anomalias
operacionais via aprendizado de máquina (HOPP; SPEARMAN, 2008). Cada uma
dessas técnicas, isoladamente, agrega valor; em conjunto, transforma o
controle do PCP de reativo para proativo.

**Acadêmica.** A literatura nacional sobre PCP aplicado a micro e pequenas
indústrias é relativamente escassa quando comparada à literatura sobre
grandes manufaturas (`<<CITAR ESTUDOS EXISTENTES DURANTE A REVISÃO>>`).
Documentar a implementação de um sistema de PCP em uma confeitaria
industrial — incluindo as adaptações necessárias ao contexto de pequena
escala e à natureza artesanal-industrial dos produtos — contribui com um
caso de estudo replicável para outras empresas do setor.

A presença de um agente cognitivo baseado em Modelo de Linguagem de Grande
Porte (LLM) como camada complementar de apoio à decisão, descrita no
Capítulo 4, representa uma fronteira emergente da prática em PCP, ainda
pouco explorada na literatura acadêmica brasileira em Engenharia de
Produção.

## 1.5 Objetivos

### 1.5.1 Objetivo geral

Desenvolver e implementar um sistema digital de Planejamento e Controle da
Produção para a confeitaria industrial Doces Vó Nena, substituindo o
controle manual em papel e incorporando funcionalidades de visualização,
sugestão automática e apoio cognitivo à decisão.

### 1.5.2 Objetivos específicos

1. **Mapear** os processos produtivos atuais da empresa, identificando
   etapas, unidades de medida, prazos e gargalos.
2. **Modelar** o domínio de dados em base relacional, preservando a
   estrutura conceitual da folha de produção em papel.
3. **Implementar a Camada 0 (digitalização)** — formulário digital
   equivalente ao papel, com persistência em banco de dados relacional.
4. **Implementar a Camada 1 (visualização e análise)** — painel de
   acompanhamento, exportação de dados e análises descritivas:
   Curva ABC, detecção de anomalias por *Isolation Forest* e média móvel
   de calibração de metas.
5. **Implementar a Camada 2 (sugestão automática)** — algoritmos de
   sugestão de corte e produção para palha e cocada, calibrados contra
   decisões reais da Gestão.
6. **Implementar o módulo de Suprimentos** com MRP simplificado a partir
   da lista de materiais (BOM) coletada em entrevista com a Gestão.
7. **Avaliar a aderência** das sugestões automáticas às decisões reais da
   Gestão, identificando padrões e limites da modelagem determinística.
8. **Discutir** o papel de um agente conversacional baseado em LLM como
   camada de apoio cognitivo, capturando contexto não estruturado que
   complementa o modelo formal.

## 1.6 Estrutura do trabalho

Este Trabalho de Conclusão de Curso está organizado em seis capítulos.

**O Capítulo 2** apresenta a revisão de literatura, abordando os
fundamentos do PCP, os conceitos de MRP, BOM, Curva ABC e princípio de
estoque versus fluxo (FORRESTER, 1961), além de uma seção sobre aplicações
recentes de aprendizado de máquina e LLMs em sistemas industriais.

**O Capítulo 3** descreve a metodologia, incluindo o levantamento de
processos junto à empresa, a modelagem de dados, as escolhas tecnológicas
(arquitetura, banco de dados, hospedagem) e o método de validação adotado.

**O Capítulo 4** apresenta os resultados em três blocos: a digitalização
da folha (Camada 0), as funcionalidades de visualização e análise
(Camada 1) e os algoritmos de sugestão automática (Camada 2). Métricas
quantitativas e qualitativas são apresentadas para cada bloco.

**O Capítulo 5** discute criticamente os resultados, contrastando as
sugestões automáticas com as decisões reais da Gestão, identificando os
gaps de modelagem (especialmente o fenômeno da "não-acomodação" — descrito
no Capítulo 4) e o papel do agente conversacional como mediador entre
modelo formal e julgamento experiente.

**O Capítulo 6** conclui o trabalho, sumariza as contribuições, reconhece
as limitações e aponta trabalhos futuros — entre eles, a integração com
o ERP da empresa (Sigee Cloud), a expansão para módulo de vendas e a
aplicação dos princípios aqui desenvolvidos em outras micro e pequenas
indústrias do setor.

---

## Notas de revisão (Leonardo + orientador)

- **Tom acadêmico:** mantive ABNT formal. Se o orientador preferir mais
  pessoal ("Este trabalho relata..."), avise que adapto.
- **Citações:** usei autores clássicos (Tubino, Slack, Hopp, Chopra,
  Nonaka, Laudon, Corrêa, Forrester) — preciso confirmar quais você já tem
  acesso ou ler. Posso te ajudar a montar uma lista de leituras.
- **`<<PREENCHER>>`:** 2 pontos — centro acadêmico da UFCG na capa e
  citação de estudos sobre PCP em PMI na seção 1.4.
- **Tamanho:** Cap 1 ABNT bem feito tem 5-8 páginas. Este esboço deve dar
  ~6 páginas formatadas. Ajustamos conforme necessidade.
- **Decisões de escopo a discutir:**
  - Incluir o LLM no escopo do TCC ou tratar como "trabalho futuro"?
    (Recomendo incluir — é o diferencial competitivo do trabalho.)
  - Mencionar Doces Vó Nena pelo nome ou usar "uma confeitaria industrial
    no estado de São Paulo"? (ABNT permite os dois, depende da preferência
    do orientador e da empresa.)
