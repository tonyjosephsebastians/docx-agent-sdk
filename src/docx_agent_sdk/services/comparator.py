from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path

from docx_agent_sdk.documents import DocxParser
from docx_agent_sdk.providers import ModelProvider
from docx_agent_sdk.schemas import (
    ChatMessage,
    CompareOptions,
    ComparisonReport,
    ParagraphChange,
    TableChange,
)
from docx_agent_sdk.services.prompts import COMPARISON_SYSTEM_PROMPT


class Comparator:
    def __init__(self, parser: DocxParser, provider: ModelProvider | None) -> None:
        self.parser = parser
        self.provider = provider

    def compare(
        self,
        source_path: str | Path,
        target_path: str | Path,
        options: CompareOptions,
    ) -> ComparisonReport:
        source = self.parser.parse(source_path)
        target = self.parser.parse(target_path)
        paragraph_changes = _compare_paragraphs(
            [paragraph.text for paragraph in source.paragraphs],
            [paragraph.text for paragraph in target.paragraphs],
        )
        table_changes = _compare_tables(
            [table.rows for table in source.tables],
            [table.rows for table in target.tables],
        )
        summary = (
            f"{len(paragraph_changes)} paragraph change(s) and "
            f"{len(table_changes)} table change(s) detected."
        )

        report = ComparisonReport(
            source_path=source.path,
            target_path=target.path,
            summary=summary,
            paragraph_changes=paragraph_changes,
            table_changes=table_changes,
        )

        if options.include_semantic_summary and self.provider:
            semantic = self.provider.generate(
                [
                    ChatMessage(role="system", content=COMPARISON_SYSTEM_PROMPT),
                    ChatMessage(
                        role="user",
                        content=(
                            "Summarize the material meaning of this DOCX comparison report.\n\n"
                            f"{report.model_dump_json(indent=2)}"
                        ),
                    ),
                ],
                options.generation,
            )
            report.semantic_summary = semantic.content.strip()
            report.model = semantic.model

        return report


def _compare_paragraphs(source: list[str], target: list[str]) -> list[ParagraphChange]:
    changes: list[ParagraphChange] = []
    matcher = SequenceMatcher(a=source, b=target, autojunk=False)
    for tag, source_start, source_end, target_start, target_end in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete":
            for index in range(source_start, source_end):
                changes.append(
                    ParagraphChange(
                        change_type="removed",
                        source_index=index,
                        source_text=source[index],
                    )
                )
        elif tag == "insert":
            for index in range(target_start, target_end):
                changes.append(
                    ParagraphChange(
                        change_type="added",
                        target_index=index,
                        target_text=target[index],
                    )
                )
        elif tag == "replace":
            changes.extend(_replace_paragraphs(source, target, source_start, source_end, target_start, target_end))
    return changes


def _replace_paragraphs(
    source: list[str],
    target: list[str],
    source_start: int,
    source_end: int,
    target_start: int,
    target_end: int,
) -> list[ParagraphChange]:
    changes: list[ParagraphChange] = []
    source_span = source[source_start:source_end]
    target_span = target[target_start:target_end]
    pair_count = min(len(source_span), len(target_span))

    for offset in range(pair_count):
        changes.append(
            ParagraphChange(
                change_type="changed",
                source_index=source_start + offset,
                target_index=target_start + offset,
                source_text=source_span[offset],
                target_text=target_span[offset],
            )
        )

    for offset in range(pair_count, len(source_span)):
        changes.append(
            ParagraphChange(
                change_type="removed",
                source_index=source_start + offset,
                source_text=source_span[offset],
            )
        )
    for offset in range(pair_count, len(target_span)):
        changes.append(
            ParagraphChange(
                change_type="added",
                target_index=target_start + offset,
                target_text=target_span[offset],
            )
        )

    return changes


def _compare_tables(source: list[list[list[str]]], target: list[list[list[str]]]) -> list[TableChange]:
    changes: list[TableChange] = []
    max_count = max(len(source), len(target))
    for index in range(max_count):
        source_rows = source[index] if index < len(source) else None
        target_rows = target[index] if index < len(target) else None
        if source_rows == target_rows:
            continue
        if source_rows is None:
            changes.append(TableChange(change_type="added", target_index=index, target_rows=target_rows))
        elif target_rows is None:
            changes.append(TableChange(change_type="removed", source_index=index, source_rows=source_rows))
        else:
            changes.append(
                TableChange(
                    change_type="changed",
                    source_index=index,
                    target_index=index,
                    source_rows=source_rows,
                    target_rows=target_rows,
                )
            )
    return changes


def report_to_json(report: ComparisonReport) -> str:
    return json.dumps(report.model_dump(), indent=2)
