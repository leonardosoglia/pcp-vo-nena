"""
pages/6_Media_Movel.py — Média Móvel por dia da semana

Compara a META BASE da tabela metas_45g (parâmetro fixo definido pela Gestão)
com a MÉDIA MÓVEL OBSERVADA nas últimas N ocorrências do mesmo dia da semana.

Métrica usada: Cortados² 45g = emb_45g + cort1_45g + joel_45g (3 camadas
de produto cortado — fórmula clássica do sistema, ver database.py:21).

Histórico: até 26/05 usava `ord_emb_45g` (só ordem de embalagem do dia),
que dava mapa SEMPRE vermelho porque é fração pequena. Corrigido após
feedback do Leonardo 26/05 — agora reflete o estoque REAL de produto
cortado no dia (todas as 3 camadas somadas).

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
    list_datas_folha, get_folha_cocada, get_papelzinho_joel, get_metas_45g,
    SABORES_COCADA,
)

st.set_page_config(
    page_title="Média Móvel • Doces Vó Nena",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tema visual centralizado (Inter font + paleta clean)
from ui_theme import aplicar_tema
aplicar_tema()


# Mapas pra trabalhar com dia da semana
WEEKDAY_TO_COL = {0: "segunda", 1: "terca", 2: "quarta", 3: "quinta", 4: "sexta"}
WEEKDAY_TO_PT = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta"}


# ════════════════════════════════════════════════════════════════════════════
# CÁLCULOS
# ════════════════════════════════════════════════════════════════════════════
def _carregar_observacoes_45g():
    """Retorna DataFrame com colunas: data, weekday, weekday_pt, sabor, cortados2_45g.

    `cortados2_45g` = emb_45g + cort1_45g + joel_45g (fórmula clássica do sistema,
    ver database.py:21). Representa o TOTAL de produto cortado 45g (em und) na
    fábrica naquele dia — soma das 3 camadas:
      - embalado (estoque/venda)
      - cortado sala da Embalagem (cort1_45g)
      - cortado pela Produção (joel_45g, papelzinho)

    Antes (até 26/05/2026) esta página usava `ord_emb_45g` — que é só a ordem
    de embalagem do dia, uma fração pequena. Resultado: mapa de calor SEMPRE
    vermelho (fugia da realidade). Corrigido pra Cortados² após feedback do
    Leonardo (26/05).
    """
    datas = list_datas_folha()
    if not datas:
        return pd.DataFrame()
    linhas = []
    for d in datas:
        folha = get_folha_cocada(d)
        papel_rows = get_papelzinho_joel(d)
        papel_by = {r["sabor"]: r for r in papel_rows} if papel_rows else {}
        for r in folha:
            s = r["sabor"]
            if s == "ZERO":
                continue  # Zero 45g não existe
            emb = int(r.get("emb_45g") or 0)
            cort1 = int(r.get("cort1_45g") or 0)
            joel = int((papel_by.get(s) or {}).get("joel_45g") or 0)
            cortados2 = emb + cort1 + joel
            if cortados2 > 0:
                data_dt = datetime.strptime(d, "%Y-%m-%d")
                wd = data_dt.weekday()
                if wd < 5:  # só dia útil
                    linhas.append({
                        "data": d,
                        "data_dt": data_dt,
                        "weekday": wd,
                        "weekday_pt": WEEKDAY_TO_PT[wd],
                        "sabor": s,
                        "cortados2_45g": cortados2,
                        "emb_45g": emb,
                        "cort1_45g": cort1,
                        "joel_45g": joel,
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
            mm = float(ultimas["cortados2_45g"].mean())

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


@st.cache_data(ttl=1800, show_spinner="Calculando médias móveis...")
def calcular_tudo(janela=4):
    df_obs = _carregar_observacoes_45g()
    if df_obs.empty:
        return df_obs, pd.DataFrame()
    df_mm = _calcular_media_movel(df_obs, janela=janela)
    return df_obs, df_mm


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ════════════════════════════════════════════════════════════════════════════
st.title("Calibração de metas")
st.caption(
    "Compara a **meta-base 45g** (tabela `metas_45g`, fixa) com o **Cortados² médio** "
    "observado nas últimas semanas — `emb_45g + cort sala + papelzinho da Produção`. "
    "Mostra onde a realidade se descolou do parâmetro e pede recalibração."
)


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
    st.caption(
        f"Considerando as últimas **{janela}** ocorrências de cada dia da semana."
    )


df_obs, df_mm = calcular_tudo(janela=janela)

if df_obs.empty:
    st.warning(
        "Ainda não há folhas com estoque 45g lançado. "
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
    "Folhas analisadas (45g)", n_obs,
    help="Quantas linhas de folha tem produto 45g cortado (emb + cort sala + papelzinho)",
)
col_b.metric(
    "Combinações analisadas", n_combos,
    help="5 sabores × 5 dias úteis = até 25 combinações possíveis",
)
col_c.metric(
    "Sugestões de recalibrar", int(n_recalibrar),
    help="Combinações em que a média móvel diverge mais de 20% da meta — "
         "sistema sugere atualizar a meta da tabela",
)
col_d.metric(
    "Sob atenção", int(n_atencao),
    help="Combinações com desvio entre 10% e 20% — ainda OK mas vale observar",
)

st.caption(
    "**Status:** OK (<10%) · Atenção (10-20%) · Recalibrar (>20%)"
)


# ════════════════════════════════════════════════════════════════════════════
# TABELA COMPARATIVA — base × média móvel × desvio
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Meta × realidade")

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

# Coluna de severidade
df_tab["sev_fmt"] = df_tab["severidade"]

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
    ["_ord", "Sabor", "Dia da semana"]
).drop(columns="_ord")

st.dataframe(df_display, width='stretch', hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# HEATMAP — visualização Sabor × Dia
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Mapa de calor")
st.caption(
    "Azul = OK · Âmbar = atenção · Vermelho = recalibrar · Branco = sem dados."
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
        [0.4, "#B45309"],   # âmbar (-10%)
        [0.5, "#0E7490"],   # azul/positivo (0%)
        [0.6, "#B45309"],   # âmbar (+10%)
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
fig_heat.update_xaxes(fixedrange=True)
fig_heat.update_yaxes(fixedrange=True)
st.plotly_chart(fig_heat, width='stretch', config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# DETALHE TEMPORAL — gráfico de linha por sabor
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Evolução temporal")
st.caption(
    "Cores = dias da semana · linha tracejada = meta média semanal."
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
    "Terça":   "#0E7490",
    "Quarta":  "#B45309",
    "Quinta":  "#A8A29E",
    "Sexta":   "#991B1B",
}
for wd_pt, cor in cores_dia.items():
    sub = df_sabor[df_sabor["weekday_pt"] == wd_pt]
    if sub.empty:
        continue
    fig_lin.add_trace(go.Scatter(
        x=sub["data_dt"],
        y=sub["cortados2_45g"],
        mode="markers+lines",
        name=wd_pt,
        line=dict(color=cor, width=2),
        marker=dict(size=10, color=cor),
        hovertemplate=(
            "<b>%{x|%d/%m/%Y}</b><br>"
            f"{wd_pt}<br>"
            "Cortados² 45g: %{y:,} und<br>"
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
            line_color="#0E7490",
            annotation_text=f"Base média semanal = {int(media_semana):,}",
            annotation_position="top left",
        )

fig_lin.update_layout(
    title=f"Cortados² 45g (emb + cort sala + papelzinho) — {labels_sabor.get(sabor_sel, sabor_sel)}",
    xaxis_title="Data",
    yaxis_title="Cortados² — unidades de 45g",
    height=400,
    margin=dict(l=20, r=20, t=60, b=40),
    plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="closest",
)
fig_lin.update_xaxes(fixedrange=True)
fig_lin.update_yaxes(fixedrange=True)
st.plotly_chart(fig_lin, width='stretch', config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# RECOMENDAÇÕES PRÁTICAS
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Sugestões de recalibração")

recalibrar = df_mm[df_mm["severidade"] == "Recalibrar"].sort_values(
    "desvio_pct", key=lambda s: s.abs(), ascending=False
)

if recalibrar.empty:
    st.success("Nenhuma meta precisa de atualização. Todas dentro de ±20%.")
else:
    # Tabela compacta em vez de cards longos
    df_sug = pd.DataFrame([
        {
            "Sabor": labels_sabor.get(row["sabor"], row["sabor"]),
            "Dia": f"{row['weekday_pt']}s",
            "Meta atual": f"{int(row['base']):,}",
            "Realidade": f"{int(row['media_movel']):,}",
            "Desvio": f"{row['desvio_pct']:+.1f}%",
            "Sugestão nova meta": f"~{int(row['media_movel']):,}",
        }
        for _, row in recalibrar.iterrows()
    ])
    st.dataframe(df_sug, width='stretch', hide_index=True)
    st.caption(
        "_A Gestão decide se atualiza as metas. Sistema apenas sugere baseado "
        "na média recente — pode ser sazonalidade ou pedido pontual._"
    )


st.divider()
st.caption(
    f"Análise atualizada em {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
    f"{n_obs} observações · janela {janela} · cache 30 min."
)
