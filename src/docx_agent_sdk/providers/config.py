from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class OpenAIProviderConfig(BaseModel):
    api_key: str
    model: str = "gpt-4o-mini"
    base_url: Optional[str] = None
    organization: Optional[str] = None


class AzureOpenAIProviderConfig(BaseModel):
    api_key: str
    endpoint: str
    api_version: str
    deployment: str = Field(..., description="Azure OpenAI deployment name")
