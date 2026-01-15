"""
Centrally - Ingesta de Datos desde MEData Medellín
====================================================
Script especializado para ingestar datos del portal de datos abiertos
de Medellín (medata.gov.co).

Autor: Alcaldía de Medellín - Centrally Team
Fecha: 2026-01-13
"""

import os
import sys
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_ingestion.scripts.ingest_datos_gov import DatosGovIngestor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MEDataIngestor(DatosGovIngestor):
    """
    Ingestor especializado para el portal MEData de Medellín.
    
    Hereda de DatosGovIngestor ya que MEData usa la misma tecnología
    (Socrata Open Data Platform).
    """
    
    def __init__(self, raw_data_path: str = "data_ingestion/raw"):
        """Inicializa el ingestor para MEData."""
        super().__init__(raw_data_path)
        
        # Actualizar base URL para MEData
        self.base_url = "https://medata.gov.co"
        
        # Catálogo de datasets conocidos de MEData (actualizar con IDs reales)
        self.datasets_conocidos = {
            # TRANSPORTE Y MOVILIDAD
            'incidentes_transito': {
                'resource_id': 'PENDIENTE',  # Actualizar con ID real
                'nombre': 'Incidentes de Tránsito',
                'descripcion': 'Registro de incidentes de tránsito en Medellín',
                'columnas_esperadas': ['fecha', 'direccion', 'tipo', 'gravedad'],
                'columna_direccion': 'direccion',
                'columna_lat': 'latitud',
                'columna_lon': 'longitud'
            },
            'accidentes_viales': {
                'resource_id': 'PENDIENTE',
                'nombre': 'Accidentes Viales',
                'descripcion': 'Accidentes de tránsito registrados',
                'columnas_esperadas': ['fecha', 'ubicacion', 'tipo_accidente'],
                'columna_direccion': 'ubicacion',
            },
            'volumen_vehicular': {
                'resource_id': 'PENDIENTE',
                'nombre': 'Volumen Vehicular',
                'descripcion': 'Mediciones de volumen de tráfico',
                'columnas_esperadas': ['fecha', 'hora', 'contador', 'volumen'],
            },
            'velocidad_promedio': {
                'resource_id': 'PENDIENTE',
                'nombre': 'Velocidad Promedio',
                'descripcion': 'Velocidades promedio en vías principales',
                'columnas_esperadas': ['fecha', 'corredor', 'velocidad'],
            }
        }
    
    def listar_datasets_disponibles(self):
        """Lista los datasets conocidos de MEData."""
        logger.info("=" * 60)
        logger.info("DATASETS CONOCIDOS DE MEDATA MEDELLÍN")
        logger.info("=" * 60)
        
        for key, info in self.datasets_conocidos.items():
            logger.info(f"\n📊 {info['nombre']}")
            logger.info(f"   Clave: {key}")
            logger.info(f"   Resource ID: {info['resource_id']}")
            logger.info(f"   Descripción: {info['descripcion']}")
            
            if info['resource_id'] == 'PENDIENTE':
                logger.info(f"   ⚠️  PENDIENTE: Necesita configurar resource_id")
        
        logger.info("\n" + "=" * 60)
    
    def ingest_medata_dataset(
        self,
        dataset_key: str,
        fecha_inicio: str = None,
        geocode: bool = True,
        max_records: int = None
    ):
        """
        Ingesta un dataset predefinido de MEData.
        
        Args:
            dataset_key: Clave del dataset (ej: 'incidentes_transito')
            fecha_inicio: Fecha inicial para filtro (formato: 'YYYY-MM-DD')
            geocode: Si geocodificar direcciones
            max_records: Máximo de registros (None = todos)
            
        Returns:
            DataFrame con los datos
        """
        if dataset_key not in self.datasets_conocidos:
            raise ValueError(
                f"Dataset '{dataset_key}' no encontrado. "
                f"Disponibles: {list(self.datasets_conocidos.keys())}"
            )
        
        config = self.datasets_conocidos[dataset_key]
        
        if config['resource_id'] == 'PENDIENTE':
            logger.error(f"❌ Dataset '{dataset_key}' no tiene resource_id configurado")
            logger.info("\n📝 PASOS PARA CONFIGURAR:")
            logger.info("1. Visitar: https://medata.gov.co/search/?theme=Transporte")
            logger.info("2. Buscar el dataset deseado")
            logger.info("3. En la página del dataset, encontrar el resource ID")
            logger.info("4. Actualizar en ingest_medata.py el campo 'resource_id'")
            return None
        
        logger.info(f"🚀 Iniciando ingesta de: {config['nombre']}")
        
        # Construir filtro de fecha si se proporciona
        where_clause = None
        if fecha_inicio:
            where_clause = f"fecha >= '{fecha_inicio}'"
        
        # Ingestar usando el método heredado
        df = self.fetch_all_pages(
            resource_id=config['resource_id'],
            where_clause=where_clause,
            max_records=max_records
        )
        
        if df.empty:
            logger.warning("No se obtuvieron datos")
            return df
        
        # Procesar con geocodificación si se requiere
        if geocode and 'columna_direccion' in config:
            df = self.process_incidentes(
                df,
                address_column=config['columna_direccion'],
                lat_column=config.get('columna_lat'),
                lon_column=config.get('columna_lon')
            )
        
        # Guardar
        import pandas as pd
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # CSV
        csv_path = self.raw_data_path / f"medata_{dataset_key}_{timestamp}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"✓ Guardado: {csv_path}")
        
        # JSON
        json_path = self.raw_data_path / f"medata_{dataset_key}_{timestamp}.json"
        df.to_json(json_path, orient='records', force_ascii=False, indent=2)
        logger.info(f"✓ Guardado: {json_path}")
        
        logger.info(f"✅ Ingesta completada: {len(df)} registros")
        
        return df
    
    def configurar_dataset(
        self,
        dataset_key: str,
        resource_id: str,
        nombre: str = None,
        descripcion: str = None,
        columna_direccion: str = 'direccion',
        columna_lat: str = None,
        columna_lon: str = None
    ):
        """
        Configura o actualiza un dataset en el catálogo.
        
        Args:
            dataset_key: Clave para identificar el dataset
            resource_id: Resource ID de MEData (formato: xxxx-yyyy)
            nombre: Nombre descriptivo
            descripcion: Descripción del dataset
            columna_direccion: Nombre de columna con dirección
            columna_lat: Nombre de columna con latitud (si existe)
            columna_lon: Nombre de columna con longitud (si existe)
        """
        config = {
            'resource_id': resource_id,
            'nombre': nombre or dataset_key,
            'descripcion': descripcion or '',
            'columna_direccion': columna_direccion,
        }
        
        if columna_lat:
            config['columna_lat'] = columna_lat
        if columna_lon:
            config['columna_lon'] = columna_lon
        
        self.datasets_conocidos[dataset_key] = config
        
        logger.info(f"✓ Dataset '{dataset_key}' configurado con resource_id: {resource_id}")


def main():
    """Función principal con ejemplos de uso."""
    
    logger.info("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║          MEDATA MEDELLÍN - INGESTA DE DATOS                   ║
    ║          Portal de Datos Abiertos de Medellín                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Crear ingestor
    ingestor = MEDataIngestor()
    
    # Listar datasets conocidos
    ingestor.listar_datasets_disponibles()
    
    logger.info("\n📖 INSTRUCCIONES DE USO:")
    logger.info("""
    1. ENCONTRAR RESOURCE ID:
       - Visitar: https://medata.gov.co/search/?theme=Transporte
       - Seleccionar dataset deseado
       - En la página del dataset, buscar botón "API"
       - El resource ID está en formato: xxxx-yyyy
    
    2. CONFIGURAR DATASET:
       
       ingestor = MEDataIngestor()
       ingestor.configurar_dataset(
           dataset_key='incidentes_transito',
           resource_id='abcd-1234',  # ← Tu resource ID aquí
           nombre='Incidentes de Tránsito',
           columna_direccion='direccion'
       )
    
    3. INGESTAR DATOS:
       
       df = ingestor.ingest_medata_dataset(
           dataset_key='incidentes_transito',
           fecha_inicio='2024-01-01',
           geocode=True
       )
    
    4. ALTERNATIVAMENTE (si conoces el resource ID):
       
       df = ingestor.fetch_all_pages('xxxx-yyyy')
       df = ingestor.process_incidentes(df, address_column='direccion')
    """)
    
    logger.info("\n💡 EJEMPLO COMPLETO:")
    logger.info("""
    # === Ejemplo ===
    from data_ingestion.scripts.ingest_medata import MEDataIngestor
    
    ingestor = MEDataIngestor()
    
    # Configurar (solo primera vez)
    ingestor.configurar_dataset(
        dataset_key='incidentes_2024',
        resource_id='gt2j-8ykr',  # Ejemplo
        nombre='Incidentes de Tránsito 2024',
        columna_direccion='ubicacion',
        columna_lat='latitud',
        columna_lon='longitud'
    )
    
    # Ingestar
    df = ingestor.ingest_medata_dataset(
        dataset_key='incidentes_2024',
        fecha_inicio='2024-01-01',
        geocode=True
    )
    
    print(f"Total registros: {len(df)}")
    print(df.head())
    # ===============
    """)
    
    logger.info("\n" + "=" * 70)
    logger.info("Listo para ingestar datos de MEData Medellín! 🚀")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
