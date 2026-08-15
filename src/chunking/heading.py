"""Stratégie de chunking heuristique "heading-based", gratuite (pas de LLM).

Réutilise `heading_chunk()` et `CONCOURS_HEADINGS`
(`src/chunking/heading_chunking.py`, `src/chunking/build_chunks.py`), aucune
duplication de l'heuristique de détection de titres.

`clean_pages()` n'est pas réutilisable ici : elle attend une liste de pages
paginées (`{"page_num":..., "text":...}`), information qu'on n'a plus une
fois les documents en base (`Complementaire.contenu` est un texte à plat).
On se contente donc de découper `contenu` en lignes non vides, sans page
associée (`page_start`/`page_end` valent `None`), comme le fait déjà
`build_remuneration_chunks()` pour `doc["text"]` dans `build_chunks.py`.
"""

from src.chunking.base import ChunkingStrategy
from src.chunking.build_chunks import CONCOURS_HEADINGS
from src.chunking.concours_parser import parse_concour_content
from src.chunking.heading_chunking import heading_chunk
from src.chunking.models import Chunk
from src.models.complementaire import Complementaire
from src.models.concour import Concour


class HeadingChunkingStrategy(ChunkingStrategy):
    """Découpage gratuit, heuristique pure Python (pas de LLM)."""

    def chunk_concour(self, concour: Concour) -> list[Chunk]:
        postes = parse_concour_content(concour.content)

        chunks = []
        idx = 0
        for poste in postes:
            for field_key, label in CONCOURS_HEADINGS:
                text = getattr(poste, field_key).strip()
                if not text:
                    continue
                chunks.append(
                    Chunk(
                        chunk_id=f"{concour.numero}_chunk_{idx}",
                        content=f"## {label}\n\n{text}",
                        metadata={
                            "numero": concour.numero,
                            "discipline": concour.discipline,
                            "corps": concour.corps,
                            "emploi_type": concour.emploi_type,
                            "poste_num": poste.poste_num,
                            "affectation": poste.affectation,
                            "groupe_fonction": poste.groupe_fonction,
                            "heading": label,
                        },
                    )
                )
                idx += 1
        return chunks

    def chunk_complementaire(self, complementaire: Complementaire) -> list[Chunk]:
        lines_with_pages = [
            (line, None) for line in complementaire.contenu.split("\n") if line.strip()
        ]
        sections, method = heading_chunk(lines_with_pages)

        chunks = []
        for idx, section in enumerate(sections):
            heading_label = section["heading"] or "Introduction"
            chunks.append(
                Chunk(
                    chunk_id=f"{complementaire.categorie}_chunk_{idx}",
                    content=f"## {heading_label}\n\n{section['body']}",
                    metadata={
                        "categorie": complementaire.categorie,
                        "heading": section["heading"],
                        "page_start": section["page_start"],
                        "page_end": section["page_end"],
                        "chunking_method": method,
                    },
                )
            )
        return chunks
