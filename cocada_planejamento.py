"""
cocada_planejamento.py — Calculadora diária de sugestão de corte e produção da cocada.

Versão v3 (24/05/2026). Cobre:
  - Corte por formato (45g, Mini, Pet) por sabor.
  - Produção de bandejas (repor o estoque-alvo de P/Virar).
  - Conversão pra tachos (1 tacho = 8 band; Zero = 3).
  - Produção de potes (260g e 605g) por sabor — repõe alvo + absorve sobra do tacho parcial.
  - Capacidade priorizada (T > L > demais) quando o teto aperta.
  - Viração calculada — sugere `ord_prod_virada` específico (não só alerta).

Diferenças vs palha:
  - Diária (não semanal).
  - 5 formatos (45g, Mini, Pet, Pote 260g, Pote 605g).
  - Parâmetros "horizonte_corte" e "horizonte_producao" distribuem a necessidade em
    N dias (em vez de fechar tudo de uma vez) — aproxima o que a Gestão faz na prática.

Princípio: o sistema SUGERE, a Gestão DECIDE.
"""
import math

SABORES = ['TRADICIONAL', 'LEITE CONDENSADO', 'BRIGADEIRO', 'CAFÉ', 'PÉ DE MOÇA', 'ZERO']
WEEKDAYS_PT = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']

REND_45G = 100
REND_MINI = 150
REND_PET = 30
REND_PET_Z = 60     # Z Pet rende o dobro

BAND_POR_TACHO = 8
BAND_POR_TACHO_Z = 3

# Estoque-alvo de P/Virar (bandejas) — CLAUDE.md seção 4
ALVO_PV_PADRAO = {
    'TRADICIONAL': 70, 'LEITE CONDENSADO': 35,
    'BRIGADEIRO': 22, 'CAFÉ': 22, 'PÉ DE MOÇA': 22, 'ZERO': 18,
}

# Estoque-alvo de POTES (Gestão, recebido 24/05/2026) — CADERNO.md seção 1.B
ALVO_POTE_260G_PADRAO = {
    'TRADICIONAL': 50, 'LEITE CONDENSADO': 50,
    'BRIGADEIRO': 20, 'CAFÉ': 15, 'PÉ DE MOÇA': 15, 'ZERO': 50,
}
ALVO_POTE_605G_PADRAO = {
    'TRADICIONAL': 20, 'LEITE CONDENSADO': 20,
    'BRIGADEIRO': 10, 'CAFÉ': 10, 'PÉ DE MOÇA': 10, 'ZERO': 20,
}

# Calendário (mais flexível na prática que a regra teórica — análise das 17 folhas):
# 45g todo dia útil (forte em Seg/Qua/Qui), Mini concentra em Qua/Ter/Sex, Pet em Ter/Sex.
DIAS_CORTE_45G = {0, 1, 2, 3, 4}
DIAS_CORTE_MINI = {1, 2, 4}        # Ter, Qua, Sex (NÃO Seg, NÃO Qui)
DIAS_CORTE_PET = {0, 1, 2, 3, 4}

# Prioridade de produção quando o teto de capacidade aperta (CADERNO 1.B).
# A ordem é do MAIS prioritário (mantém) pro MENOS prioritário (corta primeiro).
PRIORIDADE_SABOR = ['TRADICIONAL', 'LEITE CONDENSADO', 'BRIGADEIRO', 'CAFÉ', 'PÉ DE MOÇA', 'ZERO']

# Conversão de bandeja-massa em potes — aproximação calibrada contra as folhas.
# Teoricamente: bandeja pronta-corte = 5,5 kg → 21 potes 260g ou 9 potes 605g.
# Na prática observada: nem toda a "sobra" do tacho vira pote (parte vira bandeja
# extra, parte tem perda). Defaults intencionalmente CONSERVADORES — pode ser
# ajustado no parâmetro `potes_por_band_*` da função se quiser usar o teto teórico.
POTES_260G_POR_BAND = 10
POTES_605G_POR_BAND = 5

# Sabores que TIPICAMENTE viram pote quando sobra tacho parcial — análise das 17 folhas
# (CADERNO 1.B): T e Z dominam · LC eventual · B/C/P quase nunca.
# A Gestão pode override no parâmetro `sabores_com_pote_da_sobra` da função.
SABORES_COM_POTE_DA_SOBRA_PADRAO = {'TRADICIONAL', 'LEITE CONDENSADO', 'ZERO'}


def _rend_tacho(sabor):
    return BAND_POR_TACHO_Z if sabor == 'ZERO' else BAND_POR_TACHO


def priorizar_capacidade(producao_band, capacidade_tachos, prioridade=None):
    """Redistribui producao_band pra caber em capacidade_tachos, cortando dos menos prioritários.

    Retorna (producao_band_priorizada: dict, sabores_reduzidos: list).
    Sabores são reduzidos em incrementos de 1 tacho (rend bandejas por vez) até caber.
    """
    if prioridade is None:
        prioridade = PRIORIDADE_SABOR
    band = dict(producao_band)

    def tachos_total():
        return sum(math.ceil(band[s] / _rend_tacho(s)) if band[s] > 0 else 0 for s in band)

    if tachos_total() <= capacidade_tachos:
        return band, []

    reduzidos = []
    # Remove primeiro dos MENOS prioritários (final da lista).
    for s in reversed(prioridade):
        while tachos_total() > capacidade_tachos and band[s] > 0:
            rend = _rend_tacho(s)
            tachos_s = math.ceil(band[s] / rend)
            band[s] = max(0, (tachos_s - 1) * rend)
            if s not in reduzidos:
                reduzidos.append(s)
        if tachos_total() <= capacidade_tachos:
            break
    return band, reduzidos


def sobra_tacho_band(producao_band):
    """Pra cada sabor, calcula quantas bandejas de massa sobram do tacho parcial.

    Ex: ord 18 band T → ceil(18/8)=3 tachos cozidos = 24 band massa → sobra 6 band → potes.
    """
    out = {}
    for s in producao_band:
        rend = _rend_tacho(s)
        if producao_band[s] <= 0:
            out[s] = 0
        else:
            tachos = math.ceil(producao_band[s] / rend)
            out[s] = tachos * rend - producao_band[s]
    return out


def sugerir_cocada(
    emb_45g,
    emb_mini,
    emb_pet,
    joel_v,
    joel_pv,
    param_real_45g,
    param_real_mini,
    param_real_pet,
    weekday,
    estoque_pote_260g=None,
    estoque_pote_605g=None,
    cort_45g=None,
    cort_mini=None,
    cort_pet=None,
    horizonte_corte=3,
    horizonte_producao=5,
    alvo_pv=None,
    alvo_pote_260g=None,
    alvo_pote_605g=None,
    capacidade_tachos=None,
    regra_sobra_pote='completar_alvo',
    sabores_com_pote_da_sobra=None,
):
    """Computa sugestão diária de corte + produção da cocada (incluindo potes).

    cort_45g/cort_mini/cort_pet: estoque de cortados na sala da Embalagem (já cortados,
                     ainda não embalados). São subtraídos da necessidade de corte —
                     se já há cortado suficiente pra atender o param_real, não precisa
                     cortar mais hoje. Default: zeros.
    regra_sobra_pote: 'completar_alvo' (padrão — primeiro fecha gap 260g, depois 605g),
                     '260g' (tudo no 260g) ou '605g' (tudo no 605g).
    sabores_com_pote_da_sobra: conjunto de sabores onde a sobra do tacho parcial
                     vira pote. Default: T, L, Z (análise das folhas — B/C/P quase
                     nunca pedem pote).
    """
    if sabores_com_pote_da_sobra is None:
        sabores_com_pote_da_sobra = set(SABORES_COM_POTE_DA_SOBRA_PADRAO)
    if cort_45g is None:
        cort_45g = {s: 0 for s in SABORES}
    if cort_mini is None:
        cort_mini = {s: 0 for s in SABORES}
    if cort_pet is None:
        cort_pet = {s: 0 for s in SABORES}
    if alvo_pv is None:
        alvo_pv = dict(ALVO_PV_PADRAO)
    if alvo_pote_260g is None:
        alvo_pote_260g = dict(ALVO_POTE_260G_PADRAO)
    if alvo_pote_605g is None:
        alvo_pote_605g = dict(ALVO_POTE_605G_PADRAO)
    if estoque_pote_260g is None:
        estoque_pote_260g = {s: 0 for s in SABORES}
    if estoque_pote_605g is None:
        estoque_pote_605g = {s: 0 for s in SABORES}

    # 1. Corte por formato
    # need = param_real - emb - cortado (o que já está cortado na Embalagem conta como
    # "quase pronto", então reduz a necessidade de cortar mais hoje).
    corte_45g, corte_mini, corte_pet = {}, {}, {}
    for s in SABORES:
        if s != 'ZERO' and weekday in DIAS_CORTE_45G:
            need = max(0, param_real_45g.get(s, 0) - emb_45g.get(s, 0) - cort_45g.get(s, 0))
            corte_45g[s] = math.ceil(need / REND_45G / horizonte_corte) if need > 0 else 0
        else:
            corte_45g[s] = 0
        if weekday in DIAS_CORTE_MINI:
            need = max(0, param_real_mini.get(s, 0) - emb_mini.get(s, 0) - cort_mini.get(s, 0))
            corte_mini[s] = math.ceil(need / REND_MINI / horizonte_corte) if need > 0 else 0
        else:
            corte_mini[s] = 0
        if weekday in DIAS_CORTE_PET:
            rend = REND_PET_Z if s == 'ZERO' else REND_PET
            need = max(0, param_real_pet.get(s, 0) - emb_pet.get(s, 0) - cort_pet.get(s, 0))
            corte_pet[s] = math.ceil(need / rend / horizonte_corte) if need > 0 else 0
        else:
            corte_pet[s] = 0

    corte_total = {s: corte_45g[s] + corte_mini[s] + corte_pet[s] for s in SABORES}
    sobra_v = {s: joel_v.get(s, 0) - corte_total[s] for s in SABORES}

    # 2. Produção de bandejas (repor alvo P/Virar, espalhado em horizonte_producao dias)
    producao_band = {}
    for s in SABORES:
        need = max(0, alvo_pv.get(s, 0) - joel_pv.get(s, 0))
        producao_band[s] = math.ceil(need / horizonte_producao) if need > 0 else 0

    # 3. Tachos antes de priorizar
    producao_tachos = {s: math.ceil(producao_band[s] / _rend_tacho(s)) if producao_band[s] > 0 else 0 for s in SABORES}
    total_tachos_antes = sum(producao_tachos.values())

    # 4. Aplicar capacidade priorizada (T > L > demais) — v3
    if capacidade_tachos is not None and total_tachos_antes > capacidade_tachos:
        producao_band_final, sabores_reduzidos = priorizar_capacidade(producao_band, capacidade_tachos)
    else:
        producao_band_final, sabores_reduzidos = dict(producao_band), []

    producao_tachos_final = {s: math.ceil(producao_band_final[s] / _rend_tacho(s)) if producao_band_final[s] > 0 else 0 for s in SABORES}
    total_tachos = sum(producao_tachos_final.values())
    excede_capacidade = capacidade_tachos is not None and total_tachos > capacidade_tachos

    # 5. Sobra de tacho parcial → potes — v3
    # Limitada aos sabores que realmente fazem pote (default T, L, Z — observação histórica).
    sobra_band = sobra_tacho_band(producao_band_final)
    pote_260g_da_sobra, pote_605g_da_sobra = {}, {}
    for s in SABORES:
        sb = sobra_band[s] if s in sabores_com_pote_da_sobra else 0
        if sb <= 0:
            pote_260g_da_sobra[s] = 0
            pote_605g_da_sobra[s] = 0
            continue
        # Caps pelo gap remanescente — evita superprodução de pote pra estoque já alto.
        gap_260 = max(0, alvo_pote_260g.get(s, 0) - estoque_pote_260g.get(s, 0))
        gap_605 = max(0, alvo_pote_605g.get(s, 0) - estoque_pote_605g.get(s, 0))
        if regra_sobra_pote == '605g':
            pote_605g_da_sobra[s] = min(sb * POTES_605G_POR_BAND, gap_605)
            pote_260g_da_sobra[s] = 0
        elif regra_sobra_pote == '260g':
            pote_260g_da_sobra[s] = min(sb * POTES_260G_POR_BAND, gap_260)
            pote_605g_da_sobra[s] = 0
        else:  # default 'completar_alvo' — preenche 260g primeiro, sobra vai pra 605g
            potes_260_cabe = min(gap_260, sb * POTES_260G_POR_BAND)
            band_usada_260 = math.ceil(potes_260_cabe / POTES_260G_POR_BAND) if potes_260_cabe > 0 else 0
            pote_260g_da_sobra[s] = potes_260_cabe
            sobra_restante = max(0, sb - band_usada_260)
            pote_605g_da_sobra[s] = min(sobra_restante * POTES_605G_POR_BAND, gap_605)

    # 6. Potes de alvo (mesma lógica da v2) + soma com sobra
    pote_260g_alvo, pote_605g_alvo = {}, {}
    for s in SABORES:
        need260 = max(0, alvo_pote_260g.get(s, 0) - estoque_pote_260g.get(s, 0))
        pote_260g_alvo[s] = math.ceil(need260 / horizonte_producao) if need260 > 0 else 0
        need605 = max(0, alvo_pote_605g.get(s, 0) - estoque_pote_605g.get(s, 0))
        pote_605g_alvo[s] = math.ceil(need605 / horizonte_producao) if need605 > 0 else 0

    pote_260g_total = {s: pote_260g_alvo[s] + pote_260g_da_sobra[s] for s in SABORES}
    pote_605g_total = {s: pote_605g_alvo[s] + pote_605g_da_sobra[s] for s in SABORES}

    # 7. Viração calculada (v3) — quanto virar hoje pra ter o que cortar nos próximos dias
    # Aproximação: mantém viradas pra ~2 dias de corte na taxa atual.
    virada_sugerida = {}
    for s in SABORES:
        need_v = max(0, corte_total[s] * 2 - joel_v.get(s, 0))
        virada_sugerida[s] = need_v

    alerta_viracao = {s: (sobra_v[s] <= 2) for s in SABORES}

    return {
        'corte_45g': corte_45g, 'corte_mini': corte_mini, 'corte_pet': corte_pet,
        'corte_total': corte_total, 'sobra_v': sobra_v,
        # bandejas — antes e depois da priorização
        'producao_band': producao_band_final,
        'producao_band_antes_prioridade': producao_band,
        'producao_tachos': producao_tachos_final,
        'total_tachos': total_tachos,
        'total_tachos_antes': total_tachos_antes,
        'sabores_reduzidos': sabores_reduzidos,
        'excede_capacidade': excede_capacidade,
        # sobra do tacho parcial
        'sobra_band_tacho': sobra_band,
        'pote_260g_alvo': pote_260g_alvo,
        'pote_605g_alvo': pote_605g_alvo,
        'pote_260g_da_sobra': pote_260g_da_sobra,
        'pote_605g_da_sobra': pote_605g_da_sobra,
        # totais finais que a Gestão usa pra decidir
        'producao_pote_260g': pote_260g_total,
        'producao_pote_605g': pote_605g_total,
        # viração
        'virada_sugerida': virada_sugerida,
        'alerta_viracao': alerta_viracao,
    }


# Caso de validação real — segunda 11/05/2026.
EXEMPLO_11_05 = {
    'emb_45g':  {'TRADICIONAL': 3560, 'LEITE CONDENSADO': 1070, 'BRIGADEIRO': 1160, 'CAFÉ': 630, 'PÉ DE MOÇA': 870, 'ZERO': 0},
    'emb_mini': {'TRADICIONAL': 364,  'LEITE CONDENSADO': 312,  'BRIGADEIRO': 260,  'CAFÉ': 208, 'PÉ DE MOÇA': 364, 'ZERO': 380},
    'emb_pet':  {'TRADICIONAL': 32,   'LEITE CONDENSADO': 51,   'BRIGADEIRO': 100,  'CAFÉ': 76,  'PÉ DE MOÇA': 67,  'ZERO': 82},
    'joel_v':   {'TRADICIONAL': 58,   'LEITE CONDENSADO': 47,   'BRIGADEIRO': 21,   'CAFÉ': 13,  'PÉ DE MOÇA': 13,  'ZERO': 16},
    'joel_pv':  {'TRADICIONAL': 7,    'LEITE CONDENSADO': 0,    'BRIGADEIRO': 0,    'CAFÉ': 6,   'PÉ DE MOÇA': 8,   'ZERO': 0},
    'param_real_45g':  {'TRADICIONAL': 7000, 'LEITE CONDENSADO': 2600, 'BRIGADEIRO': 1300, 'CAFÉ': 1300, 'PÉ DE MOÇA': 1300, 'ZERO': 0},
    'param_real_mini': {'TRADICIONAL': 500,  'LEITE CONDENSADO': 500,  'BRIGADEIRO': 300,  'CAFÉ': 300,  'PÉ DE MOÇA': 300,  'ZERO': 2600},
    'param_real_pet':  {'TRADICIONAL': 220,  'LEITE CONDENSADO': 180,  'BRIGADEIRO': 90,   'CAFÉ': 90,   'PÉ DE MOÇA': 90,   'ZERO': 300},
    'estoque_pote_260g': {'TRADICIONAL': 0,  'LEITE CONDENSADO': 0, 'BRIGADEIRO': 0, 'CAFÉ': 0, 'PÉ DE MOÇA': 0, 'ZERO': 0},
    'estoque_pote_605g': {'TRADICIONAL': 0,  'LEITE CONDENSADO': 0, 'BRIGADEIRO': 0, 'CAFÉ': 0, 'PÉ DE MOÇA': 0, 'ZERO': 0},
    'weekday': 0,
}

ESPERADO_11_05 = {
    'corte_45g':  {'TRADICIONAL': 10, 'LEITE CONDENSADO': 5, 'BRIGADEIRO': 2, 'CAFÉ': 2, 'PÉ DE MOÇA': 2, 'ZERO': 0},
    'corte_mini': {'TRADICIONAL': 0,  'LEITE CONDENSADO': 0, 'BRIGADEIRO': 0, 'CAFÉ': 0, 'PÉ DE MOÇA': 0, 'ZERO': 0},
    'corte_pet':  {'TRADICIONAL': 3,  'LEITE CONDENSADO': 3, 'BRIGADEIRO': 0, 'CAFÉ': 0, 'PÉ DE MOÇA': 0, 'ZERO': 1},
    'producao':   {'TRADICIONAL': 18, 'LEITE CONDENSADO': 8, 'BRIGADEIRO': 0, 'CAFÉ': 8, 'PÉ DE MOÇA': 0, 'ZERO': 2},
    'pote_260g':  {'TRADICIONAL': 30, 'LEITE CONDENSADO': 0, 'BRIGADEIRO': 0, 'CAFÉ': 0, 'PÉ DE MOÇA': 0, 'ZERO': 20},
    'pote_605g':  {'TRADICIONAL': 20, 'LEITE CONDENSADO': 0, 'BRIGADEIRO': 0, 'CAFÉ': 0, 'PÉ DE MOÇA': 0, 'ZERO': 10},
}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    r = sugerir_cocada(**EXEMPLO_11_05, horizonte_corte=3, horizonte_producao=5)
    print("=== Validação 11/05/2026 (Segunda) ===\n")
    print("CORTE + PRODUÇÃO BANDEJAS:")
    print(f"{'sabor':18} | {'corte 45g':^14} | {'corte Mini':^14} | {'corte Pet':^14} | {'produção':^14}")
    print(f"{'':18} | {'sist':>5} {'Gest':>5} {'Δ':>2} | {'sist':>5} {'Gest':>5} {'Δ':>2} | {'sist':>5} {'Gest':>5} {'Δ':>2} | {'sist':>5} {'Gest':>5} {'Δ':>2}")
    print("-" * 95)
    d = {'45g': 0, 'mini': 0, 'pet': 0, 'prod': 0, 'p260': 0, 'p605': 0}
    for s in SABORES:
        c45_s, c45_g = r['corte_45g'][s], ESPERADO_11_05['corte_45g'][s]
        cmi_s, cmi_g = r['corte_mini'][s], ESPERADO_11_05['corte_mini'][s]
        cpe_s, cpe_g = r['corte_pet'][s], ESPERADO_11_05['corte_pet'][s]
        pb_s, pb_g = r['producao_band'][s], ESPERADO_11_05['producao'][s]
        d['45g'] += abs(c45_s - c45_g); d['mini'] += abs(cmi_s - cmi_g)
        d['pet'] += abs(cpe_s - cpe_g); d['prod'] += abs(pb_s - pb_g)
        print(f"  {s:16} | {c45_s:>5} {c45_g:>5} {c45_s-c45_g:>+2} | {cmi_s:>5} {cmi_g:>5} {cmi_s-cmi_g:>+2} | {cpe_s:>5} {cpe_g:>5} {cpe_s-cpe_g:>+2} | {pb_s:>5} {pb_g:>5} {pb_s-pb_g:>+2}")
    print("-" * 95)
    print(f"  Diferenças: 45g={d['45g']} · Mini={d['mini']} · Pet={d['pet']} · Produção={d['prod']}")
    print(f"  Total tachos sugerido: {r['total_tachos']}\n")
    print("POTES (estoque assumido = 0; com horizonte_producao=5):")
    print(f"{'sabor':18} | {'pote 260g':^14} | {'pote 605g':^14}")
    print(f"{'':18} | {'sist':>5} {'Gest':>5} {'Δ':>2} | {'sist':>5} {'Gest':>5} {'Δ':>2}")
    print("-" * 60)
    for s in SABORES:
        p260_s, p260_g = r['producao_pote_260g'][s], ESPERADO_11_05['pote_260g'][s]
        p605_s, p605_g = r['producao_pote_605g'][s], ESPERADO_11_05['pote_605g'][s]
        d['p260'] += abs(p260_s - p260_g); d['p605'] += abs(p605_s - p605_g)
        print(f"  {s:16} | {p260_s:>5} {p260_g:>5} {p260_s-p260_g:>+2} | {p605_s:>5} {p605_g:>5} {p605_s-p605_g:>+2}")
    print(f"  Diferenças potes: 260g={d['p260']} · 605g={d['p605']}")
    print("  (Quando a Gestão faz tacho parcial, a sobra vira pote — não está no modelo v2.)")
