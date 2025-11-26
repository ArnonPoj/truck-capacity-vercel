import math
from typing import List, Dict, Any
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# --- vehicle specs ---
VEHICLES = {
    "standard": {"name": "กระบะธรรมดา", "width": 1.6, "length": 1.7, "height": 0.9, "volume": 1.6*1.7*0.9, "max_weight": 1000, "long_ok": False, "high_ok": False},
    "rollbar": {"name": "กระบะโรลบาร์หัวกระบะ", "width": 1.6, "length": 1.7, "height": 0.9, "volume": 1.6*1.7*0.9, "max_weight": 1000, "long_ok": True, "high_ok": False},
    "high_cage": {"name": "กระบะคอกสูง", "width": 1.6, "length": 1.7, "height": 1.6, "volume": 1.6*1.7*1.6, "max_weight": 3500, "long_ok": True, "high_ok": True}
}

def compute_capacity(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    processed = []
    total_weight = total_volume = 0.0
    for it in items:
        name = it.get("name","Unnamed")
        w = float(it.get("width",0))
        l = float(it.get("length",0))
        h = float(it.get("height",0))
        wt = float(it.get("weight_per_unit", it.get("weight",0)))
        q = int(it.get("quantity",1))
        item_volume = w*l*h*q
        item_weight = wt*q
        processed.append({
            "name":name,"width":w,"length":l,"height":h,"unit_weight":wt,
            "quantity":q,"total_weight":item_weight,"total_volume":item_volume,
            "long_item": l>VEHICLES["standard"]["length"],
            "tall_item": h>VEHICLES["standard"]["height"]
        })
        total_weight += item_weight
        total_volume += item_volume

    need_rollbar = any(p["long_item"] for p in processed)
    need_high = any(p["tall_item"] for p in processed)
    overweight_standard = total_weight > VEHICLES["standard"]["max_weight"]

    if need_high or overweight_standard:
        chosen = "high_cage"
    elif need_rollbar:
        chosen = "rollbar"
    else:
        chosen = "standard"

    vehicle = VEHICLES[chosen]
    trucks_needed = math.ceil(total_weight / vehicle["max_weight"])

    bottom, top, rollbar_items = [], [], []
    for p in processed:
        if p["long_item"] and vehicle["long_ok"]:
            rollbar_items.append(p)
        elif p["total_weight"] >= 100:
            bottom.append(p)
        else:
            top.append(p)

    return {
        "vehicle_type": chosen,
        "vehicle_info": vehicle,
        "items": processed,
        "total_weight": total_weight,
        "total_volume": total_volume,
        "trucks_needed": trucks_needed,
        "arrangement": {"bottom": bottom, "top": top, "rollbar": rollbar_items},
        "notes": {"long_item_rule":need_rollbar,"tall_item_rule":need_high,"overweight_standard":overweight_standard}
    }

# ---------------- Flask Routes ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/calculate-capacity", methods=["POST"])
def calculate_capacity_route():
    data = request.get_json()
    if not data or "items" not in data:
        return jsonify({"error":"Missing items"}), 400
    result = compute_capacity(data["items"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
