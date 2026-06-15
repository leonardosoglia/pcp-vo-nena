# -*- coding: utf-8 -*-
"""
margem_produto.py — Margem por produto: preço de venda (SIGE) − custo de produção
(BOM × custo de insumo). PURO: não importa Streamlit.

É o fecho do "ir além": custo + preço = onde está o LUCRO. A Curva ABC deixa de
ser "o que vende mais" e passa a poder ser "o que dá mais margem".

HONESTIDADE — o que esta margem É e o que NÃO É:
  - É a **margem de matéria-prima** (preço de venda − custo dos insumos da receita).
  - NÃO inclui embalagem, mão de obra, energia, impostos nem margem de canal.
  É o primeiro nível de margem — ótimo pra COMPARAR produtos entre si (qual
  transforma insumo em valor de forma mais eficiente) e pra ver o impacto do
  desperdício, mas não é lucro líquido. Os custos parciais (insumo sem custo)
  são herdados de custo_producao e marcados.

DE-PARA DE VENDA: liga cada receita ao produto vendável no SIGE + quantas unidades
vendáveis saem de 1 receita (pra ratear o custo). Começa pelos formatos de
conversão CLARA (tablete 45g = 8 band × 100 und = 800 und/tacho; PM = 70 und/bolo).
Outros formatos (mini, pet, pote, cubos, palha) entram quando a fábrica confirmar
a conversão.
"""
import json
import custo_producao as cp

# (produto_receita, formato, codigo_sige_vendavel, unidades_vendaveis_por_receita)
DE_PARA_VENDA = [
    ("cocada_T_tacho", "Tablete 45g", "1",  800),
    ("cocada_L_tacho", "Tablete 45g", "2",  800),
    ("cocada_B_tacho", "Tablete 45g", "3",  800),
    ("cocada_C_tacho", "Tablete 45g", "4",  800),
    ("pm_bolo",        "Unidade 60g", "29", 70),
]


def calcular_margens(db, preco_por_codigo: dict, custo_por_id: dict | None = None) -> list[dict]:
    """Uma linha por (produto, formato): custo unitário, preço de venda, margem."""
    if custo_por_id is None:
        custo_por_id = cp._mapa_custos(db)
    # custo por receita (cache por produto)
    custo_receita_cache: dict[str, dict] = {}
    linhas = []
    for chave, formato, cod, und in DE_PARA_VENDA:
        if chave not in custo_receita_cache:
            custo_receita_cache[chave] = cp.custo_produto(db, chave, custo_por_id)
        cr = custo_receita_cache[chave]
        custo_unit = round(cr["custo_receita"] / und, 4) if und else None
        preco = preco_por_codigo.get(str(cod).strip())
        margem_rs = round(preco - custo_unit, 4) if (preco is not None and custo_unit is not None) else None
        margem_pct = round(margem_rs / preco * 100, 1) if (margem_rs is not None and preco) else None
        linhas.append({
            "produto": cr["nome"], "formato": formato, "sige_codigo": cod,
            "custo_unitario": custo_unit, "preco_venda": preco,
            "margem_rs": margem_rs, "margem_pct": margem_pct,
            "custo_parcial": cr["parcial"], "sem_custo": cr["sem_custo"],
        })
    return linhas


# ── CLI (read-only) ──────────────────────────────────────────────────────────
def main():
    import sys, os
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        import tomllib
        with open(".streamlit/secrets.toml", "rb") as f:
            cfg = tomllib.load(f)
        if "DATABASE_URL" in cfg and not os.environ.get("DATABASE_URL"):
            os.environ["DATABASE_URL"] = cfg["DATABASE_URL"]
    except Exception as e:
        print("[bootstrap]", e)
    import database as db

    # preços de venda: do snapshot _sige_vendaveis.json (codigo -> preco_venda)
    with open("_sige_vendaveis.json", encoding="utf-8") as f:
        vend = json.load(f)
    preco_por_codigo = {str(v["codigo"]).strip(): v["preco_venda"] for v in vend}

    print("=== MARGEM DE MATÉRIA-PRIMA — preço de venda − custo de insumo ===\n")
    linhas = calcular_margens(db, preco_por_codigo)
    print(f"   {'produto':<26} {'formato':<12} {'custo MP':>9} {'venda':>8} "
          f"{'margem R$':>10} {'margem %':>9}")
    print("   " + "-" * 80)
    for ln in linhas:
        cu = f"R$ {ln['custo_unitario']:.3f}" if ln["custo_unitario"] is not None else "—"
        pv = f"R$ {ln['preco_venda']:.2f}" if ln["preco_venda"] is not None else "—"
        mr = f"R$ {ln['margem_rs']:.2f}" if ln["margem_rs"] is not None else "—"
        mp = f"{ln['margem_pct']:.1f}%" if ln["margem_pct"] is not None else "—"
        flag = " ⚠" if ln["custo_parcial"] else ""
        print(f"   {ln['produto']:<26} {ln['formato']:<12} {cu:>9} {pv:>8} {mr:>10} {mp:>9}{flag}")

    print("\n   Leitura: margem ALTA = a matéria-prima é fração pequena do preço.")
    print("   O que diferencia os produtos é QUANTO insumo cada um consome —")
    print("   ali está a alavanca de custo que a fábrica controla.")
    print("   (⚠ = custo parcial: falta o custo de algum insumo; ver de-para §7.)")


if __name__ == "__main__":
    main()
