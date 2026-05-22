-- ============================================================
--  AgroIoT Eje Cafetero — Esquema SQL de referencia
--  (SQLAlchemy genera esto automáticamente con db.create_all())
--  Úsalo si prefieres gestionar la BD directamente con MySQL/PostgreSQL
-- ============================================================

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id            INTEGER     PRIMARY KEY AUTOINCREMENT,
    nombre        VARCHAR(100) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    departamento  VARCHAR(50),
    rol           VARCHAR(20)  DEFAULT 'usuario',
    activo        BOOLEAN      DEFAULT 1,
    creado_en     DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de departamentos
CREATE TABLE IF NOT EXISTS departamentos (
    id     INTEGER      PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(80)  NOT NULL
);

-- Tabla de municipios
CREATE TABLE IF NOT EXISTS municipios (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,
    nombre          VARCHAR(100) NOT NULL,
    departamento_id INTEGER     NOT NULL,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
);

-- Tabla de lecturas IoT (histórico)
CREATE TABLE IF NOT EXISTS lecturas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    municipio_id   INTEGER NOT NULL,
    temperatura    REAL,
    humedad_suelo  REAL,
    precipitacion  REAL,
    ph_suelo       REAL,
    estado         VARCHAR(30),
    fecha          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (municipio_id) REFERENCES municipios(id)
);

-- Tabla de nodos de la maqueta (lecturas en tiempo real)
CREATE TABLE IF NOT EXISTS nodos_maqueta (
    id             INTEGER      PRIMARY KEY AUTOINCREMENT,
    nodo_nombre    VARCHAR(50),
    ubicacion      VARCHAR(100),
    humedad_suelo  REAL,
    temperatura    REAL,
    ph_suelo       REAL,
    precipitacion  REAL,
    activo         BOOLEAN  DEFAULT 1,
    ultima_lectura DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── Datos semilla ─────────────────────────────────────────────────────────────

INSERT INTO departamentos (nombre) VALUES ('Caldas'), ('Risaralda'), ('Quindío');

INSERT INTO municipios (nombre, departamento_id) VALUES
    ('Manizales',          1),
    ('Chinchiná',          1),
    ('Villamaría',         1),
    ('Salamina',           1),
    ('Neira',              1),
    ('Pereira',            2),
    ('Santa Rosa de Cabal',2),
    ('Marsella',           2),
    ('Armenia',            3),
    ('Montenegro',         3),
    ('Filandia',           3),
    ('Salento',            3);

INSERT INTO lecturas (municipio_id, temperatura, humedad_suelo, precipitacion, ph_suelo, estado) VALUES
    (1,  19.2, 72, 165, 6.1, 'Óptimo'),
    (2,  21.5, 58, 142, 5.8, 'Riego requerido'),
    (3,  18.8, 80, 188, 6.3, 'Óptimo'),
    (4,  20.1, 45, 98,  5.5, 'Crítico'),
    (5,  21.8, 61, 148, 5.9, 'Óptimo'),
    (6,  22.3, 65, 130, 6.0, 'Óptimo'),
    (7,  19.9, 74, 175, 6.2, 'Óptimo'),
    (8,  21.0, 52, 110, 5.7, 'Riego requerido'),
    (9,  23.1, 60, 125, 5.9, 'Riego requerido'),
    (10, 22.7, 43, 90,  5.6, 'Crítico'),
    (11, 20.4, 76, 160, 6.1, 'Óptimo'),
    (12, 17.5, 82, 195, 6.4, 'Óptimo');

INSERT INTO nodos_maqueta (nodo_nombre, ubicacion, humedad_suelo, temperatura, ph_suelo, precipitacion) VALUES
    ('Nodo A', 'Chinchiná, Caldas',    58.0, 21.5, 5.8, 2.3),
    ('Nodo B', 'Pereira, Risaralda',   72.0, 22.3, 6.0, 0.0),
    ('Nodo C', 'Salento, Quindío',     82.0, 17.5, 6.4, 5.1),
    ('Nodo D', 'Armenia, Quindío',     43.0, 23.1, 5.6, 0.0);
