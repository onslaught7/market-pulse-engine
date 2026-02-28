# 1. Base Image: Python 3.12 (Slim & Stable)
FROM python:3.12-slim

# 2. Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# 3. Copy dependency files first (for Docker layer caching)
COPY api/pyproject.toml api/uv.lock ./

# 4. Install dependencies
# --frozen: Ensures we use exactly what is in uv.lock
# --no-dev: Skip test/dev dependencies
RUN uv sync --frozen --no-dev

# 5. Copy application logic + shared config
COPY api/api.py .
COPY config.py .

# 6. Set Environment
# Point to the virtual environment uv created
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# 7. Expose the API port
EXPOSE 8000

# 8. Run with uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
