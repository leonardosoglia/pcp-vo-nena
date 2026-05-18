"""
migrar_postgres_para_postgres.py — Migra dados de um Supabase para outro.

Uso pra migração de região (sa-east-1 -> us-east-1, 17/05/2026):

    # PowerShell (Windows):
    $env:DB_OLD_URL = "postgresql://...sa-east-1..."
    $env:DB_NEW_URL = "postgresql://...us-east-1..."
    python migrar_postgres_para_postgres.py --dry-run   # confere counts sem alterar
    python migrar_postgres_para_postgres.py             # executa migração real

Como funciona:
    1. Conecta no DB_OLD_URL (somente leitura)
    2. Inicializa schema no DB_NEW_URL via database.init_db()
    3. Pra cada tabela: TRUNCATE no destino + INSERT dos dados do origem
    4. Reseta sequências de ID pra MAX(id)+1
    5. Reporta contagens lado a lado pra você conferir

Segurança:
    - Modo --dry-run NÃO altera nada no destino, só conta
    - TRUNCATE só roda no DESTINO (NEW_URL); origem (OLD_URL) só é lida
    - Senha das URLs nunca aparece no log (mascarada)
    - Se o destino tiver dados pré-existentes (seed do init_db), são apagados
      antes do INSERT pra evitar conflito de chave duplicada
"""
import os
import sys
import argparse
import re
import psycopg
from psycopg.rows import dict_row


OLD_URL = os.environ.get("DB_OLD_URL", "").strip()
NEW_URL = os.environ.get("DB_NEW_URL", "").strip()


def _mask_url(url: str) -> str:
    """Mascara senha em URL postgres pra log seguro."""
    return re.sub(r"://([^:]+):[^@]+@", r"://\1:***@", url)


# Ordem importante: tabelas com FK referenciada devem vir ANTES das que referenciam.
# Ex: insumos antes de bom_produto/movimentos_insumo (que têm insumo_id FK).
TABELAS = [
    # Referência (seedadas pelo init_db, mas podem ter sido editadas)
    "metas_45g",
    "metas_mini_pet",
    "metas_potes",
    "parametros_pvirar_ideal",
    "conversoes",
    "estoque",
    # Folhas (mais dados, prioridade alta)
    "folha_cocada",
    "folha_palha",
    "papelzinho_joel",
    "folha_pm_balas_doces",
    # Suprimentos (em ordem de FK)
    "insumos",
    "bom_produto",
    "movimentos_insumo",
]


def _connect(url: str):
    """Conexão psycopg 3 com row_factory=dict_row + prepare_threshold=None
    (compatível com PgBouncer transaction mode do Supabase pooler)."""
    return psycopg.connect(
        url,
        row_factory=dict_row,
        prepare_threshold=None,
        autocommit=False,
    )


def _init_schema_no_destino():
    """Inicializa schema no banco destino. Importa database.py com DATABASE_URL=NEW."""
    os.environ["DATABASE_URL"] = NEW_URL
    raiz = os.path.dirname(os.path.abspath(__file__))
    if raiz not in sys.path:
        sys.path.insert(0, raiz)
    import database
    database.init_db()
    print("  ✅ Schema criado/verificado no destino.")


def _contar(conn, tabela: str) -> int:
    with conn.cursor() as c:
        try:
            c.execute(f"SELECT COUNT(*) AS n FROM {tabela}")
            row = c.fetchone()
            return int(row["n"]) if row else 0
        except Exception:
            return 0


def _copiar_tabela(tabela: str, conn_old, conn_new, dry_run: bool = False) -> tuple[int, int]:
    """Copia todos os registros de uma tabela do OLD pro NEW.

    Retorna (n_origem, n_destino_apos).
    """
    n_origem = _contar(conn_old, tabela)

    if n_origem == 0:
        # Mesmo vazio, ainda assim TRUNCATE no destino (pra apagar seed se houver)
        if not dry_run:
            with conn_new.cursor() as c:
                c.execute(f"TRUNCATE TABLE {tabela} RESTART IDENTITY CASCADE")
            conn_new.commit()
        n_destino = _contar(conn_new, tabela)
        return n_origem, n_destino

    # Lê dados do origem
    with conn_old.cursor() as c_old:
        c_old.execute(f"SELECT * FROM {tabela} ORDER BY 1")
        rows = c_old.fetchall()

    if dry_run:
        return n_origem, 0  # NÃO mexe no destino

    cols = list(rows[0].keys())
    placeholders = ", ".join(["%s"] * len(cols))
    cols_str = ", ".join(f'"{c}"' for c in cols)

    # Se a tabela tem coluna 'id' (que provavelmente é GENERATED ALWAYS AS IDENTITY
    # quando criada por database.py em Postgres), precisa de OVERRIDING SYSTEM VALUE
    # pra permitir inserção explícita do id e preservar relacionamentos/sequences.
    if "id" in cols:
        sql = (f'INSERT INTO {tabela} ({cols_str}) '
               f'OVERRIDING SYSTEM VALUE '
               f'VALUES ({placeholders})')
    else:
        sql = f'INSERT INTO {tabela} ({cols_str}) VALUES ({placeholders})'

    # TRUNCATE + INSERT em transação atômica
    try:
        with conn_new.cursor() as c_new:
            c_new.execute(f"TRUNCATE TABLE {tabela} RESTART IDENTITY CASCADE")
            for row in rows:
                c_new.execute(sql, [row[col] for col in cols])
        conn_new.commit()
    except Exception:
        # Rollback explícito pra liberar a conexão pras próximas tabelas
        # (sem isso, todo INSERT subsequente falha com "transaction is aborted")
        conn_new.rollback()
        raise

    # Se a tabela tiver coluna 'id' do tipo IDENTITY, reseta a sequência
    # pra próximo INSERT seguir a partir de MAX(id)+1.
    if "id" in cols:
        with conn_new.cursor() as c_new:
            try:
                c_new.execute(
                    f"SELECT setval(pg_get_serial_sequence('{tabela}', 'id'), "
                    f"GREATEST((SELECT MAX(id) FROM {tabela}), 1), true)"
                )
                conn_new.commit()
            except Exception as e:
                # Tabela sem sequence (raro) — só avisa, não falha
                print(f"    ⚠️  Não rebobinei sequence de {tabela}: {e}")

    n_destino = _contar(conn_new, tabela)
    return n_origem, n_destino


def main():
    parser = argparse.ArgumentParser(description="Migrar Supabase -> Supabase")
    parser.add_argument("--dry-run", action="store_true",
                        help="Conta linhas em ambos os lados sem migrar")
    args = parser.parse_args()

    if not OLD_URL or not NEW_URL:
        print("❌ ERRO: Variáveis DB_OLD_URL e DB_NEW_URL não setadas.")
        print()
        print("No PowerShell:")
        print('  $env:DB_OLD_URL = "postgresql://...sa-east-1..."')
        print('  $env:DB_NEW_URL = "postgresql://...us-east-1..."')
        print('  python migrar_postgres_para_postgres.py')
        sys.exit(1)

    print("=" * 70)
    print("MIGRAÇÃO POSTGRES -> POSTGRES")
    print("=" * 70)
    print(f"ORIGEM: {_mask_url(OLD_URL)}")
    print(f"DESTINO: {_mask_url(NEW_URL)}")
    print(f"Modo: {'🟡 DRY-RUN (não altera nada)' if args.dry_run else '🔴 EXECUTAR (migração real)'}")
    print()

    if not args.dry_run:
        print("Passo 1: Inicializando schema no destino...")
        _init_schema_no_destino()
        print()

    print("Passo 2: Copiando dados tabela por tabela...")
    print()
    print(f"{'TABELA':<28} {'ORIGEM':>10} {'DESTINO':>10}   STATUS")
    print("-" * 70)

    conn_old = _connect(OLD_URL)
    conn_new = _connect(NEW_URL)

    total_origem = 0
    total_destino = 0
    erros = 0

    for tabela in TABELAS:
        try:
            n_o, n_d = _copiar_tabela(tabela, conn_old, conn_new, dry_run=args.dry_run)
            total_origem += n_o
            total_destino += n_d
            if args.dry_run:
                status = "🟡 (dry-run)"
            elif n_o == n_d:
                status = "✅ OK"
            else:
                status = "⚠️  Conferir"
                erros += 1
            print(f"{tabela:<28} {n_o:>10} {n_d:>10}   {status}")
        except Exception as e:
            # Mensagem de erro curta (1 linha) pra não bagunçar a tabela
            err_msg = str(e).split("\n")[0][:80]
            print(f"{tabela:<28} {'?':>10} {'?':>10}   ❌ {err_msg}")
            erros += 1
            # Garante que a conexão NEW está limpa pra próxima tabela
            try:
                conn_new.rollback()
            except Exception:
                pass

    conn_old.close()
    conn_new.close()

    print("-" * 70)
    print(f"{'TOTAL':<28} {total_origem:>10} {total_destino:>10}")
    print()

    if args.dry_run:
        print("🟡 DRY-RUN concluído. Nenhum dado foi alterado.")
        print("   Pra executar de verdade, rode SEM --dry-run.")
    elif erros == 0:
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("Próximo passo:")
        print("  1. Vá no HF Spaces: Settings > Variables and secrets")
        print("  2. Substitua a DATABASE_URL pela NOVA (us-east-1)")
        print("  3. Restart o Space pra pegar a nova conexão")
    else:
        print(f"⚠️  Migração concluída com {erros} avisos. Confere os ⚠️ acima.")
        sys.exit(2)


if __name__ == "__main__":
    main()
