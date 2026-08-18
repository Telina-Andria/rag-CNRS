"""Tokenisation et vecteurs sparse pour la recherche BM25 dans Qdrant.

Le comptage des fréquences de termes se fait ici ; la pondération IDF est
calculée côté serveur par Qdrant (`Modifier.IDF` sur le vecteur sparse), pas
besoin de la répliquer côté client.
"""

import re
import unicodedata
import zlib
from collections import Counter

from qdrant_client.http.models import SparseVector

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Minuscule, retire les accents, découpe sur les suites alphanumériques."""
    normalized = unicodedata.normalize("NFKD", text.lower())
    stripped = "".join(c for c in normalized if not unicodedata.combining(c))
    return _TOKEN_RE.findall(stripped)


def _token_index(token: str) -> int:
    """Index sparse stable pour un token (hash déterministe entre process,
    contrairement à `hash()` qui dépend de `PYTHONHASHSEED`)."""
    return zlib.crc32(token.encode("utf-8"))


def text_to_sparse_vector(text: str) -> SparseVector:
    """Construit le vecteur sparse (indices, fréquences brutes) d'un texte."""
    counts = Counter(tokenize(text))
    indices = [_token_index(token) for token in counts]
    values = [float(count) for count in counts.values()]
    return SparseVector(indices=indices, values=values)
