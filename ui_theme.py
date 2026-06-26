"""
ui_theme.py — Sistema de design profissional do PCP Vó Nena.

Inspirado em design systems modernos (Linear, Vercel, Stripe).
Princípios:
1. Sidebar escura (slate-900) + conteúdo claro = padrão SaaS profissional
2. Laranja Vó Nena (#C05621) APENAS como accent (botões primários, links, item ativo)
3. Tipografia hierárquica (Inter, 5 níveis)
4. Cards com sombra sutil, sem gradientes
5. Contraste WCAG AAA em texto / WCAG AA em UI (validado)
6. Zero emoji decorativo — apenas semânticos quando inevitáveis (✓ ✗ ⚠)

Aplicação:
    from ui_theme import aplicar_tema
    aplicar_tema()  # após st.set_page_config()

Decisões de design (19/05/2026, sessão de refatoração):
- Sidebar dark slate-900 (#0F172A) > preto puro (mais elegante)
- Brand orange RESTRITO a 5 lugares: h1 (não!), botões primários, links,
  item ativo da sidebar, badges de destaque
- Texto strong (slate-950 #020617) pra títulos, slate-900 pra body
- Border slate-200 (#E4E4E7) em vez de #E5E7EB (mais frio, casa melhor)
"""
import streamlit as st


# ═══════════════════════════════════════════════════════════════════════════
# Color tokens — paleta validada (contraste WCAG)
# ═══════════════════════════════════════════════════════════════════════════
TOKENS = {
    # Brand — laranja Vó Nena (uso RESTRITO)
    "brand":         "#C05621",
    "brand_hover":   "#9A4419",
    "brand_subtle":  "#FFF7ED",

    # Surface (light)
    "page":          "#FFFFFF",
    "surface":       "#FAFAFA",
    "surface_alt":   "#F4F4F5",
    "border":        "#E4E4E7",
    "border_strong": "#D4D4D8",

    # Text (light)
    "text_strong":   "#020617",  # h1, valores de métricas
    "text":          "#0F172A",  # body, h2, h3
    "text_secondary":"#475569",  # captions importantes
    "text_muted":    "#71717A",  # captions, labels

    # Sidebar dark (slate-900 family)
    "sb_bg":         "#0F172A",
    "sb_surface":    "#1E293B",  # hover state
    "sb_surface_2":  "#334155",  # mais claro pra contraste
    "sb_border":     "#1E293B",
    "sb_text":       "#F1F5F9",
    "sb_text_muted": "#94A3B8",

    # Status (semântico)
    "success":       "#16A34A",
    "success_bg":    "#F0FDF4",
    "success_text":  "#14532D",
    "warning":       "#CA8A04",
    "warning_bg":    "#FEFCE8",
    "warning_text":  "#713F12",
    "danger":        "#DC2626",
    "danger_bg":     "#FEF2F2",
    "danger_text":   "#7F1D1D",
    "info":          "#2563EB",
    "info_bg":       "#EFF6FF",
    "info_text":     "#1E3A8A",
}


def aplicar_tema():
    """Injeta CSS global. Chamar após st.set_page_config()."""
    t = TOKENS
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ─────────────────────────── BASE ─────────────────────────── */
html, body, .stApp {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: {t['text']};
    background: {t['page']};
}}

.stApp {{
    font-size: 13px;
}}

.block-container {{
    padding-top: 0.6rem;
    padding-bottom: 1.5rem;
    max-width: 1200px;
}}

/* Colunas — gap compacto. O default do Streamlit (1rem=16px) desperdica
   ~80px numa linha de 6 colunas, espremendo os inputs numericos da folha
   a ponto de cortar o numero. 0.3rem devolve esse espaco. */
[data-testid="stMain"] [data-testid="stHorizontalBlock"] {{
    gap: 0.3rem !important;
}}

/* ─────────────────────── TIPOGRAFIA — escala modular 1.2, base 13px ───────────────────────
   Escala harmônica (Major Second) usada em UI densa profissional (Linear/Notion/Atlassian):
       h1 18 · h2 16 · h3 14 · body 13 · caption 11 · micro 10
   Cada nível é perceptivelmente distinto do anterior sem criar "zoom".
   Seletores usam [data-testid="stMain"] / [data-testid="stHeading"] — Streamlit 1.56
   nao tem mais a classe .main (verificado em runtime: 0 elementos). */

.stApp h1, [data-testid="stHeading"] h1, [data-testid="stMain"] h1, [data-testid="stMain"] h1,
section[data-testid="stMain"] h1 {{
    color: {t['text_strong']} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    line-height: 1.25;
    letter-spacing: -0.02em;
    margin: 0 0 0.4rem 0 !important;
}}

.stApp h2, [data-testid="stHeading"] h2, [data-testid="stMain"] h2, [data-testid="stMain"] h2,
section[data-testid="stMain"] h2 {{
    color: {t['text_strong']} !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    line-height: 1.3;
    letter-spacing: -0.01em;
    margin: 0.8rem 0 0.35rem 0 !important;
}}

.stApp h3, [data-testid="stHeading"] h3, [data-testid="stMain"] h3, [data-testid="stMain"] h3,
section[data-testid="stMain"] h3 {{
    color: {t['text']} !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    line-height: 1.35;
    letter-spacing: -0.005em;
    margin: 0.6rem 0 0.3rem 0 !important;
}}

.stApp h4, .stApp h5, .stApp h6, [data-testid="stMain"] h4, [data-testid="stMain"] h5, [data-testid="stMain"] h6 {{
    color: {t['text']} !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    margin: 0.45rem 0 0.25rem 0 !important;
}}

.stApp p, .stApp li, .stApp .stMarkdown,
[data-testid="stMain"] p, [data-testid="stMain"] li, [data-testid="stMain"] .stMarkdown,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {{
    color: {t['text']};
    font-size: 13px !important;
    line-height: 1.5;
}}

[data-testid="stMain"] a, .stApp a {{
    color: {t['brand']};
    text-decoration: none;
    font-weight: 500;
}}
[data-testid="stMain"] a:hover, .stApp a:hover {{
    text-decoration: underline;
}}

[data-testid="stMain"] code, .stApp code {{
    font-family: 'JetBrains Mono', 'Consolas', monospace !important;
    font-size: 12px !important;
    background: {t['surface_alt']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 4px !important;
    padding: 1px 5px !important;
    color: {t['text_strong']} !important;
}}

[data-testid="stMain"] [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"],
[data-testid="stMain"] .stCaption {{
    color: {t['text_muted']} !important;
    font-size: 11px !important;
    font-weight: 400 !important;
    line-height: 1.45;
}}

/* ─────────────────────────── SIDEBAR (dark) ─────────────────────────── */
section[data-testid="stSidebar"] {{
    background: {t['sb_bg']} !important;
    border-right: 1px solid {t['sb_border']};
}}

section[data-testid="stSidebar"] > div {{
    background: {t['sb_bg']} !important;
    padding-top: 1rem;
}}

/* Todos os textos da sidebar — branco off */
section[data-testid="stSidebar"] *:not(svg):not(path):not(circle):not(rect) {{
    color: {t['sb_text']} !important;
}}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {{
    color: {t['sb_text']} !important;
    font-weight: 600 !important;
    border-bottom: none !important;
}}

/* Nav de páginas — links */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {{
    padding-left: 0 !important;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li {{
    list-style: none !important;
    margin: 2px 0 !important;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li a {{
    color: #CBD5E1 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    border-radius: 7px !important;
    padding: 6px 11px 6px 26px !important;   /* recuo: itens "dentro" do grupo */
    display: block;
    transition: all 0.15s ease;
    text-decoration: none !important;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li a:hover {{
    background-color: {t['sb_surface']} !important;
}}

/* Item ativo (página atual) — pílula com brilho laranja suave */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li[aria-current="page"] a,
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li.active a {{
    background-color: rgba(192, 86, 33, 0.16) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-left: 3px solid {t['brand']} !important;
    border-radius: 0 8px 8px 0 !important;
    padding-left: 23px !important;   /* 23 + 3px da barra = 26, alinha c/ os itens recuados */
}}

/* Ícones dos itens do menu: discretos (cinza); o do item ATIVO fica laranja */
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] {{
    color: {t['sb_text_muted']} !important;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li[aria-current="page"] a [data-testid="stIconMaterial"] {{
    color: {t['brand']} !important;
}}

/* Títulos de grupo do menu (Operação do dia, Sugestão, ...) — hierarquia:
   risquinho de divisão acima + rótulo miúdo maiúsculo, recuado MENOS que os
   itens (que ficam a 26px) pra os itens parecerem "dentro" do grupo. */
section[data-testid="stSidebar"] [data-testid="stNavSectionHeader"] {{
    color: {t['sb_text_muted']} !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    margin: 14px 6px 4px 6px !important;
    padding: 11px 6px 0 6px !important;
    border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
}}

/* Logo no topo da sidebar — respiro */
section[data-testid="stSidebar"] [data-testid="stLogo"] {{
    margin: 4px 12px 10px !important;
}}

/* ─────────── MENU PRÓPRIO (st.page_link) — sempre aberto, por grupo ───────────
   Substitui o menu automático (que recolhe grupos). Cada grupo = título com
   risquinho de divisão; cada item = um st.page_link recuado pra "dentro" do grupo.
   Degradação segura: se alguma cor não pegar, o texto continua branco/legível. */
section[data-testid="stSidebar"] .navgrp {{
    color: {t['sb_text_muted']} !important;
    font-size: 10px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.07em;
    margin: 14px 6px 4px 6px; padding: 11px 6px 0 6px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] {{ margin: 1px 0 !important; }}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {{
    color: #CBD5E1 !important;
    border-radius: 7px !important;
    padding: 6px 11px 6px 22px !important;   /* recuo: item "dentro" do grupo */
    transition: all 0.15s ease;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{
    background-color: {t['sb_surface']} !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a p {{
    color: inherit !important; font-size: 12px !important; font-weight: 500 !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] [data-testid="stIconMaterial"] {{
    color: {t['sb_text_muted']} !important;
}}
/* Item ATIVO — pílula com brilho laranja (página atual via aria-current) */
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {{
    background-color: rgba(192, 86, 33, 0.16) !important;
    border-left: 3px solid {t['brand']} !important;
    border-radius: 0 8px 8px 0 !important;
    padding-left: 19px !important;           /* 19 + 3px da barra = 22, alinha c/ os demais */
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] p {{
    color: #FFFFFF !important; font-weight: 600 !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] [data-testid="stIconMaterial"] {{
    color: {t['brand']} !important;
}}

/* Botões na sidebar = SEMPRE laranja brand com texto branco */
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] button[kind="secondary"],
section[data-testid="stSidebar"] button[kind="primary"] {{
    background: {t['brand']} !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    padding: 5px 10px !important;
    border-radius: 4px !important;
    width: 100% !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    transition: background-color 0.15s;
}}

section[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] button[kind="secondary"]:hover,
section[data-testid="stSidebar"] button[kind="primary"]:hover {{
    background: {t['brand_hover']} !important;
    color: #FFFFFF !important;
}}

/* Todo conteúdo interno do botão sidebar = branco */
section[data-testid="stSidebar"] .stButton > button *,
section[data-testid="stSidebar"] button[kind="secondary"] *,
section[data-testid="stSidebar"] button[kind="primary"] * {{
    color: #FFFFFF !important;
}}

/* Popover button (⋮ ao lado de cada folha) — dimensionado pra ser clicável */
section[data-testid="stSidebar"] button[kind="popover"],
section[data-testid="stSidebar"] [data-testid*="opover"] button,
section[data-testid="stSidebar"] button[aria-haspopup="dialog"] {{
    background: {t['sb_surface_2']} !important;
    color: {t['sb_text']} !important;
    border: 1px solid {t['sb_surface_2']} !important;
    min-width: 34px !important;
    min-height: 32px !important;
    font-size: 16px !important;
    line-height: 1 !important;
    padding: 2px 6px !important;
    border-radius: 5px !important;
}}

section[data-testid="stSidebar"] button[kind="popover"]:hover,
section[data-testid="stSidebar"] [data-testid*="opover"] button:hover,
section[data-testid="stSidebar"] button[aria-haspopup="dialog"]:hover {{
    background: {t['brand']} !important;
    border-color: {t['brand']} !important;
}}

section[data-testid="stSidebar"] button[kind="popover"] *,
section[data-testid="stSidebar"] [data-testid*="opover"] button *,
section[data-testid="stSidebar"] button[aria-haspopup="dialog"] * {{
    color: {t['sb_text']} !important;
    font-size: 16px !important;
}}

section[data-testid="stSidebar"] button[kind="popover"] svg,
section[data-testid="stSidebar"] [data-testid*="opover"] button svg,
section[data-testid="stSidebar"] button[aria-haspopup="dialog"] svg {{
    width: 17px !important;
    height: 17px !important;
}}

/* Expanders na sidebar */
section[data-testid="stSidebar"] [data-testid="stExpander"] {{
    background: {t['sb_surface']} !important;
    border: 1px solid {t['sb_surface_2']} !important;
    border-radius: 6px !important;
    margin: 6px 0 !important;
}}

section[data-testid="stSidebar"] [data-testid="stExpander"] summary,
section[data-testid="stSidebar"] [data-testid="stExpander"] details > summary {{
    color: {t['sb_text']} !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    background: transparent !important;
    padding: 6px 10px !important;
}}

section[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {{
    background: {t['sb_surface_2']} !important;
}}

/* Inputs / Date / Select na sidebar */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: {t['sb_surface']} !important;
    color: {t['sb_text']} !important;
    border: 1px solid {t['sb_surface_2']} !important;
    border-radius: 6px !important;
}}

section[data-testid="stSidebar"] input:focus {{
    border-color: {t['brand']} !important;
    box-shadow: 0 0 0 2px rgba(192, 86, 33, 0.3) !important;
}}

section[data-testid="stSidebar"] hr {{
    border-color: {t['sb_border']} !important;
    margin: 12px 0 !important;
    opacity: 0.5;
}}

/* Caption na sidebar */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] .stCaption {{
    color: {t['sb_text_muted']} !important;
    font-size: 12px !important;
}}

/* ─────────────────────────── MÉTRICAS ─────────────────────────── */
[data-testid="stMain"] [data-testid="metric-container"],
.stApp [data-testid="metric-container"],
.stApp [data-testid="stMetric"] {{
    background: {t['page']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 5px 9px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}}

[data-testid="stMain"] [data-testid="metric-container"] label,
.stApp [data-testid="stMetric"] label {{
    color: {t['text_muted']} !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 1px;
}}

[data-testid="stMain"] [data-testid="metric-container"] [data-testid="stMetricValue"],
.stApp [data-testid="stMetricValue"] {{
    color: {t['text_strong']} !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    line-height: 1.2;
}}

[data-testid="stMain"] [data-testid="metric-container"] [data-testid="stMetricDelta"],
.stApp [data-testid="stMetricDelta"] {{
    font-size: 11px !important;
}}

/* ─────────────────────────── BOTÕES (conteúdo principal) ─────────────────────────── */
[data-testid="stMain"] .stButton > button {{
    background: {t['page']} !important;
    color: {t['text']} !important;
    border: 1px solid {t['border_strong']} !important;
    font-weight: 500 !important;
    font-size: 12px !important;
    padding: 5px 11px !important;
    border-radius: 5px !important;
    transition: all 0.15s;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}}

[data-testid="stMain"] .stButton > button:hover {{
    background: {t['surface']} !important;
    border-color: {t['brand']} !important;
    color: {t['text_strong']} !important;
}}

[data-testid="stMain"] .stButton > button[kind="primary"] {{
    background: {t['brand']} !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 600 !important;
    padding: 6px 14px !important;
    box-shadow: 0 1px 2px rgba(192, 86, 33, 0.2);
}}

[data-testid="stMain"] .stButton > button[kind="primary"]:hover {{
    background: {t['brand_hover']} !important;
    color: #FFFFFF !important;
}}

/* ─────────────────────────── INPUTS ─────────────────────────── */
[data-testid="stMain"] .stTextInput input,
[data-testid="stMain"] .stNumberInput input,
[data-testid="stMain"] .stTextArea textarea,
[data-testid="stMain"] .stDateInput input {{
    border: 1px solid {t['border']} !important;
    border-radius: 5px !important;
    font-size: 12px !important;
    font-family: 'Inter', sans-serif !important;
    color: {t['text']} !important;
    background: {t['page']} !important;
    padding: 3px 7px !important;
    min-height: 26px !important;
}}

[data-testid="stMain"] .stSelectbox > div > div {{
    border: 1px solid {t['border']} !important;
    border-radius: 5px !important;
    font-size: 12px !important;
    color: {t['text']} !important;
    background: {t['page']} !important;
    min-height: 26px !important;
}}

/* Caixa de input limpa — o st.number_input injeta DOIS controles dentro
   da caixa, ambos escondidos aqui:
   1. steppers − + (stNumberInputStepUp/Down) — aparecem na caixa.
   2. botao "x" (svg aria "Clear value") — aparece quando a caixa tem
      numero; ocupava 24px e cortava o ultimo digito (54px sobravam pro
      texto em vez de 78px).
   O usuario digita o numero direto, sem botao nenhum. */
[data-testid="stMain"] [data-testid="stNumberInputStepUp"],
[data-testid="stMain"] [data-testid="stNumberInputStepDown"],
[data-testid="stMain"] [data-testid="stNumberInputContainer"] svg[aria-label="Clear value"] {{
    display: none !important;
}}
[data-testid="stMain"] [data-testid="stNumberInputContainer"] > div:has([data-testid="stNumberInputStepUp"]),
[data-testid="stMain"] [data-testid="stNumberInputContainer"] div:has(> svg[aria-label="Clear value"]) {{
    display: none !important;
}}

[data-testid="stMain"] .stTextInput input:focus,
[data-testid="stMain"] .stNumberInput input:focus,
[data-testid="stMain"] .stTextArea textarea:focus,
[data-testid="stMain"] .stDateInput input:focus {{
    border-color: {t['brand']} !important;
    box-shadow: 0 0 0 3px rgba(192, 86, 33, 0.1) !important;
    outline: none !important;
}}

[data-testid="stMain"] .stTextInput label,
[data-testid="stMain"] .stNumberInput label,
[data-testid="stMain"] .stSelectbox label,
[data-testid="stMain"] .stTextArea label,
[data-testid="stMain"] .stDateInput label,
[data-testid="stMain"] .stSlider label,
[data-testid="stMain"] .stCheckbox label,
[data-testid="stMain"] .stRadio label {{
    color: {t['text']} !important;
    font-size: 11px !important;
    font-weight: 500 !important;
}}

/* Slider */
[data-testid="stMain"] .stSlider [data-baseweb="slider"] [role="slider"] {{
    background: {t['brand']} !important;
}}

/* ─────────────────────────── TABS ─────────────────────────── */
[data-testid="stMain"] .stTabs [data-baseweb="tab-list"] {{
    background: transparent;
    border-bottom: 1px solid {t['border']};
    gap: 4px;
}}

[data-testid="stMain"] .stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {t['text_secondary']} !important;
    font-weight: 500;
    font-size: 12px !important;
    border-radius: 5px 5px 0 0;
    padding: 5px 11px !important;
}}

[data-testid="stMain"] .stTabs [data-baseweb="tab"][aria-selected="true"] {{
    background: transparent !important;
    color: {t['brand']} !important;
    font-weight: 600;
    border-bottom: 2px solid {t['brand']} !important;
}}

/* ─────────────────────────── EXPANDER (conteúdo principal) ─────────────────────────── */
[data-testid="stMain"] [data-testid="stExpander"] {{
    background: {t['page']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 7px !important;
    margin: 4px 0;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}}

[data-testid="stMain"] [data-testid="stExpander"] summary {{
    color: {t['text']} !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 5px 9px !important;
}}

[data-testid="stMain"] [data-testid="stExpander"] summary:hover {{
    background: {t['surface']} !important;
}}

/* ─────────────────────────── DATAFRAME ─────────────────────────── */
[data-testid="stMain"] .stDataFrame {{
    border: 1px solid {t['border']} !important;
    border-radius: 8px !important;
    overflow: hidden;
}}

/* ─────────────────────────── DIVIDER ─────────────────────────── */
[data-testid="stMain"] hr {{
    border-color: {t['border']} !important;
    margin: 1.5rem 0 !important;
}}

/* ─────────────────────────── ALERTS NATIVOS ─────────────────────────── */
[data-testid="stMain"] .stAlert {{
    border-radius: 8px !important;
    border-left-width: 4px !important;
    padding: 12px 16px !important;
    font-size: 14px;
}}

/* ─────────────────────────── COMPONENTES CUSTOMIZADOS ─────────────────────────── */
.card {{
    background: {t['page']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 20px 24px;
    margin: 12px 0;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    color: {t['text']};
}}

.card-info,
.card-success,
.card-warning,
.card-danger {{
    border-radius: 8px;
    border-left-width: 4px;
    border-left-style: solid;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 14px;
    line-height: 1.6;
}}

.card-info {{
    background: {t['info_bg']};
    border-left-color: {t['info']};
    color: {t['info_text']};
}}

.card-success {{
    background: {t['success_bg']};
    border-left-color: {t['success']};
    color: {t['success_text']};
}}

.card-warning {{
    background: {t['warning_bg']};
    border-left-color: {t['warning']};
    color: {t['warning_text']};
}}

.card-danger {{
    background: {t['danger_bg']};
    border-left-color: {t['danger']};
    color: {t['danger_text']};
}}

.badge {{
    display: inline-block;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}

/* ─────────────────────────── COMPATIBILIDADE LEGACY ─────────────────────────── */
/* Sobrescreve TODO CSS antigo das páginas pra contraste correto */

[data-testid="stMain"] .insight-card-master,
[data-testid="stMain"] .insight-card-warning,
[data-testid="stMain"] .insight-card-good,
[data-testid="stMain"] .insight-card-info,
[data-testid="stMain"] .didatica,
[data-testid="stMain"] .pergunta-eraldo,
[data-testid="stMain"] .anomaly-card,
[data-testid="stMain"] .alerta-alto,
[data-testid="stMain"] .alerta-medio,
[data-testid="stMain"] .alerta-ok,
[data-testid="stMain"] .limit-warning,
[data-testid="stMain"] .card-feature,
[data-testid="stMain"] .glossario-termo,
[data-testid="stMain"] .ref-box,
[data-testid="stMain"] .card-a, [data-testid="stMain"] .card-b, [data-testid="stMain"] .card-c,
[data-testid="stMain"] .resposta-claude,
[data-testid="stMain"] .pergunta-user,
[data-testid="stMain"] .faq-q, [data-testid="stMain"] .faq-a,
[data-testid="stMain"] .erro-card,
[data-testid="stMain"] .custo-info,
[data-testid="stMain"] .exemplo-pergunta,
[data-testid="stMain"] .card-funcionario,
[data-testid="stMain"] .status-box-new,
[data-testid="stMain"] .status-box-edit {{
    background: {t['page']} !important;
    background-image: none !important;
    border: 1px solid {t['border']} !important;
    border-radius: 8px !important;
    padding: 14px 18px !important;
    margin: 10px 0 !important;
    color: {t['text']} !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}}

/* Cards de SUCESSO */
[data-testid="stMain"] .insight-card-good,
[data-testid="stMain"] .alerta-ok,
[data-testid="stMain"] .card-a,
[data-testid="stMain"] .status-box-new {{
    background: {t['success_bg']} !important;
    border-left: 4px solid {t['success']} !important;
    color: {t['success_text']} !important;
}}

[data-testid="stMain"] .insight-card-good *,
[data-testid="stMain"] .alerta-ok *,
[data-testid="stMain"] .card-a *,
[data-testid="stMain"] .status-box-new * {{
    color: {t['success_text']} !important;
}}

/* Cards de AVISO */
[data-testid="stMain"] .insight-card-warning,
[data-testid="stMain"] .alerta-medio,
[data-testid="stMain"] .card-b,
[data-testid="stMain"] .limit-warning,
[data-testid="stMain"] .didatica,
[data-testid="stMain"] .pergunta-eraldo,
[data-testid="stMain"] .glossario-termo,
[data-testid="stMain"] .faq-q,
[data-testid="stMain"] .status-box-edit {{
    background: {t['warning_bg']} !important;
    border-left: 4px solid {t['warning']} !important;
    color: {t['warning_text']} !important;
}}

[data-testid="stMain"] .insight-card-warning *,
[data-testid="stMain"] .alerta-medio *,
[data-testid="stMain"] .card-b *,
[data-testid="stMain"] .limit-warning *,
[data-testid="stMain"] .didatica *,
[data-testid="stMain"] .pergunta-eraldo *,
[data-testid="stMain"] .glossario-termo *,
[data-testid="stMain"] .faq-q *,
[data-testid="stMain"] .status-box-edit * {{
    color: {t['warning_text']} !important;
}}

/* Cards de INFO */
[data-testid="stMain"] .insight-card-info,
[data-testid="stMain"] .insight-card-master,
[data-testid="stMain"] .card-feature,
[data-testid="stMain"] .ref-box,
[data-testid="stMain"] .custo-info,
[data-testid="stMain"] .exemplo-pergunta {{
    background: {t['info_bg']} !important;
    border-left: 4px solid {t['info']} !important;
    color: {t['info_text']} !important;
}}

[data-testid="stMain"] .insight-card-info *,
[data-testid="stMain"] .insight-card-master *,
[data-testid="stMain"] .card-feature *,
[data-testid="stMain"] .ref-box *,
[data-testid="stMain"] .custo-info *,
[data-testid="stMain"] .exemplo-pergunta * {{
    color: {t['info_text']} !important;
}}

/* Cards de PERIGO */
[data-testid="stMain"] .anomaly-card,
[data-testid="stMain"] .alerta-alto,
[data-testid="stMain"] .card-c,
[data-testid="stMain"] .erro-card {{
    background: {t['danger_bg']} !important;
    border-left: 4px solid {t['danger']} !important;
    color: {t['danger_text']} !important;
}}

[data-testid="stMain"] .anomaly-card *,
[data-testid="stMain"] .alerta-alto *,
[data-testid="stMain"] .card-c *,
[data-testid="stMain"] .erro-card * {{
    color: {t['danger_text']} !important;
}}

/* Resposta do Claude — usa BRAND */
[data-testid="stMain"] .resposta-claude {{
    background: {t['brand_subtle']} !important;
    border-left: 4px solid {t['brand']} !important;
    color: {t['text_strong']} !important;
}}

[data-testid="stMain"] .resposta-claude * {{
    color: {t['text_strong']} !important;
}}

/* Pergunta do usuário — neutro */
[data-testid="stMain"] .pergunta-user,
[data-testid="stMain"] .card-funcionario {{
    background: {t['surface']} !important;
    border-left: 4px solid {t['border_strong']} !important;
    color: {t['text']} !important;
}}

/* FAQ-answer (faq-a) — sem fundo, só texto */
[data-testid="stMain"] .faq-a {{
    background: transparent !important;
    border: none !important;
    padding: 4px 18px !important;
    margin: 4px 0 12px 0 !important;
    color: {t['text']} !important;
}}

/* Badges */
[data-testid="stMain"] .badge-ativo {{
    background: {t['success_bg']} !important;
    color: {t['success']} !important;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid {t['success']}33;
}}

[data-testid="stMain"] .badge-inativo {{
    background: {t['surface_alt']} !important;
    color: {t['text_muted']} !important;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid {t['border_strong']};
}}

/* ─────────────────────── INÍCIO / PEÇAS REUTILIZÁVEIS ─────────────────────── */
.grupo-atalho {{
    font-size: 10px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.06em; color: {t['text_muted']};
    margin: 0.7rem 0 0.4rem 0;
}}

/* Cartão de atalho = st.container(border) que contém um page_link */
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPageLink"]) {{
    border-radius: 10px !important;
    border-color: {t['border']} !important;
    transition: border-color 0.15s, box-shadow 0.15s;
}}
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPageLink"]):hover {{
    border-color: {t['brand']} !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transform: translateY(-1px);
}}
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPageLink"]) [data-testid="stPageLink"] a {{
    padding: 2px 0 !important;
    background: transparent !important;
}}
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPageLink"]) [data-testid="stPageLink"] p {{
    font-weight: 600 !important; font-size: 13px !important; color: {t['text']} !important;
}}
[data-testid="stMain"] [data-testid="stPageLink"] [data-testid="stIconMaterial"] {{
    color: {t['brand']} !important;
}}
.atalho-desc {{
    color: {t['text_muted']} !important; font-size: 11.5px !important;
    margin: 2px 0 0 0 !important; line-height: 1.4;
}}

/* Mini-cartão de status (ex.: folha de hoje na Início) */
.mc-status {{
    background: {t['surface']}; border: 1px solid {t['border']};
    border-radius: 6px; padding: 8px 11px;
}}
.mc-status-label {{
    color: {t['text_muted']}; font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px;
}}
.status-pill {{
    display: inline-block; font-size: 12px; font-weight: 600;
    padding: 3px 11px; border-radius: 999px;
}}

/* ─────────────────────────── ESCONDER ELEMENTOS DESNECESSÁRIOS ─────────────────────────── */
footer {{ visibility: hidden; height: 0; }}
#MainMenu {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* ─────────── TÍTULOS DE GRUPO DO MENU (botões-sanfona) ───────────
   No FIM do tema de propósito: sobrescreve o botão laranja padrão da sidebar
   SÓ nos títulos de grupo (key=navgrp_*). Ficam planos, maiúsculos, com risquinho
   de divisão e a setinha (chevron). Degradação segura: se não pegar, vira botão. */
section[data-testid="stSidebar"] [class*="st-key-navgrp_"] button {{
    background: transparent !important;
    color: {t['sb_text_muted']} !important;
    border: none !important;
    border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
    text-align: left !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    padding: 9px 8px !important;
    margin-top: 6px !important;
}}
section[data-testid="stSidebar"] [class*="st-key-navgrp_"] button:hover {{
    background: {t['sb_surface']} !important;
    color: {t['sb_text']} !important;
}}
section[data-testid="stSidebar"] [class*="st-key-navgrp_"] button p {{
    color: inherit !important; font-weight: 600 !important;
}}
section[data-testid="stSidebar"] [class*="st-key-navgrp_"] button [data-testid="stIconMaterial"] {{
    color: {t['sb_text_muted']} !important;
    font-size: 16px !important;
}}

</style>
""", unsafe_allow_html=True)
