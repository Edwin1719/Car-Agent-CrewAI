"""
Vehicle Inventory Management System for CrewAI CarBot Pro

Este módulo maneja todo el inventario de vehículos con búsqueda inteligente,
reservas y gestión de estado. Simplificado para trabajar con CrewAI.
"""

import pandas as pd
import os
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import hashlib
import time
from functools import lru_cache
import logging

# Configurar logging para evitar problemas de encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('inventory.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Vehicle:
    """Clase que representa un vehículo individual"""
    vin: str
    make: str
    model: str
    year: int
    price: float
    mileage: int
    color: str
    body_style: str
    fuel_type: str
    transmission: str
    status: str = "Available"
    safety_rating: Optional[str] = None
    features: Optional[str] = None


class InventoryManager:
    """
    Gestor de inventario simplificado para CrewAI
    
    Funcionalidades principales:
    - Búsqueda inteligente con NLP
    - Reserva de vehículos
    - Filtrado avanzado
    - Scoring de relevancia
    """
    
    def __init__(self, csv_path: str = None):
        """Inicializa el gestor de inventario"""
        if csv_path is None:
            csv_path = os.path.join(os.path.dirname(__file__), "data", "vehicle_inventory.csv")
        
        self.csv_path = csv_path
        self.inventory_df = pd.DataFrame()

        # OPTIMIZACIÓN: Sistema de caché LRU para búsquedas
        self._cache_ttl = 300  # 5 minutos de TTL
        self._search_cache = {}
        self._cache_stats = {'hits': 0, 'misses': 0}

        self.load_inventory()
    
    def load_inventory(self) -> bool:
        """Carga el inventario desde CSV"""
        try:
            if os.path.exists(self.csv_path):
                self.inventory_df = pd.read_csv(self.csv_path)
                
                # Asegurar que existe la columna status
                if 'status' not in self.inventory_df.columns:
                    self.inventory_df['status'] = 'Available'
                
                logger.info(f"Inventario cargado exitosamente: {len(self.inventory_df)} vehiculos")
                return True
            else:
                logger.error(f"Archivo de inventario no encontrado: {self.csv_path}")
                return False
        except Exception as e:
            logger.error(f"Error cargando inventario: {e}")
            return False
    
    def intelligent_search(self, query: str, max_results: int = 8) -> List[Vehicle]:
        """
        OPTIMIZACIÓN: Búsqueda inteligente con sistema de caché LRU

        Implementa caché con TTL para mejorar performance en búsquedas repetidas.
        Mantiene exactamente la misma funcionalidad que antes.

        Ejemplos de queries:
        - "SUV seguro para familia bajo 35000"
        - "sedan rojo deportivo"
        - "vehículo económico híbrido"
        """
        if self.inventory_df.empty:
            return []

        # OPTIMIZACIÓN: Verificar caché antes de procesar
        cache_key = self._generate_cache_key(query, max_results)
        cached_result = self._get_cached_result(cache_key)

        if cached_result is not None:
            self._cache_stats['hits'] += 1
            logger.debug(f"Cache HIT para query: {query[:50]}...")
            return cached_result

        # Cache MISS - procesar búsqueda normal
        self._cache_stats['misses'] += 1
        logger.debug(f"Cache MISS para query: {query[:50]}...")

        # Parse de la query (lógica original sin cambios)
        criteria = self._parse_search_query(query)
        logger.debug(f"Criterios extraidos de busqueda: {criteria}")

        # Aplicar filtros (lógica original sin cambios)
        filtered_df = self._apply_filters(self.inventory_df.copy(), criteria)

        if filtered_df.empty:
            # Cache empty results also
            self._cache_result(cache_key, [])
            return []

        # Calcular relevancia y ordenar (lógica original sin cambios)
        filtered_df['relevance_score'] = filtered_df.apply(
            lambda row: self._calculate_relevance(row, criteria), axis=1
        )

        # Ordenar por relevancia y tomar los mejores
        top_results = filtered_df.nlargest(max_results, 'relevance_score')

        # Convertir a objetos Vehicle (lógica original sin cambios)
        vehicles = []
        for _, row in top_results.iterrows():
            vehicle = Vehicle(
                vin=row['vin'],
                make=row['make'],
                model=row['model'],
                year=int(row['year']),
                price=float(row['price']),
                mileage=int(row['mileage']),
                color=row['color'],
                body_style=row['body_styles'],
                fuel_type=row['fuel_type'],
                transmission=row['transmission'],
                status=row.get('status', 'Available'),
                safety_rating=row.get('safety_rating', None),
                features=row.get('features', None)
            )
            vehicles.append(vehicle)

        # OPTIMIZACIÓN: Guardar resultado en caché
        self._cache_result(cache_key, vehicles)

        return vehicles
    
    def _parse_search_query(self, query: str) -> Dict[str, Any]:
        """Extrae criterios de búsqueda del lenguaje natural"""
        query_lower = query.lower()
        criteria = {}
        
        # Extracción de presupuesto
        budget_patterns = [
            r'bajo (\d+)',
            r'menos de (\d+)',
            r'hasta (\d+)',
            r'máximo (\d+)',
            r'presupuesto (\d+)'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, query_lower)
            if match:
                criteria['budget_max'] = int(match.group(1))
                break
        
        # Tipos de vehículo
        vehicle_types = {
            'suv': ['suv', 'camioneta', 'todoterreno'],
            'sedan': ['sedan', 'sedán'],
            'hatchback': ['hatchback', 'compacto'],
            'truck': ['truck', 'pickup', 'camión'],
            'convertible': ['convertible', 'descapotable'],
            'coupe': ['coupe', 'coupé', 'deportivo']
        }
        
        for vehicle_type, keywords in vehicle_types.items():
            if any(keyword in query_lower for keyword in keywords):
                criteria['body_style'] = vehicle_type.upper()
                break
        
        # Colores
        colors = {
            'rojo': ['rojo', 'red'],
            'azul': ['azul', 'blue'],
            'negro': ['negro', 'black'],
            'blanco': ['blanco', 'white'],
            'gris': ['gris', 'gray', 'grey'],
            'plata': ['plata', 'silver']
        }
        
        for color, keywords in colors.items():
            if any(keyword in query_lower for keyword in keywords):
                criteria['color'] = color.title()
                break
        
        # Características especiales
        if any(word in query_lower for word in ['familia', 'familiar', 'seguro']):
            criteria['family_friendly'] = True
        
        if any(word in query_lower for word in ['económico', 'barato', 'híbrido']):
            criteria['economical'] = True
        
        if any(word in query_lower for word in ['lujo', 'premium', 'luxury']):
            criteria['luxury'] = True
        
        return criteria
    
    def _apply_filters(self, df: pd.DataFrame, criteria: Dict[str, Any]) -> pd.DataFrame:
        """Aplica filtros basados en los criterios extraídos"""
        
        # Filtro de presupuesto
        if 'budget_max' in criteria:
            df = df[df['price'] <= criteria['budget_max']]
        
        # Filtro de tipo de vehículo
        if 'body_style' in criteria:
            df = df[df['body_styles'].str.upper() == criteria['body_style']]
        
        # Filtro de color
        if 'color' in criteria:
            df = df[df['color'].str.lower().str.contains(criteria['color'].lower(), na=False)]
        
        # Solo vehículos disponibles
        df = df[df['status'] == 'Available']
        
        return df
    
    def _calculate_relevance(self, row: pd.Series, criteria: Dict[str, Any]) -> float:
        """Calcula score de relevancia para un vehículo"""
        score = 0.0
        
        # Score base por disponibilidad
        if row['status'] == 'Available':
            score += 10.0
        
        # Bonus por características familiares
        if criteria.get('family_friendly', False):
            if row['body_styles'].upper() in ['SUV', 'SEDAN']:
                score += 5.0
            if 'safety' in str(row.get('features', '')).lower():
                score += 3.0
        
        # Bonus por economía
        if criteria.get('economical', False):
            if row['price'] < 30000:
                score += 3.0
            if 'hybrid' in str(row.get('fuel_type', '')).lower():
                score += 4.0
        
        # Penalty por alto millaje
        if row['mileage'] > 100000:
            score -= 2.0
        
        # Bonus por año reciente
        current_year = datetime.now().year
        if row['year'] >= current_year - 2:
            score += 2.0
        
        return score
    
    def reserve_vehicle(self, vin: str) -> bool:
        """Reserva un vehículo por VIN"""
        try:
            vehicle_idx = self.inventory_df[self.inventory_df['vin'] == vin].index
            
            if vehicle_idx.empty:
                print(f"❌ Vehículo con VIN {vin} no encontrado")
                return False
            
            if self.inventory_df.loc[vehicle_idx[0], 'status'] != 'Available':
                print(f"❌ Vehículo {vin} no está disponible")
                return False
            
            # Reservar vehículo
            self.inventory_df.loc[vehicle_idx[0], 'status'] = 'Reserved'
            
            # Guardar cambios
            self.inventory_df.to_csv(self.csv_path, index=False)
            print(f"✅ Vehículo {vin} reservado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error reservando vehículo {vin}: {e}")
            return False
    
    def get_vehicle_by_vin(self, vin: str) -> Optional[Vehicle]:
        """Obtiene un vehículo específico por VIN"""
        vehicle_row = self.inventory_df[self.inventory_df['vin'] == vin]
        
        if vehicle_row.empty:
            return None
        
        row = vehicle_row.iloc[0]
        return self._row_to_vehicle(row)

    def _row_to_vehicle(self, row) -> Vehicle:
        """Ultra-compact row to Vehicle converter with defensive programming"""
        # Defensive column mapping - handles both naming conventions
        body_col = 'body_styles' if 'body_styles' in row.index else 'body_style'
        return Vehicle(
            vin=row['vin'], make=row['make'], model=row['model'],
            year=int(row['year']), price=float(row['price']), mileage=int(row['mileage']),
            color=row['color'], body_style=row[body_col], fuel_type=row['fuel_type'],
            transmission=row['transmission'], status=row.get('status', 'Available'),
            safety_rating=row.get('safety_rating'), features=row.get('features')
        )
    
    def get_inventory_stats(self) -> Dict[str, Any]:
        """Ultra-compact inventory analytics with defensive programming"""
        if self.inventory_df.empty: return {"total": 0, "available": 0, "reserved": 0}

        df = self.inventory_df
        # Defensive column detection - professional pattern
        body_col = next((col for col in ['body_style', 'body_styles'] if col in df.columns), None)
        fuel_col = next((col for col in ['fuel_type', 'fuel'] if col in df.columns), 'fuel_type')

        return {
            **{status.lower(): len(df[df['status'] == status]) for status in ['Available', 'Reserved'] if 'status' in df.columns},
            'total': len(df),
            'avg_price': round(df['price'].mean() if 'price' in df.columns else 0),
            'most_popular_make': df['make'].mode().iloc[0] if 'make' in df.columns and not df.empty else 'N/A',
            'price_range': f"${df['price'].min():,.0f} - ${df['price'].max():,.0f}" if 'price' in df.columns else 'N/A',
            'body_styles': len(df[body_col].unique()) if body_col else 0,
            'fuel_efficiency': len(df[df[fuel_col].isin(['Hybrid', 'Electric', 'Híbrido', 'Eléctrico'])]) if fuel_col in df.columns else 0,
            'luxury_count': len(df[df['price'] > df['price'].quantile(0.8)]) if 'price' in df.columns else 0
        }
    
    def format_vehicles_for_agent(self, vehicles: List[Vehicle], max_display: int = 5) -> str:
        """Formatea lista de vehículos para mostrar a los agentes"""
        if not vehicles:
            return "No se encontraron vehículos que coincidan con los criterios."
        
        formatted_text = f"**Vehículos Encontrados ({len(vehicles)} coincidencias):**\n\n"
        
        for i, vehicle in enumerate(vehicles[:max_display], 1):
            formatted_text += f"""**{i}. {vehicle.year} {vehicle.make} {vehicle.model}**
• **VIN:** {vehicle.vin}
• **Precio:** ${vehicle.price:,.0f}
• **Kilometraje:** {vehicle.mileage:,} km
• **Color:** {vehicle.color}
• **Tipo:** {vehicle.body_style}
• **Combustible:** {vehicle.fuel_type}
• **Estado:** {vehicle.status}

"""
        
        if len(vehicles) > max_display:
            formatted_text += f"... y {len(vehicles) - max_display} vehículos más disponibles.\n"
        
        return formatted_text

    # ULTRA-COMPACT: Professional cache methods using advanced patterns
    def _generate_cache_key(self, query: str, max_results: int) -> str:
        return hashlib.md5(f"{query.lower().strip()}:{max_results}:{len(self.inventory_df)}".encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[List[Vehicle]]:
        if (item := self._search_cache.get(cache_key)) and time.time() - item['timestamp'] <= self._cache_ttl:
            return item['result']
        self._search_cache.pop(cache_key, None)
        return None

    def _cache_result(self, cache_key: str, result: List[Vehicle]) -> None:
        if len(self._search_cache) >= 50:
            del self._search_cache[min(self._search_cache, key=lambda k: self._search_cache[k]['timestamp'])]
        self._search_cache[cache_key] = {'result': result, 'timestamp': time.time()}

    def get_advanced_search(self, filters: Dict[str, Any]) -> List[Vehicle]:
        """Ultra-compact advanced search with professional patterns"""
        df = self.inventory_df.copy()
        conditions = [(df[k].str.contains(v, case=False, na=False) if df[k].dtype == 'object' and isinstance(v, str)
                      else df[k].between(*v) if isinstance(v, tuple) else df[k] == v)
                     for k, v in filters.items() if k in df.columns]
        return [self._row_to_vehicle(row) for _, row in df[pd.concat(conditions, axis=1).all(axis=1) if conditions else df.index].iterrows()]

    def get_cache_stats(self) -> Dict[str, Any]:
        total = self._cache_stats['hits'] + self._cache_stats['misses']
        return {**self._cache_stats, 'hit_rate_percent': round(self._cache_stats['hits']/total*100, 2) if total else 0, 'cached_entries': len(self._search_cache)}

    def clear_cache(self) -> None:
        self._search_cache.clear(); self._cache_stats = {'hits': 0, 'misses': 0}; logger.info("Cache cleared")


# Instancia global para usar en las herramientas
inventory_manager = InventoryManager()