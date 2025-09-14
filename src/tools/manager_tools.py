"""
Herramientas de Delegación CrewAI - Arquitectura Original

Implementa el patrón del sistema original donde Edwin (Manager) y María (Research)
funcionan como herramientas especializadas que Carlos invoca.
"""

from crewai.tools import BaseTool
from typing import Type, Any, List, Dict
from pydantic import BaseModel, Field
import sys
import os
import logging
import re
import requests
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inventory_manager import inventory_manager, Vehicle

# Configurar logging
logger = logging.getLogger(__name__)


# ========================================
# HERRAMIENTA PRINCIPAL: ConsultManager (Edwin)
# ========================================

class ConsultManagerInput(BaseModel):
    """Input para consultar con Edwin (Manager)"""
    request: str = Field(description="Consulta específica para Edwin sobre inventario, precios, disponibilidad, VINs, etc.")


class ConsultManagerTool(BaseTool):
    """
    Herramienta principal para consultar con Edwin (Manager)
    
    Edwin maneja TODO lo relacionado con inventario, precios, disponibilidad,
    VINs y directivas de negocio. Replica el patrón del sistema original.
    """
    name: str = "ConsultManager"
    description: str = """Consulta con Edwin (Manager) para TODO lo relacionado con:
    - Búsqueda de inventario y disponibilidad
    - Detalles específicos de vehículos (VINs, características)
    - Precios, descuentos y autorización de ofertas
    - Directivas de venta y prioridades de negocio
    
    Ejemplos: 'Busca SUV familiares bajo 40000', 'VIN del Toyota Camry 2023', 'autoriza descuento 5% BMW X3'"""
    args_schema: Type[BaseModel] = ConsultManagerInput
    
    def _run(self, request: str) -> str:
        """Edwin procesa la consulta del manager"""
        try:
            logger.info(f"🏢 Edwin recibe consulta: {request}")
            
            # Analizar tipo de consulta
            request_lower = request.lower()
            
            # 1. Búsqueda de inventario (más común)
            if any(keyword in request_lower for keyword in ['busca', 'buscar', 'encuentra', 'mostrar', 'opciones', 'vehículos', 'autos']):
                return self._handle_inventory_search(request)
            
            # 2. Solicitud de VIN específico
            elif 'vin' in request_lower:
                return self._handle_vin_request(request)
            
            # 3. Consultas de precio/descuento
            elif any(keyword in request_lower for keyword in ['precio', 'descuento', 'autoriza', 'oferta', 'costo']):
                return self._handle_pricing_request(request)
            
            # 4. Detalles específicos de vehículo
            elif any(keyword in request_lower for keyword in ['detalles', 'características', 'especificaciones', 'información']):
                return self._handle_vehicle_details(request)
            
            # 5. Consulta general
            else:
                return self._handle_general_consultation(request)
                
        except Exception as e:
            error_msg = f"❌ Edwin: Error procesando consulta: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _handle_inventory_search(self, request: str) -> str:
        """Maneja búsquedas de inventario"""
        try:
            vehicles = inventory_manager.intelligent_search(request, max_results=8)
            
            if not vehicles:
                return f"""🏢 **EDWIN - BÚSQUEDA DE INVENTARIO:**

❌ No encontré vehículos que coincidan con: "{request}"

**💡 Sugerencia de Edwin:**
Podemos ampliar los criterios de búsqueda o revisar opciones similares en nuestro inventario."""
            
            formatted_results = inventory_manager.format_vehicles_for_agent(vehicles, max_display=6)
            stats = inventory_manager.get_inventory_stats()
            
            return f"""🏢 **EDWIN - BÚSQUEDA DE INVENTARIO:**

{formatted_results}

**📊 Estado del Inventario:**
• Total: {stats['total']} | Disponibles: {stats['available']} | Reservados: {stats['reserved']}

**💡 Análisis de Edwin:**
{self._generate_edwin_recommendation(vehicles, request)}"""
            
        except Exception as e:
            return f"❌ Edwin: Error en búsqueda de inventario: {str(e)}"
    
    def _handle_vin_request(self, request: str) -> str:
        """Maneja solicitudes de VIN específicas"""
        try:
            # Extraer modelo del request
            match = re.search(r'(del|de el)\s+([a-zA-Z0-9\s-]+)', request, re.IGNORECASE)
            if not match:
                return "❌ Edwin: No pude identificar el vehículo para buscar el VIN. Por favor, sé más específico."
            
            vehicle_query = match.group(2).strip()
            vehicles = inventory_manager.intelligent_search(vehicle_query, max_results=3)
            
            if not vehicles:
                return f"❌ Edwin: No encontré el vehículo '{vehicle_query}' en nuestro inventario."
            
            vehicle = vehicles[0]  # Tomar el más relevante
            return f"""🏢 **EDWIN - INFORMACIÓN VIN:**

**VIN solicitado:** {vehicle.vin}
**Vehículo:** {vehicle.year} {vehicle.make} {vehicle.model}
**Precio:** ${vehicle.price:,}
**Estado:** {vehicle.status}

**💡 Edwin:** VIN verificado y disponible para proceder con la venta."""
            
        except Exception as e:
            return f"❌ Edwin: Error obteniendo VIN: {str(e)}"
    
    def _handle_pricing_request(self, request: str) -> str:
        """Maneja consultas de precios y descuentos"""
        return f"""🏢 **EDWIN - AUTORIZACIÓN DE PRECIOS:**

**Solicitud recibida:** {request}

**💡 Directrices de Edwin:**
• Descuentos hasta 5% autorizados para compra inmediata
• Financiamiento especial disponible a 0% por 36 meses
• Trade-in valoración premium para clientes serios
• Garantía extendida con descuento del 20%

**Recomendación:** Procede con la negociación dentro de estos parámetros."""
    
    def _handle_vehicle_details(self, request: str) -> str:
        """Maneja solicitudes de detalles específicos"""
        try:
            vehicles = inventory_manager.intelligent_search(request, max_results=1)
            if not vehicles:
                return f"❌ Edwin: No encontré el vehículo específico para dar detalles."
            
            vehicle = vehicles[0]
            return f"""🏢 **EDWIN - DETALLES COMPLETOS:**

**{vehicle.year} {vehicle.make} {vehicle.model}**
• VIN: {vehicle.vin}
• Precio: ${vehicle.price:,}
• Millaje: {vehicle.mileage:,} millas
• Color: {vehicle.color}
• Tipo: {vehicle.body_style}
• Combustible: {vehicle.fuel_type}
• Transmisión: {vehicle.transmission}
• Estado: {vehicle.status}

**💡 Edwin:** Vehículo verificado y listo para presentación al cliente."""
            
        except Exception as e:
            return f"❌ Edwin: Error obteniendo detalles: {str(e)}"
    
    def _handle_general_consultation(self, request: str) -> str:
        """Maneja consultas generales"""
        return f"""🏢 **EDWIN - CONSULTA GENERAL:**

**Consulta:** {request}

**💡 Respuesta de Edwin:**
Como manager de la concesionaria, estoy aquí para apoyarte en todo lo relacionado con inventario, precios y directivas de venta. 

Para consultas específicas, puedes preguntarme sobre:
- Búsquedas de inventario
- VINs específicos
- Autorizaciones de descuentos
- Detalles técnicos de vehículos

¿Hay algo específico en lo que pueda ayudarte?"""
    
    def _generate_edwin_recommendation(self, vehicles: List[Vehicle], query: str) -> str:
        """Genera recomendación específica de Edwin"""
        if not vehicles:
            return "No hay recomendaciones disponibles."
        
        top_vehicle = vehicles[0]
        recommendations = []
        
        # Análisis de precio
        if top_vehicle.price < 25000:
            recommendations.append("Excelente valor por dinero")
        elif top_vehicle.price > 50000:
            recommendations.append("Segmento premium con máxima calidad")
        
        # Análisis de antigüedad
        current_year = datetime.now().year
        if top_vehicle.year >= current_year - 1:
            recommendations.append("Modelo prácticamente nuevo")
        elif top_vehicle.year >= current_year - 3:
            recommendations.append("Excelente relación precio-valor")
        
        # Análisis de inventario
        if len(vehicles) >= 3:
            recommendations.append(f"Buena selección disponible ({len(vehicles)} opciones)")
        
        recommendation = "Este vehículo destaca por: " + ", ".join(recommendations) if recommendations else "Opción sólida para considerar"
        return f"{recommendation}. Recomiendo presentar al cliente para evaluación."


# ========================================
# HERRAMIENTA: ResearchVehicleInfo (María)
# ========================================

class ResearchVehicleInput(BaseModel):
    """Input para investigación con María"""
    query: str = Field(description="Consulta de investigación sobre vehículos, marcas, comparativas, etc.")


class ResearchVehicleInfoTool(BaseTool):
    """
    Herramienta para consultar con María (Research Specialist + Technical Expert)

    María se especializa en investigación externa de mercado, reseñas,
    comparativas y análisis técnico NO disponible en nuestro inventario.
    """
    name: str = "ResearchVehicleInfo"
    description: str = """Consulta con María para investigación EXTERNA del mercado:
    - Reseñas y ratings de modelos específicos
    - Comparativas con competidores
    - Datos de seguridad y confiabilidad
    - Tendencias del mercado automotriz
    - NUEVO: Análisis técnico especializado (comparativas entre marcas)
    - NUEVO: Expertise en confiabilidad, consumo, rendimiento
    - NUEVO: Recomendaciones técnicas profesionales

    NO usar para inventario propio (usa ConsultManager). Solo para información externa."""
    args_schema: Type[BaseModel] = ResearchVehicleInput
    
    def _run(self, query: str) -> str:
        """María procesa la consulta de investigación"""
        try:
            logger.info(f"🔬 María recibe consulta de investigación: {query}")
            
            # Simular investigación de María (en el original usaba SerpAPI)
            analysis = self._analyze_research_query(query)
            
            return f"""🔬 **MARÍA - INVESTIGACIÓN DE MERCADO + ANÁLISIS TÉCNICO:**

**Consulta:** {query}

**📊 Análisis de María:**
{analysis}

**💡 Recomendación de María:**
{self._generate_maria_recommendation(query)}

**📅 Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
            
        except Exception as e:
            error_msg = f"❌ María: Error en investigación: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _analyze_research_query(self, query: str) -> str:
        """Analiza la consulta y proporciona investigación simulada"""
        query_lower = query.lower()
        
        # Análisis de seguridad
        if any(keyword in query_lower for keyword in ['seguridad', 'safety', 'iihs', 'nhtsa']):
            return """**Análisis de Seguridad:**
• Ratings IIHS y NHTSA disponibles para la mayoría de modelos 2020+
• Toyota y Honda lideran en confiabilidad general
• Volvo y Mercedes destacan en tecnología de seguridad activa
• Los SUV modernos tienen mejor puntuación que sedanes en rollover"""
        
        # Análisis de confiabilidad
        elif any(keyword in query_lower for keyword in ['confiabilidad', 'reliability', 'problemas', 'issues']):
            return """**Análisis de Confiabilidad:**
• Toyota, Honda y Mazda encabezan rankings de confiabilidad
• Marcas alemanas requieren más mantenimiento pero mejor ingeniería
• Modelos híbridos muestran excelente durabilidad a largo plazo
• Evitar primeros años de redesigns completos"""
        
        # Comparativas técnicas especializadas (NUEVO)
        elif any(keyword in query_lower for keyword in ['comparar', 'vs', 'mejor', 'técnica', 'bmw', 'honda', 'toyota', 'audi', 'rendimiento', 'consumo']):
            return self._technical_comparison_analysis(query_lower)

        # Comparativas de mercado generales
        elif any(keyword in query_lower for keyword in ['competencia', 'mercado']):
            return """**Comparativa de Mercado:**
• El segmento está muy competitivo con opciones sólidas
• Factores clave: precio, características, confiabilidad, reventa
• Considerar tiempo en mercado y disponibilidad de partes
• Verificar incentivos actuales del fabricante"""
        
        # Análisis general
        else:
            return """**Investigación General:**
• Mercado automotriz en transición hacia electrificación
• Valores de reventa favorables para marcas establecidas
• Importancia creciente de tecnología y conectividad
• Tendencia hacia vehículos más grandes y utilitarios"""
    
    def _technical_comparison_analysis(self, query: str) -> str:
        """NUEVO: Análisis técnico especializado de María"""
        # Detectar marcas en la consulta
        brands = []
        if 'bmw' in query: brands.append('BMW')
        if 'honda' in query: brands.append('Honda')
        if 'toyota' in query: brands.append('Toyota')
        if 'audi' in query: brands.append('Audi')
        if 'mercedes' in query: brands.append('Mercedes')
        if 'mazda' in query: brands.append('Mazda')

        if len(brands) >= 2:
            brand1, brand2 = brands[:2]
            return f"""**ANÁLISIS TÉCNICO ESPECIALIZADO - {brand1} vs {brand2}:**

**CONFIABILIDAD:**
• {brand1}: {self._get_reliability_data(brand1)}
• {brand2}: {self._get_reliability_data(brand2)}

**CONSUMO/EFICIENCIA:**
• {brand1}: {self._get_fuel_data(brand1)}
• {brand2}: {self._get_fuel_data(brand2)}

**RENDIMIENTO:**
• {brand1}: {self._get_performance_data(brand1)}
• {brand2}: {self._get_performance_data(brand2)}

**RECOMENDACIÓN TÉCNICA:**
{self._get_technical_recommendation(brand1, brand2)}"""
        else:
            return """**Análisis Técnico General:**
• Para comparativas específicas, menciona las marcas que te interesan
• Puedo analizar confiabilidad, consumo y rendimiento entre marcas
• Especializada en BMW, Honda, Toyota, Audi, Mercedes, Mazda"""

    def _get_reliability_data(self, brand: str) -> str:
        reliability_data = {
            'Toyota': "9.2/10 - Líder mundial en confiabilidad, costos mantenimiento muy bajos",
            'Honda': "8.7/10 - Excelente historial, motores duraderos, CVT reciente problemático",
            'BMW': "6.8/10 - Ingeniería avanzada, costos mantenimiento altos, problemas electrónicos",
            'Audi': "6.5/10 - Tecnología quattro excelente, depreciación rápida, reparaciones costosas",
            'Mercedes': "6.2/10 - Lujo premium, mantenimiento muy caro, complejidad electrónica",
            'Mazda': "8.1/10 - Skyactiv confiable, buen balance precio-calidad, menos espacio"
        }
        return reliability_data.get(brand, "Datos no disponibles")

    def _get_fuel_data(self, brand: str) -> str:
        fuel_data = {
            'Toyota': "Excelente - Líder en híbridos, Prius 4-5L/100km, tecnología probada",
            'Honda': "Excelente - CR-V Hybrid 6L/100km, motores eficientes, buena aerodinámica",
            'BMW': "Buena - Serie 3 7-9L/100km, TwinPower Turbo eficiente, peso afecta consumo",
            'Audi': "Promedio-Baja - Quattro penaliza eficiencia, TDI excelentes, TSI variables",
            'Mercedes': "Promedio - Motores refinados, peso alto, híbridos recientes prometedores",
            'Mazda': "Muy buena - Skyactiv-G 6-7L/100km, compresión alta, diseño aerodinámico"
        }
        return fuel_data.get(brand, "Datos no disponibles")

    def _get_performance_data(self, brand: str) -> str:
        performance_data = {
            'Toyota': "Conservador - Prioriza confiabilidad sobre performance, híbridos adecuados",
            'Honda': "Equilibrado - VTEC clásico, CR-V potente, manejo predecible y seguro",
            'BMW': "Superior - Ultimate driving machine, manejo deportivo, motores potentes",
            'Audi': "Excelente - Quattro tracción, turbos refinados, manejo deportivo-luxury",
            'Mercedes': "Lujo-Performance - AMG excepcional, confort prioritario, tecnología avanzada",
            'Mazda': "Deportivo - Soul of motion, chasis dinámico, motores responsivos"
        }
        return performance_data.get(brand, "Datos no disponibles")

    def _get_technical_recommendation(self, brand1: str, brand2: str) -> str:
        recommendations = {
            ('BMW', 'Honda'): "Honda para confiabilidad y economía familiar. BMW para experiencia de manejo premium.",
            ('Toyota', 'Audi'): "Toyota para máxima confiabilidad y economía operativa. Audi para tecnología y prestige.",
            ('Mercedes', 'Mazda'): "Mazda para mejor relación precio-valor. Mercedes para lujo absoluto.",
        }
        key = tuple(sorted([brand1, brand2]))
        return recommendations.get(key, f"Ambas marcas tienen fortalezas únicas. {brand1} vs {brand2} depende de prioridades específicas.")

    def _generate_maria_recommendation(self, query: str) -> str:
        """Genera recomendación específica de María (mantenida + mejorada)"""
        if any(keyword in query.lower() for keyword in ['comparar', 'vs', 'mejor', 'técnica']):
            return """Como especialista técnica, recomiendo considerar no solo el precio sino también costos de propiedad a largo plazo. La confiabilidad y eficiencia son factores clave para uso familiar."""
        else:
            return """Basado en datos de mercado actuales, recomiendo enfocarse en los beneficios únicos de nuestros vehículos versus la competencia. Puedo proporcionar análisis más específicos según las necesidades del cliente."""


# ========================================
# HERRAMIENTAS DE SOPORTE
# ========================================

class UpdateSalesStageInput(BaseModel):
    """Input para actualizar etapa de venta"""
    new_stage: str = Field(description="Nueva etapa: greeting, discovery, presentation, objection_handling, negotiation, closing, follow_up")
    notes: str = Field(default="", description="Notas sobre el cambio de etapa")


class UpdateSalesStageToolCorrected(BaseTool):
    """Actualiza la etapa de venta actual"""
    name: str = "UpdateSalesStage"
    description: str = "Actualiza la etapa actual del proceso de venta y registra progreso"
    args_schema: Type[BaseModel] = UpdateSalesStageInput
    
    def _run(self, new_stage: str, notes: str = "") -> str:
        """Actualiza la etapa de venta"""
        try:
            logger.info(f"📈 Actualizando etapa de venta a: {new_stage}")
            
            stage_descriptions = {
                "greeting": "Saludo inicial y construcción de rapport",
                "discovery": "Descubrimiento de necesidades del cliente", 
                "presentation": "Presentación de vehículos apropiados",
                "objection_handling": "Manejo de objeciones y preocupaciones",
                "negotiation": "Negociación de términos y precio",
                "closing": "Cierre de la venta",
                "follow_up": "Seguimiento post-venta"
            }
            
            description = stage_descriptions.get(new_stage, "Etapa personalizada")
            
            return f"""📈 **ETAPA DE VENTA ACTUALIZADA**

**Nueva Etapa:** {new_stage.title()}
**Descripción:** {description}
**Notas:** {notes}

**✅ Progreso registrado exitosamente**"""
            
        except Exception as e:
            return f"❌ Error actualizando etapa de venta: {str(e)}"