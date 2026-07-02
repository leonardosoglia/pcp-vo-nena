# -*- coding: utf-8 -*-
"""
pages/16_Producao_x_Demanda.py — O CORAÇÃO do PCP puxado pela demanda.

Cruza o que a fábrica PRODUZ (bandejas cortadas, das folhas) com o que o mercado
COMPRA (vendas reais do SIGE), por SABOR de cocada. Mostra onde a produção está
desalinhada da demanda — produzindo demais (encalhe) ou de menos (oportunidade) —
para a Gestão reequilibrar o corte.

Compara o MIX (%) de cada lado: corte é em bandejas, venda é em unidades/reais —
então o que se compara é a PROPORÇÃO de cada sabor, não o número absoluto.

SOMENTE LEITURA: lê o SIGE (vendas) e o nosso banco (folhas) — nada é escrito.
Motor: contribuicao_produto.producao_x_demanda. Capítulo central do TCC
("produção puxada pela demanda"). Referência: Pareto/Juran + estoque×fluxo.
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
import contribuicao_produto as cpr
import componentes

st.set_page_config(
    page_title="Produção × Demanda • Doces Vó Nena",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui_theme import aplicar_tema
aplicar_tema()

COR_PROD = "#A8A29E"      # cinza — produção (esforço da fábrica)
COR_DEM = "#C05621"       # laranja Vó Nena — demanda (mercado)
COR_EXCESSO = "#B45309"   # âmbar — produz mais do que vende
COR_FALTA = "#0E7490"     # azul-petróleo — vende mais do que produz (oportunidade)
ORDEM = ["Tradicional", "Leite Condensado", "Zero", "Café", "Brigadeiro", "Pé de Moça"]
LIMIAR = 1.5  # p.p. — abaixo disso consideramos "alinhado"

_CFG = {"displayModeBar": False, "responsive": True}


def _pct(v) -> str:
    return f"{float(v):.1f}%"


@st.cache_data(ttl=1800, show_spinner="Lendo as vendas do período no SIGE (pode levar ~1 min na 1ª vez)...")
def carregar(d_ini: str, d_fim: str):
    """Cruza produção (folhas) × demanda (SIGE) no período. Read-only."""
    con = sige.testar_conexao()
    if not con["ok"]:
        return None, con["mensagem"]
    try:
        import database as db
        pedidos = sige.listar_todos_pedidos(d_ini, d_fim)
        linhas = cpr.producao_x_demanda(db, pedidos)
    except Exception as e:
        return None, str(e)
    return linhas, None


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ════════════════════════════════════════════════════════════════════════════
componentes.cabecalho(
    "Vendas & resultado", "Produção × Demanda", icone="compare_arrows",
    contexto="O esforço da fábrica lado a lado com o que o mercado comprou — os gaps por sabor.",
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
    periodo = st.date_input("Período da demanda (vendas)",
                            value=(hoje - timedelta(days=30), hoje),
                            max_value=hoje, format="DD/MM/YYYY")
with c_btn:
    st.write("")
    if st.button("Atualizar do SIGE", use_container_width=True):
        st.session_state["pxd_go"] = True

if not isinstance(periodo, (tuple, list)) or len(periodo) != 2:
    st.info("Escolha a data **final** do período para calcular.")
    st.stop()

d_ini, d_fim = periodo[0].strftime("%Y-%m-%d"), periodo[1].strftime("%Y-%m-%d")

# Carregamento preguiçoso: a tela abre na hora; só lê o SIGE quando você clica.
_chave = f"{d_ini}_{d_fim}"
if st.session_state.pop("pxd_go", False):
    st.session_state["pxd_loaded"] = _chave
    carregar.clear()
if st.session_state.get("pxd_loaded") != _chave:
    st.info("A tela abre na hora. Escolha o período e clique em **Atualizar do SIGE** "
            "para puxar os dados (leva ~1 min na 1ª vez; depois fica em cache).")
    st.stop()

linhas, erro = carregar(d_ini, d_fim)
if erro:
    st.error(f"Não consegui calcular agora: {erro}")
    st.stop()
if not linhas or all((l["volume"] or 0) == 0 for l in linhas):
    st.info("Sem vendas de cocada no período (ou sem folhas com ordens de corte registradas).")
    st.stop()

# Métrica da demanda (volume ou receita) — Leonardo quis os dois disponíveis
metrica = st.radio("Medir a demanda por:", ["Volume (unidades)", "Receita (R$)"],
                   horizontal=True)
usa_vol = metrica.startswith("Volume")
pct_dem = "pct_vol" if usa_vol else "pct_rec"
gap = "gap_vol" if usa_vol else "gap_rec"
rotulo_dem = "volume vendido" if usa_vol else "receita"

linhas_ord = sorted(linhas, key=lambda l: ORDEM.index(l["sabor"]) if l["sabor"] in ORDEM else 99)


# ════════════════════════════════════════════════════════════════════════════
# CARTÕES DE RESUMO
# ════════════════════════════════════════════════════════════════════════════
maior_falta = min(linhas, key=lambda l: l[gap])      # gap mais negativo = vende > produz
maior_excesso = max(linhas, key=lambda l: l[gap])    # gap mais positivo = produz > vende

st.divider()
k1, k2, k3 = st.columns(3)
k1.metric("Sabores de cocada", f"{len(linhas)}")
k2.metric("Maior oportunidade (produzir +)", maior_falta["sabor"],
          f"{maior_falta[gap]:+.1f} p.p.")
k3.metric("Maior excesso (produzir −)", maior_excesso["sabor"],
          f"{maior_excesso[gap]:+.1f} p.p.")


# ════════════════════════════════════════════════════════════════════════════
# QUADRO 1 — corte × compra (mix lado a lado)
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Quanto a fábrica corta × quanto o mercado compra")
st.caption("Participação de cada sabor (o **mix**), em %. Cinza = produção (bandejas "
           f"cortadas). Laranja = demanda ({rotulo_dem}).")

sabores = [l["sabor"] for l in linhas_ord]
fig1 = go.Figure()
fig1.add_trace(go.Bar(x=sabores, y=[l["pct_prod"] for l in linhas_ord],
                      name="% da produção", marker_color=COR_PROD,
                      hovertemplate="<b>%{x}</b><br>produção: %{y:.1f}%<extra></extra>"))
fig1.add_trace(go.Bar(x=sabores, y=[l[pct_dem] for l in linhas_ord],
                      name="% da demanda", marker_color=COR_DEM,
                      hovertemplate="<b>%{x}</b><br>demanda: %{y:.1f}%<extra></extra>"))
fig1.update_layout(barmode="group", height=360, margin=dict(l=10, r=10, t=10, b=10),
                   plot_bgcolor="white", yaxis=dict(title="% do total", ticksuffix="%"),
                   legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
fig1.update_xaxes(fixedrange=True)
fig1.update_yaxes(fixedrange=True)
st.plotly_chart(fig1, width="stretch", config=_CFG)


# ════════════════════════════════════════════════════════════════════════════
# QUADRO 2 — DESALINHAMENTO (o destaque)
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Desalinhamento — onde reequilibrar")
st.caption("Diferença **produção − demanda**, em pontos percentuais. À **direita** = "
           "corta MAIS do que vende (excesso → avaliar reduzir). À **esquerda** = vende "
           "MAIS do que corta (oportunidade → avaliar produzir mais).")

linhas_gap = sorted(linhas, key=lambda l: l[gap])
gaps = [l[gap] for l in linhas_gap]
sab_gap = [l["sabor"] for l in linhas_gap]
cores = [COR_EXCESSO if g > 0 else COR_FALTA for g in gaps]
fig2 = go.Figure(go.Bar(
    x=gaps, y=sab_gap, orientation="h", marker_color=cores,
    text=[f"{g:+.1f} p.p." for g in gaps], textposition="auto",
    hovertemplate="<b>%{y}</b><br>produção − demanda: %{text}<extra></extra>",
))
fig2.add_vline(x=0, line_color="#1F2937", line_width=1)
fig2.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
                   xaxis=dict(title="produção − demanda (pontos percentuais)"),
                   yaxis=dict(title=""))
fig2.update_xaxes(fixedrange=True)
fig2.update_yaxes(fixedrange=True)
st.plotly_chart(fig2, width="stretch", config=_CFG)


# ════════════════════════════════════════════════════════════════════════════
# LEITURA POR SABOR (recomendação automática)
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Leitura por sabor")
st.caption("Sugestão automática — a Gestão decide; o sistema só aponta.")

for l in sorted(linhas, key=lambda x: -abs(x[gap])):
    g = l[gap]
    if g > LIMIAR:
        st.markdown(
            f"- **{l['sabor']}** — corta {_pct(l['pct_prod'])} do total e vende "
            f"{_pct(l[pct_dem])} → produz **~{abs(g):.0f} p.p. a mais** do que a "
            f"demanda (avaliar **reduzir** o corte).")
    elif g < -LIMIAR:
        st.markdown(
            f"- **{l['sabor']}** — vende {_pct(l[pct_dem])} mas corta só "
            f"{_pct(l['pct_prod'])} → o mercado puxa **~{abs(g):.0f} p.p. a mais** "
            f"(oportunidade de **produzir mais**).")
    else:
        st.markdown(
            f"- **{l['sabor']}** — produção e demanda **alinhadas** "
            f"(~{_pct(l['pct_prod'])}).")


# ════════════════════════════════════════════════════════════════════════════
# TABELA + HONESTIDADE
# ════════════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("Ver a tabela completa"):
    df = pd.DataFrame([{
        "Sabor": l["sabor"],
        "Bandejas cortadas": f"{int(l['bandejas']):,}".replace(",", "."),
        "Unidades vendidas": f"{int(round(l['volume'])):,}".replace(",", "."),
        "Receita (R$)": "R$ " + f"{float(l['receita']):,.0f}".replace(",", "."),
        "% produção": f"{float(l['pct_prod']):.1f}%".replace(".", ","),
        "% demanda": f"{float(l[pct_dem]):.1f}%".replace(".", ","),
        "Gap (p.p.)": f"{float(l[gap]):.1f}".replace(".", ","),
    } for l in linhas_ord])
    componentes.tabela(
        df,
        cols_direita=["Bandejas cortadas", "Unidades vendidas", "Receita (R$)",
                      "% produção", "% demanda", "Gap (p.p.)"],
    )

st.markdown(
    "<div class='card-info'>"
    "<b>Como ler com honestidade:</b> comparamos o <b>mix</b> (a proporção de cada "
    "sabor), não o número absoluto — porque o corte é medido em <b>bandejas</b> e a "
    "venda em <b>unidades/reais</b>. A <b>produção</b> vem do histórico de folhas; a "
    "<b>demanda</b>, do período de vendas escolhido — os períodos podem não ser os "
    "mesmos, então o que vale é a <b>forma</b> (quais sabores estão sobre/sub-"
    "representados). Cobre as <b>6 cocadas de tacho</b> (a assada, o pão de mel, a "
    "bala e a palha não entram aqui)."
    "</div>", unsafe_allow_html=True)

componentes.rodape("fonte: folhas de produção × SIGE · renova a cada 30 min")
