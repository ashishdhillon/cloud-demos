from flask import Flask, jsonify, request
from cgroup_engine import CgroupEngine

app = Flask(__name__)
engine = CgroupEngine()

@app.route("/", methods=["GET"])
def home():
    metrics = engine.get_cgroup_metrics()
    return jsonify({
        "service": "Containerized Cloud Microservice",
        "lab": "Practical 03 - Docker Containerization & Cgroups",
        "hostname": metrics["hostname"],
        "platform": metrics["platform"],
        "uptime_seconds": metrics["uptime_seconds"],
        "status": "OPERATIONAL",
        "cgroup_version": metrics["cgroup_version"],
        "isolation": {
            "unprivileged_uid": metrics["user_id"],
            "process_id": metrics["process_id"],
            "memory_limit": f"{metrics['memory_limit_mb']} MB",
            "cpu_quota": metrics["cpu_quota"]
        }
    })

@app.route("/healthz", methods=["GET"])
def health():
    if not engine.is_healthy:
        return jsonify({
            "status": "UNHEALTHY",
            "code": 503,
            "reason": "Simulated container liveness failure"
        }), 503
    return jsonify({
        "status": "HEALTHY",
        "code": 200,
        "uptime_seconds": engine.get_cgroup_metrics()["uptime_seconds"]
    }), 200

@app.route("/system-metrics", methods=["GET"])
def system_metrics():
    metrics = engine.get_cgroup_metrics()
    return jsonify({
        "cgroup_memory_ceiling": f"{metrics['memory_limit_mb']} MB",
        "cgroup_memory_current": f"{metrics['memory_current_mb']} MB",
        "process_id": metrics["process_id"],
        "user_id": metrics["user_id"],
        "cpu_quota": metrics["cpu_quota"]
    })

@app.route("/api/cgroups", methods=["GET"])
def get_cgroups():
    return jsonify(engine.get_cgroup_metrics())

@app.route("/api/cgroups/stress-memory", methods=["POST"])
def stress_memory():
    data = request.get_json(silent=True) or {}
    action = data.get("action", "allocate")
    mb = int(data.get("mb", 20))
    try:
        if action == "release":
            res = engine.release_memory()
            return jsonify(res)
        else:
            res = engine.allocate_memory(mb)
            return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/cgroups/stress-cpu", methods=["POST"])
def stress_cpu():
    data = request.get_json(silent=True) or {}
    duration = int(data.get("duration_sec", 5))
    res = engine.trigger_cpu_stress(duration)
    return jsonify(res)

@app.route("/api/health/toggle", methods=["POST"])
def toggle_health():
    res = engine.toggle_health()
    return jsonify(res)

@app.route("/api/layers", methods=["GET"])
def get_layers():
    return jsonify(engine.get_image_layers())

@app.route("/api/layers/touch-file", methods=["POST"])
def touch_file():
    res = engine.touch_ephemeral_file()
    return jsonify(res)

@app.route("/api/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": engine.get_logs()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
