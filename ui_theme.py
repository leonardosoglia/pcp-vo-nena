"""
ui_theme.py — Tema visual centralizado do PCP Vó Nena.

Define a identidade visual profissional do sistema:
- Fonte: Inter (padrão SaaS moderno — Vercel, Linear, Notion)
- Paleta clean: branco/cinza neutros como base, laranja Vó Nena apenas como accent
- Sem gradientes coloridos, sem emojis decorativos espalhados
- Contraste WCAG AA garantido (texto escuro em fundos claros, claro em escuros)

Uso em cada página:
    from ui_theme import aplicar_tema
    aplicar_tema()  # após st.set_page_config

Decisões de design (19/05/2026 — pedido do Leonardo "quero cara profissional"):
- Inter > Sora (Inter é mais "corporativa", Sora era mais "playful")
- Laranja apenas em h1, botões primários e accents (não como background de cards)
- Cards: branco com border #E5E7EB (cinza claro), zero gradiente
- Tipografia hierárquica clara: h1 24px, h2 20px, h3 16px, body 14px
"""
import streamlit as st


# ─── Paleta oficial ──────────────────────────────────────────────────────────
COLORS = {
    # Accents (uso restrito — h1, botões primários, destaques)
    "primary":        "#C05621",  # Laranja Vó Nena
    "primary_dark":   "#7B341E",  # Laranja escuro (hover, h2)
    "primary_subtle": "#FFF8F2",  # Laranja muito claro (background sutil)

    # Base neutra (estrutura)
    "bg":             "#FFFFFF",  # Background principal
    "surface":        "#F9FAFB",  # Background secundário (sidebar, cards)
    "surface_alt":    "#F3F4F6",  # Background terciário (zebra, divisores)
    "border":         "#E5E7EB",  # Borda padrão
    "border_strong":  "#D1D5DB",  # Borda mais marcada

    # Texto (contraste WCAG AA)
    "text":           "#111827",  # Texto principal (cinza quase preto)
    "text_secondary": "#4B5563",  # Texto secundário (cinza médio)
    "text_muted":     "#6B7280",  # Texto desbotado (legendas, helpers)
    "text_on_dark":   "#F9FAFB",  # Texto em fundos escuros (sidebar)

    # Status semânticos (uso pontual)
    "success":        "#059669",
    "warning":        "#D97706",
    "danger":         "#DC2626",
    "info":           "#2563EB",
}


def aplicar_tema():
    """Injeta CSS global na página. Chame após st.set_page_config()."""
    st.markdown(f"""
<style>
    /* ═══════════════════════════════════════════════════════════════════
       FONT — Inter (Google Fonts)
       Pesos: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
       ═══════════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stTextInput, .stSelectbox,
    .stNumberInput, .stTextArea, .stRadio, .stCheckbox, .stButton, .stDataFrame {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        color: {COLORS["text"]};
    }}

    /* ═══════════════════════════════════════════════════════════════════
       LAYOUT GERAL
       ═══════════════════════════════════════════════════════════════════ */
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }}

    body {{
        background-color: {COLORS["bg"]};
    }}

    /* ═══════════════════════════════════════════════════════════════════
       TIPOGRAFIA
       ═══════════════════════════════════════════════════════════════════ */
    h1 {{
        color: {COLORS["primary"]};
        font-weight: 700;
        font-size: 26px;
        line-height: 1.2;
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }}

    h2 {{
        color: {COLORS["primary_dark"]};
        font-weight: 600;
        font-size: 20px;
        line-height: 1.3;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }}

    h3 {{
        color: {COLORS["text"]};
        font-weight: 600;
        font-size: 16px;
        line-height: 1.4;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }}

    h4, h5, h6 {{
        color: {COLORS["text"]};
        font-weight: 600;
    }}

    p, li {{
        color: {COLORS["text"]};
        line-height: 1.6;
    }}

    /* Caption do Streamlit (st.caption) */
    .stCaption, [data-testid="stCaptionContainer"] {{
        color: {COLORS["text_muted"]} !important;
        font-size: 13px !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════
       SIDEBAR — fundo escuro elegante (não preto puro)
       ═══════════════════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {{
        background-color: #1F2937;
        border-right: 1px solid #374151;
    }}

    section[data-testid="stSidebar"] * {{
        color: {COLORS["text_on_dark"]} !important;
    }}

    section[data-testid="stSidebar"] a {{
        color: #FED7AA !important;
    }}

    /* Botões na sidebar */
    section[data-testid="stSidebar"] .stButton > button {{
        background-color: {COLORS["primary"]};
        color: white !important;
        border: none;
        font-weight: 600;
        font-size: 13px;
        width: 100%;
        padding: 8px 12px;
        border-radius: 6px;
        transition: background-color 0.15s;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: {COLORS["primary_dark"]};
    }}

    /* ═══════════════════════════════════════════════════════════════════
       MÉTRICAS (st.metric)
       ═══════════════════════════════════════════════════════════════════ */
    [data-testid="metric-container"] {{
        background: {COLORS["bg"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }}
    [data-testid="metric-container"] label {{
        color: {COLORS["text_secondary"]} !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    [data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: {COLORS["text"]} !important;
        font-size: 24px !important;
        font-weight: 700;
    }}

    /* ═══════════════════════════════════════════════════════════════════
       BOTÕES PRIMÁRIOS (botões fora da sidebar)
       ═══════════════════════════════════════════════════════════════════ */
    .stButton > button {{
        background-color: {COLORS["bg"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border_strong"]};
        font-weight: 500;
        font-size: 13px;
        padding: 6px 14px;
        border-radius: 6px;
        transition: all 0.15s;
    }}
    .stButton > button:hover {{
        background-color: {COLORS["surface"]};
        border-color: {COLORS["primary"]};
    }}
    .stButton > button[kind="primary"] {{
        background-color: {COLORS["primary"]};
        color: white;
        border: none;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: {COLORS["primary_dark"]};
    }}

    /* ═══════════════════════════════════════════════════════════════════
       INPUTS
       ═══════════════════════════════════════════════════════════════════ */
    .stTextInput input, .stNumberInput input, .stTextArea textarea,
    .stSelectbox > div > div {{
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        color: {COLORS["text"]} !important;
    }}
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
        border-color: {COLORS["primary"]} !important;
        box-shadow: 0 0 0 3px {COLORS["primary"]}1F !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════
       EXPANDER
       ═══════════════════════════════════════════════════════════════════ */
    .streamlit-expanderHeader {{
        background-color: {COLORS["surface"]};
        border-radius: 6px;
        font-weight: 500;
    }}

    /* ═══════════════════════════════════════════════════════════════════
       TABELA / DATAFRAME
       ═══════════════════════════════════════════════════════════════════ */
    .stDataFrame {{
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
    }}

    /* ═══════════════════════════════════════════════════════════════════
       DIVIDER
       ═══════════════════════════════════════════════════════════════════ */
    hr {{
        border-color: {COLORS["border"]};
        margin: 1.5rem 0;
    }}

    /* ═══════════════════════════════════════════════════════════════════
       CARDS CUSTOMIZADOS (usar via classes nas páginas)
       Atenção: classes legacy (.insight-card-*, .anomaly-card, .card-feature)
       são neutralizadas aqui pra desencorajar uso. Usar .card padrão.
       ═══════════════════════════════════════════════════════════════════ */
    .card {{
        background: {COLORS["bg"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 16px 20px;
        margin: 8px 0;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }}
    .card-title {{
        color: {COLORS["text"]};
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 4px;
    }}
    .card-subtitle {{
        color: {COLORS["text_muted"]};
        font-size: 12px;
        margin-bottom: 10px;
    }}

    .card-success {{
        background: #ECFDF5;
        border-left: 3px solid {COLORS["success"]};
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #064E3B;
    }}
    .card-warning {{
        background: #FFFBEB;
        border-left: 3px solid {COLORS["warning"]};
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #78350F;
    }}
    .card-danger {{
        background: #FEF2F2;
        border-left: 3px solid {COLORS["danger"]};
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #7F1D1D;
    }}
    .card-info {{
        background: #EFF6FF;
        border-left: 3px solid {COLORS["info"]};
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #1E3A8A;
    }}

    /* Compatibilidade: classes antigas mapeadas pras novas */
    .insight-card-master, .insight-card-warning, .insight-card-good,
    .insight-card-info, .pergunta-eraldo, .anomaly-card, .didatica,
    .alerta-alto, .alerta-medio, .alerta-ok, .limit-warning,
    .card-feature, .glossario-termo, .ref-box {{
        background: {COLORS["bg"]} !important;
        border: 1px solid {COLORS["border"]} !important;
        border-left: 3px solid {COLORS["primary"]} !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
        margin: 8px 0 !important;
        color: {COLORS["text"]} !important;
        background-image: none !important;
    }}

    .card-a, .card-b, .card-c {{
        background-image: none !important;
        background-color: {COLORS["bg"]} !important;
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 8px !important;
        padding: 16px !important;
        color: {COLORS["text"]} !important;
    }}
    .card-a {{ border-left: 4px solid {COLORS["success"]} !important; }}
    .card-b {{ border-left: 4px solid {COLORS["warning"]} !important; }}
    .card-c {{ border-left: 4px solid {COLORS["danger"]} !important; }}

    /* Resposta do Claude */
    .resposta-claude {{
        background: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-left: 3px solid {COLORS["primary"]};
        border-radius: 6px;
        padding: 14px 18px;
        margin: 10px 0;
        color: {COLORS["text"]};
        line-height: 1.6;
    }}
    .pergunta-user {{
        background: {COLORS["surface_alt"]};
        border-radius: 6px;
        padding: 10px 14px;
        margin: 8px 0;
        color: {COLORS["text"]};
    }}
</style>
""", unsafe_allow_html=True)
