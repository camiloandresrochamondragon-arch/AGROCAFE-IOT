from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from models.lectura import MedicionMaqueta, NodoMaqueta
from extensions import db
from datetime import datetime

maqueta_bp = Blueprint('maqueta', __name__)


@maqueta_bp.route('/')
@login_required
def index():
    # Última lectura de cada sensor para los KPIs
    ultima = MedicionMaqueta.query.order_by(
        MedicionMaqueta.timestamp.desc()
    ).first()

    # Resumen estadístico de todas las mediciones
    from sqlalchemy import func
    stats = db.session.query(
        func.avg(MedicionMaqueta.temp).label('temp_prom'),
        func.avg(MedicionMaqueta.hum).label('hum_prom'),
        func.avg(MedicionMaqueta.suelo).label('suelo_prom'),
        func.avg(MedicionMaqueta.pres).label('pres_prom'),
        func.min(MedicionMaqueta.temp).label('temp_min'),
        func.max(MedicionMaqueta.temp).label('temp_max'),
        func.count(MedicionMaqueta.id).label('total'),
    ).first()

    return render_template(
        'maqueta.html',
        titulo='Maqueta IoT',
        ultima=ultima,
        stats=stats
    )


@maqueta_bp.route('/api/mediciones')
@login_required
def api_mediciones():
    limit  = request.args.get('limit', 100, type=int)
    fecha_desde = request.args.get('desde', '')
    fecha_hasta = request.args.get('hasta', '')

    query = MedicionMaqueta.query

    if fecha_desde:
        try:
            query = query.filter(MedicionMaqueta.timestamp >= datetime.strptime(fecha_desde, '%Y-%m-%d'))
        except ValueError:
            pass
    if fecha_hasta:
        try:
            from datetime import timedelta
            hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(MedicionMaqueta.timestamp < hasta)
        except ValueError:
            pass

    registros = query.order_by(MedicionMaqueta.timestamp.desc()).limit(limit).all()
    registros.reverse()
    return jsonify([r.to_dict() for r in registros])


@maqueta_bp.route('/api/ultima')
@login_required
def api_ultima():
    """Última lectura — para el polling de actualización en tiempo real."""
    ultima = MedicionMaqueta.query.order_by(
        MedicionMaqueta.timestamp.desc()
    ).first()
    if not ultima:
        return jsonify({'error': 'Sin datos'}), 404
    return jsonify(ultima.to_dict())


@maqueta_bp.route('/api/nueva', methods=['POST'])
def nueva_medicion():
    """
    El ESP32 envía aquí sus lecturas en tiempo real.
    POST JSON:
    {
      "temp": 22.5, "hum": 70.1, "pres": 753.0,
      "luz": 85, "suelo": 72, "bomba": 0, "manual": 0
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Sin datos'}), 400

    m = MedicionMaqueta(
        timestamp = datetime.utcnow(),
        temp      = data.get('temp'),
        hum       = data.get('hum'),
        pres      = data.get('pres'),
        luz       = data.get('luz'),
        suelo     = data.get('suelo'),
        bomba     = int(data.get('bomba', 0)),
        manual    = int(data.get('manual', 0)),
        fuente    = 'sensor'
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({'ok': True, 'id': m.id}), 201