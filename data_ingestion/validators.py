"""
Centrally - Validadores de Datos
==================================
Validación de esquemas de datos usando Pandera.

Autor: Alcaldía de Medellín - Centrally Team
Fecha: 2026-01-13
"""

import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =====================================
# Esquema: Datos de Tráfico
# =====================================
trafico_schema = DataFrameSchema(
    {
        "id": Column(pa.Int, nullable=False, unique=True),
        "fecha": Column(pa.DateTime, nullable=False),
        "zona_id": Column(pa.String, nullable=False),
        "velocidad_promedio": Column(
            pa.Float,
            nullable=True,
            checks=[Check.greater_than_or_equal_to(0), Check.less_than_or_equal_to(200)]
        ),
        "volumen_vehicular": Column(
            pa.Int,
            nullable=True,
            checks=[Check.greater_than_or_equal_to(0)]
        ),
        "nivel_congestion": Column(
            pa.String,
            nullable=True,
            checks=[Check.isin(['bajo', 'medio', 'alto', 'critico'])]
        )
    },
    strict=False,
    coerce=True
)


# =====================================
# Esquema: Datos Geoespaciales
# =====================================
geo_schema = DataFrameSchema(
    {
        "id": Column(pa.Int, nullable=False, unique=True),
        "nombre": Column(pa.String, nullable=False),
        "latitud": Column(
            pa.Float,
            nullable=False,
            checks=[Check.greater_than_or_equal_to(-90), Check.less_than_or_equal_to(90)]
        ),
        "longitud": Column(
            pa.Float,
            nullable=False,
            checks=[Check.greater_than_or_equal_to(-180), Check.less_than_or_equal_to(180)]
        ),
        "tipo_zona": Column(pa.String, nullable=True)
    },
    strict=False,
    coerce=True
)


# =====================================
# Esquema: Incidentes de Tránsito
# =====================================
incidentes_schema = DataFrameSchema(
    {
        "id": Column(pa.Int, nullable=False, unique=True),
        "fecha_hora": Column(pa.DateTime, nullable=False),
        "tipo_incidente": Column(
            pa.String,
            nullable=False,
            checks=[Check.isin(['accidente', 'congestion', 'obra', 'evento', 'otro'])]
        ),
        "gravedad": Column(
            pa.String,
            checks=[Check.isin(['leve', 'moderado', 'grave'])]
        ),
        "descripcion": Column(pa.String, nullable=True),
        "latitud": Column(pa.Float, nullable=True),
        "longitud": Column(pa.Float, nullable=True)
    },
    strict=False,
    coerce=True
)


class DataValidator:
    """Clase para validar DataFrames contra esquemas predefinidos."""
    
    SCHEMAS = {
        'trafico': trafico_schema,
        'geo': geo_schema,
        'incidentes': incidentes_schema
    }
    
    @classmethod
    def validate(
        cls,
        df: pd.DataFrame,
        schema_name: str,
        lazy: bool = True
    ) -> pd.DataFrame:
        """
        Valida un DataFrame contra un esquema.
        
        Args:
            df: DataFrame a validar
            schema_name: Nombre del esquema ('trafico', 'geo', 'incidentes')
            lazy: Si True, retorna todos los errores. Si False, falla en el primero.
            
        Returns:
            DataFrame validado (puede tener coerción de tipos)
            
        Raises:
            pa.errors.SchemaError: Si la validación falla
        """
        if schema_name not in cls.SCHEMAS:
            raise ValueError(
                f"Esquema '{schema_name}' no encontrado. "
                f"Disponibles: {list(cls.SCHEMAS.keys())}"
            )
        
        schema = cls.SCHEMAS[schema_name]
        
        try:
            logger.info(f"Validando DataFrame con esquema '{schema_name}'...")
            validated_df = schema.validate(df, lazy=lazy)
            logger.info(f"✓ Validación exitosa: {len(df)} filas")
            return validated_df
            
        except pa.errors.SchemaError as e:
            logger.error(f"✗ Validación fallida:\n{e}")
            raise
    
    @classmethod
    def get_schema_info(cls, schema_name: str) -> Dict[str, Any]:
        """Retorna información sobre un esquema."""
        if schema_name not in cls.SCHEMAS:
            raise ValueError(f"Esquema '{schema_name}' no encontrado")
        
        schema = cls.SCHEMAS[schema_name]
        return {
            'columns': list(schema.columns.keys()),
            'required_columns': [
                col for col, spec in schema.columns.items()
                if not spec.nullable
            ]
        }


def main():
    """Función de ejemplo."""
    
    # Ejemplo de validación
    df_test = pd.DataFrame({
        'id': [1, 2, 3],
        'fecha': ['2026-01-13', '2026-01-13', '2026-01-13'],
        'zona_id': ['Z001', 'Z002', 'Z003'],
        'velocidad_promedio': [45.5, 30.2, 60.8],
        'volumen_vehicular': [150, 200, 100],
        'nivel_congestion': ['bajo', 'medio', 'bajo']
    })
    
    try:
        validated = DataValidator.validate(df_test, 'trafico')
        print("✓ Datos válidos")
        print(validated.dtypes)
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    main()
