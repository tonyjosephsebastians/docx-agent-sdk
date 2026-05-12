from __future__ import annotations

import os
from typing import Literal

from docx_agent_sdk.providers.azure_openai_provider import AzureOpenAIProvider
from docx_agent_sdk.providers.base import ModelProvider, ProviderConfigurationError
from docx_agent_sdk.providers.config import AzureOpenAIProviderConfig, OpenAIProviderConfig
from docx_agent_sdk.providers.openai_provider import OpenAIProvider


class ProviderFactory:
    """Factory for provider adapters from explicit config or environment variables."""

    @staticmethod
    def from_openai_config(config: OpenAIProviderConfig) -> OpenAIProvider:
        return OpenAIProvider(config)

    @staticmethod
    def from_azure_config(config: AzureOpenAIProviderConfig) -> AzureOpenAIProvider:
        return AzureOpenAIProvider(config)

    @staticmethod
    def from_env(provider: Literal["openai", "azure"] | str | None = None) -> ModelProvider:
        requested = provider.lower() if provider else None
        if requested not in {None, "openai", "azure"}:
            raise ProviderConfigurationError("provider must be one of: openai, azure")

        if requested == "azure" or (requested is None and _has_azure_env()):
            return ProviderFactory.from_azure_config(_azure_config_from_env())

        if requested == "openai" or (requested is None and os.getenv("OPENAI_API_KEY")):
            return ProviderFactory.from_openai_config(_openai_config_from_env())

        raise ProviderConfigurationError(
            "No model provider configured. Set OpenAI or Azure OpenAI environment variables."
        )


def _openai_config_from_env() -> OpenAIProviderConfig:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ProviderConfigurationError("OPENAI_API_KEY is required for OpenAI provider")

    return OpenAIProviderConfig(
        api_key=api_key,
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        organization=os.getenv("OPENAI_ORGANIZATION"),
    )


def _azure_config_from_env() -> AzureOpenAIProviderConfig:
    required = {
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
        "AZURE_OPENAI_DEPLOYMENT": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ProviderConfigurationError(
            f"Missing Azure OpenAI environment variables: {', '.join(missing)}"
        )

    return AzureOpenAIProviderConfig(
        api_key=required["AZURE_OPENAI_API_KEY"] or "",
        endpoint=required["AZURE_OPENAI_ENDPOINT"] or "",
        api_version=required["AZURE_OPENAI_API_VERSION"] or "",
        deployment=required["AZURE_OPENAI_DEPLOYMENT"] or "",
    )


def _has_azure_env() -> bool:
    return all(
        os.getenv(name)
        for name in (
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_DEPLOYMENT",
        )
    )
