"""Indexation des chunks vectorisés dans Qdrant (recherche hybride
dense + BM25 sparse)."""

import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    Fusion,
    FusionQuery,
    Modifier,
    PointStruct,
    Prefetch,
    SparseVectorParams,
    VectorParams,
)

from src.indexing.settings import QdrantSettings
from src.indexing.sparse import text_to_sparse_vector

# Namespace fixe pour dériver un id de point déterministe depuis chunk_id
# (uuid5) : ré-indexer le même chunk met à jour le point existant au lieu
# d'en créer un doublon.
_POINT_ID_NAMESPACE = uuid.UUID("a7e6b2a0-5f0e-4c2c-9c2e-6b1e2f8b6a1d")


def point_id_for(chunk_id: str) -> str:
    return str(uuid.uuid5(_POINT_ID_NAMESPACE, chunk_id))


class QdrantStore:
    """Wrapper autour du client Qdrant : création de collection, upsert et
    recherche hybride (dense + BM25 sparse, fusionnés par RRF)."""

    def __init__(
        self,
        settings: QdrantSettings | None = None,
        client: QdrantClient | None = None,
    ):
        self.settings = settings or QdrantSettings()
        self.client = client or QdrantClient(host=self.settings.host, port=self.settings.port)

    def ensure_collection(self, vector_size: int) -> None:
        """Crée la collection (vecteur dense nommé + vecteur sparse BM25 avec
        IDF calculé par Qdrant) si elle n'existe pas déjà."""
        if self.client.collection_exists(self.settings.collection_name):
            return
        self.client.create_collection(
            collection_name=self.settings.collection_name,
            vectors_config={
                self.settings.dense_vector_name: VectorParams(
                    size=vector_size, distance=Distance(self.settings.distance)
                )
            },
            sparse_vectors_config={
                self.settings.sparse_vector_name: SparseVectorParams(modifier=Modifier.IDF)
            },
        )

    def upsert_chunks(
        self, chunks: list[dict], vectors: list[list[float]], texts: list[str]
    ) -> None:
        """Indexe (ou met à jour) une liste de chunks avec leur vecteur dense
        et le vecteur sparse BM25 dérivé de `texts` (texte encodé pour chaque
        chunk, cf. `src/embedding/loader.chunk_text`)."""
        points = [
            PointStruct(
                id=point_id_for(chunk["chunk_id"]),
                vector={
                    self.settings.dense_vector_name: vector,
                    self.settings.sparse_vector_name: text_to_sparse_vector(text),
                },
                payload=chunk,
            )
            for chunk, vector, text in zip(chunks, vectors, texts, strict=True)
        ]
        self.client.upsert(collection_name=self.settings.collection_name, points=points)

    def hybrid_search(self, dense_vector: list[float], query_text: str, limit: int = 10):
        """Recherche hybride : préfetch dense + préfetch BM25 sparse,
        fusionnés par Reciprocal Rank Fusion (RRF)."""
        return self.client.query_points(
            collection_name=self.settings.collection_name,
            prefetch=[
                Prefetch(
                    query=dense_vector,
                    using=self.settings.dense_vector_name,
                    limit=limit * 2,
                ),
                Prefetch(
                    query=text_to_sparse_vector(query_text),
                    using=self.settings.sparse_vector_name,
                    limit=limit * 2,
                ),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=limit,
        )
