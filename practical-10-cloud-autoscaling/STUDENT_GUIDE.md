# 🎓 Student Lab Guide: Practical 10 — Cloud Horizontal Auto-Scaling & Load Balancing

---

## 📌 1. What is this practical about? (The Real-World Problem)

Imagine you run an online ticketing website. 
- At 9:00 AM, only 5 users are browsing tickets. One small server handles the traffic easily.
- At 10:00 AM, tickets for a major concert go live. Suddenly, 50,000 users hit the website simultaneously.
- If your system stays at 1 server, the CPU hits 100%, the server crashes, and users get `504 Gateway Timeout` errors.
- If you pay for 20 large servers 24/7 just in case, you waste thousands of dollars every month when nobody is visiting.

### The Cloud Solution: **Horizontal Auto-Scaling**
Instead of guessing or wasting money, cloud platforms (like AWS Auto Scaling Groups or Kubernetes Horizontal Pod Autoscaler) dynamically:
1. **Scale Out (Up)**: Detect high traffic / CPU, automatically spawn 2, 3, or 4 replica containers, and update the load balancer (Nginx) to distribute requests evenly.
2. **Scale In (Down)**: When traffic drops back down, wait for a safety cooldown period and gracefully shut down extra servers to save money.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed on your machine.
- No AWS, GCP, or paid cloud account needed (runs 100% locally and free).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
Open your terminal (macOS Terminal, Linux Bash, or Windows PowerShell) and run:

```bash
cd practical-10-cloud-autoscaling
cp .env.example .env
docker compose up --build -d
```
*Tip: The first build might take ~30 seconds to download base alpine images. Subsequent runs take under 2 seconds.*

### Step 2: Open the Interactive Web Dashboard
Open your web browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

Follow these 4 tasks in your browser to understand how hyperscale auto-scaling works:

### 🔹 Task 1: Baseline Idle Traffic
1. Look at the top stat cards:
   - **Active Worker Pool:** `1 Worker` (the minimum base replica).
   - **System CPU Load:** `< 20%`.
   - **Traffic Generator:** `0 req/sec`.
2. Notice how low host resources are. The load balancer routes 100% of requests to `worker-1`.

### 🔹 Task 2: Trigger a Traffic Surge (Scale-Out)
1. In the **Traffic Generator Slider**, drag the slider from `0` up to **`75 req/sec`** or click the **"⚡ Flash Crowd Surge"** button.
2. Watch the **Cluster CPU Load Gauge**:
   - The CPU will climb past the **70% Threshold**.
   - An autoscaling evaluation event triggers!
3. Watch the **Active Container Fleet Card**:
   - A new worker (`worker-2`, then `worker-3`) is spun up via Docker.
   - Nginx's `upstream.conf` is dynamically reloaded in-memory with zero dropped connections.
   - The CPU load distributes across the new containers, stabilizing below 60%.

### 🔹 Task 3: Observe Real-Time Load Balancing
1. In the **Real-Time Request Distribution** panel, observe the request counters for `worker-1`, `worker-2`, and `worker-3`.
2. Notice how the load balancer uses **Round-Robin** to balance traffic evenly across the active pool.

### 🔹 Task 4: Cool Down & Scale-In
1. Drag the traffic slider back down to **`0 req/sec`**.
2. Watch the **Event Log**:
   - CPU drops below 30%.
   - The **Cooldown Timer (10s)** starts ticking. (In real cloud environments, cooldown timers prevent rapid thrashing/flapping).
   - Once cooldown finishes, the autoscaler terminates `worker-3` and `worker-2`, returning to `1 Worker`.

---

## 💻 5. Terminal CLI Verification (Optional Practice)

For students who want to practice curl commands in the terminal:

```bash
# 1. Check system metrics and worker pool via API
curl -s http://localhost:8080/api/metrics | python3 -m json.tool

# 2. Check active workers registered in Nginx upstream
curl -s http://localhost:8080/api/workers | python3 -m json.tool

# 3. Simulate high traffic directly from the CLI
curl -s -X POST http://localhost:8080/api/traffic -H "Content-Type: application/json" -d '{"rps": 80}'
```

---

## 🧠 6. Viva & Interview Questions

1. **What is the difference between Vertical Scaling (Scale-Up) and Horizontal Scaling (Scale-Out)?**
   - *Vertical Scaling* increases the CPU/RAM of a single virtual machine (limited by hardware max, requires downtime).
   - *Horizontal Scaling* adds more identical machines/containers behind a load balancer (virtually unlimited scale, zero downtime).
2. **Why is a "Cooldown Period" critical in cloud auto-scaling?**
   - Without a cooldown, brief spikes could trigger rapid scaling up and down (known as "flapping" or "thrashing"), causing unnecessary container restarts and unstable performance.
3. **How does Nginx handle dynamic changes to backend servers?**
   - Modern cloud setups dynamically regenerate the `upstream` configuration block and issue a reload signal (`nginx -s reload`) without terminating existing client TCP connections.

---

## 🧹 7. Teardown / Reclaiming Memory
When finished, stop the lab to free host port `8080` and all memory:

```bash
docker compose down
```
All containers and networks will be cleanly removed.
