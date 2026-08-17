"""Stratégie de chunking heuristique "heading-based", gratuite (pas de LLM).

Réutilise `heading_chunk()` et `CONCOURS_HEADINGS`
(`src/chunking/heading_chunking.py`, `src/chunking/build_chunks.py`), aucune
duplication de l'heuristique de détection de titres.

`avantages`, `accompagnement`, `guide_candidat` et `instituts` ont une ligne
par page en base (`page_num`, `contenu`) : on reconstruit la liste
(ligne, page_num) sur toutes les pages de la catégorie avant de lancer
`heading_chunk`, ce qui permet à `page_start`/`page_end` d'être renseignés.
`remuneration` n'a pas de pagination (`type` texte/tableau) : les lignes de
type "tableau" deviennent chacune un chunk dédié, les lignes "texte" suivent
le même découpage heuristique que les autres catégories mais sans page
(comme le faisait déjà `build_remuneration_chunks()` dans `build_chunks.py`).
"""

from src.chunking.base import ChunkingStrategy, PageDocument
from src.chunking.build_chunks import CONCOURS_HEADINGS
from src.chunking.concours_parser import parse_concour_content
from src.chunking.heading_chunking import heading_chunk
from src.chunking.models import Chunk
from src.models.concour import Concour
from src.models.remuneration import Remuneration


class HeadingChunkingStrategy(ChunkingStrategy):
    """Découpage gratuit, heuristique pure Python."""

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

    def chunk_page_documents(self, categorie: str, rows: list[PageDocument]) -> list[Chunk]:
        rows_by_page = sorted(rows, key=lambda row: row.page_num)
        lines_with_pages = [
            (line, row.page_num)
            for row in rows_by_page
            for line in row.contenu.split("\n")
            if line.strip()
        ]
        sections, method = heading_chunk(lines_with_pages)

        chunks = []
        for idx, section in enumerate(sections):
            heading_label = section["heading"] or "Introduction"
            chunks.append(
                Chunk(
                    chunk_id=f"{categorie}_chunk_{idx}",
                    content=f"## {heading_label}\n\n{section['body']}",
                    metadata={
                        "categorie": categorie,
                        "heading": section["heading"],
                        "page_start": section["page_start"],
                        "page_end": section["page_end"],
                        "chunking_method": method,
                    },
                )
            )
        return chunks

    def chunk_remuneration(self, rows: list[Remuneration]) -> list[Chunk]:
        chunks = []
        idx = 0

        for row in rows:
            if row.type != "tableau":
                continue
            chunks.append(
                Chunk(
                    chunk_id=f"remuneration_chunk_{idx}",
                    content=row.contenu,
                    metadata={
                        "categorie": "remuneration",
                        "heading": f"Tableau {idx + 1}",
                        "chunking_method": "table",
                    },
                )
            )
            idx += 1

        for row in rows:
            if row.type != "texte":
                continue
            lines_with_pages = [(line, None) for line in row.contenu.split("\n") if line.strip()]
            sections, method = heading_chunk(lines_with_pages)
            for section in sections:
                heading_label = section["heading"] or "Introduction"
                chunks.append(
                    Chunk(
                        chunk_id=f"remuneration_chunk_{idx}",
                        content=f"## {heading_label}\n\n{section['body']}",
                        metadata={
                            "categorie": "remuneration",
                            "heading": section["heading"],
                            "chunking_method": method,
                        },
                    )
                )
                idx += 1

        return chunks
