import ipaddress
import threading
import time

class VpcEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.vpc = {
            "vpc_id": "vpc-0a91f82e",
            "cidr_block": "10.0.0.0/16",
            "total_ips": 65536,
            "state": "available",
            "dns_support": True,
            "dns_hostnames": True
        }

        self.subnets = {
            "subnet-pub-01": {
                "subnet_id": "subnet-pub-01",
                "name": "Public-Web-Subnet-1a",
                "cidr_block": "10.0.1.0/24",
                "zone": "us-east-1a",
                "type": "public",
                "gateway_id": "igw-08fe4a11",
                "route_table_id": "rtb-pub-01",
                "total_ips": 256,
                "available_ips": 251,
                "reserved_ips": [
                    {"ip": "10.0.1.0", "purpose": "Network Address"},
                    {"ip": "10.0.1.1", "purpose": "VPC Router Gateway"},
                    {"ip": "10.0.1.2", "purpose": "Amazon DNS Resolver"},
                    {"ip": "10.0.1.3", "purpose": "Future AWS Reservation"},
                    {"ip": "10.0.1.255", "purpose": "Network Broadcast Address"}
                ]
            },
            "subnet-priv-02": {
                "subnet_id": "subnet-priv-02",
                "name": "Private-Database-Subnet-1b",
                "cidr_block": "10.0.2.0/24",
                "zone": "us-east-1b",
                "type": "private",
                "gateway_id": "nat-056a29bc",
                "route_table_id": "rtb-priv-02",
                "total_ips": 256,
                "available_ips": 251,
                "reserved_ips": [
                    {"ip": "10.0.2.0", "purpose": "Network Address"},
                    {"ip": "10.0.2.1", "purpose": "VPC Router Gateway"},
                    {"ip": "10.0.2.2", "purpose": "Amazon DNS Resolver"},
                    {"ip": "10.0.2.3", "purpose": "Future AWS Reservation"},
                    {"ip": "10.0.2.255", "purpose": "Network Broadcast Address"}
                ]
            }
        }

        self.gateways = {
            "igw-08fe4a11": {
                "gateway_id": "igw-08fe4a11",
                "type": "Internet Gateway",
                "state": "attached",
                "vpc_id": "vpc-0a91f82e",
                "public_egress": True
            },
            "nat-056a29bc": {
                "gateway_id": "nat-056a29bc",
                "type": "NAT Gateway",
                "subnet_id": "subnet-pub-01",
                "elastic_ip": "54.210.12.89",
                "state": "available",
                "active": True
            }
        }

        self.route_tables = {
            "rtb-pub-01": {
                "id": "rtb-pub-01",
                "name": "Public-Route-Table",
                "routes": [
                    {"destination": "10.0.0.0/16", "target": "local", "status": "active"},
                    {"destination": "0.0.0.0/0", "target": "igw-08fe4a11", "status": "active"}
                ]
            },
            "rtb-priv-02": {
                "id": "rtb-priv-02",
                "name": "Private-Route-Table",
                "routes": [
                    {"destination": "10.0.0.0/16", "target": "local", "status": "active"},
                    {"destination": "0.0.0.0/0", "target": "nat-056a29bc", "status": "active"}
                ]
            }
        }

        # Stateful Security Groups
        self.security_groups = {
            "sg-web-public": {
                "group_id": "sg-web-public",
                "name": "Web-Public-Security-Group",
                "description": "Allows HTTP/HTTPS from Internet, restricted SSH",
                "ingress_rules": [
                    {"id": "rule-http", "port": 80, "protocol": "TCP", "source": "0.0.0.0/0", "enabled": True, "description": "Public Web Traffic"},
                    {"id": "rule-https", "port": 443, "protocol": "TCP", "source": "0.0.0.0/0", "enabled": True, "description": "Public Secure Web"},
                    {"id": "rule-ssh", "port": 22, "protocol": "TCP", "source": "198.51.100.24/32", "enabled": True, "description": "Admin VPN Bastion IP"}
                ]
            },
            "sg-db-private": {
                "group_id": "sg-db-private",
                "name": "DB-Private-Security-Group",
                "description": "Strict database isolation - accepts traffic ONLY from Public Web subnet",
                "ingress_rules": [
                    {"id": "rule-postgres", "port": 5432, "protocol": "TCP", "source": "10.0.1.0/24", "enabled": True, "description": "PostgreSQL from Web Subnet"},
                    {"id": "rule-db-ssh", "port": 22, "protocol": "TCP", "source": "10.0.1.15/32", "enabled": False, "description": "Bastion Internal SSH (Disabled)"}
                ]
            }
        }

        # Workload Instances
        self.instances = {
            "i-web-pub": {
                "instance_id": "i-web-pub",
                "name": "Public-Web-App",
                "private_ip": "10.0.1.15",
                "public_ip": "52.90.14.22",
                "subnet_id": "subnet-pub-01",
                "security_group_id": "sg-web-public",
                "role": "Frontend Nginx / Reverse Proxy"
            },
            "i-db-priv": {
                "instance_id": "i-db-priv",
                "name": "Private-DB-Master",
                "private_ip": "10.0.2.80",
                "public_ip": None, # Isolated from direct internet
                "subnet_id": "subnet-priv-02",
                "security_group_id": "sg-db-private",
                "role": "PostgreSQL Relational Storage"
            }
        }

    def get_topology(self):
        with self.lock:
            return {
                "vpc": self.vpc,
                "subnets": list(self.subnets.values()),
                "gateways": list(self.gateways.values()),
                "route_tables": list(self.route_tables.values()),
                "security_groups": list(self.security_groups.values()),
                "instances": list(self.instances.values())
            }

    def toggle_security_rule(self, group_id: str, rule_id: str):
        with self.lock:
            if group_id in self.security_groups:
                for rule in self.security_groups[group_id]["ingress_rules"]:
                    if rule["id"] == rule_id:
                        rule["enabled"] = not rule["enabled"]
                        return {"success": True, "rule": rule}
            return {"error": "Rule or Security Group not found"}, 404

    def simulate_packet_trace(self, src_ip: str, dst_ip: str, port: int, protocol: str = "TCP"):
        with self.lock:
            hops = []
            verdict = "ALLOWED"
            status_code = 200
            final_reason = "Packet successfully routed to target instance."

            vpc_net = ipaddress.ip_network(self.vpc["cidr_block"])
            src_addr = ipaddress.ip_address(src_ip)
            dst_addr = ipaddress.ip_address(dst_ip)
            src_in_vpc = src_addr in vpc_net
            dst_in_vpc = dst_addr in vpc_net

            # Find matching target instance
            target_instance = None
            for inst in self.instances.values():
                if inst["private_ip"] == dst_ip or inst.get("public_ip") == dst_ip:
                    target_instance = inst
                    break

            # Hop 1: Gateway / Boundary Ingress Check
            if not src_in_vpc:
                hops.append({
                    "hop": 1,
                    "component": "Internet Gateway (igw-08fe4a11)",
                    "status": "PASS",
                    "action": f"Inbound packet from external IP {src_ip} crossed AWS Internet Gateway boundary."
                })

                # Check if dest is directly a private subnet IP with no public IP
                if target_instance and target_instance["subnet_id"] == "subnet-priv-02":
                    hops.append({
                        "hop": 2,
                        "component": "VPC Router (CIDR 10.0.0.0/16)",
                        "status": "DROP",
                        "action": f"Packet dropped: Destination IP {dst_ip} resides in Private Subnet 'subnet-priv-02' with zero public routing or Elastic IP."
                    })
                    return {
                        "verdict": "BLOCKED",
                        "status_code": 403,
                        "hops": hops,
                        "reason": f"Private Subnet Isolation: External clients cannot route directly to isolated private subnet workloads ({dst_ip})."
                    }
            else:
                hops.append({
                    "hop": 1,
                    "component": "Internal VPC Routing (10.0.0.0/16 Local Target)",
                    "status": "PASS",
                    "action": f"Inter-subnet packet dispatched from {src_ip} across high-bandwidth AWS VPC backbone."
                })

            if not target_instance:
                hops.append({
                    "hop": 2,
                    "component": "VPC Route Table",
                    "status": "DROP",
                    "action": f"No active ENI or instance found matching destination {dst_ip}."
                })
                return {
                    "verdict": "BLOCKED",
                    "status_code": 404,
                    "hops": hops,
                    "reason": f"Host Unreachable: Destination IP {dst_ip} not bound to any virtual network interface."
                }

            # Hop 2: Subnet Route Table Lookup
            subnet_info = self.subnets[target_instance["subnet_id"]]
            hops.append({
                "hop": 2,
                "component": f"Route Table ({subnet_info['route_table_id']})",
                "status": "PASS",
                "action": f"Matched local CIDR route {subnet_info['cidr_block']} -> Forwarded to Subnet '{subnet_info['name']}' ({subnet_info['zone']})."
            })

            # Hop 3: Stateless Network ACL (Subnet Boundary)
            hops.append({
                "hop": 3,
                "component": f"Network ACL ({subnet_info['name']})",
                "status": "PASS",
                "action": f"Stateless Rule 100 ALLOW: Protocol {protocol} Port {port} from {src_ip} matches ingress permit list."
            })

            # Hop 4: Stateful Security Group (Instance ENI Boundary)
            sg_id = target_instance["security_group_id"]
            sg = self.security_groups[sg_id]

            sg_matched = False
            for rule in sg["ingress_rules"]:
                if rule["enabled"] and rule["port"] == port and rule["protocol"] == protocol:
                    # Check CIDR source match
                    rule_net = ipaddress.ip_network(rule["source"])
                    src_addr = ipaddress.ip_address(src_ip)
                    if src_addr in rule_net:
                        sg_matched = True
                        hops.append({
                            "hop": 4,
                            "component": f"Security Group ({sg['name']})",
                            "status": "PASS",
                            "action": f"Stateful Rule matched: ALLOW {protocol} Port {port} from source CIDR {rule['source']} ({rule['description']})."
                        })
                        break

            if not sg_matched:
                hops.append({
                    "hop": 4,
                    "component": f"Security Group ({sg['name']})",
                    "status": "DROP",
                    "action": f"Implicit Deny: Security Group '{sg['name']}' dropped inbound {protocol}:{port} from {src_ip}. No matching ingress permit rule."
                })
                return {
                    "verdict": "BLOCKED",
                    "status_code": 403,
                    "hops": hops,
                    "reason": f"Security Group Firewall: Ingress port {port} on {target_instance['name']} rejected by '{sg['name']}'."
                }

            # Hop 5: Target Workload Delivery
            hops.append({
                "hop": 5,
                "component": f"Virtual Workload ({target_instance['name']})",
                "status": "PASS",
                "action": f"Delivered to {target_instance['role']} on private IP {target_instance['private_ip']}:{port}."
            })

            return {
                "verdict": "ALLOWED",
                "status_code": 200,
                "hops": hops,
                "reason": f"Traffic allowed through VPC Internet Gateway, Subnet Route Table, and Security Group '{sg['name']}'."
            }
