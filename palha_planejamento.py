"""
palha_planejamento.py — Calculadora de sugestão semanal de corte e produção da palha.

Algoritmo (segunda-feira) — documentado no CADERNO.md seção 1.A:

1. CORTE 50g  = ((displays_semana − estoque_displays) × composicao_display − estoque_50g_pronto) ÷ rendimento_50g
2. CORTE Pet  = (ideal_pet_semana − estoque_pet_pronto) ÷ rendimento_pet
3. CORTE TOTAL = corte_50g + corte_pet  (por sabor, em bandejas)
4. SOBRA       = estoque_bandejas − corte_total
5. PRODUÇÃO   = estoque-alvo de bandejas − sobra

`regra_arredondamento`:
- 'round' (padrão): arredondamento clássico. Ex: 1.80 → 2, 3.85 → 4.
- 'conservador': aplica threshold só no Pet (50g e produção seguem round). No Pet:
  se a parte decimal < THRESHOLD_PET_CONSERVADOR (0.81), puxa pra baixo; senão round.
  Ex: 1.80 → 1, 1.83 → 2. Calibrado com a folha real de 25/05/2026 onde a Gestão
  arredondou Pet CH=1.67 e Pet CK=1.80 pra menos, mas Pet LIM=1.83 pra mais.
- 'floor': sempre puxa pra menos (agressivo, raramente útil — mantido para debug).

Função pura — não importa Streamlit, dá pra testar isoladamente.
Princípio: o sistema SUGERE, a Gestão DECIDE.
"""
import math

THRESHOLD_PET_CONSERVADOR = 0.81


def _arredondar_conservador(valor, threshold=THRESHOLD_PET_CONSERVADOR):
    """Threshold-based round: decimal < threshold → floor; senão round normal."""
    parte_inteira = int(valor)
    decimal = valor - parte_inteira
    if decimal < threshold:
        return parte_inteira
    return parte_inteira + 1

SABORES = ["T", "L", "CH", "CK", "LIM"]
SABORES_50G = ["T", "L", "CH"]  # palha 50g só existe em T, L, CH

# Defaults — confirmados pelo Leonardo (caderno + conversa 22-23/05/2026)
IDEAL_DISPLAYS_POR_DIA = {"seg": 32, "ter": 36, "qua": 32, "qui": 32, "sex": 36}  # soma = 168
IDEAL_PET_POR_DIA_SABOR = {"T": 170, "L": 170, "CH": 70, "CK": 60, "LIM": 70}      # cada ter e cada sex
ALVO_BANDEJAS = {"T": 18, "L": 18, "CH": 9, "CK": 4, "LIM": 5}                     # buffer-alvo
COMPOSICAO_DISPLAY = {"T": 4, "L": 4, "CH": 2}                                     # 1 display = 4T + 4L + 2CH
REND_50G_POR_BANDEJA = 80   # mínimo (rende 80-90; planejamento usa o mínimo)
REND_PET_POR_BANDEJA = 30


def sugerir_palha(
    estoque_displays,
    estoque_50g,
    estoque_pet,
    estoque_bandejas,
    ideal_displays_semana=None,
    ideal_pet_semana=None,
    alvo_bandejas=None,
    composicao_display=None,
    rend_50g=REND_50G_POR_BANDEJA,
    rend_pet=REND_PET_POR_BANDEJA,
    regra_arredondamento='round',
):
    """Computa a sugestão de corte + produção da palha.

    Inputs (estoques do dia — a Gestão preenche na segunda):
      estoque_displays : int — displays de palha 50g prontos em estoque
      estoque_50g      : dict {"T":..,"L":..,"CH":..} — palhas 50g prontas (unidades)
      estoque_pet      : dict {"T":..,"L":..,"CH":..,"CK":..,"LIM":..} — Pets prontas (unidades)
      estoque_bandejas : dict por sabor — bandejas de palha em estoque

    Defaults (constantes — alteráveis):
      ideal_displays_semana : int (default 168)
      ideal_pet_semana      : dict por sabor (default = IDEAL_PET_POR_DIA_SABOR × 2, ter + sex)
      alvo_bandejas         : dict por sabor
      composicao_display    : dict {"T":4,"L":4,"CH":2}
      rend_50g, rend_pet    : palhas/Pets por bandeja

    Retorna dict com {corte_50g, corte_pet, corte_total, sobra, producao, trace}.
    """
    if ideal_displays_semana is None:
        ideal_displays_semana = sum(IDEAL_DISPLAYS_POR_DIA.values())
    if ideal_pet_semana is None:
        ideal_pet_semana = {s: IDEAL_PET_POR_DIA_SABOR[s] * 2 for s in SABORES}
    if alvo_bandejas is None:
        alvo_bandejas = dict(ALVO_BANDEJAS)
    if composicao_display is None:
        composicao_display = dict(COMPOSICAO_DISPLAY)

    # Escolhe funções de arredondamento POR FORMATO.
    # 50g: sempre round normal (Gestão raramente puxa pra menos).
    # Pet: round normal OU threshold conservador (calibrado com 25/05).
    # 'floor' permanece como modo agressivo (debug).
    if regra_arredondamento == 'floor':
        arredondar_50g = math.floor
        arredondar_pet = math.floor
    elif regra_arredondamento == 'conservador':
        arredondar_50g = round
        arredondar_pet = _arredondar_conservador
    else:  # 'round'
        arredondar_50g = round
        arredondar_pet = round

    # 1. Corte 50g
    displays_necessarios = max(0, ideal_displays_semana - estoque_displays)
    unidades_50g_necessarias = {s: displays_necessarios * composicao_display[s] for s in SABORES_50G}
    liquido_50g = {s: max(0, unidades_50g_necessarias[s] - estoque_50g.get(s, 0)) for s in SABORES_50G}
    corte_50g = {s: arredondar_50g(liquido_50g[s] / rend_50g) for s in SABORES_50G}
    frac_50g = {s: liquido_50g[s] / rend_50g for s in SABORES_50G}
    # Sabores sem 50g (CK, LIM) → 0
    for s in SABORES:
        corte_50g.setdefault(s, 0)
        frac_50g.setdefault(s, 0.0)
        liquido_50g.setdefault(s, 0)
        unidades_50g_necessarias.setdefault(s, 0)

    # 2. Corte Pet
    liquido_pet = {s: max(0, ideal_pet_semana[s] - estoque_pet.get(s, 0)) for s in SABORES}
    corte_pet = {s: arredondar_pet(liquido_pet[s] / rend_pet) for s in SABORES}
    frac_pet = {s: liquido_pet[s] / rend_pet for s in SABORES}

    # 3. Corte total
    corte_total = {s: corte_50g[s] + corte_pet[s] for s in SABORES}

    # 4. Sobra após o corte
    sobra = {s: estoque_bandejas.get(s, 0) - corte_total[s] for s in SABORES}

    # 5. Produção pra repor o estoque-alvo
    producao = {s: max(0, alvo_bandejas[s] - sobra[s]) for s in SABORES}

    return {
        "corte_50g": corte_50g,
        "corte_pet": corte_pet,
        "corte_total": corte_total,
        "sobra": sobra,
        "producao": producao,
        "trace": {
            "displays_necessarios": displays_necessarios,
            "unidades_50g_necessarias": unidades_50g_necessarias,
            "liquido_50g": liquido_50g,
            "frac_50g": frac_50g,
            "liquido_pet": liquido_pet,
            "frac_pet": frac_pet,
            "ideal_displays_semana": ideal_displays_semana,
            "ideal_pet_semana": ideal_pet_semana,
            "alvo_bandejas": alvo_bandejas,
        },
    }


# Caso real de validação — segunda 18/05/2026 (caderno do Leonardo).
EXEMPLO_VALIDACAO_18_05 = {
    "estoque_displays": 35,
    "estoque_50g": {"T": 415, "L": 379, "CH": 186},
    "estoque_pet": {"T": 241, "L": 304, "CH": 110, "CK": 90, "LIM": 96},
    "estoque_bandejas": {"T": 14, "L": 13, "CH": 6, "CK": 3, "LIM": 4},
}

# O que a Gestão decidiu à mão naquele dia (alvo da validação).
ESPERADO_18_05 = {
    "corte_total": {"T": 4, "L": 3, "CH": 2, "CK": 1, "LIM": 1},
    "producao":    {"T": 8, "L": 8, "CH": 5, "CK": 2, "LIM": 2},
}


if __name__ == "__main__":
    r = sugerir_palha(**EXEMPLO_VALIDACAO_18_05)
    print("=== Validação 18/05/2026 ===")
    print("Corte total sistema:  ", r["corte_total"])
    print("Corte total Gestão:   ", ESPERADO_18_05["corte_total"])
    print("Produção sistema:     ", r["producao"])
    print("Produção Gestão:      ", ESPERADO_18_05["producao"])
    bate_corte = r["corte_total"] == ESPERADO_18_05["corte_total"]
    bate_prod = r["producao"] == ESPERADO_18_05["producao"]
    print(f"\nCorte bate? {bate_corte} · Produção bate? {bate_prod}")
