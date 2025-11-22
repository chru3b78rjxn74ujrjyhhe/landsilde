from flask import request, jsonify

# Store last payload from Pi
latest_data = {}

@app.route("/api/data", methods=["POST"])
def receive_data():
    global latest_data
    latest_data = request.json
    return jsonify({"status": "OK"}), 200


@app.route("/api/latest", methods=["GET"])
def send_latest():
    return jsonify(latest_data)


# -----------------------------------------
# SIMPLE LIVE DANGER FORMULAS
# -----------------------------------------
def compute_landslide(data):
    soil1 = data.get("soil1", 0)
    soil2 = data.get("soil2", 0)
    rain  = data.get("rain", 0)

    risk = 0
    risk += max(0, soil1 - 500) * 0.05
    risk += max(0, soil2 - 500) * 0.05
    risk += rain * 0.05

    return min(risk, 100)


def compute_flood(data):
    distance = data.get("distance", 100)
    rain     = data.get("rain", 0)

    water_level = max(0, 100 - distance)
    risk = water_level * 0.7 + rain * 0.03

    return min(risk, 100)


# ----------------------------------------------------
# 1) COMBINED DASHBOARD API
# ----------------------------------------------------
@app.route("/api/combined")
def api_combined():
    if not latest_data:
        return jsonify({"landslide": 0, "flood": 0, "combined": 0, "timestamp": "NA"})

    ls = compute_landslide(latest_data)
    fl = compute_flood(latest_data)
    cb = (ls + fl) / 2

    return jsonify({
        "landslide": ls,
        "flood": fl,
        "combined": cb,
        "timestamp": latest_data.get("timestamp", "")
    })


# ----------------------------------------------------
# 2) FLOOD DASHBOARD API
# ----------------------------------------------------
@app.route("/api/flood")
def api_flood():
    if not latest_data:
        return jsonify({"error": True})

    ls = compute_landslide(latest_data)
    fl = compute_flood(latest_data)

    return jsonify({
        "labels": [ latest_data.get("timestamp", "") ],
        "water_level": [ max(0, 100 - latest_data.get("distance", 100)) ],
        "rain_intensity": [ latest_data.get("rain", 0) ],
        "soil_sat": [ latest_data.get("soil1", 0) ],
        "flood_danger": fl
    })


# ----------------------------------------------------
# 3) LANDSLIDE DASHBOARD API
# ----------------------------------------------------
@app.route("/api/landslide")
def api_landslide():
    if not latest_data:
        return jsonify({"error": True})

    ls = compute_landslide(latest_data)

    # simple tilt magnitude from accelerometer
    ax = latest_data.get("acc_x", 0)
    ay = latest_data.get("acc_y", 0)
    az = latest_data.get("acc_z", 0)
    tilt = abs(ax) + abs(ay) + abs(az)

    return jsonify({
        "labels": [ latest_data.get("timestamp", "") ],
        "soil1": [ latest_data.get("soil1", 0) ],
        "soil2": [ latest_data.get("soil2", 0) ],
        "tilt": [ tilt ],
        "vibration": [ latest_data.get("vibration", 0) ],
        "rain": [ latest_data.get("rain", 0) ],
        "landslide_danger": ls
    })
