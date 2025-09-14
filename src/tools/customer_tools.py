"""
Herramientas de Gestión de Clientes para CrewAI

Estas herramientas permiten a Carlos gestionar información del cliente,
actualizar perfiles y manejar el proceso de venta.
"""

from crewai.tools import BaseTool
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class CustomerProfile:
    """Perfil del cliente"""
    # Información básica
    name: Optional[str] = None
    contact_info: Optional[str] = None
    
    # Preferencias de vehículo
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    preferred_make: Optional[str] = None
    preferred_color: Optional[str] = None
    body_style_preference: Optional[str] = None
    fuel_type_preference: Optional[str] = None
    
    # Información familiar/personal
    family_size: Optional[str] = None
    primary_use: Optional[str] = None
    
    # Prioridades
    safety_priority: bool = False
    luxury_preference: bool = False
    eco_friendly: bool = False
    
    # Notas del proceso
    needs: list = field(default_factory=list)
    objections: list = field(default_factory=list)
    interests: list = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    sales_stage: str = "greeting"


class CustomerProfileInput(BaseModel):
    """Input schema para actualización de perfil"""
    profile_data: dict = Field(..., description="Datos del perfil del cliente en formato JSON")


class SalesStageInput(BaseModel):
    """Input schema para actualización de etapa de venta"""
    new_stage: str = Field(..., description="Nueva etapa de venta: greeting, discovery, presentation, negotiation, closing, follow_up")
    notes: Optional[str] = Field(None, description="Notas adicionales sobre el cambio de etapa")


class CustomerNotesInput(BaseModel):
    """Input schema para notas del cliente"""
    note: str = Field(..., description="Nota a agregar sobre el cliente")
    category: Optional[str] = Field("general", description="Categoría de la nota: general, needs, objection, interest")


# Estado global del cliente (en una aplicación real sería una base de datos)
current_customer = CustomerProfile()
customer_notes = []


class CustomerProfileTool(BaseTool):
    """
    Herramienta para gestionar el perfil del cliente
    
    Permite a Carlos actualizar y mantener información detallada
    sobre las necesidades y preferencias del cliente.
    """
    
    name: str = "Gestión de Perfil del Cliente"
    description: str = (
        "Actualiza y gestiona el perfil del cliente con información sobre preferencias, "
        "presupuesto, necesidades familiares, y otros datos relevantes para la venta. "
        "Los datos deben proporcionarse en formato JSON."
    )
    args_schema: Type[BaseModel] = CustomerProfileInput
    
    def _run(self, profile_data: dict) -> str:
        """Actualiza el perfil del cliente"""
        try:
            global current_customer
            
            print(f"👤 Carlos actualizando perfil del cliente: {profile_data}")
            
            # Actualizar campos del perfil
            for key, value in profile_data.items():
                if hasattr(current_customer, key) and value is not None:
                    setattr(current_customer, key, value)
            
            # Actualizar timestamp
            current_customer.last_updated = datetime.now()
            
            # Generar resumen del perfil
            profile_summary = self._generate_profile_summary()
            
            response = f"""👤 **PERFIL DEL CLIENTE ACTUALIZADO**

{profile_summary}

**Última Actualización:** {current_customer.last_updated.strftime('%d/%m/%Y %H:%M')}

**✅ Información Capturada Exitosamente**
Carlos puede usar esta información para personalizar recomendaciones y mejorar la experiencia del cliente.
"""
            
            print("✅ Perfil del cliente actualizado exitosamente")
            return response
            
        except Exception as e:
            error_msg = f"❌ Error actualizando perfil del cliente: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _generate_profile_summary(self) -> str:
        """Genera un resumen del perfil actual"""
        summary_parts = []
        
        # Información básica
        if current_customer.name:
            summary_parts.append(f"**Nombre:** {current_customer.name}")
        
        # Presupuesto
        if current_customer.budget_min or current_customer.budget_max:
            budget_str = "**Presupuesto:** "
            if current_customer.budget_min:
                budget_str += f"desde ${current_customer.budget_min:,} "
            if current_customer.budget_max:
                budget_str += f"hasta ${current_customer.budget_max:,}"
            summary_parts.append(budget_str.strip())
        
        # Preferencias de vehículo
        if current_customer.preferred_make:
            summary_parts.append(f"**Marca Preferida:** {current_customer.preferred_make}")
        
        if current_customer.body_style_preference:
            summary_parts.append(f"**Tipo de Vehículo:** {current_customer.body_style_preference}")
        
        if current_customer.preferred_color:
            summary_parts.append(f"**Color Preferido:** {current_customer.preferred_color}")
        
        # Información familiar
        if current_customer.family_size:
            summary_parts.append(f"**Tamaño Familiar:** {current_customer.family_size}")
        
        if current_customer.primary_use:
            summary_parts.append(f"**Uso Principal:** {current_customer.primary_use}")
        
        # Prioridades
        priorities = []
        if current_customer.safety_priority:
            priorities.append("Seguridad")
        if current_customer.luxury_preference:
            priorities.append("Lujo")
        if current_customer.eco_friendly:
            priorities.append("Ecológico")
        
        if priorities:
            summary_parts.append(f"**Prioridades:** {', '.join(priorities)}")
        
        # Necesidades y objecciones
        if current_customer.needs:
            summary_parts.append(f"**Necesidades:** {', '.join(current_customer.needs)}")
        
        if current_customer.objections:
            summary_parts.append(f"**Objeciones:** {', '.join(current_customer.objections)}")
        
        return "\n".join(summary_parts) if summary_parts else "**Perfil en construcción - información básica pendiente**"


class SalesStageManager(BaseTool):
    """
    Herramienta para gestionar las etapas del proceso de venta
    
    Permite a Carlos rastrear y actualizar en qué etapa del proceso
    de venta se encuentra con el cliente.
    """
    
    name: str = "Gestión de Etapas de Venta"
    description: str = (
        "Actualiza la etapa actual del proceso de venta. "
        "Etapas disponibles: greeting, discovery, presentation, negotiation, closing, follow_up"
    )
    args_schema: Type[BaseModel] = SalesStageInput
    
    def _run(self, new_stage: str, notes: Optional[str] = None) -> str:
        """Actualiza la etapa de venta"""
        try:
            global current_customer
            
            valid_stages = ["greeting", "discovery", "presentation", "negotiation", "closing", "follow_up"]
            
            if new_stage not in valid_stages:
                return f"❌ Etapa inválida. Etapas válidas: {', '.join(valid_stages)}"
            
            previous_stage = current_customer.sales_stage
            current_customer.sales_stage = new_stage
            current_customer.last_updated = datetime.now()
            
            print(f"📈 Carlos cambió etapa de venta: {previous_stage} → {new_stage}")
            
            stage_descriptions = {
                "greeting": "Saludo inicial y construcción de rapport",
                "discovery": "Descubrimiento de necesidades del cliente", 
                "presentation": "Presentación de vehículos relevantes",
                "negotiation": "Negociación y manejo de objeciones",
                "closing": "Cierre de la venta",
                "follow_up": "Seguimiento post-venta"
            }
            
            response = f"""📈 **ETAPA DE VENTA ACTUALIZADA**

**Etapa Anterior:** {previous_stage.title()} → **Etapa Actual:** {new_stage.title()}

**Descripción:** {stage_descriptions.get(new_stage, new_stage.title())}

**Progreso de Venta:** {self._calculate_progress(new_stage)}%
"""
            
            if notes:
                response += f"\n**Notas:** {notes}"
            
            response += f"\n\n**Próximos Pasos Sugeridos:**\n{self._get_next_steps(new_stage)}"
            
            print(f"✅ Etapa actualizada a: {new_stage}")
            return response
            
        except Exception as e:
            error_msg = f"❌ Error actualizando etapa de venta: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _calculate_progress(self, stage: str) -> int:
        """Calcula el porcentaje de progreso según la etapa"""
        progress_map = {
            "greeting": 15,
            "discovery": 30,
            "presentation": 50,
            "negotiation": 75,
            "closing": 90,
            "follow_up": 100
        }
        return progress_map.get(stage, 0)
    
    def _get_next_steps(self, stage: str) -> str:
        """Obtiene los próximos pasos sugeridos para cada etapa"""
        next_steps = {
            "greeting": "• Establecer rapport y confianza\n• Identificar motivación principal de compra\n• Hacer transición suave a descubrimiento",
            "discovery": "• Hacer preguntas abiertas sobre necesidades\n• Identificar presupuesto y timeline\n• Consultar inventario con Edwin",
            "presentation": "• Mostrar vehículos que coincidan con necesidades\n• Solicitar investigación técnica a María\n• Permitir al cliente hacer preguntas",
            "negotiation": "• Escuchar y entender objeciones\n• Proporcionar soluciones específicas\n• Buscar puntos de acuerdo",
            "closing": "• Confirmar decisión de compra\n• Obtener VIN específico de Edwin\n• Proceder con reserva del vehículo",
            "follow_up": "• Confirmar satisfacción del cliente\n• Coordinar entrega y papeleo\n• Programar seguimientos futuros"
        }
        return next_steps.get(stage, "Continuar con el proceso según necesidades del cliente")


class CustomerNotesTool(BaseTool):
    """
    Herramienta para gestionar notas sobre el cliente
    
    Permite a Carlos añadir y gestionar notas específicas sobre
    las interacciones y observaciones del cliente.
    """
    
    name: str = "Notas del Cliente"
    description: str = (
        "Añade notas específicas sobre el cliente durante la conversación. "
        "Categorías: general, needs, objection, interest"
    )
    args_schema: Type[BaseModel] = CustomerNotesInput
    
    def _run(self, note: str, category: str = "general") -> str:
        """Añade una nota sobre el cliente"""
        try:
            global customer_notes
            
            timestamp = datetime.now()
            note_entry = {
                "timestamp": timestamp,
                "content": note,
                "category": category
            }
            
            customer_notes.append(note_entry)
            
            print(f"📝 Carlos añadió nota ({category}): {note}")
            
            # Actualizar perfil según categoría
            if category == "needs" and hasattr(current_customer, 'needs'):
                if note not in current_customer.needs:
                    current_customer.needs.append(note)
            elif category == "objection" and hasattr(current_customer, 'objections'):
                if note not in current_customer.objections:
                    current_customer.objections.append(note)
            elif category == "interest" and hasattr(current_customer, 'interests'):
                if note not in current_customer.interests:
                    current_customer.interests.append(note)
            
            response = f"""📝 **NOTA AÑADIDA AL PERFIL DEL CLIENTE**

**Categoría:** {category.title()}
**Contenido:** {note}
**Hora:** {timestamp.strftime('%H:%M')}

**Total de Notas:** {len(customer_notes)}

**✅ Nota guardada exitosamente**
Esta información ayudará a personalizar mejor la experiencia del cliente.
"""
            
            print(f"✅ Nota añadida exitosamente")
            return response
            
        except Exception as e:
            error_msg = f"❌ Error añadiendo nota del cliente: {str(e)}"
            print(error_msg)
            return error_msg


class CustomerSummaryTool(BaseTool):
    """
    Herramienta para obtener resumen completo del cliente
    
    Proporciona a Carlos un resumen completo de toda la información
    disponible sobre el cliente actual.
    """
    
    name: str = "Resumen del Cliente"
    description: str = (
        "Obtiene un resumen completo del cliente actual incluyendo perfil, "
        "etapa de venta, notas y progreso de la conversación."
    )
    
    def _run(self, **kwargs) -> str:
        """Genera resumen completo del cliente"""
        try:
            global current_customer, customer_notes
            
            print("📋 Carlos generando resumen completo del cliente")
            
            # Información básica del perfil
            profile_tool = CustomerProfileTool()
            profile_summary = profile_tool._generate_profile_summary()
            
            # Información de etapa
            stage_tool = SalesStageManager()
            progress = stage_tool._calculate_progress(current_customer.sales_stage)
            
            response = f"""📋 **RESUMEN COMPLETO DEL CLIENTE**

**📊 Progreso de Venta:** {progress}% ({current_customer.sales_stage.title()})

{profile_summary}

**📝 Notas Recientes ({len(customer_notes)} total):**
"""
            
            # Añadir últimas 5 notas
            recent_notes = customer_notes[-5:] if customer_notes else []
            if recent_notes:
                for note in reversed(recent_notes):
                    response += f"• [{note['category'].title()}] {note['content']}\n"
            else:
                response += "• No hay notas registradas aún\n"
            
            response += f"""
**⏰ Información de Sesión:**
• Perfil creado: {current_customer.created_at.strftime('%d/%m/%Y %H:%M')}
• Última actualización: {current_customer.last_updated.strftime('%d/%m/%Y %H:%M')}

**🎯 Recomendaciones para Carlos:**
{self._generate_recommendations()}
"""
            
            print("✅ Resumen del cliente generado")
            return response
            
        except Exception as e:
            error_msg = f"❌ Error generando resumen del cliente: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _generate_recommendations(self) -> str:
        """Genera recomendaciones basadas en el perfil actual"""
        recommendations = []
        
        # Recomendaciones basadas en completitud del perfil
        if not current_customer.budget_max:
            recommendations.append("Definir presupuesto máximo del cliente")
        
        if not current_customer.primary_use:
            recommendations.append("Identificar uso principal del vehículo")
        
        if not current_customer.needs:
            recommendations.append("Explorar necesidades específicas del cliente")
        
        # Recomendaciones basadas en etapa
        if current_customer.sales_stage == "greeting":
            recommendations.append("Hacer transición a descubrimiento de necesidades")
        elif current_customer.sales_stage == "discovery":
            recommendations.append("Consultar inventario con Edwin basado en necesidades")
        elif current_customer.sales_stage == "presentation":
            recommendations.append("Solicitar investigación técnica a María si es necesario")
        
        return "• " + "\n• ".join(recommendations) if recommendations else "Continuar desarrollando la relación con el cliente"


# Exportar herramientas
__all__ = [
    'CustomerProfileTool',
    'SalesStageManager', 
    'CustomerNotesTool',
    'CustomerSummaryTool',
    'CustomerProfile',
    'current_customer',
    'customer_notes'
]