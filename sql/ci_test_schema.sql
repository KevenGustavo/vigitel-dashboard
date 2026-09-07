-- ==============================================================================
-- VIGITEL Analytics - Script de Inicialização para Testes de Integração / CI
-- Cria os schemas da arquitetura Medalhão (bronze, silver, gold) e popula
-- estruturas representativas para permitir a execução autônoma do pytest em CI.
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- ── 1. Camada Bronze (Mock de Validação) ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS bronze.vigitel_raw (
    chave text, ano int, cidade text, pesorake2025 numeric,
    q6 int, q7 text, q8_anos text, q69 text, q9_i numeric, q11_i numeric,
    q42 text, q43 text, q43a text, q44 text, q45 text, q46 text,
    q50 text, q51 text, q52 text, q53 text, q54 text,
    q55 text, q55a text, q56 text, r149 text, r150_hh text, r150_mm text,
    q47 text, q48 text, q49 text, r147 text, r148_hh text, r148_mm text,
    q57 text, q58 text, q59 text, q59a text, q59b text, q59c text, r201 text,
    af smallint, ati_livre numeric, ativo_livre boolean, ina_livre boolean, inativo boolean,
    atilaz boolean, atiocu boolean, atitrans boolean, atidom boolean,
    q51medio numeric, q54medio numeric, deslocdia numeric, deslocsemana numeric,
    atiocusemana numeric, faxinasemana numeric,
    af3dominios boolean, af3dominios_insu boolean, af4dominios boolean,
    tv_d_3 boolean, tempo_tela_stv boolean, tempo_tela_total boolean,
    has boolean, db boolean, depressao boolean
);

INSERT INTO bronze.vigitel_raw (chave, ano, cidade, pesorake2025) VALUES
    ('MOCK_BRONZE_001', 2022, 'São Paulo', 1.0),
    ('MOCK_BRONZE_002', 2023, 'São Paulo', 1.0),
    ('MOCK_BRONZE_003', 2024, 'São Paulo', 1.0)
ON CONFLICT DO NOTHING;

-- ── 2. Camada Silver (Mock de Validação) ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS silver.vigitel_cleansed (
    sk_registro text PRIMARY KEY,
    id_registro text,
    ano_coleta int,
    nome_cidade text,
    peso_amostral numeric,
    idade_anos int,
    sexo text,
    anos_estudo text,
    raca_cor text,
    pratica_exercicio_lazer boolean
);

INSERT INTO silver.vigitel_cleansed (sk_registro, id_registro, ano_coleta, nome_cidade, peso_amostral, idade_anos, sexo, anos_estudo, raca_cor, pratica_exercicio_lazer) VALUES
    ('MOCK_SILVER_001', 'MOCK_001', 2022, 'São Paulo', 1.0, 25, 'Masculino', '12+ anos', 'Branca', true),
    ('MOCK_SILVER_002', 'MOCK_002', 2023, 'São Paulo', 1.0, 28, 'Feminino', '9 a 11 anos', 'Parda', true),
    ('MOCK_SILVER_003', 'MOCK_003', 2024, 'São Paulo', 1.0, 30, 'Masculino', '12+ anos', 'Branca', true)
ON CONFLICT DO NOTHING;

-- ── 3. Camada Gold: Dimensão Tempo ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gold.dim_tempo (
    sk_tempo int PRIMARY KEY,
    ano_coleta int NOT NULL,
    periodo text NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_dim_tempo_ano ON gold.dim_tempo (ano_coleta);

INSERT INTO gold.dim_tempo (sk_tempo, ano_coleta, periodo) VALUES
(1, 2022, '2020+'),
(2, 2023, '2020+'),
(3, 2024, '2020+')
ON CONFLICT (sk_tempo) DO NOTHING;

-- ── 4. Camada Gold: Dimensão Cidade (Todas as 27 Capitais Brasileiras) ────────
CREATE TABLE IF NOT EXISTS gold.dim_cidade (
    sk_cidade int PRIMARY KEY,
    nome_cidade text NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_dim_cidade_nome ON gold.dim_cidade (nome_cidade);

INSERT INTO gold.dim_cidade (sk_cidade, nome_cidade) VALUES
(1, 'Aracaju'), (2, 'Belém'), (3, 'Belo Horizonte'), (4, 'Boa Vista'), (5, 'Brasília'),
(6, 'Campo Grande'), (7, 'Cuiabá'), (8, 'Curitiba'), (9, 'Florianópolis'), (10, 'Fortaleza'),
(11, 'Goiânia'), (12, 'João Pessoa'), (13, 'Macapá'), (14, 'Maceió'), (15, 'Manaus'),
(16, 'Natal'), (17, 'Palmas'), (18, 'Porto Alegre'), (19, 'Porto Velho'), (20, 'Recife'),
(21, 'Rio Branco'), (22, 'Rio de Janeiro'), (23, 'Salvador'), (24, 'São Luís'),
(25, 'São Paulo'), (26, 'Teresina'), (27, 'Vitória')
ON CONFLICT (sk_cidade) DO NOTHING;

-- ── 5. Camada Gold: Dimensão Perfil Sociodemográfico ─────────────────────────
CREATE TABLE IF NOT EXISTS gold.dim_perfil (
    sk_perfil int PRIMARY KEY,
    sexo text NOT NULL,
    faixa_etaria text NOT NULL,
    faixa_escolaridade text NOT NULL,
    raca_cor text NOT NULL
);

INSERT INTO gold.dim_perfil (sk_perfil, sexo, faixa_etaria, faixa_escolaridade, raca_cor) VALUES
(1, 'Masculino', '18-24', '0 a 8 anos', 'Branca'),
(2, 'Feminino', '25-34', '9 a 11 anos', 'Parda'),
(3, 'Masculino', '35-44', '12 anos ou mais', 'Preta'),
(4, 'Feminino', '45-54', '0 a 8 anos', 'Amarela'),
(5, 'Masculino', '55-64', '9 a 11 anos', 'Indígena'),
(6, 'Feminino', '65+', '12 anos ou mais', 'Branca')
ON CONFLICT (sk_perfil) DO NOTHING;

-- ── 6. Camada Gold: Tabela Fato Atividade Física & Desfechos ──────────────────
CREATE TABLE IF NOT EXISTS gold.fato_atividade_fisica (
    sk_registro text PRIMARY KEY,
    sk_tempo int NOT NULL,
    sk_cidade int NOT NULL,
    sk_perfil int NOT NULL,
    peso_amostral numeric NOT NULL DEFAULT 1.0,
    pratica_exercicio_lazer boolean,
    tipo_exercicio_principal text,
    duracao_minutos_lazer text,
    deslocamento_trabalho_ativo text,
    assiste_tv boolean,
    horas_sentado_dia text,
    ind_af_total smallint,
    minutos_lazer_semana numeric,
    minutos_desloc_trabalho numeric,
    minutos_desloc_escola numeric,
    minutos_desloc_dia numeric,
    minutos_desloc_semana numeric,
    minutos_ocupacional_semana numeric,
    minutos_domestico_semana numeric,
    ind_ativo_lazer boolean,
    ind_inativo_lazer boolean,
    ind_inativo_total boolean,
    ind_ativo_lazer_150min boolean,
    ind_ativo_ocupacional boolean,
    ind_ativo_transporte boolean,
    ind_ativo_domestico boolean,
    ind_af_3dominios_150min boolean,
    ind_af_insuficiente boolean,
    ind_af_4dominios_150min boolean,
    ind_tv_maior_3h boolean,
    ind_tela_s_tv_maior_3h boolean,
    ind_tela_total_maior_3h boolean,
    ind_hipertensao boolean,
    ind_diabetes boolean,
    ind_depressao boolean,
    ind_excesso_peso boolean,
    ind_obesidade boolean,
    CONSTRAINT fk_fato_tempo FOREIGN KEY (sk_tempo) REFERENCES gold.dim_tempo (sk_tempo),
    CONSTRAINT fk_fato_cidade FOREIGN KEY (sk_cidade) REFERENCES gold.dim_cidade (sk_cidade),
    CONSTRAINT fk_fato_perfil FOREIGN KEY (sk_perfil) REFERENCES gold.dim_perfil (sk_perfil)
);

-- Índices B-Tree da Tabela Fato
CREATE INDEX IF NOT EXISTS idx_fato_tempo ON gold.fato_atividade_fisica (sk_tempo);
CREATE INDEX IF NOT EXISTS idx_fato_cidade ON gold.fato_atividade_fisica (sk_cidade);
CREATE INDEX IF NOT EXISTS idx_fato_perfil ON gold.fato_atividade_fisica (sk_perfil);
CREATE INDEX IF NOT EXISTS idx_fato_cidade_perfil ON gold.fato_atividade_fisica (sk_cidade, sk_perfil);
CREATE INDEX IF NOT EXISTS idx_fato_tempo_cidade_perfil ON gold.fato_atividade_fisica (sk_tempo, sk_cidade, sk_perfil);

-- Seed de registros para as 27 capitais e anos
INSERT INTO gold.fato_atividade_fisica (
    sk_registro, sk_tempo, sk_cidade, sk_perfil, peso_amostral,
    ind_ativo_lazer, ind_ativo_transporte, ind_ativo_ocupacional, ind_ativo_domestico,
    ind_inativo_total, ind_af_4dominios_150min, ind_tela_total_maior_3h, ind_tv_maior_3h,
    ind_hipertensao, ind_diabetes, ind_depressao, ind_excesso_peso, ind_obesidade
)
SELECT 
    'REG_' || c.sk_cidade || '_' || t.sk_tempo || '_' || p.sk_perfil,
    t.sk_tempo,
    c.sk_cidade,
    p.sk_perfil,
    1.0,
    (c.sk_cidade % 2 = 0),
    (c.sk_cidade % 3 = 0),
    (c.sk_cidade % 4 = 0),
    (c.sk_cidade % 5 = 0),
    (c.sk_cidade % 6 = 0),
    (c.sk_cidade % 2 = 1),
    (c.sk_cidade % 3 = 1),
    (c.sk_cidade % 4 = 1),
    (c.sk_cidade % 5 = 1),
    (c.sk_cidade % 6 = 1),
    (c.sk_cidade % 7 = 1),
    (c.sk_cidade % 2 = 0),
    (c.sk_cidade % 3 = 0)
FROM gold.dim_cidade c
CROSS JOIN gold.dim_tempo t
CROSS JOIN gold.dim_perfil p
ON CONFLICT (sk_registro) DO NOTHING;
