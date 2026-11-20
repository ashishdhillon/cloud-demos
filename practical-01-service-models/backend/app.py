from flask import Flask, jsonify, request
from service_models_engine import ServiceModelsEngine

app = Flask(__name__)
engine = ServiceModelsEngine()

@app.get("/")
def home():
    return jsonify({
        "service": "Cloud Service Models Architecture Simulator",
        "lab": "Practical 01 - IaaS vs PaaS vs SaaS & Shared Responsibility Model",
        "status": "OPERATIONAL",
        "models": ["IaaS", "PaaS", "SaaS"],
        "standards": "NIST SP 800-145 Cloud Computing Reference Architecture"
    })

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "service-models-simulator"})

@app.get("/api/overview")
def get_overview():
    return jsonify(engine.get_overview())

@app.get("/api/state")
def get_state():
    return jsonify(engine.get_full_state())

# IaaS Routes
@app.post("/api/iaas/provision")
def provision_iaas():
    data = request.get_json(silent=True) or {}
    os_name = data.get("os", "Ubuntu 24.04 LTS")
    vcpu = int(data.get("vcpu", 2))
    ram_gb = int(data.get("ram_gb", 4))
    res = engine.provision_iaas_vm(os_name, vcpu, ram_gb)
    return jsonify(res)

@app.post("/api/iaas/patch")
def patch_iaas():
    data = request.get_json(silent=True) or {}
    instance_id = data.get("instance_id")
    try:
        res = engine.apply_os_patch_iaas(instance_id)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.post("/api/iaas/simulate-cve")
def simulate_cve_iaas():
    data = request.get_json(silent=True) or {}
    instance_id = data.get("instance_id")
    try:
        res = engine.simulate_cve_iaas(instance_id)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.delete("/api/iaas/terminate/<instance_id>")
def terminate_iaas(instance_id):
    try:
        res = engine.terminate_iaas_vm(instance_id)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# PaaS Routes
@app.post("/api/paas/deploy")
def deploy_paas():
    data = request.get_json(silent=True) or {}
    app_name = data.get("app_name", "web-microservice")
    runtime = data.get("runtime", "Python 3.12")
    branch = data.get("branch", "main")
    res = engine.deploy_paas_app(app_name, runtime, branch)
    return jsonify(res)

@app.post("/api/paas/scale")
def scale_paas():
    data = request.get_json(silent=True) or {}
    deployment_id = data.get("deployment_id")
    replicas = int(data.get("replicas", 3))
    try:
        res = engine.scale_paas_app(deployment_id, replicas)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# SaaS Routes
@app.post("/api/saas/tenant")
def create_saas_tenant():
    data = request.get_json(silent=True) or {}
    company = data.get("company", "New Enterprise Corp")
    users = int(data.get("users", 25))
    plan = data.get("plan", "Enterprise SaaS")
    res = engine.create_saas_tenant(company, users, plan)
    return jsonify(res)

@app.delete("/api/saas/tenant/<tenant_id>")
def delete_saas_tenant(tenant_id):
    try:
        res = engine.delete_saas_tenant(tenant_id)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
