"""
Simple Automotive Tools - Sin complicaciones innecesarias
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Type
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.automotive_expert import automotive_expert, analyze_query


class BrandComparisonInput(BaseModel):
    brand1: str = Field(..., description="Primera marca a comparar")
    brand2: str = Field(..., description="Segunda marca a comparar")
    focus: Optional[str] = Field("overall", description="Enfoque de comparación")


class BrandAnalysisInput(BaseModel):
    brand: str = Field(..., description="Marca a analizar")
    aspect: Optional[str] = Field("general", description="Aspecto a analizar")


class CustomerQueryInput(BaseModel):
    query: str = Field(..., description="Consulta del cliente")


class BrandComparisonTool(BaseTool):
    name: str = "brand_comparison"
    description: str = "Compara dos marcas automotrices técnicamente"
    args_schema: Type[BaseModel] = BrandComparisonInput

    def _run(self, brand1: str, brand2: str, focus: str = "overall") -> str:
        try:
            return automotive_expert.compare_brands(brand1, brand2, focus)
        except Exception as e:
            return f"Error en comparación: {str(e)}"


class BrandAnalysisTool(BaseTool):
    name: str = "brand_analysis"
    description: str = "Analiza una marca automotriz específica"
    args_schema: Type[BaseModel] = BrandAnalysisInput

    def _run(self, brand: str, aspect: str = "general") -> str:
        try:
            return automotive_expert.get_brand_expertise(brand, aspect)
        except Exception as e:
            return f"Error en análisis: {str(e)}"


class CustomerQueryAnalysisTool(BaseTool):
    name: str = "query_analysis"
    description: str = "Analiza consultas de clientes sobre vehículos"
    args_schema: Type[BaseModel] = CustomerQueryInput

    def _run(self, query: str) -> str:
        try:
            analysis = analyze_query(query)
            return f"Análisis: {analysis}"
        except Exception as e:
            return f"Error en análisis: {str(e)}"


class TechnicalRecommendationTool(BaseTool):
    name: str = "technical_recommendation"
    description: str = "Genera recomendaciones técnicas"
    args_schema: Type[BaseModel] = CustomerQueryInput

    def _run(self, query: str) -> str:
        try:
            analysis = analyze_query(query)
            if analysis['brands'] and len(analysis['brands']) >= 2:
                brand1, brand2 = analysis['brands'][:2]
                return automotive_expert.compare_brands(brand1, brand2, "overall")
            elif analysis['brands']:
                return automotive_expert.get_brand_expertise(analysis['brands'][0])
            else:
                return "Proporciona más detalles sobre marcas específicas"
        except Exception as e:
            return f"Error en recomendación: {str(e)}"


def create_automotive_tools():
    return [
        BrandComparisonTool(),
        BrandAnalysisTool(),
        CustomerQueryAnalysisTool(),
        TechnicalRecommendationTool()
    ]

automotive_tools = create_automotive_tools()