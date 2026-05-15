# 🤖 ROADMAP IA — PCP Vó Nena

> **Propósito:** plano realista, faseado e honesto pra introduzir Inteligência Artificial e Machine Learning no projeto, alinhado com o cronograma do TCC.
>
> **Princípio central:** **não prometer mágica.** Sistema vai assistir o Eraldo, não substituí-lo. Cada técnica entra quando os dados permitirem.

---

## 0. Visão honesta — leia primeiro

### O que IA / ML **NÃO** faz bem com nossos dados atuais (15 folhas em ~5 semanas)

| Limite | Por quê |
|---|---|
| ❌ Previsão precisa de demanda | Precisa de 6-12 meses pra capturar sazonalidade (Natal, Páscoa, Festa Junina) |
| ❌ Otimizar produção do dia automaticamente | Faltam variáveis: estoque exato de insumos, custo/sabor, demanda por canal de venda |
| ❌ "Aprender a empresa sozinho" | IA aprende padrão estatístico, não contexto humano |
| ❌ Decidir ordens com confiança alta | Sistema sugere; Eraldo aprova/ajusta — sempre |

### O que IA / ML **PODE** fazer **JÁ** com esses dados

| Técnica | Resultado | Esforço |
|---|---|---|
| ✅ Detecção de anomalia estatística | Substitui regra hardcoded "LP > T+30%" por algoritmo que aprende o "normal" | Baixo |
| ✅ Curva ABC de sabores (clustering) | Quem gira muito, médio, pouco — pra priorizar atenção | Baixo |
| ✅ Média móvel por dia da semana | Projeção razoável com 4+ semanas | Baixo |
| ✅ Detecção de tendência (regressão linear) | "Vendas de Brigadeiro subindo nas últimas 2 semanas" | Baixo |
| ✅ LLM "Pergunte ao Claude" (assistente cognitivo) | Eraldo pergunta em PT-BR, sistema responde com base nos dados dele | Médio |

---

## 1. Filosofia em 4 frases

1. **Toda predição vem com nível de confiança visível.** Nada de "produz 6800 unidades" sem dizer "± 800 com 70% de confiança".
2. **O Eraldo sempre tem a última palavra.** Sistema sugere; ele aprova, ajusta ou ignora.
3. **Transparência > acurácia.** Melhor um modelo simples e explicável que um complexo e opaco.
4. **Métricas reais > vibe.** Antes de "ligar" qualquer técnica, calculamos se ela acerta mais que o método atual.

---

## 2. Fase 1 — Estatística inteligente (Semana 22-29/05, ~6h)

**Objetivo:** substituir regras hardcoded da Camada 1 por técnicas estatísticas que **aprendem** o que é "normal" pra esta fábrica.

### 2.1 Detecção de anomalias com Isolation Forest

**O que substitui:** regra atual "LP > T × 1.3" da H5 (Insights).

**Como funciona em linguagem simples:** algoritmo olha pra todas as folhas, monta a "cara da média", e sinaliza folhas que parecem fora do padrão. **Não precisa dizer pra ele o que é anormal — ele descobre olhando os dados.**

**Vantagens vs regra hardcoded:**
- Detecta anomalia em **qualquer combinação** de campos (não só razão L/T)
- Aprende com novos dados — quanto mais folhas, mais preciso
- Funciona pra cocada, palha, PM e balas com o mesmo código

**Onde plugar:** página Insights, substituindo H5. Mantém H5 como fallback até validar.

**Capítulo TCC:** "Detecção não-supervisionada de anomalia operacional".

### 2.2 Curva ABC de sabores (clustering K-Means)

**O que substitui:** lista visual de sabores sem priorização.

**Como funciona:** algoritmo separa os sabores em 3 grupos automáticos:
- **A** (alto giro): merece atenção diária, prioridade na produção
- **B** (médio giro): cadência semanal
- **C** (baixo giro): tolera ficar fora 1-2 dias

**Já existe um esboço em `analise.py`** — vamos formalizar.

**Onde plugar:** nova aba "Curva ABC" no Painel ou Insights.

**Capítulo TCC:** "Aplicação da curva ABC clássica de gestão de estoques em produção contínua".

### 2.3 Média móvel ponderada por dia da semana

**O que substitui:** parâmetros fixos da tabela `metas_45g` (T=5200 seg, T=4400 ter, ...).

**Como funciona:** pega as últimas 4 segundas e tira média ponderada (mais peso pras mais recentes). Compara com a meta atual da tabela. Se desviar muito, mostra "talvez recalibrar".

**Onde plugar:** novo Insight "H7 — Parâmetros desviando da realidade observada".

**Capítulo TCC:** "Calibração contínua de parâmetros via média móvel exponencial".

---

## 3. Fase 2 — ML supervisionado leve (Semana 29/05-04/06, ~10h)

**Pré-requisito:** ter pelo menos **8 semanas** de folhas (provavelmente atingido em junho).

### 3.1 Projeção de demanda com regressão linear simples

**Objetivo:** dado dia da semana + sabor + últimas 4 semanas, projetar produção esperada.

**Por que regressão linear (e não rede neural):**
- Funciona com pouco dado
- 100% explicável (Eraldo vê os pesos: "+15% se for segunda, +0.8 × estoque de ontem")
- Vira gráfico claro pro TCC
- Rede neural com 30 folhas overfita brutalmente

**Onde plugar:** aba "Sugestão" no Painel — sistema mostra projeção como **referência**, não comando.

**Capítulo TCC:** "Modelagem preditiva clássica para PCP em ambiente de poucos dados".

### 3.2 Detecção de tendência

**Objetivo:** alertar "Brigadeiro subindo +12% nas últimas 3 semanas — considerar elevar parâmetro?"

**Como:** regressão linear simples sobre cada sabor, slope significativo → alerta.

**Onde plugar:** Insights página, novo card "Tendências detectadas".

---

## 4. Fase 3 — LLM como assistente cognitivo (Semana 04-12/06, ~4h)

**Objetivo:** botão "🤖 Pergunte ao Claude" em cada página, que responde em PT-BR usando o contexto atual.

### 4.1 Como funciona

1. Eraldo abre o Painel, vê algo estranho.
2. Clica em "🤖 Pergunte ao Claude".
3. Modal abre com input: *"Por que o sistema está sugerindo cortar 20 bandejas hoje?"*
4. Sistema monta um prompt com:
   - Folha do dia inteira (cocada + palha + PM + balas)
   - Folhas dos últimos 7 dias
   - Achados de Insights ativos
   - Regras de negócio do CLAUDE.md (resumo)
   - Pergunta do Eraldo
5. Envia pra **Claude Haiku 4.5** via API (rápido + barato).
6. Resposta volta em 2-4 segundos.

### 4.2 Casos de uso reais

| Pergunta do Eraldo | Tipo de resposta |
|---|---|
| "Por que está sugerindo 20 bandejas de T?" | Explica a fórmula + dados que entraram |
| "Onde perdi mais venda este mês?" | Faz a conta de Cortados ③ negativo por sabor |
| "Qual sabor parece estar virando crônico?" | Detecta tendência negativa |
| "Quanto leite vou precisar comprar essa semana?" | Soma BOM × ordens projetadas |
| "Por que o sistema marcou hoje como anomalia?" | Explica regra/feature do Isolation Forest |

### 4.3 Custos reais

- **Claude Haiku 4.5:** ~U$0,80 por milhão de tokens de entrada / ~U$4 por milhão de saída
- **Estimativa por consulta:** 3-5 mil tokens entrada + 500 saída = **~R$0,02 a R$0,05 por pergunta**
- **Uso típico estimado:** 5-10 perguntas/dia → **R$0,10 a R$1,50 por mês**
- **Quem paga:** decisão sua (Leonardo) — usa cartão pessoal nos primeiros meses, depois discute com Eraldo se vira despesa da Vó Nena.

### 4.4 Caching pra economizar

- A "memória da empresa" (CLAUDE.md + regras + última semana de folhas) é **cacheável**.
- Claude API tem **prompt caching** — paga 90% mais barato em tokens repetidos entre consultas.
- Economia estimada: 60-80% pra uso frequente.

### 4.5 Onde guardar a API key

- **Streamlit Cloud / HF Spaces:** Secret chamado `ANTHROPIC_API_KEY`
- **Local (dev):** variável de ambiente no PowerShell ou arquivo `.env` no `.gitignore`
- **NUNCA no código.**

### 4.6 Capítulo TCC

**"Integração com Large Language Models como camada cognitiva em sistemas PCP"** —
diferencial forte do trabalho. Mostra maturidade técnica + visão prática.

---

## 5. Cronograma alinhado com o TCC

| Semana | Trabalho IA | Trabalho TCC | Status |
|---|---|---|---|
| 16-22/05 | — | Migrar HF Spaces + receber respostas Eraldo | Em curso |
| 22-29/05 | **Fase 1** (Isolation Forest + ABC + Média móvel) | Cap 4 — Implementação | A executar |
| 29/05-04/06 | **Fase 2** (Regressão + Tendência) | Cap 4 continuação | A executar |
| 04-12/06 | **Fase 3** (LLM "Pergunte ao Claude") | Cap 4 final | A executar |
| 12-30/06 | Polimento + métricas | Cap 5 — Resultados | A executar |
| 30/06-15/07 | (vazio) | Cap 1, 2, 3, 6 + ensaios de defesa | A executar |
| ~18/07 | **DEFESA** | — | — |

---

## 6. O que **não** prometer pro Leonardo, Eraldo ou banca

| Promessa proibida | Por quê |
|---|---|
| "Sistema vai aprender sozinho" | Aprende com dados, demora meses |
| "Vai prever exato o que produzir" | Sugere com banda de confiança; humano decide |
| "Vai eliminar o trabalho do Eraldo" | Amplifica capacidade dele, não substitui |
| "IA é o futuro do PCP da Vó Nena" | Pode ser, mas vamos provar com métrica antes |
| "Modelo tem 95% de acurácia" | Sem 3+ meses de dados de validação, não dá pra afirmar |

---

## 7. Métricas pra mostrar no Cap 5 do TCC

Pra cada técnica IA, **medir contra o método atual** (regra hardcoded ou parâmetro fixo):

| Técnica | Métrica de comparação | Como medir |
|---|---|---|
| Isolation Forest | Anomalias detectadas vs falsos alarmes | Eraldo classifica 20 anomalias detectadas: "real" ou "falso alarme"; calcula precisão |
| Curva ABC | Tempo de decisão do Eraldo | Cronometrar antes/depois |
| Média móvel | Erro absoluto vs parâmetro fixo | Compara `\|projeção − produção real\|` |
| Regressão | RMSE vs baseline (média histórica) | Cross-validation com 80/20 |
| LLM | Satisfação do Eraldo (escala 1-5) + tempo de resposta | Survey informal após 2 semanas |

**Resultado esperado pro TCC:**
> "A introdução de detecção de anomalia não-supervisionada reduziu falsos alarmes em X%, e o módulo de assistente cognitivo via LLM economizou em média Y minutos por consulta do gestor."

---

## 8. Pré-requisitos por fase (o que precisa estar pronto antes)

### Fase 1
- [x] App em produção (Streamlit Cloud OU HF Spaces)
- [x] Banco com 10+ folhas
- [ ] Adicionar `scikit-learn>=1.5` em `requirements.txt`
- [ ] Validar que cabe na RAM do HF Spaces (vai caber — pequeno)

### Fase 2
- [ ] 8+ semanas de folhas (junho)
- [ ] Tabela `metas_45g` com histórico de mudanças (criar `param_real_historico`)
- [ ] Eraldo aceitando "sugestão" como conceito (validar em entrevista)

### Fase 3
- [ ] Conta na Anthropic Console: https://console.anthropic.com
- [ ] Cartão de crédito cadastrado (mesmo que uso seja R$1/mês)
- [ ] API key gerada e em `ANTHROPIC_API_KEY` secret
- [ ] Adicionar `anthropic>=0.40` em `requirements.txt`
- [ ] Prompt template revisado por mim (Claude) numa sessão dedicada

---

## 9. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Modelo overfita em 15 folhas | Cross-validation + amostra pequena explicitada no TCC como limitação |
| Eraldo desconfia "do robô" | Sistema sempre mostra a explicação ("por que sugeriu isso") |
| Custo LLM cresce inesperado | Cache agressivo + rate limit + dashboard de custos |
| Conexão API falha | Botão "Pergunte ao Claude" tem fallback "modo offline" |
| Resposta LLM erra factualmente | Disclaimer permanente: "verificar com dados antes de agir" |

---

## 10. Pergunta pra próxima sessão decidir

- **Começar Fase 1 antes ou depois das Etapas C/D de Suprimentos?**
  - Resposta provável: **depois**, porque Suprimentos é decisão de domínio + cadastro manual; IA é técnica que cabe em qualquer momento.
- **Fase 3 (LLM) — Claude Haiku ou Claude Sonnet?**
  - Resposta provável: **começar com Haiku** (10× mais barato); migrar pra Sonnet só se respostas faltarem qualidade.
- **Quem treina os modelos da Fase 2?**
  - Resposta: eu (Claude) escrevo o código; você só roda. Sem necessidade de servidor de treino — tudo cabe na própria máquina do Streamlit/HF.

---

**Fim do roadmap.** Discutir + ajustar quando começarmos a Fase 1 (semana 22/05).
