from __future__ import annotations

import re
from typing import Any

TRACKING_RE = re.compile(r"\b(EM-\d+)\b", re.IGNORECASE)


def try_parse_devolucion_en_linea(text: str) -> tuple[str, str, str] | None:
    """
    Espera 3 partes separadas por `|` o `;`:
      producto | condición | EM-xxxx
    """

    parts = re.split(r"\s*[|;]\s*", text.strip())
    parts = [p for p in parts if p]
    if len(parts) == 3 and TRACKING_RE.fullmatch(parts[2].strip()):
        return parts[0].strip(), parts[1].strip(), parts[2].strip().upper()

    # Soporta el formato:
    #   devolución: producto | condición | EM-xxxx
    m = re.match(
        r"(?is)^\s*(?:devolución|devolucion|devolver)\s*:\s*(.+)$", text.strip()
    )
    if not m:
        return None

    inner_parts = re.split(r"\s*[|;]\s*", m.group(1).strip())
    inner_parts = [p for p in inner_parts if p]
    if len(inner_parts) >= 3:
        return (
            inner_parts[0].strip(),
            inner_parts[1].strip(),
            inner_parts[2].strip().upper(),
        )

    return None


def clasificar_consulta(texto: str) -> tuple[str, Any]:
    """
    Devuelve:
      - ("devolucion", (product_name, product_condition, order_number))
      - ("pedido", tracking_number)
      - ("devolucion_incompleta", None)
      - ("ayuda", None)
    """

    dev = try_parse_devolucion_en_linea(texto)
    if dev:
        return "devolucion", dev

    m = TRACKING_RE.search(texto)
    if m:
        return "pedido", m.group(1).upper()

    bajo = texto.lower()
    if any(
        k in bajo
        for k in (
            "devoluc",
            "devolver",
            "reembols",
            "quiero devolver",
            "quiero la devolución",
        )
    ):
        return "devolucion_incompleta", None

    return "ayuda", None

