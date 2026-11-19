# Practical 08: Cloud Security & Envelope Encryption (KMS Simulator)

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![KMS](https://img.shields.io/badge/KMS-Envelope_Encryption-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/kms/)
[![AES-256-GCM](https://img.shields.io/badge/Cipher-AES--256--GCM-green.svg)](https://csrc.nist.gov/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 35 MB RAM) **Cloud Security Architecture & Key Management Service (KMS) Simulator** demonstrating defense-in-depth, Envelope Encryption (DEK/KEK), AES-256-GCM authenticated cipher operations, X.509 TLS in-transit PKI, and Cloud Security Posture Management (CSPM).

> **👨‍🎓 For Students & Educators:** Read the [**`STUDENT_GUIDE.md`**](STUDENT_GUIDE.md) for a beginner-friendly walkthrough, interactive lab tasks, and viva/interview prep.

---

## 🏗️ Core Cryptographic Architecture

### 1. Envelope Encryption Pattern (DEK vs. KEK)
Cloud Key Management Services (AWS KMS, Google Cloud KMS, Azure Key Vault) use **Envelope Encryption**:
- **Key Encryption Key (KEK / Master Key)**: Stored inside Hardware Security Modules (HSMs). The raw plaintext KEK **never leaves the HSM boundary**.
- **Data Encryption Key (DEK)**: A unique, cryptographically random 256-bit symmetric key generated per object.
- **Workflow**:
  1. Application calls KMS: `GenerateDataKey(KeyId)`.
  2. KMS returns: `PlaintextDEK` and `CiphertextDEK` (encrypted under the HSM KEK).
  3. Application encrypts data client-side with `PlaintextDEK` using `AES-256-GCM`.
  4. Application **immediately zeroes and wipes** the `PlaintextDEK` from memory.
  5. The ciphertext is stored alongside the `CiphertextDEK` (the envelope).

### 2. Authenticated Encryption with Associated Data (AEAD)
Using `AES-256-GCM`, each encryption produces:
- 96-bit unique initialization vector (IV / Nonce).
- Encrypted ciphertext.
- 128-bit **Authentication Tag**: Mathematically guarantees data integrity. Any bit altered in transit or at rest causes immediate decryption failure (`AuthenticationFailed`).

### 3. In-Transit TLS 1.3 PKI
Generates 2048-bit RSA keys and self-signed X.509 certificates with **Subject Alternative Names (SAN)** for microservice mutual authentication.

---

## 🚀 Quickstart & Sequential Execution

### 1. Launch the Stack
```bash
cd practical-08-cloud-security
cp .env.example .env
docker compose up --build -d
```

### 2. Verify Health & KMS Status
```bash
# Verify health probe
curl -s http://localhost:8080/health | python3 -m json.tool

# Inspect KMS key status and compliance score
curl -s http://localhost:8080/api/status | python3 -m json.tool

# Inspect generated TLS certificate
curl -s http://localhost:8080/api/certificate | python3 -m json.tool
```

### 3. Interactive Web Dashboard
Open **[http://localhost:8080](http://localhost:8080)** to:
- Test real-time envelope encryption and watch the step-by-step cryptographic lifecycle.
- Decrypt stored envelopes via KMS.
- Inspect the X.509 server certificate and SAN domains.
- Remediate compliance checks in the Security Posture Matrix.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|:---|:---:|:---|
| `/health` | `GET` | Microservice health status |
| `/api/status` | `GET` | KMS key status, annual rotation, and security posture score |
| `/api/certificate` | `GET` | X.509 TLS certificate properties and SAN domains |
| `/api/envelope/encrypt` | `POST` | Encrypts payload via KMS envelope encryption |
| `/api/envelope/decrypt` | `POST` | Decrypts an envelope package using KMS DEK unwrapping |
| `/api/posture/toggle` | `POST` | Toggles a CSPM compliance check |

---

## 🧹 Teardown & RAM Reclamation
```bash
docker compose down
```
Instantly stops containers and reclaims all memory.
