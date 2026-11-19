import os
import re
import time
from typing import Any

import docker
import requests

APP_LABEL = "autoscale.role"
APP_LABEL_VALUE = "app"
APP_PORT = int(os.environ.get("APP_PORT", "5000"))
APP_IMAGE = os.environ.get("APP_IMAGE", "autoscale-app:latest")
DOCKER_NETWORK = os.environ.get("DOCKER_NETWORK", "autoscale-net")
NGINX_CONTAINER = os.environ.get("NGINX_CONTAINER", "autoscale-nginx")
UPSTREAM_PATH = os.environ.get("UPSTREAM_PATH", "/shared/upstream.conf")
CAPACITY_PER_MINUTE = os.environ.get("CAPACITY_PER_MINUTE", "20")
APP_NAME_PREFIX = os.environ.get("APP_NAME_PREFIX", "app-")


class DockerManager:
    def __init__(self) -> None:
        self.client = docker.from_env()
        self._scale_lock = False

    def set_scale_lock(self, value: bool) -> None:
        self._scale_lock = value

    def is_scale_locked(self) -> bool:
        return self._scale_lock

    def list_app_containers(self) -> list[Any]:
        containers = self.client.containers.list(
            filters={"label": f"{APP_LABEL}={APP_LABEL_VALUE}"}
        )
        return sorted(containers, key=lambda c: self._sort_key(c.name))

    def _sort_key(self, name: str) -> tuple[int, str]:
        m = re.match(r"app-(\d+)$", name)
        if m:
            return (int(m.group(1)), name)
        return (999999, name)

    def next_instance_name(self) -> str:
        containers = self.list_app_containers()
        numbers = []
        for c in containers:
            m = re.match(r"app-(\d+)$", c.name)
            if m:
                numbers.append(int(m.group(1)))
        n = max(numbers) + 1 if numbers else 1
        while True:
            name = f"{APP_NAME_PREFIX}{n}"
            try:
                self.client.containers.get(name)
                n += 1
            except docker.errors.NotFound:
                return name

    def wait_healthy(self, container: Any, timeout: float = 60.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            container.reload()
            health = container.attrs.get("State", {}).get("Health", {}).get("Status")
            if health == "healthy":
                return True
            if health is None:
                try:
                    r = requests.get(
                        f"http://{container.name}:{APP_PORT}/health",
                        timeout=2,
                    )
                    if r.status_code == 200:
                        return True
                except requests.RequestException:
                    pass
            time.sleep(1)
        return False

    def fetch_stats(self, container: Any) -> dict[str, Any] | None:
        try:
            r = requests.get(
                f"http://{container.name}:{APP_PORT}/stats",
                timeout=3,
            )
            if r.status_code != 200:
                return None
            data = r.json()
            data["container_id"] = container.short_id
            data["container_name"] = container.name
            data["status"] = container.status
            return data
        except (requests.RequestException, ValueError):
            return None

    def create_app_container(self, name: str) -> Any:
        return self.client.containers.run(
            image=APP_IMAGE,
            name=name,
            network=DOCKER_NETWORK,
            detach=True,
            labels={APP_LABEL: APP_LABEL_VALUE},
            environment={
                "INSTANCE_NAME": name,
                "INSTANCE_ID": name,
                "CAPACITY_PER_MINUTE": CAPACITY_PER_MINUTE,
            },
        )

    def remove_app_container(self, container: Any) -> None:
        try:
            container.stop(timeout=10)
        except docker.errors.APIError:
            pass
        try:
            container.remove(force=True)
        except docker.errors.APIError:
            pass

    def write_upstream(self, containers: list[Any]) -> None:
        lines = ["upstream backend {"]
        for c in containers:
            lines.append(f"    server {c.name}:{APP_PORT};")
        lines.append("}")
        lines.append("")
        content = "\n".join(lines)
        os.makedirs(os.path.dirname(UPSTREAM_PATH), exist_ok=True)
        with open(UPSTREAM_PATH, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

    def reload_nginx(self) -> bool:
        try:
            nginx = self.client.containers.get(NGINX_CONTAINER)
            code, _ = nginx.exec_run(["nginx", "-t"])
            if code != 0:
                return False
            code, _ = nginx.exec_run(["nginx", "-s", "reload"])
            return code == 0
        except docker.errors.APIError:
            return False

    def update_nginx(self, containers: list[Any]) -> bool:
        self.write_upstream(containers)
        return self.reload_nginx()

    def pick_scale_in_target(self, containers: list[Any], min_instances: int) -> Any | None:
        if len(containers) <= min_instances:
            return None
        scaled = []
        for c in containers:
            m = re.match(r"app-(\d+)$", c.name)
            if m and int(m.group(1)) > min_instances:
                scaled.append(c)
        if not scaled:
            extras = containers[min_instances:]
            if not extras:
                return None
            return sorted(extras, key=lambda c: self._sort_key(c.name), reverse=True)[0]
        return sorted(scaled, key=lambda c: self._sort_key(c.name), reverse=True)[0]