# 🎓 Student Lab Guide: Practical 04 — Container Orchestration & Kubernetes Control Plane

---

## 📌 1. What is this practical about? (The Real-World Problem)

In Practical 03, we learned how Docker uses Linux Namespaces and Cgroups to run isolated container processes. 

However, running single Docker containers in production introduces critical engineering problems:
- **What happens if a container crashes at 3:00 AM?** A raw Docker container stays dead until a human engineer logs in and runs `docker restart`.
- **What happens if user traffic surges 10x?** You need multiple copies (replicas) of your container distributed across multiple physical or virtual machines, with automatic load balancing.
- **What happens when you deploy a new version (`v1` to `v2`)?** If you kill the old containers first, your users experience downtime and HTTP 500 errors.

### The Cloud Solution: **Kubernetes (K8s) Container Orchestration**
Kubernetes is the industry standard open-source system for automating deployment, scaling, and management of containerized applications:
1. **The Control Plane (`kube-apiserver`, `etcd`, `kube-controller-manager`, `kube-scheduler`)**: Acts as the brain of the cluster, continuously evaluating the **reconciliation loop** (Desired State vs Actual State).
2. **Worker Nodes (`kubelet`, `kube-proxy`)**: Run the physical containers inside **Pods** and manage network routing.
3. **Self-Healing**: If a pod crashes, runs out of memory (OOMKilled), or its worker node catches fire, the **ReplicaSet Controller** detects the deficit and schedules a new pod immediately.
4. **Zero-Downtime Rolling Updates**: Automatically spins up new pods (`maxSurge=1`), waits for readiness checks to pass, shifts network traffic, and safely drains old pods.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- Zero local Minikube or cloud Kubernetes billing required (this project includes a built-in ultra-lightweight Kubernetes Control Plane engine).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-04-k8s-orchestration
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: ReplicaSet Self-Healing & Chaos Testing
1. Look at the **Cluster Worker Nodes & Pod Topology** pane. You will see 3 running pods distributed across `worker-node-01` and `worker-node-02`.
2. Find any pod card (e.g. `cloud-web-deploy-74b86f-x8k2m`) and click the red **`⚡ Kill Pod`** button.
   - This simulates an unexpected container crash, kernel segfault, or hardware outage.
3. **Observe the magic of Kubernetes:**
   - The dead pod is removed from the API server.
   - The ReplicaSet controller immediately detects: `Current Replicas (2) < Desired Replicas (3)`.
   - Within 1 second, a brand-new replacement pod is automatically scheduled and started!
   - Check the **K8s Cluster Event Stream** at the bottom to see the real-time `SelfHealing` event audit.

### 🔹 Task 2: Zero-Downtime Rolling Update (`v1.0.0` ➔ `v2.0.0`)
1. In the top action bar or top right of the topology pane, click **`🚀 Rollout v2.0.0`**.
2. Watch the step-by-step rolling deployment:
   - Kubernetes follows `strategy: RollingUpdate` with `maxSurge: 1, maxUnavailable: 0`.
   - It launches a `v2.0.0` pod first (surging to 4 pods total).
   - Once the new pod passes its readiness probe, it starts taking traffic.
   - Then, an old `v1.0.0` pod is gracefully terminated.
   - This cycle repeats until all replicas run `v2.0.0`—**with zero dropped client requests**!

### 🔹 Task 3: Kubelet Liveness & Readiness Probes
1. On any running pod card, click **`🩺 Fail Liveness`**:
   - This simulates the application's `/healthz` HTTP endpoint returning `500 Internal Server Error` (e.g. deadlocked thread or full disk).
   - Watch the card outline turn yellow. Within 2 seconds, Kubelet detects the probe failure, issues a kill signal, restarts the container, and increments the **Restarts** counter!
2. On any running pod card, click **`🚫 Fail Readiness`**:
   - This simulates the app warming up or running a heavy background task where it cannot accept user traffic.
   - Notice the pod status changes to `NotReady 0/1`.
   - Kubelet **does NOT kill the container**, but `kube-proxy` immediately removes its IP from the **Service Endpoints** so no user requests get routed to it!
   - Click **`✅ Pass Readiness`** to restore it to service.

### 🔹 Task 4: Ingress Traffic Balancing & Kubectl Shell
1. In the **Client Traffic Ingress** section, click **`⚡ Send HTTP Request`** multiple times.
   - Observe how client requests arriving at NodePort `30080` are round-robin load-balanced across healthy pod IPs.
2. In the right panel, use the **Kubectl Interactive Shell** quick buttons:
   - Click **`get pods`** to see standard `kubectl get pods -o wide` terminal output.
   - Click **`get deployment`** to verify desired vs available replica counts.
   - Click **`get svc`** to see ClusterIP and NodePort port bindings.
   - Click **`get endpoints`** to inspect the live IP addresses tracked by kube-proxy.

---

## 💻 5. Terminal CLI Verification

You can also interact directly with the Kubernetes Control Plane backend API from your terminal:

```bash
# 1. Check health
curl -s http://localhost:8080/health | jq .

# 2. Query cluster status & pod list
curl -s http://localhost:8080/api/status | jq .

# 3. Scale deployment to 5 replicas
curl -s -X POST http://localhost:8080/api/scale \
  -H "Content-Type: application/json" \
  -d '{"replicas": 5}' | jq .

# 4. Trigger rolling update to v2.0.0
curl -s -X POST http://localhost:8080/api/rollout \
  -H "Content-Type: application/json" \
  -d '{"version": "v2.0.0"}' | jq .

# 5. Send traffic request through NodePort
curl -s -X POST http://localhost:8080/api/traffic | jq .

# 6. Run kubectl command via API
curl -s -X POST http://localhost:8080/api/kubectl \
  -H "Content-Type: application/json" \
  -d '{"command": "kubectl get pods -o wide"}' | jq .
```

---

## 🎯 6. Viva & Job Interview Questions & Answers

### Q1: What is the fundamental difference between a Pod and a Container?
> **Answer:**
> A container is a single sandboxed Linux process (using namespaces and cgroups). A **Pod** is the smallest deployable compute unit in Kubernetes. A Pod wraps one or more tightly coupled containers that share the **same network namespace** (same IP address and localhost), the same IPC namespace, and shared storage volumes.

### Q2: How does a ReplicaSet maintain the desired number of Pods?
> **Answer:**
> The **ReplicaSet Controller** runs a continuous **reconciliation loop** inside `kube-controller-manager`:
> 1. It queries the current number of running pods matching the specified label selector (e.g. `app=cloud-web`).
> 2. It compares `actual_replicas` against `spec.replicas` (desired state).
> 3. If `actual < desired`, it calls the API Server to schedule new pods.
> 4. If `actual > desired`, it gracefully terminates the surplus pods.

### Q3: What is the difference between a Liveness Probe and a Readiness Probe?
> **Answer:**
> - **Liveness Probe:** Checks if the container process is still alive and responsive. If it fails, Kubelet **kills the container and restarts it** according to its restart policy.
> - **Readiness Probe:** Checks if the container is ready to accept user network traffic. If it fails, Kubelet does **not** restart the container; instead, `kube-proxy` temporarily removes the Pod's IP from the Service Endpoints list so no traffic is routed to it until it recovers.

### Q4: What are the differences between ClusterIP and NodePort Services?
> **Answer:**
> - **ClusterIP (Default):** Exposes the Service on an internal virtual IP reachable **only from inside the cluster**. Ideal for private databases and backend microservices.
> - **NodePort:** Exposes the Service on a static high port (range 30000–32767) across **every worker node's external IP address**. External traffic hitting `<NodeIP>:<NodePort>` is forwarded by `kube-proxy` to the backend Pods.

### Q5: What do `maxSurge` and `maxUnavailable` mean during a Rolling Update?
> **Answer:**
> - **`maxSurge`:** The maximum number of extra Pods that can be created above the desired replica count during an update (e.g., `maxSurge: 1` on 3 replicas means at most 4 pods can run concurrently).
> - **`maxUnavailable`:** The maximum number of Pods that can be unavailable during the update process (e.g., `maxUnavailable: 0` guarantees that all 3 replicas remain available throughout the entire rollout, eliminating downtime).

---

## 🛑 7. Clean Teardown
When you are done with the lab, run:
```bash
docker compose down
```
This frees host port `8080` and leaves zero lingering processes.
