from __future__ import annotations

import re
from typing import Any

TRACKING_RE = re.compile(r"\b(EM-\d+)\b", re.IGNORECASE)

# Solo la línea completa, para no confundir con "hola, quiero devolver…"
_SALUDOS_LINEA = frozenset(
    {
        "hola",
        "hey",
        "hi",
        "hello",
        "buenas",
        "saludos",
        "buenos dias",
        "buenos días",
        "buenas tardes",
        "buenas noches",
        "buen dia",
        "buen día",
    }
)


def es_saludo(texto: str) -> bool:
    s = texto.strip().lower()
    s = re.sub(r"[!?¡…\.]+$", "", s).strip()
    return bool(s) and s in _SALUDOS_LINEA


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


def try_parse_devolucion_natural_comma(texto: str) -> tuple[str, str, str] | None:
    """
    Formato coloquial en español, separado por comas, p. ej.:
      devolver yogurt natural, sin abrir
      devolver bolsa ecológica, nueva con ticket, EM-1002
    El número de pedido (EM-xxxx) es opcional; si falta, se devuelve cadena vacía.
    """

    t = texto.strip()
    m = re.match(
        r"(?is)^\s*(?:quiero\s+)?(?:devolver|devolución|devolucion)\s+(.+)$",
        t,
    )
    if not m:
        return None

    body = m.group(1).strip()
    if not body:
        return None

    parts = [p.strip() for p in body.split(",") if p.strip()]
    if len(parts) < 2:
        return None

    if TRACKING_RE.fullmatch(parts[-1]):
        order = parts[-1].upper()
        mid = parts[:-1]
        product = mid[0].strip()
        condition = ", ".join(x.strip() for x in mid[1:]) if len(mid) > 1 else ""
        if not condition:
            condition = "no indicada"
        return product, condition, order

    product = parts[0].strip()
    condition = ", ".join(x.strip() for x in parts[1:])
    return product, condition, ""


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

    dev_natural = try_parse_devolucion_natural_comma(texto)
    if dev_natural:
        return "devolucion", dev_natural

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

