FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    AZURE_CHAT_MODEL=DeepSeek-V3.2 \
    AZURE_CHAT_MODEL_VERSION=1

COPY pyproject.toml Fase3.md ./
COPY *.py ./
COPY knowledge/ ./knowledge/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

CMD ["python", "rag_ejemplo.py"]
