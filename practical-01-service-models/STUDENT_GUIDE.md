# 🎓 Student Lab Guide: Practical 01 — Cloud Service Models (IaaS vs PaaS vs SaaS)

---

## 📌 1. What is this practical about? (The Real-World Problem)

When a software engineer or startup founder wants to launch a website, they face a critical architectural decision:
- **Option 1 (IaaS - Infrastructure as a Service):** Rent a raw Linux virtual machine (like AWS EC2). You get full root access, but you have to configure firewalls, install security patches, and fix broken libraries yourself at 2:00 AM.
- **Option 2 (PaaS - Platform as a Service):** Use an application platform (like AWS Elastic Beanstalk or Vercel). You push your code via Git, and the cloud provider handles the OS, security patches, and auto-scaling automatically.
- **Option 3 (SaaS - Software as a Service):** Don't write custom software at all. Use ready-made software (like Google Workspace or Salesforce) accessible via web browser.

### The Cloud Solution: **The Cloud Shared Responsibility Model**
Published by NIST (SP 800-145), AWS, and Microsoft Azure, this model defines who is legally and operationally responsible for each layer of the computer stack:
1. **On-Premises:** Customer owns 100% (from physical diesel generators to code).
2. **IaaS:** Provider manages physical hardware and hypervisor. Customer manages the OS, runtime, and app.
3. **PaaS:** Provider manages hardware, OS, and runtimes. Customer manages app code and data.
4. **SaaS:** Provider manages the entire software stack. Customer manages only user accounts and data.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- Zero paid cloud accounts needed (runs 100% locally and free).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-01-service-models
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Compare the 9-Layer Responsibility Stack
1. In the top section, click through the 4 model buttons:
   - **`On-Premises`**: Notice all 9 layers light up in **Rose / Red (Customer Managed)**.
   - **`IaaS`**: The bottom 3 layers (Facilities, Hardware, Virtualization) turn **Cyan (Cloud Provider Managed)**. The top 6 remain Customer Managed.
   - **`PaaS`**: The bottom 6 layers turn **Cyan**. Only Data, Applications, and IAM remain Customer Managed.
   - **`SaaS`**: The bottom 8 layers turn **Cyan**. Only IAM / User Access and Customer Data remain Customer Managed.
2. Observe how higher tiers drastically reduce operational burden on developers.

### 🔹 Task 2: Toggle the "Pizza-as-a-Service" Analogy
1. In the top right of the matrix panel, click the **"🍕 Pizza Analogy"** button.
2. Notice how the technical layers transform into:
   - **On-Premises = Made at Home**: You provide dining table, drinks, gas/oven, fire, dough, sauce, cheese, and wash the dishes.
   - **IaaS = Take & Bake**: The pizzeria supplies prepared dough, sauce, and toppings. You take it home, bake it in your oven, and serve at your table.
   - **PaaS = Pizza Delivered**: The pizzeria bakes the pizza completely and delivers it hot. You just provide dining table & drinks.
   - **SaaS = Dining Out at Restaurant**: The restaurant provides everything! You just sit down, eat, and pay.

### 🔹 Task 3: IaaS Security Simulation (Kernel CVE & Patching)
1. Switch to the **🖥️ IaaS Workbench** tab.
2. Click **"⚠️ Simulate Kernel CVE"** on the virtual machine:
   - Notice the VM turns **RED** (`CRITICAL: CVE-2024-1086 Kernel Privilege Escalation Exploit Detected`).
   - This proves the key IaaS lesson: **In IaaS, the cloud provider does NOT patch your guest OS!** If an attacker exploits a Linux kernel CVE, your VM is compromised.
3. Click **"🔧 Run Security Patch (apt-get upgrade)"**:
   - The status resolves to `patched_latest`. You have fulfilled your customer responsibility!

### 🔹 Task 4: PaaS & SaaS Zero-OS Deployments
1. Switch to the **🚀 PaaS Workbench** tab.
2. Deploy an app (e.g. `analytics-api`) with runtime `Python 3.12` and click **"Deploy Application (PaaS)"**.
3. Click **"+1 Replica"** to scale horizontally.
4. Click **"🛡️ Vulnerability Immune Check"**:
   - Notice how PaaS shields you: host OS and container runtime security updates are applied automatically by the cloud provider.
5. Switch to the **🏢 SaaS Workbench** tab and provision a multi-tenant workspace to experience zero-infrastructure enterprise computing.

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
   - *PaaS (Pizza Delivered):* The pizzeria bakes the pizza and delivers it to your door; you just provide the table and drinks.
   - *SaaS (Dining Out):* You walk into a restaurant; the restaurant provides food, cooking, dining table, and clean up.

2. **Under IaaS, who is responsible for operating system security patches (e.g. Linux kernel updates)?**
   - The **Customer**. In IaaS, the provider's responsibility ends at the hypervisor. The guest OS and all software inside the VM are managed by the customer.

3. **Why do startups prefer PaaS or Serverless over IaaS despite slightly higher per-hour compute costs?**
   - Because PaaS virtually eliminates DevOps maintenance hours (~1.5 hrs/mo vs ~12 hrs/mo for IaaS), allowing small engineering teams to focus 100% of their time on shipping customer features instead of administering servers.

4. **What is the NIST standard defining cloud service models?**
   - **NIST Special Publication 800-145** (*The NIST Definition of Cloud Computing*).
