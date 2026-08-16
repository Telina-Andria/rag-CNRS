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


def make_page_rows():
    return [
        SimpleNamespace(
            page_num=1,
            contenu="AVANTAGES SOCIAUX\nLe CNRS propose de nombreux avantages sociaux à ses "
            "agents.",
        ),
        SimpleNamespace(
            page_num=2,
            contenu="FORMATION\nLa politique de formation du CNRS est ambitieuse et continue.",
        ),
    ]


def make_remuneration_rows():
    return [
        SimpleNamespace(
            type="texte",
            contenu="REMUNERATION\nVotre rémunération se compose du traitement indiciaire.",
        ),
        SimpleNamespace(type="tableau", contenu="Grade | Indice\nIR | 500"),
    ]


def test_chunk_concour_produces_one_chunk_per_rubrique():
    strategy = HeadingChunkingStrategy()
    chunks = strategy.chunk_concour(make_concour())

    assert len(chunks) == 4
    headings = [c.metadata["heading"] for c in chunks]
    assert headings == ["Mission", "Contexte", "Activités", "Compétences"]
    assert all(c.metadata["numero"] == "1" for c in chunks)
    assert chunks[0].chunk_id == "1_chunk_0"


def test_chunk_page_documents_produces_sections_with_real_pages():
    strategy = HeadingChunkingStrategy()
    chunks = strategy.chunk_page_documents("avantages", make_page_rows())

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.metadata["categorie"] == "avantages"
        assert "chunking_method" in chunk.metadata
        assert chunk.metadata["page_start"] is not None
        assert chunk.metadata["page_end"] is not None


def test_chunk_remuneration_produces_table_and_text_chunks():
    strategy = HeadingChunkingStrategy()
    chunks = strategy.chunk_remuneration(make_remuneration_rows())

    methods = {c.metadata["chunking_method"] for c in chunks}
    assert "table" in methods
    assert any(c.metadata["chunking_method"] != "table" for c in chunks)
    assert all(c.metadata["categorie"] == "remuneration" for c in chunks)
