"""
leitura_folha.py — Leitura da Folha de Produção manuscrita por foto (visão do Claude).

MÓDULO PURO: não importa Streamlit. A UI (lancamento.py) consome `ler_folha()` e
`plano_preenchimento()`; o cliente da API vem de claude_assistant._get_client().

COMO FUNCIONA (decisões de 07/07/2026):
  1. GABARITO NO PROMPT — o prompt descreve o layout exato da folha física
     (blocos, sabores nas linhas, formatos nas colunas) e pede um JSON no esquema
     do formulário. Ataca o erro mais perigoso: número certo na célula errada.
  2. DUPLA LEITURA (padrão LIGADA) — duas chamadas independentes; célula em que
     as leituras divergem fica VAZIA e marcada "conferir". Se a 2ª leitura falhar,
     degrada pra leitura única (avisa).
  3. VALIDAÇÃO PELAS REGRAS DA FÁBRICA — Zero não tem 45g; palha Cookies/Limão
     não têm 50g; número fora da faixa plausível → vazio + "conferir".
  4. NUNCA SALVA — só pré-preenche o formulário; a pessoa revisa e salva. E só
     preenche célula VAZIA (nunca sobrescreve dado salvo ou digitado).
  5. Blocos SEM campo no formulário (Viradas, P/Virar — derivados), o PARÂMETRO
     do dia e as contas a lápis das margens são IGNORADOS de propósito.

API: Opus 4.8 NÃO aceita temperature/top_p/top_k (retorna 400) — não passar.
Custo: 2 leituras ≈ US$ 0,20-0,30 por folha (~R$ 1,20). Uso: 1×/dia.
"""
from __future__ import annotations

import io
import json
import re

MODELO_LEITURA = "claude-opus-4-8"
MAX_TOKENS_LEITURA = 8192
LADO_MAX_IMG = 1568  # recomendação Anthropic; reduz tokens e latência

SABORES_COCADA_JSON = ["T", "L", "B", "C", "P", "Z"]
SABORES_PALHA_JSON = ["T", "L", "CH", "CK", "LIM"]

SIGLA_PARA_SABOR_COCADA = {
    "T": "TRADICIONAL", "L": "LEITE CONDENSADO", "B": "BRIGADEIRO",
    "C": "CAFÉ", "P": "PÉ DE MOÇA", "Z": "ZERO",
}
SIGLA_PARA_SABOR_PALHA = {
    "T": "TRADICIONAL", "L": "LEITE EM PÓ", "CH": "CHURROS",
    "CK": "COOKIES", "LIM": "LIMÃO",
}

# Parâmetro (param_real_45g) fica FORA da leitura por foto de propósito: é decisão
# de planejamento da Gestão (não contagem), e converter valor→ajuste é frágil.
CAMPOS_COCADA = [
    "emb_45g", "emb_mini", "emb_pet", "emb_potes_260g", "emb_potes_605g",
    "cort1_45g", "cort1_mini", "cort1_pet",
    "ord_corte_45g", "ord_corte_mini", "ord_corte_pet",
    "ord_prod_band", "ord_prod_virada", "ord_prod_potes_260g", "ord_prod_potes_605g",
    "ord_emb_45g", "ord_emb_mini",
]
CAMPOS_PALHA = [
    "emb_50g", "emb_pet", "cont_band_palha",
    "ord_prod_band", "ord_corte_50g", "ord_corte_pet",
]
CAMPOS_PMBD = ["cnt_pm", "ord_pm", "cnt_balas", "ord_balas",
               "cnt_doces_displays", "cnt_displays_palha"]

# Faixas de plausibilidade (fábrica real; folga generosa). Fora da faixa → conferir.
_FAIXA_MAX = {
    "emb_45g": 20000, "emb_mini": 8000, "emb_pet": 5000,
    "emb_potes_260g": 800, "emb_potes_605g": 800,
    "cort1_45g": 20000, "cort1_mini": 8000, "cort1_pet": 5000,
    "ord_corte_45g": 20000, "ord_corte_mini": 8000, "ord_corte_pet": 5000,
    "ord_prod_band": 300, "ord_prod_virada": 300,
    "ord_prod_potes_260g": 800, "ord_prod_potes_605g": 800,
    "ord_emb_45g": 20000, "ord_emb_mini": 8000,
    "emb_50g": 5000, "emb_pet": 5000, "cont_band_palha": 300,
    "ord_corte_50g": 5000, "ord_corte_pet": 5000,
    "cnt_pm": 2000, "ord_pm": 50, "cnt_balas": 3000, "ord_balas": 30,
    "cnt_doces_displays": 3000, "cnt_displays_palha": 3000,
}

_ESQUELETO_JSON = json.dumps({
    "cocada": {s: {c: None for c in CAMPOS_COCADA} for s in SABORES_COCADA_JSON},
    "palha": {s: {c: None for c in CAMPOS_PALHA} for s in SABORES_PALHA_JSON},
    "pmbd": {c: None for c in CAMPOS_PMBD},
    "duvidas": [],
}, ensure_ascii=False)

PROMPT_GABARITO = f"""Você vai ler a FOLHA DE PRODUÇÃO manuscrita de uma confeitaria (foto anexa) e transcrever os números para um JSON com esquema fixo. Você conhece o layout de antemão — NÃO adivinhe estrutura; apenas copie cada número manuscrito para o campo certo.

## LAYOUT DA FOLHA (impressa, preenchida à caneta)

Sabores de COCADA nas linhas, sempre nesta ordem: T, L, B, C, P, Z.
Sabores de PALHA nas linhas: T, L, CH, CK, LIM (se houver uma linha "P" na palha, IGNORE-A — produto fora do sistema).

Blocos, de cima pra baixo:
1. "EMBALADOS" — colunas 45g e Mini por sabor de cocada → emb_45g, emb_mini.
   Ao lado, coluna "Pet" → emb_pet. Ao lado, "Potes 260g / 605g" → emb_potes_260g, emb_potes_605g.
2. No topo à direita: "PM" (número) → cnt_pm · "Doces" → cnt_doces_displays ·
   "BALAS" → cnt_balas · "Displays" → cnt_displays_palha.
3. "Palhas 50g / Pet" (topo direito) — por sabor de palha → emb_50g, emb_pet.
4. "CORTADOS" — sub-blocos 45g, Mini e Pet. REGRA: em cada sub-bloco, transcreva
   SOMENTE a coluna mais à ESQUERDA → cort1_45g, cort1_mini, cort1_pet. As demais
   colunas de cada sub-bloco: IGNORE. A coluna de números GRANDES (milhares,
   1000-7000) ao lado do 45g é o PARÂMETRO do dia — IGNORE-A por completo.
5. "VIRADAS", "P/ VIRAR" e "PALHA" (bandejas ao lado de Viradas): IGNORE por
   completo — não entram no JSON.
6. "CORTE DE COCADA" (45g / Mini / Pet) → ord_corte_45g, ord_corte_mini, ord_corte_pet.
7. "Produção / Virada" → ord_prod_band, ord_prod_virada. "Potes 260g / 605g"
   (bloco de ordem, meio da folha) → ord_prod_potes_260g, ord_prod_potes_605g.
8. "EMBALAGEM" (45g / Mini) → ord_emb_45g, ord_emb_mini.
9. "PRODUÇÃO PALHA" → ord_prod_band (da palha). "CORTE PALHA" (50g / Pet) →
   ord_corte_50g, ord_corte_pet.
10. Rodapé "Balas / PM / Amanhã": Balas → ord_balas · PM → ord_pm · "Amanhã": IGNORE.

## REGRAS INVIOLÁVEIS
- Zero (Z) NÃO TEM 45g: emb_45g, cort1_45g, ord_corte_45g e ord_emb_45g do Z são
  SEMPRE null, mesmo que pareça haver algo escrito.
- Palha CK e LIM NÃO TÊM 50g: emb_50g e ord_corte_50g delas são SEMPRE null.
- IGNORE tudo FORA das grades impressas: contas a lápis nas margens e no rodapé,
  números de referência na borda esquerda (5200, 2600, 1300...), círculos.
- Célula em branco → null. NUNCA escreva 0 no lugar de vazio.
- NÚMEROS são INTEIROS. Um ponto de milhar (ex.: "1.160") deve ser transcrito
  SEM o ponto, como 1160 — nunca como 1.16.
- Se um número estiver borrado, rasurado, emendado ou você tiver QUALQUER dúvida
  de leitura, transcreva seu melhor palpite E acrescente uma entrada em
  "duvidas": {{"bloco": "cocada|palha|pmbd", "sabor": "T" (ou null p/ pmbd),
  "campo": "...", "motivo": "curto"}}. Na dúvida entre dois dígitos, declare a dúvida.
- Não invente valor que não está na foto.

## SAÍDA
Responda APENAS com o JSON (sem texto antes/depois, sem markdown), exatamente
neste esquema (null onde vazio/não se aplica):
{_ESQUELETO_JSON}"""


# ── Imagem ────────────────────────────────────────────────────────────────────
def _media_por_assinatura(dados: bytes) -> str:
    if dados[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    return "image/jpeg"


def preparar_imagem(dados: bytes) -> tuple[str, bytes]:
    """Aplica rotação EXIF (foto de celular vem girada), achata transparência sobre
    fundo BRANCO (senão o PNG com alfa vira fundo preto e apaga a folha),
    redimensiona pro lado máximo e converte pra JPEG. Sem Pillow, devolve o
    original com o media_type correto pela assinatura dos bytes."""
    try:
        from PIL import Image, ImageOps
        img = Image.open(io.BytesIO(dados))
        img = ImageOps.exif_transpose(img)  # respeita a orientação da câmera
        if img.mode in ("RGBA", "LA", "P"):
            rgba = img.convert("RGBA")
            fundo = Image.new("RGB", rgba.size, (255, 255, 255))
            fundo.paste(rgba, mask=rgba.split()[-1])
            img = fundo
        else:
            img = img.convert("RGB")
        maior = max(img.size)
        if maior > LADO_MAX_IMG:
            fator = LADO_MAX_IMG / maior
            img = img.resize((max(1, int(img.width * fator)), max(1, int(img.height * fator))))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=88)
        return "image/jpeg", buf.getvalue()
    except Exception:
        return _media_por_assinatura(dados), dados


def _blocos_imagem(fotos: list[bytes]) -> list[dict]:
    import base64
    blocos = []
    for dados in fotos:
        media, corpo = preparar_imagem(dados)
        blocos.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media,
                       "data": base64.b64encode(corpo).decode("ascii")},
        })
    return blocos


# ── Chamada ao modelo ─────────────────────────────────────────────────────────
def _extrair_json(texto: str) -> dict:
    """Extrai o primeiro objeto JSON balanceado (ignora texto/comentário depois)."""
    texto = texto.strip()
    i = texto.find("{")
    if i < 0:
        raise ValueError("a resposta do modelo não trouxe JSON")
    try:
        obj, _ = json.JSONDecoder().raw_decode(texto[i:])
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON malformado na resposta: {e}")
    return obj


def _uma_leitura(fotos: list[bytes], modelo: str) -> tuple[dict, dict]:
    """Uma passada de leitura. Retorna (dados, uso_de_tokens). NÃO passa
    temperature/top_p/top_k (Opus 4.8 rejeita com HTTP 400)."""
    from claude_assistant import _get_client
    client = _get_client()
    resp = client.messages.create(
        model=modelo,
        max_tokens=MAX_TOKENS_LEITURA,
        messages=[{
            "role": "user",
            "content": _blocos_imagem(fotos) + [{"type": "text", "text": PROMPT_GABARITO}],
        }],
    )
    if getattr(resp, "stop_reason", None) == "max_tokens":
        raise ValueError("resposta truncada (limite de tokens) — tente menos fotos por vez")
    texto = "".join(b.text for b in resp.content if hasattr(b, "text"))
    uso = {
        "input": getattr(resp.usage, "input_tokens", 0),
        "output": getattr(resp.usage, "output_tokens", 0),
    }
    return _extrair_json(texto), uso


def _como_int(v):
    """Normaliza valor lido: int >= 0 ou None. Rejeita float não-inteiro (evita
    '1.160'→1.16→1) e limpa separador de milhar de strings ('1.160'→1160)."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v if v >= 0 else None
    if isinstance(v, float):
        return int(v) if (v.is_integer() and v >= 0) else None
    if isinstance(v, str):
        s = re.sub(r"[.\s ,]", "", v.strip())
        return int(s) if s.isdigit() else None
    return None


def _iter_celulas():
    for s in SABORES_COCADA_JSON:
        for c in CAMPOS_COCADA:
            yield "cocada", s, c
    for s in SABORES_PALHA_JSON:
        for c in CAMPOS_PALHA:
            yield "palha", s, c
    for c in CAMPOS_PMBD:
        yield "pmbd", None, c


def _valor(dados: dict, bloco: str, sabor, campo):
    try:
        if bloco == "pmbd":
            return _como_int(dados.get("pmbd", {}).get(campo))
        return _como_int(dados.get(bloco, {}).get(sabor, {}).get(campo))
    except AttributeError:
        return None


def _proibida(bloco: str, sabor, campo: str) -> bool:
    """Células que NÃO existem na fábrica (regra dura, descarte silencioso)."""
    if bloco == "cocada" and sabor == "Z" and campo in (
            "emb_45g", "cort1_45g", "ord_corte_45g", "ord_emb_45g"):
        return True
    if bloco == "palha" and sabor in ("CK", "LIM") and campo in ("emb_50g", "ord_corte_50g"):
        return True
    return False


def ler_folha(fotos: list[bytes], modelo: str = MODELO_LEITURA,
              dupla_leitura: bool = True) -> dict:
    """Lê a folha nas fotos. Retorna:
    {
      "valores":  {"cocada": {sigla: {campo: int}}, "palha": {...}, "pmbd": {campo: int}},
      "conferir": [{"bloco","sabor","campo","motivo"}, ...],   # células amarelas
      "stats":    {"preenchidas": n, "conferir": n, "descartadas": n},
      "aviso":    str | None,   # ex.: "2ª leitura falhou — sem checagem cruzada"
      "custo_usd": float, "tokens": {"input": n, "output": n},
    }
    Fusão (dupla leitura): iguais→confia; divergem→vazio+conferir; só uma viu→
    valor+conferir; dúvida declarada→valor+conferir; fora da faixa→vazio+conferir.
    """
    l1, uso1 = _uma_leitura(fotos, modelo)
    l2, uso2 = l1, {"input": 0, "output": 0}
    aviso = None
    if dupla_leitura:
        try:
            l2, uso2 = _uma_leitura(fotos, modelo)
        except Exception:
            l2 = l1  # degrada pra leitura única
            aviso = "A segunda leitura falhou — os números não passaram pela conferência cruzada. Revise com atenção."

    duvidas = set()
    for fonte in (l1, l2):
        for d in (fonte.get("duvidas") or []):
            try:
                duvidas.add((d.get("bloco"), d.get("sabor"), d.get("campo")))
            except AttributeError:
                pass

    valores = {"cocada": {}, "palha": {}, "pmbd": {}}
    conferir = []
    n_ok = n_conf = n_desc = 0

    for bloco, sabor, campo in _iter_celulas():
        v1 = _valor(l1, bloco, sabor, campo)
        v2 = _valor(l2, bloco, sabor, campo)
        if v1 is None and v2 is None:
            continue
        if _proibida(bloco, sabor, campo):
            n_desc += 1
            continue

        motivo = None
        if v1 is not None and v2 is not None and v1 != v2:
            valor, motivo = None, f"leituras divergem ({v1} × {v2})"
        elif v1 is None or v2 is None:
            valor = v1 if v1 is not None else v2
            motivo = "só uma leitura enxergou"
        else:
            valor = v1

        if valor is not None and valor > _FAIXA_MAX.get(campo, 50000):
            motivo = f"fora da faixa plausível ({valor})"
            valor = None
        if valor is not None and (bloco, sabor, campo) in duvidas and not motivo:
            motivo = "o leitor declarou dúvida (borrão/rasura)"

        if motivo:
            conferir.append({"bloco": bloco, "sabor": sabor, "campo": campo, "motivo": motivo})
            n_conf += 1
        if valor is not None:
            n_ok += 1
            if bloco == "pmbd":
                valores["pmbd"][campo] = valor
            else:
                valores[bloco].setdefault(sabor, {})[campo] = valor

    tokens = {"input": uso1["input"] + uso2["input"],
              "output": uso1["output"] + uso2["output"]}
    try:
        from claude_assistant import estimar_custo
        custo = estimar_custo(tokens["input"], tokens["output"], 0, modelo)
    except Exception:
        custo = 0.0
    return {"valores": valores, "conferir": conferir,
            "stats": {"preenchidas": n_ok, "conferir": n_conf, "descartadas": n_desc},
            "aviso": aviso, "custo_usd": custo, "tokens": tokens}


# ── Integração com o formulário (lancamento.py) ───────────────────────────────
# campo do banco -> prefixo da key do widget no lancamento.py
_CAMPO_PARA_KEY_COCADA = {
    "emb_45g": "emb_45g", "emb_mini": "emb_mini", "emb_pet": "emb_pet",
    "emb_potes_260g": "emb_p260", "emb_potes_605g": "emb_p605",
    "cort1_45g": "cort1_45g", "cort1_mini": "cort1_mini", "cort1_pet": "cort1_pet",
    "ord_corte_45g": "ord_corte_45g", "ord_corte_mini": "ord_corte_mini",
    "ord_corte_pet": "ord_corte_pet",
    "ord_prod_band": "ord_prod_band", "ord_prod_virada": "ord_prod_virada",
    "ord_prod_potes_260g": "ord_prod_p260", "ord_prod_potes_605g": "ord_prod_p605",
    "ord_emb_45g": "ord_emb_45g", "ord_emb_mini": "ord_emb_mini",
}
_CAMPO_PARA_KEY_PALHA = {
    "emb_50g": "emb_palha_50g", "emb_pet": "emb_palha_pet",
    "cont_band_palha": "cont_band_palha", "ord_prod_band": "ord_prod_palha",
    "ord_corte_50g": "ord_corte_palha_50g", "ord_corte_pet": "ord_corte_palha_pet",
}
_CAMPO_PARA_KEY_PMBD = {
    "cnt_pm": "cnt_pm", "ord_pm": "ord_pm", "cnt_balas": "cnt_balas",
    "ord_balas": "ord_balas", "cnt_doces_displays": "cnt_doces",
    "cnt_displays_palha": "cnt_displays_palha",
}


def _key_widget(bloco: str, sabor, campo: str, data_str: str):
    if bloco == "cocada":
        pref, nome = _CAMPO_PARA_KEY_COCADA.get(campo), SIGLA_PARA_SABOR_COCADA.get(sabor, "")
    elif bloco == "palha":
        pref, nome = _CAMPO_PARA_KEY_PALHA.get(campo), SIGLA_PARA_SABOR_PALHA.get(sabor, "")
    else:
        pref, nome = _CAMPO_PARA_KEY_PMBD.get(campo), None
    if not pref:
        return None
    return f"{pref}_{nome}_{data_str}" if nome else f"{pref}_{data_str}"


def _celula_vazia_no_banco(bloco, sabor, campo, dados_cocada, dados_palha, pbd_atual) -> bool:
    if bloco == "cocada":
        return not (dados_cocada.get(SIGLA_PARA_SABOR_COCADA.get(sabor), {}) or {}).get(campo)
    if bloco == "palha":
        return not (dados_palha.get(SIGLA_PARA_SABOR_PALHA.get(sabor), {}) or {}).get(campo)
    return not (pbd_atual or {}).get(campo)


def plano_preenchimento(ocr: dict, dados_cocada: dict, dados_palha: dict,
                        pbd_atual: dict, data_str: str) -> dict:
    """Traduz a leitura em ações sobre os widgets do formulário, SÓ para células
    VAZIAS no banco (nunca sobrescreve dado salvo). Retorna:
      {"set": [(widget_key, valor), ...],   # valores lidos a aplicar
       "conferir": [widget_key, ...]}        # células a destacar em amarelo
    A UI aplica escrevendo em st.session_state[widget_key] (o único jeito que o
    Streamlit 1.56 respeita — value= é ignorado após a 1ª renderização), pulando
    ainda o que o usuário já digitou na tela."""
    vals = ocr.get("valores", {})
    conjunto_set = []
    for bloco, mapa_sabor in (("cocada", vals.get("cocada") or {}), ("palha", vals.get("palha") or {})):
        for sigla, campos in mapa_sabor.items():
            for campo, v in campos.items():
                if v is None:
                    continue
                if not _celula_vazia_no_banco(bloco, sigla, campo, dados_cocada, dados_palha, pbd_atual):
                    continue
                wk = _key_widget(bloco, sigla, campo, data_str)
                if wk:
                    conjunto_set.append((wk, v))
    for campo, v in (vals.get("pmbd") or {}).items():
        if v is None or (pbd_atual or {}).get(campo):
            continue
        wk = _key_widget("pmbd", None, campo, data_str)
        if wk:
            conjunto_set.append((wk, v))

    conferir_keys = []
    for item in ocr.get("conferir", []):
        bloco, sabor, campo = item["bloco"], item["sabor"], item["campo"]
        if not _celula_vazia_no_banco(bloco, sabor, campo, dados_cocada, dados_palha, pbd_atual):
            continue  # dado salvo é confiável — não pinta de amarelo
        wk = _key_widget(bloco, sabor, campo, data_str)
        if wk:
            conferir_keys.append(wk)
    return {"set": conjunto_set, "conferir": conferir_keys}


def css_conferir(keys: list[str]) -> str:
    """CSS que pinta de amarelo os campos 'conferir'. Keys viram classes st-key-*
    (o Streamlit troca caracteres fora de [a-zA-Z0-9_-] por '-')."""
    if not keys:
        return ""
    partes = []
    for k in keys:
        classe = re.sub(r"[^a-zA-Z0-9_-]", "-", k)
        partes.append(f'[class*="st-key-{classe}"] input')
    seletores = ",\n".join(partes)
    return (f"<style>{seletores} {{ background: #FEF9C3 !important; "
            f"border-color: #FACC15 !important; }}</style>")
