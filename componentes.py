"""
componentes.py — Peças visuais reutilizáveis do PCP Vó Nena.

Construídas sobre o `ui_theme` (que injeta o CSS global). As telas importam daqui
para terem todas a mesma cara — sem cada uma reinventar cartão/cabeçalho/aviso.
É o "kit de peças" da reforma visual.

Peças:
- `cabecalho()`     — moldura de abertura de página (selo da seção + título + contexto).
- `rodape()`        — rodapé padrão (nome · versão · data/hora · nota da fonte).
- `tabela()`        — quadro padrão do sistema (com cor de célula, selos e nº à direita).
- `selo()`          — pílula colorida pra dentro de tabela (status).
- `cartao_atalho()` — atalho clicável em forma de cartão (ícone + título + 1 linha).
- `status_badge()`  — mini-cartão de status com um selo colorido (pílula).
"""
from datetime import datetime

import streamlit as st

# Identidade única do sistema — TODA tela mostra a mesma versão no rodapé.
# (Antes o Painel dizia v1.2 e o Lançamento v2.1 ao mesmo tempo.)
APP_NOME = "PCP Doces Vó Nena"
APP_VERSAO = "2.1"


def cabecalho(secao: str, titulo: str, contexto: str = "", direita: str = "",
              icone: str = "description"):
    """Moldura de abertura de página — ícone da seção (chip) + sobretítulo (seção)
    + título + 1 linha de contexto, com uma divisória fina embaixo (estilo painel
    executivo, aprovado pelo Leonardo em 01/07).

    `secao` = grupo do menu (ex.: "Vendas & resultado") · `titulo` = nome da tela ·
    `contexto` = 1 linha do que a tela faz (aceita <b> pontual) · `direita` = HTML
    curto opcional à direita (ex.: a data de hoje) · `icone` = nome do ícone Material
    (o MESMO do menu em app.py, ex.: "shopping_cart") — usa a fonte de ícones que o
    próprio Streamlit já carrega, então o ícone fica idêntico ao da barra lateral.
    """
    dir_html = f'<div class="vn-hdr-right">{direita}</div>' if direita else ""
    ctx_html = f'<div class="vn-hdr-sub">{contexto}</div>' if contexto else ""
    st.markdown(
        '<div class="vn-hdr"><div class="vn-hdr-main">'
        f'<div class="vn-hdr-chip"><span class="vn-hdr-ico">{_esc(icone)}</span></div>'
        f'<div><div class="vn-hdr-over">{_esc(secao)}</div>'
        f'<div class="vn-hdr-title">{_esc(titulo)}</div></div></div>'
        f'{dir_html}</div>{ctx_html}',
        unsafe_allow_html=True,
    )


def rodape(extra: str = ""):
    """Rodapé padrão de toda tela: nome · versão · data/hora · nota opcional
    (ex.: "fonte: SIGE (renova a cada 30 min)")."""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    extra_html = f" · {_esc(extra)}" if extra else ""
    st.markdown(
        f'<div class="vn-rodape"><span>{APP_NOME} · v{APP_VERSAO}</span>'
        f'<span>{agora}{extra_html}</span></div>',
        unsafe_allow_html=True,
    )


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


def tabela(df, altura_max: int | None = None, cor_celula=None, cols_direita=None,
           html_cols=None):
    """Quadro padrão do sistema — tabela limpa (cabeçalho cinza-claro, linhas finas,
    1ª coluna em destaque), igual ao mockup aprovado.

    Substitui o `st.dataframe` (grid interativo) nos quadros de apresentação.
    `df` é um DataFrame do pandas. `altura_max` (px) liga a rolagem em quadros
    grandes, mantendo o cabeçalho fixo no topo.

    `cor_celula` (opcional): função `(coluna, valor) -> estilo_css | None` que
    devolve o ESTILO CSS inline da célula (ex.: "background-color:...;color:...;
    font-weight:600") pra destacar sem perder o visual limpo — ex.: pintar o fundo
    da célula de valor no Painel, ou esmaecer um zero. Quando None, tudo neutro.

    `cols_direita` (opcional): lista de nomes de coluna a alinhar à direita, com
    dígitos de largura uniforme (vírgula embaixo de vírgula). Use nas colunas de
    dinheiro/quantidade/porcentagem. Quando None, tudo fica alinhado à esquerda.

    `html_cols` (opcional): lista de colunas cujo conteúdo JÁ é HTML confiável e
    NÃO deve ser escapado — ex.: uma coluna de status montada com `selo(...)`.
    """
    dir_set = set(cols_direita or ())
    html_set = set(html_cols or ())
    ths = "".join(
        f'<th class="vn-num">{_esc(c)}</th>' if c in dir_set else f"<th>{_esc(c)}</th>"
        for c in df.columns
    )
    linhas = []
    for _, row in df.iterrows():
        tds = []
        for col, v in zip(df.columns, row):
            estilo = cor_celula(col, v) if cor_celula else None
            cls = ' class="vn-num"' if col in dir_set else ""
            estilo_td = f' style="{estilo}"' if estilo else ""
            conteudo = str(v) if col in html_set else _esc(v)
            tds.append(f"<td{cls}{estilo_td}>{conteudo}</td>")
        linhas.append(f"<tr>{''.join(tds)}</tr>")
    estilo_wrap = f' style="max-height:{int(altura_max)}px;overflow:auto"' if altura_max else ""
    st.markdown(
        f'<div class="vn-tbl-wrap"{estilo_wrap}><table class="vn-tbl">'
        f'<thead><tr>{ths}</tr></thead><tbody>{"".join(linhas)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def selo(texto, tipo: str = "ok") -> str:
    """Selo/pílula colorida pra usar dentro de uma coluna de tabela (via `html_cols`).

    `tipo`: 'ok'/'info' (azul) · 'danger' (vermelho) · 'success' (verde) ·
    'warning' (âmbar). O estilo real vem do CSS `.vn-selo` no ui_theme.
    """
    return f'<span class="vn-selo vn-selo-{tipo}">{_esc(texto)}</span>'


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
