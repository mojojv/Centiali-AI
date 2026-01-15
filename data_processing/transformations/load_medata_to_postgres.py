"""
Script de Carga de Datos MEData a PostgreSQL
==============================================
Carga datos ingestados desde MEData a la base de datos PostgreSQL.
"""

from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_to_fact_incidentes(csv_path: str):
    """
    Carga incidentes desde CSV de MEDataa PostgreSQL.
    
    Args:
        csv_path: Ruta al archivo CSV
    """
    
    # Conectar
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL no configurada en .env")
    
    engine = create_engine(db_url)
    
    # Leer CSV
    logger.info(f"Leyendo {csv_path}...")
    df = pd.read_csv(csv_path)
    logger.info(f"✓ {len(df)} registros cargados del CSV")
    
    # Mostrar columnas disponibles
    logger.info(f"Columnas disponibles: {df.columns.tolist()}")
    
    # Transformar al esquema esperado
    # Mapeo flexible (ajustar según columnas reales del dataset)
    df_transformed = pd.DataFrame()
    
    # Intentar mapear columnas comunes
    if 'fecha' in df.columns:
        df_transformed['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    elif 'fecha_hora' in df.columns:
        df_transformed['fecha'] = pd.to_datetime(df['fecha_hora'], errors='coerce')
    
    # Tipo de incidente
    if 'tipo' in df.columns:
        df_transformed['tipo_incidente'] = df['tipo']
    elif 'tipo_incidente' in df.columns:
        df_transformed['tipo_incidente'] = df['tipo_incidente']
    else:
        df_transformed['tipo_incidente'] = 'Accidente'  # Default
    
    # Gravedad
    if 'gravedad' in df.columns:
        df_transformed['gravedad'] = df['gravedad']
    elif 'severidad' in df.columns:
        df_transformed['gravedad'] = df['severidad']
    else:
        df_transformed['gravedad'] = 'Moderado'  # Default
    
    # Dirección
    if 'direccion' in df.columns:
        df_transformed['direccion'] = df['direccion']
    elif 'ubicacion' in df.columns:
        df_transformed['direccion'] = df['ubicacion']
    else:
        df_transformed['direccion'] = ''
    
    # Coordenadas
    if 'latitud' in df.columns:
        df_transformed['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
    if 'longitud' in df.columns:
        df_transformed['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
    
    # Descripción
    if 'descripcion' in df.columns:
        df_transformed['descripcion'] = df['descripcion']
    elif 'detalle' in df.columns:
        df_transformed['descripcion'] = df['detalle']
    else:
        df_transformed['descripcion'] = ''
    
    # Fuente
    df_transformed['fuente_datos'] = 'MEData Medellín'
    
    # Filtrar registros sin coordenadas
    initial_count = len(df_transformed)
    df_transformed = df_transformed.dropna(subset=['latitud', 'longitud'])
    filtered_count = initial_count - len(df_transformed)
    
    if filtered_count > 0:
        logger.warning(f"⚠️  {filtered_count} registros sin coordenadas (eliminados)")
    
    logger.info(f"✓ {len(df_transformed)} registros con coordenadas válidas")
    
    # Crear tabla staging si no existe
    with engine.connect() as conn:
        logger.info("Creando tabla staging si no existe...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS centrally.incidentes_staging (
                id SERIAL PRIMARY KEY,
                fecha TIMESTAMP,
                tipo_incidente VARCHAR(100),
                gravedad VARCHAR(50),
                direccion VARCHAR(500),
                latitud DECIMAL(10,7),
                longitud DECIMAL(10,7),
                descripcion TEXT,
                fuente_datos VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        logger.info("✓ Tabla staging lista")
    
    # Insertar datos
    logger.info("Insertando datos en PostgreSQL...")
    df_transformed.to_sql(
        'incidentes_staging',
        engine,
        schema='centrally',
        if_exists='append',
        index=False
    )
    
    logger.info(f"✅ Carga completada: {len(df_transformed)} registros en incidentes_staging")
    
    # Estadísticas
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT fecha::date) as dias_unicos,
                MIN(fecha) as fecha_min,
                MAX(fecha) as fecha_max
            FROM centrally.incidentes_staging
        """))
        stats = result.fetchone()
        
        logger.info("\n📊 ESTADÍSTICAS DE LA BASE DE DATOS:")
        logger.info(f"  Total registros: {stats[0]}")
        logger.info(f"  Días únicos: {stats[1]}")
        logger.info(f"  Fecha mínima: {stats[2]}")
        logger.info(f"  Fecha máxima: {stats[3]}")
    
    return df_transformed


def main():
    """Función principal."""
    import sys
    
    if len(sys.argv) < 2:
        logger.error("❌ Falta especificar archivo CSV")
        logger.info("\n📖 USO:")
        logger.info("  python load_medata_to_postgres.py <ruta_al_csv>\n")
        logger.info("EJEMPLO:")
        logger.info("  python data_processing/transformations/load_medata_to_postgres.py \\")
        logger.info("         data_ingestion/raw/medata_incidentes_transito_2024_20260113_221530.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    # Verificar que existe
    if not Path(csv_path).exists():
        logger.error(f"❌ Archivo no encontrado: {csv_path}")
        sys.exit(1)
    
    # Cargar
    load_to_fact_incidentes(csv_path)


if __name__ == "__main__":
    main()
