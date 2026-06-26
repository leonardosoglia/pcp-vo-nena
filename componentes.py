"""
componentes.py — Peças visuais reutilizáveis do PCP Vó Nena.

Construídas sobre o `ui_theme` (que injeta o CSS global). As telas importam daqui
para terem todas a mesma cara — sem cada uma reinventar cartão/cabeçalho/aviso.
É o "kit de peças" da reforma visual (Etapa 1).

Primeiras peças:
- `cartao_atalho()` — atalho clicável em forma de cartão (ícone + título + 1 linha).
- `status_badge()`  — mini-cartão de status com um selo colorido (pílula).
"""
import streamlit as st


def cartao_atalho(page, titulo: str, descricao: str, icone: str = ""):
    """Atalho clicável em forma de cartão: ícone + título (link) + 1 linha de contexto.

    `page` é o caminho da página (ex.: "pages/1_Painel.py"). O clique navega de
    verdade (usa o st.page_link nativo, que respeita a navegação do app).
    """
    with st.container(border=True):
        st.page_link(page, label=titulo, icon=icone or None)
        st.markdown(f"<p class='atalho-desc'>{descricao}</p>", unsafe_allow_html=True)


def _esc(v) -> str:
    """Escapa o mínimo pra não quebrar o HTML da tabela."""
    return (str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def tabela(df, altura_max: int | None = None):
    """Quadro padrão do sistema — tabela limpa (cabeçalho cinza-claro, linhas finas,
    1ª coluna em destaque), igual ao mockup aprovado.

    Substitui o `st.dataframe` (grid interativo) nos quadros de apresentação.
    `df` é um DataFrame do pandas. `altura_max` (px) liga a rolagem em quadros
    grandes, mantendo o cabeçalho fixo no topo.
    """
    ths = "".join(f"<th>{_esc(c)}</th>" for c in df.columns)
    linhas = []
    for _, row in df.iterrows():
        tds = "".join(f"<td>{_esc(v)}</td>" for v in row)
        linhas.append(f"<tr>{tds}</tr>")
    estilo = f' style="max-height:{int(altura_max)}px;overflow:auto"' if altura_max else ""
    st.markdown(
        f'<div class="vn-tbl-wrap"{estilo}><table class="vn-tbl">'
        f'<thead><tr>{ths}</tr></thead><tbody>{"".join(linhas)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def status_badge(label: str, texto: str, tipo: str = "info"):
    """Mini-cartão de status: rótulo em cima + selo colorido (pílula) embaixo.

    `tipo`: 'success' (verde) · 'warning' (âmbar) · 'info' (azul) · 'danger' (vermelho).
    """
    cores = {
        "success": ("#F0FDF4", "#14532D", "#16A34A"),
        "warning": ("#FEFCE8", "#713F12", "#CA8A04"),
        "info":    ("#EFF6FF", "#1E3A8A", "#2563EB"),
        "danger":  ("#FEF2F2", "#7F1D1D", "#DC2626"),
    }
    bg, fg, borda = cores.get(tipo, cores["info"])
    st.markdown(
        f"""<div class="mc-status">
  <div class="mc-status-label">{label}</div>
  <div><span class="status-pill" style="background:{bg};color:{fg};border:1px solid {borda}55">{texto}</span></div>
</div>""",
        unsafe_allow_html=True,
    )
