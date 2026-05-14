"""
cached_db.py — Camada de cache sobre database.py para uso em Streamlit.

Mantém database.py 100% puro (sem dependência de Streamlit) — scripts CLI como
`migrar_dados_sqlite_para_postgres.py` continuam podendo importar database.py
sem trazer Streamlit junto.

Os arquivos da UI (`lancamento.py`, `pages/*.py`) trocam:
    from database import get_folha_cocada, ...
por:
    from cached_db import get_folha_cocada, ...

E chamam `invalidar_folha()` após salvar/excluir uma folha pra forçar releitura.

TTLs escolhidos por taxa de mudança real do dado (revisado 14/05/2026 após
feedback de lentidão na produção com latência Atlântico Supabase + manutenção):
    - Tabelas de referência (metas, conversões, estoque): 24h — quase nunca mudam.
    - Folhas e derivados:                                  5 min — mudam quando o
      usuário salva. `invalidar_folha()` força releitura imediata após save/delete,
      então TTL pode ser longo sem prejudicar consistência percebida.
    - Lista de datas (sidebar):                            5 min + invalidação no
      save/delete (muda quando nova folha entra ou sai).

Trade-off do free tier:
    Latência Supabase pelo Atlântico = ~100-300 ms por query.
    Folha do dia carrega ~10-15 queries → ~2-4 s sem cache.
    Com cache hit, ~0 ms.
"""
import streamlit as st
import database as _db

# ── Reexporta constantes do domínio (sem cache, já vivem em memória) ─────────
SABORES_COCADA = _db.SABORES_COCADA
SABORES_PALHA = _db.SABORES_PALHA
SIGLA_COCADA = _db.SIGLA_COCADA
SIGLA_PALHA = _db.SIGLA_PALHA
SABORES_PALHA_50G = _db.SABORES_PALHA_50G

# ── Reexporta operações de escrita / setup (cache não faz sentido) ───────────
init_db = _db.init_db
salvar_folha_completa = _db.salvar_folha_completa
excluir_folha = _db.excluir_folha
duplicar_folha = _db.duplicar_folha
upsert_folha_cocada = _db.upsert_folha_cocada
upsert_folha_palha = _db.upsert_folha_palha
upsert_papelzinho_joel = _db.upsert_papelzinho_joel
upsert_pm_balas_doces = _db.upsert_pm_balas_doces


# ════════════════════════════════════════════════════════════════════════════
# LEITURAS DE FOLHA — TTL curto + invalidação manual no save
# ════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def get_folha_cocada(data):
    return _db.get_folha_cocada(data)


@st.cache_data(ttl=300, show_spinner=False)
def get_folha_palha(data):
    return _db.get_folha_palha(data)


@st.cache_data(ttl=300, show_spinner=False)
def get_papelzinho_joel(data):
    return _db.get_papelzinho_joel(data)


@st.cache_data(ttl=300, show_spinner=False)
def get_pm_balas_doces(data):
    return _db.get_pm_balas_doces(data)


@st.cache_data(ttl=300, show_spinner=False)
def list_datas_folha():
    return _db.list_datas_folha()


@st.cache_data(ttl=300, show_spinner=False)
def calcular_cortados(data):
    return _db.calcular_cortados(data)


@st.cache_data(ttl=300, show_spinner=False)
def calcular_viradas_pvirar(data):
    return _db.calcular_viradas_pvirar(data)


# ════════════════════════════════════════════════════════════════════════════
# TABELAS DE REFERÊNCIA — TTL longo (mudam raramente, via seed/admin)
# ════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=86400, show_spinner=False)
def get_estoque():
    return _db.get_estoque()


@st.cache_data(ttl=86400, show_spinner=False)
def get_metas_45g():
    return _db.get_metas_45g()


@st.cache_data(ttl=86400, show_spinner=False)
def get_metas_mini_pet():
    return _db.get_metas_mini_pet()


@st.cache_data(ttl=86400, show_spinner=False)
def get_metas_potes():
    return _db.get_metas_potes()


@st.cache_data(ttl=86400, show_spinner=False)
def get_pvirar_ideal():
    return _db.get_pvirar_ideal()


@st.cache_data(ttl=86400, show_spinner=False)
def get_conversoes():
    return _db.get_conversoes()


# ════════════════════════════════════════════════════════════════════════════
# INVALIDAÇÃO — chamar após operações de escrita
# ════════════════════════════════════════════════════════════════════════════
def invalidar_folha(data: str | None = None):
    """Invalida o cache das funções dependentes de folha.

    Chamar após `salvar_folha_completa()` ou `excluir_folha()` pra forçar a UI
    a buscar dados frescos no próximo rerun.

    Nota: `st.cache_data.clear()` limpa TODAS as entradas da função (não dá pra
    invalidar uma data específica preservando as outras). Pra workload do PCP
    — onde o usuário toca 1-2 folhas por dia — o custo de re-cachear as datas
    intactas no próximo acesso é desprezível.

    O parâmetro `data` é aceito mas atualmente ignorado (reservado pra futuro
    se a API do Streamlit ganhar `clear(args)` granular).
    """
    get_folha_cocada.clear()
    get_folha_palha.clear()
    get_papelzinho_joel.clear()
    get_pm_balas_doces.clear()
    list_datas_folha.clear()
    calcular_cortados.clear()
    calcular_viradas_pvirar.clear()


def invalidar_referencias():
    """Invalida cache das tabelas de referência. Raramente útil — só se o seed
    for editado manualmente (sem ferramenta de admin no app atual)."""
    get_estoque.clear()
    get_metas_45g.clear()
    get_metas_mini_pet.clear()
    get_metas_potes.clear()
    get_pvirar_ideal.clear()
    get_conversoes.clear()


def invalidar_tudo():
    """Limpa todo o cache de leitura. Útil em testes ou em botão de "atualizar"."""
    invalidar_folha()
    invalidar_referencias()
