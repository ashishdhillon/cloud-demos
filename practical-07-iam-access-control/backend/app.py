from flask import Flask, jsonify, request
from iam_engine import IAMEvaluationEngine

app = Flask(__name__)
engine = IAMEvaluationEngine()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "iam-policy-engine"})

@app.get("/api/personas")
def get_personas():
    return jsonify({"personas": engine.get_personas()})

@app.get("/api/audit")
def get_audit():
    return jsonify({"history": engine.get_audit_history()})

@app.post("/api/evaluate")
def evaluate_request():
    data = request.get_json(silent=True) or {}
    persona = data.get("persona", "junior-developer")
    action = data.get("action", "").strip()
    resource = data.get("resource", "").strip()
    context = data.get("context", {})

    if not action or not resource:
        return jsonify({"error": "Both 'action' and 'resource' are required."}), 400

    try:
        decision = engine.evaluate(persona, action, resource, context)
        return jsonify(decision)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.put("/api/custom-policy")
def update_policy():
    data = request.get_json(silent=True) or {}
    policy = data.get("policy")
    if not policy:
        return jsonify({"error": "Policy document required"}), 400
    try:
        engine.update_custom_policy(policy)
        return jsonify({"success": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
