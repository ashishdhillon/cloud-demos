#!/usr/bin/env python3
"""
Cloud Systems Engineering Labs - Web Portal & Lab Orchestrator
Zero-dependency HTTP server using standard Python 3.
Runs on http://localhost:3000 and orchestrates all 15 cloud labs.
"""

import os
import sys
import json
import time
import socket
import logging
import threading
import subprocess
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Configuration
PORT = int(os.environ.get("PORT", 3000))
LAB_HOST_PORT = 8080
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("LabPortal")

# State management
STATE_LOCK = threading.RLock()
CURRENT_ACTION = {"state": "idle", "target": None, "message": "System ready", "logs": []}

def add_log(msg: str):
    with STATE_LOCK:
        entry = f"[{time.strftime('%H:%M:%S')}] {msg}"
        CURRENT_ACTION["logs"].append(entry)
        if len(CURRENT_ACTION["logs"]) > 100:
            CURRENT_ACTION["logs"].pop(0)
        CURRENT_ACTION["message"] = msg
        logger.info(msg)

LABS = [
    {
        "id": 1,
        "num": "01",
        "dir": "practical-01-service-models",
        "title": "NIST Cloud Service Models",
        "subtitle": "IaaS vs PaaS vs SaaS Shared Responsibility & Live Kernel Exploit",
        "category": "Compute & Cloud Models",
        "icon": "Layers",
        "badge": "NIST SP 800-145",
        "description": "Interactive NIST 9-layer stack comparison vs Pizza-as-a-Service analogy, live Linux kernel CVE-2024-1086 exploit simulator, and PaaS immunity tester.",
        "tags": ["IaaS", "PaaS", "SaaS", "CVE-2024-1086", "NIST Matrix", "Architecture Decision"],
        "memory_budget": "~38 MiB",
        "real_world": "AWS EC2 vs Google App Engine vs Salesforce"
    },
    {
        "id": 2,
        "num": "02",
        "dir": "practical-02-vm-lifecycle",
        "title": "Virtual Machine Lifecycle & Hypervisor",
        "subtitle": "Type-1 vs Type-2 Hypervisors & vCPU/vRAM Overcommit Engine",
        "category": "Compute & Virtualization",
        "icon": "Cpu",
        "badge": "Virtualization",
        "description": "Simulate Type-1 (Bare Metal) vs Type-2 hypervisors, manage multi-state VM lifecycles (CREATE, RUN, PAUSE, STOP, DESTROY), and monitor host overcommitment.",
        "tags": ["KVM", "ESXi", "Hypervisor", "vCPU Overcommit", "State Machine"],
        "memory_budget": "~34 MiB",
        "real_world": "AWS Nitro / VMware vSphere VM Provisioning"
    },
    {
        "id": 3,
        "num": "03",
        "dir": "practical-03-containerization-docker",
        "title": "Docker Containerization & Linux Cgroups",
        "subtitle": "Kernel Cgroups v2 Quotas, OverlayFS CoW & Namespace Isolation",
        "category": "Containers & OS Virtualization",
        "icon": "Box",
        "badge": "Linux Kernel Cgroups",
        "description": "Inspect cgroups v2 CPU throttles (0.50 cores), 128M memory limits, OverlayFS layer mechanics, and live Linux namespace isolation.",
        "tags": ["Cgroups v2", "OverlayFS", "Namespaces", "OOM Killer", "Docker Engine"],
        "memory_budget": "~36 MiB",
        "real_world": "Docker Daemon & Containerd Runtime Isolation"
    },
    {
        "id": 4,
        "num": "04",
        "dir": "practical-04-k8s-orchestration",
        "title": "Kubernetes Pod Orchestration",
        "subtitle": "Declarative Desired State, Etcd Reconciler & Self-Healing Chaos",
        "category": "Container Orchestration",
        "icon": "Ship",
        "badge": "K8s Control Plane",
        "description": "Simulate the Kubernetes control plane (Scheduler, Controller Manager, etcd). Kill worker pods with chaos mode and watch sub-3s self-healing reconciler.",
        "tags": ["etcd", "Reconciler Loop", "Self-Healing", "Probes", "Rolling Updates"],
        "memory_budget": "~39 MiB",
        "real_world": "Production EKS / GKE Cluster Resilience"
    },
    {
        "id": 5,
        "num": "05",
        "dir": "practical-05-cloud-networking-vpc",
        "title": "Cloud Networking: Dual-Tier VPC",
        "subtitle": "Public/Private Subnets, NAT Gateways & Hop-by-Hop Packet Tracer",
        "category": "Networking & Security",
        "icon": "Network",
        "badge": "VPC & Routing",
        "description": "Explore CIDR subnet calculation (/24 to /28), configure Public/Private subnets, Internet Gateways, NAT routing, and stateful Security Group inspection.",
        "tags": ["VPC", "CIDR", "NAT Gateway", "Route Tables", "Stateful SGs"],
        "memory_budget": "~35 MiB",
        "real_world": "AWS VPC / GCP Cloud Virtual Network Architecture"
    },
    {
        "id": 6,
        "num": "06",
        "dir": "practical-06-object-storage-s3",
        "title": "Cloud Object Storage & Presigned URLs",
        "subtitle": "S3-Compatible REST API, Expiring HMAC Signatures & Lifecycle",
        "category": "Storage & Data Management",
        "icon": "HardDrive",
        "badge": "AWS S3 Mock",
        "description": "Full S3 API mock with bucket creation, file uploads, automated storage tiering (Standard -> Infrequent Access -> Glacier), and HMAC-SHA256 presigned URLs.",
        "tags": ["S3 API", "Presigned URLs", "Storage Tiers", "HMAC-SHA256", "Lifecycle Rules"],
        "memory_budget": "~37 MiB",
        "real_world": "Amazon S3 / Google Cloud Storage Buckets"
    },
    {
        "id": 7,
        "num": "07",
        "dir": "practical-07-iam-access-control",
        "title": "Cloud Identity & Access Management",
        "subtitle": "RBAC Roles, JSON Policy Engine & Principle of Least Privilege",
        "category": "Security & Governance",
        "icon": "ShieldCheck",
        "badge": "IAM & RBAC",
        "description": "Evaluate AWS-style JSON IAM policies with explicit deny precedence, simulate role assumption, and conduct automated least-privilege permission audits.",
        "tags": ["IAM", "RBAC", "JSON Policies", "Least Privilege", "AssumeRole"],
        "memory_budget": "~33 MiB",
        "real_world": "AWS IAM / Azure Active Directory RBAC Policies"
    },
    {
        "id": 8,
        "num": "08",
        "dir": "practical-08-cloud-security",
        "title": "Cloud Security: WAF & KMS Encryption",
        "subtitle": "Token-Bucket DDoS Limiter, SQLi/XSS WAF & AES-256 Envelope Encryption",
        "category": "Security & Governance",
        "icon": "Lock",
        "badge": "WAF & Cryptography",
        "description": "Inspect WAF signature matching against live SQL injection & XSS payloads, test token-bucket DDoS rate limiters, and perform AES-256-GCM envelope encryption.",
        "tags": ["WAF", "DDoS Token-Bucket", "Envelope Encryption", "AES-256-GCM", "KMS"],
        "memory_budget": "~36 MiB",
        "real_world": "Cloudflare WAF / AWS KMS Security Infrastructure"
    },
    {
        "id": 9,
        "num": "09",
        "dir": "practical-09-openstack-private-cloud",
        "title": "OpenStack Private Cloud Architecture",
        "subtitle": "Nova, Neutron, Keystone & Multi-Tenant Quota Management",
        "category": "Private Cloud & Infrastructure",
        "icon": "Server",
        "badge": "OpenStack IaaS",
        "description": "Deploy instances across simulated OpenStack core services (Nova Compute, Neutron Network, Glance Images, Keystone Identity) and manage tenant quotas.",
        "tags": ["OpenStack", "Nova", "Neutron", "Keystone", "Tenant Quotas"],
        "memory_budget": "~35 MiB",
        "real_world": "On-Premises Telco & Enterprise Private Clouds"
    },
    {
        "id": 10,
        "num": "10",
        "dir": "practical-10-cloud-autoscaling",
        "title": "Horizontal Pod & Container Auto-Scaling",
        "subtitle": "Live Dynamic Scaling Formula, Cooldown Flapping Guard & Load Balancer",
        "category": "Cloud Native & Scaling",
        "icon": "Activity",
        "badge": "Autoscaling Engine",
        "description": "Experience dynamic horizontal scaling with real-time traffic generation (Flash Sale, Morning Rush), formula inspection, flapping prevention, and cost ROI.",
        "tags": ["Auto-Scaling", "Load Balancer", "Cooldown Guard", "Capacity Planning", "Traffic Simulator"],
        "memory_budget": "~42 MiB",
        "real_world": "AWS Auto Scaling Groups & Kubernetes HPA"
    },
    {
        "id": 11,
        "num": "11",
        "dir": "practical-11-cloud-migration",
        "title": "Cloud Data Migration & 6-Rs Strategy",
        "subtitle": "Gartner 6-Rs Decision Engine & SHA-256 Cryptographic Parity",
        "category": "Migration & Architecture",
        "icon": "Move",
        "badge": "6-Rs Migration",
        "description": "Evaluate on-prem architectures against Gartner's 6-Rs (Rehost, Replatform, Refactor, etc.), run chunked online data migration, and verify bit-level parity.",
        "tags": ["6-Rs", "Data Migration", "SHA-256 Parity", "TCO Calculator", "Chunked Sync"],
        "memory_budget": "~35 MiB",
        "real_world": "AWS Database Migration Service & CloudEndure"
    },
    {
        "id": 12,
        "num": "12",
        "dir": "practical-12-serverless-lambda",
        "title": "Serverless Computing & Event FaaS",
        "subtitle": "Micro-VM Cold Starts (280ms) vs Warm (12ms) & Micro-Billing",
        "category": "Serverless & Event-Driven",
        "icon": "Zap",
        "badge": "Serverless FaaS",
        "description": "Simulate event-driven FaaS execution, measure cold start virtualization penalties vs warm container reuse, and calculate micro-billing down to milliseconds.",
        "tags": ["Serverless", "Cold Start", "Micro-VM", "Micro-Billing", "Event-Driven"],
        "memory_budget": "~34 MiB",
        "real_world": "AWS Lambda / Google Cloud Functions"
    },
    {
        "id": 13,
        "num": "13",
        "dir": "practical-13-bigdata-analytics",
        "title": "Cloud Big Data: MapReduce vs Columnar",
        "subtitle": "Distributed Map/Shuffle/Reduce vs Vectorized SIMD Parquet Queries",
        "category": "Distributed & Big Data",
        "icon": "BarChart3",
        "badge": "Big Data Analytics",
        "description": "Run distributed MapReduce pipelines on streaming log datasets and benchmark against vectorized columnar storage with compression ratio metrics.",
        "tags": ["MapReduce", "Columnar Storage", "Vectorized SIMD", "Hadoop", "DuckDB/Parquet"],
        "memory_budget": "~38 MiB",
        "real_world": "Apache Spark / Google BigQuery / AWS EMR"
    },
    {
        "id": 14,
        "num": "14",
        "dir": "practical-14-multicloud-terraform",
        "title": "Multi-Cloud Infrastructure as Code",
        "subtitle": "Terraform DAG Engine, State File & Drift Detection",
        "category": "DevOps & Multi-Cloud",
        "icon": "Terminal",
        "badge": "Terraform IaC",
        "description": "Construct declarative HCL infrastructure, inspect dependency DAG resolution, execute Init/Plan/Apply cycles, and detect out-of-band cloud state drift.",
        "tags": ["Terraform", "IaC", "DAG Graph", "State Management", "Drift Detection"],
        "memory_budget": "~35 MiB",
        "real_world": "HashiCorp Terraform Multi-Cloud Orchestration"
    },
    {
        "id": 15,
        "num": "15",
        "dir": "practical-15-edge-computing-mqtt",
        "title": "Edge Computing & IoT Telemetry Broker",
        "subtitle": "Mosquitto MQTT Pub/Sub & 85% Bandwidth Reduction Edge Filtering",
        "category": "Edge & IoT Systems",
        "icon": "Radio",
        "badge": "Edge & MQTT",
        "description": "Connect IoT temperature/vibration sensors to an Eclipse Mosquitto MQTT broker, apply anomaly detection at the edge, and stream filtered telemetry to the cloud.",
        "tags": ["Edge Computing", "MQTT Broker", "IoT Telemetry", "Bandwidth Reduction", "Pub/Sub"],
        "memory_budget": "~37 MiB",
        "real_world": "AWS IoT Greengrass & Industrial IoT Edge Gateways"
    }
]

def check_port_8080():
    try:
        req = urllib.request.Request(
            f"http://localhost:{LAB_HOST_PORT}/",
            headers={"User-Agent": "LabPortal/1.0"}
        )
        with urllib.request.urlopen(req, timeout=1.5) as response:
            return response.status in (200, 301, 302)
    except Exception:
        return False

def get_active_info():
    """Detect which practical project is running and its containers."""
    active_dir = None
    containers = []
    
    # 1. Inspect docker compose ls
    try:
        res = subprocess.run(
            ["docker", "compose", "ls", "--format", "json"],
            capture_output=True, text=True, timeout=4
        )
        if res.returncode == 0 and res.stdout.strip():
            projects = json.loads(res.stdout)
            for p in projects:
                name = p.get("Name", "")
                if name.startswith("practical-"):
                    active_dir = name
                    break
                elif "autoscale" in name:
                    active_dir = "practical-10-cloud-autoscaling"
                    break
    except Exception as e:
        logger.debug(f"Error querying docker compose ls: {e}")

    # 2. Inspect containers bound to 8080 or with practical- prefix
    try:
        ps_res = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}||{{.Status}}||{{.Ports}}"],
            capture_output=True, text=True, timeout=4
        )
        if ps_res.returncode == 0:
            for line in ps_res.stdout.strip().splitlines():
                if not line.strip():
                    continue
                parts = line.split("||")
                c_name = parts[0] if len(parts) > 0 else ""
                c_status = parts[1] if len(parts) > 1 else ""
                c_ports = parts[2] if len(parts) > 2 else ""
                
                if "practical-" in c_name or "autoscale" in c_name:
                    containers.append({
                        "name": c_name,
                        "status": c_status,
                        "ports": c_ports
                    })
                    if not active_dir:
                        for lab in LABS:
                            if lab["dir"] in c_name or lab["num"] in c_name:
                                active_dir = lab["dir"]
                                break
    except Exception as e:
        logger.debug(f"Error querying docker ps: {e}")

    is_live = check_port_8080()
    active_lab = None
    if active_dir:
        for lab in LABS:
            if lab["dir"] == active_dir:
                active_lab = dict(lab)
                break
        if not active_lab:
            # Fallback matching
            for lab in LABS:
                if lab["dir"].replace("-", "") in active_dir.replace("-", ""):
                    active_lab = dict(lab)
                    break

    return {
        "active_lab": active_lab,
        "is_port_8080_live": is_live,
        "containers": containers
    }

def perform_stop():
    """Teardown any active practical and free port 8080."""
    with STATE_LOCK:
        CURRENT_ACTION["state"] = "stopping"
        add_log("Stopping all running practical containers...")

    try:
        # Run root run.sh stop
        stop_cmd = os.path.join(ROOT_DIR, "run.sh")
        if os.path.isfile(stop_cmd):
            proc = subprocess.run([stop_cmd, "stop"], capture_output=True, text=True, timeout=30)
            for line in proc.stdout.splitlines():
                if line.strip():
                    add_log(line.strip())
        else:
            # Fallback direct compose teardown
            subprocess.run(["docker", "rm", "-f", "app-3", "app-4", "app-5"], capture_output=True)
            port_holders = subprocess.run(["docker", "ps", "--filter", "publish=8080", "-q"], capture_output=True, text=True)
            if port_holders.stdout.strip():
                subprocess.run(["docker", "stop"] + port_holders.stdout.strip().split(), capture_output=True)

        add_log("Teardown complete. Port 8080 is released.")
    except Exception as e:
        add_log(f"Error during teardown: {e}")
    finally:
        with STATE_LOCK:
            CURRENT_ACTION["state"] = "idle"
            CURRENT_ACTION["target"] = None

def perform_launch(lab_num: str):
    """Launch practical lab_num in background thread."""
    with STATE_LOCK:
        CURRENT_ACTION["state"] = "launching"
        CURRENT_ACTION["target"] = lab_num
        add_log(f"Initiating launch sequence for Practical {lab_num}...")

    try:
        lab = next((l for l in LABS if l["num"] == lab_num), None)
        if not lab:
            add_log(f"Practical {lab_num} not found in catalog.")
            return

        lab_dir = os.path.join(ROOT_DIR, lab["dir"])
        start_script = os.path.join(lab_dir, "start.sh")

        if not os.path.isfile(start_script):
            add_log(f"Missing start script: {start_script}")
            return

        add_log(f"Executing: {lab['dir']}/start.sh")
        
        # Execute start.sh
        proc = subprocess.Popen(
            [start_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=lab_dir
        )

        for line in proc.stdout:
            cleaned = line.strip()
            if cleaned:
                # Filter out raw docker layer download progress noise
                if not cleaned.startswith("=>") and "extracting" not in cleaned:
                    add_log(cleaned)

        proc.wait(timeout=120)

        # Confirm health
        add_log("Verifying service endpoint at http://localhost:8080...")
        healthy = False
        for _ in range(15):
            if check_port_8080():
                healthy = True
                break
            time.sleep(1)

        if healthy:
            add_log(f"🎉 Practical {lab_num}: {lab['title']} is LIVE and ready on http://localhost:8080!")
        else:
            add_log(f"⚠️ Containers launched, but port 8080 is still initializing.")

    except Exception as e:
        add_log(f"Launch failed with error: {e}")
    finally:
        with STATE_LOCK:
            CURRENT_ACTION["state"] = "idle"
            CURRENT_ACTION["target"] = None

class PortalRequestHandler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.serve_file(os.path.join(os.path.dirname(__file__), "index.html"), "text/html; charset=utf-8")
        elif path == "/api/status":
            info = get_active_info()
            with STATE_LOCK:
                action_info = dict(CURRENT_ACTION)
            data = {
                "active_lab": info["active_lab"],
                "is_port_8080_live": info["is_port_8080_live"],
                "containers": info["containers"],
                "action": action_info,
                "labs": LABS
            }
            self.send_json(data)
        elif path == "/api/logs":
            with STATE_LOCK:
                logs = list(CURRENT_ACTION["logs"])
            self.send_json({"logs": logs})
        elif path.startswith("/api/guide/"):
            num = path.split("/api/guide/")[1].strip()
            self.serve_guide(num)
        elif path == "/health":
            self.send_json({"status": "ok", "timestamp": time.time()})
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/launch/"):
            num = path.split("/api/launch/")[1].strip()
            if len(num) == 1:
                num = f"0{num}"

            with STATE_LOCK:
                if CURRENT_ACTION["state"] != "idle":
                    self.send_json({"status": "busy", "message": "Another action is already in progress."}, status=409)
                    return

            thread = threading.Thread(target=perform_launch, args=(num,), daemon=True)
            thread.start()
            self.send_json({"status": "starting", "num": num, "message": f"Launching Practical {num}..."})

        elif path == "/api/stop":
            with STATE_LOCK:
                if CURRENT_ACTION["state"] != "idle":
                    self.send_json({"status": "busy", "message": "Another action is already in progress."}, status=409)
                    return

            thread = threading.Thread(target=perform_stop, daemon=True)
            thread.start()
            self.send_json({"status": "stopping", "message": "Stopping all practical labs..."})
        else:
            self.send_error(404, "Unknown endpoint")

    def serve_guide(self, num: str):
        if len(num) == 1:
            num = f"0{num}"
        lab = next((l for l in LABS if l["num"] == num), None)
        if not lab:
            self.send_json({"error": "Lab not found"}, status=404)
            return

        guide_path = os.path.join(ROOT_DIR, lab["dir"], "STUDENT_GUIDE.md")
        if not os.path.isfile(guide_path):
            guide_path = os.path.join(ROOT_DIR, lab["dir"], "README.md")

        if os.path.isfile(guide_path):
            with open(guide_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_json({"num": num, "title": lab["title"], "content": content})
        else:
            self.send_json({"error": "Guide not found"}, status=404)

    def serve_file(self, filepath, content_type):
        if not os.path.isfile(filepath):
            self.send_error(404, "File Not Found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Suppress noisy health poll logging
        if "/api/status" in args[0] or "/health" in args[0]:
            return
        logger.info(f"{self.address_string()} - {args[0]}")

class ThreadedHTTPServer(socket.socket):
    pass

def run_server():
    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, PortalRequestHandler)
    print("=" * 74)
    print(" 🌐 CLOUD SYSTEMS ENGINEERING LABS - WEB CONTROL PORTAL")
    print("=" * 74)
    print(f" Status    : Online")
    print(f" URL       : http://localhost:{PORT}")
    print(f" Labs Port : http://localhost:{LAB_HOST_PORT}")
    print(f" Root Path : {ROOT_DIR}")
    print("=" * 74)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web portal server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
