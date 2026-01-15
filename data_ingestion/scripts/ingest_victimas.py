"""
Centrally - Ingesta de Víctimas de Incidentes (CSV Local)
===========================================================
Procesa el archivo 'Mede_Victimas_inci.csv' proporcionado por el usuario.

Autor: Alcaldía de Medellín - Centrally Team
Fecha: 2026-01-13
"""

import pandas as pd
import numpy as np
from pathlib import Path
# from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def clean_coordinate(val):
    """Limpia y convierte coordenadas (maneja gms o decimales con coma)."""
    if pd.isna(val) or val == '':
        return None
    
    val_str = str(val).replace(',', '.').strip()
    try:
        return float(val_str)
    except ValueError:
        return None

def ingest_victimas_csv(csv_path: str):
    """
    Ingesta el archivo de víctimas, limpia datos y carga a DB.
    """
    logger.info(f"Procesando archivo: {csv_path}")
    
    # Leer CSV
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        logger.info("UTF-8 falló, intentando latin-1...")
        df = pd.read_csv(csv_path, encoding='latin-1')
    
    logger.info(f"Registros originales: {len(df)}")
    
    # 1. Limpieza de Coordenadas
    logger.info("Limpiando coordenadas...")
    df['latitud_clean'] = df['Latitud'].apply(clean_coordinate)
    df['longitud_clean'] = df['Longitud'].apply(clean_coordinate)
    
    # Filtrar coordenadas inválidas (fuera de rango Medellín aprox)
    # Medellín ~ Lat 6.1-6.4, Lon -75.7--75.4
    mask_valid_coords = (
        (df['latitud_clean'].between(6.0, 6.5)) & 
        (df['longitud_clean'].between(-75.8, -75.3))
    )
    
    df_valid = df[mask_valid_coords].copy()
    logger.info(f"Registros con coordenadas válidas: {len(df_valid)}")
    
    # 2. Estandarización de Fechas
    logger.info("Procesando fechas...")
    df_valid['fecha_dt'] = pd.to_datetime(df_valid['Fecha_incidente'], errors='coerce')
    
    # 3. Mapeo a Esquema Centrally
    df_final = pd.DataFrame({
        'fecha': df_valid['fecha_dt'],
        'tipo_incidente': df_valid['Clase_incidente'],
        'gravedad': df_valid['Gravedad_victima'],
        'direccion': df_valid['Direccion_incidente'],
        'latitud': df_valid['latitud_clean'],
        'longitud': df_valid['longitud_clean'],
        'descripcion': (
            'Barrio: ' + df_valid['Barrio'].fillna('') + 
            ' | Comuna: ' + df_valid['Comuna'].fillna('') +
            ' | Condición: ' + df_valid['Condicion'].fillna('')
        ),
        'fuente_datos': 'CSV: Mede_Victimas_inci'
    })
    
    # 4. Guardar procesado (para uso rápido en dashboard)
    processed_path = Path("data_ingestion/raw/victimas_procesado.csv")
    df_final.to_csv(processed_path, index=False)
    logger.info(f"✓ Archivo procesado guardado en: {processed_path}")
    
    # 5. Cargar a PostgreSQL (Tabla Staging)
    # try:
    #     db_url = os.getenv('DATABASE_URL')
    #     engine = create_engine(db_url)
        
    #     with engine.connect() as conn:
    #         conn.execute(text("DELETE FROM centrally.incidentes_staging WHERE fuente_datos LIKE 'CSV:%'"))
    #         conn.commit()
            
    #     df_final.to_sql(
    #         'incidentes_staging',
    #         engine,
    #         schema='centrally',
    #         if_exists='append',
    #         index=False
    #     )
    #     logger.info(f"✓ Cargados {len(df_final)} registros a DB")
        
    # except Exception as e:
    #     logger.error(f"Error cargando a DB (verificar conexión): {e}")
    #     logger.info("Se continuará usando solo el archivo CSV procesado.")
    
    return df_final

if __name__ == "__main__":
    csv_file = "Mede_Victimas_inci.csv"
    if Path(csv_file).exists():
        ingest_victimas_csv(csv_file)
    else:
        logger.error(f"Archivo no encontrado: {csv_file}")
