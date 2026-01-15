
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    from dashboard.pages.mapas import get_incidentes_data
    print("Testing get_incidentes_data from mapas.py...")
    df = get_incidentes_data()
    print("Columns:", df.columns.tolist())
    print("Rows:", len(df))
    print("Head:", df.head(1).to_dict(orient='records'))
except Exception as e:
    print(f"Error in mapas.py: {e}")
    import traceback
    traceback.print_exc()

print("-" * 20)

try:
    from dashboard.pages.incidentes import get_incidentes_historico
    print("Testing get_incidentes_historico from incidentes.py...")
    df = get_incidentes_historico()
    print("Columns:", df.columns.tolist())
    print("Rows:", len(df))
    print("Head:", df.head(1).to_dict(orient='records'))
except Exception as e:
    print(f"Error in incidentes.py: {e}")
    import traceback
    traceback.print_exc()
