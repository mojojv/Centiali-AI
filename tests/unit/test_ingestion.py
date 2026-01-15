"""
Centrally - Tests Unitarios para Ingesta
==========================================
Tests para validar la capa de ingesta de datos.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Agregar ruta al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_ingestion.scripts.ingest_csv import CSVIngestor
from data_ingestion.validators import DataValidator


class TestCSVIngestor:
    """Tests para CSVIngestor."""
    
    def test_ingestor_initialization(self):
        """Test de inicialización del ingestor."""
        ingestor = CSVIngestor()
        assert ingestor.raw_data_path.exists()
    
    def test_metadata_generation(self):
        """Test de generación de metadata."""
        ingestor = CSVIngestor()
        
        # Crear DataFrame de prueba
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10, 20, 30]
        })
        
        # Guardar temporalmente
        temp_path = Path('temp_test.csv')
        df.to_csv(temp_path, index=False)
        
        try:
            result = ingestor.ingest(str(temp_path), 'test_dataset')
            metadata = ingestor.get_metadata()
            
            assert metadata['dataset_name'] == 'test_dataset'
            assert metadata['rows'] == 3
            assert metadata['columns'] == 2
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestDataValidator:
    """Tests para validadores de datos."""
    
    def test_trafico_schema_valid(self):
        """Test de validación con datos válidos de tráfico."""
        df = pd.DataFrame({
            'id': [1, 2],
            'fecha': ['2026-01-13', '2026-01-13'],
            'zona_id': ['Z001', 'Z002'],
            'velocidad_promedio': [45.5, 50.0],
            'volumen_vehicular': [100, 150],
            'nivel_congestion': ['bajo', 'medio']
        })
        
        # Debe pasar sin errores
        validated = DataValidator.validate(df, 'trafico')
        assert len(validated) == 2
    
    def test_trafico_schema_invalid_speed(self):
        """Test de validación con velocidad inválida."""
        df = pd.DataFrame({
            'id': [1],
            'fecha': ['2026-01-13'],
            'zona_id': ['Z001'],
            'velocidad_promedio': [250.0],  # Inválido (> 200)
            'volumen_vehicular': [100],
            'nivel_congestion': ['bajo']
        })
        
        # Debe fallar
        with pytest.raises(Exception):
            DataValidator.validate(df, 'trafico', lazy=False)
    
    def test_get_schema_info(self):
        """Test de información de esquema."""
        info = DataValidator.get_schema_info('trafico')
        
        assert 'columns' in info
        assert 'required_columns' in info
        assert 'id' in info['required_columns']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
