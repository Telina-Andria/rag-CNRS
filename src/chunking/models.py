from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """Un chunk prêt à être indexé, avec son contexte optionnel (stratégie contextualisée)."""

    chunk_id: str
    content: str
    metadata: dict = Field(default_factory=dict)
    context: str | None = None
    contextualized_content: str | None = None


class PosteParsed(BaseModel):
    """Un poste reconstruit depuis le texte fusionné de `Concour.content`."""

    poste_num: int
    affectation: str
    groupe_fonction: str
    mission: str = ""
    activites: str = ""
    competences: str = ""
    contexte: str = ""
