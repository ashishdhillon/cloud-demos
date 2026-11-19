# 🎓 Student Lab Guide: Practical 08 — Cloud Security & Envelope Encryption (KMS)

---

## 📌 1. What is this practical about? (The Real-World Problem)

Imagine you are storing a 5 GB encrypted database backup or a 500 MB video in AWS S3 or Google Cloud:
- Why don't you send the 5 GB file directly to **AWS Key Management Service (KMS)** over the network to encrypt it?
  - **Network Bottleneck:** Sending gigabytes of files over HTTP to KMS would saturate your network and cost immense bandwidth.
  - **KMS Payload Limit:** Cloud KMS services have a strict maximum payload limit of **4 Kilobytes** per API call! They cannot encrypt large files.

### The Cloud Solution: **Envelope Encryption (DEK & KEK)**
Cloud security engineers use the **Envelope Encryption pattern**:
1. **Master Key (KEK / Key Encryption Key):** Stored inside the cloud Hardware Security Module (HSM). The plaintext KEK **NEVER** leaves the HSM.
2. **Data Key (DEK):** A fast, temporary 256-bit AES symmetric key generated uniquely for each file.
3. **The Workflow:**
   - Your app asks KMS for a Data Key.
   - KMS gives you the plaintext DEK and an encrypted copy of that DEK.
   - Your application encrypts the 5 GB file locally in RAM using the plaintext DEK (`AES-256-GCM`).
   - Your application **immediately destroys the plaintext DEK from memory**.
   - You store the encrypted file alongside the encrypted DEK.
   - To decrypt later, you send only the tiny encrypted DEK to KMS to unwrap it!

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- Zero AWS accounts needed (the project includes a KMS HSM simulator and real AES-256-GCM AEAD engine).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-08-cloud-security
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Perform Envelope Encryption
1. In the **"Payload to Encrypt"** text box, keep or enter sensitive data (e.g. `Patient: Jane Doe, SSN: 987-65-4321, Card: 4111-2222-3333-4444`).
2. Click **"🔒 Encrypt Payload via KMS"**.
3. Watch the **Cryptographic Handshake & Memory Lifecycle Timeline**:
   - **Step 1 (KMS):** KMS generates a 256-bit DEK and encrypts it under the Master KEK.
   - **Step 2 (Client):** The payload is encrypted with `AES-256-GCM` using a 96-bit random IV and 128-bit authentication tag.
   - **Step 3 (Memory Guard):** The plaintext DEK is **immediately wiped from memory**.
   - **Step 4 (Storage):** The envelope package is saved (encrypted DEK + ciphertext payload).

### 🔹 Task 2: Perform KMS Decryption & Authentication Tag Check
1. Look at the **Stored Encrypted Envelopes** section.
2. Click **"🔓 Decrypt with KMS"**:
   - The app sends the encrypted DEK to KMS.
   - KMS decrypts the DEK and returns it.
   - The app verifies the AES-GCM authentication tag and restores the exact plaintext payload with zero data loss!

### 🔹 Task 3: Inspect In-Transit TLS 1.3 PKI
1. In the right panel, observe the **X.509 Server Certificate**:
   - Common Name: `cloud-service.internal`
   - Subject Alternative Names (SAN): `api.cloud-defense.internal`, `vault.cloud-defense.internal`, `localhost`.
   - Cryptographic Key: 2048-bit RSA with SHA-256 signature.
2. This demonstrates how cloud microservices authenticate each other in-transit to prevent Man-in-the-Middle (MitM) eavesdropping.

### 🔹 Task 4: Remediate Security Posture Findings
1. Look at the **Cloud Security Posture Matrix (CSPM)**:
   - Notice the baseline score: **100% Compliant**.
2. Click on **"S3 Storage Server-Side Encryption"** or **"Restricted Ingress Ports"** to simulate a security misconfiguration (toggle to `Non-Compliant`):
   - Notice the compliance score immediately drops to **75%**.
3. Toggle it back to simulate a cloud engineer applying a security patch and restoring 100% compliance.

---

## 💻 5. Terminal CLI Verification

Test KMS envelope encryption directly via curl:

```bash
# 1. Inspect KMS service status and compliance score
curl -s http://localhost:8080/api/status | python3 -m json.tool

# 2. Inspect X.509 certificate and fingerprint
curl -s http://localhost:8080/api/certificate | python3 -m json.tool

# 3. Encrypt a payload via API
curl -s -X POST http://localhost:8080/api/envelope/encrypt \
  -H "Content-Type: application/json" \
  -d '{"plaintext": "Secret Database Password: MySecurePassword123!", "label": "DB Credentials"}' | python3 -m json.tool
```

---

## 🧠 6. Viva & Interview Questions

1. **What is Envelope Encryption, and why is it used in AWS KMS and Google Cloud KMS?**
   - Envelope encryption encrypts plaintext data with a unique Data Encryption Key (DEK), and then encrypts the DEK with a root Key Encryption Key (KEK). It is used because KMS has a 4 KB payload limit and transferring massive files over the network to KMS would cause severe latency and network bottlenecks.
2. **What does the "GCM" in AES-256-GCM provide that basic AES-CBC does not?**
   - Galois/Counter Mode (GCM) provides **Authenticated Encryption with Associated Data (AEAD)**. In addition to encrypting data, it generates a 128-bit authentication tag that guarantees the ciphertext has not been tampered with or modified by an attacker.
3. **What is Subject Alternative Name (SAN) in X.509 TLS certificates?**
   - SAN allows a single SSL/TLS certificate to secure multiple domain names, subdomains, and IP addresses (e.g. `api.example.com`, `auth.example.com`, `127.0.0.1`), replacing deprecated Common Name (CN) matching.

---

## 🧹 7. Teardown / Reclaiming Memory
```bash
docker compose down
```
