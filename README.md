# DOCX Agent SDK

Python SDK and CLI for analyzing `.docx` files with OpenAI or Azure OpenAI.

## Features

- Extract paragraphs and tables from DOCX files.
- Summarize DOCX files with an injected model provider.
- Compare two DOCX files and return structured JSON changes.
- Ask questions over DOCX content.
- Use OpenAI or Azure OpenAI through the official `openai` Python package.

## Install

```bash
pip install -e ".[dev]"
```

## Configure

OpenAI:

```bash
set OPENAI_API_KEY=...
set OPENAI_MODEL=gpt-4o-mini
```

Azure OpenAI:

```bash
set AZURE_OPENAI_API_KEY=...
set AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
set AZURE_OPENAI_API_VERSION=...
set AZURE_OPENAI_DEPLOYMENT=...
```

## Python Usage

```python
from docx_agent_sdk import DocxAgent

agent = DocxAgent.from_env()

summary = agent.summarize("contract.docx")
report = agent.compare("old.docx", "new.docx")
answer = agent.ask("contract.docx", "What are the renewal terms?")
```

For offline extraction and deterministic comparison:

```python
from docx_agent_sdk import DocxAgent
from docx_agent_sdk.schemas import CompareOptions

agent = DocxAgent()
document = agent.extract("contract.docx")
report = agent.compare("old.docx", "new.docx", CompareOptions(include_semantic_summary=False))
```

## CLI Usage

```bash
docx-agent summarize contract.docx
docx-agent compare old.docx new.docx --output report.json
docx-agent extract contract.docx --format json
docx-agent ask contract.docx "What are the key obligations?"
```
