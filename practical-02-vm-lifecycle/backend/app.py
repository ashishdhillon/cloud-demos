from flask import Flask, jsonify, request
from vm_hypervisor import VMHypervisor

app = Flask(__name__)
hypervisor = VMHypervisor()

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "vm-lifecycle-hypervisor-engine"})

@app.get("/api/status")
def get_status():
    return jsonify(hypervisor.get_hypervisor_status())

@app.post("/api/vm/provision")
def provision():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "cloud-vm-node-02")
    vcpus = data.get("vcpus", 2)
    memory_mb = data.get("memory_mb", 2048)
    disk_gb = data.get("disk_gb", 20)
    cloud_init = data.get("cloud_init_yaml", "")
    res = hypervisor.provision_vm(name, vcpus, memory_mb, disk_gb, cloud_init)
    return jsonify(res)

@app.post("/api/vm/action")
def vm_action():
    data = request.get_json(silent=True) or {}
    vm_id = data.get("vm_id")
    action = data.get("action")

    if action == "start":
        res = hypervisor.start_vm(vm_id)
    elif action == "stop":
        res = hypervisor.stop_vm(vm_id)
    elif action == "pause":
        res = hypervisor.pause_vm(vm_id)
    elif action == "resume":
        res = hypervisor.resume_vm(vm_id)
    elif action == "reboot":
        res = hypervisor.reboot_vm(vm_id)
    elif action == "terminate":
        res = hypervisor.terminate_vm(vm_id)
    else:
        return jsonify({"error": f"Invalid action '{action}'"}), 400

    return jsonify(res)

@app.post("/api/vm/resize")
def resize():
    data = request.get_json(silent=True) or {}
    vm_id = data.get("vm_id")
    vcpus = data.get("vcpus", 2)
    memory_mb = data.get("memory_mb", 2048)
    disk_gb = data.get("disk_gb", 20)
    res = hypervisor.resize_vm(vm_id, vcpus, memory_mb, disk_gb)
    return jsonify(res)

@app.post("/api/vm/snapshot")
def create_snapshot():
    data = request.get_json(silent=True) or {}
    vm_id = data.get("vm_id")
    name = data.get("name", "manual-snapshot")
    res = hypervisor.create_snapshot(vm_id, name)
    return jsonify(res)

@app.post("/api/vm/restore-snapshot")
def restore_snapshot():
    data = request.get_json(silent=True) or {}
    vm_id = data.get("vm_id")
    name = data.get("name")
    res = hypervisor.restore_snapshot(vm_id, name)
    return jsonify(res)

@app.post("/api/vm/exec")
def exec_guest():
    data = request.get_json(silent=True) or {}
    vm_id = data.get("vm_id")
    cmd = data.get("command", "uname -a")
    res = hypervisor.exec_guest_command(vm_id, cmd)
    return jsonify(res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
