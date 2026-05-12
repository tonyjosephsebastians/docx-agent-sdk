from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from docx_agent_sdk.schemas import ChatMessage, GenerationOptions, GenerationResult


class ProviderConfigurationError(ValueError):
    """Raised when a model provider cannot be configured."""


class ModelProvider(ABC):
    """Strategy interface for model providers."""

    @abstractmethod
    def generate(
        self,
        messages: Sequence[ChatMessage],
        options: GenerationOptions | None = None,
    ) -> GenerationResult:
        raise NotImplementedError
