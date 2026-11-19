import datetime
import random
import re
import threading
import time
import uuid
import yaml

DEFAULT_DEPLOYMENT_YAML = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloud-web-deploy
  labels:
    app: cloud-web
    tier: frontend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: cloud-web
  template:
    metadata:
      labels:
        app: cloud-web
    spec:
      containers:
      - name: web-app
        image: registry.k8s.io/cloud-web:v1.0.0
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: "500m"
            memory: "128Mi"
          requests:
            cpu: "100m"
            memory: "64Mi"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 3
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: cloud-web-service
spec:
  type: NodePort
  selector:
    app: cloud-web
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080
    protocol: TCP
"""

class K8sControlPlane:
    def __init__(self):
        self.lock = threading.RLock()
        self.raw_yaml = DEFAULT_DEPLOYMENT_YAML.strip()
        
        # Nodes in the cluster
        self.nodes = [
            {"name": "worker-node-01", "status": "Ready", "ip": "192.168.1.101", "cpu_total": "4 vCPU", "mem_total": "8 GiB", "pods_running": 0},
            {"name": "worker-node-02", "status": "Ready", "ip": "192.168.1.102", "cpu_total": "4 vCPU", "mem_total": "8 GiB", "pods_running": 0}
        ]
        
        # Deployment & ReplicaSet Specs
        self.deployment_name = "cloud-web-deploy"
        self.desired_replicas = 3
        self.image_version = "v1.0.0"
        self.rs_hash = "74b86f"
        
        # Pods dictionary: pod_name -> Pod Object
        self.pods = {}
        
        # Services & Endpoints
        self.service = {
            "name": "cloud-web-service",
            "type": "NodePort",
            "cluster_ip": "10.96.142.88",
            "node_port": 30080,
            "port": 80,
            "target_port": 8080,
            "endpoints": []
        }
        
        # Events stream (K8s cluster audit logs)
        self.events = []
        
        # Rolling update tracking
        self.is_rolling_update = False
        self.rolling_step = 0
        
        # Request round-robin counter
        self.rr_index = 0
        
        # Initialize cluster state
        self._init_cluster()
        
        # Start background Controller Manager & Kubelet loop
        self._running = True
        self.daemon_thread = threading.Thread(target=self._controller_reconciliation_loop, daemon=True)
        self.daemon_thread.start()

    def _log_event(self, event_type: str, reason: str, message: str, object_ref: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.events.insert(0, {
            "time": now,
            "type": event_type,
            "reason": reason,
            "message": message,
            "object": object_ref
        })
        if len(self.events) > 50:
            self.events.pop()

    def _generate_pod_name(self, rs_hash: str) -> str:
        random_suffix = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=5))
        return f"{self.deployment_name}-{rs_hash}-{random_suffix}"

    def _generate_pod_ip(self) -> str:
        subnet = random.choice([1, 2])
        host = random.randint(10, 240)
        return f"10.244.{subnet}.{host}"

    def _init_cluster(self):
        with self.lock:
            self._log_event("Normal", "Starting", "Kubernetes Control Plane initialized (API Server, Controller Manager, Scheduler)", "cluster/control-plane")
            self._log_event("Normal", "ScalingReplicaSet", f"Scaled up replica set {self.deployment_name}-{self.rs_hash} to {self.desired_replicas}", f"replicaset/{self.deployment_name}-{self.rs_hash}")
            
            for _ in range(self.desired_replicas):
                self._spawn_pod(self.rs_hash, self.image_version)
            
            self._update_endpoints()

    def _spawn_pod(self, rs_hash: str, version: str) -> str:
        node = random.choice(self.nodes)["name"]
        pod_name = self._generate_pod_name(rs_hash)
        pod_ip = self._generate_pod_ip()
        
        self.pods[pod_name] = {
            "name": pod_name,
            "rs_hash": rs_hash,
            "version": version,
            "node": node,
            "ip": pod_ip,
            "status": "Running",
            "ready": True,
            "restarts": 0,
            "created_at": time.time(),
            "liveness_failing": False,
            "readiness_failing": False,
            "probe_failure_count": 0,
            "cpu_usage": f"{random.randint(25, 85)}m",
            "mem_usage": f"{random.randint(35, 75)}MiB"
        }
        
        self._log_event("Normal", "Scheduled", f"Successfully assigned default/{pod_name} to {node}", f"pod/{pod_name}")
        self._log_event("Normal", "Pulled", f"Container image \"registry.k8s.io/cloud-web:{version}\" already present on {node}", f"pod/{pod_name}")
        self._log_event("Normal", "Started", f"Started container web-app (HTTP GET /healthz 200 OK)", f"pod/{pod_name}")
        return pod_name

    def _update_endpoints(self):
        healthy_ips = [
            {"name": p["name"], "ip": p["ip"], "node": p["node"], "version": p["version"]}
            for p in self.pods.values()
            if p["status"] == "Running" and p["ready"] and not p["readiness_failing"]
        ]
        self.service["endpoints"] = healthy_ips

    def _controller_reconciliation_loop(self):
        """K8s Controller Manager reconciliation loop running every 1 second."""
        while self._running:
            time.sleep(1.0)
            with self.lock:
                # 1. Kubelet Liveness Probe check
                for p_name, pod in list(self.pods.items()):
                    if pod.get("liveness_failing", False) and pod["status"] == "Running":
                        pod["probe_failure_count"] = pod.get("probe_failure_count", 0) + 1
                        if pod["probe_failure_count"] >= 2:
                            # Liveness failed threshold: Kubelet kills and restarts container
                            pod["restarts"] += 1
                            pod["liveness_failing"] = False
                            pod["probe_failure_count"] = 0
                            self._log_event("Warning", "Unhealthy", f"Liveness probe failed: HTTP probe to /healthz returned 500", f"pod/{p_name}")
                            self._log_event("Normal", "Killing", f"Container web-app failed liveness probe, will be restarted", f"pod/{p_name}")
                            self._log_event("Normal", "Started", f"Restarted container web-app (restart #{pod['restarts']})", f"pod/{p_name}")

                # 2. ReplicaSet Controller Self-Healing loop (Desired vs Actual)
                active_pods = [p for p in self.pods.values() if p["status"] == "Running"]
                current_count = len(active_pods)
                
                if not self.is_rolling_update:
                    if current_count < self.desired_replicas:
                        deficit = self.desired_replicas - current_count
                        for _ in range(deficit):
                            new_pod = self._spawn_pod(self.rs_hash, self.image_version)
                            self._log_event("Normal", "SelfHealing", f"ReplicaSet Controller detected deficit: spawned replacement pod {new_pod}", f"replicaset/{self.deployment_name}-{self.rs_hash}")
                    elif current_count > self.desired_replicas:
                        surplus = current_count - self.desired_replicas
                        for _ in range(surplus):
                            pod_to_remove = list(self.pods.keys())[0]
                            self.pods[pod_to_remove]["status"] = "Terminating"
                            del self.pods[pod_to_remove]
                            self._log_event("Normal", "Killing", f"Scaled down: stopped container and deleted pod {pod_to_remove}", f"pod/{pod_to_remove}")

                # 3. Update node pod allocations
                for node in self.nodes:
                    node["pods_running"] = sum(1 for p in self.pods.values() if p["node"] == node["name"] and p["status"] == "Running")

                # 4. Sync Service Endpoints
                self._update_endpoints()

    def get_cluster_status(self):
        with self.lock:
            # Calculate pod ages
            now = time.time()
            pod_list = []
            for p in self.pods.values():
                age_sec = int(now - p.get("created_at", now))
                age_str = f"{age_sec}s" if age_sec < 60 else f"{age_sec // 60}m {age_sec % 60}s"
                pod_list.append({
                    **p,
                    "age": age_str
                })

            return {
                "deployment": {
                    "name": self.deployment_name,
                    "desired_replicas": self.desired_replicas,
                    "current_replicas": len([p for p in self.pods.values() if p["status"] == "Running"]),
                    "ready_replicas": len([p for p in self.pods.values() if p["status"] == "Running" and p["ready"] and not p["readiness_failing"]]),
                    "image": f"registry.k8s.io/cloud-web:{self.image_version}",
                    "version": self.image_version,
                    "rs_hash": self.rs_hash,
                    "is_rolling_update": self.is_rolling_update
                },
                "nodes": self.nodes,
                "pods": pod_list,
                "service": self.service,
                "events": self.events[:20],
                "yaml_code": self.raw_yaml
            }

    def kill_pod(self, pod_name: str):
        """Simulates a sudden hardware fault, OOMKill, or node crash on a Pod."""
        with self.lock:
            if pod_name in self.pods:
                pod = self.pods[pod_name]
                node = pod["node"]
                del self.pods[pod_name]
                self._log_event("Warning", "OOMKilled", f"Pod {pod_name} crashed: Process exited with status 137 (OOMKilled / Crash)", f"pod/{pod_name}")
                self._log_event("Normal", "NodeLost", f"Kubelet detected Pod termination on {node}; removing from API Server", f"node/{node}")
                self._update_endpoints()
                return {"success": True, "killed": pod_name}
            return {"error": f"Pod {pod_name} not found"}

    def toggle_probe(self, pod_name: str, probe_type: str):
        """Toggles liveness or readiness probe failure on a Pod."""
        with self.lock:
            if pod_name in self.pods:
                pod = self.pods[pod_name]
                if probe_type == "liveness":
                    pod["liveness_failing"] = not pod.get("liveness_failing", False)
                    status_text = "Failing (500 Internal Error)" if pod["liveness_failing"] else "Healthy (200 OK)"
                    self._log_event("Warning" if pod["liveness_failing"] else "Normal", "ProbeState", f"Pod {pod_name} liveness probe set to {status_text}", f"pod/{pod_name}")
                    return {"success": True, "liveness_failing": pod["liveness_failing"]}
                elif probe_type == "readiness":
                    pod["readiness_failing"] = not pod.get("readiness_failing", False)
                    pod["ready"] = not pod["readiness_failing"]
                    self._update_endpoints()
                    status_text = "Not Ready (Traffic Dropped from Service)" if pod["readiness_failing"] else "Ready (Traffic Accepted)"
                    self._log_event("Warning" if pod["readiness_failing"] else "Normal", "EndpointsChanged", f"Pod {pod_name} readiness probe: {status_text}", f"service/{self.service['name']}")
                    return {"success": True, "readiness_failing": pod["readiness_failing"]}
            return {"error": f"Pod {pod_name} not found"}

    def scale_deployment(self, target_replicas: int):
        with self.lock:
            target = max(1, min(10, int(target_replicas)))
            old_count = self.desired_replicas
            self.desired_replicas = target
            
            # Update yaml representation
            self.raw_yaml = re.sub(r'replicas:\s*\d+', f'replicas: {target}', self.raw_yaml)
            
            self._log_event("Normal", "ScalingReplicaSet", f"Scaled replica set {self.deployment_name}-{self.rs_hash} from {old_count} to {target}", f"deployment/{self.deployment_name}")
            return {"success": True, "desired_replicas": target}

    def start_rolling_update(self, new_version: str):
        with self.lock:
            if self.is_rolling_update:
                return {"error": "Rolling update already in progress"}
            if new_version == self.image_version:
                new_version = "v2.0.0" if self.image_version == "v1.0.0" else "v1.0.0"

            self.is_rolling_update = True
            threading.Thread(target=self._execute_rolling_update, args=(new_version,), daemon=True).start()
            return {"success": True, "target_version": new_version}

    def _execute_rolling_update(self, new_version: str):
        """Simulates Kubernetes maxSurge=1, maxUnavailable=0 step-by-step rollout."""
        with self.lock:
            old_hash = self.rs_hash
            new_hash = ''.join(random.choices("0123456789abcdef", k=6))
            self._log_event("Normal", "ScalingReplicaSet", f"Created new ReplicaSet {self.deployment_name}-{new_hash} for image version {new_version}", f"deployment/{self.deployment_name}")
            
        # Gradually surge new version and drain old version
        while True:
            time.sleep(1.5)
            with self.lock:
                old_pods = [p for p in self.pods.values() if p["version"] != new_version and p["status"] == "Running"]
                new_pods = [p for p in self.pods.values() if p["version"] == new_version and p["status"] == "Running"]
                
                if len(new_pods) < self.desired_replicas:
                    # Surge 1 new pod
                    new_pod = self._spawn_pod(new_hash, new_version)
                    self._log_event("Normal", "RollingUpdate", f"[maxSurge=1] Spawned new {new_version} pod {new_pod}", f"replicaset/{self.deployment_name}-{new_hash}")
                    self._update_endpoints()
                elif old_pods:
                    # Terminate 1 old pod
                    old_pod_name = old_pods[0]["name"]
                    del self.pods[old_pod_name]
                    self._log_event("Normal", "RollingUpdate", f"Terminated old {old_pods[0]['version']} pod {old_pod_name}", f"replicaset/{self.deployment_name}-{old_hash}")
                    self._update_endpoints()
                else:
                    # Rollout complete
                    self.image_version = new_version
                    self.rs_hash = new_hash
                    self.is_rolling_update = False
                    self.raw_yaml = re.sub(r'image:\s*registry\.k8s\.io/cloud-web:[^\n]+', f'image: registry.k8s.io/cloud-web:{new_version}', self.raw_yaml)
                    self._log_event("Normal", "DeploymentRolloutComplete", f"Deployment {self.deployment_name} successfully rolled out to {new_version} with zero downtime", f"deployment/{self.deployment_name}")
                    break

    def apply_yaml(self, new_yaml: str):
        """Applies user-edited Kubernetes YAML manifest."""
        with self.lock:
            self.raw_yaml = new_yaml.strip()
            
            # Extract replicas
            replicas_match = re.search(r'replicas:\s*(\d+)', self.raw_yaml)
            if replicas_match:
                new_reps = int(replicas_match.group(1))
                if new_reps != self.desired_replicas:
                    self.scale_deployment(new_reps)

            # Extract image version
            image_match = re.search(r'image:\s*registry\.k8s\.io/cloud-web:([^\s\n]+)', self.raw_yaml)
            if image_match:
                target_ver = image_match.group(1)
                if target_ver != self.image_version and not self.is_rolling_update:
                    self.start_rolling_update(target_ver)

            self._log_event("Normal", "AppliedManifest", f"ConfigMap/Deployment manifest reconciled via kubectl apply", f"deployment/{self.deployment_name}")
            return {"success": True, "message": "Manifest applied successfully."}

    def send_traffic_request(self):
        """Simulates incoming HTTP traffic hitting the NodePort 30080 or ClusterIP."""
        with self.lock:
            healthy_endpoints = self.service["endpoints"]
            if not healthy_endpoints:
                return {
                    "status_code": 503,
                    "message": "503 Service Unavailable: No healthy endpoints found in cloud-web-service",
                    "serving_pod": None,
                    "latency_ms": 1.2
                }
            
            # Round robin selection
            self.rr_index = (self.rr_index + 1) % len(healthy_endpoints)
            target = healthy_endpoints[self.rr_index]
            latency = round(random.uniform(4.5, 18.2), 1)

            return {
                "status_code": 200,
                "message": f"HTTP/1.1 200 OK from Pod {target['name']}",
                "serving_pod": target["name"],
                "serving_ip": target["ip"],
                "serving_node": target["node"],
                "version": target["version"],
                "node_port": self.service["node_port"],
                "cluster_ip": self.service["cluster_ip"],
                "latency_ms": latency
            }

    def run_kubectl_cli(self, command: str):
        """Simulates real kubectl CLI outputs for students."""
        cmd = command.strip()
        with self.lock:
            if "get pods" in cmd:
                lines = ["NAME                             READY   STATUS    RESTARTS   AGE     IP            NODE"]
                for p in self.pods.values():
                    age_sec = int(time.time() - p.get("created_at", time.time()))
                    age_str = f"{age_sec}s"
                    ready_str = "1/1" if p["ready"] and not p.get("readiness_failing", False) else "0/1"
                    lines.append(f"{p['name']:<32} {ready_str:<7} {p['status']:<9} {p['restarts']:<10} {age_str:<7} {p['ip']:<13} {p['node']}")
                return "\n".join(lines)

            elif "get deployment" in cmd:
                lines = [
                    "NAME               READY   UP-TO-DATE   AVAILABLE   AGE",
                    f"{self.deployment_name:<18} {len([p for p in self.pods.values() if p['ready'] and not p.get('readiness_failing', False)])}/{self.desired_replicas}     {self.desired_replicas:<12} {len([p for p in self.pods.values() if p['ready'] and not p.get('readiness_failing', False)])}           2m"
                ]
                return "\n".join(lines)

            elif "get svc" in cmd:
                lines = [
                    "NAME                 TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE",
                    "kubernetes           ClusterIP   10.96.0.1       <none>        443/TCP        15m",
                    f"{self.service['name']:<20} NodePort    {self.service['cluster_ip']:<15} <none>        80:{self.service['node_port']}/TCP   2m"
                ]
                return "\n".join(lines)

            elif "get endpoints" in cmd or "get ep" in cmd:
                eps = ", ".join([f"{ep['ip']}:8080" for ep in self.service["endpoints"]]) or "<none>"
                lines = [
                    "NAME                 ENDPOINTS",
                    f"{self.service['name']:<20} {eps}"
                ]
                return "\n".join(lines)

            else:
                return f"$ {cmd}\nError: unknown command \"{cmd}\". Supported: 'kubectl get pods -o wide', 'kubectl get deployment', 'kubectl get svc', 'kubectl get ep'"
