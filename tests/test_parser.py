from docx_agent_sdk.documents import DocxParser


def test_parser_extracts_paragraphs_and_tables(make_docx):
    path = make_docx(
        "sample.docx",
        ["Title", "First paragraph"],
        [["Name", "Value"], ["Term", "12 months"]],
    )

    document = DocxParser().parse(path)

    assert [paragraph.text for paragraph in document.paragraphs] == ["Title", "First paragraph"]
    assert document.tables[0].rows == [["Name", "Value"], ["Term", "12 months"]]
    assert "Table 0:" in document.to_text()
