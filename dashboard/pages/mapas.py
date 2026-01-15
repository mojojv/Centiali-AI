"""
Centrally - Página de Mapas Interactivos
==========================================
Visualización geoespacial de incidentes de tránsito en Medellín.

Autor: Alcaldía de Medellín - Centrally Team
Fecha: 2026-01-13
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json

# =====================================
# DATOS DE EJEMPLO (Reemplazar con DB real)
# =====================================

def get_incidentes_data():
    """Obtiene datos de incidentes reales procesados."""
    try:
        csv_path = "data_ingestion/raw/victimas_procesado.csv"
        # Verificar si existe
        import os
        if not os.path.exists(csv_path):
             # Fallback a ejemplo si no existe
             data = [
                {'id': 1, 'tipo': 'Ejemplo', 'gravedad': 'Leve', 'lat': 6.2442, 'lon': -75.5812, 'direccion': 'Sin datos reales', 'fecha': '2026-01-01', 'descripcion': 'Carga datos reales para ver info'}
             ]
             return pd.DataFrame(data)

        df = pd.read_csv(csv_path)
        
        # Mapear columnas para compatibilidad con el dashboard
        # El dashboard espera: tipo, gravedad, lat, lon, direccion, fecha, descripcion
        df = df.rename(columns={
            'tipo_incidente': 'tipo',
            'latitud': 'lat',
            'longitud': 'lon'
        })
        
        # Filtrar lat/lon nulos por seguridad
        df = df.dropna(subset=['lat', 'lon'])
        
        # Limitar a últimos 3000 registros para rendimiento del mapa si es muy grande
        if len(df) > 3000:
            df = df.tail(3000)
            
        return df
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return pd.DataFrame()


def get_marker_color(gravedad):
    """Retorna color del marcador según gravedad."""
    colors = {
        'Leve': 'green',
        'Moderado': 'orange',
        'Grave': 'red',
        'Critico': 'darkred'
    }
    return colors.get(gravedad, 'blue')


def get_marker_icon(tipo):
    """Retorna ícono según tipo de incidente."""
    icons = {
        'Accidente': 'car-crash',
        'Congestión': 'traffic-light',
        'Obra': 'tools',
        'Evento': 'calendar'
    }
    return icons.get(tipo, 'circle')


# =====================================
# LAYOUT DE LA PÁGINA
# =====================================

layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-map-marked-alt me-3"),
                "Mapas de Incidentes"
            ], className="display-5 fw-bold mb-2"),
            html.P(
                "Visualización geoespacial de incidentes de tránsito en Medellín",
                className="lead text-muted"
            ),
        ])
    ], className="mb-4"),
    
    # Filtros
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Tipo de Incidente", className="fw-bold"),
                            dcc.Dropdown(
                                id='filter-tipo',
                                options=[
                                    {'label': 'Todos', 'value': 'all'},
                                    {'label': 'Accidente', 'value': 'Accidente'},
                                    {'label': 'Congestión', 'value': 'Congestión'},
                                    {'label': 'Obra', 'value': 'Obra'},
                                    {'label': 'Evento', 'value': 'Evento'},
                                ],
                                value='all',
                                clearable=False
                            )
                        ], md=3),
                        
                        dbc.Col([
                            html.Label("Gravedad", className="fw-bold"),
                            dcc.Dropdown(
                                id='filter-gravedad',
                                options=[
                                    {'label': 'Todas', 'value': 'all'},
                                    {'label': 'Leve', 'value': 'Leve'},
                                    {'label': 'Moderado', 'value': 'Moderado'},
                                    {'label': 'Grave', 'value': 'Grave'},
                                    {'label': 'Crítico', 'value': 'Critico'},
                                ],
                                value='all',
                                clearable=False
                            )
                        ], md=3),
                        
                        dbc.Col([
                            html.Label("Rango de Fechas", className="fw-bold"),
                            dcc.DatePickerRange(
                                id='filter-fechas',
                                start_date=(datetime.now() - timedelta(days=30)).date(),
                                end_date=datetime.now().date(),
                                display_format='YYYY-MM-DD',
                                className="w-100"
                            )
                        ], md=4),
                        
                        dbc.Col([
                            html.Label("Acciones", className="fw-bold"),
                            dbc.Button(
                                [html.I(className="fas fa-sync-alt me-2"), "Actualizar"],
                                id='btn-refresh',
                                color="primary",
                                className="w-100"
                            )
                        ], md=2),
                    ])
                ])
            ], className="shadow-sm mb-4")
        ])
    ]),
    
    # Mapa Principal
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-map me-2"),
                        "Mapa de Incidentes - Medellín"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    # Mapa Leaflet
                    dl.Map(
                        id='mapa-incidentes',
                        center=[6.2476, -75.5658],  # Centro de Medellín
                        zoom=12,
                        children=[
                            dl.TileLayer(),
                            dl.LayerGroup(id="layer-incidentes"),
                        ],
                        style={'height': '600px', 'width': '100%'},
                        className="border rounded"
                    ),
                    
                    # Leyenda
                    html.Div([
                        html.H6("Leyenda:", className="mt-3 mb-2 fw-bold"),
                        dbc.Row([
                            dbc.Col([
                                html.Span("🟢 Leve", className="me-3"),
                                html.Span("🟠 Moderado", className="me-3"),
                                html.Span("🔴 Grave", className="me-3"),
                            ])
                        ])
                    ])
                ])
            ], className="shadow-sm")
        ], md=8),
        
        # Panel lateral con estadísticas
        dbc.Col([
            # KPIs
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Incidentes", className="text-muted"),
                    html.H3(id='kpi-total', className="fw-bold text-primary"),
                ], className="text-center")
            ], className="shadow-sm mb-3"),
            
            dbc.Card([
                dbc.CardBody([
                    html.H6("Incidentes Graves", className="text-muted"),
                    html.H3(id='kpi-graves', className="fw-bold text-danger"),
                ], className="text-center")
            ], className="shadow-sm mb-3"),
            
            # Distribución por tipo
            dbc.Card([
                dbc.CardHeader(html.H6("Distribución por Tipo", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='chart-tipo', config={'displayModeBar': False})
                ])
            ], className="shadow-sm mb-3"),
            
            # Lista de incidentes recientes
            dbc.Card([
                dbc.CardHeader(html.H6("Últimos Incidentes", className="mb-0")),
                dbc.CardBody([
                    html.Div(id='lista-incidentes', style={'maxHeight': '300px', 'overflowY': 'auto'})
                ])
            ], className="shadow-sm")
            
        ], md=4),
    ]),
    
], fluid=True, className="py-4")


# =====================================
# CALLBACKS
# =====================================

@callback(
    [
        Output('layer-incidentes', 'children'),
        Output('kpi-total', 'children'),
        Output('kpi-graves', 'children'),
        Output('chart-tipo', 'figure'),
        Output('lista-incidentes', 'children'),
    ],
    [
        Input('btn-refresh', 'n_clicks'),
        Input('filter-tipo', 'value'),
        Input('filter-gravedad', 'value'),
        Input('filter-fechas', 'start_date'),
        Input('filter-fechas', 'end_date'),
    ]
)
def update_mapa(n_clicks, tipo_filter, gravedad_filter, start_date, end_date):
    """Actualiza el mapa y estadísticas según filtros."""
    
    # Obtener datos
    df = get_incidentes_data()
    
    # Aplicar filtros
    if tipo_filter != 'all':
        df = df[df['tipo'] == tipo_filter]
    
    if gravedad_filter != 'all':
        df = df[df['gravedad'] == gravedad_filter]
    
    if start_date and end_date:
        df = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]
    
    # KPIs
    total_incidentes = len(df)
    incidentes_graves = len(df[df['gravedad'] == 'Grave'])
    
    # Crear marcadores para el mapa
    markers = []
    for _, row in df.iterrows():
        color = get_marker_color(row['gravedad'])
        
        popup_content = f"""
        <div style='min-width: 200px'>
            <h6><b>{row['tipo']}</b></h6>
            <p><b>Gravedad:</b> {row['gravedad']}<br>
            <b>Dirección:</b> {row['direccion']}<br>
            <b>Fecha:</b> {row['fecha']}<br>
            <b>Descripción:</b> {row['descripcion']}</p>
        </div>
        """
        
        marker = dl.Marker(
            position=[row['lat'], row['lon']],
            children=[
                dl.Tooltip(row['direccion']),
                dl.Popup(html.Div([html.P(popup_content, dangerouslySetInnerHTML={'__html': popup_content})]))
            ],
            icon={
                "iconUrl": f"https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-{color}.png",
                "shadowUrl": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.4/images/marker-shadow.png",
                "iconSize": [25, 41],
                "iconAnchor": [12, 41],
                "popupAnchor": [1, -34],
                "shadowSize": [41, 41]
            }
        )
        markers.append(marker)
    
    # Gráfico de distribución por tipo
    tipo_counts = df['tipo'].value_counts()
    fig_tipo = px.pie(
        values=tipo_counts.values,
        names=tipo_counts.index,
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_tipo.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=200,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    
    # Lista de incidentes
    lista_items = []
    for _, row in df.head(10).iterrows():
        badge_color = 'danger' if row['gravedad'] == 'Grave' else 'warning' if row['gravedad'] == 'Moderado' else 'success'
        
        item = html.Div([
            dbc.Badge(row['tipo'], color="primary", className="me-2"),
            dbc.Badge(row['gravedad'], color=badge_color, className="me-2"),
            html.P([
                html.Strong(row['direccion']),
                html.Br(),
                html.Small(f"{row['fecha']} - {row['descripcion']}", className="text-muted")
            ], className="mb-2")
        ], className="border-bottom pb-2 mb-2")
        
        lista_items.append(item)
    
    return markers, str(total_incidentes), str(incidentes_graves), fig_tipo, lista_items
