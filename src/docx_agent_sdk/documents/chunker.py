from __future__ import annotations


class TextChunker:
    """Splits document text into bounded chunks for model calls."""

    def __init__(self, max_chars: int = 8_000, overlap_chars: int = 400) -> None:
        if max_chars <= 0:
            raise ValueError("max_chars must be greater than zero")
        if overlap_chars < 0 or overlap_chars >= max_chars:
            raise ValueError("overlap_chars must be between zero and max_chars")
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars

    def chunk(self, text: str) -> list[str]:
        normalized = text.strip()
        if not normalized:
            return []
        if len(normalized) <= self.max_chars:
            return [normalized]

        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(start + self.max_chars, len(normalized))
            split_at = normalized.rfind("\n", start, end)
            if split_at <= start:
                split_at = end

            chunk = normalized[start:split_at].strip()
            if chunk:
                chunks.append(chunk)

            if split_at >= len(normalized):
                break
            start = max(0, split_at - self.overlap_chars)

        return chunks
