from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from extensions import db, login_manager
from config import config
from datetime import datetime

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'

    from routes.auth import auth_bp
    from routes.datos import datos_bp
    from routes.maqueta import maqueta_bp
    from routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(datos_bp, url_prefix='/datos')
    app.register_blueprint(maqueta_bp, url_prefix='/maqueta')

    with app.app_context():
        db.create_all()
        # seed_data()  # Desactivado: ya usamos los datos reales del IDEAM cargados con importar_bd.py

    return app

def seed_data():
    """Insertar datos de ejemplo si la base está vacía.
    (Ya no se llama automáticamente. Los datos reales se cargan con importar_bd.py)
    """
    from models.lectura import Lectura, Municipio, Departamento
    if Departamento.query.count() == 0:
        caldas = Departamento(nombre='Caldas')
        risaralda = Departamento(nombre='Risaralda')
        quindio = Departamento(nombre='Quindío')
        db.session.add_all([caldas, risaralda, quindio])
        db.session.flush()

        municipios = [
            Municipio(nombre='Manizales', departamento_id=caldas.id),
            Municipio(nombre='Chinchiná', departamento_id=caldas.id),
            Municipio(nombre='Villamaría', departamento_id=caldas.id),
            Municipio(nombre='Salamina', departamento_id=caldas.id),
            Municipio(nombre='Neira', departamento_id=caldas.id),
            Municipio(nombre='Pereira', departamento_id=risaralda.id),
            Municipio(nombre='Santa Rosa de Cabal', departamento_id=risaralda.id),
            Municipio(nombre='Marsella', departamento_id=risaralda.id),
            Municipio(nombre='Armenia', departamento_id=quindio.id),
            Municipio(nombre='Montenegro', departamento_id=quindio.id),
            Municipio(nombre='Filandia', departamento_id=quindio.id),
            Municipio(nombre='Salento', departamento_id=quindio.id),
        ]
        db.session.add_all(municipios)
        db.session.flush()

        lecturas_data = [
            (1, 19.2, 72, 165, 6.1, 'Óptimo'),
            (2, 21.5, 58, 142, 5.8, 'Riego requerido'),
            (3, 18.8, 80, 188, 6.3, 'Óptimo'),
            (4, 20.1, 45, 98,  5.5, 'Crítico'),
            (5, 21.8, 61, 148, 5.9, 'Óptimo'),
            (6, 22.3, 65, 130, 6.0, 'Óptimo'),
            (7, 19.9, 74, 175, 6.2, 'Óptimo'),
            (8, 21.0, 52, 110, 5.7, 'Riego requerido'),
            (9, 23.1, 60, 125, 5.9, 'Riego requerido'),
            (10, 22.7, 43, 90, 5.6, 'Crítico'),
            (11, 20.4, 76, 160, 6.1, 'Óptimo'),
            (12, 17.5, 82, 195, 6.4, 'Óptimo'),
        ]
        for mun_id, temp, hum, lluvia, ph, estado in lecturas_data:
            db.session.add(Lectura(
                municipio_id=mun_id,
                temperatura=temp,
                humedad_suelo=hum,
                precipitacion=lluvia,
                ph_suelo=ph,
                estado=estado,
                fecha=datetime.utcnow()
            ))
        db.session.commit()

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True)