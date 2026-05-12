"""
migrar_dados_sqlite_para_postgres.py — ETL único, idempotente, com verificação.

Roda LOCALMENTE (não no Streamlit Cloud). Lê o pcp_vo_nena.db local e replica
todas as folhas para o Postgres (Supabase) apontado por DATABASE_URL.

Pré-requisitos:
    1. Postgres alvo com schema v2 já criado (init_db do database.py refatorado).
    2. DATABASE_URL exportada no ambiente (NÃO hardcoded aqui).
    3. requirements instalados (psycopg[binary]).

Uso:
    set DATABASE_URL=postgresql://...      (Windows PowerShell: $env:DATABASE_URL = "...")
    python migrar_dados_sqlite_para_postgres.py [--dry-run]

Estratégia:
    Reaproveita database.salvar_folha_completa para cada data.
    Como salvar_folha_completa usa INSERT ... ON CONFLICT DO UPDATE, o script
    é IDEMPOTENTE: rodar duas vezes não duplica nem corrompe nada.

Verificação:
    Após a migração, conta linhas por tabela em ambos os bancos e reporta diff.
    Se houver divergência, levanta exceção (não silencia).
"""
import argparse
import os
import sqlite3
import sys

# Importa o módulo só para reaproveitar a lógica de salvamento atômico.
# IMPORTANTE: database.py precisa já estar com suporte a DATABASE_URL antes deste script rodar.
import database as db


SQLITE_PATH = os.path.join(os.path.dirname(__file__), "pcp_vo_nena.db")


def _sqlite_conn():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _strip(row, exclude=("id", "data", "sabor")):
    return {k: row[k] for k in row.keys() if k not in exclude}


def listar_datas_sqlite():
    conn = _sqlite_conn()
    rows = conn.execute("""
        SELECT DISTINCT data FROM (
            SELECT data FROM folha_cocada
            UNION SELECT data FROM folha_palha
            UNION SELECT data FROM papelzinho_joel
            UNION SELECT data FROM folha_pm_balas_doces
        ) WHERE data IS NOT NULL ORDER BY data ASC
    """).fetchall()
    conn.close()
    return [r["data"] for r in rows]


def ler_folha_completa_sqlite(data: str):
    conn = _sqlite_conn()
    cocada = {r["sabor"]: _strip(r) for r in conn.execute(
        "SELECT * FROM folha_cocada WHERE data=?", (data,)).fetchall()}
    palha = {r["sabor"]: _strip(r) for r in conn.execute(
        "SELECT * FROM folha_palha WHERE data=?", (data,)).fetchall()}
    papel = {r["sabor"]: _strip(r) for r in conn.execute(
        "SELECT * FROM papelzinho_joel WHERE data=?", (data,)).fetchall()}
    pmbd = conn.execute(
        "SELECT * FROM folha_pm_balas_doces WHERE data=?", (data,)).fetchone()
    pmbd_dict = {k: pmbd[k] for k in pmbd.keys() if k != "data"} if pmbd else {}
    conn.close()
    return cocada, palha, papel, pmbd_dict


def contar(conn, tabela):
    # Acesso por chave ('n') funciona tanto em sqlite3.Row quanto em psycopg dict_row.
    # Acesso posicional ([0]) não funciona em dict_row.
    return conn.execute(f"SELECT COUNT(*) AS n FROM {tabela}").fetchone()["n"]


def verificar_integridade():
    """Compara contagens entre SQLite e Postgres. Erra se divergir."""
    tabelas = ("folha_cocada", "folha_palha", "papelzinho_joel", "folha_pm_balas_doces")
    sqlite_conn = _sqlite_conn()
    pg_conn = db.get_conn()
    diffs = []
    for t in tabelas:
        n_sql = contar(sqlite_conn, t)
        n_pg = contar(pg_conn, t)
        marca = "✅" if n_sql == n_pg else "❌"
        print(f"  {marca} {t}: SQLite={n_sql}  Postgres={n_pg}")
        if n_sql != n_pg:
            diffs.append((t, n_sql, n_pg))
    sqlite_conn.close()
    pg_conn.close()
    if diffs:
        raise RuntimeError(f"Divergência de contagem entre backends: {diffs}")


def main():
    parser = argparse.ArgumentParser(description="Migra SQLite local → Postgres remoto.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Lista as datas que seriam migradas, sem gravar nada.")
    args = parser.parse_args()

    if not os.environ.get("DATABASE_URL"):
        print("ERRO: DATABASE_URL não está definida no ambiente.", file=sys.stderr)
        sys.exit(1)

    datas = listar_datas_sqlite()
    print(f"📋 {len(datas)} datas no SQLite local: {datas[0]} → {datas[-1]}")

    if args.dry_run:
        print("(dry-run — nenhuma operação será executada)")
        for d in datas:
            print(f"  · {d}")
        return

    # Garante schema v2 criado no Postgres (init_db é idempotente).
    print("🔧 Garantindo schema no Postgres...")
    db.init_db()

    print(f"🚚 Migrando {len(datas)} folhas...")
    erros = []
    for d in datas:
        try:
            cocada, palha, papel, pmbd = ler_folha_completa_sqlite(d)
            db.salvar_folha_completa(
                d,
                folha_cocada_por_sabor=cocada,
                folha_palha_por_sabor=palha,
                papelzinho_por_sabor=papel,
                pm_balas_doces=pmbd,
            )
            print(f"  ✅ {d}")
        except Exception as e:
            print(f"  ❌ {d}: {type(e).__name__}: {e}")
            erros.append((d, e))

    print()
    print("🔍 Verificando integridade...")
    verificar_integridade()

    if erros:
        print(f"\n⚠️  {len(erros)} datas com erro:")
        for d, e in erros:
            print(f"  · {d}: {e}")
        sys.exit(2)

    print("\n✅ Migração completa, contagens idênticas.")


if __name__ == "__main__":
    main()
