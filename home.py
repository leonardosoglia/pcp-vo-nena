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
st.markdown(
    f"<div style='font-size: 1.1em; color: #555; margin-bottom: 1.5rem;'>"
    f"Hoje é <strong>{saudacao_dia}</strong>, {data_fmt}."
    "</div>",
    unsafe_allow_html=True,
)


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
