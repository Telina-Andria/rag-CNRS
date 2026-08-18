from typing import cast

import pytest
from pydantic import ValidationError

from src.ingestion_db.transform import (
    build_concour_content,
    render_table,
    to_accompagnement_create_list,
    to_avantage_create_list,
    to_concour_create,
    to_guide_candidat_create_list,
    to_institut_create_list,
    to_remuneration_create_list,
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

RAW_AVANTAGES = {
    "doc_id": "avantages",
    "category": "avantages",
    "title": "Formation",
    "pages": [
        {"page_num": 1, "text": "La politique de formation du CNRS..."},
        {"page_num": 2, "text": "Les avantages sociaux du CNRS..."},
    ],
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


def test_render_table_contains_headers_and_rows():
    table = cast(dict, RAW_REMUNERATION["tables"][0])

    content = render_table(table)

    assert "Grade" in content
    assert "IR" in content


@pytest.mark.parametrize(
    "to_create_list",
    [
        to_avantage_create_list,
        to_accompagnement_create_list,
        to_guide_candidat_create_list,
        to_institut_create_list,
    ],
)
def test_to_page_documents_creates_one_row_per_page(to_create_list):
    items = to_create_list(RAW_AVANTAGES)

    assert len(items) == 2
    assert items[0].page_num == 1
    assert "formation" in items[0].contenu.lower()
    assert items[1].page_num == 2


@pytest.mark.parametrize(
    "to_create_list",
    [
        to_avantage_create_list,
        to_accompagnement_create_list,
        to_guide_candidat_create_list,
        to_institut_create_list,
    ],
)
def test_to_page_documents_missing_page_num_raises(to_create_list):
    raw = {**RAW_AVANTAGES, "pages": [{"text": "Sans numéro de page."}]}

    with pytest.raises(ValidationError):
        to_create_list(raw)


def test_to_remuneration_create_list_contains_text_row_and_table_row():
    items = to_remuneration_create_list(RAW_REMUNERATION)

    assert len(items) == 2
    assert items[0].type == "texte"
    assert "traitement indiciaire" in items[0].contenu
    assert items[1].type == "tableau"
    assert "Grade" in items[1].contenu


def test_to_remuneration_create_list_without_tables_contains_only_text_row():
    raw = {**RAW_REMUNERATION, "tables": []}

    items = to_remuneration_create_list(raw)

    assert len(items) == 1
    assert items[0].type == "texte"
