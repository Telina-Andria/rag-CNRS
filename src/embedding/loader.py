"""Chargement des chunks (produits par le pipeline de chunking) depuis un
répertoire de fichiers JSON, prêts à être encodés et indexés dans Qdrant."""

import json
from pathlib import Path


def load_chunks(chunks_dir: Path) -> list[dict]:
    """Charge tous les chunks des fichiers `*.json` d'un répertoire (un
    fichier par catégorie, chacun contenant une liste de chunks)."""
    chunks = []
    for path in sorted(chunks_dir.glob("*.json")):
        chunks.extend(json.loads(path.read_text(encoding="utf-8")))
    return chunks


def chunk_text(chunk: dict) -> str:
    """Texte à encoder pour un chunk : le contenu contextualisé si présent
    (technique "contextual retrieval"), sinon le contenu brut."""
    return chunk.get("contextualized_content") or chunk["content"]
