# -*- coding: utf-8 -*-
"""
custo_producao.py — Custo de produção por produto, a partir do BOM (receitas) ×
custo real dos insumos (trazido do SIGE). PURO: não importa Streamlit.

É o "ir além" da integração: o SIGE nos deu o custo de cada insumo; aqui isso
vira o custo de produzir cada cocada/palha/pão-de-mel/bala — base pra a Gestão
enxergar onde está o custo e o desperdício, e (próximo passo) a margem por produto.

HONESTIDADE: alguns insumos ainda estão sem custo (não cadastrados no SIGE, ou
com fator de unidade a confirmar). O custo desses produtos sai marcado como
PARCIAL, com a lista do que falta — nunca finge um total completo.

Custo por receita = Σ (quantidade_insumo × custo_unitário_insumo). As duas pontas
estão na MESMA unidade (a unidade da receita: kg/L/und), então a conta fecha.
"""

# Rendimento por receita -> (quantidade, unidade) pra custo por unidade vendável.
RENDIMENTO = {
    "cocada_T_tacho":  (8, "bandeja"),  "cocada_L_tacho": (8, "bandeja"),
    "cocada_B_tacho":  (8, "bandeja"),  "cocada_C_tacho": (8, "bandeja"),
    "cocada_P_tacho":  (8, "bandeja"),  "cocada_Z_tacho": (3, "bandeja"),
    "cocada_assada_cumbuca": (30, "cumbuca"),
    "palha_T_band":  (1, "bandeja"),  "palha_L_band":  (1, "bandeja"),
    "palha_CH_band": (1, "bandeja"),  "palha_CK_band": (1, "bandeja"),
    "palha_LIM_band": (1, "bandeja"),
    "pm_bolo":   (70, "unidade"),
    "bala_tacho": (30, "bala"),
}

NOME_PRODUTO = {
    "cocada_T_tacho": "Cocada Tradicional",      "cocada_L_tacho": "Cocada Leite Condensado",
    "cocada_B_tacho": "Cocada Brigadeiro",       "cocada_C_tacho": "Cocada Café",
    "cocada_P_tacho": "Cocada Pé de Moça",       "cocada_Z_tacho": "Cocada Zero",
    "cocada_assada_cumbuca": "Cocada Assada na Cumbuca",
    "palha_T_band": "Palha Tradicional",         "palha_L_band": "Palha Leite em Pó",
    "palha_CH_band": "Palha Churros",            "palha_CK_band": "Palha Cookies",
    "palha_LIM_band": "Palha Limão",
    "pm_bolo": "Pão de Mel",                     "bala_tacho": "Bala de Doce de Leite",
}

UNIDADE_RECEITA = {  # rótulo do "lote" de cada produto
    "tacho": "tacho", "band": "bandeja", "bolo": "bolo",
}


def _mapa_custos(db) -> dict:
    """{insumo_id: custo_unitário} de todos os insumos (somente leitura)."""
    return {i["id"]: float(i.get("custo_unitario") or 0.0)
            for i in db.get_insumos(somente_ativos=False)}


def custo_produto(db, produto_chave: str, custo_por_id: dict | None = None) -> dict:
    """Custo de UMA receita. Retorna dict com custo total, detalhe por insumo
    (ordenado pelo que mais pesa), insumos sem custo e cobertura."""
    if custo_por_id is None:
        custo_por_id = _mapa_custos(db)
    bom = db.get_bom_produto(produto_chave)

    total = 0.0
    sem_custo: list[str] = []
    detalhe: list[dict] = []
    for linha in bom:
        qtd = float(linha.get("quantidade") or 0.0)
        custo_unit = float(custo_por_id.get(linha["insumo_id"], 0.0))
        custo_linha = qtd * custo_unit
        total += custo_linha
        if custo_unit <= 0:
            sem_custo.append(linha.get("insumo_nome") or str(linha["insumo_id"]))
        detalhe.append({
            "insumo": linha.get("insumo_nome"),
            "qtd": qtd, "unidade": linha.get("unidade"),
            "custo_unit": round(custo_unit, 4),
            "custo": round(custo_linha, 4),
        })
    detalhe.sort(key=lambda x: -x["custo"])

    n = len(bom)
    cobertos = n - len(sem_custo)
    rend_qtd, rend_un = RENDIMENTO.get(produto_chave, (None, None))
    custo_unidade = round(total / rend_qtd, 4) if rend_qtd else None

    return {
        "produto_chave": produto_chave,
        "nome": NOME_PRODUTO.get(produto_chave, produto_chave),
        "custo_receita": round(total, 2),
        "rend_qtd": rend_qtd, "rend_unidade": rend_un,
        "custo_por_unidade": custo_unidade,
        "n_insumos": n, "cobertos": cobertos,
        "sem_custo": sem_custo,
        "parcial": len(sem_custo) > 0,
        "detalhe": detalhe,
    }


def custo_todos(db) -> list[dict]:
    """Custo de todos os produtos do BOM, na ordem de NOME_PRODUTO."""
    custo_por_id = _mapa_custos(db)
    out = []
    for chave in NOME_PRODUTO:
        try:
            out.append(custo_produto(db, chave, custo_por_id))
        except Exception as e:
            out.append({"produto_chave": chave, "nome": NOME_PRODUTO[chave],
                        "erro": str(e)})
    return out


# ── CLI (read-only) ──────────────────────────────────────────────────────────
def _bootstrap_secrets():
    import os
    try:
        import tomllib
        with open(".streamlit/secrets.toml", "rb") as f:
            cfg = tomllib.load(f)
        if "DATABASE_URL" in cfg and not os.environ.get("DATABASE_URL"):
            os.environ["DATABASE_URL"] = cfg["DATABASE_URL"]
    except Exception as e:
        print(f"[bootstrap] aviso: {e}")


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    _bootstrap_secrets()
    import database as db

    print("=== CUSTO DE PRODUÇÃO — por receita e por unidade ===\n")
    resultados = custo_todos(db)

    print(f"   {'produto':<26} {'custo/receita':>13} {'rende':>14} "
          f"{'custo/unidade':>14}  cobertura")
    print("   " + "-" * 88)
    for r in resultados:
        if "erro" in r:
            print(f"   {r['nome']:<26}  ERRO: {r['erro']}")
            continue
        rende = f"{r['rend_qtd']} {r['rend_unidade']}(s)" if r["rend_qtd"] else "—"
        cu = (f"R$ {r['custo_por_unidade']:.2f}/{r['rend_unidade']}"
              if r["custo_por_unidade"] is not None else "—")
        cob = f"{r['cobertos']}/{r['n_insumos']}"
        flag = "  ⚠ PARCIAL" if r["parcial"] else ""
        print(f"   {r['nome']:<26} {'R$ '+format(r['custo_receita'],'.2f'):>13} "
              f"{rende:>14} {cu:>14}  {cob}{flag}")

    # Detalhe de um exemplo (onde está o custo)
    print("\n   ── Onde está o custo (exemplo: Cocada Leite Condensado) ──")
    ex = next((r for r in resultados if r["produto_chave"] == "cocada_L_tacho"), None)
    if ex:
        for d in ex["detalhe"]:
            pct = (d["custo"] / ex["custo_receita"] * 100) if ex["custo_receita"] else 0
            print(f"     {d['insumo']:<26} {d['qtd']:>7} {str(d['unidade']):<4} "
                  f"× R$ {d['custo_unit']:>7.2f} = R$ {d['custo']:>7.2f}  ({pct:4.1f}%)")

    parciais = [r["nome"] for r in resultados if r.get("parcial")]
    print(f"\n   Produtos com custo PARCIAL (faltam insumos): {len(parciais)}")
    for r in resultados:
        if r.get("parcial"):
            print(f"     {r['nome']}: falta custo de {', '.join(r['sem_custo'])}")


if __name__ == "__main__":
    main()
