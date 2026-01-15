"""
Centrally - Pipeline de Transformación ETL
============================================
Script principal para transformación y limpieza de datos.

Autor: Alcaldía de Medellín - Centrally Team
Fecha: 2026-01-13
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataTransformer:
    """Clase para transformación y limpieza de datos."""
    
    def __init__(self):
        """Inicializa el transformador."""
        self.transformation_log = []
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpieza general de datos.
        
        Args:
            df: DataFrame a limpiar
            
        Returns:
            DataFrame limpio
        """
        logger.info("Iniciando limpieza de datos...")
        
        initial_rows = len(df)
        
        # Eliminar duplicados
        df = df.drop_duplicates()
        duplicates_removed = initial_rows - len(df)
        
        if duplicates_removed > 0:
            logger.info(f"✓ Eliminados {duplicates_removed} duplicados")
        
        # Eliminar filas completamente vacías
        df = df.dropna(how='all')
        
        # Normalizar nombres de columnas
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('[^a-z0-9_]', '', regex=True)
        
        logger.info(f"✓ Limpieza completada: {len(df)} filas restantes")
        
        self.transformation_log.append({
            'step': 'clean_data',
            'timestamp': datetime.now().isoformat(),
            'rows_before': initial_rows,
            'rows_after': len(df)
        })
        
        return df
    
    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: Dict[str, str] = None
    ) -> pd.DataFrame:
        """
        Manejo de valores faltantes.
        
        Args:
            df: DataFrame
            strategy: Diccionario {columna: estrategia}
                     Estrategias: 'drop', 'mean', 'median', 'mode', 'ffill', 'bfill', valor específico
        
        Returns:
            DataFrame con valores faltantes manejados
        """
        logger.info("Manejando valores faltantes...")
        
        if strategy is None:
            strategy = {}
        
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            
            if missing_count == 0:
                continue
            
            col_strategy = strategy.get(col, 'drop')
            
            if col_strategy == 'drop':
                df = df.dropna(subset=[col])
                logger.info(f"  {col}: eliminadas {missing_count} filas")
            
            elif col_strategy == 'mean':
                df[col].fillna(df[col].mean(), inplace=True)
                logger.info(f"  {col}: rellenado con media")
            
            elif col_strategy == 'median':
                df[col].fillna(df[col].median(), inplace=True)
                logger.info(f"  {col}: rellenado con mediana")
            
            elif col_strategy == 'mode':
                df[col].fillna(df[col].mode()[0], inplace=True)
                logger.info(f"  {col}: rellenado con moda")
            
            elif col_strategy in ['ffill', 'bfill']:
                df[col].fillna(method=col_strategy, inplace=True)
                logger.info(f"  {col}: rellenado con {col_strategy}")
            
            else:
                df[col].fillna(col_strategy, inplace=True)
                logger.info(f"  {col}: rellenado con valor '{col_strategy}'")
        
        logger.info("✓ Valores faltantes manejados")
        return df
    
    def normalize_datetime(
        self,
        df: pd.DataFrame,
        date_columns: list
    ) -> pd.DataFrame:
        """
        Normaliza columnas de fecha/hora.
        
        Args:
            df: DataFrame
            date_columns: Lista de columnas de fecha
            
        Returns:
            DataFrame con fechas normalizadas
        """
        logger.info("Normalizando fechas...")
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                logger.info(f"  {col}: convertido a datetime")
        
        logger.info("✓ Fechas normalizadas")
        return df
    
    def create_time_features(
        self,
        df: pd.DataFrame,
        datetime_col: str
    ) -> pd.DataFrame:
        """
        Crea features temporales a partir de una columna datetime.
        
        Args:
            df: DataFrame
            datetime_col: Nombre de columna datetime
            
        Returns:
            DataFrame con features temporales
        """
        logger.info(f"Creando features temporales desde '{datetime_col}'...")
        
        if datetime_col not in df.columns:
            logger.warning(f"Columna '{datetime_col}' no encontrada")
            return df
        
        # Asegurar que es datetime
        df[datetime_col] = pd.to_datetime(df[datetime_col])
        
        # Extraer componentes
        df['fecha'] = df[datetime_col].dt.date
        df['hora'] = df[datetime_col].dt.hour
        df['dia_semana'] = df[datetime_col].dt.day_name()
        df['dia_mes'] = df[datetime_col].dt.day
        df['mes'] = df[datetime_col].dt.month
        df['mes_nombre'] = df[datetime_col].dt.month_name()
        df['trimestre'] = df[datetime_col].dt.quarter
        df['anio'] = df[datetime_col].dt.year
        df['es_fin_semana'] = df[datetime_col].dt.dayofweek.isin([5, 6])
        
        logger.info("✓ Features temporales creados")
        return df
    
    def categorize_numeric(
        self,
        df: pd.DataFrame,
        column: str,
        bins: list,
        labels: list,
        new_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Categoriza una columna numérica.
        
        Args:
            df: DataFrame
            column: Columna a categorizar
            bins: Límites de las categorías
            labels: Etiquetas de categorías
            new_column: Nombre de nueva columna (opcional)
            
        Returns:
            DataFrame con columna categorizada
        """
        target_col = new_column or f"{column}_categoria"
        
        df[target_col] = pd.cut(
            df[column],
            bins=bins,
            labels=labels,
            include_lowest=True
        )
        
        logger.info(f"✓ Categorizada columna '{column}' -> '{target_col}'")
        return df
    
    def get_transformation_log(self) -> list:
        """Retorna el log de transformaciones."""
        return self.transformation_log


def main():
    """Función de ejemplo."""
    
    # Ejemplo de uso
    transformer = DataTransformer()
    
    # DataFrame de ejemplo
    df = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'fecha_hora': ['2026-01-13 08:00', '2026-01-13 09:00', None, '2026-01-13 11:00', '2026-01-13 12:00'],
        'velocidad': [45.5, None, 60.0, 35.0, 50.0],
        'volumen': [100, 150, 200, None, 120]
    })
    
    # Pipeline de transformación
    df = transformer.clean_data(df)
    df = transformer.normalize_datetime(df, ['fecha_hora'])
    df = transformer.handle_missing_values(
        df,
        strategy={'velocidad': 'mean', 'volumen': 'median'}
    )
    df = transformer.create_time_features(df, 'fecha_hora')
    
    print(df.head())
    print(f"\nLog de transformaciones: {transformer.get_transformation_log()}")


if __name__ == "__main__":
    main()
