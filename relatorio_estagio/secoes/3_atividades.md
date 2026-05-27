# 3 ATIVIDADES DESENVOLVIDAS

> Estrutura cronológica. Conteúdo a ser detalhado na semana 03–09/06.
> Vai ser o capítulo MAIS LONGO do relatório (~10-15 páginas).

---

## 3.1 Visão geral do período

`<<PREENCHER datas exatas — quando começou, quando terminou>>`

O estágio foi conduzido em fases iterativas. Apresento abaixo cada fase,
suas datas aproximadas, atividades principais e marcos alcançados.

## 3.2 Fase 1 — Imersão e levantamento de processos

**Período:** `<<DATAS>>`
**Carga horária aprox.:** `<<X horas>>`

### Atividades realizadas
- Apresentação aos departamentos da empresa
- Observação do cotidiano de cada departamento (Gestão, Produção, Corte, Embalagem, Suprimentos)
- Acompanhamento do ciclo completo de produção (tacho → viração → corte → embalagem → venda)
- Análise de documentos físicos (folhas de produção arquivadas)
- Entrevistas semi-estruturadas com a Gestão
- Aplicação de questionário estruturado (Anexo `<<X>>`)

### Marcos
- Documento `01_pcp_inicial.docx` preenchido com respostas da Gestão
- Cronologia operacional do dia mapeada (contagem 7h-10h, ordens ~10h, etc.)

## 3.3 Fase 2 — Modelagem e prototipagem

**Período:** `<<DATAS>>`

### Atividades realizadas
- Modelagem conceitual do banco de dados (esquema v1)
- Construção do protótipo inicial em Streamlit
- Primeira validação visual com a Gestão
- Refinamento do schema (v2) após primeiras observações

### Marcos
- Schema do banco com 13 tabelas principais
- Protótipo funcional do formulário de lançamento
- Aprovação da Gestão sobre fidelidade ao papel

## 3.4 Fase 3 — Desenvolvimento e implantação

**Período:** `<<DATAS>>`

### 3.4.1 Camada 0 — Digitalização
- Implementação completa do formulário de lançamento
- Sistema de salvamento atômico (4 tabelas em 1 transação)
- Página de painel com visualização da folha do dia

### 3.4.2 Camada 1 — Visualização e análise
- Curva ABC de sabores (com correção de princípio Estoque vs Fluxo)
- Detecção de anomalias por Isolation Forest
- Média móvel para calibração de metas
- Página de Insights com 6 achados automáticos

### 3.4.3 Camada 2 — Sugestão automática
- Algoritmo de sugestão semanal para palha (calibrado contra decisões reais)
- Algoritmo de sugestão diária para cocada com capacidade priorizada
- Painel histórico complementar à sugestão automática

### 3.4.4 Camada 3 — Apoio cognitivo (LLM)
- Integração com Claude API (Anthropic)
- Streaming, sugestões contextuais, slash commands
- Tool use — consulta direta ao banco via funções
- Seletor de modelo (Haiku/Sonnet/Opus)

### Marcos
- Sistema em produção em Hugging Face Spaces
- Base de dados migrada para Postgres us-east-1
- 11 páginas funcionais no aplicativo

## 3.5 Fase 4 — Iteração contínua

**Período:** `<<DATAS>>`

### Atividades realizadas
- Reuniões semanais (ou diárias) com a Gestão para feedback
- Calibração de algoritmos contra folhas reais lançadas no sistema
- Correção de bugs descobertos pela Gestão durante uso
- Documentação contínua no CADERNO.md

### Marcos
- Cadastro completo de BOM (Lista de Materiais) - 33 insumos + 91 linhas
- Auto-baixa de insumos por produção (em desenvolvimento)
- Etapas do roadmap A-F documentadas

## 3.6 Atividades complementares

- Documentação técnica (CLAUDE.md, CADERNO.md)
- Gravação de histórico de sessões de desenvolvimento
- Levantamento bibliográfico para o TCC
- Preparação de questionários estruturados para entrevistas
- Suporte ao uso diário do sistema pela Gestão

## 3.7 Cronograma resumido

| Mês | Atividade principal |
|---|---|
| `<<MÊS 1>>` | Imersão + entrevistas iniciais |
| `<<MÊS 2>>` | Modelagem + protótipo |
| `<<MÊS 3>>` | Camada 0 + Camada 1 (parcial) |
| `<<MÊS 4>>` | Camada 1 completa + Camada 2 (parcial) |
| `<<MÊS 5>>` | Camada 2 completa + início Camada 3 |
| `<<MÊS 6>>` | Camada 3 + BOM + iteração |
| `<<MÊS 7>>` | Polimento + redação do relatório |

---

## Notas pra completar

- Preencher TODAS as datas com base no termo de estágio + diário no CADERNO
- Adicionar fotos (com permissão) de cada fase
- Capturas de tela do sistema em cada estágio de evolução
- Validar carga horária semanal vs total declarado no termo
