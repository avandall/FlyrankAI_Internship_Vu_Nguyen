FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Sync project dependencies (without dev dependencies)
RUN uv sync --frozen --no-dev

# Copy application source code
COPY app/ ./app/
COPY main.py ./

# Expose port and start FastAPI server
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
