"""
CarBot Pro Crew Corregido - Arquitectura Original

Sistema que replica la funcionalidad del proyecto original LIDR:
- Carlos como único agente activo
- Edwin y María como herramientas especializadas
- Flujo conversacional natural
"""

# Fix para SQLite en Streamlit Cloud
try:
    import pysqlite3
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

from crewai import Crew, Task, Process, Agent
from langchain_openai import ChatOpenAI
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import sys
import logging

# Importar agente corregido y optimizaciones
sys.path.append(os.path.dirname(__file__))
from agents.carlos_agent_final import create_carlos_agent_corrected
from utils.profile_analyzer import ProfileAnalyzer
try:
    from tools.automotive_tools import automotive_tools
except ImportError:
    # Fallback - Miguel trabajará sin herramientas automotive por ahora
    automotive_tools = []
    print("⚠️ Automotive tools no disponibles - Miguel trabajará en modo básico")

# Configurar logging
logger = logging.getLogger(__name__)


class CarBotCrewCorrected:
    """
    Sistema CarBot Pro con arquitectura corregida
    
    Replica la funcionalidad del sistema original donde:
    - Carlos es el único agente activo
    - Edwin (Manager) funciona como herramienta ConsultManager
    - María (Research) funciona como herramienta ResearchVehicleInfo
    """
    
    def __init__(self, openai_api_key: str, serpapi_api_key: Optional[str] = None):
        """Inicializa el sistema corregido"""
        
        # Configurar variables de entorno
        os.environ['OPENAI_API_KEY'] = openai_api_key
        if serpapi_api_key:
            os.environ['SERPAPI_API_KEY'] = serpapi_api_key
        
        # Crear agente principal
        self.carlos = create_carlos_agent_corrected()

        # Configurar crew con arquitectura corregida
        self.crew = self._create_corrected_crew()
        
        # Sistema de tracking
        self.conversation_count = 0
        self.start_time = datetime.now()
        self.sales_stage = "greeting"
        
        # Perfil del cliente (simplificado)
        self.customer_profile = {
            'name': None,
            'budget_range': None,
            'preferences': [],
            'needs': [],
            'interaction_history': []
        }
        
        logger.info("🚗 CarBot Pro (Arquitectura Corregida) inicializado exitosamente")
        logger.info("👥 Agente activo: Carlos | Herramientas: Edwin (Manager), María (Research + Expertise)")
    
    def _create_corrected_crew(self) -> Crew:
        """Crea crew con arquitectura corregida (Carlos como único agente)"""
        
        # Tarea principal que procesa cada mensaje del cliente
        main_task = Task(
            description="""Procesa el mensaje específico del cliente: {customer_input}

Como Carlos, el asesor automotriz experto, debes:

1. **Analizar el mensaje actual del cliente**
2. **Determinar la etapa de venta apropiada** y usar UpdateSalesStage si es necesario
3. **Usar herramientas según necesidad:**
   - ConsultManager para inventario, precios, VINs, disponibilidad
   - ResearchVehicleInfo para información externa Y análisis técnico especializado
4. **Responder específicamente** al cliente con información útil y relevante
5. **Guiar la conversación** hacia el siguiente paso del proceso de venta

**CONTEXTO DE LA CONVERSACIÓN:**
- Etapa actual: {sales_stage}
- Perfil del cliente: {customer_profile}
- Historial: {interaction_history}

**IMPORTANTE:** 
- Responde ESPECÍFICAMENTE al mensaje actual del cliente
- Usa las herramientas proactivamente para obtener información
- Mantén el flujo natural de la conversación de venta
- Nunca repitas mensajes genéricos""",
            
            expected_output="""Una respuesta conversacional natural que:
- Aborde específicamente el mensaje del cliente
- Incluya información relevante del inventario (si aplica)
- Guíe al cliente hacia el siguiente paso
- Mantenga el tono profesional y consultivo
- Demuestre progreso en el proceso de venta""",
            
            agent=self.carlos
        )
        
        # Crear crew con un solo agente (Carlos)
        crew = Crew(
            agents=[self.carlos],
            tasks=[main_task],
            process=Process.sequential,
            verbose=True,
            memory=True,
            max_iterations=1  # Una iteración por mensaje
        )
        
        return crew
    
    def process_customer_input(self, user_input: str) -> str:
        """
        Procesa input del cliente a través del sistema corregido
        
        Replica el flujo del sistema original:
        Cliente → Carlos → (herramientas según necesidad) → Respuesta
        """
        try:
            self.conversation_count += 1
            logger.info(f"👤 CLIENTE (#{self.conversation_count}): {user_input}")
            
            # Actualizar perfil del cliente
            self._update_customer_profile(user_input)
            
            # Construir contexto para Carlos
            context = self._build_conversation_context(user_input)
            
            # Procesar a través del crew
            result = self.crew.kickoff(inputs={
                'customer_input': user_input,
                'sales_stage': context['sales_stage'],
                'customer_profile': context['customer_profile_summary'],
                'interaction_history': context['interaction_history']
            })
            
            # Extraer respuesta
            carlos_response = str(result)
            
            # Registrar en historial
            self._add_to_history(user_input, carlos_response)
            
            logger.info(f"💬 CARLOS: {carlos_response[:100]}...")
            return carlos_response
            
        except Exception as e:
            error_msg = f"❌ Error procesando input: {str(e)}"
            logger.error(error_msg)
            return "Disculpa, estoy teniendo dificultades técnicas. ¿Podrías reformular tu pregunta?"
    
    def _update_customer_profile(self, user_input: str) -> None:
        """
        OPTIMIZACIÓN: Actualiza el perfil del cliente usando ProfileAnalyzer

        Reemplaza ~40 líneas de código duplicado con una llamada centralizada.
        Mantiene exactamente la misma funcionalidad pero más eficiente y testeable.
        """
        # BACKUP del código original (comentado por seguridad)
        # input_lower = user_input.lower()
        # ... [código original de 40+ líneas] ...

        try:
            # NUEVO: Usar ProfileAnalyzer optimizado
            updates = ProfileAnalyzer.analyze_input(user_input)

            # Aplicar actualizaciones evitando duplicados
            self.customer_profile = ProfileAnalyzer.merge_profile_updates(
                self.customer_profile, updates
            )

            if updates:
                logger.debug(f"Perfil actualizado con: {updates}")

        except Exception as e:
            # FALLBACK: Si ProfileAnalyzer falla, no actualizar perfil
            logger.warning(f"Error en ProfileAnalyzer, manteniendo perfil actual: {e}")
            # El perfil queda intacto, no se rompe la funcionalidad
    
    def _build_conversation_context(self, user_input: str) -> Dict[str, Any]:
        """Construye contexto conversacional para Carlos"""
        
        # Perfil resumido
        profile_parts = []
        if self.customer_profile['budget_range']:
            profile_parts.append(f"Presupuesto: {self.customer_profile['budget_range']}")
        if self.customer_profile['preferences']:
            profile_parts.append(f"Preferencias: {', '.join(self.customer_profile['preferences'])}")
        if self.customer_profile['needs']:
            profile_parts.append(f"Necesidades: {', '.join(self.customer_profile['needs'])}")
        
        profile_summary = " | ".join(profile_parts) if profile_parts else "Perfil en construcción"
        
        # Historial reciente
        recent_history = self.customer_profile['interaction_history'][-3:] if self.customer_profile['interaction_history'] else []
        history_text = " → ".join([f"C: {h['customer'][:50]}... / Carlos: {h['carlos'][:50]}..." for h in recent_history])
        
        return {
            'sales_stage': self.sales_stage,
            'customer_profile_summary': profile_summary,
            'interaction_history': history_text or "Primera interacción"
        }
    
    def _add_to_history(self, customer_input: str, carlos_response: str) -> None:
        """Añade interacción al historial"""
        self.customer_profile['interaction_history'].append({
            'timestamp': datetime.now().isoformat(),
            'customer': customer_input,
            'carlos': carlos_response
        })
        
        # Mantener solo las últimas 10 interacciones
        if len(self.customer_profile['interaction_history']) > 10:
            self.customer_profile['interaction_history'] = self.customer_profile['interaction_history'][-10:]
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la conversación"""
        return {
            'conversation_count': self.conversation_count,
            'session_duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
            'sales_stage': self.sales_stage,
            'customer_profile': self.customer_profile
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado del sistema (compatibilidad con interfaz original)"""
        return {
            'status': 'active',
            'agents': {
                'carlos': {'status': 'active', 'role': 'Sales Expert', 'model': 'gpt-4o'},
                'edwin': {'status': 'active', 'role': 'Manager (Tool)', 'model': 'ConsultManager'},
                'maria': {'status': 'active', 'role': 'Research + Expert (Tool)', 'model': 'ResearchVehicleInfo'}
            },
            'conversation_count': self.conversation_count,
            'session_duration': (datetime.now() - self.start_time).total_seconds() / 60,
            'sales_stage': self.sales_stage,
            'tools_available': ['ConsultManager', 'ResearchVehicleInfo', 'UpdateSalesStage'],
            'memory_enabled': True,
            'verbose': True,
            'process': 'sequential'
        }
    
    def get_conversation_analytics(self) -> Dict[str, Any]:
        """Obtiene analíticas de la conversación (compatibilidad con interfaz original)"""
        history = self.customer_profile['interaction_history']
        
        # Calcular estadísticas básicas
        total_interactions = len(history)
        avg_response_length = 0
        if history:
            avg_response_length = sum(len(h['carlos']) for h in history) / total_interactions
        
        # Detectar temas principales
        topics = []
        all_text = " ".join([h['customer'] + " " + h['carlos'] for h in history])
        topic_keywords = {
            'precio': ['precio', 'costo', 'dinero', 'pago', 'financiamiento'],
            'seguridad': ['seguro', 'seguridad', 'familia', 'niños'],
            'rendimiento': ['motor', 'potencia', 'velocidad', 'aceleración'],
            'economía': ['económico', 'gasolina', 'híbrido', 'ahorro'],
            'espacio': ['espacio', 'asientos', 'cajuela', 'tamaño']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in all_text.lower() for keyword in keywords):
                topics.append(topic)
        
        return {
            'total_interactions': total_interactions,
            'session_duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
            'avg_response_length': avg_response_length,
            'sales_stage': self.sales_stage,
            'current_sales_stage': self.sales_stage.title(),
            'customer_interests': topics,
            'tools_used': ['ConsultManager', 'ResearchVehicleInfo', 'UpdateSalesStage'],
            'customer_profile_completeness': self._calculate_profile_completeness()
        }
    
    def _calculate_profile_completeness(self) -> float:
        """Calcula qué tan completo está el perfil del cliente"""
        profile = self.customer_profile
        fields = ['budget_range', 'preferences', 'needs']
        filled_fields = sum(1 for field in fields if profile.get(field))
        return (filled_fields / len(fields)) * 100
    
    def get_customer_profile(self):
        """Obtiene el perfil del cliente (compatibilidad con interfaz original)"""
        # Crear objeto con atributos para compatibilidad con la interfaz
        class CustomerProfileObj:
            def __init__(self, profile_dict):
                self.name = profile_dict.get('name')
                self.budget_max = None
                self.preferred_make = None
                self.body_style_preference = profile_dict.get('preferences', [None])[0] if profile_dict.get('preferences') else None
                self.family_size = None
                self.primary_use = None
                self.needs = profile_dict.get('needs', [])
                self.objections = []
                
                # Extraer budget_max si está en budget_range
                if profile_dict.get('budget_range'):
                    import re
                    match = re.search(r'\$([0-9,]+)', profile_dict['budget_range'])
                    if match:
                        self.budget_max = int(match.group(1).replace(',', ''))
        
        return CustomerProfileObj(self.customer_profile)
    
    def get_customer_notes(self) -> List[Dict[str, Any]]:
        """Obtiene las notas del cliente (compatibilidad con interfaz original)"""
        # Crear objetos de nota para compatibilidad con la interfaz
        notes = []
        for interaction in self.customer_profile.get('interaction_history', []):
            customer_msg = interaction.get('customer', '')
            if len(customer_msg) > 10:
                # Crear objeto de nota compatible
                note = {
                    'category': 'conversación',
                    'content': f"Cliente: {customer_msg[:100]}...",
                    'timestamp': datetime.fromisoformat(interaction.get('timestamp', datetime.now().isoformat()))
                }
                notes.append(note)
        
        if not notes:
            notes.append({
                'category': 'sistema',
                'content': 'No hay notas disponibles',
                'timestamp': datetime.now()
            })
        
        return notes[-5:]


def create_carbot_system_corrected(openai_api_key: str, serpapi_api_key: str = None) -> CarBotCrewCorrected:
    """Función factory para crear el sistema corregido"""
    return CarBotCrewCorrected(openai_api_key, serpapi_api_key)