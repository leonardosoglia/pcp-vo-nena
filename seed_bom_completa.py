"""
seed_bom_completa.py — Popula `insumos` + `bom_produto` com TODAS as receitas
conhecidas (CADERNO Bloco 5, recebidas da Gestão até 22/05/2026).

Receitas cobertas:
  - Cocada × 6 sabores (T, L, B, C, P, Z) — por TACHO (rende 8 band; Z rende 3).
    Inclui a "mistura padrão" somada ao leite: 500 ml + 15 g sal + 70 g sorbato.
  - Palha × 5 sabores (T, L, CH, CK, LIM) — por BANDEJA (1 panela = 1 bandeja).
  - Pão de Mel — por BOLO (1 bolo = 70 und = 7 displays).
  - Bala de doce de leite — por TACHO (1 tacho = 30 balas).

Conversões de "colheres" pra peso (confirmadas pelo Leonardo 26/05):
  - 1 colher sopa de sal = 15 g
  - 1 colher chá de antimofo (Sorbato) = 5 g (14 colheres por tacho cocada = 70 g)
  - 1 colher sopa de mel = ~21 g (9 colheres no PM = 189 g)
  - 1 sachê de café = 40 g

IDEMPOTENTE: usa o `codigo` único do insumo. Se rodar 2×, não duplica — pula os
já cadastrados e atualiza BOM existentes.

Princípio: o sistema é fonte da verdade. Estoque inicial = 0 em todos os insumos;
a Gestão atualiza depois (via SIGE Cloud / Etapa C ou movimento manual).
"""
from typing import Callable

# ════════════════════════════════════════════════════════════════════════════
# INSUMOS — código (único, idempotência), nome, categoria, unidade, obs
# ════════════════════════════════════════════════════════════════════════════
INSUMOS = [
    # ── Líquidos / laticínios ───────────────────────────────────────────────
    ("LEITE_IN_NATURA",       "Leite in natura",                "materia_prima", "L",  ""),
    ("LEITE_CONDENSADO",      "Leite condensado",               "materia_prima", "kg", ""),
    ("CREME_DE_LEITE",        "Creme de leite",                 "materia_prima", "kg", ""),
    ("LEITE_NINHO",           "Leite Ninho (em pó)",            "materia_prima", "kg", ""),
    ("MANTEIGA_SEM_SAL",      "Manteiga sem sal",               "materia_prima", "kg", ""),
    ("DOCE_DE_LEITE",         "Doce de leite",                  "materia_prima", "kg", ""),

    # ── Açúcares e adoçantes ───────────────────────────────────────────────
    ("ACUCAR_CRISTAL",        "Açúcar cristal",                 "materia_prima", "kg", ""),
    ("ACUCAR_CONFEITEIRO",    "Açúcar de confeiteiro",          "materia_prima", "kg", ""),
    ("ACUCAR_MASCAVO",        "Açúcar mascavo",                 "materia_prima", "kg", ""),
    ("ADOCANTE_LOWCUCAR_STEVIA",
                              "Adoçante Lowçucar Culinária c/ Stevia", "materia_prima", "kg", ""),
    ("ERITRITOL",             "Eritritol",                      "materia_prima", "kg", ""),
    ("XILITOL",               "Xilitol",                        "materia_prima", "kg", ""),
    ("MEL",                   "Mel",                            "materia_prima", "kg", "1 colher sopa ≈ 21 g"),
    ("ESSENCIA_MEL",          "Essência de mel",                "materia_prima", "kg", ""),

    # ── Coco e amendoim ────────────────────────────────────────────────────
    ("COCO_RALADO",           "Coco ralado",                    "materia_prima", "kg", ""),
    ("AMENDOIM",              "Amendoim",                       "materia_prima", "kg", ""),

    # ── Cacau / chocolate / café ───────────────────────────────────────────
    ("ACHOCOLATADO",          "Achocolatado / Cacau (Brigadeiro)", "materia_prima", "kg", ""),
    ("CACAU_PO",              "Cacau em pó (Pão de Mel)",       "materia_prima", "kg", ""),
    ("CHOCOLATE_MEIO_AMARGO", "Chocolate meio amargo",          "materia_prima", "kg", ""),
    ("CAFE_SACHE_40G",        "Café (sachê 40 g)",              "materia_prima", "und", "Cada sachê = 40 g"),

    # ── Biscoitos ──────────────────────────────────────────────────────────
    ("BISCOITO_MAISENA",      "Biscoito maisena",               "materia_prima", "kg", ""),
    ("BISCOITO_NEGRESCO",     "Biscoito Negresco",              "materia_prima", "kg", ""),

    # ── Especiarias e cítricos ─────────────────────────────────────────────
    ("CANELA_PO",             "Canela em pó",                   "materia_prima", "kg", ""),
    ("CRAVO_PO",              "Cravo em pó",                    "materia_prima", "kg", ""),
    ("LIMAO_TAITI",           "Limão taiti",                    "materia_prima", "und", ""),

    # ── Farinhas e fermentos ───────────────────────────────────────────────
    ("FARINHA_TRIGO",         "Farinha de trigo",               "materia_prima", "kg", ""),
    ("BICARBONATO",           "Bicarbonato (sódio)",            "materia_prima", "kg", ""),
    ("FERMENTO_PO",           "Fermento em pó",                 "materia_prima", "kg", ""),
    ("AMACIANTE",             "Amaciante",                      "materia_prima", "kg", ""),

    # ── Gordura ────────────────────────────────────────────────────────────
    ("PALMISTE",              "Palmiste (gordura vegetal)",     "materia_prima", "kg", ""),

    # ── Aditivos / sal ─────────────────────────────────────────────────────
    ("SAL",                   "Sal",                            "materia_prima", "kg", "1 colher sopa ≈ 15 g"),
    ("SORBATO",               "Sorbato (anti-mofo)",            "materia_prima", "kg", "1 colher chá ≈ 5 g"),

    # ── Embalagem ──────────────────────────────────────────────────────────
    ("ETIQUETA_PALHA",        "Etiqueta de palha",              "embalagem",     "und", "100 und por bandeja"),
]


# ════════════════════════════════════════════════════════════════════════════
# RECEITAS (BOM) — produto_chave: [(codigo_insumo, quantidade, unidade), ...]
#
# COCADA — por TACHO (rende 8 band; Zero rende 3). Mistura padrão SOMADA ao
# leite in natura: 500 ml de leite + 15 g sal + 70 g sorbato (14 colheres chá).
# ════════════════════════════════════════════════════════════════════════════
RECEITAS = {
    # Cocada Tradicional — coco normal
    "cocada_T_tacho": [
        ("LEITE_IN_NATURA",       19.5,  "L"),   # 19 L + 0.5 L da mistura
        ("ACUCAR_CRISTAL",         8.0,  "kg"),
        ("COCO_RALADO",            5.0,  "kg"),
        ("SAL",                    0.015,"kg"),
        ("SORBATO",                0.070,"kg"),
    ],

    # Cocada Leite Condensado — coco dobrado + LC
    "cocada_L_tacho": [
        ("LEITE_IN_NATURA",       19.5,  "L"),
        ("ACUCAR_CRISTAL",         8.0,  "kg"),
        ("COCO_RALADO",           10.0,  "kg"),
        ("LEITE_CONDENSADO",      15.0,  "kg"),
        ("SAL",                    0.015,"kg"),
        ("SORBATO",                0.070,"kg"),
    ],

    # Cocada Brigadeiro — coco normal + achocolatado
    "cocada_B_tacho": [
        ("LEITE_IN_NATURA",       19.5,  "L"),
        ("ACUCAR_CRISTAL",         8.0,  "kg"),
        ("COCO_RALADO",            5.0,  "kg"),
        ("ACHOCOLATADO",           0.500,"kg"),
        ("SAL",                    0.015,"kg"),
        ("SORBATO",                0.070,"kg"),
    ],

    # Cocada Café — coco normal + café (5 sachês de 40 g)
    "cocada_C_tacho": [
        ("LEITE_IN_NATURA",       19.5,  "L"),
        ("ACUCAR_CRISTAL",         8.0,  "kg"),
        ("COCO_RALADO",            5.0,  "kg"),
        ("CAFE_SACHE_40G",         5,    "und"),
        ("SAL",                    0.015,"kg"),
        ("SORBATO",                0.070,"kg"),
    ],

    # Cocada Pé de Moça — SEM COCO + amendoim
    "cocada_P_tacho": [
        ("LEITE_IN_NATURA",       19.5,  "L"),
        ("ACUCAR_CRISTAL",         8.0,  "kg"),
        ("AMENDOIM",               2.5,  "kg"),
        ("SAL",                    0.015,"kg"),
        ("SORBATO",                0.070,"kg"),
    ],

    # Cocada Zero — sem açúcar cristal, leite extra, adoçantes triplos
    "cocada_Z_tacho": [
        ("LEITE_IN_NATURA",       26.5,  "L"),   # 26 L + 0.5 da mistura
        ("COCO_RALADO",            6.0,  "kg"),
        ("ADOCANTE_LOWCUCAR_STEVIA", 2.0,"kg"),
        ("ERITRITOL",              2.0,  "kg"),
        ("XILITOL",                1.0,  "kg"),
        ("SAL",                    0.015,"kg"),
        ("SORBATO",                0.070,"kg"),
    ],

    # ── PALHA — por BANDEJA (1 panela = 1 bandeja) ──────────────────────────
    "palha_T_band": [
        ("LEITE_CONDENSADO",       3.820,"kg"),
        ("MANTEIGA_SEM_SAL",       0.070,"kg"),
        ("CREME_DE_LEITE",         0.130,"kg"),
        ("ACUCAR_CONFEITEIRO",     0.400,"kg"),
        ("BISCOITO_MAISENA",       1.250,"kg"),
        ("CHOCOLATE_MEIO_AMARGO",  0.750,"kg"),
        ("ETIQUETA_PALHA",       100,    "und"),
    ],
    "palha_L_band": [
        ("LEITE_CONDENSADO",       4.465,"kg"),
        ("MANTEIGA_SEM_SAL",       0.110,"kg"),
        ("CREME_DE_LEITE",         0.130,"kg"),
        ("ACUCAR_CONFEITEIRO",     0.300,"kg"),
        ("BISCOITO_MAISENA",       1.300,"kg"),
        ("LEITE_NINHO",            0.270,"kg"),
        ("ETIQUETA_PALHA",       100,    "und"),
    ],
    "palha_CH_band": [
        ("LEITE_CONDENSADO",       3.720,"kg"),
        ("MANTEIGA_SEM_SAL",       0.070,"kg"),
        ("CREME_DE_LEITE",         0.130,"kg"),
        ("ACUCAR_CONFEITEIRO",     0.400,"kg"),
        ("BISCOITO_MAISENA",       1.300,"kg"),
        ("DOCE_DE_LEITE",          1.000,"kg"),
        ("CANELA_PO",              0.064,"kg"),
        ("ETIQUETA_PALHA",       100,    "und"),
    ],
    "palha_CK_band": [
        ("LEITE_CONDENSADO",       4.465,"kg"),
        ("MANTEIGA_SEM_SAL",       0.110,"kg"),
        ("CREME_DE_LEITE",         0.130,"kg"),
        ("ACUCAR_CONFEITEIRO",     0.300,"kg"),
        ("BISCOITO_MAISENA",       0.300,"kg"),
        ("LEITE_NINHO",            0.270,"kg"),
        ("BISCOITO_NEGRESCO",      1.100,"kg"),
        ("ETIQUETA_PALHA",       100,    "und"),
    ],
    "palha_LIM_band": [
        ("LEITE_CONDENSADO",       4.500,"kg"),
        ("MANTEIGA_SEM_SAL",       0.110,"kg"),
        ("CREME_DE_LEITE",         0.130,"kg"),
        ("ACUCAR_CONFEITEIRO",     0.400,"kg"),
        ("BISCOITO_MAISENA",       1.250,"kg"),
        ("LIMAO_TAITI",            5,    "und"),
        ("ETIQUETA_PALHA",       100,    "und"),
    ],

    # ── PÃO DE MEL — por BOLO (1 bolo = 70 und = 7 displays) ────────────────
    "pm_bolo": [
        ("FARINHA_TRIGO",          0.360,"kg"),
        ("ACUCAR_MASCAVO",         0.340,"kg"),
        ("CACAU_PO",               0.160,"kg"),
        ("LEITE_IN_NATURA",        0.230,"L"),   # ≈ 1 xícara
        ("CANELA_PO",              0.003,"kg"),
        ("CRAVO_PO",               0.003,"kg"),
        ("MEL",                    0.189,"kg"),  # 9 colheres × 21 g
        ("ESSENCIA_MEL",           0.003,"kg"),
        ("PALMISTE",               0.220,"kg"),  # ≈ 1 xícara
        ("SORBATO",                0.010,"kg"),
        ("AMACIANTE",              0.020,"kg"),
        ("BICARBONATO",            0.011,"kg"),
        ("FERMENTO_PO",            0.014,"kg"),
    ],

    # ── BALA — por TACHO (1 tacho = 30 balas) ───────────────────────────────
    "bala_tacho": [
        # "Açúcar derretido 300 g + Açúcar 8,2 kg" — mesma matéria-prima, soma
        ("ACUCAR_CRISTAL",         8.5,  "kg"),
        ("LEITE_IN_NATURA",       28.0,  "L"),
        ("BICARBONATO",            0.035,"kg"),
        ("PALMISTE",               0.900,"kg"),
        ("SAL",                    0.005,"kg"),
        ("SORBATO",                0.010,"kg"),
    ],
}


# ════════════════════════════════════════════════════════════════════════════
# EXECUÇÃO
# ════════════════════════════════════════════════════════════════════════════
def executar_seed(db_module, log: Callable[[str], None] = print) -> dict:
    """Cadastra todos os insumos + linhas de BOM. Idempotente.

    Retorna dict com estatísticas:
        {'insumos_criados': N, 'insumos_existentes': M,
         'bom_linhas_inseridas': X, 'bom_linhas_atualizadas': Y,
         'erros': [str, ...]}
    """
    stats = {
        'insumos_criados': 0,
        'insumos_existentes': 0,
        'bom_linhas_inseridas': 0,
        'bom_linhas_atualizadas': 0,
        'erros': [],
    }

    # ── 1. Cadastrar insumos ────────────────────────────────────────────────
    insumo_id_por_codigo: dict[str, int] = {}
    for codigo, nome, categoria, unidade, obs in INSUMOS:
        try:
            existente = db_module.get_insumo_por_codigo(codigo)
            if existente:
                insumo_id_por_codigo[codigo] = existente['id']
                stats['insumos_existentes'] += 1
            else:
                novo_id = db_module.criar_insumo({
                    'codigo': codigo,
                    'nome': nome,
                    'categoria': categoria,
                    'unidade': unidade,
                    'obs': obs,
                    'estoque_atual': 0,
                    'ativo': 1,
                })
                insumo_id_por_codigo[codigo] = novo_id
                stats['insumos_criados'] += 1
                log(f"  [insumo] criado: {codigo} — {nome}")
        except Exception as e:
            stats['erros'].append(f"insumo {codigo}: {e}")

    # ── 2. Cadastrar/atualizar BOM ──────────────────────────────────────────
    for produto_chave, linhas in RECEITAS.items():
        for codigo_insumo, qtd, unidade in linhas:
            insumo_id = insumo_id_por_codigo.get(codigo_insumo)
            if insumo_id is None:
                stats['erros'].append(
                    f"BOM {produto_chave}: insumo {codigo_insumo} não foi criado"
                )
                continue
            try:
                # upsert_bom_linha já trata duplicação por (produto_chave, insumo_id)
                # Não temos como saber se inseriu ou atualizou só pelo retorno,
                # então conto ambos como "processado".
                db_module.upsert_bom_linha(produto_chave, insumo_id, qtd, unidade)
                stats['bom_linhas_inseridas'] += 1
            except Exception as e:
                stats['erros'].append(f"BOM {produto_chave}/{codigo_insumo}: {e}")

    log(f"Resumo: {stats['insumos_criados']} insumos novos, "
        f"{stats['insumos_existentes']} já existentes; "
        f"{stats['bom_linhas_inseridas']} linhas de BOM processadas; "
        f"{len(stats['erros'])} erros.")
    return stats


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    import os
    # Bootstrap secrets se rodar local fora do Streamlit
    try:
        import tomllib
        with open('.streamlit/secrets.toml', 'rb') as f:
            cfg = tomllib.load(f)
        if 'DATABASE_URL' in cfg:
            os.environ['DATABASE_URL'] = cfg['DATABASE_URL']
    except Exception:
        pass
    import database as db
    db.init_db()
    stats = executar_seed(db)
    print("\n=== Estatísticas finais ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
