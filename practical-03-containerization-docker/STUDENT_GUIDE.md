# 🎓 Student Lab Guide: Practical 03 — Docker Containerization, Namespaces & Cgroups v2

---

## 📌 1. What is this practical about? (The Real-World Problem)

Students often think Docker is a "lightweight virtual machine". **It is not!**
- Virtual Machines (VMs) emulate entire physical hardware (BIOS, virtual CPU, guest OS kernel), which consumes gigabytes of RAM and takes minutes to boot.
- Docker containers are simply standard Linux processes running directly on the host kernel, isolated by two core Linux kernel features:
  1. **Namespaces (What the container can SEE):** Isolates process trees (PID namespace), network interfaces, and user IDs (UID 10001 non-root).
  2. **Control Groups / Cgroups (What the container can USE):** Sets strict hard ceilings on physical RAM (`memory.max`), throttles CPU cycles (`cpu.max`), and caps process counts.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-03-containerization-docker
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Inspect Linux Cgroups & Memory Ceilings
1. Observe the **Memory Limits Gauge**:
   - The container has a kernel hard limit of **`128 MB`** (set in `docker-compose.yml`).
   - Baseline usage is ~33 MB.
2. Click **"+20 MB RAM"** and **"+50 MB RAM"**:
   - Watch the gauge fill up to ~103 MB (over 80%).
   - The bar changes color to amber/red, warning that the process is approaching the Linux Out-Of-Memory (OOM) threshold.
3. Click **"Reclaim Memory (Free)"**:
   - Notice the memory drops immediately back down to ~33 MB as the buffer is garbage collected.

### 🔹 Task 2: Observe Completely Fair Scheduler (CFS) CPU Throttling
1. Click **"🔥 Simulate CPU Spike (5s)"**:
   - The backend spins a heavy mathematical loop inside a worker thread.
   - Look at the top stat card: **`Throttled CFS Periods`**.
   - Because the container is capped at **`0.50 vCPU`** (`50000us / 100000us`), the Linux kernel scheduler actively throttles execution cycles, preventing a single rogue container from starving the host machine!

### 🔹 Task 3: Inspect Docker Image Layers & Copy-on-Write (OverlayFS)
1. In the right panel, observe the **Docker Image Layer Stack**:
   - Layers 1 to 4 (`base python`, `user setup`, `pip install`, `app code`) are **Immutable Read-Only**.
   - Layer 5 is the **Ephemeral Read-Write Layer (OverlayFS)**.
2. Click **"✍️ Touch File in Ephemeral Layer (CoW Demo)"**:
   - Notice a new file (`log_stream_XXXXXX.txt`) appears in Layer 5.
   - The underlying image layers remain untouched! When the container is destroyed (`docker rm`), this top layer vanishes, leaving the base image pristine.

### 🔹 Task 4: Test Container Liveness Probes
1. Look at the **Liveness Probe Indicator**: Status is `HEALTHY (200 OK)`.
2. Click **"Simulate Microservice Crash (Toggle 503)"**:
   - The `/healthz` probe immediately returns `503 Service Unavailable`.
   - The probe turns Red. In production, Docker Swarm or Kubernetes would detect this failure and automatically restart the unhealthy container.

---

## 💻 5. Terminal CLI Verification

Verify the Linux cgroups and container status via terminal:

```bash
# 1. Inspect real Linux kernel cgroups and isolation status
curl -s http://localhost:8080/system-metrics | python3 -m json.tool

# 2. Check native Docker health probe
docker ps --filter "name=practical-03"

# 3. View live container RAM consumption from Docker engine
docker stats practical-03-container-backend --no-stream
```

---

## 🧠 6. Viva & Interview Questions

1. **What is the difference between Linux Namespaces and Cgroups?**
   - *Namespaces* provide **isolation** (what a process can see: its own PID tree, network devices, mount points).
   - *Cgroups* provide **resource metering & limiting** (how much RAM, CPU, or I/O a process group can consume).
2. **What is the Linux OOM-Killer?**
   - When a container's memory consumption reaches its `memory.max` limit and cannot reclaim page cache, the Linux kernel Out-Of-Memory (OOM) killer fires `SIGKILL (signal 9)` to terminate the process instantly to protect host system stability.
3. **What is Copy-on-Write (CoW) in Docker storage drivers (OverlayFS)?**
   - Lower image layers are strictly read-only and shared across all running containers. When a container needs to modify an existing file, OverlayFS copies the file up to the container's thin writable layer before modifying it, preserving the base image.

---

## 🧹 7. Teardown / Reclaiming Memory
```bash
docker compose down
```
