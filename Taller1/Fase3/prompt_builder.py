from __future__ import annotations

import json

from data_loader import DATA_DIR, PROMPTS_DIR, load_json, load_txt


def build_prompt_estado_pedido(tracking_number: str) -> str:
    pedidos_data = load_json(DATA_DIR / "BD_solicitud_de_pedido.json")
    prompt_template = load_txt(PROMPTS_DIR / "prompt_solicitud_pedido.txt")

    tn = tracking_number.strip()
    pedidos = pedidos_data["pedidos_ecomarket"]
    coincidencia = next(
        (
            p
            for p in pedidos
            if p.get("numero_seguimiento") == tn or p.get("pedido") == tn
        ),
        None,
    )
    bloque_pedidos = [coincidencia] if coincidencia is not None else pedidos
    pedidos_json_str = json.dumps(bloque_pedidos, ensure_ascii=False, indent=2)

    if coincidencia is not None:
        resultado_busqueda = (
            f"SÍ: el pedido {tn} está registrado en la base de datos de EcoMarket."
        )
        datos_oficiales = (
            f"- Número de seguimiento: {coincidencia.get('numero_seguimiento', tn)}\n"
            f"- Estado: {coincidencia.get('estado', '')}\n"
            f"- Fecha estimada: {coincidencia.get('fecha_estimada', '')}\n"
            f"- Enlace de rastreo: {coincidencia.get('link', '')}"
        )
    else:
        resultado_busqueda = (
            f"NO: no hay ningún pedido con número {tn} en la base de datos."
        )
        datos_oficiales = "(No hay fila de pedido para ese número.)"

    return (
        prompt_template.replace("{{PEDIDOS_ECOMARKET}}", pedidos_json_str)
        .replace("{{tracking_number}}", tn)
        .replace("{{RESULTADO_BUSQUEDA}}", resultado_busqueda)
        .replace("{{DATOS_OFICIALES}}", datos_oficiales)
    )


def build_prompt_devolucion(
    product_name: str, product_condition: str, order_number: str
) -> str:
    politicas_data = load_json(DATA_DIR / "BD_politicas_devolucion.json")
    prompt_template = load_txt(PROMPTS_DIR / "prompt_devolucion.txt")

    politicas_json_str = json.dumps(
        politicas_data["politicas_devolucion_ecomarket"],
        ensure_ascii=False,
        indent=2,
    )

    pedido = order_number.strip()
    pedido_txt = pedido if pedido else "(no indicado)"

    return (
        prompt_template.replace(
            "{{POLITICAS_DEVOLUCION_ECOMARKET}}", politicas_json_str
        )
        .replace("{{product_name}}", product_name.strip())
        .replace("{{product_condition}}", product_condition.strip())
        .replace("{{order_number}}", pedido_txt)
    )

