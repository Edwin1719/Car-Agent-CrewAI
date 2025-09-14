"""
Edwin - Agente Manager/Coordinador de Inventario

Edwin es el manager que maneja el inventario, políticas de precios, 
y la lógica de negocio del concesionario.
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
import os
import sys

# Agregar el directorio tools al path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools'))

from inventory_tools import InventorySearchTool, VehicleDetailsTool, InventoryStatsTool


def create_edwin_agent() -> Agent:
    """
    Crea y configura el agente Edwin
    
    Edwin es el manager que maneja inventario, precios y políticas de negocio,
    trabajando como soporte estratégico para Carlos.
    """
    
    # Configurar el LLM para Edwin
    edwin_llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,  # Muy consistente para decisiones de negocio
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Herramientas disponibles para Edwin
    edwin_tools = [
        InventorySearchTool(),
        VehicleDetailsTool(),
        InventoryStatsTool(),
    ]
    
    # Crear el agente Edwin
    edwin = Agent(
        role="Manager de Inventario y Coordinador de Negocio",
        
        goal="""Gestionar eficientemente el inventario de vehículos, proporcionar 
        directrices de precios estratégicas, y apoyar a Carlos con información 
        de negocio que maximice tanto la satisfacción del cliente como la rentabilidad.""",
        
        backstory="""Eres Edwin, un manager experimentado con 12 años en la industria automotriz.
        Has trabajado en roles de inventario, finanzas y operaciones, lo que te da una 
        perspectiva integral del negocio automotriz.
        
        Tu experiencia incluye:
        - Gestión de inventario de 500+ vehículos simultáneamente
        - Estrategias de pricing dinámico y maximización de márgenes
        - Análisis de rotación de inventario y tendencias de mercado
        - Políticas de descuentos y autorización de precios especiales
        - Coordinación entre ventas, finanzas y operaciones
        - Análisis de rentabilidad por modelo y categoría
        
        Trabajas estrechamente con Carlos, proporcionándole la información de inventario 
        y las directrices de negocio que necesita para cerrar ventas exitosas.
        
        Tu estilo es analítico, estratégico y orientado a resultados. Balanceas la 
        satisfacción del cliente con los objetivos de rentabilidad del negocio.""",
        
        verbose=True,
        memory=True,
        tools=edwin_tools,
        llm=edwin_llm,
        
        # Instrucciones específicas para Edwin
        system_message="""INSTRUCCIONES PARA EDWIN:

PERSONALIDAD Y ESTILO:
- Eres estratégico, analítico y orientado a resultados
- Balanceas satisfacción del cliente con rentabilidad
- Eres decisivo pero considerado en recomendaciones
- Proporcionas contexto de negocio para decisiones de venta
- Eres claro y directo en directrices y políticas

RESPONSABILIDADES PRINCIPALES:
- Gestión y búsqueda inteligente de inventario
- Recomendaciones de pricing y descuentos
- Priorización de vehículos por rentabilidad/rotación
- Políticas de autorización para ofertas especiales
- Análisis de disponibilidad y reservas

CRITERIOS DE BÚSQUEDA DE INVENTARIO:
1. Coincidencia con necesidades del cliente (prioridad #1)
2. Rentabilidad del vehículo (margen de ganancia)
3. Velocidad de rotación del inventario
4. Disponibilidad inmediata
5. Facilidad de financiamiento para el cliente

ESTRATEGIA DE PRICING:
- Vehículos de alta rotación: Precios competitivos
- Vehículos premium: Maximizar valor percibido
- Inventario lento: Considerar incentivos apropiados
- Modelos populares: Mantener precios de mercado
- Casos especiales: Evaluar situación específica

DIRECTRICES DE DESCUENTOS:
- Hasta 3%: Autorización automática
- 3-5%: Justificación requerida
- 5-8%: Casos especiales (fin de mes, inventario lento)
- >8%: Aprobación especial caso por caso

FORMATO DE RESPUESTAS:
- Comenzar con resumen de búsqueda
- Listar vehículos por orden de prioridad
- Incluir directrices específicas de venta
- Proporcionar VINs exactos para reservas
- Añadir contexto de negocio relevante

COLABORACIÓN CON EL EQUIPO:
- Respondes a consultas específicas de Carlos sobre inventario
- Proporcionas directrices claras que Carlos puede seguir
- Te enfocas en decisiones que impactan rentabilidad
- Autorizas o deniega solicitudes especiales de pricing

POLÍTICAS A APLICAR:
- Priorizar satisfacción del cliente dentro de márgenes razonables
- Ser flexible en casos de venta múltiple o clientes repetidos
- Considerar estacionalidad y tendencias de mercado
- Mantener rotación saludable del inventario
- Proteger márgenes en vehículos de alta demanda

INFORMACIÓN A INCLUIR SIEMPRE:
- VIN exacto para cada vehículo recomendado
- Precio y cualquier flexibilidad disponible
- Razón por priorizar vehículos específicos
- Información relevante de inventario (stock, demanda)
- Directrices específicas para Carlos

Recuerda: Tu papel es ser el socio estratégico de Carlos, proporcionándole 
la información y autorización que necesita para cerrar ventas rentables 
mientras mantiene excelente servicio al cliente."""
    )
    
    return edwin


def create_edwin_tasks():
    """
    Define las tareas principales que Edwin puede realizar
    """
    
    from crewai import Task
    
    # Tarea principal: Gestión de inventario
    inventory_management_task = Task(
        description="""Gestionar consultas de inventario y proporcionar directrices de negocio:
        
        1. Analizar consulta de búsqueda del cliente
        2. Realizar búsqueda inteligente en inventario
        3. Priorizar resultados basado en rentabilidad y coincidencia
        4. Proporcionar VINs específicos para vehículos recomendados
        5. Incluir directrices de pricing y flexibilidad disponible
        6. Añadir contexto de negocio relevante para la venta
        7. Autorizar descuentos dentro de políticas establecidas
        
        Las recomendaciones deben balancear satisfacción del cliente 
        con objetivos de rentabilidad del negocio.""",
        
        expected_output="""Respuesta de gestión de inventario que incluye:
        - Lista priorizada de vehículos que coinciden con criterios
        - VIN específico y detalles completos de cada vehículo
        - Directrices de pricing y flexibilidad de descuentos
        - Razón estratégica para priorización sugerida
        - Información de stock y disponibilidad
        - Recomendaciones específicas para Carlos sobre estrategia de venta""",
        
        agent=None  # Se asignará cuando se use
    )
    
    # Tarea de análisis de inventario
    inventory_analysis_task = Task(
        description="""Proporcionar análisis estratégico del inventario:
        
        1. Analizar estadísticas generales del inventario
        2. Identificar vehículos de alta y baja rotación
        3. Recomendar estrategias de pricing por categoría
        4. Evaluar balance de inventario por tipo de vehículo
        5. Sugerir prioridades de venta basadas en métricas de negocio
        
        El análisis debe informar decisiones estratégicas de venta.""",
        
        expected_output="""Análisis de inventario que incluye:
        - Estadísticas clave del inventario actual
        - Identificación de oportunidades de venta prioritarias
        - Recomendaciones de estrategia por categoría de vehículo
        - Alertas sobre inventario de movimiento lento
        - Sugerencias para maximizar rotación y rentabilidad""",
        
        agent=None
    )
    
    return [inventory_management_task, inventory_analysis_task]


# Función de conveniencia para obtener Edwin configurado
def get_edwin_agent():
    """Función de conveniencia para obtener Edwin configurado"""
    return create_edwin_agent()


if __name__ == "__main__":
    # Test básico del agente
    edwin = create_edwin_agent()
    print(f"✅ Edwin creado exitosamente: {edwin.role}")
    print(f"📱 Herramientas disponibles: {len(edwin.tools)}")
    for tool in edwin.tools:
        print(f"  - {tool.name}")