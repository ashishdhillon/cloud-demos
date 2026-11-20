# 🎓 Student Lab Guide: Practical 10 — Cloud Horizontal Auto-Scaling & Load Balancing

---

## 📌 1. What is this practical about? (The Real-World Problem)

Imagine you run an online ticketing website. 
- At 9:00 AM, only 5 users are browsing tickets. Two small servers handle the traffic easily.
- At 10:00 AM, tickets for a major concert go live. Suddenly, 50,000 users hit the website simultaneously.
- If your system stays at 2 servers, CPU and capacity hit 100%, servers crash, and users get `504 Gateway Timeout` errors.
- If you pay for 20 large servers 24/7 just in case, you waste thousands of dollars every month when nobody is visiting.

### The Cloud Solution: **Horizontal Auto-Scaling**
Instead of guessing or wasting money, cloud platforms (like AWS Auto Scaling Groups or Kubernetes Horizontal Pod Autoscaler) dynamically:
1. **Scale Out (Up)**: Detect high traffic / CPU, automatically spawn 3, 4, or 5 replica containers, and update the load balancer (Nginx) to distribute requests evenly.
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
docker compose up --build -d
```
*Tip: The first build might take ~30 seconds to download base alpine images. Subsequent runs take under 2 seconds.*

### Step 2: Open the Interactive Web Dashboard
Open your web browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

Follow these 4 guided tasks in your browser to understand how hyperscale auto-scaling works:

### 🔹 Task 1: Baseline Idle Fleet
1. Look at the top KPI stat cards:
   - **Active Fleet Replicas:** `2` (the base minimum replicas: `app-1` and `app-2`).
   - **Cluster Utilization:** `0%`.
   - **Total Capacity:** `40 req/min` (20 req/min per instance).
   - **Cloud Cost Optimization:** `60% savings` vs static 5-VM deployment.
2. Notice how low host resources are. The load balancer routes requests in round-robin fashion between `app-1` and `app-2`.

### 🔹 Task 2: Trigger Flash Sale Spike (Scale-Out)
1. In the **Real-World Traffic Scenario Presets**, click the **⚡ Flash Sale Spike (30 req/s)** button.
2. Watch the **Cluster Utilization Gauge**:
   - Utilization climbs rapidly past the **80% Scale-Out Threshold**.
   - An autoscaling evaluation event triggers!
3. Watch the **Active Container Fleet Card** and **Event Log**:
   - A new worker (`app-3`) is dynamically spun up via the Docker Engine API.
   - Nginx's `upstream.conf` is dynamically reloaded in-memory with zero dropped connections.
   - The traffic automatically distributes across all 3 containers!

### 🔹 Task 3: Observe Flapping Guard & Autoscaling Formula
1. Look at the **Autoscaling Brain (Formula Inspector)**:
   - Notice the live evaluated Kubernetes/AWS formula:
     $$\text{Desired Replicas} = \left\lceil \text{Current Replicas} \times \frac{\text{Current Metric}}{\text{Target Metric (70\%)}} \right\rceil$$
2. Look at the **Thrashing / Flapping Guard**:
   - Notice the **Cooldown Timer (10s)** active badge.
   - Cloud platforms enforce a cooldown timer to prevent "thrashing" (rapidly creating and deleting instances every second).

### 🔹 Task 4: Midnight Traffic Drop & Cloud Cost Savings (Scale-In)
1. Click the **🌙 Midnight Traffic Drop (0 req/s)** preset button.
2. Watch the **Event Log**:
   - Ingestion drops to 0. Over the rolling 60s window, utilization falls below the **20% Scale-In Threshold**.
   - Once the 10-second cooldown expires, the autoscaler cleanly terminates `app-3` and updates Nginx.
3. Review the **Cloud Economics Calculator**:
   - Compare the static over-provisioned cost (\$180/mo for 5 VMs 24/7) vs dynamic auto-scaling (\$72/mo for 2 VMs).
   - Notice the direct **$108/mo (60%) savings** achieved!

---

## 💻 5. Terminal CLI Verification (Optional Practice)

For students who want to practice curl commands in the terminal:

```bash
# 1. Check system metrics and fleet status via REST API
curl -s http://localhost:8080/api/status | python3 -m json.tool

# 2. Check individual instance health and request counts
curl -s http://localhost:8080/api/instances | python3 -m json.tool

# 3. Test load-balanced HTTP request through Nginx proxy
curl -s http://localhost:8080/proxy/
```

---

## 🧠 6. Viva & Interview Questions

1. **What is the difference between Vertical Scaling (Scale-Up) and Horizontal Scaling (Scale-Out)?**
   - *Vertical Scaling* increases the CPU/RAM of a single virtual machine (limited by hardware max, requires downtime).
   - *Horizontal Scaling* adds more identical machines/containers behind a load balancer (virtually unlimited scale, zero downtime).

2. **Why is a "Cooldown Period" critical in cloud auto-scaling?**
   - It prevents "flapping" or "thrashing" — a pathological condition where the system continuously scales out and immediately scales in due to momentary traffic fluctuations.

3. **How does Nginx reload configurations dynamically without dropping user requests?**
   - Nginx uses master/worker processes. Running `nginx -s reload` sends `SIGHUP` to the master process, which starts new workers with the new configuration and allows old workers to gracefully finish active connections before terminating.

4. **What is the Kubernetes Horizontal Pod Autoscaler (HPA) formula?**
   - $$\text{Desired Replicas} = \left\lceil \text{Current Replicas} \times \frac{\text{Current Metric}}{\text{Target Metric}} \right\rceil$$
