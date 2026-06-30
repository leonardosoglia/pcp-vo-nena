"""
pages/13_Reconciliacao_SIGE.py — Reconciliação de estoque: SIGE × nosso sistema.

Compara o estoque de matéria-prima do depósito **FABRICA** no SIGE (teórico
contábil: entra por NF-e, baixa por OP) com o estoque do nosso PCP (contagem
física / auto-baixa por produção), insumo a insumo. A divergência é o gatilho do
ajuste de inventário — exatamente o que a Gestão pediu (reuniões 14/06).

SOMENTE LEITURA nos dois lados: lê o SIGE (read-only) e o nosso banco (SELECT).
Nunca escreve no SIGE. Lógica em `reconciliacao_sige.py` (testada via CLI).
Ver docs/ARQUITETURA_SIGE.md.

NOTA: precisa do token SIGE configurado nos Secrets do ambiente (HF). Sem ele, a
página mostra um aviso amigável em vez de quebrar.
"""
import os
import sys
import streamlit as st
import pandas as pd

# Bootstrap defensivo — propaga DATABASE_URL + credenciais SIGE de st.secrets
# pro ambiente (Streamlit Cloud); no HF Spaces já vêm como env var.
try:
    for _k in ("DATABASE_URL", "SIGE_AUTH_TOKEN", "SIGE_USER", "SIGE_APP",
               "SIGE_DEPOSITO_PADRAO"):
        if not os.getenv(_k) and _k in st.secrets:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

import cached_db
import sige_cloud_api as sige
import reconciliacao_sige as recon
import componentes

st.set_page_config(
    page_title="Reconciliação SIGE • Doces Vó Nena",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui_theme import aplicar_tema
aplicar_tema()

STATUS_LABEL = {
    "OK": "✅ Bate",
    "DIVERGENTE": "⚠️ Divergente",
    "NAO_COMPARAVEL": "❓ Confirmar unidade",
    "SEM_SIGE": "➖ Sem SIGE",
}


@st.cache_data(ttl=600, show_spinner="Lendo o estoque no SIGE...")
def carregar_reconciliacao():
    """Lê o saldo consolidado do SIGE e reconcilia contra o nosso banco.
    Retorna (linhas, resumo, erro). Tudo read-only."""
    con = sige.testar_conexao()
    if not con["ok"]:
        return None, None, con["mensagem"]
    try:
        produtos = sige.listar_todos_produtos(page_size=200, max_paginas=50)
    except Exception as e:
        return None, None, str(e)
    idx = recon.indexar_saldo_consolidado(produtos)
    linhas = recon.reconciliar(cached_db, idx)
    return linhas, recon.resumir(linhas), None


def _num_br(v, casas=2, sinal=False):
    """Número no padrão BR (1.234,56). `sinal`=True força +/−; None vira '—'."""
    if v is None:
        return "—"
    fmt = f"{{:+,.{casas}f}}" if sinal else f"{{:,.{casas}f}}"
    return fmt.format(float(v)).replace(",", "X").replace(".", ",").replace("X", ".")


def _qtd_br(v, un):
    """Quantidade compacta no padrão BR, com a unidade (ex.: '39,5 kg')."""
    return f"{v:g}".replace(".", ",") + (f" {un}" if un else "")


def montar_df(linhas):
    rows = []
    for ln in linhas:
        rows.append({
            "Insumo": ln["nome"],
            "Situação": STATUS_LABEL.get(ln["status"], ln["status"]),
            "SIGE (total)": _num_br(ln["sige_saldo_compra"]),
            "SIGE → receita": (_qtd_br(ln["sige_convertido"], ln["un_receita"])
                               if ln["sige_convertido"] is not None else "—"),
            "Nosso sistema": _qtd_br(ln["sistema"], ln["un_receita"]),
            "Divergência": _num_br(ln["divergencia"], sinal=True),
        })
    return pd.DataFrame(rows)


# ════════════════════════════════════════════════════════════════════════════
# UI
# ════════════════════════════════════════════════════════════════════════════
st.title("Reconciliação de estoque — SIGE × nosso sistema")
st.caption("Estoque **total** de matéria-prima no SIGE (a fábrica é um local só; "
           "somamos todos os depósitos), comparado com o nosso sistema. Somente "
           "leitura — nada é alterado no SIGE.")

if not sige.credenciais_configuradas():
    st.warning(
        "**Token do SIGE não configurado neste ambiente.** Para a reconciliação "
        "funcionar em produção, defina `SIGE_AUTH_TOKEN`, `SIGE_USER` e `SIGE_APP` "
        "nos *Secrets* do Hugging Face. (Localmente, ficam no `.streamlit/secrets.toml`.)"
    )
    st.stop()

col_btn, _ = st.columns([1, 4])
if col_btn.button("🔄 Carregar / atualizar do SIGE"):
    st.session_state["recon_go"] = True

# Carregamento preguiçoso: a tela abre na hora; só lê o SIGE quando você clica.
if st.session_state.pop("recon_go", False):
    st.session_state["recon_loaded"] = True
    carregar_reconciliacao.clear()
if not st.session_state.get("recon_loaded"):
    st.info("A tela abre na hora. Clique em **Carregar / atualizar do SIGE** para ler o "
            "estoque e reconciliar (leva ~1 min; depois fica em cache).")
    st.stop()

linhas, resumo, erro = carregar_reconciliacao()

if erro:
    st.error(f"Não consegui ler o SIGE agora: {erro}")
    st.stop()

# ── Cartões de resumo ────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Comparáveis", resumo["comparaveis"])
c2.metric("Batem", resumo["OK"])
c3.metric("Divergentes", resumo["DIVERGENTE"])
c4.metric("Confirmar unidade", resumo["NAO_COMPARAVEL"])

if resumo["maior_divergencia"]:
    chave, valor = resumo["maior_divergencia"]
    st.caption(f"Maior divergência: **{chave}** ({valor:g} na unidade da receita).")

# ── Tabela ───────────────────────────────────────────────────────────────────
df = montar_df(linhas)
componentes.tabela(
    df, altura_max=520,
    cols_direita=["SIGE (total)", "SIGE → receita", "Nosso sistema", "Divergência"],
)

# ── Como ler ─────────────────────────────────────────────────────────────────
with st.expander("Como ler esta tela"):
    st.markdown(
        "- **SIGE (total):** saldo do insumo somando todos os depósitos do SIGE "
        "(a fábrica é um local só; as divisões em depósitos/CNPJs são contábeis), "
        "na unidade de compra (caixa/fardo/pacote).\n"
        "- **SIGE → receita:** o saldo convertido pra unidade da receita (kg/L/und).\n"
        "- **Nosso sistema:** o estoque no nosso PCP. **Hoje reflete a auto-baixa "
        "por produção** (sem carga inicial), por isso aparece negativo. Depois da "
        "**contagem física**, esta coluna passa a ser o estoque real e a divergência "
        "vira o **ajuste de inventário** a tratar com a Gestão.\n"
        "- **❓ Confirmar unidade:** insumos cujo fator de conversão (caixa↔kg) "
        "ainda depende de confirmação da Suprimentos.\n"
        "- **➖ Sem SIGE:** insumos ainda não cadastrados no SIGE."
    )

st.caption("Somente leitura. A decisão de ajuste é da Gestão — o sistema só mostra "
           "a diferença. Cache de 10 min; use *Atualizar do SIGE* pra forçar a leitura.")
