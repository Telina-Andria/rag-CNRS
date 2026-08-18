from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.accompagnement import Accompagnement
from src.models.avantage import Avantage
from src.models.concour import Concour
from src.models.guide_candidat import GuideCandidat
from src.models.institut import Institut
from src.models.remuneration import Remuneration
from src.schemas.accompagnement import AccompagnementCreate
from src.schemas.avantage import AvantageCreate
from src.schemas.concour import ConcourCreate
from src.schemas.guide_candidat import GuideCandidatCreate
from src.schemas.institut import InstitutCreate
from src.schemas.remuneration import RemunerationCreate


def get_existing_numeros(session: Session) -> set[str]:
    """Récupère les numéros de concours déjà présents en base."""
    return set(session.scalars(select(Concour.numero)))


def load_concour(session: Session, data: ConcourCreate) -> Concour:
    """Insère un concours validé en base."""
    concour = Concour(**data.model_dump())
    session.add(concour)
    return concour


def count_rows(session: Session, model: type) -> int:
    """Compte les lignes déjà présentes pour une table, pour éviter de la
    re-semer si elle est déjà remplie."""
    return session.scalar(select(func.count()).select_from(model)) or 0


def load_avantage(session: Session, data: AvantageCreate) -> Avantage:
    """Insère une page d'avantages validée en base."""
    avantage = Avantage(**data.model_dump())
    session.add(avantage)
    return avantage


def load_accompagnement(session: Session, data: AccompagnementCreate) -> Accompagnement:
    """Insère une page d'accompagnement validée en base."""
    accompagnement = Accompagnement(**data.model_dump())
    session.add(accompagnement)
    return accompagnement


def load_guide_candidat(session: Session, data: GuideCandidatCreate) -> GuideCandidat:
    """Insère une page du guide candidat validée en base."""
    guide_candidat = GuideCandidat(**data.model_dump())
    session.add(guide_candidat)
    return guide_candidat


def load_institut(session: Session, data: InstitutCreate) -> Institut:
    """Insère une page d'instituts validée en base."""
    institut = Institut(**data.model_dump())
    session.add(institut)
    return institut


def load_remuneration(session: Session, data: RemunerationCreate) -> Remuneration:
    """Insère une ligne de rémunération (texte ou tableau) validée en base."""
    remuneration = Remuneration(**data.model_dump())
    session.add(remuneration)
    return remuneration
