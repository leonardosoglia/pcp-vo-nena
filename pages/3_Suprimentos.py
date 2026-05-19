"""
pages/3_Suprimentos.py — Etapa B do roadmap (15/05/2026)

Módulo de Suprimentos — matéria-prima, embalagens, potes, cintas, displays.
Aplica MRP simplificado: ordem de produção × BOM (receita) × estoque atual →
necessidade de compra.

4 abas internas:
    📦 Insumos        — catálogo (CRUD + alertas de estoque mínimo)
    📋 Receitas (BOM) — pra cada produto, quanto consome de cada insumo
    ↕️ Movimentações  — entradas (compras) e saídas (perdas/ajustes/produção)
    🚨 Necessidades   — cruzamento com folha do dia → o que vai faltar/sobrar

Conecta com a folha de produção: quando a Etapa E for implementada (22-29/05),
o salvar_folha_completa vai disparar `registrar_movimento_insumo` automático
pra cada bandeja produzida, baixando o estoque conforme a BOM.
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import sys
import os

# Bootstrap defensivo: entry point já faz, mas garante se a página for o primeiro
# hit. HF Spaces não tem secrets.toml — try/except evita StreamlitSecretNotFoundError.
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

import cached_db as db
from cached_db import (
    init_db,
    get_insumos, get_insumo, criar_insumo, atualizar_insumo, excluir_insumo,
    get_bom_produto, upsert_bom_linha, excluir_bom_linha,
    get_movimentos_insumo, registrar_movimento_insumo,
    calcular_necessidades_do_dia,
    CATEGORIAS_INSUMO, UNIDADES_INSUMO, TIPOS_MOVIMENTO, ORIGENS_MOVIMENTO,
    listar_produtos_possiveis,
    invalidar_suprimentos,
)

st.set_page_config(
    page_title="Suprimentos • Doces Vó Nena",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tema visual centralizado (Inter font + paleta clean)
from ui_theme import aplicar_tema
aplicar_tema()

# Idempotente — garante schema novo nos primeiros acessos pós-deploy
init_db()


# ── Helpers locais ─────────────────────────────────────────────────────────────
def _status_estoque(ins: dict) -> tuple[str, str]:
    """Retorna (emoji, label) baseado em estoque_atual vs estoque_minimo."""
    atual = float(ins.get("estoque_atual") or 0)
    minimo = float(ins.get("estoque_minimo") or 0)
    seguranca = float(ins.get("estoque_seguranca") or 0)
    if seguranca > 0 and atual < seguranca:
        return ("🔴", "Crítico")
    if minimo > 0 and atual < minimo:
        return ("🟡", "Abaixo do mínimo")
    return ("🟢", "OK")


def _formatar_qtd(qtd: float, unidade: str) -> str:
    """Mostra qtd com unidade. Inteiro se for redondo, senão 1 casa decimal."""
    if qtd == int(qtd):
        return f"{int(qtd):,} {unidade}".replace(",", ".")
    return f"{qtd:,.1f} {unidade}".replace(",", "X").replace(".", ",").replace("X", ".")


# ── Cabeçalho ──────────────────────────────────────────────────────────────────
st.title("Suprimentos")
st.caption(
    "Controle de matéria-prima, embalagens, potes, cintas e displays. "
    "Conectado à folha de produção: quando a Etapa E for implementada, "
    "salvar uma folha vai dar baixa automática nos insumos consumidos."
)
st.divider()


# ── Abas ──────────────────────────────────────────────────────────────────────
aba_insumos, aba_bom, aba_movs, aba_necessidades = st.tabs([
    "📦 Insumos",
    "📋 Receitas (BOM)",
    "↕️ Movimentações",
    "🚨 Necessidades do dia",
])


# ════════════════════════════════════════════════════════════════════════════
# ABA 1 — INSUMOS (catálogo + CRUD)
# ════════════════════════════════════════════════════════════════════════════
with aba_insumos:
    st.subheader("📦 Catálogo de insumos")

    # Filtros
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        filtro_cat = st.selectbox(
            "Filtrar por categoria",
            ["(todas)"] + CATEGORIAS_INSUMO,
            key="ins_filtro_cat",
        )
    with col_f2:
        filtro_busca = st.text_input(
            "🔍 Buscar por nome ou código",
            placeholder="ex: coco, plástico, 45g...",
            key="ins_filtro_busca",
        )
    with col_f3:
        st.write("")
        so_alertas = st.checkbox("Só em alerta", key="ins_so_alertas")

    # Carrega lista
    cat_arg = None if filtro_cat == "(todas)" else filtro_cat
    insumos = get_insumos(categoria=cat_arg, somente_ativos=True)

    # Filtro de busca local
    if filtro_busca:
        bq = filtro_busca.lower().strip()
        insumos = [i for i in insumos if bq in i["nome"].lower() or bq in i["codigo"].lower()]

    # Filtro de alerta
    if so_alertas:
        insumos = [i for i in insumos if _status_estoque(i)[0] != "🟢"]

    # Métricas no topo
    todos = get_insumos(somente_ativos=True)
    qtd_total = len(todos)
    qtd_alerta = sum(1 for i in todos if _status_estoque(i)[0] != "🟢")
    qtd_critico = sum(1 for i in todos if _status_estoque(i)[0] == "🔴")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total cadastrados", qtd_total)
    c2.metric("Em alerta", qtd_alerta)
    c3.metric("Crítico (< segurança)", qtd_critico)

    st.divider()

    # Botão de adicionar
    if st.button("➕ Adicionar insumo", type="primary", key="btn_add_insumo"):
        st.session_state["form_insumo"] = {"modo": "criar", "id": None}

    # Tabela de insumos
    if not insumos:
        st.info("Nenhum insumo cadastrado ainda. Clique em **➕ Adicionar insumo** acima pra começar.")
    else:
        rows = []
        for i in insumos:
            emoji, label = _status_estoque(i)
            rows.append({
                "ID": i["id"],
                "Status": emoji,
                "Código": i["codigo"],
                "Nome": i["nome"],
                "Categoria": i["categoria"],
                "Estoque": _formatar_qtd(i["estoque_atual"], i["unidade"]),
                "Mínimo": _formatar_qtd(i["estoque_minimo"], i["unidade"]) if i["estoque_minimo"] else "—",
                "Fornecedor": i["fornecedor"] or "—",
                "Lead time": f"{i['lead_time_dias']}d" if i["lead_time_dias"] else "—",
            })
        df_ins = pd.DataFrame(rows)
        st.dataframe(df_ins, use_container_width=True, hide_index=True)

        # Seletor pra editar/excluir
        st.markdown("##### ✏️ Editar / 🗑️ Excluir insumo")
        col_sel, col_btn1, col_btn2 = st.columns([3, 1, 1])
        with col_sel:
            opcoes_sel = {f"{i['codigo']} — {i['nome']}": i["id"] for i in insumos}
            sel_label = st.selectbox(
                "Escolha um insumo",
                options=list(opcoes_sel.keys()),
                key="ins_sel_edit",
                label_visibility="collapsed",
            )
            sel_id = opcoes_sel.get(sel_label)
        with col_btn1:
            if st.button("✏️ Editar", key="btn_edit_ins"):
                st.session_state["form_insumo"] = {"modo": "editar", "id": sel_id}
        with col_btn2:
            if st.button("🗑️ Excluir", key="btn_del_ins"):
                st.session_state["confirm_del_insumo"] = sel_id

    # Modal-like: formulário de criar/editar
    if "form_insumo" in st.session_state:
        modo = st.session_state["form_insumo"]["modo"]
        ins_id = st.session_state["form_insumo"]["id"]
        with st.expander(f"{'➕ Novo' if modo == 'criar' else '✏️ Editar'} insumo", expanded=True):
            atual = get_insumo(ins_id) if modo == "editar" and ins_id else {}

            f1, f2 = st.columns(2)
            with f1:
                codigo = st.text_input(
                    "Código único *", value=atual.get("codigo", ""),
                    disabled=(modo == "editar"),
                    help="Ex: INS-COCO, EMB-PLAST-45G. Não pode mudar depois de criado.",
                )
                nome = st.text_input("Nome *", value=atual.get("nome", ""))
                cat_default = atual.get("categoria", CATEGORIAS_INSUMO[0])
                categoria = st.selectbox(
                    "Categoria *", CATEGORIAS_INSUMO,
                    index=CATEGORIAS_INSUMO.index(cat_default) if cat_default in CATEGORIAS_INSUMO else 0,
                )
                un_default = atual.get("unidade", "kg")
                unidade = st.selectbox(
                    "Unidade *", UNIDADES_INSUMO,
                    index=UNIDADES_INSUMO.index(un_default) if un_default in UNIDADES_INSUMO else 0,
                )
            with f2:
                estoque_atual_val = st.number_input(
                    "Estoque atual (na criação)" if modo == "criar" else "Estoque atual (read-only)",
                    value=float(atual.get("estoque_atual") or 0),
                    min_value=0.0, step=0.5,
                    disabled=(modo == "editar"),
                    help="Pra mudar estoque depois, usar a aba ↕️ Movimentações.",
                )
                estoque_minimo = st.number_input(
                    "Estoque mínimo (alerta)", value=float(atual.get("estoque_minimo") or 0),
                    min_value=0.0, step=0.5,
                    help="Quando atual < mínimo, fica 🟡 amarelo.",
                )
                estoque_seguranca = st.number_input(
                    "Estoque segurança (crítico)", value=float(atual.get("estoque_seguranca") or 0),
                    min_value=0.0, step=0.5,
                    help="Quando atual < segurança, fica 🔴 vermelho. Geralmente menor que o mínimo.",
                )
                lead_time = st.number_input(
                    "Lead time (dias)", value=int(atual.get("lead_time_dias") or 0),
                    min_value=0, step=1,
                    help="Quantos dias entre pedir ao fornecedor e a entrega chegar.",
                )

            fornecedor = st.text_input("Fornecedor", value=atual.get("fornecedor", ""))
            custo = st.number_input(
                "Custo unitário (R$)", value=float(atual.get("custo_unitario") or 0),
                min_value=0.0, step=0.01, format="%.2f",
            )
            obs = st.text_area("Observações", value=atual.get("obs", ""), height=80)

            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 Salvar", type="primary", use_container_width=True, key="btn_save_ins"):
                    dados = {
                        "codigo": codigo.strip(),
                        "nome": nome.strip(),
                        "categoria": categoria,
                        "unidade": unidade,
                        "estoque_minimo": estoque_minimo,
                        "estoque_seguranca": estoque_seguranca,
                        "fornecedor": fornecedor.strip(),
                        "lead_time_dias": lead_time,
                        "custo_unitario": custo,
                        "obs": obs.strip(),
                    }
                    try:
                        if modo == "criar":
                            dados["estoque_atual"] = estoque_atual_val
                            criar_insumo(dados)
                            st.success(f"✅ Insumo **{codigo}** cadastrado!")
                        else:
                            atualizar_insumo(ins_id, dados)
                            st.success(f"✅ Insumo **{codigo}** atualizado!")
                        invalidar_suprimentos()
                        st.session_state.pop("form_insumo", None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {type(e).__name__}: {e}")
            with col_cancel:
                if st.button("❌ Cancelar", use_container_width=True, key="btn_cancel_ins"):
                    st.session_state.pop("form_insumo", None)
                    st.rerun()

    # Confirmação de exclusão
    if "confirm_del_insumo" in st.session_state:
        ins_id = st.session_state["confirm_del_insumo"]
        ins = get_insumo(ins_id)
        if ins:
            st.warning(
                f"⚠️ Desativar insumo **{ins['codigo']} — {ins['nome']}**? "
                "Não é apagado (movimentações antigas são preservadas), só fica oculto."
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Confirmar desativação", type="primary", use_container_width=True, key="btn_conf_del_ins"):
                    excluir_insumo(ins_id)
                    invalidar_suprimentos()
                    st.session_state.pop("confirm_del_insumo", None)
                    st.success("✅ Desativado.")
                    st.rerun()
            with c2:
                if st.button("❌ Cancelar", use_container_width=True, key="btn_cancel_del_ins"):
                    st.session_state.pop("confirm_del_insumo", None)
                    st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# ABA 2 — RECEITAS (BOM)
# ════════════════════════════════════════════════════════════════════════════
with aba_bom:
    st.subheader("📋 Receitas (Bill of Materials)")
    st.caption(
        "Pra cada produto, lista de insumos que ele consome **por unidade de produção** "
        "(1 bandeja, 1 bolo, 1 tacho). Ex: 1 bandeja de Cocada Tradicional 45g pode "
        "consumir 5 kg de coco ralado + 2 L de leite condensado + 0,5 kg de açúcar."
    )

    insumos_disponiveis = get_insumos(somente_ativos=True)
    if not insumos_disponiveis:
        st.warning(
            "⚠️ Cadastre pelo menos um **insumo** na aba 📦 Insumos antes de definir receitas."
        )
    else:
        produtos = listar_produtos_possiveis()
        # Agrupa por grupo pra dropdown organizado
        opcoes_produto = {p["nome"]: p["chave"] for p in produtos}
        nome_produto = st.selectbox(
            "Selecione o produto pra ver/editar a receita",
            options=list(opcoes_produto.keys()),
            key="bom_produto_sel",
        )
        produto_chave = opcoes_produto[nome_produto]

        bom = get_bom_produto(produto_chave)

        st.divider()
        st.markdown(f"##### Receita de **{nome_produto}**")
        if not bom:
            st.info(
                "Nenhum insumo cadastrado nesta receita ainda. "
                "Use o formulário abaixo pra adicionar o primeiro."
            )
        else:
            df_bom = pd.DataFrame([{
                "ID": l["id"],
                "Insumo": f"{l['codigo']} — {l['insumo_nome']}",
                "Categoria": l["categoria"],
                "Quantidade": _formatar_qtd(l["quantidade"], l["unidade"]),
                "Em estoque": _formatar_qtd(l["estoque_atual"], l["insumo_unidade"]),
                "Obs": l["obs"],
            } for l in bom])
            st.dataframe(df_bom, use_container_width=True, hide_index=True)

            # Excluir linha
            st.markdown("###### 🗑️ Remover linha da receita")
            col_rm, col_rm_btn = st.columns([3, 1])
            with col_rm:
                opc_rm = {f"{l['codigo']} — {l['insumo_nome']} ({_formatar_qtd(l['quantidade'], l['unidade'])})": l["id"] for l in bom}
                rm_label = st.selectbox(
                    "Linha a remover", options=list(opc_rm.keys()),
                    key="bom_rm_sel", label_visibility="collapsed",
                )
            with col_rm_btn:
                if st.button("🗑️ Remover", key="btn_rm_bom"):
                    excluir_bom_linha(opc_rm[rm_label])
                    invalidar_suprimentos()
                    st.success("✅ Linha removida.")
                    st.rerun()

        st.divider()
        st.markdown("##### ➕ Adicionar / atualizar linha")
        with st.form("form_bom", clear_on_submit=True):
            opc_ins = {f"{i['codigo']} — {i['nome']} ({i['unidade']})": i for i in insumos_disponiveis}
            ins_label = st.selectbox("Insumo", options=list(opc_ins.keys()))
            ins_obj = opc_ins[ins_label]
            qtd = st.number_input(
                f"Quantidade ({ins_obj['unidade']}) por 1 unidade do produto",
                min_value=0.0, step=0.1, format="%.3f",
                help=f"Ex: pra 1 bandeja consumir 5 kg de {ins_obj['nome']}, digite 5",
            )
            obs_bom = st.text_input("Observação (opcional)", value="")
            submitted = st.form_submit_button("💾 Salvar linha", type="primary", use_container_width=True)
            if submitted:
                if qtd <= 0:
                    st.error("Quantidade deve ser maior que zero.")
                else:
                    try:
                        upsert_bom_linha(produto_chave, ins_obj["id"], qtd, ins_obj["unidade"], obs_bom)
                        invalidar_suprimentos()
                        st.success(f"✅ Receita atualizada — {ins_obj['nome']}: {qtd} {ins_obj['unidade']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {type(e).__name__}: {e}")


# ════════════════════════════════════════════════════════════════════════════
# ABA 3 — MOVIMENTAÇÕES (entradas/saídas)
# ════════════════════════════════════════════════════════════════════════════
with aba_movs:
    st.subheader("↕️ Movimentações de estoque")
    st.caption(
        "Histórico de todas as entradas (compras, contagem inicial) e saídas (perdas, "
        "ajustes, produção) de cada insumo. Cada movimento atualiza o estoque atual "
        "automaticamente."
    )

    insumos_disponiveis_m = get_insumos(somente_ativos=True)
    if not insumos_disponiveis_m:
        st.warning("⚠️ Cadastre pelo menos um insumo antes de registrar movimentações.")
    else:
        # Filtros
        col_fm1, col_fm2, col_fm3 = st.columns(3)
        with col_fm1:
            opc_ins_filtro = {"(todos)": None}
            opc_ins_filtro.update({f"{i['codigo']} — {i['nome']}": i["id"] for i in insumos_disponiveis_m})
            ins_filtro_label = st.selectbox("Filtrar insumo", options=list(opc_ins_filtro.keys()), key="movs_ins_filtro")
            ins_filtro_id = opc_ins_filtro[ins_filtro_label]
        with col_fm2:
            tipo_filtro = st.selectbox("Tipo", ["(todos)"] + TIPOS_MOVIMENTO, key="movs_tipo_filtro")
            tipo_filtro = None if tipo_filtro == "(todos)" else tipo_filtro
        with col_fm3:
            dias_atras = st.number_input("Últimos N dias", min_value=1, max_value=365, value=30, step=1, key="movs_dias")

        data_inicio = (date.today() - timedelta(days=dias_atras)).isoformat()
        movs = get_movimentos_insumo(
            insumo_id=ins_filtro_id, data_inicio=data_inicio,
            tipo=tipo_filtro, limite=500,
        )

        st.divider()
        if not movs:
            st.info("Nenhuma movimentação encontrada com esses filtros.")
        else:
            df_movs = pd.DataFrame([{
                "Data": m["data"],
                "Tipo": "➕ Entrada" if m["tipo"] == "entrada" else "➖ Saída",
                "Insumo": f"{m['codigo']} — {m['insumo_nome']}",
                "Quantidade": _formatar_qtd(m["quantidade"], m["insumo_unidade"]),
                "Origem": m["origem"] or "—",
                "Referência": m["referencia"] or "—",
                "Obs": m["obs"] or "",
            } for m in movs])
            st.dataframe(df_movs, use_container_width=True, hide_index=True)
            st.caption(f"📊 {len(movs)} movimentações nos últimos {dias_atras} dias")

        st.divider()
        st.markdown("##### ➕ Registrar nova movimentação")
        with st.form("form_mov", clear_on_submit=True):
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                opc_ins_mov = {f"{i['codigo']} — {i['nome']} ({i['unidade']})": i for i in insumos_disponiveis_m}
                ins_mov_label = st.selectbox("Insumo *", options=list(opc_ins_mov.keys()))
                ins_mov_obj = opc_ins_mov[ins_mov_label]
                tipo_mov = st.radio("Tipo *", TIPOS_MOVIMENTO, horizontal=True,
                                     format_func=lambda t: "➕ Entrada" if t == "entrada" else "➖ Saída")
            with mc2:
                qtd_mov = st.number_input(
                    f"Quantidade ({ins_mov_obj['unidade']}) *",
                    min_value=0.0, step=0.5, format="%.2f",
                )
                origem_mov = st.selectbox(
                    "Origem", ORIGENS_MOVIMENTO,
                    help="De onde veio essa movimentação. 'compra' pra entrada de NF; "
                         "'perda' pra descarte; 'ajuste' pra correção de inventário.",
                )
            with mc3:
                data_mov = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
                referencia = st.text_input("Referência (NF, doc, etc)", value="")

            obs_mov = st.text_area("Observações", value="", height=70)
            submitted_mov = st.form_submit_button("💾 Registrar", type="primary", use_container_width=True)
            if submitted_mov:
                if qtd_mov <= 0:
                    st.error("Quantidade deve ser maior que zero.")
                else:
                    try:
                        registrar_movimento_insumo(
                            insumo_id=ins_mov_obj["id"],
                            tipo=tipo_mov,
                            quantidade=qtd_mov,
                            origem=origem_mov,
                            referencia=referencia.strip(),
                            obs=obs_mov.strip(),
                            data=data_mov.isoformat(),
                        )
                        invalidar_suprimentos()
                        st.success(
                            f"✅ {'Entrada' if tipo_mov == 'entrada' else 'Saída'} registrada: "
                            f"{qtd_mov} {ins_mov_obj['unidade']} de {ins_mov_obj['nome']}"
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {type(e).__name__}: {e}")


# ════════════════════════════════════════════════════════════════════════════
# ABA 4 — NECESSIDADES DO DIA (MRP simplificado)
# ════════════════════════════════════════════════════════════════════════════
with aba_necessidades:
    st.subheader("🚨 Necessidades de insumos pra produção do dia")
    st.caption(
        "Cruza a **folha do dia** (ordens de produção da Gestão) com as **receitas (BOM)** "
        "e com o **estoque atual** de insumos. Mostra o que vai faltar e quanto comprar."
    )

    data_sel = st.date_input(
        "Data da folha a analisar",
        value=date.today(),
        format="DD/MM/YYYY",
        key="nec_data",
    )

    necess = calcular_necessidades_do_dia(data_sel.isoformat())

    if not necess:
        st.info(
            "Nenhuma necessidade calculada. Possíveis razões:\n"
            "- Folha do dia não tem ordens de produção (`ord_prod_band` zerado)\n"
            "- Receitas (BOM) não cadastradas para os produtos da folha\n\n"
            "**Solução:** vá em 📋 Receitas e cadastre o consumo de insumos por produto."
        )
    else:
        # Contagem por status
        n_falta = sum(1 for n in necess if n["status"] == "falta")
        n_crit  = sum(1 for n in necess if n["status"] == "critico")
        n_ok    = sum(1 for n in necess if n["status"] == "ok")

        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 Vai faltar", n_falta)
        c2.metric("🟡 Pouca folga", n_crit)
        c3.metric("🟢 Suficiente", n_ok)

        st.divider()

        # Tabela detalhada
        rows = []
        for n in necess:
            emoji = {"falta": "🔴", "critico": "🟡", "ok": "🟢"}[n["status"]]
            rows.append({
                "Status": emoji,
                "Insumo": n["insumo_nome"],
                "Necessidade": _formatar_qtd(n["necessidade"], n["unidade"]),
                "Estoque atual": _formatar_qtd(n["estoque_atual"], n["unidade"]),
                "Saldo": _formatar_qtd(n["saldo"], n["unidade"]),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Alertas detalhados pra faltas
        faltas = [n for n in necess if n["status"] == "falta"]
        if faltas:
            st.markdown("##### ⚠️ Faltas que precisam de compra urgente")
            for n in faltas:
                deficit = -n["saldo"]  # quantidade a comprar
                st.markdown(
                    f"<div class='alerta-falta'>"
                    f"<b>{n['insumo_nome']}</b><br>"
                    f"Necessidade: {_formatar_qtd(n['necessidade'], n['unidade'])} · "
                    f"Tem: {_formatar_qtd(n['estoque_atual'], n['unidade'])} · "
                    f"<b>Comprar pelo menos {_formatar_qtd(deficit, n['unidade'])}</b>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.divider()
    st.caption(
        "💡 **Próximo passo (Etapa E — 22-29/05):** quando você salvar uma folha de "
        "produção, o sistema vai dar **baixa automática** nos insumos consumidos. "
        "Por enquanto, registre saídas manualmente na aba ↕️ Movimentações."
    )
