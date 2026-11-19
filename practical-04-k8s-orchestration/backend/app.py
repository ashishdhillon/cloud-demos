from flask import Flask, jsonify, request
from k8s_control_plane import K8sControlPlane

app = Flask(__name__)
k8s = K8sControlPlane()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "k8s-control-plane-engine"})

@app.get("/api/status")
def get_status():
    return jsonify(k8s.get_cluster_status())

@app.post("/api/kill-pod")
def kill_pod():
    data = request.get_json(silent=True) or {}
    pod_name = data.get("pod_name", "")
    res = k8s.kill_pod(pod_name)
    return jsonify(res)

@app.post("/api/probe")
def toggle_probe():
    data = request.get_json(silent=True) or {}
    pod_name = data.get("pod_name", "")
    probe_type = data.get("probe_type", "liveness")
    res = k8s.toggle_probe(pod_name, probe_type)
    return jsonify(res)

@app.post("/api/scale")
def scale_deployment():
    data = request.get_json(silent=True) or {}
    replicas = data.get("replicas", 3)
    res = k8s.scale_deployment(replicas)
    return jsonify(res)

@app.post("/api/rollout")
def trigger_rollout():
    data = request.get_json(silent=True) or {}
    version = data.get("version", "v2.0.0")
    res = k8s.start_rolling_update(version)
    return jsonify(res)

@app.post("/api/apply-yaml")
def apply_yaml():
    data = request.get_json(silent=True) or {}
    yaml_code = data.get("yaml_code", "")
    res = k8s.apply_yaml(yaml_code)
    return jsonify(res)

@app.post("/api/traffic")
def send_traffic():
    res = k8s.send_traffic_request()
    return jsonify(res)

@app.post("/api/kubectl")
def run_kubectl():
    data = request.get_json(silent=True) or {}
    cmd = data.get("command", "kubectl get pods -o wide")
    output = k8s.run_kubectl_cli(cmd)
    return jsonify({"command": cmd, "output": output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
