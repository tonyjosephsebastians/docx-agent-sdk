from __future__ import annotations

from pathlib import Path

from docx_agent_sdk.documents import DocxParser
from docx_agent_sdk.schemas import ExtractOptions, ExtractedDocument


class Extractor:
    def __init__(self, parser: DocxParser) -> None:
        self.parser = parser

    def extract(self, path: str | Path, options: ExtractOptions) -> ExtractedDocument:
        return self.parser.parse(path, options)
