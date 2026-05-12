from __future__ import annotations

from pathlib import Path

from docx_agent_sdk.documents import DocxParser, TextChunker
from docx_agent_sdk.providers import ModelProvider
from docx_agent_sdk.schemas import ChatMessage, SummaryOptions, SummaryResult
from docx_agent_sdk.services.prompts import SUMMARIZER_SYSTEM_PROMPT


class Summarizer:
    def __init__(
        self,
        parser: DocxParser,
        provider: ModelProvider | None,
        chunker: TextChunker | None = None,
    ) -> None:
        self.parser = parser
        self.provider = provider
        self.chunker = chunker or TextChunker()

    def summarize(self, path: str | Path, options: SummaryOptions) -> SummaryResult:
        if not self.provider:
            raise ValueError("A model provider is required to summarize documents")

        document = self.parser.parse(path)
        chunks = self.chunker.chunk(document.to_text())
        if not chunks:
            return SummaryResult(path=document.path, summary="", model=None)

        if len(chunks) == 1:
            result = self.provider.generate(
                [
                    ChatMessage(role="system", content=SUMMARIZER_SYSTEM_PROMPT),
                    ChatMessage(
                        role="user",
                        content=_summary_prompt(chunks[0], options),
                    ),
                ],
                options.generation,
            )
            return SummaryResult(path=document.path, summary=result.content.strip(), model=result.model)

        partials: list[str] = []
        model: str | None = None
        for index, chunk in enumerate(chunks, start=1):
            result = self.provider.generate(
                [
                    ChatMessage(role="system", content=SUMMARIZER_SYSTEM_PROMPT),
                    ChatMessage(
                        role="user",
                        content=(
                            f"Summarize part {index} of {len(chunks)} in no more than "
                            f"{max(80, options.max_words // len(chunks))} words.\n\n{chunk}"
                        ),
                    ),
                ],
                options.generation,
            )
            partials.append(result.content.strip())
            model = result.model or model

        final = self.provider.generate(
            [
                ChatMessage(role="system", content=SUMMARIZER_SYSTEM_PROMPT),
                ChatMessage(
                    role="user",
                    content=_summary_prompt("\n\n".join(partials), options),
                ),
            ],
            options.generation,
        )
        return SummaryResult(path=document.path, summary=final.content.strip(), model=final.model or model)


def _summary_prompt(text: str, options: SummaryOptions) -> str:
    return (
        f"Write a {options.style} summary in no more than {options.max_words} words.\n\n"
        f"DOCX content:\n{text}"
    )
