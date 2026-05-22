# AgroIoT Eje Cafetero 🌿☕

Plataforma web de monitoreo de riego inteligente para cultivos de café en Caldas, Risaralda y Quindío, construida con Flask + SQLAlchemy.

---

## Estructura del proyecto

```
agrocafe_iot/
├── app.py                  ← Punto de entrada + factory function
├── config.py               ← Configuraciones (dev / prod)
├── extensions.py           ← Instancias de db y login_manager
├── database.sql            ← Esquema SQL de referencia
├── requirements.txt        ← Dependencias Python
├── .env.example            ← Variables de entorno (copiar como .env)
│
├── models/
│   ├── __init__.py         ← Exporta todos los modelos
│   ├── user.py             ← Modelo Usuario
│   └── lectura.py          ← Modelos Departamento, Municipio, Lectura, NodoMaqueta
│
├── routes/
│   ├── __init__.py
│   ├── main.py             ← Ruta principal (/)
│   ├── auth.py             ← Login, registro, recuperación, logout
│   ├── datos.py            ← Datos IoT + API JSON
│   └── maqueta.py          ← Maqueta prototipo + API para ESP32
│
├── templates/
│   ├── base.html           ← Layout maestro (nav, flash, footer)
│   ├── index.html          ← Página de inicio
│   ├── datos.html          ← Tabla filtrable + Power BI
│   ├── maqueta.html        ← Nodos en tiempo real
│   ├── login.html          ← Login / Registro / Recuperar contraseña
│   └── partials/
│       └── casas_svg.html  ← Ilustración casas del Eje
│
└── static/
    ├── css/
    │   └── styles.css      ← Todos los estilos
    ├── js/
    │   ├── main.js         ← Utilidades globales
    │   ├── dashboard.js    ← Lógica filtros + tabla + KPIs
    │   └── auth.js         ← Tabs login / toggle contraseña
    └── img/                ← Fotos de cultivos y paisajes
```

---

## Cómo ejecutar el proyecto

### 1. Clonar y entrar al proyecto
```bash
git clone https://github.com/tu-usuario/agrocafe-iot.git
cd agrocafe_iot
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus valores
```

### 5. Ejecutar
```bash
python app.py
```

La app queda disponible en **http://localhost:5000**

---

## API endpoints

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/datos/api/lecturas` | Lecturas con filtros opcionales |
| GET | `/datos/api/municipios` | Municipios por departamento |
| POST | `/datos/api/lectura/nueva` | Registrar nueva lectura (sensor) |
| GET | `/maqueta/api/nodos` | Estado actual de nodos |
| POST | `/maqueta/api/nodo/update` | ESP32 envía datos aquí |

### Parámetros de `/datos/api/lecturas`
```
?departamento=Caldas&municipio=Chinchiná&estado=Óptimo
```

### Body para el ESP32 (`POST /maqueta/api/nodo/update`)
```json
{
  "nodo_nombre":   "Nodo A",
  "ubicacion":     "Chinchiná, Caldas",
  "humedad_suelo": 65.3,
  "temperatura":   21.5,
  "ph_suelo":      5.8,
  "precipitacion": 2.1
}
```

---

## Conectar Power BI

1. Publica tu reporte en **Power BI Service**
2. Abre el reporte → Archivo → **Publicar en web**
3. Copia el `<iframe>` generado
4. En `templates/datos.html`, reemplaza cada `<div class="pbi-placeholder">` por el `<iframe>`
