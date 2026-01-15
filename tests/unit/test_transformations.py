"""
Centrally - Tests para Transformaciones
=========================================
Tests para validar transformaciones ETL.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_processing.transformations.transform import DataTransformer


class TestDataTransformer:
    """Tests para DataTransformer."""
    
    def test_clean_data_removes_duplicates(self):
        """Test de eliminación de duplicados."""
        transformer = DataTransformer()
        
        df = pd.DataFrame({
            'id': [1, 1, 2, 3],
            'value': [10, 10, 20, 30]
        })
        
        result = transformer.clean_data(df)
        assert len(result) == 3  # Un duplicado eliminado
    
    def test_normalize_datetime(self):
        """Test de normalización de fechas."""
        transformer = DataTransformer()
        
        df = pd.DataFrame({
            'fecha': ['2026-01-13', '2026-01-14', '2026-01-15']
        })
        
        result = transformer.normalize_datetime(df, ['fecha'])
        assert pd.api.types.is_datetime64_any_dtype(result['fecha'])
    
    def test_create_time_features(self):
        """Test de creación de features temporales."""
        transformer = DataTransformer()
        
        df = pd.DataFrame({
            'timestamp': pd.date_range('2026-01-13', periods=5, freq='D')
        })
        
        result = transformer.create_time_features(df, 'timestamp')
        
        assert 'fecha' in result.columns
        assert 'hora' in result.columns
        assert 'dia_semana' in result.columns
        assert 'mes' in result.columns
        assert 'es_fin_semana' in result.columns
    
    def test_handle_missing_values_mean(self):
        """Test de manejo de valores faltantes con media."""
        transformer = DataTransformer()
        
        df = pd.DataFrame({
            'value': [10.0, 20.0, np.nan, 40.0]
        })
        
        result = transformer.handle_missing_values(
            df,
            strategy={'value': 'mean'}
        )
        
        assert result['value'].isnull().sum() == 0
        assert result['value'].iloc[2] == pytest.approx(23.33, abs=0.1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
