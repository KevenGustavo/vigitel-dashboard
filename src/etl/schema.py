"""
Contrato de Dados — VIGITEL (Mapeamento de Colunas)

Define o mapeamento oficial entre os nomes originais do inquérito (ex: q59)
e os nomes padronizados utilizados nas camadas Silver e Gold do ETL.
Serve como fonte de verdade para todo o pipeline.
"""

COLUMN_MAP = {
    # ── Metadados e Ponderação Epidemiológica ─────────────────
    'chave': 'id_registro',
    'ano': 'ano_coleta',
    'cidade': 'id_cidade',
    'pesorake2025': 'peso_amostral',

    # ── Perfil Sociodemográfico e Antropométrico ──────────────
    'q6': 'idade_anos',
    'q7': 'sexo',
    'q8_anos': 'anos_estudo',
    'q69': 'raca_cor',
    'q9_i': 'peso_kg_imputado',
    'q11_i': 'altura_cm_imputado',

    # ── Domínio 1: Atividade Física no Lazer ──────────────────
    'q42': 'pratica_exercicio_lazer',
    'q43': 'tipo_exercicio_principal',
    'q43a': 'tipo_exercicio_secundario',
    'q44': 'freq_semanal_lazer',
    'q45': 'freq_dias_lazer',
    'q46': 'duracao_minutos_lazer',

    # ── Domínio 2: Atividade Física no Deslocamento ───────────
    'q50': 'deslocamento_trabalho_ativo',
    'q51': 'duracao_trajeto_trabalho',
    'q52': 'frequenta_escola',
    'q53': 'deslocamento_escola_ativo',
    'q54': 'duracao_trajeto_escola',

    # ── Domínio 3: Atividade Física Doméstica ─────────────────
    'q55': 'pratica_faxina',
    'q55a': 'ajuda_faxina',
    'q56': 'faxina_parte_pesada',
    'r149': 'freq_dias_faxina',
    'r150_hh': 'duracao_horas_faxina',
    'r150_mm': 'duracao_minutos_faxina',

    # ── Domínio 4: Atividade Física Ocupacional ───────────────
    'q47': 'trabalha_atualmente',
    'q48': 'anda_bastante_pe_trabalho',
    'q49': 'carrega_peso_trabalho',
    'r147': 'freq_dias_trabalho_fisico',
    'r148_hh': 'duracao_horas_trabalho_fisico',
    'r148_mm': 'duracao_minutos_trabalho_fisico',

    # ── Comportamento Sedentário (Tempo de Tela) ──────────────
    'q57': 'assiste_tv',
    'q58': 'freq_dias_tv',
    'q59': 'duracao_horas_tv',
    'q59a': 'duracao_horas_tv_dia',
    'q59b': 'uso_telas_tempo_livre',
    'q59c': 'duracao_telas_tempo_livre',
    'r201': 'horas_sentado_dia',

    # ── Indicadores Oficiais Pré-Calculados (VIGITEL) ─────────
    'af': 'ind_af_total',
    'ati_livre': 'minutos_lazer_semana',
    'ativo_livre': 'ind_ativo_lazer',
    'ina_livre': 'ind_inativo_lazer',
    'inativo': 'ind_inativo_total',
    'atilaz': 'ind_ativo_lazer_150min',
    'atiocu': 'ind_ativo_ocupacional',
    'atitrans': 'ind_ativo_transporte',
    'atidom': 'ind_ativo_domestico',
    'q51medio': 'minutos_desloc_trabalho',
    'q54medio': 'minutos_desloc_escola',
    'deslocdia': 'minutos_desloc_dia',
    'deslocsemana': 'minutos_desloc_semana',
    'atiocusemana': 'minutos_ocupacional_semana',
    'faxinasemana': 'minutos_domestico_semana',
    'af3dominios': 'ind_af_3dominios_150min',
    'af3dominios_insu': 'ind_af_insuficiente',
    'af4dominios': 'ind_af_4dominios_150min',
    'tv_d_3': 'ind_tv_maior_3h',
    'tempo_tela_stv': 'ind_tela_s_tv_maior_3h',
    'tempo_tela_total': 'ind_tela_total_maior_3h',

    # ── Desfechos de Saúde (Correlação com AF/Sedentarismo) ───
    'has': 'ind_hipertensao',
    'db': 'ind_diabetes',
    'depressao': 'ind_depressao',
}

# Colunas que são valores contínuos (não devem sofrer limpeza de códigos mágicos)
CONTINUOUS_COLUMNS = {
    'peso_amostral', 'idade_anos', 'anos_estudo',
    'peso_kg_imputado', 'altura_cm_imputado',
    'minutos_lazer_semana', 'minutos_desloc_trabalho', 'minutos_desloc_escola',
    'minutos_desloc_dia', 'minutos_desloc_semana',
    'minutos_ocupacional_semana', 'minutos_domestico_semana',
    'horas_sentado_dia',
}

# Códigos do inquérito que representam ausência de resposta
MAGIC_NULL_CODES = [777, 888, 999, 555, 666, '777', '888', '999', '555', '666',
                    'não quis informar', 'não lembra', 'Não quis informar', 'Não lembra']


def get_csv_columns():
    """Retorna as chaves originais do CSV para filtrar no read_csv."""
    return list(COLUMN_MAP.keys())


def get_column_rename_map():
    """Retorna o dicionário de mapeamento para df.rename(columns=...)."""
    return COLUMN_MAP.copy()
