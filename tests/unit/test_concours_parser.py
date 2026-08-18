import pytest

from src.chunking.common.concours_parser import ConcourParsingError, parse_concour_content
from src.ingestion_db.transform import build_concour_content

RAW_CONCOUR_MULTI = {
    "postes": [
        {
            "poste_num": 1,
            "affectation": "PARIS 05",
            "groupe_fonction": "Groupe 3",
            "mission": "Analyser des données.",
            "activites": "Développer des pipelines.",
            "competences": "Python, R.",
            "contexte": "Unité de recherche.",
        },
        {
            "poste_num": 2,
            "affectation": "LYON",
            "groupe_fonction": "Groupe 2",
            "mission": "Encadrer une équipe.",
            "activites": "Superviser des projets.",
            "competences": "Management.",
            "contexte": "Direction régionale.",
        },
    ]
}

RAW_CONCOUR_RUBRIQUE_VIDE = {
    "postes": [
        {
            "poste_num": 1,
            "affectation": "PARIS 05",
            "groupe_fonction": "Groupe 3",
            "mission": "",
            "activites": "Développer des pipelines.",
            "competences": "",
            "contexte": "Unité de recherche.",
        }
    ]
}


def test_parse_concour_content_round_trip_single_poste():
    content = build_concour_content(RAW_CONCOUR_MULTI)
    postes = parse_concour_content(content)

    assert len(postes) == 2
    assert postes[0].poste_num == 1
    assert postes[0].affectation == "PARIS 05"
    assert postes[0].groupe_fonction == "Groupe 3"
    assert postes[0].mission == "Analyser des données."
    assert postes[0].activites == "Développer des pipelines."
    assert postes[0].competences == "Python, R."
    assert postes[0].contexte == "Unité de recherche."


def test_parse_concour_content_round_trip_multi_poste():
    content = build_concour_content(RAW_CONCOUR_MULTI)
    postes = parse_concour_content(content)

    assert postes[1].poste_num == 2
    assert postes[1].affectation == "LYON"
    assert postes[1].mission == "Encadrer une équipe."


def test_parse_concour_content_rubrique_vide():
    content = build_concour_content(RAW_CONCOUR_RUBRIQUE_VIDE)
    postes = parse_concour_content(content)

    assert len(postes) == 1
    assert postes[0].mission == ""
    assert postes[0].competences == ""
    assert postes[0].activites == "Développer des pipelines."


def test_parse_concour_content_groupe_fonction_multiligne():
    raw = {
        "postes": [
            {
                "poste_num": 1,
                "affectation": "GIF SUR YVETTE",
                "groupe_fonction": "Groupe 2\nFonction mutualisée avec :\nAutre laboratoire",
                "mission": "Analyser des données.",
                "activites": "Développer des pipelines.",
                "competences": "Python, R.",
                "contexte": "Unité de recherche.",
            }
        ]
    }
    content = build_concour_content(raw)

    postes = parse_concour_content(content)

    assert len(postes) == 1
    assert postes[0].affectation == "GIF SUR YVETTE"
    assert postes[0].groupe_fonction == "Groupe 2\nFonction mutualisée avec :\nAutre laboratoire"
    assert postes[0].mission == "Analyser des données."


def test_parse_concour_content_empty_returns_empty_list():
    assert parse_concour_content("") == []


def test_parse_concour_content_malformed_bloc_raises():
    with pytest.raises(ConcourParsingError):
        parse_concour_content("Ceci n'est pas un bloc de poste valide")
