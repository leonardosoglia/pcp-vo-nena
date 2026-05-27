# Inventário Completo de Pendências (27/05/2026)

> Varredura sistemática dos handoffs (HANDOFF_COMPLETO, HANDOFF_SIGEE,
> PROXIMA_SESSAO) + CADERNO.md + memórias persistentes.
>
> Justificativa: o Leonardo apontou que eu (Claude) não me lembrei
> espontaneamente do "esperando acesso ao Sigee voltar". Esse documento
> existe pra GARANTIR que nada vai se perder.
>
> **Como manter atualizado:** revisitar este arquivo no início de TODA
> nova sessão e marcar o que foi feito (✅). O que aparecer aqui é
> referência viva, não snapshot.

---

## 🔴 CRÍTICAS — bloqueiam outras frentes

| # | Pendência | Origem | Status (27/05) | Bloqueia |
|---|---|---|---|---|
| 1 | **Etapa D no banco de produção (us-east-1)** | HANDOFF roadmap | ⚠ Feito só local (sa-east-1). Falta clicar no botão "Cadastrar BOM completa" na página Admin Seed do HF. | Etapa E |
| 2 | **Etapa C completa — Sigee** | HANDOFF_SIGEE | 🟡 Em andamento. Hoje atualizamos 15 de 33 insumos no banco LOCAL. Faltam: 10 matches Mariana + 8 cadastros novos + estoque atual. | Etapa E |
| 3 | **`secrets.toml` local aponta pro banco antigo** (sa-east-1) | memória `project_migracao_hf_spaces.md` | ⚠ Pendente. Tudo que eu cadastro localmente fica no banco ANTIGO, não na produção. | Validações locais |
| 4 | **Embalagem — última peça das receitas (BOM completa)** | HANDOFF seção 6 🥈 | 🔴 Não feito. Gestão precisa passar consumo de plástico/cinta/pote/display por produto. É a última tabela do questionário `02_suprimentos.docx`. | BOM 100% completa |
| 5 | **Etapa E — Auto-baixa de insumos** | HANDOFF roadmap, PROXIMA_SESSAO | ✅ **Implementada 27/05 (sessão 3).** Backend + UI + script de histórico + smoke test passou. Aguarda Etapa D rodar no banco de produção (pendência #1) pra valer lá. | MRP completo |

---

## 🟡 IMPORTANTES — não bloqueiam, mas precisam acontecer

### Tarefas que dependem do LEONARDO

| # | Tarefa | Origem | Tempo |
|---|---|---|---|
| 6 | Ler `tcc/capitulos/1_introducao.md` e revisar | PROXIMA_SESSAO | 20 min |
| 7 | Ler `relatorio_estagio/secoes/1_introducao.md` e `2_empresa.md` | PROXIMA_SESSAO | 15 min |
| 8 | Conversar com orientador — 2 decisões de escopo (LLM no TCC?, nome da empresa?) + template UFCG | PROXIMA_SESSAO | 1 reunião |
| 9 | Pegar com Gestão/Mariana: CNPJ, endereço completo, datas/CH do estágio | PROXIMA_SESSAO | 1 conversa |
| 10 | Configurar `ANTHROPIC_API_KEY` no HF (semana que vem) | PROXIMA_SESSAO | 10 min |
| 11 | Fotos da fábrica (com permissão) pra anexos | PROXIMA_SESSAO | quando der |

### Tarefas que dependem da MARIANA (Suprimentos)

| # | Tarefa | Origem | Onde |
|---|---|---|---|
| 12 | Confirmar **10 matches múltiplos** do Sigee (leite condensado, creme leite, ninho, doce leite, eritritol, xilitol, canela, farinha, palmiste, café) | hoje | `suprimentos_sigee/01_matches_para_mariana.md` |
| 13 | Decidir 8 insumos **sem match** no Sigee (açúcar cristal, mascavo, achocolatado, essência mel, cravo, amaciante, sal, etiqueta palha) | hoje | idem |
| 14 | Exportar **Embalagens** do Sigee (Categoria = EMBALAGEM) | hoje | `suprimentos_sigee/02_checklist` |
| 15 | Exportar **Relatório de Posição de Estoque** (saldo atual) | hoje | idem |
| 16 | Estimar **estoque_minimo** e **lead_time** por insumo | hoje | idem |

### Tarefas que dependem da GESTÃO

Pendências do questionário inicial (CADERNO seção 3) — várias respondidas mas algumas ainda em aberto:

| # | Pergunta | Origem | Status |
|---|---|---|---|
| 17 | Frequência exata de produção de PM (dias da semana) | CADERNO 3.1 | ❓ pendente |
| 18 | Papelzinho separado pra Bala/PM — formato? | CADERNO 3.1 | parcialmente respondido em 15/05 |
| 19 | Quem produz Doces? | CADERNO 3.1 | ❓ pendente |
| 20 | Capacidade típica da Produção em tachos/dia | CADERNO 3.1 + 1.B | ❓ pendente — bloqueia "capacidade priorizada" da cocada |
| 21 | Capacidade do Corte em bandejas/dia | CADERNO 1.B | ❓ pendente |
| 22 | Capacidade da Embalagem em und/dia (variável — quem está no dia) | CADERNO 1.B | ❓ pendente |
| 23 | Como funcionam encomendas de cliente — afeta param_real? | CADERNO 3.1 | parcialmente respondido (Q2 do Insight Master) |
| 24 | Confirmar 15 kg leite condensado por tacho de Cocada Leite Condensado | CADERNO Bloco 5 | ❓ Parece muito — confirmar |
| 25 | Mistério dos 36 kg Pé de Moça vs 30 potes | CADERNO Bloco 7 | ❓ pendente |
| 26 | Dias exatos de corte de palha | CADERNO 3.1 | parcial |
| 27 | API do Sigee — existe? | CADERNO 1.0 Bloco 6 + HANDOFF_SIGEE | ❓ pendente (Mariana ou Sigee) |

### Pendências TÉCNICAS (eu)

| # | Pendência | Origem | Status |
|---|---|---|---|
| 28 | Cocada v4 — outra abordagem (você pausou em 26/05) | memória `project_gaps_cocada_camada2.md` | ⏸ pausada |
| 29 | Calendário operacional (curto prazo do gap "eventos da semana") | CADERNO seção 1.B gap 4 | 🔴 não iniciado |
| 30 | Campo livre "evento da semana / observação" no input | CADERNO gap 2 | 🔴 não iniciado |
| 31 | Modelagem da "não-acomodação" | CADERNO gap 3 | 🔴 não iniciado |
| 32 | Headcount diário das 3 áreas (Produção, Corte, Embalagem) | CADERNO gap 3 | 🔴 não iniciado |

---

## 🟢 NICE-TO-HAVE — pós-TCC ou se sobrar tempo

| # | Item | Origem |
|---|---|---|
| 33 | Módulo de Vendas (Caminho 1+2 do Leonardo 17/05) | CADERNO 0.3 |
| 34 | Agente "Mariana Digital" (suprimentos automatizado) | memória |
| 35 | Bot WhatsApp pra quiosques | memória |
| 36 | Integração Sigee Cloud completa via API | HANDOFF_SIGEE |
| 37 | Tracking de "perda real" — campo `perdas_und` na folha | CADERNO 4.2 |
| 38 | Validade próxima — rastrear data de cada lote | CADERNO 4.2 |
| 39 | Setup time entre sabores | CADERNO 4.2 |
| 40 | Hora extra por dia — pra calcular custo do gargalo | CADERNO 4.2 |
| 41 | Cumbucas (parte dura do coco) — investigar destino | CADERNO 4.3 |
| 42 | OEE básico | CADERNO 4.3 |

---

## 📚 DOCUMENTAÇÃO

| # | Item | Status |
|---|---|---|
| 43 | TCC Cap 1 — esboço entregue | ✅ Aguarda revisão do Leonardo |
| 44 | TCC Cap 2 (Revisão Literatura) — esboço estrutural | 🟡 Estrutura + plano de buscas pronto |
| 45 | TCC Caps 3-6 — só estrutura | 🟡 Aguarda cap 2 |
| 46 | Relatório de Estágio Seções 1-2 — esboço | ✅ |
| 47 | Relatório Seções 3-5 — só estrutura | 🟡 Aguarda cronograma exato |
| 48 | Apresentações .pptx pra TCC + estágio | 🔴 Não iniciado (faz perto da defesa) |
| 49 | HANDOFF_COMPLETO.md — atualizar | ⚠ Desatualizado desde 24/05. Atualizar quando essa sessão fechar. |
| 50 | HANDOFF_SIGEE.md — atualizar | ⚠ Documenta estado de 21/05 (acesso pausado). Atualizar com o que foi feito hoje. |

---

## 📅 PRAZO CRÍTICO

- **05/06/2026** (~8 dias) — início oficial da escrita do TCC
- **18/07/2026** (~50 dias) — DEFESA

## Recomendação de priorização

**Pra esta sessão (resto):**
1. Aplicar Etapa D no banco de produção (#1) — 30 segundos
2. Documentar essa varredura no HANDOFF_COMPLETO (#49) — assim a próxima sessão não esquece

**Pra você levar pra fábrica essa semana:**
- Pegar dados burocráticos com Mariana (#9, #12, #13, #14, #15, #16)
- Pegar respostas finais com Gestão (#17-#27)
- Conversa com orientador (#8)

**Pra próxima sessão minha (depois da fábrica):**
- Etapa E destravada (#5)
- Embalagens cadastradas (#4)
- TCC Cap 2 — pesquisa web profunda + escrita

---

## Memorando pessoal (pra próximo Claude)

**NUNCA assumir que a sessão anterior fechou tudo.** No início de cada sessão:
1. Ler `INVENTARIO_PENDENCIAS.md` (este arquivo)
2. Ler `HANDOFF_COMPLETO.md` (atualizado)
3. Confirmar com o Leonardo o que mudou desde a última sessão
4. SÓ DEPOIS partir pra ação nova
