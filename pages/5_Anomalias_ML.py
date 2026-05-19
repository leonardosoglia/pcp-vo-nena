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

# Bootstrap defensivo de secrets:
#  - Streamlit Cloud expõe via st.secrets (lê de secrets.toml)
#  - HF Spaces expõe via env vars diretas (sem secrets.toml — `in st.secrets`
#    levanta StreamlitSecretNotFoundError). Try/except cobre os dois casos.
for _key in ("DATABASE_URL", "ANTHROPIC_API_KEY"):
    if not os.getenv(_key):
        try:
            if _key in st.secrets:
                os.environ[_key] = st.secrets[_key]
        except Exception:
            pass

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

    # ── FEATURES DE ESTOQUE (Embalados — snapshot do dia) ─────────────────
    # Captura anomalias de NÍVEL DE ESTOQUE (encalhe, ruptura, contagem errada)

    # Embalados de cocada (totais por sabor — soma 45g + Mini + Pet)
    for s in SABORES_COCADA:
        r = cocada.get(s, {})
        emb_total = (int(r.get("emb_45g") or 0) +
                     int(r.get("emb_mini") or 0) +
                     int(r.get("emb_pet") or 0))
        feat[f"emb_total_{s}"] = emb_total

    # Embalados de palha (estoque snapshot)
    for s in SABORES_PALHA:
        r = palha.get(s, {})
        emb_50 = int(r.get("emb_50g") or 0)
        emb_pt = int(r.get("emb_pet") or 0)
        feat[f"palha_emb_{s}"] = emb_50 + emb_pt

    # ── FEATURES DE FLUXO (Ordens — demanda do dia) ───────────────────────
    # Captura anomalias de DEMANDA (dia atípico de pedido, mudança de mix)
    # Adicionado 17/05/2026 após insight do Leonardo: estoque e fluxo são
    # variáveis complementares — capturam tipos diferentes de anomalia.

    # Ordens de produção (band) por sabor cocada
    for s in SABORES_COCADA:
        r = cocada.get(s, {})
        feat[f"ord_band_{s}"] = int(r.get("ord_prod_band") or 0)

    # Ordens de corte por sabor cocada (45g, Mini, Pet — em bandejas)
    for s in SABORES_COCADA:
        r = cocada.get(s, {})
        feat[f"ord_corte_total_{s}"] = (
            int(r.get("ord_corte_45g") or 0) +
            int(r.get("ord_corte_mini") or 0) +
            int(r.get("ord_corte_pet") or 0)
        )

    # Ordens de embalagem por sabor cocada (45g + Mini em und)
    for s in SABORES_COCADA:
        r = cocada.get(s, {})
        feat[f"ord_emb_total_{s}"] = (
            int(r.get("ord_emb_45g") or 0) +
            int(r.get("ord_emb_mini") or 0)
        )

    # Ordens de produção e corte da palha
    for s in SABORES_PALHA:
        r = palha.get(s, {})
        feat[f"palha_ord_band_{s}"] = int(r.get("ord_prod_band") or 0)
        feat[f"palha_ord_corte_{s}"] = (
            int(r.get("ord_corte_50g") or 0) +
            int(r.get("ord_corte_pet") or 0)
        )

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
        return f"Estoque embalado de Cocada {sabor} {intensidade}{direcao}"
    if nome_feat.startswith("palha_emb_"):
        sabor = nome_feat.replace("palha_emb_", "")
        return f"Estoque embalado de Palha {sabor} {intensidade}{direcao}"
    if nome_feat.startswith("ord_band_"):
        sabor = nome_feat.replace("ord_band_", "")
        return f"Ordem de bandejas (tachos) de Cocada {sabor} {intensidade}{direcao}"
    if nome_feat.startswith("ord_corte_total_"):
        sabor = nome_feat.replace("ord_corte_total_", "")
        return f"Ordem de corte de Cocada {sabor} {intensidade}{direcao}"
    if nome_feat.startswith("ord_emb_total_"):
        sabor = nome_feat.replace("ord_emb_total_", "")
        return f"Ordem de embalagem de Cocada {sabor} {intensidade}{direcao}"
    if nome_feat.startswith("palha_ord_band_"):
        sabor = nome_feat.replace("palha_ord_band_", "")
        return f"Ordem de bandejas (tachos) de Palha {sabor} {intensidade}{direcao}"
    if nome_feat.startswith("palha_ord_corte_"):
        sabor = nome_feat.replace("palha_ord_corte_", "")
        return f"Ordem de corte de Palha {sabor} {intensidade}{direcao}"
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
        return f"Mix cocada/palha (% cocada do total embalado) {intensidade}{direcao}"
    return f"{nome_feat} {intensidade}{direcao}"


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO + EXPLICAÇÃO
# ════════════════════════════════════════════════════════════════════════════
st.title("🤖 Folhas Atípicas — Detecção Automática")
st.caption(
    "O sistema aprende sozinho o que é uma folha 'normal' analisando todo o "
    "histórico, e sinaliza as folhas que fogem desse padrão — sem precisar de "
    "ninguém programar regra nenhuma."
)

# Resumo em destaque antes do expander técnico
st.markdown(
    "<div class='didatica' style='margin-bottom:14px;'>"
    "<b>📖 Como ler esta página em 30 segundos:</b><br>"
    "1. O algoritmo <b>Isolation Forest</b> (uma técnica de ML) olha todas as "
    "folhas registradas e descobre, sozinho, qual é o 'comportamento normal' "
    "da fábrica.<br>"
    "2. Quando uma folha tem combinação de valores muito diferente do padrão, "
    "ele <b>sinaliza como atípica</b>.<br>"
    "3. A página mostra <b>quais folhas se destacaram</b> e <b>quais campos</b> "
    "(produção de Tradicional, embalagem de Pet, razão T/L, etc.) foram os "
    "responsáveis pelo desvio.<br>"
    "4. <b>Atípico ≠ erro.</b> Pode ser encomenda especial, dia atípico, "
    "feriado, etc. Use como <b>pista pra investigar</b>, não conclusão."
    "</div>",
    unsafe_allow_html=True,
)

with st.expander("📚 Explicação detalhada do método (opcional — pro TCC)", expanded=False):
    st.markdown("""
**O problema das regras programadas à mão:** o sistema antigo só detecta o que
o programador **pensou em programar** (ex: "se palha LP > tradicional × 1.3,
alerta"). Combinações estranhas que ninguém previu passam batido.

**A solução com Machine Learning:** o algoritmo **Isolation Forest** olha
todas as folhas e aprende sozinho o "perfil normal" da fábrica — sem ninguém
dizer o que é normal. Quando uma folha **destoa muito** desse perfil, ele
sinaliza.

**Analogia:** porteiro experiente — depois de 5 anos, reconhece na hora quem
chega com chapéu rosa às 3 da manhã. Sem precisar de regra escrita, só com
"vivência".

**Vantagens vs regras programadas à mão:**

| Aspecto | Regras programadas | Isolation Forest (ML) |
|---|---|---|
| Quem cria a lógica | Você programa uma a uma | Algoritmo aprende sozinho |
| Detecta combinações inesperadas? | Só as previstas | **Sim — qualquer desvio** |
| Evolui com mais dados? | Não, é fixo | Sim, melhora com volume |
| Explica o "porquê"? | Sim, a regra é explícita | Sim, mas aproximado (top 3 features) |

**Como interpreta o resultado da página:**

- **Score de anomalia alto** → folha mais "estranha" em relação ao histórico
- **Top 3 features** → quais campos da folha mais contribuíram pro desvio
- **σ (sigma)** = quantos desvios-padrão acima/abaixo do normal aquele campo
  estava (acima de ±2σ é estatisticamente raro, ~5% das observações)
- **NÃO é diagnóstico** — é **PISTA** pra investigar com a Gestão

**Referência clássica:** Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008).
*Isolation Forest*. Proceedings of the 8th IEEE International Conference on
Data Mining. Citações: 5.000+.
""")


# Slider de sensibilidade (contamination)
col_slider, col_info = st.columns([1, 2])
with col_slider:
    contamination = st.slider(
        "Quão restrito é o critério de 'atípico'?",
        min_value=0.05, max_value=0.30, value=0.15, step=0.05,
        help="Diz pro algoritmo qual a porcentagem máxima de folhas que ele "
             "deve marcar como atípicas. 5% = só as MAIS estranhas (poucas "
             "sinalizadas). 30% = critério mais frouxo, sinaliza mais folhas.",
    )
with col_info:
    n_estimado = int(round(contamination * 100))
    st.markdown(
        f"<div class='didatica'>"
        f"💡 Com <b>{n_estimado}%</b> selecionado, o algoritmo vai sinalizar "
        f"aproximadamente as <b>{n_estimado}% folhas mais diferentes</b> do "
        f"histórico. <br>"
        f"• <b>Critério rígido (5-10%)</b> = só as anomalias mais óbvias<br>"
        f"• <b>Padrão (15-20%)</b> = boa relação sensibilidade/ruído<br>"
        f"• <b>Frouxo (25-30%)</b> = força destacar mais coisas (útil quando "
        f"histórico é muito parecido)"
        f"</div>",
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
col_a.metric(
    "📋 Folhas analisadas", n_folhas,
    help="Total de folhas registradas no banco e usadas no treinamento do modelo.",
)
col_b.metric(
    "🚨 Folhas atípicas detectadas", n_anomalias,
    help="Quantas dessas folhas o algoritmo marcou como diferentes do padrão.",
)
col_c.metric(
    "🎯 Critério usado",
    f"{int(contamination*100)}% mais diferentes",
    help="Reflete a posição atual do slider acima.",
)
col_d.metric(
    "⚙️ Método",
    "Isolation Forest",
    help="Algoritmo de Machine Learning não-supervisionado.",
)


# ════════════════════════════════════════════════════════════════════════════
# RANKING DE ANOMALIAS
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("🏆 Quais folhas chamaram a atenção?")

st.caption(
    "Gráfico abaixo mostra **TODAS** as folhas com seu score de 'estranheza'. "
    "**Quanto maior o score**, mais a folha difere do padrão do histórico. "
    "**Barras vermelhas** = folhas que o algoritmo marcou como atípicas (passaram do critério). "
    "**Barras cinzas** = folhas normais."
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
    title="Score de estranheza por data — barras vermelhas marcam folhas atípicas",
    xaxis_title="Data da folha",
    yaxis_title="Score de estranheza (maior = mais diferente do padrão)",
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
st.header("🔍 Por que cada folha atípica foi marcada?")
st.caption(
    "Pra cada folha que o algoritmo considerou atípica, mostramos os **3 campos "
    "que mais contribuíram pro desvio**. O valor **σ (sigma)** significa "
    "*'quantos desvios-padrão acima/abaixo do normal'*: ±1σ é comum, ±2σ "
    "já é raro (~5% das observações), ±3σ é muito raro."
)

anomalias = df_result[df_result["is_anomaly"] == -1]

if anomalias.empty:
    st.markdown(
        "<div class='didatica'>"
        "✅ Nenhuma folha foi marcada como atípica com o critério atual. "
        "Mova o slider acima pra um valor maior se quiser forçar mais detecções."
        "</div>",
        unsafe_allow_html=True,
    )
else:
    # ── Inicializa cache de explicações por data na sessão ───────────────
    if "explicacoes_anomalias" not in st.session_state:
        st.session_state.explicacoes_anomalias = {}  # data -> dict resultado

    # ── Checa se Claude está disponível (ANTHROPIC_API_KEY configurada) ─
    api_key_disponivel = bool(os.getenv("ANTHROPIC_API_KEY", "").strip())

    for i, row in anomalias.iterrows():
        data_iso = row["data"]
        data_fmt = datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y (%A)")
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

        # ── Botão "🤖 Explicar via IA" + área de exibição ────────────────
        col_btn, col_status = st.columns([1, 3])
        with col_btn:
            btn_label = "🤖 Explicar via IA"
            btn_key = f"explicar_{data_iso}_{i}"
            btn_clicked = st.button(
                btn_label, key=btn_key, use_container_width=True,
                disabled=not api_key_disponivel,
                help=(
                    "Pede ao Claude (IA) pra explicar essa anomalia em PT-BR. "
                    "~R$0,03 por chamada."
                    if api_key_disponivel
                    else "ANTHROPIC_API_KEY não configurada. Ative no Settings > "
                         "Variables and secrets do HF Spaces pra liberar."
                ),
            )
        with col_status:
            if not api_key_disponivel:
                st.caption(
                    "🔒 *Explicação via IA requer `ANTHROPIC_API_KEY` configurada "
                    "no HF Spaces (Settings > Variables and secrets).*"
                )

        # Se já tem explicação em cache, exibe; senão, se botão foi clicado, chama Claude
        if data_iso in st.session_state.explicacoes_anomalias:
            resultado = st.session_state.explicacoes_anomalias[data_iso]
            if resultado.get("erro"):
                st.markdown(
                    f"<div class='anomaly-card' style='background:#FEF2F2;border-color:#B91C1C;'>"
                    f"<b>❌ Erro ao consultar Claude:</b><br>"
                    f"<code>{resultado['erro']}</code>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                cache_info = ""
                if resultado.get("tokens_cache_read", 0) > 0:
                    pct = (resultado["tokens_cache_read"] / max(resultado["tokens_input"], 1)) * 100
                    cache_info = f" · 💾 cache hit: {pct:.0f}%"
                st.markdown(
                    f"<div class='anomaly-card' style='background:linear-gradient(135deg,#FFF8F2 0%,#FEF3C7 100%);border-color:#C05621;'>"
                    f"<b>🤖 Análise do Claude ({resultado.get('modelo', '?')}):</b><br><br>"
                    f"{resultado.get('explicacao', '').replace(chr(10), '<br>')}"
                    f"<hr style='border-color:#FED7AA;margin:10px 0;'>"
                    f"<span style='font-size:11px;color:#7B341E;'>"
                    f"📊 {resultado['tokens_input']} tokens in + {resultado['tokens_output']} out = "
                    f"<b>~R$ {resultado['custo_brl']:.3f}</b>{cache_info}"
                    f"</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        elif btn_clicked and api_key_disponivel:
            try:
                from claude_assistant import explicar_anomalia
                with st.spinner(f"🤖 Claude analisando {data_fmt}..."):
                    resultado = explicar_anomalia(
                        data=data_iso,
                        top_features=list(top3),
                        anomaly_score=float(score),
                    )
                st.session_state.explicacoes_anomalias[data_iso] = resultado
                st.rerun()
            except ImportError as e:
                st.error(f"❌ Erro ao importar claude_assistant: {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")

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
