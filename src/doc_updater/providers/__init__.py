"""LLM provider factory and exports."""

from enum import Enum

from doc_updater.providers.base import LLMProvider, ReviewRequest, ReviewResponse
from doc_updater.providers.claude import ClaudeProvider


class ProviderType(Enum):
    """Supported LLM provider types."""

    CLAUDE = "claude"
    # Future providers:
    # OPENAI = "openai"
    # GEMINI = "gemini"


_PROVIDERS: dict[ProviderType, type[LLMProvider]] = {
    ProviderType.CLAUDE: ClaudeProvider,
}


def get_provider(provider_type: ProviderType | str, **kwargs) -> LLMProvider:
    """Factory function to get LLM provider instance.

    Args:
        provider_type: The type of provider to create.
        **kwargs: Additional arguments passed to provider constructor.

    Returns:
        LLMProvider instance.

    Raises:
        ValueError: If provider type is unknown.
    """
    if isinstance(provider_type, str):
        try:
            provider_type = ProviderType(provider_type.lower())
        except ValueError:
            raise ValueError(f"Unknown provider: {provider_type}")

    provider_class = _PROVIDERS.get(provider_type)
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_type}")

    return provider_class(**kwargs)


__all__ = [
    "LLMProvider",
    "ReviewRequest",
    "ReviewResponse",
    "ClaudeProvider",
    "ProviderType",
    "get_provider",
]
