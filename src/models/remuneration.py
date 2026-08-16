import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID

from src.db.interface.postgresql import Base

TYPES = ("texte", "tableau")


class Remuneration(Base):
    __tablename__ = "remuneration"
    __table_args__ = (CheckConstraint(f"type IN {TYPES}", name="ck_remuneration_type"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Text, nullable=False)
    contenu = Column(Text, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
