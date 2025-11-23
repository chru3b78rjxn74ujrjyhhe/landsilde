import os
import json
import threading
from flask import Flask, jsonify, render_template, Response, request

app = Flask(__name__)

# -------------------------------------------------------
# FILE PATHS
# -------------------------------------------------------
LATEST_FILE = "data/latest.json"
STATE_FILE = "data/state.json"
CALIB_FILE = "data/calibration.csv"
HISTORY_FILE = "data/history.csv"

os.makedirs("data", exist_ok=True)


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

        if os.path.exists(CALIB_FILE):
            os.remove(CALIB_FILE)

    else:
        state["collecting"] = False
        state["mode"] = "normal"
        state["message"] = "Calibration stopped"

    save_state(state)


# -------------------------------------------------------
# TRAINING CONTROL
# -------------------------------------------------------

def run_training():
    state = load_state()
    state["mode"] = "training"
    state["collecting"] = False
    state["message"] = "Training started"
    save_state(state)

    os.system("python3 train_lstm.py")

    state["mode"] = "normal"
    state["message"] = "Training completed"
    save_state(state)


# -------------------------------------------------------
# PAGE ROUTES
# -------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

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
# CAMERA FEED
# -------------------------------------------------------

@app.route("/api/camera", methods=["POST"])
def api_camera():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "no file received"}), 400

    # Save incoming image
    file.save("static/camera.jpg")
    print("📥 Camera image saved.")

    return jsonify({"status": "ok"})


# -------------------------------------------------------
# RECEIVE SENSOR DATA FROM PI
# -------------------------------------------------------

@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.json

    # Save latest readings
    with open(LATEST_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print("💾 RECEIVED:", data)
    return jsonify({"status": "ok"})


# -------------------------------------------------------
# GLOBAL STATE API
# -------------------------------------------------------

@app.route("/api/state")
def api_state():
    return jsonify(load_state())


# -------------------------------------------------------
# COMBINED DASHBOARD API
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
# FLOOD API – FIXED FIELDS
# -------------------------------------------------------

@app.route("/api/flood")
def api_flood():
    try:
        with open(LATEST_FILE) as f:
            data = json.load(f)

        return jsonify({
            "labels": [data["timestamp"]],
            "water_level": [data.get("distance", 0)],
            "rain_intensity": [data.get("rain", 0)],
            "soil_sat": [data.get("soil1", 0)],
            "flood_danger": data.get("flood", 0),
        })

    except Exception as e:
        print("FLOOD API ERROR:", e)
        return jsonify({"error": True})



# -------------------------------------------------------
# LANDSLIDE API – FIXED FIELDS + TILT COMPUTATION
# -------------------------------------------------------

@app.route("/api/landslide")
def api_landslide():
    try:
        with open(LATEST_FILE) as f:
            data = json.load(f)

        tilt_value = (
            abs(data.get("acc_x", 0)) +
            abs(data.get("acc_y", 0)) +
            abs(data.get("acc_z", 0))
        ) / 1000

        return jsonify({
            "labels": [data.get("timestamp", "NA")],
            "soil1": [data.get("soil1", 0)],
            "soil2": [data.get("soil2", 0)],
            "tilt": [tilt_value],
            "vibration": [data.get("vibration", 0)],
            "rain": [data.get("rain", 0)],
            "landslide_danger": data.get("landslide", 0)
        })

    except:
        return jsonify({"error": True})


# -------------------------------------------------------
# START SERVER
# -------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




