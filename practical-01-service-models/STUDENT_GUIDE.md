# 🎓 Student Lab Guide: Practical 01 — Cloud Service Models (IaaS vs PaaS vs SaaS)

---

## 📌 1. What is this practical about? (The Real-World Problem)

When a software engineer or startup founder wants to launch a website, they face a critical architectural decision:
- **Option 1 (IaaS - Infrastructure as a Service):** Rent a raw Linux virtual machine (like AWS EC2). You get full root access, but you have to configure firewalls, install security patches, and fix broken libraries yourself at 2:00 AM.
- **Option 2 (PaaS - Platform as a Service):** Use an application platform (like AWS Elastic Beanstalk or Vercel). You push your code via Git, and the cloud provider handles the OS, security patches, and auto-scaling automatically.
- **Option 3 (SaaS - Software as a Service):** Don't write custom software at all. Use ready-made software (like Google Workspace or Salesforce) accessible via web browser.

### The Cloud Solution: **The Cloud Shared Responsibility Model**
Published by NIST (SP 800-145), AWS, and Microsoft Azure, this model defines who is legally and operationally responsible for each of the 9 layers of the computer stack:
1. **On-Premises:** Customer owns 100% (from physical diesel generators to code).
2. **IaaS:** Provider manages physical hardware and hypervisor. Customer manages the OS, runtime, and app.
3. **PaaS:** Provider manages hardware, OS, and runtimes. Customer manages app code and data.
4. **SaaS:** Provider manages the entire software stack. Customer manages only user accounts and access.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- Zero paid cloud accounts needed (runs 100% locally and free).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-01-service-models
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Compare the 9-Layer Responsibility Stack
1. In the top section, click through the 4 model buttons:
   - **`On-Premises`**: Notice all 9 layers light up in **Orange (Customer Managed)**.
   - **`IaaS`**: The bottom 3 layers (Facilities, Hardware, Virtualization) turn **Blue (Cloud Provider Managed)**. The top 6 remain Orange.
   - **`PaaS`**: The bottom 6 layers turn **Blue**. Only Data, Applications, and IAM remain Orange.
   - **`SaaS`**: The bottom 8 layers turn **Blue**. Only IAM / User Access remains Orange.
2. Observe how higher tiers drastically reduce operational burden on developers.

### 🔹 Task 2: Provision an IaaS VM & Apply an OS Patch
1. Switch to the **🖥️ IaaS Workbench** tab.
2. Select OS: **Ubuntu 24.04 LTS**, 2 vCPU, 4 GB RAM, and click **"Provision IaaS Virtual Machine"**.
3. Inspect the newly provisioned VM in the list:
   - Notice the OS patch status: **`unpatched (Kernel updates required by customer)`**!
   - This demonstrates the IaaS responsibility rule: The cloud provider gives you the VM, but **YOU** must secure the operating system.
4. Click **"🔧 Run OS Security Patch (apt upgrade)"**:
   - The status updates to `patched_latest`. You have fulfilled your customer responsibility!

### 🔹 Task 3: Deploy a PaaS Application via Git
1. Switch to the **🚀 PaaS Workbench** tab.
2. Enter App Name: **`payment-service`**, Runtime: **`Node.js 20 LTS`**, Branch: `main`.
3. Click **"Deploy Application (PaaS)"**:
   - The PaaS engine automatically detects the language buildpack, compiles the app, and gives you a live HTTPS URL (`https://payment-service.cloud-paas.internal`).
   - Notice: **Zero OS patching required!** The cloud vendor manages the underlying Linux kernel and node runtime for you.
4. Click **"+1 Replica"** to see how PaaS handles horizontal scaling with zero infrastructure configuration.

### 🔹 Task 4: Provision a SaaS Multi-Tenant Workspace
1. Switch to the **🏢 SaaS Workbench** tab.
2. Enter Organization: **`Stark Industries`**, User Seats: `150`, Plan: **`Enterprise SaaS`**.
3. Click **"Provision SaaS Workspace"**:
   - Notice how instant the creation is: you didn't provision any VMs, install any databases, or write any code. The vendor provisions a logical tenant partition instantly.

---

## 💻 5. Terminal CLI Verification

Query the service models via the command line:

```bash
# 1. Fetch cloud architecture overview and NIST layers
curl -s http://localhost:8080/api/overview | python3 -m json.tool

# 2. Inspect active IaaS VMs, PaaS apps, and SaaS tenants
curl -s http://localhost:8080/api/state | python3 -m json.tool

# 3. Provision an IaaS VM via API
curl -s -X POST http://localhost:8080/api/iaas/provision \
  -H "Content-Type: application/json" \
  -d '{"os": "Debian 12 Bookworm", "vcpu": 4, "ram_gb": 8}' | python3 -m json.tool
```

---

## 🧠 6. Viva & Interview Questions

1. **What is the famous "Pizza as a Service" analogy for cloud service models?**
   - *On-Premises (Made at Home):* You buy the ingredients, roll the dough, heat your oven, serve at your dining table, and wash the dishes.
   - *IaaS (Take & Bake):* The grocery store provides the prepared pizza, but you must bake it in your oven and use your table.
   - *PaaS (Pizza Delivery):* The pizzeria bakes the pizza and delivers it to your door; you just provide the table and eat.
   - *SaaS (Dining at a Restaurant):* You sit at the restaurant; they provide the pizza, table, drinks, and clean up. You just eat and pay.
2. **If an AWS EC2 instance is hacked due to an unpatched Linux kernel vulnerability, who is responsible?**
   - **The Customer.** Under the IaaS Shared Responsibility Model, AWS is responsible for the security *OF* the cloud (physical servers, data centers), but the customer is responsible for security *IN* the cloud (operating system patches, firewalls, and passwords).
3. **What is Multi-Tenancy in SaaS architecture?**
   - Multi-tenancy is an architectural model where a single instance of a software application serves multiple distinct customer organizations (tenants), logically isolating each tenant's data while sharing physical compute resources for massive cost efficiency.

---

## 🧹 7. Teardown / Reclaiming Memory
```bash
docker compose down
```
