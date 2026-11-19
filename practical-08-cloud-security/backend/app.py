from flask import Flask, jsonify, request
from kms_envelope_engine import KmsEnvelopeEngine

app = Flask(__name__)
engine = KmsEnvelopeEngine()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "cloud-security-kms-engine"})

@app.get("/api/status")
def get_status():
    return jsonify(engine.get_status())

@app.get("/api/certificate")
def get_certificate():
    return jsonify(engine.get_certificate_details())

@app.post("/api/posture/toggle")
def toggle_posture():
    data = request.get_json(silent=True) or {}
    check_id = data.get("check_id")
    try:
        updated = engine.toggle_posture_check(check_id)
        return jsonify(updated)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.post("/api/envelope/encrypt")
def encrypt_payload():
    data = request.get_json(silent=True) or {}
    plaintext = data.get("plaintext", "Customer Record: John Doe, SSN: 987-65-4321")
    label = data.get("label", "Sensitive Customer Record")
    res = engine.encrypt_envelope(plaintext, label)
    return jsonify(res)

@app.post("/api/envelope/decrypt")
def decrypt_payload():
    data = request.get_json(silent=True) or {}
    envelope_id = data.get("envelope_id")
    try:
        res = engine.decrypt_envelope(envelope_id)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
