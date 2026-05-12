from __future__ import annotations

from pathlib import Path
from typing import Optional

from docx_agent_sdk.documents import DocxParser
from docx_agent_sdk.providers import ModelProvider, ProviderFactory
from docx_agent_sdk.services import Comparator, Extractor, QuestionAnswerer, Summarizer
from docx_agent_sdk.schemas import (
    AnswerResult,
    AskOptions,
    CompareOptions,
    ComparisonReport,
    ExtractOptions,
    ExtractedDocument,
    SummaryOptions,
    SummaryResult,
)


class DocxAgent:
    """Facade for common DOCX analysis workflows."""

    def __init__(
        self,
        provider: Optional[ModelProvider] = None,
        parser: Optional[DocxParser] = None,
    ) -> None:
        self.provider = provider
        self.parser = parser or DocxParser()
        self.extractor = Extractor(self.parser)
        self.summarizer = Summarizer(self.parser, provider)
        self.comparator = Comparator(self.parser, provider)
        self.question_answerer = QuestionAnswerer(self.parser, provider)

    @classmethod
    def from_env(cls, provider: str | None = None) -> "DocxAgent":
        return cls(provider=ProviderFactory.from_env(provider))

    def extract(
        self,
        path: str | Path,
        options: ExtractOptions | None = None,
    ) -> ExtractedDocument:
        return self.extractor.extract(path, options or ExtractOptions())

    def summarize(
        self,
        path: str | Path,
        options: SummaryOptions | None = None,
    ) -> SummaryResult:
        return self.summarizer.summarize(path, options or SummaryOptions())

    def compare(
        self,
        source_path: str | Path,
        target_path: str | Path,
        options: CompareOptions | None = None,
    ) -> ComparisonReport:
        return self.comparator.compare(source_path, target_path, options or CompareOptions())

    def ask(
        self,
        path: str | Path,
        question: str,
        options: AskOptions | None = None,
    ) -> AnswerResult:
        return self.question_answerer.ask(path, question, options or AskOptions())
