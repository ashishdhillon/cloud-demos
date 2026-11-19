let currentProject = "proj-prod";
let currentData = null;

document.addEventListener("DOMContentLoaded", () => {
    initEventListeners();
    fetchOverview();
    runOpenStackCli("openstack server list");
    setInterval(fetchOverview, 1000);
});

function initEventListeners() {
    // Project selector
    document.getElementById("projectSelect").addEventListener("change", (e) => {
        currentProject = e.target.value;
        fetchOverview();
        runOpenStackCli("openstack server list");
    });

    // Launch Modal
    document.getElementById("btnOpenLaunchModal").addEventListener("click", () => {
        document.getElementById("launchModal").style.display = "flex";
    });
    document.getElementById("btnCancelLaunch").addEventListener("click", () => {
        document.getElementById("launchModal").style.display = "none";
    });
    document.getElementById("btnSubmitLaunch").addEventListener("click", submitLaunchInstance);

    // CLI quick buttons
    document.querySelectorAll(".btn-term").forEach(btn => {
        btn.addEventListener("click", () => {
            const cmd = btn.getAttribute("data-cmd");
            runOpenStackCli(cmd);
        });
    });
}

async function fetchOverview() {
    try {
        const res = await fetch(`/api/overview?project=${currentProject}`);
        if (!res.ok) return;
        const data = await res.json();
        currentData = data;
        renderDashboard(data);
    } catch (err) {
        console.error("Failed to fetch OpenStack overview:", err);
    }
}

function renderDashboard(data) {
    const proj = data.current_project;
    const q = data.quotas;

    document.getElementById("currentProjectTitle").innerText = proj.name;

    // Top Stats Cards
    document.getElementById("statVcpuQuota").innerText = `${q.vcpus.used} / ${q.vcpus.limit} vCPUs`;
    document.getElementById("statRamQuota").innerText = `${(q.ram_mb.used / 1024).toFixed(1)} / ${(q.ram_mb.limit / 1024).toFixed(1)} GiB`;
    document.getElementById("statInstanceCount").innerText = `${q.instances.used} / ${q.instances.limit} Instances`;

    const net = data.networks.find(n => n.project_id === currentProject);
    document.getElementById("statSubnetCidr").innerText = net ? net.cidr : "192.168.100.0/24";

    // Render Instances Table
    renderInstances(data.servers);

    // Render Service Catalog
    renderCatalog(data.service_catalog);

    // Render Events Table
    renderEvents(data.events);
}

function renderInstances(servers) {
    const tbody = document.getElementById("instancesTableBody");
    tbody.innerHTML = "";

    if (servers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-muted text-center" style="padding: 24px;">
                    No active compute instances in project <strong>${currentProject}</strong>.<br>
                    Click "Launch Cloud Instance" above to spin up a new virtual server.
                </td>
            </tr>
        `;
        return;
    }

    servers.forEach(s => {
        const row = document.createElement("tr");
        const statusClass = `status-${s.status.toLowerCase()}`;
        const fipText = s.floating_ip ? `<span class="badge badge-openstack" style="padding: 2px 6px;">${s.floating_ip}</span>` : '<span class="text-muted">None</span>';

        row.innerHTML = `
            <td>
                <strong>${s.name}</strong><br>
                <code class="text-xs text-muted">${s.id.substring(0, 13)}...</code>
            </td>
            <td><span class="status-pill ${statusClass}">${s.status}</span></td>
            <td><strong>${s.flavor.name}</strong> (${s.flavor.vcpus} vCPU / ${s.flavor.ram}M)</td>
            <td>${s.image.name.split(' ')[0]}</td>
            <td>
                <code>${s.ip_address}</code><br>
                Floating IP: ${fipText}
            </td>
            <td><code class="text-xs">${s.hypervisor_host.split('.')[0]}</code></td>
            <td>
                <div class="instance-actions-cell">
                    ${s.status === 'ACTIVE' ? `
                        <button class="btn-action-mini" onclick="serverAction('${s.id}', 'stop')" title="ACPI Power Off">⏹ Stop</button>
                    ` : `
                        <button class="btn-action-mini" onclick="serverAction('${s.id}', 'start')" title="Power On">▶ Start</button>
                    `}
                    <button class="btn-action-mini" onclick="serverAction('${s.id}', 'floating_ip')" title="Toggle Floating IP">🌐 IP</button>
                    <button class="btn-action-mini btn-action-delete" onclick="serverAction('${s.id}', 'delete')" title="Delete Instance">🗑</button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function renderCatalog(catalog) {
    const container = document.getElementById("catalogList");
    container.innerHTML = "";

    catalog.forEach(item => {
        const card = document.createElement("div");
        card.className = "catalog-card";
        card.innerHTML = `
            <div>
                <strong>${item.name.toUpperCase()}</strong> (${item.type})
                <div class="text-xs text-muted">${item.description}</div>
            </div>
            <span class="catalog-endpoint">${item.endpoint}</span>
        `;
        container.appendChild(card);
    });
}

function renderEvents(events) {
    const tbody = document.getElementById("eventsTableBody");
    tbody.innerHTML = "";

    events.forEach(ev => {
        const row = document.createElement("tr");
        const lvlColor = ev.level === "SUCCESS" ? "text-green" : (ev.level === "WARNING" ? "text-red" : "text-cyan");
        row.innerHTML = `
            <td><code>${ev.time}</code></td>
            <td><strong>${ev.service}</strong></td>
            <td><span class="${lvlColor}">[${ev.level}]</span></td>
            <td><code>${ev.project}</code></td>
            <td>${ev.message}</td>
        `;
        tbody.appendChild(row);
    });
}

async function serverAction(serverId, action) {
    try {
        await fetch("/api/server/action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ server_id: serverId, action })
        });
        fetchOverview();
    } catch (err) {
        alert("Action failed: " + err);
    }
}

async function submitLaunchInstance() {
    const name = document.getElementById("inputServerName").value;
    const flavorRef = document.getElementById("selectFlavor").value;
    const imageRef = document.getElementById("selectImage").value;
    const assignFip = document.getElementById("checkFloatingIp").checked;

    try {
        const res = await fetch("/v2.1/servers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                server: {
                    name,
                    flavorRef,
                    imageRef
                },
                project_id: currentProject,
                assign_floating_ip: assignFip
            })
        });
        const data = await res.json();
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById("launchModal").style.display = "none";
            fetchOverview();
        }
    } catch (err) {
        alert("Launch failed: " + err);
    }
}

async function runOpenStackCli(command) {
    const outputEl = document.getElementById("cliOutput");
    outputEl.innerText = `$ ${command}\nExecuting OpenStack REST API request...`;
    try {
        const res = await fetch("/api/cli", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ command, project_id: currentProject })
        });
        const data = await res.json();
        outputEl.innerText = `$ ${data.command}\n\n${data.output}`;
    } catch (err) {
        outputEl.innerText = `$ ${command}\nError: ${err}`;
    }
}
