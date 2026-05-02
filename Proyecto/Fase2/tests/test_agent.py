from agent import EcoMarketAgent
from prompts import FALLBACK_MESSAGE


class FakeRAGEngine:
    def __init__(self, answer_text: str) -> None:
        self.answer_text = answer_text

    def answer(self, question: str) -> str:
        return self.answer_text


def test_agent_rag_query_uses_rag_response() -> None:
    agent = EcoMarketAgent(rag_engine=FakeRAGEngine("Politica resumida"), enable_logging=False)
    response = agent.run(
        user_input="Cual es la politica?",
        metadata={"interaction_type": "Consulta informativa"},
    )
    assert "Politica resumida" in response


def test_agent_return_missing_fields() -> None:
    agent = EcoMarketAgent(rag_engine=FakeRAGEngine(""), enable_logging=False)
    response = agent.run(
        user_input="Quiero devolver un producto",
        metadata={"interaction_type": "Solicitud de devolucion"},
    )
    assert "necesito algunos datos adicionales" in response.lower()


def test_agent_return_success() -> None:
    agent = EcoMarketAgent(rag_engine=FakeRAGEngine(""), enable_logging=False)
    response = agent.run(
        user_input="Quiero devolver ECO-1001 del pedido EM-1001",
        metadata={
            "interaction_type": "Solicitud de devolucion",
            "order_id": "EM-1001",
            "product_id": "ECO-1001",
            "estado_producto": "Sin uso / Nuevo",
            "customer_email": "cliente@test.com",
        },
    )
    assert "devolucion fue aprobada" in response.lower()
    assert "etiqueta:" in response.lower()


def test_agent_return_not_eligible() -> None:
    agent = EcoMarketAgent(rag_engine=FakeRAGEngine(""), enable_logging=False)
    response = agent.run(
        user_input="Compre hace 60 dias y quiero devolver ECO-1001 del pedido EM-1001",
        metadata={
            "interaction_type": "Solicitud de devolucion",
            "order_id": "EM-1001",
            "product_id": "ECO-1001",
            "estado_producto": "Sin uso / Nuevo",
            "customer_email": "cliente@test.com",
        },
    )
    assert "no es posible aprobar la devolucion" in response.lower()


def test_agent_general_fallback_to_help_message() -> None:
    agent = EcoMarketAgent(rag_engine=FakeRAGEngine(FALLBACK_MESSAGE), enable_logging=False)
    response = agent.run(user_input="Solo quiero informacion general de la tienda", metadata={})
    assert "puedo ayudarte" in response.lower()
