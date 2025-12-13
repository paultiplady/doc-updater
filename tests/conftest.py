"""Pytest fixtures for doc-updater tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_doc_content():
    """Sample markdown document with front-matter."""
    return """---
title: Test Document
auto_review: true
review_prompt: Check for outdated information.
last_reviewed: 2024-01-01
review_interval_days: 30
---

# Test Document

This is test content.
"""


@pytest.fixture
def sample_doc_no_review():
    """Sample markdown document without auto_review."""
    return """---
title: Static Document
auto_review: false
---

# Static Document

This content should not be reviewed.
"""
