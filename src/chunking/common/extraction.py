"""Étape d'extraction : lit les documents depuis PostgreSQL, séparément du
chunking proprement dit. Une fonction dédiée par table."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.accompagnement import Accompagnement
from src.models.avantage import Avantage
from src.models.concour import Concour
from src.models.guide_candidat import GuideCandidat
from src.models.institut import Institut
from src.models.remuneration import Remuneration


def extract_avantages(session: Session) -> list[Avantage]:
    return list(session.scalars(select(Avantage).order_by(Avantage.page_num)))


def extract_accompagnement(session: Session) -> list[Accompagnement]:
    return list(session.scalars(select(Accompagnement).order_by(Accompagnement.page_num)))


def extract_guide_candidat(session: Session) -> list[GuideCandidat]:
    return list(session.scalars(select(GuideCandidat).order_by(GuideCandidat.page_num)))


def extract_instituts(session: Session) -> list[Institut]:
    return list(session.scalars(select(Institut).order_by(Institut.page_num)))


def extract_remuneration(session: Session) -> list[Remuneration]:
    return list(session.scalars(select(Remuneration)))


def extract_concours(session: Session) -> list[Concour]:
    """Récupère tous les concours."""
    return list(session.scalars(select(Concour)))
