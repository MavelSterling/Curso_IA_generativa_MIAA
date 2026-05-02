import streamlit as st
import sys
import os
import time

# Añadir el directorio superior al path para poder importar los módulos de la Fase 2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Fase2")))

try:
    from rag_engine import RAGEngine
    from agent import EcoMarketAgent
except ImportError as e:
    st.error(f"Error al importar módulos de la Fase 2: {e}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Agente de Devoluciones EcoMarket",
    page_icon="🌿",
    layout="wide"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main > div {
        padding-top: 1.2rem;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.2);
    }

    .app-subtitle {
        margin-top: -0.2rem;
        margin-bottom: 1rem;
        opacity: 0.9;
    }

    .stTextArea textarea {
        font-size: 1rem;
    }

    .stSelectbox, .stTextInput, .stTextArea {
        margin-bottom: 0.3rem;
    }

    .response-title {
        margin-top: 0.8rem;
        margin-bottom: 0.4rem;
    }

    .agent-response {
        background-color: rgba(30, 41, 59, 0.22);
        color: rgb(241, 245, 249);
        padding: 16px;
        border-radius: 12px;
        border: 1px solid rgba(76, 175, 80, 0.45);
        border-left: 5px solid #4CAF50;
        line-height: 1.5;
        white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

# Carga del agente con caché
@st.cache_resource
def load_agent():
    try:
        rag_engine = RAGEngine()
        agent = EcoMarketAgent(rag_engine=rag_engine)
        return agent
    except Exception as e:
        st.error(f"Error crítico al cargar el motor RAG: {e}")
        return None

agent = load_agent()

# Inicializar historial en session_state
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/leaf.png", width=80)
    st.title("EcoMarket Support")
    st.markdown("---")
    
    st.subheader("💡 Ejemplos de Prompts")
    examples = [
        "¿Cuál es la política de devolución?",
        "¿Cuántos días tengo para devolver un producto?",
        "Quiero devolver el producto ECO-1001 del pedido EM-1001. Está sin uso y mi correo es cliente@test.com",
        "¿Qué productos no se pueden devolver?"
    ]
    for ex in examples:
        if st.button(ex, key=ex):
            st.session_state.current_input = ex
            st.rerun()

    st.markdown("---")
    st.subheader("🔄 Flujo de Devolución")
    st.info("""
    1. **Consulta:** El usuario pregunta o solicita devolución.
    2. **Validación:** El agente verifica datos y estado del pedido.
    3. **Elegibilidad:** Se comprueba si el producto cumple las reglas.
    4. **Acción:** Se genera la etiqueta de retorno si todo es correcto.
    """)

# Cuerpo principal
st.title("🌿 Agente de Devoluciones EcoMarket")
st.markdown(
    '<p class="app-subtitle">Bienvenido al asistente inteligente de EcoMarket. '
    "Puedo ayudarte con información sobre nuestras políticas o procesar tus devoluciones de forma automática.</p>",
    unsafe_allow_html=True,
)

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    user_input = st.text_area(
        "Escribe tu consulta o solicitud:",
        value=st.session_state.get("current_input", ""),
        placeholder="Ej: ¿Cómo puedo devolver mi pedido?",
        height=150
    )

    interaction_type = st.selectbox(
        "Tipo de interacción:",
        ["Automático", "Consulta informativa", "Solicitud de devolución"],
        help="Automático: El agente decidirá según tu texto. Consulta: Solo información RAG. Solicitud: Inicia proceso de devolución."
    )

    with st.expander("📦 Datos para devolución (Opcional si usas Automático)"):
        c1, c2 = st.columns(2)
        order_id = c1.text_input("ID de Pedido", placeholder="EM-1001")
        product_id = c2.text_input("ID de Producto", placeholder="ECO-1001")
        
        c3, c4 = st.columns(2)
        estado_producto = c3.selectbox("Estado del producto", ["Sin uso / Nuevo", "Abierto", "Usado", "Dañado"])
        customer_email = c4.text_input("Correo electrónico", placeholder="cliente@ejemplo.com")
        
        motivo_devolucion = st.text_area("Motivo de la devolución", placeholder="Ej: No era el tamaño esperado.")

    if st.button("Enviar solicitud", type="primary"):
        if not user_input.strip():
            st.warning("Por favor, escribe algo antes de enviar.")
        elif agent is None:
            st.error("El agente no está disponible. Por favor, revisa la configuración.")
        else:
            with st.spinner("El agente está procesando tu solicitud..."):
                try:
                    metadata = {
                        "interaction_type": interaction_type,
                        "order_id": order_id.strip() if order_id else None,
                        "product_id": product_id.strip() if product_id else None,
                        "estado_producto": estado_producto,
                        "customer_email": customer_email.strip() if customer_email else None,
                        "motivo_devolucion": motivo_devolucion
                    }
                    
                    # Llamada al agente
                    response = agent.run(user_input=user_input, metadata=metadata)
                    
                    # Guardar en historial
                    st.session_state.history.append({
                        "user": user_input,
                        "agent": response,
                        "timestamp": time.strftime("%H:%M:%S")
                    })
                    
                    # Mostrar respuesta
                    st.markdown('<h3 class="response-title">🤖 Respuesta del Agente</h3>', unsafe_allow_html=True)
                    st.markdown(f'<div class="agent-response">{response}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Ocurrió un error al ejecutar el agente: {e}")

with col2:
    st.subheader("📜 Historial Reciente")
    if not st.session_state.history:
        st.write("No hay interacciones aún.")
    else:
        for chat in reversed(st.session_state.history[-5:]):
            with st.chat_message("user"):
                st.write(chat["user"])
            with st.chat_message("assistant"):
                st.write(chat["agent"])
            st.caption(f"Hora: {chat['timestamp']}")
            st.markdown("---")

# Footer
st.markdown("---")
st.caption("EcoMarket - Fase 4: Interfaz Web con Streamlit. Desarrollado para el curso de IA Generativa.")
