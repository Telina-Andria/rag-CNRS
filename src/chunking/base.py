from abc import ABC, abstractmethod

from src.chunking.models import Chunk
from src.models.complementaire import Complementaire
from src.models.concour import Concour


class ChunkingStrategy(ABC):
    """Stratégie de découpage en chunks (pattern Strategy)."""

    @abstractmethod
    def chunk_concour(self, concour: Concour) -> list[Chunk]:
        """Découpe un concours en chunks."""

    @abstractmethod
    def chunk_complementaire(self, complementaire: Complementaire) -> list[Chunk]:
        """Découpe un document complémentaire en chunks."""
