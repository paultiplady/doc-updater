"""Tests for document parsing."""

from datetime import date

import pytest

from doc_updater.document import Document
from doc_updater.exceptions import DocumentParseError


def test_load_document(temp_dir, sample_doc_content):
    """Test loading a document with front-matter."""
    doc_path = temp_dir / "test.md"
    doc_path.write_text(sample_doc_content)

    doc = Document.load(doc_path)

    assert doc.path == doc_path
    assert doc.config.auto_review is True
    assert doc.config.review_prompt == "Check for outdated information."
    assert doc.config.last_reviewed == date(2024, 1, 1)
    assert "# Test Document" in doc.content


def test_load_document_no_frontmatter(temp_dir):
    """Test loading a document without front-matter."""
    doc_path = temp_dir / "plain.md"
    doc_path.write_text("# Just a plain document\n\nNo front-matter here.")

    doc = Document.load(doc_path)

    assert doc.config.auto_review is False
    assert "# Just a plain document" in doc.content


def test_should_review_enabled(temp_dir, sample_doc_content):
    """Test should_review returns True when due."""
    doc_path = temp_dir / "test.md"
    doc_path.write_text(sample_doc_content)

    doc = Document.load(doc_path)

    # Last reviewed was 2024-01-01, interval is 30 days
    # Should be due for review
    assert doc.should_review() is True


def test_should_review_disabled(temp_dir, sample_doc_no_review):
    """Test should_review returns False when disabled."""
    doc_path = temp_dir / "test.md"
    doc_path.write_text(sample_doc_no_review)

    doc = Document.load(doc_path)

    assert doc.should_review() is False


def test_update_last_reviewed(temp_dir, sample_doc_content):
    """Test updating the last_reviewed timestamp."""
    doc_path = temp_dir / "test.md"
    doc_path.write_text(sample_doc_content)

    doc = Document.load(doc_path)
    doc.update_last_reviewed()

    assert doc.config.last_reviewed == date.today()
    assert doc.metadata["last_reviewed"] == date.today().isoformat()


def test_save_document(temp_dir, sample_doc_content):
    """Test saving a document preserves content and metadata."""
    doc_path = temp_dir / "test.md"
    doc_path.write_text(sample_doc_content)

    doc = Document.load(doc_path)
    doc.content = "# Updated Content\n\nNew content here."
    doc.update_last_reviewed()
    doc.save()

    # Reload and verify
    doc2 = Document.load(doc_path)
    assert "# Updated Content" in doc2.content
    assert doc2.config.last_reviewed == date.today()
    assert doc2.config.auto_review is True


def test_load_nonexistent_file(temp_dir):
    """Test loading a nonexistent file raises error."""
    with pytest.raises(DocumentParseError):
        Document.load(temp_dir / "nonexistent.md")
