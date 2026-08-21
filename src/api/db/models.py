from sqlalchemy import MetaData, Table, Column, Integer, SmallInteger, String, Numeric, Boolean

metadata = MetaData(schema="gold")

dim_tempo = Table(
    'dim_tempo', metadata,
    Column('sk_tempo', Integer, primary_key=True),
    Column('ano_coleta', Integer),
    Column('periodo', String)
)

dim_cidade = Table(
    'dim_cidade', metadata,
    Column('sk_cidade', Integer, primary_key=True),
    Column('id_cidade', String),
    Column('nome_cidade', String)
)

dim_perfil = Table(
    'dim_perfil', metadata,
    Column('sk_perfil', Integer, primary_key=True),
    Column('sexo', String),
    Column('faixa_etaria', String),
    Column('faixa_escolaridade', String),
    Column('raca_cor', String)
)

fato_atividade_fisica = Table(
    'fato_atividade_fisica', metadata,
    Column('sk_registro', String, primary_key=True),
    Column('sk_tempo', Integer),
    Column('sk_cidade', Integer),
    Column('sk_perfil', Integer),
    Column('peso_amostral', Numeric),
    # Categóricos genuínos (Sim/Não convertidos para boolean na gold)
    Column('pratica_exercicio_lazer', Boolean),
    Column('tipo_exercicio_principal', String),
    Column('duracao_minutos_lazer', String),
    Column('deslocamento_trabalho_ativo', String),
    Column('assiste_tv', Boolean),
    Column('horas_sentado_dia', String),
    # Nível de AF (0, 1, 2)
    Column('ind_af_total', SmallInteger),
    # Contínuos de minutos
    Column('minutos_lazer_semana', Numeric),
    Column('minutos_desloc_trabalho', Numeric),
    Column('minutos_desloc_escola', Numeric),
    Column('minutos_desloc_dia', Numeric),
    Column('minutos_desloc_semana', Numeric),
    Column('minutos_ocupacional_semana', Numeric),
    Column('minutos_domestico_semana', Numeric),
    # Indicadores binários → BOOLEAN
    Column('ind_ativo_lazer', Boolean),
    Column('ind_inativo_lazer', Boolean),
    Column('ind_inativo_total', Boolean),
    Column('ind_ativo_lazer_150min', Boolean),
    Column('ind_ativo_ocupacional', Boolean),
    Column('ind_ativo_transporte', Boolean),
    Column('ind_ativo_domestico', Boolean),
    Column('ind_af_3dominios_150min', Boolean),
    Column('ind_af_insuficiente', Boolean),
    Column('ind_af_4dominios_150min', Boolean),
    Column('ind_tv_maior_3h', Boolean),
    Column('ind_tela_s_tv_maior_3h', Boolean),
    Column('ind_tela_total_maior_3h', Boolean),
    Column('ind_hipertensao', Boolean),
    Column('ind_diabetes', Boolean),
    Column('ind_depressao', Boolean),
    Column('ind_excesso_peso', Boolean),
    Column('ind_obesidade', Boolean)
)

