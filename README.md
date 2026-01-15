# 🏙️ Centrally - Plataforma de Analítica de Datos de Transporte Urbano

## 📋 Descripción
**Centrally** es una plataforma integral de analítica, visualización y toma de decisiones basada en datos de transporte urbano para la **Alcaldía de Medellín**. Combina ETL avanzado, modelos de Machine Learning, visualizaciones interactivas y capacidades conversacionales con LLMs para impulsar decisiones informadas en movilidad urbana.

## 🎯 Objetivos
- **Centralizar datos** de múltiples fuentes (APIs abiertas, CSV, Excel, GeoJSON)
- **Transformar datos** mediante pipelines ETL/ELT robustos
- **Analizar** con modelos predictivos, clustering y forecasting
- **Visualizar** con dashboards interactivos en Dash
- **Conversar con datos** mediante LLMs y RAG
- **Gobernar datos** con metadata, lineage y calidad

## 🏗️ Arquitectura

### Capas del Sistema
1. **Ingesta de Datos**: Conexión a fuentes abiertas, validación con Pandera
2. **Transformación ETL/ELT**: Limpieza, normalización, Star Schema
3. **Almacenamiento**: PostgreSQL + PostGIS, DuckDB
4. **Analítica & ML**: Modelos predictivos, análisis espacial, MLflow
5. **LLMs & RAG**: Consultas conversacionales, reportes automáticos
6. **Visualización**: Dashboards Dash con Plotly, mapas interactivos
7. **Backend**: FastAPI con autenticación JWT
8. **Gobernanza**: Metadata, logging, data lineage
9. **Despliegue**: Docker Compose, Cloud (Azure/AWS)

### Stack Tecnológico
- **Lenguaje**: Python 3.10+
- **Frontend**: Dash, Plotly, Dash-Leaflet, Bootstrap
- **Backend**: FastAPI, Uvicorn, Gunicorn
- **Datos**: pandas, geopandas, dbt, pandera
- **DB**: PostgreSQL + PostGIS, DuckDB
- **ML**: scikit-learn, XGBoost, Prophet, MLflow
- **LLMs**: LangChain, FAISS/ChromaDB, OpenAI/Llama
- **DevOps**: Docker, GitHub Actions, pytest, black, flake8

## 📁 Estructura del Proyecto

```
centrally/
├── data_ingestion/          # Capa 1: Ingesta de datos
│   ├── raw/                 # Datos crudos
│   ├── scripts/             # Scripts de ingesta (API, CSV, etc.)
│   └── validators.py        # Validación con Pandera
├── data_processing/         # Capa 2: Transformación ETL/ELT
│   ├── staging/             # Datos procesados intermedios
│   ├── transformations/     # Scripts de limpieza y normalización
│   ├── features/            # Feature engineering
│   └── schemas/             # Definiciones Star Schema
├── data_storage/            # Capa 3: Almacenamiento
│   ├── postgres_data/       # Volumen PostgreSQL (Docker)
│   ├── duckdb_data/         # DuckDB local
│   └── db_scripts/          # Scripts DDL/DML
├── models/                  # Capa 4: Analítica y ML
│   ├── descriptive/         # KPIs, series temporales
│   ├── predictive/          # Modelos de ML
│   ├── spatial/             # Análisis geoespacial
│   ├── evaluation/          # Métricas y evaluación
│   └── trained_models/      # Modelos serializados
├── llm/                     # Capa 5: LLMs y RAG
│   ├── prompts/             # Templates de prompts
│   ├── retrievers/          # Configuración RAG
│   ├── agents/              # Agentes conversacionales
│   └── evaluators/          # Evaluación de LLMs
├── dashboard/               # Capa 6: Visualización Dash
│   ├── app.py               # App principal
│   ├── pages/               # Páginas (overview, traffic, mapas)
│   ├── components/          # Componentes reutilizables
│   ├── callbacks/           # Callbacks de Dash
│   └── assets/              # CSS, JS, imágenes
├── backend/                 # Capa 7: Backend FastAPI
│   ├── api/                 # Endpoints REST
│   ├── auth/                # Autenticación JWT
│   ├── middleware/          # Middleware personalizado
│   └── schemas/             # Pydantic models
├── governance/              # Capa 8: Gobernanza de datos
│   ├── metadata/            # Registro de metadata
│   ├── lineage/             # Data lineage
│   └── quality/             # Validación de calidad
├── deployment/              # Capa 9: Despliegue
│   ├── docker/              # Dockerfiles
│   ├── k8s/                 # Kubernetes (opcional)
│   └── scripts/             # Scripts de deploy
├── tests/                   # Testing (pytest)
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                    # Documentación
│   ├── architecture.md
│   ├── api/
│   └── guides/
├── logs/                    # Logs de aplicación
├── .github/                 # GitHub Actions
│   └── workflows/
├── docker-compose.yml       # Orquestación de servicios
├── requirements.txt         # Dependencias Python
├── pyproject.toml           # Configuración de herramientas
├── .env.example             # Template de variables de entorno
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerrequisitos
- Python 3.10+
- Docker & Docker Compose
- Git
- PostgreSQL (o usar Docker)

### Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd Centiali-AI
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. **Levantar infraestructura con Docker**
```bash
docker-compose up -d
```

6. **Ejecutar migraciones de base de datos**
```bash
python data_storage/db_scripts/init_db.py
```

7. **Ejecutar pipeline de ingesta (ejemplo)**
```bash
python data_ingestion/scripts/ingest_csv.py
```

8. **Iniciar dashboard Dash**
```bash
python dashboard/app.py
```

Acceder a: `http://localhost:8050`

## 📊 Roadmap

### ✅ Fase 1: MVP (Actual)
- [x] Configuración de repositorio y estructura
- [ ] Ingesta básica de datos (CSV, API)
- [ ] ETL con pandas y DuckDB
- [ ] Dashboard Dash con KPIs básicos
- [ ] PostgreSQL + Docker

### 🚧 Fase 2: Analítica Avanzada
- [ ] Modelos predictivos (tráfico, demanda)
- [ ] Mapas geoespaciales interactivos
- [ ] Orquestación con Airflow/Prefect
- [ ] MLflow para versionado de modelos

### 🔮 Fase 3: IA & LLMs
- [ ] Integración de chat con RAG
- [ ] Reportes automáticos con LLMs
- [ ] Soporte a decisiones conversacional
- [ ] Dashboards con insights generados por IA

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Tests específicos
pytest tests/unit/
pytest tests/integration/
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Estándares de código
- **Linting**: `black`, `flake8`, `isort`
- **Type hints**: Usar anotaciones de tipo
- **Documentación**: Docstrings en formato Google/NumPy
- **Testing**: Cobertura mínima 80%

```bash
# Formatear código
black .

# Linting
flake8 .

# Importaciones
isort .
```

## 📝 Licencia

Este proyecto es desarrollado para la **Alcaldía de Medellín** bajo principios de datos abiertos y gobierno abierto.

## 👥 Equipo

- **Alcaldía de Medellín** - Secretaría de Movilidad
- **Equipo de Desarrollo** - Data Engineering & Analytics

## 📧 Contacto

Para preguntas o soporte: [contacto@medellin.gov.co]

---

**🌟 Construyendo una Medellín inteligente, sostenible y data-driven**
