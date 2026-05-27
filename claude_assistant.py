"""
claude_assistant.py — Assistente cognitivo via Claude API.

Módulo helper pra integrar o app Streamlit com a Claude API (Anthropic).
Permite que o usuário (Eraldo / Leonardo) pergunte em PT-BR sobre a operação,
e o Claude responde com base no contexto real da fábrica:
    - Folha do dia atual
    - Histórico de 7 dias
    - Achados de Insights ativos
    - Regras de negócio do CLAUDE.md (condensado)

Modelo: claude-haiku-4-5 (rápido + barato).
    ~R$ 0,02-0,05 por consulta com prompt caching ativo.

Caching estratégico:
    O system prompt (regras de negócio + persona) é grande e SEMPRE igual,
    então marcamos com `cache_control={"type": "ephemeral"}`. Anthropic
    cacheia por 5 min — múltiplas perguntas seguidas pagam 90% menos pelo
    contexto repetido.

Configuração necessária:
    Variável de ambiente / secret `ANTHROPIC_API_KEY` (formato `sk-ant-...`)
"""
import os
from datetime import datetime, timedelta
from typing import Optional

# Lazy import — evita erro de import se anthropic não estiver instalado em dev local.
_client = None


def _get_client():
    """Inicializa o client Anthropic na primeira chamada. Cacheia."""
    global _client
    if _client is None:
        try:
            from anthropic import Anthropic
        except ImportError:
            raise RuntimeError(
                "Biblioteca `anthropic` não instalada. Roda: pip install anthropic"
            )
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY não configurada. No HF Spaces: "
                "Settings > Variables and secrets > New secret > "
                "Name: ANTHROPIC_API_KEY, Value: sk-ant-..."
            )
        _client = Anthropic(api_key=api_key)
    return _client


# ════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT — regras de negócio + persona do assistente
# ════════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """Você é o assistente cognitivo do sistema PCP Vó Nena, projetado pra apoiar a operação da fábrica com análise em tempo real.

## QUEM VOCÊ ATENDE
- **Gestão da fábrica** — define ordens diárias, conhece o chão profundamente, leiga em tecnologia. Quer respostas curtas, diretas, em PT-BR coloquial.
- **Dev/Estagiário** — Engenheiro de Produção da UFCG, faz TCC com este projeto. Pergunta técnica + operacional misturada.

**REGRA INVIOLÁVEL:** SEM NOMES DE PESSOAS. Sempre referencie por departamento: **Gestão, Produção, Corte, Embalagem, Suprimentos**. Documentos físicos com nome histórico ("Papelzinho do Joel") mantêm o nome — referências a PESSOAS viram referências ao DEPARTAMENTO.

## SOBRE A FÁBRICA: DOCES VÓ NENA (São Paulo, SP)
Confeitaria industrial. Produz cocada, palha, pão de mel, balas de doce de leite, doces.

### PRODUTOS
- **Cocada:** 6 sabores (Tradicional, Leite Condensado, Brigadeiro, Café, Pé de Moça, Zero) em 3 formatos (45g, Mini, Pet) + Potes 260g/605g. **Zero NÃO tem 45g** — não existe.
- **Palha:** 5 sabores (Tradicional, Leite em Pó/Ninho, Churros, Cookies, Limão) em 2 formatos (50g, Pet). Palha 50g só em T, L, CH.
- **Pão de Mel:** 1 bolo = 70 unidades = 7 displays. `cnt_pm` em DISPLAYS, `ord_pm` em BOLOS.
- **Bala de Doce de Leite:** `ord_balas` em TACHOS (1 tacho = 30 balas).

### CONVERSÕES
- 1 tacho cocada = 8 bandejas (Zero = 3). **1 receita de palha = 1 panela = 1 bandeja** (NÃO é tacho!).
- 1 bandeja 45g = 100 und · Mini = 150 · Pet = 30 (Zero Pet = 60) · Palha 50g = ~80 (mín) · Palha Pet = ~30
- Bandeja cocada recém-tacho ≈ 6 kg · pronta-corte ≈ 5,5 kg (perda ~500g por evaporação)

### LEAD TIMES
- Cocada: 3 dias (tacho → virar → virada → corte)
- Potes: 1 dia
- Palha: 3 dias

### CALENDÁRIO DE CORTE — FLEXÍVEL (análise de 17 folhas)
A regra teórica é Seg/Qua/Qui=45g · Ter/Sex=Mini+Pet. Na prática:
- 45g acontece em **TODOS** os dias úteis (mais forte Qui)
- Mini concentra em Qua, Ter, Sex (raro Seg/Qui)
- Pet em Ter/Sex principalmente
A automação deve ser flexível, não rígida.

## ESTRUTURA DE DADOS — 3 CAMADAS DE PRODUTO CORTADO
Quando alguém pergunta "quanto temos de T 45g?", a resposta é a soma de TRÊS camadas:
1. `emb_45g` — embalado, pronto pra venda (estoque sala de venda)
2. `cort1_45g` — cortado na sala da Embalagem, ainda não embalado
3. `joel_45g` (papelzinho do Joel) — cortado na Produção, ainda não passou pra Embalagem

**Cortados² = emb + cort1 + joel** (joel_pet em BANDEJAS × 30 ou × 60 pra Z). Fórmula clássica do sistema (database.py:21). **SEMPRE use Cortados²** quando avaliar se um produto "está coberto" pelo param do dia — nunca olhe só emb ou ord_emb isolado.

## REGRAS OPERACIONAIS CRÍTICAS

### 1. Não-acomodação
A Gestão pede corte/produção MESMO quando o param do dia já está coberto. Exemplo: 04/05 Seg T tinha Cortados² = 5260, param = 5200 (cobertura +60 und). Mesmo assim foi ordenado cortar 26 band (2600 und extras). Razão: manter equipe ativa + buffer pra dias seguintes.

### 2. Tachos parciais NÃO são desperdício
Ordem de 18 band (não-múltiplo de 8): cozinha 3 tachos cheios (24 band massa), 18 viram bandeja, 6 viram potes 260g/605g do mesmo sabor (só T, L, Z fazem pote — B/C/P quase nunca).

### 3. param_real é antecipação de pedidos
Diferença entre `param_real_*` e a base de `metas_45g` é planejamento (pedidos futuros distribuídos), NÃO correção.

### 4. Estoque vs Fluxo (Forrester 1961)
- **Estoque** (`emb_*`, `cort1_*`) — snapshot do dia. NÃO PODE ser somado entre dias.
- **Fluxo** (`ord_*`) — pedido do dia. PODE ser somado.
- Curva ABC e Média Móvel usam FLUXO ou Cortados². Anomalia ML usa AMBOS.

### 5. Receita por TACHO (cocada) / por BANDEJA (palha) — não por formato
Cocada base T (1 tacho): 19,5 L leite (inclui 500 ml da mistura padrão) + 8 kg açúcar + 5 kg coco + 15 g sal + 70 g sorbato (anti-mofo).
Palha base T (1 bandeja): 3,82 kg leite condensado + 0,07 kg manteiga + 0,13 kg creme leite + 0,4 kg açúcar confeiteiro + 1,25 kg biscoito maisena + 0,75 kg chocolate meio amargo + 100 etiquetas.
**BOM completa cadastrada no sistema em 26/05/2026** (Etapa D) — 33 insumos + 91 linhas de BOM no banco.

### 6. Snapshot, não acumulativo
Cada folha (`data`) é independente. Derivados não persistem.

### 7. Sugestão automatizada (Camada 2)
- **Palha:** sugestão semanal (toda segunda), dois quadros lado a lado — NORMAL (round) e CONSERVADOR (threshold 0.81 no Pet, calibrado contra 25/05). Bate em ~85% dos casos.
- **Cocada:** sugestão diária, considera capacidade priorizada (T > L > demais), sobra do tacho parcial → potes, viração calculada (2 dias à frente). Cobre ~50-70% (gaps reconhecidos: eventos da semana, não-acomodação, contexto subjetivo).
- **Princípio:** o sistema SUGERE, a Gestão DECIDE.

### 8. Crescimento da fábrica
A produção semanal cresceu ~3× entre abril e maio (114 → 309 band/sem). Fórmulas com pisos fixos defasam rapidamente — use "últimas N semanas" como referência, não "histórico completo".

## SEU ESTILO DE RESPOSTA

- **PT-BR informal direto.** Nada de "Olá! Espero que esteja bem!" — vai direto.
- **Curto.** 3-7 frases ideais. Se precisar listar, usa bullets.
- **Com dados concretos.** Cita números da folha, não generalidades.
- **Reconhece incerteza.** Se a amostra é pequena, DIZ que é amostra pequena.
- **Não inventa.** Se não tem o dado, fala: "esse dado não está na folha do dia X, só verificando o histórico."
- **Sugere, não comanda.** "Considere X" / "vale verificar Y" — a Gestão sempre tem última palavra.
- **NUNCA mostra código.** Se a pergunta for técnica, descreve em linguagem natural.
- **Departamentos sempre, nunca nomes.** Use "a Gestão", "a Produção", "o Corte", "a Embalagem", "a Suprimentos".
- **Se a pergunta for ambígua, peça clarificação ANTES de inventar resposta.**

## EXEMPLOS DE PERGUNTAS QUE VOCÊ DEVE RESPONDER BEM

- "Por que o sistema sugere cortar X bandejas hoje?"
- "Quanto T 45g temos no total (somando todas as camadas)?"
- "Comparando esta semana com a anterior, o que mudou?"
- "Qual sabor parece estar precisando de mais atenção?"
- "Por que a sugestão da palha do dia foi maior que o esperado?"
- "Se eu cortar X em vez de Y, o que acontece com o estoque dos próximos dias?"

## O QUE VOCÊ NÃO DEVE FAZER

- Prometer mágica ("vai prever exato")
- Substituir o julgamento humano da Gestão
- Esconder limitações dos dados
- Citar nomes de pessoas (use departamento)
- Falar sobre coisas fora do escopo PCP (política, futebol, etc.)
"""


# ════════════════════════════════════════════════════════════════════════════
# CONTEXTO — monta um snapshot do estado atual da fábrica
# ════════════════════════════════════════════════════════════════════════════
def montar_contexto_folha(data: str, n_dias_historico: int = 7) -> str:
    """Monta texto estruturado com dados da folha do dia + histórico recente.

    Args:
        data: string YYYY-MM-DD
        n_dias_historico: quantos dias antes incluir no histórico

    Returns:
        Markdown formatado pra mandar como contexto pro Claude.
    """
    # Import preguiçoso pra evitar dependência circular se rodar em contexto puro
    from cached_db import (
        get_folha_cocada, get_folha_palha, get_papelzinho_joel,
        get_pm_balas_doces, list_datas_folha,
    )

    partes = []
    partes.append(f"# CONTEXTO ATUAL DA FÁBRICA")
    partes.append(f"## Data de referência: {data}\n")

    try:
        data_dt = datetime.strptime(data, "%Y-%m-%d")
        dias_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        partes.append(f"Dia da semana: **{dias_pt[data_dt.weekday()]}**\n")
    except Exception:
        pass

    # Folha do dia
    partes.append("## Folha do dia atual\n")
    partes.append(_resumir_folha(data, get_folha_cocada, get_folha_palha,
                                  get_papelzinho_joel, get_pm_balas_doces))

    # Histórico das últimas N folhas (até n_dias_historico)
    todas_datas = sorted(list_datas_folha(), reverse=True)
    historico_datas = [d for d in todas_datas if d < data][:n_dias_historico]
    if historico_datas:
        partes.append(f"\n## Histórico ({len(historico_datas)} folhas anteriores)\n")
        for d in reversed(historico_datas):  # ordem cronológica
            partes.append(_resumir_folha_compacta(
                d, get_folha_cocada, get_folha_palha, get_pm_balas_doces
            ))

    partes.append(f"\n## Total de folhas no banco: {len(todas_datas)}")
    partes.append(f"## Período: {todas_datas[-1] if todas_datas else '—'} a {todas_datas[0] if todas_datas else '—'}\n")

    return "\n".join(partes)


def _resumir_folha(data, get_cocada, get_palha, get_papel, get_pmbd) -> str:
    """Resumo detalhado de UMA folha (a do dia). Inclui Cortados² calculado."""
    partes = []
    cocada = list(get_cocada(data))
    palha = list(get_palha(data))
    papel = list(get_papel(data))
    pmbd = list(get_pmbd(data))

    # Indexa papelzinho por sabor pra calcular Cortados²
    papel_by = {p.get("sabor"): p for p in papel} if papel else {}

    if cocada:
        partes.append("### Cocada\n")
        for r in cocada:
            sabor = r.get("sabor", "?")
            linhas = []
            # Estoques nas 3 camadas
            emb_45 = int(r.get("emb_45g") or 0)
            emb_mini = int(r.get("emb_mini") or 0)
            emb_pet = int(r.get("emb_pet") or 0)
            cort1_45 = int(r.get("cort1_45g") or 0)
            cort1_mini = int(r.get("cort1_mini") or 0)
            cort1_pet = int(r.get("cort1_pet") or 0)
            p = papel_by.get(sabor, {})
            joel_45 = int(p.get("joel_45g") or 0)
            joel_mini = int(p.get("joel_mini") or 0)
            joel_pet_band = int(p.get("joel_pet") or 0)
            rend_pet = 60 if sabor == "ZERO" else 30
            joel_pet_und = joel_pet_band * rend_pet
            # Cortados² — TOTAL nas 3 camadas (use isso, não só emb)
            c2_45 = emb_45 + cort1_45 + joel_45
            c2_mini = emb_mini + cort1_mini + joel_mini
            c2_pet = emb_pet + cort1_pet + joel_pet_und
            if c2_45 + c2_mini + c2_pet > 0:
                linhas.append(f"Cortados² (TOTAL = emb+cort+joel): 45g={c2_45}, Mini={c2_mini}, Pet={c2_pet}")
            if emb_45 + emb_mini + emb_pet > 0:
                linhas.append(f"Embalados (sala venda): 45g={emb_45}, Mini={emb_mini}, Pet={emb_pet}")
            # Ordens (fluxo)
            ord_band = r.get("ord_prod_band") or 0
            if ord_band > 0:
                linhas.append(f"Ord. produção: {ord_band} bandejas")
            ord_corte = sum(int(r.get(f"ord_corte_{t}") or 0) for t in ("45g", "mini", "pet"))
            if ord_corte > 0:
                linhas.append(f"Ord. corte: 45g={r.get('ord_corte_45g') or 0}, Mini={r.get('ord_corte_mini') or 0}, Pet={r.get('ord_corte_pet') or 0}")
            param = r.get("param_real_45g") or 0
            if param > 0:
                deficit_45 = param - c2_45
                cover = "+" if deficit_45 <= 0 else "-"
                linhas.append(f"Param 45g={param} · Cortados² {cover}{abs(deficit_45)} vs param")
            if linhas:
                partes.append(f"- **{sabor}**: " + " · ".join(linhas))

    if palha:
        partes.append("\n### Palha\n")
        for r in palha:
            sabor = r.get("sabor", "?")
            ord_band = r.get("ord_prod_band") or 0
            emb_50 = r.get("emb_50g") or 0
            emb_pet = r.get("emb_pet") or 0
            if (ord_band + emb_50 + emb_pet) > 0:
                partes.append(f"- **{sabor}**: ord_band={ord_band}, emb_50g={emb_50}, emb_pet={emb_pet}")

    if papel:
        partes.append("\n### Papelzinho do Joel (produção)\n")
        for r in papel:
            sabor = r.get("sabor", "?")
            tachos = r.get("joel_pv") or 0  # bandejas pra virar
            viradas = r.get("joel_v") or 0
            j_45 = r.get("joel_45g") or 0
            j_mini = r.get("joel_mini") or 0
            j_pet = r.get("joel_pet") or 0
            if any((tachos, viradas, j_45, j_mini, j_pet)):
                partes.append(f"- **{sabor}**: P/Virar={tachos}, Viradas={viradas}, "
                              f"45g={j_45}, Mini={j_mini}, Pet={j_pet} band")

    if pmbd:
        partes.append("\n### PM, Balas, Doces\n")
        for r in pmbd:
            cnt_pm = r.get("cnt_pm") or 0
            ord_pm = r.get("ord_pm") or 0
            cnt_balas = r.get("cnt_balas") or 0
            ord_balas = r.get("ord_balas") or 0
            if any((cnt_pm, ord_pm, cnt_balas, ord_balas)):
                partes.append(f"- PM: estoque={cnt_pm} displays ({cnt_pm*10} und), "
                              f"ordem={ord_pm} bolos ({ord_pm*70} und)")
                partes.append(f"- Balas: estoque={cnt_balas} und, "
                              f"ordem={ord_balas} tachos ({ord_balas*30} balas)")

    return "\n".join(partes) if partes else "(folha vazia ou não preenchida)"


def _resumir_folha_compacta(data, get_cocada, get_palha, get_pmbd) -> str:
    """Resumo de 1 linha por folha do histórico (versão econômica em tokens)."""
    try:
        data_dt = datetime.strptime(data, "%Y-%m-%d")
        dia_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][data_dt.weekday()]
    except Exception:
        dia_pt = "?"

    cocada = list(get_cocada(data))
    total_emb_45g = sum(int(r.get("emb_45g") or 0) for r in cocada)
    total_ord_corte = sum(
        int(r.get("ord_corte_45g") or 0)
        + int(r.get("ord_corte_mini") or 0)
        + int(r.get("ord_corte_pet") or 0)
        for r in cocada
    )
    return f"- **{data} ({dia_pt})**: emb_45g_total={total_emb_45g} und, ord_corte_total={total_ord_corte} band"


# ════════════════════════════════════════════════════════════════════════════
# CHAMADA À API
# ════════════════════════════════════════════════════════════════════════════
def perguntar(pergunta: str, data_referencia: str,
              modelo: str = "claude-haiku-4-5",
              max_tokens: int = 1024) -> dict:
    """Manda a pergunta + contexto pro Claude e retorna a resposta.

    Args:
        pergunta: texto livre do usuário, em PT-BR.
        data_referencia: data da folha de referência (YYYY-MM-DD).
        modelo: model id (default Haiku 4.5).
        max_tokens: limite de tokens da resposta.

    Returns:
        dict com chaves:
            - 'resposta' (str): texto da resposta do Claude
            - 'tokens_input' (int): tokens de entrada
            - 'tokens_output' (int): tokens de saída
            - 'tokens_cache_read' (int): tokens lidos do cache (mais barato)
            - 'modelo' (str): modelo usado
            - 'erro' (str ou None)
    """
    client = _get_client()
    contexto = montar_contexto_folha(data_referencia)

    # Estrutura do prompt:
    # - system: instruções fixas + cacheável
    # - messages[0]: contexto + pergunta (pode mudar entre chamadas)
    try:
        response = client.messages.create(
            model=modelo,
            max_tokens=max_tokens,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"{contexto}\n\n"
                        f"---\n\n"
                        f"## PERGUNTA DO USUÁRIO\n\n{pergunta}"
                    ),
                }
            ],
        )

        resposta_texto = "".join(
            block.text for block in response.content if hasattr(block, "text")
        )

        return {
            "resposta": resposta_texto,
            "tokens_input": getattr(response.usage, "input_tokens", 0),
            "tokens_output": getattr(response.usage, "output_tokens", 0),
            "tokens_cache_read": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
            "tokens_cache_write": getattr(response.usage, "cache_creation_input_tokens", 0) or 0,
            "modelo": response.model,
            "erro": None,
        }
    except Exception as e:
        return {
            "resposta": "",
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_cache_read": 0,
            "tokens_cache_write": 0,
            "modelo": modelo,
            "erro": str(e),
        }


# ════════════════════════════════════════════════════════════════════════════
# STREAMING — versão "ChatGPT-like" (resposta vai aparecendo em tempo real)
# ════════════════════════════════════════════════════════════════════════════
class StreamingResposta:
    """Encapsula um stream da Claude API + metadata final.

    Uso típico (Streamlit):
        sr = StreamingResposta()
        texto_completo = st.write_stream(sr.chunks(pergunta, data_ref, modelo, 1024))
        # depois do stream terminar:
        meta = sr.meta  # dict com tokens, modelo, erro
    """
    def __init__(self):
        self.meta: dict = {}

    def chunks(self, pergunta: str, data_referencia: str,
               modelo: str = "claude-haiku-4-5", max_tokens: int = 1024):
        """Generator que produz pedaços de texto. Ao final, popula self.meta."""
        try:
            client = _get_client()
        except Exception as e:
            self.meta = {"erro": str(e), "tokens_input": 0, "tokens_output": 0,
                         "tokens_cache_read": 0, "tokens_cache_write": 0, "modelo": modelo}
            yield f"**Erro:** {e}"
            return

        contexto = montar_contexto_folha(data_referencia)

        try:
            with client.messages.stream(
                model=modelo,
                max_tokens=max_tokens,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"{contexto}\n\n"
                            f"---\n\n"
                            f"## PERGUNTA DO USUÁRIO\n\n{pergunta}"
                        ),
                    }
                ],
            ) as stream:
                for text in stream.text_stream:
                    yield text
                response = stream.get_final_message()

            self.meta = {
                "tokens_input": getattr(response.usage, "input_tokens", 0),
                "tokens_output": getattr(response.usage, "output_tokens", 0),
                "tokens_cache_read": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
                "tokens_cache_write": getattr(response.usage, "cache_creation_input_tokens", 0) or 0,
                "modelo": response.model,
                "erro": None,
            }
        except Exception as e:
            self.meta = {"erro": str(e), "tokens_input": 0, "tokens_output": 0,
                         "tokens_cache_read": 0, "tokens_cache_write": 0, "modelo": modelo}
            yield f"\n\n**Erro durante o streaming:** {e}"


def perguntar_streaming() -> StreamingResposta:
    """Atalho pra criar uma instância nova de StreamingResposta."""
    return StreamingResposta()


# ════════════════════════════════════════════════════════════════════════════
# SUGESTÕES CONTEXTUAIS — perguntas baseadas no estado da folha
# ════════════════════════════════════════════════════════════════════════════
def sugestoes_contextuais(data: str) -> list[str]:
    """Olha a folha do dia e gera 4-6 perguntas relevantes pra mostrar como atalhos.

    Heurística simples (não chama IA — é só lógica em cima dos dados):
      - Se há sabor com déficit (param > Cortados²) → sugere pergunta de explicação
      - Se há viração baixa → sugere pergunta sobre risco de falta nos próximos dias
      - Se há tacho parcial → sugere pergunta sobre absorção em potes
      - Sempre inclui: "Resume a folha" e "Compara com a semana anterior"
    """
    from cached_db import (
        get_folha_cocada, get_papelzinho_joel, list_datas_folha,
    )
    sugestoes = []

    try:
        folha = list(get_folha_cocada(data))
        papel = list(get_papelzinho_joel(data))
    except Exception:
        folha = []
        papel = []

    papel_by = {p.get("sabor"): p for p in papel}

    # 1. Sabor com déficit pesado (Cortados² < param × 0.7)
    sabor_deficit = None
    for r in folha:
        sabor = r.get("sabor")
        if sabor == "ZERO":
            continue
        param = r.get("param_real_45g") or 0
        if param == 0:
            continue
        emb = r.get("emb_45g") or 0
        cort1 = r.get("cort1_45g") or 0
        joel = (papel_by.get(sabor) or {}).get("joel_45g") or 0
        c2 = emb + cort1 + joel
        if c2 < param * 0.7:
            sabor_deficit = sabor
            break

    if sabor_deficit:
        sugestoes.append(
            f"Por que faltou {sabor_deficit} 45g hoje? Como tá o estoque dos próximos dias?"
        )

    # 2. Tacho parcial detectado
    parcial = None
    for r in folha:
        sabor = r.get("sabor")
        band = r.get("ord_prod_band") or 0
        modulo = 3 if sabor == "ZERO" else 8
        if band > 0 and band % modulo != 0:
            parcial = (sabor, band)
            break
    if parcial:
        sugestoes.append(
            f"Sistema sugere {parcial[1]} band de {parcial[0]}. Por que esse número? "
            f"Como fica a sobra que vira pote?"
        )

    # 3. Viração baixa em algum sabor (joel_v ≤ 5 e estoque P/Virar tb)
    viracao_baixa = None
    for s, p in papel_by.items():
        if (p.get("joel_v") or 0) <= 5 and (p.get("joel_pv") or 0) <= 5:
            viracao_baixa = s
            break
    if viracao_baixa:
        sugestoes.append(
            f"Viração de {viracao_baixa} tá baixa. Quanto cortar nos próximos 3 dias "
            f"vs quanto pedir pra virar hoje?"
        )

    # Genéricas (sempre incluídas)
    sugestoes.append(
        f"Resume a folha de {data} em 3 linhas: o que foi produzido, o que tá pendente."
    )

    # Histórico — se há folha da semana anterior no mesmo dia
    try:
        datas = sorted(list_datas_folha(), reverse=True)
        from datetime import datetime, timedelta
        d_ref = datetime.strptime(data, "%Y-%m-%d").date()
        anterior = (d_ref - timedelta(days=7)).isoformat()
        if anterior in datas:
            sugestoes.append(
                f"Compara esta folha com a do mesmo dia da semana passada ({anterior}). "
                f"O que mudou?"
            )
    except Exception:
        pass

    sugestoes.append(
        "Tem algum sabor com sinal de problema (excesso ou falta) nas últimas 5 folhas?"
    )

    return sugestoes[:6]  # cap em 6 sugestões


# ════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS — atalhos de prompt
# ════════════════════════════════════════════════════════════════════════════
SLASH_COMMANDS = {
    "/resumo":     "Faz um resumo executivo da folha do dia em 5 bullets curtos. "
                   "Cobre: produção total, sabores com déficit, sabores com excesso, "
                   "tacho parcial (se houver), e 1 alerta principal pra Gestão.",
    "/anomalias":  "Analisa as últimas 7 folhas e me diz quais sabores ou métricas "
                   "estão se comportando de forma estranha (variação muito acima ou "
                   "abaixo do normal). Cita números e explica o porquê.",
    "/comparar":   "Compara esta folha com a do mesmo dia da semana ANTERIOR. "
                   "O que mudou em volume, distribuição de sabores e produção? "
                   "Indica tendência (subindo, descendo, estável).",
    "/sugerir":    "Olha o estado atual (Cortados², papelzinho, param do dia) e "
                   "sugere 3 ações concretas que a Gestão deveria considerar HOJE "
                   "(corte, produção, viração, embalagem). Justifica cada uma.",
    "/faltas":     "Lista TODOS os sabores onde Cortados² < param_real do dia, "
                   "ordenados por déficit. Inclui sugestão de quantas bandejas "
                   "cortar pra fechar o gap.",
    "/historico":  "Faz um panorama de 14 dias: o que mudou na fábrica nesse "
                   "período? Cita 3 tendências principais com números.",
}


def expandir_slash_command(texto: str) -> str | None:
    """Se o texto começa com /, expande pro prompt completo. Senão retorna None.

    Aceita argumentos depois do comando: '/comparar 18/05' vira o prompt do
    /comparar com '18/05' no fim.
    """
    texto = texto.strip()
    if not texto.startswith("/"):
        return None
    partes = texto.split(maxsplit=1)
    cmd = partes[0].lower()
    arg = partes[1] if len(partes) > 1 else ""
    prompt = SLASH_COMMANDS.get(cmd)
    if prompt is None:
        return None
    if arg:
        return f"{prompt}\n\n(Argumento adicional do usuário: {arg})"
    return prompt


def explicar_anomalia(data: str, top_features: list,
                       anomaly_score: float,
                       modelo: str = "claude-haiku-4-5",
                       max_tokens: int = 600) -> dict:
    """Pede ao Claude pra EXPLICAR EM PT-BR uma anomalia detectada pelo
    Isolation Forest na página `pages/5_Anomalias_ML.py`.

    Diferente da função `perguntar()` (Q&A livre), aqui o prompt é específico:
    sistema recebe data + top 3 features anômalas com z-scores e gera uma
    narrativa estruturada (o-quê / por-quê-provável / o-que-verificar).

    Args:
        data: data da folha anômala (YYYY-MM-DD)
        top_features: list de tuples (nome_feature, z_score). Z-score positivo
            = acima do normal; negativo = abaixo. Ex: [("emb_total_TRADICIONAL", 2.3), ...]
        anomaly_score: score do Isolation Forest (maior = mais anômala)
        modelo: model id (default Haiku 4.5)
        max_tokens: limite de tokens da resposta

    Returns:
        dict com 'explicacao', 'tokens_input', 'tokens_output',
        'tokens_cache_read', 'modelo', 'custo_usd', 'custo_brl', 'erro'.
    """
    client = _get_client()
    contexto = montar_contexto_folha(data, n_dias_historico=7)

    # Formata as features pra mensagem
    features_str = "\n".join([
        f"  {i+1}. **{feat}** = {z:+.2f}σ (z-score)"
        for i, (feat, z) in enumerate(top_features)
    ])

    pergunta_estruturada = (
        f"## ANOMALIA DETECTADA — folha {data}\n\n"
        f"O algoritmo Isolation Forest classificou esta folha como anômala "
        f"(score = {anomaly_score:.3f}). As 3 features que mais contribuíram "
        f"foram:\n\n"
        f"{features_str}\n\n"
        f"## SUA TAREFA\n\n"
        f"Em 3-5 frases (PT-BR direto, sem jargão), explica:\n\n"
        f"1. **O QUÊ aconteceu** — quais campos da folha estão fora do padrão "
        f"e em que direção (alto/baixo). Use os dados concretos do contexto "
        f"acima.\n"
        f"2. **POR QUÊ provável** — hipóteses plausíveis pra essa combinação "
        f"de desvios. Use as regras de negócio (pedidos antecipados, calendário "
        f"de corte, sazonalidade, encomendas específicas, etc.).\n"
        f"3. **O QUE VERIFICAR** — 1 ou 2 ações concretas que o Eraldo poderia "
        f"fazer pra confirmar a hipótese ou descartar (ex: 'verificar se houve "
        f"pedido especial nessa data', 'comparar com outras folhas de mesma "
        f"característica').\n\n"
        f"**Importante:**\n"
        f"- Não use bullets ou markdown pesado — escreva em parágrafos curtos.\n"
        f"- Se a amostra é pequena (<30 folhas), reconheça isso.\n"
        f"- Não invente dados que não estão no contexto.\n"
        f"- Tom: especialista em PCP conversando com um gestor experiente."
    )

    try:
        response = client.messages.create(
            model=modelo,
            max_tokens=max_tokens,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"{contexto}\n\n---\n\n{pergunta_estruturada}",
                }
            ],
        )

        explicacao = "".join(
            block.text for block in response.content if hasattr(block, "text")
        )
        tokens_in = getattr(response.usage, "input_tokens", 0)
        tokens_out = getattr(response.usage, "output_tokens", 0)
        cache_read = getattr(response.usage, "cache_read_input_tokens", 0) or 0
        cache_write = getattr(response.usage, "cache_creation_input_tokens", 0) or 0

        custo_usd = estimar_custo(tokens_in, tokens_out, cache_read, modelo)
        custo_brl = usd_para_brl(custo_usd)

        return {
            "explicacao": explicacao,
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "tokens_cache_read": cache_read,
            "tokens_cache_write": cache_write,
            "modelo": response.model,
            "custo_usd": custo_usd,
            "custo_brl": custo_brl,
            "erro": None,
        }
    except Exception as e:
        return {
            "explicacao": "",
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_cache_read": 0,
            "tokens_cache_write": 0,
            "modelo": modelo,
            "custo_usd": 0,
            "custo_brl": 0,
            "erro": str(e),
        }


def estimar_custo(tokens_input: int, tokens_output: int,
                  tokens_cache_read: int = 0,
                  modelo: str = "claude-haiku-4-5") -> float:
    """Estima custo em USD da consulta com base no pricing público vigente.

    Pricing (USD por 1M tokens):
                       Input    Output   Cache Read  Cache Write
        Haiku 4.5      $1.00    $5.00    $0.10       $1.25
        Sonnet 4.6     $3.00    $15.00   $0.30       $3.75
        Opus 4         $15.00   $75.00   $1.50       $18.75

    Cache write é cobrado só na 1ª vez (25% mais caro que input cheio).
    Cache read é cobrado em todas as consultas que reaproveitam (90% off).
    """
    m = modelo.lower()
    if "opus" in m:
        in_rate, cache_rate, out_rate = 15.00, 1.50, 75.00
    elif "sonnet" in m:
        in_rate, cache_rate, out_rate = 3.00, 0.30, 15.00
    else:  # haiku ou desconhecido (fallback no mais barato)
        in_rate, cache_rate, out_rate = 1.00, 0.10, 5.00

    custo_in = max(0, tokens_input - tokens_cache_read) * in_rate / 1_000_000
    custo_cache = tokens_cache_read * cache_rate / 1_000_000
    custo_out = tokens_output * out_rate / 1_000_000
    return custo_in + custo_cache + custo_out


def usd_para_brl(usd: float, taxa_brl: float = 5.20) -> float:
    """Conversão USD → BRL pra exibir custos. Taxa configurável."""
    return usd * taxa_brl
