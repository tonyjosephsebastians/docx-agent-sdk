from __future__ import annotations

from pathlib import Path

from docx_agent_sdk.documents import DocxParser, TextChunker
from docx_agent_sdk.providers import ModelProvider
from docx_agent_sdk.schemas import AnswerResult, AskOptions, ChatMessage
from docx_agent_sdk.services.prompts import QA_SYSTEM_PROMPT


class QuestionAnswerer:
    def __init__(
        self,
        parser: DocxParser,
        provider: ModelProvider | None,
        chunker: TextChunker | None = None,
    ) -> None:
        self.parser = parser
        self.provider = provider
        self.chunker = chunker or TextChunker()

    def ask(self, path: str | Path, question: str, options: AskOptions) -> AnswerResult:
        if not self.provider:
            raise ValueError("A model provider is required to answer document questions")

        document = self.parser.parse(path)
        chunks = self.chunker.chunk(document.to_text())
        if not chunks:
            return AnswerResult(path=document.path, question=question, answer="", model=None)

        prompt = (
            f"Answer in no more than {options.max_answer_words} words.\n\n"
            f"Question: {question}\n\nDOCX content:\n{chr(10).join(chunks)}"
        )
        result = self.provider.generate(
            [
                ChatMessage(role="system", content=QA_SYSTEM_PROMPT),
                ChatMessage(role="user", content=prompt),
            ],
            options.generation,
        )
        return AnswerResult(
            path=document.path,
            question=question,
            answer=result.content.strip(),
            model=result.model,
        )
