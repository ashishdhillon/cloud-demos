# 🎓 Student Lab Guide: Practical 06 — Cloud Object Storage (S3), Presigned URLs & ACLs

---

## 📌 1. What is this practical about? (The Real-World Problem)

Imagine you are building a healthcare app or mobile banking app:
- A user wants to view their medical blood test report (a private PDF document).
- If you make the storage bucket public, **anyone with the link can steal confidential patient data**.
- But if you keep the bucket completely private, **how does the patient's phone download the PDF directly from cloud storage without routing heavy video/PDF megabytes through your web server?**

### The Cloud Solution: **S3 Presigned URLs**
Cloud Object Storage (AWS S3, Google Cloud Storage, MinIO) solves this using **Presigned URLs**:
1. Your backend keeps the bucket **Private**.
2. When an authenticated user requests a file, your backend generates a cryptographic **HMAC-SHA256 presigned URL** valid for a short window (e.g., 30 seconds or 5 minutes).
3. The patient downloads the file directly from S3 using the signed URL.
4. Once the expiration timestamp passes, S3 immediately rejects any further downloads with `403 Forbidden (RequestExpired)`.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- Zero paid cloud accounts required (local S3 engine runs on your machine).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-06-object-storage-s3
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Create an S3 Bucket & Understand Cloud Object Storage
1. In the **"Create New Bucket"** panel, enter a bucket name (e.g. `confidential-records`) and select Access Control: **Private**.
2. Click **"Create Bucket"**.
3. Notice how Object Storage differs from a traditional filesystem: there are no block devices or POSIX file locks; everything is flat and identified by a unique `Bucket + Key`.

### 🔹 Task 2: Upload Files with Different ACLs
1. Select your bucket and upload two files (or click **"Add Sample Medical Report"** and **"Add Sample Public Banner"**).
2. Set the Medical Report to **`private`** ACL.
3. Set the Banner to **`public-read`** ACL.
4. Try to click the direct URL of the private file:
   - Notice you receive a **`403 Forbidden`** error! Cloud storage strictly protects private objects.
5. Click the direct URL of the public file:
   - It opens immediately because public-read allows unauthenticated HTTP GET.

### 🔹 Task 3: Generate a Time-Limited Presigned URL
1. Select the private file, set the TTL slider to **`15 Seconds`**, and click **"Generate Presigned URL"**.
2. Look at the generated URL:
   - Notice the query parameters: `AWSAccessKeyId`, `Signature` (cryptographic HMAC-SHA256 digest), and `Expires` (UNIX epoch timestamp).
3. Click the generated link immediately:
   - **Result:** The private file downloads/opens successfully because the signature is mathematically valid!
4. Watch the live **Expiration Countdown Timer**:
   - `15s... 10s... 5s... EXPIRED! 🔴`
5. Click the exact same link again after it expires:
   - **Result:** **`403 Forbidden - RequestExpired`**! The cloud storage engine rejects the expired timestamp.

---

## 💻 5. Terminal CLI Verification

Test S3 operations directly from your command line:

```bash
# 1. List all S3 buckets
curl -s http://localhost:8080/api/buckets | python3 -m json.tool

# 2. Upload an object via curl
curl -s -X POST http://localhost:8080/api/buckets/confidential-records/upload \
  -F "file=@README.md" \
  -F "acl=private"

# 3. Generate a 20-second presigned URL
curl -s -X POST http://localhost:8080/api/presign \
  -H "Content-Type: application/json" \
  -d '{"bucket": "confidential-records", "key": "README.md", "expires_in": 20}'
```

---

## 🧠 6. Viva & Interview Questions

1. **What is the difference between Block Storage (EBS), File Storage (EFS), and Object Storage (S3)?**
   - *Block Storage:* Virtual hard drives attached to one VM (databases, OS boot drives).
   - *File Storage:* Shared network filesystems (NFS) mounted by multiple VMs concurrently.
   - *Object Storage:* Massive scale, internet-accessible REST API storage for unstructured files (images, backups, videos) with unlimited scale.
2. **Why do presigned URLs use HMAC-SHA256 signatures?**
   - HMAC signatures allow the cloud storage service to verify that the request parameters (bucket, key, expiration time) were signed by someone possessing the Secret Access Key, without ever transmitting the secret key over the network.
3. **Can an attacker change the expiration time in a presigned URL to make it last longer?**
   - No! If an attacker modifies even a single character in the `Expires` query parameter, the HMAC signature hash becomes invalid, and the request is immediately rejected with `SignatureDoesNotMatch`.

---

## 🧹 7. Teardown / Reclaiming Memory
```bash
docker compose down
```
