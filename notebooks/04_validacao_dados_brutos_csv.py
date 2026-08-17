"""
Exploração e validação dos dados brutos do CSV contra o contrato De-Para.
Versão otimizada: lê apenas o header para cruzamento de colunas e depois
carrega somente as colunas relevantes para análise de distribuição.

IMPORTANTE: O CSV oficial do VIGITEL já vem com:
1. Labels textuais aplicadas (não são apenas códigos numéricos).
2. Indicadores de atividade física e sedentarismo pré-calculados.
3. Encoding latin-1 (ISO-8859-1).
"""
import pandas as pd
import sys
import os

# Adiciona o diretório raiz ao path para podermos importar o módulo notebooks
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
contrato_module = importlib.import_module("notebooks.05_contrato_dados_final")
SCHEMA_BRONZE_TO_SILVER = contrato_module.SCHEMA_BRONZE_TO_SILVER

CSV_PATH = "data/raw/vigitel-2006-2024-peso-rake.csv"
ENCODING = "latin-1"

print("=" * 80)
print("PARTE 1: CRUZAMENTO DE COLUNAS (header-only)")
print("=" * 80)

# Leitura rápida: apenas o header
try:
    header_df = pd.read_csv(CSV_PATH, encoding=ENCODING, nrows=0)
except FileNotFoundError:
    print(f"ERRO: Arquivo CSV não encontrado em {CSV_PATH}")
    sys.exit(1)

colunas_csv = set(header_df.columns.tolist())
colunas_contrato = set(SCHEMA_BRONZE_TO_SILVER.keys())

print(f"Colunas no CSV: {len(colunas_csv)}")
print(f"Colunas no contrato: {len(colunas_contrato)}")

presentes = colunas_contrato & colunas_csv
faltantes = colunas_contrato - colunas_csv

print(f"\n✅ Presentes: {len(presentes)}/{len(colunas_contrato)}")
if faltantes:
    print(f"🔴 AUSENTES NO CSV:")
    for c in sorted(faltantes):
        print(f"    - {c} ({SCHEMA_BRONZE_TO_SILVER[c]})")
else:
    print("✅ Todas as colunas do contrato existem no CSV.")

# -- PARTE 2: Carga seletiva para análise de distribuição --
print(f"\n{'=' * 80}")
print("PARTE 2: DISTRIBUIÇÕES (carga seletiva)")
print("=" * 80)

df = pd.read_csv(CSV_PATH, encoding=ENCODING, usecols=list(presentes), low_memory=False)
print(f"Linhas carregadas: {len(df):,}")

# Série temporal
print(f"\n--- Série Temporal ---")
for ano, count in df['ano'].value_counts().sort_index().items():
    print(f"    {ano}: {count:>7,}")

# Distribuições das variáveis do contrato
print(f"\n--- Variáveis do Contrato ---")
for col in sorted(presentes):
    dtype = df[col].dtype
    nulos = df[col].isna().sum()
    pct_nulo = (nulos / len(df)) * 100
    uniques = df[col].nunique()

    print(f"\n  [{col}] -> {SCHEMA_BRONZE_TO_SILVER[col]}")
    print(f"      Tipo: {dtype} | Nulos: {nulos:,} ({pct_nulo:.1f}%) | Únicos: {uniques}")

    if uniques <= 15:
        vc = df[col].value_counts(dropna=False).head(10)
        for val, count in vc.items():
            label = f"{val}" if pd.notna(val) else "NaN"
            print(f"          {label:>10} -> {count:>8,} registros")
    elif pd.api.types.is_numeric_dtype(df[col]):
        desc = df[col].describe()
        print(f"          min={desc['min']:.1f}  mean={desc['mean']:.1f}  max={desc['max']:.1f}")
