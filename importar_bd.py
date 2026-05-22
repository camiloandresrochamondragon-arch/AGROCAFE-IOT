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

    # --- 1. Leer el CSV ---
    COLUMNAS = ['departamento', 'municipio', 'estacion', 'tipo', 'valor', 'unidad', 'fecha']
    df = pd.read_csv('datos/muestra_mediciones.csv', sep=';', header=None,
                     names=COLUMNAS, encoding='utf-8')
    total_crudo = len(df)
    print(f"Leídas {total_crudo} mediciones crudas del CSV.")

    # --- 2. Limpiar ---
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['valor', 'municipio', 'departamento', 'fecha'])
    df = df[df['valor'] > 0]
    print(f"Quedan {len(df)} mediciones válidas después de limpiar.")

    # --- 3. Redondear la fecha a la hora (para agrupar mediciones de la misma hora) ---
    df['hora'] = df['fecha'].dt.floor('h')

    # --- 4. Separar temperatura y humedad, y promediar por municipio + hora ---
    temp = (df[df['tipo'] == 'TEMPERATURA']
            .groupby(['departamento', 'municipio', 'hora'])['valor']
            .mean().reset_index().rename(columns={'valor': 'temperatura'}))

    hum = (df[df['tipo'] == 'HUMEDAD']
           .groupby(['departamento', 'municipio', 'hora'])['valor']
           .mean().reset_index().rename(columns={'valor': 'humedad'}))

    # --- 5. Unir temperatura y humedad (outer = no se pierde ninguna) ---
    combinado = pd.merge(temp, hum,
                         on=['departamento', 'municipio', 'hora'], how='outer')
    print(f"{len(combinado)} lecturas agrupadas (municipio + hora).")

    # --- 6. Borrar datos viejos ---
    Lectura.query.delete()
    Municipio.query.delete()
    Departamento.query.delete()
    db.session.commit()

    # --- 7. Insertar departamentos ---
    deptos = {}
    for nombre in sorted(combinado['departamento'].dropna().unique()):
        d = Departamento(nombre=nombre)
        db.session.add(d)
        db.session.flush()
        deptos[nombre] = d.id
    db.session.commit()
    print(f"✓ {len(deptos)} departamentos insertados.")

    # --- 8. Insertar municipios ---
    municipios = {}
    pares = combinado[['departamento', 'municipio']].drop_duplicates()
    for _, row in pares.iterrows():
        dep_id = deptos.get(row['departamento'])
        if dep_id is None:
            continue
        clave = (row['departamento'], row['municipio'])
        m = Municipio(nombre=row['municipio'], departamento_id=dep_id)
        db.session.add(m)
        db.session.flush()
        municipios[clave] = m.id
    db.session.commit()
    print(f"✓ {len(municipios)} municipios insertados.")

    # --- 9. Insertar lecturas ---
    n_lec = 0
    for _, row in combinado.iterrows():
        clave = (row['departamento'], row['municipio'])
        mun_id = municipios.get(clave)
        if mun_id is None:
            continue
        temp_val = None if pd.isna(row.get('temperatura')) else round(float(row['temperatura']), 1)
        hum_val = None if pd.isna(row.get('humedad')) else round(float(row['humedad']), 1)
        fecha = row['hora'] if not pd.isna(row['hora']) else datetime.utcnow()
        lectura = Lectura(
            municipio_id=mun_id,
            temperatura=temp_val,
            humedad_suelo=hum_val,
            precipitacion=None,
            ph_suelo=None,
            estado=calcular_estado(hum_val),
            fecha=fecha
        )
        db.session.add(lectura)
        n_lec += 1
        if n_lec % 500 == 0:
            db.session.commit()
            print(f"  ... {n_lec} lecturas insertadas")
    db.session.commit()

    print(f"✓ {n_lec} lecturas insertadas en total.")
    print(f"📊 MEDICIONES CRUDAS PROCESADAS (para el contador): {total_crudo}")
    print("✅ Importación completada.")