"""
baixar_historico.py — Aplica a baixa automática de insumos (Etapa E) em todas
as folhas já lançadas no banco, populando o histórico de consumo.

Uso:
    # Dry-run: mostra o que seria baixado em cada folha, sem mexer no banco.
    python baixar_historico.py --dry-run

    # Aplica de verdade.
    python baixar_historico.py

    # Subconjunto de datas:
    python baixar_historico.py --desde 2026-05-01 --ate 2026-05-15

Idempotente: rodar de novo NÃO duplica, porque baixar_insumos_da_folha estorna
qualquer baixa anterior antes de aplicar a nova. Use depois de mexer em receitas
(BOM) pra reaplicar com os valores atualizados.

Backend:
- Sem DATABASE_URL: usa SQLite local (pcp_vo_nena.db).
- Com DATABASE_URL: usa Postgres (mesmo backend que o app em produção).
- Bootstrap do secrets.toml: se o arquivo existir, propaga DATABASE_URL pro
  ambiente — mesma lógica do seed_bom_completa.py.
"""
import argparse
import os
import sys
from datetime import date


def _bootstrap_secrets():
    """Se .streamlit/secrets.toml tiver DATABASE_URL, propaga pro ambiente.
    Permite rodar fora do Streamlit no mesmo banco do app."""
    try:
        import tomllib
        with open(".streamlit/secrets.toml", "rb") as f:
            cfg = tomllib.load(f)
        if "DATABASE_URL" in cfg and not os.environ.get("DATABASE_URL"):
            os.environ["DATABASE_URL"] = cfg["DATABASE_URL"]
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="Não aplica baixa, só mostra o que seria feito.")
    parser.add_argument("--desde", type=str, default=None,
                        help="Data inicial (YYYY-MM-DD). Default = todas as datas.")
    parser.add_argument("--ate", type=str, default=None,
                        help="Data final (YYYY-MM-DD). Default = hoje.")
    parser.add_argument("--secrets", action="store_true",
                        help="Bootstrap .streamlit/secrets.toml pra usar banco remoto.")
    args = parser.parse_args()

    if args.secrets:
        _bootstrap_secrets()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    import database as db
    db.init_db()

    backend = "Postgres" if db.IS_POSTGRES else "SQLite local (pcp_vo_nena.db)"
    print(f"Backend: {backend}")
    print(f"Modo: {'DRY-RUN (não vai escrever)' if args.dry_run else 'APLICAR baixa de verdade'}")
    print()

    datas = sorted(db.list_datas_folha())
    if args.desde:
        datas = [d for d in datas if d >= args.desde]
    if args.ate:
        datas = [d for d in datas if d <= args.ate]

    if not datas:
        print("Nenhuma folha encontrada no intervalo. Nada a fazer.")
        return

    print(f"{len(datas)} folha(s) a processar: {datas[0]} a {datas[-1]}")
    print()

    total_movimentos = 0
    total_estornados = 0
    folhas_com_baixa = 0
    folhas_vazias = 0
    sem_bom_total: set[str] = set()
    alertas_negativos_total = 0
    erros = []

    for d in datas:
        try:
            pv = db.consumo_previsto_da_folha(d)
            n_consumos = len(pv["consumos"])
            n_sem_bom = len(pv["sem_bom"])
            ja_havia = pv["movs_anteriores"]

            if n_consumos == 0 and n_sem_bom == 0:
                # Folha sem ord_prod — pulo silencioso pra log limpo
                folhas_vazias += 1
                continue

            if args.dry_run:
                marca = f"(reaplicaria estorno de {ja_havia})" if ja_havia else ""
                print(f"  [DRY] {d}: {n_consumos} insumos · {n_sem_bom} sem BOM {marca}")
                for s in pv["sem_bom"]:
                    sem_bom_total.add(s["produto_chave"])
                continue

            r = db.baixar_insumos_da_folha(d)
            total_movimentos += len(r["movimentos"])
            total_estornados += r["estornados"]
            alertas_negativos_total += len(r["alertas_negativos"])
            for s in r["sem_bom"]:
                sem_bom_total.add(s["produto_chave"])
            if r["movimentos"]:
                folhas_com_baixa += 1
            extras = []
            if r["estornados"]:
                extras.append(f"estornou {r['estornados']}")
            if r["sem_bom"]:
                extras.append(f"{len(r['sem_bom'])} sem BOM")
            if r["alertas_negativos"]:
                extras.append(f"{len(r['alertas_negativos'])} negativos")
            extras_txt = f" ({', '.join(extras)})" if extras else ""
            print(f"  {d}: baixou {len(r['movimentos'])} insumos{extras_txt}")
        except Exception as e:
            erros.append((d, str(e)))
            print(f"  {d}: ERRO — {type(e).__name__}: {e}")

    print()
    print("=== Resumo ===")
    print(f"  Folhas processadas: {len(datas)} ({folhas_vazias} vazias, puladas)")
    if args.dry_run:
        print("  Modo dry-run — nada foi escrito no banco.")
    else:
        print(f"  Folhas com baixa aplicada: {folhas_com_baixa}")
        print(f"  Movimentos criados: {total_movimentos}")
        print(f"  Movimentos estornados (de baixas anteriores): {total_estornados}")
        print(f"  Insumos que ficaram negativos: {alertas_negativos_total}")
    if sem_bom_total:
        print(f"  Produtos SEM BOM cadastrada (ignorados): {sorted(sem_bom_total)}")
    if erros:
        print()
        print(f"  ERROS: {len(erros)}")
        for d, e in erros:
            print(f"    {d}: {e}")


if __name__ == "__main__":
    main()
