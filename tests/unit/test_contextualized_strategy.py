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


def make_complementaire():
    contenu = "\n".join(
        [
            "AVANTAGES SOCIAUX",
            "Le CNRS propose de nombreux avantages sociaux à ses agents.",
            "FORMATION",
            "La politique de formation du CNRS est ambitieuse et continue.",
            "SANTE",
            "Une couverture santé complémentaire est proposée aux agents.",
        ]
    )
    return SimpleNamespace(categorie="avantages", contenu=contenu)


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


def test_chunk_complementaire_calls_llm_client_once_per_chunk():
    llm_client = make_mock_llm_client()
    strategy = ContextualizedChunkingStrategy(llm_client=llm_client)
    complementaire = make_complementaire()

    chunks = strategy.chunk_complementaire(complementaire)

    assert llm_client.generate_context.call_count == len(chunks)
    for call in llm_client.generate_context.call_args_list:
        assert call.kwargs["document"] == complementaire.contenu
    for chunk in chunks:
        assert chunk.context == "Contexte généré."
        assert chunk.contextualized_content == f"Contexte généré.\n\n{chunk.content}"
