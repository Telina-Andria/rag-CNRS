import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.db.interface.postgresql import Base


class Concour(Base):
    __tablename__ = "concours"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    discipline = Column(Text, nullable=False)
    corps = Column(Text, nullable=False)
    nb_postes = Column(Integer)
    emploi_type = Column(Text)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
