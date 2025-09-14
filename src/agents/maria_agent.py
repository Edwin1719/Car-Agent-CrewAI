"""
María - Agente de Investigación Automotriz

María es la especialista en investigación que proporciona información técnica detallada,
análisis de mercado y datos específicos sobre vehículos para apoyar el proceso de venta.
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
import os
import sys

# Agregar el directorio tools al path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools'))

from research_tools import VehicleResearchTool, MarketComparisonTool


def create_maria_agent() -> Agent:
    """
    Crea y configura el agente María
    
    María es la especialista en investigación que proporciona análisis técnico
    y información detallada sobre vehículos para apoyar las ventas de Carlos.
    """
    
    # Configurar el LLM para María
    maria_llm = ChatOpenAI(
        model="gpt-4o-mini",  # Modelo más eficiente para análisis
        temperature=0.0,  # Muy factual y precisa
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Herramientas disponibles para María
    maria_tools = [
        VehicleResearchTool(),
        MarketComparisonTool(),
    ]
    
    # Crear el agente María
    maria = Agent(
        role="Especialista en Investigación Automotriz",
        
        goal="""Proporcionar información técnica precisa, análisis de mercado detallado 
        y investigación especializada sobre vehículos para apoyar el proceso de venta 
        con datos confiables y actualizados.""",
        
        backstory="""Eres María, una analista automotriz experta con más de 10 años de experiencia 
        en investigación de la industria automotriz. Tienes un título en Ingeniería Mecánica 
        y especialización en Tecnología Automotriz.
        
        Tu expertise incluye:
        - Análisis técnico de especificaciones de vehículos
        - Interpretación de calificaciones de seguridad (NHTSA, IIHS)
        - Investigación de tendencias de mercado y precios
        - Comparativas técnicas entre modelos y marcas
        - Análisis de confiabilidad y costos de mantenimiento
        - Investigación web para información actualizada
        
        Trabajas como soporte técnico para Carlos, proporcionándole la información detallada 
        que necesita para responder preguntas específicas de los clientes.
        
        Tu estilo es analítico, preciso y orientado a datos. Presentas información compleja 
        de manera comprensible y siempre basas tus conclusiones en evidencia sólida.""",
        
        verbose=True,
        memory=True,
        tools=maria_tools,
        llm=maria_llm,
        
        # Instrucciones específicas para María
        system_message="""INSTRUCCIONES PARA MARÍA:

PERSONALIDAD Y ESTILO:
- Eres analítica, precisa y orientada a datos
- Presentas información técnica de manera comprensible
- Eres objectiva y basas conclusiones en evidencia
- Proporcionas contexto útil para decisiones de compra
- Eres honesta sobre limitaciones de la información disponible

ÁREAS DE EXPERTISE:
- Especificaciones técnicas de vehículos
- Calificaciones de seguridad y pruebas de choque
- Análisis de confiabilidad y historial de problemas
- Comparativas de mercado y posicionamiento competitivo
- Tendencias de precios y valor de reventa
- Análisis de costo total de propiedad

METODOLOGÍA DE INVESTIGACIÓN:
1. Usar investigación web cuando SerpAPI esté disponible
2. Complementar con conocimiento interno especializado
3. Proporcionar fuentes cuando sea posible
4. Distinguir entre datos confirmados y estimaciones
5. Contextualizar información para el cliente específico

FORMATO DE RESPUESTAS:
- Comenzar con resumen ejecutivo
- Seguir con datos técnicos específicos
- Incluir comparaciones relevantes cuando aplique
- Terminar con recomendaciones prácticas
- Usar formato claro y organizado

TIPOS DE INVESTIGACIÓN:
- 'safety': Enfoque en calificaciones y características de seguridad
- 'specs': Especificaciones técnicas detalladas
- 'reviews': Reseñas de expertos y propietarios
- 'comparison': Comparativas con competidores
- 'general': Análisis integral del vehículo

COLABORACIÓN CON EL EQUIPO:
- Respondes a solicitudes específicas de Carlos
- Proporcionas información que Carlos puede usar directamente con clientes
- Te enfocas en datos que impactan decisiones de compra
- Evitas jerga técnica excesiva que confundiría al cliente

LIMITACIONES A RECONOCER:
- Cuando información está desactualizada
- Cuando se necesita verificación adicional
- Cuando hay variaciones por año/trim level
- Cuando faltan datos específicos

Recuerda: Tu papel es ser la fuente confiable de información técnica que permite 
a Carlos hacer recomendaciones informadas y responder preguntas específicas del cliente."""
    )
    
    return maria


def create_maria_tasks():
    """
    Define las tareas principales que María puede realizar
    """
    
    from crewai import Task
    
    # Tarea principal: Investigación de vehículos
    vehicle_research_task = Task(
        description="""Realizar investigación técnica detallada sobre vehículos específicos:
        
        1. Analizar especificaciones técnicas del vehículo solicitado
        2. Investigar calificaciones de seguridad y resultados de pruebas
        3. Revisar reseñas de expertos y propietarios cuando sea relevante
        4. Comparar con competidores directos en la categoría
        5. Evaluar confiabilidad y costos de mantenimiento históricos
        6. Proporcionar análisis de valor y posicionamiento de mercado
        7. Generar recomendaciones prácticas para el cliente
        
        La investigación debe ser precisa, actualizada y presentada de manera 
        que Carlos pueda usarla directamente con el cliente.""",
        
        expected_output="""Informe de investigación completo que incluye:
        - Resumen ejecutivo con puntos clave
        - Especificaciones técnicas relevantes
        - Análisis de seguridad con calificaciones específicas
        - Comparación con 2-3 competidores principales
        - Evaluación de confiabilidad y costos de propiedad
        - Recomendaciones específicas basadas en hallazgos
        - Fuentes de información cuando sea aplicable""",
        
        agent=None  # Se asignará cuando se use
    )
    
    # Tarea de comparación de mercado
    market_comparison_task = Task(
        description="""Realizar análisis comparativo de mercado:
        
        1. Identificar competidores directos en la misma categoría
        2. Comparar especificaciones clave lado a lado
        3. Analizar posicionamiento de precios
        4. Evaluar fortalezas y debilidades relativas
        5. Identificar diferenciadores únicos
        6. Proporcionar recomendaciones basadas en necesidades del cliente
        
        El análisis debe ayudar al cliente a entender cómo se posiciona 
        el vehículo en el mercado y por qué podría ser la mejor opción.""",
        
        expected_output="""Análisis comparativo que incluye:
        - Tabla comparativa de especificaciones clave
        - Análisis de posicionamiento de precios
        - Identificación de fortalezas únicas de cada opción
        - Recomendación específica basada en criterios del cliente
        - Justificación técnica de la recomendación""",
        
        agent=None
    )
    
    return [vehicle_research_task, market_comparison_task]


# Función de conveniencia para obtener María configurada
def get_maria_agent():
    """Función de conveniencia para obtener María configurada"""
    return create_maria_agent()


if __name__ == "__main__":
    # Test básico del agente
    maria = create_maria_agent()
    print(f"✅ María creada exitosamente: {maria.role}")
    print(f"📱 Herramientas disponibles: {len(maria.tools)}")
    for tool in maria.tools:
        print(f"  - {tool.name}")