"""Front-matter configuration schema for document review."""

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass
class ReviewConfig:
    """Configuration extracted from document front-matter.

    Attributes:
        auto_review: Whether this document should be automatically reviewed.
        review_prompt: Custom prompt for reviewing this document.
        review_context: Additional context to provide to the LLM.
        last_reviewed: Date when the document was last reviewed.
        review_interval_days: Minimum days between reviews.
    """

    auto_review: bool = False
    review_prompt: str | None = None
    review_context: str | None = None
    last_reviewed: date | None = None
    review_interval_days: int = 30

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReviewConfig":
        """Parse front-matter dict into ReviewConfig.

        Args:
            data: Dictionary from YAML front-matter.

        Returns:
            ReviewConfig instance with parsed values.
        """
        last_reviewed = data.get("last_reviewed")
        if isinstance(last_reviewed, str):
            last_reviewed = date.fromisoformat(last_reviewed)
        elif isinstance(last_reviewed, date):
            pass  # Already a date
        else:
            last_reviewed = None

        return cls(
            auto_review=bool(data.get("auto_review", False)),
            review_prompt=data.get("review_prompt"),
            review_context=data.get("review_context"),
            last_reviewed=last_reviewed,
            review_interval_days=int(data.get("review_interval_days", 30)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert back to dict for serialization.

        Returns:
            Dictionary suitable for YAML front-matter.
        """
        result: dict[str, Any] = {"auto_review": self.auto_review}

        if self.review_prompt:
            result["review_prompt"] = self.review_prompt
        if self.review_context:
            result["review_context"] = self.review_context
        if self.last_reviewed:
            result["last_reviewed"] = self.last_reviewed.isoformat()
        if self.review_interval_days != 30:
            result["review_interval_days"] = self.review_interval_days

        return result

    def needs_review(self) -> bool:
        """Check if document is due for review based on interval.

        Returns:
            True if the document should be reviewed.
        """
        if not self.auto_review:
            return False

        if self.last_reviewed is None:
            return True

        days_since_review = (date.today() - self.last_reviewed).days
        return days_since_review >= self.review_interval_days
