import os
import json
import threading
from flask import Flask, jsonify, render_template, Response, request, send_file

app = Flask(__name__)

# -------------------------------------------------------
# FILE PATHS
# -------------------------------------------------------
LATEST_FILE = "data/latest.json"
STATE_FILE = "data/state.json"
CALIB_FILE = "data/calibration.csv"
HISTORY_FILE = "data/history.csv"
CAMERA_STATIC = "static/camera.jpg"

os.makedirs("data", exist_ok=True)
os.makedirs("static", exist_ok=True)


# -------------------------------------------------------
# STATE MANAGEMENT
# -------------------------------------------------------
def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
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
    # run training (this will block in the background thread)
    os.system("python3 train_lstm.py")

    state["mode"] = "normal"
    state["message"] = "Training completed"
    save_state(state)

    print("TRAINING COMPLETE")


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
# CAMERA FEED (serve the latest static image)
# -------------------------------------------------------
@app.route("/camera_feed")
def camera_feed():
    """
    Serve the latest camera snapshot saved to static/camera.jpg.
    If not present, return an empty 1x1 jpeg response (no crash).
    """
    try:
        if os.path.exists(CAMERA_STATIC):
            # Use send_file so headers/mime are correct and it streams efficiently.
            return send_file(CAMERA_STATIC, mimetype="image/jpeg")
        else:
            # Return an empty response with correct mimetype if no image yet
            return Response(b"", mimetype="image/jpeg")
    except Exception as e:
        print("Camera feed error:", e)
        return Response(b"", mimetype="image/jpeg")


# -------------------------------------------------------
# RECEIVE CAMERA UPLOAD FROM PI
# -------------------------------------------------------
@app.route("/api/camera", methods=["POST"])
def api_camera():
    try:
        # Accept field name "file" from the Pi script
        file = request.files.get("file")
        if not file:
            # also accept "frame" or "image" just in case
            file = request.files.get("frame") or request.files.get("image")
        if not file:
            return jsonify({"error": "no file received"}), 400

        # Save incoming image to static/camera.jpg
        file.save(CAMERA_STATIC)
        print("📥 Camera image saved.")
        return jsonify({"status": "ok"})
    except Exception as e:
        print("API_CAMERA ERROR:", e)
        return jsonify({"error": "server error"}), 500


# -------------------------------------------------------
# RECEIVE SENSOR DATA FROM PI
# -------------------------------------------------------
@app.route("/api/data", methods=["POST"])
def receive_data():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "no json"}), 400

        # Save latest readings
        with open(LATEST_FILE, "w") as f:
            json.dump(data, f, indent=4)

        print("💾 RECEIVED:", data)
        return jsonify({"status": "ok"})
    except Exception as e:
        print("API_DATA ERROR:", e)
        return jsonify({"error": "server error"}), 500


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
    except Exception as e:
        print("COMBINED API ERROR:", e)
        return jsonify({"landslide": 0, "flood": 0, "combined": 0, "timestamp": "NA"})


# -------------------------------------------------------
# FLOOD API – FIXED FIELDS
# -------------------------------------------------------
@app.route("/api/flood")
def api_flood():
    try:
        with open(LATEST_FILE) as f:
            data = json.load(f)

        return jsonify({
            "labels": [data.get("timestamp", "NA")],
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
    except Exception as e:
        print("LANDSLIDE API ERROR:", e)
        return jsonify({"error": True})


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


# -------------------------------------------------------
# START SERVER
# -------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




