"""
pages/10_Sugestao_Palha.py — Camada 2 (sugestão semi-automática) pra palha.

Calculadora que aplica a lógica documentada no CADERNO.md seção 1.A:
  - CORTE     = necessidade líquida (demanda da semana − estoque pronto) ÷ rendimento.
  - PRODUÇÃO  = estoque-alvo de bandejas − sobra após o corte (order-up-to).

Pré-carregada com o exemplo real do 18/05/2026 (segunda) — o resultado deve bater
com o que a Gestão fez à mão naquele dia. É a primeira prova de que a automação
funciona.

Princípio: o sistema SUGERE, a Gestão DECIDE.
"""
import os
import sys
import streamlit as st
import pandas as pd

# Bootstrap (mantém o padrão das outras páginas)
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from palha_planejamento import (
    sugerir_palha, SABORES, SABORES_50G,
    IDEAL_DISPLAYS_POR_DIA, IDEAL_PET_POR_DIA_SABOR, ALVO_BANDEJAS,
    COMPOSICAO_DISPLAY, REND_50G_POR_BANDEJA, REND_PET_POR_BANDEJA,
    EXEMPLO_VALIDACAO_18_05, ESPERADO_18_05,
)

st.set_page_config(
    page_title="Sugestão Palha • Doces Vó Nena",
    layout="wide",
    initial_sidebar_state="expanded",
)
from ui_theme import aplicar_tema
aplicar_tema()


st.title("Sugestão de corte e produção — Palha")
st.caption(
    "**Camada 2 — semi-automação.** Toda segunda, o sistema sugere quanto cortar (50g + Pet) "
    "e quanto produzir de bandejas de palha, a partir dos estoques do dia. "
    "**A Gestão decide** — o sistema só sugere e pode ser ajustado."
)
usar_exemplo = st.toggle(
    "Carregar exemplo de validação (18/05/2026)",
    value=False,
    help=(
        "Liga pra preencher automaticamente com os números reais do 18/05 — "
        "útil pra ver como o sistema se comporta com inputs conhecidos e checar "
        "a validação no fim da página. Desligado (padrão): tabela vazia."
    ),
)
st.divider()


# ════════════════════════════════════════════════════════════════════════════
# Inputs — estoque do dia
# ════════════════════════════════════════════════════════════════════════════
st.header("Estoque do dia")

# Defaults: zeros (padrão) OU exemplo 18/05 se o toggle estiver ligado.
ZERO_DEFAULTS = {
    "estoque_displays": 0,
    "estoque_50g": {s: 0 for s in SABORES_50G},
    "estoque_pet": {s: 0 for s in SABORES},
    "estoque_bandejas": {s: 0 for s in SABORES},
}
defaults = EXEMPLO_VALIDACAO_18_05 if usar_exemplo else ZERO_DEFAULTS
# Sufixo de key — força o Streamlit a recriar os widgets quando o toggle muda,
# senão os values default não atualizam depois que o usuário interagiu.
ks = "ex" if usar_exemplo else "zero"

st.info(
    "**Input mais importante:** quantos displays de 50g já estão montados. "
    "Esse número varia muito de semana pra semana (~0 a ~50) e tem o maior impacto na sugestão. "
    "Pergunte à Embalagem antes de rodar."
)
col_d, _ = st.columns([1, 3])
estoque_displays = col_d.number_input(
    "Displays montados em estoque",
    min_value=0, value=defaults["estoque_displays"], step=1,
    key=f"displays_{ks}",
    help=(
        "1 display = 10 palhas 50g (4T + 4L + 2CH). Soma TODOS os displays prontos na "
        "geladeira/sala da Embalagem. Validado contra a semana de 18/05: com este valor "
        "em 35, a sugestão bate no centavo a decisão real da Gestão."
    ),
)
with st.expander("Por que esse input é tão crítico?", expanded=False):
    st.markdown(
        "**A semana tem ideal de 168 displays.** Se já tem 35 prontos, faltam 133 → "
        "se não tem nenhum, faltam 168 → o sistema sugere ~25% mais corte. "
        "**Validação 24/05:** rodando contra 3 semanas (04/05, 11/05, 18/05) — com o valor "
        "certo de displays, o sistema reproduz a decisão real da Gestão dentro de ~5%. Sem esse "
        "input, o erro pode chegar a +25%. **Médio prazo:** vira coluna na folha do dia."
    )

st.markdown("**Palha 50g pronta em estoque** (só T, L, CH têm 50g):")
cols = st.columns(3)
estoque_50g = {}
for i, s in enumerate(SABORES_50G):
    estoque_50g[s] = cols[i].number_input(
        f"50g {s}", min_value=0, value=defaults["estoque_50g"][s], step=1,
        key=f"50g_{s}_{ks}",
    )

st.markdown("**Pet pronto em estoque**:")
cols = st.columns(5)
estoque_pet = {}
for i, s in enumerate(SABORES):
    estoque_pet[s] = cols[i].number_input(
        f"Pet {s}", min_value=0, value=defaults["estoque_pet"][s], step=1,
        key=f"pet_{s}_{ks}",
    )

st.markdown("**Bandejas em estoque**:")
cols = st.columns(5)
estoque_bandejas = {}
for i, s in enumerate(SABORES):
    estoque_bandejas[s] = cols[i].number_input(
        f"Band {s}", min_value=0, value=defaults["estoque_bandejas"][s], step=1,
        key=f"band_{s}_{ks}",
    )

st.divider()


# ════════════════════════════════════════════════════════════════════════════
# Cálculo — 2 versões: NORMAL (arredondamento clássico) e CONSERVADOR (floor)
# ════════════════════════════════════════════════════════════════════════════
r = sugerir_palha(
    estoque_displays=estoque_displays,
    estoque_50g=estoque_50g,
    estoque_pet=estoque_pet,
    estoque_bandejas=estoque_bandejas,
    regra_arredondamento='round',
)
r_conserv = sugerir_palha(
    estoque_displays=estoque_displays,
    estoque_50g=estoque_50g,
    estoque_pet=estoque_pet,
    estoque_bandejas=estoque_bandejas,
    regra_arredondamento='conservador',
)


# ════════════════════════════════════════════════════════════════════════════
# Resultado — quadro NORMAL
# ════════════════════════════════════════════════════════════════════════════
st.header("Sugestão (normal — arredondamento clássico)")

df = pd.DataFrame({
    "Sabor": SABORES,
    "Corte 50g (band)": [r["corte_50g"][s] for s in SABORES],
    "Corte Pet (band)": [r["corte_pet"][s] for s in SABORES],
    "Corte total (band)": [r["corte_total"][s] for s in SABORES],
    "Sobra após corte": [r["sobra"][s] for s in SABORES],
    "Produção sugerida (band)": [r["producao"][s] for s in SABORES],
})
st.dataframe(df, use_container_width=True, hide_index=True)

# Sumário em uma linha
def _resumo(d):
    return " · ".join(f"{s} {d[s]}" for s in SABORES)
total_corte = sum(r["corte_total"].values())
total_prod = sum(r["producao"].values())
st.markdown(
    f"**Esta semana (normal):** cortar **{total_corte} bandejas** ({_resumo(r['corte_total'])}) · "
    f"produzir **{total_prod} bandejas** ({_resumo(r['producao'])})."
)


# ════════════════════════════════════════════════════════════════════════════
# Resultado — quadro CONSERVADOR (amarelo claro)
# ════════════════════════════════════════════════════════════════════════════
st.markdown(
    """<div style="background:#fffacd; padding: 14px 18px; border-radius: 8px; border-left: 6px solid #f0c020; margin-top: 8px;">
    <h3 style="margin: 0 0 6px 0;">Sugestão (conservadora — puxa pra menos no Pet)</h3>
    <p style="margin: 0; font-size: 0.92em; color: #555;">
    No <strong>Pet</strong>: se a fração decimal &lt; 0.81, arredonda pra baixo
    (ex: 1.80 → 1, 1.67 → 1). Acima disso, segue a regra normal (1.83 → 2).
    No <strong>50g</strong> e na <strong>produção</strong>: segue o arredondamento clássico.
    Calibrado com a folha real de 25/05/2026 — bate com a decisão da Gestão.
    </p>
    </div>""",
    unsafe_allow_html=True,
)

df_c = pd.DataFrame({
    "Sabor": SABORES,
    "Corte 50g (band)": [r_conserv["corte_50g"][s] for s in SABORES],
    "Corte Pet (band)": [r_conserv["corte_pet"][s] for s in SABORES],
    "Corte total (band)": [r_conserv["corte_total"][s] for s in SABORES],
    "Sobra após corte": [r_conserv["sobra"][s] for s in SABORES],
    "Produção sugerida (band)": [r_conserv["producao"][s] for s in SABORES],
})
st.dataframe(
    df_c.style.set_properties(**{"background-color": "#fffacd"}),
    use_container_width=True, hide_index=True,
)

total_corte_c = sum(r_conserv["corte_total"].values())
total_prod_c = sum(r_conserv["producao"].values())
st.markdown(
    f"**Esta semana (conservador):** cortar **{total_corte_c} bandejas** ({_resumo(r_conserv['corte_total'])}) · "
    f"produzir **{total_prod_c} bandejas** ({_resumo(r_conserv['producao'])})."
)

# Onde os 2 quadros divergem (fica fácil pra Gestão escolher)
divergencias = []
for s in SABORES:
    if r["corte_50g"][s] != r_conserv["corte_50g"][s]:
        divergencias.append(f"{s} 50g (normal {r['corte_50g'][s]} · conserv {r_conserv['corte_50g'][s]})")
    if r["corte_pet"][s] != r_conserv["corte_pet"][s]:
        divergencias.append(f"{s} Pet (normal {r['corte_pet'][s]} · conserv {r_conserv['corte_pet'][s]})")
if divergencias:
    st.caption("**Onde os dois quadros divergem:** " + " · ".join(divergencias))
else:
    st.caption("Os dois quadros chegaram nos mesmos valores — não há fração em zona cinza esta semana.")

# Validação automática só roda quando o toggle "Carregar exemplo" está ligado
# E os inputs não foram alterados pelo usuário.
inputs_iguais_validacao = (
    usar_exemplo
    and estoque_displays == EXEMPLO_VALIDACAO_18_05["estoque_displays"]
    and estoque_50g == EXEMPLO_VALIDACAO_18_05["estoque_50g"]
    and estoque_pet == EXEMPLO_VALIDACAO_18_05["estoque_pet"]
    and estoque_bandejas == EXEMPLO_VALIDACAO_18_05["estoque_bandejas"]
)
if inputs_iguais_validacao:
    bate_corte = r["corte_total"] == ESPERADO_18_05["corte_total"]
    bate_prod = r["producao"] == ESPERADO_18_05["producao"]
    if bate_corte and bate_prod:
        st.success(
            "**Validação 18/05/2026: bate.** O sistema produziu exatamente os mesmos "
            "números que a Gestão fez à mão. A lógica está correta."
        )
    else:
        difs = []
        if not bate_corte:
            difs.append(f"corte sistema {r['corte_total']} vs Gestão {ESPERADO_18_05['corte_total']}")
        if not bate_prod:
            difs.append(f"produção sistema {r['producao']} vs Gestão {ESPERADO_18_05['producao']}")
        st.warning(
            "**Validação 18/05/2026: diverge em algum sabor.** " + " · ".join(difs)
            + ". A diferença geralmente vem do arredondamento — a Gestão usa julgamento "
              "(tende a não sobreproduzir). Veja a 'memória de cálculo' abaixo pra entender."
        )


# ════════════════════════════════════════════════════════════════════════════
# Memória de cálculo (transparência — pra Gestão entender e checar)
# ════════════════════════════════════════════════════════════════════════════
with st.expander("Como o sistema chegou aí — memória de cálculo", expanded=False):
    t = r["trace"]
    st.markdown(
        f"**Necessidade da semana:** {t['ideal_displays_semana']} displays "
        f"− {estoque_displays} em estoque = **{t['displays_necessarios']} displays a produzir**."
    )

    st.markdown("**Corte para 50g** (1 bandeja rende ~80 palhas 50g):")
    for s in SABORES_50G:
        st.markdown(
            f"- {s}: precisa {t['unidades_50g_necessarias'][s]} unidades · em estoque {estoque_50g[s]} "
            f"· líquido **{t['liquido_50g'][s]}** ÷ {REND_50G_POR_BANDEJA} = "
            f"{t['frac_50g'][s]:.2f} → **corte {r['corte_50g'][s]} bandeja(s)**."
        )

    st.markdown("**Corte para Pet** (1 bandeja rende 30 Pets):")
    for s in SABORES:
        st.markdown(
            f"- {s}: precisa {t['ideal_pet_semana'][s]} unidades · em estoque {estoque_pet[s]} "
            f"· líquido **{t['liquido_pet'][s]}** ÷ {REND_PET_POR_BANDEJA} = "
            f"{t['frac_pet'][s]:.2f} → **corte {r['corte_pet'][s]} bandeja(s)**."
        )

    st.markdown("**Produção** (repor o estoque-alvo de bandejas):")
    for s in SABORES:
        st.markdown(
            f"- {s}: alvo {t['alvo_bandejas'][s]} − sobra {r['sobra'][s]} "
            f"= **produzir {r['producao'][s]} bandeja(s)**."
        )


# ════════════════════════════════════════════════════════════════════════════
# Constantes (avançado)
# ════════════════════════════════════════════════════════════════════════════
with st.expander("Constantes da semana (avançado)", expanded=False):
    st.caption(
        "Valores fixos por enquanto — vieram do caderno. Quando a Gestão quiser "
        "ajustar (ex: por sazonalidade), isso vira uma tela de configuração."
    )
    st.markdown(f"- **Ideal de displays por dia:** {IDEAL_DISPLAYS_POR_DIA} → semana = {sum(IDEAL_DISPLAYS_POR_DIA.values())}")
    st.markdown(f"- **Ideal de Pet por dia (cada terça e cada sexta):** {IDEAL_PET_POR_DIA_SABOR}")
    st.markdown(f"- **Estoque-alvo de bandejas:** {ALVO_BANDEJAS}")
    st.markdown(f"- **1 display de 50g = ** {COMPOSICAO_DISPLAY}")
    st.markdown(
        f"- **Rendimento da bandeja:** {REND_50G_POR_BANDEJA} palhas 50g "
        f"(mínimo; rende 80-90) · {REND_PET_POR_BANDEJA} Pets."
    )
