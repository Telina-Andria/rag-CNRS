import pytest
from testcontainers.community.postgres import PostgresContainer

from src.chunking.extraction import (
    extract_accompagnement,
    extract_avantages,
    extract_concours,
    extract_guide_candidat,
    extract_instituts,
    extract_remuneration,
)
from src.db.interface.postgresql import PostgreSQLDatabase, PostgreSQLSettings
from src.ingestion.load import load_complementaire, load_concour
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
        for categorie in [
            "avantages",
            "accompagnement",
            "guide_candidat",
            "instituts",
            "remuneration",
        ]:
            load_complementaire(
                session, ComplementaireCreate(categorie=categorie, contenu=f"Contenu {categorie}")
            )
        session.commit()
        yield session


def test_extract_concours_returns_all_concours(seeded_session):
    concours = extract_concours(seeded_session)

    assert len(concours) == 1
    assert concours[0].numero == "1"


@pytest.mark.parametrize(
    "extractor, categorie",
    [
        (extract_avantages, "avantages"),
        (extract_accompagnement, "accompagnement"),
        (extract_guide_candidat, "guide_candidat"),
        (extract_instituts, "instituts"),
        (extract_remuneration, "remuneration"),
    ],
)
def test_extract_categorie_returns_only_its_categorie(seeded_session, extractor, categorie):
    rows = extractor(seeded_session)

    assert len(rows) == 1
    assert rows[0].categorie == categorie
    assert rows[0].contenu == f"Contenu {categorie}"
