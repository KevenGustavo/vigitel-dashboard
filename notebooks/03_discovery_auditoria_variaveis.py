"""
Script de Auditoria Completa da Etapa 0
Objetivo: Cruzar TODAS as variáveis do dicionário VIGITEL com o nosso contrato De-Para
e identificar variáveis que possam ter escapado da filtragem inicial.
"""
import pandas as pd

file_path = 'data/raw/dicionario-vigitel-2006-2024.xlsx'

# ============================================================
# 1. Ler e parsear o dicionário completo (aba Variáveis_Vigitel)
# ============================================================
df = pd.read_excel(file_path, sheet_name='Variáveis_Vigitel', header=None)
headers = ['Variable name', 'storage type', 'display format', 'value label', 'Variable label', 'Código', 'Label']
df = df.iloc[3:].reset_index(drop=True)
df.columns = headers

cols_to_ffill = ['Variable name', 'storage type', 'display format', 'value label', 'Variable label']
df[cols_to_ffill] = df[cols_to_ffill].ffill()

todas_variaveis = df[['Variable name', 'Variable label']].drop_duplicates().reset_index(drop=True)

print("=" * 80)
print(f"TOTAL DE VARIÁVEIS ÚNICAS NO DICIONÁRIO: {len(todas_variaveis)}")
print("=" * 80)

# ============================================================
# 2. Listar TODAS as variáveis do dicionário
# ============================================================
print("\n--- LISTA COMPLETA DE VARIÁVEIS DO DICIONÁRIO ---\n")
for idx, row in todas_variaveis.iterrows():
    print(f"  [{row['Variable name'].strip():25s}] -> {row['Variable label']}")

# ============================================================
# 3. Busca AMPLIADA - keywords muito mais abrangentes
# ============================================================
keywords_atividade_fisica = [
    'atividade', 'exercício', 'exercicio', 'esporte', 'caminhada', 'caminh',
    'bicicleta', 'esforço', 'esforco', 'faxina', 'limpeza',
    'carrega', 'corrida', 'natação', 'natacao',
    'ginástica', 'ginastica', 'musculação', 'musculacao', 'futebol',
    'dança', 'danca', 'academia', 'alongamento', 'ioga', 'yoga',
    'pedala', 'pedal',
    'a pe', 'a pé',
    'lazer', 'tempo livre',
    'insuficiente', 'inativ',
    'pratica', 'prática',
]

keywords_sedentarismo = [
    'sedent', ' tv', 'televisão', 'televisao', 'tela',
    'computador', 'tablet', 'celular', 'smartphone',
    'sentad', 'deitad', 'tempo de tela',
    'assistir', 'assiste',
]

keywords_all = keywords_atividade_fisica + keywords_sedentarismo

todas_variaveis['label_lower'] = todas_variaveis['Variable label'].astype(str).str.lower().str.strip()
todas_variaveis['name_lower'] = todas_variaveis['Variable name'].astype(str).str.lower().str.strip()

pattern = '|'.join(keywords_all)
mask = (todas_variaveis['label_lower'].str.contains(pattern, na=False)) | \
       (todas_variaveis['name_lower'].str.contains(pattern, na=False))

vars_af_sedentarismo = todas_variaveis[mask].copy()

print("\n" + "=" * 80)
print(f"VARIÁVEIS DE ATIVIDADE FÍSICA / SEDENTARISMO (busca ampliada): {len(vars_af_sedentarismo)}")
print("=" * 80)
for idx, row in vars_af_sedentarismo.iterrows():
    print(f"  [{row['Variable name'].strip():25s}] -> {row['Variable label']}")

# ============================================================
# 4. CRUZAMENTO com o contrato atual (03_contrato_dados.py)
# ============================================================
CONTRATO_ATUAL = {
    # Metadados
    'chave', 'ano', 'cidade', 'pesorake2025',
    # Perfil Sociodemográfico
    'q6', 'q7', 'q8_anos', 'q69', 'q9_i', 'q11_i',
    # Domínio 1: Lazer
    'q42', 'q43', 'q43a', 'q44', 'q45', 'q46',
    # Domínio 2: Deslocamento
    'q50', 'q51', 'q52', 'q53', 'q54',
    # Domínio 3: Doméstica
    'q55', 'q55a', 'q56', 'r149', 'r150_hh', 'r150_mm',
    # Domínio 4: Ocupacional
    'q47', 'q48', 'q49', 'r147', 'r148_hh', 'r148_mm',
    # Sedentarismo
    'q57', 'q58', 'q59', 'q59a', 'q59b', 'q59c', 'r201',
    # Indicadores Oficiais
    'af', 'ati_livre', 'ativo_livre', 'ina_livre', 'inativo',
    'atilaz', 'atiocu', 'atitrans', 'atidom',
    'q51medio', 'q54medio', 'deslocdia', 'deslocsemana',
    'atiocusemana', 'faxinasemana',
    'af3dominios', 'af3dominios_insu', 'af4dominios',
    'tv_d_3', 'tempo_tela_stv', 'tempo_tela_total',
    # Desfechos de Saúde
    'has', 'db', 'depressao',
}

vars_af_set = set(vars_af_sedentarismo['Variable name'].str.strip().tolist())

presentes = vars_af_set & {v.strip() for v in CONTRATO_ATUAL}
faltantes = vars_af_set - {v.strip() for v in CONTRATO_ATUAL}

print("\n" + "=" * 80)
print("CRUZAMENTO: Variáveis de AF/Sedentarismo x Contrato De-Para")
print("=" * 80)

print(f"\n✅ Variáveis JÁ PRESENTES no contrato ({len(presentes)}):")
for v in sorted(presentes):
    label = todas_variaveis[todas_variaveis['Variable name'].str.strip() == v]['Variable label'].iloc[0]
    print(f"    [{v:25s}] -> {label}")

print(f"\n⚠️  Variáveis FALTANTES no contrato ({len(faltantes)}):")
for v in sorted(faltantes):
    label = todas_variaveis[todas_variaveis['Variable name'].str.strip() == v]['Variable label'].iloc[0]
    print(f"    [{v:25s}] -> {label}")

# ============================================================
# 5. Verificar a aba Indicadores_Vigitel
# ============================================================
print("\n" + "=" * 80)
print("EXPLORAÇÃO DA ABA: Indicadores_Vigitel")
print("=" * 80)

df_ind = pd.read_excel(file_path, sheet_name='Indicadores_Vigitel', header=None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 80)
print(df_ind.head(30).to_string())

# ============================================================
# 6. Listar códigos de resposta das variáveis-chave de AF/Sedentarismo
#    (para entender o que significam os valores 1, 2, 777, 888, 999)
# ============================================================
variaveis_chave = ['q42', 'q44', 'q45', 'q46', 'q50', 'q53', 'q55', 'q57', 'q58', 'q59', 'q59a', 'q59b ', 'q59c ']

print("\n" + "=" * 80)
print("CÓDIGOS DE RESPOSTA DAS VARIÁVEIS-CHAVE")
print("=" * 80)

for var in variaveis_chave:
    subset = df[(df['Variable name'].str.strip() == var.strip()) & (df['Código'].notna())]
    if not subset.empty:
        print(f"\n  [{var.strip()}] - {subset['Variable label'].iloc[0]}")
        for _, row in subset.iterrows():
            print(f"      Código: {row['Código']:>6} -> {row['Label']}")
