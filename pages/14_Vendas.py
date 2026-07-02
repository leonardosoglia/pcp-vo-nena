# -*- coding: utf-8 -*-
"""
pages/14_Vendas.py — Vendas reais (Curva ABC de DEMANDA) a partir do SIGE.

Lê os pedidos FATURADOS do SIGE (read-only) e mostra para que mais SAI dinheiro:
receita e volume por produto, por canal (QUIOSQUE/REVENDA/PADRÃO) e por empresa,
+ Curva ABC por receita (ou volume).

DISTINÇÃO IMPORTANTE (e ótima pro TCC): esta é a Curva ABC de **demanda** — o que
mais VENDE/FATURA, dado real do SIGE. A página "Curva ABC" (pages/4) é a de
**produção** — o que a fábrica mais CORTA (bandejas, dado interno das folhas).
O descompasso entre as duas é o argumento do PCP puxado pela demanda: produzir
proporcional ao que o mercado puxa, não ao hábito de produção.

NÃO mostra lucro/contribuição por produto AINDA: o motor existe (lucro_produto.py),
mas hoje só cobre ~17% da receita — falta o custo dos formatos campeões (Cubos
160g, Bala) que depende das conversões da fábrica (quantas unidades saem por
tacho). Mostrar metade seria desonesto; entra quando a fábrica confirmar os
rendimentos. Aí vira a Curva ABC por LUCRO — o prato principal.

SOMENTE LEITURA: lê o SIGE (read-only). Nunca escreve nada.
Lógica de agregação em vendas_sige.py (puro, testado via CLI).

NOTA: precisa do token SIGE nos Secrets do ambiente (HF). Sem ele, a página
mostra um aviso amigável em vez de quebrar.

Capítulo TCC associado: "Curva ABC por receita vs por produção — alinhando o
plano de produção à demanda real (dados do ERP)."
Referência clássica: Pareto / Juran (1951).
"""
import os
import sys
from datetime import date, datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Bootstrap defensivo — propaga DATABASE_URL + credenciais SIGE de st.secrets
# pro ambiente (Streamlit Cloud); no HF Spaces já vêm como env var.
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
import vendas_sige as vsige

st.set_page_config(
    page_title="Vendas • Doces Vó Nena",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

import componentes
from ui_theme import aplicar_tema
aplicar_tema()

# Cores por classe ABC — fonte única do sistema (graficos.py)
from graficos import COR_CLASSE
# Quantos produtos mostrar no gráfico de Pareto (a cauda C fica só na tabela)
MAX_BARRAS_PARETO = 35


def _brl(v) -> str:
    """Formata número em reais no padrão BR (R$ 1.234,56)."""
    try:
        s = f"{float(v):,.2f}"
    except (TypeError, ValueError):
        return "R$ 0,00"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


# ════════════════════════════════════════════════════════════════════════════
# DADOS (read-only do SIGE, cacheado por período)
# ════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=1800, show_spinner="Lendo as vendas no SIGE...")
def carregar_vendas(d_ini: str, d_fim: str):
    """Lê todos os pedidos do período e agrega. Cacheado por (d_ini, d_fim),
    TTL 30 min. Retorna (agregado, n_pedidos, erro). Tudo read-only."""
    con = sige.testar_conexao()
    if not con["ok"]:
        return None, 0, con["mensagem"]
    try:
        pedidos = sige.listar_todos_pedidos(d_ini, d_fim)
    except Exception as e:
        return None, 0, str(e)
    ag = vsige.agregar_vendas(pedidos)
    return ag, len(pedidos), None


def _n_faturados(por_status: dict) -> int:
    """Conta os pedidos cujo status é 'Faturado' (os que entram na agregação)."""
    return sum(n for s, n in por_status.items() if "fatur" in str(s).lower())


# ── Rótulos de mês p/ o histórico ────────────────────────────────────────────
MESES_PT = ["", "jan", "fev", "mar", "abr", "mai", "jun",
            "jul", "ago", "set", "out", "nov", "dez"]


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ════════════════════════════════════════════════════════════════════════════
componentes.cabecalho(
    "Vendas & resultado", "Vendas", icone="shopping_cart",
    contexto="Vendas reais (pedidos faturados) lidas do SIGE — pra onde vai o "
             "dinheiro, por produto, canal e empresa. <b>Só leitura</b>, nada muda no SIGE.",
)

# ── Guarda de credenciais ────────────────────────────────────────────────────
if not sige.credenciais_configuradas():
    st.warning(
        "**Token do SIGE não configurado neste ambiente.** Para as vendas "
        "aparecerem em produção, defina `SIGE_AUTH_TOKEN`, `SIGE_USER` e "
        "`SIGE_APP` nos *Secrets* do Hugging Face. (Localmente, ficam no "
        "`.streamlit/secrets.toml`.)"
    )
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
# HISTÓRICO MENSAL (visão geral — vem do NOSSO banco, abre instantâneo)
# ════════════════════════════════════════════════════════════════════════════
import database as db

st.divider()
st.header("Histórico mensal de vendas")
st.caption("Receita faturada mês a mês — a **tendência**. Vem do nosso banco (abre na "
           "hora); o SIGE só é lido quando você clica em **Atualizar do SIGE**. O mês "
           "atual é parcial (só até hoje).")

colh1, colh2 = st.columns([3, 1])
with colh1:
    n_meses = st.select_slider("Meses a mostrar", options=[3, 6, 12], value=6)
with colh2:
    st.write("")
    _atualizar_hist = st.button(
        "🔄 Atualizar do SIGE", use_container_width=True,
        help="Recalcula o mês atual e os meses que ainda faltam (lê o SIGE; "
             "cada mês leva alguns segundos).")

_hj = date.today()
_meses = vsige.ultimos_meses(n_meses)

if _atualizar_hist:
    _regs_atuais = db.get_vendas_mensais()
    _ja = {(r["ano"], r["mes"]) for r in _regs_atuais}
    # Meses cuja foto ficou incompleta (parcial=1): precisam ser refeitos até fechar.
    # Sem isto, um mês fotografado antes do fim (ex.: junho tirado em 24/06) congela
    # num valor parcial pra sempre, porque deixa de ser o mês corrente.
    _parciais = {(r["ano"], r["mes"]) for r in _regs_atuais if r.get("parcial")}
    _alvo = [(y, m) for (y, m) in _meses
             if (y, m) not in _ja
             or (y == _hj.year and m == _hj.month)
             or (y, m) in _parciais]
    _erros = 0
    with st.spinner(f"Lendo {len(_alvo)} mês(es) no SIGE…"):
        for (_y, _m) in _alvo:
            try:
                vsige.atualizar_vendas_mes(db, sige, _y, _m)
            except Exception:
                _erros += 1
    if _erros:
        st.warning(f"{_erros} mês(es) não puderam ser atualizados agora — tente de novo.")

_reg = {(r["ano"], r["mes"]): r for r in db.get_vendas_mensais()}
_hist = []
_faltam = 0
for (_y, _m) in _meses:
    _r = _reg.get((_y, _m))
    _corr = (_y == _hj.year and _m == _hj.month)
    if _r is None:
        _faltam += 1
        _hist.append({"rotulo": f"{MESES_PT[_m]}/{str(_y)[2:]}", "receita": 0.0,
                      "corrente": _corr, "vazio": True})
    else:
        _hist.append({"rotulo": f"{MESES_PT[_m]}/{str(_y)[2:]}",
                      "receita": _r["receita"] or 0.0, "corrente": _corr, "vazio": False})

if all(h["vazio"] for h in _hist):
    st.info("O histórico ainda não foi calculado. Clique em **Atualizar do SIGE** "
            "para montar a primeira vez (leva ~1 min; depois abre instantâneo).")
else:
    _rotulos = [h["rotulo"] for h in _hist]
    _valores = [h["receita"] for h in _hist]
    _cores = ["#E8A87C" if h["corrente"] else "#C05621" for h in _hist]
    fig_h = go.Figure(go.Bar(
        x=_rotulos, y=_valores, marker_color=_cores,
        text=[(_brl(v) if v else "—") for v in _valores], textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
    ))
    _fechados = [h["receita"] for h in _hist
                 if not h["corrente"] and not h["vazio"] and h["receita"]]
    if len(_fechados) >= 2:
        _media = sum(_fechados) / len(_fechados)
        fig_h.add_hline(y=_media, line_dash="dash", line_color="#6B7280", line_width=1.5,
                        annotation_text=f"média dos meses fechados: {_brl(_media)}",
                        annotation_position="top left")
    fig_h.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10),
                        plot_bgcolor="white", xaxis=dict(title=""),
                        yaxis=dict(title="receita faturada (R$)"))
    fig_h.update_xaxes(fixedrange=True)
    fig_h.update_yaxes(fixedrange=True)
    st.plotly_chart(fig_h, width="stretch",
                    config={"displayModeBar": False, "responsive": True})

    _legs = ["Barra mais clara = mês atual (parcial)."]
    _cur = _reg.get((_hj.year, _hj.month))
    if _cur and _cur.get("atualizado_em"):
        _legs.append(f"Mês atual atualizado em {str(_cur['atualizado_em'])[:16]}.")
    if _faltam:
        _legs.append(f"{_faltam} mês(es) ainda sem dados — use Atualizar do SIGE.")
    st.caption(" ".join(_legs))


# ════════════════════════════════════════════════════════════════════════════
# DETALHE POR PERÍODO (escolha um intervalo p/ ver canais, empresas e Curva ABC)
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Detalhe por período")

# ── Filtro de período + atualizar ────────────────────────────────────────────
hoje = date.today()
c_data, c_btn = st.columns([3, 1])
with c_data:
    periodo = st.date_input(
        "Período das vendas",
        value=(hoje - timedelta(days=30), hoje),
        max_value=hoje,
        format="DD/MM/YYYY",
    )
with c_btn:
    st.write("")  # alinha o botão com o input
    if st.button("🔄 Carregar / atualizar do SIGE", use_container_width=True):
        st.session_state["vdet_go"] = True

# st.date_input devolve 1 data enquanto o usuário escolhe a 2ª — espera as duas.
if not isinstance(periodo, (tuple, list)) or len(periodo) != 2:
    st.info("Escolha a data **final** do período para carregar as vendas.")
    st.stop()

d_ini, d_fim = periodo[0].strftime("%Y-%m-%d"), periodo[1].strftime("%Y-%m-%d")
n_dias = (periodo[1] - periodo[0]).days + 1

# Carregamento preguiçoso: o detalhe abre na hora; só lê o SIGE quando você clica.
_chave_det = f"{d_ini}_{d_fim}"
if st.session_state.pop("vdet_go", False):
    st.session_state["vdet_loaded"] = _chave_det
    carregar_vendas.clear()
if st.session_state.get("vdet_loaded") != _chave_det:
    st.info("Escolha o período e clique em **Carregar / atualizar do SIGE** para ver o "
            "detalhe por canal, empresa e a Curva ABC (leva ~1 min na 1ª vez; depois "
            "fica em cache). O histórico mensal acima já está pronto.")
    st.stop()

if n_dias > 31:
    st.caption(f"Período longo ({n_dias} dias) — a 1ª leitura pode levar até "
               "~1 min (paginação do SIGE). Depois fica em cache por 30 min.")

ag, n_pedidos, erro = carregar_vendas(d_ini, d_fim)

if erro:
    st.error(f"Não consegui ler as vendas no SIGE agora: {erro}")
    st.stop()

if not ag or not ag["por_produto"]:
    st.info(f"Nenhuma venda faturada encontrada entre {periodo[0].strftime('%d/%m/%Y')} "
            f"e {periodo[1].strftime('%d/%m/%Y')}.")
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
# KPIs
# ════════════════════════════════════════════════════════════════════════════
n_fat = _n_faturados(ag["por_status"])
receita = ag["total_receita"]
n_produtos = len([c for c in ag["por_produto"]
                  if str(c).strip() not in vsige.CODIGOS_NAO_PRODUTO])
ticket = (receita / n_fat) if n_fat else 0.0

st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Receita faturada", _brl(receita))
k2.metric("Pedidos faturados", f"{n_fat:,}".replace(",", "."))
k3.metric("Produtos vendidos", f"{n_produtos}")
k4.metric("Ticket médio", _brl(ticket))
st.caption(f"Período {periodo[0].strftime('%d/%m/%Y')} – {periodo[1].strftime('%d/%m/%Y')} "
           f"· {n_dias} dias · {n_pedidos:,} pedidos lidos (todos os status), "
           f"{n_fat} faturados.".replace(",", "."))


# ════════════════════════════════════════════════════════════════════════════
# RECEITA POR CANAL e POR EMPRESA
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("De onde vem a receita")

col_canal, col_emp = st.columns(2)

with col_canal:
    st.markdown("##### Por canal de venda")
    canais = sorted(ag["por_canal"].items(), key=lambda x: -x[1])
    if canais:
        nomes = [c[0] for c in canais]
        vals = [c[1] for c in canais]
        fig_c = go.Figure(go.Bar(
            x=vals, y=nomes, orientation="h",
            marker_color="#C05621",
            text=[_brl(v) for v in vals], textposition="auto",
            hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        ))
        fig_c.update_layout(
            height=max(180, 38 * len(nomes)),
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white",
            xaxis=dict(title="", showticklabels=False),
            yaxis=dict(autorange="reversed"),
        )
        fig_c.update_xaxes(fixedrange=True)
        fig_c.update_yaxes(fixedrange=True)
        st.plotly_chart(fig_c, width="stretch",
                        config={"displayModeBar": False, "responsive": True})
    st.caption("**(sem canal)** = venda direta / sem tabela de preço associada — "
               "costuma ser a maior fatia; vale entender com a Gestão.")

with col_emp:
    st.markdown("##### Por empresa (CNPJ)")
    emps = sorted(ag["por_empresa"].items(), key=lambda x: -x[1])
    if emps:
        nomes = [e[0] for e in emps]
        vals = [e[1] for e in emps]
        fig_e = go.Figure(go.Bar(
            x=vals, y=nomes, orientation="h",
            marker_color="#0E7490",
            text=[_brl(v) for v in vals], textposition="auto",
            hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        ))
        fig_e.update_layout(
            height=max(180, 38 * len(nomes)),
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white",
            xaxis=dict(title="", showticklabels=False),
            yaxis=dict(autorange="reversed"),
        )
        fig_e.update_xaxes(fixedrange=True)
        fig_e.update_yaxes(fixedrange=True)
        st.plotly_chart(fig_e, width="stretch",
                        config={"displayModeBar": False, "responsive": True})


# ════════════════════════════════════════════════════════════════════════════
# CURVA ABC (por receita ou volume)
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.header("Curva ABC de demanda")
st.caption("Itens que **não são produto da fábrica** ficam **fora** desta análise — "
           "ex.: \"Diversos e Embalagens\", um registro de caixa de R$ 0,01 que inflava "
           "o volume. Revenda real (produtos comprados para revender) ainda aparece.")

metrica = st.radio(
    "Classificar por:",
    options=["Receita (R$)", "Volume (unidades)"],
    horizontal=True,
)
chave = "receita" if metrica.startswith("Receita") else "qtd"
abc = vsige.curva_abc(ag["por_produto"], chave=chave)

# ── Cartões de resumo por classe ─────────────────────────────────────────────
def _resumo_classe(classe: str):
    itens = [x for x in abc if x["classe"] == classe]
    qt = len(itens)
    val_rec = sum(x["receita"] for x in itens)
    val_qtd = sum(x["qtd"] for x in itens)
    return qt, val_rec, val_qtd

col_a, col_b, col_c = st.columns(3)
for col, classe, desc in [
    (col_a, "A", "Carros-chefe (até 80%)"),
    (col_b, "B", "Intermediários (80–95%)"),
    (col_c, "C", "Cauda longa (últimos 5%)"),
]:
    qt, val_rec, val_qtd = _resumo_classe(classe)
    destaque = _brl(val_rec) if chave == "receita" else f"{val_qtd:,.0f} un".replace(",", ".")
    with col:
        st.markdown(
            f"<div class='card-{classe.lower()}'>"
            f"<b style='font-size:22px;'>Classe {classe}</b><br>"
            f"<span style='font-size:13px;opacity:0.9;'>{desc}</span>"
            f"<hr style='border-color:rgba(0,0,0,0.15);margin:8px 0;'>"
            f"<b>{qt}</b> produtos · <b>{destaque}</b>"
            f"</div>",
            unsafe_allow_html=True,
        )

# ── Diagrama de Pareto (top N) ───────────────────────────────────────────────
st.markdown("##### Diagrama de Pareto")
chart = [x for x in abc if x["classe"] in ("A", "B")][:MAX_BARRAS_PARETO]
if chart:
    xs = list(range(len(chart)))
    labels = [str(x["descricao"] or x["codigo"])[:30] for x in chart]
    ys_val = [x[chave] for x in chart]
    ys_cum = [x["pct_acum"] for x in chart]
    cores = [COR_CLASSE[x["classe"]] for x in chart]
    eixo_titulo = "Receita (R$)" if chave == "receita" else "Volume (un)"

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=xs, y=ys_val, marker_color=cores, name=eixo_titulo,
        customdata=[[lab] for lab in labels],
        hovertemplate="<b>%{customdata[0]}</b><br>" +
                      ("%{y:,.2f}" if chave == "receita" else "%{y:,.0f} un") +
                      "<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=xs, y=ys_cum, name="% acumulado", yaxis="y2",
        mode="lines+markers", line=dict(color="#1F2937", width=3),
        marker=dict(size=6, color="#1F2937"),
        hovertemplate="Acumulado: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=80, yref="y2", line_dash="dash", line_color="#059669",
                  line_width=1.5, annotation_text="80% (fim da Classe A)",
                  annotation_position="top left")
    fig.update_layout(
        xaxis=dict(title="Produto", tickmode="array", tickvals=xs,
                   ticktext=labels, tickangle=-45),
        yaxis=dict(title=eixo_titulo, side="left"),
        yaxis2=dict(title="% acumulado", side="right", overlaying="y",
                    range=[0, 105], ticksuffix="%"),
        height=560,
        margin=dict(l=20, r=20, t=20, b=200),
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        bargap=0.25,
    )
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    st.plotly_chart(fig, width="stretch",
                    config={"displayModeBar": False, "responsive": True})
    st.caption(f"Mostrando {len(chart)} produtos (Classes A e B) de {len(abc)} no "
               "total. A cauda (Classe C) está na tabela abaixo.")


# ── Tabela detalhada ─────────────────────────────────────────────────────────
st.markdown("##### Detalhamento por produto")
df = pd.DataFrame(abc)
df = df[["classe", "codigo", "descricao", "qtd", "receita", "pct_acum"]]
df.columns = ["Classe", "Código", "Produto", "Volume (un)", "Receita (R$)", "% acum."]
# Pré-formata os números em texto (R$ e % no padrão BR) pro quadro padrão.
df["Volume (un)"] = df["Volume (un)"].map(lambda v: f"{int(round(float(v))):,}".replace(",", "."))
df["Receita (R$)"] = df["Receita (R$)"].map(_brl)
df["% acum."] = df["% acum."].map(lambda v: f"{float(v):.1f}%".replace(".", ","))
componentes.tabela(
    df, altura_max=460,
    cols_direita=["Volume (un)", "Receita (R$)", "% acum."],
)


# ════════════════════════════════════════════════════════════════════════════
# PRÓXIMO PASSO (honesto): Curva ABC por LUCRO
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown(
    "<div class='card-info'>"
    "<b>Quer ver o que cada produto LUCRA?</b> Esta tela mostra receita e volume "
    "(o que mais <b>vende</b>). O que cada produto <b>deixa depois do custo do "
    "material</b> — a contribuição por produto — está na tela <b>Lucratividade</b> "
    "(menu Análises), já cobrindo a maior parte das vendas. Lembrete: vender muito "
    "≠ lucrar muito."
    "</div>",
    unsafe_allow_html=True,
)

with st.expander("Como ler esta tela"):
    st.markdown(
        "- **Receita faturada:** soma dos pedidos com status *Faturado* (vendas "
        "confirmadas) no período. Pedidos não faturados (orçamento, cancelado) "
        "não entram.\n"
        "- **Canal:** a *tabela de preço* do pedido (QUIOSQUE, REVENDA/atacado, "
        "PADRÃO/varejo). **(sem canal)** = venda direta sem tabela associada.\n"
        "- **Curva ABC (Pareto):** ordena os produtos do que mais gera (receita "
        "ou volume) para o que menos gera. **Classe A** = poucos produtos que "
        "somam até 80% — os carros-chefe; **B** = 80–95%; **C** = a cauda longa.\n"
        "- **Diferença para a página *Curva ABC*:** lá a classificação é por "
        "**bandejas cortadas** (o que a fábrica mais produz). Aqui é por **venda "
        "real**. Comparar as duas mostra se a produção está alinhada à demanda.\n"
        "- **Somente leitura:** nada é alterado no SIGE. Cache de 30 min; use "
        "*Atualizar do SIGE* para forçar a releitura."
    )

componentes.rodape("fonte: SIGE · somente leitura · renova a cada 30 min")
