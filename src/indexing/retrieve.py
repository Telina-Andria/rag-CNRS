"""Récupération des chunks pertinents pour une requête (recherche hybride
dense + BM25 sparse dans Qdrant)."""

from src.embedding.embedder import SentenceTransformerEmbedder
from src.indexing.store import QdrantStore


def retrieve(
    query: str,
    embedder: SentenceTransformerEmbedder | None = None,
    store: QdrantStore | None = None,
    limit: int = 10,
) -> list[dict]:
    """Encode la requête et retourne les chunks les plus pertinents (payload)
    triés par score de fusion RRF."""
    embedder = embedder or SentenceTransformerEmbedder()
    store = store or QdrantStore()

    dense_vector = embedder.embed_query(query)
    results = store.hybrid_search(dense_vector=dense_vector, query_text=query, limit=limit)

    return [point.payload for point in results.points]
