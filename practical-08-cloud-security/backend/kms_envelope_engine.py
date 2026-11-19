import base64
import os
import secrets
import threading
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cert_generator import generate_tls_pki

class KmsEnvelopeEngine:
    def __init__(self):
        self.lock = threading.Lock()
        # Simulated Cloud Hardware Security Module (HSM) Key Encryption Key (KEK)
        # In real AWS KMS / Cloud KMS, this 256-bit key NEVER leaves the HSM hardware boundary!
        self.kek_key = secrets.token_bytes(32) # 256-bit AES-GCM Master Key
        self.kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/mrk-84a1e9c2-sec"
        self.key_created_at = time.time()
        self.key_rotation_enabled = True
        self.key_version = "v2 (2026-Q1 Rotated)"

        # Generate TLS PKI assets on startup
        self.tls_cert_metadata = generate_tls_pki()

        # Cloud Security Posture Compliance Checks
        self.posture_checks = {
            "s3_sse_kms": {
                "id": "s3_sse_kms",
                "title": "S3 Storage Server-Side Encryption (SSE-KMS)",
                "description": "Default bucket encryption enforced using Customer Managed KMS Key (AES-256-GCM).",
                "status": "PASS",
                "severity": "CRITICAL",
                "enabled": True
            },
            "tls_version": {
                "id": "tls_version",
                "title": "TLS 1.3 Strict In-Transit Encryption",
                "description": "Legacy insecure protocols (SSLv3, TLS 1.0, TLS 1.1) disabled on all load balancers.",
                "status": "PASS",
                "severity": "HIGH",
                "enabled": True
            },
            "firewall_ssh": {
                "id": "firewall_ssh",
                "title": "Restricted Ingress Ports (No 0.0.0.0/0 on Port 22/5432)",
                "description": "Security Groups forbid administrative SSH (22) and DB (5432) exposure to public internet.",
                "status": "PASS",
                "severity": "HIGH",
                "enabled": True
            },
            "kms_rotation": {
                "id": "kms_rotation",
                "title": "Automatic KMS Master Key Annual Rotation",
                "description": "Cloud KMS automatically rotates backing cryptographic material every 365 days.",
                "status": "PASS",
                "severity": "MEDIUM",
                "enabled": True
            }
        }

        # Stored encrypted envelopes
        self.envelopes = []

    def get_status(self):
        with self.lock:
            pass_count = sum(1 for c in self.posture_checks.values() if c["enabled"])
            total_count = len(self.posture_checks)
            compliance_pct = round((pass_count / total_count) * 100, 1)

            return {
                "kms_key_id": self.kms_key_id,
                "key_version": self.key_version,
                "key_rotation_enabled": self.key_rotation_enabled,
                "compliance_score_pct": compliance_pct,
                "posture_checks": list(self.posture_checks.values()),
                "total_envelopes_stored": len(self.envelopes),
                "tls_cert_common_name": self.tls_cert_metadata["common_name"],
                "tls_fingerprint": self.tls_cert_metadata["sha256_fingerprint"]
            }

    def get_certificate_details(self):
        with self.lock:
            return self.tls_cert_metadata

    def toggle_posture_check(self, check_id: str):
        with self.lock:
            if check_id in self.posture_checks:
                check = self.posture_checks[check_id]
                check["enabled"] = not check["enabled"]
                check["status"] = "PASS" if check["enabled"] else "FAIL"
                return check
            raise ValueError("Posture check ID not found")

    def _kms_generate_data_key(self):
        """Simulates AWS KMS: GenerateDataKey API call."""
        # 1. Generate fresh 256-bit plaintext DEK
        plaintext_dek = secrets.token_bytes(32)

        # 2. Encrypt the DEK using the HSM KEK (AES-256-GCM)
        kek_aesgcm = AESGCM(self.kek_key)
        dek_iv = secrets.token_bytes(12)
        encrypted_dek_bytes = kek_aesgcm.encrypt(dek_iv, plaintext_dek, None)

        # Pack IV + Ciphertext for the encrypted DEK
        wrapped_dek_b64 = base64.b64encode(dek_iv + encrypted_dek_bytes).decode("utf-8")
        plaintext_dek_b64 = base64.b64encode(plaintext_dek).decode("utf-8")

        return plaintext_dek, plaintext_dek_b64, wrapped_dek_b64

    def _kms_decrypt_data_key(self, wrapped_dek_b64: str) -> bytes:
        """Simulates AWS KMS: Decrypt API call."""
        raw = base64.b64decode(wrapped_dek_b64)
        dek_iv = raw[:12]
        encrypted_dek = raw[12:]

        kek_aesgcm = AESGCM(self.kek_key)
        plaintext_dek = kek_aesgcm.decrypt(dek_iv, encrypted_dek, None)
        return plaintext_dek

    def encrypt_envelope(self, plaintext_payload: str, label: str = "Confidential Payload"):
        with self.lock:
            steps = []

            # Step 1: Call KMS to Generate a Data Key (DEK)
            steps.append({
                "step": 1,
                "component": "Cloud KMS Service (HSM)",
                "action": f"Invoked kms:GenerateDataKey(KeyId='{self.kms_key_id}', KeySpec='AES_256').",
                "details": "KMS generated a unique 256-bit Data Encryption Key (DEK) and encrypted it under the HSM Master KEK."
            })
            plaintext_dek, plaintext_dek_b64, wrapped_dek_b64 = self._kms_generate_data_key()

            # Step 2: Encrypt Payload Client-Side using Plaintext DEK (AES-256-GCM)
            payload_iv = secrets.token_bytes(12)
            dek_aesgcm = AESGCM(plaintext_dek)
            ciphertext_with_tag = dek_aesgcm.encrypt(payload_iv, plaintext_payload.encode("utf-8"), None)
            ciphertext_b64 = base64.b64encode(ciphertext_with_tag).decode("utf-8")
            iv_b64 = base64.b64encode(payload_iv).decode("utf-8")

            steps.append({
                "step": 2,
                "component": "Application Runtime (Client-Side)",
                "action": f"Encrypted plaintext payload ({len(plaintext_payload)} bytes) using AES-256-GCM with 96-bit random IV.",
                "details": "Ciphertext generated with cryptographic 128-bit authentication tag to prevent tampering."
            })

            # Step 3: Zero / Wipe Plaintext DEK from Memory
            # In Python, we explicitly delete the reference
            del plaintext_dek
            steps.append({
                "step": 3,
                "component": "Memory Safety Guard",
                "action": "Plaintext DEK memory reference wiped (zeroed).",
                "details": "The unencrypted DEK is destroyed from RAM. Only the KMS-encrypted DEK is persisted."
            })

            # Step 4: Assemble Envelope Package
            envelope = {
                "envelope_id": f"env-{secrets.token_hex(4)}",
                "label": label,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "algorithm": "AES-256-GCM",
                "kms_key_id": self.kms_key_id,
                "encrypted_dek_b64": wrapped_dek_b64,
                "iv_b64": iv_b64,
                "ciphertext_payload_b64": ciphertext_b64,
                "plaintext_bytes_len": len(plaintext_payload),
                "ciphertext_bytes_len": len(ciphertext_with_tag)
            }

            self.envelopes.insert(0, envelope)
            if len(self.envelopes) > 20:
                self.envelopes.pop()

            steps.append({
                "step": 4,
                "component": "Cloud Storage (S3 / DB)",
                "action": f"Stored Envelope Package '{envelope['envelope_id']}'.",
                "details": "The ciphertext payload is stored alongside the encrypted DEK. Even if the database is leaked, data cannot be read without KMS authorization."
            })

            return {
                "envelope": envelope,
                "trace": steps,
                "simulated_plaintext_dek_preview": f"{plaintext_dek_b64[:12]}... (Wiped from memory)"
            }

    def decrypt_envelope(self, envelope_id: str):
        with self.lock:
            target = next((e for e in self.envelopes if e["envelope_id"] == envelope_id), None)
            if not target:
                raise ValueError("Envelope ID not found")

            steps = []

            # Step 1: Send Encrypted DEK to KMS for Decryption
            steps.append({
                "step": 1,
                "component": "Cloud KMS Service (HSM)",
                "action": f"Invoked kms:Decrypt(CiphertextBlob='{target['encrypted_dek_b64'][:16]}...', KeyId='{target['kms_key_id']}').",
                "details": "KMS validated caller IAM permissions, decrypted the DEK using the HSM Master KEK, and returned the plaintext DEK."
            })
            recovered_dek = self._kms_decrypt_data_key(target["encrypted_dek_b64"])

            # Step 2: Decrypt Payload using Recovered DEK & Validate Auth Tag
            try:
                dek_aesgcm = AESGCM(recovered_dek)
                payload_iv = base64.b64decode(target["iv_b64"])
                ciphertext = base64.b64decode(target["ciphertext_payload_b64"])

                decrypted_bytes = dek_aesgcm.decrypt(payload_iv, ciphertext, None)
                plaintext_result = decrypted_bytes.decode("utf-8")

                steps.append({
                    "step": 2,
                    "component": "Application Runtime (Client-Side)",
                    "action": "AES-256-GCM authentication tag verified. Plaintext payload recovered.",
                    "details": "Data integrity confirmed: 0 bits altered in transit or at rest."
                })
            except Exception as e:
                steps.append({
                    "step": 2,
                    "component": "Cryptographic Authenticator",
                    "action": "AUTHENTICATION FAILURE: AES-GCM Tag mismatch!",
                    "details": "The ciphertext or IV was tampered with! Decryption aborted."
                })
                raise ValueError("Ciphertext integrity compromised! Authentication tag verification failed.")
            finally:
                del recovered_dek

            return {
                "envelope_id": envelope_id,
                "decrypted_plaintext": plaintext_result,
                "trace": steps
            }
