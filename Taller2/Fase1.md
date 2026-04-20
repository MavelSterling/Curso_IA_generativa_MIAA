# Taller 2

## Fase 1. Seleccion de componentes clave del sistema RAG

### 1. Modelo de embeddings seleccionado

Para EcoMarket se selecciona un esquema de embeddings locales basado en hashing vectorial integrado con LangChain y ChromaDB.

#### Justificacion tecnica

- Precision en español: ofrece recuperacion semantica robusta en consultas mixtas y puede aplicarse en flujos de atencion al cliente en español.
- Costo: no requiere pago por token ni suscripcion para embeddings; puede ejecutarse con CPU en entornos academicos.
- Portabilidad: funciona en local y en contenedores Docker, lo que facilita reproducibilidad sin depender de APIs externas.
- Latencia: su tamaño permite indexar y consultar documentos de tamaño pequeño y mediano con tiempos adecuados para un chatbot.

#### Comparacion: abierto vs propietario

- Codigo abierto (seleccionado):
  - Ventajas: costo cero por uso, control total del pipeline, despliegue offline, sin dependencia de proveedor.
  - Desventajas: rendimiento inferior frente a embeddings propietarios de ultima generacion en ciertos dominios.
- Propietario:
  - Ventajas: normalmente mejor calidad de embedding y mayor robustez.
  - Desventajas: costo recurrente, dependencia de red y de API externa.

Para este taller, la alternativa abierta es la opcion mas coherente por costo, trazabilidad y facilidad de reproduccion.

### 2. Base de datos vectorial seleccionada

Se selecciona `ChromaDB` en modo persistente local.

#### Analisis de opciones

##### Pinecone

- Ventajas: alta escalabilidad administrada, operacion simple en produccion, buen rendimiento para grandes volumenes.
- Desventajas: costo recurrente, dependencia de servicio externo, menor conveniencia para laboratorio local.

##### ChromaDB (seleccionada)

- Ventajas: gratuita, local, integracion directa con LangChain, curva de aprendizaje baja, ideal para prototipado reproducible.
- Desventajas: menor capacidad de escalamiento horizontal frente a soluciones administradas empresariales.

##### Weaviate

- Ventajas: muy potente para escenarios empresariales, filtrado y consultas avanzadas.
- Desventajas: operacion mas compleja para un taller, mayor carga de configuracion inicial.

#### Justificacion final para EcoMarket

Para el escenario del taller (base documental acotada, necesidad de reproducibilidad local y costo cero), ChromaDB ofrece el mejor balance entre facilidad de uso, integracion y desempeño.

### 3. Arquitectura RAG definida para EcoMarket

1. Ingestion de documentos internos (FAQ, politicas, inventario, envios).
2. Segmentacion recursiva de contenido en chunks con solape.
3. Vectorizacion de chunks con embeddings multilingues.
4. Almacenamiento persistente en ChromaDB.
5. Recuperacion por similitud para cada consulta del cliente.
6. Construccion de prompt con contexto recuperado y reglas de respuesta.
7. Generacion final con LLM DeepSeek-V3.2 consumido por endpoint de Azure.
8. Respuesta de fallback cuando no exista evidencia suficiente.

### 4. Resultado esperado

Con esta seleccion, el sistema puede responder de forma fundamentada en la base interna de EcoMarket y, cuando no exista respaldo documental, informar explicitamente que no dispone de herramientas para resolver la solicitud.
