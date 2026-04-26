from rag_engine import RAGEngine, RetrievedChunk
from prompts import FALLBACK_MESSAGE


def test_context_block_empty() -> None:
    context = RAGEngine._build_context_block([])
    assert context == "(sin contexto recuperado)"


def test_extract_sources_unique() -> None:
    chunks = [
        RetrievedChunk(source="faq_clientes.json", score=0.9, content="a"),
        RetrievedChunk(source="faq_clientes.json", score=0.8, content="b"),
        RetrievedChunk(source="catalogo_productos.csv", score=0.7, content="c"),
    ]
    sources = RAGEngine._extract_sources(chunks)
    assert sources == ["faq_clientes.json", "catalogo_productos.csv"]


def test_fallback_message_constant() -> None:
    assert "No cuento con informacion suficiente" in FALLBACK_MESSAGE
