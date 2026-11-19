# Practical 09: Deploying a Private Cloud with OpenStack (Keystone & Nova)

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![OpenStack](https://img.shields.io/badge/OpenStack-2024.1_Yoga-DA1A32.svg?logo=openstack&logoColor=white)](https://www.openstack.org/)
[![Cloud Native](https://img.shields.io/badge/Architecture-Private_Cloud-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 35 MB RAM) **OpenStack Private Cloud Architecture & Multi-Tenant Management Simulator** modeling the core OpenStack services: **Keystone v3 (Identity & Dynamic Service Catalog)**, **Nova v2.1 (Compute Orchestration & Flavors)**, **Glance (Image Registry)**, **Neutron (SDN & Floating IP Ingress)**, and the **Horizon Web Dashboard**.

> **👨‍🎓 For Students & Educators:** Read the [**`STUDENT_GUIDE.md`**](STUDENT_GUIDE.md) for a beginner-friendly explanation of why enterprises build private clouds, step-by-step interactive lab exercises, and viva/interview prep questions.

---

## 🏗️ Core Architectural Concepts

```
┌────────────────────────────────────────────────────────────────────────┐
│               Horizon Multi-Tenant Web Management Console              │
│                [Project: Production-Core vs Dev-Staging]               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│  Keystone Identity v3  │  │  Nova Compute v2.1     │  │  Glance Image Registry │
│  - X-Subject-Token     │  │  - Flavors (m1.tiny-lg)│  │  - Ubuntu 24.04 QCOW2  │
│  - Tenant Quota Engine │  │  - Hypervisor Dispatch │  │  - CirrOS Minimal      │
│  - Service Catalog     │  │  - ACPI State Machine  │  │  - Rocky Linux 9       │
└────────────────────────┘  └───────────┬────────────┘  └────────────────────────┘
                                        │
    ┌───────────────────────────────────┴───────────────────────────┐
    ▼                                                               ▼
┌────────────────────────────────────────┐  ┌────────────────────────────────────┐
│  Neutron Software-Defined Network v2.0 │  │  Cinder Block Storage v3           │
│  - VXLAN Tenant Overlay Subnets        │  │  - Persistent Virtual Volumes      │
│  - Floating Public IP Ingress Pool     │  │  - Dynamic Block Attachment        │
└────────────────────────────────────────┘  └────────────────────────────────────┘
```

### 1. Multi-Tenant Project Isolation
- Isolates compute resources, subnets, and quota limits between projects (`Production-Core` vs `Dev-Staging`).

### 2. Keystone v3 Authentication & Service Catalog
- Issues scoped cryptographic tokens (`X-Subject-Token`) and dynamically advertises active regional endpoints for Nova, Glance, Neutron, and Cinder.

### 3. Nova Hardware Flavors & Glance Images
- Enforces strict hardware tiers (`m1.tiny`, `m1.small`, `m1.medium`, `m1.large`) across physical hypervisor compute worker nodes.

### 4. Neutron SDN & Floating IPs
- Implements 1-to-1 NAT routing, dynamically associating public external IPs (`203.0.113.x`) with internal private instance interfaces.

---

## 🚀 Quickstart & Execution

### 1. Launch the Stack
```bash
cd practical-09-openstack-private-cloud
cp .env.example .env
docker compose up --build -d
```

### 2. Verify Endpoints
```bash
# Check service health
curl -s http://localhost:8080/health | python3 -m json.tool

# Authenticate to Keystone v3 and obtain token
curl -s -X POST http://localhost:8080/v3/auth/tokens | python3 -m json.tool

# Query Nova compute flavors
curl -s http://localhost:8080/v2.1/flavors | python3 -m json.tool
```

### 3. Open Web Dashboard
Navigate to `http://localhost:8080` in your web browser.

---

## 🛑 Clean Teardown
```bash
docker compose down
```
Frees host port `8080` and leaves zero lingering processes.
