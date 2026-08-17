import pandas as pd

file_path = 'data/raw/dicionario-vigitel-2006-2024.xlsx'

print("=== Etapa 0.3: Mapeamento de Variáveis de Interesse ===")
try:
    # Lendo a aba de Variáveis, sem header inicial
    df = pd.read_excel(file_path, sheet_name='Variáveis_Vigitel', header=None)
    
    # Sete o nome das colunas fixas manualmente para evitar problemas com os espaços extras do STATA
    headers = ['Variable name', 'storage type', 'display format', 'value label', 'Variable label', 'Código', 'Label']
    df = df.iloc[3:].reset_index(drop=True)
    df.columns = headers
    
    # Preenchendo os NaNs para baixo nas colunas de definição da variável
    cols_to_ffill = ['Variable name', 'storage type', 'display format', 'value label', 'Variable label']
    df[cols_to_ffill] = df[cols_to_ffill].ffill()
    
    # Lista de palavras-chave baseadas no PDF da OMS/Vigitel para buscarmos no "Variable label" ou "Variable name"
    keywords = [
        'peso', 'altura', 'idade', 'sexo', 'escolaridade', 'estudo', 'cor', 'raça', # sociodemográficas
        'atividade física', 'exercício', 'esporte', 'caminhada', 'bicicleta', 'esforço', 'faxina', 'sedentário', 'tv', 'tela', 'computador', # atividade e sedentarismo
        'pesorake', 'peso rake' # pesos estatísticos
    ]
    
    # Convertendo os labels para lower case para busca
    df['Variable label lower'] = df['Variable label'].astype(str).str.lower()
    df['Variable name lower'] = df['Variable name'].astype(str).str.lower()
    
    # Criando uma regex com as palavras-chave
    pattern = '|'.join(keywords)
    
    # Filtrando as variáveis que dão match no nome ou no label
    df_filtered = df[(df['Variable label lower'].str.contains(pattern)) | (df['Variable name lower'].str.contains(pattern))]
    
    # Extraindo apenas as variáveis únicas de interesse
    variaveis_interesse = df_filtered[['Variable name', 'Variable label']].drop_duplicates()
    
    print(f"\nEncontramos {len(variaveis_interesse)} variáveis potenciais relacionadas à Atividade Física, Sedentarismo e Perfil:")
    
    # Formatando para exibir de forma legível
    for idx, row in variaveis_interesse.iterrows():
        print(f"[{row['Variable name']}] -> {row['Variable label']}")
        
except Exception as e:
    print(f"Erro: {e}")
