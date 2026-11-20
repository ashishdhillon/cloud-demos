import datetime
import hashlib
import json
import random
import sqlite3
import threading
import time
import uuid

class MigrationEngine:
    def __init__(self):
        self.lock = threading.RLock()
        self.target_bucket = "migrated-enterprise-cloud"
        self.pipeline_state = {
            "status": "idle",  # idle, running, completed, corrupted
            "progress_pct": 0,
            "current_step": "Awaiting pipeline trigger",
            "active_file": "",
            "bytes_transferred": 0,
            "total_bytes": 0,
            "throughput_mbps": 0.0,
            "elapsed_sec": 0.0,
            "network_mode": "direct_connect_1gbps",
            "tamper_injected": False
        }
        
        # In-memory storage for on-prem files and SQLite database
        self.onprem_assets = {}
        self.cloud_s3_storage = {}
        self.audit_records = []
        self.migration_events = []
        self.tamper_details = None

        # Cutover state machine
        self.cutover_state = {
            "phase": "onprem_active",  # onprem_active, delta_sync, dns_cutover, cloud_active, rolled_back
            "active_endpoint": "192.168.1.50 (On-Premises Data Center)",
            "dns_record": "erp.enterprise.internal -> A 192.168.1.50 (TTL 60s)",
            "live_traffic_target": "On-Premises ERP",
            "delta_tx_synced": 0,
            "cutover_timestamp": None,
            "can_rollback": False
        }
        
        # Initialize initial datasets
        self.seed_onprem_environment()

    def _log_event(self, level: str, message: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.migration_events.insert(0, {
            "time": now,
            "level": level,
            "message": message
        })
        if len(self.migration_events) > 50:
            self.migration_events.pop()

    def seed_onprem_environment(self):
        with self.lock:
            self.onprem_assets = {}
            self.cloud_s3_storage = {}
            self.audit_records = []
            self.tamper_details = None
            self.pipeline_state["status"] = "idle"
            self.pipeline_state["progress_pct"] = 0
            self.pipeline_state["current_step"] = "On-premises datasets ready for migration"
            self.pipeline_state["bytes_transferred"] = 0
            self.pipeline_state["tamper_injected"] = False
            self.pipeline_state["throughput_mbps"] = 0.0
            self.pipeline_state["elapsed_sec"] = 0.0

            self.cutover_state = {
                "phase": "onprem_active",
                "active_endpoint": "192.168.1.50 (On-Premises Data Center)",
                "dns_record": "erp.enterprise.internal -> A 192.168.1.50 (TTL 60s)",
                "live_traffic_target": "On-Premises ERP",
                "delta_tx_synced": 0,
                "cutover_timestamp": None,
                "can_rollback": False
            }

            # 1. Generate SQLite in memory
            conn = sqlite3.connect(":memory:")
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE customers (
                    id INTEGER PRIMARY KEY,
                    company_name TEXT,
                    tier TEXT,
                    region TEXT,
                    account_balance REAL
                )
            """)
            cur.execute("""
                CREATE TABLE transactions (
                    tx_id TEXT PRIMARY KEY,
                    customer_id INTEGER,
                    amount REAL,
                    currency TEXT,
                    status TEXT,
                    timestamp TEXT
                )
            """)

            companies = [
                ("Global Logistics Corp", "Enterprise", "US-East", 245000.00),
                ("Apex Financial Group", "Enterprise", "EU-West", 1120000.50),
                ("Nordic Cloud Labs", "Standard", "EU-North", 84500.00),
                ("Pacific Rim Imports", "Premier", "AP-South", 630000.25),
                ("Quantum Dynamics", "Enterprise", "US-West", 950000.00),
                ("Horizon Media LLC", "Standard", "US-Central", 42000.00),
                ("BioSynth Laboratories", "Premier", "EU-Central", 780000.75),
                ("Vertex Retail AI", "Standard", "AP-East", 154000.00)
            ]
            for c in companies:
                cur.execute("INSERT INTO customers (company_name, tier, region, account_balance) VALUES (?, ?, ?, ?)", c)

            for i in range(1, 301):
                tx_id = f"TX-{uuid.uuid4().hex[:8].upper()}"
                cid = random.randint(1, len(companies))
                amt = round(random.uniform(150.0, 45000.0), 2)
                cur.execute(
                    "INSERT INTO transactions (tx_id, customer_id, amount, currency, status, timestamp) VALUES (?, ?, ?, 'USD', 'SETTLED', datetime('now', '-{} hours'))".format(random.randint(1, 720)),
                    (tx_id, cid, amt)
                )
            conn.commit()

            # Export Customers to JSONL payload
            cur.execute("SELECT * FROM customers")
            cust_rows = cur.fetchall()
            cust_jsonl_lines = [
                json.dumps({"id": r[0], "company": r[1], "tier": r[2], "region": r[3], "balance": r[4]})
                for r in cust_rows
            ]
            cust_payload = ("\n".join(cust_jsonl_lines) + "\n").encode("utf-8")

            # Export Transactions to JSONL payload
            cur.execute("SELECT * FROM transactions")
            tx_rows = cur.fetchall()
            tx_jsonl_lines = [
                json.dumps({"tx_id": r[0], "customer_id": r[1], "amount": r[2], "currency": r[3], "status": r[4], "timestamp": r[5]})
                for r in tx_rows
            ]
            tx_payload = ("\n".join(tx_jsonl_lines) + "\n").encode("utf-8")

            conn.close()

            # 2. Generate Enterprise Flat Documents
            csv_content = (
                "quarter,department,budget_allocated,budget_spent,variance_pct,auditor_approval\n"
                "Q1-2026,Engineering,1500000,1420000,-5.33,APPROVED\n"
                "Q2-2026,Operations,850000,862000,+1.41,APPROVED\n"
                "Q3-2026,Cloud-Infra,2100000,2050000,-2.38,APPROVED\n"
                "Q4-2026,Security,750000,740000,-1.33,APPROVED\n"
            ).encode("utf-8")

            compliance_txt = (
                "ENTERPRISE CLOUD COMPLIANCE & GOVERNANCE AUDIT REPORT\n"
                "Standard: SOC2 Type II, ISO/IEC 27001:2022, HIPAA Security Rule\n"
                "Encryption at Rest: AES-256 Enabled\n"
                "Data Custodian: Head of Cloud Platform Engineering\n"
                "Audit Status: 100% COMPLIANT - ZERO DEFICIENCIES IDENTIFIED.\n"
            ).encode("utf-8")

            # Calculate source SHA-256 hashes
            def asset_entry(source_name, target_s3_key, data_bytes, asset_type, record_count):
                hasher = hashlib.sha256()
                hasher.update(data_bytes)
                sha = hasher.hexdigest()
                md5_etag = hashlib.md5(data_bytes).hexdigest()
                return {
                    "source_name": source_name,
                    "target_s3_key": target_s3_key,
                    "size_bytes": len(data_bytes),
                    "record_count": record_count,
                    "asset_type": asset_type,
                    "source_sha256": sha,
                    "source_etag": md5_etag,
                    "raw_bytes": data_bytes,
                    "status": "Ready for Migration"
                }

            self.onprem_assets = {
                "customers.jsonl": asset_entry("customers.jsonl (from legacy_erp.db)", "database_exports/customers.jsonl", cust_payload, "Relational Table (JSONL)", len(cust_rows)),
                "transactions.jsonl": asset_entry("transactions.jsonl (from legacy_erp.db)", "database_exports/transactions.jsonl", tx_payload, "Relational Table (JSONL)", len(tx_rows)),
                "q3_financial_audit.csv": asset_entry("q3_financial_audit.csv", "documents/q3_financial_audit.csv", csv_content, "Flat File (CSV)", 4),
                "compliance_audit.txt": asset_entry("compliance_audit.txt", "documents/compliance_audit.txt", compliance_txt, "Text Document", 5)
            }

            self.pipeline_state["total_bytes"] = sum(a["size_bytes"] for a in self.onprem_assets.values())
            self._log_event("INFO", f"On-premises environment initialized: 4 enterprise assets ({self.pipeline_state['total_bytes']} bytes total).")

    def get_status(self):
        with self.lock:
            sanitized_onprem = {}
            for k, v in self.onprem_assets.items():
                sanitized_onprem[k] = {
                    "source_name": v["source_name"],
                    "target_s3_key": v["target_s3_key"],
                    "size_bytes": v["size_bytes"],
                    "record_count": v["record_count"],
                    "asset_type": v["asset_type"],
                    "source_sha256": v["source_sha256"],
                    "source_etag": v["source_etag"],
                    "status": v["status"]
                }

            return {
                "target_bucket": self.target_bucket,
                "pipeline_state": self.pipeline_state,
                "onprem_assets": sanitized_onprem,
                "cloud_s3_storage": self.cloud_s3_storage,
                "audit_records": self.audit_records,
                "tamper_details": self.tamper_details,
                "cutover_state": self.cutover_state,
                "events": self.migration_events[:30]
            }

    def start_migration(self, network_mode: str = "direct_connect_1gbps", tamper: bool = False):
        with self.lock:
            if self.pipeline_state["status"] == "running":
                return {"error": "Migration pipeline is already in progress"}

            self.pipeline_state["status"] = "running"
            self.pipeline_state["network_mode"] = network_mode
            self.pipeline_state["tamper_injected"] = tamper
            self.pipeline_state["progress_pct"] = 0
            self.pipeline_state["bytes_transferred"] = 0
            self.tamper_details = None
            self.cloud_s3_storage = {}
            self.audit_records = []

            # Launch background worker
            threading.Thread(target=self._run_migration_worker, daemon=True).start()
            return {"success": True, "message": "Migration pipeline initiated."}

    def _run_migration_worker(self):
        with self.lock:
            assets = list(self.onprem_assets.values())
            total_assets = len(assets)
            network_mode = self.pipeline_state["network_mode"]
            tamper = self.pipeline_state["tamper_injected"]

        mode_titles = {
            "direct_connect_1gbps": "AWS Direct Connect (1 Gbps Dedicated Fiber)",
            "internet_100mbps": "Public Internet Site-to-Site VPN (100 Mbps Shared)",
            "snowball_edge_80tb": "AWS Snowball Edge 80 TB (Offline Physical Appliance)"
        }
        self._log_event("INFO", f"Cloud Migration Pipeline triggered via {mode_titles.get(network_mode, network_mode)}.")

        start_time = time.time()

        if network_mode == "snowball_edge_80tb":
            # Simulate Snowball appliance logistics
            with self.lock:
                self.pipeline_state["current_step"] = "Step 1/4: Provisioning AWS Snowball Edge 80 TB Appliance..."
                self.pipeline_state["progress_pct"] = 15
            self._log_event("INFO", "[SNOWBALL] Appliance delivered to on-premises loading bay. Connecting 10 GbE RJ45 fiber uplink.")
            time.sleep(0.8)

            with self.lock:
                self.pipeline_state["current_step"] = "Step 2/4: Copying datasets to local Snowball AES-256 encrypted appliance..."
                self.pipeline_state["progress_pct"] = 40
            self._log_event("INFO", "[SNOWBALL] Local ingest completed at 850 MB/s. E-ink shipping label generated.")
            time.sleep(0.8)

            with self.lock:
                self.pipeline_state["current_step"] = "Step 3/4: Courier Transit to AWS US-East Hyperscale Facility..."
                self.pipeline_state["progress_pct"] = 70
            self._log_event("INFO", "[SNOWBALL] Tamper-evident seals intact. Appliance docked in AWS region data center.")
            time.sleep(0.8)

            with self.lock:
                self.pipeline_state["current_step"] = "Step 4/4: Ingesting Snowball hardware chunks directly into AWS S3 Lakehouse..."
                self.pipeline_state["progress_pct"] = 85

        for idx, asset in enumerate(assets):
            with self.lock:
                self.pipeline_state["active_file"] = asset["target_s3_key"]
                self.pipeline_state["current_step"] = f"Streaming {asset['target_s3_key']} to s3://{self.target_bucket}..."
                asset["status"] = "In Transit (Chunked Streaming)"

            # Simulated chunked transfer delay
            if network_mode == "direct_connect_1gbps":
                delay = 0.35
            elif network_mode == "internet_100mbps":
                delay = 0.9
            else:
                delay = 0.3  # Direct ingest from Snowball
            time.sleep(delay)

            # Ingest to Cloud S3
            with self.lock:
                raw_data = bytearray(asset["raw_bytes"])
                is_corrupted = False

                # If tampering / bitrot injected, flip 1 byte on transactions.jsonl
                if tamper and "transactions" in asset["target_s3_key"]:
                    # Exact corruption: Replace b'"amount":' with b'"amount": 99999 + '
                    original_bytes = bytes(raw_data)
                    corrupted_bytes = original_bytes.replace(b'"amount":', b'"amount": 99999 + ', 1)
                    raw_data = bytearray(corrupted_bytes)
                    is_corrupted = True

                    # Calculate bit differences (Hamming Distance between original and corrupted SHA-256)
                    orig_sha = hashlib.sha256(original_bytes).hexdigest()
                    bad_sha = hashlib.sha256(corrupted_bytes).hexdigest()
                    orig_bits = bin(int(orig_sha, 16))[2:].zfill(256)
                    bad_bits = bin(int(bad_sha, 16))[2:].zfill(256)
                    flipped_count = sum(c1 != c2 for c1, c2 in zip(orig_bits, bad_bits))

                    self.tamper_details = {
                        "asset_key": asset["target_s3_key"],
                        "byte_offset": "0x00A8 (Line 1, Record TX-A83B)",
                        "original_snippet": '"amount": 2450.00',
                        "corrupted_snippet": '"amount": 99999 + 2450.00',
                        "source_sha256": orig_sha,
                        "target_sha256": bad_sha,
                        "source_etag": hashlib.md5(original_bytes).hexdigest(),
                        "target_etag": hashlib.md5(corrupted_bytes).hexdigest(),
                        "avalanche_flipped_bits": f"{flipped_count} of 256 bits ({round(flipped_count / 256 * 100, 1)}%)",
                        "detected_by": "SHA-256 Cryptographic Checksum Auditor"
                    }
                    self._log_event("WARNING", f"[TAMPER INJECTED] Bit-level corruption simulated in {asset['target_s3_key']} during transit!")

                final_bytes = bytes(raw_data)
                target_sha = hashlib.sha256(final_bytes).hexdigest()
                target_etag = hashlib.md5(final_bytes).hexdigest()

                self.cloud_s3_storage[asset["target_s3_key"]] = {
                    "s3_key": asset["target_s3_key"],
                    "bucket": self.target_bucket,
                    "size_bytes": len(final_bytes),
                    "storage_class": "STANDARD",
                    "etag": target_etag,
                    "s3_sha256": target_sha,
                    "metadata": {
                        "Origin": "On-Premises Data Center",
                        "DataClassification": "Confidential",
                        "ComplianceStandard": "SOC2-TypeII",
                        "RetentionPeriod": "7-Years"
                    },
                    "uploaded_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
                }

                asset["status"] = "Migrated to S3"
                self.pipeline_state["bytes_transferred"] += len(final_bytes)
                if network_mode == "snowball_edge_80tb":
                    self.pipeline_state["progress_pct"] = min(98, 85 + int(((idx + 1) / total_assets) * 15))
                else:
                    self.pipeline_state["progress_pct"] = int(((idx + 1) / total_assets) * 100)

                self._log_event("INFO", f"Uploaded s3://{self.target_bucket}/{asset['target_s3_key']} ({len(final_bytes)} bytes).")

        # Finished transferring all assets -> Perform cryptographic audit
        elapsed = round(time.time() - start_time, 2)
        with self.lock:
            self.pipeline_state["elapsed_sec"] = elapsed
            mb_transferred = self.pipeline_state["bytes_transferred"] / (1024 * 1024)
            self.pipeline_state["throughput_mbps"] = round((mb_transferred * 8) / max(elapsed, 0.1), 2)
            self.pipeline_state["current_step"] = "Executing Post-Migration Cryptographic Audit..."
            self.pipeline_state["progress_pct"] = 100

        time.sleep(0.4)
        self.run_audit_verification()

    def run_audit_verification(self):
        """Performs SHA-256 cryptographic parity check between source on-prem files and S3 objects."""
        with self.lock:
            self.audit_records = []
            has_failures = False

            for key, source_asset in self.onprem_assets.items():
                s3_key = source_asset["target_s3_key"]
                s3_obj = self.cloud_s3_storage.get(s3_key)

                if not s3_obj:
                    self.audit_records.append({
                        "asset_key": s3_key,
                        "bytes": source_asset["size_bytes"],
                        "source_sha256": source_asset["source_sha256"],
                        "target_sha256": "N/A (Missing Object)",
                        "parity_match": False,
                        "status": "FAIL: MISSING IN CLOUD"
                    })
                    has_failures = True
                    continue

                source_hash = source_asset["source_sha256"]
                target_hash = s3_obj["s3_sha256"]
                match = (source_hash == target_hash)

                if match:
                    status_str = "PASS (100% Cryptographic Parity)"
                else:
                    status_str = "FAIL: CHECKSUM MISMATCH (BITROT / DATA TAMPERING)"
                    has_failures = True

                self.audit_records.append({
                    "asset_key": s3_key,
                    "bytes": s3_obj["size_bytes"],
                    "source_sha256": source_hash,
                    "target_sha256": target_hash,
                    "parity_match": match,
                    "status": status_str
                })

            if has_failures:
                self.pipeline_state["status"] = "corrupted"
                self.pipeline_state["current_step"] = "Audit FAILED: Cryptographic Checksum Mismatch Detected!"
                self._log_event("ERROR", "POST-MIGRATION AUDIT FAILED! Checksum mismatch detected — potential packet corruption.")
            else:
                self.pipeline_state["status"] = "completed"
                self.pipeline_state["current_step"] = "Migration & Verification Complete: 100% Parity Verified (Zero Loss)!"
                self._log_event("SUCCESS", "POST-MIGRATION AUDIT PASSED: All 4 assets verified with 0% data corruption.")

            return {
                "status": self.pipeline_state["status"],
                "records": self.audit_records
            }

    def heal_corrupted_chunk(self):
        """Self-healing block retransmission: re-uploads clean chunk for corrupted objects."""
        with self.lock:
            if not self.tamper_details:
                return {"success": False, "message": "No corrupted chunks detected to heal."}

            corrupted_key = self.tamper_details["asset_key"]
            source_key = "transactions.jsonl"
            clean_asset = self.onprem_assets.get(source_key)
            if not clean_asset:
                return {"success": False, "message": "Source asset not found."}

            clean_bytes = clean_asset["raw_bytes"]
            clean_sha = hashlib.sha256(clean_bytes).hexdigest()
            clean_etag = hashlib.md5(clean_bytes).hexdigest()

            # Replace object in cloud S3 storage
            self.cloud_s3_storage[corrupted_key] = {
                "s3_key": corrupted_key,
                "bucket": self.target_bucket,
                "size_bytes": len(clean_bytes),
                "storage_class": "STANDARD",
                "etag": clean_etag,
                "s3_sha256": clean_sha,
                "metadata": {
                    "Origin": "On-Premises Data Center",
                    "DataClassification": "Confidential",
                    "ComplianceStandard": "SOC2-TypeII",
                    "RetentionPeriod": "7-Years",
                    "SelfHealed": "True"
                },
                "uploaded_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            }

            self.tamper_details = None
            self.pipeline_state["tamper_injected"] = False
            self._log_event("INFO", f"[AUTO-HEAL] Re-transmitted clean block for s3://{self.target_bucket}/{corrupted_key}. Parity restored.")
            self.run_audit_verification()

            return {
                "success": True,
                "message": "Block retransmitted successfully. SHA-256 cryptographic parity restored to 100%."
            }

    def trigger_cutover(self):
        """Simulates zero-downtime DNS cutover with Delta CDC Synchronization."""
        with self.lock:
            if self.pipeline_state["status"] != "completed":
                return {"success": False, "message": "Cannot cutover: Migration must be completed with 100% verified parity first."}

            threading.Thread(target=self._run_cutover_worker, daemon=True).start()
            return {"success": True, "message": "Zero-downtime cutover sequence initiated."}

    def _run_cutover_worker(self):
        # Step 1: Delta CDC sync
        with self.lock:
            self.cutover_state["phase"] = "delta_sync"
            self.cutover_state["live_traffic_target"] = "On-Premises (Capturing Delta CDC Changes)"
        self._log_event("INFO", "[CUTOVER 1/3] Flushing in-flight Change-Data-Capture (CDC) write buffer to Cloud Lakehouse...")
        time.sleep(1.2)

        # Step 2: Route 53 DNS Switchover
        with self.lock:
            self.cutover_state["phase"] = "dns_cutover"
            self.cutover_state["delta_tx_synced"] = 42
            self.cutover_state["dns_record"] = "erp.enterprise.internal -> CNAME cloud-alb.aws.internal (TTL 5s)"
        self._log_event("INFO", "[CUTOVER 2/3] Route 53 DNS switchover executed: CNAME pointed to Cloud Application Load Balancer.")
        time.sleep(1.0)

        # Step 3: Cloud Active & Rollback Ready
        with self.lock:
            self.cutover_state["phase"] = "cloud_active"
            self.cutover_state["active_endpoint"] = "cloud-alb.aws.internal (AWS Cloud Lakehouse & Microservices)"
            self.cutover_state["live_traffic_target"] = "100% AWS Cloud Production"
            self.cutover_state["cutover_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            self.cutover_state["can_rollback"] = True
        self._log_event("SUCCESS", "[CUTOVER 3/3] CUTOVER COMPLETE: Zero-downtime production cutover successful. System is 100% live in AWS!")

    def trigger_rollback(self):
        """Rollback DNS instantly back to on-premises in case of canary anomaly."""
        with self.lock:
            if not self.cutover_state["can_rollback"]:
                return {"success": False, "message": "Rollback not applicable or system is not in live cloud cutover."}

            self.cutover_state["phase"] = "rolled_back"
            self.cutover_state["active_endpoint"] = "192.168.1.50 (On-Premises Data Center)"
            self.cutover_state["dns_record"] = "erp.enterprise.internal -> A 192.168.1.50 (Emergency Rollback)"
            self.cutover_state["live_traffic_target"] = "Rolled Back to On-Premises (Safety Failover)"
            self.cutover_state["can_rollback"] = False
            self._log_event("WARNING", "[ROLLBACK] Emergency DNS failover triggered. Traffic instantly restored to On-Premises core!")

            return {"success": True, "message": "Emergency rollback executed. DNS pointing to on-premises host."}

    def get_assessment_matrix(self):
        """Returns Gartner 6-Rs Strategy workload profiles and decision criteria."""
        return [
            {
                "id": "oracle_erp",
                "name": "Legacy Oracle ERP & Financials",
                "current_tech": "Oracle 12c DB, PL/SQL, Bare-Metal Solaris",
                "recommended_strategy": "Replatform (Lift, Tinker & Shift)",
                "target_architecture": "Amazon Aurora PostgreSQL + AWS DMS",
                "complexity_score": 6,
                "velocity_weeks": 8,
                "cost_savings_pct": 58,
                "rationale": "Eliminates high Oracle core licensing costs without complete application rewrite by automating schema conversion.",
                "badge_class": "badge-replatform"
            },
            {
                "id": "monolith_billing",
                "name": "Monolithic Java Billing Engine",
                "current_tech": "Java 8 WAR monolith, WebLogic cluster",
                "recommended_strategy": "Refactor / Re-architect",
                "target_architecture": "Containerized Microservices on AWS ECS / Fargate",
                "complexity_score": 9,
                "velocity_weeks": 24,
                "cost_savings_pct": 65,
                "rationale": "High business agility and auto-scaling during flash sales; breaks monolithic lock into independently deployable services.",
                "badge_class": "badge-refactor"
            },
            {
                "id": "nas_file_shares",
                "name": "Corporate NAS Storage & Document Archives",
                "current_tech": "120 TB NetApp SAN/NAS, SMB/NFS Shares",
                "recommended_strategy": "Rehost (Lift & Shift)",
                "target_architecture": "Amazon S3 Intelligent-Tiering + Glacier Deep Archive",
                "complexity_score": 2,
                "velocity_weeks": 2,
                "cost_savings_pct": 82,
                "rationale": "Fastest migration path via AWS DataSync; achieves 99.999999999% (11 9s) durability with zero application refactoring.",
                "badge_class": "badge-rehost"
            },
            {
                "id": "bugzilla_server",
                "name": "Internal Bugzilla Ticketing Server",
                "current_tech": "Custom Perl scripts, MySQL 5.5, Linux VM",
                "recommended_strategy": "Repurchase (Drop & Shop / SaaS)",
                "target_architecture": "Jira Cloud SaaS / GitHub Enterprise SaaS",
                "complexity_score": 3,
                "velocity_weeks": 3,
                "cost_savings_pct": 45,
                "rationale": "Decommissions custom server maintenance, patching, and OS administration by adopting an enterprise SaaS platform.",
                "badge_class": "badge-repurchase"
            },
            {
                "id": "banking_mainframe",
                "name": "Core Banking Ledger Mainframe",
                "current_tech": "IBM z15 Mainframe, COBOL, DB2",
                "recommended_strategy": "Retain (Keep On-Premises)",
                "target_architecture": "Tier-IV On-Prem Datacenter + AWS Direct Connect Hybrid Link",
                "complexity_score": 10,
                "velocity_weeks": 0,
                "cost_savings_pct": 0,
                "rationale": "Extreme latency sensitivity (< 1ms) and regulatory sovereign compliance make immediate migration high risk.",
                "badge_class": "badge-retain"
            },
            {
                "id": "legacy_drupal_wiki",
                "name": "Deprecated 2018 Marketing Portal",
                "current_tech": "Drupal 7, Apache 2.4, Unpatched PHP",
                "recommended_strategy": "Retire (Decommission)",
                "target_architecture": "Cold Glacier Archive Snapshot -> Power Off Host",
                "complexity_score": 1,
                "velocity_weeks": 1,
                "cost_savings_pct": 100,
                "rationale": "Workload has zero active users; decommissioning eliminates server electric costs and closes a severe security vulnerability.",
                "badge_class": "badge-retire"
            }
        ]

    def calculate_tco(self, data_size_tb: float = 10.0, servers_count: int = 20):
        """Calculates 3-Year Total Cost of Ownership (TCO) & Carbon Footprint."""
        # On-premises costs
        hw_purchase = servers_count * 5500
        datacenter_lease = 36 * 1200
        power_cooling_pue = servers_count * 120 * 36  # ~1.8 PUE
        sysadmin_ops = 36 * 4500
        onprem_total = hw_purchase + datacenter_lease + power_cooling_pue + sysadmin_ops

        # AWS Cloud costs
        s3_storage = data_size_tb * 1024 * 0.021 * 36
        compute_serverless = servers_count * 95 * 36
        direct_connect = 36 * 350
        cloudops_automation = 36 * 800
        cloud_total = s3_storage + compute_serverless + direct_connect + cloudops_automation

        savings_dollar = max(0, onprem_total - cloud_total)
        savings_pct = round((savings_dollar / onprem_total) * 100, 1)

        # Carbon calculation (Metric Tons CO2e over 3 years)
        # On-prem datacenter typical PUE: 1.8 with standard grid mix
        onprem_carbon_tons = round(servers_count * 2.8 * 3, 1)
        # AWS cloud PUE: 1.15 with hyperscale efficiency and renewable contracts (~75% reduction)
        cloud_carbon_tons = round(onprem_carbon_tons * 0.24, 1)
        carbon_reduction_pct = round(((onprem_carbon_tons - cloud_carbon_tons) / onprem_carbon_tons) * 100, 1)

        return {
            "onprem_total": round(onprem_total, 2),
            "cloud_total": round(cloud_total, 2),
            "savings_dollar": round(savings_dollar, 2),
            "savings_pct": savings_pct,
            "onprem_carbon_tons": onprem_carbon_tons,
            "cloud_carbon_tons": cloud_carbon_tons,
            "carbon_reduction_pct": carbon_reduction_pct,
            "breakdown": {
                "onprem": {
                    "Hardware Amortization": hw_purchase,
                    "Datacenter Real Estate": datacenter_lease,
                    "Power & Cooling (PUE 1.8)": power_cooling_pue,
                    "Sysadmin Maintenance": sysadmin_ops
                },
                "cloud": {
                    "S3 Intelligent-Tiering": round(s3_storage, 2),
                    "Elastic Compute / ECS": round(compute_serverless, 2),
                    "AWS Direct Connect": direct_connect,
                    "Automated CloudOps": cloudops_automation
                }
            }
        }
