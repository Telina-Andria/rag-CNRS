from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.complementaire import Complementaire
from src.models.concour import Concour
from src.schemas.complementaire import ComplementaireCreate
from src.schemas.concour import ConcourCreate


def get_existing_numeros(session: Session) -> set[str]:
    """Récupère les numéros de concours déjà présents en base."""
    return set(session.scalars(select(Concour.numero)))


def load_concour(session: Session, data: ConcourCreate) -> Concour:
    """Insère un concours validé en base."""
    concour = Concour(**data.model_dump())
    session.add(concour)
    return concour


def get_existing_categories(session: Session) -> set[str]:
    """Récupère les catégories d'informations complémentaires déjà présentes en base."""
    return set(session.scalars(select(Complementaire.categorie)))


def load_complementaire(session: Session, data: ComplementaireCreate) -> Complementaire:
    """Insère une information complémentaire validée en base."""
    complementaire = Complementaire(**data.model_dump())
    session.add(complementaire)
    return complementaire
