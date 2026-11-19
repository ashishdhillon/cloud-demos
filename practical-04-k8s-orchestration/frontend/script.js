let currentStatus = null;
let isUpdatingYaml = false;

document.addEventListener("DOMContentLoaded", () => {
    initEventListeners();
    fetchClusterStatus();
    runKubectlCommand("kubectl get pods -o wide");
    setInterval(fetchClusterStatus, 1000);
});

function initEventListeners() {
    // Scale controls
    document.getElementById("btnScaleUp").addEventListener("click", () => {
        if (!currentStatus) return;
        const target = currentStatus.deployment.desired_replicas + 1;
        scaleDeployment(target);
    });

    document.getElementById("btnScaleDown").addEventListener("click", () => {
        if (!currentStatus) return;
        const target = Math.max(1, currentStatus.deployment.desired_replicas - 1);
        scaleDeployment(target);
    });

    // Rollout button
    document.getElementById("btnTriggerRollout").addEventListener("click", () => {
        if (!currentStatus) return;
        const nextVer = currentStatus.deployment.version === "v1.0.0" ? "v2.0.0" : "v1.0.0";
        triggerRollout(nextVer);
    });

    // Apply YAML
    document.getElementById("btnApplyYaml").addEventListener("click", () => {
        const yamlCode = document.getElementById("yamlEditor").value;
        applyYaml(yamlCode);
    });

    // Send Traffic Request
    document.getElementById("btnSendTraffic").addEventListener("click", sendTrafficRequest);

    // Kubectl CLI Buttons
    document.querySelectorAll(".btn-term").forEach(btn => {
        btn.addEventListener("click", () => {
            const cmd = btn.getAttribute("data-cmd");
            runKubectlCommand(cmd);
        });
    });

    // Track when user is typing in YAML editor to avoid overwriting their edits
    const yamlEditor = document.getElementById("yamlEditor");
    yamlEditor.addEventListener("focus", () => { isUpdatingYaml = true; });
    yamlEditor.addEventListener("blur", () => { isUpdatingYaml = false; });
}

async function fetchClusterStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();
        currentStatus = data;
        renderDashboard(data);
    } catch (err) {
        console.error("Failed to fetch cluster status:", err);
    }
}

function renderDashboard(data) {
    const dep = data.deployment;
    document.getElementById("desiredReplicasVal").innerText = dep.desired_replicas;
    document.getElementById("readyPodsVal").innerText = `${dep.ready_replicas} / ${dep.current_replicas}`;
    document.getElementById("imageVersionVal").innerText = dep.version;

    // Rollout Status Pill & Button text
    const btnRollout = document.getElementById("btnTriggerRollout");
    const rolloutStatus = document.getElementById("rolloutStatusText");
    if (dep.is_rolling_update) {
        rolloutStatus.innerHTML = '<span class="text-purple">● Rolling update in progress...</span>';
        btnRollout.disabled = true;
        btnRollout.innerText = "⏳ Rolling Out...";
    } else {
        const nextVer = dep.version === "v1.0.0" ? "v2.0.0" : "v1.0.0";
        rolloutStatus.innerText = `Stable (${dep.current_replicas} active replicas)`;
        btnRollout.disabled = false;
        btnRollout.innerText = `🚀 Rollout ${nextVer}`;
    }

    // Populate YAML editor if not currently focused by user
    if (!isUpdatingYaml) {
        const editor = document.getElementById("yamlEditor");
        if (editor.value.trim() === "" || (!editor.matches(":focus") && editor.value !== data.yaml_code)) {
            editor.value = data.yaml_code;
        }
    }

    // Render Worker Nodes and their assigned Pods
    renderNodesAndPods(data.nodes, data.pods);

    // Render Events Table
    renderEvents(data.events);
}

function renderNodesAndPods(nodes, pods) {
    const container = document.getElementById("nodesContainer");
    container.innerHTML = "";

    nodes.forEach(node => {
        const nodeCard = document.createElement("div");
        nodeCard.className = "node-card";

        const nodePods = pods.filter(p => p.node === node.name);

        nodeCard.innerHTML = `
            <div class="node-header">
                <div class="node-title">
                    <span>🖥️ ${node.name}</span>
                    <span class="node-badge">Ready</span>
                </div>
                <div class="text-sm text-muted">
                    IP: ${node.ip} · Pods: ${nodePods.length} · Alloc: ${node.cpu_total} / ${node.mem_total}
                </div>
            </div>
            <div class="pods-grid" id="pods-${node.name}"></div>
        `;

        container.appendChild(nodeCard);

        const podsGrid = nodeCard.querySelector(`#pods-${node.name}`);
        if (nodePods.length === 0) {
            podsGrid.innerHTML = '<div class="text-muted text-sm" style="padding: 10px;">No pods currently scheduled on this node.</div>';
        } else {
            nodePods.forEach(pod => {
                const podCard = createPodCard(pod);
                podsGrid.appendChild(podCard);
            });
        }
    });
}

function createPodCard(pod) {
    const card = document.createElement("div");
    card.className = "pod-card";
    if (pod.liveness_failing) card.classList.add("failing-probe");
    if (pod.readiness_failing) card.classList.add("readiness-dropped");

    const versionClass = pod.version === "v2.0.0" ? "pod-version-v2" : "pod-version-v1";
    const readyStateText = pod.ready && !pod.readiness_failing ? "Ready 1/1" : "NotReady 0/1";
    const readyColor = pod.ready && !pod.readiness_failing ? "text-green" : "text-yellow";

    card.innerHTML = `
        <div class="pod-top">
            <span class="pod-name" title="${pod.name}">${pod.name}</span>
            <span class="pod-version-pill ${versionClass}">${pod.version}</span>
        </div>
        <div class="pod-details">
            <div>Status: <strong class="${readyColor}">${pod.status}</strong></div>
            <div>Gate: <span class="${readyColor}">${readyStateText}</span></div>
            <div>IP: <code>${pod.ip}</code></div>
            <div>Restarts: <strong>${pod.restarts}</strong></div>
            <div>Age: ${pod.age}</div>
            <div>Usage: ${pod.cpu_usage} / ${pod.mem_usage}</div>
        </div>
        <div class="pod-actions">
            <button class="btn-pod-action btn-pod-kill" onclick="killPod('${pod.name}')" title="Simulate process crash or node failure">⚡ Kill Pod</button>
            <button class="btn-pod-action" onclick="toggleProbe('${pod.name}', 'liveness')" title="Toggle /healthz probe 500 error">
                ${pod.liveness_failing ? "✅ Fix Liveness" : "🩺 Fail Liveness"}
            </button>
            <button class="btn-pod-action" onclick="toggleProbe('${pod.name}', 'readiness')" title="Toggle traffic acceptance">
                ${pod.readiness_failing ? "✅ Pass Readiness" : "🚫 Fail Readiness"}
            </button>
        </div>
    `;

    return card;
}

function renderEvents(events) {
    const tbody = document.getElementById("eventStreamBody");
    tbody.innerHTML = "";

    events.forEach(ev => {
        const row = document.createElement("tr");
        const typeClass = ev.type === "Warning" ? "tag-warning" : "tag-normal";
        row.innerHTML = `
            <td><code>${ev.time}</code></td>
            <td><span class="${typeClass}">${ev.type}</span></td>
            <td><strong>${ev.reason}</strong></td>
            <td><code>${ev.object}</code></td>
            <td>${ev.message}</td>
        `;
        tbody.appendChild(row);
    });
}

async function scaleDeployment(replicas) {
    try {
        await fetch("/api/scale", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ replicas })
        });
        fetchClusterStatus();
    } catch (err) {
        console.error("Scale error:", err);
    }
}

async function triggerRollout(version) {
    try {
        await fetch("/api/rollout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ version })
        });
        fetchClusterStatus();
    } catch (err) {
        console.error("Rollout error:", err);
    }
}

async function killPod(podName) {
    try {
        await fetch("/api/kill-pod", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pod_name: podName })
        });
        fetchClusterStatus();
    } catch (err) {
        console.error("Kill pod error:", err);
    }
}

async function toggleProbe(podName, probeType) {
    try {
        await fetch("/api/probe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pod_name: podName, probe_type: probeType })
        });
        fetchClusterStatus();
    } catch (err) {
        console.error("Toggle probe error:", err);
    }
}

async function applyYaml(yamlCode) {
    try {
        const res = await fetch("/api/apply-yaml", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ yaml_code: yamlCode })
        });
        const data = await res.json();
        alert(data.message || "YAML applied.");
        fetchClusterStatus();
    } catch (err) {
        alert("Failed to apply manifest: " + err);
    }
}

async function sendTrafficRequest() {
    const resBox = document.getElementById("trafficResult");
    resBox.innerHTML = '<span class="text-cyan">Routing request through kube-proxy iptables...</span>';
    try {
        const res = await fetch("/api/traffic", { method: "POST" });
        const data = await res.json();

        if (data.status_code === 200) {
            resBox.innerHTML = `
                <span class="text-green">✓ HTTP 200 OK</span>&nbsp;·&nbsp;
                Served by: <strong><code>${data.serving_pod}</code></strong>&nbsp;·&nbsp;
                Pod IP: <code>${data.serving_ip}</code>&nbsp;·&nbsp;
                Node: <code>${data.serving_node}</code>&nbsp;·&nbsp;
                Version: <span class="badge ${data.version === 'v2.0.0' ? 'badge-k8s' : 'badge-ready'}">${data.version}</span>&nbsp;·&nbsp;
                Latency: <strong>${data.latency_ms}ms</strong>
            `;
        } else {
            resBox.innerHTML = `<span class="text-red">❌ ${data.message}</span>`;
        }
    } catch (err) {
        resBox.innerHTML = `<span class="text-red">Request failed: ${err}</span>`;
    }
}

async function runKubectlCommand(command) {
    const outputEl = document.getElementById("terminalOutput");
    outputEl.innerText = `$ ${command}\nExecuting...`;
    try {
        const res = await fetch("/api/kubectl", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ command })
        });
        const data = await res.json();
        outputEl.innerText = `$ ${data.command}\n\n${data.output}`;
    } catch (err) {
        outputEl.innerText = `$ ${command}\nError: ${err}`;
    }
}
