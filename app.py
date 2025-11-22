import os
import json
import threading
from flask import Flask, jsonify, render_template, request, Response

app = Flask(__name__)

# -------------------------------------------------------
# FILE PATHS
# -------------------------------------------------------
STATE_FILE = "data/state.json"
LATEST_FILE = "data/latest.json"
CALIB_FILE = "data/calibration.csv"
HISTORY_FILE = "data/history.csv"

# -------------------------------------------------------
# STATE MANAGEMENT
# -------------------------------------------------------

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"mode": "normal", "collecting": False, "message": "Reset"}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

# -------------------------------------------------------
# CALIBRATION CONTROL
# -------------------------------------------------------

def toggle_calibration():
    state = load_state()

    if not state["collecting"]:
        state["mode"] = "calibration"
        state["collecting"] = True
        state["message"] = "Calibration started"

        # Remove old calibration file
        if os.path.exists(CALIB_FILE):
            os.remove(CALIB_FILE)

    else:
        state["collecting"] = False
        state["mode"] = "normal"
        state["message"] = "Calibration stopped"

    save_state(state)
    print("CALIBRATION STATE:", state)

# -------------------------------------------------------
# TRAINING CONTROL
# -------------------------------------------------------

def run_training():
    state = load_state()
    state["mode"] = "training"
    state["collecting"] = False
    state["message"] = "Training started"
    save_state(state)

    print("TRAINING STARTED...")

    # ML script call (Pi-side)
    os.system("python train_lstm.py")

    state["mode"] = "normal"
    state["message"] = "Training completed"
    save_state(state)

    print("TRAINING COMPLETE")

# -------------------------------------------------------
# PAGE ROUTES
# -------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")  # Combined Dashboard

@app.route("/flood")
def flood():
    return render_template("flood.html")

@app.route("/landslide")
def landslide():
    return render_template("landslide.html")

@app.route("/camera")
def camera():
    return render_template("camera.html")

# -------------------------------------------------------
# CAMERA STREAM ROUTE — STATIC IMAGE FOR NOW
# -------------------------------------------------------

@app.route("/camera_feed")
def camera_feed():
    """Temporary static image feed."""
    try:
        with open("static/camera.jpg", "rb") as f:
            img = f.read()
        return Response(img, mimetype="image/jpeg")
    except:
        return Response(b"", mimetype="image/jpeg")

# -------------------------------------------------------
# API — MACHINE LEARNING CONTROL
# -------------------------------------------------------

@app.route("/api/calibration/start", methods=["POST"])
def api_start_calibration():
    toggle_calibration()
    return jsonify({"status": "ok", "msg": "Calibration toggled"})

@app.route("/api/train", methods=["POST"])
def api_train():
    threading.Thread(target=run_training, daemon=True).start()
    return jsonify({"status": "ok", "msg": "Training started"})

@app.route("/api/state")
def api_state():
    return jsonify(load_state())

# -------------------------------------------------------
# API — COMBINED DASHBOARD
# -------------------------------------------------------

@app.route("/api/combined")
def api_combined():
    try:
        with open(LATEST_FILE) as f:
            return jsonify(json.load(f))
    except:
        return jsonify({
            "landslide": 0,
            "flood": 0,
            "combined": 0,
            "timestamp": "NA"
        })

# -------------------------------------------------------
# API — FLOOD
# -------------------------------------------------------

@app.route("/api/flood")
def api_flood():
    try:
        with open(LATEST_FILE) as f:
            data = json.load(f)

        return jsonify({
            "labels": [data["timestamp"]],
            "water_level": [data.get("water_level", 0)],
            "rain_intensity": [data.get("rain", 0)],
            "soil_sat": [data.get("soil1", 0)],
            "flood_danger": data.get("flood", 0)
        })

    except:
        return jsonify({"error": True})

# -------------------------------------------------------
# API — LANDSLIDE
# -------------------------------------------------------

@app.route("/api/landslide")
def api_landslide():
    try:
        with open(LATEST_FILE) as f:
            data = json.load(f)

        return jsonify({
            "labels": [data["timestamp"]],
            "soil1": [data.get("soil1", 0)],
            "soil2": [data.get("soil2", 0)],
            "tilt": [data.get("tilt", 0)],
            "vibration": [data.get("vibration", 0)],
            "rain": [data.get("rain", 0)],
            "landslide_danger": data.get("landslide", 0)
        })

    except:
        return jsonify({"error": True})

# -------------------------------------------------------
# API — PI SENDS DATA TO WEB SERVER
# -------------------------------------------------------

latest_data = {}

@app.route("/api/data", methods=["POST"])
def receive_data():
    global latest_data
    latest_data = request.json
    print("Received data from Pi:", latest_data)

    # Save to LATEST_FILE so dashboards update
    try:
        with open(LATEST_FILE, "w") as f:
            json.dump(latest_data, f, indent=4)
    except:
        pass

    return jsonify({"status": "OK"}), 200

@app.route("/api/latest", methods=["GET"])
def send_latest():
    return jsonify(latest_data)

# -------------------------------------------------------
# START SERVER
# -------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

