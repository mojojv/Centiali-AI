# Arquitectura Técnica - Centrally

## 📐 Visión General

Centrally es una plataforma enterprise de analítica de datos de transporte urbano construida con arquitectura modular de 9 capas, diseñada para escalar horizontalmente y soportar miles de usuarios concurrentes.

## 🏗️ Arquitectura de Capas

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 6: VISUALIZACIÓN                        │
│                    (Dash + Plotly + Leaflet)                    │
└────────────▲───────────────────────────────▲────────────────────┘
             │                               │
             │                               │
┌────────────┴──────────────┐   ┌────────────┴───────────────────┐
│  CAPA 7: BACKEND API      │   │   CAPA 5: LLMs & RAG          │
│     (FastAPI + JWT)       │   │  (LangChain + FAISS)          │
└────────────▲──────────────┘   └────────────▲───────────────────┘
             │                               │
             └───────────────┬───────────────┘
                             │
┌────────────────────────────┴──────────────────────────────────┐
│             CAPA 4: ANALÍTICA & MODELOS ML                     │
│         (scikit-learn + XGBoost + Prophet + MLflow)            │
└────────────▲───────────────────────────────────────────────────┘
             │
┌────────────┴───────────────────────────────────────────────────┐
│          CAPA 3: ALMACENAMIENTO (PostgreSQL + PostGIS)         │
│                      Star Schema: dim_* + fact_*                │
└────────────▲───────────────────────────────────────────────────┘
             │
┌────────────┴───────────────────────────────────────────────────┐
│       CAPA 2: TRANSFORMACIÓN ETL/ELT (pandas + dbt)            │
│              Staging → Processing → Analytics                   │
└────────────▲───────────────────────────────────────────────────┘
             │
┌────────────┴───────────────────────────────────────────────────┐
│      CAPA 1: INGESTA (APIs + CSV + Excel + GeoJSON)            │
│              Validators (Pandera) + Metadata                    │
└────────────────────────────────────────────────────────────────┘
             ▲
             │
    ┌────────┴────────┐
    │  DATA SOURCES   │
    │  (Datos Abiertos│
    │   Medellín)     │
    └─────────────────┘
```

┌─────────────┬───────────────────────────────────────────┐
│  CAPA 8:    │   GOBERNANZA DE DATOS                      │
│  Transversal│   Metadata + Lineage + Quality + Logs      │
└─────────────┴───────────────────────────────────────────┘

┌─────────────┬───────────────────────────────────────────┐
│  CAPA 9:    │   DESPLIEGUE & ORQUESTACIÓN               │
│  Infraest.  │   Docker + K8s + Airflow/Prefect + CI/CD  │
└─────────────┴───────────────────────────────────────────┘

## 🗄️ Modelo de Datos - Star Schema

### Dimensiones

**dim_tiempo**
- tiempo_id (PK)
- fecha, hora
- dia_semana, mes, trimestre, anio
- es_festivo, es_fin_semana

**dim_zona**
- zona_id (PK)
- codigo_zona
- nombre_zona, tipo_zona
- geometria (PostGIS POLYGON)
- area_km2, poblacion

**dim_tipo_vehiculo**
- vehiculo_id (PK)
- codigo_vehiculo
- nombre_vehiculo, categoria

**dim_tipo_incidente**
- incidente_tipo_id (PK)
- codigo_incidente
- nombre_incidente, categoria, gravedad

### Hechos

**fact_trafico**
- trafico_id (PK)
- tiempo_id (FK), zona_id (FK), vehiculo_id (FK)
- Métricas: volumen_vehicular, velocidad_promedio, tiempo_recorrido_seg, nivel_congestion

**fact_incidentes**
- incidente_id (PK)
- tiempo_id (FK), zona_id (FK), incidente_tipo_id (FK)
- latitud, longitud, ubicacion (PostGIS POINT)
- descripcion, afectacion_vial, tiempo_resolucion_min

## 🔄 Flujo de Datos

1. **Ingesta** → APIs/CSV llegan a `data_ingestion/raw/`
2. **Validación** → Pandera valida esquemas
3. **Staging** → Datos limpios en `data_processing/staging/`
4. **Transformación** → ETL genera features en `data_processing/analytics/`
5. **Carga** → PostgreSQL Star Schema
6. **Analítica** → Modelos ML generan insights
7. **Visualización** → Dash consume vía API
8. **LLMs** → RAG responde preguntas sobre datos

## 🔐 Seguridad

- **Autenticación**: JWT con roles (analista, decisor, admin)
- **Autorización**: RBAC en endpoints FastAPI
- **Datos sensibles**: No se almacenan datos personales
- **Transporte**: HTTPS en producción
- **Secrets**: Variables de entorno (.env)

## 📊 Escalabilidad

### Horizontal
- Dashboard Dash: Múltiples instancias detrás de load balancer
- API FastAPI: Auto-scaling en cloud
- PostgreSQL: Read replicas para consultas

### Vertical
- Batch processing para ETL grandes
- Caché con Redis (opcional)
- Compresión de datos históricos

## 🚀 Tecnologías Clave

| Capa | Tecnologías |
|------|-------------|
| Frontend | Dash 2.14, Plotly, Dash-Leaflet, Bootstrap |
| Backend | FastAPI 0.108, Uvicorn, Pydantic |
| Base de Datos | PostgreSQL 15 + PostGIS 3.3, DuckDB |
| ETL | pandas, dbt, Pandera |
| ML | scikit-learn, XGBoost, Prophet, MLflow |
| LLMs | LangChain, FAISS, OpenAI/Llama |
| DevOps | Docker, GitHub Actions, pytest |

## 📁 Estructura de Almacenamiento

```
data_storage/
├── postgres_data/          # Volumen Docker PostgreSQL
├── duckdb_data/            # DuckDB para prototipado local
└── db_scripts/
    ├── init.sql            # Inicialización de schema
    └── migrations/         # Migraciones (Alembic)
```

## 🔧 Configuración de Entorno

Ver `.env.example` para variables requeridas:
- `DATABASE_URL`: Conexión PostgreSQL
- `OPENAI_API_KEY`: Para LLMs
- `JWT_SECRET_KEY`: Autenticación
- `DASH_SECRET_KEY`: Sesiones Dash

## 🧪 Estrategia de Testing

- **Unit Tests**: pytest para funciones individuales
- **Integration Tests**: Tests de pipelines completos
- **E2E Tests**: Selenium para dashboard
- **Cobertura mínima**: 80%

## 📝 Gobernanza de Datos

### Metadata Tracking
- Tabla `metadata_ingesta`: Registro de todas las ingestas
- Campos: dataset_name, timestamp, registros_procesados, estado

### Data Lineage
- Tabla `metadata_lineage`: Trazabilidad de transformaciones
- Tracking: tabla_origen → transformación → tabla_destino

### Calidad de Datos
- Validación con Pandera en ingesta
- Checks de integridad referencial en PostgreSQL
- Alertas automáticas por anomalías

## 🌐 Despliegue

### Local (Desarrollo)
```bash
docker-compose up -d
python dashboard/app.py
```

### Cloud (Producción)
- **Azure**: App Service + PostgreSQL Flexible Server
- **AWS**: ECS + RDS PostgreSQL
- **Load Balancer**: Nginx
- **CI/CD**: GitHub Actions → Docker Registry → Cloud

## 🔮 Roadmap Técnico

**Fase 1 (MVP)**: ✓ Estructura base, ingesta, dashboard básico
**Fase 2**: Modelos ML, mapas geoespaciales, Airflow
**Fase 3**: LLMs integrados, chat conversacional, reportes automáticos

---

**Última actualización**: 2026-01-13
