from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingSettings(BaseSettings):
    """Configuration du modèle d'embedding (sentence-transformers)."""

    model_name: str = Field(
        default="BAAI/bge-m3",
        description=(
            "Modèle sentence-transformers utilisé (multilingue, contexte jusqu'à "
            "8192 tokens, usage symétrique document/requête)"
        ),
    )
    batch_size: int = Field(default=32, description="Taille de lot pour l'encodage")
    device: str | None = Field(
        default=None, description="Device torch ('cpu', 'cuda'...) ; auto-détecté si None"
    )
    # BAAI/bge-m3 n'a pas besoin de préfixe d'instruction (contrairement à e5
    # ou Qwen3-Embedding) : laissés vides par défaut, mais configurables si le
    # modèle est changé pour un modèle asymétrique.
    passage_prefix: str = Field(default="")
    query_prefix: str = Field(default="")

    model_config = SettingsConfigDict(env_prefix="EMBEDDING_", env_file=".env", extra="ignore")


class QdrantSettings(BaseSettings):
    """Configuration de la connexion Qdrant et de la collection cible."""

    host: str = Field(default="localhost", description="Hôte Qdrant")
    port: int = Field(default=6333, description="Port HTTP Qdrant")
    collection_name: str = Field(default="rag_cnrs_chunks", description="Nom de la collection")
    distance: str = Field(default="Cosine", description="Métrique de distance")

    model_config = SettingsConfigDict(env_prefix="QDRANT_", env_file=".env", extra="ignore")
