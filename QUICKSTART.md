# 🚀 INICIO RÁPIDO - Centrally

## Comandos Esenciales

### Setup Inicial (Primera vez)
```powershell
# 1. Activar entorno virtual
.\venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables
cp .env.example .env
# Edita .env con tus credenciales

# 4. Iniciar infraestructura
docker-compose up -d

# 5. Esperar 15 segundos...
Start-Sleep -Seconds 15

# 6. Inicializar base de datos
docker exec centrally_postgres psql -U centrally_user -d centrally_db -f /docker-entrypoint-initdb.d/init.sql
```

### Ejecución Diaria
```powershell
# Activar venv
.\venv\Scripts\activate

# Levantar servicios Docker
docker-compose up -d

# Ejecutar Dashboard
python dashboard/app.py
# Visitar: http://localhost:8050

# En otra terminal - Ejecutar API
python backend/main.py
# Docs: http://localhost:8000/api/docs
```

### Detener Servicios
```powershell
# Detener Docker
docker-compose down

# Para eliminar datos también (⚠️ destructivo)
docker-compose down -v
```

### Testing
```powershell
# Ejecutar tests
pytest --cov=. --cov-report=html

# Ver reporte
start htmlcov/index.html
```

### Formateo de Código
```powershell
# Auto-formatear
black .
isort .

# Verificar calidad
flake8 .
```

## 📂 Estructura Rápida

```
Centiali-AI/
├── data_ingestion/        → Scripts de ingesta (CSV, API)
├── data_processing/       → Transformaciones ETL
├── data_storage/          → SQL scripts + volúmenes Docker
├── dashboard/             → App Dash
├── backend/               → API FastAPI
├── tests/                 → Tests unitarios
├── docs/                  → Documentación
└── docker-compose.yml     → Orquestación
```

## 🌐 Puertos

- **Dashboard**: 8050
- **API**: 8000
- **PostgreSQL**: 5432
- **PgAdmin**: 5050
- **MLflow**: 5000

## 📚 Documentación Completa

- **README.md**: Visión general
- **docs/architecture.md**: Arquitectura técnica
- **docs/guia-inicio.md**: Guía detallada
- **Walkthrough (artifacts)**: Todo lo creado

---

✅ **Proyecto listo para desarrollo Fase 1 MVP**
