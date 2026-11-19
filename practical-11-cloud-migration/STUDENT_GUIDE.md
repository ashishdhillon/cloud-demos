# 🎓 Student Lab Guide: Practical 11 — Enterprise Cloud Data Migration & Cryptographic Parity

---

## 📌 1. What is this practical about? (The Real-World Problem)

When enterprises decide to shut down physical data centers and move to hyperscale cloud providers like AWS, Google Cloud, or Azure, their most critical asset is **data**.

Migrating petabytes of financial transactions, customer records, and compliance archives introduces severe engineering risks:
1. **Packet Loss & Silent Bitrot:** Network switches and fiber lines can drop packets or flip bits during transit, silently corrupting databases.
2. **Format Incompatibility:** Legacy relational databases (like on-premises Oracle, SQL Server, or SQLite) cannot be queried cheaply at cloud scale without transformation into cloud-native streaming formats like **JSONL** or **Apache Parquet**.
3. **Regulatory Non-Compliance:** Regulations like SOC2, HIPAA, and GDPR require cryptographic proof that zero records were altered, lost, or tampered with during the migration journey.

### The Cloud Solution: **Automated ETL Pipeline & Cryptographic Checksum Parity**
This practical demonstrates the industry-standard migration pattern:
- **Extract & Transform (ETL):** On-premises relational tables are extracted and structured into streaming JSONL chunks.
- **Dedicated Transfer:** Assets are transmitted across high-speed dedicated lines (**AWS Direct Connect 1 Gbps**) directly into Cloud Object Storage (**AWS S3**).
- **Compliance Metadata Tagging:** Every cloud object is tagged with compliance classification (`SOC2-TypeII`, `Retention: 7-Years`).
- **Post-Migration Parity Audit:** The pipeline calculates SHA-256 cryptographic hashes on the source files and verifies them against the cloud object storage checksums. **100% hash parity proves zero data loss.**

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- Zero AWS accounts or paid cloud subscriptions required (includes a self-contained high-fidelity cloud storage and ETL migration simulator).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-11-cloud-migration
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Inspect On-Premises Legacy Datasets
1. Observe the left panel: **🏢 On-Premises Legacy Data Center**.
2. Notice the 4 enterprise assets extracted from the on-premise system:
   - `customers.jsonl`: 8 enterprise accounts extracted from SQLite.
   - `transactions.jsonl`: 300 financial transaction records.
   - `q3_financial_audit.csv`: Uncompressed quarterly budget audit.
   - `compliance_audit.txt`: SOC2/ISO 27001 regulatory charter.
3. Note the **Source SHA-256 Checksums** pre-calculated before transmission.

### 🔹 Task 2: Execute Cloud Migration Pipeline via AWS Direct Connect
1. In the center panel, ensure **"AWS Direct Connect (1 Gbps Dedicated Fiber)"** is selected.
2. Click **`🚀 Start Cloud Migration`**.
3. Watch the pipeline in real-time:
   - The animated progress bar advances from 0% to 100%.
   - In-transit assets stream across the network pipe into **`s3://migrated-enterprise-cloud`**.
   - Notice the right panel populate with active S3 objects, MD5 ETags, and compliance tags (`Classification=Confidential`, `Standard=SOC2-TypeII`).

### 🔹 Task 3: Post-Migration Cryptographic Audit (Zero Loss Verification)
1. Scroll down to the **🛡️ Post-Migration Cryptographic Audit Ledger**.
2. Compare the columns:
   - **Source SHA-256 Checksum** vs **Cloud S3 SHA-256 Checksum**.
   - Look at the **Parity Result**: Every file displays a bright green **`PASS (100% Cryptographic Parity)`**!
   - This cryptographic certificate proves to auditors that all 24.8 KB of data arrived in the cloud intact with **0% packet loss**.

### 🔹 Task 4: In-Flight Bitrot & Packet Tamper Test
1. In the center panel, click **`⚡ Test Bitrot (Tamper)`**.
   - This simulates a damaged network router or an in-transit attacker modifying 1 bit in `transactions.jsonl`.
2. Watch the pipeline complete and execute the automated audit.
3. Look at the **Audit Ledger**:
   - `transactions.jsonl` is immediately highlighted in red with:
     `FAIL: CHECKSUM MISMATCH (BITROT / DATA TAMPERING)`.
   - The top header flags: **`⚠ Pipeline: Checksum Mismatch Detected`**.
   - This proves why cloud architects never rely solely on file size or HTTP 200 responses—cryptographic hashes are mandatory!
4. Click **`🔄 Reset Datasets`** to restore the baseline.

---

## 💻 5. Terminal CLI Verification

You can interact directly with the Migration Pipeline API using `curl` from your terminal:

```bash
# 1. Check service health
curl -s http://localhost:8080/health | jq .

# 2. View on-premises assets and pipeline state
curl -s http://localhost:8080/api/status | jq .

# 3. Trigger cloud migration over Direct Connect
curl -s -X POST http://localhost:8080/api/migrate \
  -H "Content-Type: application/json" \
  -d '{"network_mode": "direct_connect_1gbps", "tamper": false}' | jq .

# 4. Trigger test with in-flight bitrot/tampering
curl -s -X POST http://localhost:8080/api/migrate \
  -H "Content-Type: application/json" \
  -d '{"network_mode": "direct_connect_1gbps", "tamper": true}' | jq .

# 5. Run cryptographic audit verification
curl -s -X POST http://localhost:8080/api/verify | jq .

# 6. Reset environment to on-prem baseline
curl -s -X POST http://localhost:8080/api/reset | jq .
```

---

## 🎯 6. Viva & Job Interview Questions & Answers

### Q1: What are the "6 Rs" of Cloud Migration?
> **Answer:**
> Coined by Gartner and AWS, the 6 migration strategies are:
> 1. **Rehost ("Lift and Shift"):** Move applications as-is without code changes (e.g. copying VMs to EC2).
> 2. **Replatform ("Lift, Tinker, and Shift"):** Make minor optimizations without changing core code (e.g. moving self-hosted MySQL to Amazon RDS).
> 3. **Repurchase ("Drop and Shop"):** Switch to a cloud-native SaaS product (e.g. migrating on-prem CRM to Salesforce).
> 4. **Refactor / Re-architect:** Rewrite applications to exploit cloud-native microservices, containers, and serverless.
> 5. **Retain:** Keep legacy applications on-premises because they are too risky to move or near end-of-life.
> 6. **Retire:** Decommission applications that are no longer needed.

### Q2: Why are relational database rows transformed into JSONL or Parquet when migrating to S3?
> **Answer:**
> Relational databases store records in proprietary binary disk formats (like SQLite B-trees or Oracle tablespaces) that cannot be directly queried across distributed cloud nodes. By exporting rows to newline-delimited JSON (**JSONL**) or columnar **Apache Parquet**, cloud analytics engines (like AWS Athena, BigQuery, or Snowflake) can query the files directly in object storage with zero database server overhead.

### Q3: What is "Bitrot" and how do checksums prevent it?
> **Answer:**
> Bitrot refers to silent data corruption caused by electrical noise, cosmic rays, failing disk sectors, or transmission errors where a `0` flips to a `1`. Because file size often remains identical, ordinary file checks fail to detect it. By computing a cryptographic hash (like SHA-256) before transmission and comparing it to the received hash, even a 1-bit alteration completely changes the hash string (the *avalanche effect*), instantly flagging corruption.

### Q4: When should an enterprise use AWS Direct Connect vs AWS Snowball?
> **Answer:**
> - **AWS Direct Connect:** A dedicated physical fiber connection from an on-prem data center to AWS (1 Gbps to 100 Gbps). Best for continuous hybrid workloads or regular daily replication.
> - **AWS Snowball:** A ruggedized physical appliance shipped by courier to the customer's data center, loaded with up to 80 TB of data, and mailed back to AWS. Best for initial petabyte-scale migrations where transmitting over the internet would take months or years.

---

## 🛑 7. Clean Teardown
When you are done with the lab, run:
```bash
docker compose down
```
This frees host port `8080` and leaves zero lingering processes.
