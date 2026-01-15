"""
Centrally - Dashboard Principal (Dash)
========================================
Aplicación web con dashboards interactivos para analítica de transporte.

Autor: Alcaldía de Medellín - Centrally Team
Fecha: 2026-01-13
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
# Agregar directorio raíz al path para permitir imports absolutos
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)

from dotenv import load_dotenv

load_dotenv()

# Configuración de la aplicación
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

app.title = "Centrally - Analítica de Transporte Urbano"
server = app.server  # Para despliegue

# =====================================
# NAVBAR
# =====================================
navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.I(className="fas fa-traffic-light fa-2x text-white me-3"),
                dbc.NavbarBrand("Centrally", className="fs-3 fw-bold text-white"),
            ], width="auto"),
        ], align="center"),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Dashboard", href="/", className="text-white")),
                dbc.NavItem(dbc.NavLink("Tráfico", href="/trafico", className="text-white")),
                dbc.NavItem(dbc.NavLink("Mapas", href="/mapas", className="text-white")),
                dbc.NavItem(dbc.NavLink("Incidentes", href="/incidentes", className="text-white")),
                dbc.NavItem(dbc.NavLink("Analytics", href="/analytics", className="text-white")),
            ], className="ms-auto", navbar=True),
            id="navbar-collapse",
            navbar=True,
        ),
    ], fluid=True),
    color="primary",
    dark=True,
    className="mb-4"
)

# =====================================
# LAYOUT PRINCIPAL
# =====================================

# KPI Cards
def create_kpi_card(title, value, icon, color="primary"):
    """Crea una tarjeta KPI."""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"fas {icon} fa-3x text-{color} mb-3"),
                html.H4(title, className="text-muted"),
                html.H2(value, className="fw-bold")
            ], className="text-center")
        ])
    ], className="shadow-sm h-100")


# Generar datos de ejemplo para demostración
def generate_sample_data():
    """Genera datos de ejemplo para el dashboard."""
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='D'
    )
    
    df = pd.DataFrame({
        'fecha': dates,
        'volumen_total': np.random.randint(5000, 15000, len(dates)),
        'velocidad_promedio': np.random.uniform(35, 65, len(dates)),
        'incidentes': np.random.randint(10, 50, len(dates))
    })
    
    return df


# Layout de la página principal
home_layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Dashboard Ejecutivo", className="display-4 fw-bold mb-2"),
            html.P(
                "Analítica de Transporte Urbano - Alcaldía de Medellín",
                className="lead text-muted"
            ),
        ])
    ], className="mb-4"),
    
    # KPIs
    dbc.Row([
        dbc.Col(create_kpi_card(
            "Volumen Vehicular Hoy",
            "12,450",
            "fa-car",
            "primary"
        ), md=3),
        dbc.Col(create_kpi_card(
            "Velocidad Promedio",
            "48.5 km/h",
            "fa-tachometer-alt",
            "success"
        ), md=3),
        dbc.Col(create_kpi_card(
            "Incidentes Activos",
            "7",
            "fa-exclamation-triangle",
            "warning"
        ), md=3),
        dbc.Col(create_kpi_card(
            "Nivel de Congestión",
            "Medio",
            "fa-traffic-light",
            "info"
        ), md=3),
    ], className="mb-4 g-3"),
    
    # Gráficos
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Volumen Vehicular - Últimos 30 Días", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='graph-volumen')
                ])
            ], className="shadow-sm")
        ], md=8),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Distribución por Tipo", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='graph-tipo')
                ])
            ], className="shadow-sm")
        ], md=4),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Tendencia de Velocidad Promedio", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='graph-velocidad')
                ])
            ], className="shadow-sm")
        ], md=12),
    ]),
    
], fluid=True)

# Layout principal con routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

# =====================================
# CALLBACKS
# =====================================

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Router de páginas."""
    try:
        if pathname == '/':
            return home_layout
        elif pathname == '/trafico':
            return html.Div([html.H2("Página de Tráfico - En construcción")])
        elif pathname == '/mapas':
            # Importar página de mapas
            from dashboard.pages import mapas
            return mapas.layout
        elif pathname == '/incidentes':
            # Importar página de incidentes
            from dashboard.pages import incidentes
            return incidentes.layout
        elif pathname == '/analytics':
            return html.Div([html.H2("Página de Analytics - En construcción")])
        else:
            return home_layout
    except Exception as e:
        import traceback
        traceback.print_exc()
        return html.Div([
            html.H3("Error cargando página", className="text-danger"),
            html.Pre(str(e))
        ])


@app.callback(
    Output('graph-volumen', 'figure'),
    Input('url', 'pathname')
)
def update_graph_volumen(pathname):
    """Actualiza gráfico de volumen vehicular."""
    df = generate_sample_data()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['fecha'],
        y=df['volumen_total'],
        mode='lines+markers',
        name='Volumen Total',
        line=dict(color='#0d6efd', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=300,
        margin=dict(l=40, r=40, t=20, b=40),
        xaxis_title="Fecha",
        yaxis_title="Volumen de Vehículos"
    )
    
    return fig


@app.callback(
    Output('graph-tipo', 'figure'),
    Input('url', 'pathname')
)
def update_graph_tipo(pathname):
    """Actualiza gráfico de distribución por tipo."""
    tipos = ['Automóvil', 'Moto', 'Bus', 'Taxi', 'Camión']
    valores = [45, 30, 10, 10, 5]
    
    fig = go.Figure(data=[go.Pie(
        labels=tipos,
        values=valores,
        hole=0.4,
        marker=dict(colors=['#0d6efd', '#198754', '#ffc107', '#dc3545', '#6c757d'])
    )])
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True
    )
    
    return fig


@app.callback(
    Output('graph-velocidad', 'figure'),
    Input('url', 'pathname')
)
def update_graph_velocidad(pathname):
    """Actualiza gráfico de velocidad promedio."""
    df = generate_sample_data()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['fecha'],
        y=df['velocidad_promedio'],
        mode='lines',
        name='Velocidad Promedio',
        line=dict(color='#198754', width=2),
        fill='tozeroy',
        fillcolor='rgba(25, 135, 84, 0.1)'
    ))
    
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=300,
        margin=dict(l=40, r=40, t=20, b=40),
        xaxis_title="Fecha",
        yaxis_title="Velocidad (km/h)"
    )
    
    return fig


# =====================================
# RUN APP
# =====================================
if __name__ == '__main__':
    import numpy as np  # Necesario para generate_sample_data
    
    debug_mode = os.getenv('DASH_DEBUG', 'True').lower() == 'true'
    host = os.getenv('DASH_HOST', '0.0.0.0')
    port = int(os.getenv('DASH_PORT', 8050))
    
    print(f"🚀 Iniciando Centrally Dashboard en http://{host}:{port}")
    app.run(debug=debug_mode, host=host, port=port)
