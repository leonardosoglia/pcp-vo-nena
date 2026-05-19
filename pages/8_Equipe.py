"""
pages/8_Equipe.py — Gestão de equipe (funcionários, capacidades, presença)

Etapa A da Ideia 4 (Sugestão de Ordem do Dia) do ROADMAP_IA.

3 abas:
     Funcionários — CRUD básico (nome, departamento, ativo)
     Capacidades — quanto cada funcionário produz por atividade (band/dia,
                     tachos/dia, und/dia, etc.)
     Presença    — quem está presente em uma data específica

Os dados aqui alimentam o algoritmo de Sugestão de Ordem (Etapa C):
    capacidade_efetiva_do_dia = soma(valor_normal) de quem está PRESENTE
                                pra cada atividade

Capítulo TCC: "Modelagem de restrições de capacidade de mão-de-obra em PCP".
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os

# Bootstrap defensivo (HF Spaces sem secrets.toml — try/except evita erro)
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from cached_db import (
    get_funcionarios, get_funcionario, get_capacidades_funcionario,
    get_capacidades_atividade, get_presenca_dia, get_capacidade_efetiva_dia,
    criar_funcionario, atualizar_funcionario, excluir_funcionario,
    upsert_capacidade, excluir_capacidade,
    upsert_presenca,
    invalidar_equipe,
    DEPARTAMENTOS_FUNCIONARIO, ATIVIDADES_CAPACIDADE,
)

st.set_page_config(
    page_title="Equipe • Doces Vó Nena",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tema visual centralizado (Inter font + paleta clean)
from ui_theme import aplicar_tema
aplicar_tema()


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ════════════════════════════════════════════════════════════════════════════
st.title("Equipe — Funcionários, Capacidades e Presença")
st.caption(
    "Cadastro de quem trabalha na fábrica + capacidades por atividade + "
    "presença diária. Alimenta o algoritmo de **Sugestão de Ordem do Dia** "
    "(Camada 2 — em construção)."
)

with st.expander("ℹ️ Como essa página funciona (clica pra entender)", expanded=False):
    st.markdown("""
**3 dimensões cadastradas aqui:**

| Dimensão | Frequência de mudança | Quem usa |
|---|---|---|
| **Funcionários** (nome, departamento) | Raríssimo (entrada/saída de pessoal) | Gestão + Leonardo |
| **Capacidades** (quanto cada um produz por atividade) | Estável; recalibra a cada ~3 meses | Gestão (Eraldo informa) |
| **Presença diária** | Diária (de manhã, marca quem veio) | Eraldo / Leonardo |

**Como o sistema usa esses dados (próxima Etapa C):**

```
capacidade_efetiva_do_dia[atividade] =
    soma(valor_normal[atividade]) pra cada funcionário PRESENTE
```

Exemplo: se Gil corta 30 bandejas 45g/dia e Paulo corta 25 bandejas/dia,
e hoje só Paulo veio → capacidade efetiva de corte 45g = 25 band.
Aí o sistema sugere ordem de corte respeitando esse limite.

**Por que esse modelo é forte pro TCC:**

Modela explicitamente a **restrição de capacidade de mão-de-obra** — clássico
de PCP (Heizer & Render, *Operations Management*, Cap 13 — Capacity Planning).
A maioria dos sistemas comerciais usa capacidade FIXA por departamento;
aqui é POR FUNCIONÁRIO POR ATIVIDADE, refletindo a realidade da fábrica
artesanal onde cada pessoa tem ritmo próprio.
""")


# ════════════════════════════════════════════════════════════════════════════
# ABAS
# ════════════════════════════════════════════════════════════════════════════
tab_func, tab_cap, tab_pres = st.tabs([
    " Funcionários",
    " Capacidades",
    " Presença do dia",
])


# ────────────────────────────────────────────────────────────────────────────
# ABA 1 — FUNCIONÁRIOS (CRUD)
# ────────────────────────────────────────────────────────────────────────────
with tab_func:
    st.subheader("Cadastro de funcionários")

    col_a, col_b = st.columns(2)
    with col_a:
        mostrar_inativos = st.checkbox(
            "Mostrar também funcionários inativos", value=False,
            help="Soft delete: funcionários removidos ficam marcados inativos mas preservam histórico.",
        )
    with col_b:
        # Estatísticas rápidas
        todos = get_funcionarios(somente_ativos=False)
        ativos = [f for f in todos if f.get("ativo")]
        st.metric("Total cadastrados", f"{len(ativos)} ativos / {len(todos)} total")

    # ── Form de criação ──────────────────────────────────────────────────
    with st.expander(" Cadastrar novo funcionário", expanded=False):
        with st.form("form_criar_funcionario", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                novo_nome = st.text_input("Nome", placeholder="Ex: Gil")
            with col2:
                novo_dept = st.selectbox("Departamento", DEPARTAMENTOS_FUNCIONARIO, index=2)
            nova_obs = st.text_area("Observação (opcional)", placeholder="Ex: Especialista em 45g, trabalha desde 2018",
                                     height=70)
            criar_btn = st.form_submit_button("Criar funcionário", type="primary")

            if criar_btn:
                if not novo_nome or not novo_nome.strip():
                    st.error("️ Nome não pode ser vazio.")
                else:
                    try:
                        new_id = criar_funcionario(novo_nome.strip(), novo_dept, nova_obs)
                        invalidar_equipe()
                        st.success(f" {novo_nome} criado (ID #{new_id})")
                        st.rerun()
                    except Exception as e:
                        st.error(f" Erro: {e}")

    # ── Lista de funcionários ────────────────────────────────────────────
    funcionarios = get_funcionarios(somente_ativos=not mostrar_inativos)

    if not funcionarios:
        st.markdown(
            "<div class='didatica'>"
            "ℹ️ Nenhum funcionário cadastrado ainda. Use o expander ' Cadastrar' "
            "acima pra começar. <br><b>Sugestão de cadastros iniciais:</b><br>"
            "• Eraldo (Gestão) · Sr. Joel (Produção) · Gil (Corte) · Paulo (Auxiliar geral)<br>"
            "• Leonília (Embalagem) · Popô (Embalagem) · Maria (Produção)<br>"
            "• Mariana (Suprimentos) · Leonardo (Estoque/Contagem)"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        # Agrupa por departamento
        por_dept = {}
        for f in funcionarios:
            d = f.get("departamento", "Sem departamento")
            por_dept.setdefault(d, []).append(f)

        for dept in DEPARTAMENTOS_FUNCIONARIO:
            if dept not in por_dept:
                continue
            st.markdown(f"###  {dept}")
            for f in por_dept[dept]:
                ativo = bool(f.get("ativo"))
                badge = "<span class='badge-ativo'>ATIVO</span>" if ativo else "<span class='badge-inativo'>INATIVO</span>"
                col_info, col_acoes = st.columns([3, 1])
                with col_info:
                    st.markdown(
                        f"<div class='card-funcionario'>"
                        f"<b style='font-size:16px;'>{f['nome']}</b> &nbsp;{badge}<br>"
                        f"<span style='color:#666;font-size:12px;'>ID #{f['id']} · "
                        f"criado em {f.get('criado_em', '?')}</span><br>"
                        f"{('<i style=\"color:#7B341E;\">' + (f.get('observacao') or '') + '</i>') if f.get('observacao') else ''}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with col_acoes:
                    if ativo:
                        if st.button("️ Inativar", key=f"del_{f['id']}", use_container_width=True):
                            excluir_funcionario(f["id"])
                            invalidar_equipe()
                            st.success(f" {f['nome']} inativado.")
                            st.rerun()
                    else:
                        if st.button("️ Reativar", key=f"act_{f['id']}", use_container_width=True):
                            atualizar_funcionario(f["id"], ativo=1)
                            invalidar_equipe()
                            st.success(f" {f['nome']} reativado.")
                            st.rerun()


# ────────────────────────────────────────────────────────────────────────────
# ABA 2 — CAPACIDADES (por funcionário × atividade)
# ────────────────────────────────────────────────────────────────────────────
with tab_cap:
    st.subheader("Capacidades por funcionário")
    st.caption(
        "Pra cada funcionário, quanto ele produz em cada atividade num dia "
        "normal. Esses valores alimentam o algoritmo de Sugestão de Ordem."
    )

    funcs_ativos = get_funcionarios(somente_ativos=True)
    if not funcs_ativos:
        st.warning("️ Cadastra funcionários na aba anterior antes de definir capacidades.")
        st.stop()

    # Seleciona funcionário
    nomes = {f["id"]: f"{f['nome']} ({f['departamento']})" for f in funcs_ativos}
    func_id_sel = st.selectbox(
        "Funcionário",
        options=list(nomes.keys()),
        format_func=lambda fid: nomes[fid],
    )
    func_sel = get_funcionario(func_id_sel)

    if func_sel:
        st.markdown(f"####  Capacidades de **{func_sel['nome']}**")

        # ── Form de criação/atualização ──────────────────────────────────
        with st.expander(" Adicionar / atualizar capacidade", expanded=False):
            with st.form("form_capacidade", clear_on_submit=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    atividade_sel = st.selectbox(
                        "Atividade",
                        ATIVIDADES_CAPACIDADE,
                        help="Lista controlada pra permitir consulta estruturada pelo algoritmo.",
                    )
                with col2:
                    unidade_sel = st.text_input("Unidade", placeholder="band/dia",
                                                 help="Ex: band/dia, tachos/dia, und/dia")

                col_v1, col_v2, col_v3 = st.columns(3)
                with col_v1:
                    v_normal = st.number_input("Normal (esperado)", min_value=0.0,
                                                value=20.0, step=1.0)
                with col_v2:
                    v_min = st.number_input("Mín (dia ruim)", min_value=0.0,
                                             value=0.0, step=1.0)
                with col_v3:
                    v_max = st.number_input("Máx (dia bom)", min_value=0.0,
                                             value=0.0, step=1.0)

                obs_cap = st.text_input("Observação (opcional)",
                                          placeholder="Ex: prefere 45g, evita Pet")
                salvar_cap = st.form_submit_button("Salvar capacidade", type="primary")

                if salvar_cap:
                    try:
                        upsert_capacidade(
                            func_id_sel, atividade_sel,
                            valor_normal=v_normal,
                            valor_min=v_min, valor_max=v_max,
                            unidade=unidade_sel, observacao=obs_cap,
                        )
                        invalidar_equipe()
                        st.success(f" Capacidade '{atividade_sel}' salva pra {func_sel['nome']}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f" Erro: {e}")

        # ── Lista de capacidades ──────────────────────────────────────────
        caps = get_capacidades_funcionario(func_id_sel)
        if not caps:
            st.markdown(
                "<div class='didatica'>"
                "ℹ️ Sem capacidades cadastradas. Use ' Adicionar capacidade' acima."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            df_cap = pd.DataFrame(caps)
            df_cap = df_cap[["atividade", "valor_normal", "valor_min", "valor_max",
                              "unidade", "observacao", "id"]].copy()
            df_cap.columns = ["Atividade", "Normal", "Mín", "Máx", "Unidade", "Obs", "ID"]
            st.dataframe(df_cap.drop(columns=["ID"]),
                          use_container_width=True, hide_index=True)

            # Botões de remoção individual
            st.caption("**Remover capacidade:**")
            cols_del = st.columns(min(len(caps), 4))
            for i, cap in enumerate(caps):
                with cols_del[i % 4]:
                    if st.button(f"️ {cap['atividade']}",
                                  key=f"delcap_{cap['id']}",
                                  use_container_width=True):
                        excluir_capacidade(cap["id"])
                        invalidar_equipe()
                        st.success(f" Removida: {cap['atividade']}")
                        st.rerun()


# ────────────────────────────────────────────────────────────────────────────
# ABA 3 — PRESENÇA DO DIA
# ────────────────────────────────────────────────────────────────────────────
with tab_pres:
    st.subheader(" Presença diária")
    st.caption(
        "Quem trabalhou em cada data. Sistema usa pra calcular capacidade "
        "efetiva (só conta funcionários presentes)."
    )

    data_pres = st.date_input(
        "Data da presença",
        value=date.today(),
        max_value=date.today(),
        format="DD/MM/YYYY",
    )
    data_str = data_pres.isoformat()

    presencas = get_presenca_dia(data_str)
    if not presencas:
        st.warning("️ Cadastra funcionários na aba 'Funcionários' antes.")
        st.stop()

    # Resumo no topo
    n_presentes = sum(1 for p in presencas if p.get("presente") == 1)
    n_ausentes = sum(1 for p in presencas if p.get("presente") == 0)
    n_naomarcados = sum(1 for p in presencas if p.get("presente") is None)
    n_total = len(presencas)

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric(" Total ativos", n_total)
    col_b.metric(" Presentes", n_presentes)
    col_c.metric(" Ausentes", n_ausentes)
    col_d.metric(" Não marcado", n_naomarcados)

    st.divider()

    # Botões em massa
    col_mass_a, col_mass_b, col_mass_c = st.columns(3)
    with col_mass_a:
        if st.button(" Marcar TODOS como presentes", use_container_width=True):
            for p in presencas:
                upsert_presenca(data_str, p["funcionario_id"], presente=True)
            invalidar_equipe()
            st.success(" Todos marcados como presentes.")
            st.rerun()
    with col_mass_b:
        if st.button(" Marcar TODOS como ausentes", use_container_width=True):
            for p in presencas:
                upsert_presenca(data_str, p["funcionario_id"], presente=False)
            invalidar_equipe()
            st.success(" Todos marcados como ausentes.")
            st.rerun()
    with col_mass_c:
        st.caption("Atalhos: use os botões em massa pra começar e depois ajuste individualmente.")

    st.divider()

    # ── Lista por departamento com checkboxes ────────────────────────────
    por_dept = {}
    for p in presencas:
        d = p.get("departamento", "Sem departamento")
        por_dept.setdefault(d, []).append(p)

    for dept in DEPARTAMENTOS_FUNCIONARIO:
        if dept not in por_dept:
            continue
        st.markdown(f"###  {dept}")
        for p in por_dept[dept]:
            estado_atual = p.get("presente")
            # NULL → checkbox vazio mas indeterminado
            label = f"{p['nome']}"
            if estado_atual is None:
                label += " 🆕"
            elif estado_atual == 0:
                label += " "
            elif estado_atual == 1:
                label += " "

            col_cb, col_obs = st.columns([1, 2])
            with col_cb:
                novo_estado = st.checkbox(
                    label,
                    value=(estado_atual == 1),
                    key=f"pres_{data_str}_{p['funcionario_id']}",
                )
            with col_obs:
                obs_atual = p.get("observacao", "") or ""
                nova_obs = st.text_input(
                    "Observação",
                    value=obs_atual,
                    placeholder="Ex: chegou tarde, saiu cedo, etc.",
                    key=f"obs_{data_str}_{p['funcionario_id']}",
                    label_visibility="collapsed",
                )

            # Atualiza se mudou
            if novo_estado != (estado_atual == 1) or nova_obs != obs_atual:
                try:
                    upsert_presenca(
                        data_str, p["funcionario_id"],
                        presente=novo_estado, observacao=nova_obs,
                    )
                    invalidar_equipe()
                except Exception as e:
                    st.error(f" Erro ao salvar presença de {p['nome']}: {e}")


st.divider()
st.caption(
    " Equipe é a Etapa A da Ideia 4 (Sugestão de Ordem do Dia). "
    "Próxima etapa: o algoritmo vai consumir esses dados pra pré-calcular "
    "ord_corte / ord_emb / ord_prod, considerando capacidade efetiva do dia."
)
