"""
pages/11_Sugestao_Cocada.py — Camada 2 (sugestão semi-automática) pra cocada.

Versão v3 (24/05/2026) — capacidade priorizada + sobra do tacho parcial → potes
+ viração calculada. Cobre:
  - Corte por formato (45g, Mini, Pet) por sabor.
  - Produção de bandejas (repor o estoque-alvo de P/Virar).
  - **Capacidade priorizada** (T > L > demais): quando o teto de tachos aperta,
    redistribui cortando dos sabores menos prioritários.
  - Produção de potes 260g e 605g: repor estoque-alvo + **absorver a sobra do tacho
    parcial** (modelado, com cap pelo gap pra não overshoot).
  - **Viração calculada**: sugere `ord_prod_virada` específico (não só alerta).

Pré-carregada com o dia real 11/05/2026 — comparação com a decisão real da Gestão
é mostrada embaixo (corte, produção e potes).

Princípio: o sistema SUGERE, a Gestão DECIDE.
"""
import os
import sys
import streamlit as st
import pandas as pd

try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from cocada_planejamento import (
    sugerir_cocada, SABORES, WEEKDAYS_PT,
    ALVO_PV_PADRAO, ALVO_POTE_260G_PADRAO, ALVO_POTE_605G_PADRAO,
    REND_45G, REND_MINI, REND_PET, REND_PET_Z,
    BAND_POR_TACHO, BAND_POR_TACHO_Z,
    EXEMPLO_11_05, ESPERADO_11_05,
)

st.set_page_config(
    page_title="Sugestão Cocada • Doces Vó Nena",
    layout="wide",
    initial_sidebar_state="expanded",
)
from ui_theme import aplicar_tema
aplicar_tema()


st.title("Sugestão de corte e produção — Cocada")
st.caption(
    "**Camada 2 — semi-automação (v3).** Sugere corte por formato (45g, Mini, Pet), "
    "produção de bandejas com **capacidade priorizada** (T > L > demais), "
    "produção de potes (260g, 605g) **absorvendo a sobra do tacho parcial**, "
    "e **viração calculada** pra alimentar o corte dos próximos dias. "
    "**A Gestão decide** — o sistema só sugere e pode ser ajustado."
)
usar_exemplo = st.toggle(
    "Carregar exemplo de validação (11/05/2026)",
    value=False,
    help=(
        "Liga pra preencher automaticamente com os números reais do 11/05 — "
        "útil pra ver como o sistema se comporta com inputs conhecidos e checar "
        "a validação no fim da página. Desligado (padrão): tabela vazia."
    ),
)
st.divider()


# ════════════════════════════════════════════════════════════════════════════
# Configuração
# ════════════════════════════════════════════════════════════════════════════
st.header("Configuração")
col1, col2, col3 = st.columns(3)
weekday = col1.selectbox(
    "Dia da semana",
    options=list(range(5)),
    format_func=lambda i: WEEKDAYS_PT[i],
    index=EXEMPLO_11_05['weekday'] if usar_exemplo else 0,
)
horizonte_corte = col2.slider(
    "Horizonte do corte (dias)",
    min_value=1, max_value=7, value=3,
    help="Em quantos dias o corte de hoje deve durar. Padrão 3.",
)
horizonte_producao = col3.slider(
    "Horizonte da produção (dias)",
    min_value=1, max_value=10, value=5,
    help="Em quantos dias a produção fecha o gap de P/Virar e de potes. Padrão 5.",
)

capacidade = st.number_input(
    "Capacidade da Produção hoje (tachos) — opcional. 0 = sem teto.",
    min_value=0, max_value=30, value=0, step=1,
)
capacidade_tachos = capacidade if capacidade > 0 else None
st.divider()


# ════════════════════════════════════════════════════════════════════════════
# Inputs — estoque do dia (bandejas + produto pronto + potes)
# ════════════════════════════════════════════════════════════════════════════
st.header("Estoque do dia")
st.caption(
    "Edite os valores. **Embalado** = pronto pra venda (sala de venda/estoque). "
    "**Cortado** = já cortado mas ainda não embalado (sala da Embalagem). "
    "**joel_v / joel_pv** = bandejas viradas / pra virar (papelzinho do Joel). "
    "**Potes** = unidades de pote já produzidas."
)

# Default zero (padrão) OU exemplo 11/05 (toggle ligado).
_e = EXEMPLO_11_05 if usar_exemplo else None
def _vals(k):
    return [_e[k][s] for s in SABORES] if _e else [0 for _ in SABORES]

df_estoque_default = pd.DataFrame({
    "Sabor": SABORES,
    "emb_45g (und)": _vals('emb_45g'),
    "emb_mini (und)": _vals('emb_mini'),
    "emb_pet (und)": _vals('emb_pet'),
    "cort_45g (und)": [0 for _ in SABORES],
    "cort_mini (und)": [0 for _ in SABORES],
    "cort_pet (und)": [0 for _ in SABORES],
    "joel_v (band)": _vals('joel_v'),
    "joel_pv (band)": _vals('joel_pv'),
    "pote 260g": _vals('estoque_pote_260g'),
    "pote 605g": _vals('estoque_pote_605g'),
})
df_estoque = st.data_editor(
    df_estoque_default,
    use_container_width=True,
    hide_index=True,
    disabled=["Sabor"],
    key=f"estoque_{'ex' if usar_exemplo else 'zero'}",
)


# ════════════════════════════════════════════════════════════════════════════
# Inputs — parâmetro real do dia
# ════════════════════════════════════════════════════════════════════════════
st.header("Parâmetro real do dia")
st.caption("Alvo de unidades por dia que a Gestão definiu (já com ajustes de pedidos antecipados).")

df_param_default = pd.DataFrame({
    "Sabor": SABORES,
    "param_45g": _vals('param_real_45g'),
    "param_mini": _vals('param_real_mini'),
    "param_pet": _vals('param_real_pet'),
})
df_param = st.data_editor(
    df_param_default,
    use_container_width=True,
    hide_index=True,
    disabled=["Sabor"],
    key=f"param_{'ex' if usar_exemplo else 'zero'}",
)
st.divider()


# ════════════════════════════════════════════════════════════════════════════
# Cálculo
# ════════════════════════════════════════════════════════════════════════════
def _dict_from_col(df, col):
    return dict(zip(df["Sabor"], df[col].astype(int)))

inputs = {
    'emb_45g': _dict_from_col(df_estoque, "emb_45g (und)"),
    'emb_mini': _dict_from_col(df_estoque, "emb_mini (und)"),
    'emb_pet': _dict_from_col(df_estoque, "emb_pet (und)"),
    'cort_45g': _dict_from_col(df_estoque, "cort_45g (und)"),
    'cort_mini': _dict_from_col(df_estoque, "cort_mini (und)"),
    'cort_pet': _dict_from_col(df_estoque, "cort_pet (und)"),
    'joel_v': _dict_from_col(df_estoque, "joel_v (band)"),
    'joel_pv': _dict_from_col(df_estoque, "joel_pv (band)"),
    'estoque_pote_260g': _dict_from_col(df_estoque, "pote 260g"),
    'estoque_pote_605g': _dict_from_col(df_estoque, "pote 605g"),
    'param_real_45g': _dict_from_col(df_param, "param_45g"),
    'param_real_mini': _dict_from_col(df_param, "param_mini"),
    'param_real_pet': _dict_from_col(df_param, "param_pet"),
    'weekday': weekday,
}
r = sugerir_cocada(
    **inputs,
    horizonte_corte=horizonte_corte,
    horizonte_producao=horizonte_producao,
    capacidade_tachos=capacidade_tachos,
)


# ════════════════════════════════════════════════════════════════════════════
# Resultado — corte e produção de bandejas
# ════════════════════════════════════════════════════════════════════════════
st.header("Sugestão — corte e produção (bandejas)")
df_sug = pd.DataFrame({
    "Sabor": SABORES,
    "Corte 45g (band)": [r['corte_45g'][s] for s in SABORES],
    "Corte Mini (band)": [r['corte_mini'][s] for s in SABORES],
    "Corte Pet (band)": [r['corte_pet'][s] for s in SABORES],
    "Corte total (band)": [r['corte_total'][s] for s in SABORES],
    "Sobra de viradas": [r['sobra_v'][s] for s in SABORES],
    "Produção (band)": [r['producao_band'][s] for s in SABORES],
    "Produção (tachos)": [r['producao_tachos'][s] for s in SABORES],
})
st.dataframe(df_sug, use_container_width=True, hide_index=True)

# Mostrar o que foi reduzido pela capacidade priorizada
if r['sabores_reduzidos']:
    antes = r['producao_band_antes_prioridade']
    depois = r['producao_band']
    cortes = [(s, antes[s], depois[s]) for s in r['sabores_reduzidos']]
    detalhe = ", ".join(f"{s}: {a}→{d}" for s, a, d in cortes)
    st.warning(
        f"**Capacidade priorizada acionada.** Sugestão original precisava de "
        f"{r['total_tachos_antes']} tachos (teto = {capacidade_tachos}). Reduzi a produção "
        f"de: **{detalhe}** band — priorizei T e L. Total final: {r['total_tachos']} tachos."
    )


# ════════════════════════════════════════════════════════════════════════════
# Resultado — potes (incluindo absorção da sobra do tacho parcial)
# ════════════════════════════════════════════════════════════════════════════
st.header("Sugestão — potes (unidades)")
st.caption(
    "Os potes vêm de duas fontes: **alvo** (repor estoque-alvo, espalhado em horizonte_produção dias) + "
    "**sobra do tacho parcial** (quando a produção de bandejas não é múltiplo de 8/3, sobra massa que "
    "vira pote). Default: só T, L e Z absorvem sobra (B/C/P quase nunca pedem pote)."
)
df_pote = pd.DataFrame({
    "Sabor": SABORES,
    "Estoque 260g": [inputs['estoque_pote_260g'][s] for s in SABORES],
    "Alvo 260g": [ALVO_POTE_260G_PADRAO[s] for s in SABORES],
    "Sobra band (tacho)": [r['sobra_band_tacho'][s] for s in SABORES],
    "260g alvo": [r['pote_260g_alvo'][s] for s in SABORES],
    "260g da sobra": [r['pote_260g_da_sobra'][s] for s in SABORES],
    "260g TOTAL": [r['producao_pote_260g'][s] for s in SABORES],
    "Estoque 605g": [inputs['estoque_pote_605g'][s] for s in SABORES],
    "Alvo 605g": [ALVO_POTE_605G_PADRAO[s] for s in SABORES],
    "605g alvo": [r['pote_605g_alvo'][s] for s in SABORES],
    "605g da sobra": [r['pote_605g_da_sobra'][s] for s in SABORES],
    "605g TOTAL": [r['producao_pote_605g'][s] for s in SABORES],
})
st.dataframe(df_pote, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# Resultado — viração calculada (v3)
# ════════════════════════════════════════════════════════════════════════════
st.header("Sugestão — viração (bandejas)")
st.caption(
    "Quantas bandejas virar HOJE pra alimentar o corte dos próximos ~2 dias. "
    "Aproximação: `virada = max(0, corte_total × 2 − joel_v atual)`."
)
df_vira = pd.DataFrame({
    "Sabor": SABORES,
    "joel_v atual (band)": [inputs['joel_v'][s] for s in SABORES],
    "Corte hoje (band)": [r['corte_total'][s] for s in SABORES],
    "Virada sugerida (band)": [r['virada_sugerida'][s] for s in SABORES],
})
st.dataframe(df_vira, use_container_width=True, hide_index=True)


# Sumário
total_corte = sum(r['corte_total'].values())
total_prod = sum(r['producao_band'].values())
total_p260 = sum(r['producao_pote_260g'].values())
total_p605 = sum(r['producao_pote_605g'].values())
total_vira = sum(r['virada_sugerida'].values())
st.markdown(
    f"**Hoje:** cortar **{total_corte} bandejas** · produzir **{total_prod} bandejas** "
    f"em **{r['total_tachos']} tachos** · produzir **{total_p260} potes 260g** + "
    f"**{total_p605} potes 605g** · virar **{total_vira} bandejas**."
)

if r['excede_capacidade']:
    st.error(
        f"**Mesmo após priorizar T e L, ainda excede capacidade** "
        f"({r['total_tachos']} tachos > teto {capacidade_tachos}). Reveja."
    )

sabores_alerta = [s for s in SABORES if r['alerta_viracao'][s]]
if sabores_alerta:
    st.warning(
        f"**Atenção viração:** sobra de viradas baixa (≤ 2 band) em {', '.join(sabores_alerta)}. "
        "Veja a tabela de virada sugerida acima."
    )


# ════════════════════════════════════════════════════════════════════════════
# Validação contra 11/05/2026 (quando inputs batem com o caso pré-carregado)
# ════════════════════════════════════════════════════════════════════════════
def _inputs_iguais_11_05():
    if not usar_exemplo:
        return False
    e = EXEMPLO_11_05
    if weekday != e['weekday']:
        return False
    cols_estoque = [
        ("emb_45g (und)", 'emb_45g'), ("emb_mini (und)", 'emb_mini'),
        ("emb_pet (und)", 'emb_pet'), ("joel_v (band)", 'joel_v'),
        ("joel_pv (band)", 'joel_pv'),
        ("pote 260g", 'estoque_pote_260g'), ("pote 605g", 'estoque_pote_605g'),
    ]
    for col_df, col_dict in cols_estoque:
        for s in SABORES:
            if int(df_estoque.set_index("Sabor")[col_df][s]) != e[col_dict][s]:
                return False
    # Cortados: válido só se todos zerados (caso pré-carregado)
    for col in ["cort_45g (und)", "cort_mini (und)", "cort_pet (und)"]:
        for s in SABORES:
            if int(df_estoque.set_index("Sabor")[col][s]) != 0:
                return False
    for col_df, col_dict in [
        ("param_45g", 'param_real_45g'), ("param_mini", 'param_real_mini'),
        ("param_pet", 'param_real_pet'),
    ]:
        for s in SABORES:
            if int(df_param.set_index("Sabor")[col_df][s]) != e[col_dict][s]:
                return False
    return True

if _inputs_iguais_11_05():
    st.divider()
    st.header("Validação contra o dia 11/05/2026 real")

    df_val_band = pd.DataFrame({
        "Sabor": SABORES,
        "Corte 45g sist.": [r['corte_45g'][s] for s in SABORES],
        "Corte 45g real": [ESPERADO_11_05['corte_45g'][s] for s in SABORES],
        "Corte Pet sist.": [r['corte_pet'][s] for s in SABORES],
        "Corte Pet real": [ESPERADO_11_05['corte_pet'][s] for s in SABORES],
        "Produção sist.": [r['producao_band'][s] for s in SABORES],
        "Produção real": [ESPERADO_11_05['producao'][s] for s in SABORES],
    })
    st.markdown("**Corte e produção (bandejas):**")
    st.dataframe(df_val_band, use_container_width=True, hide_index=True)

    df_val_pote = pd.DataFrame({
        "Sabor": SABORES,
        "Pote 260g sist.": [r['producao_pote_260g'][s] for s in SABORES],
        "Pote 260g real": [ESPERADO_11_05['pote_260g'][s] for s in SABORES],
        "Pote 605g sist.": [r['producao_pote_605g'][s] for s in SABORES],
        "Pote 605g real": [ESPERADO_11_05['pote_605g'][s] for s in SABORES],
    })
    st.markdown("**Potes (unidades):**")
    st.dataframe(df_val_pote, use_container_width=True, hide_index=True)

    d_45g = sum(abs(r['corte_45g'][s] - ESPERADO_11_05['corte_45g'][s]) for s in SABORES)
    d_pet = sum(abs(r['corte_pet'][s] - ESPERADO_11_05['corte_pet'][s]) for s in SABORES)
    d_prod = sum(abs(r['producao_band'][s] - ESPERADO_11_05['producao'][s]) for s in SABORES)
    d_p260 = sum(abs(r['producao_pote_260g'][s] - ESPERADO_11_05['pote_260g'][s]) for s in SABORES)
    d_p605 = sum(abs(r['producao_pote_605g'][s] - ESPERADO_11_05['pote_605g'][s]) for s in SABORES)
    total_sis = sum(r['producao_band'].values())
    total_real = sum(ESPERADO_11_05['producao'].values())

    st.markdown(
        f"**Diferenças absolutas:** Corte 45g = {d_45g} · Corte Pet = {d_pet} · "
        f"Produção bandejas = {d_prod} · Pote 260g = {d_p260} · Pote 605g = {d_p605}."
    )
    st.info(
        f"**Total da produção de bandejas:** sistema {total_sis} · Gestão {total_real} band. "
        "Quando o total bate mas a distribuição diverge, é o efeito de **capacidade + "
        "prioridade** (Gestão concentra em T/L em dias apertados). "
        "Os potes divergem porque a Gestão absorve a **sobra do tacho parcial** em potes — "
        "esse mecanismo ainda não está modelado (v3)."
    )


# ════════════════════════════════════════════════════════════════════════════
# Memória de cálculo
# ════════════════════════════════════════════════════════════════════════════
with st.expander("Como o sistema chegou aí — memória de cálculo", expanded=False):
    st.markdown(
        f"**Dia da semana:** {WEEKDAYS_PT[weekday]} · "
        f"Horizonte corte = {horizonte_corte} dias · "
        f"Horizonte produção = {horizonte_producao} dias."
    )
    st.markdown("**Corte por formato:**")
    st.markdown(
        "- `corte_band = ceil((param_real − emb) ÷ rendimento ÷ horizonte_corte)`. "
        "Distribui a necessidade em `horizonte_corte` dias."
    )
    st.markdown(
        f"- **Rendimentos:** 45g = {REND_45G} und/band · Mini = {REND_MINI} · "
        f"Pet = {REND_PET} (Z Pet = {REND_PET_Z})."
    )
    st.markdown(
        "- **Calendário (flexível, da análise das folhas):** 45g todo dia útil · "
        "Mini Ter/Qua/Sex · Pet todo dia útil."
    )
    st.markdown("**Produção de bandejas:**")
    st.markdown(
        "- `producao_band = ceil((alvo_pv − joel_pv) ÷ horizonte_producao)`. "
        f"Alvo P/Virar (CLAUDE.md): {ALVO_PV_PADRAO}."
    )
    st.markdown(
        f"- **Bandejas por tacho:** {BAND_POR_TACHO} (Zero = {BAND_POR_TACHO_Z})."
    )
    st.markdown("**Produção de potes (v3 — alvo + sobra do tacho parcial):**")
    st.markdown(
        "- **Pote alvo:** `ceil((alvo_pote − estoque) ÷ horizonte_producao)`. "
        f"Alvo 260g: {ALVO_POTE_260G_PADRAO}. Alvo 605g: {ALVO_POTE_605G_PADRAO}."
    )
    st.markdown(
        "- **Pote da sobra:** quando `producao_band` não é múltiplo de 8 (3 pra Z), "
        "sobra massa do tacho cozido. Essa sobra vira pote (T, L, Z por default — "
        "B/C/P quase nunca pedem). Conversão conservadora: 1 band → 10 potes 260g "
        "ou 5 potes 605g."
    )
    st.markdown(
        "- **Cap pelo gap:** o pote da sobra é limitado pelo `alvo − estoque` pra "
        "não overshootar quando o estoque já está perto do alvo."
    )
    st.markdown("**Capacidade priorizada (v3):**")
    st.markdown(
        "- Quando `total_tachos > capacidade`, reduzo a produção dos sabores **menos** "
        "prioritários (Z, P, C, B, L) até caber. **T sempre preservado.** "
        "1 tacho = 8 band (Z = 3)."
    )
    st.markdown("**Viração calculada (v3):**")
    st.markdown(
        "- `virada_sugerida = max(0, corte_total × 2 − joel_v)`. Mantém ~2 dias de viradas "
        "à frente. Aproximação — pode evoluir pra olhar 3 dias específicos."
    )


with st.expander("Notas e limitações desta v3", expanded=False):
    st.markdown(
        """
        - **Validação contra 12 folhas (24/05):** comparado com a v2, a v3 mantém o erro de corte (+94 band) e produção (−41 band) — esses dependem de a `capacidade_tachos` ser passada. Pote ficou em +186 und (era −80 na v2): trocou direção do erro mas magnitude similar.
        - **Sobra do tacho → pote** é APROXIMAÇÃO. A regra real depende de julgamento da Gestão (mistura 260g/605g, decide quando ignora a sobra, etc.). Refinar exige fichas mais detalhadas das folhas (tachos cozidos + destino real).
        - **Calendário** é flexível por design — a Gestão pode override (edita o slider).
        - **Capacidade priorizada** só atua se `capacidade_tachos > 0` no input. Sem capacidade, sistema espalha em todos os sabores (o que difere do julgamento da Gestão em dias apertados — por isso o `+94 corte` da v2 persiste).
        - **Diferenças vs decisão real geralmente vêm de:** pedidos antecipados não no `param_real`, capacidade variável do dia, e julgamento de prioridade. Não é bug.
        """
    )
