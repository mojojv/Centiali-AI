"""
Centrally - Página de Analytics de Incidentes
===============================================
Análisis detallado de incidentes para toma de decisiones.

Autor: Alcaldía de Medellín - Centrally Team
Fecha: 2026-01-13
"""

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# =====================================
# DATOS DE EJEMPLO
# =====================================

def get_incidentes_historico():
    """Obtiene datos históricos reales procesados."""
    try:
        csv_path = "data_ingestion/raw/victimas_procesado.csv"
        # Verificar si existe
        import os
        if not os.path.exists(csv_path):
             return generate_dummy_data()

        df = pd.read_csv(csv_path)
        
        # Mapear columnas
        df = df.rename(columns={
            'tipo_incidente': 'tipo'
        })
        
        # Asegurar formato fecha
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['dia_semana'] = df['fecha'].dt.day_name()
        # Si la fecha tiene hora
        df['hora'] = df['fecha'].dt.hour
        
        # Zona para gráfico top zonas (extraer de descripcion si no existe columna zona)
        if 'zona' not in df.columns:
            # Intentar extraer Comuna de descripcion
            # Format: Barrio: X | Comuna: Y | ...
            df['zona'] = df['descripcion'].str.extract(r'Comuna: ([^\|]+)')
            df['zona'] = df['zona'].fillna('Medellín')
        
        return df
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return generate_dummy_data()

def generate_dummy_data():
    """Generador fallback."""
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    data = []
    for date in dates:
        for hour in range(24):
            n = np.random.poisson(2)
            for _ in range(n):
                data.append({
                    'fecha': date,
                    'hora': hour,
                    'dia_semana': date.day_name(),
                    'tipo': 'Sin Datos',
                    'gravedad': 'Leve',
                    'zona': 'Desconocida',
                    'direccion': 'N/A'
                })
    return pd.DataFrame(data)


# =====================================
# LAYOUT
# =====================================

layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-chart-line me-3"),
                "Analytics de Incidentes"
            ], className="display-5 fw-bold mb-2"),
            html.P(
                "Análisis histórico y predictivo para toma de decisiones en seguridad vial",
                className="lead text-muted"
            ),
        ])
    ], className="mb-4"),
    
    # KPIs Principales
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-exclamation-triangle fa-2x text-warning mb-2"),
                        html.H6("Total Incidentes (30d)", className="text-muted"),
                        html.H2(id='kpi-total-30d', className="fw-bold text-primary")
                    ], className="text-center")
                ])
            ], className="shadow-sm h-100")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-car-crash fa-2x text-danger mb-2"),
                        html.H6("Accidentes Graves", className="text-muted"),
                        html.H2(id='kpi-graves-30d', className="fw-bold text-danger")
                    ], className="text-center")
                ])
            ], className="shadow-sm h-100")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-arrow-trend-up fa-2x text-success mb-2"),
                        html.H6("Tendencia vs Mes Anterior", className="text-muted"),
                        html.H2(id='kpi-tendencia', className="fw-bold")
                    ], className="text-center")
                ])
            ], className="shadow-sm h-100")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-location-dot fa-2x text-info mb-2"),
                        html.H6("Zona Más Crítica", className="text-muted"),
                        html.H3(id='kpi-zona-critica', className="fw-bold text-info")
                    ], className="text-center")
                ])
            ], className="shadow-sm h-100")
        ], md=3),
    ], className="mb-4 g-3"),
    
    # Gráficos Principales
    dbc.Row([
        # Serie temporal
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-chart-area me-2"),
                        "Evolución Temporal de Incidentes"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='graph-serie-temporal')
                ])
            ], className="shadow-sm")
        ], md=8),
        
        # Distribución por tipo
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-chart-pie me-2"),
                        "Por Tipo de Incidente"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='graph-distribucion-tipo')
                ])
            ], className="shadow-sm")
        ], md=4),
    ], className="mb-4"),
    
    # Heatmap horario y Top zonas
    dbc.Row([
        # Heatmap de horarios
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-clock me-2"),
                        "Horarios Críticos (Día de la Semana vs Hora)"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='graph-heatmap-horario')
                ])
            ], className="shadow-sm")
        ], md=7),
        
        # Top zonas
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-ranking-star me-2"),
                        "Top 10 Zonas con Más Incidentes"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='graph-top-zonas')
                ])
            ], className="shadow-sm")
        ], md=5),
    ], className="mb-4"),
    
    # Tabla detallada
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-table me-2"),
                        "Registro Detallado de Incidentes Recientes"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id='tabla-incidentes-detalle', style={'maxHeight': '400px', 'overflowY': 'auto'})
                ])
            ], className="shadow-sm")
        ])
    ]),
    
], fluid=True, className="py-4")


# =====================================
# CALLBACKS
# =====================================

@callback(
    [
        Output('kpi-total-30d', 'children'),
        Output('kpi-graves-30d', 'children'),
        Output('kpi-tendencia', 'children'),
        Output('kpi-zona-critica', 'children'),
        Output('graph-serie-temporal', 'figure'),
        Output('graph-distribucion-tipo', 'figure'),
        Output('graph-heatmap-horario', 'figure'),
        Output('graph-top-zonas', 'figure'),
        Output('tabla-incidentes-detalle', 'children'),
    ],
    [Input('kpi-total-30d', 'id')]  # Trigger on load
)
def update_analytics(_):
    """Actualiza todos los componentes de analytics."""
    
    # Obtener datos
    df = get_incidentes_historico()
    
    # Últimos 30 días
    fecha_limite = datetime.now().date() - timedelta(days=30)
    df_30d = df[pd.to_datetime(df['fecha']) >= pd.to_datetime(fecha_limite)]
    
    # KPIs
    total_30d = len(df_30d)
    graves_30d = len(df_30d[(df_30d['gravedad'] == 'Grave') & (df_30d['tipo'] == 'Accidente')])
    
    # Tendencia (comparar con 30 días anteriores)
    fecha_mes_anterior = fecha_limite - timedelta(days=30)
    df_mes_anterior = df[
        (pd.to_datetime(df['fecha']) >= pd.to_datetime(fecha_mes_anterior)) &
        (pd.to_datetime(df['fecha']) < pd.to_datetime(fecha_limite))
    ]
    tendencia_pct = ((total_30d - len(df_mes_anterior)) / len(df_mes_anterior) * 100) if len(df_mes_anterior) > 0 else 0
    tendencia_text = f"{tendencia_pct:+.1f}%"
    
    # Zona más crítica
    zona_critica = df_30d['zona'].value_counts().index[0] if len(df_30d) > 0 else "N/A"
    
    # Gráfico 1: Serie temporal
    serie_temporal = df.groupby('fecha').size().reset_index(name='count')
    fig_serie = go.Figure()
    fig_serie.add_trace(go.Scatter(
        x=serie_temporal['fecha'],
        y=serie_temporal['count'],
        mode='lines+markers',
        name='Incidentes por día',
        line=dict(color='#0d6efd', width=2),
        fill='tozeroy',
        fillcolor='rgba(13, 110, 253, 0.1)'
    ))
    fig_serie.update_layout(
        template='plotly_white',
        hovermode='x unified',
        height=350,
        margin=dict(l=40, r=40, t=20, b=40),
        xaxis_title="Fecha",
        yaxis_title="Número de Incidentes"
    )
    
    # Gráfico 2: Distribución por tipo
    tipo_counts = df_30d['tipo'].value_counts()
    fig_tipo = px.pie(
        values=tipo_counts.values,
        names=tipo_counts.index,
        hole=0.5,
        color_discrete_sequence=['#0d6efd', '#198754', '#ffc107']
    )
    fig_tipo.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True
    )
    
    # Gráfico 3: Heatmap horario
    # Crear matriz día_semana vs hora
    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dias_es = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    heatmap_data = df_30d.groupby(['dia_semana', 'hora']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='dia_semana', columns='hora', values='count').fillna(0)
    heatmap_pivot = heatmap_pivot.reindex(dias_orden)
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=dias_es,
        colorscale='YlOrRd',
        hoverongaps=False,
        colorbar=dict(title="Incidentes")
    ))
    fig_heatmap.update_layout(
        template='plotly_white',
        height=350,
        margin=dict(l=80, r=40, t=20, b=40),
        xaxis_title="Hora del Día",
        yaxis_title="Día de la Semana"
    )
    
    # Gráfico 4: Top zonas
    top_zonas = df_30d['zona'].value_counts().head(10)
    fig_top_zonas = go.Figure(data=[
        go.Bar(
            x=top_zonas.values,
            y=top_zonas.index,
            orientation='h',
            marker=dict(
                color=top_zonas.values,
                colorscale='Reds',
                showscale=False
            )
        )
    ])
    fig_top_zonas.update_layout(
        template='plotly_white',
        height=350,
        margin=dict(l=120, r=40, t=20, b=40),
        xaxis_title="Número de Incidentes",
        yaxis_title="",
        yaxis={'categoryorder': 'total ascending'}
    )
    
    # Tabla detallada: últimos 50 incidentes
    tabla_rows = []
    df_recientes = df.sort_values('fecha', ascending=False).head(50)
    
    for _, row in df_recientes.iterrows():
        badge_tipo = 'primary' if row['tipo'] == 'Accidente' else 'warning' if row['tipo'] == 'Congestión' else 'info'
        badge_gravedad = 'danger' if row['gravedad'] == 'Grave' else 'warning' if row['gravedad'] == 'Moderado' else 'success'
        
        tabla_row = html.Tr([
            html.Td(str(row['fecha'])),
            html.Td(f"{row['hora']:02d}:00"),
            html.Td(dbc.Badge(row['tipo'], color=badge_tipo)),
            html.Td(dbc.Badge(row['gravedad'], color=badge_gravedad)),
            html.Td(row['zona']),
            html.Td(row['direccion'], className="small"),
        ])
        tabla_rows.append(tabla_row)
    
    tabla_detalle = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Fecha"),
                html.Th("Hora"),
                html.Th("Tipo"),
                html.Th("Gravedad"),
                html.Th("Zona"),
                html.Th("Dirección"),
            ])
        ]),
        html.Tbody(tabla_rows)
    ], striped=True, bordered=True, hover=True, size='sm')
    
    return (
        str(total_30d),
        str(graves_30d),
        tendencia_text,
        zona_critica,
        fig_serie,
        fig_tipo,
        fig_heatmap,
        fig_top_zonas,
        tabla_detalle
    )
