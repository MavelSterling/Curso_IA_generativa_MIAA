# Curso IA generativa — MIAA

Repositorio de trabajo para la asignatura de **inteligencia artificial generativa** dentro de la **Maestría en Inteligencia Artificial Aplicada (MIAA)**. Aquí se concentran los entregables y experimentos de los talleres del curso.

## Integrantes

- Felipe Guerra
- Mavelyn Sterling

## Contenido del repositorio

El desarrollo del **Taller 1** está organizado en **tres fases**, en torno al caso EcoMarket (atención al cliente con IA generativa):

| Fase | Ubicación                            | Contenido                                                                                                                                                                                                                           |
| ---- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | [`Taller1/Fase1.md`](Taller1/Fase1.md) | Selección y justificación del modelo de IA y arquitectura híbrida propuesta.                                                                                                                                                     |
| 2    | [`Taller1/Fase2.md`](Taller1/Fase2.md) | Evaluación de fortalezas, limitaciones y riesgos éticos de la solución.                                                                                                                                                          |
| 3    | [`Taller1/Fase3/`](Taller1/Fase3/)     | **Aplicación de chatbot** (mini chat en consola) para **probar ingeniería de prompts**: consultas de pedidos y devoluciones, datos de ejemplo en JSON, plantillas en `prompt/` e integración con **Ollama**. |

La guía técnica de la Fase 3 (estructura del código, flujo, variables de entorno, Docker y ejemplos) está en [`Taller1/Fase3/Fase3.md`](Taller1/Fase3/Fase3.md).

## Inicio rápido (Taller 1 — Fase 3, chatbot)

Requisitos: **Python 3**, **Ollama** instalado y en ejecución con un modelo descargado (por ejemplo `llama3.2`, según indique el proyecto).

Desde la carpeta `Taller1/Fase3/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install .
python app.py
```

En Linux o macOS, activa el entorno con `source .venv/bin/activate` en lugar del script de PowerShell.

**Cómo ejecutar la aplicación** con el detalle completo (entorno, Ollama, variables como `OLLAMA_BASE_URL` y `OLLAMA_MODEL`, Docker, errores frecuentes, etc.) está explicado en el README de la Fase 3: [`Taller1/Fase3/Fase3.md`](Taller1/Fase3/Fase3.md).
