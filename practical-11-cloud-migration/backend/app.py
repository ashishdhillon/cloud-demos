from flask import Flask, jsonify, request
from migration_engine import MigrationEngine

app = Flask(__name__)
engine = MigrationEngine()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "cloud-migration-pipeline-engine"})

@app.get("/api/status")
def get_status():
    return jsonify(engine.get_status())

@app.post("/api/migrate")
def trigger_migration():
    data = request.get_json(silent=True) or {}
    network_mode = data.get("network_mode", "direct_connect_1gbps")
    tamper = data.get("tamper", False)
    res = engine.start_migration(network_mode, tamper)
    return jsonify(res)

@app.post("/api/verify")
def trigger_verification():
    res = engine.run_audit_verification()
    return jsonify(res)

@app.post("/api/heal-chunk")
def heal_chunk():
    res = engine.heal_corrupted_chunk()
    return jsonify(res)

@app.post("/api/cutover")
def cutover():
    res = engine.trigger_cutover()
    return jsonify(res)

@app.post("/api/rollback")
def rollback():
    res = engine.trigger_rollback()
    return jsonify(res)

@app.get("/api/assessment")
def get_assessment():
    return jsonify(engine.get_assessment_matrix())

@app.get("/api/tco")
def get_tco():
    data_size = float(request.args.get("data_size_tb", 10.0))
    servers = int(request.args.get("servers_count", 20))
    return jsonify(engine.calculate_tco(data_size, servers))

@app.post("/api/reset")
def reset_environment():
    engine.seed_onprem_environment()
    return jsonify({"success": True, "message": "Environment reset to on-premises baseline."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
