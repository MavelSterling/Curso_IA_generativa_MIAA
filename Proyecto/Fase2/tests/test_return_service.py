from return_service import (
    consultar_estado_pedido,
    generar_etiqueta_devolucion,
    verificar_elegibilidad_producto,
)


def test_consultar_estado_pedido_ok() -> None:
    result = consultar_estado_pedido("EM-1001")
    assert result["success"] is True
    assert result["status"] == "entregado"


def test_consultar_estado_pedido_not_found() -> None:
    result = consultar_estado_pedido("EM-9999")
    assert result["success"] is False
    assert result["found"] is False


def test_verificar_elegibilidad_true() -> None:
    result = verificar_elegibilidad_producto(
        order_id="EM-1001",
        product_id="ECO-1001",
        estado_producto="sin uso",
        dias_desde_compra=10,
    )
    assert result["success"] is True
    assert result["eligible"] is True


def test_verificar_elegibilidad_false_fuera_de_plazo() -> None:
    result = verificar_elegibilidad_producto(
        order_id="EM-1001",
        product_id="ECO-1001",
        estado_producto="sin uso",
        dias_desde_compra=45,
    )
    assert result["success"] is True
    assert result["eligible"] is False
    assert "30 dias" in result["reason"]


def test_generar_etiqueta_ok() -> None:
    result = generar_etiqueta_devolucion(
        order_id="EM-1001",
        product_id="ECO-1001",
        customer_email="cliente@test.com",
    )
    assert result["success"] is True
    assert result["label_generated"] is True
    assert result["label_id"].startswith("RET-")


def test_generar_etiqueta_invalid_email() -> None:
    result = generar_etiqueta_devolucion(
        order_id="EM-1001",
        product_id="ECO-1001",
        customer_email="correo-invalido",
    )
    assert result["success"] is False
    assert result["label_generated"] is False
