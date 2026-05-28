# Como obter as credenciais da API do SIGE Cloud

> Passo bloqueante pra ligar o PCP direto no SIGE (modelo read-only).
> Sem essas 3 credenciais, o cliente `sige_cloud_api.py` não roda.
> Criado em 27/05/2026.

## O que precisamos

A API do SIGE Cloud exige **3 dados de autenticação** em toda requisição:

| Header | O que é |
|---|---|
| `Authorization-Token` | Token único da conta |
| `User` | E-mail do administrador da conta SIGE |
| `App` | Nome do aplicativo registrado |

Esses 3 dados só o suporte do SIGE fornece — não dá pra gerar sozinho no painel.

## Quem pede

A **Suprimentos** (responsável pela conta SIGE da empresa), porque o pedido
tem que sair **do e-mail do administrador da conta**. O suporte não atende
pedido de terceiro.

## Como pedir (texto pronto pra copiar no e-mail)

- **Para:** suporte@sigecloud.com.br
- **Assunto:** Solicitação de dados de autenticação API SIGE Cloud

> Olá, somos a Pequenas Mordidas Alimentos (Doces Vó Nena). Gostaríamos de
> obter os dados de autenticação da API de Integração (Authorization-Token,
> User e App) para uma integração de leitura com nosso sistema interno de
> planejamento de produção (PCP). Vamos apenas **consultar** o cadastro de
> produtos e o saldo de estoque — não vamos alterar nada no SIGE. Podem nos
> enviar as credenciais e a documentação da API? Obrigado.

Canais alternativos: painel https://atendimento.sigecloud.com.br · 0800 591 8755.

## Quando a resposta chegar

Guardar os 3 valores **fora do Git** (nunca commitar). Duas opções:

### Local (no computador do dev)
No arquivo `.streamlit/secrets.toml` (já está no `.gitignore`):
```toml
SIGE_AUTH_TOKEN = "valor-que-o-suporte-mandou"
SIGE_USER = "email-admin@empresa.com"
SIGE_APP = "nome-do-app"
SIGE_DEPOSITO_PADRAO = "Padrão"   # ajustar pro nome real do depósito no SIGE
```

### Produção (Hugging Face Spaces)
Settings → Variables and secrets → adicionar os mesmos 4 nomes como **Secrets**.

## Como testar depois

Com as credenciais no ambiente:
```powershell
$env:PYTHONIOENCODING="utf-8"
python -c "import sige_cloud_api as s; print(s.testar_conexao())"
```
Esperado: `{'ok': True, 'mensagem': 'Conexão OK ...', 'amostra': 1}`.

## Próximo passo (depois que conectar)

1. Confirmar o **nome exato do depósito** no SIGE (campo `deposito` é obrigatório
   na consulta de saldo).
2. Rodar `pesquisar_produtos(categoria="PRODUÇÃO")` e `categoria="EMBALAGEM"` pra
   ver o formato real da resposta (os nomes dos campos podem variar do que o
   Swagger sugere).
3. Criar `importar_sige_api.py` — espelho do `importar_csv_sigee.py`, mas puxando
   da API em vez do CSV. Mapeia produto do SIGE → insumo do PCP.
4. Adicionar um botão "Sincronizar com SIGE" na página Suprimentos.

## Lembrete de escopo (decisão de arquitetura)

O cliente está em **modo read-only** de propósito (modelo B — CADERNO Bloco 6).
As funções de escrita existem mas estão travadas por `SIGE_PERMITIR_ESCRITA`.
**Não habilitar** sem alinhar com a Suprimentos: o estoque oficial é dela, e o
PCP não deve escrever nele automaticamente.
