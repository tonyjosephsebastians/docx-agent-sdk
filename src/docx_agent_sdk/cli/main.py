from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from docx_agent_sdk import DocxAgent
from docx_agent_sdk.providers import ProviderConfigurationError
from docx_agent_sdk.schemas import AskOptions, CompareOptions, ExtractOptions, SummaryOptions

app = typer.Typer(help="Analyze DOCX files with OpenAI or Azure OpenAI.")
console = Console()


@app.command()
def summarize(
    path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    provider: Optional[str] = typer.Option(None, "--provider", help="openai or azure"),
    max_words: int = typer.Option(300, "--max-words", min=1),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """Summarize a DOCX file."""
    agent = _agent_from_env(provider)
    result = agent.summarize(path, SummaryOptions(max_words=max_words))
    _write_or_print(result.model_dump_json(indent=2), output)


@app.command()
def compare(
    source_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    target_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    provider: Optional[str] = typer.Option(None, "--provider", help="openai or azure"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    no_semantic_summary: bool = typer.Option(
        False,
        "--no-semantic-summary",
        help="Skip model-generated semantic summary.",
    ),
) -> None:
    """Compare two DOCX files and return structured JSON."""
    agent = _optional_agent_from_env(provider) if not no_semantic_summary else DocxAgent()
    result = agent.compare(
        source_path,
        target_path,
        CompareOptions(include_semantic_summary=not no_semantic_summary),
    )
    _write_or_print(result.model_dump_json(indent=2), output)


@app.command()
def extract(
    path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    format: str = typer.Option("json", "--format", help="json or text"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """Extract paragraphs and tables from a DOCX file."""
    agent = DocxAgent()
    result = agent.extract(path, ExtractOptions(include_tables=True))
    if format == "json":
        content = result.model_dump_json(indent=2)
    elif format == "text":
        content = result.to_text()
    else:
        raise typer.BadParameter("format must be json or text")
    _write_or_print(content, output)


@app.command()
def ask(
    path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    question: str = typer.Argument(...),
    provider: Optional[str] = typer.Option(None, "--provider", help="openai or azure"),
    max_words: int = typer.Option(300, "--max-words", min=1),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """Ask a question about a DOCX file."""
    agent = _agent_from_env(provider)
    result = agent.ask(path, question, AskOptions(max_answer_words=max_words))
    _write_or_print(result.model_dump_json(indent=2), output)


def _agent_from_env(provider: str | None) -> DocxAgent:
    try:
        return DocxAgent.from_env(provider)
    except ProviderConfigurationError as exc:
        raise typer.BadParameter(str(exc)) from exc


def _optional_agent_from_env(provider: str | None) -> DocxAgent:
    try:
        return DocxAgent.from_env(provider)
    except ProviderConfigurationError as exc:
        if provider:
            raise typer.BadParameter(str(exc)) from exc
        return DocxAgent()


def _write_or_print(content: str, output: Path | None) -> None:
    if output:
        output.write_text(content, encoding="utf-8")
        console.print(f"Wrote {output}")
    else:
        console.print(content)
