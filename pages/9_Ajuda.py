"""
pages/9_Ajuda.py — Central de Ajuda / Documentação do sistema.

Redesenho 26/06/2026 (reforma visual, Parte 3):
- REMOVIDOS os nomes de pessoas → departamentos (Gestão, Produção, Corte,
  Embalagem, Estoque). Regra firme do projeto.
- Conteúdo atualizado (assistente já ativado; hospedagem atual; mapa com as
  18 telas de hoje).
- Organização nova: cabeçalho + busca + abas (Como usar · Telas · Glossário ·
  Perguntas · Referências). Glossário e Perguntas são pesquisáveis.

O CSS desta tela fica AQUI (page-local) de propósito: as peças (cartões brancos,
pílulas de departamento, busca com lupa) precisam bater fielmente com o mockup
aprovado pela Gestão, e as classes antigas (`glossario-termo`, `faq-q`,
`card-feature`) são forçadas pra cards coloridos pelo tema global — reusá-las
deixaria a tela diferente do preview. Como cada página injeta seu próprio CSS,
este bloco só afeta a tela de Ajuda.
"""
import streamlit as st
import os

# Bootstrap defensivo (HF Spaces injeta DATABASE_URL como env var)
try:
    if not os.getenv("DATABASE_URL") and "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass


st.set_page_config(
    page_title="Ajuda • Doces Vó Nena",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui_theme import aplicar_tema
import componentes
aplicar_tema()


# ════════════════════════════════════════════════════════════════════════════
# CSS DA TELA (isolado nesta página) — fiel ao mockup aprovado
# ════════════════════════════════════════════════════════════════════════════
AJUDA_CSS = """
<style>
/* Cabeçalho */
.aj-eyebrow{font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#C05621;margin:2px 0 4px}
.aj-title{font-size:19px;font-weight:700;color:#0F172A;line-height:1.2;margin:0 0 3px}
.aj-sub{font-size:12.5px;color:#64748B;margin:0 0 6px}

/* Busca com lupa (estiliza o único campo de texto desta tela) */
[data-testid="stMain"] .stTextInput input{
    min-height:40px !important;
    border-radius:10px !important;
    font-size:13px !important;
    padding:8px 12px 8px 36px !important;
    border:1px solid #E2E8F0 !important;
    background-color:#FFFFFF !important;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cpath d='M21 21l-4.35-4.35'/%3E%3C/svg%3E");
    background-repeat:no-repeat;
    background-position:11px center;
}

/* Abas — um pouco mais de respiro e fonte que o padrão, igual ao preview */
[data-testid="stMain"] .stTabs [data-baseweb="tab-list"]{gap:18px !important}
[data-testid="stMain"] .stTabs [data-baseweb="tab"]{font-size:13px !important;padding:7px 2px !important}

/* Cartão branco padrão da Ajuda */
.aj-card{background:#FFFFFF;border:1px solid #E4E4E7;border-radius:12px;padding:16px 18px;margin:0 0 12px;box-shadow:0 1px 2px rgba(0,0,0,.03)}
.aj-card-head{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:10px}
.aj-card-title{font-size:15px;font-weight:600;color:#0F172A}

/* Pílulas de departamento */
.aj-pill{display:inline-block;font-size:11px;font-weight:600;padding:2px 9px;border-radius:999px;background:rgba(15,23,42,.06);color:#334155;margin:1px 2px 1px 0}
.aj-pill-brand{background:rgba(192,86,33,.12);color:#993C1D}

/* Selo verde "sem nomes" */
.aj-chip-ok{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;color:#0F6E56;background:#E1F5EE;padding:3px 10px;border-radius:999px}

/* Tabela do fluxo */
.aj-table{width:100%;border-collapse:collapse}
.aj-th{font-size:10px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:#94A3B8;text-align:left;padding:0 8px 8px}
.aj-td{font-size:12.5px;padding:9px 8px;border-top:1px solid #EEF2F6;color:#334155;vertical-align:middle}

/* Mapa de telas (grupos) */
.aj-grp{font-size:10px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:#94A3B8;margin:14px 2px 6px}
.aj-grp:first-child{margin-top:2px}
.aj-tela{display:flex;gap:10px;padding:8px 0;border-top:1px solid #F1F5F9}
.aj-tela:first-of-type{border-top:none}
.aj-tela-nome{flex:0 0 168px;font-size:12.5px;font-weight:600;color:#C05621}
.aj-tela-desc{font-size:12px;color:#475569;line-height:1.45}

/* Glossário — cartões em grade */
.aj-gloss-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}
.aj-gloss{background:#FFFFFF;border:1px solid #E4E4E7;border-radius:10px;padding:12px 14px}
.aj-gloss-termo{font-size:13px;font-weight:600;color:#C05621;margin-bottom:3px}
.aj-gloss-def{font-size:12px;color:#475569;line-height:1.5}
.aj-vazio{font-size:12.5px;color:#94A3B8;padding:14px 2px}

/* Perguntas — sanfona */
details.aj-faq{background:#FFFFFF;border:1px solid #E4E4E7;border-radius:10px;margin:8px 0;overflow:hidden}
details.aj-faq>summary{list-style:none;cursor:pointer;padding:12px 16px;font-size:12.5px;font-weight:500;color:#334155;display:flex;align-items:center;justify-content:space-between;gap:10px}
details.aj-faq>summary::-webkit-details-marker{display:none}
details.aj-faq>summary::after{content:"";flex:0 0 16px;width:16px;height:16px;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E") no-repeat center;transition:transform .15s ease}
details.aj-faq[open]>summary{color:#C05621}
details.aj-faq[open]>summary::after{transform:rotate(180deg)}
.aj-faq-a{padding:0 16px 14px;font-size:12px;color:#475569;line-height:1.55}

/* Referências */
.aj-ref{background:#FFFFFF;border:1px solid #E4E4E7;border-radius:10px;padding:12px 14px;margin:0 0 10px}
.aj-ref-titulo{font-size:12.5px;font-weight:600;color:#0F172A}
.aj-ref-corpo{font-size:12px;color:#475569;line-height:1.5;margin-top:3px}
.aj-ref-uso{font-size:11.5px;color:#C05621;margin-top:4px}
</style>
"""
st.markdown(AJUDA_CSS, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO + BUSCA
# ════════════════════════════════════════════════════════════════════════════
componentes.cabecalho(
    "Suporte", "Ajuda", icone="help",
    contexto="Como o sistema funciona, termo a termo — busque ou navegue pelas abas.",
)

q = st.text_input(
    "Buscar",
    placeholder="Buscar um termo do glossário ou uma pergunta…",
    label_visibility="collapsed",
).strip().lower()


def _casa(*textos) -> bool:
    """True se a busca está vazia ou bate em algum dos textos."""
    if not q:
        return True
    return any(q in (t or "").lower() for t in textos)


def _esc(texto: str) -> str:
    """Escapa o mínimo pra não quebrar o HTML dos cartões."""
    return (texto or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


tab_uso, tab_telas, tab_gloss, tab_faq, tab_ref = st.tabs(
    ["Como usar", "Telas do sistema", "Glossário", "Perguntas frequentes", "Referências"]
)


# ════════════════════════════════════════════════════════════════════════════
# ABA — COMO USAR (fluxo do dia, por departamento)
# ════════════════════════════════════════════════════════════════════════════
with tab_uso:
    st.markdown("""
<div class='aj-card'>
  <div class='aj-card-head'>
    <div class='aj-card-title'>Fluxo de um dia</div>
    <span class='aj-chip-ok'>&#10003; Só departamentos — sem nomes de pessoas</span>
  </div>
  <table class='aj-table'>
    <thead><tr>
      <th class='aj-th' style='width:92px'>Hora</th>
      <th class='aj-th' style='width:160px'>Responsável</th>
      <th class='aj-th'>O que acontece</th>
    </tr></thead>
    <tbody>
      <tr>
        <td class='aj-td'>06h&ndash;21h</td>
        <td class='aj-td'><span class='aj-pill'>Produção</span><span class='aj-pill'>Corte</span><span class='aj-pill'>Embalagem</span></td>
        <td class='aj-td'>Produzem, viram, cortam e embalam ao longo de todo o dia</td>
      </tr>
      <tr>
        <td class='aj-td'>08h&ndash;10h</td>
        <td class='aj-td'><span class='aj-pill'>Estoque</span></td>
        <td class='aj-td'>Conta o estoque físico na fábrica (45g, Mini, Pet, Pão de Mel, Balas)</td>
      </tr>
      <tr>
        <td class='aj-td'>~10h</td>
        <td class='aj-td'><span class='aj-pill'>Estoque</span></td>
        <td class='aj-td'>Preenche a folha do dia no Lançamento</td>
      </tr>
      <tr>
        <td class='aj-td'>~10h30</td>
        <td class='aj-td'><span class='aj-pill aj-pill-brand'>Gestão</span></td>
        <td class='aj-td'>Confere Painel e Insights e define as ordens do dia</td>
      </tr>
      <tr>
        <td class='aj-td'>~10h30</td>
        <td class='aj-td'><span class='aj-pill aj-pill-brand'>Gestão</span></td>
        <td class='aj-td'>Volta no Lançamento e ajusta corte, embalagem e produção</td>
      </tr>
      <tr>
        <td class='aj-td'>Fim do dia</td>
        <td class='aj-td'><span class='aj-pill'>Estoque</span></td>
        <td class='aj-td'>Confere e salva a folha</td>
      </tr>
    </tbody>
  </table>
</div>

<div class='aj-card'>
  <div class='aj-card-title' style='margin-bottom:8px'>Por onde começar</div>
  <div class='aj-tela'><div class='aj-tela-nome'>1. Início</div><div class='aj-tela-desc'>Mostra o status do dia, os alertas de estoque e os atalhos pras telas mais usadas.</div></div>
  <div class='aj-tela'><div class='aj-tela-nome'>2. Lançamento</div><div class='aj-tela-desc'>O coração do sistema: a folha do dia, igualzinha ao papel da fábrica.</div></div>
  <div class='aj-tela'><div class='aj-tela-nome'>3. Painel e Insights</div><div class='aj-tela-desc'>A leitura do dia por departamento e o diagnóstico automático pra apoiar a decisão.</div></div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# ABA — TELAS DO SISTEMA (mapa atualizado, 18 telas em 8 grupos)
# ════════════════════════════════════════════════════════════════════════════
GRUPOS_TELAS = [
    ("Início", [
        ("Início", "Porta de entrada: status do dia, alertas de estoque e atalhos."),
    ]),
    ("Operação do dia", [
        ("Lançamento", "Onde a folha do dia é preenchida — a mesma do papel da fábrica."),
        ("Painel", "Visão do dia por departamento: Produção, Corte, Embalagem e Estoque."),
    ]),
    ("Sugestão", [
        ("Palha", "Sugestão de corte e de produção de palha (apoio à decisão da Gestão)."),
        ("Cocada", "Sugestão de corte, produção, potes e viração de cocada."),
    ]),
    ("Vendas & resultado", [
        ("Vendas", "Curva ABC de demanda a partir das vendas reais lidas do SIGE."),
        ("Lucratividade", "Contribuição por produto: o que mais puxa o resultado."),
        ("Produção × Demanda", "Compara o que é produzido com o que é vendido, sabor a sabor."),
    ]),
    ("Análise da produção", [
        ("Curva ABC", "Classifica os produtos por volume (princípio de Pareto)."),
        ("Média Móvel", "Compara a meta com a média recente e sinaliza quando recalibrar."),
        ("Anomalias ML", "Detecta folhas fora do padrão usando aprendizado de máquina."),
        ("Insights", "Diagnóstico automático por regras conhecidas da operação."),
        ("Bala", "Acompanhamento da Bala: produção, estoque e giro."),
    ]),
    ("Cadastros", [
        ("Suprimentos", "Insumos, receitas (BOM), movimentações e necessidades do dia."),
        ("Reconciliação SIGE", "Compara o estoque do nosso sistema com o do SIGE, item a item."),
        ("Equipe", "Funcionários, capacidades por atividade e presença por dia."),
    ]),
    ("Suporte", [
        ("Assistente IA", "Pergunte ao Claude sobre a operação, em linguagem do dia a dia."),
        ("Ajuda", "Esta página."),
    ]),
    ("Admin", [
        ("Cadastrar BOM (setup)", "Carga inicial das receitas. Uso raro — área técnica."),
    ]),
]

_telas_html = ["<div class='aj-card'>"]
for grupo, telas in GRUPOS_TELAS:
    _telas_html.append(f"<div class='aj-grp'>{_esc(grupo)}</div>")
    for nome, desc in telas:
        _telas_html.append(
            f"<div class='aj-tela'><div class='aj-tela-nome'>{_esc(nome)}</div>"
            f"<div class='aj-tela-desc'>{_esc(desc)}</div></div>"
        )
_telas_html.append("</div>")

_telas_html.append("""
<div class='aj-card'>
  <div class='aj-card-title' style='margin-bottom:8px'>Status atual do sistema</div>
  <div class='aj-tela-desc' style='margin-bottom:6px'>&bull; Hospedado no Hugging Face (na nuvem), acessível pelo navegador no computador ou no celular.</div>
  <div class='aj-tela-desc' style='margin-bottom:6px'>&bull; Banco de dados em nuvem (Postgres) com backup automático diário.</div>
  <div class='aj-tela-desc' style='margin-bottom:6px'>&bull; Assistente de IA <b>ativado</b> (usa o Claude, da Anthropic).</div>
  <div class='aj-tela-desc'>&bull; Integração com o SIGE em modo <b>somente leitura</b> (lê custo, vendas e estoque; nunca escreve).</div>
</div>
""")
st.markdown("".join(_telas_html), unsafe_allow_html=True)

st.markdown("<div class='aj-grp' style='margin-top:6px'>Entenda melhor as análises</div>", unsafe_allow_html=True)
st.markdown("""
<details class='aj-faq'><summary>Insights — diagnóstico por regras</summary>
<div class='aj-faq-a'>Sinaliza padrões conhecidos da operação, sem aprendizado de máquina. Exemplos: tachos
parciais (quando a ordem de produção não é múltiplo de 8, a sobra vira pote — não é desperdício);
possível sobrecarga da Embalagem (limite configurável); proporção entre sabores fora do esperado.
São pistas pra investigar, nunca uma ordem.</div></details>

<details class='aj-faq'><summary>Curva ABC — prioridade por volume</summary>
<div class='aj-faq-a'>Separa os produtos em três classes pelo princípio de Pareto: A = os que somam ~80% do
volume (atenção máxima), B = os próximos ~15%, C = os últimos ~5%. Usa o fluxo de bandejas cortadas
somado no período — nunca o que está parado na prateleira (princípio estoque × fluxo).</div></details>

<details class='aj-faq'><summary>Anomalias ML — folhas fora do padrão</summary>
<div class='aj-faq-a'>Um algoritmo de aprendizado de máquina (Isolation Forest) aponta as folhas que mais
destoam do histórico, sem ninguém programar regra. "Atípica" não quer dizer "erro": pode ser encomenda
especial ou dia diferente. Fica confiável a partir de ~60 folhas (cerca de 3 meses de dados).</div></details>

<details class='aj-faq'><summary>Média Móvel — a meta ainda está calibrada?</summary>
<div class='aj-faq-a'>Compara a meta fixa de cada dia da semana com a média das últimas semanas. Diferença
abaixo de 10% = meta calibrada; entre 10% e 20% = acompanhar; acima de 20% = a meta provavelmente
está desatualizada e vale recalibrar. A janela de semanas é ajustável.</div></details>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# ABA — GLOSSÁRIO (pesquisável)
# ════════════════════════════════════════════════════════════════════════════
TERMOS = [
    ("Anomalia / Atípico",
     "Folha que destoa do padrão do histórico, apontada pelo algoritmo Isolation Forest. Não é necessariamente um erro — pode ser pedido especial ou dia diferente."),
    ("BOM (lista de materiais)",
     "A receita: lista de insumos e quantidades pra produzir 1 unidade do produto. Ex.: 1 tacho de Tradicional = 19,5 L de leite + 8 kg de açúcar + 5 kg de coco. Cadastrada em Suprimentos."),
    ("Bandeja",
     "Unidade física de divisão da cocada. 1 tacho rende 8 bandejas (a Zero, 3). A bandeja pronta para corte pesa ~5,5 kg."),
    ("Cortados ① (1)",
     "Cortado bruto: o que já foi cortado mas ainda não embalado. Foto do dia."),
    ("Cortados ② (2)",
     "Tudo que passou pela bancada de corte no dia. É um valor calculado (cortado bruto + embalado + papelzinho da produção). Mostra o trabalho real do dia."),
    ("Cortados ③ (3)",
     "Cortados ② menos o parâmetro real do dia. Positivo = sobrou; negativo = faltou. Indicador de calibração."),
    ("Curva ABC",
     "Classificação dos produtos em três grupos por volume: A (top ~80%), B (próximos ~15%), C (últimos ~5%). Princípio de Pareto."),
    ("Estoque × Fluxo",
     "Princípio de Forrester (1961): estoque (a foto de um dia) não pode ser somado entre dias; fluxo (o que entrou ou saiu no dia) pode. Por isso as análises usam o fluxo, não a prateleira."),
    ("Hugging Face",
     "A plataforma na nuvem onde o sistema está hospedado e acessível pelo navegador. O app foi migrado pra lá em 17/05/2026."),
    ("Isolation Forest",
     "Algoritmo de aprendizado de máquina que encontra pontos fora da curva. Usado na tela Anomalias ML."),
    ("Lead time",
     "Tempo entre pedir um insumo ao fornecedor e ele chegar à fábrica. Importante pro cálculo de necessidades do dia (Suprimentos)."),
    ("LLM / Assistente IA",
     "Modelo de linguagem como o Claude. Responde perguntas em português e explica análises em linguagem do dia a dia."),
    ("Média Móvel",
     "Média das últimas semanas (do mesmo dia da semana). Atualiza sozinha conforme novas folhas entram e detecta mudança gradual de demanda."),
    ("MRP (planejamento de materiais)",
     "Técnica clássica de PCP: calcula a necessidade de insumos a partir da ordem de produção × receita × estoque atual. Aplicada em Suprimentos."),
    ("Ordem de corte",
     "Quantas bandejas cortar no dia (em bandejas). É fluxo — pode somar entre dias."),
    ("Ordem de embalagem",
     "Quantas unidades embalar no dia (em unidades). É fluxo. A cocada Pet não tem ordem de embalagem separada."),
    ("Ordem de produção",
     "Quantas bandejas produzir no dia via tacho (responsabilidade da Produção). Quando não é múltiplo de 8, a sobra vira pote de 260 g / 605 g."),
    ("Ordem de viração",
     "Pedido pra a Produção virar X bandejas — medida corretiva quando as viradas estão baixas."),
    ("Papelzinho da Produção",
     "Documento físico onde a Produção anota a produção do dia em 5 colunas × 6 sabores. Digitalizado dentro do Lançamento."),
    ("Parâmetro real do dia",
     "A meta de produção do dia, em unidades. Pode ser diferente da meta base por causa de pedidos antecipados."),
    ("P/Virar",
     "Bandejas esperando para serem viradas (etapa da cocada, antes do corte)."),
    ("Sigma (σ) / Desvio-padrão",
     "Medida de variação. ±1σ é comum (~68% dos casos); ±2σ é raro (~5%); ±3σ é muito raro (~0,3%)."),
    ("SIGE",
     "O ERP da empresa (sistema oficial). O nosso sistema lê dele custo, vendas e estoque — em modo somente leitura."),
    ("Suprimentos",
     "Módulo de gestão de matéria-prima, embalagens, potes e cintas. Aplica MRP simplificado."),
    ("Tacho",
     "Unidade de produção. 1 tacho de cocada = 8 bandejas (Zero = 3); 1 tacho de bala = 30 balas. A receita é por tacho."),
    ("Viradas ②",
     "Bandejas viradas (etapa intermediária da cocada). Calculado: viradas anotadas menos o total das ordens de corte."),
]

with tab_gloss:
    cards = [
        f"<div class='aj-gloss'><div class='aj-gloss-termo'>{_esc(termo)}</div>"
        f"<div class='aj-gloss-def'>{_esc(definicao)}</div></div>"
        for termo, definicao in TERMOS if _casa(termo, definicao)
    ]
    if cards:
        st.markdown(f"<div class='aj-gloss-grid'>{''.join(cards)}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='aj-vazio'>Nenhum termo encontrado para “{_esc(q)}”.</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# ABA — PERGUNTAS FREQUENTES (pesquisável)
# ════════════════════════════════════════════════════════════════════════════
FAQS = [
    ("Quem decide as ordens de produção, corte e embalagem?",
     "Sempre a Gestão. O sistema sugere, visualiza e alerta, mas a decisão final é humana. A sugestão automática (em construção) vai pré-preencher os campos a partir da capacidade da equipe e da demanda — e a Gestão segue aprovando e ajustando."),
    ("Por que as análises usam as ordens do dia e não o que está embalado?",
     "Por causa do princípio estoque × fluxo (Forrester, 1961). O embalado é a foto da prateleira em cada dia e não pode ser somado entre dias; as ordens (corte, embalagem) são fluxo do dia e podem somar. Curva ABC, Média Móvel e Anomalias usam o fluxo."),
    ("Mudei a meta na tabela e não apareceu na hora. Por quê?",
     "O sistema guarda as tabelas de referência por até 30 minutos pra ficar mais rápido. Pra ver na hora, atualize a página (Ctrl+F5)."),
    ("Posso confiar 100% na detecção de anomalias?",
     "Não. Com poucas folhas a precisão é limitada — o modelo ainda está aprendendo o que é “normal”. A partir de ~60 folhas (cerca de 3 meses) fica robusto. Use como pista pra investigar, não como diagnóstico fechado."),
    ("O Assistente de IA está funcionando?",
     "Sim, está ativado. Ele usa o Claude (da Anthropic) e responde sobre a operação em linguagem simples. O custo por pergunta é baixo e roda com o crédito da conta."),
    ("Qual a diferença entre Insights e Anomalias ML?",
     "Insights usa regras escritas à mão (ex.: “se um sabor passa muito do outro, alerta”). Anomalias ML usa um algoritmo que aprende sozinho o que é normal. Os dois se completam: Insights é explicável; o de máquina acha o que ninguém previu."),
    ("O app está lento, o que pode ser?",
     "Causas comuns: primeiro acesso do dia (o servidor estava dormindo — leva alguns segundos pra acordar); primeira navegação com tudo carregando; ou uma tela que lê o SIGE (que é mais lento). Se passar de 30 segundos com frequência, me mande um print."),
    ("Dá pra usar no celular?",
     "Dá. As telas se adaptam à tela pequena. Os gráficos funcionam, mas alguns ficam mais confortáveis no computador."),
    ("Como faço backup dos dados?",
     "O banco de dados na nuvem tem backup automático diário. Pra uma cópia manual, fale com o responsável técnico do sistema."),
]

with tab_faq:
    blocos = [
        f"<details class='aj-faq'><summary>{_esc(p)}</summary><div class='aj-faq-a'>{_esc(r)}</div></details>"
        for p, r in FAQS if _casa(p, r)
    ]
    if blocos:
        st.markdown("".join(blocos), unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='aj-vazio'>Nenhuma pergunta encontrada para “{_esc(q)}”.</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# ABA — REFERÊNCIAS (pro TCC)
# ════════════════════════════════════════════════════════════════════════════
REFERENCIAS = [
    ("Pareto, V. (1896). Cours d'Économie Politique. Lausanne: Rouge.",
     "Princípio proposto ao estudar a distribuição de renda na Itália (80% da terra com 20% da população). Generalizado como Lei de Pareto.",
     "Tela Curva ABC."),
    ("Juran, J. M. (1951). Quality Control Handbook. New York: McGraw-Hill.",
     "Operacionalizou o princípio de Pareto na gestão da qualidade (“os poucos vitais e os muitos triviais”).",
     "Classificação A/B/C dos produtos."),
    ("Forrester, J. W. (1961). Industrial Dynamics. Cambridge: MIT Press.",
     "Estabeleceu a distinção entre estoque (foto) e fluxo (taxa). Conceito aplicado em todo o sistema pra não somar fotos de estoque como se fossem fluxo.",
     "Princípio transversal — Curva ABC, Média Móvel, Anomalias."),
    ("Wheelwright, S. C., & Hyndman, R. J. (1998). Forecasting: Methods and Applications. 3ª ed. New York: Wiley.",
     "Referência clássica em previsão de séries temporais; cobre os métodos de média móvel.",
     "Tela Média Móvel."),
    ("Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation Forest. 8th IEEE Int. Conf. on Data Mining, 413-422.",
     "Algoritmo de aprendizado de máquina para detecção de pontos fora da curva.",
     "Tela Anomalias ML."),
    ("Heizer, J., & Render, B. (2014). Operations Management. 11ª ed. Boston: Pearson.",
     "Livro-texto padrão de Gestão de Operações; o capítulo 13 cobre planejamento de capacidade.",
     "Tela Equipe — capacidades por funcionário."),
    ("Brown, T. B. et al. (2020). Language Models are Few-Shot Learners. NeurIPS, 33, 1877-1901.",
     "Artigo que apresentou o GPT-3 e o conceito de aprendizado com poucos exemplos em modelos de linguagem.",
     "Assistente de IA."),
    ("Anthropic. (2024). Constitutional AI: Harmlessness from AI Feedback. arXiv:2212.08073.",
     "Fundamentos do treinamento dos modelos da família Claude, usados no Assistente de IA.",
     "Assistente de IA."),
]

with tab_ref:
    st.markdown(
        "<div class='aj-sub' style='margin-bottom:10px'>Para usar no TCC (Capítulo 2 — Revisão de Literatura).</div>",
        unsafe_allow_html=True,
    )
    refs = [
        f"<div class='aj-ref'><div class='aj-ref-titulo'>{_esc(titulo)}</div>"
        f"<div class='aj-ref-corpo'>{_esc(corpo)}</div>"
        f"<div class='aj-ref-uso'>Aplicação: {_esc(uso)}</div></div>"
        for titulo, corpo, uso in REFERENCIAS
    ]
    st.markdown("".join(refs), unsafe_allow_html=True)

componentes.rodape("")
