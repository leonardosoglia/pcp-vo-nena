"""
importar_csv_sigee.py — Importa cadastro do Sigee Cloud pra nossa tabela `insumos`.

Lê o(s) Excel exportado(s) do Sigee e atualiza nossos 33 insumos cadastrados
com:
  - codigo_sigee (rastreabilidade)
  - custo_unitario (de PrecoCusto)
  - fornecedor (de Fornecedor Padrão)
  - estoque_atual (se vier no export, OU de arquivo separado de posição)

IDEMPOTENTE: roda múltiplas vezes sem duplicar. Usa o nosso `codigo` interno
(ex: LEITE_IN_NATURA) pra identificar.

ENTRADAS ESPERADAS:
    suprimentos_sigee/MateriasPrimas_<data>.xlsx (cadastro + saldos)
    suprimentos_sigee/Embalagens_<data>.xlsx     (embalagens)
    suprimentos_sigee/Estoque_Atual_<data>.xlsx  (se separado)

USO:
    python importar_csv_sigee.py --dry-run         # só simula
    python importar_csv_sigee.py                   # aplica de verdade
    python importar_csv_sigee.py --estoque arquivo # usa arquivo separado
                                                     pra posição de estoque
"""
import argparse
import os
import sys
from pathlib import Path

# Encoding pra Windows (cp1252) — forçar UTF-8 no stdout
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    import pandas as pd
except ImportError:
    print("Erro: pandas não instalado. Instale com: pip install pandas openpyxl")
    sys.exit(1)


# ════════════════════════════════════════════════════════════════════════════
# MAPEAMENTO DOS NOSSOS 33 INSUMOS → NOME DO PRODUTO NO SIGEE
# ════════════════════════════════════════════════════════════════════════════
# Atualizar este dicionário com os matches confirmados pela Mariana
# (ver arquivo 01_matches_para_mariana.md).
#
# Formato: 'NOSSO_CODIGO': 'Nome EXATO do produto no Sigee'
#
# Use None se Mariana ainda não decidiu / não tem match.

MATCHES_CONFIRMADOS = {
    # Matches diretos (alta confiança)
    'LEITE_IN_NATURA':       'LEITE PAST INTEGRAL SERRAMAR - SC',
    'COCO_RALADO':           'COCO RALADO FRESCO 1KG',
    'AMENDOIM':              'AMENDOIM GRANULADO 25kg',
    'CACAU_PO':              'CACAU EM PO SICÃO PCT 12KG',
    'CHOCOLATE_MEIO_AMARGO': 'CHOCO GAROTO MEIO AMARGO 5X2,1KG BR',
    'BISCOITO_MAISENA':      'BISCOITO MAIZENA MARILAN 350g',  # ⚠ preço R$ 0,01 — corrigir
    'BISCOITO_NEGRESCO':     'NEGRESCO BISCOITO RECHEADO 66X100G BR',
    'ACUCAR_CONFEITEIRO':    'AÇUCAR REF CONFEITEIRO GLAUÇÚCAR UNIÃO 20X500',
    'SORBATO':               'SORBATO DE POTASSIO KUNDA CX 25KG',
    'FERMENTO_PO':           'FERM. ROYAL 250G',
    'ADOCANTE_LOWCUCAR_STEVIA': 'LOWCUCAR ADOÇANTE CULINARIA C/ STEVIA com Stevia 1000G',

    # Match único achado
    'LIMAO_TAITI':           'LIMÃO TAITI PADRÃO - KG',
    'BICARBONATO':           'BICARBONATO DE SODIO 1KG SICILIANO',
    'MANTEIGA_SEM_SAL':      'MANTEIGA SEM SAL 0.5KG - FRIMESA  POTE DE 0.5KG - A PARTIR DE 2 POTES',
    'MEL':                   'MEL LITRO 1.450 GR',

    # Pendentes Mariana confirmar — múltiplas opções
    'LEITE_CONDENSADO':      None,  # ☐ Mariana escolhe entre 5
    'CREME_DE_LEITE':        None,  # ☐ Mariana escolhe entre 5
    'LEITE_NINHO':           None,
    'DOCE_DE_LEITE':         None,
    'ERITRITOL':             None,
    'XILITOL':               None,
    'CANELA_PO':             None,
    'FARINHA_TRIGO':         None,
    'PALMISTE':              None,
    'CAFE_SACHE_40G':        None,  # ☐ Mariana confirma se é sachê ou almofada

    # Não cadastrados no Sigee (precisam ser criados lá OU controle interno só)
    'ACUCAR_CRISTAL':        None,  # ⚠ provavelmente inativo no Sigee
    'ACUCAR_MASCAVO':        None,
    'ACHOCOLATADO':          None,
    'ESSENCIA_MEL':          None,
    'CRAVO_PO':              None,
    'AMACIANTE':             None,
    'SAL':                   None,
    'ETIQUETA_PALHA':        None,  # categoria EMBALAGEM (export separado)
}


# ════════════════════════════════════════════════════════════════════════════
# COLUNAS ESPERADAS NO EXPORT DO SIGEE
# ════════════════════════════════════════════════════════════════════════════
COL_NOME = 'Nome'
COL_CODIGO_SIGEE = 'Código Fornecedor Padrão'
COL_CUSTO = 'PrecoCusto'
COL_FORNECEDOR = 'Fornecedor Padrão'
COL_UNIDADE = 'EstoqueUnidade'
COL_GENERO = 'Genero'
COL_INATIVO = 'CadastroInativo'
COL_ESTOQUE_ATUAL = 'EstoqueAtual'  # Pode não existir — verificar


# ════════════════════════════════════════════════════════════════════════════
# FUNÇÕES
# ════════════════════════════════════════════════════════════════════════════
def carregar_export_sigee(caminho: str) -> pd.DataFrame:
    """Lê o Excel exportado do Sigee, filtra só matérias-primas ativas."""
    if not Path(caminho).exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    df = pd.read_excel(caminho)
    print(f"  → {len(df)} linhas lidas")
    # Filtra
    if COL_GENERO in df.columns:
        df = df[df[COL_GENERO].astype(str).str.contains('Matéria-Prima', na=False)]
    if COL_INATIVO in df.columns:
        df = df[df[COL_INATIVO].astype(str).str.upper() == 'NÃO']
    print(f"  → {len(df)} matérias-primas ativas após filtro")
    return df


def buscar_produto_no_sigee(df: pd.DataFrame, nome_esperado: str) -> dict | None:
    """Acha um produto pelo nome.

    Estratégia robusta: 1) tentativa exata, 2) case-insensitive +
    whitespace normalizado (lida com espaços extras, maiúsculas/minúsculas).
    Retorna dict ou None.
    """
    # Tentativa 1: match exato
    match = df[df[COL_NOME] == nome_esperado]
    if len(match) == 0:
        # Tentativa 2: case-insensitive + remove espaços múltiplos
        import re
        def _norm(s):
            return re.sub(r'\s+', ' ', str(s).strip().upper())
        alvo_norm = _norm(nome_esperado)
        match = df[df[COL_NOME].apply(_norm) == alvo_norm]
    if len(match) == 0:
        return None
    if len(match) > 1:
        print(f"  ⚠ {len(match)} ocorrências de '{nome_esperado}' — usando a primeira")
    r = match.iloc[0]
    return {
        'nome_sigee': r.get(COL_NOME),
        'codigo_sigee': str(r.get(COL_CODIGO_SIGEE) or '').strip(),
        'custo_unitario': float(r.get(COL_CUSTO) or 0),
        'fornecedor': str(r.get(COL_FORNECEDOR) or '').split('—')[-1].strip()[:100],
        'unidade_sigee': str(r.get(COL_UNIDADE) or '').strip(),
        'estoque_atual': float(r.get(COL_ESTOQUE_ATUAL) or 0) if COL_ESTOQUE_ATUAL in df.columns else None,
    }


def atualizar_insumo_no_banco(db, codigo_nosso: str, dados_sigee: dict, dry_run: bool = False):
    """Atualiza um insumo já cadastrado com dados do Sigee. NÃO cria novos."""
    insumo = db.get_insumo_por_codigo(codigo_nosso)
    if not insumo:
        return ('not_found', None)

    # Monta payload de atualização
    payload = {}
    if dados_sigee.get('custo_unitario', 0) > 0:
        payload['custo_unitario'] = dados_sigee['custo_unitario']
    if dados_sigee.get('fornecedor'):
        payload['fornecedor'] = dados_sigee['fornecedor']
    if dados_sigee.get('estoque_atual') is not None:
        # Importante: pra atualizar estoque_atual é via movimento de ajuste,
        # não direto. Vamos chamar registrar_movimento_insumo se tiver função.
        pass
    # Adiciona código do Sigee no campo obs (até a gente ter coluna própria)
    obs_atual = insumo.get('obs', '') or ''
    sigee_tag = f"[SIGEE: {dados_sigee['nome_sigee']} (cod {dados_sigee['codigo_sigee']})]"
    if sigee_tag not in obs_atual:
        nova_obs = (obs_atual + ' ' + sigee_tag).strip() if obs_atual else sigee_tag
        payload['obs'] = nova_obs

    if not payload:
        return ('no_change', None)

    if dry_run:
        return ('would_update', payload)

    db.atualizar_insumo(insumo['id'], payload)
    return ('updated', payload)


def main():
    parser = argparse.ArgumentParser(description='Importa cadastro Sigee → nossa tabela insumos')
    parser.add_argument('--dry-run', action='store_true',
                        help='Apenas simula, não escreve no banco')
    parser.add_argument('--arquivo-materias',
                        default='suprimentos_sigee/MateriasPrimas_28_05_2026.xlsx',
                        help='Caminho do export de matérias-primas do Sigee')
    args = parser.parse_args()

    print(f"=== IMPORT SIGEE → INSUMOS {'(DRY RUN)' if args.dry_run else ''} ===\n")

    # 1. Lê o export
    print(f"1) Lendo {args.arquivo_materias}")
    try:
        df = carregar_export_sigee(args.arquivo_materias)
    except FileNotFoundError as e:
        print(f"  ❌ {e}")
        print(f"\nPra rodar, precisa:")
        print(f"  a) Mariana exportar do Sigee (ver suprimentos_sigee/02_checklist_export_sigee.md)")
        print(f"  b) Salvar o arquivo no caminho: {args.arquivo_materias}")
        sys.exit(1)

    # 2. Inicializa banco
    print(f"\n2) Conectando ao banco")
    # Bootstrap de secrets local
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
    print(f"  → conectado")

    # 3. Aplica matches
    print(f"\n3) Aplicando matches ({sum(1 for v in MATCHES_CONFIRMADOS.values() if v)} confirmados de {len(MATCHES_CONFIRMADOS)})")
    stats = {'updated': 0, 'would_update': 0, 'not_found_no_match': 0,
             'not_found_in_sigee': 0, 'no_change': 0, 'errors': []}

    for codigo_nosso, nome_sigee in MATCHES_CONFIRMADOS.items():
        if nome_sigee is None:
            stats['not_found_no_match'] += 1
            continue

        dados = buscar_produto_no_sigee(df, nome_sigee)
        if dados is None:
            stats['not_found_in_sigee'] += 1
            print(f"  ⚠ {codigo_nosso}: '{nome_sigee}' não achado no export")
            continue

        try:
            status, payload = atualizar_insumo_no_banco(db, codigo_nosso, dados, args.dry_run)
            stats[status] = stats.get(status, 0) + 1
            if status in ('updated', 'would_update'):
                preco = payload.get('custo_unitario', '—')
                forn = payload.get('fornecedor', '—')[:30]
                print(f"  ✓ {codigo_nosso}: R$ {preco} · {forn}")
        except Exception as e:
            stats['errors'].append(f"{codigo_nosso}: {e}")
            print(f"  ❌ {codigo_nosso}: {e}")

    # 4. Relatório final
    print(f"\n=== RESUMO ===")
    print(f"  Atualizados:                {stats.get('updated', 0)}")
    print(f"  Seriam atualizados (dry):   {stats.get('would_update', 0)}")
    print(f"  Sem mudança:                {stats.get('no_change', 0)}")
    print(f"  Sem match na MATCHES_CONFIRMADOS: {stats['not_found_no_match']}")
    print(f"  Match definido mas não achado no Excel: {stats['not_found_in_sigee']}")
    print(f"  Erros:                      {len(stats['errors'])}")
    if stats['errors']:
        print(f"\nErros detalhados:")
        for e in stats['errors']:
            print(f"  • {e}")

    if args.dry_run:
        print(f"\n💡 Foi dry run. Pra aplicar: python importar_csv_sigee.py")


if __name__ == '__main__':
    main()
