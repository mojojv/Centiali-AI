from django.shortcuts import render
import pandas as pd
import os
import json
from django.conf import settings

def analytics_dashboard(request):
    """Dashboard principal de analítica."""
    try:
        csv_path = os.path.join(settings.BASE_DIR, 'data_ingestion', 'raw', 'victimas_procesado.csv')
        df = pd.read_csv(csv_path)

        # 1. Total Incidentes
        total_incidentes = len(df)

        # 2. Distribución por Gravedad (Pie Chart)
        gravedad_counts = df['gravedad'].value_counts().to_dict()
        
        # 3. Distribución por Tipo (Bar Chart)
        tipo_counts = df['tipo_incidente'].value_counts().head(10).to_dict()

        # 4. Tendencia Temporal (Line Chart - por mes/año)
        df['fecha'] = pd.to_datetime(df['fecha'])
        tendencia = df.groupby(df['fecha'].dt.to_period('M')).size()
        tendencia_labels = [str(p) for p in tendencia.index]
        tendencia_values = tendencia.values.tolist()

        context = {
            'total_incidentes': total_incidentes,
            'chart_gravedad': json.dumps({'labels': list(gravedad_counts.keys()), 'series': list(gravedad_counts.values())}),
            'chart_tipo': json.dumps({'labels': list(tipo_counts.keys()), 'series': list(tipo_counts.values())}),
            'chart_tendencia': json.dumps({'labels': tendencia_labels, 'series': tendencia_values})
        }

    except Exception as e:
        context = {'error': str(e)}

    return render(request, 'analytics/dashboard.html', context)
