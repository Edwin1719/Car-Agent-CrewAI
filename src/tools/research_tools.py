"""
Herramientas de Investigación para CrewAI

Estas herramientas permiten a María realizar investigación web y análisis técnico
de vehículos para proporcionar información detallada a Carlos y al cliente.
"""

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import os
import requests
from datetime import datetime


class VehicleResearchInput(BaseModel):
    """Input schema para investigación de vehículos"""
    vehicle_info: str = Field(..., description="Información del vehículo a investigar (marca, modelo, año)")
    research_focus: str = Field(default="general", description="Enfoque de la investigación: 'safety', 'reviews', 'specs', 'comparison', 'general'")


class MarketResearchInput(BaseModel):
    """Input schema para investigación de mercado"""
    query: str = Field(..., description="Consulta de investigación de mercado")


class VehicleResearchTool(BaseTool):
    """
    Herramienta principal de investigación de vehículos para María
    
    Proporciona información técnica, reseñas, calificaciones de seguridad
    y comparativas de vehículos específicos.
    """
    
    name: str = "Investigación de Vehículos"
    description: str = (
        "Investiga información técnica detallada sobre vehículos específicos. "
        "Incluye especificaciones, calificaciones de seguridad, reseñas de expertos, "
        "y comparativas de mercado. Enfoque puede ser: 'safety', 'reviews', 'specs', 'comparison', 'general'"
    )
    args_schema: Type[BaseModel] = VehicleResearchInput
    
    def _run(self, vehicle_info: str, research_focus: str = "general") -> str:
        """Ejecuta investigación detallada del vehículo"""
        try:
            print(f"🔍 María investigando: {vehicle_info} (enfoque: {research_focus})")
            
            # Intentar investigación web si está disponible SerpAPI
            web_results = self._web_research(vehicle_info, research_focus)
            
            if web_results:
                # Combinar con conocimiento interno
                internal_analysis = self._internal_analysis(vehicle_info, research_focus)
                
                response = f"""📊 **ANÁLISIS DE MARÍA - INVESTIGACIÓN DE VEHÍCULOS**

**Vehículo Investigado:** {vehicle_info}
**Enfoque:** {research_focus.title()}

{web_results}

{internal_analysis}

**Conclusión de María:**
{self._generate_conclusion(vehicle_info, research_focus)}

---
*Investigación realizada el {datetime.now().strftime('%d/%m/%Y %H:%M')} por María, Especialista en Investigación Automotriz*
"""
            else:
                # Solo análisis interno si no hay web research
                response = self._internal_analysis_detailed(vehicle_info, research_focus)
            
            print(f"✅ María completó investigación de {vehicle_info}")
            return response
            
        except Exception as e:
            error_msg = f"❌ Error en investigación de vehículo: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _web_research(self, vehicle_info: str, research_focus: str) -> Optional[str]:
        """Realiza investigación web usando SerpAPI si está disponible"""
        serpapi_key = os.getenv('SERPAPI_API_KEY')
        
        if not serpapi_key:
            print("⚠️ SerpAPI no disponible, usando conocimiento interno")
            return None
        
        try:
            # Construir query según el enfoque
            if research_focus == "safety":
                query = f"{vehicle_info} safety rating NHTSA IIHS crash test"
            elif research_focus == "reviews":
                query = f"{vehicle_info} expert reviews consumer reports"
            elif research_focus == "specs":
                query = f"{vehicle_info} specifications engine transmission features"
            elif research_focus == "comparison":
                query = f"{vehicle_info} vs competitors comparison"
            else:
                query = f"{vehicle_info} review specifications safety"
            
            # Realizar búsqueda
            url = "https://serpapi.com/search"
            params = {
                "engine": "google",
                "q": query,
                "api_key": serpapi_key,
                "num": 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_web_results(data, research_focus)
            else:
                print(f"⚠️ Error en SerpAPI: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error en investigación web: {e}")
            return None
    
    def _process_web_results(self, data: dict, research_focus: str) -> str:
        """Procesa los resultados de la búsqueda web"""
        organic_results = data.get('organic_results', [])
        
        if not organic_results:
            return "**Investigación Web:** No se encontraron resultados específicos."
        
        processed_info = ["**📡 Investigación Web Actualizada:**"]
        
        for i, result in enumerate(organic_results[:3], 1):
            title = result.get('title', 'Sin título')
            snippet = result.get('snippet', 'Sin descripción disponible')
            
            processed_info.append(f"""
**Fuente {i}: {title}**
{snippet}
""")
        
        return "\n".join(processed_info)
    
    def _internal_analysis(self, vehicle_info: str, research_focus: str) -> str:
        """Análisis usando conocimiento interno de María"""
        
        if research_focus == "safety":
            return self._safety_analysis(vehicle_info)
        elif research_focus == "specs":
            return self._specs_analysis(vehicle_info)
        elif research_focus == "reviews":
            return self._reviews_analysis(vehicle_info)
        else:
            return self._general_analysis(vehicle_info)
    
    def _internal_analysis_detailed(self, vehicle_info: str, research_focus: str) -> str:
        """Análisis interno detallado cuando no hay web research"""
        
        response = f"""📊 **ANÁLISIS DE MARÍA - CONOCIMIENTO INTERNO**

**Vehículo Analizado:** {vehicle_info}
**Enfoque:** {research_focus.title()}

{self._internal_analysis(vehicle_info, research_focus)}

**Recomendaciones Técnicas:**
{self._technical_recommendations(vehicle_info, research_focus)}

**Nota:** *Análisis basado en conocimiento interno. Para información más actualizada, se recomienda configurar SerpAPI.*

---
*Análisis técnico por María, Especialista en Investigación Automotriz*
"""
        return response
    
    def _safety_analysis(self, vehicle_info: str) -> str:
        """Análisis de seguridad"""
        return f"""
**🛡️ Análisis de Seguridad:**

**Estándares de Seguridad Típicos:**
• Calificaciones NHTSA: Buscar 4-5 estrellas
• Premios IIHS Top Safety Pick cuando disponible
• Sistemas de asistencia al conductor estándar

**Características de Seguridad Modernas Esperadas:**
• Frenado automático de emergencia
• Advertencia de cambio de carril
• Monitoreo de punto ciego
• Control de estabilidad avanzado

**Recomendación:** Verificar calificaciones específicas del año {vehicle_info.split()[-1] if vehicle_info.split() else 'del modelo'} para confirmación exacta.
"""
    
    def _specs_analysis(self, vehicle_info: str) -> str:
        """Análisis de especificaciones"""
        return f"""
**⚙️ Análisis de Especificaciones:**

**Aspectos Técnicos Típicos a Considerar:**
• Motor y rendimiento de combustible
• Capacidad de carga y espacio interior
• Tecnología y conectividad
• Sistemas de transmisión disponibles

**Características Modernas Esperadas:**
• Pantalla táctil con Apple CarPlay/Android Auto
• Cámara de reversa
• Puertos USB múltiples
• Sistemas de climatización automática

**Nota Técnica:** Las especificaciones exactas varían por trim level y año del modelo.
"""
    
    def _reviews_analysis(self, vehicle_info: str) -> str:
        """Análisis de reseñas"""
        return f"""
**📝 Análisis de Reseñas Típicas:**

**Aspectos Comúnmente Evaluados:**
• Confiabilidad y durabilidad a largo plazo
• Costo de mantenimiento
• Experiencia de conducción
• Valor de reventa

**Fuentes Recomendadas para Verificación:**
• Consumer Reports para confiabilidad
• Kelley Blue Book para valor de mercado
• Edmunds para reseñas de expertos
• Opiniones de propietarios en foros especializados

**Consejo:** Considerar reseñas de múltiples años para tendencias de confiabilidad.
"""
    
    def _general_analysis(self, vehicle_info: str) -> str:
        """Análisis general"""
        return f"""
**🔍 Análisis General:**

**Puntos de Investigación Clave:**
• Posición competitiva en su segmento
• Historial de confiabilidad de la marca
• Disponibilidad de piezas y servicio
• Tendencias de depreciación

**Factores de Decisión Importantes:**
• Costo total de propiedad
• Adecuación para necesidades específicas del cliente
• Disponibilidad de financiamiento
• Garantías y servicios incluidos
"""
    
    def _technical_recommendations(self, vehicle_info: str, research_focus: str) -> str:
        """Genera recomendaciones técnicas específicas"""
        recommendations = []
        
        if "SUV" in vehicle_info.upper():
            recommendations.append("Verificar capacidad de remolque si es relevante")
            recommendations.append("Evaluar sistema de tracción (AWD vs FWD)")
        
        if "sedan" in vehicle_info.lower():
            recommendations.append("Considerar eficiencia de combustible en ciudad")
            recommendations.append("Evaluar espacio de maletero")
        
        if research_focus == "safety":
            recommendations.append("Solicitar informe detallado de crash tests")
            recommendations.append("Verificar recalls de seguridad vigentes")
        
        return "• " + "\n• ".join(recommendations) if recommendations else "Evaluación caso por caso según necesidades específicas."
    
    def _generate_conclusion(self, vehicle_info: str, research_focus: str) -> str:
        """Genera conclusión personalizada"""
        conclusions = {
            "safety": f"El {vehicle_info} muestra características de seguridad acordes a estándares modernos. Recomiendo verificar calificaciones específicas del año.",
            "specs": f"Las especificaciones del {vehicle_info} son competitivas en su segmento. Considerar trim level según necesidades específicas.",
            "reviews": f"Las reseñas del {vehicle_info} generalmente reflejan buena relación calidad-precio. Evaluar según prioridades del cliente.",
            "general": f"El {vehicle_info} representa una opción sólida en su categoría. Recomiendo considerarlo dentro del contexto de necesidades específicas del cliente."
        }
        
        return conclusions.get(research_focus, f"El {vehicle_info} requiere evaluación específica según criterios del cliente.")


class MarketComparisonTool(BaseTool):
    """
    Herramienta para comparaciones de mercado
    
    Permite a María comparar vehículos similares y proporcionar
    análisis competitivo.
    """
    
    name: str = "Comparación de Mercado"
    description: str = (
        "Realiza comparaciones entre vehículos similares en el mercado. "
        "Útil para mostrar al cliente cómo se posiciona un vehículo frente a la competencia."
    )
    args_schema: Type[BaseModel] = MarketResearchInput
    
    def _run(self, query: str) -> str:
        """Ejecuta comparación de mercado"""
        try:
            print(f"📊 María comparando mercado: {query}")
            
            response = f"""📊 **COMPARACIÓN DE MERCADO - MARÍA**

**Análisis Solicitado:** {query}

**🏆 Factores de Comparación Clave:**

**Precio y Valor:**
• Posicionamiento en el segmento
• Relación precio-equipamiento
• Costo total de propiedad proyectado

**Rendimiento y Eficiencia:**
• Consumo de combustible comparativo
• Potencia y torque en la categoría
• Capacidades de carga/remolque

**Seguridad y Confiabilidad:**
• Calificaciones de seguridad relativas
• Historial de recalls y problemas
• Garantías ofrecidas

**Tecnología y Comodidad:**
• Características estándar vs opcionales
• Sistemas de infoentretenimiento
• Espacios interiores y comodidades

**Recomendación de María:**
Para una comparación precisa, considerar vehículos en rango de precio similar (+/- 15%) y categoría equivalente. Evaluar según prioridades específicas del cliente.

**Próximo Paso Sugerido:**
Definir 2-3 criterios más importantes para el cliente y enfocar comparación en esos aspectos específicos.
"""
            
            print(f"✅ María completó comparación de mercado")
            return response
            
        except Exception as e:
            error_msg = f"❌ Error en comparación de mercado: {str(e)}"
            print(error_msg)
            return error_msg


# Exportar herramientas
__all__ = [
    'VehicleResearchTool',
    'MarketComparisonTool'
]