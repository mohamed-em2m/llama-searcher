# llama-search

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/mohamed-em2m/llm-search-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/mohamed-em2m/llm-search-tool/actions/workflows/ci.yml)

**llama-search** is a professional-grade search orchestration framework designed for AI Agents and RAG (Retrieval-Augmented Generation) pipelines. It unifies traditional SEO/SERP APIs with modern neural search engines, transforming raw web data into clean, LLM-ready markdown.

---

## 🚀 Key Features

- **Deca-Engine Support**: Seamlessly switch between or aggregate results from 10+ providers:
  - **Neural AI Search**: Firecrawl, Exa (Metaphor), Tavily, Perplexity Sonar.
  - **Traditional SERP**: Google Custom Search, Bing, SerpApi, Serper.dev, Brave Search, Zenserp.
- **RAG-Ready Output**: Automatically cleans HTML, removes boilerplate (nav, footers, scripts), and returns structured markdown optimized for context windows.
- **Smart Orchestration**: Concurrent search execution, link deduplication, and intelligent content merging.
- **Event Extraction**: Built-in logic for parsing sports, calendars, and community events from structured search metadata.
- **Professional Architecture**: Production-ready modular design with standardized logging, error handling, and `dynaconf` configuration management.

## 🛠️ Tech Stack

- **Core**: Python 3.10+, Asynchronous execution with `asyncio` & `aiohttp`.
- **Scraping**: Headless Playwright (for dynamic content) & httpx (for performance).
- **AI/LLM**: LangChain, OpenAI/Gemini compatible API integration, Tiktoken for token optimization.
- **Storage**: In-memory vector stores and RAG-based similarity search.

## 🚦 Quick Start

### 1. Configuration

The project uses `dynaconf`. Populate your API keys in `.secrets.toml`:

```toml
[default]
GOOGLE_API_KEY = "your_key"
CSE_ID = "your_cse_id"
BING_API_KEY = "your_key"
FIRECRAWL_API_KEY = "your_key"
# ... add other keys as needed
```

### 2. Basic Usage

```python
from llama_search.api.search import get_events

# Use multiple engines at once
result = get_events(
    search_qeury="Music festivals in Europe 2024",
    engine="google,exa,tavily"
)
print(result)
```

## 🏗️ Architecture

```text
├── agents/             # LLM Analysis & Summarization Agents
├── api/                # Unified Search Entry point
├── core/               # Fetchers, Cleaners, RAG, and SearchProviders
├── services/           # Orchestration & Domain services
├── utils/              # Configuration (Dynaconf) & Logging
└── main.py             # Entry point
```

---
*Created with ❤️ for the Advanced Agentic Coding community.*
