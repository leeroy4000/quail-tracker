from flask import Flask, jsonify, request, render_template
import json, os

app = Flask(__name__)
DATA_FILE = "/data/quail_data.json"

DEFAULT_DATA = {
    "incubation": {
        "start_date": None
    },
    "egg_log": []
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return dict(DEFAULT_DATA)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(load_data())

@app.route("/api/incubation", methods=["POST"])
def set_incubation():
    data = load_data()
    body = request.get_json()
    data["incubation"]["start_date"] = body.get("start_date")
    save_data(data)
    return jsonify({"status": "ok"})

@app.route("/api/egg_log", methods=["POST"])
def add_egg_log():
    data = load_data()
    entry = request.get_json()
    # Replace existing entry for same date, or append
    existing = next((i for i, e in enumerate(data["egg_log"]) if e["date"] == entry["date"]), None)
    if existing is not None:
        data["egg_log"][existing] = entry
    else:
        data["egg_log"].append(entry)
    data["egg_log"].sort(key=lambda x: x["date"])
    save_data(data)
    return jsonify({"status": "ok"})

@app.route("/api/egg_log/<date>", methods=["DELETE"])
def delete_egg_log(date):
    data = load_data()
    data["egg_log"] = [e for e in data["egg_log"] if e["date"] != date]
    save_data(data)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
