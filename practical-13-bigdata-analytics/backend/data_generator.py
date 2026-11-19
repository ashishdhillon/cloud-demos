import csv
import os
import random
import time

ENDPOINTS = [
    ("/api/v1/products", "GET", 0.40, 35, 120, 2400),
    ("/healthz", "GET", 0.20, 5, 25, 180),
    ("/api/v1/checkout", "POST", 0.15, 65, 240, 850),
    ("/api/v1/login", "POST", 0.10, 45, 150, 420),
    ("/static/bundle.js", "GET", 0.10, 15, 60, 42000),
    ("/api/v1/orders", "GET", 0.05, 55, 180, 1600),
]

IPS = [
    "192.168.1.45", "10.0.4.12", "172.16.8.99", "198.51.100.24", "203.0.113.88",
    "10.0.12.105", "192.168.10.3", "172.16.14.2", "198.51.100.77", "203.0.113.12"
]

STATUS_WEIGHTS = [
    (200, 0.88),
    (201, 0.04),
    (400, 0.02),
    (401, 0.01),
    (404, 0.03),
    (500, 0.015),
    (503, 0.005)
]

def generate_dataset(csv_path: str, row_count: int = 50000):
    start = time.time()
    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)

    weights = [w[2] for w in ENDPOINTS]
    statuses = [s[0] for s in STATUS_WEIGHTS]
    s_weights = [s[1] for s in STATUS_WEIGHTS]

    base_time = int(time.time()) - 86400 # 24 hours of logs

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "client_ip", "method", "endpoint", "status_code", "response_time_ms", "bytes_sent"])

        for i in range(row_count):
            ep_info = random.choices(ENDPOINTS, weights=weights, k=1)[0]
            endpoint = ep_info[0]
            method = ep_info[1]

            ip = random.choice(IPS)
            status = random.choices(statuses, weights=s_weights, k=1)[0]

            # Latency model: base + jitter + occasional tail spike
            base_lat = random.uniform(ep_info[3], ep_info[4])
            if random.random() < 0.05: # 5% tail latency spike
                base_lat += random.uniform(150, 450)
            latency = round(base_lat, 2)

            bytes_sent = int(ep_info[5] * random.uniform(0.7, 1.4))
            ts = base_time + int((i / row_count) * 86400)

            writer.writerow([ts, ip, method, endpoint, status, latency, bytes_sent])

    duration = round(time.time() - start, 3)
    file_size_mb = round(os.path.getsize(csv_path) / (1024 * 1024), 2)
    return {
        "rows": row_count,
        "csv_path": csv_path,
        "file_size_mb": file_size_mb,
        "duration_sec": duration
    }
