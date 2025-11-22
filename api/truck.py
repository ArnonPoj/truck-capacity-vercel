from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/truck", methods=["POST"])
def api():
    data = request.json
    return jsonify({"ok": True, "input": data})

# export app for vercel
def handler(request, response):
    return app(request, response)
