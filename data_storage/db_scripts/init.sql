-- =====================================
-- CENTRALLY - Database Initialization
-- Script de inicialización PostgreSQL + PostGIS
-- =====================================

-- Habilitar extensión PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Crear esquema principal
CREATE SCHEMA IF NOT EXISTS centrally;

-- =====================================
-- DIMENSIONES (Star Schema)
-- =====================================

-- Dimensión Tiempo
CREATE TABLE IF NOT EXISTS centrally.dim_tiempo (
    tiempo_id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    dia_semana VARCHAR(20),
    mes VARCHAR(20),
    trimestre INT,
    anio INT,
    es_festivo BOOLEAN DEFAULT FALSE,
    es_fin_semana BOOLEAN DEFAULT FALSE,
    UNIQUE(fecha, hora)
);

-- Dimensión Zona Geográfica
CREATE TABLE IF NOT EXISTS centrally.dim_zona (
    zona_id SERIAL PRIMARY KEY,
    codigo_zona VARCHAR(50) UNIQUE NOT NULL,
    nombre_zona VARCHAR(200),
    tipo_zona VARCHAR(50),  -- comuna, barrio, corredor, etc.
    geometria GEOMETRY(POLYGON, 4326),
    area_km2 DECIMAL(10, 4),
    poblacion INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índice espacial
CREATE INDEX idx_zona_geometria ON centrally.dim_zona USING GIST(geometria);

-- Dimensión Tipo de Vehículo
CREATE TABLE IF NOT EXISTS centrally.dim_tipo_vehiculo (
    vehiculo_id SERIAL PRIMARY KEY,
    codigo_vehiculo VARCHAR(20) UNIQUE NOT NULL,
    nombre_vehiculo VARCHAR(100),
    categoria VARCHAR(50)  -- particular, publico, carga, moto
);

-- Dimensión Tipo de Incidente
CREATE TABLE IF NOT EXISTS centrally.dim_tipo_incidente (
    incidente_tipo_id SERIAL PRIMARY KEY,
    codigo_incidente VARCHAR(20) UNIQUE NOT NULL,
    nombre_incidente VARCHAR(100),
    categoria VARCHAR(50),  -- accidente, congestion, obra, evento
    gravedad VARCHAR(20)    -- leve, moderado, grave
);

-- =====================================
-- HECHOS (Fact Tables)
-- =====================================

-- Hecho: Tráfico
CREATE TABLE IF NOT EXISTS centrally.fact_trafico (
    trafico_id SERIAL PRIMARY KEY,
    tiempo_id INT REFERENCES centrally.dim_tiempo(tiempo_id),
    zona_id INT REFERENCES centrally.dim_zona(zona_id),
    vehiculo_id INT REFERENCES centrally.dim_tipo_vehiculo(vehiculo_id),
    
    -- Métricas
    volumen_vehicular INT,
    velocidad_promedio DECIMAL(6, 2),
    tiempo_recorrido_seg INT,
    nivel_congestion VARCHAR(20),  -- bajo, medio, alto, critico
    indice_congestion DECIMAL(5, 2),
    
    -- Metadata
    fuente_datos VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Validaciones
    CONSTRAINT chk_velocidad CHECK (velocidad_promedio >= 0 AND velocidad_promedio <= 200),
    CONSTRAINT chk_volumen CHECK (volumen_vehicular >= 0)
);

-- Índices para optimizar consultas
CREATE INDEX idx_trafico_tiempo ON centrally.fact_trafico(tiempo_id);
CREATE INDEX idx_trafico_zona ON centrally.fact_trafico(zona_id);
CREATE INDEX idx_trafico_vehiculo ON centrally.fact_trafico(vehiculo_id);

-- Hecho: Incidentes
CREATE TABLE IF NOT EXISTS centrally.fact_incidentes (
    incidente_id SERIAL PRIMARY KEY,
    tiempo_id INT REFERENCES centrally.dim_tiempo(tiempo_id),
    zona_id INT REFERENCES centrally.dim_zona(zona_id),
    incidente_tipo_id INT REFERENCES centrally.dim_tipo_incidente(incidente_tipo_id),
    
    -- Ubicación exacta
    latitud DECIMAL(10, 7),
    longitud DECIMAL(10, 7),
    ubicacion GEOMETRY(POINT, 4326),
    
    -- Detalles
    descripcion TEXT,
    afectacion_vial VARCHAR(50),  -- parcial, total
    tiempo_resolucion_min INT,
    
    -- Metadata
    fuente_datos VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_incidentes_tiempo ON centrally.fact_incidentes(tiempo_id);
CREATE INDEX idx_incidentes_zona ON centrally.fact_incidentes(zona_id);
CREATE INDEX idx_incidentes_ubicacion ON centrally.fact_incidentes USING GIST(ubicacion);

-- =====================================
-- TABLAS DE METADATA Y GOBERNANZA
-- =====================================

-- Registro de Ingesta de Datos
CREATE TABLE IF NOT EXISTS centrally.metadata_ingesta (
    ingesta_id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(100) NOT NULL,
    fuente VARCHAR(200),
    timestamp_ingesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    registros_procesados INT,
    registros_validos INT,
    registros_rechazados INT,
    estado VARCHAR(20),  -- exitoso, fallido, parcial
    log_errores TEXT
);

-- Data Lineage
CREATE TABLE IF NOT EXISTS centrally.metadata_lineage (
    lineage_id SERIAL PRIMARY KEY,
    tabla_origen VARCHAR(100),
    tabla_destino VARCHAR(100),
    transformacion_aplicada TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(100)
);

-- =====================================
-- DATOS DE EJEMPLO (Opcional - Testing)
-- =====================================

-- Insertar dimensión tiempo (ejemplo para un día)
INSERT INTO centrally.dim_tiempo (fecha, hora, dia_semana, mes, trimestre, anio, es_festivo, es_fin_semana)
SELECT 
    '2026-01-13'::DATE,
    (h || ':00:00')::TIME,
    'Lunes',
    'Enero',
    1,
    2026,
    FALSE,
    FALSE
FROM generate_series(0, 23) h
ON CONFLICT (fecha, hora) DO NOTHING;

-- Insertar tipos de vehículo
INSERT INTO centrally.dim_tipo_vehiculo (codigo_vehiculo, nombre_vehiculo, categoria)
VALUES 
    ('AUTO', 'Automóvil', 'particular'),
    ('MOTO', 'Motocicleta', 'particular'),
    ('BUS', 'Bus', 'publico'),
    ('TAXI', 'Taxi', 'publico'),
    ('CAMION', 'Camión', 'carga')
ON CONFLICT (codigo_vehiculo) DO NOTHING;

-- Insertar tipos de incidente
INSERT INTO centrally.dim_tipo_incidente (codigo_incidente, nombre_incidente, categoria, gravedad)
VALUES 
    ('ACC', 'Accidente de Tránsito', 'accidente', 'grave'),
    ('CONG', 'Congestión Vehicular', 'congestion', 'moderado'),
    ('OBRA', 'Obra en Vía', 'obra', 'leve'),
    ('EVENTO', 'Evento Especial', 'evento', 'moderado')
ON CONFLICT (codigo_incidente) DO NOTHING;

COMMIT;
