# Handoff — Integração com Sigee Cloud

> **Pra Claude da próxima sessão:** ler este arquivo INTEIRO antes de qualquer ação.
> Em seguida `CLAUDE.md`, `CADERNO.md` e memórias persistentes em `~/.claude/projects/.../memory/`.
> Sessão atual encerrada em 19/05/2026 com sistema estável em produção (HF Spaces).

---

## TL;DR

Próximo grande módulo: **integrar o sistema PCP Vó Nena com o Sigee Cloud** (ERP da
empresa) pra que o Claude (durante o desenvolvimento + em runtime) tenha acesso
aos **dados reais de insumos, NF, estoque e vendas** já cadastrados lá.

Objetivo final:
- Sistema lê insumos do Sigee → povoa nossa tabela `insumos` automaticamente
- Sistema lê vendas/saídas → desbloqueia análise "produção vs venda real"
- Eraldo + Mariana continuam usando Sigee no fluxo deles, sem retrabalho

---

## 1. O que sabemos sobre o Sigee Cloud (até hoje)

**Quem usa:**
- **Mariana** — compras + controle de estoque de matéria-prima (escritório)
- Eraldo eventualmente

**O que tem cadastrado lá:**
- ✅ **Insumos** (matéria-prima, embalagens, potes, cintas — provavelmente 30-50 itens)
- ✅ **Notas Fiscais** (entrada de compras)
- ✅ **Estoque** (saldo atual por insumo)
- ✅ **Vendas** (provavelmente saídas por cliente/produto/data)
- ✅ **NFE** (emissão fiscal)

**O que NÃO tem:**
- ❌ PCP (planejamento de produção) — é exatamente o que estamos construindo
- ❌ Folhas diárias do tipo "papelzinho do Joel"
- ❌ Capacidades por funcionário, presença diária

**Status técnico (NÃO confirmado):**
- ❓ **API do Sigee Cloud existe?** — Eraldo NÃO sabe. **Pendência crítica pra próxima sessão.**
- ❓ **Documentação pública?** — verificar em `sigeecloud.com.br` ou similar
- ❓ **Login Leonardo permite acesso aos dados?** — verificar

---

## 2. Plano de integração — 3 caminhos possíveis

### 🟢 Caminho A — CSV manual (mais simples, destrava primeiro)

**Como funciona:**
- Mariana exporta lista de insumos do Sigee em CSV/Excel (provavelmente botão "Exportar" no painel dela)
- Leonardo recebe o arquivo
- Script Python `importar_csv_sigee.py` lê e povoa nossa tabela `insumos`
- Repete periódicamente (1x/semana? 1x/mês?) pra manter sincronizado

**Vantagens:**
- ✅ Independe de API
- ✅ Mariana faz em 5 min
- ✅ Funciona AGORA, sem esperar Sigee liberar nada

**Desvantagens:**
- ❌ Não tempo-real (delay entre Sigee atualizar e nosso sistema saber)
- ❌ Trabalho manual recorrente da Mariana

**Esforço dev:** ~3h (script de importação + validação de schema)

### 🟡 Caminho B — API REST/GraphQL do Sigee (se existir)

**Como funciona:**
- Sigee oferece endpoint tipo `GET /api/insumos`
- Sistema faz polling periódico (ou webhook se suportar)
- Cache local pra evitar request a cada query

**Vantagens:**
- ✅ Tempo quase real
- ✅ Sem trabalho manual
- ✅ Bidirecional (podemos baixar consumo via POST quando salvar folha)

**Desvantagens:**
- ❌ Depende de documentação Sigee (e da existência da API)
- ❌ Pode ter limite de requests / custo
- ❌ Possível complexidade de autenticação (OAuth2, API key, etc.)

**Esforço dev:** 8-20h dependendo da qualidade da doc Sigee.

### 🔴 Caminho C — Sigee VIRA nosso ERP, mantemos PCP separado (longo prazo, pós-TCC)

**Como funciona:**
- Sigee continua sendo a fonte da verdade pra NF/Vendas/Estoque
- Nosso sistema fica sendo a fonte da verdade pra PCP (folha de produção)
- Conciliação periódica via export/import bidirecional

**Quando faz sentido:**
- Quando o PCP Vó Nena estiver em produção há 6+ meses
- Quando a fábrica decidir oficialmente "essas são as 2 ferramentas"

**Esforço dev:** muito (4-8 semanas). **NÃO é prioridade pro TCC.**

---

## 3. Recomendação — sequência da próxima sessão

### Passo 1 — Investigação (Leonardo + Claude) — ~1h

1. Leonardo abre `console.sigeecloud.com.br` (ou URL real) e tira print de:
   - Painel principal
   - Aba "Insumos" / "Produtos" / "Cadastros"
   - Aba "Vendas" / "Saídas"
   - Aba "Configurações" / "Integrações" / "API"
   - Aba "Exportar" / "Relatórios"
2. Claude da próxima sessão analisa prints e decide:
   - Tem API? → Caminho B
   - Tem export CSV mas sem API? → Caminho A
   - Nada disso? → Negociar com Mariana

### Passo 2 — Implementação do Caminho A (CSV) — ~3h

Independente da existência de API, **vale fazer o Caminho A primeiro** pra destravar
o cadastro de insumos do TCC.

**Plano:**

1. **Mariana exporta CSV** do Sigee com a lista de insumos. Pedir colunas:
   - `codigo` (SKU)
   - `nome`
   - `unidade` (kg, L, und, cx)
   - `estoque_atual`
   - `estoque_minimo` (se tiver)
   - `fornecedor` (principal)
   - `custo_unitario`
   - `categoria` (matéria-prima / embalagem / pote / etc.)
   - `lead_time_dias` (se tiver)

2. **Claude cria** `importar_csv_sigee.py`:
   - Lê CSV (encoding UTF-8 ou ISO-8859-1 — verificar)
   - Mapeia colunas Sigee → nossa schema `insumos`
   - Detecta inserts vs updates por `codigo`
   - Reporta totais (X inseridos, Y atualizados, Z não-mapeados)
   - Dry-run mode

3. **Leonardo executa** localmente uma vez. Valida no Supabase Studio.

4. **Próximas atualizações:** Mariana envia novo CSV → Leonardo roda script.

### Passo 3 — Investigar API (paralelo, sem bloquear) — ~30 min

Claude da próxima sessão:
- Tenta `GET https://api.sigeecloud.com.br/v1/produtos` (chute baseado em convenção)
- Procura em `sigeecloud.com.br/docs` ou `sigeecloud.com.br/api`
- Se achar: documenta endpoint + autenticação. Implementação fica pra outra sessão.
- Se não achar: aceita Caminho A como definitivo.

### Passo 4 — Setup acesso do Claude ao Sigee (opcional) — ~1h

Pra Claude da próxima sessão TER ACESSO direto ao Sigee:

**Opção 1 — Compartilhar credenciais via secret:**
- Leonardo cria usuário "claude-readonly" no Sigee (se Sigee permitir)
- Credentials viram secret `SIGEE_USERNAME` + `SIGEE_PASSWORD` no HF
- Script Python faz scraping/API

**Opção 2 — Leonardo é a ponte:**
- Claude pede screenshots / dados
- Leonardo manda
- Mais seguro, menos automático

Sugestão: **começar com Opção 2**. Migra pra 1 se ficar repetitivo.

---

## 4. Estado atual do projeto (19/05/2026)

### Em produção
- **App:** `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena` (HF Spaces, Docker)
- **Backup:** `https://pcp-vo-nena.streamlit.app` (Streamlit Cloud — pendente desativar)
- **Banco:** Supabase Postgres `pcp-vo-nena-us` (us-east-1), 338 linhas migradas
- **Banco antigo (sa-east-1):** ainda existe, **pausar próxima semana**

### Páginas no sistema (após esta sessão)
1. **Lançamento** (`lancamento.py`) — entry point, formulário da folha
2. **Painel** (`pages/1_Painel.py`) — visualização por departamento
3. **Insights** (`pages/2_Insights.py`) — diagnóstico operacional (regras hardcoded)
4. **Suprimentos** (`pages/3_Suprimentos.py`) — insumos + BOM + necessidades **(aguarda Sigee!)**
5. **Curva ABC** (`pages/4_Curva_ABC.py`) — Pareto dos produtos
6. **Anomalias ML** (`pages/5_Anomalias_ML.py`) — Isolation Forest + Claude explica
7. **Calibração de Metas** (`pages/6_Media_Movel.py`) — meta vs realidade
8. **Assistente IA** (`pages/7_Assistente_IA.py`) — Claude Q&A (sem ANTHROPIC_API_KEY ativada)
9. **Equipe** (`pages/8_Equipe.py`) — funcionários + capacidades + presença
10. **Ajuda** (`pages/9_Ajuda.py`) — central de documentação/glossário/FAQ

### Tema visual
- **Fonte:** Inter (não mais Sora)
- **Paleta:** clean — laranja Vó Nena apenas como accent (#C05621)
- **CSS centralizado** em `ui_theme.py` — cada página chama `aplicar_tema()`
- **Emojis reduzidos** nos st.title (Leonardo: "não é site de brincadeira")

### Folha de produção
- **Campos vazios** em vez de "0" pré-preenchido (decisão UX 19/05)
- **TAB** navega entre campos (padrão Streamlit)
- **Setas do teclado** ainda incrementam valor (limitação Streamlit nativo).
  Pra próxima sessão considerar trocar `st.number_input` por `st.text_input`
  com validação numérica.

---

## 5. Pendências críticas (em ordem)

### Bloqueadores
- [ ] **Bloco 4 questionário Eraldo** (lista insumos com fornecedor/lead time) — sem isso, Etapa C não anda
- [ ] **Capacidades funcionários** (Gil 30 band/dia, Paulo Y, Joel Z tachos) — entrevista presencial
- [ ] **Confirmar 15kg leite condensado por tacho** (parece muito, validar) — Eraldo
- [ ] **Receitas de Palha** (Bloco 5 não respondido) — Eraldo
- [ ] **Mariana topa exportar CSV do Sigee?** — Leonardo pergunta

### Importantes mas não-bloqueantes
- [ ] Pausar Supabase antigo (sa-east-1) após 2 semanas validando o novo
- [ ] Deletar app Streamlit Cloud + desabilitar GitHub Actions keepalive
- [ ] Verificar se Sigee tem API (após sessão Sigee começar)
- [ ] Trocar `st.number_input` por `st.text_input` pra setas funcionarem como navegação
- [ ] Bloco 7 questionário (frequência PM, dias palha, capacidade Joel)

### Limpeza / débito técnico
- [ ] Deprecation warnings `use_container_width` — substituir por `width="stretch"` (10 ocorrências)
- [ ] Validar que page numbering ainda faz sentido (1-9 — não há gap)

---

## 6. Como acessar o sistema (pra próxima sessão saber)

### Produção
- **URL:** `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena`
- **Status:** Running (verificar badge no canto superior)

### Repositório
- **GitHub:** `https://github.com/leonardosoglia/pcp-vo-nena` (público)
- **Branch principal:** `main`
- **HF:** mesmo repo, push pro remote `hf`

### Comando pra empurrar mudanças
```powershell
cd "C:\Users\bandr\OneDrive\Documentos\DISCIPLINAS\P10\Estágio\Novo projeto"
git push origin HEAD:main  # GitHub → Streamlit Cloud rebuilda
git push hf HEAD:main      # HF Spaces rebuilda
```

### Credenciais (NUNCA no chat, sempre no Notepad privado)
- `DATABASE_URL` (Supabase us-east-1) — Secret no HF + secret no Streamlit Cloud
- `ANTHROPIC_API_KEY` — pendente, código aceita mas Leonardo decidiu não ativar agora
- Banco antigo (Supabase sa-east-1) — `pcp-vo-nena`, pausar próxima semana

### Logs
- HF: aba `Container` no Space (depois do build)
- Streamlit Cloud: dashboard `share.streamlit.io` → app → "Manage" → logs

---

## 7. Primeira mensagem da próxima sessão

Quando Leonardo abrir sessão nova, **ele deve:**

1. Mandar: *"Continua de onde paramos. Vamos integrar com o Sigee Cloud."*
2. Trazer (se já tiver):
   - Print do painel do Sigee Cloud
   - Resposta da Mariana sobre exportar CSV
   - Bloco 4 do questionário Eraldo (lista de insumos)

**Você (Claude) deve:**

1. Ler **este arquivo INTEIRO** primeiro
2. Ler `CLAUDE.md` (referência técnica)
3. Ler `CADERNO.md` (diário do projeto)
4. Ler memórias persistentes relevantes (`project_migracao_hf_spaces.md`, `project_fase1_ml_completa.md`, `project_pessoa_mariana_e_sigee.md`)
5. Resumir em 5 linhas o estado + perguntar "Vamos pelo Caminho A (CSV) ou tentar B (API) primeiro?"

---

## 8. O que NÃO esquecer (regras da casa)

- **PT-BR informal direto.** Sem floreios.
- **Postura técnica.** Especialista em PCP + software, defende decisões.
- **Antes de codar:** identificar inconsistências com o fluxo real da fábrica.
- **Código:** sempre completo, sem placeholders.
- **Memória persistente:** salvar descobertas críticas em `~/.claude/projects/.../memory/`.
- **Decisões arquiteturais:** explicar o porquê (vira capítulo do TCC).
- **Eraldo decide:** sistema sugere/visualiza/alerta, NUNCA comanda.
- **Estoque vs Fluxo (Forrester):** nunca somar emb_* entre dias. Usar ord_corte_*/ord_emb_*.
- **Senhas em prints:** se vazar, revogar e gerar outro.

---

**Boa sorte na sessão Sigee. Quando rolar, o projeto destrava DE NOVO.**

— Claude Opus 4.7, sessão 19/05/2026
