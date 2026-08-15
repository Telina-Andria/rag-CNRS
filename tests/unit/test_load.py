import pytest
from testcontainers.community.postgres import PostgresContainer

from src.db.interface.postgresql import PostgreSQLDatabase, PostgreSQLSettings
from src.ingestion.load import (
    get_existing_categories,
    get_existing_numeros,
    load_complementaire,
    load_concour,
)
from src.schemas.complementaire import ComplementaireCreate
from src.schemas.concour import ConcourCreate


@pytest.fixture
def db():
    with PostgresContainer("postgres:16-alpine") as pg:
        config = PostgreSQLSettings(database_url=pg.get_connection_url())
        database = PostgreSQLDatabase(config=config)
        database.startup()
        yield database
        database.teardown()


def test_load_concour_inserts_and_is_visible_in_existing_numeros(db):
    data = ConcourCreate(
        numero="1",
        discipline="A : Sciences du vivant",
        corps="Ingénieur de recherche",
        nb_postes=1,
        emploi_type="Ingénieure ou ingénieur biologiste",
        content="Contenu du concours...",
    )

    with db.get_session() as session:
        assert get_existing_numeros(session) == set()

        load_concour(session, data)
        session.commit()

        assert get_existing_numeros(session) == {"1"}


def test_load_complementaire_inserts_and_is_visible_in_existing_categories(db):
    data = ComplementaireCreate(categorie="avantages", contenu="Contenu...")

    with db.get_session() as session:
        assert get_existing_categories(session) == set()

        load_complementaire(session, data)
        session.commit()

        assert get_existing_categories(session) == {"avantages"}
