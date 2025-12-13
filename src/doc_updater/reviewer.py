"""Core review orchestration logic."""

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from doc_updater.document import Document
from doc_updater.exceptions import DocumentParseError
from doc_updater.providers.base import LLMProvider, ReviewRequest, ReviewResponse

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = """You are a technical writer reviewing a living document.
Your task is to update the document with current, accurate information.

Guidelines:
- Preserve the document's structure, formatting, and style
- Update outdated information with current facts
- Keep the same writing tone
- Only make changes where information is outdated or incorrect
- If everything is up-to-date, return the document unchanged
- Do NOT add disclaimers or notes about your review process

Return your response in this format:
<updated_document>
[The complete updated markdown content - no front-matter, just the body]
</updated_document>

<summary>
[Brief bullet points of what was changed and why. If no changes, say "No updates needed."]
</summary>
"""

DEFAULT_USER_PROMPT = (
    "Please review and update this document. Check for outdated information, broken links, or inaccuracies."
)


@dataclass
class ReviewResult:
    """Result of reviewing a document.

    Attributes:
        path: Path to the document.
        changed: Whether the document was modified.
        summary: Description of changes made.
        error: Error message if review failed.
    """

    path: Path
    changed: bool
    summary: str
    error: str | None = None


class DocumentReviewer:
    """Orchestrates document review process."""

    def __init__(self, provider: LLMProvider):
        """Initialize reviewer with an LLM provider.

        Args:
            provider: LLM provider to use for reviews.
        """
        self.provider = provider

    def find_documents(self, directory: Path, recursive: bool = True) -> Iterator[Document]:
        """Find all documents marked for review.

        Args:
            directory: Directory to search.
            recursive: Whether to search recursively.

        Yields:
            Document instances that should be reviewed.
        """
        pattern = "**/*.md" if recursive else "*.md"

        for path in sorted(directory.glob(pattern)):
            try:
                doc = Document.load(path)
                if doc.should_review():
                    yield doc
            except DocumentParseError as e:
                logger.warning(f"Skipping {path}: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error loading {path}: {e}")

    async def review_document(
        self,
        document: Document,
        dry_run: bool = False,
    ) -> ReviewResult:
        """Review a single document and optionally apply changes.

        Args:
            document: Document to review.
            dry_run: If True, don't save changes.

        Returns:
            ReviewResult with outcome.
        """
        try:
            request = ReviewRequest(
                content=document.content,
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                user_prompt=document.config.review_prompt or DEFAULT_USER_PROMPT,
                context=document.config.review_context,
            )

            response: ReviewResponse = await self.provider.review(request)

            if response.changed and not dry_run:
                document.content = response.updated_content
                document.update_last_reviewed()
                document.save()

            return ReviewResult(
                path=document.path,
                changed=response.changed,
                summary=response.summary,
            )

        except Exception as e:
            logger.error(f"Failed to review {document.path}: {e}")
            return ReviewResult(
                path=document.path,
                changed=False,
                summary="",
                error=str(e),
            )

    async def review_all(
        self,
        directory: Path,
        dry_run: bool = False,
        recursive: bool = True,
    ) -> list[ReviewResult]:
        """Review all documents in directory.

        Args:
            directory: Directory to search for documents.
            dry_run: If True, don't save changes.
            recursive: Whether to search recursively.

        Returns:
            List of ReviewResult for each document processed.
        """
        results = []

        for doc in self.find_documents(directory, recursive):
            result = await self.review_document(doc, dry_run)
            results.append(result)

        return results
