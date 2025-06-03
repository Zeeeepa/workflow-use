# Workflow-Use Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY workflow_use/ ./workflow_use/
COPY backend/ ./backend/
COPY cli.py ./
COPY examples/ ./examples/

# Create virtual environment and install dependencies
RUN uv venv /app/.venv
RUN uv sync --no-dev

# Install Playwright browsers
RUN /app/.venv/bin/python -m playwright install --with-deps chromium

# Create non-root user
RUN useradd -m -u 1000 workflow && chown -R workflow:workflow /app
USER workflow

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the backend
CMD ["/app/.venv/bin/python", "-m", "backend.api"]

