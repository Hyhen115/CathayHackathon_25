# syntax=docker/dockerfile:1

FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install curl to fetch uv binary
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Copy project metadata first to leverage Docker layer cache
COPY pyproject.toml uv.lock ./

# Install dependencies with uv (uses uv.lock for reproducible installs)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose Django dev server port
EXPOSE 8000

# Default command: development server (can be overridden by compose)
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
