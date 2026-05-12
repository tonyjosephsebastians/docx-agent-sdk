from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class GenerationOptions(BaseModel):
    temperature: float = 0.2
    max_tokens: Optional[int] = None


class GenerationResult(BaseModel):
    content: str
    model: Optional[str] = None
    usage: dict[str, Any] = Field(default_factory=dict)


class ExtractOptions(BaseModel):
    include_tables: bool = True


class SummaryOptions(BaseModel):
    max_words: int = 300
    style: str = "concise"
    generation: GenerationOptions = Field(default_factory=GenerationOptions)


class CompareOptions(BaseModel):
    include_semantic_summary: bool = True
    generation: GenerationOptions = Field(default_factory=GenerationOptions)


class AskOptions(BaseModel):
    max_answer_words: int = 300
    generation: GenerationOptions = Field(default_factory=GenerationOptions)


class ExtractedParagraph(BaseModel):
    index: int
    text: str


class ExtractedTable(BaseModel):
    index: int
    rows: list[list[str]]


class ExtractedDocument(BaseModel):
    path: str
    paragraphs: list[ExtractedParagraph] = Field(default_factory=list)
    tables: list[ExtractedTable] = Field(default_factory=list)

    def to_text(self, include_tables: bool = True) -> str:
        blocks = [paragraph.text for paragraph in self.paragraphs]
        if include_tables:
            for table in self.tables:
                blocks.append(f"Table {table.index}:")
                blocks.extend(" | ".join(cell for cell in row) for row in table.rows)
        return "\n".join(block for block in blocks if block.strip())


class SummaryResult(BaseModel):
    path: str
    summary: str
    model: Optional[str] = None


class AnswerResult(BaseModel):
    path: str
    question: str
    answer: str
    model: Optional[str] = None


class ParagraphChange(BaseModel):
    change_type: Literal["added", "removed", "changed"]
    source_index: Optional[int] = None
    target_index: Optional[int] = None
    source_text: Optional[str] = None
    target_text: Optional[str] = None


class TableChange(BaseModel):
    change_type: Literal["added", "removed", "changed"]
    source_index: Optional[int] = None
    target_index: Optional[int] = None
    source_rows: Optional[list[list[str]]] = None
    target_rows: Optional[list[list[str]]] = None


class ComparisonReport(BaseModel):
    source_path: str
    target_path: str
    summary: str
    paragraph_changes: list[ParagraphChange] = Field(default_factory=list)
    table_changes: list[TableChange] = Field(default_factory=list)
    semantic_summary: Optional[str] = None
    model: Optional[str] = None
