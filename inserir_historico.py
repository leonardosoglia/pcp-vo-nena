"""
inserir_historico.py — script auxiliar pra inserir as 9 folhas históricas no banco.

Usa salvar_folha_completa com os campos extraídos das fotos via leitura visual.
Estratégia conservadora: insere apenas campos com ALTA confiança (Embalados + linha 36).
Outros campos ficam zerados pra Leonardo preencher manualmente revisando as fotos.

Datas inseridas:
    2026-04-02 (manuscrita — só casca, ele preenche tudo)
    2026-04-16 (manuscrita — só casca)
    2026-04-23, 2026-04-28, 2026-04-29, 2026-04-30
    2026-05-04, 2026-05-05, 2026-05-06, 2026-05-07
"""
from database import salvar_folha_completa, list_datas_folha


def _z(d):
    """Helper: completa um dict de cocada com defaults zero."""
    base = {
        "emb_45g": 0, "emb_mini": 0, "emb_pet": 0,
        "emb_potes_260g": 0, "emb_potes_605g": 0,
        "cort1_45g": 0, "cort1_mini": 0, "cort1_pet": 0,
        "ord_corte_45g": 0, "ord_corte_mini": 0, "ord_corte_pet": 0,
        "ord_prod_band": 0, "ord_prod_virada": 0,
        "ord_prod_potes_260g": 0, "ord_prod_potes_605g": 0,
        "ord_emb_45g": 0, "ord_emb_mini": 0,
        "param_real_45g": 0, "param_real_mini": 0, "param_real_pet": 0,
        "amanha_obs": "",
    }
    base.update(d)
    return base


def _zp(d):
    """Helper palha."""
    base = {
        "emb_50g": 0, "emb_pet": 0,
        "cont_band_palha": 0, "cont_band_pos_corte": 0,
        "ord_corte_50g": 0, "ord_corte_pet": 0,
        "ord_prod_band": 0,
    }
    base.update(d)
    return base


def _pmbd(cnt_pm=0, cnt_balas=0, cnt_doces=0,
          ord_pm=0, ord_balas=0, ord_amanha="", obs=""):
    return {
        "cnt_pm": cnt_pm, "cnt_balas": cnt_balas, "cnt_doces_displays": cnt_doces,
        "ord_pm": ord_pm, "ord_balas": ord_balas,
        "ord_amanha_obs": ord_amanha,
        "obs": obs, "obs_joel": "", "obs_gil": "", "obs_leonilia": "",
    }


# ════════════════════════════════════════════════════════════════════════════
# FOLHAS — dados extraídos das fotos (campos com alta confiança)
# ════════════════════════════════════════════════════════════════════════════

# 07/05/2026 (Quinta) — foto 12.45.13
F_07_05 = {
    "data": "2026-05-07",
    "cocada": {
        "TRADICIONAL":      _z({"emb_45g": 2880, "emb_mini": 416, "emb_pet": 75,  "emb_potes_260g": 24, "emb_potes_605g": 13}),
        "LEITE CONDENSADO": _z({"emb_45g": 1830, "emb_mini": 416, "emb_pet": 83,  "emb_potes_260g": 51, "emb_potes_605g": 9}),
        "BRIGADEIRO":       _z({"emb_45g": 1320, "emb_mini": 208, "emb_pet": 98,  "emb_potes_260g": 15, "emb_potes_605g": 8}),
        "CAFÉ":             _z({"emb_45g": 950,  "emb_mini": 104, "emb_pet": 45,  "emb_potes_260g": 23, "emb_potes_605g": 10}),
        "PÉ DE MOÇA":       _z({"emb_45g": 1110, "emb_mini": 364, "emb_pet": 28,  "emb_potes_260g": 18, "emb_potes_605g": 12}),
        "ZERO":             _z({"emb_mini": 470, "emb_pet": 141, "emb_potes_260g": 39, "emb_potes_605g": 10}),
    },
    "palha": {
        "TRADICIONAL":  _zp({"emb_50g": 244, "emb_pet": 189}),
        "LEITE EM PÓ":  _zp({"emb_50g": 283, "emb_pet": 192}),
        "CHURROS":      _zp({"emb_50g": 192, "emb_pet": 89}),
        "COOKIES":      _zp({"emb_pet": 86}),
        "LIMÃO":        _zp({"emb_pet": 74}),
    },
    "pmbd": _pmbd(cnt_pm=9, cnt_balas=7, cnt_doces=23,
                  ord_balas=2, ord_pm=4, ord_amanha="4"),
}

# 06/05/2026 (Quarta) — foto 15.29.27
F_06_05 = {
    "data": "2026-05-06",
    "cocada": {
        "TRADICIONAL":      _z({"emb_45g": 1790, "emb_mini": 416, "emb_pet": 20, "emb_potes_260g": 34, "emb_potes_605g": 12}),
        "LEITE CONDENSADO": _z({"emb_45g": 1400, "emb_mini": 416, "emb_pet": 13, "emb_potes_260g": 51, "emb_potes_605g": 9}),
        "BRIGADEIRO":       _z({"emb_45g": 1150, "emb_mini": 260, "emb_pet": 42, "emb_potes_260g": 16, "emb_potes_605g": 8}),
        "CAFÉ":             _z({"emb_45g": 850,  "emb_mini": 104, "emb_pet": 70, "emb_potes_260g": 7,  "emb_potes_605g": 6}),
        "PÉ DE MOÇA":       _z({"emb_45g": 830,  "emb_mini": 416, "emb_pet": 60, "emb_potes_260g": 18, "emb_potes_605g": 7}),
        "ZERO":             _z({"emb_mini": 930, "emb_pet": 65, "emb_potes_260g": 39, "emb_potes_605g": 4}),
    },
    "palha": {
        "TRADICIONAL":  _zp({"emb_50g": 480, "emb_pet": 200}),
        "LEITE EM PÓ":  _zp({"emb_50g": 388, "emb_pet": 236}),
        "CHURROS":      _zp({"emb_50g": 150, "emb_pet": 89}),
        "COOKIES":      _zp({"emb_pet": 6}),
        "LIMÃO":        _zp({"emb_pet": 16}),
    },
    "pmbd": _pmbd(cnt_pm=26, cnt_balas=67, cnt_doces=0,
                  ord_balas=3, ord_pm=4, ord_amanha=""),
}

# 05/05/2026 (Terça) — foto 15.29.28
F_05_05 = {
    "data": "2026-05-05",
    "cocada": {
        "TRADICIONAL":      _z({"emb_45g": 2220, "emb_mini": 104,  "emb_pet": 0,   "emb_potes_260g": 34, "emb_potes_605g": 15}),
        "LEITE CONDENSADO": _z({"emb_45g": 1400, "emb_mini": 104,  "emb_pet": 42,  "emb_potes_260g": 51, "emb_potes_605g": 14}),
        "BRIGADEIRO":       _z({"emb_45g": 980,  "emb_mini": 0,    "emb_pet": 62,  "emb_potes_260g": 17, "emb_potes_605g": 7}),
        "CAFÉ":             _z({"emb_45g": 680,  "emb_mini": 104,  "emb_pet": 103, "emb_potes_260g": 7,  "emb_potes_605g": 5}),
        "PÉ DE MOÇA":       _z({"emb_45g": 710,  "emb_mini": 52,   "emb_pet": 25,  "emb_potes_260g": 18, "emb_potes_605g": 1}),
        "ZERO":             _z({"emb_mini": 1010, "emb_pet": 100,  "emb_potes_260g": 45, "emb_potes_605g": 7}),
    },
    "palha": {
        "TRADICIONAL":  _zp({"emb_50g": 87,  "emb_pet": 176}),
        "LEITE EM PÓ":  _zp({"emb_50g": 290, "emb_pet": 153}),
        "CHURROS":      _zp({"emb_50g": 119, "emb_pet": 71}),
        "COOKIES":      _zp({"emb_pet": 22}),
        "LIMÃO":        _zp({"emb_pet": 32}),
    },
    "pmbd": _pmbd(cnt_pm=41, cnt_balas=23, cnt_doces=13,
                  ord_balas=3, ord_pm=0, ord_amanha="4"),
}

# 04/05/2026 (Segunda) — foto 15.29.30
F_04_05 = {
    "data": "2026-05-04",
    "cocada": {
        "TRADICIONAL":      _z({"emb_45g": 1780, "emb_mini": 260, "emb_pet": 92,  "emb_potes_260g": 32, "emb_potes_605g": 6}),
        "LEITE CONDENSADO": _z({"emb_45g": 1380, "emb_mini": 416, "emb_pet": 171, "emb_potes_260g": 31, "emb_potes_605g": 14}),
        "BRIGADEIRO":       _z({"emb_45g": 700,  "emb_mini": 156, "emb_pet": 88,  "emb_potes_260g": 22, "emb_potes_605g": 7}),
        "CAFÉ":             _z({"emb_45g": 780,  "emb_mini": 208, "emb_pet": 139, "emb_potes_260g": 13, "emb_potes_605g": 5}),
        "PÉ DE MOÇA":       _z({"emb_45g": 640,  "emb_mini": 156, "emb_pet": 51,  "emb_potes_260g": 12, "emb_potes_605g": 7}),
        "ZERO":             _z({"emb_mini": 660, "emb_pet": 154, "emb_potes_260g": 31, "emb_potes_605g": 16}),
    },
    "palha": {
        "TRADICIONAL":  _zp({"emb_50g": 249, "emb_pet": 212}),
        "LEITE EM PÓ":  _zp({"emb_50g": 388, "emb_pet": 176}),
        "CHURROS":      _zp({"emb_50g": 181, "emb_pet": 65}),
        "COOKIES":      _zp({"emb_pet": 42}),
        "LIMÃO":        _zp({"emb_pet": 46}),
    },
    "pmbd": _pmbd(cnt_pm=56, cnt_balas=46, cnt_doces=13,
                  ord_balas=3, ord_pm=0, ord_amanha="4"),
}

# 30/04/2026 (Quinta) — foto 15.29.31
F_30_04 = {
    "data": "2026-04-30",
    "cocada": {
        "TRADICIONAL":      _z({"emb_45g": 2120, "emb_mini": 260, "emb_pet": 35,  "emb_potes_260g": 45, "emb_potes_605g": 13}),
        "LEITE CONDENSADO": _z({"emb_45g": 1200, "emb_mini": 416, "emb_pet": 173, "emb_potes_260g": 53, "emb_potes_605g": 16}),
        "BRIGADEIRO":       _z({"emb_45g": 500,  "emb_mini": 156, "emb_pet": 108, "emb_potes_260g": 24, "emb_potes_605g": 14}),
        "CAFÉ":             _z({"emb_45g": 400,  "emb_mini": 208, "emb_pet": 70,  "emb_potes_260g": 15, "emb_potes_605g": 7}),
        "PÉ DE MOÇA":       _z({"emb_45g": 680,  "emb_mini": 156, "emb_pet": 79,  "emb_potes_260g": 20, "emb_potes_605g": 3}),
        "ZERO":             _z({"emb_mini": 1030, "emb_pet": 116, "emb_potes_260g": 41, "emb_potes_605g": 20}),
    },
    "palha": {
        "TRADICIONAL":  _zp({"emb_50g": 159, "emb_pet": 231}),
        "LEITE EM PÓ":  _zp({"emb_50g": 201, "emb_pet": 195}),
        "CHURROS":      _zp({"emb_50g": 182, "emb_pet": 72}),
        "COOKIES":      _zp({"emb_pet": 44}),
        "LIMÃO":        _zp({"emb_pet": 64}),
    },
    "pmbd": _pmbd(cnt_pm=18, cnt_balas=77, cnt_doces=33,
                  ord_balas=0, ord_pm=0, ord_amanha="4"),
}

# 29/04/2026 (Quarta) — foto 15.29.32
F_29_04 = {
    "data": "2026-04-29",
    "cocada": {
        "TRADICIONAL":      _z({"emb_45g": 2580, "emb_mini": 364, "emb_pet": 145, "emb_potes_260g": 51, "emb_potes_605g": 15}),
        "LEITE CONDENSADO": _z({"emb_45g": 1150, "emb_mini": 520, "emb_pet": 253, "emb_potes_260g": 59, "emb_potes_605g": 19}),
        "BRIGADEIRO":       _z({"emb_45g": 1000, "emb_mini": 156, "emb_pet": 130, "emb_potes_260g": 28, "emb_potes_605g": 16}),
        "CAFÉ":             _z({"emb_45g": 690,  "emb_mini": 208, "emb_pet": 115, "emb_potes_260g": 13, "emb_potes_605g": 5}),
        "PÉ DE MOÇA":       _z({"emb_45g": 480,  "emb_mini": 208, "emb_pet": 105, "emb_potes_260g": 25, "emb_potes_605g": 5}),
        "ZERO":             _z({"emb_mini": 480, "emb_pet": 206, "emb_potes_260g": 48, "emb_potes_605g": 21}),
    },
    "palha": {
        "TRADICIONAL":  _zp({"emb_50g": 412, "emb_pet": 281}),
        "LEITE EM PÓ":  _zp({"emb_50g": 298, "emb_pet": 250}),
        "CHURROS":      _zp({"emb_50g": 27,  "emb_pet": 84}),
        "COOKIES":      _zp({"emb_pet": 60}),
        "LIMÃO":        _zp({"emb_pet": 80}),
    },
    "pmbd": _pmbd(cnt_pm=42, cnt_balas=111, cnt_doces=0,
                  ord_balas=2, ord_pm=4, ord_amanha=""),
}

# 28/04/2026 (Terça) — foto 15.29.33
F_28_04 = {
    "data": "2026-04-28",
    "cocada": {
        "TRADICIONAL":      _z({"emb_45g": 1580, "emb_mini": 208, "emb_pet": 84, "emb_potes_260g": 52, "emb_potes_605g": 18}),
        "LEITE CONDENSADO": _z({"emb_45g": 2050, "emb_mini": 364, "emb_pet": 88, "emb_potes_260g": 39, "emb_potes_605g": 14}),
        "BRIGADEIRO":       _z({"emb_45g": 540,  "emb_mini": 52,  "emb_pet": 66, "emb_potes_260g": 28, "emb_potes_605g": 15}),
        "CAFÉ":             _z({"emb_45g": 520,  "emb_mini": 52,  "emb_pet": 18, "emb_potes_260g": 7,  "emb_potes_605g": 8}),
        "PÉ DE MOÇA":       _z({"emb_45g": 200,  "emb_mini": 208, "emb_pet": 111, "emb_potes_260g": 18, "emb_potes_605g": 7}),
        "ZERO":             _z({"emb_mini": 780, "emb_pet": 111, "emb_potes_260g": 18}),
    },
    "palha": {
        "TRADICIONAL":  _zp({"emb_50g": 0,  "emb_pet": 0}),
        "LEITE EM PÓ":  _zp({"emb_50g": 0,  "emb_pet": 0}),
        "CHURROS":      _zp({"emb_50g": 0,  "emb_pet": 0}),
        "COOKIES":      _zp({}),
        "LIMÃO":        _zp({}),
    },
    "pmbd": _pmbd(cnt_pm=0, cnt_balas=0, cnt_doces=0,
                  ord_balas=1, ord_pm=4, ord_amanha="4"),
}

# 23/04/2026 (Quinta) — foto 15.29.34
F_23_04 = {
    "data": "2026-04-23",
    "cocada": {
        "TRADICIONAL":      _z({"emb_45g": 1500, "emb_mini": 208, "emb_pet": 152, "emb_potes_260g": 67, "emb_potes_605g": 27}),
        "LEITE CONDENSADO": _z({"emb_45g": 1140, "emb_mini": 258, "emb_pet": 131, "emb_potes_260g": 64, "emb_potes_605g": 20}),
        "BRIGADEIRO":       _z({"emb_45g": 480,  "emb_mini": 208, "emb_pet": 217, "emb_potes_260g": 12, "emb_potes_605g": 17}),
        "CAFÉ":             _z({"emb_45g": 420,  "emb_mini": 208, "emb_pet": 64,  "emb_potes_260g": 8,  "emb_potes_605g": 16}),
        "PÉ DE MOÇA":       _z({"emb_45g": 520,  "emb_mini": 260, "emb_pet": 119, "emb_potes_260g": 18, "emb_potes_605g": 6}),
        "ZERO":             _z({"emb_mini": 890, "emb_pet": 252, "emb_potes_260g": 314, "emb_potes_605g": 18}),
    },
    "palha": {
        "TRADICIONAL":  _zp({"emb_50g": 590, "emb_pet": 183}),
        "LEITE EM PÓ":  _zp({"emb_50g": 558, "emb_pet": 183}),
        "CHURROS":      _zp({"emb_50g": 169, "emb_pet": 82}),
        "COOKIES":      _zp({}),
        "LIMÃO":        _zp({"emb_pet": 58}),
    },
    "pmbd": _pmbd(cnt_pm=39, cnt_balas=0, cnt_doces=0,
                  ord_balas=2, ord_pm=4, ord_amanha=""),
}

# 16/04/2026 (Quinta) — MANUSCRITA — só casca
F_16_04 = {
    "data": "2026-04-16",
    "cocada": {
        "TRADICIONAL":      _z({}),
        "LEITE CONDENSADO": _z({}),
        "BRIGADEIRO":       _z({}),
        "CAFÉ":             _z({}),
        "PÉ DE MOÇA":       _z({}),
        "ZERO":             _z({}),
    },
    "palha": {s: _zp({}) for s in ("TRADICIONAL", "LEITE EM PÓ", "CHURROS", "COOKIES", "LIMÃO")},
    "pmbd": _pmbd(obs="📝 FOLHA MANUSCRITA — preencher manualmente. Foto em folhas-semanais/semana_13-04_a_17-04_2026/16-04_folha_producao.jpeg"),
}

# 02/04/2026 (Quinta) — MANUSCRITA — só casca
F_02_04 = {
    "data": "2026-04-02",
    "cocada": {
        "TRADICIONAL":      _z({}),
        "LEITE CONDENSADO": _z({}),
        "BRIGADEIRO":       _z({}),
        "CAFÉ":             _z({}),
        "PÉ DE MOÇA":       _z({}),
        "ZERO":             _z({}),
    },
    "palha": {s: _zp({}) for s in ("TRADICIONAL", "LEITE EM PÓ", "CHURROS", "COOKIES", "LIMÃO")},
    "pmbd": _pmbd(obs="📝 FOLHA MANUSCRITA — preencher manualmente. Foto em folhas-semanais/semana_30-03_a_03-04_2026/02-04_folha_producao.jpeg"),
}


# ════════════════════════════════════════════════════════════════════════════
# EXECUÇÃO
# ════════════════════════════════════════════════════════════════════════════
TODAS = [F_07_05, F_06_05, F_05_05, F_04_05, F_30_04, F_29_04, F_28_04, F_23_04, F_16_04, F_02_04]

print("Datas no banco ANTES:", list_datas_folha())
print()

for f in TODAS:
    salvar_folha_completa(
        f["data"],
        folha_cocada_por_sabor=f["cocada"],
        folha_palha_por_sabor=f["palha"],
        papelzinho_por_sabor={},  # papelzinho não tem nas fotos da folha — fica vazio
        pm_balas_doces=f["pmbd"],
    )
    print(f"  [OK] {f['data']} inserida.")

print()
print("Datas no banco DEPOIS:", list_datas_folha())
