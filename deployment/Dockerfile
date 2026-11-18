# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY agent/ ./agent/
COPY corpus/ ./corpus/
COPY evaluation/ ./evaluation/
COPY observability/ ./observability/
COPY orchestration/ ./orchestration/
COPY browser_agent/ ./browser_agent/

ENV PYTHONUNBUFFERED=1
ENV OLLAMA_URL="http://host.docker.internal:11434/api/generate"

EXPOSE 8000

# Default healthcheck / evaluation run
CMD ["python", "evaluation/ci_gate.py"]
