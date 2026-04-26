# Taller 2 - Fase 3

## Implementacion de sistema RAG para EcoMarket

Esta fase extiende la base practica del Taller 1 e incorpora un flujo RAG completo con:

- Ingestion de conocimiento interno de EcoMarket.
- Segmentacion y vectorizacion con embeddings multilingues.
- Recuperacion por similitud con umbral de relevancia.
- Generacion de respuesta con DeepSeek-V3.2 usando contexto recuperado.
- Fallback controlado cuando no existe evidencia suficiente.

## Estructura

```text
Fase3/
├── app.py
├── rag_ejemplo.py
├── smoke_rag_check.py
├── model.py
├── prompts.py
├── knowledge_base.py
├── rag_engine.py
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── knowledge/
│   ├── politicas_devolucion.md
│   ├── catalogo_productos.csv
│   ├── estados_pedidos.csv
│   └── faq_clientes.json
└── tests/
    ├── test_knowledge_files.py
    └── test_rag_engine.py
```

## Preparacion local

Desde `Taller2/Fase3`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

## Ejecucion

```bash
python rag_ejemplo.py
```

Para validacion no interactiva end-to-end:

```bash
python smoke_rag_check.py
```

Comandos dentro del chat:

- `ayuda`: muestra ejemplos de consulta.
- `reindexar`: reconstruye el indice vectorial desde cero.
- `salir`: finaliza la sesion.

## Flujo tecnico

1. `knowledge_base.py` carga fuentes CSV, JSON y Markdown.
2. Aplica chunking recursivo (`chunk_size=700`, `chunk_overlap=120`).
3. Genera embeddings locales por hashing para indexacion en ChromaDB.
4. Persiste vectores en ChromaDB local (`vectorstore/`).
5. `rag_engine.py` recupera chunks relevantes para cada consulta.
6. `prompts.py` construye prompt con contexto y reglas estrictas.
7. `model.py` invoca DeepSeek-V3.2 a traves de endpoint Azure para generar la respuesta.
8. Si no hay evidencia por encima del umbral, se devuelve fallback.

## Pruebas

Desde `Taller2/Fase3`:

```bash
python -m pytest tests -q
```

## Variables de entorno

La ejecucion usa un archivo `.env` en la raiz de `Fase3` con:

- `AZURE_CHAT_COMPLETIONS_ENDPOINT`
- `AZURE_CHAT_COMPLETIONS_API_KEY`
- `AZURE_CHAT_MODEL`
- `AZURE_CHAT_MODEL_VERSION`

## Ejecucion con Docker

```bash
docker compose build taller2_rag
docker compose run --rm -it taller2_rag
```

## Limitaciones y suposiciones

- El tiempo de respuesta depende de conectividad hacia el endpoint que sirve DeepSeek-V3.2.
- En equipos sin GPU, el rendimiento depende de CPU y memoria disponible.
- La calidad final depende de actualizacion continua de documentos en `knowledge/`.
- Las consultas fuera del alcance documental se responden con mensaje de escalamiento a agente humano.
