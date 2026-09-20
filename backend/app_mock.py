import csv
import os
import random
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_DIR = "./data"
HISTORY_SIZE = 100
POLL_INTERVAL_SEC = 1  # 1 mesure par seconde

current_mode = "normal"           # "normal" | "leak" | "off"
mode_index = {"normal": 0, "leak": 0, "off": 0}  # index dans chaque CSV
measurement_counter = 0
history = []
mode_data = {}                    # contiendra les 3 listes de lignes



def load_csv(filename):
    """Charge un CSV et retourne une liste de dicts {flow1, flow2, label}."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier introuvable : {filepath}")

    rows = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "flow1": float(row["flow1"]),
                "flow2": float(row["flow2"]),
                "label": int(row["label"]),
            })
    return rows


def load_all_data():
    """Charge les 3 fichiers CSV en mémoire."""
    global mode_data
    mode_data = {
        "normal": load_csv("sim_normal.csv"),
        "leak": load_csv("sim_leak.csv"),
        "off": load_csv("sim_off.csv"),
    }
    for mode, rows in mode_data.items():
        print(f"✅ {mode}.csv chargé : {len(rows)} lignes")


def compute_features_from_buffer(buffer):
    """
    Calcule les 5 features à partir d'un buffer de 5 mesures.
    Chaque mesure est un dict {flow1, flow2}.
    """
    flow1_values = [m["flow1"] for m in buffer]
    flow2_values = [m["flow2"] for m in buffer]

    flow1_avg = sum(flow1_values) / len(flow1_values)
    flow2_avg = sum(flow2_values) / len(flow2_values)

    flow2_mean = flow2_avg
    flow2_var = sum((x - flow2_mean) ** 2 for x in flow2_values) / len(flow2_values)

    flow_diff = flow1_avg - flow2_avg
    flow_ratio = flow2_avg / flow1_avg if flow1_avg > 0.01 else 0

    return {
        "flow1_avg": round(flow1_avg, 4),
        "flow2_avg": round(flow2_avg, 4),
        "flow_diff": round(flow_diff, 4),
        "flow_ratio": round(flow_ratio, 4),
        "flow2_var": round(flow2_var, 6),
    }


def build_state_from_row(row, measurement_id):
    """
    Transforme une ligne CSV {flow1, flow2, label} en objet state complet.
    """
    now = datetime.now().isoformat()

    # Pour le state, on simule un buffer de 5 mesures identiques
    # (pour que compute_features donne des valeurs cohérentes)
    buffer = [row] * 5
    features = compute_features_from_buffer(buffer)

    # Confidence simulée
    if row["label"] == 1:
        confidence = round(random.uniform(0.85, 0.98), 2)
    else:
        confidence = round(random.uniform(0.90, 0.99), 2)

    return {
        "id": measurement_id,
        "measurement_id": measurement_id,
        "label": row["label"],
        "confidence": confidence,
        "flow1_avg": features["flow1_avg"],
        "flow2_avg": features["flow2_avg"],
        "flow_diff": features["flow_diff"],
        "flow_ratio": features["flow_ratio"],
        "flow2_var": features["flow2_var"],
        "timestamp": now,
        "flow1": row["flow1"],
        "flow2": row["flow2"],
    }


def build_initial_history():
    """
    Génère 100 prédictions simulées dans le passé (basées sur le mode normal).
    """
    global history
    history = []
    now = datetime.now()
    normal_data = mode_data["normal"]

    for i in range(HISTORY_SIZE):
        ts = (now - timedelta(seconds=HISTORY_SIZE - i)).isoformat()
        row = normal_data[i % len(normal_data)]

        # Parfois on met un leak dans l'historique pour la variété
        if i % 15 == 0:
            row = mode_data["leak"][i % len(mode_data["leak"])]

        buffer = [row] * 5
        features = compute_features_from_buffer(buffer)

        confidence = round(random.uniform(0.85, 0.99), 2)

        history.append({
            "id": i + 1,
            "measurement_id": i + 1,
            "label": row["label"],
            "confidence": confidence,
            "flow1_avg": features["flow1_avg"],
            "flow2_avg": features["flow2_avg"],
            "flow_diff": features["flow_diff"],
            "flow_ratio": features["flow_ratio"],
            "flow2_var": features["flow2_var"],
            "timestamp": ts,
            "flow1": row["flow1"],
            "flow2": row["flow2"],
        })


def get_next_row():
    """
    Retourne la prochaine ligne du CSV correspondant au mode actif,
    et incrémente l'index (avec bouclage).
    """
    global mode_index
    data = mode_data[current_mode]
    idx = mode_index[current_mode]
    row = data[idx]
    mode_index[current_mode] = (idx + 1) % len(data)
    return row


@app.route("/api/state", methods=["GET"])
def get_state():
    """
    Retourne l'état actuel basé sur le mode actif.
    - Si mode == "off" : retourne un status "pump_off"
    - Sinon : retourne un state normal (label 0 ou 1)
    """
    global measurement_counter
    measurement_counter += 1

    row = get_next_row()

    # Cas spécial : pompe éteinte
    if current_mode == "off":
        state = build_state_from_row(row, measurement_counter)
        return jsonify({
            "status": "pump_off",
            "message": "Pump appears to be off",
            "flow1_avg": state["flow1_avg"],
            "state": state,
        })

    state = build_state_from_row(row, measurement_counter)

    # Ajoute à l'historique
    history.append(state)
    if len(history) > HISTORY_SIZE:
        history.pop(0)

    return jsonify({"state": state})


@app.route("/api/history", methods=["GET"])
def get_history():
    """Retourne les 100 dernières prédictions."""
    return jsonify({"history": history})


@app.route("/api/measurements", methods=["POST"])
def add_measurement():
    """
    Simule la réception d'une mesure ESP32.
    Retourne une prédiction basée sur le mode actif.
    """
    global measurement_counter
    measurement_counter += 1

    data = request.get_json()
    if not data or "flow1" not in data or "flow2" not in data:
        return jsonify({"error": "Missing flow1 or flow2"}), 400

    # Simule un délai de "5 mesures nécessaires"
    if measurement_counter < 5:
        return jsonify({
            "status": "waiting",
            "message": "Need 5 measurements",
        })

    row = get_next_row()

    if current_mode == "off":
        return jsonify({
            "status": "pump_off",
            "message": "Pump appears to be off",
        })

    confidence = round(random.uniform(0.85, 0.99), 2)

    return jsonify({
        "label": row["label"],
        "confidence": confidence,
        "measurement_id": measurement_counter,
    })


@app.route("/api/mode", methods=["GET"])
def get_mode():
    """Retourne le mode actif."""
    return jsonify({"mode": current_mode})


@app.route("/api/mode", methods=["POST"])
def set_mode():
    """
    Change le mode actif.
    Body attendu : {"mode": "normal"} ou {"mode": "leak"} ou {"mode": "off"}
    """
    global current_mode, mode_index

    data = request.get_json()
    if not data or "mode" not in data:
        return jsonify({"error": "Missing 'mode' field"}), 400

    new_mode = data["mode"]
    if new_mode not in ["normal", "leak", "off"]:
        return jsonify({
            "error": f"Invalid mode '{new_mode}'. Must be 'normal', 'leak' or 'off'.",
        }), 400

    current_mode = new_mode
    mode_index[new_mode] = 0  # Réinitialise l'index du mode

    print(f"🔄 Mode changé : {new_mode}")

    return jsonify({
        "status": "success",
        "mode": current_mode,
    })


@app.route("/api/health", methods=["GET"])
def health():
    """Endpoint de santé."""
    return jsonify({
        "status": "ok",
        "mode": current_mode,
        "measurement_counter": measurement_counter,
        "history_size": len(history),
    })


# ------------------------------------------------------------------
# Lancement
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("BlueAi server started")
    print("   Loading CSV...")
    load_all_data()
    build_initial_history()
    print(f"   Historique initial : {len(history)} prédictions")
    print()
    print("   Endpoints :")
    print("   - GET  /api/state")
    print("   - GET  /api/history")
    print("   - POST /api/measurements")
    print("   - GET  /api/mode")
    print("   - POST /api/mode")
    print("   - GET  /api/health")
    print()
    app.run(host="0.0.0.0", port=5000, debug=True)