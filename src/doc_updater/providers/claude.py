"""Anthropic Claude LLM provider."""

import os
import re

from anthropic import AsyncAnthropic

from doc_updater.exceptions import ProviderConfigError, ProviderError
from doc_updater.providers.base import LLMProvider, ReviewRequest, ReviewResponse


class ClaudeProvider(LLMProvider):
    """Anthropic Claude LLM provider."""

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = 8192,
    ):
        """Initialize Claude provider.

        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var.
            model: Model to use. Defaults to claude-sonnet-4-20250514.
            max_tokens: Maximum tokens in response.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens
        self._client: AsyncAnthropic | None = None

    @property
    def client(self) -> AsyncAnthropic:
        """Get or create the Anthropic client."""
        if self._client is None:
            if not self.api_key:
                raise ProviderConfigError("ANTHROPIC_API_KEY not set")
            self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client

    async def review(self, request: ReviewRequest) -> ReviewResponse:
        """Send document to Claude for review.

        Args:
            request: ReviewRequest with document content and prompts.

        Returns:
            ReviewResponse with updated content and summary.

        Raises:
            ProviderError: If the API call fails.
        """
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=request.system_prompt,
                messages=[{"role": "user", "content": self._build_user_message(request)}],
            )

            return self._parse_response(message, request.content)
        except ProviderConfigError:
            raise
        except Exception as e:
            raise ProviderError(f"Claude API error: {e}") from e

    def _build_user_message(self, request: ReviewRequest) -> str:
        """Build the user message with document content."""
        parts = []

        if request.context:
            parts.append(f"Context:\n{request.context}\n")

        parts.append(request.user_prompt)
        parts.append(f"\n\n<document>\n{request.content}\n</document>")

        return "\n".join(parts)

    def _parse_response(self, message, original_content: str) -> ReviewResponse:
        """Parse Claude's response into ReviewResponse."""
        response_text = message.content[0].text

        # Extract updated document from XML tags
        doc_match = re.search(r"<updated_document>\s*(.*?)\s*</updated_document>", response_text, re.DOTALL)

        if doc_match:
            updated_content = doc_match.group(1).strip()
        else:
            # If no tags, assume the whole response is the document
            # (fallback for simpler responses)
            updated_content = response_text.strip()

        # Extract summary
        summary_match = re.search(r"<summary>\s*(.*?)\s*</summary>", response_text, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else "Document reviewed"

        # Determine if content changed
        changed = updated_content.strip() != original_content.strip()

        return ReviewResponse(
            updated_content=updated_content,
            summary=summary,
            changed=changed,
        )

    def validate_config(self) -> bool:
        """Check that ANTHROPIC_API_KEY is set."""
        return bool(self.api_key)
