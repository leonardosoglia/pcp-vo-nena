"""
graficos.py — Figurino oficial dos gráficos do PCP Vó Nena (Leva B da reforma).

Antes, cada tela vestia os gráficos por conta própria: 7+ paletas espalhadas,
fontes/margens/grades diferentes, e o laranja da marca significando 4 coisas
distintas conforme a tela. Este módulo centraliza:

1. `PALETA` — cores com SIGNIFICADO FIXO no sistema inteiro:
   Classe A é sempre verde, o laranja é sempre a marca/série principal,
   vermelho é sempre alerta. Ver o dicionário abaixo.
2. Template Plotly "vonena" registrado como padrão global — fonte Inter,
   fundo branco, grade sutil, legenda no topo, margens equilibradas.
   Todo `st.plotly_chart` do app herda SEM precisar mudar o gráfico;
   cores/margens explícitas de cada tela continuam valendo (override local).
3. `CFG` — configuração padrão do plotly_chart (sem barra de ferramentas,
   responsivo no celular).

Chamado por `ui_theme.aplicar_tema()` — nenhuma tela precisa importar isto
diretamente, a não ser que queira usar a PALETA pelas cores semânticas.
"""

# ── Paleta semântica (cores com significado fixo) ────────────────────────────
PALETA = {
    "marca":       "#C05621",  # laranja Vó Nena — série principal / destaque
    "marca_clara": "#E8A87C",  # laranja suave — parcial / secundário da marca
    "classe_a":    "#059669",  # verde — Classe A (Curva ABC, qualquer tela)
    "classe_b":    "#B45309",  # caramelo — Classe B
    "classe_c":    "#991B1B",  # vinho — Classe C
    "info":        "#0E7490",  # azul-petróleo — série de contraste/informativa
    "neutro":      "#A8A29E",  # cinza — contexto, produção vs demanda
    "alerta":      "#B91C1C",  # vermelho — alerta/limite
    "grafite":     "#1F2937",  # cinza-escuro — tendência/média móvel
    "meta":        "#C3C9D1",  # cinza-claro — linhas de meta tracejadas
}

# Cores por classe ABC prontas pra mapear (fonte única — não redefinir por tela)
COR_CLASSE = {"A": PALETA["classe_a"], "B": PALETA["classe_b"], "C": PALETA["classe_c"]}

# Ordem de cores quando o gráfico não escolhe (1ª série = marca, 2ª = contraste...)
COLORWAY = [PALETA["marca"], PALETA["info"], PALETA["neutro"],
            PALETA["classe_b"], PALETA["classe_a"], PALETA["grafite"]]

# Config padrão do st.plotly_chart — sem barra de ferramentas (evita zoom
# acidental no celular), responsivo.
CFG = {"displayModeBar": False, "responsive": True}


def registrar_template():
    """Registra o template "vonena" e o define como padrão global do Plotly.

    Idempotente e à prova de falha: se o Plotly não estiver disponível na tela,
    simplesmente não faz nada (nenhuma tela quebra por causa de gráfico).
    """
    try:
        import plotly.graph_objects as go
        import plotly.io as pio
    except Exception:
        return

    if "vonena" not in pio.templates:
        pio.templates["vonena"] = go.layout.Template(
            layout=go.Layout(
                font=dict(family="Inter, 'Segoe UI', sans-serif",
                          size=12, color="#3A4250"),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                colorway=COLORWAY,
                margin=dict(l=20, r=20, t=36, b=40),
                xaxis=dict(gridcolor="#F2F4F7", zerolinecolor="#E5E7EB",
                           linecolor="#E5E7EB", ticks=""),
                yaxis=dict(gridcolor="#F2F4F7", zerolinecolor="#E5E7EB",
                           linecolor="#E5E7EB", ticks=""),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="left", x=0),
                hoverlabel=dict(font=dict(family="Inter, 'Segoe UI', sans-serif",
                                          size=12)),
            )
        )
    pio.templates.default = "plotly_white+vonena"
