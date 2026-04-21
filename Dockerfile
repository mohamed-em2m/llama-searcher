FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml .
COPY uv.lock .
COPY README.md .
COPY llama_searcher/ llama_searcher/

# Install dependencies using uv
RUN uv sync --frozen

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI server
CMD ["uv", "run", "python", "-m", "llama_searcher.api.app"]
