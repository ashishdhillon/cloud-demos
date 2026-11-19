let currentStatus = null;

document.addEventListener("DOMContentLoaded", () => {
    initEventListeners();
    fetchStatus();
    setInterval(fetchStatus, 1000);
});

function initEventListeners() {
    document.getElementById("btnStartMigration").addEventListener("click", () => {
        const mode = document.getElementById("networkModeSelect").value;
        triggerMigration(mode, false);
    });

    document.getElementById("btnTamperMigration").addEventListener("click", () => {
        const mode = document.getElementById("networkModeSelect").value;
        triggerMigration(mode, true);
    });

    document.getElementById("btnResetEnv").addEventListener("click", resetEnvironment);
    document.getElementById("btnRunAudit").addEventListener("click", triggerVerification);
}

async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();
        currentStatus = data;
        renderDashboard(data);
    } catch (err) {
        console.error("Failed to fetch migration status:", err);
    }
}

function renderDashboard(data) {
    const pipe = data.pipeline_state;

    // Header Badge
    const badge = document.getElementById("pipelineStatusBadge");
    if (pipe.status === "running") {
        badge.className = "badge badge-s3";
        badge.innerText = "⏳ Pipeline: In Progress...";
    } else if (pipe.status === "completed") {
        badge.className = "badge badge-ready";
        badge.innerText = "● Pipeline: 100% Parity Verified";
    } else if (pipe.status === "corrupted") {
        badge.className = "badge";
        badge.style.background = "rgba(239, 68, 68, 0.2)";
        badge.style.color = "#f87171";
        badge.style.border = "1px solid rgba(239, 68, 68, 0.4)";
        badge.innerText = "⚠ Pipeline: Checksum Mismatch Detected";
    } else {
        badge.className = "badge badge-ready";
        badge.innerText = "● Pipeline: Ready";
    }

    // Top Stats Cards
    const totalBytes = pipe.total_bytes || 24800;
    document.getElementById("statVolumeTransferred").innerText = `${formatBytes(pipe.bytes_transferred)} / ${formatBytes(totalBytes)}`;
    document.getElementById("statThroughput").innerText = `Throughput: ${pipe.throughput_mbps} Mbps (${pipe.elapsed_sec}s)`;

    const netModeText = pipe.network_mode === "direct_connect_1gbps" ? "1.0 Gbps (AWS Direct Connect)" : "100 Mbps (Public VPN)";
    document.getElementById("statNetworkMode").innerText = pipe.network_mode === "direct_connect_1gbps" ? "1.0 Gbps" : "100 Mbps";

    const statIntegrity = document.getElementById("statIntegrity");
    const statIntegritySub = document.getElementById("statIntegritySub");
    if (pipe.status === "completed") {
        statIntegrity.innerHTML = '<span class="text-green">100% PASS</span>';
        statIntegritySub.innerText = "Zero Bitrot / Zero Data Loss";
    } else if (pipe.status === "corrupted") {
        statIntegrity.innerHTML = '<span class="text-red">FAIL: BITROT</span>';
        statIntegritySub.innerText = "1-Bit Tamper Caught by SHA-256";
    } else {
        statIntegrity.innerText = "Pending";
        statIntegritySub.innerText = "SHA-256 & MD5 ETag Parity";
    }

    // Progress Box
    document.getElementById("pipelineStepText").innerText = pipe.current_step;
    document.getElementById("pipelinePctText").innerText = `${pipe.progress_pct}%`;
    document.getElementById("progressBarFill").style.width = `${pipe.progress_pct}%`;

    // Disable start buttons while running
    const isRunning = (pipe.status === "running");
    document.getElementById("btnStartMigration").disabled = isRunning;
    document.getElementById("btnTamperMigration").disabled = isRunning;

    // Render On-Premises Assets
    renderOnPremAssets(data.onprem_assets);

    // Render Cloud S3 Objects
    renderCloudStorage(data.cloud_s3_storage, data.target_bucket);

    // Render Audit Ledger
    renderAuditLedger(data.audit_records);

    // Render Events Log
    renderEvents(data.events);
}

function renderOnPremAssets(assets) {
    const container = document.getElementById("onpremAssetsList");
    container.innerHTML = "";

    Object.values(assets).forEach(asset => {
        const card = document.createElement("div");
        card.className = "asset-card";
        card.innerHTML = `
            <div class="asset-title">
                <span>📄 ${asset.source_name}</span>
                <span class="pill pill-muted">${asset.status}</span>
            </div>
            <div class="asset-meta">
                <span>Type: <strong>${asset.asset_type}</strong></span>
                <span>Size: <strong>${formatBytes(asset.size_bytes)}</strong> (${asset.record_count} items)</span>
            </div>
            <div class="hash-preview" title="Source SHA-256 Checksum">
                SHA-256: ${asset.source_sha256}
            </div>
        `;
        container.appendChild(card);
    });
}

function renderCloudStorage(s3Storage, bucketName) {
    const container = document.getElementById("s3ObjectsList");
    const keys = Object.keys(s3Storage);

    if (keys.length === 0) {
        container.innerHTML = `
            <div class="empty-state text-muted" style="padding: 24px; text-align: center;">
                No objects in <code>s3://${bucketName}</code> yet.<br>Click "Start Cloud Migration" to transfer assets.
            </div>
        `;
        return;
    }

    container.innerHTML = "";
    keys.forEach(k => {
        const obj = s3Storage[k];
        const card = document.createElement("div");
        card.className = "s3-card";
        card.innerHTML = `
            <div class="s3-title">
                <span>☁️ s3://${obj.bucket}/${obj.s3_key}</span>
                <span class="pill pill-s3">${obj.storage_class}</span>
            </div>
            <div class="asset-meta">
                <span>Size: <strong>${formatBytes(obj.size_bytes)}</strong></span>
                <span>ETag: <code>"${obj.etag}"</code></span>
            </div>
            <div class="hash-preview" title="Cloud S3 Object SHA-256 Checksum">
                SHA-256: ${obj.s3_sha256}
            </div>
            <div class="asset-meta" style="margin-top: 4px; font-size: 0.68rem; color: #a5b4fc;">
                Tags: Class=Confidential · Standard=SOC2-TypeII · Retain=7Y
            </div>
        `;
        container.appendChild(card);
    });
}

function renderAuditLedger(records) {
    const tbody = document.getElementById("auditTableBody");
    if (!records || records.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-muted text-center" style="padding: 16px;">
                    Awaiting migration completion to generate cryptographic audit report.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = "";
    records.forEach(r => {
        const row = document.createElement("tr");
        const statusClass = r.parity_match ? "parity-pass" : "parity-fail";
        row.innerHTML = `
            <td><code>${r.asset_key}</code></td>
            <td><strong>${formatBytes(r.bytes)}</strong></td>
            <td><code class="hash-mono">${r.source_sha256.substring(0, 16)}...</code></td>
            <td><code class="hash-mono">${r.target_sha256.substring(0, 16)}...</code></td>
            <td><span class="${statusClass}">${r.status}</span></td>
        `;
        tbody.appendChild(row);
    });
}

function renderEvents(events) {
    const container = document.getElementById("eventsLog");
    container.innerHTML = "";

    events.forEach(ev => {
        const div = document.createElement("div");
        div.className = "event-line";
        const lvlClass = `event-level-${ev.level.toLowerCase()}`;
        div.innerHTML = `
            <span class="event-time">[${ev.time}]</span>
            <span class="${lvlClass}">[${ev.level}]</span>
            <span>${ev.message}</span>
        `;
        container.appendChild(div);
    });
}

async function triggerMigration(networkMode, tamper) {
    try {
        await fetch("/api/migrate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ network_mode: networkMode, tamper })
        });
        fetchStatus();
    } catch (err) {
        alert("Failed to start migration: " + err);
    }
}

async function triggerVerification() {
    try {
        await fetch("/api/verify", { method: "POST" });
        fetchStatus();
    } catch (err) {
        alert("Failed to run verification: " + err);
    }
}

async function resetEnvironment() {
    try {
        await fetch("/api/reset", { method: "POST" });
        fetchStatus();
    } catch (err) {
        alert("Failed to reset: " + err);
    }
}

function formatBytes(bytes) {
    if (!bytes || bytes === 0) return "0 B";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}
