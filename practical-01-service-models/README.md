# Practical 01: Cloud Service Models (IaaS, PaaS, SaaS) & Shared Responsibility

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Standard](https://img.shields.io/badge/Standard-NIST_SP_800--145-0284C7.svg)](https://csrc.nist.gov/publications/detail/sp/800-145/final)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 35 MB RAM) **Cloud Service Models & Shared Responsibility Model Simulator** mapping the 9-layer cloud architecture across **Infrastructure as a Service (IaaS)**, **Platform as a Service (PaaS)**, and **Software as a Service (SaaS)** with interactive deployment workbenches.

> **👨‍🎓 For Students & Educators:** Read the [**`STUDENT_GUIDE.md`**](STUDENT_GUIDE.md) for a beginner-friendly walkthrough, the "Pizza as a Service" analogy, interactive lab tasks, and viva/interview prep.

---

## 🏗️ Core Cloud Architectural Concepts

### 1. The 9-Layer NIST SP 800-145 Hierarchy
1. **Facilities**: Data center physical perimeter, cooling, electricity.
2. **Hardware**: Physical rack servers, CPU silicon, RAM, network switches.
3. **Virtualization**: Type-1/Type-2 Hypervisors (KVM, Nitro, Xen, ESXi).
4. **Operating System**: Guest Linux/Windows kernel, security updates.
5. **Middleware**: Web servers (Nginx, Gunicorn), database drivers.
6. **Runtime**: Execution environments (Node.js, Python, Java, Go).
7. **Data**: Persistent records, customer databases, encryption.
8. **Applications**: Custom business logic, API endpoints, microservices.
9. **Identity & Access Management (IAM)**: User accounts, passwords, MFA.

### 2. Service Model Responsibilities Breakdown
| Cloud Model | Cloud Provider Responsibility | Customer Responsibility | Key Examples |
|:---|:---|:---|:---|
| **On-Premises** | *None* | **All 9 Layers** | Private Datacenter |
| **IaaS** | Facilities, Hardware, Virtualization | OS, Middleware, Runtime, Data, App, IAM | AWS EC2, GCP Compute Engine, Azure VMs |
| **PaaS** | Facilities, Hardware, Virtualization, OS, Middleware, Runtime | Data, Application Code, IAM | AWS Elastic Beanstalk, Heroku, Vercel |
| **SaaS** | Facilities through Application Code (**8 Layers**) | User Access & Tenant Configurations | Google Workspace, Microsoft 365, Salesforce |

---

## 🚀 Quickstart & Sequential Execution

### 1. Launch the Simulator
```bash
cd practical-01-service-models
cp .env.example .env
docker compose up --build -d
```

### 2. Verify Endpoints
```bash
# Verify health probe
curl -s http://localhost:8080/health | python3 -m json.tool

# Query NIST 9-layer responsibility matrix
curl -s http://localhost:8080/api/overview | python3 -m json.tool

# Query active IaaS VMs, PaaS apps, and SaaS tenants
curl -s http://localhost:8080/api/state | python3 -m json.tool
```

### 3. Interactive Web Dashboard
Open **[http://localhost:8080](http://localhost:8080)** in your browser to:
- Dynamically toggle the 9-layer stack between On-Prem, IaaS, PaaS, and SaaS.
- Provision a virtual machine in the **IaaS Workbench** and apply a simulated OS security patch.
- Deploy an application via Git in the **PaaS Workbench** with zero OS management.
- Provision a multi-tenant enterprise workspace in the **SaaS Workbench**.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|:---|:---:|:---|
| `/` | `GET` | Microservice metadata and NIST SP 800-145 reference info |
| `/health` | `GET` | Microservice health status |
| `/api/overview` | `GET` | 9-layer stack and model definitions |
| `/api/state` | `GET` | Active IaaS instances, PaaS deployments, and SaaS tenants |
| `/api/iaas/provision` | `POST` | Provision a new virtual machine (`{"os": "Ubuntu 24.04", "vcpu": 2, "ram_gb": 4}`) |
| `/api/iaas/patch` | `POST` | Apply OS security patch to an IaaS VM |
| `/api/iaas/terminate/<id>`| `DELETE` | Terminate an IaaS virtual machine |
| `/api/paas/deploy` | `POST` | Deploy an application via Git push buildpack |
| `/api/paas/scale` | `POST` | Adjust PaaS replica count |
| `/api/saas/tenant` | `POST` | Provision an isolated multi-tenant SaaS workspace |
| `/api/saas/tenant/<id>` | `DELETE` | Decommission a SaaS workspace partition |

---

## 🧹 Teardown & RAM Reclamation
```bash
docker compose down
```
Instantly stops containers and reclaims all memory.
