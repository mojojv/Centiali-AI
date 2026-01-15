# Guía de Inicio Rápido - Centrally

## 🎯 Objetivos
Esta guía te ayudará a levantar Centrally en tu entorno local en menos de 10 minutos.

## 📋 Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.10+**: [Descargar](https://www.python.org/downloads/)
- **Docker Desktop**: [Descargar](https://www.docker.com/products/docker-desktop/)
- **Git**: [Descargar](https://git-scm.com/downloads)

## 🚀 Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone <repository-url>
cd Centiali-AI
```

### Paso 2: Crear Entorno Virtual

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏱️ Esto puede tomar 5-10 minutos dependiendo de tu conexión.

### Paso 4: Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar .env con tus credenciales (usar nano, vim, o editor de texto)
nano .env
```

**Configuración mínima** para empezar:
```env
POSTGRES_PASSWORD=tu_password_seguro
DASH_SECRET_KEY=clave_secreta_random
JWT_SECRET_KEY=otra_clave_secreta_random
```

### Paso 5: Levantar Infraestructura con Docker

```bash
docker-compose up -d
```

Esto iniciará:
- ✅ PostgreSQL + PostGIS (puerto 5432)
- ✅ PgAdmin (puerto 5050)
- ✅ MLflow (puerto 5000)

Verifica que los contenedores están corriendo:
```bash
docker-compose ps
```

### Paso 6: Inicializar Base de Datos

```bash
# Esperar 10 segundos a que PostgreSQL inicie completamente
sleep 10

# Ejecutar script de inicialización
docker exec centrally_postgres psql -U centrally_user -d centrally_db -f /docker-entrypoint-initdb.d/init.sql
```

✅ Esto crea el Star Schema con todas las tablas.

## 🎨 Ejecutar Dashboard

### Opción A: Modo Desarrollo (Local)

```bash
python dashboard/app.py
```

Acceder a: **http://localhost:8050**

### Opción B: Modo Docker

```bash
docker-compose up dashboard
```

## 🔌 Ejecutar API

```bash
python backend/main.py
```

Acceder a:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 📊 Acceder a PgAdmin (Opcional)

1. Ir a: **http://localhost:5050**
2. Login:
   - Email: `admin@centrally.com`
   - Password: `admin`
3. Agregar servidor:
   - Host: `postgres`
   - Port: `5432`
   - Database: `centrally_db`
   - Username: `centrally_user`
   - Password: (el que configuraste en .env)

## 🧪 Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Solo tests unitarios
pytest tests/unit/

# Test específico
pytest tests/unit/test_ingestion.py -v
```

Ver reporte de cobertura: abrir `htmlcov/index.html` en navegador.

## 📥 Ingestar Datos de Ejemplo

```bash
# Ejemplo de ingesta desde CSV (crear archivo de prueba primero)
python data_ingestion/scripts/ingest_csv.py

# Ejemplo de ingesta desde API
python data_ingestion/scripts/ingest_api.py
```

## 🛑 Detener Servicios

```bash
# Detener contenedores
docker-compose down

# Detener y eliminar volúmenes (⚠️ borra datos)
docker-compose down -v
```

## ⚡ Comandos Útiles

### Formatear Código
```bash
# Auto-formatear con Black
black .

# Ordenar imports
isort .

# Linting
flake8 .
```

### Ver Logs de Docker
```bash
# Todos los servicios
docker-compose logs -f

# Solo PostgreSQL
docker-compose logs -f postgres

# Solo Dashboard
docker-compose logs -f dashboard
```

### Reiniciar un Servicio
```bash
docker-compose restart postgres
docker-compose restart dashboard
```

## 🐛 Solución de Problemas

### Error: "Puerto 5432 ya en uso"
Ya tienes PostgreSQL corriendo localmente. Opciones:
1. Detener PostgreSQL local
2. Cambiar puerto en `docker-compose.yml`: `"5433:5432"`

### Error: "ModuleNotFoundError"
Asegúrate de:
1. Tener el entorno virtual activado
2. Haber ejecutado `pip install -r requirements.txt`

### Error: "Connection refused" al dashboard
1. Verifica que PostgreSQL esté corriendo: `docker-compose ps`
2. Espera 30 segundos más para que PostgreSQL inicie
3. Revisa logs: `docker-compose logs postgres`

### Dashboard no carga gráficos
Es normal en primera ejecución (datos de ejemplo). Para poblar con datos reales, ejecutar scripts de ingesta.

## 📚 Próximos Pasos

1. **Explorar Dashboard**: Navega por las diferentes páginas
2. **Revisar Documentación**: Lee `docs/architecture.md`
3. **Crear tu primera ingesta**: Modifica `data_ingestion/scripts/ingest_csv.py`
4. **Agregar una nueva visual**: Edita `dashboard/app.py`

## 🤝 ¿Necesitas Ayuda?

- **Documentación completa**: `docs/`
- **Issues**: Abre un issue en GitHub
- **Contribuir**: Lee `CONTRIBUTING.md` (próximamente)

---

¡Listo! Ahora tienes Centrally corriendo en tu máquina. 🎉
