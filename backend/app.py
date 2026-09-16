from flask import Flask, jsonify, request
from db import insert_prediction, get_5_last_measurements, insert_measurement, get_history, get_latest_prediction
from features import compute_feature
from model import predict
from flask_cors import CORS
from utils import row_to_dict

app = Flask(__name__)
CORS(app)

@app.route("/api/measurements", methods = ["POST"])
def add_measurement():
    data = request.get_json()
    # check if the esp hasn't sent any data or incorrect format
    if not data or "flow1" not in data or "flow2" not in data:
        return jsonify({"error": "Missing flow1 or flow2"}), 400
    
    flow1, flow2 = data["flow1"], data["flow2"]
    measurement_id = insert_measurement(flow1, flow2)

    last_measurements = get_5_last_measurements()
    if len(last_measurements) < 5:
        return jsonify({"status": "waiting", "message": "Need 5 measurements"})

    features = compute_feature(last_measurements)

    # Verify if the pump is off then return directly a specific class
    if features[0] < 0.1:
        insert_prediction(measurement_id, -1, 1.0, *features)
        return jsonify({
            "status": "pump_off",
            "message": "Pump appears to be off",
            "flow1_avg": float(features[0])
        })
    label, confidence = predict(features)
    insert_prediction(measurement_id, label, confidence, *features)

    return jsonify({    
        "label": int(label),
        "confidence": float(confidence),
        "measurement_id": measurement_id
    })

@app.route("/api/history", methods = ["GET"])
def history():
    rows = get_history(100)
    history = [row_to_dict(row) for row in rows]
    return jsonify({"history": history})

@app.route("/api/state", methods = ["GET"])
def get_actual_state():
    state = get_latest_prediction()
    if state is None:
        return jsonify({"state": None, "message": "No prediction yet"})
    return jsonify({"state": row_to_dict(state)})

