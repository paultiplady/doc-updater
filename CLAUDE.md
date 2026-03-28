# doc-updater

Review and update living documents using LLMs. Installed via `uvx doc-updater`.

## Project structure

```
src/doc_updater/    # Package source
tests/              # pytest tests
.github/workflows/  # CI: publish.yml (PyPI), doc-review.yml (scheduled reviews)
```

## Development

```bash
uv sync --group dev     # Install deps
uv run pytest           # Run tests
uv run ruff check .     # Lint
```

## Publishing a new release

The publish workflow triggers on `v*` tags. It runs tests, builds, and publishes to PyPI using trusted publishing (no API token needed).

1. Bump version in both `pyproject.toml` and `src/doc_updater/__init__.py`
2. Run `uv lock` to update `uv.lock`
3. Commit: `git add pyproject.toml src/doc_updater/__init__.py uv.lock && git commit -m "Bump version to X.Y.Z"`
4. Push:   `git push`
5. Tag:    `git tag vX.Y.Z && git push --tags`
6. Verify: check the **Actions** tab for the "Publish to PyPI" workflow
7. Test:   `uvx doc-updater version` (may need `--refresh` to bust cache)
