# Fase 3. Aplicación de la ingeniería de prompts (mini chat)

## Objetivo de la aplicación de la Ingeniería de Prompts.

En esta fase práctica, los estudiantes diseñarán prompts para su modelo. Esto les permitirá entender la conexión directa entre la instrucción y el resultado.

Para esto, los estudiantes pueden usar una estructura similar a la que abordamos en el tutorial práctico de prompts en la primera sesión. La idea es poder ver, en código, cómo se estructura una cadena de prompts con el fin de que los usuarios puedan obtener respuestas óptimas en sus interacciones con el chat de atención al cliente.

**Nota**: si bien en las primeras fases los estudiantes pueden proponer un modelo complejo o un modelo de pago, para este ejercicio pueden usar un modelo open-source sin ningún problema, con el fin de evidenciar el impacto de los prompts.

### Ejercicios de prompts

1. **Prompt de Solicitud de Pedido**: redactar un prompt que le pida al modelo el estado de un pedido, proporcionando el número de seguimiento. Deben crear y agregar al prompt, como parte del proceso, un documento/texto con el estado de 10 pedidos como mínimo. Este documento es un ejemplo de prueba y actuará como la base de datos para que el modelo pueda responder ante las solicitudes.
   - **Ejemplo de prompt básico**: "Dame el estado del pedido 12345."
   - **Ejemplo de prompt mejorado**: "Actúa como un agente de servicio al cliente amable. Proporciona el estado actual del pedido con el número de seguimiento '{{tracking_number}}'. Incluye una estimación de la fecha de entrega y un enlace para rastrear el paquete en tiempo real. Si el pedido está retrasado, ofrece una disculpa y una breve explicación."

2. **Prompt de Devolución de Producto**: crear un prompt para guiar al cliente en el proceso de devolución.
   - **Desafío**: diseñar el prompt para que el modelo sea capaz de distinguir entre productos que pueden devolverse y los que no (ej.: productos perecederos, productos de higiene). La respuesta debe ser clara y empática, incluso si la devolución no es posible.

Demo en video: [https://www.youtube.com/watch?v=h99ReCGX_qg](https://www.youtube.com/watch?v=h99ReCGX_qg)

## Contenido de la carpeta

| Archivo                                | Rol                                                                                                                                                |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app.py`                             | Interfaz de consola: lee input del usuario, muestra ayuda/salida y delega lógica a otros módulos.                                                |
| `classifier.py`                      | Detecta tipo de consulta (`pedido`, `devolucion`, `devolucion_incompleta`, `ayuda`) y extrae datos.                                        |
| `prompt_builder.py`                  | Construye prompts finales para pedido/devolución inyectando JSON en las plantillas TXT.                                                           |
| `data_loader.py`                     | Carga archivos `JSON` y `TXT` desde `data/` y `prompt/`.                                                                                   |
| `model.py`                           | Conexión y llamada al LLM vía**Ollama** (arranque, resolución de modelo y generación).                                                   |
| `pyproject.toml`                     | Dependencias del proyecto (`requests`); instalar con `pip install .` o `pip install -e .` desde esta carpeta.                                |
| `data/BD_solicitud_de_pedido.json`   | “Base de datos” de ejemplo: al menos 10 pedidos con estado, fecha estimada y enlace de rastreo.                                                  |
| `data/BD_politicas_devolucion.json`  | Reglas de devolución (qué sí / qué no, p. ej. perecederos o higiene).                                                                          |
| `prompt/prompt_solicitud_pedido.txt` | Plantilla: rol de agente, datos `{{PEDIDOS_ECOMARKET}}`, consulta con `{{tracking_number}}`, instrucciones y formato de salida.                |
| `prompt/prompt_devolucion.txt`       | Plantilla: política `{{POLITICAS_DEVOLUCION_ECOMARKET}}`, datos del cliente (`product_name`, etc.) e instrucciones para decidir con empatía. |

Los marcadores `{{...}}` se reemplazan en `prompt_builder.py` con texto JSON legible para el modelo.

## Estructura de la aplicación

Árbol principal de la carpeta `Fase3/` (los caminos son relativos a esta carpeta):

```text
Fase3/
├── app.py                 # Punto de entrada: consola, comandos, bucle de chat
├── classifier.py          # Clasificación de la consulta y extracción de datos
├── prompt_builder.py      # Sustitución de placeholders en plantillas .txt
├── data_loader.py         # Lectura de JSON/TXT (rutas base a data/ y prompt/)
├── model.py               # Ollama: salud del servicio, modelo y generación
├── pyproject.toml         # Dependencias e instalación del paquete
├── data/
│   ├── BD_solicitud_de_pedido.json
│   └── BD_politicas_devolucion.json
└── prompt/
    ├── prompt_solicitud_pedido.txt
    └── prompt_devolucion.txt
```

### Capas y dependencias entre módulos

| Capa                          | Archivos                                  | Responsabilidad                                                                           |
| ----------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------------- |
| Presentación                 | `app.py`                                | `input`/`print`, ayuda, orquestación del flujo hacia el prompt y Ollama.      |
| Intención y datos de usuario | `classifier.py`                         | Decide si la entrada es pedido, devolución, devolución incompleta o ayuda.              |
| Contexto + prompt             | `prompt_builder.py`, `data_loader.py` | Carga datos y plantillas; sustituye `{{...}}` y devuelve el texto final para el modelo. |
| Proveedor LLM                 | `model.py`                              | HTTP a Ollama (`/api/tags`, `/api/chat`, fallback OpenAI si aplica).                  |

**Orden de dependencias (quién importa a quién):**

- `app.py` importa `classifier`, `prompt_builder` y `model`.
- `prompt_builder.py` importa `data_loader` (para rutas y lectura de archivos).
- `classifier.py` no depende de Ollama ni de los prompts (solo reglas sobre el texto).

El ejecutable lógico es `python app.py`; el resto son módulos importados en el mismo directorio.

## Flujo de ejecución

1. El usuario escribe una consulta en consola (`app.py`).
2. `classifier.py` decide si es estado de pedido, devolución o ayuda.
3. `prompt_builder.py` arma el prompt con plantillas y datos de `data/*.json`.
4. `model.py` valida Ollama/modelo y envía el prompt al LLM.
5. `app.py` imprime la respuesta final o un error entendible.

## Cómo hablar con el bot

Desde la carpeta `Fase3/`, usa un **entorno virtual** (`.venv`) para no mezclar dependencias con el Python del sistema:

```bash
python -m venv .venv
```

Activa el entorno:

- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **Windows (cmd):** `.venv\Scripts\activate.bat`
- **Linux / macOS:** `source .venv/bin/activate`

Instala el proyecto y ejecuta el chat:

```bash
pip install --upgrade pip
pip install .
python app.py
```

El repositorio incluye un `.gitignore` en la raíz que excluye `.venv/`, `*.egg-info/` y otros artefactos de Python.

Ejemplos de entrada:

- **Estado de pedido:** pregunta que incluya un código como `EM-1004`, p. ej. `¿Dónde va mi pedido EM-1004?`
- **Devolución en una línea:** `producto | condición | pedido`, por ejemplo `yogurt natural | sin abrir | EM-1001`, o `devolución: bolsa ecológica | nueva | EM-1002`
- **Devolución guiada:** escribe solo `devolución` y responde a las tres preguntas.
- **`ayuda`** / **`salir`**

Si la consulta no encaja en pedido ni devolución, el programa muestra ejemplos.

## Ejemplos de preguntas y respuesta esperada

Las respuestas reales las redacta el modelo; lo importante es que **no contradigan el JSON** y cumplan el tono y la estructura del prompt (saludo, datos concretos, cierre). Abajo se indica qué debe contener cada respuesta “correcta” según la base de prueba.

### Consulta de estado de pedido

| Pregunta (ejemplo en el chat)      | Respuesta esperada (contenido mínimo)                                                                                                                                    |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `¿Estado de mi pedido EM-1002?` | Estado **En tránsito**, fecha estimada **2026-04-04**, enlace `https://tracking.ecomarket.com/EM-1002`, tono cordial.                                     |
| `¿Qué pasó con EM-1004?`      | Estado **Retrasado**, fecha estimada **2026-04-08**, mismo enlace de rastreo, **disculpa breve** por el retraso.                                         |
| `EM-1005`                        | Estado **Cancelado**, indicar que **no hay** fecha estimada de entrega (o “No aplica”), enlace si el prompt lo pide para consulta; sin inventar nueva fecha. |
| `¿Dónde está EM-1010?`        | Estado **Entregado**, fecha **2026-03-27**, enlace `https://tracking.ecomarket.com/EM-1010`.                                                                 |
| `Pedido EM-9999`                 | El código **no está** en la base: decirlo claramente y sugerir verificar el número o contactar soporte **sin inventar** un estado.                          |

### Devoluciones

Formatos de entrada (una sola línea; ver también `ayuda` en la consola):

| Formato | Ejemplo |
| ------- | ------- |
| Tres partes con `\|` o `;` | `producto \| condición \| EM-xxxx` |
| Misma idea con prefijo | `devolución: producto \| condición \| EM-xxxx` |
| Lenguaje natural con comas | `devolver producto, condición` — el `EM-xxxx` al **final**, separado por comas, es **opcional** (p. ej. `devolver bolsa ecológica, nueva, EM-1003`). Si falta el pedido, el prompt marca **(no indicado)** y el modelo debe seguir aplicando la política al producto. |

Ejemplos de comportamiento esperado (según `BD_politicas_devolucion.json`):

| Entrada (ejemplo en el chat) | Respuesta esperada (contenido mínimo) |
| ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| `yogurt natural ; sin abrir ; EM-1001` | **No** procede: encaja en **Productos perecederos** (o alimentos perecederos); explicación breve según política; **empatía**; alternativa razonable (p. ej. contactar soporte EcoMarket) **sin** prometer excepciones no escritas. |
| `devolver yogurt natural, sin abrir` | Mismo criterio que la fila anterior; el número de pedido aparece como **(no indicado)** en el prompt — el veredicto sobre el producto sigue siendo **no procede** por perecedero; puede pedirse el `EM-xxxx` para futuras gestiones según **regla_general**. |
| `jabón líquido ; sin abrir ; EM-1002` | **No** procede: **Productos de higiene personal**; claridad, empatía y alternativa sin inventar reglas. |
| `bolsa ecológica comprada ; nueva con etiquetas ; EM-1003` | **Sí** puede proceder si encaja en **Bolsas ecológicas** — plazo **hasta 15 días** tal como en el JSON; **regla_general**: pedido, motivo de devolución y estado del producto; pasos concretos sin repetir datos ya dichos. |
| `devolver bolsa ecológica, nueva con etiquetas, EM-1003` | Equivalente al caso anterior (mismo veredicto y plazo) usando el formato con comas y pedido al final. |
| `camiseta de algodón orgánico ; con etiquetas originales ; EM-1006` | Tratar como **Ropa sostenible**: devolución posible **hasta 20 días con etiquetas originales** si la condición declarada coincide con la política de esa categoría. |
| `crema facial ; abierta y usada ; EM-1007` | **No** procede: al menos una de **Cosméticos abiertos** y **Productos usados o sin empaque original**; respuesta empática y alineada a las exclusiones del JSON. |
| devolver crema facial abierta y usada

Si el modelo se aleja de estos hechos, conviene revisar el **prompt**, el **clasificador** (formatos aceptados) o los **datos inyectados** antes que culpar solo al modelo.

## Modelo (solo Ollama)

La app usa la API HTTP de **Ollama** (`/api/tags`, `/api/chat`; si hace falta, `/v1/chat/completions`). Al iniciar, comprueba que el servicio responda; si no, intenta ejecutar `ollama serve` en segundo plano y espera hasta que esté listo. Luego lista los modelos con `/api/tags`: si el nombre en `OLLAMA_MODEL` no está instalado, el programa termina con un mensaje explícito.

Variables útiles:

| Variable                  | Significado                                                                                                           |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `OLLAMA_BASE_URL`       | Por defecto `http://127.0.0.1:11434`.                                                                               |
| `OLLAMA_HOST`           | Por defecto `127.0.0.1:11434` (variable que usa el CLI de Ollama; la app la fija con `setdefault` si hace falta). |
| `OLLAMA_MODEL`          | Por defecto `llama3.2`. Debe coincidir con un modelo que hayas descargado (`ollama pull ...`).                    |

### Errores comunes y cómo resolverlos

1. **Mensaje:** `No se pudo conectar con Ollama ...`**Causa típica:** servicio apagado o URL incorrecta.**Solución:** inicia Ollama con `ollama serve` y valida `OLLAMA_BASE_URL`.
2. **Mensaje:** `El modelo llama3.2 no está instalado.`**Causa típica:** `OLLAMA_MODEL` no coincide con lo descargado.**Solución:** instala ese modelo (`ollama pull llama3.2`) o ajusta la variable al modelo existente.
3. **Caso frecuente en clase:** instalaste `llama3.1`, pero configuraste `OLLAMA_MODEL=llama3.2`.**Qué hacer:** alinea ambos valores.

   - Opción A: `ollama pull llama3.2`
   - Opción B: `$env:OLLAMA_MODEL="llama3.1"` (PowerShell)

### Ejemplo: `llama3.1` en Windows (PowerShell)

Desde `Fase3/`, con el entorno virtual activado:

```powershell
ollama pull llama3.1
$env:OLLAMA_MODEL="llama3.1"
python app.py
```

La variable `OLLAMA_MODEL` solo afecta a **esa** ventana de PowerShell hasta que la cierres (si quieres dejarla fija en la sesión, puedes repetir el `$env:OLLAMA_MODEL=...` antes de cada ejecución o configurarla en el sistema).

Luego instala el paquete Python (desde la carpeta que contiene `pyproject.toml`):

```bash
pip install .
```

Descarga el modelo y arranca el chat (Ollama puede iniciarse solo al correr `app.py` si aún no hay servidor en el puerto):

```bash
ollama pull llama3.2
python app.py
```

## Ejecución con Docker

Desde la raíz del repositorio, entra en la carpeta de Fase 3 y usa Compose (hay un `docker-compose.yml` que levanta Ollama con `llama3.2` y la imagen de la app):

```powershell
cd Taller1\Fase3

# Primera vez o tras cambiar el código Python
docker compose build fase3

# Motor LLM (segundo plano)
docker compose up -d ollama

# Chat (repetible)
docker compose run --rm -it fase3
```
