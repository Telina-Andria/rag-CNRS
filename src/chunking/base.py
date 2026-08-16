from abc import ABC, abstractmethod

from src.chunking.models import Chunk
from src.models.accompagnement import Accompagnement
from src.models.avantage import Avantage
from src.models.concour import Concour
from src.models.guide_candidat import GuideCandidat
from src.models.institut import Institut
from src.models.remuneration import Remuneration

PageDocument = Avantage | Accompagnement | GuideCandidat | Institut


class ChunkingStrategy(ABC):
    """Stratégie de découpage en chunks (pattern Strategy)."""

    @abstractmethod
    def chunk_concour(self, concour: Concour) -> list[Chunk]:
        """Découpe un concours en chunks."""

    @abstractmethod
    def chunk_page_documents(self, categorie: str, rows: list[PageDocument]) -> list[Chunk]:
        """Découpe les pages d'une catégorie "une ligne par page" (avantages,
        accompagnement, guide_candidat, instituts) en chunks."""

    @abstractmethod
    def chunk_remuneration(self, rows: list[Remuneration]) -> list[Chunk]:
        """Découpe les lignes (texte + tableaux) de la table remuneration en chunks."""
