"""
pages/1_Painel.py — PCP Vó Nena v1.2

Visualização operacional por departamento (Gestão, Produção, Corte, Embalagem, Estoque, Análise).
Acessível pelo sidebar do app principal (entry point: lancamento.py).

Stack: Python + Streamlit + Postgres (Supabase) — fallback SQLite local em dev.
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys, os

# Bootstrap defensivo: o entry point (lancamento.py) já faz isso, mas idempotente
# garante que se essa página for aberta direto não quebra.
if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
    os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]

# sys.path do pai pra importar cached_db / database / analise da raiz
_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from cached_db import (
    init_db, get_folha_cocada, get_folha_palha, get_pm_balas_doces,
    get_papelzinho_joel, get_estoque, get_metas_45g, get_metas_mini_pet,
    get_metas_potes, get_pvirar_ideal, get_conversoes, list_datas_folha,
    calcular_cortados, calcular_viradas_pvirar, get_folha_completa,
    SABORES_COCADA, SABORES_PALHA
)

st.set_page_config(page_title="Painel • Doces Vó Nena", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sora', sans-serif; font-size: 14px; }
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    h1, h2, h3 { color: #C05621; font-weight: 700; }
    section[data-testid="stSidebar"] { background-color: #1C1410; }
    section[data-testid="stSidebar"] * { color: #F5E6D3 !important; }
    section[data-testid="stSidebar"] .stButton > button { background-color: #C05621; color: white; border: none; font-weight: 600; }
    div[data-testid="stButton"] > button[kind="primary"] { background-color: #C05621 !important; color: white !important; font-weight: 700; border-radius: 6px; }
    thead tr th { background-color: #F7EDE2 !important; color: #7B341E !important; font-weight: 700 !important; font-size: 13px !important; }
    hr { border-color: #F7EDE2; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; font-size: 14px; color: #7B341E; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #C05621; color: #C05621 !important; }
    [data-testid="metric-container"] { background: #FFF8F2; border: 1px solid #F7EDE2; border-radius: 10px; padding: 10px 16px; }
    [data-testid="metric-container"] label { color: #7B341E !important; font-size: 12px !important; font-weight: 600 !important; }
    [data-testid="stExpander"] summary { font-weight: 600; color: #C05621; }
</style>
""", unsafe_allow_html=True)

# init_db é idempotente — entry point já chamou, mas defensivo se a página
# for o primeiro hit do processo (cold start).
init_db()

# ── Helpers de estilo ──────────────────────────────────────────────────────────
def cor(val, c="rgba(192,86,33,0.18)"):
    try:
        if pd.notna(val) and float(val) > 0:
            return f"background-color:{c};color:#1a1a1a;font-weight:600;"
    except: pass
    return "color:rgba(0,0,0,0.18);" if val == 0 or val == "0" else ""

def estilo_laranja(v): return cor(v,"rgba(192,86,33,0.18)")
def estilo_verde(v):   return cor(v,"rgba(5,150,105,0.18)")
def estilo_azul(v):    return cor(v,"rgba(37,99,235,0.16)")
def estilo_vermelho(v):return cor(v,"rgba(220,38,38,0.18)")

def df_styled(df, fn, excluir=None):
    if df.empty: return df.style
    cols = [c for c in df.columns if c not in (excluir or [])]
    return df.style.map(fn, subset=cols)

def saldo_style(val):
    try:
        v = float(val)
        if v > 0: return "background-color:rgba(220,38,38,0.2);color:#7f1d1d;font-weight:700;"
        if v == 0: return "background-color:rgba(5,150,105,0.2);color:#065f46;font-weight:700;"
    except: pass
    return ""

def reord_cocada(df):
    df = df.copy()
    df["sabor"] = pd.Categorical(df["sabor"], categories=SABORES_COCADA, ordered=True)
    return df.sort_values("sabor").reset_index(drop=True)

def reord_palha(df):
    df = df.copy()
    df["sabor"] = pd.Categorical(df["sabor"], categories=SABORES_PALHA, ordered=True)
    return df.sort_values("sabor").reset_index(drop=True)


def mask_zero_45g(df, col_45g_name="45g", sabor_col="Sabor"):
    """ZERO não tem cocada 45g — produto não existe na fábrica.
    Substitui o valor por '—' visualmente. Mantém o restante dos sabores intacto."""
    if df.empty or col_45g_name not in df.columns or sabor_col not in df.columns:
        return df
    df = df.copy()
    df[col_45g_name] = df.apply(
        lambda r: "—" if str(r[sabor_col]).upper() == "ZERO" else r[col_45g_name],
        axis=1,
    )
    return df

# ── Modal alertas ──────────────────────────────────────────────────────────────
@st.dialog("⚠️ Produtos com Estoque Crítico", width="large")
def modal_alertas(df):
    st.markdown("Produtos **abaixo do estoque de segurança:**")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Total: **{len(df)}** produtos em alerta")

# ── Carregar dados ─────────────────────────────────────────────────────────────
# Mostra a folha de hoje. Se não houver dados de hoje, cai pra última data registrada
# (útil enquanto o Leonardo está digitalizando histórico antes da folha do dia).
hoje_real = str(date.today())
datas_disponiveis = list_datas_folha()
# Usa cache de list_datas_folha em vez de query separada — zero round-trips se já cacheado.
if hoje_real in datas_disponiveis or not datas_disponiveis:
    hoje = hoje_real
else:
    hoje = datas_disponiveis[0]   # mais recente
# 1 chamada paralela em vez de 3-4 sequenciais
_folha = get_folha_completa(hoje)
df_cocada  = pd.DataFrame(_folha["cocada"])
df_palha   = pd.DataFrame(_folha["palha"])
pbd        = _folha["pmbd"]
df_est     = pd.DataFrame(get_estoque())

# ── Cabeçalho ──────────────────────────────────────────────────────────────────
col_t, col_d, col_r = st.columns([5,2,1])
with col_t: st.title("🍬 PCP — Doces Vó Nena")
with col_d:
    if hoje == hoje_real:
        st.markdown(f"<div style='margin-top:14px;color:#7B341E;font-weight:600;'>📅 {datetime.today().strftime('%A, %d/%m/%Y').capitalize()}</div>", unsafe_allow_html=True)
    else:
        from datetime import datetime as _dt
        d_show = _dt.strptime(hoje, "%Y-%m-%d").strftime("%d/%m/%Y")
        st.markdown(f"<div style='margin-top:14px;color:#C05621;font-weight:600;'>📅 Última folha registrada: {d_show}</div>", unsafe_allow_html=True)
with col_r:
    st.write("")
    if st.button("🔄", type="primary", use_container_width=True, help="Atualizar"): st.rerun()
st.divider()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🍬 Vó Nena")
    st.markdown("**Sistema PCP** — v1.2")
    st.divider()
    st.markdown("#### 🚨 Estoque Crítico")
    alertas = [e for e in get_estoque() if "GERAR" in e.get("alerta","")]
    if not alertas:
        st.success("✅ Tudo controlado!")
    else:
        st.warning(f"**{len(alertas)} produtos** precisam de produção!")
        if st.button("📋 Ver lista completa", use_container_width=True):
            df_al = pd.DataFrame(alertas)[["id_produto","stock_real","stock_seguranca"]]
            df_al.columns = ["Produto","Em Estoque","Meta"]
            modal_alertas(df_al)
    st.divider()
    st.caption("Atualizado em tempo real.\nUse 🔄 para forçar atualização.")

# ── Abas ───────────────────────────────────────────────────────────────────────
aba_gestao, aba_producao, aba_corte, aba_embalagem, aba_estoque, aba_analise = st.tabs([
    "📋 Gestão — Planejamento",
    "🧑‍🍳 Produção",
    "🔪 Corte",
    "📦 Embalagem",
    "📊 Estoque",
    "📊 Análise",
])

# ══════════════════════════════════════════════════════════════════
# ABA ERALDO
# ══════════════════════════════════════════════════════════════════
with aba_gestao:

    with st.expander("📚 Parâmetros e Metas Ideais — clique para consultar", expanded=False):
        s1,s2,s3,s4 = st.tabs(["📅 45g (semanal)","📆 Mini e Pet","🫙 Potes","⚙️ Conversões"])
        with s1:
            st.caption("⚠️ Semanas com feriado: adiantar produção no dia anterior.")
            df_m = pd.DataFrame(get_metas_45g())
            df_m.columns = ["Sabor","Segunda","Terça","Quarta","Quinta","Sexta"]
            st.dataframe(df_styled(df_m, estilo_laranja, ["Sabor"]), use_container_width=True, hide_index=True)
        with s2:
            df_mp = pd.DataFrame(get_metas_mini_pet())
            df_mp.columns = ["Sabor","Mini (und)","Pet (und)"]
            st.dataframe(df_mp, use_container_width=True, hide_index=True)
        with s3:
            df_pt = pd.DataFrame(get_metas_potes())
            df_pt.columns = ["Sabor","Potes 260g","Potes 605g","Ref. Bandejas/dia"]
            st.dataframe(df_styled(df_pt, estilo_laranja, ["Sabor"]), use_container_width=True, hide_index=True)
        with s4:
            df_cv = pd.DataFrame(get_conversoes())[["descricao","rende"]]
            df_cv.columns = ["Unidade","Rende"]
            st.dataframe(df_cv, use_container_width=True, hide_index=True)
            st.info("💡 **Regra de ouro:** 1 Tacho = 8 Bandejas. Coluna Produção (Joel): sempre múltiplo de 8 (exceto ZERO).")

    st.subheader("📊 Visão Geral do Dia")
    if not df_cocada.empty:
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Embalados 45g",   f"{df_cocada['emb_45g'].sum():,}")
        c2.metric("Embalados Mini",  f"{df_cocada['emb_mini'].sum():,}")
        c3.metric("Embalados Pet",   f"{df_cocada['emb_pet'].sum():,}")
        c4.metric("Bandejas produz.",f"{df_cocada['ord_prod_band'].sum()}")
        c5.metric("Cortados ① 45g",  f"{df_cocada['cort1_45g'].sum():,}")
    st.divider()

    st.subheader("🎁 Embalados — Cocada")
    if not df_cocada.empty:
        df_e = reord_cocada(df_cocada)[["sabor","emb_45g","emb_mini","emb_pet","emb_potes_260g","emb_potes_605g"]]
        df_e.columns = ["Sabor","45g","Mini","Pet","Potes 260g","Potes 605g"]
        df_e = mask_zero_45g(df_e)
        st.dataframe(df_styled(df_e, estilo_laranja, ["Sabor"]), use_container_width=True, hide_index=True)

    st.subheader("🌾 Embalados — Palha")
    if not df_palha.empty:
        df_ep = reord_palha(df_palha)[["sabor","emb_50g","emb_pet"]]
        df_ep.columns = ["Sabor","50g","Pet"]
        st.dataframe(df_styled(df_ep, estilo_laranja, ["Sabor"]), use_container_width=True, hide_index=True)
    st.divider()

    st.subheader("✂️ Cortados — Cocada")
    st.caption("① cortados hoje (lado embalagem) · ② = ① + Embalados + Joel · ③ = ② − Parâmetro Real (45g)")
    cort_data = calcular_cortados(hoje)
    if cort_data and not df_cocada.empty:
        df_c = pd.DataFrame(cort_data)[["sabor","c1_45g","c2_45g","c3_45g","c1_mini","c2_mini","c1_pet","c2_pet"]]
        df_c.columns = ["Sabor","①45g","②45g","③45g","①Mini","②Mini","①Pet","②Pet"]
        st.dataframe(df_styled(df_c, estilo_verde, ["Sabor"]), use_container_width=True, hide_index=True)
    st.divider()

    st.subheader("🔄 Viradas e P/Virar")
    col_v, col_pv = st.columns(2)
    vp = calcular_viradas_pvirar(hoje)
    with col_v:
        st.caption("Viradas cocada: ① Joel · ② = ① − soma das ordens de corte")
        if vp:
            df_vir = pd.DataFrame(vp)[["sabor","vir1","vir2"]]
            df_vir.columns = ["Sabor","① Joel","② Pós-corte"]
            st.dataframe(df_styled(df_vir, estilo_azul, ["Sabor"]), use_container_width=True, hide_index=True)
        if not df_palha.empty:
            df_palha_v = reord_palha(df_palha)[["sabor","cont_band_palha"]]
            df_palha_v.columns = ["Palha (sabor)","Bandejas"]
            df_palha_v_f = df_palha_v[df_palha_v["Bandejas"] > 0]
            if not df_palha_v_f.empty:
                st.caption("Coluna PALHA (bandejas que Leonardo conta):")
                st.dataframe(df_palha_v_f, use_container_width=True, hide_index=True)
    with col_pv:
        st.caption("P/Virar: ① Joel · ② = ① + Viradas② · Meta = referência fixa por sabor")
        if vp:
            df_pv = pd.DataFrame(vp)[["sabor","pv1","pv2","pv_meta"]]
            df_pv.columns = ["Sabor","① Joel","② c/Viradas","Meta"]
            st.dataframe(df_styled(df_pv, estilo_azul, ["Sabor"]), use_container_width=True, hide_index=True)
    st.divider()

    st.subheader("🍭 PM · Balas · Doces")
    if pbd:
        col_pm, col_b, col_d_col = st.columns(3)
        with col_pm:
            st.markdown("**🍞 Pão de Mel**")
            st.metric("Hoje (cnt)",   pbd.get("cnt_pm", 0))
            st.metric("Ordem do dia", pbd.get("ord_pm", 0))
        with col_b:
            st.markdown("**🍭 Balas**")
            st.metric("Hoje (cnt)",     pbd.get("cnt_balas", 0))
            balas_tachos = pbd.get("ord_balas", 0)
            st.metric("Ordem (tachos)", balas_tachos,
                      help=f"1 tacho = 30 balas → equivale a {balas_tachos*30} balas")
        with col_d_col:
            st.markdown("**🍫 Doces**")
            st.metric("Unidades", pbd.get("cnt_doces_displays", 0))
        if pbd.get("ord_amanha_obs"): st.info(f"📅 Amanhã: {pbd['ord_amanha_obs']}")
        if pbd.get("obs"): st.info(f"📝 {pbd['obs']}")

# ══════════════════════════════════════════════════════════════════
# ABA SR. JOEL
# ══════════════════════════════════════════════════════════════════
with aba_producao:
    st.subheader("🧑‍🍳 Quadro de Produção")
    if not df_cocada.empty:
        col_j, col_l = st.columns([3,1])
        with col_j:
            df_joel = reord_cocada(df_cocada)[["sabor","ord_prod_band","ord_prod_virada","ord_prod_potes_260g","ord_prod_potes_605g"]]
            df_joel.columns = ["Sabor","Produção (band.)","Virada","Potes 260g","Potes 605g"]
            st.dataframe(df_styled(df_joel, estilo_laranja, ["Sabor"]), use_container_width=True, hide_index=True)
            c1,c2 = st.columns(2)
            tot_band = int(df_cocada["ord_prod_band"].sum())
            c1.metric("Total bandejas", tot_band)
            c2.metric("Equiv. tachos (excl. Z)", f"{tot_band/8:.1f}")
        with col_l:
            st.markdown("**📝 Lembretes / Amanhã**")
            lem = reord_cocada(df_cocada)[["sabor","amanha_obs"]]
            lem = lem[lem["amanha_obs"].astype(str).str.strip() != ""]
            if lem.empty: st.success("Nenhum lembrete.")
            else:
                for _, row in lem.iterrows(): st.info(f"**{row['sabor']}:** {row['amanha_obs']}")

    st.divider()
    st.subheader("🌾 Produção Palha")
    if not df_palha.empty:
        df_pp = reord_palha(df_palha)[["sabor","ord_prod_band"]]
        df_pp.columns = ["Sabor","Bandejas"]
        df_pp_f = df_pp[df_pp["Bandejas"] > 0]
        if df_pp_f.empty: st.info("Nenhuma produção de palha hoje.")
        else: st.dataframe(df_styled(df_pp_f, estilo_laranja, ["Sabor"]), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🍭 PM · Balas · Doces")
    if pbd:
        df_pbd = pd.DataFrame([{
            "🍞 PM (cnt)":         pbd.get("cnt_pm",0),
            "🍞 PM (ordem)":       pbd.get("ord_pm",0),
            "🍭 Balas (tachos)":   pbd.get("ord_balas",0),
            "🍫 Doces (und)": pbd.get("cnt_doces_displays",0),
        }])
        st.dataframe(df_pbd, use_container_width=True, hide_index=True)
        if pbd.get("ord_amanha_obs"):
            st.info(f"📅 Amanhã: {pbd['ord_amanha_obs']}")

# ══════════════════════════════════════════════════════════════════
# ABA GIL
# ══════════════════════════════════════════════════════════════════
with aba_corte:
    st.subheader("🔪 Quadro de Corte — Gil")
    st.caption("Ordens de corte do dia (em bandejas). O realizado vira CORTADOS① no dia seguinte.")

    if not df_cocada.empty:
        st.markdown("##### 🍬 Corte de Cocada")
        df_cc = reord_cocada(df_cocada)[["sabor","ord_corte_45g","ord_corte_mini","ord_corte_pet"]].copy()
        df_cc.columns = ["Sabor","Ordem 45g","Ordem Mini","Ordem Pet"]
        df_cc = mask_zero_45g(df_cc, col_45g_name="Ordem 45g")
        col_t, col_ref = st.columns([3,1])
        with col_t:
            st.dataframe(df_styled(df_cc, estilo_azul, ["Sabor"]), use_container_width=True, hide_index=True)
            c1,c2,c3 = st.columns(3)
            c1.metric("Total 45g (band.)",  int(df_cocada["ord_corte_45g"].sum()))
            c2.metric("Total Mini (band.)", int(df_cocada["ord_corte_mini"].sum()))
            c3.metric("Total Pet (band.)",  int(df_cocada["ord_corte_pet"].sum()))
        with col_ref:
            st.info("**Rendimento:**\n\n• 1 band. 45g → 100 und\n• 1 band. Mini → 150 und\n• 1 band. Pet → 30 und (Z=60)")

        st.divider()
        st.markdown("##### 🌾 Corte de Palha")
        if not df_palha.empty:
            df_cp = reord_palha(df_palha)[["sabor","ord_corte_50g","ord_corte_pet"]].copy()
            df_cp.columns = ["Sabor","Ordem 50g","Ordem Pet"]
            df_cp_f = df_cp[df_cp[["Ordem 50g","Ordem Pet"]].sum(axis=1) > 0]
            if df_cp_f.empty:
                st.info("Nenhum corte de palha previsto.")
            else:
                st.dataframe(df_styled(df_cp_f, estilo_azul, ["Sabor"]),
                             use_container_width=True, hide_index=True)
    else:
        st.info("Sem ordens de corte para hoje.")

# ══════════════════════════════════════════════════════════════════
# ABA LEONÍLIA
# ══════════════════════════════════════════════════════════════════
with aba_embalagem:
    st.subheader("📦 Quadro de Embalagem")
    st.caption("Unidades a embalar (valores já em unidades, conforme ordem da Gestão).")

    if not df_cocada.empty:
        st.markdown("##### 🍬 Embalagem — Cocada")
        df_emb = reord_cocada(df_cocada)[["sabor","ord_emb_45g","ord_emb_mini"]].copy()
        df_emb.columns = ["Sabor","45g (und.)","Mini (und.)"]
        df_emb = mask_zero_45g(df_emb, col_45g_name="45g (und.)")

        col_el, col_ref2 = st.columns([2,1])
        with col_el:
            st.dataframe(df_styled(df_emb, estilo_azul, ["Sabor"]), use_container_width=True, hide_index=True)
            c1,c2 = st.columns(2)
            c1.metric("Pendente 45g (und.)",  f"{int(df_cocada['ord_emb_45g'].sum()):,}")
            c2.metric("Pendente Mini (und.)", f"{int(df_cocada['ord_emb_mini'].sum()):,}")
        with col_ref2:
            total = int(df_cocada["ord_emb_45g"].sum() + df_cocada["ord_emb_mini"].sum())
            if total == 0: st.success("✅ Embalagem em dia!")
            else: st.warning(f"**{total:,} unidades** pendentes")
            st.caption("📌 Ref:\n\n1 band. 45g = 100 und\n\n1 band. Mini = 150 und")

        st.divider()
        st.markdown("##### 🌾 Embalagem — Palha")
        if not df_palha.empty:
            df_ep = reord_palha(df_palha)[["sabor","emb_50g","emb_pet"]]
            df_ep.columns = ["Sabor","50g","Pet"]
            df_ep_f = df_ep[df_ep[["50g","Pet"]].sum(axis=1) > 0]
            if df_ep_f.empty: st.info("Nenhuma palha embalada registrada.")
            else: st.dataframe(df_styled(df_ep_f, estilo_azul, ["Sabor"]), use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados de embalagem para hoje.")

# ══════════════════════════════════════════════════════════════════
# ABA ESTOQUE
# ══════════════════════════════════════════════════════════════════
with aba_estoque:
    st.subheader("📊 Estoque Geral")
    if df_est.empty:
        st.info("Sem dados de estoque.")
    else:
        col_f1, col_f2 = st.columns([2,1])
        with col_f1: filtro = st.text_input("🔍 Filtrar produto", placeholder="Ex: TRAD, COC, PAL, MINI...")
        with col_f2: so_alertas = st.checkbox("Mostrar apenas em alerta", value=False)

        df_show = df_est.copy()
        if filtro: df_show = df_show[df_show["id_produto"].str.contains(filtro.upper(), na=False)]
        if so_alertas: df_show = df_show[df_show["alerta"].str.contains("GERAR", na=False)]
        df_show.columns = ["Produto","Em Estoque","Estoque Segurança","Status"]

        def estilo_status(val):
            if "GERAR" in str(val): return "background-color:rgba(254,202,202,0.6);color:#7f1d1d;font-weight:700;"
            if "OK" in str(val):    return "background-color:rgba(209,250,229,0.6);color:#065f46;font-weight:600;"
            return ""

        st.dataframe(df_show.style.map(estilo_status, subset=["Status"]), use_container_width=True, hide_index=True)

        c1,c2 = st.columns(2)
        c1.metric("✅ Produtos OK",       len(df_show[df_show["Status"].str.contains("OK",na=False)]))
        c2.metric("⚠️ Precisam produção", len(df_show[df_show["Status"].str.contains("GERAR",na=False)]))

# ══════════════════════════════════════════════════════════════════
# ABA ANÁLISE (Camada 1 — visualização de tendências)
# ══════════════════════════════════════════════════════════════════
with aba_analise:
    import analise
    analise.render()

st.divider()
st.caption(f"🍬 PCP Doces Vó Nena — v1.2 · {datetime.today().strftime('%d/%m/%Y %H:%M')} · Python + Streamlit + Postgres")
