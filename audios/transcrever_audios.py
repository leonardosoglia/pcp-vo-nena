#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transcrever_audios.py
---------------------
Transcreve LOCALMENTE os audios da reuniao com a gestora usando faster-whisper
e gera um Markdown estruturado, pronto para o Claude Code ler.

Por que local (e nao um site de transcricao):
    e uma conversa interna sobre operacao/financeiro da empresa. Rodando na sua
    maquina, o audio nao sai para nenhum servico de terceiros.

Pre-requisito (rode UMA vez no terminal):
    pip install faster-whisper

Na PRIMEIRA execucao o modelo e baixado automaticamente (alguns minutos +
espaco em disco). Sua maquina tem internet liberada, entao isso funciona normal.

Como usar:
    1. Coloque este script na MESMA pasta dos audios limpos
       (audio_limpo.mp3 e audio2_limpo.mp3), ou ajuste a lista AUDIOS abaixo.
    2. Rode:  python transcrever_audios.py
    3. A transcricao sai em:  docs/transcricao_reuniao_gestora.md
"""

from pathlib import Path
from datetime import datetime
from faster_whisper import WhisperModel

# ----------------------------------------------------------------------
# CONFIGURACAO
# ----------------------------------------------------------------------
# Modelo: troque conforme o equilibrio qualidade x velocidade na CPU.
#   "small"     -> mais rapido, qualidade boa
#   "medium"    -> recomendado (bom PT-BR, velocidade aceitavel)   <== padrao
#   "large-v3"  -> melhor qualidade, porem LENTO sem GPU
MODELO = "medium"

# Audios a transcrever: (arquivo, rotulo que aparece no Markdown)
# Pode usar tambem os .wav 16k (audio_limpo_16k.wav) -> sao o formato ideal.
AUDIOS = [
    ("audio_limpo.mp3",  "Audio longo (~15 min)"),
    ("audio2_limpo.mp3", "Audio curto (~1 min)"),
]

IDIOMA = "pt"
SAIDA = Path("docs") / "transcricao_reuniao_gestora.md"
# ----------------------------------------------------------------------


def mmss(segundos: float) -> str:
    m, s = divmod(int(segundos), 60)
    return f"{m:02d}:{s:02d}"


def main() -> None:
    # int8 = mais leve/rapido em CPU sem perder muita qualidade
    print(f"Carregando modelo '{MODELO}' (na primeira vez ele e baixado)...")
    model = WhisperModel(MODELO, device="cpu", compute_type="int8")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)

    linhas = [
        "# Transcricao - Reuniao com a gestora (Doces Vo Nena)",
        "",
        f"- Gerado em: {datetime.now():%d/%m/%Y %H:%M}",
        f"- Modelo: faster-whisper `{MODELO}` (idioma: {IDIOMA})",
        "- Participantes: **Gestora** (apoia o dono na gestao) e **Leo**",
        "",
        "> Os rotulos de quem fala ainda NAO estao marcados. Use os tempos",
        "> [mm:ss] para conferir no audio e marcar **Gestora:** / **Leo:**,",
        "> ou peca ao Claude Code para inferir pelos trechos.",
        "",
    ]

    for arquivo, rotulo in AUDIOS:
        caminho = Path(arquivo)
        print(f"\nTranscrevendo: {arquivo}  ->  {rotulo}")
        linhas.append(f"## {rotulo} - `{arquivo}`")
        linhas.append("")

        if not caminho.exists():
            aviso = f"_(arquivo nao encontrado: {arquivo} - ajuste a lista AUDIOS)_"
            print("  " + aviso)
            linhas.append(aviso)
            linhas.append("")
            continue

        segments, info = model.transcribe(
            str(caminho),
            language=IDIOMA,
            vad_filter=True,   # ignora silencios
            beam_size=5,
        )
        print(f"  Duracao detectada: {mmss(info.duration)}")

        for seg in segments:
            texto = seg.text.strip()
            print(f"    [{mmss(seg.start)}] {texto}")
            linhas.append(f"- **[{mmss(seg.start)}]** {texto}")
        linhas.append("")

    # Secoes que o Claude Code vai preencher a partir da transcricao acima
    linhas += [
        "---",
        "",
        "## O que a gestora pediu  _(a preencher pelo Claude Code)_",
        "",
        "- ",
        "",
        "## Requisitos da integracao com o SIGE Cloud  _(a preencher pelo Claude Code)_",
        "",
        "- ",
        "",
        "## Perguntas em aberto / a confirmar com ela  _(a preencher pelo Claude Code)_",
        "",
        "- ",
        "",
    ]

    SAIDA.write_text("\n".join(linhas), encoding="utf-8")
    print(f"\nOK -> transcricao salva em: {SAIDA.resolve()}")
    print("Proximo passo: abra o Claude Code na pasta do projeto e rode o prompt indicado.")


if __name__ == "__main__":
    main()
