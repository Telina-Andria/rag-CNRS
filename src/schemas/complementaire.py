from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Categorie = Literal["avantages", "accompagnement", "guide_candidat", "instituts", "remuneration"]


class ComplementaireBase(BaseModel):
    categorie: Categorie = Field(..., description="Catégorie de l'information complémentaire")
    contenu: str = Field(..., description="Contenu textuel")


class ComplementaireCreate(ComplementaireBase):
    pass


class ComplementaireResponse(ComplementaireBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
