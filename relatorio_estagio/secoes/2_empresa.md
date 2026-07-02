# 2 CARACTERIZAÇÃO DA EMPRESA

## 2.1 Apresentação

A empresa concedente do meu estágio é a **Pequenas Mordidas Alimentos
Eireli**, conhecida comercialmente como **Doces Vó Nena**, indústria de
alimentos do setor de confeitaria localizada em São Paulo (SP). A operação
fabril ocorre sob a estrutura **Soglia Indústria**. A empresa atua na
fabricação de doces tradicionais brasileiros — cocada, palha italiana, pão
de mel e bala de doce de leite — com distribuição em pontos de venda
próprios (quiosques), atacado e fornecimento a clientes corporativos.

Trata-se de uma operação **semi-industrial**: o processo conserva a base
artesanal das receitas (tachos, viração manual, corte de bandeja), mas já
trabalha em escala e volume típicos de indústria de pequeno porte. No
período em que estagiei, observei que a empresa atravessa uma fase de
crescimento da produção e da comercialização, o que torna a sistematização
do planejamento especialmente oportuna — foi justamente essa lacuna que o
trabalho aqui descrito buscou endereçar.

[[IMG: Foto da fachada e da área de produção da empresa]]

## 2.2 Localização e infraestrutura

A unidade fabril localiza-se no bairro do Ipiranga, em São Paulo (SP), em
imóvel adaptado às necessidades de produção semi-industrial. Durante o
estágio, percorri diariamente o espaço para realizar a contagem de estoque,
e pude mapeá-lo em áreas funcionais distintas:

- **Cozinha/Produção** — tachos, panelas, bancadas de viração e mesa de
  resfriamento das bandejas;
- **Sala de Corte** — bancadas para o fatiamento das bandejas de cocada e
  palha nos formatos finais;
- **Sala de Embalagem** — máquinas de plástico individual e bancadas para a
  aplicação das cintas de papel;
- **Estoque de matéria-prima, semi-acabados e produto acabado**;
- **Área administrativa**.

Essa organização física corresponde, de forma quase direta, ao
encadeamento dos departamentos descrito mais adiante (seção 2.6): o produto
caminha da cozinha para o corte, do corte para a embalagem e da embalagem
para o estoque de produto acabado.

## 2.3 Produtos

A Doces Vó Nena produz **quatro linhas principais** de doces. Ao longo do
estágio, foi necessário compreender cada uma em detalhe — sabores, formatos,
unidades de medida e rendimento —, porque é essa estrutura que o sistema de
PCP precisou representar fielmente. Para consolidar esse conhecimento,
montei um catálogo com **38 fichas de produto**, preenchidas a partir da
leitura das fotos dos produtos e cruzadas com os dados do próprio sistema,
de modo a validar a correspondência entre o que a fábrica produz e o que o
sistema registra.

### 2.3.1 Cocada

Doce tradicional à base de coco ralado, leite e açúcar, é o principal
produto da empresa. É produzido em **seis sabores**: Tradicional, Leite
Condensado, Brigadeiro, Café, Pé de Moça e Zero (sem açúcar). É
comercializado em vários formatos — unidades de 45g, Mini, Pet (cubos),
Pote 260g e Pote 605g —, sendo que **o sabor Zero não possui o formato 45g**.

A cocada segue um fluxo de produção de **três estágios** — tacho, viração e
corte —, com lead time aproximado de **três dias** (potes saem em um dia).
A unidade física de planejamento da cocada é a **bandeja**: cada tacho rende
**8 bandejas** (no sabor Zero, 3), e cada bandeja pesa cerca de **5,5 kg**
quando já pronta para o corte. Vale registrar um achado relevante do
estágio: o **custo de material por quilo varia muito entre os sabores** —
enquanto a Tradicional custa cerca de R$ 5,60/kg, a Zero chega a R$ 25,79/kg,
**aproximadamente 4,6 vezes mais cara**, em razão dos adoçantes especiais e
do menor rendimento. Esse contraste, que detalho nas seções de resultados,
mostra que o sabor mais vendido não é necessariamente o mais lucrativo.

### 2.3.2 Palha italiana

Doce no formato de barra, feito em panela individual com base de leite
condensado, biscoito triturado e ingredientes que variam por sabor. São
**cinco sabores**: Tradicional (chocolate meio amargo), Leite em Pó (Ninho),
Churros (doce de leite e canela), Cookies (Negresco) e Limão (limão taiti).
É comercializada em barras de 50g e em mini-barras no formato Pet. A palha
também tem lead time aproximado de três dias e, por ser produzida em poucos
dias da semana, exige planejamento de corte e de reposição de bandejas
relativamente estável — característica que tornou a palha o produto onde as
sugestões automáticas do sistema atingiram maior aderência.

### 2.3.3 Pão de mel

Bolo assado com cobertura, comercializado em **displays de 10 unidades**. Um
bolo (o lote de produção) rende **70 unidades**, equivalentes a **7 displays**.
Essa dupla unidade — bolo na ordem de produção, display no estoque — foi um
dos pontos que precisei modelar com cuidado no sistema, para evitar
confusão entre o que se planeja produzir e o que se conta na prateleira.

### 2.3.4 Bala de doce de leite

Doce tradicional produzido em tacho, com rendimento de **30 balas por
tacho**. Sua produção compartilha tachos com a cocada e tem ciclo de
reposição mais longo (da ordem de oito dias). A bala opera por reposição de
estoque: quanto menor o estoque na prateleira, mais tachos são programados.

Além dessas quatro linhas, a empresa produz, em menor escala, **doces finos
e cocada assada**, e mantém alguns itens **terceirizados** (produzidos fora)
em seu catálogo de vendas — distinção importante, porque nem tudo o que a
empresa vende é fabricado internamente.

## 2.4 Estrutura organizacional

Para descrever a operação de forma profissional e independente das pessoas
que ocupam cada função, adotei ao longo do trabalho uma **nomenclatura de
departamentos**, e não de nomes próprios. A operação organiza-se em **cinco
departamentos** funcionais:

1. **Gestão** — Define as ordens diárias de produção, ajusta os parâmetros
   por sabor e dia da semana, decide prioridades e atende pedidos
   corporativos. É a responsável pelo planejamento tático-operacional. Uma
   constatação central do estágio é que **a decisão de produção é humana**:
   a Gestão decide olhando o estoque de produto acabado, o estoque de
   semi-acabados e a demanda esperada — nenhum sistema decide por ela.

2. **Produção** — Opera tachos e panelas, executa a viração das bandejas de
   cocada, conduz a contagem matinal por sabor e formato (registrada no
   documento que a fábrica chama de "Papelzinho do Joel") e mantém o estoque
   de produtos semi-acabados.

3. **Corte** — Executa o fatiamento das bandejas nos produtos finais,
   conforme as ordens da Gestão e seguindo um calendário de corte (as
   unidades de 45g em todos os dias úteis; os formatos Mini e Pet
   concentrados em dias específicos da semana).

4. **Embalagem** — Atua em duas etapas: a embalagem plástica individual e,
   em seguida, a aplicação da cinta de papel. A capacidade diária é
   variável, dependendo do número de funcionários disponíveis no dia, e a
   prioridade recai sobre o formato 45g.

5. **Suprimentos** — Controla a matéria-prima, os insumos auxiliares, as
   embalagens e os potes. Mantém o relacionamento com fornecedores e executa
   as compras conforme a necessidade.

A identificação formal das pessoas envolvidas no estágio (estagiário,
supervisor na empresa e orientador acadêmico) consta da folha de
identificação deste relatório.

## 2.5 Documentos operacionais

Antes do desenvolvimento do sistema digital descrito neste relatório, todo
o controle operacional era feito em **papel**, por meio de dois documentos
preenchidos diariamente:

- **Folha de Produção** — Documento principal, com quadros (embalados,
  cortados, viradas e a virar) preenchidos manualmente durante a manhã,
  após a contagem física do estoque. Cada folha funciona como um
  **retrato do dia**: registra a situação naquele momento, não um acumulado.

- **Papelzinho do Joel** — Documento auxiliar preenchido pela Produção, com
  a contagem matinal de cada sabor por formato, usado para alimentar os
  quadros da Folha de Produção.

Esses documentos eram arquivados fisicamente após a operação do dia, sem
qualquer agregação em sistema. As decisões diárias eram tomadas com base
neles e na **memória da Gestão** sobre pedidos antecipados e sazonalidade.
Foi exatamente esse ponto — informação valiosa que se perdia no papel e na
memória — que motivou a digitalização: preservar fielmente a estrutura do
documento existente e, a partir dela, abrir caminho para análise e apoio à
decisão.

## 2.6 Fluxo produtivo

De forma simplificada, o fluxo produtivo encadeia os cinco departamentos.
Ele parte do **Suprimentos** (matéria-prima e insumos), segue para a
**Produção** (preparo no tacho ou na panela e, no caso da cocada, a viração
das bandejas), passa pelo **Corte** (que transforma as bandejas nos formatos
finais), avança para a **Embalagem** (plástico individual e, depois, cinta
de papel) e termina na **distribuição** (quiosques, atacado e clientes
corporativos), com o produto acabado mantido em estoque até a venda.

Uma característica importante desse fluxo, que aprendi observando a rotina,
é a existência de **estoques intermediários** em pontos distintos da
cadeia: há o estoque de produto acabado na prateleira, o estoque de
semi-acabados (bandejas viradas, aguardando corte) e o material ainda em
produção. Essa distinção entre **estoque e fluxo** (FORRESTER, 1961) foi um
dos fundamentos conceituais do trabalho e teve impacto direto na forma como
modelei os dados e as análises do sistema.

[[IMG: Fluxograma do processo produtivo — Suprimentos -> Produção -> Corte -> Embalagem -> Distribuição]]

## 2.7 Sistemas de informação existentes

A empresa utiliza o **SIGE Cloud** como ERP, com módulos de Estoque, Vendas e
Notas Fiscais. O SIGE registra o **ciclo de materiais** da operação: a
entrada de matéria-prima pela nota fiscal eletrônica (NF-e/XML) alimenta o
estoque; a Ordem de Produção (OP) consome esse estoque a partir da ficha
técnica do produto; e a finalização da OP registra o rendimento. É, nesse
sentido, a **fonte da verdade contábil e fiscal** dos materiais da empresa.

Entretanto, no início do estágio constatei que **o SIGE não possui um módulo
de Planejamento e Controle da Produção**. Ele registra o que entrou, o que
foi consumido e o que foi vendido, mas não apoia a decisão diária de
**quanto produzir, cortar e embalar de cada sabor e formato** — que é
justamente a rotina em que atuei e o objeto do sistema que desenvolvi. Essa
lacuna é parte central da motivação deste trabalho: o sistema de PCP que
construí (com o apoio do Claude Code, assistente de programação baseado em
inteligência artificial) conversa com o SIGE de forma **somente leitura**,
aproveitando os dados de custo, estoque e vendas que o ERP já possui, sem
substituí-lo nem interferir em seus registros. A descrição dessa integração
e das ferramentas dela derivadas é objeto das seções seguintes.

---
