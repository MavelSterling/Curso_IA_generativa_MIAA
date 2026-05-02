from rag_engine import RAGEngine
from agent import EcoMarketAgent


def main() -> None:
    agent = EcoMarketAgent(rag_engine=RAGEngine(force_reindex=False), enable_logging=False)

    cases = [
        {
            "title": "Consulta informativa",
            "input": "Cual es la politica de devoluciones de EcoMarket?",
            "metadata": {"interaction_type": "Consulta informativa"},
        },
        {
            "title": "Datos faltantes",
            "input": "Quiero devolver un producto",
            "metadata": {"interaction_type": "Solicitud de devolucion"},
        },
        {
            "title": "Devolucion elegible",
            "input": "Quiero devolver el producto ECO-1001 del pedido EM-1001",
            "metadata": {
                "interaction_type": "Solicitud de devolucion",
                "order_id": "EM-1001",
                "product_id": "ECO-1001",
                "estado_producto": "Sin uso / Nuevo",
                "customer_email": "cliente@test.com",
                "motivo_devolucion": "No era lo que esperaba",
            },
        },
        {
            "title": "Pedido no entregado",
            "input": "Necesito devolver el producto ECO-1003 del pedido EM-1002",
            "metadata": {
                "interaction_type": "Solicitud de devolucion",
                "order_id": "EM-1002",
                "product_id": "ECO-1003",
                "estado_producto": "Sin uso / Nuevo",
                "customer_email": "cliente@test.com",
            },
        },
        {
            "title": "Fuera de plazo",
            "input": "Compre hace 60 dias y quiero devolver ECO-1001 del pedido EM-1001",
            "metadata": {
                "interaction_type": "Solicitud de devolucion",
                "order_id": "EM-1001",
                "product_id": "ECO-1001",
                "estado_producto": "Sin uso / Nuevo",
                "customer_email": "cliente@test.com",
            },
        },
    ]

    print("=== Smoke test agente EcoMarket ===")
    for idx, case in enumerate(cases, start=1):
        print(f"\n[{idx}] {case['title']}")
        print(f"Entrada: {case['input']}")
        response = agent.run(user_input=case["input"], metadata=case["metadata"])
        print(f"Respuesta: {response}")


if __name__ == "__main__":
    main()
