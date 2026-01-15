"""
Centrally - Ingesta de Datos desde APIs
=========================================
Script para ingestar datos desde APIs REST con manejo de errores y reintentos.

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


class APIIngestor:
    """Clase para ingestar datos desde APIs REST."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        raw_data_path: str = "data_ingestion/raw"
    ):
        """
        Inicializa el ingestor de API.
        
        Args:
            base_url: URL base de la API
            api_key: API key para autenticación
            raw_data_path: Ruta para datos crudos
        """
        self.base_url = base_url or os.getenv('MEDELLIN_OPEN_DATA_API', '')
        self.api_key = api_key or os.getenv('MEDELLIN_API_KEY', '')
        self.raw_data_path = Path(raw_data_path)
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        self.metadata: Dict[str, Any] = {}
        
    def fetch_data(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Obtiene datos de un endpoint con reintentos.
        
        Args:
            endpoint: Endpoint de la API
            params: Parámetros de la consulta
            max_retries: Número máximo de reintentos
            timeout: Timeout en segundos
            
        Returns:
            Respuesta JSON de la API
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Petición a {url} (intento {attempt + 1}/{max_retries})")
                
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )
                response.raise_for_status()
                
                logger.info(f"✓ Respuesta exitosa (status {response.status_code})")
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento {attempt + 1} falló: {str(e)}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"✗ Todos los intentos fallaron")
                    raise
    
    def ingest(
        self,
        endpoint: str,
        dataset_name: str,
        params: Optional[Dict[str, Any]] = None,
        save_json: bool = True,
        save_csv: bool = True
    ) -> pd.DataFrame:
        """
        Ingesta datos de API y los guarda en raw.
        
        Args:
            endpoint: Endpoint de la API
            dataset_name: Nombre del dataset
            params: Parámetros de consulta
            save_json: Guardar respuesta JSON cruda
            save_csv: Guardar como CSV
            
        Returns:
            DataFrame con los datos
        """
        try:
            logger.info(f"Iniciando ingesta desde API: {endpoint}")
            
            # Obtener datos
            data = self.fetch_data(endpoint, params)
            
            # Guardar JSON crudo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if save_json:
                json_path = self.raw_data_path / f"{dataset_name}_{timestamp}.json"
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"✓ JSON guardado en: {json_path}")
            
            # Convertir a DataFrame
            # Ajustar según estructura de respuesta de la API
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'results' in data:
                df = pd.DataFrame(data['results'])
            elif isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
            else:
                df = pd.DataFrame([data])
            
            # Guardar CSV
            if save_csv:
                csv_path = self.raw_data_path / f"{dataset_name}_{timestamp}.csv"
                df.to_csv(csv_path, index=False)
                logger.info(f"✓ CSV guardado en: {csv_path}")
            
            # Metadata
            self.metadata = {
                'dataset_name': dataset_name,
                'source_endpoint': endpoint,
                'ingestion_timestamp': datetime.now().isoformat(),
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist()
            }
            
            logger.info(f"✓ Ingesta completada: {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"✗ Error en ingesta: {str(e)}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadata de última ingesta."""
        return self.metadata


def main():
    """Función principal de ejemplo."""
    
    # Ejemplo de uso
    ingestor = APIIngestor()
    
    # Ejemplo: Datos abiertos de Medellín
    # df = ingestor.ingest(
    #     endpoint='resource/dataset-id.json',
    #     dataset_name='trafico_tiempo_real',
    #     params={'$limit': 1000}
    # )
    
    logger.info("Script de ingesta API listo. Configurar endpoint para usar.")


if __name__ == "__main__":
    main()
