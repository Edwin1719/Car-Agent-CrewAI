"""
Herramientas de Delegación para CrewAI - Patrón Original

Edwin (Manager) y María (Research) funcionan como herramientas especializadas
que Carlos invoca, replicando la arquitectura del sistema original.
"""

from crewai.tools import BaseTool
from typing import Type, Any, List, Dict
from pydantic import BaseModel, Field
import sys
import os
import logging

# Agregar el directorio src al path para importar nuestros módulos
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inventory_manager import inventory_manager, Vehicle

# Configurar logging
logger = logging.getLogger(__name__)


class InventorySearchInput(BaseModel):
    """Input schema para búsqueda de inventario"""
    query: str = Field(..., description="Consulta de búsqueda en lenguaje natural (ej: 'SUV seguro para familia bajo 35000')")
    max_results: int = Field(default=8, description="Número máximo de resultados a retornar")


class VehicleReservationInput(BaseModel):
    """Input schema para reserva de vehículos"""
    vin: str = Field(..., description="VIN del vehículo a reservar")


class VehicleDetailInput(BaseModel):
    """Input schema para obtener detalles de vehículo"""
    vin: str = Field(..., description="VIN del vehículo del cual obtener detalles")


class InventorySearchTool(BaseTool):
    """
    Herramienta para buscar vehículos en el inventario
    
    Esta herramienta es la principal que Edwin usa para buscar vehículos
    según las necesidades del cliente expresadas por Carlos.
    """
    
    name: str = "Búsqueda de Inventario"
    description: str = (
        "Busca vehículos en el inventario usando lenguaje natural. "
        "Puedes buscar por tipo de vehículo, presupuesto, color, características familiares, etc. "
        "Ejemplos: 'SUV seguro para familia bajo 35000', 'sedan rojo deportivo', 'vehículo económico híbrido'"
    )
    args_schema: Type[BaseModel] = InventorySearchInput
    
    def _run(self, query: str, max_results: int = 8) -> str:
        """Ejecuta la búsqueda de inventario"""
        try:
            print(f"🔍 Edwin busca: '{query}' (máx {max_results} resultados)")
            
            # Realizar búsqueda inteligente
            vehicles = inventory_manager.intelligent_search(query, max_results)
            
            if not vehicles:
                return f"❌ No se encontraron vehículos que coincidan con: '{query}'"
            
            # Formatear resultados para Edwin
            formatted_results = inventory_manager.format_vehicles_for_agent(vehicles, max_results)
            
            # Agregar estadísticas del inventario
            stats = inventory_manager.get_inventory_stats()
            
            response = f"""🏢 **RESPUESTA DE EDWIN - BÚSQUEDA DE INVENTARIO:**

{formatted_results}

**📊 Estadísticas del Inventario:**
• Total de vehículos: {stats['total']}
• Disponibles: {stats['available']}
• Reservados: {stats['reserved']}

**💡 Recomendación de Edwin:**
{self._generate_recommendation(vehicles, query)}
"""
            
            print(f"✅ Edwin encontró {len(vehicles)} vehículos")
            return response
            
        except Exception as e:
            error_msg = f"❌ Error en búsqueda de inventario: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _generate_recommendation(self, vehicles: List[Vehicle], query: str) -> str:
        """Genera recomendación de Edwin basada en los resultados"""
        if not vehicles:
            return "No hay recomendaciones disponibles."
        
        top_vehicle = vehicles[0]  # El de mayor relevancia
        
        recommendations = []
        
        # Recomendación por precio
        if top_vehicle.price < 25000:
            recommendations.append("Excelente opción económica")
        elif top_vehicle.price > 50000:
            recommendations.append("Vehículo premium con excelentes características")
        
        # Recomendación por año
        from datetime import datetime
        current_year = datetime.now().year
        if top_vehicle.year >= current_year - 1:
            recommendations.append("Modelo muy reciente")
        
        # Recomendación por tipo
        if top_vehicle.body_style.upper() == 'SUV':
            recommendations.append("Ideal para familias por espacio y seguridad")
        
        # Estrategia de venta
        if len(vehicles) > 3:
            recommendations.append(f"Priorizar {top_vehicle.make} {top_vehicle.model} por mejor relación calidad-precio")
        
        return ". ".join(recommendations) if recommendations else "Vehículo sólido según criterios solicitados."


class VehicleReservationTool(BaseTool):
    """
    Herramienta para reservar vehículos
    
    Esta herramienta es usada exclusivamente por Carlos cuando el cliente
    confirma la compra de un vehículo específico.
    """
    
    name: str = "Reservar Vehículo"
    description: str = (
        "Reserva un vehículo específico usando su VIN. "
        "SOLO usar cuando el cliente haya confirmado explícitamente que quiere comprar el vehículo. "
        "Requiere el VIN exacto del vehículo."
    )
    args_schema: Type[BaseModel] = VehicleReservationInput
    
    def _run(self, vin: str) -> str:
        """Ejecuta la reserva del vehículo"""
        try:
            print(f"🔒 Intentando reservar vehículo VIN: {vin}")
            
            # Obtener detalles del vehículo primero
            vehicle = inventory_manager.get_vehicle_by_vin(vin)
            
            if not vehicle:
                return f"❌ Error: No se encontró vehículo con VIN {vin}. Verificar VIN con Edwin."
            
            if vehicle.status != 'Available':
                return f"❌ Error: Vehículo {vehicle.make} {vehicle.model} (VIN: {vin}) no está disponible para reserva."
            
            # Intentar reservar
            success = inventory_manager.reserve_vehicle(vin)
            
            if success:
                response = f"""✅ **VEHÍCULO RESERVADO EXITOSAMENTE**

**Detalles de la Reserva:**
• **Vehículo:** {vehicle.year} {vehicle.make} {vehicle.model}
• **VIN:** {vin}
• **Precio:** ${vehicle.price:,.0f}
• **Color:** {vehicle.color}
• **Estado:** RESERVADO

**Próximos Pasos:**
• El cliente debe proceder con el papeleo
• Coordinación de entrega pendiente
• Reserva válida por 48 horas

¡Felicitaciones por cerrar la venta! 🎉"""
                
                print(f"✅ Vehículo {vin} reservado exitosamente")
                return response
            else:
                return f"❌ Error técnico al reservar vehículo {vin}. Contactar con Edwin para verificar disponibilidad."
                
        except Exception as e:
            error_msg = f"❌ Error en reserva de vehículo {vin}: {str(e)}"
            print(error_msg)
            return error_msg


class VehicleDetailsTool(BaseTool):
    """
    Herramienta para obtener detalles específicos de un vehículo
    
    Útil cuando Carlos necesita información detallada de un vehículo específico
    para responder preguntas del cliente.
    """
    
    name: str = "Detalles de Vehículo"
    description: str = (
        "Obtiene información detallada de un vehículo específico usando su VIN. "
        "Útil para responder preguntas específicas del cliente sobre un vehículo."
    )
    args_schema: Type[BaseModel] = VehicleDetailInput
    
    def _run(self, vin: str) -> str:
        """Obtiene detalles completos del vehículo"""
        try:
            print(f"📋 Obteniendo detalles del vehículo VIN: {vin}")
            
            vehicle = inventory_manager.get_vehicle_by_vin(vin)
            
            if not vehicle:
                return f"❌ No se encontró vehículo con VIN {vin}"
            
            response = f"""📋 **DETALLES COMPLETOS DEL VEHÍCULO**

**Información Básica:**
• **Marca y Modelo:** {vehicle.make} {vehicle.model}
• **Año:** {vehicle.year}
• **VIN:** {vehicle.vin}
• **Precio:** ${vehicle.price:,.0f}
• **Estado:** {vehicle.status}

**Especificaciones:**
• **Kilometraje:** {vehicle.mileage:,} km
• **Color:** {vehicle.color}
• **Tipo de Carrocería:** {vehicle.body_style}
• **Combustible:** {vehicle.fuel_type}
• **Transmisión:** {vehicle.transmission}
"""
            
            # Agregar calificación de seguridad si está disponible
            if vehicle.safety_rating:
                response += f"• **Calificación de Seguridad:** {vehicle.safety_rating}\n"
            
            # Agregar características si están disponibles
            if vehicle.features:
                response += f"\n**Características Adicionales:**\n{vehicle.features}\n"
            
            print(f"✅ Detalles obtenidos para {vehicle.make} {vehicle.model}")
            return response
            
        except Exception as e:
            error_msg = f"❌ Error obteniendo detalles del vehículo {vin}: {str(e)}"
            print(error_msg)
            return error_msg


class InventoryStatsTool(BaseTool):
    """
    Herramienta para obtener estadísticas generales del inventario
    
    Útil para Edwin cuando necesita dar información general sobre disponibilidad.
    """
    
    name: str = "Estadísticas de Inventario"
    description: str = (
        "Obtiene estadísticas generales del inventario: total de vehículos, "
        "disponibles, reservados, y resumen por categorías."
    )
    
    def _run(self, **kwargs) -> str:
        """Obtiene estadísticas del inventario"""
        try:
            print("📊 Generando estadísticas del inventario")
            
            stats = inventory_manager.get_inventory_stats()
            
            # Obtener información adicional
            df = inventory_manager.inventory_df
            
            if df.empty:
                return "❌ Inventario vacío o no disponible"
            
            # Estadísticas por marca
            top_makes = df['make'].value_counts().head(5)
            
            # Rango de precios
            min_price = df['price'].min()
            max_price = df['price'].max()
            avg_price = df['price'].mean()
            
            response = f"""📊 **ESTADÍSTICAS DEL INVENTARIO**

**Resumen General:**
• **Total de vehículos:** {stats['total']}
• **Disponibles:** {stats['available']}
• **Reservados:** {stats['reserved']}

**Información de Precios:**
• **Rango:** ${min_price:,.0f} - ${max_price:,.0f}
• **Precio promedio:** ${avg_price:,.0f}

**Top Marcas Disponibles:**
"""
            
            for make, count in top_makes.items():
                response += f"• {make}: {count} vehículos\n"
            
            print("✅ Estadísticas generadas exitosamente")
            return response
            
        except Exception as e:
            error_msg = f"❌ Error generando estadísticas: {str(e)}"
            print(error_msg)
            return error_msg


# Exportar todas las herramientas para fácil importación
__all__ = [
    'InventorySearchTool',
    'VehicleReservationTool', 
    'VehicleDetailsTool',
    'InventoryStatsTool'
]