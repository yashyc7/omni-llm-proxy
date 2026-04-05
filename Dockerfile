# Multi-stage build for omni-llm-proxy
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml pyproject.lock* ./
COPY . .

# Create virtual environment and install dependencies
RUN uv sync --frozen --no-dev


# Production stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies (Playwright browsers + required system libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libglib2.0-bin \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcb1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app . 

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Load .env file if it exists (users provide via docker run -e or --env-file)
# Default environment variables
ENV DEFAULT_PROVIDER=chatgpt \
    PORT=5000 \
    HEADLESS=true \
    LOGIN_TIMEOUT=120000 \
    RESPONSE_TIMEOUT=60000

# Install Playwright browsers
RUN playwright install chromium

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run application
CMD ["python", "main.py"]
