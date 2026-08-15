from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnthropicSettings(BaseSettings):
    """Configuration du client Anthropic (contextual retrieval)."""

    api_key: str = Field(default="", description="Clé API Anthropic")
    model: str = Field(default="claude-haiku-4-5-20251001", description="Modèle Anthropic utilisé")
    max_tokens: int = Field(default=300, description="Nombre max de tokens en sortie")

    model_config = SettingsConfigDict(env_prefix="ANTHROPIC_", env_file=".env", extra="ignore")
