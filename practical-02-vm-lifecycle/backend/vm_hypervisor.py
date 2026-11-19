import datetime
import random
import re
import threading
import time
import uuid
import yaml

DEFAULT_CLOUD_INIT = """#cloud-config
# Cloud-Init Bootstrap Manifest for Ubuntu IaaS Virtual Machine
hostname: cloud-vm-node-01
manage_etc_hosts: true

users:
  - name: cloud-admin
    gecos: Cloud Systems Administrator
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: [adm, sudo, docker]
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKeyForCloudDevs2026 admin@cloud-infra

package_update: true
package_upgrade: false

packages:
  - nginx
  - curl
  - htop
  - net-tools

write_files:
  - path: /var/www/html/index.html
    owner: www-data:www-data
    permissions: '0644'
    content: |
      <!DOCTYPE html>
      <html>
      <head><title>Cloud VM Instance Active</title></head>
      <body style="font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 40px;">
        <h1 style="color: #38bdf8;">✓ Cloud VM Instance Online</h1>
        <p><strong>Architecture:</strong> IaaS Hypervisor Node (KVM / QEMU)</p>
        <p><strong>Provisioned By:</strong> Automated Cloud-Init Bootstrap</p>
        <p><strong>Status:</strong> HTTP Nginx Service Running</p>
      </body>
      </html>

runcmd:
  - systemctl enable nginx
  - systemctl restart nginx
  - echo "Cloud-Init Provisioning Completed Successfully." > /var/log/cloud-init-custom.log
"""

class VMHypervisor:
    def __init__(self):
        self.lock = threading.RLock()
        
        # Physical Hypervisor Host Specifications
        self.host_specs = {
            "hypervisor_type": "Type-1 Bare-Metal (KVM / Linux QEMU)",
            "host_os": "Linux 6.8.0-31-generic (Enterprise KVM Hypervisor)",
            "cpu_model": "AMD EPYC 9654 (96-Core High-Density Virtualization Processor)",
            "total_cores": 16,
            "total_ram_mb": 65536,  # 64 GB
            "total_disk_gb": 2048,  # 2.0 TB NVMe
            "allocated_cores": 0,
            "allocated_ram_mb": 0,
            "allocated_disk_gb": 0
        }
        
        self.vms = {}
        self.hypervisor_events = []
        self._running = True

        # Pre-seed default VM instance
        self._seed_default_vm()

        # Background metrics ticker
        self.metrics_thread = threading.Thread(target=self._metrics_loop, daemon=True)
        self.metrics_thread.start()

    def _log_event(self, level: str, message: str, vm_name: str = "Host"):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.hypervisor_events.insert(0, {
            "time": now,
            "level": level,
            "vm": vm_name,
            "message": message
        })
        if len(self.hypervisor_events) > 50:
            self.hypervisor_events.pop()

    def _recalculate_host_allocation(self):
        allocated_cores = sum(v["vcpus"] for v in self.vms.values() if v["state"] != "Terminated")
        allocated_ram = sum(v["memory_mb"] for v in self.vms.values() if v["state"] != "Terminated")
        allocated_disk = sum(v["disk_gb"] for v in self.vms.values() if v["state"] != "Terminated")

        self.host_specs["allocated_cores"] = allocated_cores
        self.host_specs["allocated_ram_mb"] = allocated_ram
        self.host_specs["allocated_disk_gb"] = allocated_disk

    def _seed_default_vm(self):
        with self.lock:
            vm_id = "vm-" + uuid.uuid4().hex[:8]
            default_vm = {
                "id": vm_id,
                "name": "cloud-vm-node-01",
                "state": "Running",  # Provisioning, Running, Suspended, Stopped, Terminated
                "vcpus": 2,
                "memory_mb": 2048,
                "disk_gb": 20,
                "os_image": "Ubuntu 24.04 LTS (Noble Numbat)",
                "ip_address": "192.168.122.45",
                "mac_address": "52:54:00:8b:39:a1",
                "uptime_seconds": 128,
                "cpu_usage_pct": 3.8,
                "ram_usage_mb": 460,
                "cloud_init_yaml": DEFAULT_CLOUD_INIT.strip(),
                "cloud_init_status": "Done (Provisioned)",
                "cloud_init_logs": [
                    "[cloud-init-local] Discovered data source: NoCloud",
                    "[cloud-init-local] Network configured: static 192.168.122.45/24 via virbr0",
                    "[cloud-init] Creating user cloud-admin with sudo privileges",
                    "[cloud-init] Injecting SSH authorized ed25519 public key",
                    "[cloud-init] Package update & installing: nginx, curl, htop, net-tools",
                    "[cloud-init] Wrote /var/www/html/index.html (Permissions: 0644)",
                    "[cloud-init] Executing runcmd: systemctl restart nginx",
                    "[cloud-init-final] Bootstrap sequence completed in 4.2 seconds."
                ],
                "snapshots": [
                    {
                        "name": "baseline-post-cloud-init",
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "size_mb": 145,
                        "description": "Clean state with Nginx active"
                    }
                ]
            }
            self.vms[vm_id] = default_vm
            self._recalculate_host_allocation()
            self._log_event("INFO", f"Hypervisor initialized: Virtual Machine '{default_vm['name']}' online.", default_vm["name"])

    def _metrics_loop(self):
        while self._running:
            time.sleep(1.0)
            with self.lock:
                for vm in self.vms.values():
                    if vm["state"] == "Running":
                        vm["uptime_seconds"] += 1
                        # Realistic gentle fluctuation
                        vm["cpu_usage_pct"] = round(random.uniform(2.5, 8.5), 1)
                        vm["ram_usage_mb"] = min(vm["memory_mb"], max(350, int(vm["memory_mb"] * 0.25) + random.randint(-15, 25)))
                    elif vm["state"] == "Suspended":
                        vm["cpu_usage_pct"] = 0.0
                    elif vm["state"] == "Stopped":
                        vm["cpu_usage_pct"] = 0.0
                        vm["ram_usage_mb"] = 0

    def get_hypervisor_status(self):
        with self.lock:
            vm_list = []
            for vm in self.vms.values():
                uptime_sec = vm["uptime_seconds"]
                uptime_str = f"{uptime_sec}s" if uptime_sec < 60 else f"{uptime_sec // 60}m {uptime_sec % 60}s"
                vm_list.append({
                    **vm,
                    "uptime_formatted": uptime_str
                })

            return {
                "host_specs": self.host_specs,
                "vms": vm_list,
                "events": self.hypervisor_events[:25]
            }

    def provision_vm(self, name: str, vcpus: int, memory_mb: int, disk_gb: int, cloud_init: str):
        with self.lock:
            # Resource bounds validation
            vcpus = max(1, min(8, int(vcpus)))
            memory_mb = max(512, min(8192, int(memory_mb)))
            disk_gb = max(10, min(100, int(disk_gb)))

            # Capacity check
            if (self.host_specs["allocated_cores"] + vcpus) > self.host_specs["total_cores"]:
                return {"error": "Insufficient Hypervisor host CPU capacity"}
            if (self.host_specs["allocated_ram_mb"] + memory_mb) > self.host_specs["total_ram_mb"]:
                return {"error": "Insufficient Hypervisor host RAM capacity"}

            vm_id = "vm-" + uuid.uuid4().hex[:8]
            clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', name.strip()) or f"cloud-vm-{len(self.vms)+1}"
            ip = f"192.168.122.{random.randint(50, 240)}"
            mac = "52:54:00:" + ":".join([f"{random.randint(0, 255):02x}" for _ in range(3)])

            new_vm = {
                "id": vm_id,
                "name": clean_name,
                "state": "Provisioning",
                "vcpus": vcpus,
                "memory_mb": memory_mb,
                "disk_gb": disk_gb,
                "os_image": "Ubuntu 24.04 LTS (Noble Numbat)",
                "ip_address": ip,
                "mac_address": mac,
                "uptime_seconds": 0,
                "cpu_usage_pct": 0.0,
                "ram_usage_mb": 0,
                "cloud_init_yaml": cloud_init.strip() if cloud_init else DEFAULT_CLOUD_INIT.strip(),
                "cloud_init_status": "Executing Bootstrap...",
                "cloud_init_logs": ["[hypervisor] Creating QEMU/KVM virtual machine container"],
                "snapshots": []
            }
            self.vms[vm_id] = new_vm
            self._recalculate_host_allocation()
            self._log_event("INFO", f"Hypervisor context created: {clean_name} ({vcpus} vCPU, {memory_mb} MB RAM)", clean_name)

            # Asynchronous cloud-init bootstrap worker
            threading.Thread(target=self._run_cloud_init_bootstrap, args=(vm_id,), daemon=True).start()
            return {"success": True, "vm_id": vm_id, "vm": new_vm}

    def _run_cloud_init_bootstrap(self, vm_id: str):
        steps = [
            "[bios] Hypervisor UEFI firmware POST passed. Initializing ACPI tables...",
            "[kernel] Booting Linux 6.8.0-31-generic with SMP enabled.",
            "[systemd] Reached target System Initialization.",
            "[cloud-init-local] Ingesting /var/lib/cloud/seed/nocloud-net/user-data...",
            "[cloud-init] Creating user cloud-admin and injecting SSH public keys.",
            "[cloud-init] Updating apt cache and installing requested packages: nginx, curl.",
            "[cloud-init] Rendering /var/www/html/index.html custom payload.",
            "[cloud-init-final] Cloud-Init bootstrap completed successfully. In-guest services active!"
        ]

        for s in steps:
            time.sleep(0.4)
            with self.lock:
                if vm_id in self.vms:
                    self.vms[vm_id]["cloud_init_logs"].append(s)

        with self.lock:
            if vm_id in self.vms:
                self.vms[vm_id]["state"] = "Running"
                self.vms[vm_id]["cloud_init_status"] = "Done (Provisioned)"
                self.vms[vm_id]["ram_usage_mb"] = 380
                self._log_event("SUCCESS", f"Virtual machine '{self.vms[vm_id]['name']}' is now RUNNING.", self.vms[vm_id]["name"])

    def start_vm(self, vm_id: str):
        with self.lock:
            if vm_id not in self.vms:
                return {"error": "VM not found"}
            vm = self.vms[vm_id]
            if vm["state"] == "Running":
                return {"error": "VM is already running"}
            vm["state"] = "Running"
            self._log_event("INFO", f"ACPI Power-On signal delivered to VM '{vm['name']}'.", vm["name"])
            return {"success": True, "state": "Running"}

    def stop_vm(self, vm_id: str):
        with self.lock:
            if vm_id not in self.vms:
                return {"error": "VM not found"}
            vm = self.vms[vm_id]
            if vm["state"] == "Stopped":
                return {"error": "VM is already stopped"}
            vm["state"] = "Stopped"
            vm["cpu_usage_pct"] = 0.0
            vm["ram_usage_mb"] = 0
            self._log_event("INFO", f"ACPI Graceful Shutdown completed on VM '{vm['name']}'.", vm["name"])
            return {"success": True, "state": "Stopped"}

    def pause_vm(self, vm_id: str):
        with self.lock:
            if vm_id not in self.vms:
                return {"error": "VM not found"}
            vm = self.vms[vm_id]
            if vm["state"] != "Running":
                return {"error": "Only running VMs can be suspended"}
            vm["state"] = "Suspended"
            vm["cpu_usage_pct"] = 0.0
            self._log_event("INFO", f"Hypervisor suspended vCPU execution; RAM state preserved for '{vm['name']}'.", vm["name"])
            return {"success": True, "state": "Suspended"}

    def resume_vm(self, vm_id: str):
        with self.lock:
            if vm_id not in self.vms:
                return {"error": "VM not found"}
            vm = self.vms[vm_id]
            if vm["state"] != "Suspended":
                return {"error": "Only suspended VMs can be resumed"}
            vm["state"] = "Running"
            self._log_event("INFO", f"Hypervisor resumed vCPU execution for '{vm['name']}'.", vm["name"])
            return {"success": True, "state": "Running"}

    def reboot_vm(self, vm_id: str):
        with self.lock:
            if vm_id not in self.vms:
                return {"error": "VM not found"}
            vm = self.vms[vm_id]
            vm["state"] = "Rebooting"
            vm["uptime_seconds"] = 0
            self._log_event("INFO", f"ACPI Warm Reboot signal sent to '{vm['name']}'.", vm["name"])

            def finish_reboot():
                time.sleep(1.5)
                with self.lock:
                    if vm_id in self.vms:
                        self.vms[vm_id]["state"] = "Running"
                        self._log_event("SUCCESS", f"VM '{self.vms[vm_id]['name']}' reboot cycle complete. All services online.", self.vms[vm_id]["name"])

            threading.Thread(target=finish_reboot, daemon=True).start()
            return {"success": True, "state": "Rebooting"}

    def resize_vm(self, vm_id: str, vcpus: int, memory_mb: int, disk_gb: int):
        with self.lock:
            if vm_id not in self.vms:
                return {"error": "VM not found"}
            vm = self.vms[vm_id]
            if vm["state"] == "Running":
                return {"error": "VM must be stopped before resizing hardware specifications (or use hotplug)"}

            vm["vcpus"] = max(1, min(8, int(vcpus)))
            vm["memory_mb"] = max(512, min(8192, int(memory_mb)))
            vm["disk_gb"] = max(vm["disk_gb"], int(disk_gb))  # Disks can only grow, not shrink
            self._recalculate_host_allocation()
            self._log_event("INFO", f"Resized VM '{vm['name']}' hardware: {vm['vcpus']} vCPU, {vm['memory_mb']} MB RAM, {vm['disk_gb']} GB Disk.", vm["name"])
            return {"success": True, "vm": vm}

    def create_snapshot(self, vm_id: str, snap_name: str):
        with self.lock:
            if vm_id not in self.vms:
                return {"error": "VM not found"}
            vm = self.vms[vm_id]
            clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', snap_name.strip()) or f"snap-{len(vm['snapshots'])+1}"
            
            snap = {
                "name": clean_name,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "size_mb": random.randint(110, 220),
                "vcpus": vm["vcpus"],
                "memory_mb": vm["memory_mb"],
                "disk_gb": vm["disk_gb"],
                "state_at_snapshot": vm["state"]
            }
            vm["snapshots"].append(snap)
            self._log_event("SUCCESS", f"Created Hypervisor point-in-time snapshot '{clean_name}' ({snap['size_mb']} MB).", vm["name"])
            return {"success": True, "snapshot": snap}

    def restore_snapshot(self, vm_id: str, snap_name: str):
        with self.lock:
            if vm_id not in self.vms:
                return {"error": "VM not found"}
            vm = self.vms[vm_id]
            match = next((s for s in vm["snapshots"] if s["name"] == snap_name), None)
            if not match:
                return {"error": f"Snapshot '{snap_name}' not found"}

            vm["vcpus"] = match["vcpus"]
            vm["memory_mb"] = match["memory_mb"]
            vm["disk_gb"] = match["disk_gb"]
            vm["state"] = match["state_at_snapshot"]
            self._recalculate_host_allocation()
            self._log_event("SUCCESS", f"Reverted VM '{vm['name']}' to snapshot '{snap_name}'.", vm["name"])
            return {"success": True, "message": f"VM rolled back to snapshot {snap_name}"}

    def terminate_vm(self, vm_id: str):
        with self.lock:
            if vm_id not in self.vms:
                return {"error": "VM not found"}
            vm = self.vms[vm_id]
            name = vm["name"]
            vm["state"] = "Terminated"
            del self.vms[vm_id]
            self._recalculate_host_allocation()
            self._log_event("WARNING", f"VM '{name}' deallocated and storage reclaimed by Hypervisor.", name)
            return {"success": True, "terminated": name}

    def exec_guest_command(self, vm_id: str, command: str):
        """Simulates in-guest terminal commands on the virtual machine."""
        with self.lock:
            if vm_id not in self.vms:
                return {"error": "VM not found"}
            vm = self.vms[vm_id]
            if vm["state"] != "Running":
                return {"error": f"Cannot execute command: VM '{vm['name']}' is {vm['state'].upper()} (Must be RUNNING)"}

            cmd = command.strip()
            name = vm["name"]
            ip = vm["ip_address"]
            vcpus = vm["vcpus"]
            mem_mb = vm["memory_mb"]
            disk_gb = vm["disk_gb"]

            if cmd == "uname -a":
                out = f"Linux {name} 6.8.0-31-generic #31-Ubuntu SMP PREEMPT_DYNAMIC x86_64 x86_64 x86_64 GNU/Linux"
            elif cmd == "lscpu":
                out = (
                    f"Architecture:            x86_64\n"
                    f"  CPU op-mode(s):        32-bit, 64-bit\n"
                    f"  Address sizes:         48 bits physical, 48 bits virtual\n"
                    f"  Byte Order:            Little Endian\n"
                    f"CPU(s):                  {vcpus}\n"
                    f"  On-line CPU(s) list:   0-{vcpus-1}\n"
                    f"Vendor ID:               AuthenticAMD\n"
                    f"  Model name:            QEMU Virtual CPU version 2.5+\n"
                    f"  CPU family:            6\n"
                    f"Hypervisor vendor:       KVM\n"
                    f"Virtualization type:     full"
                )
            elif cmd == "free -m" or cmd == "free -h":
                used = vm["ram_usage_mb"]
                free = mem_mb - used
                out = (
                    f"               total        used        free      shared  buff/cache   available\n"
                    f"Mem:            {mem_mb}         {used}         {free}           8         112        {free-50}\n"
                    f"Swap:           2048           0        2048"
                )
            elif cmd == "df -h":
                out = (
                    f"Filesystem      Size  Used Avail Use% Mounted on\n"
                    f"udev            980M     0  980M   0% /dev\n"
                    f"tmpfs           200M  1.2M  199M   1% /run\n"
                    f"/dev/vda1        {disk_gb}G  3.1G   {disk_gb-4}G  18% /\n"
                    f"tmpfs           1000M     0 1000M   0% /dev/shm"
                )
            elif cmd.startswith("ip ") or cmd == "ifconfig":
                out = (
                    f"1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN\n"
                    f"    inet 127.0.0.1/8 scope host lo\n"
                    f"2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP\n"
                    f"    link/ether {vm['mac_address']} brd ff:ff:ff:ff:ff:ff\n"
                    f"    inet {ip}/24 brd 192.168.122.255 scope global dynamic eth0"
                )
            elif "systemctl status nginx" in cmd:
                out = (
                    f"● nginx.service - A high performance web server and a reverse proxy server\n"
                    f"     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; preset: enabled)\n"
                    f"     Active: active (running) since {datetime.datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')}; {vm['uptime_seconds']}s ago\n"
                    f"    Process: 612 ExecStartPost=/bin/sleep 0.1 (code=exited, status=0/SUCCESS)\n"
                    f"   Main PID: 611 (nginx)\n"
                    f"      Tasks: 2 (limit: 2321)\n"
                    f"     Memory: 6.8M\n"
                    f"        CPU: 18ms\n"
                    f"     CGroup: /system.slice/nginx.service\n"
                    f"             ├─611 \"nginx: master process /usr/sbin/nginx -g daemon on; master_process on;\"\n"
                    f"             └─613 \"nginx: worker process\""
                )
            elif "curl http://localhost" in cmd or "curl http://127.0.0.1" in cmd:
                out = (
                    f"HTTP/1.1 200 OK\n"
                    f"Server: nginx/1.24.0 (Ubuntu)\n"
                    f"Content-Type: text/html\n"
                    f"Content-Length: 382\n\n"
                    f"<!DOCTYPE html>\n"
                    f"<html>\n"
                    f"<head><title>Cloud VM Instance Active</title></head>\n"
                    f"<body>\n"
                    f"  <h1>✓ Cloud VM Instance Online</h1>\n"
                    f"  <p>Host: {name} (IP: {ip})</p>\n"
                    f"  <p>Hypervisor-managed Ubuntu Instance initialized via Cloud-Init</p>\n"
                    f"  <p>Hardware: {vcpus} vCPU, {mem_mb} MB RAM</p>\n"
                    f"</body>\n"
                    f"</html>"
                )
            else:
                out = f"root@{name}:~# {cmd}\nCommand executed successfully."

            return {"command": cmd, "output": out}
