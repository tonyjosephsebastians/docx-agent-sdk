import pytest

from docx_agent_sdk.providers import ProviderConfigurationError, ProviderFactory
from docx_agent_sdk.providers.config import AzureOpenAIProviderConfig, OpenAIProviderConfig


def test_openai_config_factory(monkeypatch):
    created = {}

    def fake_openai(config):
        created["config"] = config
        return "openai-provider"

    monkeypatch.setattr(ProviderFactory, "from_openai_config", staticmethod(fake_openai))
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    monkeypatch.setenv("OPENAI_MODEL", "model")

    provider = ProviderFactory.from_env("openai")

    assert provider == "openai-provider"
    assert isinstance(created["config"], OpenAIProviderConfig)
    assert created["config"].model == "model"


def test_azure_config_factory(monkeypatch):
    created = {}

    def fake_azure(config):
        created["config"] = config
        return "azure-provider"

    monkeypatch.setattr(ProviderFactory, "from_azure_config", staticmethod(fake_azure))
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-01-01")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "deployment")

    provider = ProviderFactory.from_env("azure")

    assert provider == "azure-provider"
    assert isinstance(created["config"], AzureOpenAIProviderConfig)
    assert created["config"].deployment == "deployment"


def test_provider_factory_raises_without_env(monkeypatch):
    for name in (
        "OPENAI_API_KEY",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(ProviderConfigurationError):
        ProviderFactory.from_env()
