FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    AZURE_CHAT_MODEL=DeepSeek-V3.2 \
    AZURE_CHAT_MODEL_VERSION=1

# Copiar archivos de la Fase 2 (necesarios para el motor RAG y el Agente)
COPY Fase2/pyproject.toml ./
COPY Fase2/*.py ./
COPY Fase2/knowledge/ ./knowledge/

# Copiar archivos de la Fase 4 (Streamlit)
COPY Fase4/streamlit_app.py ./

# Instalar dependencias
# Se instala streamlit adicionalmente a las dependencias de pyproject.toml
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && pip install --no-cache-dir streamlit

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0"]
