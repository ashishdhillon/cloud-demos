# 🎓 Student Lab Guide: Practical 14 — Multi-Cloud Infrastructure as Code (Terraform)

---

## 📌 1. What is this practical about? (The Real-World Problem)

In traditional IT operations, system administrators configured servers, networks, and databases manually by clicking around in web consoles—a practice engineers call **"ClickOps"**.

### Why ClickOps Fails in Production:
1. **Human Error:** Forgetting to check a firewall checkbox or misconfiguring an S3 bucket ACL can cause massive security breaches.
2. **Zero Audit Trail:** Who changed that security group rule at 2:00 AM? Nobody knows.
3. **Configuration Drift:** When production environments drift away from documentation, disaster recovery and replication become impossible.

### The Cloud Solution: **Infrastructure as Code (IaC) with HashiCorp Terraform**
Terraform allows DevOps teams to define cloud infrastructure using **HashiCorp Configuration Language (HCL)**. 
- **Declarative Approach:** You describe *what* the infrastructure should look like (the desired state), not the imperative step-by-step shell commands to create it.
- **Provider Ecosystem:** Terraform talks to multiple cloud providers (AWS, Google Cloud, Azure, Docker, Kubernetes) through a unified workflow.
- **State Management (`terraform.tfstate`):** Terraform tracks the real-world state of your cloud resources in a cryptographic state file, enabling it to compute deterministic execution plans (`terraform plan`) and automatically detect and fix **Cloud Drift**.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- Zero paid cloud accounts required (this practical includes a built-in multi-cloud provider simulator executing real HCL parsing and state reconciliation).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-14-multicloud-terraform
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Initialize Providers & Generate Execution Plan
1. Look at the left pane: **`main.tf` (HashiCorp Configuration Language)**.
   - Note the multi-cloud resource declarations: AWS S3 Bucket, AWS EC2 Security Group, Google Cloud Storage, and Docker Container.
2. In the top toolbar, click **`terraform init`**:
   - Observe the initialization output: Terraform downloads and locks the AWS, Google Cloud, and Docker provider plugins.
3. Click **`terraform plan`**:
   - Inspect the generated execution plan in the console:
   - Notice the green `+ create` symbols for all 4 resources:
     `Plan: 4 to add, 0 to change, 0 to destroy.`
   - Notice that at this stage, **zero real cloud resources have been modified**. Terraform guarantees safety by letting you review plans first.

### 🔹 Task 2: Apply the Plan & Inspect `terraform.tfstate`
1. Click **`terraform apply`**:
   - Watch the **Live Cloud Infrastructure Topology** populate in real time across AWS, GCP, and Docker.
   - Observe the **Resource Summary**: 4 Active Resources, zero drift.
2. Scroll to the bottom pane: **`terraform.tfstate` (State File)**:
   - Inspect the JSON state metadata: `serial`, `lineage`, resource IDs, and provider attributes.
   - This state file acts as the single source of truth connecting your code to physical cloud assets.

### 🔹 Task 3: Simulate "ClickOps" Cloud Drift & Automatic Reconciliation
1. In the top action bar, click **`⚡ Trigger Cloud Drift (ClickOps)`**:
   - This simulates a rogue admin or attacker who logged into the AWS Web Console and manually changed the S3 bucket ACL from `private` to `public-read`, and altered GCP compute labels.
   - Notice the UI immediately flags **Cloud Drift Detected!**
2. Click **`terraform plan`**:
   - Terraform compares the live cloud state against your `main.tf` code.
   - Notice the output: Terraform detects the unauthorized change:
     `~ aws_s3_bucket.app_storage: acl "public-read" => "private"`
     `Plan: 0 to add, 1 to change, 0 to destroy.`
3. Click **`terraform apply`**:
   - Terraform automatically overwrites the rogue changes and reconciles the cloud back to your version-controlled code!

### 🔹 Task 4: Infrastructure Teardown (`terraform destroy`)
1. Click **`terraform destroy`**:
   - Terraform generates a destruction plan (`- destroy`) and safely deprovisions all multi-cloud resources in reverse dependency order.
   - Notice the topology clears and `terraform.tfstate` resources list empties out cleanly.

---

## 💻 5. Terminal CLI Verification

You can also interact directly with the backend API using `curl` from your terminal:

```bash
# 1. Check service health
curl -s http://localhost:8080/health

# 2. View current Terraform status and provisioned resources
curl -s http://localhost:8080/api/status | jq .

# 3. Run Terraform Plan
curl -s -X POST http://localhost:8080/api/plan | jq .

# 4. Run Terraform Apply
curl -s -X POST http://localhost:8080/api/apply | jq .

# 5. Simulate unauthorized Cloud Drift
curl -s -X POST http://localhost:8080/api/drift | jq .

# 6. Destroy all infrastructure
curl -s -X POST http://localhost:8080/api/destroy | jq .
```

---

## 🎯 6. Viva & Job Interview Questions & Answers

### Q1: What is the difference between Declarative and Imperative Infrastructure as Code?
> **Answer:** 
> - **Imperative (e.g. Bash scripts, AWS CLI commands):** You specify the exact sequence of steps to reach a state (e.g. `create bucket`, `set acl`, `wait`). If run twice, it often errors or duplicates resources.
> - **Declarative (e.g. Terraform HCL, Kubernetes YAML):** You specify the desired end state (e.g. `acl = "private"`). The IaC engine figures out what differences exist between the current state and the target state and applies only the required delta. It is inherently **idempotent**.

### Q2: What is the purpose of `terraform.tfstate` and why is it dangerous to commit to Git?
> **Answer:**
> The `terraform.tfstate` file maps your declarative HCL configuration to real-world cloud resource IDs and attributes. Committing it to Git is a severe anti-pattern because:
> 1. It may contain plaintext secrets, passwords, and private keys generated during provisioning.
> 2. Concurrent team applies without state locking can cause race conditions and state corruption. In production, teams use **remote backends with state locking** (e.g. AWS S3 + DynamoDB or Terraform Cloud).

### Q3: What is "Configuration Drift" and how does Terraform resolve it?
> **Answer:**
> Configuration drift occurs when cloud resources are modified outside of Terraform (via the AWS Web Console, manual CLI commands, or emergency hotfixes). During `terraform plan` or `terraform refresh`, Terraform queries the actual cloud APIs, compares the live reality against the desired code, highlights the discrepancies, and generates an update plan to reconcile the live environment back to code.

### Q4: What are Terraform Providers?
> **Answer:**
> Providers are plugins that translate Terraform's generic HCL resource blocks into vendor-specific REST API calls (e.g. AWS SDK, Google Cloud Client Library, Docker Engine API). This decoupled architecture allows Terraform to support hundreds of disparate cloud platforms and SaaS tools.

---

## 🛑 7. Clean Teardown
When you are done with the lab, run:
```bash
docker compose down
```
This frees host port `8080` and leaves zero residual containers running.
