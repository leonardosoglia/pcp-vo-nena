# -*- coding: utf-8 -*-
"""
vendas_sige.py — Módulo de Vendas a partir do SIGE (READ-ONLY). Lê os pedidos de
venda (com seus itens) e agrega: volume e receita por produto, por canal, por
empresa, + Curva ABC por receita. É a peça que fecha o ciclo do PCP — com o custo/
margem, vira LUCRO por produto e Curva ABC por lucro (a visão do Leonardo:
produção puxada pela demanda).

Fonte: sige_cloud_api.listar_todos_pedidos (Pedidos/Pesquisar). Cada pedido tem
Items (Codigo, Descricao, Quantidade, ValorTotal) e Tabela (=canal: QUIOSQUE/
REVENDA/PADRÃO). Considera só pedidos FATURADOS (vendas confirmadas) por padrão.

PURO: não importa Streamlit.
"""
from collections import Counter


def _num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def agregar_vendas(pedidos: list[dict], filtro_status=("Fatur",)) -> dict:
    """Agrega os itens dos pedidos. filtro_status: só conta pedidos cujo
    StatusSistema contém um desses termos (default: 'Fatur' = faturado). Passe
    None pra contar todos."""
    por_produto: dict[str, dict] = {}
    por_canal: Counter = Counter()
    por_empresa: Counter = Counter()
    por_status: Counter = Counter()
    total = 0.0

    for ped in pedidos:
        status = str(ped.get("StatusSistema") or "?")
        por_status[status] += 1
        if filtro_status and not any(t.lower() in status.lower() for t in filtro_status):
            continue
        canal = str(ped.get("Tabela") or "(sem canal)")
        empresa = str(ped.get("Empresa") or "?")
        for it in (ped.get("Items") or []):
            cod = str(it.get("Codigo") or "?").strip()
            qtd = _num(it.get("Quantidade"))
            rec = _num(it.get("ValorTotal"))
            d = por_produto.setdefault(cod, {
                "descricao": it.get("Descricao"), "qtd": 0.0,
                "receita": 0.0, "linhas": 0, "canais": Counter()})
            d["qtd"] += qtd
            d["receita"] += rec
            d["linhas"] += 1
            d["canais"][canal] += rec
            por_canal[canal] += rec
            por_empresa[empresa] += rec
            total += rec

    return {"por_produto": por_produto, "por_canal": dict(por_canal),
            "por_empresa": dict(por_empresa), "por_status": dict(por_status),
            "total_receita": round(total, 2)}


def curva_abc(por_produto: dict, chave="receita") -> list[dict]:
    """Ordena por receita (ou 'qtd') e classifica A (até 80% acum.), B (80-95%),
    C (95-100%) — Curva ABC."""
    itens = sorted(por_produto.items(), key=lambda x: -x[1][chave])
    total = sum(d[chave] for _, d in itens) or 1.0
    acum = 0.0
    out = []
    for cod, d in itens:
        acum += d[chave]
        pct = acum / total * 100
        classe = "A" if pct <= 80 else ("B" if pct <= 95 else "C")
        out.append({"codigo": cod, "descricao": d["descricao"], "qtd": round(d["qtd"], 1),
                    "receita": round(d["receita"], 2), "pct_acum": round(pct, 1),
                    "classe": classe})
    return out


# ── CLI (read-only) ──────────────────────────────────────────────────────────
def main():
    import sys, os
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        import tomllib
        with open(".streamlit/secrets.toml", "rb") as f:
            cfg = tomllib.load(f)
        for k in ("SIGE_AUTH_TOKEN", "SIGE_USER", "SIGE_APP", "SIGE_DEPOSITO_PADRAO"):
            if k in cfg and not os.environ.get(k):
                os.environ[k] = str(cfg[k])
    except Exception as e:
        print("[bootstrap]", e)
    import sige_cloud_api as sige

    D_INI, D_FIM = "2026-06-08", "2026-06-15"
    print(f"=== VENDAS DO SIGE  ·  {D_INI} a {D_FIM}  ·  READ-ONLY ===\n")
    pedidos = sige.listar_todos_pedidos(D_INI, D_FIM)
    print(f"{len(pedidos)} pedidos lidos.\n")

    ag = agregar_vendas(pedidos)
    print("Status dos pedidos:", ag["por_status"])
    print(f"\nReceita total (faturados): R$ {ag['total_receita']:,.2f}")
    print(f"Produtos distintos vendidos: {len(ag['por_produto'])}\n")

    print("── Receita por CANAL ──")
    for canal, rec in sorted(ag["por_canal"].items(), key=lambda x: -x[1]):
        print(f"   {canal:<22} R$ {rec:>12,.2f}")

    print("\n── Receita por EMPRESA ──")
    for emp, rec in sorted(ag["por_empresa"].items(), key=lambda x: -x[1]):
        print(f"   {emp:<22} R$ {rec:>12,.2f}")

    print("\n── CURVA ABC por receita (top 20) ──")
    abc = curva_abc(ag["por_produto"])
    na = sum(1 for x in abc if x["classe"] == "A")
    print(f"   ({na} produtos classe A respondem por 80% da receita, de {len(abc)} no total)\n")
    print(f"   {'cls':<4}{'cod':>7}  {'qtd':>8} {'receita':>12}  produto")
    for x in abc[:20]:
        print(f"   {x['classe']:<4}{x['codigo']:>7}  {x['qtd']:>8.0f} "
              f"R$ {x['receita']:>10,.2f}  {str(x['descricao'])[:42]}")


if __name__ == "__main__":
    main()
