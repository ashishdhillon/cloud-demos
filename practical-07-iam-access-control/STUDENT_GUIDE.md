# 🎓 Student Lab Guide: Practical 07 — Identity & Access Management (IAM) & Least Privilege Simulator

---

## 📌 1. What is this practical about? (The Real-World Problem)

In cloud computing, a single leaked credential can destroy an entire company:
- If every developer has full `AdministratorAccess` (`"Action": "*", "Resource": "*"`), a junior developer who accidentally types `aws s3 rm s3://customer-backups --recursive` will delete everything permanently.
- Or if an attacker steals an API key via GitHub, they can spin up 500 cryptocurrency mining virtual machines, running up a $100,000 cloud bill overnight.

### The Cloud Solution: **The Principle of Least Privilege & AWS IAM Engine**
Cloud platforms use strict Identity & Access Management (IAM) policies:
1. **Default Deny:** Every user starts with zero permissions.
2. **Least Privilege:** Users only get the exact permissions they need to do their specific job (e.g., a DBA can access RDS databases, but cannot touch S3 buckets or delete VPCs).
3. **Explicit Deny Overrides Everything:** Even if 10 policies say `ALLOW`, a single `DENY` policy immediately blocks the request.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- No AWS account needed (includes an AWS-standard IAM evaluation engine).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-07-iam-access-control
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Test the "Junior Developer" Persona
1. Select Persona: **Junior Developer**.
2. Action: **`s3:GetObject`** on Resource: **`arn:aws:s3:::app-public-assets/*`**.
3. Click **"Evaluate IAM Authorization Request"**:
   - **Verdict:** `ALLOWED (200)`. Junior developers can read public application assets.
4. Now change the Action to **`s3:DeleteBucket`** or **`ec2:TerminateInstances`**:
   - Click **"Evaluate"**.
   - **Verdict:** `BLOCKED (403 Implicit Deny)`. The request is denied because no policy explicitly granted destruction permissions.

### 🔹 Task 2: Observe "Explicit Deny Overrides Allow"
1. Select Persona: **DevOps Engineer**.
2. Notice the DevOps persona has broad permissions: `ec2:*`, `s3:*`.
3. Try action **`ec2:TerminateInstances`** on **Production Server (`arn:aws:ec2:*:*:instance/i-prod-*`)**:
   - Click **"Evaluate"**.
   - **Verdict:** `BLOCKED (403 Explicit Deny)`!
   - Look at the **Evaluation Decision Tree**: Notice there is an explicit guardrail policy: `"DenyProductionTermination"`. Even though the DevOps policy allowed EC2 operations, the explicit Deny completely superseded it!

### 🔹 Task 3: Test Context Conditions (MFA Enforcement)
1. Select Persona: **Database Administrator (DBA)**.
2. Action: **`rds:DeleteDBInstance`**.
3. Toggle the **"Multi-Factor Authentication (MFA)"** switch:
   - When **MFA is OFF**: The request is **`BLOCKED (403 ConditionCheckFailed: aws:MultiFactorAuthPresent is false)`**.
   - When **MFA is ON**: The request is **`ALLOWED (200)`**.

---

## 💻 5. Terminal CLI Verification

Test IAM evaluations directly from your terminal:

```bash
# 1. Fetch available IAM personas and attached policies
curl -s http://localhost:8080/api/personas | python3 -m json.tool

# 2. Simulate an authorization request via API
curl -s -X POST http://localhost:8080/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "persona": "junior_dev",
    "action": "s3:GetObject",
    "resource": "arn:aws:s3:::app-public-assets/logo.png",
    "context": {"mfa_active": false}
  }' | python3 -m json.tool
```

---

## 🧠 6. Viva & Interview Questions

1. **What are the four components of an AWS IAM Policy statement?**
   - **Effect:** Either `Allow` or `Deny`.
   - **Action:** The API calls permitted or restricted (e.g., `s3:PutObject`, `ec2:StartInstances`).
   - **Resource:** The ARN (Amazon Resource Name) identifying the specific target resource.
   - **Condition:** Optional criteria (e.g., must come from corporate IP range, must have MFA enabled).
2. **What happens if a request matches both an Allow rule and a Deny rule in AWS IAM?**
   - **Explicit Deny always wins.** The request is denied immediately.
3. **What is an IAM Role and how does it differ from an IAM User?**
   - An *IAM User* has long-term credentials (password, access keys) and is tied to a specific person.
   - An *IAM Role* is assumed by an entity (like an EC2 instance, Lambda function, or federated user) to obtain temporary security credentials (valid for hours).

---

## 🧹 7. Teardown / Reclaiming Memory
```bash
docker compose down
```
