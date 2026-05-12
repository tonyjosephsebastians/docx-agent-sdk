from typer.testing import CliRunner

from docx_agent_sdk.cli.main import app


def test_extract_cli_outputs_json(make_docx):
    path = make_docx("sample.docx", ["Hello"])
    runner = CliRunner()

    result = runner.invoke(app, ["extract", str(path), "--format", "json"])

    assert result.exit_code == 0
    assert '"paragraphs"' in result.stdout
    assert "Hello" in result.stdout


def test_compare_cli_without_semantic_summary_outputs_json(make_docx):
    old = make_docx("old.docx", ["Old"])
    new = make_docx("new.docx", ["New"])
    runner = CliRunner()

    result = runner.invoke(app, ["compare", str(old), str(new), "--no-semantic-summary"])

    assert result.exit_code == 0
    assert '"paragraph_changes"' in result.stdout
    assert '"changed"' in result.stdout


def test_compare_cli_outputs_json_without_provider_env(make_docx, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_VERSION", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)
    old = make_docx("old.docx", ["Old"])
    new = make_docx("new.docx", ["New"])
    runner = CliRunner()

    result = runner.invoke(app, ["compare", str(old), str(new)])

    assert result.exit_code == 0
    assert '"semantic_summary": null' in result.stdout
