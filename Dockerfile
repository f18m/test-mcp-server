# Use Python 3.14 slim image as base
FROM python:3.14-slim

LABEL org.opencontainers.image.source=https://github.com/f18m/test-mcp-server

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY main.py .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose the default MCP server port
EXPOSE 8000

# Set environment variable defaults (can be overridden at runtime)
ENV MCP_BEARER_TOKEN=default-secret-token-change-me

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/mcp', timeout=5, headers={'Authorization': f'Bearer {__import__(\"os\").getenv(\"MCP_BEARER_TOKEN\")}'}).raise_for_status()" || exit 1

# Run the MCP server
CMD ["python", "main.py"]
