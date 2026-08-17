import pandas as pd

# Caminho para o arquivo do dicionário
file_path = 'data/raw/dicionario-vigitel-2006-2024.xlsx'

print("=== Explorando o Arquivo do Dicionário ===")
try:
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    print(f"Abas encontradas: {sheet_names}")
    
    if sheet_names:
        first_sheet = sheet_names[0]
        df = pd.read_excel(xls, sheet_name=first_sheet, header=None)
        print(f"\n--- Amostra da Aba: {first_sheet} (sem header) ---")
        pd.set_option('display.max_columns', None)
        print(df.head(20))
        
except Exception as e:
    print(f"Erro ao ler o arquivo: {e}")
