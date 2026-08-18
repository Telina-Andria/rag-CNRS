import pytest
from testcontainers.community.postgres import PostgresContainer

from src.chunking.common.extraction import (
    extract_accompagnement,
    extract_avantages,
    extract_concours,
    extract_guide_candidat,
    extract_instituts,
    extract_remuneration,
)
from src.db.interface.postgresql import PostgreSQLDatabase, PostgreSQLSettings
from src.ingestion_db.load import (
    load_accompagnement,
    load_avantage,
    load_concour,
    load_guide_candidat,
    load_institut,
    load_remuneration,
)
from src.schemas.accompagnement import AccompagnementCreate
from src.schemas.avantage import AvantageCreate
from src.schemas.concour import ConcourCreate
from src.schemas.guide_candidat import GuideCandidatCreate
from src.schemas.institut import InstitutCreate
from src.schemas.remuneration import RemunerationCreate


@pytest.fixture
def db():
    with PostgresContainer("postgres:16-alpine") as pg:
        config = PostgreSQLSettings(database_url=pg.get_connection_url())
        database = PostgreSQLDatabase(config=config)
        database.startup()
        yield database
        database.teardown()


@pytest.fixture
def seeded_session(db):
    with db.get_session() as session:
        load_concour(
            session,
            ConcourCreate(
                numero="1",
                discipline="A : Sciences du vivant",
                corps="Ingénieur de recherche",
                content="Contenu du concours...",
            ),
        )
        load_avantage(session, AvantageCreate(page_num=1, contenu="Contenu avantages page 1"))
        load_avantage(session, AvantageCreate(page_num=2, contenu="Contenu avantages page 2"))
        load_accompagnement(
            session, AccompagnementCreate(page_num=1, contenu="Contenu accompagnement")
        )
        load_guide_candidat(
            session, GuideCandidatCreate(page_num=1, contenu="Contenu guide_candidat")
        )
        load_institut(session, InstitutCreate(page_num=1, contenu="Contenu instituts"))
        load_remuneration(session, RemunerationCreate(type="texte", contenu="Contenu texte"))
        load_remuneration(session, RemunerationCreate(type="tableau", contenu="Contenu tableau"))
        session.commit()
        yield session


def test_extract_concours_returns_all_concours(seeded_session):
    concours = extract_concours(seeded_session)

    assert len(concours) == 1
    assert concours[0].numero == "1"


def test_extract_avantages_returns_all_pages_sorted(seeded_session):
    rows = extract_avantages(seeded_session)

    assert len(rows) == 2
    assert [row.page_num for row in rows] == [1, 2]


@pytest.mark.parametrize(
    "extractor",
    [extract_accompagnement, extract_guide_candidat, extract_instituts],
)
def test_extract_page_categorie_returns_its_rows(seeded_session, extractor):
    rows = extractor(seeded_session)

    assert len(rows) == 1
    assert rows[0].page_num == 1


def test_extract_remuneration_returns_texte_and_tableau_rows(seeded_session):
    rows = extract_remuneration(seeded_session)

    assert {row.type for row in rows} == {"texte", "tableau"}
