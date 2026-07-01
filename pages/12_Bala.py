"""
pages/12_Bala.py — Análise da Bala de Doce de Leite

A bala era o produto mais "cego" do sistema: lançada (cnt_balas = estoque na
prateleira, ord_balas = ordem do dia em TACHOS) mas SEM nenhuma análise — fora
da Curva ABC, dos Insights e da Média Móvel (todos focados em cocada/palha).

Esta página dá à bala o tratamento que cocada/palha já têm: evolução da
produção, do estoque, e o descompasso entre os dois (proxy de saída/giro).

LIMITAÇÕES HONESTAS (esclarecido com o Leonardo em 10/06/2026):
  - cnt_balas = SÓ a prateleira embalada (0-205 no histórico). O estoque TOTAL
    que a Gestão usa pra decidir os tachos (~1.000-1.100) inclui as "balas
    prontas pra cortar" — camada que o sistema AINDA NÃO captura. Logo o estoque
    aqui é parcial; um "0" NÃO é ruptura (havia balas pra cortar por trás).
  - A regra de decisão (base-stock: menos estoque -> mais tachos) é REFERÊNCIA,
    não lei. Imprevistos do dia e a capacidade de tacho compartilhada com a
    cocada fazem os números oscilarem muito. Esta tela MOSTRA o real; não impõe.

Lead time da bala: ~8 dias (processo do lote). Produção em pipeline diário.
1 tacho = 30 balas.

Capítulo TCC: "Da invisibilidade ao controle — instrumentando um produto
secundário (bala) com os dados que já existem."
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Bootstrap defensivo (HF Spaces injeta DATABASE_URL como env var)
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from cached_db import list_datas_folha, get_pm_balas_doces

st.set_page_config(
    page_title="Bala • Doces Vó Nena",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui_theme import aplicar_tema
from componentes import tabela
aplicar_tema()

BALAS_POR_TACHO = 30
LEAD_TIME_DIAS = 8
WEEKDAY_PT = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

COR_PRODUCAO = "#C05621"   # laranja Vó Nena (série principal de produção)
COR_ESTOQUE = "#0E7490"    # azul-petróleo (contraste com a produção)
COR_ALERTA = "#B91C1C"     # vermelho
COR_MEDIA = "#1F2937"      # cinza escuro (linha de tendência)


# ════════════════════════════════════════════════════════════════════════════
# DADOS
# ════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=1800, show_spinner="Carregando dados da bala...")
def carregar_serie_bala():
    """Série temporal da bala: data, estoque (prateleira), tachos, balas produzidas."""
    datas = sorted(list_datas_folha())
    linhas = []
    for d in datas:
        pmbd = get_pm_balas_doces(d) or {}
        try:
            data_dt = datetime.strptime(d, "%Y-%m-%d")
        except Exception:
            continue
        tachos = int(pmbd.get("ord_balas") or 0)
        cnt = int(pmbd.get("cnt_balas") or 0)
        linhas.append({
            "data": d,
            "data_dt": data_dt,
            "dia_pt": WEEKDAY_PT[data_dt.weekday()],
            "estoque_prateleira": cnt,
            "tachos": tachos,
            "balas_produzidas": tachos * BALAS_POR_TACHO,
        })
    return pd.DataFrame(linhas)


df = carregar_serie_bala()


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ════════════════════════════════════════════════════════════════════════════
st.title("Bala de Doce de Leite")
st.caption(
    "O produto que era invisível pro sistema agora tem análise própria — "
    "produção (tachos → balas), estoque na prateleira e o descompasso entre eles."
)

if df.empty or df["tachos"].sum() == 0:
    st.warning("Ainda não há folhas com produção de bala lançada.")
    st.stop()

st.info(
    "**Leitura honesta:** o estoque aqui é só a **prateleira embalada** "
    "(`cnt_balas`). O estoque TOTAL que a Gestão usa pra decidir os tachos "
    "(~1.000–1.100, incluindo as **balas prontas pra cortar**) ainda não está no "
    "sistema — então um '0' aqui **não é falta**, é prateleira vazia com buffer "
    "pra cortar por trás. Já a produção (tachos) é dado completo e confiável."
)


# ════════════════════════════════════════════════════════════════════════════
# CARTÕES
# ════════════════════════════════════════════════════════════════════════════
st.divider()

dias_producao = df[df["tachos"] > 0]
total_balas = int(df["balas_produzidas"].sum())
total_tachos = int(df["tachos"].sum())
n_dias_prod = len(dias_producao)
media_dia = total_balas / n_dias_prod if n_dias_prod else 0
estoque_atual = int(df.iloc[-1]["estoque_prateleira"])
data_atual = df.iloc[-1]["data"]
df_ativos = df[(df["tachos"] > 0) | (df["estoque_prateleira"] > 0)]
n_prateleira_zero = int((df_ativos["estoque_prateleira"] == 0).sum())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Balas produzidas (total)", f"{total_balas:,}",
          help=f"{total_tachos} tachos × {BALAS_POR_TACHO} balas, no período todo")
c2.metric("Média por dia de produção", f"{int(media_dia):,}",
          help=f"Média nos {n_dias_prod} dias em que houve produção")
c3.metric("Dias com produção", f"{n_dias_prod} / {len(df)}",
          help="Quase diária — a bala é produto de linha, não esporádico")
c4.metric("Estoque prateleira (hoje)", f"{estoque_atual:,}",
          help=f"Folha de {data_atual} · só embaladas, fora as 'pra cortar'")
c5.metric("Dias de prateleira zerada", n_prateleira_zero,
          help="NÃO é ruptura — havia balas prontas pra cortar (camada fora do sistema)")


# ════════════════════════════════════════════════════════════════════════════
# 1. PRODUÇÃO DIÁRIA + MÉDIA MÓVEL
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Produção diária")
st.caption(
    "Balas saídas do tacho por dia (tachos × 30). A oscilação é normal — depende "
    "da capacidade do dia e de quanto a cocada precisa dos tachos."
)

janela = st.slider("Janela da média móvel (dias)", 3, 14, 7, 1,
                   help="Suaviza a oscilação diária pra mostrar a tendência de fundo")

df_g = df.copy()
df_g["media_movel"] = df_g["balas_produzidas"].rolling(window=janela, min_periods=1).mean()

fig_prod = go.Figure()
fig_prod.add_trace(go.Bar(
    x=df_g["data_dt"], y=df_g["balas_produzidas"],
    name="Balas/dia", marker_color=COR_PRODUCAO,
    hovertemplate="<b>%{x|%d/%m}</b><br>%{y} balas<extra></extra>",
))
fig_prod.add_trace(go.Scatter(
    x=df_g["data_dt"], y=df_g["media_movel"],
    name=f"Média móvel ({janela}d)", mode="lines",
    line=dict(color=COR_MEDIA, width=2.5, dash="dash"),
    hovertemplate="<b>%{x|%d/%m}</b><br>tendência %{y:.0f}<extra></extra>",
))
fig_prod.update_layout(
    height=380, margin=dict(l=20, r=20, t=20, b=40), plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis_title="Balas/dia", hovermode="x unified",
)
fig_prod.update_xaxes(fixedrange=True)
fig_prod.update_yaxes(fixedrange=True)
st.plotly_chart(fig_prod, width='stretch', config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# 2. ESTOQUE NA PRATELEIRA
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Estoque na prateleira")
st.caption("Só as balas embaladas (`cnt_balas`). Marcador vermelho = prateleira zerou.")

zerados = df[df["estoque_prateleira"] == 0]
fig_est = go.Figure()
fig_est.add_trace(go.Scatter(
    x=df["data_dt"], y=df["estoque_prateleira"],
    name="Estoque prateleira", mode="lines+markers",
    line=dict(color=COR_ESTOQUE, width=2), marker=dict(size=6, color=COR_ESTOQUE),
    hovertemplate="<b>%{x|%d/%m}</b><br>%{y} balas na prateleira<extra></extra>",
))
if not zerados.empty:
    fig_est.add_trace(go.Scatter(
        x=zerados["data_dt"], y=zerados["estoque_prateleira"],
        name="Prateleira zerada", mode="markers",
        marker=dict(size=13, color=COR_ALERTA, symbol="x"),
        hovertemplate="<b>%{x|%d/%m}</b><br>prateleira zerada (havia pra cortar)<extra></extra>",
    ))
fig_est.update_layout(
    height=360, margin=dict(l=20, r=20, t=20, b=40), plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis_title="Balas embaladas", hovermode="x unified",
)
fig_est.update_xaxes(fixedrange=True)
fig_est.update_yaxes(fixedrange=True)
st.plotly_chart(fig_est, width='stretch', config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# 3. PRODUÇÃO × ESTOQUE — o descompasso (proxy de giro)
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Produção × Estoque — o descompasso")
st.caption(
    "Quando o estoque cai apesar de produzir, a bala está saindo mais rápido do "
    "que repõe — é a leitura mais próxima de 'giro' que dá pra ter sem dado de "
    "venda. Barras = produzidas/dia · linha = estoque na prateleira."
)

fig_mix = go.Figure()
fig_mix.add_trace(go.Bar(
    x=df["data_dt"], y=df["balas_produzidas"],
    name="Produzidas/dia", marker_color=COR_PRODUCAO, opacity=0.55,
    hovertemplate="<b>%{x|%d/%m}</b><br>produzidas %{y}<extra></extra>",
))
fig_mix.add_trace(go.Scatter(
    x=df["data_dt"], y=df["estoque_prateleira"],
    name="Estoque prateleira", mode="lines+markers", yaxis="y2",
    line=dict(color=COR_ESTOQUE, width=2.5), marker=dict(size=5),
    hovertemplate="<b>%{x|%d/%m}</b><br>estoque %{y}<extra></extra>",
))
fig_mix.update_layout(
    height=380, margin=dict(l=20, r=20, t=20, b=40), plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis=dict(title="Produzidas/dia"),
    yaxis2=dict(title="Estoque prateleira", overlaying="y", side="right", showgrid=False),
    hovermode="x unified",
)
fig_mix.update_xaxes(fixedrange=True)
fig_mix.update_yaxes(fixedrange=True)
st.plotly_chart(fig_mix, width='stretch', config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# 4. LINHA DO TEMPO (tabela)
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Linha do tempo")
df_tab = df[df["tachos"] + df["estoque_prateleira"] > 0][
    ["data", "dia_pt", "tachos", "balas_produzidas", "estoque_prateleira"]
].copy()
df_tab.columns = ["Data", "Dia", "Tachos", "Balas produzidas", "Estoque prateleira"]
df_tab = df_tab.sort_values("Data", ascending=False)
tabela(df_tab, cols_direita=["Tachos", "Balas produzidas", "Estoque prateleira"])


# ════════════════════════════════════════════════════════════════════════════
# COMO LER (e o que falta)
# ════════════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("Como ler estes números (e o que ainda falta)", expanded=False):
    st.markdown(
        f"""
**A regra de produção da bala (referência, não lei):** a Gestão mira um
estoque-alvo de ~1.000–1.100 balas e ajusta os tachos inversamente — menos
estoque, mais tachos (~900 → 4 tachos · ~1.000 → 3 · ~1.100 → 2). Mas é só
referência: a capacidade de tacho (dividida com a cocada), os imprevistos do dia
e a demanda real fazem o número oscilar bastante. Por isso esta tela mostra o
**real**, não a regra.

**Por que ainda falta a peça principal:** essa decisão usa o estoque **total**
(prateleira + balas prontas pra cortar). O sistema hoje só registra a
**prateleira** (`cnt_balas`). Enquanto a camada "pra cortar" não for capturada,
dá pra analisar produção e tendência (sólido), mas **não** dá pra sugerir os
tachos automaticamente como a Gestão faz.

**Próximo passo:** capturar as "balas pra cortar" (uma contagem a mais na folha)
→ aí ligamos a sugestão automática (base-stock) e o giro real. Lead time da
bala: ~{LEAD_TIME_DIAS} dias (processo do lote).
        """
    )

st.divider()
st.caption(
    f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
    f"{len(df)} folhas · cache 30 min · 1 tacho = {BALAS_POR_TACHO} balas."
)
