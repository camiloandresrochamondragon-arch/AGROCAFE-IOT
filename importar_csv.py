"""
═══════════════════════════════════════════════════════════════════
  importar_bd.py
  Importa datos\muestra_mediciones.csv a agrocafe.db
  Ejecutar UNA sola vez:
      python importar_bd.py
═══════════════════════════════════════════════════════════════════

El CSV tiene separador ; y estas columnas (sin encabezado):
    Departamento;Municipio;NombreEstacion;TipoMedicion;Valor;Unidad;FechaObservacion
"""

import pandas as pd
from datetime import datetime
from app import create_app
from extensions import db
from models.lectura import Departamento, Municipio, Lectura

app = create_app('development')


def calcular_estado(humedad):
    if humedad is None or humedad <= 0:
        return 'Sin señal'
    elif humedad < 40:
        return 'Crítico'
    elif humedad < 60:
        return 'Riego requerido'
    else:
        return 'Óptimo'


with app.app_context():
    db.create_all()

    # ── Leer CSV ──────────────────────────────────────────────────
    COLUMNAS = ['departamento', 'municipio', 'estacion',
                'tipo', 'valor', 'unidad', 'fecha']

    df = pd.read_csv(
        'datos/muestra_mediciones.csv',
        sep=';',
        header=None,
        names=COLUMNAS,
        encoding='utf-8',
    )
    print(f"Leídas {len(df)} filas del CSV.")

    # ── Limpiar: quitar valor 0 y nulos ───────────────────────────
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df = df[df['valor'] > 0].dropna(subset=['valor', 'municipio'])
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    print(f"Quedan {len(df)} filas después de limpiar.\n")

    # ── Pivotear: una fila por (municipio, fecha) con temp y hum ──
    # Separar humedad y temperatura en columnas distintas
    hum  = df[df['tipo'] == 'HUMEDAD'][['departamento', 'municipio', 'fecha', 'valor']]\
             .rename(columns={'valor': 'humedad'})
    temp = df[df['tipo'] == 'TEMPERATURA'][['municipio', 'fecha', 'valor']]\
             .rename(columns={'valor': 'temperatura'})

    # Unir por municipio + fecha exacta
    combinado = pd.merge(hum, temp, on=['municipio', 'fecha'], how='left')
    print(f"{len(combinado)} lecturas combinadas (humedad + temperatura).\n")

    # ── Limpiar tabla previa ───────────────────────────────────────
    Lectura.query.delete()
    Municipio.query.delete()
    Departamento.query.delete()
    db.session.commit()

    # ── Insertar Departamentos ─────────────────────────────────────
    deptos = {}
    for nombre in sorted(combinado['departamento'].dropna().unique()):
        d = Departamento(nombre=nombre)
        db.session.add(d)
        db.session.flush()
        deptos[nombre] = d.id
    db.session.commit()
    print(f"✓ {len(deptos)} departamentos insertados.")

    # ── Insertar Municipios (únicos) ───────────────────────────────
    municipios = {}
    for _, row in combinado.drop_duplicates(subset=['municipio']).iterrows():
        dep_id = deptos.get(row['departamento'])
        if dep_id is None:
            continue
        m = Municipio(nombre=row['municipio'], departamento_id=dep_id)
        db.session.add(m)
        db.session.flush()
        municipios[row['municipio']] = m.id
    db.session.commit()
    print(f"✓ {len(municipios)} municipios insertados.")

    # ── Insertar Lecturas ──────────────────────────────────────────
    n_lec = 0
    for _, row in combinado.iterrows():
        mun_id = municipios.get(row['municipio'])
        if mun_id is None:
            continue

        hum_val  = None if pd.isna(row.get('humedad'))      else float(row['humedad'])
        temp_val = None if pd.isna(row.get('temperatura'))  else float(row['temperatura'])
        fecha    = row['fecha'] if not pd.isna(row['fecha']) else datetime.utcnow()

        lectura = Lectura(
            municipio_id  = mun_id,
            temperatura   = temp_val,
            humedad_suelo = hum_val,
            precipitacion = None,
            ph_suelo      = None,
            estado        = calcular_estado(hum_val),
            fecha         = fecha,
        )
        db.session.add(lectura)
        n_lec += 1

        # Commit cada 500 filas para no saturar memoria
        if n_lec % 500 == 0:
            db.session.commit()
            print(f"  ... {n_lec} lecturas insertadas")

    db.session.commit()
    print(f"✓ {n_lec} lecturas insertadas.")
    print("\n✅ Importación completada. Corre 'python app.py' y entra a /datos")