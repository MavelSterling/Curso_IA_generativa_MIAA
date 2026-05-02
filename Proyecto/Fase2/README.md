# Proyecto Final - Fase 2

Implementacion del agente de EcoMarket para consultas informativas y automatizacion del flujo de devoluciones.

## Componentes

- `rag_engine.py`: motor RAG reutilizado desde el Taller 2.
- `return_service.py`: reglas simuladas de negocio para devoluciones.
- `agent_tools.py`: tools del agente (`responder_con_rag`, consulta de pedido, elegibilidad y etiqueta).
- `agent.py`: clase `EcoMarketAgent` con router de intencion y orquestacion de tools.
- `agent_logger.py`: registro JSONL en `logs/agent_actions.jsonl`.
- `app.py`: CLI para probar el agente localmente.
- `smoke_agent_check.py`: prueba rapida de escenarios clave.

## Flujo de devolucion

1. Detectar intencion.
2. Solicitar datos faltantes si aplica.
3. `consultar_estado_pedido`.
4. `verificar_elegibilidad_producto`.
5. Si es elegible, `generar_etiqueta_devolucion`.
6. Responder con mensaje claro para el usuario.

## Ejecucion local

Desde `Proyecto/Fase2`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
python app.py
```

## Pruebas

```bash
python -m pytest tests -q
python smoke_agent_check.py
```

## Prompts sugeridos

- "Hola, quiero saber como funciona EcoMarket."
- "Cual es la politica de devoluciones de EcoMarket?"
- "Quiero devolver un producto que compre hace 10 dias."
- "Compre un producto hace 45 dias, lo puedo devolver?"
- "Genera una etiqueta para devolver mi pedido EM-1001 con producto ECO-1001."
