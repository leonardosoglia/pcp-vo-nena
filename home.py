"""
home.py — Página Início.

Saudação do dia + atalhos pras ações principais + status resumido.
Substitui a entrada direta no Lançamento.
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
aplicar_tema()


WEEKDAYS_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
               "Sexta-feira", "Sábado", "Domingo"]
MESES_PT = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


hoje = date.today()
saudacao_dia = WEEKDAYS_PT[hoje.weekday()]
data_fmt = f"{hoje.day} de {MESES_PT[hoje.month]} de {hoje.year}"


st.title("PCP Vó Nena")
st.caption(f"Hoje é {saudacao_dia}, {data_fmt}.")


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


col1, col2, col3 = st.columns(3)

with col1:
    if folha_hoje_existe:
        st.success(f"**Folha de hoje** ({hoje.strftime('%d/%m')}) já lançada.")
    else:
        if ultima_folha:
            st.warning(
                f"**Folha de hoje** ({hoje.strftime('%d/%m')}) ainda não foi lançada. "
                f"Última: {ultima_folha}."
            )
        else:
            st.info(f"Nenhuma folha lançada ainda no banco.")

with col2:
    st.metric("Folhas no histórico", len(datas_existentes))

with col3:
    st.metric("Última lançada", ultima_folha or "—")


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
        st.divider()
        st.subheader("Alertas de estoque")
        n_card, lista_card = st.columns([1, 3])
        with n_card:
            if negativos:
                st.metric(
                    "Estoque negativo",
                    len(negativos),
                    help="Consumido mais do que o cadastrado. Lançar entrada de compra ou ajuste.",
                )
            st.metric("Abaixo do mínimo", len(abaixo_min))
        with lista_card:
            piores = sorted(
                negativos + abaixo_min,
                key=lambda i: (i.get("estoque_atual") or 0) - (i.get("estoque_minimo") or 0),
            )[:8]
            linhas = []
            for i in piores:
                atual = i.get("estoque_atual") or 0
                minimo = i.get("estoque_minimo") or 0
                unid = i.get("unidade") or ""
                if atual < 0:
                    rotulo = f"**{i['nome']}** — estoque {atual:.2f} {unid} (NEGATIVO)"
                else:
                    rotulo = f"**{i['nome']}** — {atual:.2f} {unid} (mínimo {minimo:.2f})"
                linhas.append(f"- {rotulo}")
            st.markdown("\n".join(linhas))
            st.caption("Ver tudo em **Cadastros → Suprimentos**.")
    elif minimos_cadastrados == 0:
        # Ninguém tem mínimo configurado — aviso discreto pra ativar a feature
        st.info(
            "Dica: configure **estoque mínimo** em Cadastros → Suprimentos pra ativar "
            "alertas automáticos aqui na Home."
        )


# ════════════════════════════════════════════════════════════════════════════
# Atalhos principais
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("O que você quer fazer agora?")

cA, cB, cC = st.columns(3)

with cA:
    st.markdown(
        """
        ### Operação do dia

        - **Lançamento** — preencher a folha de produção de hoje
        - **Painel** — ver o que está acontecendo na fábrica
        - **Sugestão** — corte e produção de palha / cocada
        """
    )
with cB:
    st.markdown(
        """
        ### Planejamento

        - **Suprimentos** — insumos, receitas (BOM), necessidades
        - **Equipe** — funcionários, capacidades, presença
        - **Insights** — diagnóstico automático do dia
        """
    )
with cC:
    st.markdown(
        """
        ### Análise

        - **Curva ABC** — sabores que mais giram
        - **Anomalias ML** — dias atípicos detectados
        - **Média Móvel** — calibração de metas
        - **Assistente IA** — perguntar em PT-BR
        """
    )


# ════════════════════════════════════════════════════════════════════════════
# Rodapé com referência rápida
# ════════════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("Não sabe por onde começar?", expanded=False):
    st.markdown(
        """
        **De manhã (~10h)** — após contar o estoque:
        1. Vá em **Lançamento** e preencha a folha do dia.
        2. Em **Sugestão**, escolha entre Palha (semanal, na segunda) ou Cocada (diário).
        3. Discuta os números com a Produção/Corte e ajuste se precisar.

        **Durante o dia** — quando aparecer dúvida:
        - **Painel** mostra um resumo do que foi feito.
        - **Insights** dá diagnóstico automático (tachos parciais, sobrecarga de embalagem, etc).
        - **Assistente IA** responde em português a perguntas livres sobre o dia.

        **Toda semana** — manutenção do sistema:
        - Em **Suprimentos**, atualizar estoque de insumos críticos.
        - Em **Equipe**, marcar presenças do dia.
        - Em **Média Móvel**, ver se as metas base precisam ser recalibradas.
        """
    )
