from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from models.lectura import Lectura, Municipio, Departamento
from sqlalchemy import func

datos_bp = Blueprint('datos', __name__)

# Mediciones crudas del IDEAM que se procesaron para generar las lecturas.
# (Es el número que imprime importar_bd.py: "MEDICIONES CRUDAS PROCESADAS")
MEDICIONES_CRUDAS_IDEAM = 100000

# Cuántas lecturas se muestran por página en la tabla
POR_PAGINA = 50


@datos_bp.route('/')
@login_required
def index():
    departamentos = Departamento.query.order_by(Departamento.nombre).all()
    return render_template(
        'datos.html',
        titulo='Datos IoT',
        departamentos=departamentos
    )


@datos_bp.route('/api/lecturas')
@login_required
def api_lecturas():
    """
    API JSON para la tabla — recibe filtros por query string:
    ?departamento=Caldas&municipio=Manizales&estado=Óptimo&pagina=1
    """

    dept_nombre = request.args.get('departamento', '')
    mun_nombre = request.args.get('municipio', '')
    estado = request.args.get('estado', '')
    try:
        pagina = int(request.args.get('pagina', 1))
    except ValueError:
        pagina = 1
    if pagina < 1:
        pagina = 1

    query = (
        Lectura.query
        .join(Municipio)
        .join(Departamento)
        .order_by(Lectura.fecha.desc())
    )

    # ─────────────────────────────────────────────
    # FILTROS
    # ─────────────────────────────────────────────
    if dept_nombre:
        query = query.filter(Departamento.nombre == dept_nombre)

    if mun_nombre:
        query = query.filter(Municipio.nombre == mun_nombre)

    if estado:
        query = query.filter(Lectura.estado == estado)

    # ─────────────────────────────────────────────
    # KPIs — se calculan sobre TODAS las lecturas filtradas
    # (no solo la página visible), con promedios en la base de datos.
    # ─────────────────────────────────────────────
    total_lecturas = query.count()

    # Para los promedios quitamos el ORDER BY (PostgreSQL no permite
    # ordenar por una columna que no está en el agregado).
    agg = query.order_by(None).with_entities(
        func.avg(Lectura.temperatura),
        func.avg(Lectura.humedad_suelo),
        func.avg(Lectura.precipitacion),
        func.avg(Lectura.ph_suelo),
    ).first()

    criticas = query.order_by(None).filter(Lectura.estado == 'Crítico').count()

    def r(v):
        return round(v, 1) if v is not None else 0

    kpis = {
        'temp_prom': r(agg[0]),
        'hum_prom': r(agg[1]),
        'lluvia_prom': r(agg[2]),
        'ph_prom': r(agg[3]),
        'total_sensores': total_lecturas,
        'lecturas_criticas': criticas,
    }

    # ─────────────────────────────────────────────
    # PAGINACIÓN — solo se envían POR_PAGINA lecturas
    # ─────────────────────────────────────────────
    total_paginas = max(1, (total_lecturas + POR_PAGINA - 1) // POR_PAGINA)
    if pagina > total_paginas:
        pagina = total_paginas

    lecturas = (
        query
        .offset((pagina - 1) * POR_PAGINA)
        .limit(POR_PAGINA)
        .all()
    )

    # ─────────────────────────────────────────────
    # RESPUESTA JSON
    # ─────────────────────────────────────────────
    return jsonify({
        'lecturas': [l.to_dict() for l in lecturas],
        'kpis': kpis,
        'paginacion': {
            'pagina': pagina,
            'total_paginas': total_paginas,
            'total_lecturas': total_lecturas,
            'por_pagina': POR_PAGINA,
        },
        'mediciones_crudas': MEDICIONES_CRUDAS_IDEAM,
    })


@datos_bp.route('/api/municipios')
@login_required
def api_municipios():
    """
    Devuelve municipios filtrados por departamento
    para el select dinámico.
    """

    dept_nombre = request.args.get('departamento', '')

    query = Municipio.query.join(Departamento)

    if dept_nombre:
        query = query.filter(
            Departamento.nombre == dept_nombre
        )

    municipios = query.order_by(
        Municipio.nombre
    ).all()

    return jsonify([
        m.to_dict()
        for m in municipios
    ])


@datos_bp.route('/api/lectura/nueva', methods=['POST'])
def nueva_lectura():
    """
    Endpoint para ESP32 / Arduino.

    POST JSON:
    {
        municipio_id,
        temperatura,
        humedad_suelo,
        precipitacion,
        ph_suelo,
        estado
    }
    """

    data = request.get_json()

    if not data:
        return jsonify({
            'error': 'Sin datos'
        }), 400

    from extensions import db
    from datetime import datetime

    lectura = Lectura(
        municipio_id=data.get('municipio_id'),
        temperatura=data.get('temperatura'),
        humedad_suelo=data.get('humedad_suelo'),
        precipitacion=data.get('precipitacion'),
        ph_suelo=data.get('ph_suelo'),
        estado=data.get('estado', 'Óptimo'),
        fecha=datetime.utcnow()
    )

    db.session.add(lectura)
    db.session.commit()

    return jsonify({
        'ok': True,
        'id': lectura.id
    }), 201