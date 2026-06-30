# -*- coding: utf-8 -*-
"""
pages/15_Lucratividade.py — O que puxa o resultado: contribuição (receita − custo
do material) por produto, a partir das vendas reais do SIGE × custo do BOM.

A visão diferenciada pro gestor: deixa de ser "o que vende mais" e passa a ser
"o que mais CONTRIBUI". 4 quadros: (1) quem mais contribui, (2) custo por kg por
sabor (alerta Zero), (3) matriz giro × ticket, (4) produção × venda.

HONESTIDADE (sempre visível na tela): contribuição = receita − custo de MATÉRIA-
PRIMA. NÃO é lucro líquido (falta o custo de conversão, externo ao SIGE). Cobre a
parte da receita com custo mapeado (cocada por peso + Pão de Mel); o resto fica
marcado. Lógica em contribuicao_produto.py (testada via CLI).

SOMENTE LEITURA: lê o SIGE (pedidos) e o nosso banco (custos/folhas) — não escreve.
NOTA: precisa do token SIGE nos Secrets do ambiente (HF).
"""
import os
import sys
from datetime import date, datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Bootstrap defensivo — propaga DATABASE_URL + credenciais SIGE de st.secrets.
try:
    for _k in ("DATABASE_URL", "SIGE_AUTH_TOKEN", "SIGE_USER", "SIGE_APP",
               "SIGE_DEPOSITO_PADRAO"):
        if not os.getenv(_k) and _k in st.secrets:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

import sige_cloud_api as sige
import vendas_sige as vs
import contribuicao_produto as cpr
import componentes

st.set_page_config(
    page_title="Lucratividade • Doces Vó Nena",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui_theme import aplicar_tema
aplicar_tema()

# Paleta (consistente com o app)
COR_CONTRIB = "#C05621"   # laranja Vó Nena — contribuição
COR_NEUTRO = "#A8A29E"    # cinza — produção / barras neutras
COR_ALERTA = "#B91C1C"    # vermelho — alerta (Zero)
COR_CUBOS = "#0E7490"     # azul-petróleo — cubos
COR_PM = "#B45309"        # caramelo — pão de mel
ORDEM_SABOR = ["Tradicional", "Leite Condensado", "Zero", "Café", "Brigadeiro", "Pé de Moça"]


def _brl(v, milhar=False) -> str:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return "R$ 0"
    if milhar:
        return "R$ " + f"{x/1000:,.0f}".replace(",", ".") + " mil"
    s = f"{x:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def _brl0(v) -> str:
    """Reais sem centavos (R$ 1.234) — pra tabelas com valores grandes."""
    try:
        return "R$ " + f"{float(v):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "R$ 0"


def _categoria(desc: str) -> str:
    d = (desc or "").upper()
    if "PAO DE MEL" in d or "PÃO DE MEL" in d:
        return "Pão de mel"
    if "TABLETE" in d:
        return "Tablete"
    return "Cubos / pedaço"


def _nome_curto(desc, n=38) -> str:
    """Nome do produto sem o código, encurtado preservando a gramatura (evita que
    'Tablete Leite Condensado 30g' e '45g' fiquem com o mesmo rótulo cortado)."""
    s = str(desc or "").split(" - ")[-1].strip()
    return s if len(s) <= n else s[:n - 1] + "…"


def _percentil(valores_ordenados, p):
    """Percentil simples (sem numpy) de uma lista JÁ ordenada."""
    if not valores_ordenados:
        return 0.0
    i = min(len(valores_ordenados) - 1,
            int(round((p / 100) * (len(valores_ordenados) - 1))))
    return valores_ordenados[i]


@st.cache_data(ttl=1800, show_spinner="Calculando a lucratividade...")
def carregar(d_ini: str, d_fim: str):
    """Lê vendas (SIGE) + custos (banco) e calcula a contribuição. Read-only."""
    con = sige.testar_conexao()
    if not con["ok"]:
        return None, con["mensagem"]
    try:
        import database as db
        pedidos = sige.listar_todos_pedidos(d_ini, d_fim)
        ag = vs.agregar_vendas(pedidos)
        res = cpr.contribuicao(db, ag)
        res["por_sabor"] = cpr.contribuicao_por_sabor(res["linhas"])
        res["producao"] = cpr.producao_por_sabor(db)
        res["n_pedidos"] = len(pedidos)
    except Exception as e:
        return None, str(e)
    return res, None


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ════════════════════════════════════════════════════════════════════════════
st.title("Lucratividade — o que puxa o resultado")
st.caption(
    "Vendas reais do SIGE cruzadas com o custo do material. **Contribuição = "
    "receita − custo do material** (o que sobra pra pagar a operação). Ainda não "
    "é o lucro final — falta o custo de mão de obra/energia, em levantamento. "
    "Somente leitura."
)

if not sige.credenciais_configuradas():
    st.warning(
        "**Token do SIGE não configurado neste ambiente.** Defina `SIGE_AUTH_TOKEN`, "
        "`SIGE_USER` e `SIGE_APP` nos *Secrets* do Hugging Face para esta tela funcionar."
    )
    st.stop()

hoje = date.today()
c_data, c_btn = st.columns([3, 1])
with c_data:
    periodo = st.date_input("Período das vendas",
                            value=(hoje - timedelta(days=30), hoje),
                            max_value=hoje, format="DD/MM/YYYY")
with c_btn:
    st.write("")
    if st.button("🔄 Carregar / atualizar do SIGE", use_container_width=True):
        st.session_state["lucr_go"] = True

if not isinstance(periodo, (tuple, list)) or len(periodo) != 2:
    st.info("Escolha a data **final** do período para calcular.")
    st.stop()

d_ini, d_fim = periodo[0].strftime("%Y-%m-%d"), periodo[1].strftime("%Y-%m-%d")

# Carregamento preguiçoso: a tela abre na hora; só lê o SIGE quando você clica.
_chave = f"{d_ini}_{d_fim}"
if st.session_state.pop("lucr_go", False):
    st.session_state["lucr_loaded"] = _chave
    carregar.clear()
if st.session_state.get("lucr_loaded") != _chave:
    st.info("A tela abre na hora. Escolha o período e clique em **Carregar / atualizar "
            "do SIGE** para puxar os dados (leva ~1 min na 1ª vez; depois fica em cache).")
    st.stop()

res, erro = carregar(d_ini, d_fim)
if erro:
    st.error(f"Não consegui calcular agora: {erro}")
    st.stop()

mapeados = [l for l in res["linhas"] if l["mapeado"]]
if not mapeados:
    st.info("Nenhuma venda com custo mapeado no período.")
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
# CARTÕES DE RESUMO
# ════════════════════════════════════════════════════════════════════════════
custo_kg = res["custo_kg"]
mais_caro = max(custo_kg.values(), key=lambda d: d["custo_kg"] or 0)
campeao = max(mapeados, key=lambda l: l["contrib"])

st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Receita analisada", _brl(res["receita_coberta"], milhar=True),
          f"{res['cobertura_pct']:.0f}% das vendas")
k2.metric("Contribuição (material)", _brl(res["contrib_total"], milhar=True))
k3.metric("Mais caro por quilo", mais_caro["label"], _brl(mais_caro["custo_kg"]) + "/kg")
k4.metric("Campeão de contribuição",
          str(campeao["descricao"]).split(" - ")[-1][:16], _brl(campeao["contrib"], milhar=True))


# ════════════════════════════════════════════════════════════════════════════
# QUADRO 1 — QUEM MAIS CONTRIBUI
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Quem mais contribui")
st.caption("Quanto cada produto deixa depois do custo do material, no período. "
           "É a Curva ABC por **retorno**, não por volume.")

top = sorted(mapeados, key=lambda l: l["contrib"])[-12:]  # ascendente p/ maior no topo
nomes = [_nome_curto(l["descricao"]) for l in top]
vals = [l["contrib"] for l in top]
fig1 = go.Figure(go.Bar(
    x=vals, y=nomes, orientation="h", marker_color=COR_CONTRIB,
    text=[_brl(v, milhar=True) for v in vals], textposition="auto",
    hovertemplate="<b>%{y}</b><br>Contribuição: %{text}<extra></extra>",
))
fig1.update_layout(
    height=460, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
    xaxis=dict(title="contribuição de material (R$)", tickformat=",.0f"),
    yaxis=dict(title=""))
fig1.update_xaxes(fixedrange=True)
fig1.update_yaxes(fixedrange=True)
st.plotly_chart(fig1, width="stretch", config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# QUADRO 2 — CUSTO POR KG POR SABOR
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("O custo de cada sabor, por quilo")
st.caption("A **Zero** é a mais cara de produzir — adoçantes especiais e rende "
           "menos por tacho.")

ck = sorted(custo_kg.values(), key=lambda d: d["custo_kg"] or 0)
labels_kg = [d["label"] for d in ck]
vals_kg = [round(d["custo_kg"], 2) for d in ck]
cores_kg = [COR_ALERTA if d["label"] == "Zero" else COR_NEUTRO for d in ck]
fig2 = go.Figure(go.Bar(
    x=vals_kg, y=labels_kg, orientation="h", marker_color=cores_kg,
    text=[_brl(v) for v in vals_kg], textposition="auto",
    hovertemplate="<b>%{y}</b><br>%{text} por kg<extra></extra>",
))
fig2.update_layout(
    height=300, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
    xaxis=dict(title="custo de material por quilo (R$)"), yaxis=dict(title=""))
fig2.update_xaxes(fixedrange=True)
fig2.update_yaxes(fixedrange=True)
st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# QUADRO 3 — MATRIZ GIRO × TICKET
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Matriz: giro × ticket")
st.caption("Direita = vende muita unidade (giro). Topo = deixa mais por unidade "
           "(ticket). Tamanho da bolha = contribuição total.")

cores_cat = {"Cubos / pedaço": COR_CUBOS, "Tablete": COR_CONTRIB, "Pão de mel": COR_PM}

# Escala robusta no eixo Y: um produto de altíssima contribuição/unidade (ex.: um
# pote grande de baixo giro) estica a escala e espreme todo o resto lá embaixo.
# Limitamos o eixo ao percentil 90 (×1,25); os pontos acima ficam no TOPO da escala
# (com o valor real no toque) em vez de sumir ou achatar os demais.
mat_pts = [l for l in mapeados if l["qtd"] > 0]
cpu_ord = sorted(l["contrib"] / l["qtd"] for l in mat_pts)
cap = max(1.0, _percentil(cpu_ord, 90) * 1.25) if cpu_ord else 1.0
n_acima = sum(1 for v in cpu_ord if v > cap)

fig3 = go.Figure()
for cat, cor in cores_cat.items():
    pts = [l for l in mat_pts if _categoria(l["descricao"]) == cat]
    if not pts:
        continue
    fig3.add_trace(go.Scatter(
        x=[l["qtd"] for l in pts],
        y=[min(l["contrib"] / l["qtd"], cap) for l in pts],
        mode="markers", name=cat,
        marker=dict(size=[max(10, (l["contrib"] ** 0.5) / 9) for l in pts],
                    color=cor, opacity=0.65, line=dict(width=1, color=cor)),
        customdata=[[_nome_curto(l["descricao"]), l["contrib"], l["contrib"] / l["qtd"]]
                    for l in pts],
        hovertemplate=("<b>%{customdata[0]}</b><br>%{x:,.0f} un · "
                       "R$ %{customdata[2]:.2f}/un<br>contribui R$ %{customdata[1]:,.0f}"
                       "<extra></extra>"),
    ))
fig3.update_layout(
    height=380, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
    xaxis=dict(title="unidades vendidas no período", rangemode="tozero"),
    yaxis=dict(title="contribuição por unidade (R$)", range=[0, cap]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
fig3.update_xaxes(fixedrange=True)
fig3.update_yaxes(fixedrange=True)
st.plotly_chart(fig3, width="stretch", config={"displayModeBar": False, "responsive": True})
if n_acima:
    st.caption(f"{n_acima} produto(s) de contribuição/unidade muito alta estão no topo "
               f"da escala (acima de {_brl(cap)}/un) — passe o mouse para ver o valor real.")


# ════════════════════════════════════════════════════════════════════════════
# QUADRO 4 — PRODUÇÃO × VENDA
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Produção × venda, por sabor")
st.caption("A fábrica corta na proporção do que dá retorno? Cinza = esforço de "
           "produção (bandejas cortadas). Laranja = contribuição. Onde o laranja "
           "passa o cinza, o sabor **rende mais do que o esforço que recebe**.")

prod = res["producao"]
porsab = res["por_sabor"]
tot_band = sum(prod.values()) or 1
tot_contrib = sum(d["contrib"] for d in porsab.values()) or 1
sabores = [s for s in ORDEM_SABOR if (prod.get(s) or porsab.get(s))]
pct_prod = [round(prod.get(s, 0) / tot_band * 100, 1) for s in sabores]
pct_contrib = [round(porsab.get(s, {}).get("contrib", 0) / tot_contrib * 100, 1) for s in sabores]

fig4 = go.Figure()
fig4.add_trace(go.Bar(x=sabores, y=pct_prod, name="% da produção",
                      marker_color=COR_NEUTRO,
                      hovertemplate="<b>%{x}</b><br>produção: %{y:.1f}%<extra></extra>"))
fig4.add_trace(go.Bar(x=sabores, y=pct_contrib, name="% da contribuição",
                      marker_color=COR_CONTRIB,
                      hovertemplate="<b>%{x}</b><br>contribuição: %{y:.1f}%<extra></extra>"))
fig4.update_layout(
    barmode="group", height=340, margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="white", yaxis=dict(title="% do total", ticksuffix="%"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
fig4.update_xaxes(fixedrange=True)
fig4.update_yaxes(fixedrange=True)
st.plotly_chart(fig4, width="stretch", config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# HONESTIDADE + TABELA
# ════════════════════════════════════════════════════════════════════════════
st.divider()
nao_map = sorted([l for l in res["linhas"] if not l["mapeado"]],
                 key=lambda l: -l["receita"])[:6]
falta_txt = ", ".join(str(l["descricao"]).split(" - ")[-1][:24] for l in nao_map)
st.markdown(
    "<div class='card-info'>"
    f"<b>O que estes números cobrem:</b> {res['cobertura_pct']:.0f}% das vendas "
    "(cocada por peso + Pão de Mel + Bala). A contribuição é só de <b>material</b> — falta "
    "o custo de mão de obra/energia (em levantamento à parte). O custo por quilo "
    "usa o rendimento <b>confirmado pela fábrica</b>: 8 bandejas por tacho "
    "(Zero, 3 bandejas)."
    f"<br><b>Ainda sem custo</b> (a confirmar): {falta_txt}."
    "</div>", unsafe_allow_html=True)

with st.expander("Ver a tabela completa (produto a produto)"):
    df = pd.DataFrame([{
        "Produto": str(l["descricao"]).split(" - ")[-1],
        "Qtd": f"{int(round(float(l['qtd']))):,}".replace(",", "."),
        "Receita (R$)": _brl0(l["receita"]),
        "Custo material (R$)": _brl0(l["custo_mp"]),
        "Contribuição (R$)": _brl0(l["contrib"]),
        "Margem material": (f"{l['margem_pct']:.0f}%" if l["margem_pct"] is not None else "—"),
    } for l in sorted(mapeados, key=lambda x: -x["contrib"])])
    componentes.tabela(
        df, altura_max=460,
        cols_direita=["Qtd", "Receita (R$)", "Custo material (R$)",
                      "Contribuição (R$)", "Margem material"],
    )

st.caption(f"Calculado em {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
           f"período {periodo[0].strftime('%d/%m/%Y')}–{periodo[1].strftime('%d/%m/%Y')} · "
           f"{res['n_pedidos']:,} pedidos · cache de 30 min.".replace(",", "."))
