# 🎓 Student Lab Guide: Practical 11 — Enterprise Cloud Data Migration & Cryptographic Parity

---

## 📌 1. What is this practical about? (The Real-World Problem)

When enterprises shut down physical data centers and move to hyperscale cloud platforms (AWS, Google Cloud, Azure), data integrity and strategy planning are paramount.

Migrating petabytes of financial transactions, customer records, and compliance archives introduces severe engineering risks:
1. **Silent Bitrot & Network Tampering:** Packets can suffer bit-flips during transit across switches and public fiber, silently corrupting balances and audit trails.
2. **Schema Incompatibility:** Legacy relational databases (e.g., Oracle, SQL Server, SQLite) cannot be queried cost-effectively across cloud lakehouses without schema transformation into streaming **JSONL** or **Apache Parquet**.
3. **The Migration Strategy Dilemma (Gartner's 6-Rs):** Not every system should be moved the same way. Moving an unmaintained legacy portal to expensive cloud VMs wastes money, while rewriting a stable mainframe in one year introduces catastrophic risk.
4. **Downtime During Cutover:** How do you switch thousands of daily users from an on-prem server to the cloud without dropping a single active customer checkout?

### The Cloud Solutions Demonstrated in this Lab:
- **Gartner 6-Rs Framework:** Strategic workload classification (Rehost, Replatform, Refactor, Repurchase, Retain, Retire).
- **Automated Schema Transformation (ETL):** Relational tables extracted into streaming newline-delimited JSON (JSONL).
- **Multi-Mode Network Transport:** Dedicated fiber (AWS Direct Connect), shared IPsec VPN, and physical encrypted appliances (AWS Snowball Edge 80 TB).
- **Cryptographic Parity & Bitrot Detection:** SHA-256 hash digests computed at source and validated against destination S3 object checksums (**100% Parity = Zero Loss**).
- **Avalanche Effect Dissector & 1-Click Auto-Healing:** Visualizing how a 1-bit tamper flips >50% of the SHA-256 bits, and how chunk-level retransmissions repair pipelines without restarting.
- **Zero-Downtime Route 53 Cutover:** Change-Data-Capture (CDC) buffer flushing, DNS CNAME switchover, and instant safety rollback.

---

## 🛠️ 2. Step-by-Step Interactive Lab Exercises

### 🔹 Task 1: Evaluate Workloads in the 6-Rs Strategy Matrix
1. Look at the top section: **🧭 Gartner 6-Rs Enterprise Cloud Migration Strategy Matrix**.
2. Click through each of the 6 enterprise workload cards:
   - **Legacy Oracle ERP:** Replatform (Aurora PostgreSQL via AWS DMS).
   - **Monolithic Java Billing:** Refactor (Microservices on ECS/Fargate).
   - **Corporate NAS Shares (120 TB):** Rehost (Lift & Shift to Amazon S3 / Glacier).
   - **Internal Bugzilla Server:** Repurchase (Jira Cloud SaaS).
   - **Core Banking Mainframe:** Retain (Keep on-prem; Direct Connect hybrid link).
   - **Deprecated Marketing Portal:** Retire (Decommission & save $1,400/mo).
3. Observe how complexity ratings (1-10), migration velocity (weeks), and target architectures change.

### 🔹 Task 2: Execute Multi-Mode Cloud Migration
1. In the center panel, select your transport mode:
   - **AWS Direct Connect (1 Gbps Dedicated Fiber)**: Ultra-fast private line.
   - **Public Internet VPN (100 Mbps Shared)**: Slower public routing with latency.
   - **AWS Snowball Edge 80 TB (Offline Physical Appliance)**: Offline courier logistics simulation.
2. Click **🚀 Start Cloud Migration**.
3. Watch the real-time progress bar stream all 4 assets (`customers.jsonl`, `transactions.jsonl`, `q3_financial_audit.csv`, `compliance_audit.txt`).
4. Notice the right panel populate with live `s3://migrated-enterprise-cloud` objects, storage classes, and compliance metadata tags.

### 🔹 Task 3: Post-Migration Cryptographic Audit
1. Inspect the **🛡️ Post-Migration Cryptographic Audit Ledger**.
2. Compare the **Source SHA-256 Fingerprint** column with the **Target Cloud S3 SHA-256** column.
3. Verify that all 4 rows display **`PASS (100% Cryptographic Parity)`**.

### 🔹 Task 4: Inject Bitrot (Network Tamper Test) & Auto-Heal
1. Click **⚡ Test Bitrot (Tamper)**.
2. The pipeline simulates a single flipped byte in the transaction payload during transit.
3. Observe the audit ledger immediately flag **`FAIL: CHECKSUM MISMATCH (BITROT / DATA TAMPERING)`**.
4. Scroll down to inspect the **⚠️ Cryptographic Parity Dissector & Bitrot Inspector**:
   - Notice the exact corrupted snippet (`"amount": 99999 + 2450.00`).
   - Notice the **Avalanche Effect**: a single altered character flipped **over 50% of the 256 hash bits**!
5. Click **🛡️ Auto-Heal & Retransmit Block**.
6. The engine retransmits the clean chunk, recalculates the target checksum, and restores **100% Cryptographic Parity**.

### 🔹 Task 5: Zero-Downtime DNS Cutover & Safety Rollback
1. With migration verified at 100% parity, look at the **Zero-Downtime Cutover Simulator**.
2. Click **🚀 Execute DNS Cutover**.
3. Observe the 3-step transition:
   - Step 1: Flushes Change-Data-Capture (CDC) delta buffer (42 transactions).
   - Step 2: Switches Route 53 DNS from On-Prem A-record (`192.168.1.50`) to Cloud CNAME (`cloud-alb.aws.internal`).
   - Step 3: Production is 100% Live in AWS Cloud.
4. Click **⏪ Emergency Safety Rollback** to observe how enterprise SREs execute an instantaneous safety failover back to on-prem if alarms trigger.

### 🔹 Task 6: 3-Year Cloud TCO & Carbon ROI Calculator
1. In the bottom section, adjust the **Data Volume (TB)** and **Decommissioned Servers** sliders.
2. Compare the 3-year costs:
   - On-Premises: Hardware amortization, rack real-estate, PUE 1.8 power, sysadmin ops.
   - AWS Cloud: S3 Intelligent-Tiering, Aurora Serverless, Direct Connect, CloudOps automation.
3. Review estimated dollar savings (~65%) and carbon footprint reduction (~76% CO2e avoided).

---

## 🎯 5. Viva & Technical Interview Questions

**Q1: What are Gartner's 6-Rs of Cloud Migration?**
> *Answer:* Rehost (Lift & Shift), Replatform (Lift, Tinker & Shift), Refactor (Re-architect for Cloud Native), Repurchase (Drop & Shop to SaaS), Retain (Keep On-Prem), and Retire (Decommission).

**Q2: Why is SHA-256 cryptographic parity preferred over simple file size comparisons?**
> *Answer:* Two files can have identical byte lengths while containing completely different or corrupted data. A cryptographic hash like SHA-256 produces a unique 256-bit fingerprint. If even a single bit is modified, the Avalanche Effect causes more than 50% of the hash output to change, making silent bitrot impossible to hide.

**Q3: When would an enterprise choose AWS Snowball over a 1 Gbps Direct Connect line?**
> *Answer:* When data volume exceeds ~50 to 100 TB and network bandwidth is constrained or costly. Transferring 100 TB over a 100 Mbps connection takes ~3 months, whereas an 80 TB Snowball appliance can be loaded locally in 1 day and shipped via courier in 2 days.

**Q4: How do cloud migrations achieve zero downtime for live transactional databases?**
> *Answer:* By using **Change-Data-Capture (CDC)** (such as AWS DMS). An initial baseline snapshot is copied to the cloud while the on-premises database remains live. The CDC engine continuously streams all INSERT/UPDATE/DELETE write logs to the cloud replica. Once delta lag reaches near-zero, a brief 5-second DNS switchover directs traffic to the cloud with zero data loss.
