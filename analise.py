"""
analise.py — Camada 1 de inteligência do PCP Vó Nena.

Visualização de tendências e padrões a partir do histórico de folhas salvas.
Renderizada como aba "📊 Análise" no painel.py.

5 sub-abas internas:
    📈 Evolução temporal — linha por sabor ao longo do tempo
    📊 Dia da Semana — média por dia da semana (descobre o calendário da Gestão)
    🔥 Heatmap — intensidade por (dia × sabor)
    ⚙️ Ajustes da Gestão — quantas vezes ajustou cada parâmetro vs base
    ⚠️ Anomalias — alertas de proporções atípicas (ex: LP > T em palha)

A inteligência cresce conforme o histórico cresce.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from cached_db import (
    get_folha_cocada, get_folha_palha, get_papelzinho_joel, get_pm_balas_doces,
    get_metas_45g, get_metas_mini_pet, list_datas_folha,
    SABORES_COCADA, SABORES_PALHA, SIGLA_COCADA, SIGLA_PALHA,
)

DIAS_PT_FULL = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta",
                4: "Sexta", 5: "Sábado", 6: "Domingo"}
DIAS_PT_SHORT = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}
ORDEM_DIAS_SHORT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
DIAS_COL_METAS = {0: "segunda", 1: "terca", 2: "quarta", 3: "quinta", 4: "sexta"}

# Calendário descoberto via entrevista com a Gestão
CALENDARIO_CORTE = {
    0: "45g", 1: "Mini+Pet", 2: "45g", 3: "45g", 4: "Mini+Pet",
    5: None, 6: None,
}

# Cores Vó Nena (consistente com painel)
PALETA_SABORES = ["#C05621", "#7B341E", "#B45309", "#92400E", "#78350F", "#451A03"]


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS DE CARREGAMENTO
# ══════════════════════════════════════════════════════════════════════════════
def _datas_no_periodo(data_ini, data_fim):
    """Lista de strings de datas (YYYY-MM-DD) salvas no banco dentro do período."""
    todas = list_datas_folha()
    out = []
    for d in todas:
        try:
            d_obj = datetime.strptime(d, "%Y-%m-%d").date()
            if data_ini <= d_obj <= data_fim:
                out.append(d)
        except ValueError:
            continue
    return sorted(out)


def carregar_cocada(datas):
    """DataFrame wide com todas as métricas de cocada por (data, sabor)."""
    linhas = []
    cols_int = (
        "emb_45g", "emb_mini", "emb_pet", "emb_potes_260g", "emb_potes_605g",
        "cort1_45g", "cort1_mini", "cort1_pet",
        "ord_corte_45g", "ord_corte_mini", "ord_corte_pet",
        "ord_prod_band", "ord_prod_virada",
        "ord_prod_potes_260g", "ord_prod_potes_605g",
        "ord_emb_45g", "ord_emb_mini",
        "param_real_45g", "param_real_mini", "param_real_pet",
    )
    for d in datas:
        for r in get_folha_cocada(d):
            linha = {"data": d, "sabor": r["sabor"]}
            for c in cols_int:
                linha[c] = int(r.get(c) or 0)
            linhas.append(linha)
    df = pd.DataFrame(linhas)
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
        df["dia_semana_idx"] = df["data"].dt.weekday
        df["dia_semana"] = df["dia_semana_idx"].map(DIAS_PT_SHORT)
    return df


def carregar_palha(datas):
    linhas = []
    cols_int = ("emb_50g", "emb_pet", "cont_band_palha", "cont_band_pos_corte",
                "ord_corte_50g", "ord_corte_pet", "ord_prod_band")
    for d in datas:
        for r in get_folha_palha(d):
            linha = {"data": d, "sabor": r["sabor"]}
            for c in cols_int:
                linha[c] = int(r.get(c) or 0)
            linhas.append(linha)
    df = pd.DataFrame(linhas)
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
        df["dia_semana_idx"] = df["data"].dt.weekday
        df["dia_semana"] = df["dia_semana_idx"].map(DIAS_PT_SHORT)
    return df


def carregar_papelzinho(datas):
    linhas = []
    cols_int = ("joel_45g", "joel_mini", "joel_pet", "joel_pv", "joel_v")
    for d in datas:
        for r in get_papelzinho_joel(d):
            linha = {"data": d, "sabor": r["sabor"]}
            for c in cols_int:
                linha[c] = int(r.get(c) or 0)
            linhas.append(linha)
    df = pd.DataFrame(linhas)
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
        df["dia_semana_idx"] = df["data"].dt.weekday
        df["dia_semana"] = df["dia_semana_idx"].map(DIAS_PT_SHORT)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# SUB-ABA 1 — Evolução temporal
# ══════════════════════════════════════════════════════════════════════════════
def _render_evolucao(df_cocada, df_palha, df_joel, sabores_cocada):
    st.markdown("##### 📈 Evolução temporal por sabor")

    if df_cocada.empty and df_palha.empty and df_joel.empty:
        st.info("Sem dados pra mostrar.")
        return

    # Seletor: o que medir
    opcoes_metricas = {
        "Embalados 45g (cocada)":             ("cocada", "emb_45g",  "Embalados 45g · unidades"),
        "Embalados Mini (cocada)":            ("cocada", "emb_mini", "Embalados Mini · unidades"),
        "Embalados Pet (cocada)":             ("cocada", "emb_pet",  "Embalados Pet · unidades"),
        "Cortados ① 45g (cocada)":            ("cocada", "cort1_45g","Cortados ① 45g · unidades"),
        "Cortados ① Mini (cocada)":           ("cocada", "cort1_mini","Cortados ① Mini · unidades"),
        "Ordem produção (bandejas) (cocada)": ("cocada", "ord_prod_band","Ordem produção · bandejas"),
        "Ordem corte 45g (bandejas)":         ("cocada", "ord_corte_45g","Ordem corte 45g · bandejas"),
        "Ordem corte Mini (bandejas)":        ("cocada", "ord_corte_mini","Ordem corte Mini · bandejas"),
        "Ordem embalagem 45g (und)":          ("cocada", "ord_emb_45g","Ordem embalagem 45g · unidades"),
        "Produção — V (bandejas viradas)":    ("joel",   "joel_v",    "Produção V · bandejas viradas"),
        "Produção — PV (bandejas P/Virar)":   ("joel",   "joel_pv",   "Produção PV · bandejas p/virar"),
        "Produção — 45g (sala produção)":     ("joel",   "joel_45g",  "Produção 45g · und sala produção"),
        "Embalados Palha 50g":                ("palha",  "emb_50g",   "Embalados Palha 50g · und"),
        "Embalados Palha Pet":                ("palha",  "emb_pet",   "Embalados Palha Pet · und"),
    }
    rotulo = st.selectbox("📊 Métrica a visualizar", list(opcoes_metricas.keys()),
                          key="evol_metrica")
    categoria, coluna, titulo = opcoes_metricas[rotulo]

    if categoria == "cocada":
        df = df_cocada[df_cocada["sabor"].isin(sabores_cocada)]
    elif categoria == "joel":
        df = df_joel[df_joel["sabor"].isin(sabores_cocada)]
    else:
        df = df_palha

    if df.empty or coluna not in df.columns:
        st.info("Sem dados dessa métrica no período.")
        return

    df_plot = df[["data", "sabor", coluna]].rename(columns={coluna: "valor"})
    fig = px.line(
        df_plot, x="data", y="valor", color="sabor",
        title=titulo, markers=True,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(
        xaxis_title="Data", yaxis_title="Valor",
        hovermode="x unified", legend_title="Sabor",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Métrica auxiliar — total agregado por dia
    total_por_dia = df_plot.groupby("data")["valor"].sum()
    if len(total_por_dia) > 1:
        st.caption(
            f"📊 Média {len(total_por_dia)} dias: **{total_por_dia.mean():.0f}** · "
            f"Máximo: **{total_por_dia.max():.0f}** · Mínimo: **{total_por_dia.min():.0f}**"
        )


# ══════════════════════════════════════════════════════════════════════════════
# SUB-ABA 2 — Dia da semana
# ══════════════════════════════════════════════════════════════════════════════
def _render_dia_semana(df_cocada, sabores_cocada):
    st.markdown("##### 📊 Média por dia da semana")
    st.caption(
        "Revela o **calendário implícito** das decisões. Compare com o calendário da Gestão: "
        "Seg/Qua/Qui = 45g · Ter/Sex = Mini+Pet."
    )

    if df_cocada.empty:
        st.info("Sem dados.")
        return

    df = df_cocada[df_cocada["sabor"].isin(sabores_cocada)]
    metricas = {
        "Ordem corte 45g":  "ord_corte_45g",
        "Ordem corte Mini": "ord_corte_mini",
        "Ordem corte Pet":  "ord_corte_pet",
        "Ordem produção":   "ord_prod_band",
        "Ordem embalagem 45g": "ord_emb_45g",
    }
    metrica_label = st.selectbox("Métrica", list(metricas.keys()), key="dia_metrica")
    metrica = metricas[metrica_label]

    if metrica not in df.columns:
        return

    df_grouped = (
        df.groupby(["dia_semana_idx", "dia_semana", "sabor"])[metrica]
          .mean().reset_index()
    )
    df_grouped["dia_semana"] = pd.Categorical(
        df_grouped["dia_semana"], categories=ORDEM_DIAS_SHORT, ordered=True
    )
    df_grouped = df_grouped.sort_values(["dia_semana_idx", "sabor"])

    fig = px.bar(
        df_grouped, x="dia_semana", y=metrica, color="sabor", barmode="group",
        title=f"Média de {metrica_label} por dia da semana",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(
        xaxis_title="Dia da semana", yaxis_title="Média",
        legend_title="Sabor",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar destaque: dia com maior média
    if not df_grouped.empty:
        media_por_dia = df_grouped.groupby("dia_semana", observed=False)[metrica].sum()
        if media_por_dia.max() > 0:
            dia_top = media_por_dia.idxmax()
            st.caption(f"🏆 Dia com maior {metrica_label}: **{dia_top}**")


# ══════════════════════════════════════════════════════════════════════════════
# SUB-ABA 3 — Heatmap
# ══════════════════════════════════════════════════════════════════════════════
def _render_heatmap(df_cocada, sabores_cocada):
    st.markdown("##### 🔥 Heatmap (dia da semana × sabor)")
    st.caption(
        "Intensidade de uma métrica em cada combinação dia × sabor. "
        "Quanto mais escuro, mais alto o valor médio."
    )

    if df_cocada.empty:
        st.info("Sem dados.")
        return

    df = df_cocada[df_cocada["sabor"].isin(sabores_cocada)]
    metricas = {
        "Ordem corte 45g":  "ord_corte_45g",
        "Ordem corte Mini": "ord_corte_mini",
        "Ordem corte Pet":  "ord_corte_pet",
        "Embalados 45g":    "emb_45g",
        "Embalados Mini":   "emb_mini",
        "Ordem produção (band)": "ord_prod_band",
    }
    metrica_label = st.selectbox("Métrica", list(metricas.keys()), key="heat_metrica")
    metrica = metricas[metrica_label]

    pivot = df.pivot_table(index="sabor", columns="dia_semana", values=metrica, aggfunc="mean")
    # Ordenar
    cols_existentes = [d for d in ORDEM_DIAS_SHORT if d in pivot.columns]
    pivot = pivot[cols_existentes]
    pivot = pivot.reindex([s for s in SABORES_COCADA if s in pivot.index])

    if pivot.empty:
        st.info("Sem dados pra essa combinação.")
        return

    fig = px.imshow(
        pivot, text_auto=".0f", aspect="auto",
        labels=dict(x="Dia da semana", y="Sabor", color=metrica_label),
        color_continuous_scale="Oranges",
        title=f"{metrica_label} — média por (dia, sabor)",
    )
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SUB-ABA 4 — Ajustes da Gestão
# ══════════════════════════════════════════════════════════════════════════════
def _render_ajustes_eraldo(df_cocada, sabores_cocada):
    st.markdown("##### ⚙️ Ajustes da Gestão (Parâmetro Real vs Base esperada)")
    st.caption(
        "Quanto a Gestão desviou da tabela de referência em cada folha. "
        "Positivo = aumentou produção · Negativo = diminuiu."
    )

    if df_cocada.empty:
        st.info("Sem dados.")
        return

    metas_45g = {r["sabor"]: r for r in get_metas_45g()}
    metas_mp = {r["sabor"]: r for r in get_metas_mini_pet()}

    # Calcular ajuste de 45g
    df = df_cocada[df_cocada["sabor"].isin(sabores_cocada)].copy()
    df["dia_col"] = df["dia_semana_idx"].map(DIAS_COL_METAS)

    def base_45g(row):
        if row["dia_col"] is None or pd.isna(row["dia_col"]):
            return 0
        meta = metas_45g.get(row["sabor"], {})
        return int(meta.get(row["dia_col"]) or 0)

    df["base_45g"] = df.apply(base_45g, axis=1)
    df["ajuste_45g"] = df["param_real_45g"] - df["base_45g"]

    # Tabela resumo: ajustes não-zero
    df_ajustes = df[df["ajuste_45g"] != 0][["data", "sabor", "base_45g", "param_real_45g", "ajuste_45g"]]
    df_ajustes = df_ajustes.sort_values("data", ascending=False)

    if df_ajustes.empty:
        st.success("✅ Nenhum ajuste de 45g registrado no período (Gestão seguiu a base semanal).")
    else:
        st.markdown("**Ajustes registrados (45g):**")
        df_ajustes_show = df_ajustes.copy()
        df_ajustes_show["data"] = df_ajustes_show["data"].dt.strftime("%d/%m/%Y")
        df_ajustes_show.columns = ["Data", "Sabor", "Base", "Real", "Ajuste"]
        st.dataframe(
            df_ajustes_show.style.map(
                lambda v: ("color:#065F46;font-weight:700;" if isinstance(v, (int, float)) and v > 0
                           else "color:#7F1D1D;font-weight:700;" if isinstance(v, (int, float)) and v < 0
                           else ""),
                subset=["Ajuste"],
            ),
            use_container_width=True, hide_index=True,
        )

    # Sumário por sabor
    st.markdown("**Sumário por sabor:**")
    agg = df.groupby("sabor")["ajuste_45g"].agg(["sum", "mean", "count"])
    agg.columns = ["Soma ajustes", "Média ajustes", "Folhas no período"]
    st.dataframe(agg, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SUB-ABA 5 — Detecção de anomalias
# ══════════════════════════════════════════════════════════════════════════════
def _render_anomalias(df_cocada, df_palha):
    st.markdown("##### ⚠️ Detecção de anomalias")
    st.caption(
        "Sistema avisa quando proporções típicas entre sabores são violadas — "
        "pode indicar erro de contagem ou situação atípica que merece atenção."
    )

    alertas = []

    # Anomalia 1: Palha 50g — Leite em pó > Tradicional + 30%
    if not df_palha.empty:
        df_50 = df_palha[df_palha["emb_50g"] > 0]
        if not df_50.empty:
            pivot = df_50.pivot_table(index="data", columns="sabor", values="emb_50g", aggfunc="last")
            if "TRADICIONAL" in pivot.columns and "LEITE EM PÓ" in pivot.columns:
                for data_idx, row in pivot.iterrows():
                    t = row.get("TRADICIONAL", 0) or 0
                    l = row.get("LEITE EM PÓ", 0) or 0
                    if t > 0 and l > t * 1.3:
                        alertas.append({
                            "tipo": "🌾 Palha 50g",
                            "data": data_idx.strftime("%d/%m/%Y"),
                            "descrição": (
                                f"Leite em Pó ({l}) está mais de 30% acima do Tradicional ({t}). "
                                f"Padrão esperado: LP ≤ T."
                            ),
                        })

    # Anomalia 2: Cocada 45g — embalado de Tradicional muito abaixo dos outros
    # (T deveria ser sempre o maior em 45g)
    if not df_cocada.empty:
        df_45 = df_cocada[df_cocada["emb_45g"] > 0]
        if not df_45.empty:
            pivot = df_45.pivot_table(index="data", columns="sabor", values="emb_45g", aggfunc="last")
            if "TRADICIONAL" in pivot.columns:
                for data_idx, row in pivot.iterrows():
                    t = row.get("TRADICIONAL", 0) or 0
                    if t > 0:
                        for outro in ("LEITE CONDENSADO", "BRIGADEIRO", "CAFÉ", "PÉ DE MOÇA"):
                            v = row.get(outro, 0) or 0
                            if v > t:
                                alertas.append({
                                    "tipo": "🍬 Cocada 45g",
                                    "data": data_idx.strftime("%d/%m/%Y"),
                                    "descrição": (
                                        f"{outro} ({v}) está acima do Tradicional ({t}). "
                                        f"T normalmente é o sabor mais embalado."
                                    ),
                                })

    if not alertas:
        st.success("✅ Nenhuma anomalia detectada no período selecionado.")
    else:
        st.warning(f"⚠️ {len(alertas)} anomalia(s) detectada(s):")
        df_al = pd.DataFrame(alertas)
        df_al.columns = ["Tipo", "Data", "Descrição"]
        st.dataframe(df_al, use_container_width=True, hide_index=True)

    st.divider()
    st.caption(
        "💡 Mais regras de anomalia serão adicionadas conforme o histórico crescer e novos padrões "
        "forem identificados."
    )


# ══════════════════════════════════════════════════════════════════════════════
# RENDER PRINCIPAL — chamado pelo painel.py
# ══════════════════════════════════════════════════════════════════════════════
def render():
    st.subheader("📊 Análise de Tendências e Padrões")
    st.caption(
        "Camada 1 da inteligência do sistema — visualização do histórico de folhas. "
        "Quanto mais folhas você digitalizar (atuais e antigas), mais ricos ficam os gráficos."
    )

    datas_disponiveis = sorted(list_datas_folha())
    if not datas_disponiveis:
        st.info(
            "📋 **Nenhuma folha registrada ainda.** "
            "Salve folhas no formulário **Lançamento** (porta 8502) e os gráficos aparecerão aqui."
        )
        return

    # ── Filtros ──
    data_min = datetime.strptime(datas_disponiveis[0], "%Y-%m-%d").date()
    data_max = datetime.strptime(datas_disponiveis[-1], "%Y-%m-%d").date()

    col_ini, col_fim, col_sab = st.columns([1, 1, 2.5])
    with col_ini:
        data_ini = st.date_input("📅 De", value=data_min, min_value=data_min, max_value=data_max)
    with col_fim:
        data_fim = st.date_input("📅 Até", value=data_max, min_value=data_min, max_value=data_max)
    with col_sab:
        sabores_filtro = st.multiselect(
            "🍬 Sabores cocada",
            options=SABORES_COCADA,
            default=SABORES_COCADA,
            help="Filtra os gráficos de cocada por sabor (palha não filtra).",
        )

    if data_ini > data_fim:
        st.error("Data inicial maior que final.")
        return

    # ── Carregar dataframes ──
    datas_periodo = _datas_no_periodo(data_ini, data_fim)
    df_cocada = carregar_cocada(datas_periodo)
    df_palha = carregar_palha(datas_periodo)
    df_joel = carregar_papelzinho(datas_periodo)

    if df_cocada.empty and df_palha.empty and df_joel.empty:
        st.warning(f"Nenhuma folha encontrada entre {data_ini.strftime('%d/%m/%Y')} e {data_fim.strftime('%d/%m/%Y')}.")
        return

    # ── KPIs ──
    n_folhas = len(datas_periodo)
    n_dias = (data_fim - data_ini).days + 1

    st.markdown("### 🎯 KPIs do período")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Folhas registradas", n_folhas, help=f"Período de {n_dias} dias")
    if not df_cocada.empty and "emb_45g" in df_cocada.columns:
        media_emb = df_cocada.groupby("data")["emb_45g"].sum().mean()
        c2.metric("Média Emb 45g/dia", f"{media_emb:,.0f}")
    if not df_cocada.empty and "ord_prod_band" in df_cocada.columns:
        total_band = df_cocada["ord_prod_band"].sum()
        c3.metric("Total bandejas produção", f"{total_band:,}")
    if not df_cocada.empty and "ord_emb_45g" in df_cocada.columns:
        total_emb = df_cocada["ord_emb_45g"].sum() + df_cocada["ord_emb_mini"].sum()
        c4.metric("Total und embalagem", f"{total_emb:,}")

    st.divider()

    # ── Sub-abas ──
    sub_evol, sub_dia, sub_heat, sub_aj, sub_anom = st.tabs([
        "📈 Evolução",
        "📊 Dia da Semana",
        "🔥 Heatmap",
        "⚙️ Ajustes da Gestão",
        "⚠️ Anomalias",
    ])
    with sub_evol: _render_evolucao(df_cocada, df_palha, df_joel, sabores_filtro)
    with sub_dia:  _render_dia_semana(df_cocada, sabores_filtro)
    with sub_heat: _render_heatmap(df_cocada, sabores_filtro)
    with sub_aj:   _render_ajustes_eraldo(df_cocada, sabores_filtro)
    with sub_anom: _render_anomalias(df_cocada, df_palha)
