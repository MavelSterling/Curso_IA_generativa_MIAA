# Fase 1. Diseño de la Arquitectura del Agente

## 1. Objetivo de la fase

El objetivo de esta fase es diseñar la arquitectura de un  **Agente de IA para EcoMarket** , extendiendo la solución RAG construida en el Taller 2. El nuevo agente permitirá automatizar el proceso de devolución de productos, incluyendo la verificación de elegibilidad y la generación de una etiqueta de devolución.

La arquitectura propuesta busca que el asistente no solo responda preguntas sobre políticas de devolución, sino que también pueda ejecutar acciones controladas mediante herramientas simuladas.

---

## 2. Contexto de la solución base

En el Taller 2 se construyó un sistema RAG para EcoMarket con las siguientes capacidades:

* Ingesta de conocimiento interno.
* Segmentación y vectorización de documentos.
* Recuperación por similitud.
* Generación de respuestas con contexto recuperado.
* Fallback controlado cuando no existe evidencia suficiente.

Para el proyecto final, este sistema RAG se mantiene como base y se incorpora dentro del agente como una herramienta especializada para responder consultas informativas sobre políticas, condiciones, productos, pedidos y preguntas frecuentes.

---

## 3. Arquitectura propuesta

La arquitectura propuesta combina un flujo RAG con un agente de IA que puede decidir cuándo responder con conocimiento documental y cuándo ejecutar herramientas de negocio.

```text
Usuario
  │
  ▼
Interfaz Web Streamlit
  │
  ▼
Agente de IA EcoMarket
  │
  ├── Router de intención
  │       ├── Consulta informativa
  │       │       └── Tool RAG: responder_con_rag
  │       │
  │       └── Solicitud de devolución
  │               ├── Tool 1: consultar_estado_pedido
  │               ├── Tool 2: verificar_elegibilidad_producto
  │               └── Tool 3: generar_etiqueta_devolucion
  │
  ▼
Modelo LLM DeepSeek-V3.2
  │
  ▼
Respuesta final al usuario
```

---

## 4. Descripción de los componentes

| Componente             | Descripción                                                                                         |
| ---------------------- | ---------------------------------------------------------------------------------------------------- |
| Usuario                | Persona que interactúa con el asistente para consultar políticas o solicitar una devolución.      |
| Interfaz Web           | Aplicación simple construida en Streamlit donde el usuario escribe su solicitud.                    |
| Agente de IA EcoMarket | Componente principal que interpreta la intención del usuario y decide qué herramienta usar.        |
| Router de intención   | Lógica que clasifica la solicitud como consulta informativa o proceso de devolución.               |
| Tool RAG               | Componente que reutiliza el sistema RAG del Taller 2 para responder preguntas basadas en documentos. |
| Tools de devolución   | Funciones simuladas que permiten consultar pedidos, validar elegibilidad y generar etiquetas.        |
| Modelo LLM             | Modelo usado para interpretar instrucciones y generar respuestas en lenguaje natural.                |
| Respuesta final        | Mensaje claro para el usuario, con el resultado de la consulta o del proceso de devolución.         |

---

## 5. Extensión de la arquitectura RAG

La arquitectura RAG del Taller 2 se incorpora como una herramienta del agente llamada `responder_con_rag`.

Esta herramienta se usa cuando el usuario realiza preguntas como:

```text
¿Cuál es la política de devolución?
¿Cuántos días tengo para devolver un producto?
¿Qué productos no se pueden devolver?
¿Cuánto tarda el reembolso?
```

En estos casos, el agente no ejecuta acciones de devolución. En su lugar, consulta la base de conocimiento y genera una respuesta basada en la información recuperada.

Esto permite conservar la funcionalidad del Taller 2 y extenderla con capacidades agenticas sin modificar innecesariamente el motor RAG existente.

---

## 6. Definición de herramientas del agente

Para cumplir con la fase, se definen tres herramientas nuevas para el agente, sin contar la funcionalidad RAG.

---

## 6.1 Tool: `consultar_estado_pedido`

### Propósito

Consultar si el pedido existe y validar su estado actual antes de iniciar una devolución.

### Entrada esperada

```json
{
  "order_id": "ECO-1001"
}
```

### Salida esperada

```json
{
  "success": true,
  "found": true,
  "order_id": "ECO-1001",
  "status": "entregado",
  "delivery_date": "2026-04-10",
  "products": ["PROD-001", "PROD-002"]
}
```

### Posibles errores

```json
{
  "success": false,
  "found": false,
  "message": "No se encontró un pedido con ese identificador."
}
```

### Justificación

Antes de validar una devolución, el agente debe confirmar que el pedido exista y que ya haya sido entregado. Si el pedido no existe o aún está en tránsito, el proceso se detiene.

---

## 6.2 Tool: `verificar_elegibilidad_producto`

### Propósito

Determinar si un producto cumple las condiciones para ser devuelto.

### Entrada esperada

```json
{
  "order_id": "ECO-1001",
  "product_id": "PROD-001",
  "estado_producto": "sin uso",
  "motivo_devolucion": "No era el producto esperado"
}
```

### Salida esperada cuando el producto es elegible

```json
{
  "success": true,
  "eligible": true,
  "reason": "El producto cumple las condiciones de devolución.",
  "next_step": "Generar etiqueta de devolución."
}
```

### Salida esperada cuando el producto no es elegible

```json
{
  "success": true,
  "eligible": false,
  "reason": "El producto supera el plazo máximo de 30 días para devolución.",
  "next_step": "Escalar el caso a soporte humano."
}
```

### Reglas de elegibilidad

```text
- El pedido debe existir.
- El pedido debe estar en estado entregado.
- El producto debe pertenecer al pedido.
- El producto debe estar dentro del plazo permitido para devolución.
- El producto debe encontrarse en buen estado, nuevo o sin uso.
```

### Justificación

Esta herramienta es clave porque evita que el agente apruebe devoluciones inválidas. La decisión de elegibilidad se controla mediante reglas explícitas y no únicamente por generación del modelo.

---

## 6.3 Tool: `generar_etiqueta_devolucion`

### Propósito

Generar una etiqueta simulada de devolución cuando el producto cumple las condiciones establecidas.

### Entrada esperada

```json
{
  "order_id": "ECO-1001",
  "product_id": "PROD-001",
  "customer_email": "cliente@correo.com"
}
```

### Salida esperada

```json
{
  "success": true,
  "label_id": "RET-A1B2C3D4",
  "order_id": "ECO-1001",
  "product_id": "PROD-001",
  "tracking_url": "https://ecomarket.example.com/devoluciones/RET-A1B2C3D4",
  "message": "Etiqueta de devolución generada exitosamente."
}
```

### Restricción

Esta herramienta solo debe ejecutarse si previamente la herramienta `verificar_elegibilidad_producto` confirma que el producto es elegible.

### Justificación

La generación de etiqueta representa la acción final del agente. Por eso debe estar condicionada por validaciones previas para evitar acciones incorrectas.

---

## 6.4 Tool RAG: `responder_con_rag`

### Propósito

Responder preguntas informativas usando la base de conocimiento construida en el Taller 2.

### Entrada esperada

```json
{
  "query": "¿Cuál es la política de devolución de EcoMarket?"
}
```

### Salida esperada

```json
{
  "success": true,
  "answer": "Según la política de EcoMarket, los productos pueden devolverse..."
}
```

### Casos de uso

```text
- Preguntas sobre políticas de devolución.
- Preguntas sobre tiempos de reembolso.
- Preguntas sobre productos que aplican o no aplican para devolución.
- Preguntas frecuentes de atención al cliente.
```

### Justificación

Esta herramienta permite reutilizar la solución RAG existente y separar las consultas informativas de las acciones operativas del agente.

---

## 7. Selección del marco de agentes

El marco seleccionado para la implementación del agente es **LangChain** .

### Justificación

Se selecciona LangChain porque permite:

* Crear agentes capaces de usar herramientas.
* Registrar funciones como tools.
* Integrar fácilmente el RAG existente como una herramienta.
* Manejar flujos de decisión entre consulta informativa y acción.
* Conectar el modelo LLM con funciones externas.
* Mantener una estructura modular y fácil de probar.

Además, LangChain es adecuado para este proyecto porque el objetivo principal no es únicamente consultar documentos, sino permitir que el modelo decida cuándo debe responder y cuándo debe ejecutar funciones simuladas.

---

## 8. Flujo de trabajo del agente

```text
Inicio
  │
  ▼
Usuario ingresa una solicitud
  │
  ▼
Agente clasifica la intención
  │
  ├── Consulta informativa
  │       │
  │       ▼
  │   Ejecutar responder_con_rag
  │       │
  │       ▼
  │   Responder con base en documentos
  │
  └── Solicitud de devolución
          │
          ▼
      Validar datos requeridos:
      order_id, product_id, estado_producto, customer_email
          │
          ├── Datos incompletos
          │       ▼
          │   Solicitar información faltante
          │
          └── Datos completos
                  │
                  ▼
          Ejecutar consultar_estado_pedido
                  │
                  ▼
          ¿Pedido existe y fue entregado?
                  │
                  ├── No
                  │     ▼
                  │   Informar motivo y detener proceso
                  │
                  └── Sí
                        │
                        ▼
              Ejecutar verificar_elegibilidad_producto
                        │
                        ▼
              ¿Producto elegible?
                        │
                        ├── No
                        │     ▼
                        │   Explicar motivo y sugerir siguiente paso
                        │
                        └── Sí
                              │
                              ▼
                    Ejecutar generar_etiqueta_devolucion
                              │
                              ▼
                    Entregar etiqueta e instrucciones al usuario
```

---

## 9. Ejemplos de funcionamiento esperado

### Ejemplo 1: Consulta informativa

**Usuario:**

```text
¿Cuántos días tengo para devolver un producto?
```

**Acción esperada del agente:**

```text
Usar responder_con_rag.
```

**Respuesta esperada:**

```text
Según la política de EcoMarket, puedes solicitar la devolución de un producto dentro del plazo establecido en la política de devoluciones. Si deseas iniciar una devolución, indícame el número de pedido y el código del producto.
```

---

### Ejemplo 2: Solicitud de devolución con datos incompletos

**Usuario:**

```text
Quiero devolver un producto.
```

**Acción esperada del agente:**

```text
Solicitar datos faltantes.
```

**Respuesta esperada:**

```text
Para ayudarte con la devolución necesito que me compartas el número de pedido, el código del producto, el estado actual del producto y tu correo electrónico.
```

---

### Ejemplo 3: Solicitud de devolución exitosa

**Usuario:**

```text
Quiero devolver el producto PROD-001 del pedido ECO-1001. El producto está sin uso y mi correo es cliente@correo.com.
```

**Acción esperada del agente:**

```text
1. consultar_estado_pedido
2. verificar_elegibilidad_producto
3. generar_etiqueta_devolucion
```

**Respuesta esperada:**

```text
Tu devolución fue aprobada.

Número de pedido: ECO-1001
Producto: PROD-001
Etiqueta de devolución: RET-A1B2C3D4
Enlace de seguimiento: https://ecomarket.example.com/devoluciones/RET-A1B2C3D4

Por favor empaca el producto en buen estado y presenta esta etiqueta en el punto logístico autorizado.
```

---

### Ejemplo 4: Solicitud no elegible

**Usuario:**

```text
Quiero devolver el producto PROD-003 del pedido ECO-1002.
```

**Acción esperada del agente:**

```text
1. consultar_estado_pedido
2. Detectar que el pedido no está entregado
3. Detener el proceso
```

**Respuesta esperada:**

```text
No es posible iniciar la devolución porque el pedido ECO-1002 aún no ha sido entregado. Solo se pueden devolver productos después de su entrega. Te recomiendo intentarlo nuevamente cuando el estado del pedido sea entregado.
```
