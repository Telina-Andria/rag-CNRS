from src.db.interface.base import BaseDatabase
from src.db.interface.postgresql import PostgreSQLDatabase, PostgreSQLSettings

# Import des modèles pour qu'ils soient enregistrés sur Base.metadata
# avant la création des tables (create_all) dans startup().
from src.models import complementaire, concour  # noqa: F401


def make_database() -> BaseDatabase:
    """
    Factory function to create a database instance.

    Returns:
        BaseDatabase: An instance of the database.
    """
    # PostgreSQLSettings charge automatiquement les variables d'environnement
    # préfixées par POSTGRES_ (voir SettingsConfigDict(env_prefix="POSTGRES_")).
    config = PostgreSQLSettings()

    return PostgreSQLDatabase(config=config)
