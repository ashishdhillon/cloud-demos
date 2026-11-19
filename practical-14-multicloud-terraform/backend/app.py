from flask import Flask, jsonify, request
from terraform_engine import TerraformEngine

app = Flask(__name__)
engine = TerraformEngine()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "multicloud-terraform-engine"})

@app.get("/api/status")
def get_status():
    return jsonify(engine.get_status())

@app.post("/api/hcl")
def update_hcl():
    data = request.get_json(silent=True) or {}
    hcl = data.get("hcl_code", "")
    res = engine.update_hcl(hcl)
    return jsonify(res)

@app.post("/api/init")
def run_init():
    res = engine.run_init()
    return jsonify(res)

@app.post("/api/plan")
def run_plan():
    res = engine.run_plan()
    return jsonify(res)

@app.post("/api/apply")
def run_apply():
    res = engine.run_apply()
    return jsonify(res)

@app.post("/api/drift")
def trigger_drift():
    res = engine.trigger_drift()
    return jsonify(res)

@app.post("/api/refresh")
def run_refresh():
    res = engine.run_refresh()
    return jsonify(res)

@app.post("/api/destroy")
def run_destroy():
    res = engine.run_destroy()
    return jsonify(res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
