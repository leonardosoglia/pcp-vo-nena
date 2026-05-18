"""
pages/4_Curva_ABC.py — Análise ABC de sabores

Aplica o princípio de Pareto (80/20) ao histórico de produção da Vó Nena.
Classifica cada produto (sabor × tamanho) em 3 grupos:
    A — 80% acumulado do volume → carros-chefe, prioridade máxima
    B — próximos 15% → cadência regular
    C — últimos 5% → cauda longa, lotes maiores e espaçados

Fonte da verdade: EMBALADOS (produto acabado pronto pra venda), não ordens.
Razão: ordem mostra intenção; embalado mostra realidade.

Atualiza automaticamente conforme novas folhas entram. Quanto mais histórico,
mais confiável a classificação.

Capítulo TCC associado: "Aplicação da Curva ABC no PCP em confeitaria
industrial — apoio à priorização operacional".
Referência clássica: Juran, J. M. (1951) Quality Control Handbook + Pareto.
"""
import streamlit as st
import pandas as pd
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
    list_datas_folha, get_folha_cocada, get_folha_palha,
    SABORES_COCADA, SABORES_PALHA,
)

st.set_page_config(
    page_title="Curva ABC • Doces Vó Nena",
    page_icon="📊",
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
    .card-a {
        background: linear-gradient(135deg, #065F46 0%, #047857 100%);
        color: #ECFDF5; padding: 18px 22px; border-radius: 10px; margin: 8px 0;
    }
    .card-b {
        background: linear-gradient(135deg, #92400E 0%, #B45309 100%);
        color: #FFFBEB; padding: 18px 22px; border-radius: 10px; margin: 8px 0;
    }
    .card-c {
        background: linear-gradient(135deg, #7F1D1D 0%, #991B1B 100%);
        color: #FEE2E2; padding: 18px 22px; border-radius: 10px; margin: 8px 0;
    }
    .didatica {
        background: #FFFBEB; border-left: 5px solid #D97706;
        border-radius: 6px; padding: 14px 18px; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CÁLCULOS
# ════════════════════════════════════════════════════════════════════════════
def _carregar_embalados_por_produto():
    """Soma o total embalado de cada (sabor × tamanho) ao longo de TODAS as folhas.

    Cocada: EMB 45g, EMB Mini, EMB Pet (unidades)
    Palha:  EMB 50g (× 10 = unidades de palha), EMB Pet (unidades)

    Retorna DataFrame com colunas:
        produto (str)  — ex: "Cocada T 45g"
        grupo (str)    — "Cocada" ou "Palha"
        sabor (str)
        tamanho (str)
        volume_und (int)  — total embalado no período
    """
    datas = list_datas_folha()
    if not datas:
        return pd.DataFrame()

    soma = {}  # chave (grupo, sabor, tamanho) -> total em unidades

    # COCADA: emb_45g, emb_mini, emb_pet
    for d in datas:
        for r in get_folha_cocada(d):
            s = r["sabor"]
            if s == "ZERO":
                # Zero 45g não existe — só Mini e Pet
                tamanhos = [("Mini", "emb_mini"), ("Pet", "emb_pet")]
            else:
                tamanhos = [("45g", "emb_45g"), ("Mini", "emb_mini"), ("Pet", "emb_pet")]
            for tam, col in tamanhos:
                qt = int(r.get(col) or 0)
                if qt > 0:
                    chave = ("Cocada", s, tam)
                    soma[chave] = soma.get(chave, 0) + qt

    # PALHA: emb_50g e emb_pet ambos em UNIDADES (schema database.py:516)
    for d in datas:
        for r in get_folha_palha(d):
            s = r["sabor"]
            # 50g só existe em T, L, CH
            emb_50g = int(r.get("emb_50g") or 0)
            if emb_50g > 0 and s in ("TRADICIONAL", "LEITE EM PÓ", "CHURROS"):
                chave = ("Palha", s, "50g")
                soma[chave] = soma.get(chave, 0) + emb_50g
            emb_pet = int(r.get("emb_pet") or 0)
            if emb_pet > 0:
                chave = ("Palha", s, "Pet")
                soma[chave] = soma.get(chave, 0) + emb_pet

    if not soma:
        return pd.DataFrame()

    linhas = []
    for (grupo, sabor, tamanho), vol in soma.items():
        linhas.append({
            "produto": f"{grupo[:1]} {sabor[:3]} {tamanho}",
            "produto_completo": f"{grupo} {sabor} {tamanho}",
            "grupo": grupo,
            "sabor": sabor,
            "tamanho": tamanho,
            "volume_und": vol,
        })
    df = pd.DataFrame(linhas)
    df = df.sort_values("volume_und", ascending=False).reset_index(drop=True)
    return df


def _classificar_abc(df, corte_a=0.80, corte_b=0.95):
    """Adiciona colunas 'pct', 'pct_acumulado' e 'classe' ao DataFrame.

    Convenção clássica (Juran):
        A = produtos que somam até 80% do volume cumulativo
        B = de 80% até 95%
        C = últimos 5%
    """
    if df.empty:
        return df
    total = df["volume_und"].sum()
    df = df.copy()
    df["pct"] = df["volume_und"] / total
    df["pct_acumulado"] = df["pct"].cumsum()

    def _classe(pct_acum):
        if pct_acum <= corte_a:
            return "A"
        elif pct_acum <= corte_b:
            return "B"
        return "C"

    df["classe"] = df["pct_acumulado"].apply(_classe)
    return df


@st.cache_data(ttl=1800, show_spinner="🔍 Calculando Curva ABC...")
def calcular_curva_abc():
    df = _carregar_embalados_por_produto()
    if df.empty:
        return df
    return _classificar_abc(df)


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO + EXPLICAÇÃO DIDÁTICA
# ════════════════════════════════════════════════════════════════════════════
st.title("📊 Curva ABC de produtos")
st.caption(
    "Classifica automaticamente os produtos da Vó Nena em 3 grupos de prioridade, "
    "baseado no princípio de Pareto (80/20). Quanto mais histórico, mais confiável."
)

with st.expander("ℹ️ Como funciona a Curva ABC (clica pra entender)", expanded=False):
    st.markdown("""
**O princípio de Pareto** diz que numa fábrica, normalmente **20% dos produtos
geram 80% do volume**. A Curva ABC operacionaliza isso, separando o catálogo em:

| Classe | O que representa | Como tratar |
|---|---|---|
| **A** | Top produtos — somam **80%** do volume embalado | Atenção máxima. Estoque sempre cheio. Cabeça de ordem todo dia. |
| **B** | Intermediários — próximos **15%** | Cadência regular. Tolera ficar sem 1 dia. |
| **C** | Cauda longa — últimos **5%** | Lotes maiores e mais espaçados. Tolera 2-3 dias fora. |

**Esta página usa EMBALADOS** (produto acabado pronto pra venda) como métrica,
não ordens nem cortados. Razão: ordem mostra intenção; embalado mostra realidade.

**Referência clássica:** Juran, J. M. (1951). *Quality Control Handbook*.
Princípio originalmente proposto por Vilfredo Pareto (1896) ao estudar
distribuição de renda na Itália — observou que 80% da terra pertencia a 20%
da população.
""")


df_abc = calcular_curva_abc()

if df_abc.empty:
    st.warning(
        "⚠️ Ainda não há folhas com EMBALADOS preenchidos. "
        "Cadastra algumas folhas em Lançamento antes."
    )
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# RESUMO POR CLASSE
# ════════════════════════════════════════════════════════════════════════════
st.divider()

col_a, col_b, col_c = st.columns(3)

for col, classe, descricao, cor in [
    (col_a, "A", "Carros-chefe (80% do volume)", "#059669"),
    (col_b, "B", "Intermediários (+15%)", "#B45309"),
    (col_c, "C", "Cauda longa (últimos 5%)", "#991B1B"),
]:
    df_grupo = df_abc[df_abc["classe"] == classe]
    qt = len(df_grupo)
    vol = int(df_grupo["volume_und"].sum())
    pct = float(df_grupo["pct"].sum()) * 100
    with col:
        st.markdown(
            f"<div class='card-{classe.lower()}'>"
            f"<b style='font-size:22px;'>Classe {classe}</b><br>"
            f"<span style='font-size:13px;opacity:0.9;'>{descricao}</span>"
            f"<hr style='border-color:rgba(255,255,255,0.3);margin:8px 0;'>"
            f"<b>{qt}</b> produtos · <b>{vol:,}</b> und · <b>{pct:.1f}%</b>"
            f"</div>",
            unsafe_allow_html=True,
        )


st.divider()


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO DE PARETO (barras + linha cumulativa)
# ════════════════════════════════════════════════════════════════════════════
st.header("📈 Diagrama de Pareto")
st.caption(
    "Barras = volume de cada produto (eixo esquerdo). "
    "Linha = % acumulado do volume total (eixo direito). "
    "A linha cruza 80% no fim da Classe A."
)

fig = go.Figure()

# Cores por classe
cor_por_classe = {"A": "#059669", "B": "#B45309", "C": "#991B1B"}
cores_barras = [cor_por_classe[c] for c in df_abc["classe"]]

fig.add_trace(go.Bar(
    x=df_abc["produto"],
    y=df_abc["volume_und"],
    name="Volume embalado (und)",
    marker_color=cores_barras,
    text=[f"{v:,}" for v in df_abc["volume_und"]],
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Volume: %{y:,} und<br>"
        "<extra></extra>"
    ),
))

fig.add_trace(go.Scatter(
    x=df_abc["produto"],
    y=df_abc["pct_acumulado"] * 100,
    name="% acumulado",
    yaxis="y2",
    mode="lines+markers",
    line=dict(color="#1F2937", width=3),
    marker=dict(size=8, color="#1F2937"),
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Acumulado: %{y:.1f}%<br>"
        "<extra></extra>"
    ),
))

# Linhas horizontais de referência: 80% (corte A) e 95% (corte B)
fig.add_hline(
    y=80, yref="y2",
    line_dash="dash", line_color="#059669", line_width=1.5,
    annotation_text="80% (fim da Classe A)", annotation_position="top left",
)
fig.add_hline(
    y=95, yref="y2",
    line_dash="dash", line_color="#B45309", line_width=1.5,
    annotation_text="95% (fim da Classe B)", annotation_position="bottom left",
)

fig.update_layout(
    xaxis=dict(title="Produto", tickangle=-45),
    yaxis=dict(title="Volume embalado (unidades)", side="left"),
    yaxis2=dict(title="% acumulado", side="right", overlaying="y",
                range=[0, 105], ticksuffix="%"),
    height=520,
    margin=dict(l=20, r=20, t=40, b=120),
    plot_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# TABELA DETALHADA
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("📋 Detalhamento por produto")

df_tab = df_abc.copy()
df_tab["volume_und"] = df_tab["volume_und"].apply(lambda v: f"{v:,}")
df_tab["pct"] = (df_abc["pct"] * 100).apply(lambda v: f"{v:.1f}%")
df_tab["pct_acumulado"] = (df_abc["pct_acumulado"] * 100).apply(lambda v: f"{v:.1f}%")
df_tab = df_tab[["produto_completo", "classe", "volume_und", "pct", "pct_acumulado"]]
df_tab.columns = ["Produto", "Classe", "Volume embalado (und)", "% do total", "% acumulado"]

st.dataframe(df_tab, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# RECOMENDAÇÕES OPERACIONAIS
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("🎯 Recomendações práticas pela classe")

st.markdown("""
<div class='didatica'>
<b>⚠️ Importante:</b> a Curva ABC é uma <i>ferramenta de apoio à decisão</i>, não
um comando. A Gestão pode (e deve) ajustar quando há restrição operacional
(mão de obra, insumo, encomenda específica). O sistema mostra o padrão; o
humano decide.
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🟢 Classe A")
    produtos_a = df_abc[df_abc["classe"] == "A"]["produto_completo"].tolist()
    st.markdown("**O que fazer:**")
    st.markdown("""
- Estoque sempre cheio
- Ordem de produção todo dia útil
- Falta = perda de venda imediata
- Conferir estoque antes de qualquer outro
""")
    if produtos_a:
        st.markdown("**Produtos nesta classe:**")
        for p in produtos_a:
            st.markdown(f"- {p}")

with col2:
    st.markdown("### 🟡 Classe B")
    produtos_b = df_abc[df_abc["classe"] == "B"]["produto_completo"].tolist()
    st.markdown("**O que fazer:**")
    st.markdown("""
- Cadência regular (ex: 3-4× por semana)
- Tolera 1 dia sem produzir
- Estoque de segurança menor
- Pode ajustar conforme demanda do mês
""")
    if produtos_b:
        st.markdown("**Produtos nesta classe:**")
        for p in produtos_b:
            st.markdown(f"- {p}")

with col3:
    st.markdown("### 🔴 Classe C")
    produtos_c = df_abc[df_abc["classe"] == "C"]["produto_completo"].tolist()
    st.markdown("**O que fazer:**")
    st.markdown("""
- Lotes maiores e espaçados (1-2× semana)
- Tolera 2-3 dias sem estoque
- Considerar tirar de catálogo se cair muito
- Evitar produzir sob pressão de tempo
""")
    if produtos_c:
        st.markdown("**Produtos nesta classe:**")
        for p in produtos_c:
            st.markdown(f"- {p}")


st.divider()
st.caption(
    f"📊 Curva ABC gerada em {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
    f"baseada em {len(df_abc)} produtos com volume registrado · "
    f"recalculada a cada 30 minutos ou ao salvar nova folha."
)
st.caption(
    "💡 Esta classificação vai se refinar conforme novas folhas entram. "
    "Em ~3 meses (~60 folhas), a Curva ABC vira referência confiável pra decisões "
    "estruturais como mix de catálogo e estoque de segurança por sabor."
)
