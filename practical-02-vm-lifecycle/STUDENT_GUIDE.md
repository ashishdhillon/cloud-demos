# 🎓 Student Lab Guide: Practical 02 — Virtual Machine Deployment & Lifecycle Management

---

## 📌 1. What is this practical about? (The Real-World Problem)

At the foundation of cloud computing (IaaS) lies **Hardware Virtualization**. 

Before cloud computing, deploying a new application required purchasing physical 1U/2U rack servers, mounting them in a data center, cabling power and Ethernet, and manually installing an operating system—a process that took **weeks or months**.

### The Cloud Solution: **Hypervisors & Virtual Machine Lifecycles**
A **Hypervisor** (Virtual Machine Monitor / VMM) is software or firmware that pools physical silicon (CPUs, ECC RAM, NVMe SSDs, NICs) and dynamically slices it into multiple isolated **Virtual Machines (VMs)**.
1. **Type-1 Hypervisor (Bare-Metal):** Runs directly on the physical server hardware with zero underlying host OS overhead (e.g. Linux KVM, VMware ESXi, AWS Nitro Hypervisor, Xen).
2. **Type-2 Hypervisor (Hosted):** Runs on top of a conventional operating system (e.g. Oracle VirtualBox, VMware Workstation).
3. **Automated Bootstrapping with `cloud-init`:** When a VM boots for the first time, cloud providers inject a metadata script (`cloud-init.yaml`). It automatically sets up hostnames, user accounts, SSH authorized keys, installs packages, and starts web servers without requiring human keyboard intervention!

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- Zero local Multipass, VirtualBox, or QEMU installs required (includes a self-contained high-fidelity KVM Hypervisor emulation management studio).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-02-vm-lifecycle
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Inspect the Running Virtual Machine
1. Look at the left panel: **🖥️ Hypervisor Virtual Machine Fleet**.
2. Notice the pre-provisioned instance: **`cloud-vm-node-01`**:
   - Status: **`RUNNING`** (green badge).
   - Resources: **2 vCPUs**, **2048 MB RAM**, **20 GB Disk**.
   - Network: IP `192.168.122.45`, virtual MAC `52:54:00:...`.
3. Check the top metrics bar:
   - Notice that the Hypervisor has allocated 2 out of 16 physical host cores and 2.0 GiB of RAM.

### 🔹 Task 2: Interact with the In-Guest Virtual Serial Console
1. In the right panel, ensure the **🖥️ Guest Serial Console** tab is selected.
2. Click the quick command buttons:
   - Click **`lscpu`**: See the virtualized AMD EPYC CPU configuration exposed to the guest Linux kernel.
   - Click **`free -m`**: Inspect in-guest physical memory (2048 MB total, active memory, and buffers).
   - Click **`systemctl nginx`**: Observe that Nginx was automatically installed and started by `cloud-init`!
   - Click **`curl web`**: View the actual HTML web page rendered by the VM's web server.
3. You can also type custom Linux commands in the prompt (e.g., `ip addr`, `df -h`) and click **Run**.

### 🔹 Task 3: ACPI Lifecycle Transitions
1. On the `cloud-vm-node-01` card, click **`⏸ Suspend`**:
   - The hypervisor freezes vCPU execution cycles and preserves the guest's RAM state.
   - Status changes to **`SUSPENDED`** (yellow badge), and CPU utilization drops to `0.0%`.
2. Click **`⏯ Resume`**:
   - The VM resumes execution instantly without a reboot.
3. Click **`⏹ Stop`**:
   - The hypervisor sends an ACPI shutdown signal. In-guest processes terminate cleanly, and guest RAM is deallocated (`0 MB`).
4. Click **`▶ Start`**:
   - The hypervisor powers the VM back up, restoring services.

### 🔹 Task 4: Point-in-Time Snapshots & Dynamic Hardware Resizing
1. Click **`📸 Snapshot`** and enter a checkpoint name (e.g. `checkpoint-v1`).
   - The hypervisor records the differential disk layer and memory checkpoint.
2. Ensure the VM is **Stopped** (click `⏹ Stop`).
3. Click **`⚙ Resize Hardware`**:
   - Select **4 vCPUs** and **4096 MB (4.0 GB)** RAM.
   - Click **Apply Hardware Resize**.
4. Click **`▶ Start`** to power on the newly resized instance!
5. In the Guest Serial Console, click **`lscpu`** and **`free -m`**:
   - Observe that the guest kernel now detects **4 vCPUs** and **4096 MB RAM**—demonstrating true cloud elasticity!

---

## 💻 5. Terminal CLI Verification

You can interact directly with the Hypervisor Management Engine using `curl` from your terminal:

```bash
# 1. Check service health
curl -s http://localhost:8080/health | jq .

# 2. View Hypervisor host specs and provisioned VM instances
curl -s http://localhost:8080/api/status | jq .

# 3. Provision a new VM instance via API
curl -s -X POST http://localhost:8080/api/vm/provision \
  -H "Content-Type: application/json" \
  -d '{"name": "cloud-worker-node", "vcpus": 2, "memory_mb": 2048, "disk_gb": 40}' | jq .

# 4. Execute in-guest command on a VM
curl -s -X POST http://localhost:8080/api/vm/exec \
  -H "Content-Type: application/json" \
  -d '{"vm_id": "vm-8b39a1c2", "command": "lscpu"}' | jq .

# 5. Trigger ACPI Graceful Stop
curl -s -X POST http://localhost:8080/api/vm/action \
  -H "Content-Type: application/json" \
  -d '{"vm_id": "vm-8b39a1c2", "action": "stop"}' | jq .
```

---

## 🎯 6. Viva & Job Interview Questions & Answers

### Q1: What is the architectural difference between a Type-1 and Type-2 Hypervisor?
> **Answer:**
> - **Type-1 (Bare-Metal):** Runs directly on the physical server silicon without an intervening host operating system (e.g. Linux KVM, VMware ESXi, AWS Nitro). It delivers near-native performance, low latency, and is the foundation of all enterprise public clouds.
> - **Type-2 (Hosted):** Runs inside an existing consumer operating system like Windows or macOS (e.g. Oracle VirtualBox, VMware Workstation). It incurs higher virtualization overhead and is meant for local desktop development rather than production cloud infrastructure.

### Q2: How does a Virtual Machine differ fundamentally from a Docker Container?
> **Answer:**
> - **Virtual Machine:** Virtualizes the **hardware layer**. Each VM runs its own independent operating system kernel, device drivers, and init system. It provides strong hardware-level isolation, but requires significant RAM and takes 10–30 seconds to boot.
> - **Container:** Virtualizes the **operating system layer**. All containers share the single host Linux kernel and use Namespaces and Cgroups to isolate userland processes. Containers boot in milliseconds and consume megabytes rather than gigabytes.

### Q3: What is `cloud-init` and why is it essential in cloud operations?
> **Answer:**
> `cloud-init` is the standard multi-distribution package for automating early cloud instance initialization. Without `cloud-init`, deploying 500 EC2 instances would require manual SSH logins to configure hostnames, passwords, and packages. With `cloud-init`, users provide a declarative `#cloud-config` YAML file during API provisioning; the VM automatically executes it on first boot.

### Q4: What is the difference between Suspending (Pausing) and Stopping a VM?
> **Answer:**
> - **Suspending (Pause):** Freezes CPU execution cycles and dumps or holds the active guest RAM state in memory/disk. When resumed, execution picks up at the exact instruction clock cycle with zero reboot.
> - **Stopping:** Delivers an ACPI shutdown signal. The guest OS cleanly terminates processes, flushes disk buffers, unmounts filesystems, and completely frees all host CPU and RAM allocations.

---

## 🛑 7. Clean Teardown
When you are done with the lab, run:
```bash
docker compose down
```
This frees host port `8080` and leaves zero lingering processes.
