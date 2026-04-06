import os
import subprocess
import time
from typing import Any

import requests

# URL base del servicio HTTP de Ollama
OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")

# Sin esto, Ollama suele usar temperatura ~0.8: cada respuesta varía mucho y los
# modelos locales a veces inventan negativas o frases incoherentes entre un intento y otro.
def _ollama_generation_options() -> dict[str, Any]:
    raw = os.environ.get("OLLAMA_TEMPERATURE", "0.0").strip()
    try:
        temp = float(raw)
    except ValueError:
        temp = 0.2
    temp = max(0.0, min(2.0, temp))
    opts: dict[str, Any] = {"temperature": temp}
    seed_raw = os.environ.get("OLLAMA_SEED", "").strip()
    if seed_raw.isdigit():
        opts["seed"] = int(seed_raw)
    return opts

# Variable que usa el CLI de Ollama (por si no coincide con la configuración del entorno)
os.environ.setdefault("OLLAMA_HOST", "127.0.0.1:11434")

_ollama_process: subprocess.Popen | None = None
_resolved_ollama_model: str | None = None


def ollama_ready(url: str = OLLAMA_URL) -> bool:
    try:
        response = requests.get(f"{url}/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def _mensaje_sin_conexion(url: str) -> str:
    root = url.rstrip("/")
    return (
        f"No se pudo conectar con Ollama en {root}. "
        "Comprueba que el servicio esté en marcha (por ejemplo `ollama serve`) "
        "y que OLLAMA_BASE_URL apunte al puerto correcto."
    )


def ensure_ollama_running(url: str = OLLAMA_URL) -> None:
    """
    Verifica que Ollama esté levantado.
    Si no responde, intenta lanzar `ollama serve` (útil en entornos tipo Colab).
    """
    global _ollama_process

    if ollama_ready(url):
        print("Ollama está activo.")
        return

    _ollama_process = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    for _ in range(60):
        if ollama_ready(url):
            print("Ollama está activo.")
            return
        time.sleep(2)

    raise RuntimeError(_mensaje_sin_conexion(url))


def ollama_list_model_names(base_url: str) -> list[str]:
    root = base_url.rstrip("/")
    try:
        r = requests.get(f"{root}/api/tags", timeout=10)
        r.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise RuntimeError(_mensaje_sin_conexion(root)) from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(
            f"No se pudo conectar con Ollama en {root}. Detalle: {e}"
        ) from e

    data = r.json()
    names: list[str] = []
    for m in data.get("models") or []:
        n = (m.get("name") or "").strip()
        if n:
            names.append(n)
    return names


def ollama_resolve_model(requested: str, base_url: str) -> str:
    """
    Comprueba que el modelo exista localmente.
    (Ollama suele responder 404 en el chat si el modelo no existe.)
    """
    requested = requested.strip()
    if not requested:
        raise RuntimeError(
            "OLLAMA_MODEL está vacía. Define un modelo, por ejemplo: OLLAMA_MODEL=llama3.2"
        )

    names = ollama_list_model_names(base_url)
    base = requested.split(":")[0]
    if not names:
        raise RuntimeError(
            "Ollama no tiene ningún modelo instalado.\n"
            f"Ejecuta `ollama pull {base}` antes de iniciar la aplicación."
        )

    if requested in names:
        return requested

    for n in names:
        if n.split(":")[0] == base:
            return n

    instalados = ", ".join(names)
    raise RuntimeError(
        f"El modelo {requested} no está instalado.\n"
        f"Ejecuta `ollama pull {base}` antes de iniciar.\n\n"
        f"Modelos instalados ahora: {instalados}\n\n"
        "Si ya descargaste otro modelo, el nombre en OLLAMA_MODEL debe ser el mismo "
        "que ves en `ollama list` (ej.: instalaste llama3.1 y en OLLAMA_MODEL pusiste "
        "llama3.2: alinea ambos o vuelve a hacer pull del modelo que pediste)."
    )


def resolve_ollama_model_once() -> str:
    global _resolved_ollama_model
    if _resolved_ollama_model is None:
        requested = os.environ.get("OLLAMA_MODEL", "llama3.2").strip()
        _resolved_ollama_model = ollama_resolve_model(requested, OLLAMA_URL)
    return _resolved_ollama_model


def complete_chat_ollama(
    messages: list[dict[str, Any]], model: str, base_url: str = OLLAMA_URL
) -> str:
    root = base_url.rstrip("/")
    modelo_base = model.split(":")[0]

    def _post(url: str, payload: dict[str, Any]) -> requests.Response:
        try:
            return requests.post(url, json=payload, timeout=120)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise RuntimeError(_mensaje_sin_conexion(root)) from e

    gen_opts = _ollama_generation_options()
    native = _post(
        f"{root}/api/chat",
        {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": gen_opts,
        },
    )

    if native.status_code == 200:
        return native.json()["message"]["content"].strip()

    # Algunas instalaciones exponen compatibilidad OpenAI.
    if native.status_code == 404:
        compat_body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": gen_opts.get("temperature", 0.2),
        }
        if "seed" in gen_opts:
            compat_body["seed"] = gen_opts["seed"]
        compat = _post(f"{root}/v1/chat/completions", compat_body)
        if compat.status_code == 200:
            data = compat.json()
            return data["choices"][0]["message"]["content"].strip()
        raise RuntimeError(
            f"El modelo {model} no está instalado o no está disponible.\n"
            f"Ejecuta `ollama pull {modelo_base}` antes de iniciar."
        )

    try:
        native.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"Ollama respondió con un error al generar la respuesta.\n"
            f"Si el modelo no existe, ejecuta `ollama pull {modelo_base}` antes de iniciar.\n"
            f"Detalle: {e}"
        ) from e

    raise RuntimeError(
        f"Respuesta inesperada de Ollama (código HTTP {native.status_code})."
    )


def run_model(user_prompt: str) -> str:
    model = resolve_ollama_model_once()
    messages = [
        {
            "role": "system",
            "content": (
                "Cumple las instrucciones del mensaje del usuario con precisión. "
                "Responde en español."
            ),
        },
        {"role": "user", "content": user_prompt},
    ]
    return complete_chat_ollama(messages, model, OLLAMA_URL)
