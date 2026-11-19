import hashlib
import json
import random
import threading
import time
import uuid
from typing import Any, Dict, List

IDLE_SANDBOX_TTL = 15.0  # Seconds before an idle sandbox is evicted
AWS_LAMBDA_GB_SECOND_COST = 0.0000166667
AWS_LAMBDA_REQUEST_COST = 0.20 / 1_000_000

FUNCTIONS = {
    "image-thumbnailer": {
        "name": "Image Thumbnail Generator",
        "description": "Transforms high-resolution image uploads into 200x200 thumbnails.",
        "memory_mb": 256,
        "runtime": "python3.12",
        "base_exec_ms": 35.0,
        "handler": "thumbnailer.handler"
    },
    "sentiment-analyzer": {
        "name": "NLP Sentiment Classification",
        "description": "Performs fast tokenization and sentiment classification on incoming user reviews.",
        "memory_mb": 128,
        "runtime": "python3.12",
        "base_exec_ms": 18.0,
        "handler": "nlp_worker.analyze"
    },
    "pdf-watermarker": {
        "name": "PDF Security Watermarking",
        "description": "Injects dynamic cryptographic watermarks and signatures into PDF contracts.",
        "memory_mb": 512,
        "runtime": "python3.12",
        "base_exec_ms": 65.0,
        "handler": "pdf_engine.stamp"
    },
    "crypto-hasher": {
        "name": "Cryptographic Hash Worker",
        "description": "Compute-intensive multi-round PBKDF2/SHA-512 password hashing and verification.",
        "memory_mb": 1024,
        "runtime": "python3.12",
        "base_exec_ms": 95.0,
        "handler": "hasher.compute_key"
    }
}

class Sandbox:
    def __init__(self, function_id: str, memory_mb: int):
        self.sandbox_id = f"sandbox-{uuid.uuid4().hex[:8]}"
        self.function_id = function_id
        self.memory_mb = memory_mb
        self.created_at = time.time()
        self.last_active_at = time.time()
        self.reuse_count = 0
        self.is_busy = False

    def touch(self):
        self.last_active_at = time.time()
        self.reuse_count += 1
        self.is_busy = False

    def get_ttl_remaining(self) -> float:
        elapsed = time.time() - self.last_active_at
        return max(0.0, round(IDLE_SANDBOX_TTL - elapsed, 1))

class FaaSEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.sandboxes: Dict[str, Sandbox] = {}
        self.invocation_history: List[Dict[str, Any]] = []
        self.total_invocations = 0
        self.total_cold_starts = 0
        self.total_warm_reuses = 0
        self.total_billed_cost = 0.0

        # Background reaper for expired idle sandboxes
        self.running = True
        self.reaper_thread = threading.Thread(target=self._reaper_loop, daemon=True)
        self.reaper_thread.start()

    def _reaper_loop(self):
        while self.running:
            time.sleep(1.0)
            now = time.time()
            with self.lock:
                to_delete = []
                for sid, s in self.sandboxes.items():
                    if not s.is_busy and (now - s.last_active_at > IDLE_SANDBOX_TTL):
                        to_delete.append(sid)
                for sid in to_delete:
                    del self.sandboxes[sid]

    def get_functions(self) -> Dict[str, Any]:
        return FUNCTIONS

    def get_active_sandboxes(self) -> List[Dict[str, Any]]:
        with self.lock:
            result = []
            for s in self.sandboxes.values():
                result.append({
                    "sandbox_id": s.sandbox_id,
                    "function_id": s.function_id,
                    "memory_mb": s.memory_mb,
                    "reuse_count": s.reuse_count,
                    "is_busy": s.is_busy,
                    "ttl_remaining_s": s.get_ttl_remaining()
                })
            return sorted(result, key=lambda x: x["ttl_remaining_s"], reverse=True)

    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            warm_ratio = 0.0
            if self.total_invocations > 0:
                warm_ratio = round((self.total_warm_reuses / self.total_invocations) * 100, 1)

            return {
                "total_invocations": self.total_invocations,
                "total_cold_starts": self.total_cold_starts,
                "total_warm_reuses": self.total_warm_reuses,
                "warm_reuse_ratio_pct": warm_ratio,
                "active_sandboxes_count": len(self.sandboxes),
                "total_billed_cost_usd": f"${self.total_billed_cost:.8f}"
            }

    def invoke(self, function_id: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        if function_id not in FUNCTIONS:
            raise ValueError(f"Function '{function_id}' does not exist.")

        func = FUNCTIONS[function_id]
        memory_mb = func["memory_mb"]
        payload = payload or {}

        # 1. Check for available warm sandbox
        sandbox = None
        is_cold_start = False
        init_duration_ms = 0.0

        with self.lock:
            for s in self.sandboxes.values():
                if s.function_id == function_id and not s.is_busy:
                    sandbox = s
                    sandbox.is_busy = True
                    break

            if not sandbox:
                # Provision new sandbox (Cold Start)
                is_cold_start = True
                sandbox = Sandbox(function_id, memory_mb)
                sandbox.is_busy = True
                self.sandboxes[sandbox.sandbox_id] = sandbox
                self.total_cold_starts += 1
            else:
                self.total_warm_reuses += 1

            self.total_invocations += 1

        # 2. Simulate Cold Start Init Duration vs Warm Execution
        if is_cold_start:
            # Simulate container spawn, python runtime initialization, and module loading
            init_duration_ms = round(random.uniform(230.0, 310.0), 2)
            time.sleep(init_duration_ms / 1000.0)

        # 3. Simulate Actual Handler Execution
        base_ms = func["base_exec_ms"]
        jitter = random.uniform(-3.0, 5.0)
        execution_duration_ms = round(max(5.0, base_ms + jitter), 2)
        time.sleep(execution_duration_ms / 1000.0)

        total_duration_ms = round(init_duration_ms + execution_duration_ms, 2)
        billed_duration_ms = int(total_duration_ms) + 1  # AWS Lambda rounds up to 1ms

        # 4. Compute Micro-Billing
        gb_seconds = (memory_mb / 1024.0) * (billed_duration_ms / 1000.0)
        cost_usd = AWS_LAMBDA_REQUEST_COST + (gb_seconds * AWS_LAMBDA_GB_SECOND_COST)

        with self.lock:
            self.total_billed_cost += cost_usd
            sandbox.touch()

        # Simulated function output
        sample_output = {
            "status": "success",
            "processed_at": int(time.time()),
            "message": f"Processed payload via {func['handler']}"
        }

        invocation_record = {
            "request_id": str(uuid.uuid4()),
            "function_id": function_id,
            "function_name": func["name"],
            "sandbox_id": sandbox.sandbox_id,
            "is_cold_start": is_cold_start,
            "init_duration_ms": init_duration_ms,
            "execution_duration_ms": execution_duration_ms,
            "total_duration_ms": total_duration_ms,
            "billed_duration_ms": billed_duration_ms,
            "memory_allocated_mb": memory_mb,
            "max_memory_used_mb": int(memory_mb * random.uniform(0.32, 0.48)),
            "cost_usd": f"${cost_usd:.8f}",
            "response": sample_output,
            "timestamp": time.strftime("%H:%M:%S")
        }

        with self.lock:
            self.invocation_history.append(invocation_record)

        return invocation_record

    def get_history(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(reversed(self.invocation_history[-50:]))
