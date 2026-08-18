from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QdrantSettings(BaseSettings):
    """Configuration de la connexion Qdrant et de la collection cible."""

    host: str = Field(default="localhost", description="Hôte Qdrant")
    port: int = Field(default=6333, description="Port HTTP Qdrant")
    collection_name: str = Field(default="rag_cnrs_chunks", description="Nom de la collection")
    distance: str = Field(default="Cosine", description="Métrique de distance")
    dense_vector_name: str = Field(default="dense", description="Nom du vecteur dense (bge-m3)")
    sparse_vector_name: str = Field(
        default="bm25", description="Nom du vecteur sparse (BM25, IDF calculé par Qdrant)"
    )

    model_config = SettingsConfigDict(env_prefix="QDRANT_", env_file=".env", extra="ignore")
