# Cloud Systems Engineering Labs & Interactive Demos

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Cloud_Native-orange.svg)]()
[![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen.svg)]()

A curated collection of **lightweight, production-grade, interactive cloud systems engineering projects and real-time simulators**.

Designed for engineers, students, and educators to experience core hyperscale cloud concepts (auto-scaling, object storage, IAM engines, serverless cold starts, and IoT edge brokers) running **100% locally on personal hardware with zero paid cloud accounts or subscriptions required**.

---

## 🧭 Project Roadmap & Curriculum Index

Each project is self-contained in its own directory, includes an interactive web dashboard or visual simulator, and adheres to strict resource-efficiency constraints (< 150 MB RAM per practical). Every practical includes a comprehensive **Student Lab Guide (`STUDENT_GUIDE.md`)** with real-world explanations, interactive step-by-step tasks, and viva/interview prep.

| Lab # | Project Directory | Core Cloud Concept | Student Walkthrough | PDF Explainer | Status |
|:---:|:---|:---|:---:|:---:|:---:|
| **10** | [**`practical-10-cloud-autoscaling/`**](practical-10-cloud-autoscaling/README.md) | Horizontal Auto-Scaling & Load Balancing | [📖 **Student Guide**](practical-10-cloud-autoscaling/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-10-cloud-autoscaling/EXPLAINER.pdf) | **Production Ready** |
| **06** | [**`practical-06-object-storage-s3/`**](practical-06-object-storage-s3/README.md) | Object Storage, Presigned URLs & Expiring ACLs | [📖 **Student Guide**](practical-06-object-storage-s3/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-06-object-storage-s3/EXPLAINER.pdf) | **Production Ready** |
| **15** | [**`practical-15-edge-computing-mqtt/`**](practical-15-edge-computing-mqtt/README.md) | Edge Computing & IoT Telemetry Broker | [📖 **Student Guide**](practical-15-edge-computing-mqtt/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-15-edge-computing-mqtt/EXPLAINER.pdf) | **Production Ready** |
| **07** | [**`practical-07-iam-access-control/`**](practical-07-iam-access-control/README.md) | Identity & Access Management (IAM / Least Privilege) | [📖 **Student Guide**](practical-07-iam-access-control/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-07-iam-access-control/EXPLAINER.pdf) | **Production Ready** |
| **12** | [**`practical-12-serverless-lambda/`**](practical-12-serverless-lambda/README.md) | Serverless FaaS, Cold Starts & Micro-Billing | [📖 **Student Guide**](practical-12-serverless-lambda/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-12-serverless-lambda/EXPLAINER.pdf) | **Production Ready** |
| **03** | [**`practical-03-containerization-docker/`**](practical-03-containerization-docker/README.md) | Cgroups v2 Resource Quotas & OverlayFS CoW | [📖 **Student Guide**](practical-03-containerization-docker/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-03-containerization-docker/EXPLAINER.pdf) | **Production Ready** |
| **13** | [**`practical-13-bigdata-analytics/`**](practical-13-bigdata-analytics/README.md) | Vectorized Columnar Analytics vs. MapReduce | [📖 **Student Guide**](practical-13-bigdata-analytics/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-13-bigdata-analytics/EXPLAINER.pdf) | **Production Ready** |
| **05** | [**`practical-05-cloud-networking-vpc/`**](practical-05-cloud-networking-vpc/README.md) | Dual-Tier VPC, Hop-by-Hop Packet Tracer & SGs | [📖 **Student Guide**](practical-05-cloud-networking-vpc/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-05-cloud-networking-vpc/EXPLAINER.pdf) | **Production Ready** |
| **08** | [**`practical-08-cloud-security/`**](practical-08-cloud-security/README.md) | **Cloud Security & Envelope Encryption (KMS)** | [📖 **Student Guide**](practical-08-cloud-security/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-08-cloud-security/EXPLAINER.pdf) | **Production Ready** |
| **01** | [**`practical-01-service-models/`**](practical-01-service-models/README.md) | **Cloud Service Models (IaaS vs PaaS vs SaaS)** | [📖 **Student Guide**](practical-01-service-models/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-01-service-models/EXPLAINER.pdf) | **Production Ready** |
| **14** | [**`practical-14-multicloud-terraform/`**](practical-14-multicloud-terraform/README.md) | **Multi-Cloud Infrastructure as Code (Terraform)** | [📖 **Student Guide**](practical-14-multicloud-terraform/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-14-multicloud-terraform/EXPLAINER.pdf) | **Production Ready** |
| **04** | [**`practical-04-k8s-orchestration/`**](practical-04-k8s-orchestration/README.md) | **Container Orchestration & Kubernetes Control Plane** | [📖 **Student Guide**](practical-04-k8s-orchestration/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-04-k8s-orchestration/EXPLAINER.pdf) | **Production Ready** |
| **11** | [**`practical-11-cloud-migration/`**](practical-11-cloud-migration/README.md) | **Cloud Data Migration & Cryptographic Parity** | [📖 **Student Guide**](practical-11-cloud-migration/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-11-cloud-migration/EXPLAINER.pdf) | **Production Ready** |
| **02** | [**`practical-02-vm-lifecycle/`**](practical-02-vm-lifecycle/README.md) | **Virtual Machine Deployment & Lifecycle Management** | [📖 **Student Guide**](practical-02-vm-lifecycle/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-02-vm-lifecycle/EXPLAINER.pdf) | **Production Ready** |
| **09** | [**`practical-09-openstack-private-cloud/`**](practical-09-openstack-private-cloud/README.md) | **Private Cloud Architecture with OpenStack** | [📖 **Student Guide**](practical-09-openstack-private-cloud/STUDENT_GUIDE.md) | [📄 **PDF Guide**](practical-09-openstack-private-cloud/EXPLAINER.pdf) | **Production Ready** |

---

## 👨‍🎓 How to Run Any Lab

Every demo in this collection runs with **zero configuration** and includes automated port conflict resolution, health checks, and one-command execution:

### 🌟 Option 1: Web Command Portal (Recommended — 1-Click Browser Hub)
Launch the unified browser-based mission control to view, launch, switch, and inspect all 15 cloud labs with a single click:

```bash
# Start the web portal (zero external dependencies, pure Python 3)
./portal.sh

# Open your browser:
# 👉 http://localhost:3000
```
- **One-Click Launching**: Launch or stop any of the 15 practicals directly from the web interface.
- **Automated Port 8080 Management**: Seamlessly switches containers with zero port binding errors.
- **In-Portal Split Workbench**: Test the live simulator side-by-side with the complete **Student Lab Guide**, interactive tasks, and viva interview questions.
- **Live Search & Filter**: Filter by category (Compute, Storage, Networking, Security, Scaling, Edge) or search by keyword (e.g. `autoscaling`, `cgroups`, `S3`, `KMS`, `MQTT`).

---

### Option 2: Terminal Interactive Master Launcher
If you prefer a terminal interface, run the interactive CLI menu:

```bash
# Run the interactive menu
./run.sh

# Or launch any specific practical directly:
./run.sh 4       # Launches Practical 04 (Kubernetes Orchestration)
./run.sh 10      # Launches Practical 10 (Cloud Auto-Scaling)
./run.sh status  # Shows active lab and container health
./run.sh stop    # Stops all active labs and frees port 8080
./run.sh web     # Launches the Web Command Portal
```

*Using `make`? You can also use `make web`, `make run`, `make p4`, `make p10`, `make status`, or `make stop`.*

---

### Option 3: Run Inside Any Practical Directory
Every practical contains a dedicated `start.sh` and `stop.sh` script:

```bash
# 1. Enter any practical directory
cd practical-04-k8s-orchestration

# 2. Launch the demo (auto-creates .env, resolves port conflicts, probes health)
./start.sh

# 3. Open your browser:
# 👉 http://localhost:8080

# 4. When finished, stop and release all resources:
./stop.sh
```

---

### Option C: Manual Docker Compose
If you prefer raw Docker commands:

```bash
cd practical-04-k8s-orchestration
cp .env.example .env
docker compose up --build -d
# Open http://localhost:8080
docker compose down -v
```

---

## ⚡ Featured Project: Practical 10 — Cloud Auto-Scaling Engine

The first completed project in this collection is **Practical 10**, an end-to-end, real-time Horizontal Container Auto-Scaling Engine with live Nginx load balancing:

```
cd practical-10-cloud-autoscaling
cp .env.example .env
docker compose up --build -d
```
Open **[http://localhost:8080](http://localhost:8080)** to interact with the live traffic controls, observe real-time scaling events, and inspect the balanced container pool.

Read the [Practical 10 Full Documentation](practical-10-cloud-autoscaling/README.md) for architecture deep-dives and testing instructions.

---

## 📜 Design Principles

1. **Zero External Billing Accounts:** All projects run 100% locally or inside zero-credential emulation harnesses.
2. **Deterministic & Lightweight:** Strict memory budgets ($\le 150$ MB RAM) ensure smooth execution on macOS, Linux, and Windows.
3. **Instant Visual Feedback:** Every lab replaces dry CLI logs with interactive dashboards, live metrics graphs, and real-time state visualizers.
4. **General & Open Source:** Free from proprietary campus or institutional dependencies, suitable for global developer portfolios and production reference architectures.
