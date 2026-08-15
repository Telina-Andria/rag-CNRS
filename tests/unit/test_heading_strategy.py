from types import SimpleNamespace

from src.chunking.heading import HeadingChunkingStrategy


def make_concour():
    content = (
        "Poste 1 - PARIS 05 (Groupe 3)\n"
        "Mission:\nAnalyser des données.\n\n"
        "Activités:\nDévelopper des pipelines.\n\n"
        "Compétences:\nPython, R.\n\n"
        "Contexte:\nUnité de recherche."
    )
    return SimpleNamespace(
        numero="1",
        discipline="A : Sciences du vivant",
        corps="Ingénieur de recherche",
        emploi_type="Ingénieure ou ingénieur biologiste",
        content=content,
    )


def make_complementaire():
    contenu = "\n".join(
        [
            "AVANTAGES SOCIAUX",
            "Le CNRS propose de nombreux avantages sociaux à ses agents.",
            "FORMATION",
            "La politique de formation du CNRS est ambitieuse et continue.",
        ]
    )
    return SimpleNamespace(categorie="avantages", contenu=contenu)


def test_chunk_concour_produces_one_chunk_per_rubrique():
    strategy = HeadingChunkingStrategy()
    chunks = strategy.chunk_concour(make_concour())

    assert len(chunks) == 4
    headings = [c.metadata["heading"] for c in chunks]
    assert headings == ["Mission", "Contexte", "Activités", "Compétences"]
    assert all(c.metadata["numero"] == "1" for c in chunks)
    assert chunks[0].chunk_id == "1_chunk_0"


def test_chunk_complementaire_produces_sections_with_heading_metadata():
    strategy = HeadingChunkingStrategy()
    chunks = strategy.chunk_complementaire(make_complementaire())

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.metadata["categorie"] == "avantages"
        assert "chunking_method" in chunk.metadata
        assert chunk.metadata["page_start"] is None
        assert chunk.metadata["page_end"] is None
