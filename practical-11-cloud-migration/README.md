# Practical 11: Enterprise Cloud Data Migration & Cryptographic Parity

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS S3](https://img.shields.io/badge/AWS-S3_Object_Storage-FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/s3/)
[![Security](https://img.shields.io/badge/Integrity-SHA--256_Cryptographic_Audit-10B981.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 45 MiB RAM) **Enterprise Cloud Data Migration Simulator** featuring automated ETL schema transformation (relational SQLite to streaming JSONL), multi-mode network transport (AWS Direct Connect 1 Gbps, 100 Mbps VPN, and AWS Snowball 80 TB), Gartner 6-Rs Migration Strategy Matrix, automated **SHA-256 Cryptographic Checksum Parity & Avalanche Bitrot Dissector**, 1-click **Self-Healing Block Retransmission**, **Zero-Downtime Route 53 DNS Cutover & Safety Rollback**, and a **3-Year Cloud TCO & Carbon ROI Calculator**.

> **👨‍🎓 For Students & Educators:** Read the [**`STUDENT_GUIDE.md`**](STUDENT_GUIDE.md) for a comprehensive explanation of the Gartner 6-Rs Migration Framework, step-by-step interactive lab exercises, and viva/interview defense questions.

---

## 🏗️ Core Architectural Concepts

```
┌──────────────────────────────────────────────┐              ┌──────────────────────────────────────────────┐
│       On-Premises Legacy Datacenter          │              │           AWS Cloud Target Lakehouse         │
│                                              │              │                                              │
│  ┌────────────────────────────────────────┐  │              │  ┌────────────────────────────────────────┐  │
│  │ legacy_erp.db (SQLite)                 │  │              │  │ s3://migrated-enterprise-cloud/        │  │
│  │ - customers (Table)                    │  │              │  │ - database_exports/                    │  │
│  │ - transactions (Table)                 │  │              │  │   customers.jsonl                      │  │
│  └───────────────────┬────────────────────┘  │  Multi-Mode  │  │   transactions.jsonl                   │  │
│                      │ ETL Stream            │  Transport   │  │ - documents/                           │  │
│                      ▼                       ├─────────────►│  │   q3_financial_audit.csv               │  │
│  ┌────────────────────────────────────────┐  │  1. Direct   │  │   compliance_audit.txt                 │  │
│  │ Source SHA-256 Hash Digest Engine      │  │     Connect  │  └───────────────────┬────────────────────┘  │
│  └────────────────────────────────────────┘  │  2. Snowball │                      │                       │
│                                              │  3. VPN      │                      ▼                       │
└──────────────────────┬───────────────────────┘              └──────────────────────┼───────────────────────┘
                       │                                                             │
                       ▼                                                             ▼
     ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
     │                     Post-Migration Cryptographic Audit Ledger & Avalanche Dissector             │
     │                      Source SHA-256 Checksum == Cloud S3 SHA-256 Checksum                       │
     │                           [100% PARITY VERIFIED · ZERO DATA LOSS]                               │
     └─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Gartner 6-Rs Migration Framework Decision Matrix
- Evaluates 6 distinct enterprise workloads with complexity ratings (1-10), velocity schedules, and AWS target architectures:
  1. **Rehost (Lift & Shift):** Unstructured NAS file shares -> Amazon S3 Glacier.
  2. **Replatform (Lift, Tinker & Shift):** Oracle 12c DB -> Amazon Aurora PostgreSQL.
  3. **Refactor (Re-architect):** Monolithic Java Billing -> Containerized Microservices on AWS ECS/Fargate.
  4. **Repurchase (Drop & Shop):** Self-hosted Bugzilla -> Jira Cloud SaaS.
  5. **Retain (Keep On-Premises):** Core Banking Mainframe -> Tier-IV Datacenter + Direct Connect Hybrid.
  6. **Retire (Decommission):** Deprecated 2018 Intranet Portal -> Decommission and archive.

### 2. Multi-Mode Enterprise Transport Simulator
- **AWS Direct Connect (1 Gbps Dedicated Fiber):** Private 802.1Q VLAN, ultra-low jitter, 99.99% SLA.
- **Public Internet VPN (100 Mbps Shared):** IPsec encapsulation over public transit.
- **AWS Snowball Edge 80 TB (Offline Physical Appliance):** Ruggedized encrypted hardware appliance shipped by courier.

### 3. Bit-Level Cryptographic Parity & Avalanche Effect Dissector
- Demonstrates how a 1-bit packet modification during transit triggers the cryptographic **Avalanche Effect** (flipping > 50% of the 256 hash bits).
- Features **1-Click Self-Healing Block Retransmission** mimicking AWS DataSync block repair.

### 4. Zero-Downtime Route 53 DNS Cutover & Safety Rollback
- Simulates in-flight Change-Data-Capture (CDC) buffer flushing, Route 53 TTL switchover from On-Premises IP (`192.168.1.50`) to Cloud ALB (`cloud-alb.aws.internal`), and instantaneous safety rollback.

### 5. 3-Year Total Cost of Ownership (TCO) & Carbon ROI Calculator
- Compares on-premises server purchase, rack lease, cooling (PUE 1.8), and DBA maintenance against hyperscale AWS cloud infrastructure, computing dollar savings and metric tons of CO2e avoided.

---

## 🚀 Quickstart & Execution

### 1. Launch the Stack
```bash
./start.sh
# OR manually:
docker compose up --build -d
```

### 2. Open Web Dashboard
Navigate to `http://localhost:8080` in your web browser.

### 3. Verify Endpoints via Terminal
```bash
# Service Health
curl -s http://localhost:8080/health | python3 -m json.tool

# Query migration state
curl -s http://localhost:8080/api/status | python3 -m json.tool

# Query Gartner 6-Rs Strategy Matrix
curl -s http://localhost:8080/api/assessment | python3 -m json.tool

# Calculate 3-Year Cloud TCO
curl -s "http://localhost:8080/api/tco?data_size_tb=15&servers_count=25" | python3 -m json.tool
```

---

## 🛑 Clean Teardown
```bash
./stop.sh
# OR:
docker compose down
```
Frees host port `8080` and leaves zero lingering background processes.
