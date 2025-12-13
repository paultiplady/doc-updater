"""Tests for front-matter configuration."""

from datetime import date

from doc_updater.frontmatter import ReviewConfig


def test_from_dict_minimal():
    """Test creating ReviewConfig with minimal data."""
    config = ReviewConfig.from_dict({"auto_review": True})

    assert config.auto_review is True
    assert config.review_prompt is None
    assert config.review_context is None
    assert config.last_reviewed is None
    assert config.review_interval_days == 30


def test_from_dict_full():
    """Test creating ReviewConfig with all fields."""
    config = ReviewConfig.from_dict(
        {
            "auto_review": True,
            "review_prompt": "Check for updates.",
            "review_context": "Technical doc for engineers.",
            "last_reviewed": "2024-06-15",
            "review_interval_days": 60,
        }
    )

    assert config.auto_review is True
    assert config.review_prompt == "Check for updates."
    assert config.review_context == "Technical doc for engineers."
    assert config.last_reviewed == date(2024, 6, 15)
    assert config.review_interval_days == 60


def test_from_dict_date_object():
    """Test creating ReviewConfig with date object."""
    config = ReviewConfig.from_dict(
        {
            "auto_review": True,
            "last_reviewed": date(2024, 6, 15),
        }
    )

    assert config.last_reviewed == date(2024, 6, 15)


def test_to_dict():
    """Test converting ReviewConfig to dict."""
    config = ReviewConfig(
        auto_review=True,
        review_prompt="Check updates.",
        last_reviewed=date(2024, 6, 15),
    )

    result = config.to_dict()

    assert result["auto_review"] is True
    assert result["review_prompt"] == "Check updates."
    assert result["last_reviewed"] == "2024-06-15"
    assert "review_interval_days" not in result  # Default not included


def test_needs_review_no_auto():
    """Test needs_review returns False when auto_review disabled."""
    config = ReviewConfig(auto_review=False)
    assert config.needs_review() is False


def test_needs_review_never_reviewed():
    """Test needs_review returns True when never reviewed."""
    config = ReviewConfig(auto_review=True, last_reviewed=None)
    assert config.needs_review() is True


def test_needs_review_due():
    """Test needs_review returns True when interval passed."""
    config = ReviewConfig(
        auto_review=True,
        last_reviewed=date(2020, 1, 1),  # Long ago
        review_interval_days=30,
    )
    assert config.needs_review() is True


def test_needs_review_not_due():
    """Test needs_review returns False when recently reviewed."""
    config = ReviewConfig(
        auto_review=True,
        last_reviewed=date.today(),
        review_interval_days=30,
    )
    assert config.needs_review() is False
