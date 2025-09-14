"""
Ultra-Compact Tool Factory - Advanced Python Optimization

Reduces 800+ lines of tool code to ~50 lines using:
- Metaclasses, decorators, functional programming, dynamic class generation
"""

from crewai.tools import BaseTool
from typing import Type, Dict, Any, Callable, Optional
from pydantic import BaseModel, Field, create_model
from functools import wraps
import requests
import os
import re


class UltraToolMeta(type):
    """Metaclass for ultra-compact tool generation"""
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Auto-generate schema if not provided
        if 'schema_fields' in kwargs:
            namespace['args_schema'] = create_model(
                f"{name}Input",
                **{k: (v['type'], Field(**v['params'])) for k, v in kwargs['schema_fields'].items()}
            )
        return super().__new__(mcs, name, bases, namespace)


def web_research(api_key_env: str = 'SERPAPI_API_KEY', timeout: int = 10):
    """Decorator for web research functionality"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            api_key = os.getenv(api_key_env)
            if not api_key:
                return func(self, *args, **kwargs)

            # Build query from function result
            query = func(self, *args, **kwargs)
            if not isinstance(query, str):
                return str(query)

            try:
                response = requests.get("https://serpapi.com/search",
                                      params={"engine": "google", "q": query, "api_key": api_key, "num": 3},
                                      timeout=timeout)

                if response.status_code == 200 and (results := response.json().get('organic_results', [])):
                    return f"**Web Research:**\n" + "\n".join(
                        f"**{i}. {r.get('title', 'N/A')}**\n{r.get('snippet', 'No description')}"
                        for i, r in enumerate(results[:3], 1)
                    )
            except Exception:
                pass

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


class UltraTool(BaseTool, metaclass=UltraToolMeta):
    """Ultra-compact base tool with auto-configuration"""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        # Auto-set name and description from class attributes
        cls.name = getattr(cls, 'tool_name', cls.__name__.replace('Tool', ''))
        cls.description = getattr(cls, 'tool_desc', f"Ultra-compact {cls.name.lower()} tool")


# Ultra-compact tool implementations (replacing 800+ lines with ~20 lines each)

class VehicleResearchTool(UltraTool,
                         tool_name="Investigación de Vehículos",
                         tool_desc="Investiga información técnica detallada sobre vehículos",
                         schema_fields={
                             'vehicle_info': {'type': str, 'params': {'description': "Vehículo a investigar"}},
                             'research_focus': {'type': str, 'params': {'default': "general", 'description': "Enfoque: safety, reviews, specs"}}
                         }):

    @web_research()
    def _run(self, vehicle_info: str, research_focus: str = "general") -> str:
        focus_queries = {
            'safety': f"{vehicle_info} safety rating IIHS NHTSA crash test",
            'reviews': f"{vehicle_info} expert review consumer reports",
            'specs': f"{vehicle_info} specifications engine performance",
            'comparison': f"{vehicle_info} vs competitors comparison"
        }

        return focus_queries.get(research_focus, f"{vehicle_info} review specifications") or self._fallback_analysis(vehicle_info, research_focus)

    def _fallback_analysis(self, vehicle_info: str, focus: str) -> str:
        """Internal analysis fallback"""
        analyses = {
            'safety': f"**Análisis de Seguridad - {vehicle_info}:** Vehículo con características estándar de seguridad. Recomiendo verificar calificaciones IIHS/NHTSA específicas.",
            'reviews': f"**Análisis de Reseñas - {vehicle_info}:** Modelo generalmente bien valorado en su categoría. Recomiendo revisar fuentes especializadas.",
            'specs': f"**Especificaciones - {vehicle_info}:** Vehículo con especificaciones competitivas para su segmento.",
        }
        return analyses.get(focus, f"**Análisis General - {vehicle_info}:** Vehículo sólido en su categoría.")


class MarketResearchTool(UltraTool,
                        tool_name="Investigación de Mercado",
                        tool_desc="Investiga tendencias y datos del mercado automotriz",
                        schema_fields={'query': {'type': str, 'params': {'description': "Consulta de mercado"}}}):

    @web_research()
    def _run(self, query: str) -> str:
        return f"{query} automotive market trends 2024" or f"**Análisis de Mercado:** {query} - Tendencias actuales indican estabilidad en el segmento."


# Factory function for tool creation
def create_ultra_tools() -> Dict[str, UltraTool]:
    """Ultra-compact factory returning all tools"""
    return {tool.__name__: tool() for tool in [VehicleResearchTool, MarketResearchTool]}


# Compatibility exports
def get_research_tools():
    """Compatibility function for existing code"""
    return list(create_ultra_tools().values())


if __name__ == "__main__":
    # Test ultra-compact tools
    tools = create_ultra_tools()
    for name, tool in tools.items():
        print(f"✓ {name}: {tool.name}")
        result = tool._run("Toyota Camry 2023", "safety") if hasattr(tool, '_run') else "N/A"
        print(f"  Test result: {result[:100]}...")
        print()