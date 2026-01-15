from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import os
import json
from django.conf import settings

def map_view(request):
    """Vista principal del mapa."""
    return render(request, 'maps/index.html', {
        'page_title': 'Mapa de Calor e Incidentes'
    })

def incidentes_api(request):
    """API que devuelve datos de incidentes en formato JSON para el mapa."""
    try:
        # Ruta al CSV procesado (usando la ruta absoluta del proyecto)
        csv_path = os.path.join(settings.BASE_DIR, 'data_ingestion', 'raw', 'victimas_procesado.csv')
        
        if not os.path.exists(csv_path):
            return JsonResponse({'error': 'Archivo de datos no encontrado', 'path': str(csv_path)}, status=404)
            
        df = pd.read_csv(csv_path)
        
        # Filtrar datos inválidos
        df = df.dropna(subset=['latitud', 'longitud'])
        
        # Optimización: Limitar puntos si son demasiados para probar
        if len(df) > 5000:
            df = df.sample(5000)

        # Convertir a lista de dicts
        data = df[[
            'latitud', 'longitud', 'tipo_incidente', 
            'fecha', 'gravedad', 'direccion', 'descripcion'
        ]].to_dict(orient='records')
        
        return JsonResponse({'incidentes': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
