# Practical 13: Big Data Cloud Analytics & Vectorized Columnar Processing

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.1-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Parquet](https://img.shields.io/badge/Apache-Parquet_ZSTD-red.svg)](https://parquet.apache.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 50 MB RAM) **Big Data Cloud Analytics Engine** demonstrating the architectural shift from legacy row-oriented MapReduce pipelines to modern **vectorized columnar execution (DuckDB, Google BigQuery, AWS Athena, ClickHouse)** on large-scale cloud access log datasets.

---

## 🏗️ Core Cloud Big Data Architectures

### 1. Row Storage vs. Columnar Parquet
- **Row Storage (CSV/JSON)**: Every record stores all attributes contiguously. Scanning a single metric (e.g. `response_time_ms`) forces the engine to read, parse, and discard all unneeded columns (IP, timestamp, user agent), saturating memory bus bandwidth.
- **Columnar Storage (Apache Parquet + ZSTD)**: Attributes are stored in separate, compressed column chunks with dictionary encoding. With **Projection Pushdown**, DuckDB reads only the target columns from disk, reducing storage footprint by **~83%** and I/O wait times by **> 90%**.

### 2. Algorithmic MapReduce vs. Vectorized SIMD
- **MapReduce Pipeline (Map &rarr; Shuffle &rarr; Reduce)**:
  - *Map Phase*: Tokenizes row strings, generating key-value pairs `((endpoint, method), (latency, bytes, is_error))`.
  - *Shuffle/Sort*: Partitions pairs across hash buckets.
  - *Reduce Phase*: Aggregates records, sorts latencies to compute P95 quantiles.
  - *Bottleneck*: Object allocation overhead, pointer chasing, and sequential row scanning.
- **Vectorized SIMD Engine (DuckDB)**:
  - Operates on columnar vectors (arrays of data in CPU cache).
  - Employs CPU vector registers (SIMD) to execute filter and aggregation operations natively in C++/Rust without dynamic typing or interpretive overhead.
  - Runs typical batch analytical queries **10x to 30x faster** than row-oriented pipelines.

---

## 🚀 Quickstart & Sequential Execution

### 1. Launch the Stack
```bash
cd practical-13-bigdata-analytics
cp .env.example .env
docker compose up --build -d
```

### 2. Verify Health & Analytics Engine
```bash
# Verify health probe
curl -s http://localhost:8080/health | python3 -m json.tool

# Inspect dataset storage stats & compression ratio
curl -s http://localhost:8080/api/stats | python3 -m json.tool
```

### 3. Run Architectural Benchmark Race via CLI
```bash
curl -s -X POST http://localhost:8080/api/benchmark | python3 -m json.tool
```

### 4. Interactive Web Dashboard
Open **[http://localhost:8080](http://localhost:8080)** in your browser to:
- Run the **Architectural Race** to observe real-time MapReduce phase latencies vs. DuckDB speedup.
- Explore preset queries (HTTP status code error distribution, top egress IPs, hourly traffic surge).
- Write custom SQL queries directly against the in-memory `logs` columnar table.
- Dynamically scale the dataset from 25,000 to 100,000 rows.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|:---|:---:|:---|
| `/health` | `GET` | Microservice health status |
| `/api/stats` | `GET` | Dataset row count, CSV size, Parquet size, and compression savings |
| `/api/benchmark` | `POST` | Executes the head-to-head race between Python MapReduce and DuckDB |
| `/api/query/<query_id>` | `GET` | Runs a preset query (`status_codes`, `top_ips`, `hourly_trends`) |
| `/api/query/custom` | `POST` | Executes custom analytical SQL (`{"sql": "SELECT COUNT(*) FROM logs"}`) |
| `/api/dataset/regenerate` | `POST` | Regenerates dataset with custom volume (`{"rows": 50000}`) |

---

## 🧹 Teardown & RAM Reclamation
```bash
docker compose down
```
Instantly terminates containers and frees all memory.
