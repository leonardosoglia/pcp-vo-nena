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
home = st.Page("home.py", title="Início", icon=":material/home:", default=True)

# Operação do dia — o fluxo principal da Gestão
lancamento_pg = st.Page("lancamento.py", title="Lançamento", icon=":material/edit_note:")
painel_pg = st.Page("pages/1_Painel.py", title="Painel", icon=":material/dashboard:")
sugestao_palha_pg = st.Page("pages/10_Sugestao_Palha.py", title="Palha", icon=":material/bakery_dining:")
sugestao_cocada_pg = st.Page("pages/11_Sugestao_Cocada.py", title="Cocada", icon=":material/cake:")

# Análises — investigação dos dados
insights_pg = st.Page("pages/2_Insights.py", title="Insights", icon=":material/lightbulb:")
vendas_pg = st.Page("pages/14_Vendas.py", title="Vendas", icon=":material/shopping_cart:")
lucratividade_pg = st.Page("pages/15_Lucratividade.py", title="Lucratividade", icon=":material/trending_up:")
producao_demanda_pg = st.Page("pages/16_Producao_x_Demanda.py", title="Produção × Demanda", icon=":material/compare_arrows:")
curva_abc_pg = st.Page("pages/4_Curva_ABC.py", title="Curva ABC", icon=":material/bar_chart:")
anomalias_pg = st.Page("pages/5_Anomalias_ML.py", title="Anomalias ML", icon=":material/warning:")
media_movel_pg = st.Page("pages/6_Media_Movel.py", title="Média Móvel", icon=":material/show_chart:")
bala_pg = st.Page("pages/12_Bala.py", title="Bala", icon=":material/cookie:")

# Cadastros — gestão de dados mestres
suprimentos_pg = st.Page("pages/3_Suprimentos.py", title="Suprimentos", icon=":material/inventory_2:")
reconciliacao_pg = st.Page("pages/13_Reconciliacao_SIGE.py", title="Reconciliação SIGE", icon=":material/sync:")
equipe_pg = st.Page("pages/8_Equipe.py", title="Equipe", icon=":material/group:")

# Suporte — ajuda ao usuário
assistente_pg = st.Page("pages/7_Assistente_IA.py", title="Assistente IA", icon=":material/smart_toy:")
ajuda_pg = st.Page("pages/9_Ajuda.py", title="Ajuda", icon=":material/help:")

# Admin — operações raras
admin_seed_pg = st.Page("pages/0_Admin_Seed.py", title="Cadastrar BOM (setup)", icon=":material/settings:")


# ════════════════════════════════════════════════════════════════════════════
# LOGO / CABEÇALHO NO TOPO DA SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
_LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo_vo_nena.svg")
try:
    st.logo(_LOGO, size="large")
except Exception:
    pass


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR ORGANIZADA POR GRUPOS
# ════════════════════════════════════════════════════════════════════════════
pg = st.navigation({
    "": [home],                                       # Início sem rótulo de grupo
    "Operação do dia": [lancamento_pg, painel_pg],
    "Sugestão": [sugestao_palha_pg, sugestao_cocada_pg],
    "Vendas & resultado": [vendas_pg, lucratividade_pg, producao_demanda_pg],
    "Análise da produção": [curva_abc_pg, media_movel_pg, anomalias_pg, insights_pg, bala_pg],
    "Cadastros": [suprimentos_pg, reconciliacao_pg, equipe_pg],
    "Suporte": [assistente_pg, ajuda_pg],
    "Admin": [admin_seed_pg],
}, expanded=True)  # menu SEMPRE aberto (sem o "Ver mais/menos" que ficava grudado)

pg.run()
