# Taller 2

## Fase 2. Creacion de la base de conocimiento de documentos

### 1. Identificacion de documentos clave para EcoMarket

Se construye una base de conocimiento con cuatro fuentes internas, de las cuales tres cumplen el minimo solicitado:

1. `faq_clientes.json`  
   Preguntas frecuentes y respuestas oficiales de atencion al cliente.
2. `catalogo_productos.csv`  
   Catalogo de productos con atributos comerciales y disponibilidad.
3. `politicas_devolucion.md`  
   Politicas narrativas de devolucion y exclusiones.
4. `estados_pedidos.csv`  
   Estado logistico de pedidos de referencia para consultas operativas.

Estas fuentes cubren los flujos mas frecuentes de soporte: informacion de pedidos, devoluciones y producto.

### 2. Estrategia de segmentacion (chunking)

Se usa segmentacion recursiva con `RecursiveCharacterTextSplitter`:

- `chunk_size`: 700 caracteres
- `chunk_overlap`: 120 caracteres
- separadores: salto doble de linea, salto simple, punto y espacio, espacio

#### Justificacion de la estrategia

- Mejor que tamaño fijo puro: respeta estructura semantica y evita cortes abruptos.
- Mejor que solo por parrafos: mantiene control sobre limite de contexto para embeddings.
- Mejor para este caso de uso: combina coherencia semantica con granularidad adecuada para consultas cortas de clientes.

El solape evita perder informacion en bordes de chunks, especialmente en reglas de politica o descripciones largas.

### 3. Proceso de indexacion

1. Carga de archivos de conocimiento por tipo (JSON, CSV, Markdown).
2. Normalizacion de contenido a documentos textuales con metadata de origen.
3. Segmentacion recursiva en chunks con metadatos heredados.
4. Generacion de embeddings multilingues por chunk.
5. Insercion de vectores en ChromaDB persistente.
6. Consulta por similitud con umbral minimo de relevancia.
7. Envio del contexto recuperado al LLM para generar respuesta final.

### 4. Criterios de calidad de la base de conocimiento

- Trazabilidad: cada chunk conserva fuente y tipo de documento.
- Cobertura: se incluyen documentos para consultas de pedido, devolucion, inventario y FAQ.
- Consistencia: el asistente responde solo con evidencia recuperada.
- Seguridad de respuesta: cuando no hay evidencia suficiente, activa respuesta de no disponibilidad.

### 5. Suposiciones operativas

- La calidad de respuesta depende de la actualizacion de documentos internos.
- El sistema no reemplaza canales humanos para casos fuera de alcance documental.
- Los datos de ejemplo de pedidos e inventario se tratan como base de referencia para el taller.
