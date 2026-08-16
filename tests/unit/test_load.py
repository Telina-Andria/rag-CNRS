import pytest
from sqlalchemy.exc import IntegrityError
from testcontainers.community.postgres import PostgresContainer

from src.db.interface.postgresql import PostgreSQLDatabase, PostgreSQLSettings
from src.ingestion.load import (
    count_rows,
    get_existing_numeros,
    load_avantage,
    load_concour,
    load_remuneration,
)
from src.models.avantage import Avantage
from src.models.remuneration import Remuneration
from src.schemas.avantage import AvantageCreate
from src.schemas.concour import ConcourCreate
from src.schemas.remuneration import RemunerationCreate


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


def test_load_avantage_inserts_and_is_counted(db):
    data = AvantageCreate(page_num=1, contenu="Contenu...")

    with db.get_session() as session:
        assert count_rows(session, Avantage) == 0

        load_avantage(session, data)
        session.commit()

        assert count_rows(session, Avantage) == 1


def test_load_remuneration_inserts_and_is_counted(db):
    data = RemunerationCreate(type="tableau", contenu="Contenu...")

    with db.get_session() as session:
        assert count_rows(session, Remuneration) == 0

        load_remuneration(session, data)
        session.commit()

        assert count_rows(session, Remuneration) == 1


def test_load_concour_duplicate_numero_raises_integrity_error(db):
    data = ConcourCreate(
        numero="1",
        discipline="A : Sciences du vivant",
        corps="Ingénieur de recherche",
        content="Contenu du concours...",
    )

    with db.get_session() as session:
        load_concour(session, data)
        session.commit()

    with db.get_session() as session, pytest.raises(IntegrityError):
        load_concour(session, data)
        session.commit()
