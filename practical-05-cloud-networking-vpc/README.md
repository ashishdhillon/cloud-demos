# Practical 05: Cloud Networking Fundamentals & VPC Topology Simulator

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-VPC_Networking-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/vpc/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 35 MB RAM) **Amazon Virtual Private Cloud (VPC) & Packet Routing Topology Simulator** demonstrating dual-tier public/private subnet isolation, Internet & NAT Gateways, route table resolution, Network ACLs, and stateful Security Group rule evaluation.

---

## 🏗️ Core Cloud Networking Architecture

### 1. CIDR Block Segmentation
- **VPC (`10.0.0.0/16`)**: Defines an isolated virtual private network within the cloud provider with $2^{16} = 65,536$ private IP addresses.
- **Public Subnet (`10.0.1.0/24`, `us-east-1a`)**: Designated for internet-facing resources (web servers, load balancers, NAT gateways).
- **Private Subnet (`10.0.2.0/24`, `us-east-1b`)**: Completely isolated from direct internet ingress, reserved for sensitive databases and internal compute.

### 2. Cloud Reserved IP Addresses (RFC 1918)
In every AWS `/24` subnet (256 theoretical addresses), **5 addresses are strictly reserved** by the cloud infrastructure:
1. `10.0.X.0` &rarr; **Network Address** (Subnet base identifier).
2. `10.0.X.1` &rarr; **VPC Router Gateway**.
3. `10.0.X.2` &rarr; **Amazon DNS Resolver** (Base + 2).
4. `10.0.X.3` &rarr; **Future Cloud Provider Reservation**.
5. `10.0.X.255` &rarr; **Network Broadcast Address**.
- **Usable Host Addresses**: $256 - 5 = 251$ IPs per subnet.

### 3. Gateway Architecture: IGW vs. NAT Gateway
- **Internet Gateway (IGW)**: Horizontally scaled, redundant VPC component enabling two-way (ingress and egress) internet communication for public subnets (`0.0.0.0/0` &rarr; `igw`).
- **NAT Gateway**: Resides in the public subnet with an allocated **Elastic IP (EIP)** (`54.210.12.89`). Allows private instances to initiate outbound connections (e.g. security patches) via Source Network Address Translation (**SNAT**) while preventing internet hosts from initiating inbound connections.

### 4. Defense-in-Depth: Security Groups vs. Network ACLs
| Attribute | Security Groups (SG) | Network ACLs (NACL) |
|:---|:---|:---|
| **Boundary** | Instance Network Interface (ENI) | Subnet Boundary |
| **State Tracking** | **Stateful**: Return traffic automatically permitted | **Stateless**: Inbound and outbound rules evaluated separately |
| **Rule Processing** | All rules evaluated before decision | Evaluated sequentially in ascending rule order (100, 110...) |
| **Action Types** | Permit rules only (**Implicit Deny**) | Explicit **ALLOW** and **DENY** rules |

---

## 🚀 Quickstart & Sequential Execution

### 1. Launch the Simulator
```bash
cd practical-05-cloud-networking-vpc
cp .env.example .env
docker compose up --build -d
```

### 2. Verify Cloud Endpoints
```bash
# Verify health probe
curl -s http://localhost:8080/health | python3 -m json.tool

# Inspect VPC topology metadata
curl -s http://localhost:8080/api/topology | python3 -m json.tool

# AWS EC2 API mock endpoints
curl -s http://localhost:8080/api/vpcs | python3 -m json.tool
curl -s http://localhost:8080/api/subnets | python3 -m json.tool
curl -s http://localhost:8080/api/route-tables | python3 -m json.tool
```

### 3. Trace a Packet via CLI
```bash
# Scenario A: External client to Public Web Server on Port 80 (Allowed)
curl -s -X POST http://localhost:8080/api/packet/simulate \
  -H "Content-Type: application/json" \
  -d '{"source_ip": "203.0.113.50", "dest_ip": "52.90.14.22", "port": 80, "protocol": "TCP"}' | python3 -m json.tool

# Scenario B: External client attempting direct connection to Private DB (Dropped)
curl -s -X POST http://localhost:8080/api/packet/simulate \
  -H "Content-Type: application/json" \
  -d '{"source_ip": "203.0.113.50", "dest_ip": "10.0.2.80", "port": 5432, "protocol": "TCP"}' | python3 -m json.tool
```

### 4. Interactive Web Dashboard
Open **[http://localhost:8080](http://localhost:8080)** in your browser to:
- Visually explore the interactive **VPC & Subnet Topology Map**.
- Run automated packet routing scenarios and inspect hop-by-hop decisions.
- Toggle Security Group rules (e.g. deny HTTP port 80 or enable SSH port 22) and witness instantaneous firewall enforcement.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|:---|:---:|:---|
| `/health` | `GET` | Microservice health status |
| `/api/topology` | `GET` | Complete VPC, subnet, gateway, and route table structure |
| `/api/packet/simulate` | `POST` | Simulates a packet crossing gateways, route tables, and firewalls |
| `/api/security-groups/toggle` | `POST` | Toggles an ingress rule in a security group |
| `/api/vpcs` | `GET` | AWS EC2 mock endpoint (`DescribeVpcs`) |
| `/api/subnets` | `GET` | AWS EC2 mock endpoint (`DescribeSubnets`) |
| `/api/route-tables` | `GET` | AWS EC2 mock endpoint (`DescribeRouteTables`) |

---

## 🧹 Teardown & RAM Reclamation
```bash
docker compose down
```
Instantly stops and removes all containers, networks, and reclaims memory.
