import pytest
from pydantic import ValidationError

from src.schemas.avantage import AvantageCreate
from src.schemas.concour import ConcourCreate
from src.schemas.remuneration import RemunerationCreate


def test_concour_create_valid():
    concour = ConcourCreate(
        numero="1",
        discipline="A : Sciences du vivant",
        corps="Ingénieur de recherche",
        nb_postes=3,
        emploi_type="Ingénieure ou ingénieur biologiste",
        content="Contenu du concours...",
    )

    assert concour.numero == "1"
    assert concour.nb_postes == 3


def test_concour_create_missing_required_field_raises():
    with pytest.raises(ValidationError):
        ConcourCreate(
            discipline="A : Sciences du vivant",
            corps="Ingénieur de recherche",
            content="Contenu du concours...",
        )


def test_concour_create_wrong_type_raises():
    with pytest.raises(ValidationError):
        ConcourCreate(
            numero="1",
            discipline="A : Sciences du vivant",
            corps="Ingénieur de recherche",
            nb_postes="pas un nombre",
            content="Contenu du concours...",
        )


def test_avantage_create_valid():
    avantage = AvantageCreate(page_num=1, contenu="Contenu...")

    assert avantage.page_num == 1


def test_avantage_create_missing_page_num_raises():
    with pytest.raises(ValidationError):
        AvantageCreate(contenu="Contenu...")


def test_remuneration_create_valid():
    remuneration = RemunerationCreate(type="tableau", contenu="Contenu...")

    assert remuneration.type == "tableau"


def test_remuneration_create_invalid_type_raises():
    with pytest.raises(ValidationError):
        RemunerationCreate(type="autre", contenu="Contenu...")
