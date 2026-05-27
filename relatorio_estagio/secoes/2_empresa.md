# 2 CARACTERIZAÇÃO DA EMPRESA

> Esboço inicial. Procurar `<<PREENCHER>>` pra pontos a confirmar com a empresa.

---

## 2.1 Apresentação

A **Pequenas Mordidas Alimentos Eireli**, com nome fantasia **Doces Vó
Nena**, é uma indústria de alimentos do setor de confeitaria, localizada
em São Paulo (SP). A empresa atua na fabricação de doces tradicionais
brasileiros, com distribuição em pontos de venda próprios (quiosques) e
fornecimento a clientes corporativos e eventos.

`<<PREENCHER história resumida: ano de fundação, fundadores, marcos
principais. Pedir pra Mariana ou pra Gestão um histórico rápido.>>`

## 2.2 Localização e infraestrutura

A unidade fabril localiza-se em `<<endereço/bairro de São Paulo>>`, em
imóvel adaptado às necessidades de produção semi-industrial. O espaço é
organizado em áreas funcionais distintas:

- **Cozinha/Produção** — tachos, panelas, bancadas de viração e mesa de
  resfriamento
- **Sala de Corte** — bancadas para fatiamento das bandejas de cocada e
  palha
- **Sala de Embalagem** — máquinas de plástico individual e bancadas
  para cintas de papel
- **Estoque de matéria-prima e produto acabado**
- **Área administrativa**

## 2.3 Produtos

A Doces Vó Nena produz quatro linhas principais:

### 2.3.1 Cocada
Doce tradicional à base de coco ralado, leite e açúcar. Produzido em
**seis sabores**: Tradicional, Leite Condensado, Brigadeiro, Café, Pé de
Moça e Zero (sem açúcar). Comercializado em cinco formatos: unidades de
45g, Mini (30g), Pet (cubinhos de 30 unidades por bandeja), Pote 260g e
Pote 605g. A produção segue fluxo de três estágios — tacho, viração e
corte — com lead time aproximado de três dias.

### 2.3.2 Palha italiana
Doce no formato barra, feito em panela individual com base de leite
condensado, biscoito triturado e ingredientes variáveis por sabor. Cinco
sabores: Tradicional (chocolate meio amargo), Leite em Pó (Ninho),
Churros (doce de leite e canela), Cookies (Negresco) e Limão (limão
taiti). Comercializado em barras de 50g e mini-barras Pet.

### 2.3.3 Pão de mel
Bolo assado com cobertura, comercializado em displays de 10 unidades.
Um bolo (lote de produção) rende 70 unidades, equivalentes a 7 displays.

### 2.3.4 Bala de doce de leite
Doce tradicional produzido em tacho, com rendimento de 30 balas por lote.
Inclui aplicação de sorbato (anti-mofo) e gordura vegetal.

A empresa também produz, em menor escala, doces finos e cocada assada.

## 2.4 Estrutura organizacional

A operação é organizada em **cinco departamentos** funcionais:

1. **Gestão** — Define ordens diárias de produção, ajusta parâmetros por
   sabor e dia da semana, decide prioridades e atende pedidos corporativos.
   Responsável pelo planejamento tático-operacional.

2. **Produção** — Opera tachos e panelas, executa viração de bandejas de
   cocada, conduz a contagem matinal de estoque (registrada no "Papelzinho
   do Joel") e mantém o estoque de produtos semi-acabados.

3. **Corte** — Executa o fatiamento das bandejas em produtos finais
   conforme as ordens da Gestão, seguindo o calendário de corte
   (45g em todos os dias úteis; Mini concentrado em terça, quarta e
   sexta; Pet em terça e sexta).

4. **Embalagem** — Atua em duas etapas: embalagem plástica individual e
   aplicação de cinta de papel. A capacidade diária é variável,
   dependendo do número de funcionários disponíveis.

5. **Suprimentos** — Controla matéria-prima, insumos auxiliares,
   embalagens e potes. Mantém o relacionamento com fornecedores e
   executa as compras conforme necessidade.

## 2.5 Documentos operacionais

Antes do desenvolvimento do sistema digital descrito neste relatório, o
controle operacional era realizado por meio de dois documentos físicos
preenchidos diariamente:

- **Folha de Produção** — Documento principal, contendo quatro quadros
  (Embalados, Cortados, Viradas, Pra Virar) preenchidos manualmente
  durante a manhã, após a contagem física de estoque.

- **Papelzinho do Joel** — Documento auxiliar preenchido pela Produção,
  contendo a contagem matinal de cada sabor por formato.

Esses documentos eram arquivados fisicamente após a operação do dia, sem
agregação em sistema digital. As decisões diárias eram tomadas com base
nesses documentos e na memória da Gestão sobre pedidos antecipados e
sazonalidade.

## 2.6 Fluxo produtivo simplificado

```
            +----------------+
            |   Suprimentos   |
            +-------+--------+
                    |
                    v
         +--------------------+
         |     Produção       |  (tacho → viração)
         +---------+----------+
                    |
                    v
         +--------------------+
         |       Corte        |  (bandeja → 45g/Mini/Pet/Pote)
         +---------+----------+
                    |
                    v
         +--------------------+
         |     Embalagem      |  (plástico + cinta)
         +---------+----------+
                    |
                    v
         +--------------------+
         |     Distribuição    |  (quiosques + corporativo)
         +--------------------+
```

`<<SUBSTITUIR esse fluxograma textual por uma imagem profissional no
.docx final — gero com Plotly/Mermaid>>`

## 2.7 Sistemas de informação existentes

A empresa utiliza o **Sigee Cloud** como ERP, com módulos de Estoque,
Vendas e Notas Fiscais. O sistema **não possui módulo de PCP** — limitação
que constitui parte da motivação do trabalho aqui descrito.

---

## Notas pra completar

- Pedir pra Gestão/Mariana: histórico da empresa, ano de fundação, número
  de funcionários, faturamento (se for divulgável)
- Tirar foto da fachada e da área produtiva pra anexar
- Pegar organograma oficial, se houver
- Confirmar nome jurídico exato (Pequenas Mordidas Alimentos Eireli)
  no contrato social ou no CNPJ
