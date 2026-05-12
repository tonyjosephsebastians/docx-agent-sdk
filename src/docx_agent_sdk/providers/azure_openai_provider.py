from __future__ import annotations

from collections.abc import Sequence

from docx_agent_sdk.providers.base import ModelProvider
from docx_agent_sdk.providers.config import AzureOpenAIProviderConfig
from docx_agent_sdk.schemas import ChatMessage, GenerationOptions, GenerationResult


class AzureOpenAIProvider(ModelProvider):
    """Azure OpenAI adapter using the official openai Python package."""

    def __init__(self, config: AzureOpenAIProviderConfig) -> None:
        from openai import AzureOpenAI

        self.config = config
        self.client = AzureOpenAI(
            api_key=config.api_key,
            api_version=config.api_version,
            azure_endpoint=config.endpoint,
        )

    def generate(
        self,
        messages: Sequence[ChatMessage],
        options: GenerationOptions | None = None,
    ) -> GenerationResult:
        options = options or GenerationOptions()
        response = self.client.chat.completions.create(
            model=self.config.deployment,
            messages=[message.model_dump() for message in messages],
            temperature=options.temperature,
            max_tokens=options.max_tokens,
        )
        choice = response.choices[0]
        usage = response.usage.model_dump() if response.usage else {}
        return GenerationResult(
            content=choice.message.content or "",
            model=response.model,
            usage=usage,
        )
