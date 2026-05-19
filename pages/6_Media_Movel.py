"""
pages/6_Media_Movel.py — Média Móvel por dia da semana

Compara a META BASE da tabela metas_45g (parâmetro fixo definido pela Gestão)
com a MÉDIA MÓVEL OBSERVADA nas últimas N ocorrências do mesmo dia da semana.

Métrica usada: ord_emb_45g (fluxo de embalagem 45g) — fluxo, não estoque
(mesma lição da Curva ABC corrigida com insight do Leonardo 17/05).

Objetivo: alertar quando a realidade observada se descolar muito do
parâmetro base. Permite que a Gestão recalibre antecipadamente em vez de
descobrir tarde demais que o ano mudou.

Princípio: média ponderada por recência (mais peso pras ocorrências recentes).
Implementação simples — média aritmética das últimas 4 ocorrências
do mesmo dia da semana. Janela configurável via slider.

Capítulo TCC: "Calibração contínua de parâmetros via média móvel — ajuste
adaptativo de metas em PCP."
Referência: Wheelwright & Hyndman (1998). *Forecasting: Methods and Apps*.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Bootstrap defensivo (HF Spaces sem secrets.toml — try/except evita erro)
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from cached_db import (
    list_datas_folha, get_folha_cocada, get_metas_45g,
    SABORES_COCADA,
)

st.set_page_config(
    page_title="Média Móvel • Doces Vó Nena",
    page_icon="📈",
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
    .didatica {
        background: #FFFBEB; border-left: 5px solid #D97706;
        border-radius: 6px; padding: 14px 18px; margin: 10px 0;
    }
    .alerta-alto {
        background: #FEF2F2; border-left: 5px solid #B91C1C;
        border-radius: 6px; padding: 12px 16px; margin: 6px 0;
    }
    .alerta-medio {
        background: #FFFBEB; border-left: 5px solid #D97706;
        border-radius: 6px; padding: 12px 16px; margin: 6px 0;
    }
    .alerta-ok {
        background: #ECFDF5; border-left: 5px solid #059669;
        border-radius: 6px; padding: 12px 16px; margin: 6px 0;
    }
</style>
""", unsafe_allow_html=True)


# Mapas pra trabalhar com dia da semana
WEEKDAY_TO_COL = {0: "segunda", 1: "terca", 2: "quarta", 3: "quinta", 4: "sexta"}
WEEKDAY_TO_PT = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta"}


# ════════════════════════════════════════════════════════════════════════════
# CÁLCULOS
# ════════════════════════════════════════════════════════════════════════════
def _carregar_observacoes_45g():
    """Retorna DataFrame com colunas: data, weekday, weekday_pt, sabor, ord_emb_45g.
    Uma linha por (data × sabor) onde houve ordem de embalagem > 0.
    """
    datas = list_datas_folha()
    if not datas:
        return pd.DataFrame()
    linhas = []
    for d in datas:
        for r in get_folha_cocada(d):
            s = r["sabor"]
            if s == "ZERO":
                continue  # Zero 45g não existe
            ord_emb = int(r.get("ord_emb_45g") or 0)
            if ord_emb > 0:
                data_dt = datetime.strptime(d, "%Y-%m-%d")
                wd = data_dt.weekday()
                if wd < 5:  # só dia útil
                    linhas.append({
                        "data": d,
                        "data_dt": data_dt,
                        "weekday": wd,
                        "weekday_pt": WEEKDAY_TO_PT[wd],
                        "sabor": s,
                        "ord_emb_45g": ord_emb,
                    })
    return pd.DataFrame(linhas)


def _calcular_media_movel(df, janela=4):
    """Pra cada (sabor × weekday), calcula média móvel das últimas `janela`
    ocorrências e compara com a meta base (metas_45g).

    Retorna DataFrame com colunas:
        sabor, weekday, weekday_pt,
        n_observacoes, media_movel, base, desvio_abs, desvio_pct, severidade
    """
    if df.empty:
        return pd.DataFrame()

    # Carrega metas base
    metas = {row["sabor"]: row for row in get_metas_45g()}

    linhas = []
    for sabor in SABORES_COCADA:
        if sabor == "ZERO":
            continue
        meta = metas.get(sabor, {})
        for wd in range(5):  # seg a sex
            col_dia = WEEKDAY_TO_COL[wd]
            base = int(meta.get(col_dia) or 0)

            sub = df[(df["sabor"] == sabor) & (df["weekday"] == wd)].sort_values("data_dt")
            n = len(sub)
            if n == 0:
                continue

            # Janela: as ÚLTIMAS `janela` observações
            ultimas = sub.tail(janela)
            mm = float(ultimas["ord_emb_45g"].mean())

            desvio_abs = mm - base if base > 0 else 0
            desvio_pct = (desvio_abs / base * 100) if base > 0 else 0

            # Classificação de severidade do desvio
            abs_pct = abs(desvio_pct)
            if abs_pct < 10:
                severidade = "OK"
            elif abs_pct < 20:
                severidade = "Atenção"
            else:
                severidade = "Recalibrar"

            linhas.append({
                "sabor": sabor,
                "weekday": wd,
                "weekday_pt": WEEKDAY_TO_PT[wd],
                "n_observacoes": n,
                "media_movel": mm,
                "base": base,
                "desvio_abs": desvio_abs,
                "desvio_pct": desvio_pct,
                "severidade": severidade,
            })

    return pd.DataFrame(linhas)


@st.cache_data(ttl=1800, show_spinner="📊 Calculando médias móveis...")
def calcular_tudo(janela=4):
    df_obs = _carregar_observacoes_45g()
    if df_obs.empty:
        return df_obs, pd.DataFrame()
    df_mm = _calcular_media_movel(df_obs, janela=janela)
    return df_obs, df_mm


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ════════════════════════════════════════════════════════════════════════════
st.title("📈 Calibração de Metas — Média Móvel")
st.caption(
    "Compara as METAS fixas que a Gestão definiu (\"toda segunda produz 5.200 "
    "de Tradicional\") com o que de fato está acontecendo nas últimas semanas. "
    "Se a realidade subiu ou desceu muito, o sistema sugere atualizar a meta."
)

# Resumo curto em destaque (antes do expander técnico)
st.markdown(
    "<div class='didatica' style='margin-bottom:14px;'>"
    "<b>📖 Como ler esta página em 30 segundos:</b><br>"
    "1. A fábrica tem metas pré-definidas pra cada sabor em cada dia útil "
    "(ex: <i>Tradicional 45g segunda = 5.200 und</i>). Essas metas estão na "
    "tabela <code>metas_45g</code> e foram fixadas uma vez.<br>"
    "2. O <b>volume real</b> pedido na Embalagem oscila ao longo do tempo "
    "(sazonalidade, novos clientes, encomendas).<br>"
    "3. Esta página calcula a <b>média das últimas N segundas/terças/etc.</b> "
    "(janela ajustável abaixo) e compara com a meta fixa.<br>"
    "4. Quando o <b>desvio passa de 20%</b>, o sistema sugere recalibrar a "
    "meta. A Gestão decide se aceita."
    "</div>",
    unsafe_allow_html=True,
)

with st.expander("📚 Explicação detalhada do método (opcional — pro TCC)", expanded=False):
    st.markdown("""
**O problema:** a tabela `metas_45g` foi preenchida uma vez (ex: *"Tradicional 45g
segunda = 5.200 und"*) e ficou fixa. Mas a demanda real muda com o ano (Páscoa,
Festa Junina, Natal, novos clientes, etc.). Se ninguém atualizar manualmente,
o sistema fica trabalhando com **parâmetro defasado**.

**A solução — Média Móvel:** olha as últimas N segundas-feiras, tira a média.
Compara com a meta. Se a média observada subiu/desceu muito, sinaliza:
*"Considera atualizar a meta. A realidade tá X% acima/abaixo."*

**Exemplo numérico passo a passo:**

| Data (segunda) | Ordem Embalagem Tradicional 45g |
|---|---|
| 04/05/2026 | 5.100 und |
| 11/05/2026 | 5.300 und |
| 18/05/2026 | 5.200 und |
| 25/05/2026 | 5.400 und |
| **Média das 4 últimas** | **5.250 und** |
| Meta fixa atual (tabela `metas_45g`) | 5.200 und |
| Diferença | +50 und = **+1%** → **OK** |

Mas se nas últimas 4 segundas a média virou **6.200 und** (+19% sobre 5.200):
*"Demanda real tá 19% acima da meta. Recalibrar?"*

**Sobre a "janela móvel":** é quantas ocorrências do mesmo dia da semana
o cálculo usa.
- **Janela pequena (2-3)** = reage rápido a mudanças, mas pode pegar ruído
- **Janela maior (5-8)** = mais estável, suaviza picos pontuais
- Padrão 4: equilíbrio razoável pra demanda mensal/semanal

**Por que usar `ord_emb_45g` (fluxo de embalagem) e não `emb_45g` (estoque)?**
Estoque (`emb_*`) é foto do que tá na prateleira NO DIA — não pode somar
entre dias. Fluxo (`ord_emb_*`) é demanda pedida NAQUELE dia — pode somar.
Princípio estoque vs fluxo (Forrester, 1961).

**Referência clássica:** Wheelwright, S. C., & Hyndman, R. J. (1998).
*Forecasting: Methods and Applications*. Wiley. Cap. 2 — Moving Averages.
""")


# Slider de janela
col_slider, col_info = st.columns([1, 2])
with col_slider:
    janela = st.slider(
        "Quantas semanas considerar na média?",
        min_value=2, max_value=8, value=4, step=1,
        help="Quantas ocorrências do mesmo dia da semana o cálculo usa. "
             "Ex: 4 = média das últimas 4 segundas, 4 terças, etc.",
    )
with col_info:
    st.markdown(
        f"<div class='didatica'>"
        f"💡 Com janela = <b>{janela}</b>, pra cada dia útil o sistema calcula "
        f"a média das <b>últimas {janela} ocorrências desse dia</b> da semana. "
        f"Ex: pra segundas, pega as últimas {janela} segundas-feiras que tiveram "
        f"ordem de embalagem 45g registrada."
        f"</div>",
        unsafe_allow_html=True,
    )


df_obs, df_mm = calcular_tudo(janela=janela)

if df_obs.empty:
    st.warning(
        "⚠️ Ainda não há folhas com ordens de embalagem 45g (`ord_emb_45g`) preenchidas. "
        "Cadastra algumas folhas em Lançamento antes."
    )
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# RESUMO GERAL
# ════════════════════════════════════════════════════════════════════════════
st.divider()

n_obs = len(df_obs)
n_combos = len(df_mm)
n_recalibrar = (df_mm["severidade"] == "Recalibrar").sum()
n_atencao = (df_mm["severidade"] == "Atenção").sum()

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric(
    "📋 Folhas analisadas (45g)", n_obs,
    help="Quantas linhas de folha tem ordem de embalagem 45g preenchida",
)
col_b.metric(
    "🎯 Combinações analisadas", n_combos,
    help="5 sabores × 5 dias úteis = até 25 combinações possíveis",
)
col_c.metric(
    "🔴 Sugestões de recalibrar", int(n_recalibrar),
    help="Combinações em que a média móvel diverge mais de 20% da meta — "
         "sistema sugere atualizar a meta da tabela",
)
col_d.metric(
    "🟡 Sob atenção", int(n_atencao),
    help="Combinações com desvio entre 10% e 20% — ainda OK mas vale observar",
)

# Mini legenda dos status (logo abaixo das métricas, pra contexto imediato)
st.caption(
    "**Status dos desvios:** "
    "✅ **OK** = diferença < 10% (meta calibrada) · "
    "🟡 **Atenção** = 10-20% (acompanhar) · "
    "🔴 **Recalibrar** = > 20% (meta provavelmente desatualizada)"
)


# ════════════════════════════════════════════════════════════════════════════
# TABELA COMPARATIVA — base × média móvel × desvio
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("📊 Comparativo: Meta × Realidade")
st.caption(
    "Pra cada combinação **sabor × dia útil**, mostra a meta fixa da tabela vs "
    "a média das últimas N ocorrências (realidade). A coluna 'Desvio' mostra "
    "quanto a realidade está acima (+) ou abaixo (–) da meta."
)

df_tab = df_mm.copy()
df_tab["sabor"] = df_tab["sabor"].apply(lambda s: s.capitalize() if s.isupper() else s)
df_tab["sabor"] = df_tab["sabor"].replace({
    "Leite condensado": "Leite Condensado",
    "Pé de moça": "Pé de Moça",
    "Café": "Café",
})
df_tab["base_fmt"] = df_tab["base"].apply(lambda v: f"{int(v):,}" if v else "—")
df_tab["mm_fmt"] = df_tab["media_movel"].apply(lambda v: f"{int(v):,}")
df_tab["desvio_fmt"] = df_tab.apply(
    lambda r: f"{r['desvio_pct']:+.1f}% ({int(r['desvio_abs']):+,})" if r["base"] > 0 else "—",
    axis=1,
)

# Coluna de severidade com emoji
emoji_sev = {"OK": "✅ OK", "Atenção": "🟡 Atenção", "Recalibrar": "🔴 Recalibrar"}
df_tab["sev_fmt"] = df_tab["severidade"].map(emoji_sev)

df_display = df_tab[[
    "sabor", "weekday_pt", "n_observacoes",
    "base_fmt", "mm_fmt", "desvio_fmt", "sev_fmt",
]].copy()
df_display.columns = [
    "Sabor",
    "Dia da semana",
    "Semanas usadas",      # antes "N obs."
    "Meta atual (und)",    # antes "Base (meta)"
    "Realidade (média)",   # antes "Média móvel"
    "Desvio (% e und)",    # antes "Desvio"
    "Status",
]

# Ordena: primeiro 'Recalibrar', depois 'Atenção', depois 'OK'; dentro de cada, sabor
ord_sev = {"Recalibrar": 0, "Atenção": 1, "OK": 2}
df_display = df_display.assign(_ord=df_tab["severidade"].map(ord_sev)).sort_values(
    ["_ord", "Sabor", "Dia"]
).drop(columns="_ord")

st.dataframe(df_display, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# HEATMAP — visualização Sabor × Dia
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("🔥 Mapa de calor: quem precisa de atenção?")
st.caption(
    "Visualização rápida de TODAS as combinações sabor × dia. "
    "Cada quadrado mostra o desvio em %. "
    "**Verde** = realidade próxima da meta (OK). "
    "**Amarelo** = desvio moderado (10-20%). "
    "**Vermelho** = desvio grande (> 20%, sugerir recalibrar). "
    "Quadrados em branco = sem dados pra esse sabor/dia."
)

# Monta matriz wide: sabor × weekday
pivot = df_mm.pivot_table(
    index="sabor", columns="weekday_pt",
    values="desvio_pct", aggfunc="first",
)
# Reordena colunas (segunda → sexta)
ordem_dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
pivot = pivot.reindex(columns=ordem_dias)

# Reordena sabores
ordem_sab = ["TRADICIONAL", "LEITE CONDENSADO", "BRIGADEIRO", "CAFÉ", "PÉ DE MOÇA"]
pivot = pivot.reindex(index=[s for s in ordem_sab if s in pivot.index])

# Rótulos amigáveis
labels_sabor = {
    "TRADICIONAL": "Tradicional",
    "LEITE CONDENSADO": "Leite Condensado",
    "BRIGADEIRO": "Brigadeiro",
    "CAFÉ": "Café",
    "PÉ DE MOÇA": "Pé de Moça",
}
pivot.index = [labels_sabor.get(s, s) for s in pivot.index]

fig_heat = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index,
    colorscale=[
        [0.0, "#B91C1C"],   # vermelho profundo (-50%)
        [0.4, "#FCD34D"],   # amarelo (-10%)
        [0.5, "#10B981"],   # verde (0%)
        [0.6, "#FCD34D"],   # amarelo (+10%)
        [1.0, "#B91C1C"],   # vermelho profundo (+50%)
    ],
    zmid=0,
    zmin=-50, zmax=50,
    text=[[f"{v:+.1f}%" if not pd.isna(v) else "—" for v in row] for row in pivot.values],
    texttemplate="%{text}",
    textfont={"size": 13, "color": "white"},
    hovertemplate="<b>%{y}</b> em <b>%{x}</b><br>Desvio: %{z:+.1f}%<extra></extra>",
    colorbar=dict(title="Desvio %", ticksuffix="%"),
))
fig_heat.update_layout(
    height=380,
    margin=dict(l=20, r=20, t=20, b=40),
    plot_bgcolor="white",
    xaxis=dict(side="top"),
)
st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# DETALHE TEMPORAL — gráfico de linha por sabor
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("📉 Evolução de um sabor ao longo do tempo")
st.caption(
    "Selecione um sabor abaixo pra ver como as ordens de embalagem de 45g "
    "evoluíram dia a dia. Cada cor é um dia da semana — útil pra ver se segundas "
    "subiram mais que sextas, por exemplo. A linha tracejada preta mostra a meta "
    "média semanal do sabor (referência)."
)

sabores_dispo = sorted(df_obs["sabor"].unique().tolist())
sabor_sel = st.selectbox(
    "Escolha o sabor pra detalhar",
    options=sabores_dispo,
    index=0,
    format_func=lambda s: labels_sabor.get(s, s),
)

df_sabor = df_obs[df_obs["sabor"] == sabor_sel].copy().sort_values("data_dt")
df_sabor["weekday_pt"] = df_sabor["weekday"].map(WEEKDAY_TO_PT)

# Pega meta base do sabor
metas = {row["sabor"]: row for row in get_metas_45g()}
meta_sabor = metas.get(sabor_sel, {})

fig_lin = go.Figure()

# Pontos coloridos por dia da semana
cores_dia = {
    "Segunda": "#C05621",
    "Terça":   "#7B341E",
    "Quarta":  "#B45309",
    "Quinta":  "#92400E",
    "Sexta":   "#451A03",
}
for wd_pt, cor in cores_dia.items():
    sub = df_sabor[df_sabor["weekday_pt"] == wd_pt]
    if sub.empty:
        continue
    fig_lin.add_trace(go.Scatter(
        x=sub["data_dt"],
        y=sub["ord_emb_45g"],
        mode="markers+lines",
        name=wd_pt,
        line=dict(color=cor, width=2),
        marker=dict(size=10, color=cor),
        hovertemplate=(
            "<b>%{x|%d/%m/%Y}</b><br>"
            f"{wd_pt}<br>"
            "Ord. embalagem: %{y:,} und<br>"
            "<extra></extra>"
        ),
    ))

# Linha de meta-base (média semanal — média dos 5 dias úteis)
if meta_sabor:
    dias_base = [meta_sabor.get(c) for c in ["segunda", "terca", "quarta", "quinta", "sexta"]]
    dias_base = [int(b) for b in dias_base if b is not None]
    if dias_base:
        media_semana = sum(dias_base) / len(dias_base)
        fig_lin.add_hline(
            y=media_semana,
            line_dash="dash",
            line_color="#1F2937",
            annotation_text=f"Base média semanal = {int(media_semana):,}",
            annotation_position="top left",
        )

fig_lin.update_layout(
    title=f"Ordens de embalagem 45g — {labels_sabor.get(sabor_sel, sabor_sel)}",
    xaxis_title="Data",
    yaxis_title="Unidades pedidas pra embalar",
    height=400,
    margin=dict(l=20, r=20, t=60, b=40),
    plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="closest",
)
st.plotly_chart(fig_lin, use_container_width=True, config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# RECOMENDAÇÕES PRÁTICAS
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("🎯 Sugestões pra atualizar metas defasadas")

recalibrar = df_mm[df_mm["severidade"] == "Recalibrar"].sort_values(
    "desvio_pct", key=lambda s: s.abs(), ascending=False
)

if recalibrar.empty:
    st.markdown(
        "<div class='alerta-ok'>"
        "✅ <b>Nenhuma meta precisa ser atualizada agora.</b> "
        "Todas as combinações sabor × dia da semana têm desvio dentro de ±20% — "
        "as metas fixas estão acompanhando bem a realidade observada."
        "</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<div class='didatica'>"
        "💡 As combinações listadas abaixo têm <b>desvio maior que 20%</b> entre "
        "a meta fixa e a média das últimas semanas. Isso pode indicar que:<br>"
        "&nbsp;&nbsp;• A demanda real mudou (sazonalidade, novos clientes)<br>"
        "&nbsp;&nbsp;• Existe um pedido específico antecipado (não é desvio permanente)<br>"
        "&nbsp;&nbsp;• A meta foi calibrada há muito tempo e ficou defasada<br><br>"
        "<b>A Gestão decide</b> se atualiza a meta ou se aguarda mais semanas. "
        "Sistema só sugere — não muda nada automaticamente."
        "</div>",
        unsafe_allow_html=True,
    )

    for _, row in recalibrar.iterrows():
        sabor_nice = labels_sabor.get(row["sabor"], row["sabor"])
        direcao = "acima" if row["desvio_pct"] > 0 else "abaixo"
        emoji_dir = "📈" if row["desvio_pct"] > 0 else "📉"
        sugestao = int(row["media_movel"])
        st.markdown(
            f"<div class='alerta-alto'>"
            f"<b>{emoji_dir} {sabor_nice} em {row['weekday_pt']}s</b> "
            f"— desvio {direcao} da meta<br>"
            f"&nbsp;&nbsp;• <b>Meta atual:</b> {int(row['base']):,} unidades<br>"
            f"&nbsp;&nbsp;• <b>Realidade</b> (média das últimas {janela} {row['weekday_pt'].lower()}s): {int(row['media_movel']):,} unidades<br>"
            f"&nbsp;&nbsp;• <b>Diferença:</b> {row['desvio_pct']:+.1f}% "
            f"({int(row['desvio_abs']):+,} und)<br>"
            f"&nbsp;&nbsp;• <i>💡 Se atualizar, considere ~{sugestao:,} und como nova meta.</i>"
            f"</div>",
            unsafe_allow_html=True,
        )


st.divider()
st.caption(
    f"📈 Calculado em {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
    f"{n_obs} observações de 45g em {df_obs['sabor'].nunique()} sabores · "
    f"janela móvel de {janela} ocorrências · "
    f"atualiza a cada 30 min ou quando nova folha é salva."
)
st.caption(
    "💡 Esta é a 3ª e última feature da **Fase 1 ROADMAP_IA**. Com Curva ABC + "
    "Detecção de Anomalia + Média Móvel, a Camada 1.5 do sistema está completa."
)
