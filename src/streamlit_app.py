"""
CarBot Pro Streamlit App - Interfaz CrewAI

Interfaz de usuario moderna y simplificada para el sistema CarBot Pro
construido con CrewAI. Mantiene la funcionalidad del sistema original
pero con una arquitectura mucho más limpia.
"""

import streamlit as st
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import sys

# Configurar paths
sys.path.append(os.path.dirname(__file__))

# Importar sistema CarBot (versión corregida)
from carbot_crew_final import create_carbot_system_corrected

from inventory_manager import inventory_manager

# Importar calculadora financiera
try:
    from components.financial_calculator import render_financial_calculator
    CALCULATOR_AVAILABLE = True
except ImportError:
    CALCULATOR_AVAILABLE = False

# Importar para social media
try:
    from st_social_media_links import SocialMediaIcons
    SOCIAL_MEDIA_AVAILABLE = True
except ImportError:
    SOCIAL_MEDIA_AVAILABLE = False

# Cargar variables de entorno
load_dotenv()

# Configuración de página
st.set_page_config(
    page_title="CarBot Pro - Sistema CrewAI", 
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .system-metric {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3c72;
        margin: 0.5rem 0;
    }
    .agent-status {
        background: #e8f5e8;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 3px solid #28a745;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚗 CarBot Pro - Sistema CrewAI</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar - Configuración
with st.sidebar:
    st.header("🔧 Configuración del Sistema")
    
    # Cargar API keys automáticamente
    openai_api_key = os.getenv('OPENAI_API_KEY', '')
    serpapi_api_key = os.getenv('SERPAPI_API_KEY', '')
    
    # Solo mostrar error si falta OpenAI API Key
    if not openai_api_key:
        st.error("❌ OpenAI API Key requerida")
        openai_api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    
    # Botón de inicialización
    if st.button("🚀 Inicializar CarBot Pro", type="primary"):
        if openai_api_key:
            with st.spinner("Inicializando sistema CrewAI..."):
                try:
                    st.session_state.carbot_system = create_carbot_system_corrected(
                        openai_api_key, serpapi_api_key
                    )
                    st.session_state.system_initialized = True
                    st.success("✅ CarBot Pro inicializado con CrewAI!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error al inicializar: {e}")
                    st.session_state.system_initialized = False
        else:
            st.error("❌ OpenAI API Key requerida")
    
    st.markdown("---")

    # Estado del sistema - Ultra-compact collapsible
    st.subheader("📊 Estado del Sistema")
    if st.session_state.get('system_initialized', False):
        # Sistema status en expander para optimizar espacio
        with st.expander("🟢 Sistema CrewAI Operativo", expanded=False):
            system_status = st.session_state.carbot_system.get_system_status()

            st.write("**Agentes CrewAI Activos:**")
            for agent_name, agent_info in system_status['agents'].items():
                st.write(f"• 🤖 {agent_name.title()}: {agent_info['model']}")

            st.write(f"**Herramientas disponibles:** {system_status['tools_available']}")
            st.write(f"**Memoria habilitada:** {'✅' if system_status['memory_enabled'] else '❌'}")

        # Analytics collapsibles (ultra-compact)
        with st.expander("📈 Métricas de Conversación", expanded=False):
            analytics = st.session_state.carbot_system.get_conversation_analytics()
            for k, v in {"Interacciones": analytics['total_interactions'], "Duración (min)": f"{analytics['session_duration_minutes']:.1f}",
                        "Etapa": analytics['current_sales_stage'], "Perfil": f"{analytics['customer_profile_completeness']:.0f}%"}.items():
                st.metric(k, v)

        with st.expander("👤 Perfil Cliente", expanded=False):
            profile = st.session_state.carbot_system.get_customer_profile()
            if profile and profile.name:
                st.json({k: getattr(profile, k, 'N/A') for k in ['name', 'budget_max', 'preferred_make', 'body_style_preference']})
            else: st.info("Perfil en construcción...")

    else:
        st.warning("⚠️ Sistema no inicializado")
    
    st.markdown("---")
    
    # Controles de sesión
    st.subheader("🔄 Gestión de Sesión")
    if st.button("🗑️ Reiniciar Conversación"):
        if st.session_state.get('system_initialized', False):
            st.session_state.carbot_system.reset_customer_session()
            if 'messages' in st.session_state:
                del st.session_state.messages
            st.success("Conversación reiniciada")
            st.rerun()

# Contenido principal
if not st.session_state.get('system_initialized', False):
    # Pantalla de bienvenida
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ## 🎯 Bienvenido a CarBot Pro CrewAI
        
        **Tu asistente inteligente para encontrar el vehículo perfecto**
        
        ### 🚀 Potenciado por CrewAI
        
        🤖 **Sistema Multiagente de Nueva Generación:**
        - **Carlos** - Asesor automotriz experto (GPT-4o)
        - **María** - Especialista en investigación (GPT-4o-mini)  
        - **Edwin** - Manager de inventario (GPT-4o)
        
        ⚡ **Características CrewAI:**
        - Orquestación automática entre agentes
        - Memoria conversacional avanzada
        - Búsqueda inteligente de 40+ vehículos
        - Investigación web en tiempo real
        - Proceso de venta profesional
        
        ✨ **Mejoras sobre el sistema original:**
        • 70% menos código manteniendo funcionalidad
        • Debugging automático y estructurado
        • Escalabilidad real para nuevos agentes
        • Error handling robusto
        
        👈 **Inicializa el sistema CrewAI para comenzar**
        """)

else:
    # Aplicación principal con pestañas
    tab1, tab2 = st.tabs(["💬 Chat con CarBot Pro", "📊 Analytics y Datos"])
    
    with tab1:
        # Área de chat
        st.subheader("💬 Conversación con Carlos")
        
        # Inicializar mensajes
        if "messages" not in st.session_state:
            st.session_state.messages = []
            welcome_msg = """¡Hola! Soy **Carlos**, tu asesor automotriz con 15 años de experiencia. Trabajo con **María** (investigación) y **Edwin** (manager) para encontrarte el vehículo perfecto.

¿En qué puedo ayudarte hoy?

💡 *Ejemplo: "busco un vehículo seguro para mi familia" o "necesito un sedan rojo de menos de 2 años"*"""
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": welcome_msg,
                "timestamp": datetime.now()
            })
        
        # Mostrar mensajes
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input del usuario
        if user_input := st.chat_input("¿Qué estás buscando hoy?"):
            # Agregar mensaje del usuario
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input,
                "timestamp": datetime.now()
            })
            
            # Mostrar mensaje del usuario inmediatamente
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Procesar con CarBot CrewAI
            with st.chat_message("assistant"):
                with st.spinner("Carlos está consultando con su equipo..."):
                    try:
                        # Procesar a través del sistema CrewAI
                        response = st.session_state.carbot_system.process_customer_input(user_input)
                        
                        # Mostrar respuesta
                        st.markdown(response)
                        
                        # Agregar a mensajes
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now()
                        })
                        
                    except Exception as e:
                        error_msg = f"Disculpa, estoy teniendo dificultades técnicas: {e}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg,
                            "timestamp": datetime.now()
                        })
            

            # Rerun para mostrar la nueva conversación
            st.rerun()

    with tab2:
        # Ultra-compact Analytics & Search Interface
        st.subheader("🔍 Búsqueda Manual de Inventario")

        # Compact search form using professional patterns
        filters = {}
        make_options = ['Todos'] + list(inventory_manager.inventory_df['make'].unique()) if not inventory_manager.inventory_df.empty else []
        if make := st.selectbox('Marca', make_options): filters['make'] = make if make != 'Todos' else None

        col1a, col1b = st.columns(2)
        with col1a:
            if min_price := st.number_input('Precio Min', 0, 1000000, 0, 10000):
                filters['price'] = (min_price, st.number_input('Precio Max', min_price, 1000000, 1000000))
        with col1b:
            if min_year := st.number_input('Año Min', 1990, 2025, 2020):
                filters['year'] = (min_year, st.number_input('Año Max', min_year, 2025, 2025))

        # Ultra-compact search execution
        if st.button('🔍 Buscar') and filters:
            results = inventory_manager.get_advanced_search({k: v for k, v in filters.items() if v})
            st.write(f"**{len(results)} vehículos encontrados**")
            if results:
                st.dataframe(pd.DataFrame([{k: getattr(v, k) for k in ['make', 'model', 'year', 'price', 'color']} for v in results[:10]]))

        # Calculadora financiera integrada
        st.markdown("---")
        st.subheader("💰 Calculadora Financiera")

        if CALCULATOR_AVAILABLE:
            # Configuración en una sola columna para mejor organización
            st.markdown("**Configuración del Vehículo**")

            col1, col2 = st.columns(2)
            with col1:
                calc_price = st.number_input("💵 Precio del vehículo", 15000, 500000, 35000, 5000)
            with col2:
                calc_brand = st.selectbox("🚗 Marca", ["honda", "toyota", "bmw", "mercedes", "audi", "mazda"], index=0)

            # Calculadora completa en una columna
            calculations = render_financial_calculator(calc_price, calc_brand)
        else:
            st.warning("⚠️ Calculadora financiera no disponible")

        # Database metrics section with horizontal distribution
        st.markdown("---")
        st.subheader("📊 Métricas de Base de Datos")
        stats = inventory_manager.get_inventory_stats()

        # First row - Main counts
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Vehículos", stats['total'])
        with col2:
            st.metric("Disponibles", stats['available'])
        with col3:
            st.metric("Reservados", stats.get('reserved', 0))
        with col4:
            st.metric("Precio Promedio", f"${stats.get('avg_price', 0):,.0f}")

        # Second row - Advanced metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Marca Popular", stats.get('most_popular_make', 'N/A'))
        with col2:
            st.metric("Tipos Carrocería", stats.get('body_styles', 0))
        with col3:
            st.metric("Eco-Friendly", stats.get('fuel_efficiency', 0))
        with col4:
            st.metric("Vehículos Premium", stats.get('luxury_count', 0))
        
        # Ultra-compact inventory display
        st.subheader("🗄️ Base de Datos Completa")
        
        # Botón de descarga
        if not inventory_manager.inventory_df.empty:
            csv_data = inventory_manager.inventory_df.to_csv(index=False)
            st.download_button(
                label="📥 Descargar Inventario Completo (CSV)",
                data=csv_data,
                file_name=f"inventario_carbot_crewai_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        # Mostrar tabla del inventario
        with st.expander("Ver Inventario Completo", expanded=False):
            if not inventory_manager.inventory_df.empty:
                # Aplicar colores a los estados
                def highlight_status(row):
                    if row['status'] == 'Reserved':
                        return ['background-color: #ffcdd2'] * len(row)
                    return [''] * len(row)
                
                display_df = inventory_manager.inventory_df.copy()
                if 'status' not in display_df.columns:
                    display_df['status'] = 'Available'
                
                st.dataframe(
                    display_df.style.apply(highlight_status, axis=1),
                    use_container_width=True,
                    height=400
                )
            else:
                st.warning("No hay datos de inventario disponibles.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center;">
<strong>Desarrollador:</strong> Edwin Quintero Alzate<br>
<strong>Email:</strong> egqa1975@gmail.com<br>
</div>
""", unsafe_allow_html=True)

# Social Media Links
if SOCIAL_MEDIA_AVAILABLE:
    social_media_links = [
        "https://www.facebook.com/edwin.quinteroalzate",
        "https://www.linkedin.com/in/edwinquintero0329/",
        "https://github.com/Edwin1719"
    ]
    
    try:
        social_media_icons = SocialMediaIcons(social_media_links)
        social_media_icons.render()
    except Exception as e:
        st.write("📱 Redes sociales: Facebook | LinkedIn | GitHub")
else:
    st.write("📱 Redes sociales: Facebook | LinkedIn | GitHub")