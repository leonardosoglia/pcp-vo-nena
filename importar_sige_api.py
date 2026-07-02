# -*- coding: utf-8 -*-
"""
importar_sige_api.py — Ponte READ-ONLY do SIGE → nossa tabela `insumos`, via API.

Espelha o `importar_csv_sigee.py` (plano B, por planilha), mas puxa direto da
API do SIGE Cloud e casa pelo CÓDIGO do produto (não pelo nome) usando o de-para
validado em `suprimentos_sigee/de_para_sige.md`.

O QUE IMPORTA (decisão arquitetural — CADERNO / de_para_sige.md §6, vai pro TCC):
  - ✅ CUSTO de referência (PrecoCusto do SIGE, convertido pra unidade da receita).
  - ✅ IDENTIDADE (código SIGE + nome) gravada na `obs` pra rastreabilidade.
  - ✅ FORNECEDOR (texto).
  - 🚫 NÃO importa estoque. O saldo do SIGE reflete nota fiscal, não o físico no
       chão (3 camadas Forrester). A carga inicial de QUANTIDADE vem da contagem
       física do Leonardo (registrar_movimento_insumo / contagem_inicial).
  - 🚫 NUNCA escreve no SIGE (read-only — SIGE_PERMITIR_ESCRITA segue bloqueado).

CONVERSÃO DE CUSTO: o PrecoCusto do SIGE é por UNIDADE DE COMPRA (caixa/fardo/
pacote). custo_unitario do nosso insumo é por unidade da RECEITA (kg/L/und). Logo
custo_receita = PrecoCusto / fator. Só aplicamos o custo quando: há fator, o
PrecoCusto não está quebrado (>R$0,05) e o resultado passa num sanity check
(R$0,30–600/un). Caso contrário, gravamos só a ficha na obs + fornecedor, e o
custo fica pendente de confirmação da Suprimentos (status no relatório).

IDEMPOTENTE: a ficha `[SIGE ...]` na obs é substituída, não duplicada.

USO:
    $env:PYTHONIOENCODING="utf-8"; python importar_sige_api.py            # DRY-RUN (não escreve)
    $env:PYTHONIOENCODING="utf-8"; python importar_sige_api.py --apply    # aplica no banco

ATENÇÃO: o secrets.toml local aponta pra PRODUÇÃO (us-east-1). Com --apply, a
escrita é no banco REAL. Por padrão é dry-run.
"""
import argparse
import os
import re
import sys
from datetime import date

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ════════════════════════════════════════════════════════════════════════════
# DE-PARA — base 14/06 + re-mapeamento v3 (23/06, por UltimaAlteracao) aplicado
# em 02/07/2026 com códigos conferidos AO VIVO no catálogo (0 fantasmas).
# (chave_insumo, codigo_sige, fator→un.receita ou None, un.receita, status)
# fator None  => não calcular custo (unidade de compra ambígua) — só obs/fornecedor.
# codigo None => NAO_CADASTRADO (pular).
# ════════════════════════════════════════════════════════════════════════════
DEPARA = [
    ("LEITE_IN_NATURA",          "01021",                  1.0,  "L",   "CONFIRMADO"),
    ("LEITE_CONDENSADO",         "000000000000012332",    20.0,  "kg",  "AMBIGUO"),
    # v3: 6943 "CREME DE LEITE GRANDE FOOD SERVICE PIRACANJUBA 1,030" (alt 26/06,
    # vivo). Preço R$213,72 sugere CAIXA 12x1,03kg (=R$17,29/kg) mas o nome não
    # confirma — custo só depois da confirmação do fator.
    ("CREME_DE_LEITE",           "6943",                  None,  "kg",  "TROCADO_v3_FATOR_INCERTO"),
    ("LEITE_NINHO",              "560077",                None,  "kg",  "FATOR_INCERTO"),
    # v3: 5620 é MARGARINA USO GERAL S/SAL AMELIA 12x1,01kg (não manteiga!).
    # Pergunta pra fábrica: a receita usa manteiga ou margarina sem sal?
    ("MANTEIGA_SEM_SAL",         "5620",                  None,  "kg",  "CONFIRMAR_MARGARINA_X_MANTEIGA"),
    ("DOCE_DE_LEITE",            "409000198",              4.8,  "kg",  "FATOR_INCERTO"),
    # v3: açúcar da cocada é REFINADO. O Guarani 992 (foto 23/06) está parado
    # desde ago/25; o cadastro VIVO é 7566 "ALTO ALEGRE 1KG (FDO 10 PCT)"
    # (alterado 30/06/26) — R$46/fardo 10x1kg = R$4,60/kg. Confirmar no chão.
    ("ACUCAR_CRISTAL",           "7566",                  10.0,  "kg",  "TROCADO_v3_CONFIRMAR_CAMPO"),
    ("ACUCAR_CONFEITEIRO",       "409001130",             10.0,  "kg",  "CONFIRMADO"),
    ("ACUCAR_MASCAVO",           "7908089414219",          1.0,  "kg",  "CONFIRMADO"),
    ("ADOCANTE_LOWCUCAR_STEVIA", "409000415",              1.0,  "kg",  "CONFIRMADO"),
    ("ERITRITOL",                "409000463",              1.0,  "kg",  "CONFIRMADO"),
    ("XILITOL",                  "XILITOL",               25.0,  "kg",  "AMBIGUO"),
    ("MEL",                      "02",                     1.45, "kg",  "FATOR_INCERTO"),
    ("ESSENCIA_MEL",             None,                    None,  "kg",  "NAO_CADASTRADO"),
    ("COCO_RALADO",              "008",                    2.0,  "kg",  "AMBIGUO"),
    ("AMENDOIM",                 "649",                    5.0,  "kg",  "AMBIGUO"),
    # v3: 409000334 "CX OVO BCO GD 20UN" (alt mar/26, mais recente que o 291 de
    # set/24) — R$13,99/caixa = R$0,70/ovo. Nenhum cadastro de ovo é claramente
    # vivo; segue ambíguo.
    ("OVO",                      "409000334",             20.0,  "und", "TROCADO_v3_AMBIGUO"),
    ("ACHOCOLATADO",             "82143",                  0.5,  "kg",  "AMBIGUO"),
    ("CACAU_PO",                 "82143",                  0.5,  "kg",  "AMBIGUO"),
    ("CHOCOLATE_MEIO_AMARGO",    "409000228",              2.1,  "kg",  "FATOR_INCERTO"),
    # v3: caixa Nescafé Tradição Forte 24x40g (alt 18/06, saldo 3) —
    # R$130,05/caixa = R$5,42/sachê de 40g (a unidade da receita).
    ("CAFE_SACHE_40G",           "000000000012610012",    24.0,  "und", "TROCADO_v3_CONFIRMADO"),
    ("BISCOITO_MAISENA",         "740226",                None,  "kg",  "AMBIGUO"),
    # v3: 83726 "BISC.NESTLE NEGRESCO RECH.ORIGINAL" (alt 18/06, vivo) — sem
    # gramatura no nome (R$10,14 não bate com pacote de 140g); fator a confirmar.
    ("BISCOITO_NEGRESCO",        "83726",                 None,  "kg",  "TROCADO_v3_FATOR_INCERTO"),
    ("CANELA_PO",                "5769",                  None,  "kg",  "AMBIGUO"),
    ("CRAVO_PO",                 None,                    None,  "kg",  "NAO_CADASTRADO"),
    ("LIMAO_TAITI",              "1805",                  None,  "und", "FATOR_INCERTO"),
    # v3: 1462 "FARINHA DE TRIGO FDO 10X1KG" (alt 13/06, vivo) — MAS o preço
    # R$4,99 parece ser do PACOTE de 1kg, não do fardo (R$0,50/kg é irreal e a
    # trava de sanidade não pegaria); custo só depois de confirmar a unidade.
    ("FARINHA_TRIGO",            "1462",                  None,  "kg",  "TROCADO_v3_FATOR_INCERTO"),
    ("BICARBONATO",              "26818",                  1.0,  "kg",  "CONFIRMADO"),
    ("FERMENTO_PO",              "409000330",              0.25, "kg",  "CONFIRMADO"),
    ("AMACIANTE",                None,                    None,  "kg",  "NAO_CADASTRADO"),
    ("PALMISTE",                 "OLEO DE PALMISTE TAUA", 14.5,  "kg",  "AMBIGUO"),
    ("SAL",                      "344",                    1.0,  "kg",  "AMBIGUO"),
    # v3: cadastro POR KG criado pelo Leonardo em 23-25/06 (o Kunda antigo era
    # caixa de 25 kg — não cabia os 70 g da receita). R$24,89/kg direto.
    ("SORBATO",                  "7908089414222",          1.0,  "kg",  "TROCADO_v3_CONFIRMADO"),
    ("ETIQUETA_PALHA",           None,                    None,  "und", "NAO_CADASTRADO"),
]

# Sanity check do custo convertido (R$/unidade-da-receita) — pega custo quebrado
# (ex.: doce de leite a R$0,01) e fator de ordem de grandeza errada.
CUSTO_MIN, CUSTO_MAX = 0.30, 600.0
PRECO_MIN_VALIDO = 0.05  # abaixo disso, custo do SIGE está quebrado


# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════
def _bootstrap_secrets():
    """Propaga DATABASE_URL + SIGE_* do secrets.toml pro ambiente, sem imprimir."""
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


def _campo(p, *nomes):
    low = {str(k).lower(): v for k, v in p.items()}
    for n in nomes:
        v = low.get(n.lower())
        if v not in (None, ""):
            return v
    return ""


def _to_float(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def _ficha_sige(codigo, nome, preco, un_compra, fator, un_receita, custo_conv, status, hoje):
    """Monta a tag [SIGE ...] que vai pra obs (rastreabilidade + custo de referência)."""
    if fator and custo_conv is not None:
        conv = (f"1 {un_compra or 'un'}={_fmt(fator)} {un_receita} -> "
                f"R${_fmt(custo_conv)}/{un_receita}")
    elif fator:
        conv = f"1 {un_compra or 'un'}={_fmt(fator)} {un_receita} (custo suspeito, nao aplicado)"
    else:
        conv = "fator a confirmar"
    return (f'[SIGE cod={codigo} "{nome}" compra=R${_fmt(preco)}/{un_compra or "un"} '
            f'| {conv} | {status} | sync {hoje}]')


def _fmt(x):
    if x is None:
        return "?"
    return f"{x:.2f}".rstrip("0").rstrip(".") if isinstance(x, float) else str(x)


def _nova_obs(obs_atual, tag):
    """Remove qualquer ficha [SIGE ...] antiga e anexa a nova. Preserva o resto."""
    base = re.sub(r"\s*\[SIGE[^\]]*\]", "", obs_atual or "").strip()
    return (base + " " + tag).strip() if base else tag


# ════════════════════════════════════════════════════════════════════════════
# Núcleo reutilizável (CLI + futuro botão na página Suprimentos)
# ════════════════════════════════════════════════════════════════════════════
def sincronizar_insumos(db, produtos_por_codigo, depara=DEPARA, dry_run=True):
    """Aplica o de-para: atualiza custo/fornecedor/obs dos insumos. NÃO toca estoque.

    Retorna (stats, detalhes).
      detalhes: [{chave, status_depara, codigo_sige, custo_aplicado, custo_status,
                  fornecedor, acao}]
    """
    hoje = date.today().isoformat()
    stats = {"custo_aplicado": 0, "so_ficha": 0, "nao_cadastrado": 0,
             "codigo_fantasma": 0, "insumo_ausente": 0, "erros": []}
    detalhes = []

    for chave, codigo, fator, un_receita, status in depara:
        if codigo is None:
            stats["nao_cadastrado"] += 1
            detalhes.append({"chave": chave, "status_depara": status,
                             "codigo_sige": None, "custo_aplicado": None,
                             "custo_status": "nao_cadastrado", "fornecedor": None,
                             "acao": "pular (criar no SIGE)"})
            continue

        prod = produtos_por_codigo.get(str(codigo).strip())
        if not prod:
            stats["codigo_fantasma"] += 1
            stats["erros"].append(f"{chave}: codigo {codigo!r} nao existe no SIGE")
            detalhes.append({"chave": chave, "status_depara": status,
                             "codigo_sige": codigo, "custo_aplicado": None,
                             "custo_status": "codigo_fantasma", "fornecedor": None,
                             "acao": "ERRO"})
            continue

        insumo = db.get_insumo_por_codigo(chave)
        if not insumo:
            stats["insumo_ausente"] += 1
            stats["erros"].append(f"{chave}: insumo nao existe no nosso banco")
            detalhes.append({"chave": chave, "status_depara": status,
                             "codigo_sige": codigo, "custo_aplicado": None,
                             "custo_status": "insumo_ausente", "fornecedor": None,
                             "acao": "ERRO"})
            continue

        preco = _to_float(_campo(prod, "PrecoCusto"))
        forn = str(_campo(prod, "Fornecedor"))[:100] or None
        un_compra = str(_campo(prod, "EstoqueUnidade"))
        nome = str(_campo(prod, "Nome"))

        # Custo convertido pra unidade da receita — com sanity check
        custo_conv = None
        custo_status = "pendente"
        if fator and preco > PRECO_MIN_VALIDO:
            c = round(preco / fator, 4)
            if CUSTO_MIN <= c <= CUSTO_MAX:
                custo_conv = c
                custo_status = "aplicado"
            else:
                custo_status = "suspeito_nao_aplicado"
        elif not fator:
            custo_status = "sem_fator"
        else:
            custo_status = "preco_quebrado"

        tag = _ficha_sige(codigo, nome, preco, un_compra, fator, un_receita,
                          custo_conv, status, hoje)
        payload = {"obs": _nova_obs(insumo.get("obs"), tag)}
        if forn:
            payload["fornecedor"] = forn
        if custo_status == "aplicado":
            payload["custo_unitario"] = custo_conv
            stats["custo_aplicado"] += 1
            acao = f"custo R${custo_conv}/{un_receita} + fornecedor + ficha"
        else:
            stats["so_ficha"] += 1
            acao = f"fornecedor + ficha (custo {custo_status})"

        if not dry_run:
            try:
                db.atualizar_insumo(insumo["id"], payload)
            except Exception as e:
                stats["erros"].append(f"{chave}: {e}")
                acao = f"ERRO ao gravar: {e}"

        detalhes.append({"chave": chave, "status_depara": status,
                         "codigo_sige": codigo, "custo_aplicado": custo_conv,
                         "custo_status": custo_status, "fornecedor": forn,
                         "acao": acao})

    return stats, detalhes


# ════════════════════════════════════════════════════════════════════════════
# CLI
# ════════════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="Sincroniza custo/identidade dos insumos a partir do SIGE (read-only no SIGE).")
    parser.add_argument("--apply", action="store_true",
                        help="Escreve no banco. Sem isso, é DRY-RUN (só simula).")
    args = parser.parse_args()

    dry = not args.apply
    print(f"=== IMPORT SIGE (API) -> INSUMOS {'(DRY-RUN)' if dry else '(APLICANDO NO BANCO REAL)'} ===\n")

    _bootstrap_secrets()
    import sige_cloud_api as sige
    import database as db

    # 1. Lê o catálogo do SIGE (read-only)
    print("1) Lendo catálogo do SIGE...")
    con = sige.testar_conexao()
    if not con["ok"]:
        print(f"   SIGE indisponível: {con['mensagem']}")
        sys.exit(1)
    produtos = sige.listar_todos_produtos(page_size=200, max_paginas=50)
    por_codigo = {}
    for p in produtos:
        por_codigo.setdefault(str(_campo(p, "Codigo")).strip(), p)
    print(f"   {len(produtos)} produtos lidos.\n")

    # 2. Sincroniza
    print(f"2) Aplicando de-para ({len(DEPARA)} insumos)...")
    stats, detalhes = sincronizar_insumos(db, por_codigo, dry_run=dry)

    # 3. Relatório
    print(f"\n   {'insumo':<26} {'custo aplicado':>14}  ação")
    print("   " + "-" * 92)
    for d in detalhes:
        custo = (f"R${d['custo_aplicado']}" if d["custo_aplicado"] is not None
                 else "—")
        print(f"   {d['chave']:<26} {custo:>14}  {d['acao']}")

    print(f"\n=== RESUMO ===")
    print(f"  Custo aplicado:            {stats['custo_aplicado']}")
    print(f"  Só ficha+fornecedor:       {stats['so_ficha']}  (custo pendente de confirmação)")
    print(f"  Não cadastrados no SIGE:   {stats['nao_cadastrado']}")
    print(f"  Códigos fantasma:          {stats['codigo_fantasma']}")
    print(f"  Insumos ausentes no banco: {stats['insumo_ausente']}")
    print(f"  Erros:                     {len(stats['erros'])}")
    for e in stats["erros"]:
        print(f"    • {e}")

    if dry:
        print(f"\n💡 Dry-run — nada foi gravado. Pra aplicar no banco REAL: python importar_sige_api.py --apply")
    else:
        print(f"\n✅ Aplicado. (Estoque NÃO foi tocado — carga inicial vem da contagem física.)")


if __name__ == "__main__":
    main()
