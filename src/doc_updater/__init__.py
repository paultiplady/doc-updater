"""Doc-Updater: Review and update living documents using LLMs."""

from doc_updater.document import Document
from doc_updater.frontmatter import ReviewConfig
from doc_updater.reviewer import DocumentReviewer

__version__ = "0.2.0"
__all__ = ["Document", "ReviewConfig", "DocumentReviewer", "__version__"]
