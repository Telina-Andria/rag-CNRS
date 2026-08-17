"""Indexation des chunks vectorisés dans Qdrant."""

import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from src.embedding.settings import QdrantSettings

# Namespace fixe pour dériver un id de point déterministe depuis chunk_id
# (uuid5) : ré-indexer le même chunk met à jour le point existant au lieu
# d'en créer un doublon.
_POINT_ID_NAMESPACE = uuid.UUID("a7e6b2a0-5f0e-4c2c-9c2e-6b1e2f8b6a1d")


def point_id_for(chunk_id: str) -> str:
    return str(uuid.uuid5(_POINT_ID_NAMESPACE, chunk_id))


class QdrantStore:
    """Wrapper autour du client Qdrant : création de collection et upsert."""

    def __init__(
        self,
        settings: QdrantSettings | None = None,
        client: QdrantClient | None = None,
    ):
        self.settings = settings or QdrantSettings()
        self.client = client or QdrantClient(host=self.settings.host, port=self.settings.port)

    def ensure_collection(self, vector_size: int) -> None:
        """Crée la collection si elle n'existe pas déjà."""
        if self.client.collection_exists(self.settings.collection_name):
            return
        self.client.create_collection(
            collection_name=self.settings.collection_name,
            vectors_config=VectorParams(
                size=vector_size, distance=Distance(self.settings.distance)
            ),
        )

    def upsert_chunks(self, chunks: list[dict], vectors: list[list[float]]) -> None:
        """Indexe (ou met à jour) une liste de chunks avec leurs vecteurs."""
        points = [
            PointStruct(
                id=point_id_for(chunk["chunk_id"]),
                vector=vector,
                payload=chunk,
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self.client.upsert(collection_name=self.settings.collection_name, points=points)
