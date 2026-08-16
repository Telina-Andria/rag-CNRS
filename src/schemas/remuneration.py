from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

TypeContenu = Literal["texte", "tableau"]


class RemunerationBase(BaseModel):
    type: TypeContenu = Field(..., description="Type de contenu (texte ou tableau)")
    contenu: str = Field(..., description="Contenu textuel")


class RemunerationCreate(RemunerationBase):
    pass


class RemunerationResponse(RemunerationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
