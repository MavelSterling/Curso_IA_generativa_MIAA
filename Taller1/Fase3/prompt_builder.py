from __future__ import annotations

import json

from data_loader import DATA_DIR, PROMPTS_DIR, load_json, load_txt


def build_prompt_estado_pedido(tracking_number: str) -> str:
    pedidos_data = load_json(DATA_DIR / "BD_solicitud_de_pedido.json")
    prompt_template = load_txt(PROMPTS_DIR / "prompt_solicitud_pedido.txt")

    pedidos = pedidos_data["pedidos_ecomarket"]
    pedidos_json_str = json.dumps(pedidos, ensure_ascii=False, indent=2)

    return (
        prompt_template.replace("{{PEDIDOS_ECOMARKET}}", pedidos_json_str)
        .replace("{{tracking_number}}", tracking_number.strip())
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

    return (
        prompt_template.replace(
            "{{POLITICAS_DEVOLUCION_ECOMARKET}}", politicas_json_str
        )
        .replace("{{product_name}}", product_name.strip())
        .replace("{{product_condition}}", product_condition.strip())
        .replace("{{order_number}}", order_number.strip())
    )

