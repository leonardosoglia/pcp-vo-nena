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

.block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}}

/* ─────────────────────────── TIPOGRAFIA ─────────────────────────── */
.main h1 {{
    color: {t['text_strong']} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    line-height: 1.2;
    letter-spacing: -0.02em;
    margin: 0 0 0.5rem 0 !important;
}}

.main h2 {{
    color: {t['text_strong']} !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    line-height: 1.3;
    letter-spacing: -0.01em;
    margin: 1.5rem 0 0.5rem 0 !important;
}}

.main h3 {{
    color: {t['text']} !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    line-height: 1.4;
    margin: 1rem 0 0.4rem 0 !important;
}}

.main h4, .main h5, .main h6 {{
    color: {t['text']} !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    margin: 0.75rem 0 0.4rem 0 !important;
}}

.main p, .main li, .main .stMarkdown {{
    color: {t['text']};
    font-size: 13px;
    line-height: 1.55;
}}

.main a {{
    color: {t['brand']};
    text-decoration: none;
    font-weight: 500;
}}
.main a:hover {{
    text-decoration: underline;
}}

.main code {{
    font-family: 'JetBrains Mono', 'Consolas', monospace !important;
    font-size: 13px !important;
    background: {t['surface_alt']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 4px !important;
    padding: 1px 6px !important;
    color: {t['text_strong']} !important;
}}

.main [data-testid="stCaptionContainer"],
.main .stCaption {{
    color: {t['text_muted']} !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    line-height: 1.5;
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
    color: {t['sb_text']} !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    padding: 8px 14px !important;
    display: block;
    transition: background-color 0.15s;
    text-decoration: none !important;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li a:hover {{
    background-color: {t['sb_surface']} !important;
}}

/* Item ativo (página atual) */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li[aria-current="page"] a,
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li.active a {{
    background-color: {t['sb_surface']} !important;
    color: {t['sb_text']} !important;
    font-weight: 600 !important;
    border-left: 3px solid {t['brand']} !important;
}}

/* Botões na sidebar = SEMPRE laranja brand com texto branco */
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] button[kind="secondary"],
section[data-testid="stSidebar"] button[kind="primary"] {{
    background: {t['brand']} !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 14px !important;
    border-radius: 6px !important;
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

/* Popover button (⋮ ao lado de cada folha) */
section[data-testid="stSidebar"] button[kind="popover"],
section[data-testid="stSidebar"] [data-testid*="opover"] button,
section[data-testid="stSidebar"] button[aria-haspopup="dialog"] {{
    background: {t['sb_surface_2']} !important;
    color: {t['sb_text']} !important;
    border: 1px solid {t['sb_surface_2']} !important;
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
    font-size: 13px !important;
    background: transparent !important;
    padding: 8px 12px !important;
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
.main [data-testid="metric-container"] {{
    background: {t['page']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    transition: box-shadow 0.15s;
}}

.main [data-testid="metric-container"]:hover {{
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}}

.main [data-testid="metric-container"] label {{
    color: {t['text_muted']} !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 4px;
}}

.main [data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {t['text_strong']} !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    line-height: 1.2;
}}

.main [data-testid="metric-container"] [data-testid="stMetricDelta"] {{
    font-size: 13px !important;
}}

/* ─────────────────────────── BOTÕES (conteúdo principal) ─────────────────────────── */
.main .stButton > button {{
    background: {t['page']} !important;
    color: {t['text']} !important;
    border: 1px solid {t['border_strong']} !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 7px 14px !important;
    border-radius: 6px !important;
    transition: all 0.15s;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}}

.main .stButton > button:hover {{
    background: {t['surface']} !important;
    border-color: {t['brand']} !important;
    color: {t['text_strong']} !important;
}}

.main .stButton > button[kind="primary"] {{
    background: {t['brand']} !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
    box-shadow: 0 1px 2px rgba(192, 86, 33, 0.2);
}}

.main .stButton > button[kind="primary"]:hover {{
    background: {t['brand_hover']} !important;
    color: #FFFFFF !important;
}}

/* ─────────────────────────── INPUTS ─────────────────────────── */
.main .stTextInput input,
.main .stNumberInput input,
.main .stTextArea textarea,
.main .stDateInput input {{
    border: 1px solid {t['border']} !important;
    border-radius: 6px !important;
    font-size: 14px !important;
    font-family: 'Inter', sans-serif !important;
    color: {t['text']} !important;
    background: {t['page']} !important;
    padding: 8px 12px !important;
}}

.main .stSelectbox > div > div {{
    border: 1px solid {t['border']} !important;
    border-radius: 6px !important;
    font-size: 14px !important;
    color: {t['text']} !important;
    background: {t['page']} !important;
}}

.main .stTextInput input:focus,
.main .stNumberInput input:focus,
.main .stTextArea textarea:focus,
.main .stDateInput input:focus {{
    border-color: {t['brand']} !important;
    box-shadow: 0 0 0 3px rgba(192, 86, 33, 0.1) !important;
    outline: none !important;
}}

.main .stTextInput label,
.main .stNumberInput label,
.main .stSelectbox label,
.main .stTextArea label,
.main .stDateInput label,
.main .stSlider label,
.main .stCheckbox label,
.main .stRadio label {{
    color: {t['text']} !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}}

/* Slider */
.main .stSlider [data-baseweb="slider"] [role="slider"] {{
    background: {t['brand']} !important;
}}

/* ─────────────────────────── TABS ─────────────────────────── */
.main .stTabs [data-baseweb="tab-list"] {{
    background: transparent;
    border-bottom: 1px solid {t['border']};
    gap: 4px;
}}

.main .stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {t['text_secondary']} !important;
    font-weight: 500;
    border-radius: 6px 6px 0 0;
    padding: 8px 16px !important;
}}

.main .stTabs [data-baseweb="tab"][aria-selected="true"] {{
    background: transparent !important;
    color: {t['brand']} !important;
    font-weight: 600;
    border-bottom: 2px solid {t['brand']} !important;
}}

/* ─────────────────────────── EXPANDER (conteúdo principal) ─────────────────────────── */
.main [data-testid="stExpander"] {{
    background: {t['page']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 8px !important;
    margin: 6px 0;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}}

.main [data-testid="stExpander"] summary {{
    color: {t['text']} !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
}}

.main [data-testid="stExpander"] summary:hover {{
    background: {t['surface']} !important;
}}

/* ─────────────────────────── DATAFRAME ─────────────────────────── */
.main .stDataFrame {{
    border: 1px solid {t['border']} !important;
    border-radius: 8px !important;
    overflow: hidden;
}}

/* ─────────────────────────── DIVIDER ─────────────────────────── */
.main hr {{
    border-color: {t['border']} !important;
    margin: 1.5rem 0 !important;
}}

/* ─────────────────────────── ALERTS NATIVOS ─────────────────────────── */
.main .stAlert {{
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

.main .insight-card-master,
.main .insight-card-warning,
.main .insight-card-good,
.main .insight-card-info,
.main .didatica,
.main .pergunta-eraldo,
.main .anomaly-card,
.main .alerta-alto,
.main .alerta-medio,
.main .alerta-ok,
.main .limit-warning,
.main .card-feature,
.main .glossario-termo,
.main .ref-box,
.main .card-a, .main .card-b, .main .card-c,
.main .resposta-claude,
.main .pergunta-user,
.main .faq-q, .main .faq-a,
.main .erro-card,
.main .custo-info,
.main .exemplo-pergunta,
.main .card-funcionario,
.main .status-box-new,
.main .status-box-edit {{
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
.main .insight-card-good,
.main .alerta-ok,
.main .card-a,
.main .status-box-new {{
    background: {t['success_bg']} !important;
    border-left: 4px solid {t['success']} !important;
    color: {t['success_text']} !important;
}}

.main .insight-card-good *,
.main .alerta-ok *,
.main .card-a *,
.main .status-box-new * {{
    color: {t['success_text']} !important;
}}

/* Cards de AVISO */
.main .insight-card-warning,
.main .alerta-medio,
.main .card-b,
.main .limit-warning,
.main .didatica,
.main .pergunta-eraldo,
.main .glossario-termo,
.main .faq-q,
.main .status-box-edit {{
    background: {t['warning_bg']} !important;
    border-left: 4px solid {t['warning']} !important;
    color: {t['warning_text']} !important;
}}

.main .insight-card-warning *,
.main .alerta-medio *,
.main .card-b *,
.main .limit-warning *,
.main .didatica *,
.main .pergunta-eraldo *,
.main .glossario-termo *,
.main .faq-q *,
.main .status-box-edit * {{
    color: {t['warning_text']} !important;
}}

/* Cards de INFO */
.main .insight-card-info,
.main .insight-card-master,
.main .card-feature,
.main .ref-box,
.main .custo-info,
.main .exemplo-pergunta {{
    background: {t['info_bg']} !important;
    border-left: 4px solid {t['info']} !important;
    color: {t['info_text']} !important;
}}

.main .insight-card-info *,
.main .insight-card-master *,
.main .card-feature *,
.main .ref-box *,
.main .custo-info *,
.main .exemplo-pergunta * {{
    color: {t['info_text']} !important;
}}

/* Cards de PERIGO */
.main .anomaly-card,
.main .alerta-alto,
.main .card-c,
.main .erro-card {{
    background: {t['danger_bg']} !important;
    border-left: 4px solid {t['danger']} !important;
    color: {t['danger_text']} !important;
}}

.main .anomaly-card *,
.main .alerta-alto *,
.main .card-c *,
.main .erro-card * {{
    color: {t['danger_text']} !important;
}}

/* Resposta do Claude — usa BRAND */
.main .resposta-claude {{
    background: {t['brand_subtle']} !important;
    border-left: 4px solid {t['brand']} !important;
    color: {t['text_strong']} !important;
}}

.main .resposta-claude * {{
    color: {t['text_strong']} !important;
}}

/* Pergunta do usuário — neutro */
.main .pergunta-user,
.main .card-funcionario {{
    background: {t['surface']} !important;
    border-left: 4px solid {t['border_strong']} !important;
    color: {t['text']} !important;
}}

/* FAQ-answer (faq-a) — sem fundo, só texto */
.main .faq-a {{
    background: transparent !important;
    border: none !important;
    padding: 4px 18px !important;
    margin: 4px 0 12px 0 !important;
    color: {t['text']} !important;
}}

/* Badges */
.main .badge-ativo {{
    background: {t['success_bg']} !important;
    color: {t['success']} !important;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid {t['success']}33;
}}

.main .badge-inativo {{
    background: {t['surface_alt']} !important;
    color: {t['text_muted']} !important;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid {t['border_strong']};
}}

/* ─────────────────────────── ESCONDER ELEMENTOS DESNECESSÁRIOS ─────────────────────────── */
footer {{ visibility: hidden; height: 0; }}
#MainMenu {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}

</style>
""", unsafe_allow_html=True)
