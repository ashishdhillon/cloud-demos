import concurrent.futures
from flask import Flask, jsonify, request
from faas_engine import FaaSEngine

app = Flask(__name__)
engine = FaaSEngine()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "faas-serverless-engine"})

@app.get("/api/functions")
def get_functions():
    return jsonify({"functions": engine.get_functions()})

@app.get("/api/stats")
def get_stats():
    return jsonify(engine.get_stats())

@app.get("/api/sandboxes")
def get_sandboxes():
    return jsonify({"sandboxes": engine.get_active_sandboxes()})

@app.get("/api/history")
def get_history():
    return jsonify({"history": engine.get_history()})

@app.post("/api/invoke")
def invoke_function():
    data = request.get_json(silent=True) or {}
    function_id = data.get("function_id", "image-thumbnailer")
    payload = data.get("payload", {})
    try:
        record = engine.invoke(function_id, payload)
        return jsonify(record)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.post("/api/invoke-burst")
def invoke_burst():
    data = request.get_json(silent=True) or {}
    function_id = data.get("function_id", "sentiment-analyzer")
    count = min(15, max(2, int(data.get("count", 6))))

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=count) as executor:
        futures = [executor.submit(engine.invoke, function_id, {}) for _ in range(count)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    return jsonify({
        "burst_count": count,
        "function_id": function_id,
        "results": results
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
