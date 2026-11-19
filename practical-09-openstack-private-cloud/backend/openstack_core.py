import datetime
import random
import threading
import time
import uuid

class OpenStackCore:
    def __init__(self):
        self.lock = threading.RLock()
        
        # Multi-Tenant Projects
        self.projects = {
            "proj-prod": {
                "id": "proj-prod",
                "name": "Production-Core",
                "description": "Enterprise Production Workloads & Database Clusters",
                "quotas": {"vcpus": 20, "ram_mb": 65536, "disk_gb": 500, "instances": 10}
            },
            "proj-dev": {
                "id": "proj-dev",
                "name": "Dev-Staging",
                "description": "Internal Development & CI/CD Pipelines",
                "quotas": {"vcpus": 8, "ram_mb": 16384, "disk_gb": 100, "instances": 4}
            }
        }
        
        # Valid Users & Roles
        self.users = {
            "admin": {"id": "usr-admin-01", "name": "admin", "password": "SecretAdminPass123", "role": "admin", "default_project": "proj-prod"},
            "developer": {"id": "usr-dev-02", "name": "developer", "password": "DevPassword2026", "role": "member", "default_project": "proj-dev"}
        }
        
        self.active_tokens = {}
        
        # Keystone Service Catalog
        self.service_catalog = [
            {"name": "keystone", "type": "identity", "description": "OpenStack Identity Service v3", "endpoint": "/v3", "status": "ACTIVE"},
            {"name": "nova", "type": "compute", "description": "OpenStack Compute API v2.1", "endpoint": "/v2.1", "status": "ACTIVE"},
            {"name": "glance", "type": "image", "description": "OpenStack Image Registry v2", "endpoint": "/v2/images", "status": "ACTIVE"},
            {"name": "neutron", "type": "network", "description": "OpenStack Software-Defined Networking v2.0", "endpoint": "/v2.0", "status": "ACTIVE"},
            {"name": "cinder", "type": "volumev3", "description": "OpenStack Block Storage v3", "endpoint": "/v3/volumes", "status": "ACTIVE"}
        ]
        
        # Nova Compute Hardware Flavors
        self.flavors = [
            {"id": "1", "name": "m1.tiny", "vcpus": 1, "ram": 512, "disk": 1},
            {"id": "2", "name": "m1.small", "vcpus": 1, "ram": 2048, "disk": 20},
            {"id": "3", "name": "m1.medium", "vcpus": 2, "ram": 4096, "disk": 40},
            {"id": "4", "name": "m1.large", "vcpus": 4, "ram": 8192, "disk": 80}
        ]
        
        # Glance Virtual Machine Disk Images
        self.images = [
            {"id": "img-cirros-01", "name": "CirrOS 0.6.0 (Cloud-Init Minimal x86_64)", "size_mb": 16, "status": "ACTIVE", "format": "QCOW2"},
            {"id": "img-ubuntu-02", "name": "Ubuntu 24.04 LTS Noble Server CloudImage", "size_mb": 580, "status": "ACTIVE", "format": "QCOW2"},
            {"id": "img-rocky-03", "name": "Rocky Linux 9 Enterprise Cloud", "size_mb": 640, "status": "ACTIVE", "format": "QCOW2"}
        ]
        
        # Neutron Virtual Networks & Floating IP Pool
        self.networks = [
            {"id": "net-prod-priv", "name": "private-net-prod", "cidr": "192.168.100.0/24", "gateway": "192.168.100.1", "project_id": "proj-prod", "type": "VXLAN"},
            {"id": "net-dev-priv", "name": "private-net-dev", "cidr": "10.0.10.0/24", "gateway": "10.0.10.1", "project_id": "proj-dev", "type": "VXLAN"},
            {"id": "net-ext-public", "name": "public-ext-net", "cidr": "203.0.113.0/24", "gateway": "203.0.113.1", "project_id": "shared", "type": "Flat (External)"}
        ]
        
        # Instances Database (Nova Servers)
        self.servers = {}
        
        # Audit Event Log
        self.events = []
        
        # Seed initial servers
        self._seed_initial_state()

    def _log_event(self, service: str, level: str, message: str, project_id: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.events.insert(0, {
            "time": now,
            "service": service,
            "level": level,
            "message": message,
            "project": self.projects.get(project_id, {}).get("name", project_id)
        })
        if len(self.events) > 50:
            self.events.pop()

    def _seed_initial_state(self):
        with self.lock:
            # Server in Production
            s1_id = str(uuid.uuid4())
            self.servers[s1_id] = {
                "id": s1_id,
                "name": "prod-app-server-01",
                "project_id": "proj-prod",
                "status": "ACTIVE",
                "power_state": "Running",
                "flavor": {"id": "2", "name": "m1.small", "vcpus": 1, "ram": 2048, "disk": 20},
                "image": {"id": "img-ubuntu-02", "name": "Ubuntu 24.04 LTS Noble Server CloudImage"},
                "ip_address": "192.168.100.15",
                "floating_ip": "203.0.113.45",
                "hypervisor_host": "compute-node-01.datacenter.internal",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            # Server in Dev
            s2_id = str(uuid.uuid4())
            self.servers[s2_id] = {
                "id": s2_id,
                "name": "dev-ci-runner-01",
                "project_id": "proj-dev",
                "status": "ACTIVE",
                "power_state": "Running",
                "flavor": {"id": "1", "name": "m1.tiny", "vcpus": 1, "ram": 512, "disk": 1},
                "image": {"id": "img-cirros-01", "name": "CirrOS 0.6.0 (Cloud-Init Minimal x86_64)"},
                "ip_address": "10.0.10.22",
                "floating_ip": None,
                "hypervisor_host": "compute-node-02.datacenter.internal",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            self._log_event("KEYSTONE", "INFO", "Keystone v3 Identity Service & Service Catalog initialized.", "proj-prod")
            self._log_event("NOVA", "SUCCESS", "Nova Compute spawned initial instance 'prod-app-server-01'.", "proj-prod")

    def authenticate_keystone(self, username, password, project_name="Production-Core"):
        with self.lock:
            user = self.users.get(username)
            if not user or user["password"] != password:
                return {"error": "Unauthorized: Invalid Keystone credentials"}, 401

            target_proj = next((p for p in self.projects.values() if p["name"] == project_name), None)
            if not target_proj:
                target_proj = self.projects[user["default_project"]]

            token_id = f"gAAAAAB{uuid.uuid4().hex[:26]}"
            expires_at = datetime.datetime.now() + datetime.timedelta(hours=1)

            self.active_tokens[token_id] = {
                "user": username,
                "role": user["role"],
                "project_id": target_proj["id"],
                "expires_at": expires_at.isoformat()
            }

            self._log_event("KEYSTONE", "SUCCESS", f"User '{username}' scoped auth token generated for project '{target_proj['name']}'.", target_proj["id"])

            return {
                "token": {
                    "id": token_id,
                    "user": {"name": username, "role": user["role"]},
                    "project": target_proj,
                    "catalog": self.service_catalog,
                    "expires_at": expires_at.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            }, 201

    def get_overview(self, project_id="proj-prod"):
        with self.lock:
            if project_id not in self.projects:
                project_id = "proj-prod"

            proj = self.projects[project_id]
            proj_servers = [s for s in self.servers.values() if s["project_id"] == project_id]

            used_vcpus = sum(s["flavor"]["vcpus"] for s in proj_servers if s["status"] != "DELETED")
            used_ram = sum(s["flavor"]["ram"] for s in proj_servers if s["status"] != "DELETED")
            used_disk = sum(s["flavor"]["disk"] for s in proj_servers if s["status"] != "DELETED")

            return {
                "current_project": proj,
                "all_projects": list(self.projects.values()),
                "quotas": {
                    "vcpus": {"used": used_vcpus, "limit": proj["quotas"]["vcpus"]},
                    "ram_mb": {"used": used_ram, "limit": proj["quotas"]["ram_mb"]},
                    "disk_gb": {"used": used_disk, "limit": proj["quotas"]["disk_gb"]},
                    "instances": {"used": len(proj_servers), "limit": proj["quotas"]["instances"]}
                },
                "service_catalog": self.service_catalog,
                "flavors": self.flavors,
                "images": self.images,
                "networks": [n for n in self.networks if n["project_id"] in [project_id, "shared"]],
                "servers": proj_servers,
                "events": self.events[:25]
            }

    def create_server(self, project_id, name, flavor_id, image_id, assign_floating=False):
        with self.lock:
            if project_id not in self.projects:
                project_id = "proj-prod"

            proj = self.projects[project_id]
            flavor = next((f for f in self.flavors if f["id"] == str(flavor_id)), self.flavors[0])
            image = next((img for img in self.images if img["id"] == image_id), self.images[0])

            # Check quota
            proj_servers = [s for s in self.servers.values() if s["project_id"] == project_id]
            used_vcpus = sum(s["flavor"]["vcpus"] for s in proj_servers)
            if (used_vcpus + flavor["vcpus"]) > proj["quotas"]["vcpus"]:
                return {"error": f"Quota Exceeded: Requested {flavor['vcpus']} vCPU, but project limit is {proj['quotas']['vcpus']} vCPUs."}

            server_id = str(uuid.uuid4())
            host_node = random.choice(["compute-node-01.datacenter.internal", "compute-node-02.datacenter.internal"])
            priv_ip = f"192.168.100.{random.randint(20, 240)}" if project_id == "proj-prod" else f"10.0.10.{random.randint(20, 240)}"
            floating_ip = f"203.0.113.{random.randint(10, 99)}" if assign_floating else None

            new_server = {
                "id": server_id,
                "name": name.strip() or f"instance-{server_id[:6]}",
                "project_id": project_id,
                "status": "ACTIVE",
                "power_state": "Running",
                "flavor": flavor,
                "image": image,
                "ip_address": priv_ip,
                "floating_ip": floating_ip,
                "hypervisor_host": host_node,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            }

            self.servers[server_id] = new_server
            self._log_event("NOVA", "SUCCESS", f"Nova Compute provisioned instance '{new_server['name']}' ({flavor['name']}) on {host_node}.", project_id)
            if floating_ip:
                self._log_event("NEUTRON", "INFO", f"Neutron allocated Floating IP {floating_ip} to '{new_server['name']}'.", project_id)

            return {"success": True, "server": new_server}

    def server_action(self, server_id, action):
        with self.lock:
            if server_id not in self.servers:
                return {"error": "Server not found"}

            srv = self.servers[server_id]
            p_id = srv["project_id"]

            if action == "stop":
                srv["status"] = "SHUTOFF"
                srv["power_state"] = "Shut Down"
                self._log_event("NOVA", "INFO", f"Instance '{srv['name']}' ACPI power off.", p_id)
            elif action == "start":
                srv["status"] = "ACTIVE"
                srv["power_state"] = "Running"
                self._log_event("NOVA", "INFO", f"Instance '{srv['name']}' powered on.", p_id)
            elif action == "reboot":
                srv["status"] = "REBOOT"
                self._log_event("NOVA", "INFO", f"Instance '{srv['name']}' warm reboot signal sent.", p_id)
                def finish_reboot():
                    time.sleep(1.2)
                    with self.lock:
                        if server_id in self.servers:
                            self.servers[server_id]["status"] = "ACTIVE"
                threading.Thread(target=finish_reboot, daemon=True).start()
            elif action == "floating_ip":
                if srv["floating_ip"]:
                    old_ip = srv["floating_ip"]
                    srv["floating_ip"] = None
                    self._log_event("NEUTRON", "INFO", f"Disassociated Floating IP {old_ip} from '{srv['name']}'.", p_id)
                else:
                    new_fip = f"203.0.113.{random.randint(10, 99)}"
                    srv["floating_ip"] = new_fip
                    self._log_event("NEUTRON", "SUCCESS", f"Associated Floating IP {new_fip} with '{srv['name']}'.", p_id)
            elif action == "delete":
                del self.servers[server_id]
                self._log_event("NOVA", "WARNING", f"Instance '{srv['name']}' deallocated and storage released.", p_id)
                return {"success": True, "deleted": srv["name"]}

            return {"success": True, "server": srv}

    def run_openstack_cli(self, command, project_id="proj-prod"):
        cmd = command.strip()
        with self.lock:
            proj = self.projects.get(project_id, self.projects["proj-prod"])
            proj_servers = [s for s in self.servers.values() if s["project_id"] == project_id]

            if "token issue" in cmd:
                return (
                    f"+------------+----------------------------------+\n"
                    f"| Field      | Value                            |\n"
                    f"+------------+----------------------------------+\n"
                    f"| expires    | 2026-11-20T01:30:00Z             |\n"
                    f"| id         | gAAAAAB{uuid.uuid4().hex[:26]}    |\n"
                    f"| project_id | {proj['id']:<32} |\n"
                    f"| user_id    | usr-admin-01                     |\n"
                    f"+------------+----------------------------------+"
                )

            elif "server list" in cmd:
                lines = [
                    "+--------------------------------------+---------------------+---------+----------------------------------------------+",
                    "| ID                                   | Name                | Status  | Networks                                     |",
                    "+--------------------------------------+---------------------+---------+----------------------------------------------+"
                ]
                for s in proj_servers:
                    net_str = f"private={s['ip_address']}"
                    if s["floating_ip"]:
                        net_str += f", {s['floating_ip']}"
                    lines.append(f"| {s['id']:<36} | {s['name']:<19} | {s['status']:<7} | {net_str:<44} |")
                lines.append("+--------------------------------------+---------------------+---------+----------------------------------------------+")
                return "\n".join(lines)

            elif "flavor list" in cmd:
                lines = [
                    "+----+-----------+-------+------+-----------+-------+-----------+",
                    "| ID | Name      |   RAM | Disk | Ephemeral | VCPUs | Is Public |",
                    "+----+-----------+-------+------+-----------+-------+-----------+"
                ]
                for f in self.flavors:
                    lines.append(f"| {f['id']:<2} | {f['name']:<9} | {f['ram']:>5} | {f['disk']:>4} |         0 | {f['vcpus']:>5} | True      |")
                lines.append("+----+-----------+-------+------+-----------+-------+-----------+")
                return "\n".join(lines)

            elif "image list" in cmd:
                lines = [
                    "+------------------+-----------------------------------------------+--------+",
                    "| ID               | Name                                          | Status |",
                    "+------------------+-----------------------------------------------+--------+"
                ]
                for img in self.images:
                    lines.append(f"| {img['id']:<16} | {img['name']:<45} | ACTIVE |")
                lines.append("+------------------+-----------------------------------------------+--------+")
                return "\n".join(lines)

            elif "network list" in cmd:
                lines = [
                    "+----------------+--------------------+--------------------------------------+",
                    "| ID             | Name               | Subnets                              |",
                    "+----------------+--------------------+--------------------------------------+",
                    "| net-prod-priv  | private-net-prod   | 192.168.100.0/24 (Gateway: .1)       |",
                    "| net-dev-priv   | private-net-dev    | 10.0.10.0/24 (Gateway: .1)           |",
                    "| net-ext-public | public-ext-net     | 203.0.113.0/24 (Floating IP Pool)    |",
                    "+----------------+--------------------+--------------------------------------+"
                ]
                return "\n".join(lines)

            elif "catalog list" in cmd:
                lines = [
                    "+----------+----------+-------------------------------------------------------------+",
                    "| Name     | Type     | Endpoints                                                   |",
                    "+----------+----------+-------------------------------------------------------------+"
                ]
                for cat in self.service_catalog:
                    lines.append(f"| {cat['name']:<8} | {cat['type']:<8} | public: http://localhost:8080{cat['endpoint']:<26} |")
                lines.append("+----------+----------+-------------------------------------------------------------+")
                return "\n".join(lines)

            else:
                return f"$ {cmd}\nSupported commands: 'openstack token issue', 'openstack server list', 'openstack flavor list', 'openstack image list', 'openstack network list', 'openstack catalog list'"
