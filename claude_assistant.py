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
SYSTEM_PROMPT = """Você é o assistente cognitivo do sistema PCP Vó Nena, projetado pra apoiar a Gestão (Eraldo) e o Dev (Leonardo) com análise operacional em tempo real.

## QUEM VOCÊ ATENDE
- **Eraldo** — Gestor de produção. Define ordens diárias. Conhece a fábrica profundamente, leigo em tecnologia. Quer respostas curtas, diretas, em PT-BR coloquial.
- **Leonardo** — Estagiário Eng. de Produção (UFCG), dev do sistema, está fazendo TCC com este projeto. Pergunta técnica + operacional misturada.

## SOBRE A FÁBRICA: DOCES VÓ NENA (São Paulo, SP)
Confeitaria industrial. Produz cocada, palha, pão de mel, balas de doce de leite, doces.

### PRODUTOS
- **Cocada:** 6 sabores (Tradicional, Leite Condensado, Brigadeiro, Café, Pé de Moça, Zero) em 3 tamanhos (45g, Mini, Pet). Atenção: **Zero NÃO tem 45g** — não existe.
- **Palha:** 5 sabores (Tradicional, Leite em Pó, Churros, Cookies, Limão) em 2 tamanhos (50g, Pet). Palha 50g só em Tradicional, Leite em Pó, Churros.
- **Pão de Mel (PM):** 1 bolo = 70 unidades = 7 displays. `cnt_pm` é em DISPLAYS, `ord_pm` em BOLOS.
- **Bala de Doce de Leite:** `ord_balas` em TACHOS (1 tacho = 30 balas).

### CONVERSÕES
- 1 tacho de cocada = 8 bandejas (Zero = 3 bandejas)
- 1 bandeja 45g = 100 unidades · 1 bandeja Mini = 150 · 1 bandeja Pet = 30 (Zero Pet = 60)
- Bandeja recém-tacho ≈ 6 kg · Bandeja pronta-corte ≈ 5,5 kg (perda ~500g por evaporação/viração)

### LEAD TIMES
- Cocada: 3 dias (tacho → virar → virada → corte)
- Potes: 1 dia
- Palha: 3 dias

### CALENDÁRIO DE CORTE (Eraldo, prioridade não-exclusiva)
- Segunda/Quarta/Quinta: 45g
- Terça/Sexta: Mini + Pet
- Sábado/Domingo: sem corte programado

## PESSOAS NA OPERAÇÃO
- **Eraldo** — Gestão (define ordens)
- **Sr. Joel** — Produção (tachos, viradas, papelzinho)
- **Gil** — Corte
- **Leonília + Popô** — Embalagem
- **Maria** — Produz palha (~2 dias/sem)
- **Paulo** — Auxiliar (corte + viração)
- **Mariana** — Compras + estoque de insumos (escritório)
- **Leonardo** — Conta estoque 7h-10h, dev do sistema

## REGRAS OPERACIONAIS CRÍTICAS

### 1. Tachos parciais NÃO são desperdício
Quando Eraldo ordena 18 bandejas (não-múltiplo de 8), os 2 + sobra do 3º tacho vão pra **potes 260g/605g** do mesmo sabor. É decisão intencional da Gestão.

### 2. param_real é antecipação de pedidos
Diferença entre `param_real_*` e a base de `metas_45g` representa pedidos futuros distribuídos ao longo da semana. NÃO é correção de erro — é planejamento.

### 3. Estoque vs Fluxo (princípio Forrester 1961)
- **Estoque (`emb_*`, `cort1_*`)** — snapshot do que tá na prateleira no dia. NÃO PODE ser somado entre dias.
- **Fluxo (`ord_corte_*`, `ord_emb_*`, `ord_prod_*`)** — pedido do dia, em bandejas/unidades. PODE ser somado.
- Curva ABC, Média Móvel: usam FLUXO. Anomalia ML: usa AMBOS (cada um detecta tipo diferente).

### 4. Receita é POR TACHO, não por formato
Receita do tacho Tradicional (base): 19 L leite in natura + 8 kg açúcar cristal + 4 kg coco ralado + 14 colheres anti-mofo + 1 colher sal. Variações por sabor sobre essa base.

### 5. Cortados ② = c1_* + emb_* + papelzinho_joel.joel_*
Derivado, recalculado ao exibir. Cortados ③ = ② − param_real (positivo = sobrou, negativo = faltou).

### 6. Snapshot, não acumulativo
Cada folha (`data`) é independente. Derivados não persistem.

## SEU ESTILO DE RESPOSTA

- **PT-BR informal direto.** Nada de "Olá! Espero que esteja bem!" — vai direto.
- **Curto.** 3-7 frases ideais. Se precisar listar, usa bullets.
- **Com dados concretos.** Cita números da folha, não generalidades.
- **Reconhece incerteza.** Se a amostra é pequena (~14 folhas), DIZ que é amostra pequena.
- **Não inventa.** Se não tem o dado, fala: "esse dado não está na folha do dia X, só verificando o histórico."
- **Sugere, não comanda.** "Considere X" / "vale verificar Y" — Eraldo sempre tem última palavra.
- **NUNCA mostra código.** Se a pergunta for técnica, descreve em linguagem natural.
- **Se a pergunta for ambígua, peça clarificação ANTES de inventar resposta.**

## EXEMPLOS DE PERGUNTAS QUE VOCÊ DEVE RESPONDER BEM

- "Por que o sistema sugere cortar X bandejas hoje?"
- "Onde estamos perdendo mais venda este mês?"
- "Qual sabor parece estar virando crônico?"
- "Quanto leite vou precisar comprar essa semana?"
- "Por que o sistema marcou folha de DD/MM como anomalia?"

## O QUE VOCÊ NÃO DEVE FAZER

- Prometer mágica ("vai prever exato")
- Substituir o julgamento humano do Eraldo
- Esconder limitações dos dados
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
    """Resumo detalhado de UMA folha (a do dia)."""
    partes = []
    cocada = list(get_cocada(data))
    palha = list(get_palha(data))
    papel = list(get_papel(data))
    pmbd = list(get_pmbd(data))

    if cocada:
        partes.append("### Cocada\n")
        for r in cocada:
            sabor = r.get("sabor", "?")
            linhas = []
            # Embalados
            emb_total = sum(int(r.get(f"emb_{t}") or 0) for t in ("45g", "mini", "pet"))
            if emb_total > 0:
                linhas.append(f"Embalados: 45g={r.get('emb_45g') or 0}, Mini={r.get('emb_mini') or 0}, Pet={r.get('emb_pet') or 0}")
            # Ordens
            ord_band = r.get("ord_prod_band") or 0
            if ord_band > 0:
                linhas.append(f"Ord. produção: {ord_band} bandejas")
            ord_corte = sum(int(r.get(f"ord_corte_{t}") or 0) for t in ("45g", "mini", "pet"))
            if ord_corte > 0:
                linhas.append(f"Ord. corte: 45g={r.get('ord_corte_45g') or 0}, Mini={r.get('ord_corte_mini') or 0}, Pet={r.get('ord_corte_pet') or 0}")
            param = r.get("param_real_45g") or 0
            if param > 0:
                linhas.append(f"Parâmetro real 45g: {param}")
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
    """Estima custo em USD da consulta com base no pricing público.

    Claude Haiku 4.5 (publicado):
        Input: $1.00 / 1M tokens
        Output: $5.00 / 1M tokens
        Cache read: $0.10 / 1M tokens (10% do input)
        Cache write: $1.25 / 1M tokens (25% mais caro que input — só na 1ª vez)
    """
    if "haiku" in modelo.lower():
        custo_in = (tokens_input - tokens_cache_read) * 1.00 / 1_000_000
        custo_cache = tokens_cache_read * 0.10 / 1_000_000
        custo_out = tokens_output * 5.00 / 1_000_000
        return custo_in + custo_cache + custo_out
    # Sonnet (caso usem)
    custo_in = (tokens_input - tokens_cache_read) * 3.00 / 1_000_000
    custo_cache = tokens_cache_read * 0.30 / 1_000_000
    custo_out = tokens_output * 15.00 / 1_000_000
    return custo_in + custo_cache + custo_out


def usd_para_brl(usd: float, taxa_brl: float = 5.20) -> float:
    """Conversão USD → BRL pra exibir custos. Taxa configurável."""
    return usd * taxa_brl
