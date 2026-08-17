"""Encodage des chunks en vecteurs, via un modèle sentence-transformers
multilingue. Le modèle par défaut (`BAAI/bge-m3`) a un usage symétrique
document/requête : pas de préfixe d'instruction nécessaire (contrairement à
e5 ou Qwen3-Embedding), `passage_prefix`/`query_prefix` valent "" par défaut
mais restent configurables (voir `EmbeddingSettings`)."""

from sentence_transformers import SentenceTransformer

from src.embedding.settings import EmbeddingSettings


class SentenceTransformerEmbedder:
    """Encode des textes en vecteurs avec un modèle sentence-transformers."""

    def __init__(
        self,
        settings: EmbeddingSettings | None = None,
        model: SentenceTransformer | None = None,
    ):
        self.settings = settings or EmbeddingSettings()
        self.model = model or SentenceTransformer(
            self.settings.model_name, device=self.settings.device
        )

    @property
    def vector_size(self) -> int:
        return self.model.get_embedding_dimension()

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        """Encode des textes destinés à être indexés (chunks)."""
        prefixed = [f"{self.settings.passage_prefix}{text}" for text in texts]
        return self._encode(prefixed)

    def embed_query(self, text: str) -> list[float]:
        """Encode une requête de recherche."""
        return self._encode([f"{self.settings.query_prefix}{text}"])[0]

    def _encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts,
            batch_size=self.settings.batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return vectors.tolist()
