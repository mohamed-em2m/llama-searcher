# 🦙 llama-search Tutorial

Welcome to the comprehensive tutorial for **llama-search**! This guide will take you from installation to advanced orchestration of multi-engine AI searches.

---

## 📖 Introduction

**llama-search** is a professional-grade search orchestration framework. It acts as a bridge between your AI agents and the vast information on the web. Unlike simple search wrappers, `llama-search`:

- **Multiplexes** 10+ search engines concurrently.
- **Cleans** HTML into LLM-ready Markdown.
- **Orchestrates** RAG (Retrieval-Augmented Generation) automatically.
- **Extracts** structured events (Sports, Calendars, etc.) using AI.

---

## ⚡ Getting Started

### 1. Installation

We recommend using [uv](https://github.com/astral-sh/uv) for fast and reliable dependency management.

```bash
git clone https://github.com/mohamed-em2m/llm-search-tool.git
cd llm-search-tool
uv sync
```

### 2. Configuration

`llama-search` uses [Dynaconf](https://www.dynaconf.com/) for secure configuration.

1. Copy `.secrets.toml` template.
2. Add your API keys.

```toml
# .secrets.toml
[default]
GOOGLE_API_KEY = "your_google_key"
CSE_ID = "your_custom_search_engine_id"
BING_API_KEY = "your_bing_key"
FIRECRAWL_API_KEY = "your_firecrawl_key"
EXA_API_KEY = "your_exa_key"
TAVILY_API_KEY = "your_tavily_key"
PERPLEXITY_API_KEY = "your_perplexity_key"
# ... and more
```

---

## 🚀 Usage Guide

### Simple Multi-Engine Search

The core power of `llama-search` lies in the `get_events` tool. It allows you to query multiple engines with a single call.

```python
from llama_search.api.search import get_events

# Aggregate results from Google, Exa, and Tavily
results = get_events(
    search_qeury="Tech conferences in Europe 2025",
    engine="google,exa,tavily"
)

print(results)
```

- **Special**: `multi` (aggregates top providers).

---

## 🌐 FastAPI & REST Access

`llama-search` can be run as a standalone web service, allowing you to integrate it with any language or platform.

### Running the API

```bash
uv run python -m llama_search.api.app
```

The server will start at `http://0.0.0.0:8000`.

### Endpoints

- **GET `/search?q=query&engine=multi`**: Returns search results.
- **POST `/search`**: Accepts a JSON body: `{"query": "...", "engine": "multi"}`.

---

## 🤖 MCP (Model Context Protocol) Support

Integrate `llama-search` directly into AI agents like Claude Desktop or other MCP-compatible platforms.

### Running the MCP Server

```bash
uv run python -m llama_search.mcp_server
```

### Integration with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "llama-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/llm-search-tool",
        "run",
        "python",
        "-m",
        "llama_search.mcp_server"
      ]
    }
  }
}
```

Now Claude can natively search the web using all 10+ engines!

---

## 🏗️ Architecture Overview

The project is built with a modular package structure:

- **`llama_search/api/`**: The standard entry point for tool integration.
- **`llama_search/core/`**:
  - `search_providers.py`: Implementation of all search engine logic.
  - `fetchers.py`: Static and Dynamic (Playwright) web scraping.
  - `cleaners.py`: Semantic HTML parsing into clean text.
  - `rag.py`: Similarity search and embedding logic.
- **`llama_search/services/`**: High-level orchestration for scraping tasks and event extraction.
- **`llama_search/agents/`**: AI agents for summarization and analysis.

---

## 🛠️ Developer Guide: Adding a Search Provider

Adding a new engine is easy! Simply implement the `BaseSearchProvider` interface in `llama_search/core/search_providers.py`.

```python
class MyNewSearchProvider(BaseSearchProvider):
    def search(self, query, num_results=10, lang="lang_it"):
        # Your API call logic here
        return raw_json_results

    def extract_urls(self, results, filters):
        # Your URL extraction logic here
        return [r['link'] for r in results if not filter_match]
```

---

## 🔒 Security & Quality

We maintain high standards through:

- **Pre-commit hooks**: Automated linting (Ruff) and secret detection (Gitleaks).
- **GitHub Actions**: Every PR is automatically tested and linted.
- **Semantic HTML Cleaning**: We strip ads, navbars, and footers to keep your token count low.

---

*Happy searching! If you encounter any issues, please open an issue on GitHub.*
