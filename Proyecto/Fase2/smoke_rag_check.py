from rag_engine import RAGEngine


def main() -> None:
    engine = RAGEngine(force_reindex=True)
    queries = [
        "Cual es el estado del pedido EM-1004?",
        "Se puede devolver una crema facial abierta y usada?",
        "Tienen stock de camiseta de algodon organico?",
        "Necesito asesoria legal para importar productos desde otro pais.",
    ]

    print("=== Smoke test RAG ===")
    for idx, query in enumerate(queries, start=1):
        answer = engine.answer(query)
        print(f"\n[{idx}] Pregunta: {query}")
        print(f"[{idx}] Respuesta: {answer}")


if __name__ == "__main__":
    main()
