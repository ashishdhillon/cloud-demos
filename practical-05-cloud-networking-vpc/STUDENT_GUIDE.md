# 🎓 Student Lab Guide: Practical 05 — Cloud Networking & VPC Architecture

---

## 📌 1. What is this practical about? (The Real-World Problem)

When a company deploys an application in AWS or Google Cloud:
- You have a **Public Web Server** that users on the internet must be able to visit over port 80/443.
- You also have a **Database Server** holding customer credit cards and passwords.
- **Critical Security Rule:** Your database must **NEVER** have a public IP address or be directly reachable from the open internet!

### The Cloud Solution: **Amazon Virtual Private Cloud (VPC)**
You create a custom software-defined network (VPC) segmented into:
1. **Public Subnet (`10.0.1.0/24`):** Connected to an **Internet Gateway (IGW)** so web servers can talk to public users.
2. **Private Subnet (`10.0.2.0/24`):** Isolated with no direct public route. The database sits here safely.
3. **NAT Gateway:** Sits in the public subnet to allow private databases to download outbound security updates without allowing inbound connections.
4. **Stateful Security Groups:** Virtual firewalls attached to each instance.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- Zero AWS account required.

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-05-cloud-networking-vpc
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Trace Inbound Web Traffic (Public Subnet)
1. In the **Packet Tracer Console**, click **"Scenario A: Public HTTP (Port 80)"**.
2. Click **"Transmit Packet & Trace Route"**.
3. Watch the hop-by-hop packet inspection timeline:
   - **Hop 1 (IGW):** External packet crosses Internet Gateway &rarr; `PASS`.
   - **Hop 2 (Route Table):** Matches Public Route Table (`rtb-pub-01`) &rarr; `PASS`.
   - **Hop 3 (NACL):** Stateless subnet rule 100 permits TCP port 80 &rarr; `PASS`.
   - **Hop 4 (Security Group):** `sg-web-public` allows HTTP &rarr; `PASS`.
   - **Verdict:** `ALLOWED (200 OK)`.

### 🔹 Task 2: Observe Private Subnet Protection (Direct DB Probe)
1. Click **"Scenario B: Direct DB Ingress (Drop)"** (External client trying to connect directly to `10.0.2.80:5432`).
2. Click **"Transmit Packet"**:
   - Watch Hop 2 fail with **`BLOCKED (403 Forbidden)`**!
   - **Reason:** Destination `10.0.2.80` is in the isolated private subnet with no public routing or Elastic IP. The cloud router drops the packet at the perimeter!

### 🔹 Task 3: Test Security Group Firewall Rule Modification
1. Click **"Scenario C: External SSH Probe (Drop)"** (Port 22 on the Web Server).
2. Click **"Transmit Packet"**:
   - The packet reaches Hop 4, but is **`BLOCKED (403)`** by `sg-web-public` because SSH is restricted to internal VPN IPs.
3. Now, in the right panel under **`sg-web-public`**, find the **Admin VPN Bastion IP (Port 22)** rule and toggle it:
   - Notice how changing the firewall policy immediately affects subsequent packet traces in real-time.

### 🔹 Task 4: Trace Inter-Subnet Internal Routing
1. Click **"Scenario D: Web &rarr; DB Inter-Subnet"** (`10.0.1.15` &rarr; `10.0.2.80:5432`).
2. Click **"Transmit Packet"**:
   - **Verdict:** `ALLOWED (200 OK)`.
   - Notice that while external internet users cannot reach the database, the public web server CAN reach the database over the internal VPC backbone. This is the gold standard for secure cloud tiering!

---

## 💻 5. Terminal CLI Verification

Query VPC topology and trace packets using curl:

```bash
# 1. Inspect VPC configuration (AWS EC2 compatible mock)
curl -s http://localhost:8080/api/vpcs | python3 -m json.tool
curl -s http://localhost:8080/api/subnets | python3 -m json.tool

# 2. Trace a packet via API
curl -s -X POST http://localhost:8080/api/packet/simulate \
  -H "Content-Type: application/json" \
  -d '{"source_ip": "203.0.113.50", "dest_ip": "52.90.14.22", "port": 80, "protocol": "TCP"}' | python3 -m json.tool
```

---

## 🧠 6. Viva & Interview Questions

1. **Why are there only 251 usable IP addresses in an AWS `/24` subnet instead of 256?**
   - AWS reserves 5 IP addresses in every subnet:
     - `.0`: Network address.
     - `.1`: VPC Router gateway.
     - `.2`: Amazon DNS server.
     - `.3`: Future AWS reservation.
     - `.255`: Network broadcast address.
2. **What is the difference between an Internet Gateway (IGW) and a NAT Gateway?**
   - An *Internet Gateway* enables bidirectional (inbound and outbound) public traffic for public subnets.
   - A *NAT Gateway* provides outbound-only connectivity for private subnets (translating private IPs via SNAT) while blocking any inbound connections initiated from the internet.
3. **What is the difference between a Security Group (SG) and a Network ACL (NACL)?**
   - Security Groups operate at the *instance network interface (ENI)* level and are **stateful** (return traffic is automatically allowed).
   - Network ACLs operate at the *subnet boundary* and are **stateless** (both inbound and outbound rules must be explicitly defined).

---

## 🧹 7. Teardown / Reclaiming Memory
```bash
docker compose down
```
