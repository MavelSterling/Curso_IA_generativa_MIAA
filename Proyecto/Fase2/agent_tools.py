from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from rag_engine import RAGEngine
from return_service import (
    consultar_estado_pedido,
    generar_etiqueta_devolucion,
    verificar_elegibilidad_producto,
)


def build_rag_tool(rag_engine: RAGEngine):
    @tool("responder_con_rag")
    def responder_con_rag(query: str) -> str:
        """Responde consultas informativas con la base documental de EcoMarket."""
        return rag_engine.answer(query)

    return responder_con_rag


@tool
def tool_consultar_estado_pedido(order_id: str) -> dict[str, Any]:
    """Consulta si un pedido existe y su estado actual."""
    return consultar_estado_pedido(order_id=order_id)


@tool
def tool_verificar_elegibilidad_producto(
    order_id: str,
    product_id: str,
    estado_producto: str,
    motivo_devolucion: str = "",
    dias_desde_compra: int | None = None,
) -> dict[str, Any]:
    """Valida si un producto cumple reglas de devolucion."""
    return verificar_elegibilidad_producto(
        order_id=order_id,
        product_id=product_id,
        estado_producto=estado_producto,
        motivo_devolucion=motivo_devolucion,
        dias_desde_compra=dias_desde_compra,
    )


@tool
def tool_generar_etiqueta_devolucion(
    order_id: str,
    product_id: str,
    customer_email: str,
) -> dict[str, Any]:
    """Genera una etiqueta de devolucion simulada para pedidos elegibles."""
    return generar_etiqueta_devolucion(
        order_id=order_id,
        product_id=product_id,
        customer_email=customer_email,
    )
