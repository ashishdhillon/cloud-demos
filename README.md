# Cloud Systems Engineering Labs & Interactive Demos

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Cloud_Native-orange.svg)]()
[![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen.svg)]()

A curated collection of **lightweight, production-grade, interactive cloud systems engineering projects and real-time simulators**.

Designed for engineers, students, and educators to experience core hyperscale cloud concepts (auto-scaling, object storage, IAM engines, serverless cold starts, and IoT edge brokers) running **100% locally on personal hardware with zero paid cloud accounts or subscriptions required**.

---

## 🧭 Project Roadmap & Curriculum Index

Each project is self-contained in its own directory, includes an interactive web dashboard or visual simulator, and adheres to strict resource-efficiency constraints (< 150 MB RAM per practical).

| Lab # | Project Directory | Core Cloud Concept | Primary Technology | Status |
|:---:|:---|:---|:---|:---:|
| **10** | [**`practical-10-cloud-autoscaling/`**](practical-10-cloud-autoscaling/README.md) | **Horizontal Auto-Scaling & Load Balancing** | Docker, Nginx, Python Autoscaler, SSE | **Active / Production Ready** |
| **06** | `practical-06-object-storage-s3/` | Object Storage, Presigned URLs & ACLs | S3 API Simulator, Drag & Drop UI | *Upcoming* |
| **15** | `practical-15-edge-computing-mqtt/` | Edge Computing & IoT Telemetry Broker | Eclipse Mosquitto, WebSockets, Live Gauges | *Upcoming* |
| **07** | `practical-07-iam-access-control/` | Identity & Access Management (RBAC/Least Privilege) | IAM Policy Engine, Interactive Evaluator | *Upcoming* |
| **12** | `practical-12-serverless-lambda/` | Serverless FaaS, Cold Starts & Concurrency | Ephemeral Container Worker, Micro-Billing | *Upcoming* |
| **03** | `practical-03-containerization-docker/` | Container Layering & Cgroup Resource Throttling | Docker Engine, Cgroups v2 Inspector | *Upcoming* |
| **13** | `practical-13-bigdata-analytics/` | Columnar vs. Row Big Data Querying | DuckDB WebAssembly, S3 Parquet Engine | *Upcoming* |
| **05** | `practical-05-cloud-networking-vpc/` | Virtual Private Clouds, Subnets & NAT Routing | Packet Animation, Security Group Matrix | *Upcoming* |
| **08** | `practical-08-cloud-security/` | Cloud Security & Envelope Encryption (KMS) | OpenSSL, DEK/KEK Key Lifecycle Visualizer | *Upcoming* |
| **01** | `practical-01-service-models/` | Cloud Service Models (IaaS vs PaaS vs SaaS) | Shared Responsibility Dynamic Matrix | *Upcoming* |
| **14** | `practical-14-multicloud-terraform/` | Multi-Cloud Infrastructure as Code (IaC) | Declarative State & Drift Reconciliation | *Upcoming* |
| **04** | `practical-04-k8s-orchestration/` | Container Orchestration & Pod Self-Healing | Lightweight Kubelet Pod Reconciler | *Upcoming* |
| **11** | `practical-11-cloud-migration/` | Cloud Data Migration & Checksum Verification | SQLite to Cloud Storage Streamer | *Upcoming* |
| **02** | `practical-02-vm-lifecycle/` | Virtual Machine Provisioning & Teardown | Lightweight Hypervisor Lifecycle Controller | *Upcoming* |
| **09** | `practical-09-openstack-private-cloud/` | Private Cloud Multi-Tenant Architecture | Mock Keystone v3 & Nova Compute API | *Upcoming* |

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
