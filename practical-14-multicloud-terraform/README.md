# Practical 14: Multi-Cloud Infrastructure as Code (Terraform)

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![IaC](https://img.shields.io/badge/IaC-HashiCorp_Terraform-844FBA.svg?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Multi--Cloud](https://img.shields.io/badge/Cloud-AWS_%7C_GCP_%7C_Docker-FF9900.svg)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 45 MB RAM) **Multi-Cloud Infrastructure as Code (Terraform) Simulator** featuring real declarative HCL parsing, provider plugin initialization, deterministic dependency execution planning (`terraform plan`), atomic state convergence (`terraform apply`), and live **Cloud Drift Detection & Reconciliation**.

> **👨‍🎓 For Students & Educators:** Read the [**`STUDENT_GUIDE.md`**](STUDENT_GUIDE.md) for a beginner-friendly explanation of why tech companies forbid "ClickOps", step-by-step interactive lab exercises, and viva/interview prep questions.

---

## 🏗️ Core Architectural Concepts

### 1. HashiCorp Configuration Language (HCL) & Multi-Provider Architecture
Terraform abstracts heterogeneous cloud infrastructure under a unified declarative syntax:
- **`provider "aws"`**: Provisions AWS resources (e.g. S3 Buckets, VPC Security Groups).
- **`provider "google"`**: Provisions Google Cloud resources (e.g. Google Cloud Storage, Compute instances).
- **`provider "docker"`**: Provisions local or cloud container environments.

### 2. The Four Stages of the Terraform Lifecycle
```
[ main.tf Code ] ──> terraform init (Download Providers)
                        │
                        ▼
                     terraform plan (Calculate Delta against tfstate)
                        │
                        ▼
                     terraform apply (Reconcile Cloud to Desired State)
                        │
                        ▼
                     terraform destroy (Safely Tear Down in Reverse Order)
```

### 3. State Management & Cloud Drift Detection
- **Single Source of Truth (`terraform.tfstate`)**: Stores resource IDs, metadata, and state lineage.
- **Drift Detection**: When manual changes occur outside Terraform (via Web Consoles / "ClickOps"), running `terraform plan` queries live cloud provider APIs, exposes the unauthorized drift, and generates corrective updates to enforce the code's declared state.

---

## 🚀 Quickstart & Execution

### 1. Launch the Stack
```bash
cd practical-14-multicloud-terraform
cp .env.example .env
docker compose up --build -d
```

### 2. Verify Endpoints
```bash
# Check service health
curl -s http://localhost:8080/health | python3 -m json.tool

# Query current Terraform engine state
curl -s http://localhost:8080/api/status | python3 -m json.tool

# Run plan
curl -s -X POST http://localhost:8080/api/plan | python3 -m json.tool
```

### 3. Open Web Dashboard
Navigate to `http://localhost:8080` in your web browser.

---

## 🛑 Clean Teardown
```bash
docker compose down
```
Frees host port `8080` and leaves zero lingering processes.
