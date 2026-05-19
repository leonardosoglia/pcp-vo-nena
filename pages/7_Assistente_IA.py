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

# Bootstrap
if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
    os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
if not os.getenv("ANTHROPIC_API_KEY") and "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

_RAIZ = os.path.dirname(os.path.dirname(__file__))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from cached_db import list_datas_folha

st.set_page_config(
    page_title="Pergunte ao Claude • Doces Vó Nena",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sora', sans-serif; font-size: 14px; }
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    h1, h2, h3 { color: #C05621; font-weight: 700; }
    section[data-testid="stSidebar"] { background-color: #1C1410; }
    section[data-testid="stSidebar"] * { color: #F5E6D3 !important; }
    .resposta-claude {
        background: linear-gradient(135deg, #FFF8F2 0%, #FEF3C7 100%);
        border-left: 6px solid #C05621;
        border-radius: 10px;
        padding: 20px 24px;
        margin: 16px 0;
        font-size: 15px;
        line-height: 1.6;
    }
    .pergunta-user {
        background: #1C1410;
        color: #F5E6D3;
        border-radius: 10px;
        padding: 12px 18px;
        margin: 12px 0;
        font-style: italic;
    }
    .custo-info {
        background: #ECFDF5;
        border-left: 4px solid #059669;
        border-radius: 4px;
        padding: 6px 12px;
        margin: 4px 0;
        font-size: 11px;
        color: #064E3B;
    }
    .exemplo-pergunta {
        background: #FFFBEB;
        border: 1px dashed #D97706;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 6px 0;
        cursor: pointer;
        font-size: 13px;
        color: #92400E;
    }
    .exemplo-pergunta:hover { background: #FEF3C7; }
    .erro-card {
        background: #FEF2F2;
        border-left: 5px solid #B91C1C;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 10px 0;
        color: #7F1D1D;
    }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ════════════════════════════════════════════════════════════════════════════
st.title("🤖 Pergunte ao Claude")
st.caption(
    "Pergunte em português sobre a operação da Vó Nena. O sistema manda sua "
    "pergunta + dados da folha + histórico recente pro Claude, que responde "
    "em ~3-5s com explicação humana baseada nos dados reais."
)

with st.expander("ℹ️ Como funciona (clica pra entender)", expanded=False):
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
- **Com cache ativo** (system prompt cacheado por 5min): ~60% mais barato
- **Mês típico (10 perguntas/dia):** ~R$5-10

**Limitações honestas:**
- Não substitui o julgamento do Eraldo
- Pode errar em perguntas muito específicas se o dado não está estruturado
- Não tem acesso a vendas reais (só produção/embalagem)
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
        "<b>⚠️ ANTHROPIC_API_KEY não configurada.</b><br><br>"
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
    from claude_assistant import perguntar, estimar_custo, usd_para_brl
except ImportError as e:
    st.markdown(
        f"<div class='erro-card'>"
        f"<b>❌ Erro ao importar claude_assistant:</b> {e}<br>"
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
        st.warning("⚠️ Nenhuma folha registrada no banco. Cadastra alguma em Lançamento antes.")
        st.stop()
    data_ref = st.selectbox(
        "📅 Data de referência (qual folha consultar)",
        options=datas_disponiveis,
        index=0,
        help="O Claude vai analisar essa folha + as 7 anteriores como contexto.",
    )

with col_modelo:
    modelo = st.selectbox(
        "🧠 Modelo",
        options=["claude-haiku-4-5", "claude-sonnet-4-6"],
        index=0,
        help="Haiku 4.5 é mais barato e rápido (~R$0,03/consulta). "
             "Sonnet 4.6 é mais sofisticado (~R$0,10/consulta).",
    )


# Exemplos de perguntas pra clicar
st.markdown("##### 💡 Exemplos de perguntas (clica pra usar)")
exemplos = [
    "Resume pra mim a folha do dia em 3 linhas: o que foi produzido, o que tá pendente.",
    "Comparado com a semana passada no mesmo dia da semana, como foi a produção hoje?",
    "Tem algum sabor que parece estar com problema (excesso ou falta) nos últimos dias?",
    "Quais sabores estão precisando de atenção máxima hoje (estoque baixo, alta demanda)?",
    "Por que o sistema sugere essa ordem de corte específica hoje?",
]
cols_exemplos = st.columns(len(exemplos))
for i, exemplo in enumerate(exemplos):
    with cols_exemplos[i]:
        if st.button(exemplo[:60] + "...", key=f"ex_{i}", use_container_width=True,
                     help=exemplo):
            st.session_state["_pergunta_input"] = exemplo


# Campo principal de pergunta
pergunta_default = st.session_state.get("_pergunta_input", "")
pergunta = st.text_area(
    "✍️ Sua pergunta",
    value=pergunta_default,
    height=100,
    placeholder="Ex: 'Por que estamos sugerindo cortar 20 bandejas de Tradicional hoje?'",
)

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
with col_btn1:
    perguntar_clicked = st.button("🤖 Perguntar", type="primary", use_container_width=True)
with col_btn2:
    limpar = st.button("🗑️ Limpar histórico", use_container_width=True)

if limpar:
    st.session_state.historico_perguntas = []
    st.session_state["_pergunta_input"] = ""
    st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# EXECUTA A CONSULTA
# ════════════════════════════════════════════════════════════════════════════
if perguntar_clicked:
    pergunta_limpa = (pergunta or "").strip()
    if not pergunta_limpa:
        st.warning("⚠️ Escreve uma pergunta antes de clicar em Perguntar.")
    else:
        with st.spinner("🤖 Claude está pensando..."):
            resultado = perguntar(
                pergunta=pergunta_limpa,
                data_referencia=data_ref,
                modelo=modelo,
            )

        if resultado["erro"]:
            st.markdown(
                f"<div class='erro-card'>"
                f"<b>❌ Erro ao consultar o Claude:</b><br>"
                f"<code>{resultado['erro']}</code><br><br>"
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
                resultado["tokens_input"],
                resultado["tokens_output"],
                resultado["tokens_cache_read"],
                modelo=resultado["modelo"],
            )
            custo_brl = usd_para_brl(custo_usd)

            # Salva no histórico
            st.session_state.historico_perguntas.insert(0, {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "pergunta": pergunta_limpa,
                "resposta": resultado["resposta"],
                "data_ref": data_ref,
                "modelo": resultado["modelo"],
                "tokens_input": resultado["tokens_input"],
                "tokens_output": resultado["tokens_output"],
                "tokens_cache_read": resultado["tokens_cache_read"],
                "custo_usd": custo_usd,
                "custo_brl": custo_brl,
            })

            # Limpa o input pra próxima
            st.session_state["_pergunta_input"] = ""
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# HISTÓRICO DA CONVERSA (sessão atual)
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.historico_perguntas:
    st.divider()
    st.header("💬 Conversa")

    for i, item in enumerate(st.session_state.historico_perguntas):
        # Pergunta do usuário
        st.markdown(
            f"<div class='pergunta-user'>"
            f"<b>🧑 {item['timestamp']} · folha {item['data_ref']}:</b><br>"
            f"{item['pergunta']}"
            f"</div>",
            unsafe_allow_html=True,
        )
        # Resposta
        st.markdown(
            f"<div class='resposta-claude'>"
            f"<b>🤖 Claude ({item['modelo']}):</b><br><br>"
            f"{item['resposta'].replace(chr(10), '<br>')}"
            f"</div>",
            unsafe_allow_html=True,
        )
        # Custo
        cache_info = ""
        if item["tokens_cache_read"] > 0:
            pct_cache = (item["tokens_cache_read"] / item["tokens_input"]) * 100
            cache_info = f" · 💾 cache hit: {pct_cache:.0f}%"
        st.markdown(
            f"<div class='custo-info'>"
            f"📊 {item['tokens_input']} tokens in + {item['tokens_output']} tokens out "
            f"= <b>~R$ {item['custo_brl']:.3f}</b> (US$ {item['custo_usd']:.5f}){cache_info}"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Totais
    total_brl = sum(item["custo_brl"] for item in st.session_state.historico_perguntas)
    total_perguntas = len(st.session_state.historico_perguntas)
    st.divider()
    st.caption(
        f"💰 Total da sessão: **{total_perguntas} perguntas · ~R$ {total_brl:.2f}** "
        f"(média ~R$ {total_brl/total_perguntas:.3f} por consulta)"
    )


# ════════════════════════════════════════════════════════════════════════════
# RODAPÉ
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.caption(
    "🤖 Powered by **Claude** (Anthropic) · "
    f"Sessão iniciada {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
    "Custos exibidos são estimativas baseadas no pricing público vigente."
)
st.caption(
    "💡 **Lembrete pro TCC:** este é o componente que coroa a Camada 2 do sistema. "
    "Capítulo associado: \"Integração com LLMs como camada cognitiva em PCP\". "
    "Métricas pra o Cap 5: tempo médio de resposta, satisfação subjetiva do Eraldo (escala 1-5), "
    "custo médio por consulta, % de perguntas que levaram a decisão concreta."
)
