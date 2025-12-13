"""Custom exceptions for doc-updater."""


class DocUpdaterError(Exception):
    """Base exception for doc-updater."""

    pass


class DocumentParseError(DocUpdaterError):
    """Raised when a document cannot be parsed."""

    pass


class ProviderError(DocUpdaterError):
    """Raised when an LLM provider encounters an error."""

    pass


class ProviderConfigError(ProviderError):
    """Raised when a provider is not properly configured."""

    pass


class ReviewError(DocUpdaterError):
    """Raised when a review operation fails."""

    pass
