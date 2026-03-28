"""Document model for markdown files with front-matter."""

from datetime import date
from pathlib import Path

import frontmatter
import yaml

from doc_updater.exceptions import DocumentParseError
from doc_updater.frontmatter import ReviewConfig


class _MultilineYAMLHandler(frontmatter.YAMLHandler):
    """YAML handler that preserves block scalar style for multiline strings."""

    def export(self, metadata, **kwargs):
        def _str_representer(dumper, data):
            if "\n" in data:
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        class _Dumper(yaml.SafeDumper):
            pass

        _Dumper.add_representer(str, _str_representer)

        kwargs["Dumper"] = _Dumper
        kwargs.setdefault("default_flow_style", False)
        kwargs.setdefault("sort_keys", False)
        return yaml.dump(metadata, **kwargs)


class Document:
    """Represents a markdown document with YAML front-matter.

    Attributes:
        path: Path to the document file.
        config: ReviewConfig extracted from front-matter.
    """

    def __init__(self, path: Path, post: frontmatter.Post):
        """Initialize a Document.

        Args:
            path: Path to the document file.
            post: Parsed frontmatter.Post object.
        """
        self.path = path
        self._post = post
        self.config = ReviewConfig.from_dict(post.metadata)

    @classmethod
    def load(cls, path: Path | str) -> "Document":
        """Load a document from file path.

        Args:
            path: Path to the markdown file.

        Returns:
            Document instance.

        Raises:
            DocumentParseError: If the file cannot be parsed.
        """
        path = Path(path)
        try:
            post = frontmatter.load(path)
            return cls(path, post)
        except Exception as e:
            raise DocumentParseError(f"Failed to parse {path}: {e}") from e

    @property
    def content(self) -> str:
        """Get the markdown content (without front-matter)."""
        return self._post.content

    @content.setter
    def content(self, value: str) -> None:
        """Update the markdown content."""
        self._post.content = value

    @property
    def metadata(self) -> dict:
        """Access front-matter metadata."""
        return self._post.metadata

    def update_last_reviewed(self) -> None:
        """Update the last_reviewed timestamp to today."""
        self._post.metadata["last_reviewed"] = date.today().isoformat()
        self.config.last_reviewed = date.today()

    def save(self) -> None:
        """Write document back to disk."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(self._post, handler=_MultilineYAMLHandler()))

    def should_review(self) -> bool:
        """Check if this document should be reviewed.

        Returns:
            True if auto_review is enabled and interval has passed.
        """
        return self.config.needs_review()

    def __repr__(self) -> str:
        return f"Document({self.path!r})"
