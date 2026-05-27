# 4 RESULTADOS

> Esboço estrutural — coração do TCC (capítulo mais longo, ~25-35 páginas).
> Conteúdo a ser desenvolvido na semana 17–23/06.

## 4.1 Camada 0 — Digitalização

### 4.1.1 Schema de banco de dados
- 13 tabelas principais (folha_cocada, folha_palha, papelzinho_joel, pmbd, etc.)
- Tabelas de referência (metas, conversões, P/Virar ideal)
- Decisões: chave (data, sabor); snapshot não acumulativo; derivados não persistidos

### 4.1.2 Formulário de lançamento
- Espelhamento dos quadros do papel
- Renderização inversa (Joel antes da coluna oficial)
- Cálculo de derivados em tempo real (Cortados②③, Viradas②)

### 4.1.3 Métrica
- Tempo médio pra preencher uma folha: `<<X>>` min (medir)
- Reduções vs. tempo no papel: estimar com a Gestão

## 4.2 Camada 1 — Visualização e análise

### 4.2.1 Painel da fábrica
- Tabela diária + KPIs

### 4.2.2 Curva ABC
- Implementação corrigida (fluxo, não estoque — princípio de Forrester)
- Resultado: T domina; L, B, C, P, Z em ranking decrescente

### 4.2.3 Detecção de anomalia (Isolation Forest)
- Features de estoque + features de fluxo
- Casos detectados: 04/05 (palha LP), 06/05 (palha LP), 04/05 cocada T

### 4.2.4 Média móvel — calibração de metas
- Comparação meta-base × Cortados² médio
- Mapa de calor por sabor × dia da semana
- Recalibração proposta automaticamente

### 4.2.5 Insights — diagnóstico automático
- 6 achados clássicos (Insight Master, tachos parciais, etc.)
- Recalibração: Eraldo NÃO confirma desbalanceamento → viés de amostra pequena

## 4.3 Camada 2 — Sugestão automática

### 4.3.1 Palha — MRP semanal manual
- Algoritmo: corte = necessidade líquida; produção = order-up-to
- Calibração: quadro Normal vs. Conservador (threshold 0.81 no Pet, piso 60 und no 50g)
- Validação: 04/05, 11/05, 18/05, 25/05, 27/05 — aderência ~85%

### 4.3.2 Cocada — diária, multi-formato
- v1: param − Cortados²
- v2: + potes 260g/605g
- v3: + capacidade priorizada (T > L > demais) + sobra do tacho parcial → potes + viração calculada
- v4: + painel histórico (mediana das últimas N folhas do mesmo dia)
- Aderência: ~50-70% (limites identificados na seção 4.5)

## 4.4 Camada 3 — Agente cognitivo (LLM)

### 4.4.1 Arquitetura
- Claude Haiku 4.5 + Sonnet 4.6 + Opus 4 (seletor de modelo)
- System prompt rico (regras de negócio + departamentos)
- Contexto da folha do dia + 7 dias de histórico

### 4.4.2 Otimização de custo
- Prompt caching (`cache_control`): ~90% de redução
- Custo médio: R$0,03 (Haiku), R$0,10 (Sonnet), R$0,30 (Opus)

### 4.4.3 Funcionalidades
- Streaming de resposta (efeito ChatGPT)
- Sugestões contextuais (perguntas baseadas no estado da folha)
- Slash commands (/resumo, /anomalias, /comparar, /sugerir, /faltas, /historico)
- Tool use — Claude consulta o banco direto (7 ferramentas)

### 4.4.4 Casos de uso documentados
- Resumo executivo da folha do dia
- Comparação inter-semanal automática
- Investigação de déficits específicos
- Análise estratégica multi-camada (com Opus)

## 4.5 Suprimentos — MRP simplificado

### 4.5.1 Cadastro de insumos (Etapa C)
- 33 matérias-primas + embalagem
- Origem: receitas oficiais + entrevista com a Gestão

### 4.5.2 BOM cadastrada (Etapa D)
- 91 linhas de BOM para 12 produtos
- 6 cocadas (por tacho), 5 palhas (por bandeja), pão de mel (por bolo), bala (por tacho)
- Mistura padrão somada ao leite

### 4.5.3 Cálculo de necessidades do dia
- Folha salva → MRP simplificado → necessidades de matéria-prima
- Bug histórico: palha como tacho corrigido para bandeja

## 4.6 Métricas consolidadas
- Tempo de preenchimento da folha: papel × digital
- Número de folhas registradas: `<<N>>`
- Acertividade da Camada 2 (palha e cocada): por sabor × dia
- Custos do Assistente IA por mês de uso típico
