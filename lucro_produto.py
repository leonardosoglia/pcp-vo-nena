# -*- coding: utf-8 -*-
"""
lucro_produto.py — Cruza VENDAS (do SIGE) × CUSTO (do BOM) = contribuição por
produto. O fecho do ciclo do PCP: volume real × margem → onde está o retorno.
PURO: não importa Streamlit.

HONESTIDADE: a "contribuição" aqui é receita − custo de MATÉRIA-PRIMA (não inclui
mão de obra/embalagem/energia — ver project_custo_margem). E só cobre os produtos
cujo formato já tem custo mapeado (tablete 45g, Pão de Mel); os demais (cubos 160g,
cremosa, potes…) aparecem como "custo a mapear" até a fábrica passar as conversões.
"""
import custo_producao as cp
from margem_produto import DE_PARA_VENDA


def _custo_unit_por_codigo(db, custo_por_id=None) -> dict:
    """codigo_sige_vendável -> custo de MP por unidade vendável (do de-para de venda)."""
    if custo_por_id is None:
        custo_por_id = cp._mapa_custos(db)
    out = {}
    for chave, formato, cod, und in DE_PARA_VENDA:
        cr = cp.custo_produto(db, chave, custo_por_id)
        out[str(cod).strip()] = (cr["custo_receita"] / und if und else None)
    return out


def cruzar(db, agregado_vendas: dict, custo_por_id=None) -> dict:
    """Cruza o agregado de vendas (vendas_sige.agregar_vendas) com o custo de MP.
    Retorna {linhas, cobertura_receita, total_receita, total_contrib_mp}."""
    custo_unit = _custo_unit_por_codigo(db, custo_por_id)
    linhas = []
    total_receita = 0.0
    receita_mapeada = 0.0
    total_contrib = 0.0
    for cod, d in agregado_vendas["por_produto"].items():
        total_receita += d["receita"]
        cmp = custo_unit.get(str(cod).strip())
        if cmp is not None:
            custo_total = d["qtd"] * cmp
            contrib = d["receita"] - custo_total
            receita_mapeada += d["receita"]
            total_contrib += contrib
            linhas.append({
                "codigo": cod, "descricao": d["descricao"], "qtd": round(d["qtd"], 0),
                "receita": round(d["receita"], 2), "custo_mp_unit": round(cmp, 4),
                "custo_mp_total": round(custo_total, 2),
                "contrib_mp": round(contrib, 2), "mapeado": True})
        else:
            linhas.append({
                "codigo": cod, "descricao": d["descricao"], "qtd": round(d["qtd"], 0),
                "receita": round(d["receita"], 2), "custo_mp_unit": None,
                "custo_mp_total": None, "contrib_mp": None, "mapeado": False})
    return {"linhas": linhas, "total_receita": round(total_receita, 2),
            "receita_mapeada": round(receita_mapeada, 2),
            "cobertura_pct": round(receita_mapeada / total_receita * 100, 1) if total_receita else 0,
            "total_contrib_mp": round(total_contrib, 2)}


# ── CLI (read-only) ──────────────────────────────────────────────────────────
def main():
    import sys, os
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        import tomllib
        with open(".streamlit/secrets.toml", "rb") as f:
            cfg = tomllib.load(f)
        for k in ("DATABASE_URL", "SIGE_AUTH_TOKEN", "SIGE_USER", "SIGE_APP", "SIGE_DEPOSITO_PADRAO"):
            if k in cfg and not os.environ.get(k):
                os.environ[k] = str(cfg[k])
    except Exception as e:
        print("[bootstrap]", e)
    import sige_cloud_api as sige
    import database as db
    import vendas_sige as vs

    D_INI, D_FIM = "2026-06-08", "2026-06-15"
    print(f"=== VENDAS × CUSTO  ·  {D_INI} a {D_FIM}  ·  READ-ONLY ===\n")
    pedidos = sige.listar_todos_pedidos(D_INI, D_FIM)
    ag = vs.agregar_vendas(pedidos)
    res = cruzar(db, ag)

    print(f"Receita total da semana: R$ {res['total_receita']:,.2f}")
    print(f"Coberta por produtos COM custo: R$ {res['receita_mapeada']:,.2f} "
          f"({res['cobertura_pct']}%)\n")

    print("── PRODUTOS COM CUSTO — contribuição de matéria-prima (ordem) ──")
    print(f"   {'cod':>7} {'qtd':>6} {'receita':>11} {'custo MP':>10} {'contrib. MP':>12}  produto")
    mapeados = [l for l in res["linhas"] if l["mapeado"]]
    for l in sorted(mapeados, key=lambda x: -x["contrib_mp"]):
        print(f"   {l['codigo']:>7} {l['qtd']:>6.0f} R$ {l['receita']:>8,.2f} "
              f"R$ {l['custo_mp_total']:>7,.2f} R$ {l['contrib_mp']:>9,.2f}  {str(l['descricao'])[:34]}")
    print(f"\n   Contribuição de MP total (mapeados): R$ {res['total_contrib_mp']:,.2f}")

    print("\n── MAIORES VENDAS AINDA SEM CUSTO (a mapear c/ a fábrica) ──")
    nao = [l for l in res["linhas"] if not l["mapeado"]]
    for l in sorted(nao, key=lambda x: -x["receita"])[:10]:
        print(f"   {l['codigo']:>7} {l['qtd']:>6.0f} R$ {l['receita']:>8,.2f}  {str(l['descricao'])[:40]}")

    print("\nNota: contribuição = receita − custo de MATÉRIA-PRIMA (não é lucro líquido;")
    print("falta o custo de conversão). Cobre só os formatos já mapeados.")


if __name__ == "__main__":
    main()
