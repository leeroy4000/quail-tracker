from flask import Flask, jsonify, request, render_template, Response
import json, os, uuid
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
DATA_FILE = "/data/quail_data.json"

DEFAULT_DATA = {"batches": [], "egg_log": []}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
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

def parse_date(s):
    y, m, d = map(int, s.split("-"))
    return datetime(y, m, d, tzinfo=timezone.utc)

def add_days(dt, n):
    return dt + timedelta(days=n)

def ics_dt(dt):
    return dt.strftime("%Y%m%d")

def ics_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def fold(s):
    """Fold long ICS lines at 75 octets."""
    result, line = [], ""
    for ch in s:
        if len((line + ch).encode("utf-8")) > 75:
            result.append(line)
            line = " " + ch
        else:
            line += ch
    if line:
        result.append(line)
    return "\r\n".join(result)

INC_MILESTONES = [
    (0,  "Eggs Set",         "Confirm incubator stable at 99.5F / 45-55% humidity. Start auto-turner. Rest shipped eggs pointy-end down 12-24h before setting."),
    (7,  "First Candle",     "Candle eggs. Remove clearly infertile eggs or early quitters. Veins = developing. Fully clear = likely infertile."),
    (14, "Second Candle",    "Final candle before lockdown. Remove late quitters. Air cell should be large and well-defined. Target 13-15% egg weight loss by today."),
    (15, "Lockdown",         "Stop turning eggs. Raise humidity to 65-70%. Do NOT open incubator until hatch is complete. Lay eggs on their sides."),
    (17, "Hatch Begins",     "Watch for pipping and zipping. Do not assist unless a chick is stuck for 24h+. Do not open the lid."),
    (18, "Hatch Complete",   "Move dry fluffy chicks to brooder. Discard unhatched eggs after 24h. Chicks survive 24-48h on yolk reserves."),
]

BRD_MILESTONES = [
    (0,  "Move to Brooder",      "Set brooder at 95F. Dip beaks in water. Chick starter feed. Marbles in water dish. Paper towels on floor first 3 days."),
    (7,  "Brooder: Drop Temp",   "Reduce brooder temp to 90F. Check for pasty butt daily. Piling up = cold; spread to edges = hot."),
    (14, "Brooder: Drop Temp",   "Reduce brooder temp to 85F. Switch floor to pine shavings if not already done."),
    (21, "Sexing Window",        "Sex by feather coloration. Pharaoh males: rusty-red chest. Females: speckled/tan. Begin culling plan for extra roosters beyond 1:4-5 ratio."),
    (28, "Fully Feathered",      "Reduce heat if ambient temp >70F. Transition to grower feed. Watch for feather pecking if crowded."),
    (42, "Harvest Window Opens", "Extra roosters ready for harvest (~4-5 oz dressed weight). Hens may begin laying - watch for eggs."),
    (56, "Full Production",      "All keepers at full size. Consistent egg laying expected. Target colony ratio: 1 rooster per 4-5 hens."),
]

def build_ics(data):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Quail Tracker//quail-tracker//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Quail Tracker",
        "X-WR-CALDESC:Quail incubation and brooder milestones",
    ]

    stamp = ics_stamp()

    for batch in data.get("batches", []):
        if not batch.get("start_date"):
            continue
        start = parse_date(batch["start_date"])
        hatch = add_days(start, 18)
        name  = batch["name"]
        bid   = batch["id"].replace("-", "")

        for offset, label, desc in INC_MILESTONES:
            dt  = add_days(start, offset)
            uid = f"inc-{bid}-{offset}@quail-tracker"
            lines += [
                "BEGIN:VEVENT",
                fold(f"UID:{uid}"),
                f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{ics_dt(dt)}",
                f"DTEND;VALUE=DATE:{ics_dt(add_days(dt, 1))}",
                fold(f"SUMMARY:[{name}] {label}"),
                fold(f"DESCRIPTION:{desc}"),
                "END:VEVENT",
            ]

        for offset, label, desc in BRD_MILESTONES:
            dt  = add_days(hatch, offset)
            uid = f"brd-{bid}-{offset}@quail-tracker"
            lines += [
                "BEGIN:VEVENT",
                fold(f"UID:{uid}"),
                f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{ics_dt(dt)}",
                f"DTEND;VALUE=DATE:{ics_dt(add_days(dt, 1))}",
                fold(f"SUMMARY:[{name}] {label}"),
                fold(f"DESCRIPTION:{desc}"),
                "END:VEVENT",
            ]

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(load_data())

@app.route("/calendar.ics")
def calendar_ics():
    data = load_data()
    ics  = build_ics(data)
    return Response(
        ics,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=quail-tracker.ics"}
    )

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
