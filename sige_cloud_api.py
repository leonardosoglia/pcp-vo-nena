"""
sige_cloud_api.py — Cliente HTTP do SIGE Cloud (ERP da empresa).

DECISÃO ARQUITETURAL (CADERNO Bloco 6, 27/05/2026 — vai pro TCC):
    Modelo B — READ-ONLY. O PCP LÊ cadastro de produtos e saldo de estoque do
    SIGE Cloud; NÃO escreve de volta. Razão (DDD, bounded contexts):
      - SIGE = fonte da verdade CONTÁBIL (estoque fechado por NF + contagem física).
      - PCP  = fonte da verdade OPERACIONAL (consumo por produção, via Etapa E).
    Manter as duas visões separadas evita conflito de escrita e preserva o
    controle da Suprimentos sobre o número oficial. A conferência é mensal
    (consumo do PCP × NFs do SIGE), e a diferença vira ajuste de inventário.

    As funções de ESCRITA (criar_produto, atualizar_produto, salvar_movimento_estoque)
    existem pra não fechar a porta ao modelo C no futuro, mas ficam DESABILITADAS
    por padrão (SIGE_PERMITIR_ESCRITA != "1"). Ativar exige decisão consciente.

MÓDULO PURO: não importa Streamlit. A UI consome via cached_db (a criar) ou
direto. Scripts CLI podem importar à vontade.

AUTENTICAÇÃO (3 headers em toda requisição — doc oficial SIGE):
    Authorization-Token: <token>
    User:                <email do administrador da conta>
    App:                 <nome do app registrado>

Credenciais lidas do ambiente (nunca hardcoded):
    SIGE_AUTH_TOKEN, SIGE_USER, SIGE_APP
Opcional:
    SIGE_DEPOSITO_PADRAO  — nome do depósito pra consultar saldo (default "Padrão")
    SIGE_PERMITIR_ESCRITA — "1" libera as funções de escrita (default bloqueado)

Como obter credenciais: a Suprimentos envia email do email administrador da conta
pra suporte@sigecloud.com.br com assunto "Solicitação de dados de autenticação
API SIGE Cloud". Ver suprimentos_sigee/03_solicitar_credenciais_api.md.

Endpoints (confirmados no Swagger https://api.sigecloud.com.br/swagger/ui/index
em 27/05/2026 — podem variar por versão; centralizados em ENDPOINTS pra ajuste fácil):
    GET  /request/Produtos/GetAll            — lista paginada de produtos
    GET  /request/Produtos/Pesquisar         — busca por filtros
    GET  /request/Estoque/BuscarQuantidades  — saldo por depósito
    POST /request/Produtos/Criar             — cria produto       (escrita)
    PUT  /request/Produtos/Atualizar         — atualiza produto   (escrita)
    POST /request/ProdutosEstoque/Salvar     — movimenta estoque  (escrita)
"""
from __future__ import annotations

import os
import requests


BASE_URL = "https://api.sigecloud.com.br/request"
TIMEOUT = 20  # segundos — ERP externo, latência variável

ENDPOINTS = {
    # ── Leitura (modelo B — habilitada) ──────────────────────────────────────
    "produtos_listar":    "/Produtos/GetAll",
    "produtos_pesquisar": "/Produtos/Pesquisar",
    "estoque_saldo":      "/Estoque/BuscarQuantidades",
    "depositos_listar":   "/Depositos/GetTodosDepositos",
    "empresas_listar":    "/Empresas/GetTodasEmpresas",
    "op_pesquisar":       "/OrdensProducao/Pesquisar",
    "op_checklist":       "/OrdensProducao/BuscarCheckListQualidade",
    # ── Escrita — só usados se SIGE_PERMITIR_ESCRITA == "1" ───────────────────
    "produtos_criar":     "/Produtos/Criar",
    "produtos_atualizar": "/Produtos/Atualizar",
    "estoque_movimentar": "/ProdutosEstoque/Salvar",
    # Escrita da OP — RAMO PENDENTE (decisão da Gestão). Ver docs/ARQUITETURA_SIGE.md.
    "op_cadastrar":       "/OrdensProducao/Cadastrar",
    "op_finalizar":       "/OrdensProducao/Finalizar",
}


# ── Exceções ─────────────────────────────────────────────────────────────────
class SigeError(Exception):
    """Erro genérico de comunicação/uso da API SIGE."""


class SigeAuthError(SigeError):
    """Credenciais ausentes ou inválidas."""


class SigeWriteBlockedError(SigeError):
    """Tentativa de escrita com SIGE_PERMITIR_ESCRITA desabilitado (modelo B)."""


# ── Configuração / credenciais ───────────────────────────────────────────────
def credenciais_configuradas() -> bool:
    """True se os 3 segredos de auth estão no ambiente. Não valida contra o SIGE."""
    return all(os.getenv(k) for k in ("SIGE_AUTH_TOKEN", "SIGE_USER", "SIGE_APP"))


def escrita_habilitada() -> bool:
    return os.getenv("SIGE_PERMITIR_ESCRITA") == "1"


def deposito_padrao() -> str:
    return os.getenv("SIGE_DEPOSITO_PADRAO") or "Padrão"


def _headers() -> dict:
    token = os.getenv("SIGE_AUTH_TOKEN")
    user = os.getenv("SIGE_USER")
    app = os.getenv("SIGE_APP")
    if not (token and user and app):
        raise SigeAuthError(
            "Credenciais do SIGE Cloud ausentes. Defina as variáveis de ambiente "
            "SIGE_AUTH_TOKEN, SIGE_USER e SIGE_APP. Para obtê-las, a Suprimentos "
            "solicita ao suporte SIGE (suporte@sigecloud.com.br). "
            "Ver suprimentos_sigee/03_solicitar_credenciais_api.md."
        )
    return {
        "Authorization-Token": token,
        "User": user,
        "App": app,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ── Transporte ───────────────────────────────────────────────────────────────
def _request(method: str, endpoint_key: str, *, params: dict | None = None,
             json_body: dict | None = None) -> object:
    """Executa a chamada HTTP e devolve o JSON decodificado.

    Levanta SigeAuthError (401/403/sem credencial) ou SigeError (demais falhas),
    sempre com mensagem legível — nunca vaza stacktrace de requests pra UI.
    """
    url = BASE_URL + ENDPOINTS[endpoint_key]
    try:
        resp = requests.request(
            method, url, headers=_headers(),
            params=params, json=json_body, timeout=TIMEOUT,
        )
    except requests.Timeout:
        raise SigeError(f"SIGE não respondeu em {TIMEOUT}s ({endpoint_key}). Tente de novo.")
    except requests.RequestException as e:
        raise SigeError(f"Falha de rede ao chamar o SIGE ({endpoint_key}): {e}")

    if resp.status_code in (401, 403):
        raise SigeAuthError(
            f"SIGE recusou as credenciais (HTTP {resp.status_code}). "
            "Confira SIGE_AUTH_TOKEN / SIGE_USER / SIGE_APP."
        )
    if resp.status_code >= 400:
        # SIGE devolve descrição do erro no corpo; inclui o início pra diagnóstico.
        corpo = (resp.text or "")[:300]
        raise SigeError(f"SIGE retornou HTTP {resp.status_code} em {endpoint_key}: {corpo}")

    if not resp.content:
        return None
    try:
        return resp.json()
    except ValueError:
        raise SigeError(f"SIGE devolveu resposta não-JSON em {endpoint_key}: {resp.text[:200]}")


# ── Leitura (modelo B — habilitada) ──────────────────────────────────────────
def listar_produtos(page_size: int = 100, skip: int = 0) -> list[dict]:
    """Lista paginada de produtos do SIGE. Use page_size/skip pra paginar.
    Retorna a lista crua de dicts do SIGE — o mapeamento pra `insumos` do PCP
    fica em importar_sige_api.py (a criar), não aqui."""
    data = _request("GET", "produtos_listar", params={"pageSize": page_size, "skip": skip})
    return _extrair_lista(data)


def listar_todos_produtos(page_size: int = 200, max_paginas: int = 50) -> list[dict]:
    """Pagina automaticamente até esgotar (ou bater max_paginas, trava de segurança).
    Útil pra um sync completo do catálogo."""
    todos: list[dict] = []
    for pagina in range(max_paginas):
        lote = listar_produtos(page_size=page_size, skip=pagina * page_size)
        if not lote:
            break
        todos.extend(lote)
        if len(lote) < page_size:
            break  # última página
    return todos


def pesquisar_produtos(*, codigo: str | None = None, nome: str | None = None,
                       categoria: str | None = None, marca: str | None = None,
                       ativo: bool | None = None, page_size: int = 50,
                       skip: int = 0) -> list[dict]:
    """Busca produtos por filtros. Todos opcionais; combina os que forem passados.
    Pra povoar o PCP, o filtro mais útil é categoria='PRODUÇÃO' / 'EMBALAGEM'
    (ver memória project_pessoa_mariana_e_sigee — só essas categorias interessam)."""
    params: dict = {"pageSize": page_size, "skip": skip}
    if codigo is not None:
        params["codigo"] = codigo
    if nome is not None:
        params["nome"] = nome
    if categoria is not None:
        params["categoria"] = categoria
    if marca is not None:
        params["marca"] = marca
    if ativo is not None:
        params["ativo"] = str(ativo).lower()
    data = _request("GET", "produtos_pesquisar", params=params)
    return _extrair_lista(data)


def buscar_saldo_estoque(deposito: str | None = None,
                         visivel_catalogo: bool | None = None) -> list[dict]:
    """Saldo de estoque por depósito. `deposito` é obrigatório no SIGE — se não
    passado, usa SIGE_DEPOSITO_PADRAO (ou 'Padrão')."""
    params: dict = {"deposito": deposito or deposito_padrao()}
    if visivel_catalogo is not None:
        params["visivelCatalogo"] = str(visivel_catalogo).lower()
    data = _request("GET", "estoque_saldo", params=params)
    return _extrair_lista(data)


def buscar_estoque_deposito(deposito: str | None = None) -> list[dict]:
    """Saldo por produto NUM depósito específico (READ-ONLY). Devolve a lista de
    itens `{ProdutoCodigo, EstoqueAtual, SaldoReservado}` do depósito informado.
    `SaldoReservado` = pré-reserva das OPs (some da necessidade de compra).

    A MATÉRIA-PRIMA da fábrica vive no depósito **"FABRICA"** (confirmado 14/06):
    os demais depósitos são lojas (produto acabado). Use isto na reconciliação,
    não o EstoqueSaldo consolidado do GetAll (que dá número diferente)."""
    dep = deposito or deposito_padrao()
    data = _request("GET", "estoque_saldo", params={"deposito": dep})
    if isinstance(data, dict):
        itens = data.get("EstoqueItens") or data.get("Itens")
        if isinstance(itens, list):
            return itens
    return _extrair_lista(data)


def listar_depositos() -> list[dict]:
    """Lista os depósitos (almoxarifados) do SIGE. Campos: ID, Nome, EmpresaID,
    Empresa. Use o Nome certo em buscar_saldo_estoque/SIGE_DEPOSITO_PADRAO."""
    data = _request("GET", "depositos_listar")
    return _extrair_lista(data)


def listar_empresas() -> list[dict]:
    """Lista as empresas (CNPJs) da conta SIGE. Campos: ID, NomeFantasia,
    RazaoSocial, CNPJ. Uma credencial cobre todos os CNPJs."""
    data = _request("GET", "empresas_listar")
    return _extrair_lista(data)


def pesquisar_ordens_producao(*, codigo: int | None = None,
                              codigo_pedido: int | None = None,
                              situacao: str | None = None,
                              status: str | None = None,
                              filtrar_por: str | None = None,
                              data_inicial: str | None = None,
                              data_final: str | None = None,
                              page_size: int = 50, skip: int = 0) -> list[dict]:
    """Lê ordens de produção (READ-ONLY). Cada OP (OrdemProducaoRetorno) traz:
    Codigo, Situacao, Deposito, Produtos[] (SKU/Quantidade/Lote/AtributosGrade),
    PrevisaoInicio/Termino, DataInicio/Termino, ValidadeLote, responsáveis,
    CheckList[] e Historicos[]. O RENDIMENTO real e o descarte saem da avaliação/
    finalização (QuantidadeProduzida vs planejada).

    Datas no formato YYYY-MM-DD; pra filtrar por período passe filtrar_por='Data'.
    NOTA: hoje o módulo de produção do SIGE ainda não tem OPs cadastradas — o
    endpoint responde, mas devolve lista vazia. Fica pronto pra quando a fábrica
    começar a lançar OPs (ver docs/ARQUITETURA_SIGE.md)."""
    params: dict = {"pageSize": page_size, "skip": skip}
    if codigo is not None:
        params["codigo"] = codigo
    if codigo_pedido is not None:
        params["codigoPedido"] = codigo_pedido
    if situacao is not None:
        params["situacao"] = situacao
    if status is not None:
        params["status"] = status
    if filtrar_por is not None:
        params["filtrarPor"] = filtrar_por
    if data_inicial is not None:
        params["dataInicial"] = data_inicial
    if data_final is not None:
        params["dataFinal"] = data_final
    data = _request("GET", "op_pesquisar", params=params)
    return _extrair_lista(data)


def listar_todas_ordens_producao(data_inicial: str | None = None,
                                 data_final: str | None = None,
                                 page_size: int = 100,
                                 max_paginas: int = 50) -> list[dict]:
    """Pagina todas as OPs (opcionalmente por intervalo de datas). Trava de
    segurança em max_paginas."""
    todas: list[dict] = []
    usa_data = bool(data_inicial or data_final)
    for pagina in range(max_paginas):
        lote = pesquisar_ordens_producao(
            filtrar_por=("Data" if usa_data else None),
            data_inicial=data_inicial, data_final=data_final,
            page_size=page_size, skip=pagina * page_size)
        if not lote:
            break
        todas.extend(lote)
        if len(lote) < page_size:
            break
    return todas


def buscar_checklist_qualidade(codigo_op: int) -> object:
    """Checklist de qualidade de uma OP específica (READ-ONLY)."""
    return _request("GET", "op_checklist", params={"codigo": codigo_op})


# ── Escrita (modelo C — BLOQUEADA por padrão) ────────────────────────────────
def _exigir_escrita():
    if not escrita_habilitada():
        raise SigeWriteBlockedError(
            "Escrita no SIGE está desabilitada (modelo read-only — decisão "
            "arquitetural, CADERNO Bloco 6). Pra habilitar conscientemente, "
            "defina SIGE_PERMITIR_ESCRITA=1. Pense bem: isso acopla o PCP ao "
            "estoque contábil da Suprimentos."
        )


def criar_produto(produto: dict) -> object:
    """Cria produto no SIGE. Campos esperados: Categoria, Marca, Codigo, Nome,
    PrecoCusto, PrecoVenda, EstoqueSaldo, Ativo. BLOQUEADA por padrão."""
    _exigir_escrita()
    return _request("POST", "produtos_criar", json_body=produto)


def atualizar_produto(produto_id: str, produto: dict) -> object:
    """Atualiza produto existente (por id). BLOQUEADA por padrão."""
    _exigir_escrita()
    return _request("PUT", "produtos_atualizar", params={"id": produto_id}, json_body=produto)


def salvar_movimento_estoque(produto_codigo: str, quantidade: float,
                             eh_entrada: bool, deposito: str | None = None) -> object:
    """Registra entrada/saída de estoque no SIGE.
    Body: {ProdutoCodigo, DepositoNome, Quantidade, EhEntrada}. BLOQUEADA por padrão.

    NOTA: este seria o ponto de two-way sync (Etapa E → SIGE). NÃO ativar sem
    alinhar com a Suprimentos — ela é a dona do estoque oficial."""
    _exigir_escrita()
    body = {
        "ProdutoCodigo": produto_codigo,
        "DepositoNome": deposito or deposito_padrao(),
        "Quantidade": float(quantidade),
        "EhEntrada": bool(eh_entrada),
    }
    return _request("POST", "estoque_movimentar", json_body=body)


# ── Ordem de Produção: RAMO DE ESCRITA PENDENTE (decisão da Gestão) ───────────
# A OP é o ponto de ligação PCP↔SIGE. As pessoas (Gestão + planejamento) decidem
# a produção; isso vira uma OP no SIGE. COMO a OP entra está EM ABERTO:
#   (a) lançada manualmente por uma pessoa a partir do nosso plano  -> read-only;
#   (b) escrita pelo nosso sistema via estas funções                -> único ponto
#       de escrita.
# Decisão pendente com a Gestão (ver docs/ARQUITETURA_SIGE.md). Estas funções
# ficam ISOLADAS e DESLIGADAS de propósito: não montam o corpo nem chamam a API.
def cadastrar_ordem_producao(ordem: dict) -> object:
    """[PENDENTE — NÃO ATIVAR] Cadastraria uma OP no SIGE (POST /OrdensProducao/
    Cadastrar) a partir do plano do PCP. Seria o ÚNICO ponto de escrita no SIGE.
    Bloqueada por SIGE_PERMITIR_ESCRITA E não implementada — aguarda a decisão da
    Gestão sobre OP manual vs via API."""
    _exigir_escrita()
    raise NotImplementedError(
        "Escrita da OP no SIGE é decisão pendente da Gestão (OP manual vs via API). "
        "Ramo isolado e não implementado de propósito. Ver docs/ARQUITETURA_SIGE.md."
    )


def finalizar_ordem_producao(codigo_op: int, avaliacao: dict) -> object:
    """[PENDENTE — NÃO ATIVAR] Finalizaria a OP com o rendimento real (POST
    /OrdensProducao/Finalizar). Mesma regra: bloqueada e não implementada até a
    decisão da Gestão."""
    _exigir_escrita()
    raise NotImplementedError(
        "Finalização de OP é escrita no SIGE — pendente da decisão da Gestão. "
        "Ramo isolado e não implementado. Ver docs/ARQUITETURA_SIGE.md."
    )


# ── Diagnóstico ──────────────────────────────────────────────────────────────
def testar_conexao() -> dict:
    """Smoke test de conectividade + auth. Não escreve nada.

    Retorna dict: {ok: bool, mensagem: str, amostra: int}.
    Nunca levanta exceção — captura tudo pra UI mostrar status amigável.
    """
    if not credenciais_configuradas():
        return {
            "ok": False,
            "mensagem": "Credenciais não configuradas (SIGE_AUTH_TOKEN/USER/APP).",
            "amostra": 0,
        }
    try:
        produtos = listar_produtos(page_size=1, skip=0)
        return {
            "ok": True,
            "mensagem": "Conexão OK — autenticação aceita pelo SIGE.",
            "amostra": len(produtos),
        }
    except SigeError as e:
        return {"ok": False, "mensagem": str(e), "amostra": 0}


# ── Helpers internos ─────────────────────────────────────────────────────────
def _extrair_lista(data: object) -> list[dict]:
    """Normaliza a resposta do SIGE pra sempre devolver uma lista de dicts.

    O SIGE pode devolver a coleção direto (`[...]`) ou embrulhada num envelope
    (`{"Data": [...]}` / `{"Result": [...]}` / `{"Itens": [...]}`). Sem credencial
    real ainda não sabemos qual — então cobrimos os formatos comuns e, na dúvida,
    devolvemos lista vazia em vez de quebrar. Ajustar quando virmos a resposta real.
    """
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for chave in ("Data", "data", "Result", "result", "Itens", "Items", "Produtos", "EstoqueItens"):
            valor = data.get(chave)
            if isinstance(valor, list):
                return valor
        # dict único (1 produto) — embrulha em lista
        return [data]
    return []
