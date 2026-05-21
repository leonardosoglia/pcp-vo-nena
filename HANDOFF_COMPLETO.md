# HANDOFF COMPLETO — Encerramento sessão 21/05/2026

> **Pra Claude da próxima sessão:** este é o documento MASTER. Ler INTEIRO antes
> de qualquer ação. Em seguida: `CLAUDE.md` (referência técnica), `HANDOFF_SIGEE.md`
> (plano de integração com o SIGE Cloud), `CADERNO.md` (diário), e as memórias
> persistentes em `~/.claude/projects/C--Users-bandr-.../memory/` (abrir `MEMORY.md`,
> que é o índice).

---

## 🔴 PRIMEIRA AÇÃO NA PRÓXIMA SESSÃO

A sessão encerrou **no meio da extração dos insumos do SIGE Cloud**. Retomar daí.

**Contexto:** o Leonardo está sem acesso às pessoas (Eraldo, Mariana) pra responder
o questionário, mas tem a conta do SIGE Cloud aberta. Estávamos investigando como
extrair a lista de insumos de lá.

**O que já descobrimos do SIGE Cloud (`app.sigecloud.com.br`):**
- O cadastro de **Estoque → Produtos** tem um botão **"Importar/Exportar"** (dentro
  do menu "Mais Ações") — ou seja, **dá pra exportar** os produtos (Excel/CSV).
- O catálogo de produtos é **GRANDE** — tem muito mais coisa que os insumos da
  fábrica. NÃO exportar tudo: filtrar primeiro.
- Existem **categorias de produtos**. As relevantes pro módulo de Suprimentos:
  - **PRODUÇÃO** (provável: ingredientes das receitas — a confirmar)
  - **EMBALAGEM** (embalagens: plástico, cinta, pote, display)
  - **PRODUTOS DE USO FABRICA** (conteúdo desconhecido — perguntar ao Leonardo)
  - As demais (ATIVO, PRODUTOS LOJA, VENDAS LOJAS, Despesas Fixas, etc) NÃO interessam.

**Próximo passo concreto:** pedir ao Leonardo pra, na tela Estoque → Produtos, usar
a **Busca Avançada** e filtrar por **Categoria = PRODUÇÃO**; mandar print. Confirmar
que são os ingredientes. Depois exportar as categorias PRODUÇÃO + EMBALAGEM
(+ talvez PRODUTOS DE USO FABRICA) num arquivo, receber esse arquivo, e criar o
script `importar_csv_sigee.py` pra povoar a tabela `insumos`.

**Lembrar:** Claude NÃO acessa o SIGE (conta privada). O Leonardo é a ponte —
ele clica, manda print, Claude orienta.

---

## 1. ESTADO ATUAL DO SISTEMA (21/05/2026)

### URLs
- **App em produção:** `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena` (HF Spaces, Docker)
- **Repositório:** `https://github.com/leonardosoglia/pcp-vo-nena` (público)
- **Banco:** Supabase Postgres `pcp-vo-nena-us` (região us-east-1)
- Remotes git locais: `origin` (GitHub) e `hf` (Hugging Face). Push vai pros dois.

### Git
- Branch `main`. Todos os commits desta sessão já foram pushed pra `origin` e `hf`.
- Há um stash pendente: `entrevistas-eraldo-respondida-15-05` (arquivos
  `entrevistas/01_pcp_inicial.docx/.pdf` modificados — guardados no início da sessão
  durante o `git pull`; decidir o destino: provavelmente commitar como "respostas
  do Eraldo").

### 10 páginas do sistema
`lancamento.py` (folha) · `pages/1_Painel.py` · `2_Insights.py` · `3_Suprimentos.py` ·
`4_Curva_ABC.py` · `5_Anomalias_ML.py` · `6_Media_Movel.py` · `7_Assistente_IA.py` ·
`8_Equipe.py` · `9_Ajuda.py`.

---

## 2. O QUE FOI FEITO NESTA SESSÃO (20-21/05/2026)

### 2.1 Sincronização e segurança (git)
- `main` local estava 13 commits atrás de `origin/main` — feito fast-forward.
- A credencial `pcp-vo-nena-us.txt` estava SOLTA dentro do repo. Movida pra
  `~/Documentos/credenciais/` (fora do repo) + `.gitignore` ganhou bloco
  "Credenciais". **Atenção:** a senha nesse arquivo está DESATUALIZADA (de antes do
  reset de senha de 19/05) — não serve mais; a senha boa está no painel do Supabase.
- `.gitattributes` (Git LFS pra docx/pdf/xlsx) tinha sido deletado por engano —
  restaurado.

### 2.2 Design — 4 passadas de fonte/tema
**Causa raiz descoberta:** o `ui_theme.py` usava seletores CSS `.main ...`, mas o
Streamlit 1.56 NÃO tem mais a classe `.main` (verificado em runtime: 0 elementos).
Os 123 seletores estavam mortos — por isso reduzir a fonte no código não surtia
efeito. Corrigido: `.main` → `[data-testid="stMain"]`.
- Escala tipográfica modular base 13px: h1 18 / h2 16 / h3 14 / body 13 /
  caption 11 / micro 10. Definida no `ui_theme.py`.
- Coluna "Sabor" da folha alargada; `hdr_cell`/`label_sabor` uniformizados.
- Commits: `196b03c`, `53ab76a`, `159a659`.

### 2.3 Inputs da folha — número cortado
O número aparecia cortado ao digitar. Causas (todas corrigidas):
- Gap padrão do Streamlit entre colunas (16px) desperdiçava espaço — reduzido p/ 0.3rem.
- Os **steppers − +** do `st.number_input` ocupavam espaço — escondidos via CSS.
- O botão **"Clear value" (x)** do `st.number_input` (aparece quando o campo tem
  número) cobria o último dígito — escondido via CSS.
- Commits: `b960a4b`, `0259770`, `3f663b0`.

### 2.4 Performance
Diagnóstico (instrumentação): cada rerun do app levava **~12 s** — setup 2,2 s +
render da folha 9,7 s.
- **`init_db` cacheado** (`be6146e`): rodava ~25 queries no banco a CADA rerun, em
  toda página. Agora roda 1× por processo via `@st.cache_resource` no `cached_db.py`.
- **Folha num `st.form`** (`df1b5e4`): a folha (lancamento.py linhas ~387-1155) foi
  envolvida num `st.form`. Preencher os campos NÃO dispara mais rerun — só o botão
  "Salvar" dispara. Antes: ~12 s por campo. Agora: preencher é instantâneo.
  **Trade-off aceito pelo Leonardo:** os quadros derivados (Cortados ②③, Viradas,
  P/Virar) deixaram de atualizar em tempo real — recalculam ao Salvar.
  O Leonardo testou e confirmou que o Salvar funciona.
- **Pendente:** "abrir uma folha" ainda leva ~12 s (1 render dos ~700 widgets).
  A reforma pra resolver isso ("carregar sob demanda" / lazy render) foi **ADIADA
  pra depois do TCC** — decisão do Leonardo, por ser reforma grande e arriscada na
  reta final.

### 2.5 Módulo de Suprimentos
- **Questionário criado:** `entrevistas/02_suprimentos.docx` (Word, paisagem). 6
  tabelas: receita de cocada (Tradicional pré-preenchida), receita de palha, receita
  de PM, receita de bala, embalagens, lista de insumos. Pendente: o Leonardo abrir
  no Word e conferir o visual (Claude não conseguiu converter pra ver — sem
  LibreOffice no PC).
- **Chaves de BOM refatoradas** (`aba1272`): de por-formato (`cocada_T_45g_band`)
  pra **por-tacho** (`cocada_T_tacho`). A entrevista de 15/05 revelou que a receita
  é por tacho/sabor, não por formato. `chave_produto_cocada/palha` perderam o
  parâmetro `tamanho`; `listar_produtos_possiveis()` foi de 28 → 14 produtos;
  `calcular_necessidades_do_dia()` converte bandejas → tachos (1 tacho = 8 band,
  Zero = 3). Rendimento do tacho de **palha** ficou provisório (8) — confirmar no
  questionário.
- **SIGE Cloud:** exploração iniciada (ver seção "Primeira Ação" acima).

### Commits desta sessão (em ordem)
```
196b03c  ux: compactar fontes (2a passada) + ajustar coluna Sabor
53ab76a  ux: fontes 3a passada — seletores universais + uniformidade
159a659  ux: corrigir tema (bug raiz: seletor .main morto no Streamlit 1.56)
b960a4b  fix(ux): inputs cortavam o numero — gap das colunas + coluna Sabor
0259770  fix(ux): esconder steppers do number_input — caixa de input limpa
3f663b0  fix(ux): esconder tambem o botao "Clear value" do number_input
be6146e  perf: rodar init_db 1x por processo (era ~25 queries a cada rerun)
df1b5e4  perf: envolver a folha num st.form — fim do rerun a cada campo
aba1272  fix(suprimentos): chaves de BOM por tacho, nao por formato
```

---

## 3. PRÓXIMOS PASSOS (priorizados)

### 🥇 Continuar a extração dos insumos do SIGE Cloud
Detalhado na seção "Primeira Ação". Filtrar Produtos por categoria, exportar
PRODUÇÃO + EMBALAGEM, receber o arquivo, criar `importar_csv_sigee.py`.

### 🥈 Coletar respostas do questionário
- O Leonardo leva `entrevistas/02_suprimentos.docx` pro **Eraldo** (receitas) e
  pra **Mariana** (insumos — ou resolver via export do SIGE).
- Pendências antigas que o questionário cobre: receitas de palha; quantidades de
  amendoim (Pé de Moça) e adoçante (Zero); confirmar 15 kg de leite condensado;
  rendimento do tacho de palha.

### 🥉 Etapas C / D / E do roadmap
- **C — Cadastro de insumos:** povoar a tabela `insumos` (via `importar_csv_sigee.py`
  ou cadastro manual).
- **D — BOM (receitas):** cadastrar as receitas na aba Receitas da página
  Suprimentos, usando as chaves por tacho.
- **E — Auto-baixa por produção:** quando a folha é salva, baixar o consumo de
  insumos automaticamente. Integra com `salvar_folha_completa`.

### Refinos pendentes (menores)
- Reforma da folha (lazy render — resolver o "abrir 12 s") — **adiada pós-TCC**.
- Decidir destino do stash `entrevistas-eraldo-respondida-15-05`.
- Atualizar o `CLAUDE.md` (seção 6 cita chaves de BOM antigas `..._band`;
  seção 8 "estado atual" está em 13/05).
- Limpeza técnica: deprecation `use_container_width` → `width="stretch"`; pausar
  Supabase antigo (sa-east-1); desativar app Streamlit Cloud + GitHub Actions
  keepalive.

### 🎓 Escrita do TCC — começa ~05/06/2026 (faltam ~2 semanas)

---

## 4. PROBLEMAS CONHECIDOS / LIMITAÇÕES

- **"Abrir uma folha" leva ~12 s** — 1 render de ~700 widgets. Reforma adiada.
- **`PoolClosed`** — em testes locais, após vários reloads, o pool de conexões
  Postgres fechava (`psycopg_pool.PoolClosed`). Reiniciar o app resolve. Pode
  afetar produção se o HF Space dormir/acordar — investigar `database.py` se o
  Leonardo relatar tela de erro de banco. Não confirmado em produção.
- **Questionário .docx não foi visualizado** — gerado e conferido na estrutura (6
  tabelas), mas Claude não converteu pra imagem (sem LibreOffice no PC do Leonardo).
  Leonardo precisa abrir no Word e validar o visual.

---

## 5. ARQUIVOS-CHAVE

| Arquivo | O que é |
|---|---|
| `database.py` | Schema + CRUD, backend dual SQLite/Postgres. Chaves de BOM por tacho. |
| `cached_db.py` | Wrappers `@st.cache_data`/`@st.cache_resource` sobre database.py. `init_db` cacheado aqui. |
| `ui_theme.py` | Tema visual. Escala modular base 13px. Seletores `[data-testid="stMain"]`. |
| `lancamento.py` | Folha do dia. A folha está dentro de um `st.form`. |
| `pages/3_Suprimentos.py` | Módulo de Suprimentos — 4 abas. Aba Receitas usa chaves por tacho. |
| `entrevistas/02_suprimentos.docx` | Questionário de Suprimentos gerado nesta sessão. |
| `entrevistas/01_pcp_inicial.docx` | Entrevista anterior (parcial). |

---

## 6. DECISÕES IMPORTANTES DESTA SESSÃO

- **Streamlit 1.56 não tem `.main`** — CSS deve mirar `[data-testid="stMain"]`.
- **Folha num `st.form`** — preencher não dispara rerun; derivados atualizam no
  Salvar (não em tempo real). Decisão do Leonardo, ciente do trade-off.
- **Receita é por tacho** — chaves de BOM `cocada_<sigla>_tacho` / `palha_<sigla>_tacho`.
- **Reforma da folha (lazy render) adiada** — não fazer reforma grande na reta do TCC.
- **Comunicação sem jargão** — o Leonardo é engenheiro de produção, não programador.
  Explicar tudo em linguagem simples, pelo efeito visível. Termos de PCP são ok.
- **Validar UI antes de entregar** — medir no DOM renderizado (preview local), não
  chutar. (3 passadas de fonte foram desperdiçadas chutando.)

---

## 7. REGRAS INVARIÁVEIS

1. **PT-BR informal e direto.** Sem floreio. **Sem jargão de programação** com o Leonardo.
2. Especialista técnico em PCP + software sênior. Defender decisões com argumentos.
3. **Eraldo/Gestão decide.** O sistema sugere/visualiza/alerta, nunca comanda.
4. Antes de codar: identificar inconsistências com o fluxo real da fábrica.
5. Código completo, sem placeholders. Pedaços validáveis antes do próximo.
6. Unidades explícitas: und · band · tachos · kg · L · displays · bolos.
7. **Estoque vs Fluxo (Forrester 1961):** nunca somar `emb_*` entre dias.
8. Memória persistente: salvar descobertas críticas em `~/.claude/.../memory/`.
9. Decisões arquiteturais explicam o porquê — viram capítulo do TCC.
10. Senha exposta em print → revogar imediatamente.
11. Zero emoji decorativo no sistema.
12. Validar mudança de UI no app renderizado antes de commitar.

---

## 8. CRONOGRAMA TCC

| Data | O quê |
|---|---|
| 21/05 (hoje) | Sessão encerrada — módulo de Suprimentos / extração SIGE em andamento |
| 22/05 – 04/06 | Extração SIGE + Etapa C (insumos) + D (receitas) + E (auto-baixa) |
| **~05/06** | **Início da escrita do TCC** |
| 05/06 – 25/06 | Capítulos 1-5 + coleta de métricas reais |
| 25/06 – 10/07 | Cap 6 + revisão + ensaios |
| **~18/07/2026** | **DEFESA** |

---

## 9. TEXTO INICIAL PRA COPIAR NA PRÓXIMA SESSÃO

```
Oi, sessão nova do PCP Vó Nena.

Antes de QUALQUER ação, lê na ordem:
1. HANDOFF_COMPLETO.md (raiz do repo) — documento MASTER, estado atual,
   o que foi feito, próximos passos. Tem a "primeira ação" no topo.
2. HANDOFF_SIGEE.md — plano de integração com o SIGE Cloud (atualizado
   com o que descobrimos sobre as categorias e a exportação).
3. CLAUDE.md — referência técnica.
4. CADERNO.md — diário do projeto.
5. Memórias em ~/.claude/projects/.../memory/ — abre MEMORY.md (índice).

Depois me dá um resumo em ~7 linhas:
   (a) Estado atual do sistema
   (b) O que a sessão passada fez (design, performance, Suprimentos)
   (c) Onde paramos: extração dos insumos do SIGE Cloud
   (d) O próximo passo concreto

Contexto pra retomar: eu estou com o SIGE Cloud aberto. Na sessão passada
a gente descobriu que dá pra exportar os produtos e que existem categorias
(PRODUÇÃO, EMBALAGEM, PRODUTOS DE USO FABRICA). O próximo passo era eu
filtrar a lista de Produtos por categoria e te mandar print. Me guia daí.

Lembra: fala comigo em linguagem simples, sem termo técnico de programação.

Manda ver.
```

---

**Fim do handoff. Sessão encerrada em 21/05/2026.**
*Próxima sessão retoma na extração dos insumos do SIGE Cloud.*

— Claude Opus 4.7 (1M context)
