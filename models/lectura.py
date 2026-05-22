from extensions import db
from datetime import datetime


class Departamento(db.Model):
    __tablename__ = 'departamentos'
    id      = db.Column(db.Integer, primary_key=True)
    nombre  = db.Column(db.String(80), nullable=False)
    municipios = db.relationship('Municipio', backref='departamento', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'nombre': self.nombre}


class Municipio(db.Model):
    __tablename__ = 'municipios'
    id              = db.Column(db.Integer, primary_key=True)
    nombre          = db.Column(db.String(100), nullable=False)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=False)
    lecturas        = db.relationship('Lectura', backref='municipio', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'departamento': self.departamento.nombre
        }


class Lectura(db.Model):
    __tablename__ = 'lecturas'
    id             = db.Column(db.Integer, primary_key=True)
    municipio_id   = db.Column(db.Integer, db.ForeignKey('municipios.id'), nullable=False)
    temperatura    = db.Column(db.Float)
    humedad_suelo  = db.Column(db.Float)
    precipitacion  = db.Column(db.Float)
    ph_suelo       = db.Column(db.Float)
    estado         = db.Column(db.String(30))
    fecha          = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':            self.id,
            'municipio':     self.municipio.nombre,
            'departamento':  self.municipio.departamento.nombre,
            'temperatura':   self.temperatura,
            'humedad_suelo': self.humedad_suelo,
            'precipitacion': self.precipitacion,
            'ph_suelo':      self.ph_suelo,
            'estado':        self.estado,
            'fecha':         self.fecha.strftime('%Y-%m-%d %H:%M')
        }


class NodoMaqueta(db.Model):
    __tablename__ = 'nodos_maqueta'
    id             = db.Column(db.Integer, primary_key=True)
    nodo_nombre    = db.Column(db.String(50))
    ubicacion      = db.Column(db.String(100))
    humedad_suelo  = db.Column(db.Float)
    temperatura    = db.Column(db.Float)
    ph_suelo       = db.Column(db.Float)
    precipitacion  = db.Column(db.Float)
    activo         = db.Column(db.Boolean, default=True)
    ultima_lectura = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':            self.id,
            'nodo':          self.nodo_nombre,
            'ubicacion':     self.ubicacion,
            'humedad_suelo': self.humedad_suelo,
            'temperatura':   self.temperatura,
            'ph_suelo':      self.ph_suelo,
            'precipitacion': self.precipitacion,
            'activo':        self.activo,
        }


class MedicionMaqueta(db.Model):
    __tablename__ = 'mediciones_maqueta'
    id        = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    temp      = db.Column(db.Float)
    hum       = db.Column(db.Float)
    pres      = db.Column(db.Float)
    luz       = db.Column(db.Integer)
    suelo     = db.Column(db.Integer)
    bomba     = db.Column(db.Integer, default=0)
    manual    = db.Column(db.Integer, default=0)
    fuente    = db.Column(db.String(20), default='sensor')

    def to_dict(self):
        return {
            'id':        self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'temp':      self.temp,
            'hum':       self.hum,
            'pres':      self.pres,
            'luz':       self.luz,
            'suelo':     self.suelo,
            'bomba':     self.bomba,
            'manual':    self.manual,
        }