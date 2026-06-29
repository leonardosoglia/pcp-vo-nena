# Correções do professor + plano de aplicação (TCC PCP Vó Nena)

Fonte: `PONTOS MUITO FORTES.docx` (feedback do orientador) + `TCC_Final___Hudson.docx`
(modelo de formatação/organização/ABNT a seguir — tema diferente, só a forma).
Recebido/registrado em 28/06/2026.

---

## Pontos fortes (o professor elogiou)
- Tema extremamente atual.
- Grande contribuição prática.
- Excelente domínio técnico.

## O modelo (Hudson) — o que aprender da forma
- Estrutura: Introdução (objetivos Geral/Específicos) · Fundamentação Teórica (com
  subseções) · Metodologia · Resultados e Discussão · Conclusão · Referências.
- **~18 Figuras + Tabelas, com Lista de Figuras** (legenda padrão "Figura N — Título").
  → confirma o recado: TCC tem que ser MUITO ilustrado.
- Fonte Arial; margens ABNT.

---

## Correções pedidas (o que mudar)

1. **Modelo conceitual de pesquisa (o MAIOR problema p/ ele).** Falta um diagrama:
   Problema → Diagnóstico → Digitalização → Banco de dados → MRP → Integração ERP →
   Custos → IA → Resultados. Deve aparecer no fim do Cap. 2 ou início do Cap. 3.
2. **Fluxograma metodológico.** Levantamento → Mapeamento → Modelagem → Implementação
   → Validação → Análise → Conclusões. "Toda banca gosta."
3. **Pouquíssimas figuras.** Incluir: fluxograma do processo produtivo, arquitetura do
   sistema, modelo entidade-relacionamento, fluxo ERP-PCP, telas principais, dashboard,
   curvas ABC, gráficos, heatmaps, arquitetura da IA.
4. **Resultados muito textuais — mais tabelas.** Ex.: (a) Módulo | Desenvolvido | Validado;
   (b) Funcionalidade | Objetivo | Resultado | Impacto; (c) Antes | Depois (tempo de
   preenchimento, consulta, análise, nº de erros).
5. **Falta comparação quantitativa.** Medir: tempo p/ preencher, localizar info, calcular
   necessidade, gerar ordem, identificar estoque, redução de erros (papel × sistema).
6. **Pouca análise estatística.** MAE, MAPE, precisão, recall, F1, matriz de confusão,
   erro médio, desvio padrão, intervalos de confiança (onde aplicável).
7. **Faltam limitações do algoritmo.** Baixa quantidade de dados; sazonalidade; dependência
   do conhecimento do gestor; risco de overfitting; necessidade de recalibração.
8. **Revisão de literatura — acrescentar artigos recentes (2022–2025):** Smart Manufacturing,
   AI in Production Planning, Digital Twins, Industry 5.0, Explainable AI, Decision Support
   Systems. (Hoje predominam clássicos: Tubino, Slack, Corrêa, Martins, Laudon.)
9. **Metodologia — deixar explícito:** tipo de pesquisa, população, amostra, instrumentos,
   variáveis, procedimento, análise dos dados (hoje estão distribuídos).
10. **Resultados — estruturar cada um:** Figura → Descrição → Discussão → Comparação com a
    literatura. Quebrar blocos longos de texto.
11. **Discussão — comparar mais com outros autores** ("Fulano (2020) encontrou… neste
    trabalho… a diferença pode ser explicada por…").
12. **Conclusão — quadro final:** Objetivo específico | Resultado alcançado | Evidência.
13. **Referências — verificar:** DOI dos artigos; ABNT NBR 6023:2018; URLs + data de acesso;
    uniformidade de autores/títulos.
14. **Marcadores `<<PREENCHER>>`** (nº de folhas; datas/sabores das anomalias; datas das
    folhas-controle) → substituir pelos dados finais.
15. **Reduzir a 1ª pessoa** ("desenvolvi", "observei", "vejo", "considero") → redação
    impessoal (no TCC; o relatório de estágio continua em 1ª pessoa).

---

## Plano de aplicação — POR PARTES (uma de cada vez, validando cada uma)

> Legenda: **[aqui]** = feito no Claude Code · **[você]** = depende de você (dados/prints)
> · **[aqui→você aprova]** = eu faço e você valida.

- **Parte 1 — Os dois fluxogramas-chave.** [aqui→você aprova] (correções 1 e 2)
  Modelo conceitual da pesquisa (fim Cap. 2/início Cap. 3) + fluxograma metodológico (Cap. 3).
- **Parte 2 — Metodologia explícita.** [aqui] (correção 9)
  Tipo de pesquisa, população, amostra, instrumentos, variáveis, procedimento, análise.
- **Parte 3 — Resultados em tabelas + comparação quantitativa.** [aqui + você os números] (4, 5, 10)
  As 3 tabelas; quebrar texto; estruturar Figura→Descrição→Discussão→Comparação. Os tempos
  antes/depois precisam de medição/estimativa sua.
- **Parte 4 — Estatística da IA + limitações do algoritmo.** [aqui] (6, 7)
  Indicadores onde fazem sentido (erro/MAPE da Média Móvel = calculável; ser honesto que o
  Isolation Forest é não-supervisionado) + limitações.
- **Parte 5 — Discussão (comparar autores) + Conclusão (quadro final).** [aqui + busca de refs] (11, 12)
- **Parte 6 — Literatura recente + referências ABNT.** [aqui busca/formata · você confere] (8, 13)
  Referências REAIS (não inventar) — eu busco, você confere DOI/links.
- **Parte 7 — Figuras restantes + telas + Lista de Figuras.** [aqui desenho · você manda prints] (3)
  Eu desenho: processo produtivo, arquitetura do sistema, entidade-relacionamento, fluxo
  ERP↔PCP, arquitetura da IA. Você manda os prints (dashboard, ABC, heatmaps, telas).
  ✅ **FEITO (29/06):** Opção A escolhida = **12 figuras**. Todos os marcadores `[[IMG:]]` +
  legendas "Figura N — Título" + "Fonte" colocados nos capítulos (Figs 1–12, numeradas por
  ordem de aparição). Lista de Figuras automática montada no gerador (campo que atualiza no
  Word, igual ao Sumário). Word regenerado: `tcc/TCC_PCP_Vo_Nena_2026-06-29.docx`.
  ⚠️ **Ação sua:** trocar o número escrito DENTRO da imagem do diagrama ERP↔PCP de "Figura 6"
  para "Figura 9"; tirar/colar os 6 prints de tela (Figs 6, 7, 8, 10, 11, 12).
- **Parte 8 — Passada final: impessoal + dados + formatação ao modelo + gerar o Word.** [aqui · você dados] (14, 15)

### O que NÃO dá pra fazer 100% aqui
- **Fotos/telas reais** do app e da fábrica → você tira/manda os prints.
- **Acabamento final no Word** (posicionar imagens, quebras de página) → mais rápido você fazer.
- **Dados medidos** (tempos antes/depois) e os `<<PREENCHER>>` → você fornece.
- **Diagramas:** eu desenho a versão (mockup) e geramos a imagem; refino fino pode ser num
  programa de desenho se você quiser.
