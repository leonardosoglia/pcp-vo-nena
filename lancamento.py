"""
lancamento.py v2.1 — PCP Vó Nena
Folha de produção digital — espelha o papel físico campo por campo.

Esta versão usa **expanders** (caixas que abrem/fecham) em cada quadro.

LAYOUT (na tela):
    ┌─────────────────────────────────────┬──────────────────────────────┐
    │   FOLHA DE PRODUÇÃO (lado esq.)   │   PAPELZINHO DO JOEL       │
    │  Quadros 1-12 da folha oficial      │  + Orientações do dia        │
    └─────────────────────────────────────┴──────────────────────────────┘
                       [ SALVAR FOLHA COMPLETA]

Sidebar: lista de datas já preenchidas (atalho rápido para histórico).
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
from collections import defaultdict
import sys, os

# Bootstrap: Streamlit Cloud expõe secrets só via st.secrets, mas database.py
# lê os.environ["DATABASE_URL"] em import time. Propaga aqui antes de importar database.
# Preserva env var explícita (dev pode setar manualmente no shell pra rodar scripts).
# Bootstrap defensivo: Streamlit Cloud expõe via st.secrets; HF Spaces usa
# env vars diretas (sem secrets.toml — `in st.secrets` levantaria
# StreamlitSecretNotFoundError). Try/except cobre os dois casos.
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

sys.path.insert(0, os.path.dirname(__file__))
# Usa cached_db (wrapper @st.cache_data sobre database) — reduz latência
# percebida no app em produção. Invalidação manual após save/delete.
import cached_db as db
from cached_db import (
    init_db, get_folha_cocada, get_folha_palha, get_pm_balas_doces,
    get_papelzinho_joel, get_pvirar_ideal, get_metas_45g, get_metas_mini_pet,
    list_datas_folha, salvar_folha_completa,
    excluir_folha,
    SABORES_COCADA, SABORES_PALHA, SIGLA_COCADA, SIGLA_PALHA,
)


# Pre-warm dos caches mais consultados — paga o custo de TCP+TLS+round-trip
# Atlântico UMA vez no startup, em vez de na primeira interação do usuário.
# Crítico no HF Spaces (us-east-1) com Supabase (sa-east-1), latência ~150 ms/query.
# Total ~1 s no startup, mas usuário vê navegação instantânea depois (cache hit).
# Silencia exceções: se o banco estiver lento/indisponível, app sobe mesmo assim
# e o lazy load entra em ação no primeiro acesso.
@st.cache_resource(show_spinner=False)
def _prewarm_cache():
    try:
        list_datas_folha()
        get_metas_45g()
        get_metas_mini_pet()
        get_pvirar_ideal()
    except Exception:
        pass
    return True


_prewarm_cache()

# Mapa weekday() -> coluna da tabela metas_45g
DIAS_COL_METAS = {0: "segunda", 1: "terca", 2: "quarta", 3: "quinta", 4: "sexta"}

# Palha 50g só existe em T, L, CH (não em Cookies nem Limão)
SABORES_PALHA_50G = {"TRADICIONAL", "LEITE EM PÓ", "CHURROS"}

# Calendário de prioridade de corte definido pela Gestão (descoberto via entrevista)
CALENDARIO_CORTE = {
    0: "45g",          # segunda
    1: "Mini + Pet",   # terça
    2: "45g",          # quarta
    3: "45g",          # quinta
    4: "Mini + Pet",   # sexta
    5: None,           # sábado — sem corte programado
    6: None,           # domingo
}

# ── Configuração da página ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Folha de Produção • Vó Nena",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tema visual centralizado (Inter font + paleta clean)
from ui_theme import aplicar_tema
aplicar_tema()

init_db()

DIAS_PT = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta",
           4: "Sexta", 5: "Sábado", 6: "Domingo"}

MESES_PT = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

# Meta de displays de palha 50g por dia da semana
# (cada display = 10 palhas: 4 Tradicional + 4 Leite em pó + 2 Churros)
META_DISPLAYS_PALHA = {
    "Segunda": 32, "Terça": 36, "Quarta": 32, "Quinta": 32, "Sexta": 36,
    "Sábado": 0, "Domingo": 0,
}


def folha_existe(data_str: str) -> bool:
    # Reaproveita o cache da lista de datas: se a data está na lista, tem folha.
    # Antes: 4 queries por verificação. Agora: 0 (hit no cache de list_datas_folha).
    return data_str in list_datas_folha()


def hdr_cell(col, txt):
    # Header de coluna — 12px, peso 700, cor brand. Menor que o body (13px)
    # mas destacado pela cor — hierarquia sem virar "zoom".
    col.markdown(
        f"<div style='font-size:12px;font-weight:700;color:#7B341E;"
        f"padding:0 0 3px 0;white-space:nowrap;letter-spacing:-0.01em;"
        f"line-height:1.2;'>{txt}</div>",
        unsafe_allow_html=True,
    )


def label_sabor(col, sabor):
    # Label de linha — 12px, peso 700, cor dark. Toda a tabela da folha usa
    # 12px (hdr_cell + label_sabor + inputs) — densa e uniforme, 1px abaixo
    # do body (13px). nowrap impede quebra em 2 linhas.
    col.markdown(
        f"<div style='padding-top:7px;font-size:12px;font-weight:700;color:#1a1a1a;"
        f"white-space:nowrap;letter-spacing:-0.015em;line-height:1.2;'>{sabor}</div>",
        unsafe_allow_html=True,
    )


def celula_vazia(col, motivo="—"):
    col.markdown(
        f"<div style='padding-top:7px;font-size:12px;color:#bbb;text-align:center;"
        f"line-height:1.2;'>{motivo}</div>",
        unsafe_allow_html=True,
    )


def num_input_compact(col, key, valor_inicial, step=None):
    """Input numérico compacto pra folha.

    Decisão de UX (19/05/2026): campos vazios em vez de zero pré-preenchido.
    - valor_inicial em (None, 0) → campo aparece VAZIO (placeholder)
    - valor_inicial > 0 → mostra valor real
    Retorna 0 quando vazio (compatibilidade com código a jusante que faz int()).

    step=None desabilita os botões +/- do widget (setas do teclado movem
    cursor no texto em vez de incrementar valor). Combinado com value=None,
    dá experiência de planilha — usuário tabula entre células e digita números.
    """
    valor_int = int(valor_inicial or 0)
    valor_exibir = None if valor_int == 0 else valor_int
    with col:
        v = st.number_input(
            label=key, min_value=0,
            value=valor_exibir,
            step=step, key=key,
            placeholder="",
            label_visibility="collapsed",
        )
        return int(v) if v is not None else 0


def estilo_dif(v):
    try:
        n = float(v)
        if n >= 0: return "color:#065F46;font-weight:700;background:#ECFDF5;"
        return "color:#7F1D1D;font-weight:700;background:#FEF2F2;"
    except Exception:
        return "color:#999;"


# ── Sidebar ────────────────────────────────────────────────────────────────────
def _fmt_data_pt(d_str):
    """Formata YYYY-MM-DD → '08/05/2026 (Sexta)'."""
    try:
        do = datetime.strptime(d_str, "%Y-%m-%d").date()
        return f"{do.strftime('%d/%m/%Y')} ({DIAS_PT[do.weekday()]})"
    except ValueError:
        return d_str


# ════════════════════════════════════════════════════════════════════════════
# NAVEGAÇÃO DE FOLHAS — barra superior na própria página (não sidebar)
# Antes (até 26/05) ficava no sidebar e brigava com o st.navigation do app.py.
# Movida pra dentro do conteúdo da página, em barra horizontal compacta.
# ════════════════════════════════════════════════════════════════════════════
with st.container(border=True):
    col_nova, col_existentes, col_data_atual = st.columns([1.5, 2, 2])

    with col_nova:
        with st.popover("Abrir / criar folha de outra data", width='stretch'):
            st.caption("Escolha a data — passada, hoje ou futura.")
            nova_data = st.date_input(
                "Data:",
                value=date.today(),
                format="DD/MM/YYYY",
                key="nova_folha_data",
            )
            if st.button("Abrir folha desta data", width='stretch', type="primary", key="btn_nova"):
                st.session_state["data_selecionada"] = nova_data.isoformat()
                st.rerun()
            st.caption("Se ainda não existir, abre vazia pra preencher.")

    with col_existentes:
        with st.popover("Folhas anteriores", width='stretch'):
            datas = list_datas_folha()
            if not datas:
                st.info("Nenhuma folha salva ainda.")
            else:
                st.caption(f"{len(datas)} folha(s) no histórico. Clique pra abrir.")

                # Agrupar por (ano, mês) — mais recente primeiro
                por_mes = defaultdict(list)
                for d in datas:
                    try:
                        do = datetime.strptime(d, "%Y-%m-%d").date()
                        por_mes[(do.year, do.month)].append(d)
                    except ValueError:
                        por_mes[(0, 0)].append(d)

                meses_ordenados = sorted(por_mes.keys(), reverse=True)

                for i, (ano, mes) in enumerate(meses_ordenados):
                    folhas_mes = por_mes[(ano, mes)]
                    nome_mes = MESES_PT.get(mes, str(mes))
                    label_mes = f"{nome_mes} / {ano}  ·  {len(folhas_mes)} folha{'s' if len(folhas_mes) > 1 else ''}"
                    # Primeiro mês (mais recente) abre por padrão
                    with st.expander(label_mes, expanded=(i == 0)):
                        for d in folhas_mes:
                            label = _fmt_data_pt(d)
                            cols = st.columns([5, 1])
                            with cols[0]:
                                if st.button(label, key=f"goto_{d}", width='stretch'):
                                    st.session_state["data_selecionada"] = d
                                    st.rerun()
                            with cols[1]:
                                with st.popover("⋮", width='stretch'):
                                    st.caption(f"Folha de {_fmt_data_pt(d)}")
                                    if st.button("Abrir / Editar", key=f"act_edit_{d}", width='stretch'):
                                        st.session_state["data_selecionada"] = d
                                        st.rerun()
                                    try:
                                        from exportar import gerar_xlsx_folha
                                        xlsx_bytes = gerar_xlsx_folha(d)
                                        st.download_button(
                                            "Exportar Excel",
                                            data=xlsx_bytes,
                                            file_name=f"folha_pcp_vonena_{d}.xlsx",
                                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            key=f"act_xlsx_{d}",
                                            width='stretch',
                                        )
                                    except Exception as e:
                                        st.caption(f"Erro Excel: {e}")
                                    if st.button("Excluir folha", key=f"act_del_{d}", width='stretch'):
                                        st.session_state["confirm_excluir"] = d
                                        st.rerun()

    with col_data_atual:
        data_atual_str = st.session_state.get("data_selecionada", date.today().isoformat())
        st.markdown(
            f"<div style='padding-top:6px;text-align:right;'>"
            f"<span style='color:#888;font-size:0.85em;'>Editando folha de</span><br>"
            f"<strong style='font-size:1.1em;'>{_fmt_data_pt(data_atual_str)}</strong>"
            "</div>",
            unsafe_allow_html=True,
        )

# Confirmação de exclusão (mostrada inline na página quando confirm_excluir está setado)
pendente = st.session_state.get("confirm_excluir")
if pendente:
    st.warning(f"Excluir folha de **{_fmt_data_pt(pendente)}**? Não há undo.")
    cc1, cc2, _ = st.columns([1, 1, 4])
    with cc1:
        if st.button("Confirmar exclusão", type="primary", width='stretch', key="btn_confirm_del"):
            try:
                excluir_folha(pendente)
                db.invalidar_folha(pendente)
                st.session_state.pop("confirm_excluir", None)
                if st.session_state.get("data_selecionada") == pendente:
                    st.session_state.pop("data_selecionada", None)
                st.success(f"Folha {_fmt_data_pt(pendente)} excluída.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao excluir: {e}")
    with cc2:
        if st.button("Cancelar", width='stretch', key="btn_cancel_del"):
            st.session_state.pop("confirm_excluir", None)
            st.rerun()

    st.divider()
    st.markdown("### Sobre")
    st.caption(
        "Folha de produção digital. Espelha o papel físico campo por campo.\n\n"
        "Cada quadro abre quando você clica nele.\n\n"
        "**+ Adicionar nova folha** — botão no topo.\n"
        "**⋮ Editar / Excluir** — em cada folha da lista."
    )

# ── Cabeçalho ──────────────────────────────────────────────────────────────────
col_t, col_d = st.columns([5, 2])
with col_t:
    st.title("Folha de Produção — Doces Vó Nena")
with col_d:
    st.markdown(
        "<div style='margin-top:24px;text-align:right;color:#C05621;font-weight:700;font-size:15px;'>"
        "PCP Vó Nena · v2.1</div>",
        unsafe_allow_html=True,
    )

# ── Date picker + status ───────────────────────────────────────────────────────
default_data = st.session_state.get("data_selecionada")
if default_data:
    try:
        default_dt = datetime.strptime(default_data, "%Y-%m-%d").date()
    except ValueError:
        default_dt = date.today()
else:
    default_dt = date.today()

col_dp, col_st = st.columns([2, 5])
with col_dp:
    data_sel = st.date_input(
        "Data da folha",
        value=default_dt,
        format="DD/MM/YYYY",
        help="Escolha qualquer data — passada, hoje ou futura.",
    )
data_str = data_sel.isoformat()
nome_dia = DIAS_PT[data_sel.weekday()]
data_label = f"{data_sel.strftime('%d/%m/%Y')} ({nome_dia})"

with col_st:
    if folha_existe(data_str):
        st.markdown(
            f"<div class='status-box-edit'> <b>Editando folha existente</b> — "
            f"{data_label}. Clique nos quadros abaixo para abrir e editar.</div>",
            unsafe_allow_html=True,
        )
    else:
        if data_sel == date.today():
            box = "novo"; icon = ""; tag = "Nova folha de hoje"
        elif data_sel < date.today():
            box = "novo"; icon = ""; tag = "Nova folha (preenchimento retroativo)"
        else:
            box = "edit"; icon = ""; tag = "Folha futura"
        st.markdown(
            f"<div class='status-box-{box}'>{icon} <b>{tag}</b> — {data_label}. "
            f"Clique nos quadros abaixo e preencha. Salve no final da página.</div>",
            unsafe_allow_html=True,
        )

# Calendário de prioridade de corte do dia (descoberto via entrevista com Leonardo)
prioridade_corte = CALENDARIO_CORTE.get(data_sel.weekday())
if prioridade_corte:
    st.markdown(
        f"<div style='background:#FEF3C7; border-left:5px solid #D97706; "
        f"padding:8px 14px; border-radius:6px; color:#92400E; font-weight:600; margin:6px 0;'>"
        f" <b>{nome_dia}</b> — dia de prioridade de corte: <b>{prioridade_corte}</b> "
        f"<span style='font-weight:400; font-size:10px;'>(referência da Gestão; não exclusivo)</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.divider()

# ── Carregar dados existentes (4 queries paralelas em Postgres, 1 round-trip) ──
_folha = db.get_folha_completa(data_str)
dados_cocada = {r["sabor"]: r for r in _folha["cocada"]}
dados_palha = {r["sabor"]: r for r in _folha["palha"]}
papelzinho_existente = {r["sabor"]: r for r in _folha["papelzinho"]}
pbd_atual = _folha["pmbd"] or {}

# ══════════════════════════════════════════════════════════════════════════════
# CONTEÚDO PRINCIPAL — duas colunas espelhando a folha física
# ══════════════════════════════════════════════════════════════════════════════
with st.form("folha_completa", border=False):
    col_folha, col_papel = st.columns([3, 2])

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║ LADO DIREITO: PAPELZINHO DO JOEL + ORIENTAÇÕES                           ║
    # ║ Renderizado primeiro pra alimentar derivados em tempo real               ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    with col_papel:
        st.markdown("### Papelzinho do Joel & Orientações")

        with st.expander("Papelzinho do Joel — 5 colunas × 6 sabores", expanded=False):
            st.caption(
                "Contagem matinal da Produção · **45g, 30g (=Mini)** em unidades · "
                "**P (Pet), PV, V** em **bandejas** · Z não tem 45g. "
                "Rendimento Pet: 30 und/band (T,L,B,C,P) · 60 und/band (Z)."
            )
            cols_h_pj = st.columns([0.6, 1, 1, 0.9, 0.9, 0.9])
            for col, lbl in zip(cols_h_pj, ["", "45g (und)", "30g (und)", "P (band)", "PV (band)", "V (band)"]):
                hdr_cell(col, lbl)

            papel_joel_v = {}
            for sabor in SABORES_COCADA:
                d = papelzinho_existente.get(sabor, {})
                cols = st.columns([0.6, 1, 1, 0.9, 0.9, 0.9])
                sigla = SIGLA_COCADA.get(sabor, sabor[:1])
                cols[0].markdown(
                    f"<div style='padding-top:7px;font-weight:700;color:#7B341E;font-size:14px;'>{sigla}</div>",
                    unsafe_allow_html=True,
                )
                if sabor == "ZERO":
                    celula_vazia(cols[1])
                    j45 = 0
                else:
                    j45 = num_input_compact(cols[1], f"joel_45g_{sabor}_{data_str}",  d.get("joel_45g"))
                jmi = num_input_compact(cols[2], f"joel_mini_{sabor}_{data_str}", d.get("joel_mini"))
                jpt = num_input_compact(cols[3], f"joel_pet_{sabor}_{data_str}",  d.get("joel_pet"))
                jpv = num_input_compact(cols[4], f"joel_pv_{sabor}_{data_str}",   d.get("joel_pv"))
                jv  = num_input_compact(cols[5], f"joel_v_{sabor}_{data_str}",    d.get("joel_v"))
                papel_joel_v[sabor] = {
                    "joel_45g": j45, "joel_mini": jmi, "joel_pet": jpt,
                    "joel_pv": jpv, "joel_v": jv,
                }
            st.caption(
                " Os valores acima alimentam **Cortados ②**, **Viradas** e **P/Virar** "
                "no lado esquerdo em tempo real."
            )

        with st.expander("Orientações do dia", expanded=False):
            st.caption(
                "Avisos da Gestão para a equipe. Pode mencionar quem é o destinatário no próprio texto "
                "(ex: \"Corte: cortar cumbucas após 14h · Embalagem: até 16h e depois sobe pra cortar bala\")."
            )
            # Caixa única — dados antigos de obs_joel/gil/leonilia ficam concatenados se existirem
            valor_inicial = pbd_atual.get("obs", "") or ""
            # Migra orientações antigas das 4 caixas pra 1 só (read-only de retrocompat)
            # Campos legados do banco mantêm nomes antigos; labels exibidos usam departamentos.
            for legado_campo, legado_label in [("obs_joel", "Produção"), ("obs_gil", "Corte"), ("obs_leonilia", "Embalagem")]:
                extra = pbd_atual.get(legado_campo, "")
                if extra:
                    valor_inicial = (valor_inicial + ("\n" if valor_inicial else "")
                                     + f"[{legado_label}]: {extra}")

            obs_geral = st.text_area(
                "Orientações",
                value=valor_inicial,
                height=180, key=f"obs_geral_{data_str}",
                placeholder=(
                    "Ex:\n"
                    "Gil: corta cumbucas após 14h\n"
                    "Joel: avisa o Paulo pra virar bandejas\n"
                    "Popô: embala até 16h e depois sobe pra cortar bala\n"
                    "Geral: amanhã feriado, adiantar produção"
                ),
            )
            # Mantemos os campos antigos apenas pra compatibilidade — vão zerados ao salvar
            obs_joel_v = ""
            obs_gil_v = ""
            obs_leonilia_v = ""

        # ── Bala de Doce de Leite (papelzinho separado do Joel) ──────────────────
        with st.expander("Bala de Doce de Leite — papelzinho do Joel", expanded=False):
            st.caption(
                "Contagem do papelzinho separado da Produção. Total = P/cortar + Cortadas (automático)."
            )
            cols_bdl = st.columns([1, 1, 1])
            with cols_bdl[0]:
                st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;'>P/ cortar</div>", unsafe_allow_html=True)
                bala_p_cortar = st.number_input(
                    label="bala_p_cortar", min_value=0,
                    value=int(pbd_atual.get("bala_p_cortar") or 0),
                    key=f"bala_p_cortar_{data_str}", label_visibility="collapsed",
                )
            with cols_bdl[1]:
                st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;'> Cortadas</div>", unsafe_allow_html=True)
                bala_cortadas = st.number_input(
                    label="bala_cortadas", min_value=0,
                    value=int(pbd_atual.get("bala_cortadas") or 0),
                    key=f"bala_cortadas_{data_str}", label_visibility="collapsed",
                )
            with cols_bdl[2]:
                total_bala = bala_p_cortar + bala_cortadas
                st.markdown(
                    f"<div style='font-size:12px;font-weight:700;color:#7B341E;'>Σ Total</div>"
                    f"<div style='font-size:18px;font-weight:800;color:#C05621;padding:6px 0;'>{total_bala}</div>",
                    unsafe_allow_html=True,
                )

        # ── Pão de Mel inacabado + Bolos + Cocada Assada ─────────────────────────
        with st.expander("Pão de Mel (inacabado + bolos) · Cocada Assada", expanded=False):
            st.caption(
                " **PM inacabado** em unidades · **Bolos** (1 bolo = 70 und de PM). "
                "**ASS / Cocada Assada** é outro produto independente, em unidades."
            )
            cols_pm = st.columns([1, 1, 1])
            with cols_pm[0]:
                st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;'> PM inacabado (und)</div>", unsafe_allow_html=True)
                pm_inacabado = st.number_input(
                    label="pm_inacabado_und", min_value=0,
                    value=int(pbd_atual.get("pm_inacabado_und") or 0),
                    key=f"pm_inacabado_{data_str}", label_visibility="collapsed",
                )
            with cols_pm[1]:
                st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;'> Bolos (×70)</div>", unsafe_allow_html=True)
                pm_bolos = st.number_input(
                    label="pm_bolos", min_value=0,
                    value=int(pbd_atual.get("pm_bolos") or 0),
                    key=f"pm_bolos_{data_str}", label_visibility="collapsed",
                )
            with cols_pm[2]:
                total_pm_disp = pm_inacabado + (pm_bolos * 70)
                st.markdown(
                    f"<div style='font-size:12px;font-weight:700;color:#7B341E;'>Σ Total disponível</div>"
                    f"<div style='font-size:14px;font-weight:800;color:#C05621;padding:6px 0;'>{total_pm_disp} und</div>"
                    f"<div style='font-size:11px;color:#888;'>= {pm_inacabado} + ({pm_bolos}×70)</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;margin-top:12px;'> Cocada Assada — ASS (und)</div>", unsafe_allow_html=True)
            st.caption("Produto independente do PM, apesar de aparecer junto no papelzinho.")
            cocada_assada = st.number_input(
                label="cocada_assada_und", min_value=0,
                value=int(pbd_atual.get("cocada_assada_und") or 0),
                key=f"cocada_assada_{data_str}", label_visibility="collapsed",
            )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║ LADO ESQUERDO: folha de produção oficial                                 ║
    # ╚══════════════════════════════════════════════════════════════════════════╝
    with col_folha:
        st.markdown("### Folha de Produção Oficial")

        # ── 1. EMBALADOS — Cocada ────────────────────────────────────────────────
        with st.expander("Embalados — Cocada", expanded=False):
            st.caption("Estoque embalado · **45g, Mini, Pet, Potes** em unidades. Z não tem 45g.")
            cols_h = st.columns([2.0, 1, 1, 1, 1, 1])
            for col, lbl in zip(cols_h, ["Sabor", "45g (und)", "Mini (und)", "Pet (und)", "Potes 260g", "Potes 605g"]):
                hdr_cell(col, lbl)
            emb_v = {}
            for sabor in SABORES_COCADA:
                d = dados_cocada.get(sabor, {})
                cols = st.columns([2.0, 1, 1, 1, 1, 1])
                label_sabor(cols[0], sabor)
                if sabor == "ZERO":
                    celula_vazia(cols[1]); v45 = 0
                else:
                    v45 = num_input_compact(cols[1], f"emb_45g_{sabor}_{data_str}", d.get("emb_45g"))
                vmi  = num_input_compact(cols[2], f"emb_mini_{sabor}_{data_str}",  d.get("emb_mini"))
                vpt  = num_input_compact(cols[3], f"emb_pet_{sabor}_{data_str}",   d.get("emb_pet"))
                vp26 = num_input_compact(cols[4], f"emb_p260_{sabor}_{data_str}", d.get("emb_potes_260g"))
                vp60 = num_input_compact(cols[5], f"emb_p605_{sabor}_{data_str}", d.get("emb_potes_605g"))
                emb_v[sabor] = {
                    "emb_45g": v45, "emb_mini": vmi, "emb_pet": vpt,
                    "emb_potes_260g": vp26, "emb_potes_605g": vp60,
                }

        # ── 2. CORTADOS ① — Cocada ───────────────────────────────────────────────
        with st.expander("Cortados ① — Cocada (em unidades)", expanded=False):
            st.caption(
                "**①** = cortados hoje (lado embalagem) em **unidades** · "
                "**②** = ① + Embalados + Joel · **③** = ② − Parâmetro Real."
            )
            cols_h2 = st.columns([1.6, 1, 1, 1])
            for col, lbl in zip(cols_h2, ["Sabor", "① 45g (und)", "① Mini (und)", "① Pet (und)"]):
                hdr_cell(col, lbl)
            cort_v = {}
            for sabor in SABORES_COCADA:
                d = dados_cocada.get(sabor, {})
                cols = st.columns([1.6, 1, 1, 1])
                label_sabor(cols[0], sabor)
                if sabor == "ZERO":
                    celula_vazia(cols[1]); c1_45 = 0
                else:
                    c1_45 = num_input_compact(cols[1], f"cort1_45g_{sabor}_{data_str}", d.get("cort1_45g"))
                c1_mi = num_input_compact(cols[2], f"cort1_mini_{sabor}_{data_str}", d.get("cort1_mini"))
                c1_pt = num_input_compact(cols[3], f"cort1_pet_{sabor}_{data_str}",  d.get("cort1_pet"))
                cort_v[sabor] = {"cort1_45g": c1_45, "cort1_mini": c1_mi, "cort1_pet": c1_pt}

        # ── 3. CORTE DE COCADA — Ordens ──────────────────────────────────────────
        with st.expander("Corte de Cocada — Ordens (bandejas)", expanded=False):
            st.caption(
                "Em **bandejas** · conversão para unidades em cinza ao lado. "
                "1 band 45g=100 · Mini=150 · Pet=30 (Z=60)."
            )
            cols_h3 = st.columns([2.0, 1, 0.7, 1, 0.7, 1, 0.7])
            for col, lbl in zip(cols_h3, ["Sabor", "45g (band)", "= und", "Mini (band)", "= und", "Pet (band)", "= und"]):
                hdr_cell(col, lbl)
            ord_corte_v = {}
            for sabor in SABORES_COCADA:
                d = dados_cocada.get(sabor, {})
                cols = st.columns([2.0, 1, 0.7, 1, 0.7, 1, 0.7])
                label_sabor(cols[0], sabor)
                if sabor == "ZERO":
                    celula_vazia(cols[1]); celula_vazia(cols[2]); oc45 = 0
                else:
                    oc45 = num_input_compact(cols[1], f"ord_corte_45g_{sabor}_{data_str}", d.get("ord_corte_45g"))
                    cols[2].markdown(
                        f"<div style='padding-top:7px;color:#888;font-size:10px;'>{oc45 * 100:,}</div>",
                        unsafe_allow_html=True,
                    )
                ocm = num_input_compact(cols[3], f"ord_corte_mini_{sabor}_{data_str}", d.get("ord_corte_mini"))
                cols[4].markdown(
                    f"<div style='padding-top:7px;color:#888;font-size:10px;'>{ocm * 150:,}</div>",
                    unsafe_allow_html=True,
                )
                ocp = num_input_compact(cols[5], f"ord_corte_pet_{sabor}_{data_str}", d.get("ord_corte_pet"))
                rend_pet = 60 if sabor == "ZERO" else 30
                cols[6].markdown(
                    f"<div style='padding-top:7px;color:#888;font-size:10px;'>{ocp * rend_pet:,}</div>",
                    unsafe_allow_html=True,
                )
                ord_corte_v[sabor] = {
                    "ord_corte_45g": oc45,
                    "ord_corte_mini": ocm,
                    "ord_corte_pet": ocp,
                }

        # ── 4. PARÂMETRO REAL DO DIA (45g + Mini + Pet) ──────────────────────────
        with st.expander("Parâmetro Real do dia — Ajuste da Gestão (45g · Mini · Pet)", expanded=False):
            st.caption(
                "**Base** vem da tabela de referência · **Ajuste** = +/- da Gestão (passos de 100) · "
                "**Real** alimenta a coluna ③ do Cortados acima."
            )
            metas_dia = {r["sabor"]: r for r in get_metas_45g()}
            col_metas = DIAS_COL_METAS.get(data_sel.weekday())
            metas_mp = {r["sabor"]: r for r in get_metas_mini_pet()}

            if col_metas is None:
                st.warning(
                    f" {nome_dia} — sem produção de 45g programada (tabela cobre Seg-Sex)."
                )

            tab_45, tab_mi, tab_pt = st.tabs(["45g", "Mini (30g)", "Pet"])

            param_real_v = {}

            # --- Aba 45g ---
            with tab_45:
                st.caption(f"Base do dia da semana ({nome_dia}) · Z não tem 45g.")
                ch = st.columns([1.6, 1, 1, 1])
                for c, l in zip(ch, ["Sabor", "Base", "Ajuste (+/-)", "= Real"]):
                    hdr_cell(c, l)
                param_real_v["45g"] = {}
                for sabor in SABORES_COCADA:
                    if sabor == "ZERO":
                        continue
                    d = dados_cocada.get(sabor, {})
                    cols = st.columns([1.6, 1, 1, 1])
                    label_sabor(cols[0], sabor)
                    base = int(metas_dia.get(sabor, {}).get(col_metas) or 0) if col_metas else 0
                    cols[1].markdown(f"<div style='padding-top:7px;color:#666;'>{base:,}</div>", unsafe_allow_html=True)
                    with cols[2]:
                        salvo = int(d.get("param_real_45g") or 0)
                        aj_def = (salvo - base) if salvo else 0
                        aj = st.number_input(
                            label=f"aj45_{sabor}", value=aj_def, step=100,
                            key=f"aj45_{sabor}_{data_str}", label_visibility="collapsed",
                        )
                    real = base + aj
                    cor = "#065F46" if real >= base and real > 0 else ("#7F1D1D" if real < base else "#1a1a1a")
                    cols[3].markdown(
                        f"<div style='padding-top:7px;font-weight:700;color:{cor};'>{real:,}</div>",
                        unsafe_allow_html=True,
                    )
                    param_real_v["45g"][sabor] = real
                param_real_v["45g"]["ZERO"] = 0

            # --- Aba Mini (30g) ---
            with tab_mi:
                st.caption(
                    "Base **fixa por sabor** (todos os dias) · "
                    "Z Mini = igual ao **45g do Leite Condensado do dia** (dinâmico)."
                )
                ch = st.columns([1.6, 1, 1, 1])
                for c, l in zip(ch, ["Sabor", "Base", "Ajuste (+/-)", "= Real"]):
                    hdr_cell(c, l)
                param_real_v["mini"] = {}
                for sabor in SABORES_COCADA:
                    d = dados_cocada.get(sabor, {})
                    cols = st.columns([1.6, 1, 1, 1])
                    label_sabor(cols[0], sabor)
                    # Base Mini
                    if sabor == "ZERO":
                        # Z mini = 45g do L do dia
                        base = param_real_v["45g"].get("LEITE CONDENSADO", 0)
                        cols[1].markdown(
                            f"<div style='padding-top:7px;color:#C05621;font-size:10px;'>= L 45g/dia · {base:,}</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        raw = metas_mp.get(sabor, {}).get("mini", "0")
                        try:
                            base = int(str(raw).strip())
                        except (ValueError, TypeError):
                            base = 0
                        cols[1].markdown(f"<div style='padding-top:7px;color:#666;'>{base:,}</div>", unsafe_allow_html=True)

                    with cols[2]:
                        salvo = int(d.get("param_real_mini") or 0)
                        aj_def = (salvo - base) if salvo else 0
                        aj = st.number_input(
                            label=f"ajmi_{sabor}", value=aj_def, step=100,
                            key=f"ajmi_{sabor}_{data_str}", label_visibility="collapsed",
                        )
                    real = base + aj
                    cor = "#065F46" if real >= base and real > 0 else ("#7F1D1D" if real < base else "#1a1a1a")
                    cols[3].markdown(
                        f"<div style='padding-top:7px;font-weight:700;color:{cor};'>{real:,}</div>",
                        unsafe_allow_html=True,
                    )
                    param_real_v["mini"][sabor] = real

            # --- Aba Pet ---
            with tab_pt:
                st.caption("Base **fixa por sabor** (todos os dias). Z Pet = 300.")
                ch = st.columns([1.6, 1, 1, 1])
                for c, l in zip(ch, ["Sabor", "Base", "Ajuste (+/-)", "= Real"]):
                    hdr_cell(c, l)
                param_real_v["pet"] = {}
                for sabor in SABORES_COCADA:
                    d = dados_cocada.get(sabor, {})
                    cols = st.columns([1.6, 1, 1, 1])
                    label_sabor(cols[0], sabor)
                    base = int(metas_mp.get(sabor, {}).get("pet") or 0)
                    cols[1].markdown(f"<div style='padding-top:7px;color:#666;'>{base:,}</div>", unsafe_allow_html=True)
                    with cols[2]:
                        salvo = int(d.get("param_real_pet") or 0)
                        aj_def = (salvo - base) if salvo else 0
                        aj = st.number_input(
                            label=f"ajpt_{sabor}", value=aj_def, step=10,
                            key=f"ajpt_{sabor}_{data_str}", label_visibility="collapsed",
                        )
                    real = base + aj
                    cor = "#065F46" if real >= base and real > 0 else ("#7F1D1D" if real < base else "#1a1a1a")
                    cols[3].markdown(
                        f"<div style='padding-top:7px;font-weight:700;color:{cor};'>{real:,}</div>",
                        unsafe_allow_html=True,
                    )
                    param_real_v["pet"][sabor] = real

        # ── 5. CORTADOS ②③ — derivado (read-only) ────────────────────────────────
        with st.expander("Cortados ② ③ — Cálculos derivados (read-only)", expanded=False):
            st.caption(
                "Atualiza em tempo real conforme você edita Embalados, Cortados① e Papelzinho do Joel."
            )
            st.markdown(
                "<div style='background:#F3F4F6;border-left:5px solid #6B7280;"
                "padding:8px 14px;border-radius:6px;color:#374151;font-size:10px;margin:6px 0;'>"
                "<b>Nota — caso eventual de duplicação:</b> em alguns dias, uma célula de "
                "<b>Mini (30g)</b> ou <b>P (Pet)</b> do Papelzinho do Joel pode já ter sido enviada "
                "pra sala de embalagem antes da folha ser fechada — nesse caso, o valor aparece "
                "duplicado no Cortados ②. No papel, essas células levam um asterisco <code>*</code>. "
                "Quando isso acontecer, anote pra revisar manualmente. "
                "<b>Feature futura:</b> sinalização por célula + baixa automática."
                "</div>",
                unsafe_allow_html=True,
            )
            rows_calc = []
            for sabor in SABORES_COCADA:
                pj = papel_joel_v.get(sabor, {})
                e = emb_v[sabor]
                c = cort_v[sabor]
                joel_45 = int(pj.get("joel_45g") or 0)
                joel_mi = int(pj.get("joel_mini") or 0)
                # joel_pet está em BANDEJAS — converter pra unidades:
                joel_pt_band = int(pj.get("joel_pet") or 0)
                rend_pet = 60 if sabor == "ZERO" else 30
                joel_pt_und = joel_pt_band * rend_pet
                c2_45 = c["cort1_45g"] + e["emb_45g"] + joel_45
                c2_mi = c["cort1_mini"] + e["emb_mini"] + joel_mi
                c2_pt = c["cort1_pet"] + e["emb_pet"] + joel_pt_und
                param_45 = param_real_v["45g"].get(sabor, 0)
                param_mi = param_real_v["mini"].get(sabor, 0)
                param_pt = param_real_v["pet"].get(sabor, 0)
                c3_45 = (c2_45 - param_45) if param_45 else None
                c3_mi = (c2_mi - param_mi) if param_mi else None
                c3_pt = (c2_pt - param_pt) if param_pt else None
                rows_calc.append({
                    "Sabor":   sabor,
                    "② 45g":   None if sabor == "ZERO" else c2_45,
                    "③ 45g":   None if sabor == "ZERO" else c3_45,
                    "② Mini":  c2_mi,
                    "③ Mini":  c3_mi,
                    "② Pet":   c2_pt,
                    "③ Pet":   c3_pt,
                })
            df_calc = pd.DataFrame(rows_calc).convert_dtypes()
            st.dataframe(
                df_calc.style.map(estilo_dif, subset=["③ 45g", "③ Mini", "③ Pet"]),
                width='stretch', hide_index=True,
                column_config={
                    "Sabor":  st.column_config.TextColumn(width=92),
                    "② 45g":  st.column_config.NumberColumn(width=44),
                    "③ 45g":  st.column_config.NumberColumn(width=44),
                    "② Mini": st.column_config.NumberColumn(width=44),
                    "③ Mini": st.column_config.NumberColumn(width=44),
                    "② Pet":  st.column_config.NumberColumn(width=44),
                    "③ Pet":  st.column_config.NumberColumn(width=44),
                },
            )

        # ── 6. VIRADAS — derivado ────────────────────────────────────────────────
        with st.expander("Viradas — Cocada (derivado, read-only)", expanded=False):
            st.caption(
                "① puxa do papelzinho · ② = ① − (corte 45g + Mini + Pet)."
            )
            rows_vir = []
            for sabor in SABORES_COCADA:
                pj = papel_joel_v.get(sabor, {})
                o = ord_corte_v[sabor]
                v1 = int(pj.get("joel_v") or 0)
                ord_total = o["ord_corte_45g"] + o["ord_corte_mini"] + o["ord_corte_pet"]
                v2 = v1 - ord_total
                rows_vir.append({
                    "Sabor": sabor,
                    "① do Joel (V)": v1,
                    "Σ Cortes": ord_total,
                    "② Pós-corte": v2,
                })
            df_vir = pd.DataFrame(rows_vir)
            st.dataframe(
                df_vir.style.map(estilo_dif, subset=["② Pós-corte"]),
                width='stretch', hide_index=True,
                column_config={
                    "Sabor":         st.column_config.TextColumn(width=112),
                    "① do Joel (V)": st.column_config.NumberColumn(width=92),
                    "Σ Cortes":      st.column_config.NumberColumn(width=78),
                    "② Pós-corte":   st.column_config.NumberColumn(width=96),
                },
            )

        # ── 7. P/VIRAR — derivado ────────────────────────────────────────────────
        with st.expander("P/Virar — Cocada (derivado, read-only)", expanded=False):
            st.caption(
                "① puxa do papelzinho · ② = ① + Viradas② · Meta = referência fixa por sabor."
            )
            pv_metas = {r["sabor"]: r["band"] for r in get_pvirar_ideal()}
            rows_pv = []
            for sabor in SABORES_COCADA:
                pj = papel_joel_v.get(sabor, {})
                o = ord_corte_v[sabor]
                v1 = int(pj.get("joel_v") or 0)
                v2 = v1 - (o["ord_corte_45g"] + o["ord_corte_mini"] + o["ord_corte_pet"])
                pv1 = int(pj.get("joel_pv") or 0)
                pv2 = pv1 + v2
                meta = pv_metas.get(sabor, 0)
                rows_pv.append({
                    "Sabor": sabor,
                    "① do Joel (PV)": pv1,
                    "② = ① + Vir②": pv2,
                    "Meta": meta,
                    "Dif vs Meta": pv2 - meta,
                })
            df_pv = pd.DataFrame(rows_pv)
            st.dataframe(
                df_pv.style.map(estilo_dif, subset=["② = ① + Vir②", "Dif vs Meta"]),
                width='stretch', hide_index=True,
                column_config={
                    "Sabor":          st.column_config.TextColumn(width=100),
                    "① do Joel (PV)": st.column_config.NumberColumn(width=92),
                    "② = ① + Vir②":   st.column_config.NumberColumn(width=96),
                    "Meta":           st.column_config.NumberColumn(width=56),
                    "Dif vs Meta":    st.column_config.NumberColumn(width=78),
                },
            )

        # ── 8. PRODUÇÃO — Cocada (Ordens) ────────────────────────────────────────
        with st.expander("Produção — Cocada (Ordens)", expanded=False):
            st.caption(
                "Bandejas em múltiplo de 8 (Z: múltiplo de 3) · Virada · Potes em **unidades**."
            )
            cols_h5 = st.columns([2.0, 1, 0.7, 1, 1, 1])
            for col, lbl in zip(cols_h5, ["Sabor", "Bandejas", "= tachos", "Virada", "Potes 260g", "Potes 605g"]):
                hdr_cell(col, lbl)
            ord_prod_v = {}
            for sabor in SABORES_COCADA:
                d = dados_cocada.get(sabor, {})
                cols = st.columns([2.0, 1, 0.7, 1, 1, 1])
                label_sabor(cols[0], sabor)
                step_band = 3 if sabor == "ZERO" else 8
                div_t = 3 if sabor == "ZERO" else 8
                pb = num_input_compact(cols[1], f"ord_prod_band_{sabor}_{data_str}", d.get("ord_prod_band"), step=step_band)
                if pb > 0:
                    cols[2].markdown(
                        f"<div style='padding-top:7px;color:#C05621;font-weight:600;font-size:10px;'>{pb / div_t:.1f}T</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    cols[2].markdown("<div style='padding-top:7px;color:#bbb;font-size:10px;'>—</div>", unsafe_allow_html=True)
                pv  = num_input_compact(cols[3], f"ord_prod_virada_{sabor}_{data_str}", d.get("ord_prod_virada"))
                p26 = num_input_compact(cols[4], f"ord_prod_p260_{sabor}_{data_str}",   d.get("ord_prod_potes_260g"))
                p60 = num_input_compact(cols[5], f"ord_prod_p605_{sabor}_{data_str}",   d.get("ord_prod_potes_605g"))
                ord_prod_v[sabor] = {
                    "ord_prod_band": pb, "ord_prod_virada": pv,
                    "ord_prod_potes_260g": p26, "ord_prod_potes_605g": p60,
                }
            soma_n = sum(ord_prod_v[s]["ord_prod_band"] for s in SABORES_COCADA if s != "ZERO")
            soma_z = ord_prod_v["ZERO"]["ord_prod_band"]
            if soma_n + soma_z > 0:
                st.caption(
                    f" **Total a produzir:** {soma_n + soma_z} bandejas "
                    f"≈ **{soma_n / 8 + soma_z / 3:.1f} tachos** (Zero conta 1/3)"
                )

        # ── 9. EMBALAGEM — Cocada (Ordens) ───────────────────────────────────────
        with st.expander("Embalagem — Cocada (Ordens, em unidades)", expanded=False):
            st.caption("Unidades a embalar hoje. Z não tem 45g.")
            cols_h6 = st.columns([1.6, 1, 1])
            for col, lbl in zip(cols_h6, ["Sabor", "45g (und)", "Mini (und)"]):
                hdr_cell(col, lbl)
            ord_emb_v = {}
            for sabor in SABORES_COCADA:
                d = dados_cocada.get(sabor, {})
                cols = st.columns([1.6, 1, 1])
                label_sabor(cols[0], sabor)
                if sabor == "ZERO":
                    celula_vazia(cols[1]); e45 = 0
                else:
                    e45 = num_input_compact(cols[1], f"ord_emb_45g_{sabor}_{data_str}", d.get("ord_emb_45g"))
                emi = num_input_compact(cols[2], f"ord_emb_mini_{sabor}_{data_str}", d.get("ord_emb_mini"))
                ord_emb_v[sabor] = {"ord_emb_45g": e45, "ord_emb_mini": emi}
            t45 = sum(ord_emb_v[s]["ord_emb_45g"] for s in SABORES_COCADA)
            tmi = sum(ord_emb_v[s]["ord_emb_mini"] for s in SABORES_COCADA)
            if t45 + tmi > 0:
                st.caption(f"**Total a embalar:** {t45:,} und 45g + {tmi:,} und Mini = **{t45 + tmi:,} unidades**")

        # ── 10. EMBALADOS — Palha ────────────────────────────────────────────────
        with st.expander("Embalados — Palha", expanded=False):
            st.caption("**50g** apenas em T, L, CH · **Pet 160g** em todos · em **unidades**.")
            cols_hpe = st.columns([1.4, 1, 1])
            for col, lbl in zip(cols_hpe, ["Sabor", "50g (und)", "Pet 160g (und)"]):
                hdr_cell(col, lbl)
            emb_palha_v = {}
            for sabor in SABORES_PALHA:
                d = dados_palha.get(sabor, {})
                cols = st.columns([1.4, 1, 1])
                sigla = SIGLA_PALHA.get(sabor, sabor)
                cols[0].markdown(
                    f"<div style='padding-top:7px;font-weight:600;'>{sabor} <span style='color:#999;'>({sigla})</span></div>",
                    unsafe_allow_html=True,
                )
                if sabor in SABORES_PALHA_50G:
                    v50 = num_input_compact(cols[1], f"emb_palha_50g_{sabor}_{data_str}", d.get("emb_50g"))
                else:
                    celula_vazia(cols[1]); v50 = 0
                vpt = num_input_compact(cols[2], f"emb_palha_pet_{sabor}_{data_str}", d.get("emb_pet"))
                emb_palha_v[sabor] = {"emb_50g": v50, "emb_pet": vpt}

        # ── 10b. DISPLAYS DE PALHA 50g — contagem manual ─────────────────────────
        with st.expander("Displays de Palha 50g", expanded=False):
            st.caption(
                "Quantos displays você tem hoje em estoque. "
                "Cada display contém **10 palhas** (4 Tradicional + 4 Leite em pó + 2 Churros)."
            )
            meta_dia = META_DISPLAYS_PALHA.get(nome_dia, 0)
            cols_disp = st.columns([1, 1])
            with cols_disp[0]:
                st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;'> Displays (qtd)</div>", unsafe_allow_html=True)
                cnt_displays = st.number_input(
                    label="cnt_displays_palha", min_value=0,
                    value=int(pbd_atual.get("cnt_displays_palha") or 0),
                    key=f"cnt_displays_palha_{data_str}",
                    label_visibility="collapsed",
                )
            with cols_disp[1]:
                if meta_dia > 0:
                    st.markdown(
                        f"<div style='font-size:10px;color:#7B341E;padding-top:6px;'>"
                        f"Meta de <b>{nome_dia}</b>: <b>{meta_dia}</b> displays</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div style='font-size:10px;color:#999;padding-top:6px;'>"
                        f"Sem meta para {nome_dia}.</div>",
                        unsafe_allow_html=True,
                    )

        # ── 11. PRODUÇÃO PALHA ───────────────────────────────────────────────────
        with st.expander("Produção Palha — Ordens", expanded=False):
            st.caption("Bandejas a produzir de palha (não se produz palha todo dia).")
            cols_hpp = st.columns([1.4, 1])
            for col, lbl in zip(cols_hpp, ["Sabor", "Bandejas"]):
                hdr_cell(col, lbl)
            prod_palha_v = {}
            for sabor in SABORES_PALHA:
                d = dados_palha.get(sabor, {})
                cols = st.columns([1.4, 1])
                sigla = SIGLA_PALHA.get(sabor, sabor)
                cols[0].markdown(
                    f"<div style='padding-top:7px;font-weight:600;'>{sabor} <span style='color:#999;'>({sigla})</span></div>",
                    unsafe_allow_html=True,
                )
                pb = num_input_compact(cols[1], f"ord_prod_palha_{sabor}_{data_str}", d.get("ord_prod_band"))
                prod_palha_v[sabor] = {"ord_prod_band": pb}
            tot_pp = sum(prod_palha_v[s]["ord_prod_band"] for s in SABORES_PALHA)
            if tot_pp > 0:
                st.caption(f"**Total produção palha:** {tot_pp} bandejas")

        # ── 12. CORTE PALHA — Ordens (renderizado ANTES da Coluna PALHA porque
        #       seus valores alimentam o cálculo de "Pós-corte" do quadro Coluna PALHA)
        with st.expander("Corte Palha — Ordens (bandejas)", expanded=False):
            st.caption("**50g** apenas em T, L, CH · **Pet** em todos.")
            cols_hcp = st.columns([1.4, 1, 1])
            for col, lbl in zip(cols_hcp, ["Sabor", "50g (band)", "Pet (band)"]):
                hdr_cell(col, lbl)
            corte_palha_v = {}
            for sabor in SABORES_PALHA:
                d = dados_palha.get(sabor, {})
                cols = st.columns([1.4, 1, 1])
                sigla = SIGLA_PALHA.get(sabor, sabor)
                cols[0].markdown(
                    f"<div style='padding-top:7px;font-weight:600;'>{sabor} <span style='color:#999;'>({sigla})</span></div>",
                    unsafe_allow_html=True,
                )
                if sabor in SABORES_PALHA_50G:
                    c50 = num_input_compact(cols[1], f"ord_corte_palha_50g_{sabor}_{data_str}", d.get("ord_corte_50g"))
                else:
                    celula_vazia(cols[1]); c50 = 0
                cpt = num_input_compact(cols[2], f"ord_corte_palha_pet_{sabor}_{data_str}", d.get("ord_corte_pet"))
                corte_palha_v[sabor] = {"ord_corte_50g": c50, "ord_corte_pet": cpt}

        # ── 13. COLUNA PALHA — Bandejas (Leonardo) ─────────────────────────────
        # Bandejas = input · Pós-corte = DERIVADO (Bandejas − Corte 50g − Corte Pet)
        with st.expander("Coluna PALHA — Bandejas (Leonardo)", expanded=False):
            st.caption(
                "**Bandejas (band)** = você conta a quantidade total de bandejas de palha por sabor. "
                "**Pós-corte (band)** = calculado automaticamente subtraindo o que foi definido em "
                "Corte Palha (50g + Pet). Em **bandejas**."
            )
            cols_hpv = st.columns([1.4, 1, 1])
            for col, lbl in zip(cols_hpv, ["Sabor", "Bandejas (band)", "Pós-corte (calc.)"]):
                hdr_cell(col, lbl)
            cont_palha_v = {}
            for sabor in SABORES_PALHA:
                d = dados_palha.get(sabor, {})
                cols = st.columns([1.4, 1, 1])
                sigla = SIGLA_PALHA.get(sabor, sabor)
                cols[0].markdown(
                    f"<div style='padding-top:7px;font-weight:600;'>{sabor} <span style='color:#999;'>({sigla})</span></div>",
                    unsafe_allow_html=True,
                )
                cb = num_input_compact(cols[1], f"cont_band_palha_{sabor}_{data_str}", d.get("cont_band_palha"))
                # Pós-corte: derivado em tempo real
                corte_total = corte_palha_v[sabor]["ord_corte_50g"] + corte_palha_v[sabor]["ord_corte_pet"]
                pos_corte = cb - corte_total
                cor = "#065F46" if pos_corte >= 0 else "#7F1D1D"
                cols[2].markdown(
                    f"<div style='padding-top:7px;font-weight:700;color:{cor};text-align:center;'>"
                    f"{pos_corte}</div>",
                    unsafe_allow_html=True,
                )
                cont_palha_v[sabor] = {"cont_band_palha": cb, "cont_band_pos_corte": pos_corte}

        # ── 14.  PÃO DE MEL — caixa unificada ──────────────────────────────────
        with st.expander("Pão de Mel", expanded=False):
            st.caption(
                "Tudo sobre Pão de Mel num só lugar: quantidade atual + ordem do dia + "
                "lembrete pro próximo dia útil. Produzido pela Produção + uma auxiliar."
            )

            cnt_cols = st.columns([1, 1])
            with cnt_cols[0]:
                st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;'> Quantidade atual (qtd)</div>", unsafe_allow_html=True)
                cnt_pm = st.number_input(
                    label="cnt_pm", min_value=0, value=int(pbd_atual.get("cnt_pm") or 0),
                    key=f"cnt_pm_{data_str}", label_visibility="collapsed",
                )
            with cnt_cols[1]:
                st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;'> Ordem do dia (a produzir)</div>", unsafe_allow_html=True)
                ord_pm = st.number_input(
                    label="ord_pm", min_value=0, value=int(pbd_atual.get("ord_pm") or 0),
                    key=f"ord_pm_{data_str}", label_visibility="collapsed",
                )

            st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;margin-top:10px;'> PM pro próximo dia útil</div>", unsafe_allow_html=True)
            st.caption(
                "Lembrete pra Produção: quantos PM produzir no próximo dia útil. "
                "Ex: na sexta, escrever '4' lembra Joel de produzir 4 PM na segunda."
            )
            ord_amanha_obs = st.text_area(
                label="ord_amanha_obs",
                value=pbd_atual.get("ord_amanha_obs", "") or "",
                height=70, key=f"ord_amanha_{data_str}",
                placeholder="Ex: 4 (quantidade de PM a produzir no próximo dia útil)",
                label_visibility="collapsed",
            )

        # ── 15.  BALAS — caixa unificada ───────────────────────────────────────
        with st.expander("Balas", expanded=False):
            st.caption(
                "Balas de doce de leite (produto distinto do PM). Produzidas pela Produção e "
                "cortadas pelo Popô. **Ordem em TACHOS** (1 tacho = 30 balas)."
            )

            bal_cols = st.columns([1, 1])
            with bal_cols[0]:
                st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;'> Quantidade atual (qtd)</div>", unsafe_allow_html=True)
                cnt_balas = st.number_input(
                    label="cnt_balas", min_value=0, value=int(pbd_atual.get("cnt_balas") or 0),
                    key=f"cnt_balas_{data_str}", label_visibility="collapsed",
                )
            with bal_cols[1]:
                st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;'> Ordem do dia (tachos)</div>", unsafe_allow_html=True)
                ord_balas = st.number_input(
                    label="ord_balas", min_value=0, value=int(pbd_atual.get("ord_balas") or 0),
                    key=f"ord_balas_{data_str}", label_visibility="collapsed",
                )
                if ord_balas > 0:
                    st.markdown(
                        f"<div style='font-size:10px;color:#C05621;font-weight:600;'>= {ord_balas * 30} balas</div>",
                        unsafe_allow_html=True,
                    )

        # ── 16.  DOCES — caixa unificada ───────────────────────────────────────
        with st.expander("Doces", expanded=False):
            st.caption(
                "Pequenos doces de leite (produto distinto). Decisão sob demanda — a Gestão "
                "costuma perguntar diretamente à Embalagem. Normalmente este campo fica vazio."
            )

            st.markdown("<div style='font-size:12px;font-weight:700;color:#7B341E;'> Quantidade atual (unidades)</div>", unsafe_allow_html=True)
            cnt_doces = st.number_input(
                label="cnt_doces", min_value=0, value=int(pbd_atual.get("cnt_doces_displays") or 0),
                key=f"cnt_doces_{data_str}", label_visibility="collapsed",
            )

    # ══════════════════════════════════════════════════════════════════════════════
    # BOTÃO DE SALVAR (transação atômica)
    # ══════════════════════════════════════════════════════════════════════════════
    st.divider()
    col_btn, col_badge, col_info = st.columns([2, 1.2, 4])
    with col_btn:
        salvar_clicked = st.form_submit_button(
            "Salvar folha completo",
            type="primary",
            width='stretch',
        )
    with col_badge:
        # Badge " Salvo" só aparece após o clique em salvar (mesma sessão, mesma data)
        if st.session_state.get("folha_salva_em") == data_str:
            st.markdown(
                "<div class='badge-salvo' style='margin-top:10px;text-align:center;"
                "padding:8px 12px;font-size:13px;'> Salvo</div>",
                unsafe_allow_html=True,
            )
    with col_info:
        st.caption(
            " Salva **toda** a folha (cocada + palha + papelzinho + PM/Balas + orientações + parâmetros) "
            "em uma única transação atômica."
        )

if salvar_clicked:
    try:
        folha_cocada_dict = {}
        for sabor in SABORES_COCADA:
            folha_cocada_dict[sabor] = {
                **emb_v[sabor],
                **cort_v[sabor],
                **ord_corte_v[sabor],
                **ord_prod_v[sabor],
                **ord_emb_v[sabor],
                "param_real_45g":  int(param_real_v["45g"].get(sabor, 0) or 0),
                "param_real_mini": int(param_real_v["mini"].get(sabor, 0) or 0),
                "param_real_pet":  int(param_real_v["pet"].get(sabor, 0) or 0),
                "amanha_obs": "",
            }

        folha_palha_dict = {}
        for sabor in SABORES_PALHA:
            folha_palha_dict[sabor] = {
                **emb_palha_v[sabor],
                **cont_palha_v[sabor],
                **prod_palha_v[sabor],
                **corte_palha_v[sabor],
            }

        papelzinho_dict = dict(papel_joel_v)

        pm_balas_doces_dict = {
            "cnt_pm": int(cnt_pm or 0),
            "cnt_balas": int(cnt_balas or 0),
            "cnt_doces_displays": int(cnt_doces or 0),
            "cnt_displays_palha": int(cnt_displays or 0),
            "ord_pm": int(ord_pm or 0),
            "ord_balas": int(ord_balas or 0),
            "ord_amanha_obs": ord_amanha_obs or "",
            "obs": obs_geral or "",
            "obs_joel": obs_joel_v or "",
            "obs_gil": obs_gil_v or "",
            "obs_leonilia": obs_leonilia_v or "",
            "bala_p_cortar": int(bala_p_cortar or 0),
            "bala_cortadas": int(bala_cortadas or 0),
            "pm_inacabado_und": int(pm_inacabado or 0),
            "pm_bolos": int(pm_bolos or 0),
            "cocada_assada_und": int(cocada_assada or 0),
        }

        salvar_folha_completa(
            data_str,
            folha_cocada_por_sabor=folha_cocada_dict,
            folha_palha_por_sabor=folha_palha_dict,
            papelzinho_por_sabor=papelzinho_dict,
            pm_balas_doces=pm_balas_doces_dict,
            # auto_baixa=False: preview obrigatório (Etapa E). A Gestão confirma
            # a baixa no expander que aparece após o salvamento.
        )
        db.invalidar_folha(data_str)  # força releitura no próximo rerun
        # Marca a folha como recém-salva (mostra badge ao lado do botão)
        st.session_state["folha_salva_em"] = data_str
        # Etapa E — sinaliza pra renderizar o preview da baixa no próximo rerun
        st.session_state["preview_baixa_pendente"] = data_str

        # Animação de confirmação — toast discreto no canto + mensagem inline.
        # NÃO usar st.balloons (festivo demais pra ambiente profissional).
        st.toast(
            f"Folha de {data_sel.strftime('%d/%m/%Y')} salva com sucesso",
            icon="✅",
        )
        st.success(
            f"**Folha de {data_sel.strftime('%d/%m/%Y')} ({nome_dia}) salva.** "
            f"Os dados já aparecem na sidebar e no Painel."
        )
        st.rerun()

    except Exception as e:
        st.error(f"Erro ao salvar: {type(e).__name__}: {e}")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════════
# PREVIEW DA BAIXA DE INSUMOS (Etapa E)
# Aparece quando a folha acabou de ser salva. A Gestão revisa o consumo e
# confirma pra atualizar o estoque. Ficar fora do form é obrigatório porque
# st.form bloqueia interações até o submit.
# ══════════════════════════════════════════════════════════════════════════════
_preview_data = st.session_state.get("preview_baixa_pendente")
if _preview_data == data_str:
    st.divider()
    st.markdown("### Baixa de insumos no estoque")
    st.caption(
        "A folha foi salva. Veja abaixo o consumo previsto e confirme pra atualizar "
        "o estoque de Suprimentos. Você pode pular se quiser lançar manualmente depois."
    )

    try:
        _pv = db.consumo_previsto_da_folha(_preview_data)
    except Exception as e:
        st.error(f"Erro ao calcular consumo: {type(e).__name__}: {e}")
        _pv = None

    if _pv is not None:
        if _pv["baixa_anterior"]:
            st.warning(
                f"Esta folha já teve baixa anterior ({_pv['movs_anteriores']} movimentos). "
                "Confirmar vai **estornar a baixa antiga** e **refazer com os valores atuais** "
                "da folha. O estoque fica coerente automaticamente."
            )
        if _pv["sem_bom"]:
            chaves = ", ".join(s["produto_chave"] for s in _pv["sem_bom"])
            st.info(
                f"Produtos da folha que **não têm receita (BOM) cadastrada**: {chaves}. "
                "Serão ignorados na baixa. Pra incluir, cadastre a receita em "
                "Cadastros → Suprimentos → Receitas."
            )

        if not _pv["consumos"]:
            st.info(
                "Nenhum insumo a baixar nesta folha — não há ordens de produção, "
                "ou os produtos lançados ainda não têm receita cadastrada."
            )
            if st.button("Fechar preview", key="fechar_preview_vazio"):
                del st.session_state["preview_baixa_pendente"]
                st.rerun()
        else:
            # Tabela de consumo previsto, ordenada por status (faltas primeiro).
            ordem = {"falta": 0, "critico": 1, "ok": 2}
            consumos_ord = sorted(_pv["consumos"], key=lambda c: (ordem[c["status"]], c["insumo_nome"]))
            df_prev = pd.DataFrame([{
                "Status": {"falta": "FALTA", "critico": "JUSTO", "ok": "OK"}[c["status"]],
                "Insumo": c["insumo_nome"],
                "Consumo": f"{c['quantidade']:.3f} {c['unidade']}",
                "Estoque atual": f"{c['estoque_atual']:.3f} {c['unidade']}",
                "Estoque depois": f"{c['estoque_depois']:.3f} {c['unidade']}",
            } for c in consumos_ord])
            st.dataframe(df_prev, width='stretch', hide_index=True)

            _n_falta = sum(1 for c in _pv["consumos"] if c["status"] == "falta")
            if _n_falta:
                st.warning(
                    f"{_n_falta} insumo(s) ficarão com estoque **negativo** após a baixa. "
                    "Isso é esperado se o estoque atual está desatualizado (ex.: ainda "
                    "não lançamos as compras). Você pode confirmar mesmo assim — depois "
                    "ajusta com uma entrada de compra ou ajuste de inventário."
                )

            col_conf, col_pular = st.columns([2, 1])
            with col_conf:
                if st.button(
                    "Confirmar baixa de estoque",
                    type="primary",
                    key="confirmar_baixa",
                    width='stretch',
                ):
                    try:
                        _r = db.baixar_insumos_da_folha(_preview_data)
                        del st.session_state["preview_baixa_pendente"]
                        db.invalidar_suprimentos()
                        _msg = f"Baixa registrada: {len(_r['movimentos'])} insumo(s) consumido(s)"
                        if _r["estornados"]:
                            _msg += f" (estornou {_r['estornados']} mov. anteriores)"
                        st.toast(_msg)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro na baixa: {type(e).__name__}: {e}")
                        st.exception(e)
            with col_pular:
                if st.button("Pular baixa", key="pular_baixa", width='stretch'):
                    del st.session_state["preview_baixa_pendente"]
                    st.info(
                        "Baixa adiada. Lance os movimentos depois em "
                        "Cadastros → Suprimentos → Movimentações."
                    )
                    st.rerun()

# ── Rodapé ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    f" Folha de Produção — PCP Doces Vó Nena v2.1 · "
    f"Sessão aberta em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
)
