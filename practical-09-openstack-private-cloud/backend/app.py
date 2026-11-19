from flask import Flask, jsonify, request, make_response
from openstack_core import OpenStackCore

app = Flask(__name__)
openstack = OpenStackCore()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "openstack-private-cloud-core"})

@app.get("/api/overview")
def overview():
    project_id = request.args.get("project", "proj-prod")
    return jsonify(openstack.get_overview(project_id))

# --- KEYSTONE v3 REST AUTHENTICATION ---
@app.post("/v3/auth/tokens")
def keystone_tokens():
    payload = request.get_json(silent=True) or {}
    try:
        user_identity = payload.get("auth", {}).get("identity", {}).get("password", {}).get("user", {})
        username = user_identity.get("name", "admin")
        password = user_identity.get("password", "SecretAdminPass123")
        scope_proj = payload.get("auth", {}).get("scope", {}).get("project", {}).get("name", "Production-Core")
    except Exception:
        username = "admin"
        password = "SecretAdminPass123"
        scope_proj = "Production-Core"

    doc, code = openstack.authenticate_keystone(username, password, scope_proj)
    resp = make_response(jsonify(doc), code)
    if code == 201:
        resp.headers["X-Subject-Token"] = doc["token"]["id"]
    return resp

# --- NOVA v2.1 COMPUTE REST API ---
@app.get("/v2.1/flavors")
@app.get("/v2.1/flavors/detail")
def get_flavors():
    return jsonify({"flavors": openstack.flavors})

@app.get("/v2.1/images")
@app.get("/v2.1/images/detail")
def get_images():
    return jsonify({"images": openstack.images})

@app.get("/v2.1/servers")
def list_servers():
    project_id = request.args.get("project", "proj-prod")
    data = openstack.get_overview(project_id)
    return jsonify({"servers": data["servers"]})

@app.post("/v2.1/servers")
def launch_server():
    data = request.get_json(silent=True) or {}
    srv = data.get("server", {})
    project_id = data.get("project_id", "proj-prod")
    name = srv.get("name", "app-instance")
    flavor_id = srv.get("flavorRef", "1")
    image_id = srv.get("imageRef", "img-cirros-01")
    assign_fip = data.get("assign_floating_ip", False)
    
    res = openstack.create_server(project_id, name, flavor_id, image_id, assign_fip)
    if "error" in res:
        return jsonify(res), 400
    return jsonify(res), 202

@app.post("/api/server/action")
def server_action():
    data = request.get_json(silent=True) or {}
    server_id = data.get("server_id")
    action = data.get("action")
    res = openstack.server_action(server_id, action)
    if "error" in res:
        return jsonify(res), 400
    return jsonify(res)

@app.post("/api/cli")
def run_cli():
    data = request.get_json(silent=True) or {}
    cmd = data.get("command", "openstack server list")
    project_id = data.get("project_id", "proj-prod")
    out = openstack.run_openstack_cli(cmd, project_id)
    return jsonify({"command": cmd, "output": out})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
