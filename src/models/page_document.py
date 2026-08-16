import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID


class PageDocumentMixin:
    """Colonnes communes aux tables "une ligne par page" (avantages,
    accompagnement, guide_candidat, instituts)."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_num = Column(Integer, nullable=False)
    contenu = Column(Text, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
