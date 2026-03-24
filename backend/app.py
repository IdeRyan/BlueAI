from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, Sensor, Measurement, Alert
from database import init_db, get_or_create_sensor, create_alert, get_active_alerts
from analyse import check_status, Status, _expert  # Import the expert
from config import Config
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI

CORS(app)

db.init_app(app)

# Helper function to convert status to color
def get_color_from_status(status):
    colors = {
        Status.NORMAL.value: "#4CAF50",  # Green
        Status.WARNING.value: "#FF9800",  # Orange
        Status.CRITICAL.value: "#F44336",  # Red
        Status.LEAK.value: "#9C27B0",  # Purple
        Status.UNKNOWN.value: "#9E9E9E"  # Grey
    }
    return colors.get(status, "#9E9E9E")

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'name': 'BlueAI - Leak Detection System',
        'version': '1.0',
        'status': 'operational',
        'endpoints': {
            'GET /': 'This page',
            'POST /api/sensors': 'Register new sensor',
            'POST /api/measurements': 'Send measurement',
            'GET /api/network/status': 'Network status for display',
            'GET /api/alerts': 'List active alerts'
        }
    })

@app.route('/api/sensors', methods=['POST'])
def register_sensor():
    try:
        data = request.json
        
        required = ['id', 'name', 'type', 'location']
        for field in required:
            if field not in data:
                return jsonify({
                    'error': f'Missing field: {field}',
                    'status': 'error'
                }), 400
        
        sensor = get_or_create_sensor(
            sensor_id=data['id'],
            name=data['name'],
            sensor_type=data['type'],
            location=data['location']
        )
        
        return jsonify({
            'message': 'Sensor registered successfully',
            'sensor': sensor.to_dict() if hasattr(sensor, 'to_dict') else {'id': sensor.id},
            'status': 'success'
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/measurements', methods=['POST'])
def add_measurement():
    try:
        data = request.json
        
        if 'sensor_id' not in data:
            return jsonify({'error': 'Missing sensor_id'}), 400
        if 'value' not in data:
            return jsonify({'error': 'Missing value'}), 400
        
        sensor = Sensor.query.get(data['sensor_id'])
        if not sensor:
            return jsonify({
                'error': f'Sensor {data["sensor_id"]} not found',
                'status': 'error'
            }), 404
        
        # 1. Save measurement
        measurement = Measurement(
            sensor_id=data['sensor_id'],
            value=data['value'],
            pump_on=data['pump_on']
        )
        db.session.add(measurement)
        db.session.commit()
        
        # 2. Analyze with expert system
        pump_on = data.get('pump_on', None)
        status_value = check_status(data['value'], pump_on)
        status_enum = next((s for s in Status if s.value == status_value), Status.UNKNOWN)
        
        # 3. Create alert if needed
        alert_created = None
        if status_value in ['leak', 'critical', 'warning']:
            message = _expert.get_status_message(status_enum, data['value'])
            
            alert = create_alert(
                sensor_id=data['sensor_id'],
                alert_type=status_value,
                message=message,
                value=data['value']
            )
            alert_created = alert.id if alert else None
        
        return jsonify({
            'message': 'Measurement saved',
            'measurement_id': measurement.id,
            'status': status_value,
            'alert_created': alert_created,
            'success': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/network/status', methods=['GET'])
def network_status():
    try:
        from sqlalchemy import desc, func
        
        subquery = db.session.query(
            Measurement.sensor_id,
            func.max(Measurement.timestamp).label('max_timestamp')
        ).group_by(Measurement.sensor_id).subquery()
        
        latest_measurements = db.session.query(Measurement).join(
            subquery,
            (Measurement.sensor_id == subquery.c.sensor_id) &
            (Measurement.timestamp == subquery.c.max_timestamp)
        ).all()
        
        sensors_data = []
        for m in latest_measurements:
            pump_on = None
            status_value = check_status(m.value, pump_on)
            status_enum = next((s for s in Status if s.value == status_value), Status.UNKNOWN)
            
            sensors_data.append({
                'id': m.sensor_id,
                'name': m.sensor.name if m.sensor else m.sensor_id,
                'value': m.value,
                'unit': 'L/min',
                'status': status_value,
                'message': _expert.get_status_message(status_enum, m.value),
                'color': get_color_from_status(status_value),
                'timestamp': m.timestamp.isoformat() if m.timestamp else None,
                'location': m.sensor.location if m.sensor else None
            })
        
        alerts = get_active_alerts()
        alerts_data = []
        for a in alerts:
            alerts_data.append({
                'id': a.id,
                'sensor_id': a.sensor_id,
                'type': a.alert_type,
                'message': a.message,
                'value': a.value_at_alert,
                'timestamp': a.timestamp.isoformat() if a.timestamp else None
            })
        
        return jsonify({
            'sensors': sensors_data,
            'alerts': alerts_data,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts_endpoint():
    try:
        alerts = get_active_alerts()
        
        alerts_data = []
        for a in alerts:
            alerts_data.append({
                'id': a.id,
                'sensor_id': a.sensor_id,
                'sensor_name': a.sensor.name if a.sensor else None,
                'type': a.alert_type,
                'message': a.message,
                'value': a.value_at_alert,
                'timestamp': a.timestamp.isoformat() if a.timestamp else None
            })
        
        return jsonify({
            'alerts': alerts_data,
            'count': len(alerts_data),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert_endpoint(alert_id):
    try:
        from database import resolve_alert
        success = resolve_alert(alert_id)
        
        if success:
            return jsonify({
                'message': 'Alert resolved',
                'status': 'success'
            })
        else:
            return jsonify({
                'error': 'Alert not found',
                'status': 'error'
            }), 404
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'BlueAI API operational',
        'database': 'connected',
        'analyzer': 'loaded',
        'status': 'success'
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database initialized")
    
    print("Starting BlueAI server...")
    print("API available at http://localhost:5000")
    print("Endpoints:")
    print("   - POST /api/sensors")
    print("   - POST /api/measurements")
    print("   - GET /api/network/status")
    print("   - GET /api/alerts")
    
    app.run(host='0.0.0.0', port=5000, debug=True)