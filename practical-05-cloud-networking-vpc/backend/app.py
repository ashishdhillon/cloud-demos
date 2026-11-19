from flask import Flask, jsonify, request
from vpc_engine import VpcEngine

app = Flask(__name__)
engine = VpcEngine()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "cloud-vpc-networking-engine"})

@app.get("/api/topology")
def get_topology():
    return jsonify(engine.get_topology())

@app.post("/api/security-groups/toggle")
def toggle_sg_rule():
    data = request.get_json(silent=True) or {}
    group_id = data.get("group_id")
    rule_id = data.get("rule_id")
    res = engine.toggle_security_rule(group_id, rule_id)
    if isinstance(res, tuple):
        return jsonify(res[0]), res[1]
    return jsonify(res)

@app.post("/api/packet/simulate")
def simulate_packet():
    data = request.get_json(silent=True) or {}
    src_ip = data.get("source_ip", "203.0.113.50")
    dst_ip = data.get("dest_ip", "52.90.14.22")
    port = int(data.get("port", 80))
    protocol = data.get("protocol", "TCP").upper()

    try:
        trace = engine.simulate_packet_trace(src_ip, dst_ip, port, protocol)
        return jsonify(trace)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# AWS EC2 Mock Compatibility Endpoints
@app.get("/api/vpcs")
def describe_vpcs():
    topo = engine.get_topology()
    return jsonify({"Vpcs": [topo["vpc"]]})

@app.get("/api/subnets")
def describe_subnets():
    topo = engine.get_topology()
    return jsonify({"Subnets": topo["subnets"]})

@app.get("/api/route-tables")
def describe_route_tables():
    topo = engine.get_topology()
    return jsonify({"RouteTables": topo["route_tables"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
