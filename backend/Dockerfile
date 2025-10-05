FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency manifests and app code
COPY pyproject.toml .
COPY README.md .
COPY uv.lock .
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Install dependencies from lock file
RUN uv sync --frozen --no-dev

# Expose port
EXPOSE 8000

# Default command
CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]