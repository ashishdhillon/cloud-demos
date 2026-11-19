from flask import Flask, jsonify, request
from analytics_engine import AnalyticsEngine

app = Flask(__name__)
engine = AnalyticsEngine()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "cloud-bigdata-analytics-engine"})

@app.get("/api/stats")
def get_stats():
    return jsonify(engine.get_stats())

@app.post("/api/benchmark")
def run_benchmark():
    try:
        report = engine.run_benchmark_race()
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/api/query/<query_id>")
def run_preset_query(query_id):
    try:
        res = engine.execute_preset_query(query_id)
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.post("/api/query/custom")
def run_custom_query():
    data = request.get_json(silent=True) or {}
    sql = data.get("sql", "SELECT COUNT(*) FROM logs;")
    try:
        res = engine.execute_custom_sql(sql)
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.post("/api/dataset/regenerate")
def regenerate():
    data = request.get_json(silent=True) or {}
    rows = int(data.get("rows", 50000))
    stats = engine.regenerate_dataset(rows)
    return jsonify(stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
