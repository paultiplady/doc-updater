"""CLI interface for doc-updater."""

import asyncio
from enum import Enum
from pathlib import Path

import typer

from doc_updater.document import Document
from doc_updater.exceptions import DocumentParseError
from doc_updater.providers import ProviderType, get_provider
from doc_updater.reviewer import DocumentReviewer

app = typer.Typer(
    name="doc-updater",
    help="Review and update living documents using LLMs.",
    no_args_is_help=True,
)


class Provider(str, Enum):
    """CLI provider choices."""

    claude = "claude"


@app.command()
def review(
    path: Path = typer.Argument(
        ...,
        help="Directory or file to review",
        exists=True,
    ),
    provider: Provider = typer.Option(
        Provider.claude,
        "--provider",
        "-p",
        help="LLM provider to use",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="Model to use (provider-specific)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would be changed without modifying files",
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        "-r/-R",
        help="Search for documents recursively",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Review and update documents marked with auto_review: true."""
    # Build provider kwargs
    provider_kwargs: dict = {}
    if model:
        provider_kwargs["model"] = model

    llm_provider = get_provider(ProviderType(provider.value), **provider_kwargs)

    if not llm_provider.validate_config():
        typer.echo("Error: Provider not configured. Set ANTHROPIC_API_KEY environment variable.", err=True)
        raise typer.Exit(1)

    reviewer = DocumentReviewer(llm_provider)

    if dry_run:
        typer.echo("[DRY RUN] No files will be modified.\n")

    if path.is_file():
        # Review single file
        try:
            doc = Document.load(path)
        except DocumentParseError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)

        if not doc.config.auto_review:
            typer.echo(f"Skipping {path}: auto_review not enabled")
            return

        result = asyncio.run(reviewer.review_document(doc, dry_run))

        if result.error:
            typer.echo(f"Error reviewing {path}: {result.error}", err=True)
            raise typer.Exit(1)

        if result.changed:
            typer.echo(f"Updated: {path}")
        else:
            typer.echo(f"No changes: {path}")

        if verbose and result.summary:
            typer.echo(f"  Summary: {result.summary}")
    else:
        # Review directory
        results = asyncio.run(reviewer.review_all(path, dry_run, recursive))

        if not results:
            typer.echo("No documents found for review.")
            return

        changed_count = sum(1 for r in results if r.changed)
        error_count = sum(1 for r in results if r.error)

        typer.echo(f"Reviewed {len(results)} document(s): {changed_count} updated, {error_count} errors\n")

        for result in results:
            if result.error:
                typer.echo(f"  ERROR: {result.path}")
                if verbose:
                    typer.echo(f"    {result.error}")
            elif result.changed:
                typer.echo(f"  UPDATED: {result.path}")
                if verbose and result.summary:
                    typer.echo(f"    {result.summary}")
            else:
                typer.echo(f"  OK: {result.path}")
                if verbose and result.summary:
                    typer.echo(f"    {result.summary}")


@app.command("list")
def list_docs(
    path: Path = typer.Argument(
        ".",
        help="Directory to search",
        exists=True,
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        "-r/-R",
        help="Search recursively",
    ),
) -> None:
    """List all documents marked for auto-review."""
    pattern = "**/*.md" if recursive else "*.md"
    found = 0

    for md_path in sorted(path.glob(pattern)):
        try:
            doc = Document.load(md_path)
            if doc.config.auto_review:
                found += 1
                status = "DUE" if doc.should_review() else "OK"
                typer.echo(f"[{status}] {md_path}")
                if doc.config.last_reviewed:
                    typer.echo(f"       Last reviewed: {doc.config.last_reviewed}")
        except DocumentParseError:
            pass

    if found == 0:
        typer.echo("No documents with auto_review: true found.")
    else:
        typer.echo(f"\nFound {found} document(s) with auto_review enabled.")


@app.command()
def version() -> None:
    """Show version information."""
    from doc_updater import __version__

    typer.echo(f"doc-updater {__version__}")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
