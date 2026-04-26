import os
import time
from typing import Any
from urllib.parse import urlparse

import requests

AZURE_ENDPOINT = os.environ.get("AZURE_CHAT_COMPLETIONS_ENDPOINT", "").strip()
AZURE_API_KEY = os.environ.get("AZURE_CHAT_COMPLETIONS_API_KEY", "").strip()
AZURE_MODEL = os.environ.get("AZURE_CHAT_MODEL", "DeepSeek-V3.2").strip()
AZURE_MODEL_VERSION = os.environ.get("AZURE_CHAT_MODEL_VERSION", "1").strip()


def _require_env(name: str, value: str) -> str:
    if value:
        return value
    raise RuntimeError(f"Falta variable requerida: {name}")


def _generation_options() -> dict[str, Any]:
    raw = os.environ.get("AZURE_TEMPERATURE", "0.1").strip()
    try:
        temperature = float(raw)
    except ValueError:
        temperature = 0.1
    temperature = max(0.0, min(2.0, temperature))
    return {"temperature": temperature}


def resolve_model_once() -> str:
    _require_env("AZURE_CHAT_COMPLETIONS_ENDPOINT", AZURE_ENDPOINT)
    _require_env("AZURE_CHAT_COMPLETIONS_API_KEY", AZURE_API_KEY)
    return AZURE_MODEL


def complete_chat_azure(messages: list[dict[str, Any]]) -> str:
    endpoint = _require_env("AZURE_CHAT_COMPLETIONS_ENDPOINT", AZURE_ENDPOINT)
    api_key = _require_env("AZURE_CHAT_COMPLETIONS_API_KEY", AZURE_API_KEY)

    body: dict[str, Any] = {
        "messages": messages,
        "model": AZURE_MODEL,
        **_generation_options(),
    }
    if AZURE_MODEL_VERSION:
        body["model_version"] = AZURE_MODEL_VERSION

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    max_attempts = 5
    response: requests.Response | None = None
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.post(endpoint, headers=headers, json=body, timeout=180)
            last_error = None
            break
        except requests.exceptions.RequestException as error:
            last_error = error
            if attempt == max_attempts:
                break
            time.sleep(min(2 * attempt, 8))

    if response is None:
        host = urlparse(endpoint).netloc or endpoint
        raise RuntimeError(
            "No fue posible conectar con el endpoint de DeepSeek-V3.2. "
            f"Fallo de red/DNS al resolver o conectar con: {host}"
        ) from last_error

    if response.status_code != 200:
        detail = response.text.strip()
        raise RuntimeError(
            f"Azure Chat Completions devolvio HTTP {response.status_code}: {detail}"
        )

    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("Azure devolvio respuesta sin choices.")
    message = choices[0].get("message") or {}
    content = (message.get("content") or "").strip()
    if not content:
        raise RuntimeError("Azure devolvio respuesta vacia.")
    return content


def run_model(user_prompt: str) -> str:
    resolve_model_once()
    messages = [{"role": "user", "content": user_prompt}]
    return complete_chat_azure(messages)
