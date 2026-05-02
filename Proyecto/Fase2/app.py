import sys

import model as llm
from agent import EcoMarketAgent
from rag_engine import RAGEngine


def print_help() -> None:
    print(
        """
Ejemplos de consultas:
  - Estado de mi pedido EM-1004
  - Quiero devolver una botella reutilizable sin usar
  - Cual es el stock de la camiseta de algodon organico
  - Cuales son los tiempos de entrega para Medellin

Comandos:
  - ayuda
  - reindexar
  - salir
""".strip()
    )


def chat_loop() -> None:
    print("=== EcoMarket Agent - Atencion al cliente ===")
    print(f"Modelo: {llm.resolve_model_once()} (servido por endpoint Azure)")
    print("Base vectorial: ChromaDB local + flujo de devoluciones")
    print("Escribe 'ayuda' para ver ejemplos o 'salir' para terminar.\n")

    rag = RAGEngine()
    agent = EcoMarketAgent(rag_engine=rag)

    while True:
        try:
            user_input = input("Tu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSesion finalizada.")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in {"salir", "exit", "quit"}:
            print("Sesion finalizada.")
            break
        if cmd in {"ayuda", "help", "?"}:
            print_help()
            continue
        if cmd == "reindexar":
            rag = RAGEngine(force_reindex=True)
            agent = EcoMarketAgent(rag_engine=rag)
            print("Indice reconstruido correctamente.")
            continue

        try:
            response = agent.run(
                user_input=user_input,
                metadata={"interaction_type": "Automatico"},
            )
        except RuntimeError as err:
            print(f"\nError: {err}\n")
            continue
        except Exception as err:
            print(f"\nError inesperado: {err}\n")
            continue

        print(f"\nEcoMarket: {response}\n")


def main() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass

    llm.resolve_model_once()
    chat_loop()


if __name__ == "__main__":
    main()
