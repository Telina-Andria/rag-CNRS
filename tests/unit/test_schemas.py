import pytest
from pydantic import ValidationError

from src.schemas.complementaire import ComplementaireCreate
from src.schemas.concour import ConcourCreate


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


def test_complementaire_create_valid():
    complementaire = ComplementaireCreate(categorie="avantages", contenu="Contenu...")

    assert complementaire.categorie == "avantages"


def test_complementaire_create_invalid_categorie_raises():
    with pytest.raises(ValidationError):
        ComplementaireCreate(categorie="categorie_inexistante", contenu="Contenu...")
