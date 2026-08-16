from typing import Any

from src.schemas.accompagnement import AccompagnementCreate
from src.schemas.avantage import AvantageCreate
from src.schemas.concour import ConcourCreate
from src.schemas.guide_candidat import GuideCandidatCreate
from src.schemas.institut import InstitutCreate
from src.schemas.page_document import PageDocumentBase
from src.schemas.remuneration import RemunerationCreate


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


def to_page_documents(raw: dict[str, Any], schema_cls: type[PageDocumentBase]) -> list[Any]:
    """Valide et transforme un document paginé brut (avantages, accompagnement,
    guide_candidat, instituts) en une ligne par page."""
    return [
        schema_cls(page_num=page.get("page_num"), contenu=page.get("text"))
        for page in raw.get("pages", [])
    ]


def to_avantage_create_list(raw: dict[str, Any]) -> list[AvantageCreate]:
    return to_page_documents(raw, AvantageCreate)


def to_accompagnement_create_list(raw: dict[str, Any]) -> list[AccompagnementCreate]:
    return to_page_documents(raw, AccompagnementCreate)


def to_guide_candidat_create_list(raw: dict[str, Any]) -> list[GuideCandidatCreate]:
    return to_page_documents(raw, GuideCandidatCreate)


def to_institut_create_list(raw: dict[str, Any]) -> list[InstitutCreate]:
    return to_page_documents(raw, InstitutCreate)


def render_table(table: dict[str, Any]) -> str:
    """Rend un tableau structuré (headers + rows) en texte."""
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    lignes = [" | ".join(headers)]
    lignes.extend(" | ".join(row) for row in rows)
    return "\n".join(lignes)


def to_remuneration_create_list(raw: dict[str, Any]) -> list[RemunerationCreate]:
    """Valide et transforme un document de rémunération brut en une ligne
    "texte" puis une ligne "tableau" par tableau structuré."""
    items = [RemunerationCreate(type="texte", contenu=raw.get("text", ""))]
    items.extend(
        RemunerationCreate(type="tableau", contenu=render_table(table))
        for table in raw.get("tables", [])
    )
    return items
