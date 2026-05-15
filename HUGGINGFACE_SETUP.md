# 🤗 Guia passo-a-passo: deployar o PCP Vó Nena no Hugging Face Spaces

> **Pra quem é este guia:** Leonardo (leigo em DevOps).
> **Objetivo:** colocar o app rodando em `huggingface.co/spaces/...` **sem** mexer no Streamlit Cloud que já está no ar.
> **Tempo estimado:** 30-45 min na primeira vez.
> **Risco:** zero pra produção atual — Streamlit Cloud continua rodando o tempo todo.

---

## Antes de começar

Você precisa ter:

- [x] Conta no GitHub (já tem — `leonardosoglia/pcp-vo-nena`)
- [x] Conta no Supabase (já tem)
- [x] Git instalado no PC (já tem)
- [ ] **Conta no Hugging Face** ← passo 1 abaixo
- [ ] **URL do banco Supabase em mãos** (a mesma DATABASE_URL que tá no Streamlit Cloud)

Pra recuperar a `DATABASE_URL`:
1. Abre `https://share.streamlit.io/` e faz login
2. Clica no app `pcp-vo-nena`
3. Botão "⋮" > **Settings** > aba **Secrets**
4. Copia o valor de `DATABASE_URL` (começa com `postgresql://`)
5. Guarda essa string num lugar seguro (Notepad temporário) — vai precisar no passo 4.

---

## Passo 1 — Criar conta no Hugging Face

1. Abre **`https://huggingface.co/join`** no navegador
2. Clica em **"Sign up with Google"** (mais rápido) ou usa email/senha
3. Escolhe um username — sugestão: **`leonardosoglia`** (mesmo do GitHub, pra ficar consistente)
4. Confirma o email se pedir
5. ✅ Conta criada

**Dica:** o HF tem perfil público. Tudo bem deixar — Spaces de portfolio é bem-vindo na comunidade. Mas o Space em si pode ser privado, vamos ver no passo 2.

---

## Passo 2 — Criar o Space

1. Logado no HF, clica no botão **"+"** no canto superior direito > **"New Space"**
   (ou abre direto: **`https://huggingface.co/new-space`**)

2. Preenche o formulário:
   - **Owner:** seu username (leonardosoglia)
   - **Space name:** `pcp-vo-nena` (igual ao repo GitHub, pra ficar fácil)
   - **License:** `mit` (padrão liberal, pode trocar depois)
   - **Select the Space SDK:** clica em **"Docker"** → depois em **"Blank"** (template vazio)

     > ⚠️ Importante: **NÃO escolhe "Streamlit"** (ele força versão antiga 1.25). Escolhe **Docker** porque nosso `Dockerfile` já controla tudo.

   - **Space hardware:** `CPU basic - 2 vCPU - 16GB - FREE` (já vem selecionado)
   - **Visibility:** seleciona **"Public"** por enquanto (mais fácil pra testar; pode trocar pra privado depois)

3. Clica em **"Create Space"**

4. ✅ Você cai numa página tipo `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena` com um README de boas-vindas vazio.

**Não se assusta** — o Space tá ainda vazio. A gente vai mandar nosso código nele agora.

---

## Passo 3 — Configurar o secret DATABASE_URL no Space

Antes de mandar o código, configura o banco. Senão o app vai dar erro ao subir.

1. Na página do seu Space, clica na aba **"Settings"** (canto direito, em cima)

2. Rola até a seção **"Variables and secrets"**

3. Clica em **"New secret"** (botão verde)

4. Preenche:
   - **Name:** `DATABASE_URL` (exatamente assim, em MAIÚSCULAS)
   - **Value:** cola aquela string que você copiou do Streamlit Cloud (começa com `postgresql://`)

5. Clica em **"Save"**

6. ✅ Secret salvo. O HF NÃO mostra mais o valor depois de salvar (segurança). Se precisar trocar, deleta e cria de novo.

**Por que "Secret" e não "Variable":**
- **Variable** = público, qualquer um que duplica seu Space consegue ver
- **Secret** = privado, só seu app dentro do Space consegue ler

A `DATABASE_URL` tem senha do banco lá dentro — sempre Secret.

---

## Passo 4 — Conectar o repo local ao HF

Agora vamos dizer pro Git da sua máquina que existe um servidor a mais (além do GitHub) pra onde podemos mandar o código.

1. Abre o **PowerShell** dentro da pasta do projeto:
   ```powershell
   cd "C:\Users\bandr\OneDrive\Documentos\DISCIPLINAS\P10\Estágio\Novo projeto"
   ```

2. Adiciona o HF como um "remote" extra chamado `hf`:
   ```powershell
   git remote add hf https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena
   ```

   > 💡 **O que isso faz:** ensina o Git que `origin` é o GitHub e `hf` é o Hugging Face. Você passa a poder mandar mudanças pra qualquer um dos dois (ou os dois) quando quiser.

3. Confere se ficou certo:
   ```powershell
   git remote -v
   ```

   Você deve ver **2 origens**:
   ```
   hf      https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena (fetch)
   hf      https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena (push)
   origin  https://github.com/leonardosoglia/pcp-vo-nena (fetch)
   origin  https://github.com/leonardosoglia/pcp-vo-nena (push)
   ```

---

## Passo 5 — Gerar token de acesso do HF

O Hugging Face não aceita senha pra push — precisa de um **token** (tipo uma "senha descartável só pra Git").

1. Abre **`https://huggingface.co/settings/tokens`**

2. Clica em **"New token"** (ou **"Create new token"**)

3. Preenche:
   - **Token name:** `pcp-vo-nena-push` (qualquer nome)
   - **Token type:** clica em **"Write"** (precisa ser write, não read)
   - Em **"Repositories permissions"**, marca `Write access to contents/settings of all repos under your personal namespace`

4. Clica em **"Create token"**

5. **COPIA O TOKEN AGORA** — começa com `hf_...` (uns 40 caracteres). O HF só mostra UMA vez. Cola no Notepad temporário.

6. ✅ Token criado.

> ⚠️ Se você perder o token, não tem como recuperar — só criar um novo. Sem stress, é gratuito.

---

## Passo 6 — Primeiro push pro HF Spaces (o deploy de verdade)

Aqui o app efetivamente vai pro ar no HF.

1. No PowerShell, dentro da pasta do projeto, garante que tá tudo commitado:
   ```powershell
   git status
   ```
   Se aparecer "nothing to commit, working tree clean", segue. Senão, me avisa.

2. Manda o branch atual pro HF:
   ```powershell
   git push hf HEAD:main
   ```

3. Vai pedir login:
   - **Username:** `leonardosoglia` (seu username HF)
   - **Password:** **cola o TOKEN** que você criou no passo 5 (NÃO a senha da sua conta — o token `hf_...`)

4. O Git vai mandar todos os commits pro HF. Aparece algo tipo:
   ```
   Writing objects: 100% (456/456), 2.3 MiB
   To https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena
    * [new branch]      HEAD -> main
   ```

5. ✅ Push concluído.

6. Volta pra página do seu Space no navegador (`huggingface.co/spaces/leonardosoglia/pcp-vo-nena`) e atualiza (F5).
   - Você vai ver uma aba **"App"** com status **"Building"** (montando) ou **"Running"** (rodando)
   - Build inicial demora **3-6 minutos** (precisa instalar pandas, plotly, psycopg... tudo do zero)
   - Pode acompanhar em tempo real clicando na aba **"Logs"**

7. Quando o status virar **"Running"** (verde), clica em **"App"** — o app abre dentro de um iframe da HF.

8. ✅ Se você consegue abrir o Lançamento, ver as folhas no Painel, e abrir Insights/Suprimentos: **SUCESSO**.

---

## Passo 7 — O que fazer SE der erro no build

Cenários comuns:

### "ModuleNotFoundError: No module named 'X'"
- Significa que alguma biblioteca não foi instalada
- Verifica se está em `requirements.txt`
- Se sim, refaz `git push hf HEAD:main`

### "could not connect to server" ao abrir o app
- Significa que `DATABASE_URL` não chegou no app
- Volta no Settings > Secrets, confere que `DATABASE_URL` existe com nome em MAIÚSCULAS
- Restart o Space: Settings > **"Factory reboot"**

### Build trava ou demora mais de 15 minutos
- Cancela: Settings > **"Pause Space"**
- Olha os logs pra ver onde travou
- Me chama, mando pra próxima sessão investigar

### "Permission denied" no push
- Você usou a senha da conta HF em vez do token
- Refaz com o token `hf_...`

---

## Passo 8 — Validar em paralelo por uma semana

Durante a próxima semana (16-22/05), use o app **no HF Spaces** no dia a dia:
- URL nova: `https://huggingface.co/spaces/leonardosoglia/pcp-vo-nena`
- URL antiga: `https://pcp-vo-nena.streamlit.app` (ainda funciona — banco é o mesmo)

Anota mentalmente (ou no CADERNO.md):
- HF é mais rápido pra abrir?
- Demora muito pra recarregar quando salva folha?
- Algum botão/interação não funciona como antes?
- O sidebar com lista de datas tá completo?

Se algo der errado, você simplesmente **continua usando o Streamlit Cloud normalmente**. Zero risco.

---

## Passo 9 — Como atualizar o HF depois (rotina)

Quando eu (Claude) ou você fizer mudança no código:

```powershell
# Trabalha no código normalmente, commita
git add .
git commit -m "feat: minha mudança"

# Manda pros DOIS lugares:
git push origin main   # GitHub → Streamlit Cloud rebuilda em 1-2 min
git push hf HEAD:main  # HF Spaces rebuilda em 3-5 min
```

Os dois ambientes vão estar sincronizados.

> 💡 **Truque pra um comando só:** dá pra configurar Git pra fazer os 2 push automaticamente. Quando você quiser, me pede pra configurar.

---

## Passo 10 — Descomissionar o Streamlit Cloud (DEPOIS de validar HF)

**Só fazer isso depois de 5-7 dias com HF Spaces estável.**

1. Acessa `https://share.streamlit.io/`
2. Clica no app `pcp-vo-nena`
3. ⋮ > **Settings** > **Delete app**
4. Confirma

5. Desabilita o keepalive (não precisa mais — HF Spaces dorme em 48h, e você usa direito todo dia):
   - Vai em `https://github.com/leonardosoglia/pcp-vo-nena/actions`
   - Workflow **"Keepalive PCP Vó Nena"** > clica em **"Disable workflow"**

6. ✅ Migração 100% concluída.

> 🛡️ **Plano B — se mudar de ideia:** mesmo depois de deletar o app do Streamlit Cloud, você pode recriar em 5 min (Streamlit Cloud → New app → escolhe `leonardosoglia/pcp-vo-nena` → branch main → arquivo `lancamento.py`). O banco Supabase continua o mesmo. Não é decisão irreversível.

---

## Resumo executivo (cola de cola)

| Etapa | O que faz | Quanto tempo | Risco |
|---|---|---|---|
| 1 | Criar conta HF | 2 min | 0 |
| 2 | Criar Space (Docker) | 3 min | 0 |
| 3 | Adicionar secret DATABASE_URL | 2 min | 0 |
| 4 | `git remote add hf ...` | 1 min | 0 |
| 5 | Gerar token de push | 2 min | 0 |
| 6 | `git push hf HEAD:main` | 5-10 min (build) | 0 |
| 7 | Resolver erro se aparecer | 5-15 min | 0 |
| 8 | Validar 1 semana | em background | 0 |
| 9 | Rotina de update | 30s extras por push | 0 |
| 10 | Deletar Streamlit Cloud (só depois) | 2 min | reversível |

---

## FAQ

**Q: E se eu errar o push e mandar coisa errada pro HF?**
A: Refaz com o conteúdo certo e dá push de novo. HF rebuilda em cima.

**Q: O HF cobra alguma coisa?**
A: Não, o tier `cpu-basic` (2 vCPU + 16 GB) é grátis pra sempre. Só cobra se você fizer upgrade pra GPU ou hardware superior.

**Q: O Supabase aguenta os 2 apps batendo no mesmo banco?**
A: Sim. O Supabase nem percebe — pra ele é tudo a mesma origem de conexão. Free tier suporta 60 conexões simultâneas; cada app usa 2-5.

**Q: Posso fechar o repo no GitHub depois?**
A: SIM, mas perde a integração automática com Streamlit Cloud. Como vamos descomissionar Streamlit Cloud no passo 10, daí pode fechar tranquilo. Mas tem 2 razões pra deixar aberto: (1) história pública pro TCC, (2) facilita Mariana/Eraldo verem o código se quiserem.

**Q: Vou continuar precisando do GitHub Actions keepalive?**
A: Não — HF Spaces no `cpu-basic` só dorme após 48h sem ninguém abrir. Como o Eraldo usa todo dia, nunca dorme.

---

**Quando estiver pronto pra começar, me chama na próxima sessão.** Eu fico ao lado tirando dúvidas em cada passo.
