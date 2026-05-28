"""
═══════════════════════════════════════════════════════════════════
  importar_csv.py
  Importa los 4 CSV de mediciones de la maqueta IoT a Neon
  Ejecutar UNA sola vez:
      python importar_csv.py
═══════════════════════════════════════════════════════════════════

Los CSV tienen estas columnas (con encabezado):
    timestamp,temp,hum,pres,luz,suelo,bomba,manual
"""

import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from extensions import db
from models.lectura import MedicionMaqueta

app = create_app('production')

ARCHIVOS = [
    'datos/mediciones_cafe_20260521.csv',
    'datos/mediciones_cafe_20260522.csv',
    'datos/mediciones_cafe_20260523.csv',
    'datos/mediciones_cafe_20260526.csv',
]

with app.app_context():
    db.create_all()

    total = 0

    for archivo in ARCHIVOS:
        if not os.path.exists(archivo):
            print(f"⚠️  No encontrado: {archivo} — saltando.")
            continue

        df = pd.read_csv(archivo)
        print(f"Leyendo {archivo}: {len(df)} filas.")

        # Limpiar: quitar filas sin timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])

        for _, row in df.iterrows():
            m = MedicionMaqueta(
                timestamp = row['timestamp'].to_pydatetime(),
                temp      = float(row['temp'])   if pd.notna(row['temp'])   else None,
                hum       = float(row['hum'])    if pd.notna(row['hum'])    else None,
                pres      = float(row['pres'])   if pd.notna(row['pres'])   else None,
                luz       = int(row['luz'])      if pd.notna(row['luz'])    else None,
                suelo     = int(row['suelo'])    if pd.notna(row['suelo'])  else None,
                bomba     = int(row['bomba'])    if pd.notna(row['bomba'])  else 0,
                manual    = int(row['manual'])   if pd.notna(row['manual']) else 0,
                fuente    = 'sensor'
            )
            db.session.add(m)
            total += 1

        db.session.commit()
        print(f"  ✓ {archivo} cargado ({len(df)} registros)")

    print(f"\n✅ Importación completada. {total} mediciones cargadas en Neon.")
    print("Corre la app y entra a /maqueta para ver los datos.")