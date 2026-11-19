// Practical 03: Containerization with Docker & Cgroups Frontend Controller

let isHealthy = true;

document.addEventListener("DOMContentLoaded", () => {
    fetchCgroups();
    fetchLayers();
    fetchLogs();

    // Polling loops
    setInterval(fetchCgroups, 1500);
    setInterval(fetchLogs, 3000);

    // Event listeners
    document.getElementById("btn-alloc-20").addEventListener("click", () => allocateMemory(20));
    document.getElementById("btn-alloc-50").addEventListener("click", () => allocateMemory(50));
    document.getElementById("btn-mem-free").addEventListener("click", releaseMemory);
    document.getElementById("btn-cpu-burn").addEventListener("click", triggerCpuSpike);
    document.getElementById("btn-touch-file").addEventListener("click", touchEphemeralFile);
    document.getElementById("btn-toggle-health").addEventListener("click", toggleHealth);
    document.getElementById("btn-refresh-logs").addEventListener("click", fetchLogs);
});

async function fetchCgroups() {
    try {
        const res = await fetch("/api/cgroups");
        if (!res.ok) return;
        const data = await res.json();

        // Top Stats
        document.getElementById("stat-hostname").textContent = data.hostname || "unknown";
        document.getElementById("stat-platform").textContent = (data.platform || "").substring(0, 24);
        document.getElementById("stat-cgroup-ver").textContent = data.cgroup_version || "cgroup v2";

        const memUsed = data.memory_current_mb;
        const memLimit = data.memory_limit_mb;
        const memPct = data.memory_usage_pct;

        document.getElementById("stat-mem-usage").textContent = `${memUsed} / ${memLimit} MB`;
        document.getElementById("stat-mem-pct").textContent = `${memPct}% of Kernel Hard Limit`;

        document.getElementById("stat-cpu-quota").textContent = data.cpu_quota;
        document.getElementById("stat-throttled").textContent = `${data.cpu_throttled_count} Throttled CFS Periods`;
        document.getElementById("stat-user-id").textContent = `UID ${data.user_id} (${data.is_unprivileged ? "Non-Root" : "Root"})`;

        // Memory Bar
        const bar = document.getElementById("mem-bar");
        bar.style.width = `${Math.min(100, Math.max(15, memPct))}%`;
        document.getElementById("mem-pill").textContent = `${memUsed} MB / ${memLimit} MB (${memPct}%)`;

        if (memPct > 80) {
            bar.style.background = "#ef4444"; // Red (near OOM)
        } else if (memPct > 60) {
            bar.style.background = "#f59e0b"; // Amber
        } else {
            bar.style.background = "linear-gradient(90deg, #0284c7, #8b5cf6)"; // Normal Docker blue
        }

        // CPU Stress Badge
        const cpuBadge = document.getElementById("cpu-stress-badge");
        if (data.cpu_stress_active) {
            cpuBadge.textContent = "🔥 Active CPU Burner (Throttling Running)";
            cpuBadge.style.color = "#dc2626";
        } else {
            cpuBadge.textContent = "Idle (0% Throttling)";
            cpuBadge.style.color = "#64748b";
        }

        // Namespaces
        document.getElementById("ns-pid").textContent = `PID ${data.process_id} (Container PID Namespace)`;
        document.getElementById("ns-uid").textContent = `UID ${data.user_id} : GID ${data.group_id} (Unprivileged)`;
        document.getElementById("ns-uts").textContent = `Hostname: ${data.hostname}`;
        document.getElementById("ns-pids").textContent = `Active: ${data.pids_current} / Max: ${data.pids_max}`;

        // Live Health Check
        checkLiveHealth();

    } catch (err) {
        console.error("Failed to fetch cgroup metrics:", err);
    }
}

async function checkLiveHealth() {
    try {
        const res = await fetch("/healthz");
        const statHealth = document.getElementById("stat-health");
        const probePill = document.getElementById("probe-status-pill");
        const toggleBtn = document.getElementById("btn-toggle-health");

        if (res.ok) {
            isHealthy = true;
            statHealth.textContent = "200 OK";
            statHealth.className = "value text-success";
            probePill.textContent = "Status: HEALTHY (200 OK)";
            probePill.className = "pill pill-green";
            toggleBtn.textContent = "Simulate Microservice Crash (Toggle 503)";
            toggleBtn.className = "btn btn-outline-danger";
        } else {
            isHealthy = false;
            statHealth.textContent = "503 FAIL";
            statHealth.className = "value text-danger";
            probePill.textContent = "Status: UNHEALTHY (503 Service Unavailable)";
            probePill.className = "pill pill-red";
            toggleBtn.textContent = "Restore Microservice Health (Toggle 200)";
            toggleBtn.className = "btn btn-primary";
        }
    } catch (err) {
        const statHealth = document.getElementById("stat-health");
        statHealth.textContent = "OFFLINE";
        statHealth.className = "value text-danger";
    }
}

async function allocateMemory(mb) {
    try {
        const res = await fetch("/api/cgroups/stress-memory", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "allocate", mb })
        });
        const data = await res.json();
        if (!res.ok) {
            alert(`Cgroup Guardrail: ${data.error}`);
        }
        fetchCgroups();
        fetchLogs();
    } catch (err) {
        alert("Failed to allocate memory: " + err.message);
    }
}

async function releaseMemory() {
    try {
        await fetch("/api/cgroups/stress-memory", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "release" })
        });
        fetchCgroups();
        fetchLogs();
    } catch (err) {
        console.error("Failed to release memory:", err);
    }
}

async function triggerCpuSpike() {
    try {
        await fetch("/api/cgroups/stress-cpu", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ duration_sec: 5 })
        });
        fetchCgroups();
        fetchLogs();
    } catch (err) {
        console.error("Failed to trigger CPU spike:", err);
    }
}

async function toggleHealth() {
    try {
        await fetch("/api/health/toggle", { method: "POST" });
        checkLiveHealth();
        fetchLogs();
    } catch (err) {
        console.error("Failed to toggle health:", err);
    }
}

async function fetchLayers() {
    try {
        const res = await fetch("/api/layers");
        if (!res.ok) return;
        const data = await res.json();
        renderLayers(data.layers);
    } catch (err) {
        console.error("Failed to fetch image layers:", err);
    }
}

function renderLayers(layers) {
    const container = document.getElementById("layers-stack");
    container.innerHTML = "";

    layers.forEach(layer => {
        const card = document.createElement("div");
        let typeClass = "layer-base";
        if (layer.layer_index === 2) typeClass = "layer-security";
        if (layer.layer_index === 3) typeClass = "layer-pkgs";
        if (layer.layer_index === 4) typeClass = "layer-app";
        if (layer.layer_index === 5) typeClass = "layer-rw";

        card.className = `layer-card ${typeClass}`;

        let filesHtml = "";
        if (layer.files && layer.files.length > 0) {
            filesHtml = `<div class="layer-files-list">Files in Ephemeral Layer: ` +
                layer.files.map(f => `<code>${f.filename}</code> (${f.size_kb} KB)`).join(", ") +
                `</div>`;
        } else if (layer.layer_index === 5) {
            filesHtml = `<div class="layer-files-list" style="color: #94a3b8;">Ephemeral layer is clean (no modified files yet).</div>`;
        }

        card.innerHTML = `
            <div class="layer-top-line">
                <span class="layer-name">Layer ${layer.layer_index}: ${layer.type}</span>
                <span class="pill">${layer.size_approx}</span>
            </div>
            <div>
                <span class="layer-cmd">${layer.command}</span>
            </div>
            <div class="layer-meta">
                <span>Digest: ${layer.digest}</span>
                <span>Status: <strong>${layer.status}</strong></span>
            </div>
            ${filesHtml}
        `;
        container.appendChild(card);
    });
}

async function touchEphemeralFile() {
    try {
        const res = await fetch("/api/layers/touch-file", { method: "POST" });
        const data = await res.json();
        fetchLayers();
        fetchLogs();
    } catch (err) {
        console.error("Failed to touch ephemeral file:", err);
    }
}

async function fetchLogs() {
    try {
        const res = await fetch("/api/logs");
        if (!res.ok) return;
        const data = await res.json();
        const tbody = document.getElementById("log-body");

        if (!data.logs || data.logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" class="text-center">No logs recorded.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.logs.map(log => `
            <tr>
                <td style="font-family: var(--font-mono); color: var(--text-muted);">${log.timestamp}</td>
                <td><span class="category-tag cat-${log.category}">${log.category}</span></td>
                <td>${log.message}</td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("Failed to fetch logs:", err);
    }
}
