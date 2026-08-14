import pytest
from pydantic import ValidationError

from src.ingestion.transform import (
    build_concour_content,
    build_remuneration_content,
    to_complementaire_create,
    to_concour_create,
)

RAW_CONCOUR = {
    "doc_id": "concours_001",
    "concours_num": "1",
    "discipline": "A : Sciences du vivant",
    "corps": "Ingénieur de recherche",
    "nb_postes_declares": 1,
    "emploi_type": "Ingénieure ou ingénieur biologiste",
    "postes": [
        {
            "poste_num": 1,
            "affectation": "PARIS 05",
            "groupe_fonction": "Groupe 3",
            "mission": "Analyser des données.",
            "activites": "Développer des pipelines.",
            "competences": "Python, R.",
            "contexte": "Unité de recherche.",
        }
    ],
}

RAW_COMPLEMENTAIRE_AVANTAGES = {
    "doc_id": "avantages",
    "category": "avantages",
    "title": "Formation",
    "full_text": "La politique de formation du CNRS...",
}

RAW_REMUNERATION = {
    "doc_id": "remuneration",
    "category": "remuneration",
    "title": "Rémunération des fonctionnaires",
    "text": "Votre rémunération se compose du traitement indiciaire.",
    "tables": [
        {
            "table_index": 0,
            "headers": ["Grade", "Indice"],
            "rows": [["IR", "500"]],
        }
    ],
}


def test_build_concour_content_contains_poste_info():
    content = build_concour_content(RAW_CONCOUR)

    assert "PARIS 05" in content
    assert "Analyser des données." in content
    assert "Python, R." in content


def test_to_concour_create_valid():
    data = to_concour_create(RAW_CONCOUR)

    assert data.numero == "1"
    assert data.nb_postes == 1
    assert "PARIS 05" in data.content


def test_to_concour_create_missing_discipline_raises():
    raw = {k: v for k, v in RAW_CONCOUR.items() if k != "discipline"}

    with pytest.raises(ValidationError):
        to_concour_create(raw)


def test_build_remuneration_content_contains_text_and_table():
    content = build_remuneration_content(RAW_REMUNERATION)

    assert "traitement indiciaire" in content
    assert "Grade" in content
    assert "IR" in content


def test_to_complementaire_create_valid_full_text():
    data = to_complementaire_create(RAW_COMPLEMENTAIRE_AVANTAGES)

    assert data.categorie == "avantages"
    assert "formation" in data.contenu.lower()


def test_to_complementaire_create_valid_remuneration_tables():
    data = to_complementaire_create(RAW_REMUNERATION)

    assert data.categorie == "remuneration"
    assert "Grade" in data.contenu


def test_to_complementaire_create_invalid_category_raises():
    raw = {**RAW_COMPLEMENTAIRE_AVANTAGES, "category": "categorie_inexistante"}

    with pytest.raises(ValidationError):
        to_complementaire_create(raw)
