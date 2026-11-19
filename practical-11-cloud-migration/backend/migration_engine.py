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
            self.pipeline_state["status"] = "idle"
            self.pipeline_state["progress_pct"] = 0
            self.pipeline_state["current_step"] = "On-premises datasets ready for migration"
            self.pipeline_state["bytes_transferred"] = 0
            self.pipeline_state["tamper_injected"] = False

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
            self._log_event("INFO", f"On-premises environment seeded: 4 enterprise assets ({self.pipeline_state['total_bytes']} bytes total).")

    def get_status(self):
        with self.lock:
            # Strip raw bytes when returning JSON status to avoid huge payloads
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
                "events": self.migration_events[:25]
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

        self._log_event("INFO", f"Cloud Migration Pipeline started via {network_mode.replace('_', ' ').upper()}...")

        start_time = time.time()
        for idx, asset in enumerate(assets):
            with self.lock:
                self.pipeline_state["active_file"] = asset["target_s3_key"]
                self.pipeline_state["current_step"] = f"Streaming {asset['target_s3_key']} to s3://{self.target_bucket}..."
                asset["status"] = "In Transit (Chunked Streaming)"

            # Simulated chunked transfer delay based on network speed
            delay = 0.4 if network_mode == "direct_connect_1gbps" else 1.2
            time.sleep(delay)

            # Ingest to Cloud S3
            with self.lock:
                raw_data = asset["raw_bytes"]
                
                # If tampering / bitrot injected, flip 1 byte on transactions.jsonl
                is_corrupted = False
                if tamper and "transactions" in asset["target_s3_key"]:
                    # Modify 1 byte: Change 1 to 9
                    raw_data = raw_data.replace(b'"amount":', b'"amount": 99999 + ')
                    is_corrupted = True
                    self._log_event("WARNING", f"[TAMPER] Injected 1-bit packet bitrot into {asset['target_s3_key']} during transit!")

                target_sha = hashlib.sha256(raw_data).hexdigest()
                target_etag = hashlib.md5(raw_data).hexdigest()

                self.cloud_s3_storage[asset["target_s3_key"]] = {
                    "s3_key": asset["target_s3_key"],
                    "bucket": self.target_bucket,
                    "size_bytes": len(raw_data),
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
                self.pipeline_state["bytes_transferred"] += asset["size_bytes"]
                self.pipeline_state["progress_pct"] = int(((idx + 1) / total_assets) * 100)
                self._log_event("INFO", f"Uploaded s3://{self.target_bucket}/{asset['target_s3_key']} ({asset['size_bytes']} bytes).")

        # Finished transferring all assets -> Perform automatic audit verification
        elapsed = round(time.time() - start_time, 2)
        with self.lock:
            self.pipeline_state["elapsed_sec"] = elapsed
            mb_transferred = self.pipeline_state["bytes_transferred"] / (1024 * 1024)
            self.pipeline_state["throughput_mbps"] = round((mb_transferred * 8) / max(elapsed, 0.1), 2)
            self.pipeline_state["current_step"] = "Executing Post-Migration Cryptographic Audit..."
            
        time.sleep(0.5)
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
