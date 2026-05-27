# 3 METODOLOGIA

> Esboço estrutural — conteúdo a ser desenvolvido na semana 10–16/06.

## 3.1 Classificação da pesquisa
- Quanto à natureza: aplicada
- Quanto aos objetivos: descritiva-exploratória
- Quanto à abordagem: quali-quantitativa
- Quanto aos procedimentos: estudo de caso (Yin, 2014)

## 3.2 Levantamento dos processos
- Imersão no chão de fábrica (estágio)
- Análise dos documentos físicos (folha de produção, papelzinho)
- Entrevistas semi-estruturadas com Gestão e Produção
- Questionários estruturados (`entrevistas/01_pcp_inicial.docx` e `02_suprimentos.docx`)

## 3.3 Modelagem de dados
- Mapeamento conceitual: folha em papel → entidades relacionais
- Decisão de manter fidelidade ao papel antes de automatizar
- Versionamento incremental (Schema v1 → v2)

## 3.4 Arquitetura técnica
- Stack: Python 3.14, Streamlit, PostgreSQL (Supabase), pandas, scikit-learn, Plotly
- Hospedagem: Hugging Face Spaces (us-east-1)
- Banco: Postgres us-east-1 com pooler (porta 6543)
- Justificar cada escolha tecnológica

## 3.5 Camadas funcionais — visão geral
- Camada 0: digitalização do papel
- Camada 1: visualização e análise
- Camada 2: sugestão automática
- Camada 3 (proposta): agente cognitivo (LLM)

## 3.6 Validação dos algoritmos
- Comparação com decisões reais da Gestão
- Métrica: aderência por sabor, formato, dia da semana
- Casos-controle: folhas de 04/05, 11/05, 18/05, 25/05, 27/05

## 3.7 Limitações da metodologia
- Amostra pequena (17 folhas)
- Crescimento da fábrica durante a coleta (+200% em 3 semanas)
- Subjetividade nas decisões de Gestão (não 100% modelável)
