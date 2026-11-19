import os
import time
import csv
import threading
import duckdb
from collections import defaultdict
from data_generator import generate_dataset

DATA_DIR = "/app/data"
CSV_FILE = os.path.join(DATA_DIR, "cloud_access_logs.csv")
PARQUET_FILE = os.path.join(DATA_DIR, "cloud_access_logs.parquet")

class AnalyticsEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.row_count = 50000
        self.is_ready = False
        self.db = duckdb.connect(database=":memory:")
        self._init_data()

    def _init_data(self):
        with self.lock:
            if not os.path.exists(CSV_FILE):
                generate_dataset(CSV_FILE, self.row_count)

            # Create Parquet file from CSV using DuckDB
            self.db.execute(f"""
                CREATE TABLE logs AS SELECT * FROM read_csv_auto('{CSV_FILE}', header=True);
            """)
            self.db.execute(f"""
                COPY logs TO '{PARQUET_FILE}' (FORMAT PARQUET, COMPRESSION ZSTD);
            """)
            self.is_ready = True

    def get_stats(self):
        with self.lock:
            csv_size_mb = round(os.path.getsize(CSV_FILE) / (1024 * 1024), 2) if os.path.exists(CSV_FILE) else 0.0
            parquet_size_mb = round(os.path.getsize(PARQUET_FILE) / (1024 * 1024), 2) if os.path.exists(PARQUET_FILE) else 0.0
            compression_ratio = round((1 - (parquet_size_mb / csv_size_mb)) * 100, 1) if csv_size_mb > 0 else 0.0

            count_res = self.db.execute("SELECT COUNT(*) FROM logs;").fetchone()
            total_records = count_res[0] if count_res else 0

            return {
                "total_records": total_records,
                "csv_size_mb": csv_size_mb,
                "parquet_size_mb": parquet_size_mb,
                "storage_reduction_pct": compression_ratio,
                "duckdb_version": duckdb.__version__,
                "vectorized_engine": "Vectorized SIMD Columnar Execution"
            }

    def regenerate_dataset(self, rows: int = 50000):
        with self.lock:
            self.row_count = max(5000, min(150000, rows))
            if os.path.exists(CSV_FILE):
                os.remove(CSV_FILE)
            if os.path.exists(PARQUET_FILE):
                os.remove(PARQUET_FILE)
            self.db.execute("DROP TABLE IF EXISTS logs;")
            generate_dataset(CSV_FILE, self.row_count)
            self.db.execute(f"""
                CREATE TABLE logs AS SELECT * FROM read_csv_auto('{CSV_FILE}', header=True);
            """)
            self.db.execute(f"""
                COPY logs TO '{PARQUET_FILE}' (FORMAT PARQUET, COMPRESSION ZSTD);
            """)
            return self.get_stats()

    def run_benchmark_race(self):
        """
        Runs both the Python MapReduce pipeline and the DuckDB Vectorized SQL engine
        on the exact same dataset to demonstrate architectural performance differences.
        """
        with self.lock:
            # 1. Pure Python MapReduce Pipeline
            mr_start = time.time()
            map_start = time.time()

            # --- MAP PHASE ---
            intermediate_pairs = []
            with open(CSV_FILE, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = (row["endpoint"], row["method"])
                    val = (float(row["response_time_ms"]), int(row["bytes_sent"]), 1 if int(row["status_code"]) >= 400 else 0)
                    intermediate_pairs.append((key, val))
            map_duration = round((time.time() - map_start) * 1000, 2)

            # --- SHUFFLE & SORT PHASE ---
            shuffle_start = time.time()
            grouped_data = defaultdict(list)
            for key, val in intermediate_pairs:
                grouped_data[key].append(val)
            shuffle_duration = round((time.time() - shuffle_start) * 1000, 2)

            # --- REDUCE PHASE ---
            reduce_start = time.time()
            mr_results = []
            for (endpoint, method), records in grouped_data.items():
                req_count = len(records)
                latencies = [r[0] for r in records]
                bytes_list = [r[1] for r in records]
                error_count = sum(r[2] for r in records)

                avg_latency = round(sum(latencies) / req_count, 2)
                # p95 calculation via sort
                latencies.sort()
                p95_idx = int(req_count * 0.95)
                p95_latency = round(latencies[p95_idx], 2)
                traffic_mb = round(sum(bytes_list) / (1024 * 1024), 2)

                mr_results.append({
                    "endpoint": endpoint,
                    "method": method,
                    "requests": req_count,
                    "avg_latency": avg_latency,
                    "p95_latency": p95_latency,
                    "traffic_mb": traffic_mb,
                    "errors": error_count
                })

            mr_results.sort(key=lambda x: x["requests"], reverse=True)
            reduce_duration = round((time.time() - reduce_start) * 1000, 2)
            mr_total_ms = round((time.time() - mr_start) * 1000, 2)

            # 2. DuckDB Vectorized Columnar SQL Execution
            sql_start = time.time()
            duck_res = self.db.execute("""
                SELECT 
                    endpoint, 
                    method, 
                    COUNT(*) as requests, 
                    ROUND(AVG(response_time_ms), 2) as avg_latency, 
                    ROUND(quantile_cont(response_time_ms, 0.95), 2) as p95_latency, 
                    ROUND(SUM(bytes_sent) / (1024 * 1024), 2) as traffic_mb,
                    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as errors
                FROM logs
                GROUP BY endpoint, method
                ORDER BY requests DESC;
            """).fetchall()
            duck_total_ms = round((time.time() - sql_start) * 1000, 2)

            columns = ["endpoint", "method", "requests", "avg_latency", "p95_latency", "traffic_mb", "errors"]
            duck_results = [dict(zip(columns, row)) for row in duck_res]

            speedup_factor = round(mr_total_ms / max(0.1, duck_total_ms), 1)

            return {
                "records_evaluated": len(intermediate_pairs),
                "mapreduce": {
                    "total_ms": mr_total_ms,
                    "map_phase_ms": map_duration,
                    "shuffle_phase_ms": shuffle_duration,
                    "reduce_phase_ms": reduce_duration,
                    "paradigm": "Row-by-Row Algorithmic MapReduce"
                },
                "duckdb": {
                    "total_ms": duck_total_ms,
                    "paradigm": "Vectorized Columnar In-Memory Processing",
                    "speedup_vs_mapreduce": f"{speedup_factor}x Faster"
                },
                "results": duck_results
            }

    def execute_preset_query(self, query_id: str):
        with self.lock:
            queries = {
                "status_codes": {
                    "title": "HTTP Status Code & Error Rate Distribution",
                    "sql": """
                        SELECT 
                            status_code,
                            COUNT(*) as total_occurrences,
                            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage_of_traffic,
                            ROUND(AVG(response_time_ms), 2) as avg_latency_ms
                        FROM logs
                        GROUP BY status_code
                        ORDER BY total_occurrences DESC;
                    """
                },
                "top_ips": {
                    "title": "Top Client IP Addresses by Bandwidth & Egress",
                    "sql": """
                        SELECT 
                            client_ip,
                            COUNT(*) as total_requests,
                            ROUND(SUM(bytes_sent) / (1024 * 1024), 2) as total_egress_mb,
                            ROUND(AVG(bytes_sent), 1) as avg_payload_bytes,
                            COUNT(CASE WHEN status_code >= 400 THEN 1 END) as failed_requests
                        FROM logs
                        GROUP BY client_ip
                        ORDER BY total_egress_mb DESC
                        LIMIT 10;
                    """
                },
                "hourly_trends": {
                    "title": "Hourly Traffic Surge & Latency Profile",
                    "sql": """
                        SELECT 
                            strftime(epoch_ms(timestamp * 1000), '%H:00') as hour_of_day,
                            COUNT(*) as requests,
                            ROUND(AVG(response_time_ms), 2) as avg_latency_ms,
                            ROUND(quantile_cont(response_time_ms, 0.99), 2) as p99_latency_ms,
                            ROUND(SUM(bytes_sent) / (1024 * 1024), 2) as traffic_mb
                        FROM logs
                        GROUP BY hour_of_day
                        ORDER BY hour_of_day ASC;
                    """
                }
            }

            if query_id not in queries:
                query_id = "status_codes"

            target = queries[query_id]
            start = time.time()
            cursor = self.db.execute(target["sql"])
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            duration_ms = round((time.time() - start) * 1000, 2)

            return {
                "query_id": query_id,
                "title": target["title"],
                "sql": target["sql"].strip(),
                "duration_ms": duration_ms,
                "columns": columns,
                "rows": [dict(zip(columns, r)) for r in rows]
            }

    def execute_custom_sql(self, sql_query: str):
        with self.lock:
            # Guard against dangerous statements
            normalized = sql_query.strip().lower()
            if not normalized.startswith("select") and not normalized.startswith("with"):
                raise ValueError("Only read-only SELECT and WITH analytical queries are permitted.")

            start = time.time()
            cursor = self.db.execute(sql_query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            duration_ms = round((time.time() - start) * 1000, 2)

            return {
                "sql": sql_query.strip(),
                "duration_ms": duration_ms,
                "columns": columns,
                "rows": [dict(zip(columns, r)) for r in rows[:100]] # Limit to 100 rows for display safety
            }
