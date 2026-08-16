from types import SimpleNamespace
from unittest.mock import MagicMock

from src.chunking.contextualized import ContextualizedChunkingStrategy


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
        SimpleNamespace(
            page_num=3,
            contenu="SANTE\nUne couverture santé complémentaire est proposée aux agents.",
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


def make_mock_llm_client():
    mock = MagicMock()
    mock.generate_context.return_value = "Contexte généré."
    return mock


def test_chunk_concour_never_calls_llm_client():
    llm_client = make_mock_llm_client()
    strategy = ContextualizedChunkingStrategy(llm_client=llm_client)

    chunks = strategy.chunk_concour(make_concour())

    llm_client.generate_context.assert_not_called()
    assert len(chunks) == 4
    for chunk in chunks:
        assert chunk.context is not None
        assert chunk.contextualized_content == f"{chunk.context}\n\n{chunk.content}"


def test_chunk_page_documents_calls_llm_client_once_per_chunk():
    llm_client = make_mock_llm_client()
    strategy = ContextualizedChunkingStrategy(llm_client=llm_client)
    rows = make_page_rows()

    chunks = strategy.chunk_page_documents("avantages", rows)

    assert llm_client.generate_context.call_count == len(chunks)
    expected_document = "\n".join(row.contenu for row in rows)
    for call in llm_client.generate_context.call_args_list:
        assert call.kwargs["document"] == expected_document
    for chunk in chunks:
        assert chunk.context == "Contexte généré."
        assert chunk.contextualized_content == f"Contexte généré.\n\n{chunk.content}"


def test_chunk_remuneration_calls_llm_client_once_per_chunk():
    llm_client = make_mock_llm_client()
    strategy = ContextualizedChunkingStrategy(llm_client=llm_client)
    rows = make_remuneration_rows()

    chunks = strategy.chunk_remuneration(rows)

    assert llm_client.generate_context.call_count == len(chunks)
    for chunk in chunks:
        assert chunk.context == "Contexte généré."
        assert chunk.contextualized_content == f"Contexte généré.\n\n{chunk.content}"
