import os
import socket
import time
from collections import deque

from flask import Flask, jsonify, request

app = Flask(__name__)

CAPACITY = int(os.environ.get("CAPACITY_PER_MINUTE", "20"))
INSTANCE_NAME = os.environ.get("INSTANCE_NAME", socket.gethostname())
INSTANCE_ID = os.environ.get("INSTANCE_ID", INSTANCE_NAME)

request_times = deque()


def prune_old():
    cutoff = time.time() - 60
    while request_times and request_times[0] < cutoff:
        request_times.popleft()


def current_count():
    prune_old()
    return len(request_times)


def utilization():
    if CAPACITY <= 0:
        return 0.0
    return round((current_count() / CAPACITY) * 100.0, 2)


def stats_payload():
    count = current_count()
    util = utilization()
    return {
        "instance_name": INSTANCE_NAME,
        "instance_id": INSTANCE_ID,
        "requests_last_60s": count,
        "capacity": CAPACITY,
        "utilization_percent": util,
    }


@app.before_request
def count_request():
    if request.path in ("/health", "/stats"):
        return None
    prune_old()
    if len(request_times) >= CAPACITY:
        return (
            jsonify(
                {
                    "error": "overloaded",
                    "message": "Instance capacity exceeded",
                    "capacity": CAPACITY,
                }
            ),
            429,
        )
    request_times.append(time.time())
    return None


@app.get("/")
def root():
    return jsonify(stats_payload())


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "instance_name": INSTANCE_NAME})


@app.get("/stats")
def stats():
    return jsonify(stats_payload())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)