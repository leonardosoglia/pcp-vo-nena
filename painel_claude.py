# =============================================================================
# PAINEL DE CONTROLE DE PRODUÇÃO - DOCES VÓ NENA
# Engenharia de Software: Python 3 + Streamlit + Pandas + Google Sheets
# Arquitetura: Leitura em tempo real de CSV exportado pelo Google Sheets.
#              O Streamlit atua como "lente" visual sobre os dados — sem gravar.
# =============================================================================

# --- 1. IMPORTS ---
import streamlit as st
import pandas as pd

# =============================================================================
# --- 2. CONFIGURAÇÃO DA PÁGINA ---
# =============================================================================
st.set_page_config(
    page_title="PCP • Doces Vó Nena",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS global: deixa a UI mais limpa e legível em tablets/celulares do chão de fábrica
st.markdown(
    """
    <style>
        /* Fonte um pouco maior para leitura em tablets */
        html, body, [class*="css"] { font-size: 15px; }
        /* Remove padding excessivo do topo */
        .block-container { padding-top: 1rem; padding-bottom: 1rem; }
        /* Cabeçalhos de seção com cor da marca */
        h1, h2, h3 { color: #b5451b; }
        /* Botão de atualizar destacado */
        div[data-testid="stButton"] > button[kind="primary"] {
            background-color: #b5451b;
            color: white;
            font-weight: bold;
        }
        /* Sidebar: fundo levemente escuro para separar visualmente */
        section[data-testid="stSidebar"] { background-color: #1a1a2e; color: white; }
        section[data-testid="stSidebar"] * { color: white !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# --- 3. URLs DO GOOGLE SHEETS (substitua os GIDs reais aqui) ---
# Formato: .../export?format=csv&gid=<GID_DA_ABA>
# =============================================================================
BASE_URL = "https://docs.google.com/spreadsheets/d/1YPYm7yrKjzR95DdKfRcKALXS_QSUJt4MwtpRgQs5gfM"

URLS = {
    "PAINEL_GESTAO":     f"{BASE_URL}/gviz/tq?tqx=out:csv&gid=177579187",
    "QUADRO_ERALDO":     f"{BASE_URL}/gviz/tq?tqx=out:csv&gid=629774064",
    "PRODUCAO_JOEL":     f"{BASE_URL}/gviz/tq?tqx=out:csv&gid=201565125",
    "CORTE_GIL":         f"{BASE_URL}/gviz/tq?tqx=out:csv&gid=534903008",
    "EMBALAGEM_LEONICE": f"{BASE_URL}/gviz/tq?tqx=out:csv&gid=587696180",
}

# =============================================================================
# --- 4. FUNÇÃO DE CARGA DE DADOS COM CACHE (60 segundos) ---
# @st.cache_data evita requisições repetidas ao Sheets a cada interação do usuário.
# =============================================================================
@st.cache_data(ttl=60)
def carregar_dados(url: str, colunas_int: list = None) -> pd.DataFrame:
    """
    Lê uma aba do Google Sheets via CSV exportado.
    - Trata NaN em colunas numéricas com fillna(0).
    - Converte colunas especificadas para int (evita '5.0' em vez de '5').
    - Retorna DataFrame vazio em caso de falha (com st.error amigável).
    """
    try:
        df = pd.read_csv(url)
        if colunas_int:
            for col in colunas_int:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        # Preenche strings NaN com string vazia
        df = df.fillna("")
        return df
    except Exception as e:
        st.error(
            f"❌ Erro ao carregar dados do Google Sheets. "
            f"Verifique se a planilha está pública e o link está correto.\n\n"
            f"Detalhe técnico: `{e}`"
        )
        return pd.DataFrame()


# =============================================================================
# --- 5. FUNÇÕES DE ESTILIZAÇÃO (GESTÃO À VISTA — CÓDIGO DE CORES) ---
# Pinta o fundo das células para facilitar leitura rápida no chão de fábrica.
# =============================================================================

def destacar_positivos_vermelho(valor):
    """Verde-escuro suave para valores > 0 (trabalho pendente)."""
    try:
        if pd.notna(valor) and float(valor) > 0:
            return "background-color: rgba(255, 75, 75, 0.25); color: #fff;"
    except (ValueError, TypeError):
        pass
    return ""


def destacar_positivos_verde(valor):
    """Verde para o quadro de corte/embalagem — tarefa a fazer."""
    try:
        if pd.notna(valor) and float(valor) > 0:
            return "background-color: rgba(39, 174, 96, 0.30); color: #fff;"
    except (ValueError, TypeError):
        pass
    return ""


def destacar_positivos_azul(valor):
    """Azul para o quadro de produção do Joel."""
    try:
        if pd.notna(valor) and float(valor) > 0:
            return "background-color: rgba(52, 152, 219, 0.30); color: #fff;"
    except (ValueError, TypeError):
        pass
    return ""


def estilizar_df(df: pd.DataFrame, estilo_func, colunas_excluir: list = None):
    """
    Aplica uma função de estilo a todas as colunas do DataFrame,
    exceto as listadas em `colunas_excluir` (ex.: coluna de nome/produto).
    """
    if df.empty:
        return df.style
    cols_alvo = [c for c in df.columns if c not in (colunas_excluir or [])]
    return df.style.map(estilo_func, subset=cols_alvo)


# =============================================================================
# --- 6. MODAL / DIALOG (ALERTA DE ESTOQUE CRÍTICO) ---
# Janela pop-up centralizada acionada pelo botão da sidebar.
# =============================================================================
@st.dialog("⚠️ Produtos com Estoque Crítico", width="large")
def modal_estoque_critico(df_alertas: pd.DataFrame):
    """Exibe tabela limpa dos produtos abaixo do estoque de segurança."""
    st.markdown(
        "Os produtos abaixo estão com estoque **abaixo da meta mínima** e precisam de ordem de produção:"
    )
    df_exibir = df_alertas[["ID_Produto", "Stock_Real", "Stock_Seguranca"]].copy()
    df_exibir.columns = ["Produto", "Em Estoque", "Meta (Seg.)"]
    st.dataframe(
        df_exibir.style.map(
            lambda v: "background-color: rgba(255,75,75,0.3); color:white;"
            if isinstance(v, (int, float)) and v > 0
            else "",
            subset=["Em Estoque"],
        ),
        width='stretch',
        hide_index=True,
    )
    st.caption(f"Total de produtos em alerta: **{len(df_alertas)}**")


# =============================================================================
# --- 7. BOTÃO DE REFRESH (ATUALIZAÇÃO MANUAL) ---
# Limpa o cache e força recarregamento da página / do Sheets.
# =============================================================================
col_titulo, col_refresh = st.columns([5, 1])
with col_titulo:
    st.title("🍬 Painel PCP — Doces Vó Nena")
with col_refresh:
    st.write("")  # espaçamento vertical
    if st.button("🔄 Atualizar", type="primary", width='stretch'):
        st.cache_data.clear()
        st.rerun()

st.divider()

# =============================================================================
# --- 8. CARREGAMENTO DE DADOS (todas as abas) ---
# =============================================================================
df_gestao = carregar_dados(
    URLS["PAINEL_GESTAO"],
    colunas_int=["Total_Produzido", "Total_Saidas", "Stock_Real", "Stock_Seguranca"],
)
df_eraldo = carregar_dados(
    URLS["QUADRO_ERALDO"],
    colunas_int=["Bandejas_PV", "Bandejas_V", "Corte_Gil", "Saldo_Amanha"],
)
df_joel = carregar_dados(
    URLS["PRODUCAO_JOEL"],
    colunas_int=["Potes_260g", "Potes_605g"],
)
df_gil = carregar_dados(
    URLS["CORTE_GIL"],
    colunas_int=["Falta_Cortar", "Corte"],
)
df_leonice = carregar_dados(
    URLS["EMBALAGEM_LEONICE"],
    colunas_int=["Para_Embalar", "Embalado"],
)

# =============================================================================
# --- 8.1 SIDEBAR — ALERTAS DE ESTOQUE CRÍTICO ---
# Apenas a contagem de alertas fica na sidebar; a tabela abre em modal.
# =============================================================================
with st.sidebar:
    st.header("🚨 Estoque Crítico")
    st.markdown("---")

    if df_gestao.empty:
        st.warning("Dados não carregados.")
    else:
        # Filtra produtos cujo campo Alerta_Producao contém "GERAR"
        df_alertas = df_gestao[
            df_gestao["Alerta_Producao"].astype(str).str.contains("GERAR", na=False)
        ].copy()

        if df_alertas.empty:
            st.success("✅ Tudo controlado!\nNenhum produto em alerta.")
        else:
            st.warning(
                f"⚠️ **Atenção:** {len(df_alertas)} produto(s) precisam de produção!"
            )
            # Botão que abre o modal pop-up com a lista completa
            if st.button("📋 Ver Produtos em Falta", width='stretch'):
                modal_estoque_critico(df_alertas)

    st.markdown("---")
    st.caption("Dados atualizados a cada 60s.\nUse '🔄 Atualizar' para forçar.")


# =============================================================================
# --- 8.2 NAVEGAÇÃO PRINCIPAL — ABAS POR PERSONA ---
# =============================================================================
aba_eraldo, aba_gil, aba_leonice = st.tabs(
    ["📋 Planejamento (Eraldo)", "🔪 Corte (Gil)", "📦 Embalagem (Leonice)"]
)

# =============================================================================
# ============== ABA 1: ÁREA DO ERALDO (PLANEJAMENTO) ========================
# =============================================================================
with aba_eraldo:

    # ---- 8.2.1 GAVETA DE PARÂMETROS E METAS (consulta rápida para o gestor) ----
    with st.expander("📊 Parâmetros e Metas Ideais — Clique para consultar", expanded=False):

        sub_semanal, sub_diario, sub_conversao = st.tabs(
            ["📅 Metas 45g (Semanal)", "📆 Metas Fixas (Diário)", "⚙️ Conversões"]
        )

        # --- Metas Semanais de 45g ---
        with sub_semanal:
            st.markdown("##### Metas de Produção — Doces 45g por Dia da Semana")
            st.caption("ℹ️ Em semanas com feriado, adiantar produção.")
            df_semanal = pd.DataFrame({
                "Sabor":        ["TRADICIONAL", "LEITE COND.", "BRIGADEIRO", "CAFÉ", "PÉ DE MOÇA"],
                "Segunda":      [5200, 2600, 1300, 1300, 1300],
                "Terça":        [4400, 2200, 1100, 1100, 1100],
                "Quarta":       [5200, 2600, 1300, 1300, 1300],
                "Quinta":       [6800, 3400, 1700, 1700, 1700],
                "Sexta":        [5600, 2800, 1400, 1400, 1400],
            })
            st.dataframe(df_semanal, width='stretch', hide_index=True)

        # --- Metas Fixas Diárias (Mini e Pet) ---
        with sub_diario:
            st.markdown("##### Metas Diárias Fixas — Mini, Pet e Potes")

            df_mini_pet = pd.DataFrame({
                "Sabor":        ["TRADICIONAL", "LEITE COND.", "BRIGADEIRO", "CAFÉ", "PÉ DE MOÇA", "ZERO"],
                "Mini (und)":   [500, 500, 300, 300, 300, "= Leite Cond. 45g do dia"],
                "Pet (und)":    [220, 180,  90,  90,  90, 300],
            })
            st.dataframe(df_mini_pet, width='stretch', hide_index=True)

            st.markdown("---")
            st.markdown("##### Potes e Referência de Produção (Bandejas/dia)")
            df_potes = pd.DataFrame({
                "Sabor":              ["TRADICIONAL", "LEITE COND.", "BRIGADEIRO", "CAFÉ", "PÉ DE MOÇA", "ZERO"],
                "Potes 260g":         [50, 5, 20, 15, 15, 50],
                "Potes 605g":         [20, 20, 10, 10, 10, 20],
                "Ref. Bandejas/dia":  [70, 35, 22, 22, 22, 18],
            })
            st.dataframe(df_potes, width='stretch', hide_index=True)

        # --- Tabela de Conversões / Rendimentos ---
        with sub_conversao:
            st.markdown("##### Taxas de Conversão e Rendimento da Fábrica")
            df_conv = pd.DataFrame({
                "Unidade":      ["1 Tacho", "1 Bandeja 45g", "1 Bandeja Mini", "1 Bandeja Pet Normal", "1 Bandeja Pet ZERO (Diet)"],
                "Rende":        ["8 Bandejas", "100 unidades", "150 unidades", "30 unidades", "60 unidades"],
            })
            st.dataframe(df_conv, width='stretch', hide_index=True)

    # ---- 8.2.2 SALDOS E PROJEÇÕES DE BANDEJAS (QUADRO_ERALDO) ----
    st.subheader("📦 Saldos e Projeções de Bandejas")
    if df_eraldo.empty:
        st.info("Sem dados de saldo disponíveis.")
    else:
        cols_num_eraldo = ["Bandejas_PV", "Bandejas_V", "Corte_Gil", "Saldo_Amanha"]
        st.dataframe(
            estilizar_df(df_eraldo, destacar_positivos_azul, colunas_excluir=["Produto"]),
            width='stretch',
            hide_index=True,
        )

    st.divider()

    # ---- 8.2.3 QUADRO DE PRODUÇÃO (SR. JOEL) + LEMBRETES ----
    # Layout: 75% tabela Joel | 25% bloco de lembretes (coluna "Amanha")
    st.subheader("👨‍🍳 Quadro de Produção — Sr. Joel")

    if df_joel.empty:
        st.info("Sem ordens de produção disponíveis.")
    else:
        col_joel, col_lembretes = st.columns([3, 1])

        with col_joel:
            # Colunas principais da ordem de produção (sem "Amanha", que vai para lembretes)
            colunas_joel_tabela = [c for c in df_joel.columns if c != "Amanha"]
            df_joel_tabela = df_joel[colunas_joel_tabela]
            st.dataframe(
                estilizar_df(df_joel_tabela, destacar_positivos_azul, colunas_excluir=["Sabor"]),
                width='stretch',
                hide_index=True,
            )

        with col_lembretes:
            st.markdown("**📝 Lembretes / Amanhã**")
            if "Amanha" in df_joel.columns:
                lembretes = df_joel[["Sabor", "Amanha"]].copy()
                lembretes = lembretes[lembretes["Amanha"].astype(str).str.strip() != ""]
                if lembretes.empty:
                    st.success("Nenhum lembrete para amanhã.")
                else:
                    for _, row in lembretes.iterrows():
                        st.info(f"**{row['Sabor']}:** {row['Amanha']}")
            else:
                st.caption("Coluna 'Amanha' não encontrada na aba.")


# =============================================================================
# ============== ABA 2: ÁREA DO GIL (CORTE) ==================================
# =============================================================================
with aba_gil:
    st.subheader("🔪 Quadro de Corte — Gil")
    st.caption("O que precisa ser cortado hoje e quantas bandejas faltam.")

    if df_gil.empty:
        st.info("Sem ordens de corte disponíveis.")
    else:
        st.dataframe(
            estilizar_df(df_gil, destacar_positivos_verde, colunas_excluir=["Produto"]),
            width='stretch',
            hide_index=True,
        )

        # Resumo rápido: total de bandejas a cortar
        total_corte = df_gil["Corte"].sum() if "Corte" in df_gil.columns else 0
        total_falta = df_gil["Falta_Cortar"].sum() if "Falta_Cortar" in df_gil.columns else 0
        c1, c2 = st.columns(2)
        c1.metric("Total a Cortar (meta do dia)", f"{total_corte} bandejas")
        c2.metric("Total ainda Faltando Cortar", f"{total_falta} bandejas")


# =============================================================================
# ============== ABA 3: ÁREA DA LEONICE (EMBALAGEM) ==========================
# =============================================================================
with aba_leonice:
    st.subheader("📦 Quadro de Embalagem — Leonice")
    st.caption("Bandejas aguardando embalagem para liberar ao estoque final.")

    if df_leonice.empty:
        st.info("Sem bandejas para embalar no momento.")
    else:
        st.dataframe(
            estilizar_df(df_leonice, destacar_positivos_vermelho, colunas_excluir=["Produto"]),
            width='stretch',
            hide_index=True,
        )

        # Resumo rápido: total pendente de embalagem
        total_embalar = df_leonice["Para_Embalar"].sum() if "Para_Embalar" in df_leonice.columns else 0
        total_embalado = df_leonice["Embalado"].sum() if "Embalado" in df_leonice.columns else 0
        c1, c2 = st.columns(2)
        c1.metric("Total Pendente de Embalagem", f"{total_embalar} bandejas")
        c2.metric("Total Já Embalado (hoje)", f"{total_embalado} bandejas")

# =============================================================================
# FIM DO ARQUIVO painel.py
# Para rodar localmente: streamlit run painel.py
# Para deploy: Streamlit Community Cloud (https://streamlit.io/cloud)
# Dependências (requirements.txt): streamlit>=1.35.0  pandas>=2.0.0
# =============================================================================