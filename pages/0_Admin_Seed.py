"""
pages/0_Admin_Seed.py — Página de admin pra cadastrar a BOM completa (Etapa D).

Roda 1 vez por banco. Idempotente — pode rodar de novo sem duplicar.

Acesso: sidebar → "0 Admin Seed".

Princípio: ferramenta de setup, não operação rotineira. Quando a BOM estiver
estável, esta página pode ser ocultada/removida.
"""
import os
import sys
import streamlit as st

# Bootstrap padrão
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

import database as db_real
import cached_db
import componentes
from seed_bom_completa import executar_seed, INSUMOS, RECEITAS

st.set_page_config(
    page_title="Cadastrar BOM (setup) • Doces Vó Nena",
    layout="wide",
    initial_sidebar_state="auto",
)
from ui_theme import aplicar_tema
aplicar_tema()


componentes.cabecalho(
    "Admin", "Cadastrar BOM (setup)", icone="settings",
    contexto="Área administrativa — recria insumos e receitas no banco. Só para configuração; não é tela do dia a dia.",
)
st.warning("Área administrativa — os botões desta tela escrevem no banco de produção. Use apenas na configuração inicial.")

# ── Status atual ───────────────────────────────────────────────────────────
st.header("Status atual do banco")
try:
    insumos_atuais = db_real.get_insumos(somente_ativos=False)
    bom_atuais = []
    for produto_chave in RECEITAS.keys():
        bom_atuais.extend(db_real.get_bom_produto(produto_chave))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Insumos cadastrados", len(insumos_atuais))
    col2.metric("Total previsto", len(INSUMOS))
    col3.metric("Linhas de BOM", len(bom_atuais))
    col4.metric("Total previsto", sum(len(v) for v in RECEITAS.values()))
except Exception as e:
    st.error(f"Erro ao ler status: {e}")
    insumos_atuais = []


# ── Pré-visualização ───────────────────────────────────────────────────────
st.divider()
st.header("Pré-visualização do que será cadastrado")

import pandas as pd

with st.expander(f"Insumos ({len(INSUMOS)} itens)", expanded=False):
    df_ins = pd.DataFrame(
        INSUMOS, columns=["código", "nome", "categoria", "unidade", "obs"]
    )
    componentes.tabela(df_ins, altura_max=380)

with st.expander(f"Receitas (BOM) — {len(RECEITAS)} produtos", expanded=False):
    for produto_chave, linhas in RECEITAS.items():
        st.markdown(f"**{produto_chave}** — {len(linhas)} insumos:")
        df = pd.DataFrame(linhas, columns=["insumo", "quantidade", "unidade"])
        componentes.tabela(df, cols_direita=["quantidade"])


# ── Botão de ação ──────────────────────────────────────────────────────────
st.divider()
st.header("Executar")
st.caption(
    "Clica no botão pra rodar o seed. O sistema vai criar os insumos que "
    "ainda não existem e cadastrar todas as linhas de BOM. Os estoques "
    "começam em zero — a Gestão preenche depois."
)

if "seed_exec" not in st.session_state:
    st.session_state.seed_exec = None

if st.button("Cadastrar BOM completa", type="primary", width='stretch'):
    logs = []
    def _log(msg):
        logs.append(msg)
    with st.spinner("Cadastrando..."):
        stats = executar_seed(db_real, log=_log)
    st.session_state.seed_exec = {"stats": stats, "logs": logs}
    cached_db.invalidar_suprimentos()  # cache de insumos/BOM cai
    st.rerun()

if st.session_state.seed_exec:
    res = st.session_state.seed_exec
    st.success("Seed executado.")
    s = res["stats"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Insumos novos", s["insumos_criados"])
    c2.metric("Insumos já existentes", s["insumos_existentes"])
    c3.metric("Linhas BOM processadas", s["bom_linhas_inseridas"])
    c4.metric("Atualizações BOM", s["bom_linhas_atualizadas"])
    c5.metric("Erros", len(s["erros"]))

    if s["erros"]:
        st.error("Erros encontrados:")
        for e in s["erros"]:
            st.text(f"  • {e}")

    with st.expander("Ver log detalhado", expanded=False):
        for ln in res["logs"]:
            st.text(ln)


# ── Avisos ────────────────────────────────────────────────────────────────
st.divider()
with st.expander("Quando ocultar / remover esta página", expanded=False):
    st.markdown(
        "- **Quando a BOM estiver estável:** mover este arquivo pra fora de "
        "`pages/` (ex: `_admin/0_Seed.py`) ou prefixar com `_` (Streamlit "
        "esconde arquivos que começam com `_`).\n"
        "- **Se quiser apagar de vez:** delete o arquivo. As receitas no banco "
        "ficam preservadas.\n"
        "- **Não use esta página em rotina** — é só pra setup inicial e "
        "re-aplicação após mudança no script."
    )

componentes.rodape("")
