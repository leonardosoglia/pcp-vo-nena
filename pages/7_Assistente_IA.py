"""
pages/7_Assistente_IA.py — Botão "Pergunte ao Claude"

Página do assistente cognitivo: usuário (Eraldo / Leonardo) digita uma
pergunta em PT-BR, sistema monta contexto da folha + histórico + regras de
negócio, manda pro Claude API, retorna resposta humana em ~3-5s.

Modelo: Claude Haiku 4.5 (rápido, ~R$0,02-0,05 por consulta com cache).

Capítulo TCC: "Integração com Large Language Models como camada cognitiva
em sistemas PCP — apoio à decisão via linguagem natural."

Referência: Brown et al. (2020). Language Models are Few-Shot Learners.
"""
import streamlit as st
from datetime import datetime
import sys
import os

# Bootstrap defensivo de secrets (vide pages/5_Anomalias_ML.py pra explicação).
for _key in ("DATABASE_URL", "ANTHROPIC_API_KEY"):
    if not os.getenv(_key):
        try:
            if _key in st.secrets:
                os.environ[_key] = st.secrets[_key]
        except Exception:
            pass

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from cached_db import list_datas_folha
import componentes

st.set_page_config(
    page_title="Assistente IA • Doces Vó Nena",
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
componentes.cabecalho(
    "Suporte", "Assistente IA", icone="smart_toy",
    contexto="Pergunte em português sobre a produção — o assistente lê os dados e responde. Cada pergunta custa centavos.",
)

with st.expander("Como funciona (clica pra entender)", expanded=False):
    st.markdown("""
**O sistema funciona em 4 passos automáticos:**

1. **Você escreve uma pergunta** em PT-BR no campo abaixo
2. **O sistema monta um pacote** com:
   - Folha do dia escolhido (Cocada, Palha, Papelzinho, PM/Balas)
   - Histórico das últimas 7 folhas (resumo compacto)
   - Regras de negócio (CLAUDE.md condensado)
   - Sua pergunta
3. **Manda pro Claude (modelo Haiku 4.5)** via API da Anthropic
4. **Resposta volta em ~3-5 segundos**, em PT-BR informal, baseada no contexto real

**Vantagens vs ChatGPT/conversas avulsas:**
- Tem **contexto real da fábrica** — não é genérico
- Sabe a **gramática do negócio** (cocada, palha, papelzinho, viradas, etc.)
- Cita **dados concretos** da folha (não inventa)
- Reconhece **limitações** (amostra pequena, dado faltando)

**Custos:**
- **Por consulta:** ~R$0,02 a R$0,05
- **No modo profundo** (com ferramentas): o contexto repetido é cacheado, baixando o custo de perguntas em sequência. No modo rápido, o custo já é mínimo
- **Mês típico (10 perguntas/dia):** ~R$5-10

**Limitações honestas:**
- Não substitui o julgamento da Gestão
- Pode errar em perguntas muito específicas se o dado não está estruturado
- **Agora enxerga vendas reais por mês e o custo de produção (material) por produto.** Vendas por produto / lucratividade ainda ficam nas telas Vendas e Lucratividade
- O custo que ele vê é só de **material** — não inclui mão de obra/energia, então não é lucro líquido
- Quanto mais dados acumular (folhas), melhor a qualidade da resposta

**Referência (vai pro TCC):** Brown, T. B. et al. (2020). "Language Models
are Few-Shot Learners". *NeurIPS 2020*. Princípio do few-shot learning em
LLMs aplicado a domínio específico via prompt engineering.
""")


# ════════════════════════════════════════════════════════════════════════════
# CHECAGEM DE SECRET
# ════════════════════════════════════════════════════════════════════════════
api_key_configurada = bool(os.getenv("ANTHROPIC_API_KEY", "").strip())

if not api_key_configurada:
    st.markdown(
        "<div class='erro-card'>"
        "<b>ANTHROPIC_API_KEY não configurada.</b><br><br>"
        "Pra ativar essa página, configure a secret <code>ANTHROPIC_API_KEY</code> "
        "no Hugging Face Spaces:<br>"
        "1. Vai em <code>Settings &gt; Variables and secrets</code><br>"
        "2. Clica em <b>New secret</b><br>"
        "3. Name: <code>ANTHROPIC_API_KEY</code><br>"
        "4. Value: sua chave da Anthropic (formato <code>sk-ant-...</code>)<br>"
        "5. Salva + restart o Space<br><br>"
        "A chave é gerada em <a href='https://console.anthropic.com' target='_blank'>console.anthropic.com</a> "
        "(Settings &gt; API Keys &gt; Create Key)."
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# IMPORT lazy do helper (depois de checar key)
# ════════════════════════════════════════════════════════════════════════════
try:
    from claude_assistant import (
        perguntar, estimar_custo, usd_para_brl,
        perguntar_streaming, sugestoes_contextuais,
        expandir_slash_command, SLASH_COMMANDS,
        perguntar_com_tools, gerar_briefing_do_dia,
    )
except ImportError as e:
    st.markdown(
        f"<div class='erro-card'>"
        f"<b> Erro ao importar claude_assistant:</b> {e}<br>"
        f"Provavelmente a biblioteca <code>anthropic</code> não está instalada. "
        f"Confere o <code>requirements.txt</code>."
        f"</div>",
        unsafe_allow_html=True,
    )
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# ESTADO DA SESSÃO — histórico de perguntas + respostas
# ════════════════════════════════════════════════════════════════════════════
if "historico_perguntas" not in st.session_state:
    st.session_state.historico_perguntas = []  # list of dicts: pergunta, resposta, custo, data_ref


# ════════════════════════════════════════════════════════════════════════════
# INPUT
# ════════════════════════════════════════════════════════════════════════════
st.divider()

col_data, col_modelo = st.columns([2, 1])

with col_data:
    datas_disponiveis = sorted(list_datas_folha(), reverse=True)
    if not datas_disponiveis:
        st.warning("Nenhuma folha registrada no banco. Cadastra alguma em Lançamento antes.")
        st.stop()
    data_ref = st.selectbox(
        "Data de referência (qual folha consultar)",
        options=datas_disponiveis,
        index=0,
        help="O Claude vai analisar essa folha + as 7 anteriores como contexto.",
    )

with col_modelo:
    MODELOS_DISPONIVEIS = {
        "claude-haiku-4-5":  "Haiku 4.5 — rápido (~R$0,03)",
        "claude-sonnet-4-6": "Sonnet 4.6 — equilibrado (~R$0,10)",
        "claude-opus-4-8":   "Opus 4.8 — análise profunda (~R$0,25)",
    }
    modelo = st.selectbox(
        "Modelo",
        options=list(MODELOS_DISPONIVEIS.keys()),
        format_func=lambda m: MODELOS_DISPONIVEIS[m],
        index=0,
        help=(
            "**Haiku 4.5** — default. Perguntas comuns, rápido (~3-5s). "
            "**Sonnet 4.6** — comparações e análise de tendência (~5-10s). "
            "**Opus 4.8** — raciocínio multi-camada, análise estratégica, "
            "decisões de longo prazo. Mais lento (~10-20s) e ~5× mais caro "
            "que Haiku. Use só pra perguntas pesadas — não pra dia a dia."
        ),
    )


# Briefing proativo do dia — a IA observa e te avisa SEM você perguntar
st.markdown("##### Briefing do dia (a IA observa e avisa, sem você perguntar)")
if st.button("Gerar briefing do dia", type="primary",
             help="A IA cruza a folha do dia + giro + insumos + eventos e devolve um resumo com alertas e próximos passos."):
    with st.spinner("A IA está observando o dia..."):
        try:
            _brief = gerar_briefing_do_dia(data_ref, modelo=modelo)
        except Exception as _e:
            _brief = {"erro": str(_e)}
    if _brief.get("erro"):
        st.error(f"Não consegui gerar o briefing: {_brief['erro']}")
    else:
        st.markdown(_brief.get("resposta", "") or "_(sem resposta)_")
        try:
            _c = usd_para_brl(estimar_custo(_brief.get("tokens_input", 0),
                                            _brief.get("tokens_output", 0),
                                            _brief.get("tokens_cache_read", 0),
                                            modelo=modelo))
            st.caption(f"Briefing gerado · {_brief.get('iteracoes', 0)} passos · ~R${_c:.2f}")
        except Exception:
            pass

st.divider()

# Sugestões contextuais (perguntas baseadas no estado da folha selecionada)
sugestoes = sugestoes_contextuais(data_ref)
st.markdown("##### Sugestões pra esta folha (clica pra usar)")
cols_sug = st.columns(min(3, len(sugestoes)))
for i, sug in enumerate(sugestoes):
    col = cols_sug[i % len(cols_sug)]
    with col:
        # Mostra os primeiros ~70 chars como label do botão; tooltip mostra completo
        label = sug if len(sug) <= 70 else sug[:67] + "..."
        if st.button(label, key=f"sug_{i}", width='stretch', help=sug):
            st.session_state["_pergunta_input"] = sug

# Slash commands disponíveis (expander pra não poluir)
with st.expander("Comandos rápidos (digite `/` no campo abaixo)", expanded=False):
    st.markdown("**Atalhos disponíveis:**")
    for cmd, descr in SLASH_COMMANDS.items():
        st.markdown(f"- **`{cmd}`** — {descr.split('.')[0]}.")
    st.caption(
        "Digite o comando como pergunta (ex: `/resumo` ou `/comparar 18/05`) "
        "e clique em Perguntar. O sistema expande pra um prompt completo."
    )

# Campo principal de pergunta
pergunta_default = st.session_state.get("_pergunta_input", "")
pergunta = st.text_area(
    "Sua pergunta",
    value=pergunta_default,
    height=100,
    placeholder="Ex: 'Por que estamos sugerindo cortar 20 bandejas de Tradicional hoje?' "
                "ou um comando como /resumo, /anomalias, /comparar 18/05",
)

col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 2, 2])
with col_btn1:
    perguntar_clicked = st.button("Perguntar", type="primary", width='stretch')
with col_btn2:
    limpar = st.button("Limpar histórico", width='stretch')
with col_btn4:
    modo_profundo = st.toggle(
        "Modo profundo (tools)",
        value=False,
        help=(
            "Quando ligado, o Claude pode CONSULTAR O BANCO direto via funções "
            "(buscar folha de qualquer data, agregar métricas, comparar dias "
            "da semana, etc). Resposta mais precisa pra perguntas que envolvem "
            "muitos dados ou períodos longos, mas SEM streaming (mostra spinner) "
            "e custa um pouco mais. Desligado: streaming rápido só com contexto "
            "pré-enviado (folha + 7 dias)."
        ),
    )

if limpar:
    st.session_state.historico_perguntas = []
    st.session_state["_pergunta_input"] = ""
    st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# EXECUTA A CONSULTA — com streaming (resposta aparece em tempo real)
# ════════════════════════════════════════════════════════════════════════════
if perguntar_clicked:
    pergunta_limpa = (pergunta or "").strip()
    if not pergunta_limpa:
        st.warning("Escreve uma pergunta antes de clicar em Perguntar.")
    else:
        # Slash command? Expande pro prompt completo
        prompt_expandido = expandir_slash_command(pergunta_limpa)
        if prompt_expandido is not None:
            pergunta_efetiva = prompt_expandido
            slash_usado = pergunta_limpa.split(maxsplit=1)[0].lower()
        else:
            pergunta_efetiva = pergunta_limpa
            slash_usado = None

        # Renderiza pergunta acima (antes do streaming começar)
        st.divider()
        from datetime import datetime as _dt
        ts_now = _dt.now().strftime("%H:%M:%S")
        label_pergunta = f"**{ts_now} · folha {data_ref}**"
        if slash_usado:
            label_pergunta += f" · comando `{slash_usado}`"
        if modo_profundo:
            label_pergunta += " · modo profundo (tools)"
        st.markdown(label_pergunta)
        st.markdown(f"> {pergunta_limpa}")

        # Dispatch: modo profundo (tools) ou streaming simples
        resposta_completa = ""
        tools_chamadas = []
        if modo_profundo:
            with st.chat_message("assistant"):
                with st.spinner("Claude está consultando o banco e raciocinando..."):
                    resultado = perguntar_com_tools(
                        pergunta_efetiva, data_ref, modelo, max_tokens=2048
                    )
                resposta_completa = resultado.get("resposta", "")
                tools_chamadas = resultado.get("tools_chamadas", [])
                if resposta_completa:
                    st.markdown(resposta_completa)
                # Mostra as tools chamadas
                if tools_chamadas:
                    with st.expander(
                        f"Ferramentas usadas ({len(tools_chamadas)}) — clique pra ver",
                        expanded=False,
                    ):
                        for i, tc in enumerate(tools_chamadas, 1):
                            st.markdown(f"**{i}. `{tc['name']}`**")
                            st.json(tc["input"], expanded=False)
                            st.caption(f"Resultado (preview): `{tc['result_preview']}`")
            meta = {
                "tokens_input": resultado.get("tokens_input", 0),
                "tokens_output": resultado.get("tokens_output", 0),
                "tokens_cache_read": resultado.get("tokens_cache_read", 0),
                "tokens_cache_write": resultado.get("tokens_cache_write", 0),
                "modelo": resultado.get("modelo", modelo),
                "iteracoes": resultado.get("iteracoes", 0),
                "erro": resultado.get("erro"),
            }
        else:
            # Streaming da resposta
            sr = perguntar_streaming()
            with st.chat_message("assistant"):
                resposta_completa = st.write_stream(
                    sr.chunks(pergunta_efetiva, data_ref, modelo, 1024)
                )
            meta = sr.meta

        # Erro?
        if meta.get("erro"):
            st.markdown(
                f"<div class='erro-card'>"
                f"<b>Erro ao consultar o Claude:</b><br>"
                f"<code>{meta['erro']}</code><br><br>"
                f"<b>Causas comuns:</b><br>"
                f"• API key inválida ou sem créditos<br>"
                f"• Falha de rede temporária<br>"
                f"• Limite de tokens excedido<br><br>"
                f"<b>O que tentar:</b><br>"
                f"• Confirmar no console.anthropic.com se há saldo<br>"
                f"• Verificar se a API key começa com <code>sk-ant-</code><br>"
                f"• Tentar de novo em 30s"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            # Calcula custo
            custo_usd = estimar_custo(
                meta.get("tokens_input", 0),
                meta.get("tokens_output", 0),
                meta.get("tokens_cache_read", 0),
                modelo=meta.get("modelo", modelo),
            )
            custo_brl = usd_para_brl(custo_usd)

            # Mostra rodapé compacto com custo + tokens
            cache_pct = ""
            if meta.get("tokens_cache_read", 0) > 0 and meta.get("tokens_input", 0) > 0:
                pct = (meta["tokens_cache_read"] / meta["tokens_input"]) * 100
                cache_pct = f" · cache {pct:.0f}%"
            st.caption(
                f"R$ {custo_brl:.3f} (US$ {custo_usd:.4f}) · "
                f"{meta.get('tokens_input', 0)} tokens entrada, "
                f"{meta.get('tokens_output', 0)} saída{cache_pct} · "
                f"modelo {meta.get('modelo', modelo)}"
            )

            # Salva no histórico
            st.session_state.historico_perguntas.insert(0, {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "pergunta": pergunta_limpa,
                "resposta": resposta_completa,
                "data_ref": data_ref,
                "modelo": meta.get("modelo", modelo),
                "tokens_input": meta.get("tokens_input", 0),
                "tokens_output": meta.get("tokens_output", 0),
                "tokens_cache_read": meta.get("tokens_cache_read", 0),
                "custo_usd": custo_usd,
                "custo_brl": custo_brl,
                "slash_command": slash_usado,
            })

            # Limpa input pra próxima (mas não rerun — assim o stream fica visível)
            st.session_state["_pergunta_input"] = ""


# ════════════════════════════════════════════════════════════════════════════
# HISTÓRICO DA CONVERSA (sessão atual) — pula o item 0 se acabou de stream
# ════════════════════════════════════════════════════════════════════════════
# Se acabou de fazer pergunta com streaming, o item 0 do histórico JÁ FOI
# mostrado via st.write_stream acima — não duplicar. Senão, mostra tudo.
historico_pra_exibir = st.session_state.historico_perguntas
if perguntar_clicked and historico_pra_exibir and not historico_pra_exibir[0].get("_ja_mostrado"):
    # marca como já mostrado pra próximo rerun não pular
    historico_pra_exibir[0]["_ja_mostrado"] = True
    historico_pra_exibir = historico_pra_exibir[1:]

if historico_pra_exibir:
    st.divider()
    st.header("Conversas anteriores nesta sessão")

    for i, item in enumerate(historico_pra_exibir):
        # Pergunta do usuário
        st.markdown(
            f"<div class='pergunta-user'>"
            f"<b> {item['timestamp']} · folha {item['data_ref']}:</b><br>"
            f"{item['pergunta']}"
            f"</div>",
            unsafe_allow_html=True,
        )
        # Resposta
        st.markdown(
            f"<div class='resposta-claude'>"
            f"<b> Claude ({item['modelo']}):</b><br><br>"
            f"{item['resposta'].replace(chr(10), '<br>')}"
            f"</div>",
            unsafe_allow_html=True,
        )
        # Custo
        cache_info = ""
        if item["tokens_cache_read"] > 0:
            pct_cache = (item["tokens_cache_read"] / item["tokens_input"]) * 100
            cache_info = f" ·  cache hit: {pct_cache:.0f}%"
        st.markdown(
            f"<div class='custo-info'>"
            f" {item['tokens_input']} tokens in + {item['tokens_output']} tokens out "
            f"= <b>~R$ {item['custo_brl']:.3f}</b> (US$ {item['custo_usd']:.5f}){cache_info}"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Totais (considera TODAS as perguntas da sessão, inclui a atual que acabou de stream)
    total_brl = sum(item.get("custo_brl", 0) for item in st.session_state.historico_perguntas)
    total_perguntas = len(st.session_state.historico_perguntas)
    if total_perguntas > 0:
        st.divider()
        st.caption(
            f"Total da sessão: **{total_perguntas} perguntas · ~R$ {total_brl:.2f}** "
            f"(média ~R$ {total_brl/total_perguntas:.3f} por consulta)"
        )


# ════════════════════════════════════════════════════════════════════════════
# RODAPÉ
# ════════════════════════════════════════════════════════════════════════════
# Nota interna (não exibir na tela): componente que coroa a Camada 2. Capítulo do
# TCC: "Integração com LLMs como camada cognitiva em PCP". Métricas pro Cap 5:
# tempo médio de resposta, satisfação subjetiva da Gestão (1-5), custo médio por
# consulta, % de perguntas que viraram decisão concreta.
componentes.rodape("as respostas usam os dados do dia — confira antes de decidir")
