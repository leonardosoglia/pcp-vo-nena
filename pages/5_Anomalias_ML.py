"""
pages/5_Anomalias_ML.py — Detecção de Anomalias via Machine Learning

Substitui (complementa) as regras hardcoded da página Insights por um algoritmo
não-supervisionado que APRENDE o que é normal a partir do histórico de folhas.

Algoritmo: Isolation Forest (Liu et al., 2008).
    Funcionamento: isola pontos atípicos através de árvores de decisão aleatórias.
    Pontos que precisam de POUCAS divisões pra ficar isolados são, por
    construção, "fáceis de isolar" — ou seja, anômalos.

Features extraídas de cada folha:
    - Embalados totais por sabor (cocada 45g + Mini + Pet, palha 50g + Pet)
    - Ordens de produção (band, virada) por sabor
    - Razões entre sabores (T/L, T/B, T/C, T/P)
    - Razão LP/T da palha
    - Total geral embalado e ordenado
    - Indicadores de mix (% cocada vs palha)

Pra cada folha anômala, mostra QUAL feature mais contribuiu pra anomalia
(via Mahalanobis distance simplificada — comparação z-score por feature).

Capítulo TCC: "Detecção não-supervisionada de anomalia operacional em PCP:
substituindo regras heurísticas por algoritmos que aprendem com os dados."
Referência: Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation Forest.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Bootstrap defensivo
if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
    os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from cached_db import (
    list_datas_folha, get_folha_cocada, get_folha_palha,
    SABORES_COCADA, SABORES_PALHA,
)

st.set_page_config(
    page_title="Anomalias ML • Doces Vó Nena",
    page_icon="🤖",
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
    .anomaly-card {
        background: linear-gradient(135deg, #FFF8F2 0%, #FEE2E2 100%);
        border-left: 6px solid #B91C1C;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 10px 0;
    }
    .didatica {
        background: #FFFBEB; border-left: 5px solid #D97706;
        border-radius: 6px; padding: 14px 18px; margin: 10px 0;
    }
    .limit-warning {
        background: #EFF6FF; border-left: 5px solid #2563EB;
        border-radius: 6px; padding: 14px 18px; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CONSTRUÇÃO DAS FEATURES
# ════════════════════════════════════════════════════════════════════════════
def _safe_ratio(num, den):
    """Razão protegida contra divisão por zero — retorna 0 se denominador é 0."""
    return float(num) / float(den) if den else 0.0


def _features_de_folha(d):
    """Extrai um dict de features de UMA folha (data string YYYY-MM-DD).

    As features são todas numéricas — exigência do Isolation Forest.
    Nomes são auto-descritivos pra explicar a anomalia ao usuário depois.
    """
    cocada = {r["sabor"]: r for r in get_folha_cocada(d)}
    palha  = {r["sabor"]: r for r in get_folha_palha(d)}

    feat = {"data": d}

    # Embalados de cocada (totais por sabor — soma 45g + Mini + Pet)
    for s in SABORES_COCADA:
        r = cocada.get(s, {})
        emb_total = (int(r.get("emb_45g") or 0) +
                     int(r.get("emb_mini") or 0) +
                     int(r.get("emb_pet") or 0))
        feat[f"emb_total_{s}"] = emb_total

    # Embalados de palha
    for s in SABORES_PALHA:
        r = palha.get(s, {})
        emb_50 = int(r.get("emb_50g") or 0)
        emb_pt = int(r.get("emb_pet") or 0)
        feat[f"palha_emb_{s}"] = emb_50 + emb_pt

    # Ordens de produção (band) por sabor cocada
    for s in SABORES_COCADA:
        r = cocada.get(s, {})
        feat[f"ord_band_{s}"] = int(r.get("ord_prod_band") or 0)

    # Razões da regra clássica (T = 2L = 4B/C/P em 45g embalados)
    t_45 = int((cocada.get("TRADICIONAL", {}).get("emb_45g") or 0))
    l_45 = int((cocada.get("LEITE CONDENSADO", {}).get("emb_45g") or 0))
    b_45 = int((cocada.get("BRIGADEIRO", {}).get("emb_45g") or 0))
    c_45 = int((cocada.get("CAFÉ", {}).get("emb_45g") or 0))
    p_45 = int((cocada.get("PÉ DE MOÇA", {}).get("emb_45g") or 0))
    feat["razao_T_L_45g"] = _safe_ratio(t_45, l_45)
    feat["razao_T_BCP_45g"] = _safe_ratio(t_45, b_45 + c_45 + p_45)

    # Razão LP/T da palha (regra H5 hardcoded)
    t_palha = int((palha.get("TRADICIONAL", {}).get("ord_prod_band") or 0))
    lp_palha = int((palha.get("LEITE EM PÓ", {}).get("ord_prod_band") or 0))
    feat["razao_LP_T_palha"] = _safe_ratio(lp_palha, t_palha)

    # Totais agregados
    feat["total_emb_cocada"] = sum(feat[f"emb_total_{s}"] for s in SABORES_COCADA)
    feat["total_emb_palha"]  = sum(feat[f"palha_emb_{s}"] for s in SABORES_PALHA)
    feat["total_ord_cocada"] = sum(feat[f"ord_band_{s}"] for s in SABORES_COCADA)

    # Mix cocada vs palha (% do total embalado)
    total_emb = feat["total_emb_cocada"] + feat["total_emb_palha"]
    feat["pct_cocada"] = _safe_ratio(feat["total_emb_cocada"], total_emb)

    return feat


@st.cache_data(ttl=1800, show_spinner="🤖 Treinando modelo de detecção de anomalias...")
def detectar_anomalias(contamination=0.1):
    """Roda Isolation Forest sobre todas as folhas + retorna DataFrame com score.

    Parâmetro `contamination`: proporção esperada de anomalias (0.1 = 10%).
    Quanto maior, mais folhas classificadas como anômalas. Padrão conservador.

    Retorna DataFrame ordenado por anomaly_score (mais anômalas primeiro):
        data, anomaly_score, is_anomaly (-1 = anômala, 1 = normal),
        + todas as features
        + top_3_features (lista das features que mais contribuíram)
    """
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    datas = list_datas_folha()
    if len(datas) < 5:
        return None, "amostra_insuficiente"

    # Constrói matriz de features
    linhas = [_features_de_folha(d) for d in datas]
    df = pd.DataFrame(linhas)
    feature_cols = [c for c in df.columns if c != "data"]

    # Normaliza (Isolation Forest é menos sensível à escala que outros, mas
    # standardização ajuda na interpretação de "feature mais anômala" depois)
    scaler = StandardScaler()
    X = scaler.fit_transform(df[feature_cols].values)
    X_df = pd.DataFrame(X, columns=feature_cols)

    # Treina modelo
    model = IsolationForest(
        contamination=contamination,
        n_estimators=100,
        random_state=42,
    )
    df["is_anomaly"] = model.fit_predict(X)
    df["anomaly_score"] = -model.score_samples(X)  # negativa pra "maior = mais anômala"

    # Pra cada folha, calcula z-score absoluto por feature e pega top 3
    z_abs = X_df.abs()
    top3 = []
    for i in range(len(z_abs)):
        row = z_abs.iloc[i]
        top_features = row.nlargest(3)
        top3.append([
            (feat, X_df.iloc[i][feat])  # (nome, z-score com sinal)
            for feat in top_features.index
        ])
    df["top_3_features"] = top3

    df = df.sort_values("anomaly_score", ascending=False).reset_index(drop=True)
    return df, "ok"


def _explicar_feature(nome_feat: str, z_score: float) -> str:
    """Traduz nome técnico de feature pra português leigo, com direção do desvio."""
    direcao = "alto" if z_score > 0 else "baixo"
    intensidade = "muito " if abs(z_score) > 2 else ""

    if nome_feat.startswith("emb_total_"):
        sabor = nome_feat.replace("emb_total_", "")
        return f"Embalado de {sabor} {intensidade}{direcao} pro padrão"
    if nome_feat.startswith("palha_emb_"):
        sabor = nome_feat.replace("palha_emb_", "")
        return f"Embalado de Palha {sabor} {intensidade}{direcao}"
    if nome_feat.startswith("ord_band_"):
        sabor = nome_feat.replace("ord_band_", "")
        return f"Ordem de bandejas de {sabor} {intensidade}{direcao}"
    if nome_feat == "razao_T_L_45g":
        return f"Razão T/L em 45g {intensidade}{direcao} (esperado: ~2.0)"
    if nome_feat == "razao_T_BCP_45g":
        return f"Razão T/(B+C+P) {intensidade}{direcao} (esperado: ~1.33)"
    if nome_feat == "razao_LP_T_palha":
        return f"Razão Leite em Pó / Tradicional na palha {intensidade}{direcao}"
    if nome_feat == "total_emb_cocada":
        return f"Total embalado de cocada {intensidade}{direcao}"
    if nome_feat == "total_emb_palha":
        return f"Total embalado de palha {intensidade}{direcao}"
    if nome_feat == "total_ord_cocada":
        return f"Total de ordens de cocada {intensidade}{direcao}"
    if nome_feat == "pct_cocada":
        return f"Mix cocada/palha {intensidade}{direcao}"
    return f"{nome_feat} {intensidade}{direcao}"


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO + EXPLICAÇÃO
# ════════════════════════════════════════════════════════════════════════════
st.title("🤖 Detecção de Anomalias com Machine Learning")
st.caption(
    "Algoritmo Isolation Forest aprende o 'normal' do histórico e sinaliza folhas atípicas. "
    "Não precisa programar regra — o modelo descobre sozinho."
)

with st.expander("ℹ️ Como funciona (clica pra entender)", expanded=False):
    st.markdown("""
**O problema das regras hardcoded:** o sistema só detecta o que o programador
**pensou em programar**. Combinações estranhas não previstas passam batido.

**A solução ML:** o algoritmo **Isolation Forest** olha todas as folhas e
aprende sozinho o "perfil normal" da fábrica — sem ninguém dizer o que é
normal. Quando uma folha **destoa muito** desse perfil, ele sinaliza.

**Analogia:** porteiro experiente — depois de 5 anos, reconhece na hora quem
chega com chapéu rosa às 3 da manhã. Sem precisar de regra escrita.

**Vantagens vs regras hardcoded:**

| Aspecto | Regras hardcoded | Isolation Forest |
|---|---|---|
| Quem programa | Você (uma a uma) | Algoritmo aprende sozinho |
| Detecta combinações? | Só as previstas | **Qualquer** desvio |
| Evolui com dados? | Não | Sim — quanto mais dados, melhor |
| Explica o motivo? | Sim (a regra diz) | Aproximadamente (top 3 features) |

**Como interpreta o resultado:**

- **Anomaly score alto** → folha mais "estranha" em relação ao histórico
- **Top 3 features** → quais campos mais contribuíram pro desvio
- **Não é diagnóstico** — é PISTA pra investigar com a Gestão

**Referência clássica:** Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008).
*Isolation Forest*. Proceedings of the 8th IEEE ICDM. Citações: 5000+.
""")


# Slider de sensibilidade (contamination)
col_slider, col_info = st.columns([1, 2])
with col_slider:
    contamination = st.slider(
        "Sensibilidade (% esperado de anomalias)",
        min_value=0.05, max_value=0.30, value=0.15, step=0.05,
        help="Quanto maior, mais folhas serão marcadas como anômalas. "
             "0.15 = 15% das folhas (padrão balanceado).",
    )
with col_info:
    st.markdown(
        "<div class='didatica'>"
        "💡 A <b>sensibilidade</b> diz pro algoritmo quantas anomalias esperar. "
        "Padrão 15% é conservador. Se o histórico vier muito 'parecido', "
        "talvez subir pra 25% pra forçar destacar as mais diferentes."
        "</div>",
        unsafe_allow_html=True,
    )


df_result, status = detectar_anomalias(contamination=contamination)

if status == "amostra_insuficiente":
    st.warning(
        "⚠️ Precisa de pelo menos **5 folhas** no banco pra treinar o modelo. "
        "Cadastra mais folhas em Lançamento e volta aqui."
    )
    st.stop()

n_folhas = len(df_result)
n_anomalias = int((df_result["is_anomaly"] == -1).sum())

# Aviso sobre tamanho da amostra
if n_folhas < 30:
    st.markdown(
        f"<div class='limit-warning'>"
        f"<b>📊 Amostra atual: {n_folhas} folhas.</b> "
        f"Com <30 folhas, a precisão é limitada — o algoritmo ainda está aprendendo o 'normal'. "
        f"Use estes resultados como <b>pistas pra investigar</b>, não conclusões fechadas. "
        f"A partir de ~60 folhas (3 meses), a detecção fica robusta."
        f"</div>",
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# RESUMO
# ════════════════════════════════════════════════════════════════════════════
st.divider()

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("📋 Folhas analisadas", n_folhas)
col_b.metric("🚨 Anomalias detectadas", n_anomalias)
col_c.metric("🎯 Sensibilidade", f"{int(contamination*100)}%")
col_d.metric("⚙️ Algoritmo", "Isolation Forest")


# ════════════════════════════════════════════════════════════════════════════
# RANKING DE ANOMALIAS
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("🏆 Ranking de folhas mais atípicas")

st.caption(
    "Ordenadas por score de anomalia (decrescente). As marcadas como 'anômala' "
    "passaram do limiar de sensibilidade. As demais são 'normais' mas com score."
)

# Gráfico de score por folha (com cor diferenciada pra anomalias)
df_plot = df_result.copy()
df_plot["data_dt"] = pd.to_datetime(df_plot["data"])
df_plot["status"] = df_plot["is_anomaly"].map({-1: "Anomalia", 1: "Normal"})

fig = go.Figure()
for status_val, cor in [("Anomalia", "#B91C1C"), ("Normal", "#9CA3AF")]:
    sub = df_plot[df_plot["status"] == status_val].sort_values("data_dt")
    fig.add_trace(go.Bar(
        x=sub["data_dt"],
        y=sub["anomaly_score"],
        name=status_val,
        marker_color=cor,
        hovertemplate=(
            "<b>%{x|%d/%m/%Y}</b><br>"
            f"Status: {status_val}<br>"
            "Score: %{y:.3f}<br>"
            "<extra></extra>"
        ),
    ))

fig.update_layout(
    title="Anomaly score por data (vermelho = anomalia)",
    xaxis_title="Data da folha",
    yaxis_title="Anomaly score (maior = mais atípica)",
    height=380,
    margin=dict(l=20, r=20, t=60, b=40),
    plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# DETALHES DE CADA ANOMALIA
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("🔍 Detalhes das anomalias detectadas")

anomalias = df_result[df_result["is_anomaly"] == -1]

if anomalias.empty:
    st.markdown(
        "<div class='didatica'>"
        "✅ Nenhuma folha foi classificada como anômala com a sensibilidade atual. "
        "Aumente a sensibilidade no slider acima pra forçar mais detecções."
        "</div>",
        unsafe_allow_html=True,
    )
else:
    for i, row in anomalias.iterrows():
        data_fmt = datetime.strptime(row["data"], "%Y-%m-%d").strftime("%d/%m/%Y (%A)")
        dias_pt = {
            "Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
            "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado",
            "Sunday": "Domingo",
        }
        for en, pt in dias_pt.items():
            data_fmt = data_fmt.replace(en, pt)

        score = row["anomaly_score"]
        top3 = row["top_3_features"]

        explicacoes = [
            f"&nbsp;&nbsp;{i+1}. {_explicar_feature(feat, z)} <i>(desvio: {z:+.2f}σ)</i>"
            for i, (feat, z) in enumerate(top3)
        ]
        explicacoes_html = "<br>".join(explicacoes)

        st.markdown(
            f"<div class='anomaly-card'>"
            f"<b style='font-size:18px;color:#7B341E;'>📅 {data_fmt}</b><br>"
            f"<span style='color:#991B1B;font-weight:600;'>Score de anomalia: {score:.3f}</span>"
            f"<hr style='border-color:#FECACA;margin:10px 0;'>"
            f"<b>O que mais contribuiu (top 3 features):</b><br>"
            f"{explicacoes_html}"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='didatica'>"
        "<b>Como ler:</b> '<b>desvio: +2.5σ</b>' significa que esse campo estava "
        "<b>2.5 desvios-padrão</b> acima do normal. Valores acima de ±2σ são "
        "estatisticamente raros (~5% das observações)."
        "</div>",
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# TABELA COMPLETA (TODAS AS FOLHAS COM SCORE)
# ════════════════════════════════════════════════════════════════════════════
with st.expander("📋 Ver todas as folhas com score (não só anomalias)", expanded=False):
    df_tab = df_result[["data", "status", "anomaly_score"]].copy() \
        if "status" not in df_result.columns else df_result[["data", "anomaly_score"]].copy()
    df_tab["status"] = df_result["is_anomaly"].map({-1: "🚨 Anomalia", 1: "✅ Normal"})
    df_tab["data"] = pd.to_datetime(df_tab["data"]).dt.strftime("%d/%m/%Y")
    df_tab["anomaly_score"] = df_tab["anomaly_score"].apply(lambda v: f"{v:.3f}")
    df_tab = df_tab[["data", "status", "anomaly_score"]]
    df_tab.columns = ["Data", "Status", "Anomaly Score"]
    st.dataframe(df_tab, use_container_width=True, hide_index=True)


st.divider()
st.caption(
    f"🤖 Detecção rodada em {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
    f"Isolation Forest (scikit-learn) sobre {n_folhas} folhas · "
    f"recalcula a cada 30 min ou quando nova folha entra."
)
st.caption(
    "💡 Esta página COMPLEMENTA, não substitui, a página Insights. As regras "
    "hardcoded continuam ativas lá (H5, H1, H4 etc) — porque são *explicáveis*. "
    "Aqui o modelo detecta o *inesperado*. Os dois se reforçam."
)
