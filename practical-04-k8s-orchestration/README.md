# Practical 04: Container Orchestration & Kubernetes Control Plane

[![Docker](https://img.shields.io/badge/Docker-Compose_v2-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-v1.30-326CE5.svg?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Cloud Native](https://img.shields.io/badge/Architecture-Cloud_Native-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An ultra-lightweight (< 35 MB RAM) **Kubernetes Control Plane & Container Orchestration Simulator** demonstrating the core primitives of cloud-native computing: **ReplicaSet Self-Healing Reconciliation Loops**, **Zero-Downtime Rolling Updates (`maxSurge=1, maxUnavailable=0`)**, **Kubelet Liveness & Readiness Probes**, and **NodePort Service Ingress**.

> **👨‍🎓 For Students & Educators:** Read the [**`STUDENT_GUIDE.md`**](STUDENT_GUIDE.md) for a beginner-friendly explanation of why tech companies use Kubernetes over raw Docker, step-by-step interactive lab exercises, and viva/interview prep questions.

---

## 🏗️ Core Architectural Concepts

```
                  ┌──────────────────────────────────────────────┐
                  │          K8s Control Plane (Master)          │
                  │  ┌──────────────┐      ┌──────────────────┐  │
                  │  │kube-apiserver│ ───► │  etcd (Cluster   │  │
                  │  └──────────────┘      │      State)      │  │
                  │         ▲              └──────────────────┘  │
                  │         │                                    │
                  │  ┌──────────────┐      ┌──────────────────┐  │
                  │  │  Controller  │ ───► │  kube-scheduler  │  │
                  │  │   Manager    │      └──────────────────┘  │
                  │  └──────────────┘                            │
                  └─────────┬────────────────────────────────────┘
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
   ┌───────────────────────┐ ┌───────────────────────┐
   │    worker-node-01     │ │    worker-node-02     │
   │  ┌─────────────────┐  │ │  ┌─────────────────┐  │
   │  │  kubelet daemon │  │ │  │  kubelet daemon │  │
   │  └─────────────────┘  │ │  └─────────────────┘  │
   │  ┌─────────────────┐  │ │  ┌─────────────────┐  │
   │  │   kube-proxy    │  │ │  │   kube-proxy    │  │
   │  └─────────────────┘  │ │  └─────────────────┘  │
   │  [Pod 1]    [Pod 2]   │ │  [Pod 3]    [Pod 4]   │
   └───────────────────────┘ └───────────────────────┘
```

### 1. ReplicaSet Controller Reconciliation Loop
- Continuous feedback loop: `actual_replicas` vs `spec.replicas`.
- Automatic detection of missing pods with sub-second replacement scheduling.

### 2. Zero-Downtime Rolling Deployment
- `maxSurge: 1, maxUnavailable: 0` ensures capacity is never reduced during application version updates (`v1.0.0` ➔ `v2.0.0`).

### 3. Kubelet Health Probes
- **Liveness Probe**: Restarts frozen or deadlocked containers.
- **Readiness Probe**: Drops unready pods from Service Endpoints without killing the container.

---

## 🚀 Quickstart & Execution

### 1. Launch the Stack
```bash
cd practical-04-k8s-orchestration
cp .env.example .env
docker compose up --build -d
```

### 2. Verify Endpoints
```bash
# Check service health
curl -s http://localhost:8080/health | python3 -m json.tool

# Query cluster status & pod list
curl -s http://localhost:8080/api/status | python3 -m json.tool

# Send traffic through NodePort
curl -s -X POST http://localhost:8080/api/traffic | python3 -m json.tool
```

### 3. Open Web Dashboard
Navigate to `http://localhost:8080` in your web browser.

---

## 🛑 Clean Teardown
```bash
docker compose down
```
Frees host port `8080` and leaves zero lingering processes.
