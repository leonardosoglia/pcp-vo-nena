"""
home.py — Página Início (redesenho visual 25/06/2026).

Cabeçalho com a ação principal · status do dia em cartões · alertas de estoque
numa caixa de aviso padronizada · atalhos em cartões com ícone.
Usa as peças reutilizáveis de `componentes.py` (kit da reforma visual).
"""
import os
import sys
from datetime import date
import streamlit as st

# Bootstrap defensivo
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

_RAIZ = os.path.dirname(os.path.abspath(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

import cached_db
from ui_theme import aplicar_tema
from componentes import cartao_atalho, status_badge

aplicar_tema()


WEEKDAYS_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
               "Sexta-feira", "Sábado", "Domingo"]
MESES_PT = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

hoje = date.today()
saudacao_dia = WEEKDAYS_PT[hoje.weekday()]
data_fmt = f"{hoje.day} de {MESES_PT[hoje.month]} de {hoje.year}"


# ════════════════════════════════════════════════════════════════════════════
# Cabeçalho com a ação principal do dia
# ════════════════════════════════════════════════════════════════════════════
cab_esq, cab_dir = st.columns([3, 1.3], vertical_alignment="center")
with cab_esq:
    st.title("PCP Vó Nena")
    st.caption(f"Hoje é {saudacao_dia}, {data_fmt}.")
with cab_dir:
    if st.button("Lançar folha de hoje", type="primary",
                 icon=":material/note_add:", use_container_width=True):
        st.switch_page("lancamento.py")


# ════════════════════════════════════════════════════════════════════════════
# Status do dia
# ════════════════════════════════════════════════════════════════════════════
try:
    datas_existentes = cached_db.list_datas_folha()
    folha_hoje_existe = hoje.isoformat() in datas_existentes
    ultima_folha = max(datas_existentes) if datas_existentes else None
except Exception:
    folha_hoje_existe = False
    ultima_folha = None
    datas_existentes = []

ultima_fmt = "—"
if ultima_folha:
    try:
        ultima_fmt = date.fromisoformat(ultima_folha).strftime("%d/%m")
    except Exception:
        ultima_fmt = str(ultima_folha)

s1, s2, s3 = st.columns(3)
with s1:
    if folha_hoje_existe:
        status_badge("Folha de hoje", "Já lançada", "success")
    elif ultima_folha:
        status_badge("Folha de hoje", "Ainda não lançada", "warning")
    else:
        status_badge("Folha de hoje", "Nenhuma no banco", "info")
with s2:
    st.metric("Folhas no histórico", len(datas_existentes))
with s3:
    st.metric("Última lançada", ultima_fmt)


# ════════════════════════════════════════════════════════════════════════════
# Alertas de estoque (Etapa E)
# ════════════════════════════════════════════════════════════════════════════
try:
    insumos_todos = cached_db.get_insumos(somente_ativos=True)
except Exception:
    insumos_todos = []

if insumos_todos:
    negativos = [i for i in insumos_todos if (i.get("estoque_atual") or 0) < 0]
    abaixo_min = [
        i for i in insumos_todos
        if (i.get("estoque_minimo") or 0) > 0
        and (i.get("estoque_atual") or 0) >= 0
        and (i.get("estoque_atual") or 0) < (i.get("estoque_minimo") or 0)
    ]
    minimos_cadastrados = sum(1 for i in insumos_todos if (i.get("estoque_minimo") or 0) > 0)

    if negativos or abaixo_min:
        piores = sorted(
            negativos + abaixo_min,
            key=lambda i: (i.get("estoque_atual") or 0) - (i.get("estoque_minimo") or 0),
        )[:6]
        partes = []
        for i in piores:
            atual = i.get("estoque_atual") or 0
            minimo = i.get("estoque_minimo") or 0
            unid = i.get("unidade") or ""
            if atual < 0:
                partes.append(f"<strong>{i['nome']}</strong> — {atual:.2f} {unid} (negativo)")
            else:
                partes.append(f"<strong>{i['nome']}</strong> — {atual:.2f} {unid} (mínimo {minimo:.2f})")
        n = len(negativos) + len(abaixo_min)
        st.markdown(
            f"""<div class="card-warning">
<strong>Alertas de estoque — {n} insumo(s) precisam de atenção</strong><br>
<span style="font-size:13px">{' · '.join(partes)}</span>
</div>""",
            unsafe_allow_html=True,
        )
        st.page_link("pages/3_Suprimentos.py", label="Ver tudo em Suprimentos",
                     icon=":material/arrow_forward:")
    elif minimos_cadastrados == 0:
        st.info(
            "Dica: configure **estoque mínimo** em Suprimentos pra ativar "
            "alertas automáticos aqui na Início."
        )


# ════════════════════════════════════════════════════════════════════════════
# Atalhos principais — em cartões com ícone
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("O que você quer fazer?")

GRUPOS_ATALHOS = [
    ("Operação do dia", [
        ("lancamento.py", "Lançamento", "preencher a folha de hoje", ":material/edit_document:"),
        ("pages/1_Painel.py", "Painel", "o que está acontecendo na fábrica", ":material/dashboard:"),
        ("pages/11_Sugestao_Cocada.py", "Sugestão", "corte e produção do dia", ":material/lightbulb:"),
    ]),
    ("Vendas & análise", [
        ("pages/14_Vendas.py", "Vendas", "faturamento por mês e canal", ":material/shopping_cart:"),
        ("pages/15_Lucratividade.py", "Lucratividade", "quem dá mais retorno", ":material/trending_up:"),
        ("pages/7_Assistente_IA.py", "Assistente", "perguntar em português", ":material/smart_toy:"),
    ]),
    ("Planejamento & cadastros", [
        ("pages/3_Suprimentos.py", "Suprimentos", "insumos, receitas, necessidades", ":material/inventory_2:"),
        ("pages/8_Equipe.py", "Equipe", "presença e capacidades", ":material/group:"),
        ("pages/2_Insights.py", "Insights", "diagnóstico automático do dia", ":material/auto_awesome:"),
    ]),
]

for titulo_grupo, atalhos in GRUPOS_ATALHOS:
    st.markdown(f"<div class='grupo-atalho'>{titulo_grupo}</div>", unsafe_allow_html=True)
    colunas = st.columns(3)
    for coluna, (page, titulo, descricao, icone) in zip(colunas, atalhos):
        with coluna:
            cartao_atalho(page, titulo, descricao, icone)


# ════════════════════════════════════════════════════════════════════════════
# Ajuda rápida
# ════════════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("Não sabe por onde começar?", expanded=False):
    st.markdown(
        """
        **De manhã** — após contar o estoque:
        1. Vá em **Lançamento** e preencha a folha do dia.
        2. Em **Sugestão**, veja o corte e a produção do dia.
        3. Discuta os números com a Produção/Corte e ajuste se precisar.

        **Durante o dia** — quando aparecer dúvida:
        - **Painel** mostra um resumo do que foi feito.
        - **Insights** dá diagnóstico automático (tachos parciais, sobrecarga de embalagem, etc).
        - **Assistente IA** responde em português a perguntas livres sobre o dia.

        **Toda semana** — manutenção:
        - Em **Suprimentos**, atualizar o estoque de insumos críticos.
        - Em **Equipe**, marcar presenças.
        - Em **Média Móvel**, ver se as metas base precisam de recalibração.
        """
    )
