import os
import sys

import classifier as classifier_mod
import model as llm
import prompt_builder


def normalizar_entrada_usuario(linea: str) -> str:
    """Quita comillas o `tipografía markdown` accidental al pegar ejemplos."""
    s = linea.strip()
    if len(s) >= 2 and s[0] == "`" and s[-1] == "`":
        s = s[1:-1].strip()
    return s


def imprimir_ayuda() -> None:
    print(
        """
No reconocí la consulta. Ejemplos:
  • Pedido:  "¿Estado del pedido EM-1004?"  o solo  EM-1004
  • Devolución en una línea:
      yogurt natural | sin abrir | EM-1001
    o:
      devolución: bolsa ecológica | nueva con ticket | EM-1002
  • Escribe  devolución  (solo) para modo guiado (te preguntamos datos).
  • Comandos:  ayuda  |  salir
""".strip()
    )


def chat_loop(prompt_only: bool) -> None:
    print("=== Mini chat EcoMarket (Fase 3) ===")
    if prompt_only:
        print("Modo solo-prompt: se mostrará el texto enviado al modelo, sin llamada HTTP.")
    else:
        print(
            f"Modelo Ollama: {llm.resolve_ollama_model_once()} ({llm.OLLAMA_URL})"
        )
        print("Los datos salen de data/*.json; el comportamiento lo definen prompt/*.txt\n")

    while True:
        try:
            linea = normalizar_entrada_usuario(input("Tú: "))
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break

        if not linea:
            continue
        if linea.lower() in ("salir", "exit", "quit"):
            print("Hasta luego.")
            break
        if linea.lower() in ("ayuda", "help", "?"):
            imprimir_ayuda()
            continue

        if linea.lower() in ("devolución", "devolucion"):
            if prompt_only:
                print(
                    "(En modo guiado necesitas tres líneas; "
                    "usa formato producto | cond | EM-xxxx)\n"
                )
                imprimir_ayuda()
                continue
            try:
                p = input("  Producto: ").strip()
                c = input("  Condición (ej. sin abrir): ").strip()
                o = input("  Pedido (ej. EM-1001): ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                continue
            user_prompt = prompt_builder.build_prompt_devolucion(p, c, o)
        else:
            tipo, payload = classifier_mod.clasificar_consulta(linea)
            if tipo == "devolucion_incompleta":
                imprimir_ayuda()
                continue
            if tipo == "ayuda":
                imprimir_ayuda()
                continue
            if tipo == "pedido":
                user_prompt = prompt_builder.build_prompt_estado_pedido(str(payload))
            else:
                d_name, d_cond, d_ord = payload
                user_prompt = prompt_builder.build_prompt_devolucion(
                    d_name, d_cond, d_ord
                )

        if prompt_only:
            print("\n--- Prompt para el modelo ---\n")
            print(user_prompt)
            print("\n--- Fin del prompt ---\n")
            continue

        try:
            respuesta = llm.run_model(user_prompt)
        except RuntimeError as e:
            print(f"\n{e}\n")
            continue
        except Exception as e:
            print(
                f"\nNo se pudo conectar con Ollama o hubo un error inesperado: {e}\n"
            )
            continue

        print(f"\nEcoMarket: {respuesta}\n")


def main() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass

    prompt_only = os.environ.get("ECOMARKET_PROMPT_ONLY", "").strip() in (
        "1",
        "true",
        "yes",
    )

    if not prompt_only:
        llm.ensure_ollama_running(llm.OLLAMA_URL)
        try:
            llm.resolve_ollama_model_once()
        except RuntimeError as e:
            print(str(e))
            sys.exit(1)

    chat_loop(prompt_only)


if __name__ == "__main__":
    main()
