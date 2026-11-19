import json
from flask import Flask, jsonify, request
from edge_gateway import EdgeGateway

app = Flask(__name__)
gateway = EdgeGateway()
gateway.start()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "edge-telemetry-gateway"})

@app.get("/api/snapshot")
def get_snapshot():
    return jsonify(gateway.get_snapshot())

@app.post("/api/fault")
def set_fault():
    data = request.get_json(silent=True) or {}
    fault_type = data.get("fault", "none")
    gateway.set_fault(fault_type)
    return jsonify({"success": True, "active_fault": fault_type})

@app.post("/api/publish")
def manual_publish():
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "edge/custom/message")
    payload = data.get("payload", {})
    gateway.publish_mqtt(topic, payload)
    gateway.log_event("ManualPublish", f"Sent to {topic}", "CUSTOM", "info")
    return jsonify({"success": True, "topic": topic})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
