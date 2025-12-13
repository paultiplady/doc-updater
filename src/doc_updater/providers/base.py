"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ReviewRequest:
    """Request to review a document.

    Attributes:
        content: The markdown content to review.
        system_prompt: System prompt for the LLM.
        user_prompt: User prompt describing what to review.
        context: Optional additional context.
    """

    content: str
    system_prompt: str
    user_prompt: str
    context: str | None = None


@dataclass
class ReviewResponse:
    """Response from LLM with updated content.

    Attributes:
        updated_content: The updated markdown content.
        summary: Brief description of changes made.
        changed: Whether any changes were made.
    """

    updated_content: str
    summary: str
    changed: bool


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def review(self, request: ReviewRequest) -> ReviewResponse:
        """Send document for review and return updated content.

        Args:
            request: ReviewRequest with document content and prompts.

        Returns:
            ReviewResponse with updated content and summary.

        Raises:
            ProviderError: If the review fails.
        """
        ...

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate that provider is properly configured.

        Returns:
            True if provider is ready to use.
        """
        ...
