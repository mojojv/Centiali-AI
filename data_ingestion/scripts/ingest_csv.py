"""
Centrally - Ingesta de Datos desde CSV
=========================================
Script para ingestar datos desde archivos CSV con validación y metadata.

Autor: Alcaldía de Medellín - Centrally Team
Fecha: 2026-01-13
"""

import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


class CSVIngestor:
    """Clase para ingestar datos desde archivos CSV."""
    
    def __init__(self, raw_data_path: str = "data_ingestion/raw"):
        """
        Inicializa el ingestor de CSV.
        
        Args:
            raw_data_path: Ruta donde se almacenarán los datos crudos
        """
        self.raw_data_path = Path(raw_data_path)
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        self.metadata: Dict[str, Any] = {}
        
    def ingest(
        self,
        file_path: str,
        dataset_name: str,
        encoding: str = 'utf-8',
        separator: str = ',',
        **kwargs
    ) -> pd.DataFrame:
        """
        Ingesta un archivo CSV y guarda metadata.
        
        Args:
            file_path: Ruta al archivo CSV
            dataset_name: Nombre identificador del dataset
            encoding: Codificación del archivo
            separator: Separador de columnas
            **kwargs: Argumentos adicionales para pd.read_csv
            
        Returns:
            DataFrame con los datos ingestados
        """
        try:
            logger.info(f"Iniciando ingesta de {file_path}")
            
            # Leer CSV
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                sep=separator,
                **kwargs
            )
            
            # Generar metadata
            self.metadata = {
                'dataset_name': dataset_name,
                'source_file': file_path,
                'ingestion_timestamp': datetime.now().isoformat(),
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'dtypes': df.dtypes.astype(str).to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
            
            # Guardar copia en raw
            output_path = self.raw_data_path / f"{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(output_path, index=False)
            
            logger.info(f"✓ Ingesta completada: {len(df)} filas, {len(df.columns)} columnas")
            logger.info(f"✓ Datos guardados en: {output_path}")
            
            return df
            
        except Exception as e:
            logger.error(f"✗ Error en ingesta: {str(e)}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna la metadata de la última ingesta."""
        return self.metadata


def main():
    """Función principal de ejemplo."""
    
    # Ejemplo de uso
    ingestor = CSVIngestor()
    
    # Ejemplo: Ingestar datos de tráfico (reemplazar con ruta real)
    # df = ingestor.ingest(
    #     file_path='path/to/trafico_medellin.csv',
    #     dataset_name='trafico_urbano',
    #     encoding='utf-8',
    #     separator=','
    # )
    
    # metadata = ingestor.get_metadata()
    # print(f"Metadata: {metadata}")
    
    logger.info("Script de ingesta CSV listo. Descomentar ejemplo para usar.")


if __name__ == "__main__":
    main()
