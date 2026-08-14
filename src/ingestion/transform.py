from typing import Any

from src.schemas.complementaire import ComplementaireCreate
from src.schemas.concour import ConcourCreate


def build_concour_content(raw: dict[str, Any]) -> str:
    """Concatène les postes d'un concours en un seul texte."""
    blocs = []
    for poste in raw.get("postes", []):
        blocs.append(
            f"Poste {poste.get('poste_num')} - {poste.get('affectation')} "
            f"({poste.get('groupe_fonction')})\n"
            f"Mission:\n{poste.get('mission', '')}\n\n"
            f"Activités:\n{poste.get('activites', '')}\n\n"
            f"Compétences:\n{poste.get('competences', '')}\n\n"
            f"Contexte:\n{poste.get('contexte', '')}"
        )
    return "\n\n---\n\n".join(blocs)


def to_concour_create(raw: dict[str, Any]) -> ConcourCreate:
    """Valide et transforme un concours brut (concours.json) en ConcourCreate."""
    return ConcourCreate(
        numero=raw.get("concours_num"),
        discipline=raw.get("discipline"),
        corps=raw.get("corps"),
        nb_postes=raw.get("nb_postes_declares"),
        emploi_type=raw.get("emploi_type"),
        content=build_concour_content(raw),
    )


def build_remuneration_content(raw: dict[str, Any]) -> str:
    """Assemble le texte et les tableaux d'un document de type rémunération."""
    blocs = [raw.get("text", "")]
    for table in raw.get("tables", []):
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        lignes = [" | ".join(headers)]
        lignes.extend(" | ".join(row) for row in rows)
        blocs.append("\n".join(lignes))
    return "\n\n".join(blocs)


def to_complementaire_create(raw: dict[str, Any]) -> ComplementaireCreate:
    """Valide et transforme un document complémentaire brut en ComplementaireCreate."""
    contenu = raw.get("full_text") or build_remuneration_content(raw)
    return ComplementaireCreate(categorie=raw.get("category"), contenu=contenu)
