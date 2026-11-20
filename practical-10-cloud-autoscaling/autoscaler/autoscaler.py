import json
import os
import threading
import time
from collections import deque
from datetime import datetime
from queue import Empty, Queue
from typing import Any

from flask import Flask, Response, jsonify, request

from docker_manager import DockerManager

MIN_INSTANCES = int(os.environ.get("MIN_INSTANCES", "2"))
MAX_INSTANCES = int(os.environ.get("MAX_INSTANCES", "5"))
CAPACITY_PER_INSTANCE = int(os.environ.get("CAPACITY_PER_MINUTE", "20"))
SCALE_OUT_THRESHOLD = float(os.environ.get("SCALE_OUT_THRESHOLD", "80"))
SCALE_IN_THRESHOLD = float(os.environ.get("SCALE_IN_THRESHOLD", "20"))
SCALING_COOLDOWN = float(os.environ.get("SCALING_COOLDOWN", "10"))
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "2"))
dm = DockerManager()
app = Flask(__name__)

config = {
    "min_instances": MIN_INSTANCES,
    "max_instances": MAX_INSTANCES,
    "capacity_per_instance": CAPACITY_PER_INSTANCE,
    "scale_out_threshold": SCALE_OUT_THRESHOLD,
    "scale_in_threshold": SCALE_IN_THRESHOLD,
    "scaling_cooldown": SCALING_COOLDOWN,
}

state = {
    "scaling_status": "steady",
    "incoming_rpm": 0,
    "last_avg_utilization": 0.0,
    "total_requests_window": 0,
}

events: deque = deque(maxlen=500)
event_queues: list[Queue] = []
events_lock = threading.Lock()
config_lock = threading.Lock()
scale_lock = threading.Lock()

last_scale_at = 0.0
low_load_since: float | None = None


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log_event(message: str) -> None:
    line = f"[{timestamp()}] {message}"
    with events_lock:
        events.append(line)
        dead = []
        for q in event_queues:
            try:
                q.put_nowait(line)
            except Exception:
                dead.append(q)
        for q in dead:
            if q in event_queues:
                event_queues.remove(q)
    print(line, flush=True)


def subscribe_events() -> Queue:
    q: Queue = Queue(maxsize=200)
    with events_lock:
        for line in events:
            try:
                q.put_nowait(line)
            except Exception:
                break
        event_queues.append(q)
    return q


def collect_metrics() -> tuple[list[dict[str, Any]], float, int]:
    containers = dm.list_app_containers()
    stats_list = []
    utils = []
    total_requests = 0
    for c in containers:
        s = dm.fetch_stats(c)
        if s is None:
            s = {
                "container_name": c.name,
                "container_id": c.short_id,
                "instance_name": c.name,
                "instance_id": c.name,
                "requests_last_60s": 0,
                "capacity": config["capacity_per_instance"],
                "utilization_percent": 0.0,
                "status": c.status,
            }
        stats_list.append(s)
        total_requests += int(s.get("requests_last_60s", 0))
        utils.append(float(s.get("utilization_percent", 0)))
    avg = round(sum(utils) / len(utils), 2) if utils else 0.0
    return stats_list, avg, total_requests


def one_fewer_can_absorb_load(total_requests: int, count: int) -> bool:
    if count <= config["min_instances"]:
        return False
    cap = config["capacity_per_instance"]
    headroom = config["scale_out_threshold"] / 100.0
    ceiling = (count - 1) * cap * headroom
    return total_requests <= ceiling


def perform_scale_out() -> bool:
    global last_scale_at
    with scale_lock:
        if dm.is_scale_locked():
            return False
        dm.set_scale_lock(True)
        try:
            containers = dm.list_app_containers()
            if len(containers) >= config["max_instances"]:
                log_event("Maximum instance limit reached; cannot scale out.")
                state["scaling_status"] = "at_max"
                return False
            name = dm.next_instance_name()
            log_event("Creating new instance...")
            container = dm.create_app_container(name)
            log_event(f"Instance {name} started.")
            if not dm.wait_healthy(container):
                log_event(f"Instance {name} failed health check; removing.")
                dm.remove_app_container(container)
                return False
            container.reload()
            refreshed = dm.list_app_containers()
            log_event("Updating Nginx configuration.")
            if not dm.update_nginx(refreshed):
                log_event("Nginx reload failed after scale out.")
                dm.remove_app_container(container)
                dm.update_nginx(dm.list_app_containers())
                return False
            log_event("Nginx reloaded successfully.")
            log_event(f"Scaled out successfully. Active instances: {len(refreshed)}.")
            last_scale_at = time.time()
            state["scaling_status"] = "scaled_out"
            return True
        except Exception as exc:
            log_event(f"Scale out error: {exc}")
            return False
        finally:
            dm.set_scale_lock(False)


def perform_scale_in() -> bool:
    global last_scale_at
    with scale_lock:
        if dm.is_scale_locked():
            return False
        dm.set_scale_lock(True)
        try:
            containers = dm.list_app_containers()
            if len(containers) <= config["min_instances"]:
                return False
            target = dm.pick_scale_in_target(containers, config["min_instances"])
            if target is None:
                return False
            name = target.name
            log_event(f"Terminating scaled instance {name}.")
            remaining = [c for c in containers if c.id != target.id]
            log_event("Updating Nginx configuration.")
            if not dm.update_nginx(remaining):
                log_event("Nginx update failed; aborting scale in.")
                return False
            log_event("Nginx configuration updated.")
            dm.remove_app_container(target)
            log_event(f"Scaled in successfully. Active instances: {len(remaining)}.")
            last_scale_at = time.time()
            state["scaling_status"] = "scaled_in"
            return True
        except Exception as exc:
            log_event(f"Scale in error: {exc}")
            return False
        finally:
            dm.set_scale_lock(False)


def monitor_loop() -> None:
    global low_load_since, last_scale_at
    time.sleep(3)
    refreshed = dm.list_app_containers()
    dm.update_nginx(refreshed)
    log_event("Autoscaler started.")
    log_event(f"Minimum instances: {config['min_instances']}.")
    log_event(f"Maximum instances: {config['max_instances']}.")
    while True:
        try:
            _, avg, total_requests = collect_metrics()
            state["last_avg_utilization"] = avg
            state["total_requests_window"] = total_requests
            state["incoming_rpm"] = total_requests
            now = time.time()
            since_scale = now - last_scale_at
            containers = dm.list_app_containers()
            count = len(containers)

            if avg > config["scale_out_threshold"] and since_scale >= config["scaling_cooldown"]:
                if count < config["max_instances"]:
                    log_event("HIGH LOAD DETECTED.")
                    log_event(f"Average utilization: {avg}%.")
                    perform_scale_out()
                    low_load_since = None
                else:
                    state["scaling_status"] = "at_max"
            else:
                scale_in_due_to_util = avg < config["scale_in_threshold"]
                scale_in_due_to_headroom = one_fewer_can_absorb_load(total_requests, count)
                if (
                    count > config["min_instances"]
                    and (scale_in_due_to_util or scale_in_due_to_headroom)
                ):
                    if low_load_since is None:
                        low_load_since = now
                    if (
                        now - low_load_since >= config["scaling_cooldown"]
                        and since_scale >= config["scaling_cooldown"]
                    ):
                        if scale_in_due_to_headroom and not scale_in_due_to_util:
                            log_event("EXCESS CAPACITY DETECTED.")
                            log_event(
                                f"Total requests (60s): {total_requests}; "
                                f"{count - 1} instances can stay under "
                                f"{config['scale_out_threshold']}% utilization."
                            )
                        else:
                            log_event("LOW LOAD DETECTED.")
                            log_event(f"Average utilization: {avg}%.")
                        perform_scale_in()
                        low_load_since = None
                    else:
                        state["scaling_status"] = "low_load"
                else:
                    low_load_since = None
                    if state["scaling_status"] not in ("scaled_out", "scaled_in"):
                        state["scaling_status"] = "steady"
                    else:
                        state["scaling_status"] = "steady"

        except Exception as exc:
            log_event(f"Monitor error: {exc}")
        time.sleep(POLL_INTERVAL)


@app.get("/api/status")
def api_status():
    instances, avg, total = collect_metrics()
    with config_lock:
        cfg = dict(config)
    now = time.time()
    since_scale = now - last_scale_at
    cooldown_rem = max(0, int(cfg["scaling_cooldown"] - since_scale)) if since_scale < cfg["scaling_cooldown"] else 0
    return jsonify(
        {
            "active_instances": len(instances),
            "min_instances": cfg["min_instances"],
            "max_instances": cfg["max_instances"],
            "capacity_per_instance": cfg["capacity_per_instance"],
            "total_capacity": cfg["capacity_per_instance"] * len(instances),
            "incoming_rpm": total,
            "scaling_status": state["scaling_status"],
            "average_utilization": avg,
            "scale_out_threshold": cfg["scale_out_threshold"],
            "scale_in_threshold": cfg["scale_in_threshold"],
            "scaling_cooldown": cfg["scaling_cooldown"],
            "cooldown_remaining": cooldown_rem,
        }
    )


@app.get("/api/instances")
def api_instances():
    instances, _, _ = collect_metrics()
    return jsonify({"instances": instances})


@app.post("/api/config")
def api_config():
    data = request.get_json(silent=True) or {}
    with config_lock:
        if "min_instances" in data:
            config["min_instances"] = max(1, int(data["min_instances"]))
        if "max_instances" in data:
            config["max_instances"] = max(config["min_instances"], int(data["max_instances"]))
    log_event(f"Configuration updated. Min: {config['min_instances']}, Max: {config['max_instances']}.")
    return jsonify(config)


@app.get("/api/events")
def api_events():
    def stream():
        q = subscribe_events()
        try:
            while True:
                try:
                    line = q.get(timeout=25)
                    yield f"data: {json.dumps({'message': line})}\n\n"
                except Empty:
                    yield ": keepalive\n\n"
        finally:
            with events_lock:
                if q in event_queues:
                    event_queues.remove(q)

    return Response(stream(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    threading.Thread(target=monitor_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=9000, threaded=True)