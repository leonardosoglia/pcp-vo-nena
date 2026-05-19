"""
pages/4_Curva_ABC.py — Análise ABC de sabores

Aplica o princípio de Pareto (80/20) ao histórico de produção da Vó Nena.
Classifica cada produto (sabor × tamanho) em 3 grupos:
    A — 80% acumulado do volume → carros-chefe, prioridade máxima
    B — próximos 15% → cadência regular
    C — últimos 5% → cauda longa, lotes maiores e espaçados

MÉTRICA: BANDEJAS CORTADAS (`ord_corte_*`) acumuladas ao longo das folhas.
Razão (descoberta com Leonardo 17/05/2026): EMBALADO é estoque (snapshot),
NÃO se soma entre dias — "o que tem embalado na sexta também tá na prateleira
segunda". Ordens de corte são FLUXO — cada folha registra a demanda do dia,
e somar dia a dia faz sentido estatístico. Bandeja é a unidade comum de
fluxo entre cocada e palha (não exige conversão por tipo).

Pro Leonardo: o critério aqui responde "quais produtos a fábrica MAIS
PRODUZ ao longo do tempo", não "qual estoque está maior agora".

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

# Bootstrap defensivo: entry point já faz, mas se a página for o primeiro hit,
# garante. HF Spaces não tem secrets.toml — try/except evita StreamlitSecretNotFoundError.
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
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
def _carregar_volume_corte_por_produto():
    """Soma o total de BANDEJAS CORTADAS de cada (sabor × tamanho) ao longo de
    TODAS as folhas registradas.

    MÉTRICA: ord_corte_* — ordens de corte do dia, em BANDEJAS.
    É um FLUXO (cada folha registra demanda do dia), então pode ser somado
    entre dias com significado estatístico válido.

    Por que NÃO usar emb_* (Embalado):
        emb_* é snapshot do estoque atual. Somar emb_45g de seg + ter +
        qua = nonsense estatístico (mistura repetições do mesmo estoque).
        Insight do Leonardo (17/05/2026): "o que tá embalado na sexta tá na
        prateleira segunda também".

    Cocada: ord_corte_45g, ord_corte_mini, ord_corte_pet (bandejas).
        Zero 45g não existe — pula.
    Palha:  ord_corte_50g, ord_corte_pet (bandejas).
        Palha 50g só existe em T, L, CH.

    Retorna DataFrame com colunas:
        produto_completo (str)  — ex: "Cocada Tradicional 45g"
        grupo (str)             — "Cocada" ou "Palha"
        sabor (str)
        tamanho (str)
        volume_band (int)       — total de bandejas cortadas no período
    """
    datas = list_datas_folha()
    if not datas:
        return pd.DataFrame()

    soma = {}  # chave (grupo, sabor, tamanho) -> total em bandejas

    # COCADA: ord_corte_45g, ord_corte_mini, ord_corte_pet (bandejas)
    for d in datas:
        for r in get_folha_cocada(d):
            s = r["sabor"]
            if s == "ZERO":
                # Zero 45g não existe — só Mini e Pet
                tamanhos = [("Mini", "ord_corte_mini"), ("Pet", "ord_corte_pet")]
            else:
                tamanhos = [
                    ("45g", "ord_corte_45g"),
                    ("Mini", "ord_corte_mini"),
                    ("Pet", "ord_corte_pet"),
                ]
            for tam, col in tamanhos:
                qt = int(r.get(col) or 0)
                if qt > 0:
                    chave = ("Cocada", s, tam)
                    soma[chave] = soma.get(chave, 0) + qt

    # PALHA: ord_corte_50g, ord_corte_pet (bandejas)
    for d in datas:
        for r in get_folha_palha(d):
            s = r["sabor"]
            # 50g só existe em T, L, CH
            ord_50 = int(r.get("ord_corte_50g") or 0)
            if ord_50 > 0 and s in ("TRADICIONAL", "LEITE EM PÓ", "CHURROS"):
                chave = ("Palha", s, "50g")
                soma[chave] = soma.get(chave, 0) + ord_50
            ord_pet = int(r.get("ord_corte_pet") or 0)
            if ord_pet > 0:
                chave = ("Palha", s, "Pet")
                soma[chave] = soma.get(chave, 0) + ord_pet

    if not soma:
        return pd.DataFrame()

    linhas = []
    for (grupo, sabor, tamanho), vol in soma.items():
        # Capitaliza sabor pra ficar mais legível (TRADICIONAL → Tradicional)
        sabor_nice = sabor.capitalize() if sabor.isupper() else sabor
        # Palha "LEITE EM PÓ" fica "Leite em Pó" (mantém preposições minúsculas)
        sabor_nice = sabor_nice.replace(" Em ", " em ").replace(" De ", " de ")
        linhas.append({
            "produto_completo": f"{grupo} {sabor_nice} {tamanho}",
            "grupo": grupo,
            "sabor": sabor,
            "tamanho": tamanho,
            "volume_band": vol,
        })
    df = pd.DataFrame(linhas)
    df = df.sort_values("volume_band", ascending=False).reset_index(drop=True)
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
    total = df["volume_band"].sum()
    df = df.copy()
    df["pct"] = df["volume_band"] / total
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
    df = _carregar_volume_corte_por_produto()
    if df.empty:
        return df
    return _classificar_abc(df)


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO + EXPLICAÇÃO DIDÁTICA
# ════════════════════════════════════════════════════════════════════════════
st.title("📊 Curva ABC — Classificação dos Produtos por Volume")
st.caption(
    "Separa automaticamente os produtos da Vó Nena em 3 grupos de prioridade "
    "(A, B, C), baseado em quanto cada um já foi produzido no histórico. "
    "Foca atenção nos que mais movimentam — clássico de Engenharia de Produção."
)

# Resumo curto em destaque
st.markdown(
    "<div class='didatica' style='margin-bottom:14px;'>"
    "<b>📖 Como ler esta página em 30 segundos:</b><br>"
    "1. A regra geral 'da indústria' é que <b>20% dos produtos respondem por "
    "80% do volume produzido</b> (princípio de Pareto). A Curva ABC torna "
    "isso operacional.<br>"
    "2. O sistema soma todas as <b>bandejas cortadas</b> (ord_corte) de cada "
    "produto ao longo de TODAS as folhas registradas.<br>"
    "3. Ordena do maior pro menor e separa em <b>3 grupos</b>:<br>"
    "&nbsp;&nbsp;• <b>Classe A 🟢</b> — os 'carros-chefe' que somam 80% do volume<br>"
    "&nbsp;&nbsp;• <b>Classe B 🟡</b> — produtos intermediários (próximos 15%)<br>"
    "&nbsp;&nbsp;• <b>Classe C 🔴</b> — cauda longa (últimos 5%)<br>"
    "4. <b>Use pra priorizar:</b> Classe A merece atenção diária; Classe C "
    "tolera ficar fora 2-3 dias."
    "</div>",
    unsafe_allow_html=True,
)

with st.expander("📚 Explicação detalhada do método (opcional — pro TCC)", expanded=False):
    st.markdown("""
**O princípio de Pareto** observou que **80% dos efeitos vêm de 20% das
causas** em muitos contextos. Aplicado à indústria, **20% dos produtos
geralmente respondem por 80% do volume produzido**.

A **Curva ABC** operacionaliza essa observação, separando o catálogo em
3 classes de prioridade:

| Classe | Acumula | Como tratar |
|---|---|---|
| **A** | Os primeiros que somam até **80%** do volume | Atenção máxima. Estoque sempre cheio. Cabeça de ordem todo dia. Risco de perda de venda alto se faltar. |
| **B** | Próximos produtos até **95%** | Cadência regular. Tolera ficar sem 1 dia. Atenção média. |
| **C** | Últimos produtos (5% finais) | Lotes maiores e mais espaçados. Tolera 2-3 dias fora. Atenção mínima. |

**Métrica usada nesta página: bandejas cortadas (`ord_corte_*`)** —
acumuladas ao longo de TODAS as folhas registradas.

**Por que NÃO somar "Embalados" (estoque na prateleira)?**

> *Insight do Leonardo (17/05/2026):* o campo "Embalado" é o ESTOQUE NA
> PRATELEIRA em cada dia, não o que passou pela embalagem. Se segunda tem
> 1.000 embalados e terça tem 950 (porque vendeu 50 e não embalou nada
> novo), somar daria 1.950 — como se 1.950 tivessem sido produzidos. Mas
> só 1.000 passaram pela embalagem.

**Ordens de corte (`ord_corte_*`) são FLUXO:** cada folha registra quantas
bandejas a Gestão pediu pra cortar naquele dia. Somar dias faz sentido
estatístico — é igual somar entrada/saída de um caixa, não saldo final.
Princípio **estoque vs fluxo** (Forrester, 1961, *Industrial Dynamics*).

**Bandejas (não unidades) como unidade:** cocada e palha têm rendimentos
diferentes por bandeja. Bandeja é a unidade comum de fluxo entre os dois.
Evita conversões com números inventados.

**Referência clássica:** Juran, J. M. (1951). *Quality Control Handbook*.
Princípio originalmente proposto por **Vilfredo Pareto (1896)** ao estudar
distribuição de renda na Itália — observou que 80% da terra pertencia a
20% da população. Generalizou-se como **"Lei de Pareto"** em economia,
qualidade e gestão.
""")


df_abc = calcular_curva_abc()

if df_abc.empty:
    st.warning(
        "⚠️ Ainda não há folhas com ordens de corte (`ord_corte_*`) preenchidas. "
        "Cadastra algumas folhas com ordens de corte em Lançamento antes."
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
    vol = int(df_grupo["volume_band"].sum())
    pct = float(df_grupo["pct"].sum()) * 100
    with col:
        st.markdown(
            f"<div class='card-{classe.lower()}'>"
            f"<b style='font-size:22px;'>Classe {classe}</b><br>"
            f"<span style='font-size:13px;opacity:0.9;'>{descricao}</span>"
            f"<hr style='border-color:rgba(255,255,255,0.3);margin:8px 0;'>"
            f"<b>{qt}</b> produtos · <b>{vol:,}</b> bandejas · <b>{pct:.1f}%</b>"
            f"</div>",
            unsafe_allow_html=True,
        )


st.divider()


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO DE PARETO (barras + linha cumulativa)
# ════════════════════════════════════════════════════════════════════════════
st.header("📈 Diagrama de Pareto")
st.caption(
    "Barras = bandejas cortadas (volume acumulado nas folhas registradas, eixo esquerdo). "
    "Linha = % acumulado do volume total (eixo direito). "
    "A linha cruza 80% no fim da Classe A — a partir dali são produtos secundários."
)

fig = go.Figure()

# Cores por classe
cor_por_classe = {"A": "#059669", "B": "#B45309", "C": "#991B1B"}
cores_barras = [cor_por_classe[c] for c in df_abc["classe"]]

fig.add_trace(go.Bar(
    x=df_abc["produto_completo"],
    y=df_abc["volume_band"],
    name="Bandejas cortadas (acumulado)",
    marker_color=cores_barras,
    text=[f"{v:,}" for v in df_abc["volume_band"]],
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Volume: %{y:,} bandejas<br>"
        "<extra></extra>"
    ),
))

fig.add_trace(go.Scatter(
    x=df_abc["produto_completo"],
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
    yaxis=dict(title="Bandejas cortadas (acumulado)", side="left"),
    yaxis2=dict(title="% acumulado", side="right", overlaying="y",
                range=[0, 105], ticksuffix="%"),
    height=580,  # +60 pra acomodar nomes mais longos no eixo X
    margin=dict(l=20, r=20, t=40, b=180),  # +60 de bottom pelos nomes longos
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
df_tab["volume_band"] = df_tab["volume_band"].apply(lambda v: f"{v:,}")
df_tab["pct"] = (df_abc["pct"] * 100).apply(lambda v: f"{v:.1f}%")
df_tab["pct_acumulado"] = (df_abc["pct_acumulado"] * 100).apply(lambda v: f"{v:.1f}%")
df_tab = df_tab[["produto_completo", "classe", "volume_band", "pct", "pct_acumulado"]]
df_tab.columns = ["Produto", "Classe", "Bandejas cortadas", "% do total", "% acumulado"]

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
