# -*- coding: utf-8 -*-
"""
reconciliacao_sige.py — Reconcilia o estoque do SIGE (teórico contábil: entra por
NF-e, baixa por OP) com o estoque do nosso PCP (contagem física / auto-baixa).
READ-ONLY nos DOIS lados: lê do SIGE (GetAll) e do nosso banco (SELECT). Não
escreve nada, nunca toca o SIGE.

SALDO CONSOLIDADO (decisão 14/06, confirmada por Leonardo): a fábrica é **um único
local físico**. Os 22 "depósitos" do SIGE (FABRICA, ITAQUERA, LOJA MATRIZ...) e os
vários CNPJs são divisões CONTÁBEIS/FISCAIS, não locais distintos. A contagem
física conta TODO o insumo da fábrica → o número do SIGE pra comparar é o
**EstoqueSaldo consolidado do GetAll** (soma de todos os depósitos), não o de um
depósito isolado. Ex.: leite = 2.050 (FABRICA) + 1.600 (ITAQUERA) − 360 (LOJA
MATRIZ) = 3.290 (consolidado). Comparar só com a FABRICA daria um falso alarme.
Os "vazamentos" contábeis (saldos negativos em lojas) aparecem como divergência
na contagem — que é exatamente o erro a reconciliar.

PRINCÍPIO (3 camadas de estoque — Forrester/stock-vs-flow): o número diverge entre
(1) SIGE contábil, (2) nosso sistema e (3) o físico real. A Gestão usa a divergência
pra disparar o ajuste de inventário e a análise. Ver docs/ARQUITETURA_SIGE.md.

UNIDADES: o saldo do SIGE está na unidade de COMPRA (caixa/fardo/pacote); o nosso
estoque está na unidade da RECEITA (kg/L/und). Convertemos pelo fator do de-para
(suprimentos_sigee/de_para_sige.md). Onde o fator é incerto, fica NAO_COMPARAVEL.

MÓDULO PURO: não importa Streamlit. A UI chama `reconciliar()`.
"""
from importar_sige_api import DEPARA, _campo

TOLERANCIA = 0.001  # unidade da receita


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def indexar_saldo_consolidado(produtos_sige: list[dict]) -> dict:
    """Do GetAll -> {codigo: EstoqueSaldo consolidado (soma de todos os depósitos)}."""
    idx: dict[str, float] = {}
    for p in produtos_sige:
        cod = str(_campo(p, "Codigo")).strip()
        if cod:
            idx[cod] = _num(_campo(p, "EstoqueSaldo"))
    return idx


def reconciliar(db, saldo_idx: dict, depara=DEPARA) -> list[dict]:
    """Cruza, por insumo do BOM: saldo consolidado do SIGE (convertido) x estoque
    do nosso sistema. Uma linha por insumo, com divergência e status.

    saldo_idx: {codigo_sige: saldo_consolidado} (de indexar_saldo_consolidado).

    status:
      OK            — bate dentro da tolerância.
      DIVERGENTE    — diferença relevante (gera ajuste/investigação).
      NAO_COMPARAVEL— fator de unidade ainda incerto (a Gestão confirma).
      SEM_SIGE      — insumo não cadastrado no SIGE.
    """
    linhas: list[dict] = []

    for chave, codigo, fator, un_receita, status_dp in depara:
        insumo = db.get_insumo_por_codigo(chave)
        sistema = float((insumo or {}).get("estoque_atual") or 0.0)
        nome = (insumo or {}).get("nome") or chave

        linha = {
            "chave": chave, "nome": nome, "un_receita": un_receita,
            "sige_codigo": codigo, "sige_saldo_compra": None,
            "fator": fator, "sige_convertido": None,
            "sistema": round(sistema, 3), "divergencia": None, "status": "",
        }

        if codigo is None or str(codigo).strip() not in saldo_idx:
            linha["status"] = "SEM_SIGE"
            linhas.append(linha)
            continue

        saldo_compra = saldo_idx[str(codigo).strip()]
        linha["sige_saldo_compra"] = round(saldo_compra, 3)

        if fator:
            convertido = round(saldo_compra * fator, 3)
            divergencia = round(convertido - sistema, 3)
            linha["sige_convertido"] = convertido
            linha["divergencia"] = divergencia
            linha["status"] = "OK" if abs(divergencia) <= TOLERANCIA else "DIVERGENTE"
        else:
            linha["status"] = "NAO_COMPARAVEL"

        linhas.append(linha)

    return linhas


def resumir(linhas: list[dict]) -> dict:
    """Contadores por status + maior divergência absoluta comparável."""
    r = {"OK": 0, "DIVERGENTE": 0, "NAO_COMPARAVEL": 0, "SEM_SIGE": 0,
         "comparaveis": 0, "maior_divergencia": None}
    for ln in linhas:
        r[ln["status"]] = r.get(ln["status"], 0) + 1
        if ln["divergencia"] is not None:
            r["comparaveis"] += 1
            d = abs(ln["divergencia"])
            if r["maior_divergencia"] is None or d > r["maior_divergencia"][1]:
                r["maior_divergencia"] = (ln["chave"], d)
    return r


# ── CLI (read-only) ──────────────────────────────────────────────────────────
def _bootstrap_secrets():
    import os
    try:
        import tomllib
        with open(".streamlit/secrets.toml", "rb") as f:
            cfg = tomllib.load(f)
        for k in ("DATABASE_URL", "SIGE_AUTH_TOKEN", "SIGE_USER", "SIGE_APP",
                  "SIGE_DEPOSITO_PADRAO"):
            if k in cfg and not os.environ.get(k):
                os.environ[k] = str(cfg[k])
    except Exception as e:
        print(f"[bootstrap] aviso: {e}")


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    _bootstrap_secrets()
    import sige_cloud_api as sige
    import database as db

    print("=== RECONCILIAÇÃO  SIGE (consolidado)  x  nosso sistema  — READ-ONLY ===\n")
    con = sige.testar_conexao()
    if not con["ok"]:
        print("SIGE indisponível:", con["mensagem"])
        return
    produtos = sige.listar_todos_produtos(page_size=200, max_paginas=50)
    print(f"SIGE: {len(produtos)} produtos lidos (saldo consolidado).\n")
    saldo_idx = indexar_saldo_consolidado(produtos)

    linhas = reconciliar(db, saldo_idx)

    print(f"   {'insumo':<24} {'SIGE total':>12} {'SIGE→receita':>14} "
          f"{'sistema':>10} {'divergência':>12}  status")
    print("   " + "-" * 94)
    for ln in linhas:
        sc = (f"{ln['sige_saldo_compra']}" if ln["sige_saldo_compra"] is not None else "—")
        conv = (f"{ln['sige_convertido']} {ln['un_receita']}"
                if ln["sige_convertido"] is not None else "—")
        sis = f"{ln['sistema']} {ln['un_receita']}"
        dv = (f"{ln['divergencia']:+.2f}" if ln["divergencia"] is not None else "—")
        print(f"   {ln['chave']:<24} {sc:>12} {conv:>14} {sis:>10} {dv:>12}  {ln['status']}")

    r = resumir(linhas)
    print("\n=== RESUMO ===")
    print(f"  Comparáveis: {r['comparaveis']}  |  batem (OK): {r['OK']}  |  "
          f"divergentes: {r['DIVERGENTE']}")
    print(f"  Não comparáveis (fator a confirmar): {r['NAO_COMPARAVEL']}  |  "
          f"sem SIGE: {r['SEM_SIGE']}")
    if r["maior_divergencia"]:
        print(f"  Maior divergência: {r['maior_divergencia'][0]} "
              f"({r['maior_divergencia'][1]:.2f} na unidade da receita)")
    print("\nNota: 'sistema' hoje reflete a auto-baixa por produção (sem carga "
          "inicial). Após a contagem física, esta coluna passa a ser o estoque "
          "real e a divergência vira o ajuste de inventário a tratar com a Gestão.")


if __name__ == "__main__":
    main()
