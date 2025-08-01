FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv pip install --system --no-cache-dir -r pyproject.toml

WORKDIR /app

COPY main.py .
COPY src src/

RUN mkdir -p /app/data /app/report

ENTRYPOINT ["python", "-u", "main.py"]
