"""Étape d'extraction : lit les documents depuis PostgreSQL, séparément du
chunking proprement dit. Une fonction dédiée par catégorie de complémentaire,
plus une pour les concours."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.complementaire import Complementaire
from src.models.concour import Concour


def _extract_categorie(session: Session, categorie: str) -> list[Complementaire]:
    """Récupère les lignes `complementaire` d'une catégorie donnée."""
    stmt = select(Complementaire).where(Complementaire.categorie == categorie)
    return list(session.scalars(stmt))


def extract_avantages(session: Session) -> list[Complementaire]:
    return _extract_categorie(session, "avantages")


def extract_accompagnement(session: Session) -> list[Complementaire]:
    return _extract_categorie(session, "accompagnement")


def extract_guide_candidat(session: Session) -> list[Complementaire]:
    return _extract_categorie(session, "guide_candidat")


def extract_instituts(session: Session) -> list[Complementaire]:
    return _extract_categorie(session, "instituts")


def extract_remuneration(session: Session) -> list[Complementaire]:
    return _extract_categorie(session, "remuneration")


def extract_concours(session: Session) -> list[Concour]:
    """Récupère tous les concours."""
    return list(session.scalars(select(Concour)))
