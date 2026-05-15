"""
pages/2_Insights.py — Diagnóstico operacional automático

Página que mostra SINAIS detectados pelo sistema ao analisar todas as folhas
registradas. Linguagem do chão de fábrica, sem jargão técnico.

⚠️ Após questionário 15/05/2026 com a Gestão, vários sinais foram recalibrados:
   - Insight Master: NÃO é desbalanceamento confirmado — pode ser viés de amostra
     + reflexo dos ajustes antecipados de pedido embutidos no param_real.
   - H1 Tachos parciais: NÃO é desperdício — sobra do tacho vira pote 260g/605g.
   - H4 Embalagem: capacidade NÃO é fixa em 3000 — varia conforme equipe do dia.
   - H5 Anomalia palha: validado pela Gestão — manter detecção.

Atualiza automaticamente conforme novas folhas entram no banco.

Cálculos rodam em memória com cache de 60s. Para refresh manual, recarregar a página.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Bootstrap defensivo (entry point já fez, mas se a página for o primeiro hit, garante)
if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
    os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from cached_db import (
    list_datas_folha, get_folha_cocada, get_folha_palha, get_papelzinho_joel,
    SABORES_COCADA,
)

st.set_page_config(
    page_title="Insights • Doces Vó Nena",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sora', sans-serif; font-size: 14px; }
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    h1, h2, h3 { color: #C05621; font-weight: 700; }
    section[data-testid="stSidebar"] { background-color: #1C1410; }
    section[data-testid="stSidebar"] * { color: #F5E6D3 !important; }
    [data-testid="metric-container"] {
        background: #FFF8F2; border: 1px solid #F7EDE2;
        border-radius: 10px; padding: 12px 18px;
    }
    [data-testid="metric-container"] label {
        color: #7B341E !important; font-size: 13px !important; font-weight: 600 !important;
    }
    .insight-card-master {
        background: linear-gradient(135deg, #FFF8F2 0%, #FEF3C7 100%);
        border-left: 6px solid #C05621;
        border-radius: 8px;
        padding: 20px 24px;
        margin: 12px 0 20px 0;
    }
    .insight-card-warning {
        background: #FEF2F2;
        border-left: 5px solid #B91C1C;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .insight-card-good {
        background: #ECFDF5;
        border-left: 5px solid #059669;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .insight-card-info {
        background: #EFF6FF;
        border-left: 5px solid #2563EB;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .pergunta-eraldo {
        background: #FFFBEB;
        border: 1px dashed #D97706;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 6px 0;
        font-style: italic;
        color: #92400E;
    }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CÁLCULOS — funções puras, sem Streamlit dentro
# ════════════════════════════════════════════════════════════════════════════
def _calc_tachos_parciais(datas, folhas_cocada):
    """H1 — ordens com ord_prod_band fora dos múltiplos de tacho."""
    total = 0
    parciais = []
    for d in datas:
        for s in SABORES_COCADA:
            fc = folhas_cocada[d].get(s, {})
            band = fc.get("ord_prod_band") or 0
            if band == 0:
                continue
            modulo = 3 if s == "ZERO" else 8
            total += 1
            sobra = band % modulo
            if sobra != 0:
                parciais.append({
                    "data": d,
                    "sabor": s,
                    "bandejas": band,
                    "tachos_cheios": band // modulo,
                    "sobra_band": sobra,
                    "falta_pra_completar": modulo - sobra,
                })
    pct = (len(parciais) / total * 100) if total else 0
    return {"total": total, "parciais": parciais, "pct": pct}


def _calc_terceiro_por_sabor(datas, folhas_cocada, papelzinhos):
    """H2 — soma e média de Cortados ③ por sabor/tamanho."""
    soma_3 = {s: {"45g": 0, "Mini": 0, "Pet": 0,
                  "n_45g": 0, "n_mini": 0, "n_pet": 0} for s in SABORES_COCADA}

    for d in datas:
        for s in SABORES_COCADA:
            fc = folhas_cocada[d].get(s, {})
            pj = papelzinhos[d].get(s, {})

            c2_45 = (fc.get("cort1_45g") or 0) + (fc.get("emb_45g") or 0) + (pj.get("joel_45g") or 0)
            c2_mi = (fc.get("cort1_mini") or 0) + (fc.get("emb_mini") or 0) + (pj.get("joel_mini") or 0)
            rend_pet = 60 if s == "ZERO" else 30
            joel_pet_und = (pj.get("joel_pet") or 0) * rend_pet
            c2_pt = (fc.get("cort1_pet") or 0) + (fc.get("emb_pet") or 0) + joel_pet_und

            p_45 = fc.get("param_real_45g") or 0
            p_mi = fc.get("param_real_mini") or 0
            p_pt = fc.get("param_real_pet") or 0

            if p_45 > 0 and s != "ZERO":
                soma_3[s]["45g"]  += (c2_45 - p_45)
                soma_3[s]["n_45g"] += 1
            if p_mi > 0:
                soma_3[s]["Mini"] += (c2_mi - p_mi)
                soma_3[s]["n_mini"] += 1
            if p_pt > 0:
                soma_3[s]["Pet"]  += (c2_pt - p_pt)
                soma_3[s]["n_pet"] += 1

    # Achata em lista
    flat = []
    for s in SABORES_COCADA:
        r = soma_3[s]
        for tam, key_n in [("45g", "n_45g"), ("Mini", "n_mini"), ("Pet", "n_pet")]:
            n = r[key_n]
            if n > 0:
                media = r[tam] / n
                flat.append({
                    "sabor": s, "tamanho": tam,
                    "soma": r[tam], "media": media, "n_folhas": n,
                })
    return {"por_sabor": soma_3, "flat": flat}


def _calc_anomalias_palha(datas, folhas_palha, fator=1.3):
    """H5 — Leite em Pó > Tradicional × 1.3 nas ordens de produção."""
    anomalias = []
    for d in datas:
        fp_t = folhas_palha[d].get("TRADICIONAL", {})
        fp_l = folhas_palha[d].get("LEITE EM PÓ", {})
        t_band = fp_t.get("ord_prod_band") or 0
        l_band = fp_l.get("ord_prod_band") or 0
        if t_band > 0 and l_band > t_band * fator:
            anomalias.append({
                "data": d, "tradicional": t_band, "leite_po": l_band,
                "razao": l_band / t_band,
            })
    return {"anomalias": anomalias, "fator_usado": fator}


def _calc_sobrecarga_embalagem(datas, folhas_cocada, capacidade=3000):
    """H4 — soma ord_emb_* por dia, compara com capacidade da Embalagem."""
    rows = []
    for d in datas:
        e45 = sum((folhas_cocada[d].get(s, {}).get("ord_emb_45g") or 0) for s in SABORES_COCADA)
        emi = sum((folhas_cocada[d].get(s, {}).get("ord_emb_mini") or 0) for s in SABORES_COCADA)
        total = e45 + emi
        rows.append({"data": d, "emb_45g": e45, "emb_mini": emi, "total": total, "vs_meta": total - capacidade})
    sobrecarga = [r for r in rows if r["vs_meta"] > 0]
    return {"todas": rows, "sobrecarga": sobrecarga, "capacidade": capacidade}


def _calc_proporcao_45g(datas, folhas_cocada):
    """H6 — razão T/L e T/(B+C+P) por folha, baseada em EMBALADOS."""
    rows = []
    for d in datas:
        t   = folhas_cocada[d].get("TRADICIONAL", {}).get("emb_45g") or 0
        l   = folhas_cocada[d].get("LEITE CONDENSADO", {}).get("emb_45g") or 0
        bcp = sum((folhas_cocada[d].get(s, {}).get("emb_45g") or 0) for s in ("BRIGADEIRO", "CAFÉ", "PÉ DE MOÇA"))
        tl   = (t / l) if l else None
        tbcp = (t / bcp) if bcp else None
        rows.append({"data": d, "T": t, "L": l, "B+C+P": bcp, "T/L": tl, "T/(B+C+P)": tbcp})
    return {"rows": rows}


# ════════════════════════════════════════════════════════════════════════════
# ORQUESTRADOR — carrega dados + chama todas as análises
# ════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60, show_spinner="🔍 Recalculando insights...")
def calcular_todos_insights():
    """Carrega tudo do banco UMA vez, roda as 6 análises, retorna dict."""
    datas = sorted(list_datas_folha())
    if not datas:
        return None

    folhas_cocada = {d: {r["sabor"]: r for r in get_folha_cocada(d)} for d in datas}
    folhas_palha  = {d: {r["sabor"]: r for r in get_folha_palha(d)}  for d in datas}
    papelzinhos   = {d: {r["sabor"]: r for r in get_papelzinho_joel(d)} for d in datas}

    return {
        "datas": datas,
        "n_folhas": len(datas),
        "primeira": datas[0],
        "ultima": datas[-1],
        "h1": _calc_tachos_parciais(datas, folhas_cocada),
        "h2": _calc_terceiro_por_sabor(datas, folhas_cocada, papelzinhos),
        "h4": _calc_sobrecarga_embalagem(datas, folhas_cocada),
        "h5": _calc_anomalias_palha(datas, folhas_palha),
        "h6": _calc_proporcao_45g(datas, folhas_cocada),
    }


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO + DADOS
# ════════════════════════════════════════════════════════════════════════════
st.title("🔍 Insights & Diagnóstico")
st.caption(
    "Sinais que o sistema detectou ao analisar todas as folhas registradas. "
    "Atualiza sozinho quando novas folhas entram. "
    "⚠️ **Importante:** sinais ≠ diagnósticos confirmados. "
    "Cada achado é uma pista pra investigar com a Gestão — não conclusão fechada."
)

dados = calcular_todos_insights()

if dados is None:
    st.warning("⚠️ Ainda não há folhas no banco. Cadastre algumas em Lançamento antes.")
    st.stop()

# Cabeçalho com período analisado
col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("📋 Folhas analisadas", dados["n_folhas"])
col_b.metric("📅 Primeira", datetime.strptime(dados["primeira"], "%Y-%m-%d").strftime("%d/%m/%Y"))
col_c.metric("📅 Última", datetime.strptime(dados["ultima"], "%Y-%m-%d").strftime("%d/%m/%Y"))
# Conta sabores com ③ médio significativo
flat_h2 = dados["h2"]["flat"]
n_alertas = sum(1 for r in flat_h2 if abs(r["media"]) > 100)
col_d.metric("🔎 Sabores com sinal forte", n_alertas, help="③ médio acima de ±100 und/dia — pista pra investigar, não diagnóstico confirmado")

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# 1. INSIGHT MASTER — Sinal detectado (validar com mais dados)
# ════════════════════════════════════════════════════════════════════════════
st.header("🎯 Padrão detectado — possível viés por sabor (a validar)")

st.markdown(
    f"<div class='insight-card-master'>"
    f"<b style='font-size:18px;color:#7B341E;'>O sistema detectou um sinal nas {dados['n_folhas']} folhas analisadas:</b><br><br>"
    f"Alguns sabores aparecem com Cortados ③ médio <b>persistentemente negativo</b> (produção abaixo do parâmetro real), "
    f"outros com ③ médio <b>persistentemente positivo</b> (produção acima do parâmetro real). "
    f"<br><br>"
    f"<b>⚠️ Importante:</b> a Gestão confirmou (15/05/2026) que <b>NÃO sente</b> esse desbalanceamento na prática. "
    f"Esse sinal pode ser:<br>"
    f"&nbsp;&nbsp;• <b>Viés de amostra pequena</b> (só {dados['n_folhas']} folhas — precisa de 60-90 pra estabilizar)<br>"
    f"&nbsp;&nbsp;• <b>Reflexo dos ajustes antecipados</b> da Gestão: o <code>param_real</code> do dia já embute pedidos da semana seguinte, então a produção 'atrasa' em relação ao parâmetro inflado.<br><br>"
    f"<b>Tratar como pista pra investigar, não como conclusão fechada.</b>"
    f"</div>",
    unsafe_allow_html=True,
)

# Dados pro gráfico
df_h2 = pd.DataFrame(flat_h2)
df_h2 = df_h2.sort_values("media", ascending=True)

# Gráfico de barras horizontais ordenadas
fig_h2 = go.Figure()
cores = ["#B91C1C" if v < -100 else ("#059669" if v > 100 else "#9CA3AF") for v in df_h2["media"]]
fig_h2.add_trace(go.Bar(
    y=[f"{r['sabor']} {r['tamanho']}" for _, r in df_h2.iterrows()],
    x=df_h2["media"],
    orientation="h",
    marker_color=cores,
    text=[f"{v:+.0f} und/dia" for v in df_h2["media"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Média: %{x:+.0f} und/dia<extra></extra>",
))
fig_h2.update_layout(
    title="③ médio por sabor/tamanho — vermelho = abaixo do param_real · verde = acima",
    xaxis_title="Cortados ③ médio (unidades/dia útil)",
    yaxis_title="",
    height=420,
    margin=dict(l=20, r=80, t=60, b=40),
    showlegend=False,
    plot_bgcolor="white",
)
fig_h2.add_vline(x=0, line_width=2, line_color="#1a1a1a")
st.plotly_chart(fig_h2, use_container_width=True, config={"displayModeBar": False, "responsive": True})

# Tabela com soma + média + n
df_h2_tab = df_h2.copy()
df_h2_tab["soma"] = df_h2_tab["soma"].apply(lambda v: f"{v:+,.0f}")
df_h2_tab["media"] = df_h2_tab["media"].apply(lambda v: f"{v:+,.0f}")
df_h2_tab.columns = ["Sabor", "Tamanho", "Total acumulado (und)", "Média por dia (und)", "Folhas medidas"]

with st.expander("📊 Ver tabela completa", expanded=False):
    st.dataframe(df_h2_tab, use_container_width=True, hide_index=True)

# Caixa "Como ler os números"
st.markdown(
    "<div class='insight-card-info'>"
    "<b>🔵 Como ler os números:</b><br>"
    "• Média <b>negativa</b> (vermelho) → produção média ficou <b>abaixo</b> do <code>param_real</code> nas folhas analisadas.<br>"
    "• Média <b>positiva</b> (verde) → produção média ficou <b>acima</b> do <code>param_real</code> nas folhas analisadas.<br>"
    "• O <code>param_real</code> não é fixo — varia diariamente conforme a Gestão antecipa pedidos da semana seguinte. Por isso o sinal aqui é sensível a quando o pedido foi distribuído e quando a produção alcançou."
    "</div>",
    unsafe_allow_html=True,
)

# Já respondido pela Gestão (15/05/2026)
st.markdown(
    "<div class='insight-card-good'>"
    "<b>✅ Já discutido com a Gestão (15/05/2026):</b><br>"
    "• <i>\"Eu não sinto Pé de Moça sobrando — talvez pareça por sempre ter no estoque acima, mas não tem me incomodado.\"</i><br>"
    "• <i>\"A proporção T/L oscila porque eu antecipo pedidos da semana seguinte distribuindo entre os dias — não é capacidade, é planejamento.\"</i><br>"
    "→ Recalibrado: este achado vira <b>sinal pra acompanhar</b>, não diagnóstico confirmado. Reavaliar quando houver 60+ folhas."
    "</div>",
    unsafe_allow_html=True,
)

# Perguntas que continuam abertas
st.markdown("#### 💬 Ainda em aberto pra acompanhar")
perguntas_master = [
    "O padrão se mantém quando temos 60+ folhas, ou some quando a amostra cresce?",
    "Os ajustes antecipados (param_real − base) deveriam aparecer marcados na folha com origem do pedido (cliente X, semana Y)?",
    "Quando o sistema mostrar 'sinal forte', a Gestão prefere ver no Insights ou no Painel do dia?",
]
for p in perguntas_master:
    st.markdown(f"<div class='pergunta-eraldo'>❓ {p}</div>", unsafe_allow_html=True)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# 2. TACHOS PARCIAIS
# ════════════════════════════════════════════════════════════════════════════
h1 = dados["h1"]
st.header(f"🥥 Tachos parciais — conversão para potes ({h1['pct']:.0f}% das ordens)")

st.markdown(
    f"<div class='insight-card-info'>"
    f"<b>De {h1['total']} ordens de produção, {len(h1['parciais'])} têm bandejas que não fecham tacho cheio.</b><br><br>"
    f"Cada tacho rende 8 bandejas (3 no Zero). Quando a Gestão ordena 18 em vez de 16 ou 24, "
    f"a sobra do último tacho <b>não é perdida</b> — vai pra <b>potes 260g ou 605g</b> do mesmo sabor. "
    f"Confirmado pela Gestão (15/05/2026): <i>\"o resto do tacho vai pros potes\"</i>."
    f"</div>",
    unsafe_allow_html=True,
)

if h1["parciais"]:
    df_h1 = pd.DataFrame(h1["parciais"])
    df_h1["data"] = pd.to_datetime(df_h1["data"]).dt.strftime("%d/%m/%Y")
    df_h1.columns = ["Data", "Sabor", "Bandejas ordenadas", "Tachos cheios", "Sobra (band) → potes", "Pra fechar próximo tacho"]
    st.dataframe(df_h1, use_container_width=True, hide_index=True)

st.markdown(
    "<div class='insight-card-good'>"
    "<b>✅ Decisão intencional, não desperdício.</b> Tacho parcial é estratégia da Gestão pra balancear "
    "bandejas (45g/Mini/Pet) <b>e</b> potes 260g/605g no mesmo dia, com a mesma massa do tacho. Sem perda de ingrediente."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='insight-card-info'>"
    "<b>💡 Melhoria futura (UX):</b> quando a Gestão lançar <code>ord_prod_band = 18</code>, mostrar ao lado: "
    "<i>\"18 = 2 tachos cheios (16 band) + sobra do 3º tacho (~10 kg de massa) — sugestão de pote: 605g × Y ou 260g × Z\"</i>. "
    "Informativo, não impositivo."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("#### 💬 Em aberto pra acompanhar")
for p in [
    "Mistério dos 36 kg de Pé de Moça vs apenas 30 potes 260g (15/05) — pra onde foram os outros 28 kg?",
    "Sistema deveria sugerir automaticamente ord_prod_potes a partir da sobra do tacho parcial?",
]:
    st.markdown(f"<div class='pergunta-eraldo'>❓ {p}</div>", unsafe_allow_html=True)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# 3. ANOMALIAS PALHA
# ════════════════════════════════════════════════════════════════════════════
h5 = dados["h5"]
st.header(f"🌾 Palha — {len(h5['anomalias'])} dia(s) com Leite em Pó dominando")

if h5["anomalias"]:
    st.markdown(
        f"<div class='insight-card-warning'>"
        f"<b>Em {len(h5['anomalias'])} dia(s), a ordem de Palha Leite em Pó ultrapassou Tradicional em mais de 30%.</b><br><br>"
        f"Normalmente Tradicional é o sabor mais pedido. Quando Leite em Pó passa muito, costuma ser encomenda especial."
        f"</div>",
        unsafe_allow_html=True,
    )

    df_h5 = pd.DataFrame(h5["anomalias"])
    df_h5["data"] = pd.to_datetime(df_h5["data"]).dt.strftime("%d/%m/%Y")
    df_h5["razao"] = df_h5["razao"].apply(lambda v: f"{v:.2f}x")
    df_h5.columns = ["Data", "Tradicional (band)", "Leite em Pó (band)", "Razão L/T"]
    st.dataframe(df_h5, use_container_width=True, hide_index=True)

    st.markdown(
        "<div class='insight-card-good'>"
        "<b>✅ Detecção validada pela Gestão (15/05/2026):</b> "
        "<i>\"Sim, me parece que nesses dias realmente foi maior. É interessante que o sistema sempre entregue isso.\"</i><br>"
        "Manter este alerta ativo — é exatamente o tipo de sinal que vale acompanhar."
        "</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<div class='insight-card-good'>"
        "✅ Nenhuma anomalia de palha detectada no período. Tradicional continua dominando, como esperado."
        "</div>",
        unsafe_allow_html=True,
    )

if h5["anomalias"]:
    st.markdown("#### 💬 Em aberto pra acompanhar")
    for p in [
        "Quando o sistema detectar nova anomalia, vale notificar a Gestão imediatamente (push/email) ou só ao abrir o app?",
        "Existe lista de encomendas grandes esperadas (cliente X pede Y palha LP toda quinta)?",
    ]:
        st.markdown(f"<div class='pergunta-eraldo'>❓ {p}</div>", unsafe_allow_html=True)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# 4. SOBRECARGA EMBALAGEM
# ════════════════════════════════════════════════════════════════════════════
h4 = dados["h4"]
st.header("📦 Embalagem — capacidade VARIÁVEL (ajustar conforme equipe do dia)")

# Capacidade configurável — a Gestão confirmou (15/05/2026) que não é fixa: varia
# com quantas pessoas estão embalando e a velocidade individual de cada uma.
cap = st.slider(
    "Capacidade de embalagem assumida para este alerta (und/dia)",
    min_value=800, max_value=5000,
    value=int(h4["capacidade"]),
    step=100,
    help="Variável conforme quem está embalando. Padrão 3000 (1 pessoa rápida). "
         "Reduza pra ~1500 quando só há 1 embalador devagar; suba pra 4000+ quando equipe completa.",
)

# Recalcula sobrecarga com a capacidade escolhida (sem ir ao banco de novo)
sobrecarga_dinamica = [r for r in h4["todas"] if r["total"] > cap]

st.markdown(
    f"<div class='insight-card-info'>"
    f"<b>Capacidade NÃO é fixa.</b> A Gestão confirmou (15/05/2026): "
    f"<i>\"a capacidade de 3000 não é fixa, varia — às vezes tem mais pessoas, ou pessoas com capacidade maior\"</i>.<br><br>"
    f"Com a capacidade atual de <b>{cap:,} und/dia</b>, <b>{len(sobrecarga_dinamica)} dia(s)</b> "
    f"do histórico passariam do limite."
    f"</div>",
    unsafe_allow_html=True,
)

if sobrecarga_dinamica:
    df_h4 = pd.DataFrame(sobrecarga_dinamica)
    df_h4["data"] = pd.to_datetime(df_h4["data"]).dt.strftime("%d/%m/%Y")
    df_h4 = df_h4.copy()
    df_h4["acima"] = df_h4["total"] - cap
    df_h4 = df_h4[["data", "emb_45g", "emb_mini", "total", "acima"]]
    df_h4["acima"] = df_h4["acima"].apply(lambda v: f"+{v:,}")
    df_h4.columns = ["Data", "45g (und)", "Mini (und)", "Total", "Acima do limite assumido"]
    st.dataframe(df_h4, use_container_width=True, hide_index=True)
else:
    st.markdown(
        "<div class='insight-card-good'>"
        "✅ Nenhum dia do histórico ultrapassa essa capacidade. "
        "Mova o slider pra baixo (ex: 1800) pra simular dias com equipe reduzida."
        "</div>",
        unsafe_allow_html=True,
    )

# Gráfico de embalagem ao longo do tempo
df_emb_all = pd.DataFrame(h4["todas"])
df_emb_all["data"] = pd.to_datetime(df_emb_all["data"])
df_emb_all = df_emb_all.sort_values("data")
fig_h4 = go.Figure()
fig_h4.add_trace(go.Bar(
    x=df_emb_all["data"], y=df_emb_all["emb_45g"],
    name="45g (und)", marker_color="#C05621",
))
fig_h4.add_trace(go.Bar(
    x=df_emb_all["data"], y=df_emb_all["emb_mini"],
    name="Mini (und)", marker_color="#7B341E",
))
fig_h4.add_hline(
    y=cap, line_dash="dash", line_color="#B91C1C",
    annotation_text=f"Capacidade assumida ≈ {cap:,}", annotation_position="top right",
)
fig_h4.update_layout(
    title="Ordens de embalagem por dia",
    barmode="stack",
    xaxis_title="Data",
    yaxis_title="Unidades a embalar",
    height=380,
    margin=dict(l=20, r=20, t=60, b=40),
    plot_bgcolor="white",
)
st.plotly_chart(fig_h4, use_container_width=True, config={"displayModeBar": False, "responsive": True})

st.markdown("#### 💬 Em aberto pra acompanhar")
for p in [
    "Faz sentido a folha ter um campo 'embaladores presentes hoje' pra capacidade ser calculada automaticamente?",
    "Existe registro de quanto cada pessoa embala em média (Popô × Leonília × extras)?",
    "Hora extra da Embalagem é registrada em algum lugar (papel, sistema, planilha)?",
]:
    st.markdown(f"<div class='pergunta-eraldo'>❓ {p}</div>", unsafe_allow_html=True)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# 5. PROPORÇÃO 45g AO LONGO DO TEMPO (visualizar H6 graficamente)
# ════════════════════════════════════════════════════════════════════════════
st.header("📈 Proporção Tradicional / Leite Condensado ao longo do tempo")

st.caption(
    "A regra base da Gestão prescreve **T/L = 2.0** (T = 2× L em 45g). "
    "Oscilações fora da banda 1.8–2.2 **não significam desbalanceamento automaticamente** — "
    "podem refletir pedidos antecipados de cliente distribuídos pelos dias da semana "
    "(confirmado pela Gestão 15/05/2026). Trate como contexto, não diagnóstico."
)

df_h6 = pd.DataFrame(dados["h6"]["rows"])
df_h6["data"] = pd.to_datetime(df_h6["data"])
df_h6 = df_h6.sort_values("data")
df_h6_valid = df_h6.dropna(subset=["T/L"])

if not df_h6_valid.empty:
    fig_h6 = go.Figure()
    fig_h6.add_trace(go.Scatter(
        x=df_h6_valid["data"], y=df_h6_valid["T/L"],
        mode="lines+markers",
        line=dict(color="#C05621", width=3),
        marker=dict(size=8, color="#7B341E"),
        name="T/L observada",
    ))
    # Banda aceitável (1.8 - 2.2)
    fig_h6.add_hrect(
        y0=1.8, y1=2.2,
        fillcolor="#059669", opacity=0.15,
        line_width=0,
        annotation_text="Banda aceitável (1.8 – 2.2)", annotation_position="top left",
    )
    fig_h6.add_hline(
        y=2.0, line_dash="dash", line_color="#059669",
        annotation_text="Meta = 2.0", annotation_position="bottom right",
    )
    fig_h6.update_layout(
        title="Razão T/L (Embalados 45g) — esperado: 2.0",
        xaxis_title="Data",
        yaxis_title="Razão T/L",
        height=380,
        margin=dict(l=20, r=20, t=60, b=40),
        plot_bgcolor="white",
        showlegend=False,
    )
    st.plotly_chart(fig_h6, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    # Estatísticas
    media_tl = df_h6_valid["T/L"].mean()
    min_tl = df_h6_valid["T/L"].min()
    max_tl = df_h6_valid["T/L"].max()
    fora_banda = df_h6_valid[(df_h6_valid["T/L"] < 1.8) | (df_h6_valid["T/L"] > 2.2)].shape[0]
    pct_fora = (fora_banda / len(df_h6_valid)) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Média observada", f"{media_tl:.2f}", help="Esperado: 2.00")
    c2.metric("Mínima", f"{min_tl:.2f}")
    c3.metric("Máxima", f"{max_tl:.2f}")
    c4.metric("Folhas fora da banda", f"{fora_banda} de {len(df_h6_valid)}", help=f"{pct_fora:.0f}% dos dias")

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# 6. LEAD TIME — INCONCLUSIVO POR ENQUANTO
# ════════════════════════════════════════════════════════════════════════════
st.header("⏱️ Lead time da cocada (P/Virar → Cortados)")

# Conta pares de 3 dias
datas = dados["datas"]
def _dias_entre(d1, d2):
    dd1 = datetime.strptime(d1, "%Y-%m-%d").date()
    dd2 = datetime.strptime(d2, "%Y-%m-%d").date()
    return (dd2 - dd1).days

pares_3d = []
for i, d1 in enumerate(datas):
    for d2 in datas[i+1:]:
        delta = _dias_entre(d1, d2)
        if delta == 3:
            pares_3d.append((d1, d2))
        elif delta > 3:
            break

st.markdown(
    f"<div class='insight-card-info'>"
    f"<b>Lead time teórico da cocada:</b> 3 dias (tacho → virar → virada → cortar).<br><br>"
    f"Pra validar com dado real, o sistema precisa comparar P/Virar do dia D com Cortados① do dia D+3 — mas só temos "
    f"<b>{len(pares_3d)} pares</b> de dias com 3 dias entre eles preenchidos completamente. "
    f"Amostra ainda <b>pequena demais</b> pra conclusão estatística confiável."
    f"</div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='insight-card-good'>"
    "<b>✅ Próximo passo:</b> manter folhas completas por 2-3 semanas seguidas. "
    "Quando tiver ~15+ pares de D / D+3, esse gráfico mostra se o lead time real é 3 dias mesmo, ou se varia (e por quê)."
    "</div>",
    unsafe_allow_html=True,
)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# RODAPÉ
# ════════════════════════════════════════════════════════════════════════════
st.caption(
    f"🔍 Análise gerada automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
    f"baseada em {dados['n_folhas']} folhas registradas · "
    f"atualizada a cada 60 segundos ou quando nova folha é salva."
)
st.caption(
    "💡 Esta página mostra **sinais a investigar** — não conclusões fechadas. "
    "Conforme novas folhas entram, padrões mais ricos emergem e os falsos positivos diminuem. "
    "Achados que a Gestão confirmar viram **regras automatizadas** na Camada 2 (sugestão de corte). "
    "Achados que a Gestão refutar são marcados aqui e desligados como alerta."
)
