# -*- coding: utf-8 -*-
"""
contribuicao_produto.py — Contribuição (receita − custo de matéria-prima) por
produto, generalizando o custo pelo PESO do formato. PURO: não importa Streamlit.

A SACADA: o nome do produto no SIGE traz a gramatura ("Cubos 160G", "Zero 100G").
Tendo o custo por KG de cada sabor de cocada (do BOM ÷ kg vendável por tacho),
o custo de QUALQUER formato de cocada = custo/kg × peso. Isso cobre a maior parte
da receita (cocada), sem depender de mapear formato por formato.

HONESTIDADE (sempre): a "contribuição" aqui é receita − custo de MATÉRIA-PRIMA.
NÃO é lucro líquido — falta o custo de conversão (mão de obra/energia/embalagem),
que é externo ao SIGE e está sendo levantado à parte. O RANKING (quem contribui
mais) é robusto; o valor ABSOLUTO escala com o rendimento do tacho (em disputa).
Cobre cocada (por peso) + Pão de Mel; palha/bala/outros ficam marcados "a confirmar".
"""
import re
import unicodedata
import custo_producao as cp

# Base de rendimento: 1 bandeja 45g = 100 und × 45 g = 4,5 kg de cocada vendável
# (≠ 5,5 kg da bandeja úmida; ~1 kg vira aparas/umidade/cinta).
# >>> CONFIRMADO PELA FÁBRICA (15/06/2026): tacho normal = 8 bandejas, Zero = 3.
# (Bandeja = 5,5 kg em todos. A dúvida do "4-5" foi descartada: é 8 mesmo.)
KG_VENDAVEL_POR_BANDEJA = 4.5
BAND_POR_TACHO = {"cocada_T_tacho": 8, "cocada_L_tacho": 8, "cocada_B_tacho": 8,
                  "cocada_C_tacho": 8, "cocada_P_tacho": 8, "cocada_Z_tacho": 3}

SABOR_LABEL = {
    "cocada_T_tacho": "Tradicional", "cocada_L_tacho": "Leite Condensado",
    "cocada_B_tacho": "Brigadeiro",  "cocada_C_tacho": "Café",
    "cocada_P_tacho": "Pé de Moça",  "cocada_Z_tacho": "Zero",
}

# Detecção de sabor por palavra-chave (sem acento). Ordem importa.
_SABOR_KEYS = [
    ("ZERO", "cocada_Z_tacho"),
    ("LEITE CONDENSADO", "cocada_L_tacho"), ("LEITE COND", "cocada_L_tacho"),
    ("BRIGADEIRO", "cocada_B_tacho"),
    ("CAFE", "cocada_C_tacho"),
    ("PE DE MOCA", "cocada_P_tacho"),
    ("TRADICIONAL", "cocada_T_tacho"), ("TRADICONAL", "cocada_T_tacho"),
]


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").upper()


def custo_kg_cocada(db, custo_por_id=None) -> dict:
    """{chave_bom: {nome, custo_tacho, kg_tacho, custo_kg, parcial}} por sabor."""
    if custo_por_id is None:
        custo_por_id = cp._mapa_custos(db)
    out = {}
    for chave, band in BAND_POR_TACHO.items():
        cr = cp.custo_produto(db, chave, custo_por_id)
        kg = band * KG_VENDAVEL_POR_BANDEJA
        out[chave] = {
            "nome": cr["nome"], "label": SABOR_LABEL[chave],
            "custo_tacho": cr["custo_receita"], "kg_tacho": kg,
            "custo_kg": cr["custo_receita"] / kg if kg else None,
            "parcial": cr["parcial"],
        }
    return out


def custo_unit_pm(db, custo_por_id=None):
    """Custo de matéria-prima por unidade de Pão de Mel (R$/und)."""
    cr = cp.custo_produto(db, "pm_bolo", custo_por_id or cp._mapa_custos(db))
    rend = cr.get("rend_qtd") or 70
    return cr["custo_receita"] / rend if rend else None


def custo_unit_bala(db, custo_por_id=None):
    """Custo de matéria-prima por bala (pacote de 400 g). 1 tacho = 30 balas
    (confirmado pela fábrica 15/06/2026)."""
    cr = cp.custo_produto(db, "bala_tacho", custo_por_id or cp._mapa_custos(db))
    return cr.get("custo_por_unidade")  # já é custo_receita / 30


def custo_unit_assada(db, custo_por_id=None):
    """Custo de matéria-prima por cumbuca de Cocada Assada (1 lote = 30 cumbucas;
    Leonardo 17/06/2026). É só a MASSA — o casco/cumbuca e a embalagem NÃO entram
    (sem custo disponível), igual às demais cocadas que também não contam embalagem.
    Logo o custo sai PARCIAL/subestimado. Retorna None se a receita ainda não foi
    cadastrada no banco (evita mostrar margem 100% falsa antes do seed rodar)."""
    cr = cp.custo_produto(db, "cocada_assada_cumbuca", custo_por_id or cp._mapa_custos(db))
    c = cr.get("custo_por_unidade")
    return c if c else None  # já é custo_receita / 30


def classificar(nome: str):
    """(tipo, chave, gramas). tipo: 'cocada' | 'pm' | 'bala' | None.
    cocada: precisa de sabor + gramatura no nome. pm: 'PAO DE MEL'.
    bala: 'BALA DE DOCE DE LEITE' (1 tacho = 30 balas de 400g — fábrica 15/06)."""
    n = _sem_acento(nome)
    if "BALA DE DOCE DE LEITE" in n:
        m = re.search(r"(\d+)\s*G\b", n)
        return "bala", None, (float(m.group(1)) if m else None)
    if "PAO DE MEL" in n:
        m = re.search(r"(\d+)\s*G\b", n)
        return "pm", None, (float(m.group(1)) if m else None)
    if "PALHA" in n:
        return None, None, None
    # Cocada Assada na Cumbuca — receita/processo próprios (assada, leva ovo).
    # Detecta por ASSADA/CUMBUCA antes do casamento por sabor (não tem sabor).
    if "ASSADA" in n or "CUMBUCA" in n:
        m = re.search(r"(\d+)\s*G\b", n)
        return "assada", "cocada_assada_cumbuca", (float(m.group(1)) if m else None)
    # Indicadores de que é cocada (alguns nomes não trazem "COCADA", ex.:
    # "PE DE MOCA CUBOS 160G"): aceita COCADA / TABLETE / CUBOS / CREMOSA.
    if not any(t in n for t in ("COCADA", "TABLETE", "CUBOS", "CREMOSA")):
        return None, None, None
    chave = next((ch for termo, ch in _SABOR_KEYS if termo in n), None)
    if not chave:
        return None, None, None
    m = re.search(r"(\d+)\s*G\b", n)
    if not m:
        return None, None, None
    return "cocada", chave, float(m.group(1))


def custo_unit_produto(nome, ckg, custo_pm, custo_bala=None, custo_assada=None):
    """Custo de MP por unidade vendável de um produto, ou None se não mapeável."""
    tipo, chave, gramas = classificar(nome)
    if tipo == "cocada" and chave and gramas:
        ck = ckg.get(chave, {}).get("custo_kg")
        return ck * (gramas / 1000.0) if ck else None
    if tipo == "pm":
        return custo_pm
    if tipo == "bala":
        return custo_bala
    if tipo == "assada":
        return custo_assada
    return None


def contribuicao(db, agregado_vendas: dict, custo_por_id=None) -> dict:
    """Cruza o agregado de vendas (vendas_sige.agregar_vendas) com o custo por peso.
    Retorna linhas por produto + totais + cobertura."""
    if custo_por_id is None:
        custo_por_id = cp._mapa_custos(db)
    ckg = custo_kg_cocada(db, custo_por_id)
    cpm = custo_unit_pm(db, custo_por_id)
    cba = custo_unit_bala(db, custo_por_id)
    cas = custo_unit_assada(db, custo_por_id)

    linhas = []
    total_receita = receita_coberta = contrib_total = 0.0
    for cod, d in agregado_vendas["por_produto"].items():
        total_receita += d["receita"]
        cu = custo_unit_produto(d["descricao"], ckg, cpm, cba, cas)
        tipo, chave, gramas = classificar(d["descricao"])
        if cu is not None:
            custo = cu * d["qtd"]
            contrib = d["receita"] - custo
            receita_coberta += d["receita"]
            contrib_total += contrib
            linhas.append({
                "codigo": cod, "descricao": d["descricao"], "qtd": round(d["qtd"], 0),
                "receita": round(d["receita"], 2), "custo_mp": round(custo, 2),
                "contrib": round(contrib, 2),
                "margem_pct": round(contrib / d["receita"] * 100, 1) if d["receita"] else None,
                "sabor": SABOR_LABEL.get(chave, {"pm": "Pão de Mel", "bala": "Bala",
                                                 "assada": "Cocada Assada"}.get(tipo, "—")),
                "gramas": gramas, "mapeado": True,
            })
        else:
            linhas.append({
                "codigo": cod, "descricao": d["descricao"], "qtd": round(d["qtd"], 0),
                "receita": round(d["receita"], 2), "custo_mp": None, "contrib": None,
                "margem_pct": None, "sabor": "—", "gramas": None, "mapeado": False,
            })
    return {
        "linhas": linhas, "custo_kg": ckg, "custo_pm": cpm,
        "total_receita": round(total_receita, 2),
        "receita_coberta": round(receita_coberta, 2),
        "cobertura_pct": round(receita_coberta / total_receita * 100, 1) if total_receita else 0,
        "contrib_total": round(contrib_total, 2),
    }


def contribuicao_por_sabor(linhas: list) -> dict:
    """Agrega as linhas mapeadas por sabor: {sabor: {receita, contrib, qtd}}."""
    out = {}
    for l in linhas:
        if not l["mapeado"]:
            continue
        s = l["sabor"]
        d = out.setdefault(s, {"receita": 0.0, "contrib": 0.0, "qtd": 0.0})
        d["receita"] += l["receita"]
        d["contrib"] += l["contrib"]
        d["qtd"] += l["qtd"]
    return out


def producao_por_sabor(db) -> dict:
    """Bandejas de cocada CORTADAS por sabor, somadas em todas as folhas (FLUXO).
    Mesma métrica da Curva ABC de produção (ord_corte_*). {label_sabor: bandejas}."""
    datas = db.list_datas_folha()
    soma = {}
    for d in datas:
        for r in db.get_folha_cocada(d):
            chave = next((ch for termo, ch in _SABOR_KEYS
                          if termo in _sem_acento(r.get("sabor", ""))), None)
            if not chave:
                continue
            band = (int(r.get("ord_corte_45g") or 0) + int(r.get("ord_corte_mini") or 0)
                    + int(r.get("ord_corte_pet") or 0))
            if band:
                lab = SABOR_LABEL[chave]
                soma[lab] = soma.get(lab, 0) + band
    return soma


def por_canal(db, pedidos: list, custo_por_id=None) -> dict:
    """Contribuição por canal de venda (Tabela). Aplica o custo por peso a cada
    item faturado. {canal: {receita, custo, contrib, margem_pct}}."""
    if custo_por_id is None:
        custo_por_id = cp._mapa_custos(db)
    ckg = custo_kg_cocada(db, custo_por_id)
    cpm = custo_unit_pm(db, custo_por_id)
    cba = custo_unit_bala(db, custo_por_id)
    cas = custo_unit_assada(db, custo_por_id)

    def _num(v):
        try:
            return float(str(v).replace(",", "."))
        except (TypeError, ValueError):
            return 0.0

    canais = {}
    for ped in pedidos:
        if "fatur" not in str(ped.get("StatusSistema") or "").lower():
            continue
        canal = str(ped.get("Tabela") or "(sem canal)")
        for it in (ped.get("Items") or []):
            rec = _num(it.get("ValorTotal"))
            qtd = _num(it.get("Quantidade"))
            cu = custo_unit_produto(it.get("Descricao"), ckg, cpm, cba, cas)
            d = canais.setdefault(canal, {"receita": 0.0, "custo": 0.0,
                                          "receita_coberta": 0.0})
            d["receita"] += rec
            if cu is not None:
                d["custo"] += cu * qtd
                d["receita_coberta"] += rec
    for c, d in canais.items():
        d["contrib"] = round(d["receita_coberta"] - d["custo"], 2)
        d["margem_pct"] = (round(d["contrib"] / d["receita_coberta"] * 100, 1)
                           if d["receita_coberta"] else None)
        d["receita"] = round(d["receita"], 2)
        d["custo"] = round(d["custo"], 2)
        d["receita_coberta"] = round(d["receita_coberta"], 2)
    return canais


# ── Produção × Demanda (o coração: o que a fábrica corta × o que o mercado compra)
def demanda_por_sabor(pedidos: list) -> dict:
    """Volume (un) e receita (R$) de COCADA por SABOR (os 6 sabores de tacho), a
    partir dos pedidos faturados do SIGE. Usa classificar() pra mapear cada item →
    sabor; ignora o que não é cocada de tacho (assada/PM/bala/palha/revenda).
    {label_sabor: {volume, receita}}."""
    def _n(v):
        try:
            return float(str(v).replace(",", "."))
        except (TypeError, ValueError):
            return 0.0
    out = {}
    for ped in pedidos:
        if "fatur" not in str(ped.get("StatusSistema") or "").lower():
            continue
        for it in (ped.get("Items") or []):
            tipo, chave, _g = classificar(it.get("Descricao"))
            if tipo != "cocada" or not chave:
                continue
            lab = SABOR_LABEL[chave]
            d = out.setdefault(lab, {"volume": 0.0, "receita": 0.0})
            d["volume"] += _n(it.get("Quantidade"))
            d["receita"] += _n(it.get("ValorTotal"))
    return out


def producao_x_demanda(db, pedidos: list) -> list:
    """Cruza PRODUÇÃO (bandejas cortadas das folhas, por sabor) com DEMANDA (volume
    + receita vendidos do SIGE, por sabor). Compara o MIX (%) — corte está em
    bandejas e venda em unidades/reais, então o que se compara é a PROPORÇÃO de cada
    sabor em cada lado. gap > 0 ⇒ produz mais (em proporção) do que vende; gap < 0 ⇒
    vende mais do que produz (oportunidade). 1 linha por sabor."""
    prod = producao_por_sabor(db)                     # {label: bandejas}
    dem = demanda_por_sabor(pedidos)                  # {label: {volume, receita}}
    ordem = [SABOR_LABEL[k] for k in BAND_POR_TACHO]  # 6 sabores, ordem fixa
    tot_b = sum(prod.values()) or 1.0
    tot_v = sum(d["volume"] for d in dem.values()) or 1.0
    tot_r = sum(d["receita"] for d in dem.values()) or 1.0
    linhas = []
    for s in ordem:
        b = prod.get(s, 0) or 0
        v = dem.get(s, {}).get("volume", 0) or 0
        r = dem.get(s, {}).get("receita", 0) or 0
        pct_prod = b / tot_b * 100
        pct_vol = v / tot_v * 100
        pct_rec = r / tot_r * 100
        linhas.append({
            "sabor": s, "bandejas": b, "volume": v, "receita": r,
            "pct_prod": round(pct_prod, 1),
            "pct_vol": round(pct_vol, 1),
            "pct_rec": round(pct_rec, 1),
            "gap_vol": round(pct_prod - pct_vol, 1),
            "gap_rec": round(pct_prod - pct_rec, 1),
        })
    return linhas


# ── CLI de validação (read-only) ─────────────────────────────────────────────
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
    import database as db
    import sige_cloud_api as sige
    import vendas_sige as vs

    D_INI, D_FIM = "2026-05-16", "2026-06-15"
    print(f"=== CONTRIBUIÇÃO · {D_INI}..{D_FIM} · READ-ONLY ===\n")
    pedidos = sige.listar_todos_pedidos(D_INI, D_FIM)
    ag = vs.agregar_vendas(pedidos)
    res = contribuicao(db, ag)

    print("[1] CUSTO POR KG (sabor):")
    for ch, d in res["custo_kg"].items():
        print(f"    {d['label']:<18} R$ {d['custo_kg']:>5.2f}/kg" + (" ⚠" if d["parcial"] else ""))
    print(f"    Pão de Mel (und): R$ {res['custo_pm']:.3f}")

    print(f"\n[2] COBERTURA: R$ {res['receita_coberta']:,.0f} de R$ {res['total_receita']:,.0f} "
          f"= {res['cobertura_pct']}%")
    print(f"    Contribuição de MP coberta: R$ {res['contrib_total']:,.0f}")

    print("\n[3] TOP 10 por CONTRIBUIÇÃO:")
    for l in sorted([x for x in res["linhas"] if x["mapeado"]], key=lambda x: -x["contrib"])[:10]:
        print(f"    R$ {l['contrib']:>8,.0f}  ({l['margem_pct']:>4.0f}%)  {str(l['descricao'])[:34]}")

    print("\n[4] POR SABOR (contribuição):")
    cps = contribuicao_por_sabor(res["linhas"])
    for s, d in sorted(cps.items(), key=lambda x: -x[1]["contrib"]):
        print(f"    {s:<18} R$ {d['contrib']:>8,.0f}  (receita R$ {d['receita']:>8,.0f})")

    print("\n[5] PRODUÇÃO × VENDA (por sabor):")
    prod = producao_por_sabor(db)
    tot_band = sum(prod.values()) or 1
    tot_contrib = sum(d["contrib"] for d in cps.values()) or 1
    print(f"    {'sabor':<18}{'%produção':>10}{'%contrib':>10}")
    for s in SABOR_LABEL.values():
        pb = prod.get(s, 0) / tot_band * 100
        pc = cps.get(s, {}).get("contrib", 0) / tot_contrib * 100
        print(f"    {s:<18}{pb:>9.1f}%{pc:>9.1f}%")

    print("\n[6] MARGEM POR CANAL:")
    canais = por_canal(db, pedidos)
    for c, d in sorted(canais.items(), key=lambda x: -x[1]["contrib"]):
        print(f"    {c:<14} receita R$ {d['receita']:>9,.0f} | contrib(coberto) "
              f"R$ {d['contrib']:>9,.0f} ({d['margem_pct']}%)")

    print("\n[7] MAIORES VENDAS SEM CUSTO (a confirmar):")
    for l in sorted([x for x in res["linhas"] if not x["mapeado"]], key=lambda x: -x["receita"])[:6]:
        print(f"    R$ {l['receita']:>8,.0f}  {str(l['descricao'])[:42]}")


if __name__ == "__main__":
    main()
