FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    OLLAMA_BASE_URL=http://ollama:11434 \
    OLLAMA_MODEL=llama3.2

COPY pyproject.toml Fase3.md ./
COPY *.py ./
COPY data/ ./data/
COPY prompt/ ./prompt/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

CMD ["python", "app.py"]
