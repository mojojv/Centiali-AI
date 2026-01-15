"""
Centrally - FastAPI Backend
=============================
API REST para servir datos y autenticación.

Autor: Alcaldía de Medellín - Centrally Team
Fecha: 2026-01-13
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Inicializar FastAPI
app = FastAPI(
    title="Centrally API",
    description="API de Analítica de Transporte Urbano - Alcaldía de Medellín",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# =====================================
# MODELOS PYDANTIC
# =====================================

class TraficoData(BaseModel):
    """Modelo de datos de tráfico."""
    id: int
    fecha_hora: datetime
    zona_id: str
    volumen_vehicular: int = Field(ge=0)
    velocidad_promedio: float = Field(ge=0, le=200)
    nivel_congestion: str = Field(pattern="^(bajo|medio|alto|critico)$")


class IncidenteData(BaseModel):
    """Modelo de incidente."""
    id: int
    fecha_hora: datetime
    tipo_incidente: str
    gravedad: str
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    descripcion: Optional[str] = None


class KPIResponse(BaseModel):
    """Modelo de respuesta de KPIs."""
    volumen_total: int
    velocidad_promedio: float
    incidentes_activos: int
    nivel_congestion: str


# =====================================
# ENDPOINTS
# =====================================

@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "message": "Centrally API - Alcaldía de Medellín",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/kpis", response_model=KPIResponse)
async def get_kpis():
    """
    Obtiene KPIs principales del dashboard.
    """
    # TODO: Conectar con base de datos real
    return {
        "volumen_total": 12450,
        "velocidad_promedio": 48.5,
        "incidentes_activos": 7,
        "nivel_congestion": "medio"
    }


@app.get("/api/trafico", response_model=List[TraficoData])
async def get_trafico_data(
    zona_id: Optional[str] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    limit: int = 100
):
    """
    Obtiene datos de tráfico con filtros opcionales.
    
    Args:
        zona_id: ID de zona geográfica
        fecha_inicio: Fecha inicio del rango
        fecha_fin: Fecha fin del rango
        limit: Número máximo de registros
    """
    # TODO: Implementar consulta a base de datos
    return []


@app.get("/api/incidentes", response_model=List[IncidenteData])
async def get_incidentes(
    tipo: Optional[str] = None,
    gravedad: Optional[str] = None,
    activos: bool = True,
    limit: int = 50
):
    """
    Obtiene incidentes de tránsito.
    
    Args:
        tipo: Tipo de incidente (accidente, congestion, obra, evento)
        gravedad: Gravedad (leve, moderado, grave)
        activos: Solo incidentes activos
        limit: Número máximo de registros
    """
    # TODO: Implementar consulta a base de datos
    return []


@app.post("/api/trafico")
async def create_trafico_record(data: TraficoData):
    """Crea un nuevo registro de tráfico."""
    # TODO: Implementar inserción en base de datos
    return {"message": "Registro creado", "id": data.id}


@app.post("/api/incidentes")
async def create_incidente(data: IncidenteData):
    """Crea un nuevo incidente."""
    # TODO: Implementar inserción en base de datos
    return {"message": "Incidente creado", "id": data.id}


# =====================================
# AUTENTICACIÓN (Placeholder)
# =====================================

@app.post("/api/auth/login")
async def login(username: str, password: str):
    """
    Login de usuario.
    
    TODO: Implementar JWT y verificación real.
    """
    # Placeholder - Implementar con JWT
    return {
        "access_token": "placeholder_token",
        "token_type": "bearer",
        "user": {"username": username, "role": "analyst"}
    }


# =====================================
# RUN
# =====================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    reload = os.getenv('API_RELOAD', 'True').lower() == 'true'
    
    print(f"🚀 Iniciando Centrally API en http://{host}:{port}")
    print(f"📚 Documentación en http://{host}:{port}/api/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    )
