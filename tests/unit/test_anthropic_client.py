from types import SimpleNamespace
from unittest.mock import MagicMock

from src.llm.anthropic_client import AnthropicContextGenerator
from src.llm.settings import AnthropicSettings


def make_stub_client(response_text="Ceci situe le chunk dans le document."):
    stub = MagicMock()
    stub.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(text=response_text)]
    )
    return stub


def test_generate_context_returns_stripped_text():
    stub_client = make_stub_client("  Contexte généré.  ")
    generator = AnthropicContextGenerator(settings=AnthropicSettings(), client=stub_client)

    context = generator.generate_context(document="Document complet.", chunk_content="Un extrait.")

    assert context == "Contexte généré."


def test_generate_context_calls_client_with_configured_model():
    stub_client = make_stub_client()
    settings = AnthropicSettings(model="claude-haiku-4-5-20251001", max_tokens=200)
    generator = AnthropicContextGenerator(settings=settings, client=stub_client)

    generator.generate_context(document="Document complet.", chunk_content="Un extrait.")

    stub_client.messages.create.assert_called_once()
    _, kwargs = stub_client.messages.create.call_args
    assert kwargs["model"] == "claude-haiku-4-5-20251001"
    assert kwargs["max_tokens"] == 200
    assert "Document complet." in kwargs["messages"][0]["content"]
    assert "Un extrait." in kwargs["messages"][0]["content"]


def test_generate_context_never_hits_network_without_key():
    # settings.api_key vide, aucune clé requise puisque le client est injecté
    stub_client = make_stub_client()
    settings = AnthropicSettings(api_key="")
    generator = AnthropicContextGenerator(settings=settings, client=stub_client)

    context = generator.generate_context(document="Doc.", chunk_content="Chunk.")

    assert context
    stub_client.messages.create.assert_called_once()
