from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConcourBase(BaseModel):
    numero: str = Field(..., description="Numéro du concours")
    discipline: str = Field(..., description="Discipline du concours")
    corps: str = Field(..., description="Corps concerné")
    nb_postes: int | None = Field(default=None, description="Nombre de postes déclarés")
    emploi_type: str | None = Field(default=None, description="Type d'emploi")
    content: str = Field(..., description="Contenu textuel du concours (postes inclus)")


class ConcourCreate(ConcourBase):
    pass


class ConcourResponse(ConcourBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
