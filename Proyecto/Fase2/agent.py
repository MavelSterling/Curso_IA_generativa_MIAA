from __future__ import annotations

import re
from typing import Any
import unicodedata

from agent_logger import log_agent_action
from agent_prompts import AGENT_SYSTEM_PROMPT
from agent_tools import (
    build_rag_tool,
    tool_consultar_estado_pedido,
    tool_generar_etiqueta_devolucion,
    tool_verificar_elegibilidad_producto,
)
from prompts import FALLBACK_MESSAGE
from rag_engine import RAGEngine


class EcoMarketAgent:
    @staticmethod
    def _normalize_text(value: str) -> str:
        base = unicodedata.normalize("NFKD", value.lower())
        return "".join(char for char in base if not unicodedata.combining(char))

    def __init__(self, rag_engine: RAGEngine, enable_logging: bool = True) -> None:
        self.rag_engine = rag_engine
        self.rag_tool = build_rag_tool(rag_engine)
        self.enable_logging = enable_logging
        self.system_prompt = AGENT_SYSTEM_PROMPT

    @staticmethod
    def _extract_order_id(text: str, metadata: dict[str, Any]) -> str | None:
        if metadata.get("order_id"):
            return str(metadata["order_id"]).strip().upper()
        match = re.search(r"\bEM-\d{4,}\b", text.upper())
        return match.group(0) if match else None

    @staticmethod
    def _extract_product_id(text: str, metadata: dict[str, Any]) -> str | None:
        if metadata.get("product_id"):
            return str(metadata["product_id"]).strip().upper()
        match = re.search(r"\bECO-\d{4,}\b", text.upper())
        return match.group(0) if match else None

    @staticmethod
    def _extract_email(text: str, metadata: dict[str, Any]) -> str | None:
        if metadata.get("customer_email"):
            return str(metadata["customer_email"]).strip()
        match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        return match.group(0) if match else None

    @staticmethod
    def _extract_days(text: str) -> int | None:
        match = re.search(r"hace\s+(\d+)\s+d[i\u00ed]as?", text.lower())
        return int(match.group(1)) if match else None

    @staticmethod
    def _normalize_product_state(text: str, metadata: dict[str, Any]) -> str | None:
        raw = EcoMarketAgent._normalize_text(str(metadata.get("estado_producto") or "").strip())
        if raw:
            if "sin uso" in raw or "nuevo" in raw:
                return "sin uso"
            if "abierto" in raw:
                return "abierto"
            if "usado" in raw:
                return "usado"
            if "danado" in raw:
                return "danado"

        lowered = EcoMarketAgent._normalize_text(text)
        if "sin uso" in lowered or "nuevo" in lowered:
            return "sin uso"
        if "abierto" in lowered:
            return "abierto"
        if "usado" in lowered:
            return "usado"
        if "danado" in lowered:
            return "danado"
        return None

    @staticmethod
    def _detect_intent(user_input: str, metadata: dict[str, Any]) -> str:
        interaction_type = EcoMarketAgent._normalize_text(
            str(metadata.get("interaction_type") or "").strip()
        )
        if "consulta" in interaction_type:
            return "rag_query"
        if "solicitud" in interaction_type:
            return "return_process"

        text = EcoMarketAgent._normalize_text(user_input)
        return_keywords = [
            "devolver",
            "devolucion",
            "etiqueta",
            "reembolso",
        ]
        info_keywords = [
            "politica",
            "como funciona",
            "que es",
            "informacion",
        ]
        action_phrases = [
            "quiero devolver",
            "necesito devolver",
            "genera una etiqueta",
            "generar una etiqueta",
            "iniciar devolucion",
            "tramitar devolucion",
        ]
        question_markers = ["cual", "como", "que", "puedo", "?"]

        if "solo quiero informacion" in text or "no quiero iniciar una devolucion" in text:
            return "rag_query"
        if any(phrase in text for phrase in action_phrases):
            return "return_process"
        if any(keyword in text for keyword in info_keywords) and any(
            marker in text for marker in question_markers
        ):
            return "rag_query"

        if any(keyword in text for keyword in return_keywords):
            return "return_process"
        if any(keyword in text for keyword in info_keywords):
            return "rag_query"
        return "general"

    @staticmethod
    def _mask_email(email: str) -> str:
        local, _, domain = email.partition("@")
        if len(local) <= 2:
            return f"{local[0]}***@{domain}" if local else email
        return f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}@{domain}"

    @staticmethod
    def _build_missing_data_response(missing_fields: list[str]) -> str:
        labels = {
            "order_id": "ID de pedido (EM-XXXX)",
            "product_id": "ID de producto (ECO-XXXX)",
            "estado_producto": "estado del producto",
            "customer_email": "correo electronico",
        }
        missing_text = ", ".join(labels[field] for field in missing_fields)
        return (
            "Para iniciar la devolucion necesito algunos datos adicionales: "
            f"{missing_text}. Compartelos y continuo con el proceso."
        )

    def _run_rag(self, user_input: str) -> str:
        answer = self.rag_tool.invoke({"query": user_input}).strip()
        if answer and answer != FALLBACK_MESSAGE:
            return answer
        normalized_input = self._normalize_text(user_input)
        if "como funciona" in normalized_input and "ecomarket" in normalized_input:
            return (
                "EcoMarket funciona como una tienda en linea de productos sostenibles. "
                "Desde aqui te puedo ayudar en dos cosas: resolver dudas sobre politicas y "
                "tramitar devoluciones.\n\n"
                "Si quieres solo informacion, preguntame por politicas, plazos o condiciones. "
                "Si quieres iniciar una devolucion, comparteme ID de pedido, ID de producto, "
                "estado del producto y correo para continuar."
            )
        return (
            "Puedo ayudarte con devoluciones, estado de pedidos y politicas de EcoMarket. "
            "Si deseas iniciar una devolucion, comparte pedido, producto, estado y correo."
        )

    def _run_general_response(self, user_input: str) -> str:
        text = user_input.lower()
        if any(greet in text for greet in ["hola", "buenas", "hey", "saludos"]):
            return (
                "Hola, soy el asistente de EcoMarket. "
                "Puedo resolver dudas de politicas y ayudarte a tramitar devoluciones."
            )
        return self._run_rag(user_input)

    def _run_return_flow(self, user_input: str, metadata: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        tools_called: list[str] = []
        order_id = self._extract_order_id(user_input, metadata)
        product_id = self._extract_product_id(user_input, metadata)
        customer_email = self._extract_email(user_input, metadata)
        estado_producto = self._normalize_product_state(user_input, metadata)
        dias_desde_compra = self._extract_days(user_input)
        motivo_devolucion = str(metadata.get("motivo_devolucion") or "").strip() or user_input.strip()

        missing_fields: list[str] = []
        if not order_id:
            missing_fields.append("order_id")
        if not product_id:
            missing_fields.append("product_id")
        if not estado_producto:
            missing_fields.append("estado_producto")
        if not customer_email:
            missing_fields.append("customer_email")
        if missing_fields:
            return self._build_missing_data_response(missing_fields), {
                "status": "missing_data",
                "tools_called": tools_called,
                "missing_fields": missing_fields,
            }

        order_result = tool_consultar_estado_pedido.invoke({"order_id": order_id})
        tools_called.append("consultar_estado_pedido")
        if not order_result.get("success"):
            return (
                f"No pude iniciar la devolucion: {order_result.get('message', 'pedido invalido')}",
                {"status": "order_not_found", "tools_called": tools_called},
            )

        eligibility_result = tool_verificar_elegibilidad_producto.invoke(
            {
                "order_id": order_id,
                "product_id": product_id,
                "estado_producto": estado_producto,
                "motivo_devolucion": motivo_devolucion,
                "dias_desde_compra": dias_desde_compra,
            }
        )
        tools_called.append("verificar_elegibilidad_producto")
        if not eligibility_result.get("eligible"):
            reason = eligibility_result.get("reason", "No cumple las condiciones de devolucion.")
            next_step = eligibility_result.get(
                "next_step",
                "Si lo deseas, te ayudo a escalar el caso con soporte humano.",
            )
            return (
                "No es posible aprobar la devolucion por ahora.\n\n"
                f"Motivo: {reason}\n"
                f"Siguiente paso: {next_step}"
            ), {"status": "rejected", "tools_called": tools_called, "eligible": False}

        label_result = tool_generar_etiqueta_devolucion.invoke(
            {
                "order_id": order_id,
                "product_id": product_id,
                "customer_email": customer_email,
            }
        )
        tools_called.append("generar_etiqueta_devolucion")
        if not label_result.get("success"):
            return (
                "El producto es elegible, pero no pude generar la etiqueta en este intento. "
                f"Detalle: {label_result.get('message', 'error no especificado')}."
            ), {"status": "label_error", "tools_called": tools_called, "eligible": True}

        masked_email = self._mask_email(customer_email)
        response = (
            "Tu devolucion fue aprobada y la etiqueta ya fue generada.\n\n"
            f"Pedido: {label_result['order_id']}\n"
            f"Producto: {label_result['product_id']}\n"
            f"Etiqueta: {label_result['label_id']}\n"
            f"Seguimiento: {label_result['tracking_url']}\n"
            f"Envio de confirmacion: {masked_email}\n\n"
            "Empaca el producto y presenta la etiqueta en el punto logistico autorizado."
        )
        return response, {
            "status": "success",
            "tools_called": tools_called,
            "eligible": True,
            "label_generated": True,
            "order_id": label_result["order_id"],
            "product_id": label_result["product_id"],
        }

    def run(self, user_input: str, metadata: dict[str, Any] | None = None) -> str:
        metadata = metadata or {}
        intent = self._detect_intent(user_input=user_input, metadata=metadata)
        tools_called: list[str] = []
        status = "success"

        try:
            if intent == "rag_query":
                tools_called.append("responder_con_rag")
                response = self._run_rag(user_input)
            elif intent == "return_process":
                response, flow_state = self._run_return_flow(user_input=user_input, metadata=metadata)
                tools_called = flow_state.get("tools_called", tools_called)
                status = flow_state.get("status", status)
            else:
                response = self._run_general_response(user_input)
        except Exception:
            response = (
                "Ocurrio un error inesperado al procesar tu solicitud. "
                "Intentalo nuevamente o contacta a soporte humano."
            )
            status = "error"

        if self.enable_logging:
            log_agent_action(
                {
                    "intent": intent,
                    "status": status,
                    "tools_called": tools_called,
                    "user_input": user_input,
                }
            )
        return response
