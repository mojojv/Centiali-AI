"""
Centrally - Ingesta de Datos desde datos.gov.co
=================================================
Script especializado para ingestar datos de incidentes/accidentes de tránsito
desde la plataforma de datos abiertos de Colombia (datos.gov.co).

Autor: Alcaldía de Medellín - Centrally Team
Fecha: 2026-01-13
"""

import os
import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
from dotenv import load_dotenv
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


class DatosGovIngestor:
    """
    Ingestor especializado para datos.gov.co (Socrata Open Data API).
    
    Soporta:
    - API Socrata (formato usado por datos.gov.co)
    - Paginación automática
    - Filtros por fecha
    - Geocodificación automática si hay direcciones
    """
    
    def __init__(self, raw_data_path: str = "data_ingestion/raw"):
        """
        Inicializa el ingestor.
        
        Args:
            raw_data_path: Ruta para almacenar datos crudos
        """
        self.raw_data_path = Path(raw_data_path)
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        
        # URLs comunes de datos.gov.co (ejemplos - actualizar con URLs reales)
        self.endpoints = {
            'incidentes_transito': 'https://www.datos.gov.co/resource/[dataset-id].json',
            'accidentes_medellin': 'https://www.datos.gov.co/resource/[dataset-id].json',
        }
    
    def fetch_socrata_data(
        self,
        resource_id: str,
        limit: int = 10000,
        offset: int = 0,
        where_clause: Optional[str] = None,
        app_token: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtiene datos de una API Socrata (datos.gov.co).
        
        Args:
            resource_id: ID del recurso (ej: 'xxxx-yyyy')
            limit: Registros por página
            offset: Offset para paginación
            where_clause: Cláusula WHERE en SoQL (ej: "fecha > '2024-01-01'")
            app_token: Token de aplicación (opcional, mejora rate limits)
            
        Returns:
            Lista de registros JSON
        """
        base_url = f"https://www.datos.gov.co/resource/{resource_id}.json"
        
        params = {
            '$limit': limit,
            '$offset': offset,
        }
        
        if where_clause:
            params['$where'] = where_clause
        
        headers = {}
        if app_token:
            headers['X-App-Token'] = app_token
        
        try:
            logger.info(f"Fetching from {base_url} (limit={limit}, offset={offset})")
            response = requests.get(base_url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✓ Obtenidos {len(data)} registros")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error en API: {str(e)}")
            raise
    
    def fetch_all_pages(
        self,
        resource_id: str,
        page_size: int = 10000,
        max_records: Optional[int] = None,
        where_clause: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Obtiene todos los registros paginando automáticamente.
        
        Args:
            resource_id: ID del recurso
            page_size: Tamaño de página
            max_records: Máximo de registros (None = todos)
            where_clause: Filtro SoQL
            
        Returns:
            DataFrame con todos los registros
        """
        all_data = []
        offset = 0
        
        logger.info(f"Iniciando descarga paginada de {resource_id}")
        
        while True:
            # Fetch página
            page_data = self.fetch_socrata_data(
                resource_id,
                limit=page_size,
                offset=offset,
                where_clause=where_clause
            )
            
            if not page_data:
                logger.info("No hay más datos")
                break
            
            all_data.extend(page_data)
            offset += len(page_data)
            
            logger.info(f"Total descargado: {len(all_data)} registros")
            
            # Verificar límite
            if max_records and len(all_data) >= max_records:
                all_data = all_data[:max_records]
                logger.info(f"Alcanzado límite de {max_records} registros")
                break
            
            # Si la página no está llena, no hay más datos
            if len(page_data) < page_size:
                break
            
            # Rate limiting
            time.sleep(0.5)
        
        df = pd.DataFrame(all_data)
        logger.info(f"✓ Total final: {len(df)} registros, {len(df.columns)} columnas")
        return df
    
    def geocode_address(self, address: str, city: str = "Medellín") -> Dict[str, float]:
        """
        Geocodifica una dirección a coordenadas lat/lon usando Nominatim (OpenStreetMap).
        
        Args:
            address: Dirección a geocodificar
            city: Ciudad (default: Medellín)
            
        Returns:
            {'lat': float, 'lon': float} o None si falla
        """
        try:
            # Nominatim API (gratuito, con rate limit)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': f"{address}, {city}, Colombia",
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': 'Centrally/1.0 (centrally@medellin.gov.co)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            if results:
                return {
                    'lat': float(results[0]['lat']),
                    'lon': float(results[0]['lon'])
                }
            else:
                logger.warning(f"No se encontró geocodificación para: {address}")
                return None
                
        except Exception as e:
            logger.error(f"Error geocodificando '{address}': {str(e)}")
            return None
    
    def process_incidentes(
        self,
        df: pd.DataFrame,
        address_column: str = 'direccion',
        lat_column: Optional[str] = None,
        lon_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Procesa DataFrame de incidentes agregando geocodificación si es necesario.
        
        Args:
            df: DataFrame con datos de incidentes
            address_column: Nombre de columna con dirección
            lat_column: Columna de latitud (si ya existe)
            lon_column: Columna de longitud (si ya existe)
            
        Returns:
            DataFrame procesado con lat/lon
        """
        logger.info("Procesando incidentes...")
        
        # Si ya tiene coordenadas, validar
        if lat_column and lon_column and lat_column in df.columns and lon_column in df.columns:
            logger.info("✓ Coordenadas ya presentes en datos")
            df['latitud'] = pd.to_numeric(df[lat_column], errors='coerce')
            df['longitud'] = pd.to_numeric(df[lon_column], errors='coerce')
        
        # Si no tiene coordenadas pero tiene dirección, geocodificar
        elif address_column in df.columns:
            logger.info(f"Geocodificando direcciones desde columna '{address_column}'...")
            
            # Geocodificar solo direcciones únicas (optimización)
            unique_addresses = df[address_column].dropna().unique()
            logger.info(f"Geocodificando {len(unique_addresses)} direcciones únicas...")
            
            geocode_map = {}
            for i, address in enumerate(unique_addresses):
                if i % 10 == 0:
                    logger.info(f"Progreso: {i}/{len(unique_addresses)}")
                
                coords = self.geocode_address(address)
                geocode_map[address] = coords
                
                # Rate limiting (Nominatim permite 1 req/seg)
                time.sleep(1.1)
            
            # Aplicar geocodificación al DataFrame
            df['coords'] = df[address_column].map(geocode_map)
            df['latitud'] = df['coords'].apply(lambda x: x['lat'] if x else None)
            df['longitud'] = df['coords'].apply(lambda x: x['lon'] if x else None)
            df.drop('coords', axis=1, inplace=True)
            
            logger.info(f"✓ Geocodificados {df['latitud'].notna().sum()} de {len(df)} registros")
        
        else:
            logger.warning("No se encontraron columnas de dirección o coordenadas")
        
        return df
    
    def ingest(
        self,
        resource_id: str,
        dataset_name: str,
        where_clause: Optional[str] = None,
        geocode: bool = True,
        address_column: str = 'direccion'
    ) -> pd.DataFrame:
        """
        Ingesta completa de un dataset de datos.gov.co.
        
        Args:
            resource_id: ID del recurso Socrata
            dataset_name: Nombre para guardar el dataset
            where_clause: Filtro SoQL (opcional)
            geocode: Si geocodificar direcciones
            address_column: Columna con dirección
            
        Returns:
            DataFrame procesado
        """
        logger.info(f"=== Iniciando ingesta de {dataset_name} ===")
        
        # Fetch datos
        df = self.fetch_all_pages(resource_id, where_clause=where_clause)
        
        if df.empty:
            logger.warning("No se obtuvieron datos")
            return df
        
        # Procesar incidentes (geocodificación)
        if geocode:
            df = self.process_incidentes(df, address_column=address_column)
        
        # Guardar datos crudos
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON
        json_path = self.raw_data_path / f"{dataset_name}_{timestamp}.json"
        df.to_json(json_path, orient='records', force_ascii=False, indent=2)
        logger.info(f"✓ JSON guardado: {json_path}")
        
        # CSV
        csv_path = self.raw_data_path / f"{dataset_name}_{timestamp}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"✓ CSV guardado: {csv_path}")
        
        logger.info(f"=== Ingesta completada: {len(df)} registros ===")
        
        return df


def main():
    """Función principal de ejemplo."""
    
    ingestor = DatosGovIngestor()
    
    # EJEMPLO DE USO - Actualizar con resource_id real
    # 
    # df = ingestor.ingest(
    #     resource_id='xxxx-yyyy',  # ID del dataset en datos.gov.co
    #     dataset_name='incidentes_transito_medellin',
    #     where_clause="fecha > '2024-01-01'",  # Filtro opcional
    #     geocode=True
    # )
    
    logger.info("""
    =====================================================
    Script listo para ingestar datos de datos.gov.co
    =====================================================
    
    Para usar:
    1. Obtener el resource_id del dataset en datos.gov.co
       (aparece en la URL: datos.gov.co/resource/XXXX-YYYY)
    
    2. Ejecutar:
       ingestor = DatosGovIngestor()
       df = ingestor.ingest(
           resource_id='xxxx-yyyy',
           dataset_name='nombre_dataset',
           geocode=True
       )
    
    3. Los datos se guardarán en data_ingestion/raw/
    """)


if __name__ == "__main__":
    main()
