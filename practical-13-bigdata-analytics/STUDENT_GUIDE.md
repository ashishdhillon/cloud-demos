# 🎓 Student Lab Guide: Practical 13 — Big Data Cloud Analytics & Vectorized Columnar Processing

---

## 📌 1. What is this practical about? (The Real-World Problem)

In hyperscale clouds (Google BigQuery, AWS Athena, Snowflake, Databricks), companies query billions of web access logs every day:
- **The Old Way (Row-Oriented MapReduce / Hadoop):** Every log row is stored sequentially as text (CSV/JSON). If you only want to know the *Average Response Time*, the computer still has to read all the IPs, user agents, and timestamps off disk. This chokes memory bandwidth and is painfully slow.
- **The Modern Cloud Way (Vectorized Columnar Engines):**
  1. **Columnar Storage (Apache Parquet):** Data is stored column-by-column. The query engine only reads the *Latency* column from disk (**Projection Pushdown**), ignoring 85% of unneeded bytes.
  2. **SIMD Vectorization (DuckDB):** Operates on arrays of values packed directly into CPU vector registers in native C++, running **10x to 30x faster** than row-by-row loops.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-13-bigdata-analytics
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Compare Parquet vs. CSV Storage
1. Look at the top stat cards:
   - **Row CSV Storage:** `~2.81 MB` (50,000 uncompressed HTTP logs).
   - **Columnar Parquet:** `~0.38 MB` (ZSTD dictionary compressed).
   - **Storage Reduction:** **`~86.5% Saved!`**
2. In cloud storage (like AWS S3), reducing your dataset from 2.8 GB to 380 MB saves 86% of storage and network transfer costs.

### 🔹 Task 2: Run the Architectural Race (MapReduce vs. DuckDB)
1. Click the big blue button: **"🚀 Run Benchmark Race (50,000 Records)"**.
2. Watch the side-by-side results:
   - **Classic MapReduce:** Takes `~150 ms` (Map phase tokenizing strings, Shuffle grouping keys, Reduce calculating percentiles).
   - **Vectorized Columnar (DuckDB):** Takes `~11 ms`!
   - **Speedup:** Over **`13x to 20x Faster`** on identical 50,000 rows.
3. Review the aggregated output table: Notice both engines return the exact same mathematical results (Requests, Avg Latency, P95 Latency, Errors).

### 🔹 Task 3: Interactive Cloud SQL Analytics
1. In the **Interactive Cloud SQL Console**, click preset buttons:
   - **"HTTP Status Distribution"**: Analyzes percentage breakdown of 200 OK vs 4xx/5xx errors.
   - **"Top IPs by Egress (DDoS)"**: Identifies top bandwidth consumers in milliseconds.
   - **"Hourly Traffic Profile"**: Groups traffic by hour of the day.
2. Notice every analytical query executes in **sub-15 milliseconds**!

---

## 💻 5. Terminal CLI Verification

Run queries directly from the command line:

```bash
# 1. Fetch dataset storage statistics
curl -s http://localhost:8080/api/stats | python3 -m json.tool

# 2. Trigger the benchmark race via API
curl -s -X POST http://localhost:8080/api/benchmark | python3 -m json.tool

# 3. Execute a preset query
curl -s http://localhost:8080/api/query/top_ips | python3 -m json.tool
```

---

## 🧠 6. Viva & Interview Questions

1. **Why is Columnar format (Parquet) faster than Row format (CSV) for analytical queries (OLAP)?**
   - Analytical queries typically aggregate a few columns across millions of rows (e.g. `SUM(bytes)`). Columnar formats enable **Projection Pushdown**, loading only the specific column needed from disk, skipping 80%+ of I/O.
2. **What are the three core phases of the MapReduce paradigm?**
   - **Map:** Filters and transforms raw input records into intermediate key-value pairs.
   - **Shuffle & Sort:** Re-partitions and groups all intermediate values sharing the same key.
   - **Reduce:** Aggregates values for each key to produce final summarized results.
3. **What is SIMD in modern vectorized query engines?**
   - Single Instruction, Multiple Data (SIMD) allows a single CPU instruction to perform an operation (like addition or comparison) on an entire vector/array of data simultaneously rather than one element at a time.

---

## 🧹 7. Teardown / Reclaiming Memory
```bash
docker compose down
```
