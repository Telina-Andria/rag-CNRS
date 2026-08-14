import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID

from src.db.interface.postgresql import Base

CATEGORIES = ("avantages", "accompagnement", "guide_candidat", "instituts", "remuneration")


class Complementaire(Base):
    __tablename__ = "complementaire"
    __table_args__ = (
        CheckConstraint(f"categorie IN {CATEGORIES}", name="ck_complementaire_categorie"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    categorie = Column(Text, nullable=False)
    contenu = Column(Text, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
