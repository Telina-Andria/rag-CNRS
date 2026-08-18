"""Stratégie de chunking contextualisée (technique "contextual retrieval").

Pour les concours : gabarit Python déterministe à partir des métadonnées du
chunk, sans appel API (évite d'envoyer des centaines de chunks déjà
structurés à l'API).
Pour les catégories complémentaires (avantages, accompagnement,
guide_candidat, instituts, remuneration) : un appel réel à
`llm_client.generate_context` par chunk, avec le texte complet de la
catégorie comme document de contexte.
"""

from src.chunking.common.models import Chunk
from src.chunking.interface.base import ChunkingStrategy, PageDocument
from src.chunking.strategies.heading import HeadingChunkingStrategy
from src.llm.anthropic_client import AnthropicContextGenerator
from src.models.concour import Concour
from src.models.remuneration import Remuneration

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

    def chunk_page_documents(self, categorie: str, rows: list[PageDocument]) -> list[Chunk]:
        chunks = self.heading_strategy.chunk_page_documents(categorie, rows)
        document = "\n".join(row.contenu for row in sorted(rows, key=lambda row: row.page_num))
        for chunk in chunks:
            context = self.llm_client.generate_context(
                document=document, chunk_content=chunk.content
            )
            chunk.context = context
            chunk.contextualized_content = f"{context}\n\n{chunk.content}"
        return chunks

    def chunk_remuneration(self, rows: list[Remuneration]) -> list[Chunk]:
        chunks = self.heading_strategy.chunk_remuneration(rows)
        document = "\n".join(row.contenu for row in rows)
        for chunk in chunks:
            context = self.llm_client.generate_context(
                document=document, chunk_content=chunk.content
            )
            chunk.context = context
            chunk.contextualized_content = f"{context}\n\n{chunk.content}"
        return chunks
