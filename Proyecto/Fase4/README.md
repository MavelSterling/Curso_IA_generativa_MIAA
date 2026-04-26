# Fase 4 - Interfaz Web con Streamlit 🌿

Esta carpeta contiene la interfaz gráfica del **Agente de Devoluciones EcoMarket**, desarrollada con Streamlit. Esta interfaz permite interactuar de forma sencilla con el motor RAG y el agente de acciones implementados en las fases anteriores.

## 🚀 Cómo ejecutar la aplicación

Para ejecutar la aplicación, sigue estos pasos desde la terminal:

1. **Asegúrate de estar en la raíz del repositorio o en esta carpeta.**
2. **Instala las dependencias necesarias** (si aún no lo has hecho):
   ```bash
   pip install streamlit
   ```
   *Nota: También debes tener instaladas las dependencias de la Fase 2 (langchain, chromadb, etc.).*

3. **Ejecuta el comando de Streamlit:**
   ```bash
   streamlit run streamlit_app.py
   ```

## 🐳 Ejecución con Docker

Puedes ejecutar todo el sistema (Fase 2 + Fase 4) usando Docker Compose:

1. **Asegúrate de tener un archivo `.env` en `Proyecto/Fase2/`** con tus credenciales de Azure OpenAI.
2. **Desde esta carpeta (`Proyecto/Fase4`), ejecuta:**
   ```bash
   docker-compose up --build
   ```
3. **Accede a la aplicación** en tu navegador en `http://localhost:8501`.

## 🛠️ Funcionalidades de la Interfaz

- **Consulta Informativa (RAG):** El agente responde preguntas sobre políticas, tiempos y condiciones basándose en los documentos de EcoMarket.
- **Gestión de Devoluciones:** Un formulario dedicado para ingresar `ID de Pedido`, `ID de Producto`, `Estado` y `Correo`.
- **Modo Automático:** El agente utiliza procesamiento de lenguaje natural para decidir si debe responder una duda o iniciar un trámite de devolución.
- **Historial de Sesión:** Permite visualizar las últimas interacciones realizadas durante la ejecución actual.
- **Ejemplos Rápidos:** Botones en la barra lateral para probar el sistema con un solo clic.

## 🧪 Casos de Prueba Recomendados

1. **Consulta RAG:** "¿Cuántos días tengo para devolver un producto?"
2. **Datos Faltantes:** Selecciona "Solicitud de devolución" y presiona enviar sin llenar el formulario.
3. **Devolución Exitosa:** 
   - Pedido: `EM-1001`
   - Producto: `ECO-1001`
   - Estado: `Sin uso / Nuevo`
4. **Devolución Rechazada (En tránsito):**
   - Pedido: `EM-1002` (Este pedido aún no ha sido entregado).
5. **Devolución Rechazada (Estado):**
   - Indica que el producto está `Usado` o `Dañado`.

---
**EcoMarket Agent** - Proyecto Final de IA Generativa.
