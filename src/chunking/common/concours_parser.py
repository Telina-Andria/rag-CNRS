"""Reconstruit les postes structurés depuis le texte fusionné de
`Concour.content`, produit par `build_concour_content()`
(`src/ingestion/transform.py`). Format déterministe :

    Poste {num} - {affectation} ({groupe_fonction})
    Mission:
    {mission}

    Activités:
    {activites}

    Compétences:
    {competences}

    Contexte:
    {contexte}

les postes étant séparés par "\n\n---\n\n". Ce parseur dépend exactement de
ce format ; il est protégé par un test de round-trip avec
`build_concour_content()` (voir tests/unit/test_concours_parser.py).
"""

import re

from src.chunking.common.models import PosteParsed

_POSTE_HEADER_RE = re.compile(
    r"\APoste (?P<poste_num>\d+) - (?P<affectation>.+?) \((?P<groupe_fonction>.+?)\)\n"
    r"(?=Mission:)",
    re.DOTALL,
)

_FIELDS_RE = re.compile(
    r"Mission:\n(?P<mission>.*?)\n\n"
    r"Activités:\n(?P<activites>.*?)\n\n"
    r"Compétences:\n(?P<competences>.*?)\n\n"
    r"Contexte:\n(?P<contexte>.*)",
    re.DOTALL,
)


class ConcourParsingError(Exception):
    """Levée quand un bloc de poste ne respecte pas le format attendu."""


def parse_concour_content(content: str) -> list[PosteParsed]:
    """Reconstruit la liste des postes depuis le texte fusionné d'un concours."""
    if not content.strip():
        return []

    postes = []
    for bloc in content.split("\n\n---\n\n"):
        header_match = _POSTE_HEADER_RE.match(bloc)
        if not header_match:
            raise ConcourParsingError(f"En-tête de poste introuvable dans le bloc : {bloc!r}")

        rest = bloc[header_match.end() :].lstrip("\n")
        fields_match = _FIELDS_RE.match(rest)
        if not fields_match:
            raise ConcourParsingError(f"Rubriques introuvables dans le bloc : {bloc!r}")

        postes.append(
            PosteParsed(
                poste_num=int(header_match.group("poste_num")),
                affectation=header_match.group("affectation"),
                groupe_fonction=header_match.group("groupe_fonction"),
                mission=fields_match.group("mission").strip(),
                activites=fields_match.group("activites").strip(),
                competences=fields_match.group("competences").strip(),
                contexte=fields_match.group("contexte").strip(),
            )
        )
    return postes
