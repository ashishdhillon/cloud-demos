import threading
import time
import uuid

class ServiceModelsEngine:
    def __init__(self):
        self.lock = threading.Lock()

        # 1. 9-Layer Cloud Shared Responsibility Model Matrix
        self.layers = [
            {"id": "facilities", "name": "Physical Facilities & Data Centers", "category": "Infrastructure"},
            {"id": "hardware", "name": "Physical Servers, CPUs, Disks & Networking", "category": "Infrastructure"},
            {"id": "virtualization", "name": "Hypervisor & VM Isolation Layer", "category": "Infrastructure"},
            {"id": "os", "name": "Operating System Kernel & Security Patches", "category": "Platform"},
            {"id": "middleware", "name": "Middleware & Web Servers (Nginx, Gunicorn)", "category": "Platform"},
            {"id": "runtime", "name": "Language Runtime (Python, Node.js, Java, Go)", "category": "Platform"},
            {"id": "data", "name": "Customer Data, Databases & Encryption Keys", "category": "Application"},
            {"id": "applications", "name": "Custom Application Source Code & Logic", "category": "Application"},
            {"id": "identity_access", "name": "Identity, Access Management (IAM) & Logins", "category": "Application"}
        ]

        self.models_matrix = {
            "on_premise": {
                "name": "On-Premises Traditional Datacenter",
                "provider_managed": [],
                "customer_managed": ["facilities", "hardware", "virtualization", "os", "middleware", "runtime", "data", "applications", "identity_access"],
                "summary": "Customer owns and operates 100% of the stack, from physical diesel backup generators to application code."
            },
            "iaas": {
                "name": "Infrastructure as a Service (IaaS)",
                "examples": "AWS EC2, Google Compute Engine, Azure VMs, Linode",
                "provider_managed": ["facilities", "hardware", "virtualization"],
                "customer_managed": ["os", "middleware", "runtime", "data", "applications", "identity_access"],
                "summary": "Cloud provider supplies raw compute and hypervisors. Customer must install OS patches, configure firewalls, and install runtimes."
            },
            "paas": {
                "name": "Platform as a Service (PaaS)",
                "examples": "AWS Elastic Beanstalk, Google App Engine, Heroku, Vercel",
                "provider_managed": ["facilities", "hardware", "virtualization", "os", "middleware", "runtime"],
                "customer_managed": ["data", "applications", "identity_access"],
                "summary": "Cloud provider manages servers, OS patching, and language runtimes. Customer only provides application code and data."
            },
            "saas": {
                "name": "Software as a Service (SaaS)",
                "examples": "Google Workspace, Microsoft 365, Salesforce, Slack, GitHub",
                "provider_managed": ["facilities", "hardware", "virtualization", "os", "middleware", "runtime", "data_platform", "applications"],
                "customer_managed": ["identity_access"],
                "summary": "Entire application stack managed by the vendor. End customers access software via web browser or API with zero infrastructure maintenance."
            }
        }

        # 2. In-Memory IaaS State
        self.iaas_instances = {
            "i-a4f78b12": {
                "instance_id": "i-a4f78b12",
                "os": "Ubuntu 24.04 LTS",
                "vcpu": 2,
                "ram_gb": 4,
                "private_ip": "10.0.1.10",
                "public_ip": "54.204.88.19",
                "os_patch_status": "pending_security_patches (3 CVEs)",
                "firewall_ports_open": [22],
                "uptime": "24 days",
                "status": "RUNNING"
            }
        }

        # 3. In-Memory PaaS State
        self.paas_deployments = {
            "dep-e3c12a": {
                "deployment_id": "dep-e3c12a",
                "app_name": "ecommerce-api",
                "runtime": "Python 3.12 (Buildpack Auto-Detected)",
                "git_branch": "main (commit 8fa42b1)",
                "url": "https://ecommerce-api.cloud-paas.internal",
                "replicas": 3,
                "auto_scaling_range": "1 - 10 Replicas",
                "health": "HEALTHY (200 OK)",
                "os_management": "Provider-Managed (Zero Customer OS Patching)"
            }
        }

        # 4. In-Memory SaaS State
        self.saas_tenants = {
            "tenant-alpha": {
                "tenant_id": "tenant-alpha",
                "company": "Acme Corp",
                "users": 142,
                "plan": "Enterprise SaaS",
                "storage_used_mb": 1240,
                "created_at": "2026-01-15"
            },
            "tenant-beta": {
                "tenant_id": "tenant-beta",
                "company": "Globex Inc",
                "users": 38,
                "plan": "Team SaaS",
                "storage_used_mb": 420,
                "created_at": "2026-02-01"
            }
        }

    def get_overview(self):
        with self.lock:
            return {
                "layers": self.layers,
                "models_matrix": self.models_matrix,
                "counts": {
                    "iaas_instances": len(self.iaas_instances),
                    "paas_deployments": len(self.paas_deployments),
                    "saas_tenants": len(self.saas_tenants)
                }
            }

    # IaaS Operations
    def provision_iaas_vm(self, os_name: str, vcpu: int, ram_gb: int):
        with self.lock:
            inst_id = f"i-{uuid.uuid4().hex[:8]}"
            subnet_last = len(self.iaas_instances) + 11
            instance = {
                "instance_id": inst_id,
                "os": os_name,
                "vcpu": max(1, min(16, vcpu)),
                "ram_gb": max(1, min(64, ram_gb)),
                "private_ip": f"10.0.1.{subnet_last}",
                "public_ip": f"54.{120 + subnet_last}.14.99",
                "os_patch_status": "unpatched (Kernel updates required by customer)",
                "firewall_ports_open": [22],
                "uptime": "Just Started",
                "status": "RUNNING"
            }
            self.iaas_instances[inst_id] = instance
            return instance

    def apply_os_patch_iaas(self, instance_id: str):
        with self.lock:
            if instance_id not in self.iaas_instances:
                raise ValueError("Instance ID not found")
            inst = self.iaas_instances[instance_id]
            inst["os_patch_status"] = "patched_latest (Linux kernel & packages up to date)"
            return inst

    def terminate_iaas_vm(self, instance_id: str):
        with self.lock:
            if instance_id in self.iaas_instances:
                del self.iaas_instances[instance_id]
                return {"success": True, "instance_id": instance_id}
            raise ValueError("Instance ID not found")

    # PaaS Operations
    def deploy_paas_app(self, app_name: str, runtime: str, git_branch: str = "main"):
        with self.lock:
            dep_id = f"dep-{uuid.uuid4().hex[:6]}"
            deployment = {
                "deployment_id": dep_id,
                "app_name": app_name.lower().replace(" ", "-"),
                "runtime": f"{runtime} (Buildpack Detected)",
                "git_branch": f"{git_branch} (commit {uuid.uuid4().hex[:7]})",
                "url": f"https://{app_name.lower().replace(' ', '-')}.cloud-paas.internal",
                "replicas": 2,
                "auto_scaling_range": "1 - 8 Replicas",
                "health": "HEALTHY (200 OK)",
                "os_management": "Provider-Managed (Zero Customer OS Patching)"
            }
            self.paas_deployments[dep_id] = deployment
            return deployment

    def scale_paas_app(self, deployment_id: str, replicas: int):
        with self.lock:
            if deployment_id not in self.paas_deployments:
                raise ValueError("Deployment ID not found")
            dep = self.paas_deployments[deployment_id]
            dep["replicas"] = max(1, min(20, replicas))
            return dep

    # SaaS Operations
    def create_saas_tenant(self, company: str, users: int, plan: str):
        with self.lock:
            tenant_id = f"tenant-{uuid.uuid4().hex[:6]}"
            tenant = {
                "tenant_id": tenant_id,
                "company": company,
                "users": max(1, users),
                "plan": plan,
                "storage_used_mb": max(10, users * 15),
                "created_at": time.strftime("%Y-%m-%d")
            }
            self.saas_tenants[tenant_id] = tenant
            return tenant

    def delete_saas_tenant(self, tenant_id: str):
        with self.lock:
            if tenant_id in self.saas_tenants:
                del self.saas_tenants[tenant_id]
                return {"success": True, "tenant_id": tenant_id}
            raise ValueError("Tenant ID not found")

    def get_full_state(self):
        with self.lock:
            return {
                "iaas_instances": list(self.iaas_instances.values()),
                "paas_deployments": list(self.paas_deployments.values()),
                "saas_tenants": list(self.saas_tenants.values()),
                "matrix": self.models_matrix
            }
