import os
import json
import threading
from flask import Flask, jsonify, render_template, Response, request

# -------------------------------------------------------
# CREATE FLASK APP
# -------------------------------------------------------
app = Flask(__name__)

# Store latest sensor data received from Raspberry Pi
latest_data = {}

# -------------------------------------------------------
# HELPER — compute danger scores
# -------------------------------------------------------
def compute_dangers(d):
    # DEFAULT if missing keys
    soil1 = float(d.get("soil1", 0))
    soil2 = float(d.get("soil2", 0))
    rain = float(d.get("rain", 0))
    distance = float(d.get("distance", 100))
    vibration = float(d.get("vibration", 0))
    ax = float(d.get("acc_x", 0))
    ay = float(d.get("acc_y", 0))
    az = float(d.get("acc_z", 0))

    # Simple tilt estimation
    tilt = abs(ax) + abs(ay) + abs(az)

    # ---- Landslide ----
    ls = 0
    ls += max(0, soil1 - 500) * 0.03
    ls += max(0, soil2 - 500) * 0.03
    ls += rain * 0.05
    if vibration > 0:
        ls += 15
    if tilt > 20000:
        ls += 20
    landslide = min(ls, 100)

    # ---- Flood ----
    fl = 0
    # water_level = 100 - distance (approx)
    water_level = max(0, 100 - distance)
    fl += water_level * 0.7
    fl += rain * 0.03
    flood = min(fl, 100)

    combined = round((landslide + flood) / 2, 2)

    return landslide, flood, combined


# -------------------------------------------------------
# API (RASPBERRY PI → WEB)
# -------------------------------------------------------
@app.route("/api/data", methods=["POST"])
def receive_data():
    global latest_data
    latest_data = request.json

    # Compute dangers automatically
    ls, fl, cb = compute_dangers(latest_data)
    latest_data["landslide"] = ls
    latest_data["flood"] = fl
    latest_data["combined"] = cb

    print("💾 RECEIVED:", latest_data)
    return jsonify({"status": "OK"}), 200


# -------------------------------------------------------
# PAGES
# -------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/flood")
def flood_page():
    return render_template("flood.html")

@app.route("/landslide")
def landslide_page():
    return render_template("landslide.html")

@app.route("/camera")
def camera_page():
    return render_template("camera.html")


# -------------------------------------------------------
# CAMERA FEED (STATIC FOR NOW)
# -------------------------------------------------------
@app.route("/camera_feed")
def camera_feed():
    try:
        with open("static/camera.jpg", "rb") as f:
            return Response(f.read(), mimetype="image/jpeg")
    except:
        return Response(b"", mimetype="image/jpeg")


# -------------------------------------------------------
# API — COMBINED DASHBOARD
# -------------------------------------------------------
@app.route("/api/combined")
def api_combined():
    if not latest_data:
        return jsonify({
            "landslide": 0,
            "flood": 0,
            "combined": 0,
            "timestamp": "NA"
        })

    return jsonify({
        "landslide": latest_data.get("landslide", 0),
        "flood": latest_data.get("flood", 0),
        "combined": latest_data.get("combined", 0),
        "timestamp": latest_data.get("timestamp", "NA")
    })


# -------------------------------------------------------
# API — FLOOD PAGE
# -------------------------------------------------------
@app.route("/api/flood")
def api_flood():
    if not latest_data:
        return jsonify({"error": True})

    return jsonify({
        "labels": [latest_data.get("timestamp", "NA")],
        "water_level": [max(0, 100 - float(latest_data.get("distance", 100)))],
        "rain_intensity": [latest_data.get("rain", 0)],
        "soil_sat": [latest_data.get("soil1", 0)],
        "flood_danger": latest_data.get("flood", 0)
    })


# -------------------------------------------------------
# API — LANDSLIDE PAGE
# -------------------------------------------------------
@app.route("/api/landslide")
def api_landslide():
    if not latest_data:
        return jsonify({"error": True})

    # simple tilt magnitude
    tilt = abs(latest_data.get("acc_x", 0)) + \
           abs(latest_data.get("acc_y", 0)) + \
           abs(latest_data.get("acc_z", 0))

    return jsonify({
        "labels": [latest_data.get("timestamp", "NA")],
        "soil1": [latest_data.get("soil1", 0)],
        "soil2": [latest_data.get("soil2", 0)],
        "tilt": [tilt],
        "vibration": [latest_data.get("vibration", 0)],
        "rain": [latest_data.get("rain", 0)],
        "landslide_danger": latest_data.get("landslide", 0)
    })


# -------------------------------------------------------
# RUN (local only, NOT used on Render)
# -------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

