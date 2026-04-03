# Fase 3. Aplicación de la ingeniería de prompts (mini chat)

Objetivo: ver en código cómo se arma **contexto + instrucciones** (prompt) a partir de datos de prueba, y cómo eso condiciona la respuesta del modelo. No hay frontend avanzado, autenticación, base de datos real ni despliegue: solo consola, archivos JSON/TXT y una llamada HTTP al modelo.

## Contenido de la carpeta

| Archivo | Rol |
|--------|-----|
| `app.py` | Bucle de chat: interpreta la consulta, inyecta datos en la plantilla y llama a **Ollama** (o solo muestra el prompt). |
| `model.py` | Conexión y llamada al LLM vía **Ollama** (arranque, resolución de modelo y generación). |
| `pyproject.toml` | Dependencias del proyecto (`requests`); instalar con `pip install .` o `pip install -e .` desde esta carpeta. |
| `data/BD_solicitud_de_pedido.json` | “Base de datos” de ejemplo: al menos 10 pedidos con estado, fecha estimada y enlace de rastreo. |
| `data/BD_politicas_devolucion.json` | Reglas de devolución (qué sí / qué no, p. ej. perecederos o higiene). |
| `prompt/prompt_solicitud_pedido.txt` | Plantilla: rol de agente, datos `{{PEDIDOS_ECOMARKET}}`, consulta con `{{tracking_number}}`, instrucciones y formato de salida. |
| `prompt/prompt_devolucion.txt` | Plantilla: política `{{POLITICAS_DEVOLUCION_ECOMARKET}}`, datos del cliente (`product_name`, etc.) e instrucciones para decidir con empatía. |

Los marcadores `{{...}}` se reemplazan en `app.py` con texto JSON legible para el modelo.

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

| Pregunta (ejemplo en el chat) | Respuesta esperada (contenido mínimo) |
|--------------------------------|---------------------------------------|
| `¿Estado de mi pedido EM-1002?` | Estado **En tránsito**, fecha estimada **2026-04-04**, enlace `https://tracking.ecomarket.com/EM-1002`, tono cordial. |
| `¿Qué pasó con EM-1004?` | Estado **Retrasado**, fecha estimada **2026-04-08**, mismo enlace de rastreo, **disculpa breve** por el retraso. |
| `EM-1005` | Estado **Cancelado**, indicar que **no hay** fecha estimada de entrega (o “No aplica”), enlace si el prompt lo pide para consulta; sin inventar nueva fecha. |
| `¿Dónde está EM-1010?` | Estado **Entregado**, fecha **2026-03-27**, enlace `https://tracking.ecomarket.com/EM-1010`. |
| `Pedido EM-9999` | El código **no está** en la base: decirlo claramente y sugerir verificar el número o contactar soporte **sin inventar** un estado. |

### Devoluciones

Entrada en una línea con tres partes separadas por `|` o `;` (ver `ayuda` en la consola). Ejemplos:

1. **Entrada:** `yogurt natural ; sin abrir ; EM-1001`  
   **Esperado:** **No** procede devolución (encaja en **perecederos** / alimentos); explicación breve según política; **empatía**; alternativa razonable (p. ej. soporte) sin prometer excepciones no escritas.

2. **Entrada:** `jabón líquido ; sin abrir ; EM-1002`  
   **Esperado:** **No** procede (**higiene personal**); mismo criterio de claridad y empatía.

3. **Entrada:** `bolsa ecológica comprada ; nueva con etiquetas ; EM-1003`  
   **Esperado:** **Sí** puede proceder si cumple **Bolsas ecológicas** (hasta **15 días**); pasos acordes a la **regla_general** (pedido, motivo, estado del producto) y plazo de la categoría.

4. **Entrada:** `camiseta de algodón orgánico ; con etiquetas originales ; EM-1006`  
   **Esperado:** Tratar como **ropa sostenible**: devolución posible hasta **20 días** con etiquetas, si la condición cuadra con la política.

5. **Entrada:** `crema facial ; abierta y usada ; EM-1007`  
   **Esperado:** **No** procede por **cosméticos abiertos** y/o **productos usados**; respuesta empática y alineada a las exclusiones del JSON.

Si el modelo se aleja de estos hechos, conviene revisar el prompt o los datos inyectados antes que el modelo en sí.

## Modelo (solo Ollama)

La app usa la API HTTP de **Ollama** (`/api/tags`, `/api/chat`; si hace falta, `/v1/chat/completions`). Al iniciar, comprueba que el servicio responda; si no, intenta ejecutar `ollama serve` en segundo plano y espera hasta que esté listo (útil en **Google Colab**). Luego **lista los modelos con `/api/tags`**: si el nombre en `OLLAMA_MODEL` no está instalado, el programa termina con un mensaje claro (en Ollama, un **404** en el chat suele significar *modelo no encontrado*, no que falte la ruta `/api/chat`).

Variables útiles:

| Variable | Significado |
|----------|-------------|
| `OLLAMA_BASE_URL` | Por defecto `http://127.0.0.1:11434`. |
| `OLLAMA_HOST` | Por defecto `127.0.0.1:11434` (variable que usa el CLI de Ollama; la app la fija con `setdefault` si hace falta). |
| `OLLAMA_MODEL` | Por defecto `llama3.2`. Debe coincidir con un modelo que hayas descargado (`ollama pull ...`). |
| `ECOMARKET_PROMPT_ONLY` | `1` = no llama a Ollama; solo imprime el prompt generado (útil para depurar prompts sin GPU). |

### Ejemplo: `llama3.1` en Windows (PowerShell)

Desde `Fase3/`, con el entorno virtual activado:

```powershell
ollama pull llama3.1
$env:OLLAMA_MODEL="llama3.1"
python app.py
```

La variable `OLLAMA_MODEL` solo afecta a **esa** ventana de PowerShell hasta que la cierres (si quieres dejarla fija en la sesión, puedes repetir el `$env:OLLAMA_MODEL=...` antes de cada ejecución o configurarla en el sistema).

### Entorno tipo Google Colab (instalación)

En una celda del cuaderno puedes instalar dependencias del sistema y Ollama antes de ejecutar `app.py`:

```bash
apt-get update -qq && apt-get install -y zstd
if ! command -v ollama >/dev/null 2>&1; then curl -fsSL https://ollama.com/install.sh | sh; else echo "Ollama ya está instalado."; fi
```

Luego instala el paquete Python (desde la carpeta que contiene `pyproject.toml`):

```bash
pip install .
```

Descarga el modelo y arranca el chat (Ollama puede iniciarse solo al correr `app.py` si aún no hay servidor en el puerto):

```bash
ollama pull llama3.2
python app.py
```

## Idea pedagógica

1. **Solicitud de pedido:** el modelo solo debe usar filas presentes en el JSON; el prompt prohíbe inventar y pide tono, fecha, enlace y disculpa si hay retraso.
2. **Devolución:** el modelo debe combinar el nombre del producto con las listas *con* / *sin* devolución y responder con claridad aunque no proceda la devolución.

Cambiar una política o un pedido en los JSON y repetir la misma pregunta suele mostrar de inmediato el efecto del **contexto inyectado** sin tocar el código de la app.
