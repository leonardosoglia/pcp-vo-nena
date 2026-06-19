"""
assistant_tools.py — Ferramentas (tools) que o Claude pode chamar via tool use.

Em vez de empacotar TODO o contexto no prompt (caro + limitado por janela),
o Claude DECIDE quando precisa consultar dados específicos e chama uma destas
ferramentas. O sistema executa a função, retorna o resultado pro Claude, e
ele continua o raciocínio.

Benefícios:
  - Dados sempre FRESCOS do banco (não dependem de um snapshot pré-enviado)
  - Escalável: o Claude pode consultar 6 meses de folhas sem estourar contexto
  - Transparente: a página mostra QUAIS tools foram chamadas e com que input

As funções aqui são PURAS (sem Streamlit). A camada de UI usa via wrappers.
"""
import datetime as dt
import statistics
from typing import Any

# Lazy imports — só carregam quando o módulo for usado
def _db():
    import cached_db
    return cached_db


SABORES_COCADA = ['TRADICIONAL', 'LEITE CONDENSADO', 'BRIGADEIRO', 'CAFÉ', 'PÉ DE MOÇA', 'ZERO']
SABORES_PALHA = ['TRADICIONAL', 'LEITE EM PÓ', 'CHURROS', 'COOKIES', 'LIMÃO']
WEEKDAYS_PT = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']


# ════════════════════════════════════════════════════════════════════════════
# DEFINIÇÕES DE TOOLS (formato Anthropic — JSON Schema)
# ════════════════════════════════════════════════════════════════════════════
TOOLS = [
    {
        "name": "buscar_folha",
        "description": (
            "Busca a folha de produção completa de uma data específica. Retorna "
            "cocada (todos os 6 sabores), palha (5 sabores), papelzinho do Joel, "
            "e PM/Balas/Doces. Use quando precisar de detalhes específicos de um "
            "dia (ex: 'o que aconteceu em 25/05?' ou 'compare os números de duas "
            "datas')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "Data no formato YYYY-MM-DD. Ex: '2026-05-25'."
                }
            },
            "required": ["data"]
        }
    },
    {
        "name": "listar_folhas_no_periodo",
        "description": (
            "Lista todas as datas com folha lançada entre duas datas (inclusivo). "
            "Útil pra saber QUAIS dias têm dados antes de buscar detalhes. "
            "Não retorna o conteúdo das folhas, só as datas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data_inicio": {"type": "string", "description": "YYYY-MM-DD"},
                "data_fim": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["data_inicio", "data_fim"]
        }
    },
    {
        "name": "comparar_dia_da_semana",
        "description": (
            "Pega as últimas N folhas do MESMO DIA DA SEMANA antes de uma data de "
            "referência. Útil pra 'compara essa segunda com as anteriores' ou "
            "'como costuma ser a quinta-feira'. Retorna lista compacta com "
            "métricas-chave por folha."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data_referencia": {
                    "type": "string",
                    "description": "Data de referência YYYY-MM-DD. As folhas retornadas serão do mesmo dia da semana, ANTES desta data."
                },
                "n_semanas": {
                    "type": "integer",
                    "description": "Quantas semanas voltar (padrão 4).",
                    "default": 4
                },
            },
            "required": ["data_referencia"]
        }
    },
    {
        "name": "metricas_agregadas",
        "description": (
            "Retorna agregação (soma, média, mediana, mín, máx, contagem) de uma "
            "métrica entre duas datas. Útil pra perguntas tipo 'total produzido "
            "no mês' ou 'média de bandejas por dia'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data_inicio": {"type": "string", "description": "YYYY-MM-DD"},
                "data_fim": {"type": "string", "description": "YYYY-MM-DD"},
                "metrica": {
                    "type": "string",
                    "enum": [
                        "ord_corte_45g", "ord_corte_mini", "ord_corte_pet",
                        "ord_prod_band", "ord_emb_45g",
                        "emb_45g", "emb_mini", "emb_pet",
                        "param_real_45g",
                        "cortados2_45g",
                    ],
                    "description": (
                        "Qual coluna agregar. 'cortados2_45g' é calculado "
                        "(emb + cort1 + joel_45g). As outras vêm direto do banco."
                    )
                },
                "sabor": {
                    "type": "string",
                    "description": "Filtrar por sabor (TRADICIONAL, LEITE CONDENSADO, etc). Omitir = todos os sabores."
                },
                "agregacao": {
                    "type": "string",
                    "enum": ["sum", "avg", "median", "min", "max", "count"],
                    "description": "Função de agregação. Padrão 'sum'.",
                    "default": "sum"
                },
            },
            "required": ["data_inicio", "data_fim", "metrica"]
        }
    },
    {
        "name": "info_meta_base_cocada_45g",
        "description": (
            "Retorna a meta-base (param fixo definido pela Gestão) de cocada 45g "
            "de um sabor por dia da semana (Seg/Ter/Qua/Qui/Sex). É o número "
            "TEÓRICO; o param_real do dia pode diferir por causa de pedidos "
            "antecipados."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sabor": {
                    "type": "string",
                    "enum": ["TRADICIONAL", "LEITE CONDENSADO", "BRIGADEIRO", "CAFÉ", "PÉ DE MOÇA"],
                    "description": "Sabor (Zero não tem 45g)."
                },
            },
            "required": ["sabor"]
        }
    },
    {
        "name": "info_alvos_estoque",
        "description": (
            "Retorna os alvos de estoque definidos pela Gestão: alvo de P/Virar "
            "(bandejas), alvo de potes 260g e 605g por sabor. Use quando o "
            "usuário perguntar 'qual o alvo de X' ou 'quanto deveríamos ter de Y'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
        }
    },
    {
        "name": "calcular_cortados2",
        "description": (
            "Calcula Cortados² (= emb_45g + cort1_45g + joel_45g) por sabor pra "
            "uma data específica. É o TOTAL de 45g cortado/preparado na fábrica "
            "naquele dia (3 camadas somadas). Use quando precisar saber 'quanto "
            "T 45g temos hoje' considerando todas as camadas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["data"]
        }
    },
    {
        "name": "necessidades_insumos",
        "description": (
            "Cruza a folha do dia × receitas (BOM) × estoque de insumos e retorna "
            "o que vai FALTAR (ou sobrar) pra produzir o que está ordenado no dia. "
            "Use pra 'quanto de leite/açúcar/coco vou precisar?' ou 'algum insumo "
            "vai faltar?'. Depende de BOM e insumos cadastrados."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["data"]
        }
    },
    {
        "name": "eventos_semana",
        "description": (
            "Lista eventos/observações de um período (equipe reduzida, feriado, "
            "pedido grande, manutenção, observação livre). É o CONTEXTO que a folha "
            "numérica não mostra mas que muda a decisão da Gestão. Use pra entender "
            "por que um dia foi atípico ou o que está previsto."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data_inicio": {"type": "string", "description": "YYYY-MM-DD"},
                "data_fim": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["data_inicio", "data_fim"]
        }
    },
    {
        "name": "giro_estoque",
        "description": (
            "Tendência do estoque de produto EMBALADO por produto ao longo das "
            "folhas (proxy de giro SEM dados de venda): subindo = possível PARADO/"
            "super-produzido; caindo = SAINDO bem. Use pra 'o que está encalhando?' "
            "ou 'qual sai mais rápido?'. Em fábrica em crescimento, subir é esperado."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data_inicio": {"type": "string", "description": "YYYY-MM-DD (opcional)"},
                "data_fim": {"type": "string", "description": "YYYY-MM-DD (opcional)"},
            },
        }
    },
    {
        "name": "historico_mensal_vendas",
        "description": (
            "Receita faturada por MÊS — vendas REAIS do SIGE, já calculadas e "
            "guardadas no nosso banco (resposta RÁPIDA). Use pra tendência de "
            "vendas, qual mês vendeu mais, comparar meses, sazonalidade (ex.: "
            "Natal/fim de ano). É o TOTAL por mês (não por produto). O mês "
            "corrente é parcial (só até hoje)."
        ),
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "custo_producao_por_produto",
        "description": (
            "Custo de PRODUÇÃO (material) por produto + o custo por kg por sabor "
            "de cocada, calculado do BOM (receitas) × custo dos insumos vindo do "
            "SIGE. Resposta RÁPIDA (lê o banco). Use pra 'quanto custa produzir "
            "X', 'qual sabor é mais caro de produzir', 'custo por kg'. ATENÇÃO: é "
            "custo de MATERIAL só — NÃO inclui mão de obra/energia/embalagem, "
            "então NÃO é o custo total nem dá pra concluir lucro/margem só com isso."
        ),
        "input_schema": {"type": "object", "properties": {}}
    },
]


# ════════════════════════════════════════════════════════════════════════════
# IMPLEMENTAÇÃO DAS TOOLS
# ════════════════════════════════════════════════════════════════════════════
def _tool_buscar_folha(data: str) -> dict:
    try:
        folha = _db().get_folha_completa(data)
        return {"data": data, **folha}
    except Exception as e:
        return {"erro": f"Falha ao buscar folha {data}: {e}"}


def _tool_listar_folhas_no_periodo(data_inicio: str, data_fim: str) -> dict:
    try:
        datas = _db().list_datas_folha()
        filtradas = [d for d in datas if data_inicio <= d <= data_fim]
        # Adiciona dia da semana
        info = []
        for d in filtradas:
            try:
                wd = dt.datetime.strptime(d, "%Y-%m-%d").weekday()
                info.append({"data": d, "dia_semana": WEEKDAYS_PT[wd]})
            except Exception:
                info.append({"data": d, "dia_semana": "?"})
        return {"total": len(filtradas), "folhas": info}
    except Exception as e:
        return {"erro": str(e)}


def _tool_comparar_dia_da_semana(data_referencia: str, n_semanas: int = 4) -> dict:
    try:
        d_ref = dt.datetime.strptime(data_referencia, "%Y-%m-%d").date()
    except Exception as e:
        return {"erro": f"Data inválida: {e}"}

    datas_existentes = set(_db().list_datas_folha())
    folhas = []
    for k in range(1, max(n_semanas * 3, n_semanas + 1) + 1):
        if len(folhas) >= n_semanas:
            break
        d = d_ref - dt.timedelta(days=7 * k)
        d_iso = d.isoformat()
        if d_iso not in datas_existentes:
            continue
        try:
            folha = _db().get_folha_cocada(d_iso)
            papel_rows = _db().get_papelzinho_joel(d_iso)
            papel_by = {r['sabor']: r for r in papel_rows}
            # Resumo compacto da folha
            resumo = []
            for r in folha:
                sabor = r.get('sabor')
                if not sabor:
                    continue
                p = papel_by.get(sabor, {})
                emb45 = r.get('emb_45g') or 0
                cort1 = r.get('cort1_45g') or 0
                joel45 = p.get('joel_45g') or 0
                c2_45 = emb45 + cort1 + joel45
                resumo.append({
                    "sabor": sabor,
                    "cortados2_45g": c2_45,
                    "param_real_45g": r.get('param_real_45g') or 0,
                    "ord_corte_45g": r.get('ord_corte_45g') or 0,
                    "ord_prod_band": r.get('ord_prod_band') or 0,
                })
            folhas.append({"data": d_iso, "dia_semana": WEEKDAYS_PT[d.weekday()], "sabores": resumo})
        except Exception:
            continue
    return {"dia_semana_referencia": WEEKDAYS_PT[d_ref.weekday()], "folhas": folhas}


def _tool_metricas_agregadas(
    data_inicio: str, data_fim: str, metrica: str,
    sabor: str = None, agregacao: str = "sum"
) -> dict:
    try:
        datas = [d for d in _db().list_datas_folha() if data_inicio <= d <= data_fim]
    except Exception as e:
        return {"erro": str(e)}

    valores = []
    detalhes = []  # pra inspeção (limitado)
    for d in datas:
        try:
            folha = _db().get_folha_cocada(d)
        except Exception:
            continue
        if metrica == "cortados2_45g":
            try:
                papel_rows = _db().get_papelzinho_joel(d)
                papel_by = {r['sabor']: r for r in papel_rows}
            except Exception:
                papel_by = {}
            for r in folha:
                s = r.get('sabor')
                if sabor and s != sabor:
                    continue
                emb = r.get('emb_45g') or 0
                cort1 = r.get('cort1_45g') or 0
                joel = (papel_by.get(s, {})).get('joel_45g') or 0
                v = emb + cort1 + joel
                if v > 0:
                    valores.append(v)
                    detalhes.append({"data": d, "sabor": s, "valor": v})
        else:
            for r in folha:
                s = r.get('sabor')
                if sabor and s != sabor:
                    continue
                v = r.get(metrica) or 0
                if v > 0:
                    valores.append(v)
                    detalhes.append({"data": d, "sabor": s, "valor": v})

    if not valores:
        return {
            "agregado": 0, "n": 0, "agregacao": agregacao, "metrica": metrica,
            "sabor": sabor or "(todos)", "periodo": f"{data_inicio} a {data_fim}",
            "obs": "Nenhum dado encontrado pro período/filtros."
        }

    if agregacao == "sum":
        ag = sum(valores)
    elif agregacao == "avg":
        ag = sum(valores) / len(valores)
    elif agregacao == "median":
        ag = statistics.median(valores)
    elif agregacao == "min":
        ag = min(valores)
    elif agregacao == "max":
        ag = max(valores)
    elif agregacao == "count":
        ag = len(valores)
    else:
        return {"erro": f"agregação desconhecida: {agregacao}"}

    return {
        "agregado": round(ag, 2) if isinstance(ag, float) else ag,
        "n": len(valores),
        "agregacao": agregacao,
        "metrica": metrica,
        "sabor": sabor or "(todos)",
        "periodo": f"{data_inicio} a {data_fim}",
        "amostra_primeiros_10": detalhes[:10],
    }


def _tool_info_meta_base_cocada_45g(sabor: str) -> dict:
    try:
        metas = _db().get_metas_45g()
        for r in metas:
            if r.get('sabor') == sabor:
                return {
                    "sabor": sabor,
                    "segunda": r.get('segunda'),
                    "terca": r.get('terca'),
                    "quarta": r.get('quarta'),
                    "quinta": r.get('quinta'),
                    "sexta": r.get('sexta'),
                }
        return {"erro": f"Sabor {sabor} não encontrado em metas_45g"}
    except Exception as e:
        return {"erro": str(e)}


def _tool_info_alvos_estoque() -> dict:
    try:
        from cocada_planejamento import (
            ALVO_PV_PADRAO, ALVO_POTE_260G_PADRAO, ALVO_POTE_605G_PADRAO
        )
        return {
            "alvo_pvirar_bandejas": ALVO_PV_PADRAO,
            "alvo_pote_260g": ALVO_POTE_260G_PADRAO,
            "alvo_pote_605g": ALVO_POTE_605G_PADRAO,
            "nota": "Alvos definidos pela Gestão. P/Virar = bandejas em estoque pra cortar nos próximos dias. Potes em unidades."
        }
    except Exception as e:
        return {"erro": str(e)}


def _tool_calcular_cortados2(data: str) -> dict:
    try:
        folha = _db().get_folha_cocada(data)
        papel_rows = _db().get_papelzinho_joel(data)
        papel_by = {r['sabor']: r for r in papel_rows}
    except Exception as e:
        return {"erro": str(e)}
    sabores = []
    for r in folha:
        s = r.get('sabor')
        if s == 'ZERO':
            continue  # Z não tem 45g
        p = papel_by.get(s, {})
        emb = r.get('emb_45g') or 0
        cort1 = r.get('cort1_45g') or 0
        joel = p.get('joel_45g') or 0
        sabores.append({
            "sabor": s,
            "emb_45g": emb,
            "cort1_45g (sala embalagem)": cort1,
            "joel_45g (papelzinho)": joel,
            "cortados2_45g (TOTAL)": emb + cort1 + joel,
            "param_real_45g": r.get('param_real_45g') or 0,
            "deficit_vs_param": (r.get('param_real_45g') or 0) - (emb + cort1 + joel),
        })
    return {"data": data, "sabores_45g": sabores}


def _tool_necessidades_insumos(data: str) -> dict:
    try:
        nec = _db().calcular_necessidades_do_dia(data)
        return {"data": data, "total_insumos": len(nec), "necessidades": nec}
    except Exception as e:
        return {"erro": str(e)}


def _tool_eventos_semana(data_inicio: str, data_fim: str) -> dict:
    try:
        return {"eventos": _db().get_eventos_periodo(data_inicio, data_fim)}
    except Exception as e:
        return {"erro": str(e)}


def _tool_giro_estoque(data_inicio: str = None, data_fim: str = None) -> dict:
    from collections import defaultdict
    try:
        db = _db()
        datas = sorted(db.list_datas_folha())
        if data_inicio:
            datas = [d for d in datas if d >= data_inicio]
        if data_fim:
            datas = [d for d in datas if d <= data_fim]
        if not datas:
            return {"erro": "sem folhas no período"}
        COC = [('emb_45g', '45g'), ('emb_mini', 'Mini'), ('emb_pet', 'Pet'),
               ('emb_potes_260g', 'P260'), ('emb_potes_605g', 'P605')]
        series = defaultdict(dict)
        for d in datas:
            for row in db.get_folha_cocada(d):
                s = row.get('sabor', '?')
                for col, lbl in COC:
                    series[f'COC {s} {lbl}'][d] = row.get(col) or 0
            for row in db.get_folha_palha(d):
                s = row.get('sabor', '?')
                for col, lbl in (('emb_50g', '50g'), ('emb_pet', 'Pet')):
                    series[f'PAL {s} {lbl}'][d] = row.get(col) or 0
        linhas = []
        for prod, dv in series.items():
            vals = [dv[d] for d in sorted(dv)]
            if not any(vals):
                continue
            k = min(3, len(vals))
            ini = sum(vals[:k]) / k
            fim = sum(vals[-k:]) / k
            linhas.append({"produto": prod, "n": len(vals), "inicio": round(ini),
                           "fim": round(fim), "delta": round(fim - ini),
                           "media": round(sum(vals) / len(vals)), "pico": max(vals)})
        linhas.sort(key=lambda r: r["delta"], reverse=True)
        return {
            "periodo": f"{datas[0]} a {datas[-1]}", "n_folhas": len(datas),
            "acumulando_mais": linhas[:8], "reduzindo_mais": linhas[-5:],
            "nota": ("Proxy de giro SEM dados de venda. Subindo = possível parado/super-"
                     "produzido; caindo = saindo bem. Em crescimento, subir é esperado."),
        }
    except Exception as e:
        return {"erro": str(e)}


# ════════════════════════════════════════════════════════════════════════════
# DISPATCHER
# ════════════════════════════════════════════════════════════════════════════
def _tool_historico_mensal_vendas() -> dict:
    """Receita faturada por mês (do nosso banco — rápido, sem ler o SIGE ao vivo)."""
    import database as _dbmod
    try:
        rows = _dbmod.get_vendas_mensais()
    except Exception as e:
        return {"erro": f"não consegui ler o histórico mensal: {e}"}
    if not rows:
        return {"erro": "Histórico mensal de vendas ainda não calculado "
                        "(abra a tela de Vendas e clique em Atualizar do SIGE)."}
    meses = [{
        "mes": f"{int(r['mes']):02d}/{int(r['ano'])}",
        "receita": round(float(r['receita'] or 0), 2),
        "faturados": int(r['n_faturados'] or 0),
        "parcial": bool(r['parcial']),
    } for r in rows]
    return {"fonte": "vendas reais faturadas do SIGE, somadas por mês",
            "meses": meses}


def _tool_custo_producao_por_produto() -> dict:
    """Custo de material por produto + custo/kg por sabor (do BOM — rápido)."""
    import database as _dbmod
    try:
        import custo_producao as cp
        import contribuicao_produto as cpr
        produtos = cp.custo_todos(_dbmod)
        ckg = cpr.custo_kg_cocada(_dbmod)
    except Exception as e:
        return {"erro": f"não consegui calcular o custo: {e}"}
    prod = []
    for p in produtos:
        if p.get("erro"):
            continue
        prod.append({
            "produto": p["nome"],
            "custo_receita": p.get("custo_receita"),
            "rende": (f"{p['rend_qtd']} {p['rend_unidade']}" if p.get("rend_qtd") else None),
            "custo_por_unidade": p.get("custo_por_unidade"),
            "parcial": p.get("parcial"),
            "falta_custo_de": p.get("sem_custo") or [],
        })
    custo_kg = {d["label"]: round(d["custo_kg"], 2)
                for d in ckg.values() if d.get("custo_kg")}
    return {
        "obs": ("Custo de MATERIAL (insumos do BOM × custo do SIGE). NÃO inclui "
                "mão de obra/energia/embalagem — não é custo total nem lucro."),
        "produtos": prod,
        "custo_por_kg_cocada": custo_kg,
    }


_TOOL_REGISTRY = {
    "buscar_folha": _tool_buscar_folha,
    "historico_mensal_vendas": _tool_historico_mensal_vendas,
    "custo_producao_por_produto": _tool_custo_producao_por_produto,
    "listar_folhas_no_periodo": _tool_listar_folhas_no_periodo,
    "comparar_dia_da_semana": _tool_comparar_dia_da_semana,
    "metricas_agregadas": _tool_metricas_agregadas,
    "info_meta_base_cocada_45g": _tool_info_meta_base_cocada_45g,
    "info_alvos_estoque": _tool_info_alvos_estoque,
    "calcular_cortados2": _tool_calcular_cortados2,
    "necessidades_insumos": _tool_necessidades_insumos,
    "eventos_semana": _tool_eventos_semana,
    "giro_estoque": _tool_giro_estoque,
}


def executar_tool(name: str, input_args: dict) -> Any:
    """Executa uma tool por nome. Retorna o resultado (qualquer JSON-serializável).
    Em caso de erro, retorna dict com chave 'erro'."""
    func = _TOOL_REGISTRY.get(name)
    if func is None:
        return {"erro": f"Tool desconhecida: {name}"}
    try:
        return func(**input_args)
    except TypeError as e:
        return {"erro": f"Argumentos inválidos pra tool {name}: {e}"}
    except Exception as e:
        return {"erro": f"Erro ao executar tool {name}: {e}"}
