"""Client Anthropic pour la technique "contextual retrieval" : génère un
court contexte par chunk à partir du document complet, pour améliorer la
recherche ultérieure des chunks isolés de leur document d'origine."""

import anthropic

from src.llm.settings import AnthropicSettings

_PROMPT_TEMPLATE = """Voici le document complet :
<document>
{document}
</document>

Voici un extrait (chunk) de ce document :
<chunk>
{chunk_content}
</chunk>

Rédige un court contexte (2 à 3 phrases maximum, en français) qui situe cet \
extrait dans le document complet, afin d'améliorer sa recherche ultérieure. \
Réponds uniquement avec le contexte, sans préambule."""


class AnthropicContextGenerator:
    """Génère un contexte par chunk avec Claude."""

    def __init__(self, settings: AnthropicSettings | None = None, client=None):
        self.settings = settings or AnthropicSettings()
        self.client = client or anthropic.Anthropic(api_key=self.settings.api_key)

    def generate_context(self, document: str, chunk_content: str) -> str:
        """Appelle Claude pour générer un contexte court situant le chunk dans le document."""
        response = self.client.messages.create(
            model=self.settings.model,
            max_tokens=self.settings.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": _PROMPT_TEMPLATE.format(
                        document=document, chunk_content=chunk_content
                    ),
                }
            ],
        )
        return response.content[0].text.strip()
