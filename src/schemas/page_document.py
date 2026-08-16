from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PageDocumentBase(BaseModel):
    """Schéma commun aux catégories "une ligne par page" (avantages,
    accompagnement, guide_candidat, instituts)."""

    page_num: int = Field(..., description="Numéro de page dans le document source")
    contenu: str = Field(..., description="Contenu textuel de la page")


class PageDocumentResponse(PageDocumentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
