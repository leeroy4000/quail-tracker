from flask import Flask, jsonify, request, render_template
import json, os, uuid

app = Flask(__name__)
DATA_FILE = "/data/quail_data.json"

DEFAULT_DATA = {
    "batches": [],
    "egg_log": []
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Migrate old single-incubation format
            if "incubation" in data and "batches" not in data:
                batches = []
                if data["incubation"].get("start_date"):
                    batches.append({
                        "id": str(uuid.uuid4()),
                        "name": "Initial Batch",
                        "start_date": data["incubation"]["start_date"],
                        "active": True
                    })
                data["batches"] = batches
                del data["incubation"]
                save_data(data)
            return data
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

# ── Batches ────────────────────────────────────────────────────────────────
@app.route("/api/batches", methods=["POST"])
def add_batch():
    data = load_data()
    body = request.get_json()
    batch = {
        "id": str(uuid.uuid4()),
        "name": body.get("name", "Unnamed Batch"),
        "start_date": body.get("start_date"),
        "active": True
    }
    data["batches"].append(batch)
    save_data(data)
    return jsonify(batch)

@app.route("/api/batches/<batch_id>", methods=["DELETE"])
def delete_batch(batch_id):
    data = load_data()
    data["batches"] = [b for b in data["batches"] if b["id"] != batch_id]
    save_data(data)
    return jsonify({"status": "ok"})

@app.route("/api/batches/<batch_id>/archive", methods=["POST"])
def archive_batch(batch_id):
    data = load_data()
    for b in data["batches"]:
        if b["id"] == batch_id:
            b["active"] = False
    save_data(data)
    return jsonify({"status": "ok"})

# ── Egg Log ────────────────────────────────────────────────────────────────
@app.route("/api/egg_log", methods=["POST"])
def save_egg_log():
    data = load_data()
    entry = request.get_json()
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
