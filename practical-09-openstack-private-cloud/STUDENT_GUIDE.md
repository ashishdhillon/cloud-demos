# 🎓 Student Lab Guide: Practical 09 — Private Cloud Architecture with OpenStack

---

## 📌 1. What is this practical about? (The Real-World Problem)

While public clouds like AWS, Azure, and Google Cloud are dominant, thousands of enterprises, defense agencies, telecom providers (5G/Telco Cloud), and research institutions cannot host their workloads in third-party public clouds due to:
1. **Data Sovereignty & Legal Jurisdiction:** Strict national laws requiring data to reside within physical country or company borders.
2. **Extreme Bandwidth Costs:** Transmitting petabytes of telemetry or financial feeds to public clouds creates massive egress bill shock.
3. **Hardware Predictability:** Need for bare-metal control, specialized accelerators, and deterministic latency.

### The Cloud Solution: **OpenStack Private Cloud Operating System**
**OpenStack** is the global standard open-source platform for deploying and operating private clouds. It pools bare-metal data center hardware and controls large pools of compute, storage, and networking resources through unified REST APIs:
- **Keystone (Identity Service v3):** Central authentication, role-based access control (RBAC), and dynamic service endpoint catalogs.
- **Nova (Compute Engine v2.1):** Orchestrates virtual machine instances, scheduling them across physical hypervisor worker nodes according to hardware **Flavors**.
- **Glance (Image Registry v2):** Stores and retrieves virtual machine disk templates (QCOW2, RAW, ISO).
- **Neutron (Software-Defined Networking v2.0):** Manages virtual switches, overlay networks (VXLAN/GENEVE), tenant private subnets, and **Floating IPs** for public internet ingress.
- **Cinder (Block Storage v3):** Provides persistent block storage volumes that can be attached and detached from running instances.
- **Horizon (Dashboard):** Web-based graphic user interface for administrators and tenant users.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- Zero massive DevStack or multi-node Kolla-Ansible setup required (includes a self-contained OpenStack Core REST API engine).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-09-openstack-private-cloud
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Multi-Tenant Project Isolation
1. In the top-right header, find the **Active Tenant / Project** dropdown.
2. Select **`Production-Core`**:
   - Notice the instance `prod-app-server-01` running on private subnet `192.168.100.0/24`.
   - Observe the quota: 20 vCPUs, 64 GB RAM.
3. Switch to **`Dev-Staging`**:
   - Notice that `prod-app-server-01` disappears! Instead, you see `dev-ci-runner-01` isolated in subnet `10.0.10.0/24`.
   - The quota changes to: 8 vCPUs, 16 GB RAM.
   - This demonstrates **multi-tenancy**: complete tenant network and compute isolation within a single physical data center.

### 🔹 Task 2: Launch Compute Instance via Nova & Glance
1. Switch back to **`Production-Core`**.
2. Click **`➕ Launch Cloud Instance`**:
   - Name: `web-app-node-02`
   - Flavor: Select **`m1.small (1 vCPU, 2048 MB RAM, 20 GB Disk)`**.
   - Image: Select **`Ubuntu 24.04 LTS Noble Server CloudImage`**.
   - Check **"Assign Neutron Public Floating IP"**.
   - Click **`Launch Instance`**.
3. Watch Nova Compute provision the instance on a hypervisor node, allocate private IP `192.168.100.x`, and assign a public Floating IP (`203.0.113.x`).

### 🔹 Task 3: Neutron SDN & Floating IP Routing
1. Find any running instance in the table.
2. Click **`🌐 IP` (Toggle Floating IP)**:
   - Notice how Neutron SDN immediately disassociates or reassociates an external routable IP address from the tenant instance.
3. Click **`⏹ Stop`** to send an ACPI shutdown signal. The instance enters **`SHUTOFF`** status, freeing CPU cycles.
4. Click **`▶ Start`** to power the instance back online.

### 🔹 Task 4: OpenStack REST CLI Console
1. In the right panel, observe the **OpenStack Client Shell**.
2. Click the quick CLI buttons:
   - Click **`token issue`**: Simulates `openstack token issue`, authenticating to Keystone v3 and printing the cryptographic auth token.
   - Click **`server list`**: Queries Nova v2.1 to print formatted tables of active instances and their network mappings.
   - Click **`flavor list`**: Lists all hardware compute tiers (`m1.tiny` to `m1.large`).
   - Click **`image list`**: Queries Glance for registered cloud OS templates.
   - Click **`catalog list`**: Displays the active Keystone dynamic service catalog with all API endpoint URLs.

---

## 💻 5. Terminal CLI Verification

You can interact directly with the OpenStack REST APIs using `curl` from your terminal:

```bash
# 1. Health check
curl -s http://localhost:8080/health | jq .

# 2. Authenticate to Keystone v3 and obtain X-Subject-Token
curl -s -X POST http://localhost:8080/v3/auth/tokens \
  -H "Content-Type: application/json" \
  -d '{"auth": {"identity": {"password": {"user": {"name": "admin", "password": "SecretAdminPass123"}}}}}' | jq .

# 3. Query Nova Flavors
curl -s http://localhost:8080/v2.1/flavors | jq .

# 4. Query Glance Images
curl -s http://localhost:8080/v2.1/images | jq .

# 5. List Nova instances in Production-Core
curl -s "http://localhost:8080/v2.1/servers?project=proj-prod" | jq .

# 6. Execute OpenStack CLI simulation via API
curl -s -X POST http://localhost:8080/api/cli \
  -H "Content-Type: application/json" \
  -d '{"command": "openstack server list", "project_id": "proj-prod"}' | jq .
```

---

## 🎯 6. Viva & Job Interview Questions & Answers

### Q1: What is OpenStack and what is its primary use case?
> **Answer:**
> OpenStack is an open-source cloud computing infrastructure software platform (IaaS). It allows enterprises, universities, and service providers to transform pools of physical servers, storage arrays, and network switches in their private data centers into self-service, API-driven private clouds similar to AWS or Azure.

### Q2: What is the role of Keystone in an OpenStack cloud?
> **Answer:**
> **Keystone** is the centralized Identity, Authentication, and Service Catalog component:
> 1. It authenticates users via passwords or tokens and issues scoped tokens (**`X-Subject-Token`**).
> 2. It manages multi-tenant isolation through **Projects / Tenants** and Role-Based Access Control (RBAC).
> 3. It publishes the **Service Catalog**, which tells clients and services the exact REST endpoint URLs for Nova, Glance, Neutron, Cinder, and Swift across different regions.

### Q3: What is the difference between a Fixed IP and a Floating IP in OpenStack Neutron?
> **Answer:**
> - **Fixed IP:** A private IP address allocated automatically by Neutron from the tenant's internal subnet (e.g. `192.168.100.15`). It remains permanently bound to the virtual interface throughout its lifecycle, but is unreachable from outside the private cloud.
> - **Floating IP:** A routable public or external IP address (e.g. `203.0.113.45`) allocated from an external network pool. It can be dynamically assigned and re-assigned to any running instance using 1-to-1 NAT routing, allowing internet users to reach internal services.

### Q4: What are Nova Compute Flavors?
> **Answer:**
> A **Flavor** is an OpenStack virtual hardware template defining the virtual resources allocated to an instance: virtual CPUs (**vCPUs**), system memory (**RAM in MB**), and root disk space (**Disk in GB**) (e.g. `m1.small` = 1 vCPU, 2048 MB RAM, 20 GB disk).

---

## 🛑 7. Clean Teardown
When you are done with the lab, run:
```bash
docker compose down
```
This frees host port `8080` and leaves zero lingering processes.
