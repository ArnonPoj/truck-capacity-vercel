from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__, template_folder='templates', static_folder='static')

TRUCK_TYPES = {
    "pickup_normal": {
        "name": "กระบะธรรมดา",
        "width": 1.6,
        "length": 1.7,
        "height": 0.9,
        "max_weight": 1000,
        "type": "normal"
    },
    "pickup_rollbar": {
        "name": "กระบะโรลบาร์",
        "width": 1.6,
        "length": 1.7,
        "height": 0.9,
        "max_weight": 1000,
        "type": "rollbar"
    },
    "pickup_cage": {
        "name": "กระบะคอกสูง",
        "width": 1.6,
        "length": 1.7,
        "height": 1.6,
        "max_weight": 3500,
        "type": "cage"
    }
}


def select_trucks_for_product(p):
    """Return list of truck keys that can carry this product by size and long-item rule."""
    suitable = []
    for key, t in TRUCK_TYPES.items():
        fit_size = (p['width'] <= t['width'] and p['length'] <= t['length'] and p['height'] <= t['height'])
        long_fit = (p['length'] > t['length'] and t['type'] in ['rollbar', 'cage'])
        if fit_size or long_fit:
            suitable.append(key)
    return suitable


def truck_count_for_weight(total_weight, truck_key):
    max_w = TRUCK_TYPES[truck_key]['max_weight']
    return math.ceil(total_weight / max_w)


def arrange_products(products, chosen_truck_key):
    bottom = []
    top = []
    rollbar = []
    truck = TRUCK_TYPES[chosen_truck_key]

    for p in products:
        # long items that require rollbar/cage
        if p['length'] > truck['length'] and truck['type'] in ['rollbar', 'cage']:
            rollbar.append(p)
            continue

        # heavy threshold — you can adjust this rule
        if p['weight'] >= 100:
            bottom.append(p)
        else:
            top.append(p)

    return {'bottom': bottom, 'top': top, 'rollbar': rollbar}


@app.route('/')
def index():
    return render_template('index.html', truck_types=TRUCK_TYPES)


@app.route('/api/compute', methods=['POST'])
def api_compute():
    payload = request.get_json() or {}
    products = payload.get('products', [])
    
    # normalize numbers
    for p in products:
        for k in ['width','length','height','weight']:
            p[k] = float(p.get(k, 0))

    # 1) For each product, list suitable trucks
    per_product = []
    total_weight = 0.0
    for p in products:
        suitable = select_trucks_for_product(p)
        per_product.append({**p, 'suitable_trucks': suitable})
        total_weight += p['weight']

    # 2) Choose best truck heuristic
    chosen_truck = None
    need_cage = any(
        (p['height'] > TRUCK_TYPES['pickup_normal']['height'] or
         p['weight'] > TRUCK_TYPES['pickup_normal']['max_weight'])
        for p in products
    )
    if need_cage:
        chosen_truck = 'pickup_cage'
    else:
        all_fit_normal = all(
            p['length'] <= TRUCK_TYPES['pickup_normal']['length'] and
            p['width'] <= TRUCK_TYPES['pickup_normal']['width'] and
            p['height'] <= TRUCK_TYPES['pickup_normal']['height']
            for p in products
        )
        if all_fit_normal:
            chosen_truck = 'pickup_normal'
        else:
            chosen_truck = 'pickup_rollbar'

    # 3) Number of vehicles needed by weight
    trucks_needed = truck_count_for_weight(total_weight, chosen_truck)

    # 4) Arrangement
    arrangement = arrange_products(products, chosen_truck)

    return jsonify({
        'per_product': per_product,
        'chosen_truck': chosen_truck,
        'chosen_truck_meta': TRUCK_TYPES[chosen_truck],
        'total_weight': total_weight,
        'trucks_needed': trucks_needed,
        'arrangement': arrangement
    })


if __name__ == '__main__':
    app.run(debug=True, port=3000)
