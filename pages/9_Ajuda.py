"""
pages/9_Ajuda.py — Central de Ajuda / Documentação do Sistema

Página dedicada com:
- Glossário de termos técnicos
- Explicação de cada feature do sistema
- Perguntas frequentes (FAQ)
- Referências bibliográficas (pra TCC)

Decisão (19/05/2026): mover TODO conteúdo didático pra cá pra deixar
as outras páginas limpas e profissionais. Pedido do Leonardo:
"esses textos longos e desnecessários nas abas onde visualizamos
informação — quero cara profissional".
"""
import streamlit as st
import os

# Bootstrap defensivo (HF Spaces sem secrets.toml)
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

# Tema visual centralizado (Inter font + paleta clean)
from ui_theme import aplicar_tema
aplicar_tema()


# ════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ════════════════════════════════════════════════════════════════════════════
st.title("Central de Ajuda")
st.caption(
    "Documentação completa do sistema PCP Vó Nena. Use o índice abaixo pra "
    "navegar até a seção que te interessa."
)


# ════════════════════════════════════════════════════════════════════════════
# ÍNDICE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
### Índice

| Seção | O que tem |
|---|---|
|  [Como usar o sistema](#como-usar) | Fluxo do dia, abas principais, atalhos |
|  [Páginas de Análise](#paginas-analise) | Insights, Curva ABC, Anomalias ML, Média Móvel |
|  [Suprimentos](#suprimentos) | Insumos, BOM, Movimentações, Necessidades |
|  [Equipe](#equipe) | Funcionários, Capacidades, Presença |
|  [Assistente IA](#assistente-ia) | Como funciona, custos, status atual |
|  [Glossário](#glossario) | Termos técnicos explicados |
|  [Perguntas Frequentes](#faq) | FAQ sobre o sistema |
|  [Referências Bibliográficas](#referencias) | Pro TCC |
""")

st.divider()


# ════════════════════════════════════════════════════════════════════════════
# COMO USAR O SISTEMA
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<a id='como-usar'></a>", unsafe_allow_html=True)
st.header("Como usar o sistema")

st.markdown("""
**Fluxo típico de um dia:**

| Hora | Quem | O quê |
|---|---|---|
| 7h–10h | Leonardo | Conta estoque físico (45g, Mini, Pet, PM, Balas) na fábrica |
| ~10h | Leonardo | Abre **Lançamento** → preenche a folha do dia |
| ~10h30 | Eraldo | Confere o **Painel** + **Insights** + decide ordens |
| ~10h30 | Eraldo | Volta no **Lançamento** → ajusta ord_corte / ord_emb / ord_prod |
| 11h–18h | Equipe | Executa as ordens (Joel produz, Gil corta, Leonília embala) |
| Fim do dia | Leonardo | Confere folha + salva |

**Mapa de páginas (sidebar esquerda):**

| Página | Pra quê |
|---|---|
| **Lançamento** | Onde a folha do dia é preenchida (Eraldo + Leonardo) |
| **Painel** | Visualização por departamento (Produção, Corte, Embalagem) |
| **Insights** | Diagnóstico operacional automático (regras hardcoded) |
| **Suprimentos** | Cadastro de insumos + receitas + estoque MP |
| **Curva ABC** | Classificação dos produtos por volume |
| **Anomalias ML** | Detecção de folhas atípicas via Machine Learning |
| **Média Móvel** | Comparativo meta × realidade observada |
| **Assistente IA** | Pergunte ao Claude (LLM) — quando ativado |
| **Equipe** | Funcionários, capacidades, presença diária |
| **Ajuda** | Esta página |
""")

st.divider()


# ════════════════════════════════════════════════════════════════════════════
# PÁGINAS DE ANÁLISE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<a id='paginas-analise'></a>", unsafe_allow_html=True)
st.header("Páginas de Análise")

# --- Insights ---
st.subheader("Insights")
st.markdown("""
<div class='card-feature'>
<b>O que faz:</b> diagnóstico operacional automático baseado em <b>regras hardcoded</b>.
Sinaliza padrões conhecidos sem precisar de Machine Learning.<br><br>
<b>Hipóteses ativas:</b>
<ul>
<li><b>Insight Master</b> — possível viés sistemático no Cortados ③ (a validar com mais dados)</li>
<li><b>H1 — Tachos parciais</b> — quando ord_prod_band não é múltiplo de 8, sobra vira pote 260g/605g (NÃO é desperdício)</li>
<li><b>H4 — Sobrecarga Embalagem</b> — slider configurável de capacidade (padrão 3000 und/dia, varia conforme equipe)</li>
<li><b>H5 — Anomalia Palha</b> — Leite em Pó &gt; Tradicional × 1.3 (validado pela Gestão)</li>
<li><b>H6 — Proporção T/L</b> — meta 2:1; oscilações podem ser pedidos antecipados, não desbalanceamento</li>
</ul>
</div>
""", unsafe_allow_html=True)

# --- Curva ABC ---
st.subheader("Curva ABC")
st.markdown("""
<div class='card-feature'>
<b>O que faz:</b> separa automaticamente os produtos em 3 classes de prioridade,
baseado no princípio de Pareto (80/20).<br><br>
<b>Classes:</b>
<ul>
<li><b>A </b> — produtos que somam 80% do volume produzido. Atenção máxima.</li>
<li><b>B </b> — próximos 15%. Cadência regular.</li>
<li><b>C </b> — últimos 5%. Lotes maiores e espaçados.</li>
</ul>
<b>Métrica usada:</b> <code>ord_corte_*</code> (fluxo de bandejas), somada ao longo de
todas as folhas registradas. <b>NÃO usa Embalados</b> (que é estoque na prateleira,
não pode ser somado entre dias — princípio Forrester 1961).
</div>
""", unsafe_allow_html=True)

# --- Anomalias ML ---
st.subheader("Anomalias ML")
st.markdown("""
<div class='card-feature'>
<b>O que faz:</b> usa <b>Machine Learning não-supervisionado</b> (algoritmo Isolation
Forest) pra detectar folhas que destoam do padrão histórico — sem ninguém precisar
programar regra.<br><br>
<b>Como ler:</b>
<ul>
<li><b>Score de estranheza alto</b> = folha mais diferente do padrão</li>
<li><b>Top 3 features</b> = quais campos mais contribuíram pro desvio</li>
<li><b>σ (sigma)</b> = quantos desvios-padrão acima/abaixo do normal. ±2σ é raro (~5%).</li>
<li><b>"Atípica" ≠ "erro"</b>: pode ser encomenda especial, dia atípico, etc. É <b>pista pra investigar</b>.</li>
</ul>
<b>Limitação:</b> com menos de 30 folhas, precisão é limitada. Fica robusto a partir de ~60 folhas (3 meses).
</div>
""", unsafe_allow_html=True)

# --- Média Móvel ---
st.subheader("Média Móvel")
st.markdown("""
<div class='card-feature'>
<b>O que faz:</b> compara a meta fixa da tabela <code>metas_45g</code> (ex: "Tradicional
45g segunda = 5.200 und") com a média das últimas N semanas. Se a realidade
descolou da meta, sinaliza pra recalibrar.<br><br>
<b>Status dos desvios:</b>
<ul>
<li><b> OK</b> — diferença &lt; 10% (meta calibrada)</li>
<li><b> Atenção</b> — 10-20% (acompanhar)</li>
<li><b> Recalibrar</b> — &gt; 20% (meta provavelmente desatualizada)</li>
</ul>
<b>Janela móvel ajustável:</b> 2-8 ocorrências do mesmo dia da semana. Padrão 4.<br>
<b>Métrica usada:</b> <code>ord_emb_45g</code> (fluxo de embalagem 45g). Não usa Embalados.
</div>
""", unsafe_allow_html=True)

st.divider()


# ════════════════════════════════════════════════════════════════════════════
# SUPRIMENTOS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<a id='suprimentos'></a>", unsafe_allow_html=True)
st.header("Suprimentos")

st.markdown("""
<div class='card-feature'>
<b>O que é:</b> módulo de gestão de matéria-prima, embalagens, potes, cintas — qualquer
item consumível. Aplica MRP simplificado (Material Requirements Planning).<br><br>
<b>4 abas:</b>
<ul>
<li><b> Insumos</b> — cadastro de cada item (nome, código, unidade, estoque atual, estoque mínimo, fornecedor, lead time)</li>
<li><b> BOM</b> — receitas (Bill of Materials): pra produzir 1 tacho de Tradicional → 19L leite + 8kg açúcar + 4kg coco + ...</li>
<li><b> Movimentações</b> — histórico de entradas (compras) e saídas (consumo na produção)</li>
<li><b>Necessidades do dia</b> — cruza folha do dia × BOM × estoque atual → "Vai faltar X kg de Y"</li>
</ul>
<b>Status atual:</b> schema pronto, aguardando cadastro real de insumos (depende de
entrevista com Eraldo + exportação CSV do Sigee Cloud com Mariana).
</div>
""", unsafe_allow_html=True)

st.divider()


# ════════════════════════════════════════════════════════════════════════════
# EQUIPE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<a id='equipe'></a>", unsafe_allow_html=True)
st.header("Equipe")

st.markdown("""
<div class='card-feature'>
<b>O que é:</b> cadastro de funcionários + capacidades por atividade + presença diária.
Fundação da Camada 2 do sistema (Sugestão Automática de Ordem do Dia — em construção).<br><br>
<b>3 abas:</b>
<ul>
<li><b> Funcionários</b> — CRUD agrupado por departamento (Gestão, Produção, Corte, Embalagem, etc.)</li>
<li><b> Capacidades</b> — pra cada funcionário, quanto produz por atividade (ex: "Gil corta 30 band 45g/dia")</li>
<li><b> Presença do dia</b> — quem trabalhou em cada data, com observações (chegou tarde, etc.)</li>
</ul>
<b>Como será usado (próxima etapa):</b> o algoritmo de Sugestão de Ordem vai calcular
a <b>capacidade efetiva do dia</b> = soma(capacidade × presente) e usar como restrição
pra pré-preencher ord_corte, ord_emb, ord_prod.
</div>
""", unsafe_allow_html=True)

st.divider()


# ════════════════════════════════════════════════════════════════════════════
# ASSISTENTE IA
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<a id='assistente-ia'></a>", unsafe_allow_html=True)
st.header("Assistente IA")

st.markdown("""
<div class='card-feature'>
<b>O que é:</b> integração com o Claude (LLM da Anthropic). Permite perguntas em
PT-BR sobre a operação, e respostas em linguagem humana baseadas no contexto real
da fábrica.<br><br>
<b>Funcionalidades implementadas:</b>
<ul>
<li><b>Q&A geral</b> (página Assistente IA) — pergunta livre + contexto da folha + histórico</li>
<li><b>Explicação de Anomalia</b> (botão na página Anomalias ML) — traduz output técnico (z-score) em narrativa</li>
</ul>
<b>Status atual:</b> código entregue mas <b>não ativado em produção</b> por questão de
custo. Pra ativar, basta configurar a secret <code>ANTHROPIC_API_KEY</code> no HF Spaces.<br><br>
<b>Custos estimados (se ativar):</b>
<ul>
<li>Por consulta Haiku 4.5: ~R$0,02-0,05</li>
<li>Mês típico (10 perguntas/dia): ~R$5-10</li>
<li>Pro TCC inteiro (~2 meses): ~R$10-25 total</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.divider()


# ════════════════════════════════════════════════════════════════════════════
# GLOSSÁRIO
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<a id='glossario'></a>", unsafe_allow_html=True)
st.header("Glossário")
st.caption("Termos técnicos do sistema, em ordem alfabética.")

termos = [
    ("Anomalia / Atípico",
     "Folha que destoa do padrão do histórico. Detectada pelo algoritmo Isolation Forest. Não é necessariamente um erro — pode ser pedido especial, dia diferente, etc."),
    ("BOM (Bill of Materials)",
     "Receita: lista de insumos e quantidades pra produzir 1 unidade do produto. Ex: 1 tacho Tradicional = 19L leite + 8kg açúcar + 4kg coco. Cadastrado em Suprimentos > BOM."),
    ("Camada 0",
     "Folha de Produção digital substituindo o papel. Núcleo do sistema (Lançamento + Painel)."),
    ("Camada 1",
     "Visualização e diagnóstico (Insights). Regras hardcoded ativas hoje."),
    ("Camada 1.5",
     "ML e IA estatística (Curva ABC, Anomalias ML, Média Móvel). Atual fase do projeto."),
    ("Camada 2",
     "Sugestão automática (Sugestão de Ordem do Dia). Em construção — depende de cadastro de Equipe + capacidades."),
    ("Cortados ① (1)",
     "Cortado bruto: produto que foi cortado mas ainda não embalado. Snapshot do dia."),
    ("Cortados ② (2)",
     "Total que passou pela bancada de corte hoje. Derivado: cort1_* + emb_* + papelzinho_joel.joel_*. Mostra o trabalho REAL do dia."),
    ("Cortados ③ (3)",
     "Cortados ② menos o param_real do dia. Positivo = sobrou; negativo = faltou. Indicador de calibração."),
    ("Curva ABC",
     "Classificação dos produtos em 3 grupos por volume: A (top 80%), B (próximos 15%), C (últimos 5%). Princípio de Pareto."),
    ("Estoque vs Fluxo",
     "Princípio de Forrester (1961): valor de estoque (snapshot) NÃO pode ser somado entre dias; valor de fluxo (entrada/saída do dia) PODE. emb_* é estoque; ord_corte_*/ord_emb_* são fluxo."),
    ("HF Spaces / Hugging Face Spaces",
     "Plataforma onde o app está hospedado (huggingface.co/spaces). Migramos do Streamlit Cloud em 17/05/2026 pra ter 16x mais memória RAM."),
    ("Isolation Forest",
     "Algoritmo de Machine Learning não-supervisionado que detecta outliers. Usado na página Anomalias ML."),
    ("Lead time",
     "Tempo entre pedir um insumo ao fornecedor e ele chegar na fábrica. Crítico pro cálculo de Necessidades do dia (Suprimentos)."),
    ("LLM (Large Language Model)",
     "Modelo de linguagem como o Claude. Usado pra responder perguntas em PT-BR ou explicar anomalias em linguagem humana."),
    ("Média Móvel",
     "Média das últimas N ocorrências (do mesmo dia da semana). Atualiza automaticamente conforme novas folhas entram. Detecta mudança gradual de demanda."),
    ("MRP (Material Requirements Planning)",
     "Técnica clássica de PCP: calcula necessidade de insumos a partir de ordem de produção × BOM × estoque atual. Aplicado em Suprimentos > Necessidades do dia."),
    ("ord_corte_* (45g, Mini, Pet)",
     "Ordem do dia pra cortar X bandejas. Em bandejas. FLUXO — pode somar entre dias."),
    ("ord_emb_* (45g, Mini)",
     "Ordem do dia pra embalar X unidades. Em unidades. FLUXO. Cocada Pet não tem ord_emb separado."),
    ("ord_prod_band",
     "Ordem do dia pra produzir X bandejas via tacho (Sr. Joel). Quando não múltiplo de 8: sobra vira pote 260g/605g."),
    ("ord_prod_virada",
     "Ordem do dia pra Sr. Joel virar X bandejas (resposta corretiva quando Viradas② tá baixo)."),
    ("P/Virar",
     "Bandejas que estão esperando ser viradas (etapa do processo de cocada antes do corte). joel_pv no banco."),
    ("Papelzinho do Joel",
     "Documento físico onde o Sr. Joel anota produção do dia em 5 colunas × 6 sabores. Digitalizado em papelzinho_joel."),
    ("param_real_45g / Mini / Pet",
     "Parâmetro real do dia: meta de produção em unidades. Pode ser diferente da meta base (metas_45g) por causa de pedidos antecipados."),
    ("Score de estranheza / Anomaly score",
     "Valor que o Isolation Forest atribui a cada folha. Quanto maior, mais a folha destoa do padrão."),
    ("σ (sigma) / Desvio-padrão",
     "Medida estatística de variação. ±1σ é comum (~68% das observações). ±2σ é raro (~5%). ±3σ é muito raro (~0,3%)."),
    ("Suprimentos",
     "Módulo de gestão de matéria-prima + embalagens + potes + cintas. MRP simplificado."),
    ("Tacho",
     "Unidade de produção do Sr. Joel. 1 tacho cocada = 8 bandejas (Zero = 3). 1 tacho bala = 30 balas. Receita por tacho."),
    ("Viradas ②",
     "Bandejas viradas (etapa intermediária do processo de cocada). joel_v − ord_corte_total. Snapshot."),
    ("z-score",
     "Quantos desvios-padrão um valor está acima/abaixo da média. Igual ao σ. Usado nas Top 3 features das anomalias."),
]

for termo, def_ in termos:
    st.markdown(
        f"<div class='glossario-termo'><b>{termo}</b> — {def_}</div>",
        unsafe_allow_html=True,
    )

st.divider()


# ════════════════════════════════════════════════════════════════════════════
# FAQ
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<a id='faq'></a>", unsafe_allow_html=True)
st.header("Perguntas Frequentes (FAQ)")

faqs = [
    ("Por que algumas páginas usam ord_corte_* e não emb_* nos cálculos?",
     "Princípio estoque vs fluxo (Forrester, 1961). emb_* é snapshot do estoque na prateleira em cada dia, NÃO pode ser somado entre dias. ord_corte_* é fluxo (demanda do dia), pode somar. Curva ABC, Média Móvel e Anomalias ML usam fluxo."),

    ("Por que minha alteração na meta da tabela metas_45g não aparece no app imediatamente?",
     "O sistema tem cache de 30 minutos pras tabelas de referência. Pra forçar atualização imediata, dá refresh na página (Ctrl+F5)."),

    ("Posso confiar 100% na Detecção de Anomalia ML?",
     "Não. Com menos de 30 folhas, a precisão é limitada — o modelo ainda está aprendendo o 'normal'. A partir de ~60 folhas (3 meses), fica robusto. Use como pista pra investigar, não diagnóstico fechado."),

    ("O Assistente IA está funcionando?",
     "O código está pronto, mas não está ativado. Pra ativar, é preciso criar conta na Anthropic (console.anthropic.com), gerar API key e configurar como secret ANTHROPIC_API_KEY no HF Spaces. Custo estimado: R$5-10/mês de uso típico."),

    ("Quem decide as ordens de produção/corte/embalagem?",
     "Sempre o Eraldo (Gestão). O sistema sugere/visualiza/alerta, mas a decisão final é humana. A Camada 2 (em construção) vai pré-preencher os campos baseado em capacidade da equipe + demanda — mas o Eraldo continua aprovando/ajustando."),

    ("Qual a diferença entre as páginas Insights e Anomalias ML?",
     "Insights usa REGRAS PROGRAMADAS à mão (ex: 'se LP > T × 1.3, alerta'). Anomalias ML usa um ALGORITMO que aprende sozinho o normal. Os dois se complementam: Insights é explicável; ML detecta coisas que ninguém previu."),

    ("Por que algumas anomalias aparecem com valor positivo e outras negativo no z-score?",
     "Positivo (+σ) = aquele campo estava ACIMA do normal. Negativo (-σ) = abaixo. Ex: 'Ordem de embalagem de Tradicional +3.2σ' significa que naquele dia foi muito acima do esperado."),

    ("O app está lento, o que pode ser?",
     "Várias causas possíveis: (1) primeiro carregamento (cold start) — normal demorar 5-10s; (2) cache vazio — primeira navegação carrega tudo; (3) folha do dia muito grande. Se persistir mais de 30s, me avisa via prints."),

    ("Posso usar o sistema no celular?",
     "Sim, todas as páginas são responsivas. O Streamlit detecta tela pequena e adapta layout. Os gráficos Plotly funcionam, mas alguns expandem melhor em desktop."),

    ("Como faço backup dos dados?",
     "Os dados ficam no Supabase (Postgres), que tem backup automático diário. Pra exportar manualmente, peça pro Leonardo gerar um dump SQL via psql ou pgAdmin."),
]

for q, a in faqs:
    st.markdown(f"<div class='faq-q'> {q}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='faq-a'>{a}</div>", unsafe_allow_html=True)

st.divider()


# ════════════════════════════════════════════════════════════════════════════
# REFERÊNCIAS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<a id='referencias'></a>", unsafe_allow_html=True)
st.header("Referências Bibliográficas")
st.caption("Pra usar no TCC (Capítulo 2 — Revisão de Literatura).")

st.markdown("""
**Princípios fundamentais aplicados no sistema:**

<div class='ref-box'>
<b>Pareto, V. (1896).</b> <i>Cours d'Économie Politique.</i> Lausanne: Rouge.<br>
Princípio originalmente proposto ao estudar distribuição de renda na Itália:
80% da terra pertencia a 20% da população. Generalizado como "Lei de Pareto".
<br><i>Aplicação no sistema: página Curva ABC.</i>
</div>

<div class='ref-box'>
<b>Juran, J. M. (1951).</b> <i>Quality Control Handbook.</i> New York: McGraw-Hill.<br>
Operacionalizou o princípio de Pareto em gestão de qualidade. Introduziu o termo
"the vital few and the trivial many" (poucos vitais e muitos triviais).
<br><i>Aplicação no sistema: classificação A/B/C dos produtos.</i>
</div>

<div class='ref-box'>
<b>Forrester, J. W. (1961).</b> <i>Industrial Dynamics.</i> Cambridge: MIT Press.<br>
Estabeleceu a distinção fundamental entre <b>stock</b> (estoque, snapshot) e
<b>flow</b> (fluxo, taxa). Conceito aplicado em todo o sistema PCP Vó Nena
pra evitar somar snapshots de estoque como se fossem fluxos.
<br><i>Aplicação: princípio transversal — Curva ABC, Média Móvel, Anomalias ML.</i>
</div>

<div class='ref-box'>
<b>Wheelwright, S. C., & Hyndman, R. J. (1998).</b> <i>Forecasting: Methods and
Applications.</i> 3rd ed. New York: Wiley.<br>
Referência clássica em previsão de séries temporais. Capítulo 2 cobre
métodos de média móvel.
<br><i>Aplicação no sistema: página Média Móvel.</i>
</div>

<div class='ref-box'>
<b>Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008).</b> <i>Isolation Forest.</i>
Proceedings of the 8th IEEE International Conference on Data Mining, 413-422.<br>
Algoritmo de Machine Learning não-supervisionado pra detecção de outliers.
Mais de 5.000 citações em literatura.
<br><i>Aplicação no sistema: página Anomalias ML.</i>
</div>

<div class='ref-box'>
<b>Heizer, J., & Render, B. (2014).</b> <i>Operations Management: Sustainability
and Supply Chain Management.</i> 11th ed. Boston: Pearson.<br>
Livro-texto padrão em Operations Management. Capítulo 13 cobre Capacity Planning.
<br><i>Aplicação no sistema: página Equipe — modelagem de capacidades por funcionário.</i>
</div>

<div class='ref-box'>
<b>Brown, T. B. et al. (2020).</b> <i>Language Models are Few-Shot Learners.</i>
Advances in Neural Information Processing Systems (NeurIPS), 33, 1877-1901.<br>
Paper introduzindo GPT-3 e o conceito de few-shot learning em LLMs grandes.
<br><i>Aplicação no sistema: Assistente IA via Claude API (LLM).</i>
</div>

<div class='ref-box'>
<b>Anthropic. (2024).</b> <i>Constitutional AI: Harmlessness from AI Feedback.</i>
arXiv:2212.08073.<br>
Fundamentos do treinamento de modelos da família Claude (usados no Assistente IA).
<br><i>Aplicação no sistema: Assistente IA.</i>
</div>
""", unsafe_allow_html=True)


st.divider()
st.caption(
    " Esta página é a fonte central de documentação do sistema. "
    "Quando tiver dúvida sobre alguma feature, comece por aqui antes de chamar o dev. "
    "Atualizada conforme o sistema evolui."
)
