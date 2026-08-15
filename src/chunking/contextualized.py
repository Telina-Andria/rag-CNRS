"""Stratégie de chunking contextualisée (technique "contextual retrieval").

Pour les concours : gabarit Python déterministe à partir des métadonnées du
chunk, sans appel API (évite d'envoyer des centaines de chunks déjà
structurés à l'API).
Pour les complémentaires : un appel réel à `llm_client.generate_context` par
chunk, avec le document entier (`complementaire.contenu`) comme contexte.
"""

from src.chunking.base import ChunkingStrategy
from src.chunking.heading import HeadingChunkingStrategy
from src.chunking.models import Chunk
from src.llm.anthropic_client import AnthropicContextGenerator
from src.models.complementaire import Complementaire
from src.models.concour import Concour

_CONCOUR_CONTEXT_TEMPLATE = (
    "Ce chunk fait partie du concours {numero} ({discipline}, {corps}), "
    "rubrique « {heading} » du poste {poste_num} ({affectation}, {groupe_fonction})."
)


class ContextualizedChunkingStrategy(ChunkingStrategy):
    """Ajoute un contexte par chunk, via `HeadingChunkingStrategy` en interne."""

    def __init__(
        self,
        heading_strategy: HeadingChunkingStrategy | None = None,
        llm_client: AnthropicContextGenerator | None = None,
    ):
        self.heading_strategy = heading_strategy or HeadingChunkingStrategy()
        self.llm_client = llm_client or AnthropicContextGenerator()

    def chunk_concour(self, concour: Concour) -> list[Chunk]:
        chunks = self.heading_strategy.chunk_concour(concour)
        for chunk in chunks:
            context = _CONCOUR_CONTEXT_TEMPLATE.format(**chunk.metadata)
            chunk.context = context
            chunk.contextualized_content = f"{context}\n\n{chunk.content}"
        return chunks

    def chunk_complementaire(self, complementaire: Complementaire) -> list[Chunk]:
        chunks = self.heading_strategy.chunk_complementaire(complementaire)
        for chunk in chunks:
            context = self.llm_client.generate_context(
                document=complementaire.contenu, chunk_content=chunk.content
            )
            chunk.context = context
            chunk.contextualized_content = f"{context}\n\n{chunk.content}"
        return chunks
