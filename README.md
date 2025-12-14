# doc-updater

Review and update living documents using LLMs. Designed to run via GitHub Actions to periodically check if your documentation is outdated and create PRs with updates.

## Features

- **Front-matter driven**: Documents opt-in to review via `auto_review: true`
- **Custom prompts**: Each document can specify what to focus on
- **Obsidian compatible**: Standard YAML front-matter works everywhere
- **GitHub Actions ready**: Includes workflow for automated PR creation
- **Pluggable providers**: Start with Claude, add others as needed

## Installation

```bash
# Using uv
uv pip install doc-updater

# Or from source
git clone https://github.com/your-org/doc-updater
cd doc-updater
uv pip install -e .
```

## Quick Start

### 1. Add front-matter to your documents

```markdown
---
auto_review: true
review_prompt: |
  Review this document for outdated information.
  Focus on the "Alternatives" section.
review_context: |
  This is a technical comparison for our engineering team.
last_reviewed: 2024-06-15
review_interval_days: 30
---

# Your Document Title

Your content here...
```

### 2. Run the review

```bash
# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Review all documents in a directory
doc-updater review ./docs

# Dry run (no changes)
doc-updater review ./docs --dry-run

# Review a single file
doc-updater review ./docs/platform-comparison.md
```

### 3. List documents due for review

```bash
doc-updater list ./docs
```

## Front-Matter Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `auto_review` | boolean | Yes | Enable automatic review |
| `review_prompt` | string | No | Custom prompt for this document |
| `review_context` | string | No | Additional context for the LLM |
| `last_reviewed` | date | No | Updated automatically after review |
| `review_interval_days` | integer | No | Days between reviews (default: 30) |

## GitHub Actions Setup

### 1. Add the workflow

Copy `.github/workflows/doc-review.yml` to your repository.

### 2. Set up secrets

Add `ANTHROPIC_API_KEY` to your repository secrets.

### 3. Configure the schedule

Edit the cron expression in the workflow to set your review frequency:

```yaml
on:
  schedule:
    - cron: "0 0 1 * *"  # Monthly on the 1st
```

### 4. Manual trigger

You can also trigger reviews manually from the Actions tab.

## CLI Reference

```
Usage: doc-updater [OPTIONS] COMMAND [ARGS]...

Commands:
  review   Review and update documents marked with auto_review: true
  list     List all documents marked for auto-review
  version  Show version information

Options:
  --help  Show this message and exit
```

### review

```
Usage: doc-updater review [OPTIONS] PATH

Arguments:
  PATH  Directory or file to review  [required]

Options:
  -p, --provider [claude]   LLM provider to use  [default: claude]
  -m, --model TEXT          Model to use (provider-specific)
  -n, --dry-run             Show what would be changed without modifying files
  -r, --recursive           Search for documents recursively  [default: True]
  -v, --verbose             Show detailed output
  -d, --debug               Enable debug logging
  --help                    Show this message and exit
```

## Development

```bash
# Clone and install dev dependencies
git clone https://github.com/your-org/doc-updater
cd doc-updater
uv sync --group dev

# Run tests
uv run pytest

# Format code
uv run black src tests
uv run ruff check --fix src tests
```

## License

MIT
