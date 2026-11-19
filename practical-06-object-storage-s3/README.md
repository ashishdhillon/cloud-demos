# Practical 06: Cloud Object Storage S3 & Expiring Presigned URLs

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Nginx](https://img.shields.io/badge/Nginx-1.27_Alpine-009639?logo=nginx&logoColor=white)](https://nginx.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 35 MB RAM), production-modeled **Cloud Object Storage (S3) Engine** featuring an interactive web explorer, granular Public/Private Access Control Lists (ACLs), and **cryptographic HMAC-SHA256 Expiring Presigned URLs** with live real-time countdown simulation.

This practical demonstrates the fundamental storage security architecture used by Amazon S3, Google Cloud Storage, and Azure Blob Storage to securely delegate temporary access to private assets without exposing backend credentials or proxying high-bandwidth file streams through application servers.

---

## 🏗️ Architecture & Security Model

```mermaid
sequenceDiagram
    autonumber
    actor Client as User / Browser
    participant Gateway as Nginx Reverse Proxy (:8080)
    participant S3Engine as S3 API Engine (:5000)
    participant Storage as Persistent Storage Volume

    Note over Client,Storage: Scenario A: Direct Access to Private Object (Forbidden)
    Client->>Gateway: GET /s3/secure-vault/invoice.pdf
    Gateway->>S3Engine: Check Object ACL
    S3Engine-->>Gateway: ACL is 'private' & no valid signature
    Gateway-->>Client: HTTP 403 Forbidden (XML AccessDenied)

    Note over Client,Storage: Scenario B: Authenticated Presigned URL Generation
    Client->>S3Engine: POST /api/buckets/secure-vault/objects/invoice.pdf/presign {expires_in: 30}
    S3Engine->>S3Engine: Calculate HMAC-SHA256(SecretKey, CanonicalString, Timestamp)
    S3Engine-->>Client: Return Signed URL with X-Amz-Expires=30

    Note over Client,Storage: Scenario C: Valid Time Window (Authorized)
    Client->>Gateway: GET /s3/secure-vault/invoice.pdf?X-Amz-Signature=... (within 30s)
    Gateway->>S3Engine: Verify Signature & Current Time < (Created + Expires)
    S3Engine->>Storage: Read file bytes
    Storage-->>Client: HTTP 200 OK (Stream File Payload)

    Note over Client,Storage: Scenario D: Post-Expiration Window (Expired)
    Client->>Gateway: GET /s3/secure-vault/invoice.pdf?X-Amz-Signature=... (at 31s)
    S3Engine->>S3Engine: Current Time > (Created + Expires)
    Gateway-->>Client: HTTP 403 Forbidden (XML RequestExpired)
```

---

## 📐 Mathematical Signature & Expiration Model

In AWS Signature Version 4 (SigV4), presigned URLs authenticate requests using query string parameters instead of HTTP headers:

### 1. Canonical String Construction
$$\text{CanonicalString} = \text{Bucket} \,\|\, \text{"/"} \,\|\, \text{Key} \,\|\, \text{":"} \,\|\, t_{\text{created}} \,\|\, \text{":"} \,\|\, \Delta t_{\text{expires}}$$

### 2. Cryptographic Digest Calculation
The signature is generated using keyed-hash message authentication code (HMAC) with SHA-256:
$$\text{Signature} = \text{HMAC-SHA256}\left(\text{SecretKey}, \text{CanonicalString}\right)$$

### 3. Server-Side Validation Rule
When an incoming request is evaluated at timestamp $t_{\text{now}}$:
1. **Integrity Check:** The server re-computes the expected HMAC signature using the local secret key and compares it in constant time (`hmac.compare_digest`). If signatures do not match $\rightarrow$ Return `403 SignatureDoesNotMatch`.
2. **Temporal Window Gate:**
   $$t_{\text{now}} \le t_{\text{created}} + \Delta t_{\text{expires}}$$
   If $t_{\text{now}} > t_{\text{created}} + \Delta t_{\text{expires}}$ $\rightarrow$ Return `403 RequestExpired`.

---

## ⚙️ Component Breakdown

| Component | Technology | Role & Function | Resource Usage |
| :--- | :--- | :--- | :---: |
| **Reverse Proxy & Host** | `nginx:1.27-alpine` | High-performance HTTP server serving the single-page application dashboard and proxying binary S3 object streams. | **~7 MiB** |
| **S3 Control & Data Plane** | Python 3.12 + Flask + Gunicorn | Manages bucket metadata, object writes, ACL state, HMAC-SHA256 signature verification, and real-time audit event logging. | **~26 MiB** |
| **Object Data Store** | Docker Volume (`./data`) | Emulated flat S3 namespace with multi-bucket isolation, automatic MD5/ETag calculation, and MIME type resolution. | Disk-only |
| **Interactive Dashboard** | Vanilla HTML5 / CSS3 / ES6 | Live bucket explorer, drag-and-drop file uploader, ACL toggles, and **live visual countdown timer**. | Client Browser |

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS / Windows / Linux) with Docker Compose v2.

### 2. Configure Environment
```bash
cd practical-06-object-storage-s3
cp .env.example .env
```

Default configuration:
```ini
HOST_PORT=8080
S3_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
S3_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### 3. Launch Stack
```bash
docker compose up --build -d
```

### 4. Verify Containers
```bash
docker compose ps
```
You should see:
* `practical-06-s3-backend` (Up on port 5000)
* `practical-06-nginx` (Up on port 8080)

---

## 🖥️ Interactive Testing & Demonstration Protocol

Open your browser at **[http://localhost:8080](http://localhost:8080)**.

### Step 1: Upload a Private Object
1. Select the `secure-vault` bucket on the left sidebar.
2. Drag and drop any test file (e.g., an image or text document) into the **Upload Object** drop zone.
3. Select **Private (Default, secure)** and click **PutObject to S3**.
4. The file appears in the objects table with a gold `🔒 Private` badge.

### Step 2: Test Direct Access (Observe AccessDenied)
1. Click the **Direct (403)** button next to your uploaded private object.
2. A new tab opens showing a standard AWS S3 XML error:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <Error>
       <Code>AccessDenied</Code>
       <Message>Access Denied. Object ACL is private...</Message>
       <Resource>/secure-vault/your-file.png</Resource>
   </Error>
   ```

### Step 3: Generate a 10-Second Presigned URL
1. Click the **Presign URL ⏳** button next to your private object.
2. Select **10 Seconds** and click **Generate Signed URL**.
3. An **Active Presigned URL Authorization Monitor** banner appears at the top:
   * A pulsing green indicator and a real-time countdown timer (`10s remaining... 9s... 8s...`).
   * The generated URL is displayed with HMAC parameters.
4. Click **Test Presigned Link ↗** while the timer is green:
   * The file **downloads or renders successfully** (`200 OK`).

### Step 4: Observe Expiration in Real-Time
1. Wait for the countdown timer to hit `0s`.
2. Notice the monitor changes:
   * The banner shifts from emerald to crimson.
   * The countdown turns to **`EXPIRED (0s)`**.
   * The button updates to **`Test Expired Link (403) ↗`**.
3. Click the expired link:
   * S3 immediately rejects the request with a genuine expired error:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <Error>
       <Code>RequestExpired</Code>
       <Message>Request has expired. URL was valid for 10s and expired 3s ago.</Message>
   </Error>
   ```

---

## 🧪 CLI-Driven Validation

You can verify the entire S3 workflow directly from your command line:

```bash
# 1. Upload a private object via curl
echo "Confidential cloud data payload" > confidential.txt
curl -F "file=@confidential.txt" -F "acl=private" http://localhost:8080/api/buckets/secure-vault/objects

# 2. Attempt direct download without signature (Expect 403 Forbidden)
curl -i http://localhost:8080/s3/secure-vault/confidential.txt

# 3. Request a 15-second presigned URL
PRESIGNED_URL=$(curl -s -X POST http://localhost:8080/api/buckets/secure-vault/objects/confidential.txt/presign \
  -H "Content-Type: application/json" \
  -d '{"expires_in": 15}' | python3 -c "import sys, json; print(json.load(sys.stdin)['url'])")

echo "Generated Signed URL: $PRESIGNED_URL"

# 4. Access immediately via presigned URL (Expect 200 OK)
curl -i "http://localhost:8080${PRESIGNED_URL}"

# 5. Wait 16 seconds and access again (Expect 403 RequestExpired)
sleep 16
curl -i "http://localhost:8080${PRESIGNED_URL}"
```

---

## 📊 Measured Resource Consumption

Inspected via `docker stats --no-stream` under live operation:

| Container | Memory Usage | Memory % | Idle CPU |
| :--- | :---: | :---: | :---: |
| `practical-06-nginx` | **7.4 MiB** | 0.19% | 0.00% |
| `practical-06-s3-backend` | **25.8 MiB** | 0.67% | 0.25% |
| **Total Stack** | **~33.2 MiB** | **0.86%** | **~0.25%** |

---

## 🛠️ Teardown

To stop the containers and free system resources:
```bash
docker compose down
```
