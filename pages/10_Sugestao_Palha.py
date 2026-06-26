"""
pages/10_Sugestao_Palha.py — Camada 2 (sugestão semi-automática) pra palha.

Calculadora que aplica a lógica documentada no CADERNO.md seção 1.A:
  - CORTE     = necessidade líquida (demanda da semana − estoque pronto) ÷ rendimento.
  - PRODUÇÃO  = estoque-alvo de bandejas − sobra após o corte (order-up-to).

Reforma visual 26/06/2026: virou PAINEL DE DECISÃO — números-chave em cartões no
topo, textos enxutos, estoque/conservadora/memória em seções recolhíveis.
NENHUM cálculo mudou (sugerir_palha, tabelas e validação idênticos).

Princípio: o sistema SUGERE, a Gestão DECIDE.
"""
import os
import sys
from datetime import date
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
import cached_db

# Sabor no banco → sigla na calculadora
SIGLA_PALHA_DB = {
    'TRADICIONAL': 'T', 'LEITE EM PÓ': 'L',
    'CHURROS': 'CH', 'COOKIES': 'CK', 'LIMÃO': 'LIM',
}

st.set_page_config(
    page_title="Sugestão Palha • Doces Vó Nena",
    layout="wide",
    initial_sidebar_state="expanded",
)
from ui_theme import aplicar_tema
aplicar_tema()


# ════════════════════════════════════════════════════════════════════════════
# CSS do painel de decisão (page-local — fiel ao mockup aprovado)
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
.sgp-eyebrow{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#C05621;background:#FBEADF;padding:3px 9px;border-radius:6px;margin-bottom:9px}
.sgp-title{font-size:20px;font-weight:700;color:#151921;margin:0 0 4px;letter-spacing:-.01em}
.sgp-sub{font-size:12.5px;color:#6B7280;margin:0 0 6px;line-height:1.5;max-width:680px}
.sgp-card{background:#fff;border:1px solid #ECEDEF;border-radius:14px;padding:15px 16px;box-shadow:0 1px 2px rgba(16,24,40,.04),0 4px 10px rgba(16,24,40,.04)}
.sgp-chip{width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;margin-bottom:11px}
.sgp-lab{font-size:10px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:#9AA1AC;margin-bottom:3px}
.sgp-val{font-size:26px;font-weight:700;color:#151921;line-height:1;letter-spacing:-.02em}
.sgp-unit{font-size:13px;font-weight:500;color:#9AA1AC;margin-left:5px}
.sgp-csub{font-size:11px;color:#B0B6BE;margin-top:6px}
.sgp-ctx{display:inline-flex;align-items:center;gap:6px;font-size:11.5px;font-weight:500;color:#475569;background:#EEF0F3;padding:4px 11px;border-radius:999px;margin-top:6px}
.sgp-h{font-size:13px;font-weight:600;color:#151921;margin:14px 0 8px}
</style>
""", unsafe_allow_html=True)

_SVG_SCISSORS = '<svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><line x1="20" y1="4" x2="8.12" y2="15.88"></line><line x1="14.47" y1="14.48" x2="20" y2="20"></line><line x1="8.12" y1="8.12" x2="12" y2="12"></line></svg>'
_SVG_LAYERS = '<svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>'


def _kpi(col, icone_svg, cor, chip_bg, label, valor, unidade, sub):
    """Cartão de indicador do painel de decisão."""
    col.markdown(
        f'<div class="sgp-card"><div class="sgp-chip" style="background:{chip_bg}">'
        f'{icone_svg.format(c=cor)}</div><div class="sgp-lab">{label}</div>'
        f'<div><span class="sgp-val">{valor}</span><span class="sgp-unit">{unidade}</span></div>'
        f'<div class="sgp-csub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# Cabeçalho enxuto
# ════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="sgp-eyebrow">Sugestão · Palha</div>'
    '<div class="sgp-title">Corte e produção da semana</div>'
    '<div class="sgp-sub">A partir dos estoques do dia, o sistema sugere quanto cortar '
    '(50g + Pet) e quanto produzir de bandejas. <b>A Gestão decide.</b></div>',
    unsafe_allow_html=True,
)

# Painel de decisão (preenchido depois do cálculo) — fica no topo
kpi_box = st.container()


# ════════════════════════════════════════════════════════════════════════════
# Seletor de data: puxa os estoques direto do banco
# ════════════════════════════════════════════════════════════════════════════
col_data, _ = st.columns([1, 3])
data_sel = col_data.date_input(
    "Data da folha",
    value=None,
    format="DD/MM/YYYY",
    help=(
        "Selecione uma data com folha lançada — o sistema preenche os estoques "
        "do dia automaticamente. Deixe vazio pra preencher manualmente."
    ),
)

# Tenta carregar do banco se a data foi escolhida
ZERO_DEFAULTS = {
    "estoque_displays": 0,
    "estoque_50g": {s: 0 for s in SABORES_50G},
    "estoque_pet": {s: 0 for s in SABORES},
    "estoque_bandejas": {s: 0 for s in SABORES},
}
defaults = dict(ZERO_DEFAULTS)
ks = "manual"  # sufixo das keys dos widgets
fonte_dados = "manual"

if data_sel is not None:
    try:
        rows = cached_db.get_folha_palha(data_sel.isoformat())
    except Exception as e:
        st.error(f"Não consegui ler a folha do banco: {e}")
        rows = []
    if rows:
        by_sabor = {r['sabor']: r for r in rows}
        e50 = {}
        ep = {}
        cb = {}
        for nome, sigla in SIGLA_PALHA_DB.items():
            r = by_sabor.get(nome, {})
            ep[sigla] = r.get('emb_pet') or 0
            cb[sigla] = r.get('cont_band_palha') or 0
            if sigla in SABORES_50G:
                e50[sigla] = r.get('emb_50g') or 0
        defaults = {
            "estoque_displays": 0,  # não está no banco
            "estoque_50g": e50,
            "estoque_pet": ep,
            "estoque_bandejas": cb,
        }
        ks = data_sel.isoformat()
        fonte_dados = "banco"
        st.success(
            f"Folha de **{data_sel.strftime('%d/%m/%Y')}** carregada do banco. "
            "Os estoques (50g, Pet, bandejas) vieram da folha lançada. "
            "Abra o painel de estoque abaixo pra ver/editar."
        )
    else:
        st.warning(
            f"Não há folha lançada pra **{data_sel.strftime('%d/%m/%Y')}**. "
            "Os campos ficam zerados — preencha manualmente no painel abaixo."
        )
        ks = f"vazio_{data_sel.isoformat()}"


# ════════════════════════════════════════════════════════════════════════════
# Inputs — estoque do dia + ajustes da semana (recolhível)
# ════════════════════════════════════════════════════════════════════════════
with st.expander("Estoque do dia & ajustes da semana (editar)", expanded=(fonte_dados != "banco")):
    st.caption(
        "Input mais sensível: **quantos displays de 50g já estão montados** "
        "(varia ~0 a ~50 por semana e é o que mais mexe na sugestão — pergunte à Embalagem). "
        "50g, Pet e bandejas vêm da folha quando você escolhe a data."
    )

    _col_sem, _ = st.columns([1, 3])
    ideal_displays_semana = _col_sem.number_input(
        "Somatório de displays da semana",
        min_value=0, value=136, step=1,
        key=f"ideal_disp_{ks}",
        help="Ex.: 136 (ter–sex) · 168 (seg–sex) · ou o que a semana pedir. × composição (T=4) → unidades de T.",
    )

    col_d, _ = st.columns([1, 3])
    estoque_displays = col_d.number_input(
        "Displays montados em estoque",
        min_value=0, value=defaults["estoque_displays"], step=1,
        key=f"displays_{ks}",
        help=(
            "1 display = 10 palhas 50g (4T + 4L + 2CH). Soma TODOS os displays prontos na "
            "geladeira/sala da Embalagem. Quanto mais prontos, menos corte o sistema sugere."
        ),
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


# ════════════════════════════════════════════════════════════════════════════
# Cálculo — 2 versões: NORMAL (arredondamento clássico) e CONSERVADOR (floor)
# ════════════════════════════════════════════════════════════════════════════
r = sugerir_palha(
    estoque_displays=estoque_displays,
    estoque_50g=estoque_50g,
    estoque_pet=estoque_pet,
    estoque_bandejas=estoque_bandejas,
    ideal_displays_semana=ideal_displays_semana,
    regra_arredondamento='round',
)
r_conserv = sugerir_palha(
    estoque_displays=estoque_displays,
    estoque_50g=estoque_50g,
    estoque_pet=estoque_pet,
    estoque_bandejas=estoque_bandejas,
    ideal_displays_semana=ideal_displays_semana,
    regra_arredondamento='conservador',
)


# Totais + resumo por sabor
def _resumo(d):
    return " · ".join(f"{s} {d[s]}" for s in SABORES)
total_corte = sum(r["corte_total"].values())
total_prod = sum(r["producao"].values())


# ════════════════════════════════════════════════════════════════════════════
# Painel de decisão (topo) — números-chave em cartões
# ════════════════════════════════════════════════════════════════════════════
with kpi_box:
    _c1, _c2, _c3 = st.columns([1, 1, 1])
    _kpi(_c1, _SVG_SCISSORS, "#C05621", "#FBEADF", "Cortar esta semana", total_corte, "band", "50g + Pet, por sabor")
    _kpi(_c2, _SVG_LAYERS, "#A16207", "#FBF1DA", "Produzir", total_prod, "band", "repor o estoque-alvo")
    _ctx = (
        f"Semana de {data_sel.strftime('%d/%m/%Y')}" if data_sel is not None
        else "Selecione uma data ou preencha os estoques"
    )
    _c3.markdown(f'<span class="sgp-ctx">{_ctx}</span>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# Detalhe por sabor — quadro NORMAL
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sgp-h">Detalhe por sabor</div>', unsafe_allow_html=True)

df = pd.DataFrame({
    "Sabor": SABORES,
    "Corte 50g (band)": [r["corte_50g"][s] for s in SABORES],
    "Corte Pet (band)": [r["corte_pet"][s] for s in SABORES],
    "Corte total (band)": [r["corte_total"][s] for s in SABORES],
    "Sobra após corte": [r["sobra"][s] for s in SABORES],
    "Produção sugerida (band)": [r["producao"][s] for s in SABORES],
})
st.dataframe(df, width='stretch', hide_index=True)
st.caption(
    f"Esta semana: cortar **{total_corte} band** ({_resumo(r['corte_total'])}) · "
    f"produzir **{total_prod} band** ({_resumo(r['producao'])})."
)


# ════════════════════════════════════════════════════════════════════════════
# Versão conservadora (recolhível) — evita cortar bandeja pra cobrir sobra pequena
# ════════════════════════════════════════════════════════════════════════════
with st.expander("Versão conservadora — evita cortar bandeja pra cobrir sobra pequena", expanded=False):
    st.caption(
        "No 50g: se a necessidade líquida < 60 unidades, NÃO corta nenhuma bandeja. "
        "No Pet: fração decimal < 0,81 arredonda pra baixo (1,80 → 1). "
        "Na produção: arredondamento clássico. Calibrado com folhas reais de 25/05 (Pet) e 27/05 (50g)."
    )

    df_c = pd.DataFrame({
        "Sabor": SABORES,
        "Corte 50g (band)": [r_conserv["corte_50g"][s] for s in SABORES],
        "Corte Pet (band)": [r_conserv["corte_pet"][s] for s in SABORES],
        "Corte total (band)": [r_conserv["corte_total"][s] for s in SABORES],
        "Sobra após corte": [r_conserv["sobra"][s] for s in SABORES],
        "Produção sugerida (band)": [r_conserv["producao"][s] for s in SABORES],
    })
    st.dataframe(df_c, width='stretch', hide_index=True)

    total_corte_c = sum(r_conserv["corte_total"].values())
    total_prod_c = sum(r_conserv["producao"].values())
    st.caption(
        f"Conservador: cortar **{total_corte_c} band** ({_resumo(r_conserv['corte_total'])}) · "
        f"produzir **{total_prod_c} band** ({_resumo(r_conserv['producao'])})."
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


# Validação automática só roda quando a data é 18/05/2026 + displays = 35
# (valor histórico que faz o sistema bater com a decisão real da Gestão).
inputs_iguais_validacao = (
    data_sel == date(2026, 5, 18)
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

_rodape_data = data_sel.strftime('%d/%m/%Y') if data_sel is not None else "sem data selecionada"
st.caption(
    f"Calculado para {_rodape_data} · fonte: {fonte_dados} · "
    "dados em cache ~1 min."
)
