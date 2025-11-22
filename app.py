from flask import Flask, render_template, request, jsonify
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


# 2) Choose best truck heuristic: prefer smallest truck that fits all by size OR choose cage if any long/heavy item
chosen_truck = None
# if any product needs cage by height or weight > 1000 use cage
need_cage = any((p['height'] > TRUCK_TYPES['pickup_normal']['height'] or p['weight'] > TRUCK_TYPES['pickup_normal']['max_weight']) for p in products)
if need_cage:
chosen_truck = 'pickup_cage'
else:
# try normal or rollbar if all products fit
all_fit_normal = all(p['length'] <= TRUCK_TYPES['pickup_normal']['length'] and p['width'] <= TRUCK_TYPES['pickup_normal']['width'] and p['height'] <= TRUCK_TYPES['pickup_normal']['height'] for p in products)
if all_fit_normal:
chosen_truck = 'pickup_normal'
else:
chosen_truck = 'pickup_rollbar'


# 3) number of vehicles needed by weight
trucks_needed = truck_count_for_weight(total_weight, chosen_truck)


# 4) arrangement
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
