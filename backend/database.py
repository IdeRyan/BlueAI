from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialisation de SQLAlchemy
# Cet objet db sera importé dans app.py
db = SQLAlchemy()

class Sensor(db.Model):
    __tablename__ = 'sensors'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    unit = db.Column(db.String(10))
    description = db.Column(db.Text)
    
    measurements = db.relationship('Measurement', backref='sensor', lazy=True, cascade='all, delete-orphan')
    
    alerts = db.relationship('Alert', backref='sensor', lazy=True, cascade='all, delete-orphan')
    

    #representation de l'object
    def __repr__(self):
        return f'<Sensor {self.id}: {self.name}>'
    

    #conversion de l'objet en dictionnaire
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'location': self.location,
            'active': self.active,
            'unit': self.unit,
            'description': self.description
        }

class Measurement(db.Model):

    __tablename__ = 'measurements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.String(50), db.ForeignKey('sensors.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    

    def __repr__(self):
        return f'<Measurement {self.id}: {self.sensor_id} = {self.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sensor_name': self.sensor.name if self.sensor else None
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.String(50), db.ForeignKey('sensors.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), default='warning')
    message = db.Column(db.Text)
    value_at_alert = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        status = "résolue" if self.resolved else "active"
        return f'<Alert {self.id}: {self.sensor_id} - {self.alert_type} ({status})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'sensor_name': self.sensor.name if self.sensor else None,
            'type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'value': self.value_at_alert,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by
        }

#autres fonctions
def init_db(app):
    with app.app_context():
        db.create_all()
        print("Base de données initialisée (tables créées si nécessaire)")

#Récupère un capteur s'il existe, le crée sinon pour éviter les doublons
def get_or_create_sensor(sensor_id, name, sensor_type, location, unit=None, description=None):
    sensor = Sensor.query.get(sensor_id)
    if not sensor:
        sensor = Sensor(
            id=sensor_id,
            name=name,
            type=sensor_type,
            location=location,
            unit=unit,
            description=description
        )
        db.session.add(sensor)
        db.session.commit()
        print(f"Capteur {sensor_id} créé")
    else:
        print(f"Capteur {sensor_id} déjà existant")
    return sensor

def create_alert(sensor_id, alert_type, message, value=None, severity='warning'):
    alert = Alert(
        sensor_id=sensor_id,
        alert_type=alert_type,
        severity=severity,
        message=message,
        value_at_alert=value
    )
    db.session.add(alert)
    db.session.commit()
    print(f" ALERTE: {sensor_id} - {alert_type} ({value})")
    return alert

def get_active_alerts():
    return Alert.query.filter_by(resolved=False).order_by(Alert.timestamp.desc()).all()

def resolve_alert(alert_id, resolved_by=None):
    alert = Alert.query.get(alert_id)
    if alert:
        alert.resolved = True
        alert.resolved_at = datetime.now()
        alert.resolved_by = resolved_by
        db.session.commit()
        print(f"  ✓ Alerte {alert_id} résolue")
        return True
    return False