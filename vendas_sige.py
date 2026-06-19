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
import calendar
from collections import Counter
from datetime import date


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


# Cadastros do SIGE que NÃO são produto da fábrica (poluem a Curva ABC de demanda).
# cod 66 = "DIVERSOS E EMBALAGENS": coringa de caixa (R$0,01) p/ itens avulsos/embalagens —
# aparecia 2º em VOLUME mas é centavos de receita. Lista extensível.
CODIGOS_NAO_PRODUTO = {"66"}


def curva_abc(por_produto: dict, chave="receita") -> list[dict]:
    """Ordena por receita (ou 'qtd') e classifica A (até 80% acum.), B (80-95%),
    C (95-100%) — Curva ABC. Ignora itens não-produto (CODIGOS_NAO_PRODUTO)."""
    itens = sorted(((c, d) for c, d in por_produto.items()
                    if str(c).strip() not in CODIGOS_NAO_PRODUTO),
                   key=lambda x: -x[1][chave])
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


# ── Histórico mensal (persistido no NOSSO banco p/ não reler o SIGE toda hora) ──
def ultimos_meses(n: int):
    """Lista de (ano, mes) dos últimos n meses, incluindo o atual, em ordem."""
    hj = date.today()
    y, m, out = hj.year, hj.month, []
    for _ in range(n):
        out.append((y, m))
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    return list(reversed(out))


def _mes_intervalo(ano: int, mes: int):
    """(data_inicial, data_final, parcial). O mês corrente vai só até hoje."""
    ult = calendar.monthrange(ano, mes)[1]
    hj = date.today()
    corrente = (ano == hj.year and mes == hj.month)
    fim = hj.day if corrente else ult
    return f"{ano:04d}-{mes:02d}-01", f"{ano:04d}-{mes:02d}-{fim:02d}", corrente


def atualizar_vendas_mes(db, sige, ano: int, mes: int) -> dict:
    """Lê UM mês do SIGE (read-only no SIGE) e grava o total faturado em
    `vendas_mensais` do nosso banco. Faz o cálculo na MESMA base do resto da tela
    (soma dos itens dos pedidos faturados). Retorna o registro gravado."""
    d_ini, d_fim, parcial = _mes_intervalo(ano, mes)
    pedidos = sige.listar_todos_pedidos(d_ini, d_fim)
    ag = agregar_vendas(pedidos)
    n_fat = sum(n for s, n in ag["por_status"].items() if "fatur" in str(s).lower())
    db.upsert_vendas_mes(ano, mes, ag["total_receita"], n_fat, 1 if parcial else 0)
    return {"ano": ano, "mes": mes, "receita": ag["total_receita"],
            "n_faturados": n_fat, "parcial": 1 if parcial else 0}


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
