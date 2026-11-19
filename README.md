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

| Lab # | Project Directory | Core Cloud Concept | Student Walkthrough | Status |
|:---:|:---|:---|:---:|:---:|
| **10** | [**`practical-10-cloud-autoscaling/`**](practical-10-cloud-autoscaling/README.md) | Horizontal Auto-Scaling & Load Balancing | [📖 **Student Guide**](practical-10-cloud-autoscaling/STUDENT_GUIDE.md) | **Production Ready** |
| **06** | [**`practical-06-object-storage-s3/`**](practical-06-object-storage-s3/README.md) | Object Storage, Presigned URLs & Expiring ACLs | [📖 **Student Guide**](practical-06-object-storage-s3/STUDENT_GUIDE.md) | **Production Ready** |
| **15** | [**`practical-15-edge-computing-mqtt/`**](practical-15-edge-computing-mqtt/README.md) | Edge Computing & IoT Telemetry Broker | [📖 **Student Guide**](practical-15-edge-computing-mqtt/STUDENT_GUIDE.md) | **Production Ready** |
| **07** | [**`practical-07-iam-access-control/`**](practical-07-iam-access-control/README.md) | Identity & Access Management (IAM / Least Privilege) | [📖 **Student Guide**](practical-07-iam-access-control/STUDENT_GUIDE.md) | **Production Ready** |
| **12** | [**`practical-12-serverless-lambda/`**](practical-12-serverless-lambda/README.md) | Serverless FaaS, Cold Starts & Micro-Billing | [📖 **Student Guide**](practical-12-serverless-lambda/STUDENT_GUIDE.md) | **Production Ready** |
| **03** | [**`practical-03-containerization-docker/`**](practical-03-containerization-docker/README.md) | Cgroups v2 Resource Quotas & OverlayFS CoW | [📖 **Student Guide**](practical-03-containerization-docker/STUDENT_GUIDE.md) | **Production Ready** |
| **13** | [**`practical-13-bigdata-analytics/`**](practical-13-bigdata-analytics/README.md) | Vectorized Columnar Analytics vs. MapReduce | [📖 **Student Guide**](practical-13-bigdata-analytics/STUDENT_GUIDE.md) | **Production Ready** |
| **05** | [**`practical-05-cloud-networking-vpc/`**](practical-05-cloud-networking-vpc/README.md) | Dual-Tier VPC, Hop-by-Hop Packet Tracer & SGs | [📖 **Student Guide**](practical-05-cloud-networking-vpc/STUDENT_GUIDE.md) | **Production Ready** |
| **08** | [**`practical-08-cloud-security/`**](practical-08-cloud-security/README.md) | **Cloud Security & Envelope Encryption (KMS)** | [📖 **Student Guide**](practical-08-cloud-security/STUDENT_GUIDE.md) | **Production Ready** |
| **01** | [**`practical-01-service-models/`**](practical-01-service-models/README.md) | **Cloud Service Models (IaaS vs PaaS vs SaaS)** | [📖 **Student Guide**](practical-01-service-models/STUDENT_GUIDE.md) | **Production Ready** |
| **14** | [**`practical-14-multicloud-terraform/`**](practical-14-multicloud-terraform/README.md) | **Multi-Cloud Infrastructure as Code (Terraform)** | [📖 **Student Guide**](practical-14-multicloud-terraform/STUDENT_GUIDE.md) | **Production Ready** |
| **04** | [**`practical-04-k8s-orchestration/`**](practical-04-k8s-orchestration/README.md) | **Container Orchestration & Kubernetes Control Plane** | [📖 **Student Guide**](practical-04-k8s-orchestration/STUDENT_GUIDE.md) | **Production Ready** |
| **11** | [**`practical-11-cloud-migration/`**](practical-11-cloud-migration/README.md) | **Cloud Data Migration & Cryptographic Parity** | [📖 **Student Guide**](practical-11-cloud-migration/STUDENT_GUIDE.md) | **Production Ready** |
| **02** | [**`practical-02-vm-lifecycle/`**](practical-02-vm-lifecycle/README.md) | **Virtual Machine Deployment & Lifecycle Management** | [📖 **Student Guide**](practical-02-vm-lifecycle/STUDENT_GUIDE.md) | **Production Ready** |
| **09** | `practical-09-openstack-private-cloud/` | Private Cloud Multi-Tenant Architecture | *Upcoming* | *Upcoming* |

---

## 👨‍🎓 How to Run Any Lab (3 Simple Steps)

Every demo in this collection is designed to run in under 30 seconds with **zero configuration**:

```bash
# 1. Choose any practical directory
cd practical-10-cloud-autoscaling

# 2. Copy the environment config and launch with Docker Compose
cp .env.example .env
docker compose up --build -d

# 3. Open your browser to interact with the live dashboard
open http://localhost:8080
```

To stop the lab and free all host resources:
```bash
docker compose down
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
