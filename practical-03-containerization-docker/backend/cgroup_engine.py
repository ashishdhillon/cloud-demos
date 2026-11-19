import os
import platform
import socket
import threading
import time
import math
import uuid

class CgroupEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.hostname = socket.gethostname()
        self.start_time = time.time()
        self.is_healthy = True
        self.health_override_code = 200

        # Memory allocation buffer to demonstrate cgroup limits & OOM thresholds
        self.allocated_buffers = []
        self.allocated_mb = 0

        # CPU stress status
        self.cpu_stress_active = False
        self.cpu_stress_end_time = 0.0

        # Ephemeral container layer simulated files
        self.ephemeral_dir = "/tmp/overlay_demo"
        os.makedirs(self.ephemeral_dir, exist_ok=True)

        # Audit logs
        self.logs = []
        self._add_log("SYSTEM", f"Container initialized with hostname {self.hostname} on {platform.system()} {platform.machine()}")

    def _add_log(self, category: str, message: str):
        self.logs.insert(0, {
            "timestamp": time.strftime("%H:%M:%S"),
            "category": category,
            "message": message
        })
        if len(self.logs) > 60:
            self.logs.pop()

    def get_logs(self):
        with self.lock:
            return list(self.logs)

    def get_cgroup_metrics(self):
        with self.lock:
            cgroup_version = "cgroup v2"
            mem_current_bytes = 0
            mem_limit_bytes = 0
            cpu_quota_str = "0.50 vCPU"
            cpu_throttled_count = 0
            pids_current = 1
            pids_max = "max"

            # Check cgroup v2 paths
            cgroup_v2_mem_current = "/sys/fs/cgroup/memory.current"
            cgroup_v2_mem_max = "/sys/fs/cgroup/memory.max"
            cgroup_v2_cpu_max = "/sys/fs/cgroup/cpu.max"
            cgroup_v2_cpu_stat = "/sys/fs/cgroup/cpu.stat"
            cgroup_v2_pids_curr = "/sys/fs/cgroup/pids.current"
            cgroup_v2_pids_max = "/sys/fs/cgroup/pids.max"

            # Check cgroup v1 paths
            cgroup_v1_mem_current = "/sys/fs/cgroup/memory/memory.usage_in_bytes"
            cgroup_v1_mem_max = "/sys/fs/cgroup/memory/memory.limit_in_bytes"

            # 1. Memory current
            if os.path.exists(cgroup_v2_mem_current):
                try:
                    with open(cgroup_v2_mem_current, "r") as f:
                        mem_current_bytes = int(f.read().strip())
                except Exception:
                    pass
            elif os.path.exists(cgroup_v1_mem_current):
                cgroup_version = "cgroup v1"
                try:
                    with open(cgroup_v1_mem_current, "r") as f:
                        mem_current_bytes = int(f.read().strip())
                except Exception:
                    pass

            # 2. Memory limit
            if os.path.exists(cgroup_v2_mem_max):
                try:
                    with open(cgroup_v2_mem_max, "r") as f:
                        val = f.read().strip()
                        if val.isdigit():
                            mem_limit_bytes = int(val)
                except Exception:
                    pass
            elif os.path.exists(cgroup_v1_mem_max):
                try:
                    with open(cgroup_v1_mem_max, "r") as f:
                        val = f.read().strip()
                        if val.isdigit():
                            mem_limit_bytes = int(val)
                except Exception:
                    pass

            # If inside Docker on Mac / VM where limits are enforced
            # Fallback to compose-configured 128MB limit if unlimited or 0
            enforced_limit_mb = 128
            if mem_limit_bytes > 0 and mem_limit_bytes < 100 * 1024 * 1024 * 1024:
                enforced_limit_mb = round(mem_limit_bytes / (1024 * 1024), 1)

            # Simulated / process memory offset if running in dev mode
            current_mb = round(mem_current_bytes / (1024 * 1024), 2)
            if current_mb <= 0:
                current_mb = 32.4 + self.allocated_mb
            else:
                # Add allocated memory to display
                current_mb = max(current_mb, 32.4 + self.allocated_mb)

            # 3. CPU Quotas
            if os.path.exists(cgroup_v2_cpu_max):
                try:
                    with open(cgroup_v2_cpu_max, "r") as f:
                        parts = f.read().strip().split()
                        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                            quota = int(parts[0])
                            period = int(parts[1])
                            ratio = quota / period
                            cpu_quota_str = f"{ratio:.2f} vCPU ({quota}us / {period}us)"
                except Exception:
                    pass

            # 4. CPU Throttling
            if os.path.exists(cgroup_v2_cpu_stat):
                try:
                    with open(cgroup_v2_cpu_stat, "r") as f:
                        for line in f:
                            if line.startswith("nr_throttled"):
                                cpu_throttled_count = int(line.split()[1])
                except Exception:
                    pass

            # 5. PIDs
            if os.path.exists(cgroup_v2_pids_curr):
                try:
                    with open(cgroup_v2_pids_curr, "r") as f:
                        pids_current = int(f.read().strip())
                except Exception:
                    pass
            if os.path.exists(cgroup_v2_pids_max):
                try:
                    with open(cgroup_v2_pids_max, "r") as f:
                        pids_max = f.read().strip()
                except Exception:
                    pass

            mem_usage_pct = round((current_mb / enforced_limit_mb) * 100, 1)

            return {
                "cgroup_version": cgroup_version,
                "memory_limit_mb": enforced_limit_mb,
                "memory_current_mb": round(current_mb, 2),
                "memory_usage_pct": min(100.0, mem_usage_pct),
                "allocated_stress_mb": self.allocated_mb,
                "cpu_quota": cpu_quota_str,
                "cpu_throttled_count": cpu_throttled_count,
                "cpu_stress_active": self.cpu_stress_active,
                "pids_current": pids_current,
                "pids_max": pids_max,
                "process_id": os.getpid(),
                "user_id": os.getuid() if hasattr(os, "getuid") else 10001,
                "group_id": os.getgid() if hasattr(os, "getgid") else 10001,
                "is_unprivileged": (os.getuid() if hasattr(os, "getuid") else 10001) != 0,
                "hostname": self.hostname,
                "platform": platform.platform(),
                "uptime_seconds": round(time.time() - self.start_time, 1)
            }

    def allocate_memory(self, mb: int):
        with self.lock:
            # Enforce safety ceiling (don't exceed 110MB so process doesn't get hard killed by OOM killer)
            if self.allocated_mb + mb > 95:
                raise ValueError("Cgroup safety threshold reached! Exceeding 95MB of manual stress allocation risks immediate Linux OOM-Killer SIGKILL.")

            # Allocate bytearray (1MB chunks)
            for _ in range(mb):
                chunk = bytearray(1024 * 1024)
                # Touch memory to ensure physical RAM page faulting
                chunk[0] = 1
                chunk[1024 * 512] = 2
                self.allocated_buffers.append(chunk)

            self.allocated_mb += mb
            self._add_log("MEMORY", f"Allocated +{mb} MB into RAM buffer. Total stress allocation: {self.allocated_mb} MB.")
            return {"allocated_mb": self.allocated_mb, "status": "allocated"}

    def release_memory(self):
        with self.lock:
            freed = self.allocated_mb
            self.allocated_buffers.clear()
            self.allocated_mb = 0
            self._add_log("MEMORY", f"Reclaimed all stress memory buffers. Freed {freed} MB RAM.")
            return {"freed_mb": freed, "current_allocated_mb": 0}

    def trigger_cpu_stress(self, duration_sec: int = 5):
        with self.lock:
            if self.cpu_stress_active:
                return {"status": "already_running"}
            self.cpu_stress_active = True
            self.cpu_stress_end_time = time.time() + duration_sec
            self._add_log("CPU_QUOTA", f"Initiated {duration_sec}-second CPU stress loop to trigger CFS scheduler throttling.")

        def burn():
            start = time.time()
            while time.time() - start < duration_sec:
                # Math calculation to keep CPU saturated
                _ = [math.sqrt(x) for x in range(2000)]
                time.sleep(0.001) # Small yield to prevent freeze
            with self.lock:
                self.cpu_stress_active = False
                self._add_log("CPU_QUOTA", "CPU stress loop completed. CFS throttling calmed.")

        thread = threading.Thread(target=burn, daemon=True)
        thread.start()
        return {"status": "started", "duration_sec": duration_sec}

    def toggle_health(self):
        with self.lock:
            self.is_healthy = not self.is_healthy
            self.health_override_code = 200 if self.is_healthy else 503
            status_text = "HEALTHY (200 OK)" if self.is_healthy else "UNHEALTHY (503 Service Unavailable)"
            self._add_log("HEALTH_PROBE", f"Probe state toggled to {status_text}.")
            return {"healthy": self.is_healthy, "http_code": self.health_override_code}

    def get_image_layers(self):
        with self.lock:
            # Query files in ephemeral overlay directory
            ephemeral_files = []
            if os.path.exists(self.ephemeral_dir):
                for f in sorted(os.listdir(self.ephemeral_dir)):
                    filepath = os.path.join(self.ephemeral_dir, f)
                    if os.path.isfile(filepath):
                        size_kb = round(os.path.getsize(filepath) / 1024, 2)
                        ephemeral_files.append({"filename": f, "size_kb": size_kb})

            layers = [
                {
                    "layer_index": 1,
                    "command": "FROM python:3.12-slim",
                    "type": "Read-Only Base Image",
                    "size_approx": "118.4 MB",
                    "digest": "sha256:5e2bdb1b...",
                    "status": "Immutable Base"
                },
                {
                    "layer_index": 2,
                    "command": "RUN useradd -u 10001 -m -s /bin/bash cloudapp",
                    "type": "Read-Only Security Layer",
                    "size_approx": "1.2 MB",
                    "digest": "sha256:88fa2b10...",
                    "status": "Immutable Security"
                },
                {
                    "layer_index": 3,
                    "command": "RUN pip install -r requirements.txt (flask, gunicorn)",
                    "type": "Read-Only Dependencies",
                    "size_approx": "18.6 MB",
                    "digest": "sha256:4b901aef...",
                    "status": "Immutable Packages"
                },
                {
                    "layer_index": 4,
                    "command": "COPY app.py cgroup_engine.py .",
                    "type": "Read-Only Source Layer",
                    "size_approx": "24.5 KB",
                    "digest": "sha256:9f338d12...",
                    "status": "Immutable Application"
                },
                {
                    "layer_index": 5,
                    "command": "Container Runtime (OverlayFS Top Layer)",
                    "type": "Read-Write Ephemeral Layer (CoW)",
                    "size_approx": f"{round(sum(x['size_kb'] for x in ephemeral_files), 2)} KB",
                    "digest": "Ephemeral (destroyed on container rm)",
                    "status": "Writable Container Layer",
                    "files": ephemeral_files
                }
            ]
            return {"layers": layers, "ephemeral_file_count": len(ephemeral_files)}

    def touch_ephemeral_file(self):
        with self.lock:
            file_id = uuid.uuid4().hex[:6]
            filename = f"log_stream_{file_id}.txt"
            filepath = os.path.join(self.ephemeral_dir, filename)
            content = f"Copy-on-Write (CoW) demonstration record created at {time.strftime('%Y-%m-%d %H:%M:%S')}\nHost: {self.hostname}\nUID: 10001\n"
            with open(filepath, "w") as f:
                f.write(content)
            size_kb = round(os.path.getsize(filepath) / 1024, 2)
            self._add_log("OVERLAYFS", f"Created ephemeral layer file '{filename}' ({size_kb} KB). Base layers remained strictly immutable.")
            return {"filename": filename, "size_kb": size_kb}
