let currentStatus = null;
let activeVmId = null;

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initEventListeners();
    fetchStatus();
    setInterval(fetchStatus, 1000);
});

function initTabs() {
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(tc => tc.style.display = "none");

            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            document.getElementById(targetId).style.display = "flex";
        });
    });
}

function initEventListeners() {
    // Provision toggle
    document.getElementById("btnToggleProvisionForm").addEventListener("click", () => {
        const box = document.getElementById("provisionFormBox");
        box.style.display = (box.style.display === "none") ? "flex" : "none";
    });
    document.getElementById("btnCancelProvision").addEventListener("click", () => {
        document.getElementById("provisionFormBox").style.display = "none";
    });

    // Provision Submit
    document.getElementById("btnSubmitProvision").addEventListener("click", submitProvision);

    // Console quick command buttons
    document.querySelectorAll(".btn-console-cmd").forEach(btn => {
        btn.addEventListener("click", () => {
            const cmd = btn.getAttribute("data-cmd");
            execCommand(cmd);
        });
    });

    // Console Input prompt
    document.getElementById("btnConsoleSend").addEventListener("click", () => {
        const input = document.getElementById("consoleInput");
        if (input.value.trim()) {
            execCommand(input.value.trim());
            input.value = "";
        }
    });

    document.getElementById("consoleInput").addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            const input = document.getElementById("consoleInput");
            if (input.value.trim()) {
                execCommand(input.value.trim());
                input.value = "";
            }
        }
    });

    // Resize Modal
    document.getElementById("btnCancelResize").addEventListener("click", () => {
        document.getElementById("resizeModal").style.display = "none";
    });
    document.getElementById("btnSubmitResize").addEventListener("click", submitResize);
}

async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();
        currentStatus = data;
        renderDashboard(data);
    } catch (err) {
        console.error("Failed to fetch hypervisor status:", err);
    }
}

function renderDashboard(data) {
    const host = data.host_specs;
    document.getElementById("statCpuAlloc").innerText = `${host.allocated_cores} / ${host.total_cores} Cores`;
    document.getElementById("statRamAlloc").innerText = `${(host.allocated_ram_mb / 1024).toFixed(1)} / ${(host.total_ram_mb / 1024).toFixed(1)} GiB`;
    document.getElementById("statDiskAlloc").innerText = `${host.allocated_disk_gb} / ${host.total_disk_gb} GB`;
    document.getElementById("statVmCount").innerText = `${data.vms.filter(v => v.state === "Running").length} Online`;

    // Ensure active VM selection
    if (!activeVmId && data.vms.length > 0) {
        activeVmId = data.vms[0].id;
    } else if (activeVmId && !data.vms.some(v => v.id === activeVmId)) {
        activeVmId = data.vms.length > 0 ? data.vms[0].id : null;
    }

    renderVmCards(data.vms);
    renderActiveVmDetails();
    renderEvents(data.events);
}

function renderVmCards(vms) {
    const container = document.getElementById("vmCardsList");
    container.innerHTML = "";

    if (vms.length === 0) {
        container.innerHTML = `<div class="text-muted" style="padding: 24px; text-align: center;">No VMs provisioned. Click "Provision New VM" above.</div>`;
        return;
    }

    vms.forEach(vm => {
        const card = document.createElement("div");
        card.className = "vm-card" + (vm.id === activeVmId ? " selected-vm" : "");
        card.onclick = (e) => {
            if (e.target.tagName !== "BUTTON" && !e.target.closest("button")) {
                activeVmId = vm.id;
                renderVmCards(vms);
                renderActiveVmDetails();
            }
        };

        const stateClass = `state-${vm.state.toLowerCase()}`;

        card.innerHTML = `
            <div class="vm-top-bar">
                <div class="vm-title-group">
                    <span class="vm-name">${vm.name}</span>
                    <span class="state-badge ${stateClass}">${vm.state}</span>
                </div>
                <div class="text-sm text-muted">
                    Uptime: <strong>${vm.uptime_formatted}</strong>
                </div>
            </div>

            <div class="vm-info-grid">
                <div>IP Address: <strong>${vm.ip_address}</strong></div>
                <div>Hardware: <strong>${vm.vcpus} vCPU · ${vm.memory_mb} MB</strong></div>
                <div>Disk: <strong>${vm.disk_gb} GB NVMe</strong></div>
                <div>CPU Usage: <strong>${vm.cpu_usage_pct}%</strong></div>
                <div>RAM Usage: <strong>${vm.ram_usage_mb} MB</strong></div>
                <div>Snapshots: <strong>${vm.snapshots.length}</strong></div>
            </div>

            <div class="vm-actions-bar">
                ${vm.state === 'Running' ? `
                    <button class="btn-vm-action" onclick="vmAction('${vm.id}', 'pause')">⏸ Suspend</button>
                    <button class="btn-vm-action" onclick="vmAction('${vm.id}', 'stop')">⏹ Stop</button>
                    <button class="btn-vm-action" onclick="vmAction('${vm.id}', 'reboot')">🔄 Reboot</button>
                    <button class="btn-vm-action" onclick="takeSnapshot('${vm.id}')">📸 Snapshot</button>
                ` : vm.state === 'Suspended' ? `
                    <button class="btn-vm-action btn-success" onclick="vmAction('${vm.id}', 'resume')">⏯ Resume</button>
                    <button class="btn-vm-action" onclick="vmAction('${vm.id}', 'stop')">⏹ Stop</button>
                ` : vm.state === 'Stopped' ? `
                    <button class="btn-vm-action btn-success" onclick="vmAction('${vm.id}', 'start')">▶ Start</button>
                    <button class="btn-vm-action" onclick="openResizeModal('${vm.id}', ${vm.vcpus}, ${vm.memory_mb})">⚙ Resize Hardware</button>
                ` : ''}
                <button class="btn-vm-action btn-danger-hover" onclick="vmAction('${vm.id}', 'terminate')">🗑 Terminate</button>
            </div>
        `;

        container.appendChild(card);
    });
}

function renderActiveVmDetails() {
    if (!currentStatus) return;
    const vm = currentStatus.vms.find(v => v.id === activeVmId);
    if (!vm) return;

    // Prompt label
    document.getElementById("consolePromptLabel").innerText = `root@${vm.name}:~#`;

    // Cloud init tab
    const viewer = document.getElementById("cloudInitViewer");
    if (viewer.value !== vm.cloud_init_yaml) {
        viewer.value = vm.cloud_init_yaml;
    }

    // Bootstrap logs tab
    const logsScreen = document.getElementById("bootstrapLogsScreen");
    logsScreen.innerHTML = "";
    vm.cloud_init_logs.forEach(log => {
        const div = document.createElement("div");
        div.innerText = log;
        logsScreen.appendChild(div);
    });
}

function renderEvents(events) {
    const tbody = document.getElementById("eventsTableBody");
    tbody.innerHTML = "";

    events.forEach(ev => {
        const row = document.createElement("tr");
        const lvlColor = ev.level === "SUCCESS" ? "text-green" : (ev.level === "WARNING" ? "text-yellow" : "text-cyan");
        row.innerHTML = `
            <td><code>${ev.time}</code></td>
            <td><strong>${ev.vm}</strong></td>
            <td><span class="${lvlColor}">[${ev.level}]</span></td>
            <td>${ev.message}</td>
        `;
        tbody.appendChild(row);
    });
}

async function vmAction(vmId, action) {
    try {
        await fetch("/api/vm/action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ vm_id: vmId, action })
        });
        fetchStatus();
    } catch (err) {
        alert("Action failed: " + err);
    }
}

async function takeSnapshot(vmId) {
    const snapName = prompt("Enter snapshot name (e.g. pre-upgrade-snap):", "checkpoint-snap-1");
    if (!snapName) return;

    try {
        await fetch("/api/vm/snapshot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ vm_id: vmId, name: snapName })
        });
        fetchStatus();
    } catch (err) {
        alert("Snapshot failed: " + err);
    }
}

function openResizeModal(vmId, vcpus, memoryMb) {
    document.getElementById("resizeVmId").value = vmId;
    document.getElementById("resizeVcpus").value = vcpus;
    document.getElementById("resizeMemory").value = memoryMb;
    document.getElementById("resizeModal").style.display = "flex";
}

async function submitResize() {
    const vmId = document.getElementById("resizeVmId").value;
    const vcpus = parseInt(document.getElementById("resizeVcpus").value);
    const memoryMb = parseInt(document.getElementById("resizeMemory").value);

    try {
        const res = await fetch("/api/vm/resize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ vm_id: vmId, vcpus, memory_mb: memoryMb })
        });
        const data = await res.json();
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById("resizeModal").style.display = "none";
            fetchStatus();
        }
    } catch (err) {
        alert("Resize error: " + err);
    }
}

async function submitProvision() {
    const name = document.getElementById("inputVmName").value;
    const vcpus = parseInt(document.getElementById("selectVcpus").value);
    const memoryMb = parseInt(document.getElementById("selectMemory").value);
    const diskGb = parseInt(document.getElementById("selectDisk").value);

    try {
        await fetch("/api/vm/provision", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, vcpus, memory_mb: memoryMb, disk_gb: diskGb })
        });
        document.getElementById("provisionFormBox").style.display = "none";
        fetchStatus();
    } catch (err) {
        alert("Provisioning failed: " + err);
    }
}

async function execCommand(command) {
    if (!activeVmId) {
        alert("Please select a running VM first.");
        return;
    }

    const screen = document.getElementById("serialConsoleOutput");
    screen.innerText = `root@cloud-vm:~# ${command}\nExecuting on hypervisor vCPU...`;

    try {
        const res = await fetch("/api/vm/exec", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ vm_id: activeVmId, command })
        });
        const data = await res.json();
        if (data.error) {
            screen.innerText = `Error: ${data.error}`;
        } else {
            screen.innerText = `root@cloud-vm:~# ${data.command}\n\n${data.output}`;
        }
    } catch (err) {
        screen.innerText = `Execution failed: ${err}`;
    }
}
