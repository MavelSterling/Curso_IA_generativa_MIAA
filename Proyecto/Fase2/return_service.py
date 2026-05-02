from __future__ import annotations

from datetime import date
import hashlib
import re
from typing import Any
import unicodedata

ORDERS: dict[str, dict[str, Any]] = {
    "EM-1001": {
        "status": "entregado",
        "delivery_date": "2026-03-28",
        "products": ["ECO-1001", "ECO-1002"],
    },
    "EM-1002": {
        "status": "en transito",
        "delivery_date": None,
        "products": ["ECO-1003"],
    },
    "EM-1003": {
        "status": "preparando envio",
        "delivery_date": None,
        "products": ["ECO-1004"],
    },
    "EM-1004": {
        "status": "retrasado",
        "delivery_date": None,
        "products": ["ECO-1006"],
    },
    "EM-1006": {
        "status": "entregado",
        "delivery_date": "2026-03-30",
        "products": ["ECO-1003", "ECO-1005"],
    },
    "EM-1010": {
        "status": "entregado",
        "delivery_date": "2026-03-27",
        "products": ["ECO-1004"],
    },
}

PRODUCT_POLICIES: dict[str, dict[str, Any]] = {
    "ECO-1001": {"name": "Botella reutilizable 750ml", "max_days": 30, "requires_new": True},
    "ECO-1002": {"name": "Bolsa ecologica premium", "max_days": 15, "requires_new": False},
    "ECO-1003": {"name": "Organizador reciclado modular", "max_days": 30, "requires_new": False},
    "ECO-1004": {"name": "Camiseta de algodon organico", "max_days": 20, "requires_new": True},
    "ECO-1005": {"name": "Kit higiene personal bamboo", "max_days": 0, "returnable": False},
    "ECO-1006": {"name": "Crema facial natural", "max_days": 0, "returnable": False},
}

NON_RETURNABLE_CATEGORIES_MESSAGE = (
    "El producto pertenece a una categoria sin devolucion segun la politica de EcoMarket."
)


def _normalize_text(value: str | None) -> str:
    base = unicodedata.normalize("NFKD", (value or "").strip().lower())
    return "".join(char for char in base if not unicodedata.combining(char))


def _is_valid_email(email: str | None) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (email or "").strip()))


def consultar_estado_pedido(order_id: str) -> dict[str, Any]:
    order_key = (order_id or "").strip().upper()
    if not order_key:
        return {
            "success": False,
            "found": False,
            "message": "Debes indicar un numero de pedido con formato EM-XXXX.",
        }

    order_data = ORDERS.get(order_key)
    if not order_data:
        return {
            "success": False,
            "found": False,
            "order_id": order_key,
            "message": "No se encontro un pedido con ese identificador.",
        }

    return {
        "success": True,
        "found": True,
        "order_id": order_key,
        "status": order_data["status"],
        "delivery_date": order_data["delivery_date"],
        "products": list(order_data["products"]),
    }


def verificar_elegibilidad_producto(
    order_id: str,
    product_id: str,
    estado_producto: str,
    motivo_devolucion: str | None = None,
    dias_desde_compra: int | None = None,
) -> dict[str, Any]:
    order_result = consultar_estado_pedido(order_id)
    if not order_result.get("success"):
        return {
            "success": True,
            "eligible": False,
            "reason": order_result.get("message", "No se pudo validar el pedido."),
            "next_step": "Verifica el numero de pedido e intentalo de nuevo.",
        }

    if order_result["status"] != "entregado":
        return {
            "success": True,
            "eligible": False,
            "reason": f"El pedido {order_result['order_id']} aun no tiene estado entregado.",
            "next_step": "Debes esperar la entrega para iniciar una devolucion.",
        }

    normalized_product = (product_id or "").strip().upper()
    if normalized_product not in order_result["products"]:
        return {
            "success": True,
            "eligible": False,
            "reason": "El producto no pertenece al pedido indicado.",
            "next_step": "Confirma el codigo de producto o valida tu historial de compras.",
        }

    policy = PRODUCT_POLICIES.get(normalized_product)
    if not policy:
        return {
            "success": True,
            "eligible": False,
            "reason": "No existe informacion de politica para ese producto.",
            "next_step": "Contacta soporte para revision manual.",
        }

    if not policy.get("returnable", True):
        return {
            "success": True,
            "eligible": False,
            "reason": NON_RETURNABLE_CATEGORIES_MESSAGE,
            "next_step": "Podemos escalar tu caso a soporte humano para revisar alternativas.",
        }

    normalized_state = _normalize_text(estado_producto)
    if normalized_state in {"usado", "danado"}:
        return {
            "success": True,
            "eligible": False,
            "reason": "El estado reportado del producto no cumple las condiciones de devolucion.",
            "next_step": "Si llego defectuoso, te recomiendo solicitar revision con soporte humano.",
        }

    if policy.get("requires_new") and normalized_state not in {"sin uso", "sin uso / nuevo", "nuevo"}:
        return {
            "success": True,
            "eligible": False,
            "reason": "Este producto solo admite devolucion si esta nuevo y sin uso.",
            "next_step": "Si necesitas ayuda adicional, puedo escalar el caso a soporte.",
        }

    days = dias_desde_compra

    max_days = int(policy.get("max_days", 0))
    if days is not None and days > max_days:
        return {
            "success": True,
            "eligible": False,
            "reason": f"El producto supera el plazo maximo de {max_days} dias para devolucion.",
            "next_step": "Puedes contactar soporte para revisar excepciones.",
        }

    return {
        "success": True,
        "eligible": True,
        "order_id": order_result["order_id"],
        "product_id": normalized_product,
        "reason": "El producto cumple las condiciones de devolucion.",
        "next_step": "Puedes generar la etiqueta de devolucion.",
        "motivo_devolucion": (motivo_devolucion or "").strip() or None,
    }


def generar_etiqueta_devolucion(order_id: str, product_id: str, customer_email: str) -> dict[str, Any]:
    order_result = consultar_estado_pedido(order_id)
    if not order_result.get("success"):
        return {
            "success": False,
            "label_generated": False,
            "message": "No se puede generar la etiqueta porque el pedido no es valido.",
        }

    normalized_product = (product_id or "").strip().upper()
    if normalized_product not in order_result["products"]:
        return {
            "success": False,
            "label_generated": False,
            "message": "No se puede generar la etiqueta porque el producto no coincide con el pedido.",
        }

    if not _is_valid_email(customer_email):
        return {
            "success": False,
            "label_generated": False,
            "message": "Debes proporcionar un correo valido para emitir la etiqueta.",
        }

    token = f"{order_result['order_id']}|{normalized_product}|{customer_email.strip().lower()}|{date.today().isoformat()}"
    label_suffix = hashlib.sha1(token.encode("utf-8")).hexdigest()[:8].upper()
    label_id = f"RET-{label_suffix}"

    return {
        "success": True,
        "label_generated": True,
        "label_id": label_id,
        "order_id": order_result["order_id"],
        "product_id": normalized_product,
        "tracking_url": f"https://ecomarket.example.com/devoluciones/{label_id}",
        "message": "Etiqueta de devolucion generada exitosamente.",
    }
