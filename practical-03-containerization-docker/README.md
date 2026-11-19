# Practical 03: Containerization with Docker & Cgroups Inspector

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Nginx](https://img.shields.io/badge/Nginx-1.27_Alpine-009639?logo=nginx&logoColor=white)](https://nginx.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 35 MB RAM) **Docker Containerization, Linux Namespaces & Cgroups v2 Resource Inspector** demonstrating container isolation, image layering (UnionFS/OverlayFS), Copy-on-Write (CoW) disk mechanics, kernel-enforced memory and CPU quotas, and non-root security sandboxing.

---

## 🏗️ Core Cloud & Containerization Concepts

### 1. Linux Control Groups (Cgroups v2)
Container engines do not provide hardware emulation; they use Linux kernel **cgroups** to meter, limit, and throttle physical hardware resources:
- **`memory.max` / `memory.current`**: Enforces a strict memory ceiling (configured to `128 MB`). If processes exceed this limit without reclaimable page cache, the kernel invokes the **Out-Of-Memory (OOM) Killer** to terminate rogue tasks with `SIGKILL`.
- **`cpu.max`**: Controls Completely Fair Scheduler (CFS) quotas. Configured to `50000 100000` (50ms per 100ms period), capping CPU consumption to `0.50 vCPU`. When intensive computation exceeds this quota, execution is throttled (`nr_throttled`).

### 2. Linux Namespaces (Kernel Isolation)
- **PID Namespace**: Inside the container, the primary process runs as **PID 1**, isolated from the host operating system's process tree.
- **User Namespace**: Security hardening creates an unprivileged user `cloudapp` (`UID 10001 : GID 10001`), preventing container breakout privileges.
- **UTS Namespace**: Provides an isolated virtual hostname distinct from the physical host.

### 3. Image Layering & OverlayFS (Copy-on-Write)
Docker images are built as stacked immutable read-only filesystem layers. During runtime:
- Layers 1–4 (`base-os`, `user-setup`, `pip-deps`, `app-code`) are strictly **Read-Only**.
- Docker mounts an ephemeral **Read-Write layer** on top using OverlayFS. Modifying files creates a copy in the upper layer without touching the lower layers (**Copy-on-Write**).

---

## 🚀 Quickstart & Sequential Execution

### 1. Clone & Launch the Stack
```bash
cd practical-03-containerization-docker
cp .env.example .env
docker compose up --build -d
```

### 2. Verify Container Health & Cgroups
```bash
# Check container status
docker ps --filter "name=practical-03"

# Verify health endpoint (200 OK)
curl -s http://localhost:8080/healthz | python3 -m json.tool

# Inspect cgroup memory ceiling and user ID
curl -s http://localhost:8080/system-metrics | python3 -m json.tool
```

### 3. Open the Interactive Web Dashboard
Navigate to **[http://localhost:8080](http://localhost:8080)** in your browser to:
- Test real-time memory stress (+20 MB / +50 MB) and observe the cgroup limit gauge.
- Fire the CPU burst loop to see CFS scheduler throttling active in real-time.
- Click **"Touch File in Ephemeral Layer"** to observe Copy-on-Write (CoW) file creation.
- Toggle the **Liveness Probe Crash** switch to simulate how orchestrators detect unhealthy microservices.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|:---|:---:|:---|
| `/` | `GET` | Microservice metadata, kernel platform, and isolation status |
| `/healthz` | `GET` | Liveness & readiness probe (returns `200 OK` or `503 Service Unavailable`) |
| `/system-metrics` | `GET` | Raw cgroup memory ceiling, PID, and UID |
| `/api/cgroups` | `GET` | Full cgroup v2 metrics (`memory.current`, `cpu.max`, `pids.current`, etc.) |
| `/api/cgroups/stress-memory` | `POST` | Allocate (`{"action": "allocate", "mb": 20}`) or free memory |
| `/api/cgroups/stress-cpu` | `POST` | Trigger a 5-second CPU burner loop |
| `/api/layers` | `GET` | List Docker image layer breakdown and ephemeral layer files |
| `/api/layers/touch-file` | `POST` | Write a new file to the ephemeral container layer (CoW demo) |
| `/api/health/toggle` | `POST` | Toggle liveness probe status between healthy (200) and failed (503) |
| `/api/logs` | `GET` | Fetch recent kernel and container lifecycle audit events |

---

## 🧹 Teardown & RAM Reclamation
```bash
docker compose down
```
Instantly reclaims all allocated ports and host memory.
