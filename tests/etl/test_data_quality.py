"""
Testes de qualidade de dados para as camadas Bronze, Silver e Gold.
Validam volumetria, integridade referencial e ausência de artefatos.
"""

from sqlalchemy import text
from src.etl.database import engine


class TestBronze:
    """Validações da camada Bronze."""

    def test_has_data(self):
        """A tabela bronze.vigitel_raw deve conter registros."""
        with engine.connect() as conn:
            count = conn.execute(text("SELECT count(*) FROM bronze.vigitel_raw")).scalar()
        assert count > 0, "Tabela Bronze está vazia."

    def test_column_count(self):
        """A tabela deve ter exatamente o número de colunas do contrato."""
        from src.etl.schema import COLUMN_MAP

        with engine.connect() as conn:
            cols = conn.execute(
                text(
                    "SELECT count(*) FROM information_schema.columns "
                    "WHERE table_schema = 'bronze' AND table_name = 'vigitel_raw'"
                )
            ).scalar()
        assert cols == len(COLUMN_MAP), f"Esperado {len(COLUMN_MAP)} colunas, encontrado {cols}."


class TestSilver:
    """Validações da camada Silver."""

    def test_has_data(self):
        """A tabela silver.vigitel_cleansed deve conter registros."""
        with engine.connect() as conn:
            count = conn.execute(text("SELECT count(*) FROM silver.vigitel_cleansed")).scalar()
        assert count > 0, "Tabela Silver está vazia."

    def test_surrogate_key_filled(self):
        """Todas as linhas devem ter sk_registro preenchido."""
        with engine.connect() as conn:
            nulls = conn.execute(
                text("SELECT count(*) FROM silver.vigitel_cleansed WHERE sk_registro IS NULL")
            ).scalar()
        assert nulls == 0, f"Encontradas {nulls} linhas sem surrogate key."

    def test_no_magic_nulls_in_categoricals(self):
        """Códigos mágicos (777, 888, 999) não devem existir em colunas categóricas."""
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT count(*) FROM silver.vigitel_cleansed "
                    "WHERE pratica_exercicio_lazer::text IN ('777', '888', '999')"
                )
            ).scalar()
        assert result == 0, "Códigos mágicos residuais na Silver."

    def test_continuous_columns_preserved(self):
        """Valores numéricos contínuos não devem ter sido apagados pela limpeza."""
        with engine.connect() as conn:
            count = conn.execute(
                text("SELECT count(*) FROM silver.vigitel_cleansed WHERE peso_amostral IS NOT NULL")
            ).scalar()
        assert count > 0, "Coluna peso_amostral ficou toda nula (limpeza incorreta)."

    def test_row_count_matches_bronze(self):
        """A Silver deve ter o mesmo número de linhas que a Bronze."""
        with engine.connect() as conn:
            bronze = conn.execute(text("SELECT count(*) FROM bronze.vigitel_raw")).scalar()
            silver = conn.execute(text("SELECT count(*) FROM silver.vigitel_cleansed")).scalar()
        assert bronze == silver, f"Bronze={bronze}, Silver={silver}. Houve perda de dados."


class TestGold:
    """Validações da camada Gold (Star Schema)."""

    def test_fato_has_data(self):
        """A tabela Fato deve conter registros."""
        with engine.connect() as conn:
            count = conn.execute(text("SELECT count(*) FROM gold.fato_atividade_fisica")).scalar()
        assert count > 0, "Tabela Fato está vazia."

    def test_dim_tempo_coverage(self):
        """A dimensão tempo deve cobrir os anos presentes na Silver."""
        with engine.connect() as conn:
            silver_years = conn.execute(
                text(
                    "SELECT count(DISTINCT ano_coleta) FROM silver.vigitel_cleansed WHERE ano_coleta IS NOT NULL"
                )
            ).scalar()
            dim_years = conn.execute(text("SELECT count(*) FROM gold.dim_tempo")).scalar()
        assert dim_years == silver_years, f"dim_tempo={dim_years}, Silver anos={silver_years}."

    def test_dim_cidade_has_names(self):
        """Pelo menos 20 capitais devem ter nomes preenchidos."""
        with engine.connect() as conn:
            named = conn.execute(
                text("SELECT count(*) FROM gold.dim_cidade WHERE nome_cidade IS NOT NULL")
            ).scalar()
        assert named >= 20, f"Apenas {named} cidades com nome. Esperado >= 20."

    def test_dim_perfil_has_bands(self):
        """A dimensão perfil deve conter faixas etárias, não idades individuais."""
        with engine.connect() as conn:
            faixas = conn.execute(
                text("SELECT DISTINCT faixa_etaria FROM gold.dim_perfil ORDER BY faixa_etaria")
            ).fetchall()
            faixa_names = {row[0] for row in faixas}
        expected = {"18-24", "25-34", "35-44", "45-54", "55-64", "65+"}
        assert expected.issubset(faixa_names), (
            f"Faixas esperadas: {expected}, encontradas: {faixa_names}"
        )

    def test_fato_referential_integrity_tempo(self):
        """Não devem existir registros órfãos na FK sk_tempo."""
        with engine.connect() as conn:
            orphans = conn.execute(
                text(
                    "SELECT count(*) FROM gold.fato_atividade_fisica f "
                    "LEFT JOIN gold.dim_tempo d ON f.sk_tempo = d.sk_tempo "
                    "WHERE f.sk_tempo IS NOT NULL AND d.sk_tempo IS NULL"
                )
            ).scalar()
        assert orphans == 0, f"Encontradas {orphans} referências órfãs para dim_tempo."

    def test_fato_referential_integrity_cidade(self):
        """Não devem existir registros órfãos na FK sk_cidade."""
        with engine.connect() as conn:
            orphans = conn.execute(
                text(
                    "SELECT count(*) FROM gold.fato_atividade_fisica f "
                    "LEFT JOIN gold.dim_cidade d ON f.sk_cidade = d.sk_cidade "
                    "WHERE f.sk_cidade IS NOT NULL AND d.sk_cidade IS NULL"
                )
            ).scalar()
        assert orphans == 0, f"Encontradas {orphans} referências órfãs para dim_cidade."

    def test_fato_referential_integrity_perfil(self):
        """Não devem existir registros órfãos na FK sk_perfil."""
        with engine.connect() as conn:
            orphans = conn.execute(
                text(
                    "SELECT count(*) FROM gold.fato_atividade_fisica f "
                    "LEFT JOIN gold.dim_perfil d ON f.sk_perfil = d.sk_perfil "
                    "WHERE f.sk_perfil IS NULL OR d.sk_perfil IS NULL"
                )
            ).scalar()
        assert orphans == 0, f"Encontradas {orphans} referências órfãs para dim_perfil."

    def test_fato_constraints_exist(self):
        """Primary Key e Foreign Keys devem estar registradas na tabela Fato."""
        with engine.connect() as conn:
            constraints = conn.execute(
                text(
                    "SELECT conname FROM pg_constraint "
                    "WHERE conrelid = 'gold.fato_atividade_fisica'::regclass"
                )
            ).fetchall()
            constraint_names = {row[0] for row in constraints}
        assert "fato_atividade_fisica_pkey" in constraint_names, "PK da Fato não encontrada."
        assert "fk_fato_tempo" in constraint_names, "FK fk_fato_tempo não encontrada."
        assert "fk_fato_cidade" in constraint_names, "FK fk_fato_cidade não encontrada."
        assert "fk_fato_perfil" in constraint_names, "FK fk_fato_perfil não encontrada."

    def test_indexes_exist(self):
        """Índices B-Tree devem existir nas FKs da tabela Fato."""
        with engine.connect() as conn:
            indexes = conn.execute(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE schemaname = 'gold' AND tablename = 'fato_atividade_fisica'"
                )
            ).fetchall()
            index_names = {row[0] for row in indexes}
        assert "idx_fato_tempo" in index_names, "Índice idx_fato_tempo não encontrado."
        assert "idx_fato_cidade" in index_names, "Índice idx_fato_cidade não encontrado."
        assert "idx_fato_perfil" in index_names, "Índice idx_fato_perfil não encontrado."
        assert "idx_fato_cidade_perfil" in index_names, (
            "Índice composto idx_fato_cidade_perfil não encontrado."
        )
        assert "idx_fato_tempo_cidade_perfil" in index_names, (
            "Índice composto idx_fato_tempo_cidade_perfil não encontrado."
        )
