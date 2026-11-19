# Practical 11: Enterprise Cloud Data Migration & Cryptographic Parity

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS S3](https://img.shields.io/badge/AWS-S3_Object_Storage-FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/s3/)
[![Security](https://img.shields.io/badge/Integrity-SHA--256_Cryptographic_Audit-10B981.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 35 MB RAM) **Enterprise Cloud Data Migration Simulator** featuring automated ETL schema transformation (relational SQLite to streaming JSONL), dedicated high-speed network transmission (AWS Direct Connect emulation), cloud object storage ingestion with compliance metadata tagging, and automated **SHA-256 Cryptographic Checksum Parity & Bitrot Detection**.

> **👨‍🎓 For Students & Educators:** Read the [**`STUDENT_GUIDE.md`**](STUDENT_GUIDE.md) for a beginner-friendly explanation of the "6 Rs of Cloud Migration", step-by-step interactive lab exercises, and viva/interview prep questions.

---

## 🏗️ Core Architectural Concepts

```
┌─────────────────────────────────┐           ┌─────────────────────────────────┐
│  On-Premises Legacy Datacenter  │           │      AWS Cloud Object Storage   │
│                                 │           │                                 │
│  ┌───────────────────────────┐  │           │  ┌───────────────────────────┐  │
│  │ legacy_erp.db (SQLite)    │  │           │  │ s3://migrated-enterprise- │  │
│  │ - customers (Table)       │  │           │  │      cloud/               │  │
│  │ - transactions (Table)    │  │           │  │                           │  │
│  └─────────────┬─────────────┘  │           │  │ - database_exports/       │  │
│                │ ETL / JSONL    │           │  │   customers.jsonl         │  │
│                ▼                │           │  │   transactions.jsonl      │  │
│  ┌───────────────────────────┐  │  Direct   │  │ - documents/              │  │
│  │ Source SHA-256 Generator  │ ─┼───────────┼─►│   q3_audit.csv            │  │
│  └───────────────────────────┘  │  Connect  │  │   compliance.txt          │  │
│                                 │  (1 Gbps) │  └─────────────┬─────────────┘  │
└─────────────────────────────────┘           └────────────────┼────────────────┘
                                                               │
                                                               ▼
                                              ┌─────────────────────────────────┐
                                              │ Post-Migration Audit Ledger     │
                                              │ SHA-256 Source == S3 Target?    │
                                              │ [100% Parity: ZERO BITROT]      │
                                              └─────────────────────────────────┘
```

### 1. Database Schema Transformation (ETL)
- Relational tables with foreign key constraints are extracted and converted into cloud-native newline-delimited JSON (**JSONL**) payloads suitable for distributed analytical query engines (AWS Athena, Snowflake, BigQuery).

### 2. High-Speed Transport Emulation
- Compares **AWS Direct Connect (1 Gbps dedicated fiber)** against **Public Internet VPN (100 Mbps shared)** with transfer latency modeling.

### 3. Cryptographic Parity & Bitrot Detection
- Generates 256-bit cryptographic digest on the source assets before transmission.
- Compares against cloud storage hashes upon arrival.
- Includes a built-in **Tamper / Bitrot Simulator** allowing students to see how a single modified byte causes immediate audit failure.

---

## 🚀 Quickstart & Execution

### 1. Launch the Stack
```bash
cd practical-11-cloud-migration
cp .env.example .env
docker compose up --build -d
```

### 2. Verify Endpoints
```bash
# Check service health
curl -s http://localhost:8080/health | python3 -m json.tool

# Query on-premises assets and migration state
curl -s http://localhost:8080/api/status | python3 -m json.tool

# Trigger cloud migration
curl -s -X POST http://localhost:8080/api/migrate | python3 -m json.tool
```

### 3. Open Web Dashboard
Navigate to `http://localhost:8080` in your web browser.

---

## 🛑 Clean Teardown
```bash
docker compose down
```
Frees host port `8080` and leaves zero lingering processes.
