# 🎓 Student Lab Guide: Practical 12 — Serverless Applications (FaaS), Cold Starts & Micro-Billing

---

## 📌 1. What is this practical about? (The Real-World Problem)

Traditionally, when hosting code in the cloud, you rent a Virtual Machine (e.g. AWS EC2).
- You pay for that VM 24 hours a day, 365 days a year, even when nobody is calling your code.
- You have to manage the operating system, install Linux security patches, and configure auto-scaling.

### The Cloud Solution: **Serverless Function-as-a-Service (FaaS)**
With AWS Lambda or Google Cloud Functions, you simply upload your Python or JavaScript code:
1. **Zero Cost at Rest:** When no traffic arrives, 0 containers run and you pay exactly **$0.00**.
2. **Event-Driven Execution:** When an HTTP request arrives, the cloud spins up an ephemeral sandbox container, runs your code, returns the response, and bills you only for the exact milliseconds used (**Micro-Billing**).
3. **The Trade-Off (Cold Starts vs Warm Reuse):**
   - **Cold Start (~280 ms):** The very first request must wait for the cloud provider to allocate a container, download code, and initialize the runtime.
   - **Warm Reuse (~15 ms):** Subsequent requests reuse the pre-warmed sandbox container instantly, running over **15x faster and 4x cheaper**!

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- No AWS or paid cloud account needed.

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-12-serverless-lambda
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Trigger a Cold Start Invocation
1. Select Function: **Image Thumbnail Generator** (256 MB RAM).
2. Click **"🚀 Invoke Single Function"**.
3. Look at the execution trace result:
   - **Status:** `COLD START 🔵`.
   - **Initialization Duration:** `~270 ms` (MicroVM container creation & dependency import).
   - **Execution Duration:** `~35 ms`.
   - **Total Billed Duration:** `~305 ms` &rarr; Billed Cost: `~$0.00000150`.
   - Notice the created sandbox ID (e.g. `sandbox-ead1ffa1`).

### 🔹 Task 2: Trigger an Immediate Warm Reuse Invocation
1. Immediately click **"🚀 Invoke Single Function"** a second time.
2. Look at the new result:
   - **Status:** `WARM CONTAINER REUSE 🟢`.
   - **Initialization Duration:** `0.00 ms`!
   - **Total Execution Duration:** `~35 ms` (Over **8x faster** than the cold start).
   - Notice the sandbox ID is identical (`sandbox-ead1ffa1`) — the cloud runtime kept the sandbox alive in memory!
   - Billed cost dropped to `~$0.00000035` (over 4x cheaper because no container spawn time was billed).

### 🔹 Task 3: Test Concurrency Fan-Out (Burst Invocations)
1. Select Function: **NLP Sentiment Classification** (128 MB RAM).
2. Set Concurrency Burst Count to **`4 Requests`**.
3. Click **"⚡ Dispatch Concurrency Burst"**:
   - Because 4 requests arrived at the exact same millisecond, a single container cannot execute them simultaneously.
   - The FaaS engine automatically **fans out**, provisioning 4 parallel sandboxes in parallel!
   - Watch the active sandboxes counter increase in the top stats.

---

## 💻 5. Terminal CLI Verification

Invoke functions directly using `curl`:

```bash
# 1. Fetch available serverless functions
curl -s http://localhost:8080/api/functions | python3 -m json.tool

# 2. Invoke a function (triggers cold start if idle)
curl -s -X POST http://localhost:8080/api/invoke \
  -H "Content-Type: application/json" \
  -d '{"function_id": "image-thumbnailer"}' | python3 -m json.tool

# 3. View cumulative micro-billing and warm reuse efficiency
curl -s http://localhost:8080/api/stats | python3 -m json.tool
```

---

## 🧠 6. Viva & Interview Questions

1. **What is a Cold Start in AWS Lambda?**
   - A cold start occurs when a serverless function is invoked after being idle or when scaling out to new concurrent workers. The cloud provider must locate compute resources, download the code package, launch the container runtime, and execute initialization code before handling the request.
2. **How do cloud engineers mitigate cold starts in production?**
   - By using **Provisioned Concurrency** (pre-warming instances), keeping deployment packages small, utilizing lightweight runtimes (Node.js/Go/Python over heavy JVM), or configuring periodic scheduled "ping" warmers.
3. **How does AWS Lambda calculate billing?**
   - AWS Lambda bills based on two factors:
     1. Number of requests ($0.20 per 1 million requests).
     2. Duration multiplied by allocated memory, measured in **GB-seconds** (billed rounded up to the nearest 1 ms).

---

## 🧹 7. Teardown / Reclaiming Memory
```bash
docker compose down
```
