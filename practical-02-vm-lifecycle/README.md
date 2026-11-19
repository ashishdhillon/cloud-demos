# Practical 02: Virtual Machine Deployment & Lifecycle Management

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Hypervisor](https://img.shields.io/badge/Hypervisor-KVM_%2F_QEMU-0284C7.svg?logo=linux&logoColor=white)](https://www.linux-kvm.org/)
[![Cloud-Init](https://img.shields.io/badge/Bootstrap-Cloud--Init_v24.1-38BDF8.svg)](https://cloud-init.io/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 35 MB RAM) **Virtual Machine Deployment & Hypervisor Lifecycle Management Simulator** modeling Type-1 bare-metal hypervisor architectures (Linux KVM / QEMU / AWS Nitro), automated declarative `cloud-init` bootstrapping, ACPI lifecycle state machines (Start, Stop, Suspend, Resume, Reboot), dynamic hardware sizing, and interactive in-guest serial console execution.

> **👨‍🎓 For Students & Educators:** Read the [**`STUDENT_GUIDE.md`**](STUDENT_GUIDE.md) for a beginner-friendly explanation of hardware virtualization vs containerization, step-by-step interactive lab exercises, and viva/interview prep questions.

---

## 🏗️ Core Architectural Concepts

```
┌────────────────────────────────────────────────────────────────────────┐
│             Bare-Metal Physical Server (AMD EPYC Silicon)              │
│       [16 Physical Cores] ── [64 GB DDR5 ECC] ── [2 TB NVMe Pool]      │
├────────────────────────────────────────────────────────────────────────┤
│             Type-1 Hypervisor (Linux KVM Kernel / QEMU VMM)            │
│  ┌───────────────────────┐                  ┌───────────────────────┐  │
│  │ Virtual Machine 01    │                  │ Virtual Machine 02    │  │
│  │ Name: cloud-vm-01     │                  │ Name: cloud-worker-02 │  │
│  │ - 2 vCPUs             │                  │ - 4 vCPUs             │  │
│  │ - 2048 MB vRAM        │                  │ - 4096 MB vRAM        │  │
│  │ - IP: 192.168.122.45  │                  │ - IP: 192.168.122.88  │  │
│  │                       │                  │                       │  │
│  │ ┌───────────────────┐ │                  │ ┌───────────────────┐ │  │
│  │ │ Guest OS: Ubuntu  │ │                  │ │ Guest OS: Ubuntu  │ │  │
│  │ │ Kernel 6.8.0      │ │                  │ │ Kernel 6.8.0      │ │  │
│  │ │ - Nginx Web Svc   │ │                  │ │ - PostgreSQL Svc  │ │  │
│  │ └───────────────────┘ │                  │ └───────────────────┘ │  │
│  └───────────────────────┘                  └───────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Type-1 Bare-Metal Hypervisor Architecture
- Operates directly at Ring -1 on hardware without an intervening desktop operating system.
- Enforces strict hardware quotas per virtual domain (vCPUs, vRAM, virtual block storage).

### 2. Automated Bootstrapping (`cloud-init`)
- Decouples base OS disk images from workload configuration.
- Executes declaratively on first boot: injects user accounts, SSH keys, installs packages, and writes custom application payloads.

### 3. ACPI Lifecycle State Machine
- **Running**: Active vCPU instruction scheduling and RAM consumption.
- **Suspended**: Freezes vCPU cycles; dumps state to RAM/checkpoint snapshot with zero boot delay upon resumption.
- **Stopped**: Clean ACPI shutdown; unmounts virtual block devices and deallocates all host memory.
- **Dynamic Resize**: Scale vCPUs and RAM on demand, modeling true cloud elasticity.

---

## 🚀 Quickstart & Execution

### 1. Launch the Stack
```bash
cd practical-02-vm-lifecycle
cp .env.example .env
docker compose up --build -d
```

### 2. Verify Endpoints
```bash
# Check service health
curl -s http://localhost:8080/health | python3 -m json.tool

# Query Hypervisor host specs and active VMs
curl -s http://localhost:8080/api/status | python3 -m json.tool
```

### 3. Open Web Dashboard
Navigate to `http://localhost:8080` in your web browser.

---

## 🛑 Clean Teardown
```bash
docker compose down
```
Frees host port `8080` and leaves zero lingering processes.
