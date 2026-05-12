from docx_agent_sdk import DocxAgent
from docx_agent_sdk.schemas import CompareOptions


def test_fake_provider_works_with_summarize_and_ask(make_docx, fake_provider):
    path = make_docx("sample.docx", ["Contract term is 12 months."])
    agent = DocxAgent(provider=fake_provider)

    summary = agent.summarize(path)
    answer = agent.ask(path, "What is the term?")

    assert summary.summary == "fake response"
    assert answer.answer == "fake response"
    assert len(fake_provider.calls) == 2


def test_comparator_detects_paragraph_and_table_changes(make_docx):
    old = make_docx("old.docx", ["Title", "Old paragraph"], [["Name", "Value"]])
    new = make_docx("new.docx", ["Title", "New paragraph", "Added paragraph"], [["Name", "New value"]])
    agent = DocxAgent()

    report = agent.compare(old, new, CompareOptions(include_semantic_summary=False))

    assert report.summary == "2 paragraph change(s) and 1 table change(s) detected."
    assert [change.change_type for change in report.paragraph_changes] == ["changed", "added"]
    assert report.table_changes[0].change_type == "changed"
    assert report.semantic_summary is None


def test_comparator_adds_semantic_summary_when_provider_exists(make_docx, fake_provider):
    old = make_docx("old.docx", ["Old paragraph"])
    new = make_docx("new.docx", ["New paragraph"])
    agent = DocxAgent(provider=fake_provider)

    report = agent.compare(old, new)

    assert report.semantic_summary == "fake response"
    assert report.model == "fake-model"
