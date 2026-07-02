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

# Bootstrap defensivo: entry point já faz, mas se essa página for aberta direto
# garante. HF Spaces não tem secrets.toml — try/except evita
# StreamlitSecretNotFoundError ao verificar `in st.secrets`.
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

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
import componentes

st.set_page_config(page_title="Painel • Doces Vó Nena", page_icon="", layout="wide", initial_sidebar_state="expanded")

# Tema visual centralizado (Inter font + paleta clean)
from ui_theme import aplicar_tema
aplicar_tema()

# init_db é idempotente — entry point já chamou, mas defensivo se a página
# for o primeiro hit do processo (cold start).
init_db()

# ── Helpers de quadro (quadro padrão do sistema, com destaque de célula) ─────────
# Cores de fundo da célula com valor > 0 (reproduzem o Painel antigo):
# laranja = Gestão/Produção · teal (verde/azul) = Cortados/Viradas/Corte/Embalagem.
COR_LARANJA = "rgba(192,86,33,0.18)"
COR_VERDE   = "rgba(14,116,144,0.18)"
COR_AZUL    = "rgba(14,116,144,0.16)"

def _fmt_cell(v):
    """Inteiro no padrão BR (1.234); preserva texto e o traço '—'.
    None/NaN viram '—' (o quadro esmaece) — sem isso, int(NaN) derruba a tela."""
    if v is None:
        return "—"
    if isinstance(v, str):
        return v
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if f != f or abs(f) == float("inf"):   # NaN é o único valor diferente de si mesmo
        return "—"
    if f == int(f):
        return f"{int(f):,}".replace(",", ".")
    return f"{f:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")

def quadro(df, cor_fundo=None, rotulos=("Sabor",), html_cols=None, altura_max=None):
    """Renderiza um quadro no padrão do sistema (tabela limpa + números à direita).

    Se `cor_fundo`, pinta o fundo da célula com valor > 0 e esmaece os zeros — igual
    ao destaque colorido do Painel antigo (negativos ficam neutros, como antes).
    `rotulos` = colunas de texto (sem cor, à esquerda). `html_cols` = colunas com
    HTML pronto (ex.: selo de status)."""
    if df is None or df.empty:
        st.info("Sem dados.")
        return
    rot = set(rotulos)
    html_set = set(html_cols or ())
    cols_val = [c for c in df.columns if c not in rot and c not in html_set]
    dfx = df.copy()
    for c in cols_val:
        dfx[c] = dfx[c].map(_fmt_cell)
    cc = None
    if cor_fundo:
        def cc(col, v, _cor=cor_fundo, _rot=rot, _html=html_set):
            if col in _rot or col in _html:
                return None
            s = str(v).strip()
            if s in ("", "—", "-"):
                return "color:rgba(0,0,0,0.25)"
            try:
                num = float(s.replace(".", "").replace(",", "."))
            except ValueError:
                return None
            if num > 0:
                return f"background-color:{_cor};color:#1a1a1a;font-weight:600"
            if num == 0:
                return "color:rgba(0,0,0,0.25)"
            return None
    componentes.tabela(dfx, altura_max=altura_max, cor_celula=cc,
                       cols_direita=cols_val, html_cols=list(html_set) or None)

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
@st.dialog("Produtos com Estoque Crítico", width="large")
def modal_alertas(df):
    st.markdown("Produtos **abaixo do estoque de segurança:**")
    quadro(df, rotulos=("Produto",))
    st.caption(f"Total: **{len(df)}** produtos em alerta")

# ── Carregar dados ─────────────────────────────────────────────────────────────
# Mostra a folha de hoje. Se não houver dados de hoje, cai pra última data registrada
# (útil enquanto o histórico está sendo digitalizado antes da folha do dia).
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
with col_t:
    st.title("PCP — Doces Vó Nena")
    st.caption("Visão operacional do dia por departamento.")
with col_d:
    if hoje == hoje_real:
        st.markdown(f"<div style='margin-top:14px;color:#C05621;font-weight:600;'>{datetime.today().strftime('%A, %d/%m/%Y').capitalize()}</div>", unsafe_allow_html=True)
    else:
        from datetime import datetime as _dt
        d_show = _dt.strptime(hoje, "%Y-%m-%d").strftime("%d/%m/%Y")
        st.markdown(f"<div style='margin-top:14px;color:#C05621;font-weight:600;'>Última folha registrada: {d_show}</div>", unsafe_allow_html=True)
with col_r:
    st.write("")
    if st.button("🔄 Atualizar", type="primary", width='stretch', help="Atualizar"): st.rerun()
st.divider()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Vó Nena")
    st.markdown("**Sistema PCP** — v1.2")
    st.divider()
    st.markdown("#### Estoque Crítico")
    alertas = [e for e in get_estoque() if "GERAR" in e.get("alerta","")]
    if not alertas:
        st.success("Tudo controlado!")
    else:
        st.warning(f"**{len(alertas)} produtos** precisam de produção!")
        if st.button("Ver lista completa", width='stretch'):
            df_al = pd.DataFrame(alertas)[["id_produto","stock_real","stock_seguranca"]]
            df_al.columns = ["Produto","Em Estoque","Meta"]
            modal_alertas(df_al)
    st.divider()
    st.caption("Atualizado em tempo real.\nUse 🔄 Atualizar para forçar atualização.")

# ── Abas ───────────────────────────────────────────────────────────────────────
aba_gestao, aba_producao, aba_corte, aba_embalagem, aba_estoque, aba_analise = st.tabs([
    "Gestão — Planejamento",
    "Produção",
    "Corte",
    "Embalagem",
    "Estoque",
    "Análise",
])

# ══════════════════════════════════════════════════════════════════
# ABA GESTÃO
# ══════════════════════════════════════════════════════════════════
with aba_gestao:

    with st.expander("Parâmetros e Metas Ideais — clique para consultar", expanded=False):
        s1,s2,s3,s4 = st.tabs(["45g (semanal)","Mini e Pet","Potes","Conversões"])
        with s1:
            st.caption("Semanas com feriado: adiantar produção no dia anterior.")
            df_m = pd.DataFrame(get_metas_45g())
            df_m.columns = ["Sabor","Segunda","Terça","Quarta","Quinta","Sexta"]
            quadro(df_m, COR_LARANJA)
        with s2:
            df_mp = pd.DataFrame(get_metas_mini_pet())
            df_mp.columns = ["Sabor","Mini (und)","Pet (und)"]
            quadro(df_mp, rotulos=("Sabor",))
        with s3:
            df_pt = pd.DataFrame(get_metas_potes())
            df_pt.columns = ["Sabor","Potes 260g","Potes 605g","Ref. Bandejas/dia"]
            quadro(df_pt, COR_LARANJA)
        with s4:
            df_cv = pd.DataFrame(get_conversoes())[["descricao","rende"]]
            df_cv.columns = ["Unidade","Rende"]
            componentes.tabela(df_cv)
            st.info("**Regra de ouro:** 1 Tacho = 8 Bandejas. Coluna Produção: sempre múltiplo de 8 (exceto ZERO).")

    st.subheader("Visão Geral do Dia")
    if not df_cocada.empty:
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Embalados 45g",   f"{df_cocada['emb_45g'].sum():,}")
        c2.metric("Embalados Mini",  f"{df_cocada['emb_mini'].sum():,}")
        c3.metric("Embalados Pet",   f"{df_cocada['emb_pet'].sum():,}")
        c4.metric("Bandejas produz.",f"{df_cocada['ord_prod_band'].sum()}")
        c5.metric("Cortados ① 45g",  f"{df_cocada['cort1_45g'].sum():,}")
    st.divider()

    st.subheader("Embalados — Cocada")
    if not df_cocada.empty:
        df_e = reord_cocada(df_cocada)[["sabor","emb_45g","emb_mini","emb_pet","emb_potes_260g","emb_potes_605g"]]
        df_e.columns = ["Sabor","45g","Mini","Pet","Potes 260g","Potes 605g"]
        df_e = mask_zero_45g(df_e)
        quadro(df_e, COR_LARANJA)

    st.subheader("Embalados — Palha")
    if not df_palha.empty:
        df_ep = reord_palha(df_palha)[["sabor","emb_50g","emb_pet"]]
        df_ep.columns = ["Sabor","50g","Pet"]
        quadro(df_ep, COR_LARANJA)
    st.divider()

    st.subheader("Cortados — Cocada")
    st.caption("① cortados hoje (lado embalagem) · ② = ① + Embalados + Produção · ③ = ② − Parâmetro Real (45g)")
    cort_data = calcular_cortados(hoje)
    if cort_data and not df_cocada.empty:
        df_c = pd.DataFrame(cort_data)[["sabor","c1_45g","c2_45g","c3_45g","c1_mini","c2_mini","c1_pet","c2_pet"]]
        df_c.columns = ["Sabor","①45g","②45g","③45g","①Mini","②Mini","①Pet","②Pet"]
        quadro(df_c, COR_VERDE)
    st.divider()

    st.subheader("Viradas e P/Virar")
    col_v, col_pv = st.columns(2)
    vp = calcular_viradas_pvirar(hoje)
    with col_v:
        st.caption("Viradas cocada: ① Produção · ② = ① − soma das ordens de corte")
        if vp:
            df_vir = pd.DataFrame(vp)[["sabor","vir1","vir2"]]
            df_vir.columns = ["Sabor","① Produção","② Pós-corte"]
            quadro(df_vir, COR_AZUL)
        if not df_palha.empty:
            df_palha_v = reord_palha(df_palha)[["sabor","cont_band_palha"]]
            df_palha_v.columns = ["Palha (sabor)","Bandejas"]
            df_palha_v_f = df_palha_v[df_palha_v["Bandejas"] > 0]
            if not df_palha_v_f.empty:
                st.caption("Coluna Palha (bandejas em contagem):")
                quadro(df_palha_v_f, rotulos=("Palha (sabor)",))
    with col_pv:
        st.caption("P/Virar: ① Produção · ② = ① + Viradas② · Meta = referência fixa por sabor")
        if vp:
            df_pv = pd.DataFrame(vp)[["sabor","pv1","pv2","pv_meta"]]
            df_pv.columns = ["Sabor","① Produção","② c/Viradas","Meta"]
            quadro(df_pv, COR_AZUL)
    st.divider()

    st.subheader("PM · Balas · Doces")
    if pbd:
        col_pm, col_b, col_d_col = st.columns(3)
        with col_pm:
            st.markdown("**Pão de Mel**")
            st.metric("Hoje (cnt)",   pbd.get("cnt_pm", 0))
            st.metric("Ordem do dia", pbd.get("ord_pm", 0))
        with col_b:
            st.markdown("**Balas**")
            st.metric("Hoje (cnt)",     pbd.get("cnt_balas", 0))
            balas_tachos = pbd.get("ord_balas", 0)
            st.metric("Ordem (tachos)", balas_tachos,
                      help=f"1 tacho = 30 balas → equivale a {balas_tachos*30} balas")
        with col_d_col:
            st.markdown("**Doces**")
            st.metric("Unidades", pbd.get("cnt_doces_displays", 0))
        if pbd.get("ord_amanha_obs"): st.info(f"Amanhã: {pbd['ord_amanha_obs']}")
        if pbd.get("obs"): st.info(f"{pbd['obs']}")

# ══════════════════════════════════════════════════════════════════
# ABA PRODUÇÃO
# ══════════════════════════════════════════════════════════════════
with aba_producao:
    st.subheader("Quadro de Produção")
    if not df_cocada.empty:
        col_j, col_l = st.columns([3,1])
        with col_j:
            df_joel = reord_cocada(df_cocada)[["sabor","ord_prod_band","ord_prod_virada","ord_prod_potes_260g","ord_prod_potes_605g"]]
            df_joel.columns = ["Sabor","Produção (band.)","Virada","Potes 260g","Potes 605g"]
            quadro(df_joel, COR_LARANJA)
            c1,c2 = st.columns(2)
            tot_band = int(df_cocada["ord_prod_band"].sum())
            c1.metric("Total bandejas", tot_band)
            c2.metric("Equiv. tachos (excl. Z)", f"{tot_band/8:.1f}")
        with col_l:
            st.markdown("**Lembretes / Amanhã**")
            lem = reord_cocada(df_cocada)[["sabor","amanha_obs"]]
            lem = lem[lem["amanha_obs"].astype(str).str.strip() != ""]
            if lem.empty: st.success("Nenhum lembrete.")
            else:
                for _, row in lem.iterrows(): st.info(f"**{row['sabor']}:** {row['amanha_obs']}")

    st.divider()
    st.subheader("Produção Palha")
    if not df_palha.empty:
        df_pp = reord_palha(df_palha)[["sabor","ord_prod_band"]]
        df_pp.columns = ["Sabor","Bandejas"]
        df_pp_f = df_pp[df_pp["Bandejas"] > 0]
        if df_pp_f.empty: st.info("Nenhuma produção de palha hoje.")
        else: quadro(df_pp_f, COR_LARANJA)

    st.divider()
    st.subheader("PM · Balas · Doces")
    if pbd:
        df_pbd = pd.DataFrame([{
            "PM (cnt)":         pbd.get("cnt_pm",0),
            "PM (ordem)":       pbd.get("ord_pm",0),
            "Balas (tachos)":   pbd.get("ord_balas",0),
            "Doces (und)": pbd.get("cnt_doces_displays",0),
        }])
        quadro(df_pbd, rotulos=())
        if pbd.get("ord_amanha_obs"):
            st.info(f"Amanhã: {pbd['ord_amanha_obs']}")

# ══════════════════════════════════════════════════════════════════
# ABA CORTE
# ══════════════════════════════════════════════════════════════════
with aba_corte:
    st.subheader("Quadro de Corte")
    st.caption("Ordens de corte do dia (em bandejas). O realizado vira Cortados① no dia seguinte.")

    if not df_cocada.empty:
        st.markdown("##### Corte de Cocada")
        df_cc = reord_cocada(df_cocada)[["sabor","ord_corte_45g","ord_corte_mini","ord_corte_pet"]].copy()
        df_cc.columns = ["Sabor","Ordem 45g","Ordem Mini","Ordem Pet"]
        df_cc = mask_zero_45g(df_cc, col_45g_name="Ordem 45g")
        col_t, col_ref = st.columns([3,1])
        with col_t:
            quadro(df_cc, COR_AZUL)
            c1,c2,c3 = st.columns(3)
            c1.metric("Total 45g (band.)",  int(df_cocada["ord_corte_45g"].sum()))
            c2.metric("Total Mini (band.)", int(df_cocada["ord_corte_mini"].sum()))
            c3.metric("Total Pet (band.)",  int(df_cocada["ord_corte_pet"].sum()))
        with col_ref:
            st.info("**Rendimento:**\n\n• 1 band. 45g → 100 und\n• 1 band. Mini → 150 und\n• 1 band. Pet → 30 und (Z=60)")

        st.divider()
        st.markdown("##### Corte de Palha")
        if not df_palha.empty:
            df_cp = reord_palha(df_palha)[["sabor","ord_corte_50g","ord_corte_pet"]].copy()
            df_cp.columns = ["Sabor","Ordem 50g","Ordem Pet"]
            df_cp_f = df_cp[df_cp[["Ordem 50g","Ordem Pet"]].sum(axis=1) > 0]
            if df_cp_f.empty:
                st.info("Nenhum corte de palha previsto.")
            else:
                quadro(df_cp_f, COR_AZUL)
    else:
        st.info("Sem ordens de corte para hoje.")

# ══════════════════════════════════════════════════════════════════
# ABA EMBALAGEM
# ══════════════════════════════════════════════════════════════════
with aba_embalagem:
    st.subheader("Quadro de Embalagem")
    st.caption("Unidades a embalar (valores já em unidades, conforme ordem da Gestão).")

    if not df_cocada.empty:
        st.markdown("##### Embalagem — Cocada")
        df_emb = reord_cocada(df_cocada)[["sabor","ord_emb_45g","ord_emb_mini"]].copy()
        df_emb.columns = ["Sabor","45g (und.)","Mini (und.)"]
        df_emb = mask_zero_45g(df_emb, col_45g_name="45g (und.)")

        col_el, col_ref2 = st.columns([2,1])
        with col_el:
            quadro(df_emb, COR_AZUL)
            c1,c2 = st.columns(2)
            c1.metric("Pendente 45g (und.)",  f"{int(df_cocada['ord_emb_45g'].sum()):,}")
            c2.metric("Pendente Mini (und.)", f"{int(df_cocada['ord_emb_mini'].sum()):,}")
        with col_ref2:
            total = int(df_cocada["ord_emb_45g"].sum() + df_cocada["ord_emb_mini"].sum())
            if total == 0: st.success("Embalagem em dia!")
            else: st.warning(f"**{total:,} unidades** pendentes")
            st.caption("Ref:\n\n1 band. 45g = 100 und\n\n1 band. Mini = 150 und")

        st.divider()
        st.markdown("##### Embalagem — Palha")
        if not df_palha.empty:
            df_ep = reord_palha(df_palha)[["sabor","emb_50g","emb_pet"]]
            df_ep.columns = ["Sabor","50g","Pet"]
            df_ep_f = df_ep[df_ep[["50g","Pet"]].sum(axis=1) > 0]
            if df_ep_f.empty: st.info("Nenhuma palha embalada registrada.")
            else: quadro(df_ep_f, COR_AZUL)
    else:
        st.info("Sem dados de embalagem para hoje.")

# ══════════════════════════════════════════════════════════════════
# ABA ESTOQUE
# ══════════════════════════════════════════════════════════════════
with aba_estoque:
    st.subheader("Estoque Geral")
    if df_est.empty:
        st.info("Sem dados de estoque.")
    else:
        col_f1, col_f2 = st.columns([2,1])
        with col_f1: filtro = st.text_input("Filtrar produto", placeholder="Ex: TRAD, COC, PAL, MINI...")
        with col_f2: so_alertas = st.checkbox("Mostrar apenas em alerta", value=False)

        df_show = df_est.copy()
        if filtro: df_show = df_show[df_show["id_produto"].str.contains(filtro.upper(), na=False)]
        if so_alertas: df_show = df_show[df_show["alerta"].str.contains("GERAR", na=False)]
        df_show.columns = ["Produto","Em Estoque","Estoque Segurança","Status"]
        df_show["Status"] = df_show["Status"].map(
            lambda s: componentes.selo(str(s), "danger" if "GERAR" in str(s) else "ok"))
        quadro(df_show, rotulos=("Produto",), html_cols=["Status"])

        c1,c2 = st.columns(2)
        c1.metric("Produtos OK",       len(df_show[df_show["Status"].str.contains("OK",na=False)]))
        c2.metric("Precisam produção", len(df_show[df_show["Status"].str.contains("GERAR",na=False)]))

# ══════════════════════════════════════════════════════════════════
# ABA ANÁLISE (Camada 1 — visualização de tendências)
# ══════════════════════════════════════════════════════════════════
with aba_analise:
    import analise
    analise.render()

st.divider()
st.caption(f"PCP Doces Vó Nena — v1.2 · {datetime.today().strftime('%d/%m/%Y %H:%M')} · Python + Streamlit + Postgres")
