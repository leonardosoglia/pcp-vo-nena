"""
app.py — Entry point novo com navegação organizada (st.navigation).

Substitui o `lancamento.py` como entry. Define a sidebar custom em grupos
lógicos. Ordem dos grupos reflete o fluxo diário da Gestão: o que ela faz
de manhã (lançar, ver painel, ver sugestões) vem primeiro; cadastros e
análises ficam depois; ajuda/admin no final.

A estrutura `st.navigation` ignora a pasta `pages/` — apenas as páginas
listadas aqui aparecem no sidebar. Os arquivos em `pages/` continuam
sendo o "código" de cada tela, mas o nome exibido vem do parâmetro
`title=` aqui (assim podemos usar "Lançamento" mesmo com arquivo
`lancamento.py` sem cedilha).

Princípio: a Gestão decide olhando uma sidebar limpa, sem ruído de
páginas técnicas (Admin Seed fica num grupo separado e discreto).
"""
import os
import streamlit as st

# Bootstrap defensivo — Streamlit Cloud expõe via st.secrets; HF Spaces
# injeta DATABASE_URL diretamente como env var.
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass


# ════════════════════════════════════════════════════════════════════════════
# DEFINIÇÃO DAS PÁGINAS
# ════════════════════════════════════════════════════════════════════════════
home = st.Page("home.py", title="Início", default=True)

# Operação do dia — o fluxo principal da Gestão
lancamento_pg = st.Page("lancamento.py", title="Lançamento")
painel_pg = st.Page("pages/1_Painel.py", title="Painel")
sugestao_palha_pg = st.Page("pages/10_Sugestao_Palha.py", title="Palha")
sugestao_cocada_pg = st.Page("pages/11_Sugestao_Cocada.py", title="Cocada")

# Análises — investigação dos dados
insights_pg = st.Page("pages/2_Insights.py", title="Insights")
vendas_pg = st.Page("pages/14_Vendas.py", title="Vendas")
curva_abc_pg = st.Page("pages/4_Curva_ABC.py", title="Curva ABC")
anomalias_pg = st.Page("pages/5_Anomalias_ML.py", title="Anomalias ML")
media_movel_pg = st.Page("pages/6_Media_Movel.py", title="Média Móvel")
bala_pg = st.Page("pages/12_Bala.py", title="Bala")

# Cadastros — gestão de dados mestres
suprimentos_pg = st.Page("pages/3_Suprimentos.py", title="Suprimentos")
reconciliacao_pg = st.Page("pages/13_Reconciliacao_SIGE.py", title="Reconciliação SIGE")
equipe_pg = st.Page("pages/8_Equipe.py", title="Equipe")

# Suporte — ajuda ao usuário
assistente_pg = st.Page("pages/7_Assistente_IA.py", title="Assistente IA")
ajuda_pg = st.Page("pages/9_Ajuda.py", title="Ajuda")

# Admin — operações raras
admin_seed_pg = st.Page("pages/0_Admin_Seed.py", title="Cadastrar BOM (setup)")


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR ORGANIZADA POR GRUPOS
# ════════════════════════════════════════════════════════════════════════════
pg = st.navigation({
    "": [home],                                       # Início sem rótulo de grupo
    "Operação do dia": [lancamento_pg, painel_pg],
    "Sugestão": [sugestao_palha_pg, sugestao_cocada_pg],
    "Análises": [insights_pg, vendas_pg, curva_abc_pg, anomalias_pg, media_movel_pg, bala_pg],
    "Cadastros": [suprimentos_pg, reconciliacao_pg, equipe_pg],
    "Suporte": [assistente_pg, ajuda_pg],
    "Admin": [admin_seed_pg],
})

pg.run()
