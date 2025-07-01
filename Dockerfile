# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
COPY data/ ./data/
COPY datasets/ ./datasets/

# Install dependencies
RUN uv sync --frozen --no-dev

# Expose port (if needed for future HTTP interface)
EXPOSE 8000

# Set the default command to run the MCP server in SSE mode for network access
CMD ["uv", "run", "python", "-m", "data_query_server", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
