"""
Construit les chunks de tous les documents sources (data/json/*.json) par
decoupage "heading-based", sur le meme schema que
data/exemple/codebase_chunks_exemple_source.json : une entree par document
source (doc_id, metadata, content = texte complet), avec une liste "chunks"
(chunk_id, original_index, content, metadata du chunk).

Deux familles de documents :
- concours.json : champs structures (Mission, Contexte, Activites,
  Competences) deja identifies a l'extraction -> un chunk par rubrique et
  par poste (voir HEADINGS/render_poste).
- guide_candidat.json, instituts.json, accompagnement.json, avantages.json,
  remuneration.json : texte libre issu de PDF/HTML -> les rubriques ne sont
  pas balisees, on les detecte par heuristique (voir heading_chunking.py)
  a partir des lignes de texte (titres tout en MAJUSCULES ou courtes lignes
  isolees suivies d'un paragraphe). En cas d'echec de detection (texte trop
  desordonne pour une heuristique fiable), on retombe sur un chunk par page.
  remuneration.json ajoute un chunk dedie par tableau structure.

Entree  : data/json/*.json
Sortie  : data/chunks/{nom}_chunk.json
"""

import json
from pathlib import Path

from src.chunking.common.heading_chunking import clean_pages, heading_chunk

DATA_DIR = Path(__file__).resolve().parents[3]
IN_DIR = DATA_DIR / "data" / "json"
OUT_DIR = DATA_DIR / "data" / "chunks"


def write_chunks(name, docs):
    out_path = OUT_DIR / f"{name}_chunk.json"
    out_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    n_chunks = sum(len(d["chunks"]) for d in docs)
    print(f"OK: {out_path} ({n_chunks} chunk(s) pour {len(docs)} document(s))")


# ---------------------------------------------------------------------------
# CONCOURS : rubriques deja structurees (mission/contexte/activites/competences)
# ---------------------------------------------------------------------------

CONCOURS_HEADINGS = [
    ("mission", "Mission"),
    ("contexte", "Contexte"),
    ("activites", "Activités"),
    ("competences", "Compétences"),
]


def render_poste(poste):
    """Reconstruit le texte complet d'un poste (toutes rubriques, avec
    headings), utilise pour le champ "content" du document."""
    parts = [f"Poste {poste['poste_num']} - {poste['affectation']} ({poste['groupe_fonction']})"]
    for field_key, label in CONCOURS_HEADINGS:
        text = poste.get(field_key, "").strip()
        if text:
            parts.append(f"## {label}\n\n{text}")
    return "\n\n".join(parts)


def build_concours_chunks():
    with open(IN_DIR / "concours.json", encoding="utf-8") as f:
        raw_docs = json.load(f)

    docs = []
    for doc in raw_docs:
        full_content = "\n\n".join(render_poste(p) for p in doc["postes"])

        chunks = []
        idx = 0
        for poste in doc["postes"]:
            for field_key, label in CONCOURS_HEADINGS:
                text = poste.get(field_key, "").strip()
                if not text:
                    continue
                chunks.append(
                    {
                        "chunk_id": f"{doc['doc_id']}_chunk_{idx}",
                        "original_index": idx,
                        "content": f"## {label}\n\n{text}",
                        "metadata": {
                            "poste_num": poste["poste_num"],
                            "affectation": poste["affectation"],
                            "groupe_fonction": poste["groupe_fonction"],
                            "heading": label,
                        },
                    }
                )
                idx += 1

        docs.append(
            {
                "doc_id": doc["doc_id"],
                "source_file": doc["source_file"],
                "category": doc["category"],
                "concours_num": doc["concours_num"],
                "discipline": doc["discipline"],
                "corps": doc["corps"],
                "nb_postes_declares": doc["nb_postes_declares"],
                "emploi_type": doc["emploi_type"],
                "content": full_content,
                "chunks": chunks,
            }
        )

    return docs


# ---------------------------------------------------------------------------
# DOCUMENTS PDF GENERIQUES (guide_candidat, instituts, accompagnement, avantages)
# ---------------------------------------------------------------------------


def build_generic_pdf_chunks(name):
    with open(IN_DIR / f"{name}.json", encoding="utf-8") as f:
        raw_docs = json.load(f)

    docs = []
    for doc in raw_docs:
        lines_with_pages = clean_pages(doc["pages"])
        sections, method = heading_chunk(lines_with_pages)

        content = "\n".join(line for line, _ in lines_with_pages)

        chunks = []
        for idx, section in enumerate(sections):
            heading_label = section["heading"] or "Introduction"
            chunks.append(
                {
                    "chunk_id": f"{doc['doc_id']}_chunk_{idx}",
                    "original_index": idx,
                    "content": f"## {heading_label}\n\n{section['body']}",
                    "metadata": {
                        "heading": section["heading"],
                        "page_start": section["page_start"],
                        "page_end": section["page_end"],
                        "chunking_method": method,
                    },
                }
            )

        docs.append(
            {
                "doc_id": doc["doc_id"],
                "source_file": doc["source_file"],
                "category": doc["category"],
                "title": doc["title"],
                "content": content,
                "chunks": chunks,
            }
        )

    return docs


# ---------------------------------------------------------------------------
# REMUNERATION (texte + tableaux structures)
# ---------------------------------------------------------------------------


def render_table(table):
    lines = [f"## Tableau {table['table_index'] + 1}", ""]
    for row in table["rows"]:
        cells = [f"{h}: {v}" for h, v in zip(table["headers"], row)]
        lines.append(" ; ".join(cells))
    return "\n".join(lines)


def build_remuneration_chunks():
    with open(IN_DIR / "remuneration.json", encoding="utf-8") as f:
        raw_docs = json.load(f)

    docs = []
    for doc in raw_docs:
        chunks = []
        idx = 0

        for table in doc["tables"]:
            chunks.append(
                {
                    "chunk_id": f"{doc['doc_id']}_chunk_{idx}",
                    "original_index": idx,
                    "content": render_table(table),
                    "metadata": {
                        "heading": f"Tableau {table['table_index'] + 1}",
                        "chunking_method": "table",
                    },
                }
            )
            idx += 1

        text_lines = [(l, None) for l in doc["text"].split("\n") if l.strip()]
        sections, method = heading_chunk(text_lines)
        for section in sections:
            heading_label = section["heading"] or "Introduction"
            chunks.append(
                {
                    "chunk_id": f"{doc['doc_id']}_chunk_{idx}",
                    "original_index": idx,
                    "content": f"## {heading_label}\n\n{section['body']}",
                    "metadata": {
                        "heading": section["heading"],
                        "chunking_method": method,
                    },
                }
            )
            idx += 1

        docs.append(
            {
                "doc_id": doc["doc_id"],
                "source_file": doc["source_file"],
                "category": doc["category"],
                "title": doc["title"],
                "content": doc["text"],
                "chunks": chunks,
            }
        )

    return docs


# ---------------------------------------------------------------------------


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    write_chunks("concours", build_concours_chunks())
    for name in ["guide_candidat", "instituts", "accompagnement", "avantages"]:
        write_chunks(name, build_generic_pdf_chunks(name))
    write_chunks("remuneration", build_remuneration_chunks())


if __name__ == "__main__":
    main()
