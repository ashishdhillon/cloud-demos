let currentStatus = null;
let assessmentWorkloads = [];
let selectedWorkloadIndex = 0;

document.addEventListener("DOMContentLoaded", () => {
    initEventListeners();
    fetchAssessment();
    fetchStatus();
    updateTco();
    setInterval(fetchStatus, 1000);
});

function initEventListeners() {
    // Pipeline Controls
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
    document.getElementById("btnAutoHeal").addEventListener("click", triggerAutoHeal);

    // Cutover & Rollback Controls
    document.getElementById("btnCutover").addEventListener("click", triggerCutover);
    document.getElementById("btnRollback").addEventListener("click", triggerRollback);

    // TCO Sliders
    const dataSlider = document.getElementById("tcoDataSize");
    const serverSlider = document.getElementById("tcoServers");

    dataSlider.addEventListener("input", (e) => {
        document.getElementById("tcoDataSizeVal").innerText = `${e.target.value} TB`;
        updateTco();
    });

    serverSlider.addEventListener("input", (e) => {
        document.getElementById("tcoServersVal").innerText = `${e.target.value} Hosts`;
        updateTco();
    });
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

async function fetchAssessment() {
    try {
        const res = await fetch("/api/assessment");
        if (!res.ok) return;
        assessmentWorkloads = await res.json();
        renderAssessmentGrid();
    } catch (err) {
        console.error("Failed to fetch assessment workloads:", err);
    }
}

function renderAssessmentGrid() {
    const grid = document.getElementById("workloadsGrid");
    grid.innerHTML = "";

    assessmentWorkloads.forEach((w, index) => {
        const card = document.createElement("div");
        card.className = `workload-card ${index === selectedWorkloadIndex ? 'active' : ''}`;
        card.innerHTML = `
            <div class="workload-header">
                <span class="badge ${w.badge_class}">${w.recommended_strategy.split(' ')[0]}</span>
                <span class="text-xs text-muted">Diff: ${w.complexity_score}/10</span>
            </div>
            <div class="workload-name">${w.name}</div>
            <div class="workload-strategy text-sm text-secondary">${w.recommended_strategy}</div>
        `;
        card.addEventListener("click", () => {
            selectedWorkloadIndex = index;
            renderAssessmentGrid();
            renderAssessmentDetail(w);
        });
        grid.appendChild(card);
    });

    if (assessmentWorkloads[selectedWorkloadIndex]) {
        renderAssessmentDetail(assessmentWorkloads[selectedWorkloadIndex]);
    }
}

function renderAssessmentDetail(w) {
    document.getElementById("detailBadge").className = `badge ${w.badge_class}`;
    document.getElementById("detailBadge").innerText = w.recommended_strategy;
    document.getElementById("detailTitle").innerText = w.name;
    document.getElementById("detailComplexity").innerText = `${w.complexity_score} / 10`;
    document.getElementById("detailVelocity").innerText = `${w.velocity_weeks} Weeks`;
    document.getElementById("detailSavings").innerText = `${w.cost_savings_pct}% TCO Reduction`;
    document.getElementById("detailCurrentTech").innerText = w.current_tech;
    document.getElementById("detailTargetArch").innerText = w.target_architecture;
    document.getElementById("detailRationale").innerText = w.rationale;
}

function renderDashboard(data) {
    const pipe = data.pipeline_state;
    const cutover = data.cutover_state || {};

    // Header Status Pill
    const badge = document.getElementById("pipelineStatusBadge");
    if (pipe.status === "running") {
        badge.innerHTML = '<span class="dot-pulse" style="background: #ea580c;"></span> Pipeline: In Progress...';
    } else if (pipe.status === "completed") {
        badge.innerHTML = '<span class="dot-pulse" style="background: #059669;"></span> Pipeline: 100% Parity Verified';
    } else if (pipe.status === "corrupted") {
        badge.innerHTML = '<span class="dot-pulse" style="background: #dc2626;"></span> Pipeline: Checksum Mismatch (Bitrot)';
    } else {
        badge.innerHTML = '<span class="dot-pulse"></span> Pipeline: Ready';
    }

    // Top Stats Cards
    const totalBytes = pipe.total_bytes || 24800;
    document.getElementById("statVolumeTransferred").innerText = `${formatBytes(pipe.bytes_transferred)} / ${formatBytes(totalBytes)}`;
    document.getElementById("statThroughput").innerText = `Throughput: ${pipe.throughput_mbps} Mbps (${pipe.elapsed_sec}s elapsed)`;

    // Network Transport Pipe Display
    const modeLabels = {
        "direct_connect_1gbps": { title: "1.0 Gbps", sub: "Dedicated Fiber" },
        "internet_100mbps": { title: "100 Mbps", sub: "Public VPN" },
        "snowball_edge_80tb": { title: "80 TB Appliance", sub: "Offline Snowball" }
    };
    const netInfo = modeLabels[pipe.network_mode] || { title: "1.0 Gbps", sub: "Dedicated Fiber" };
    document.getElementById("statNetworkMode").innerText = netInfo.title;
    document.getElementById("statNetworkSub").innerText = netInfo.sub;

    // Cryptographic Integrity KPI
    const statIntegrity = document.getElementById("statIntegrity");
    const statIntegritySub = document.getElementById("statIntegritySub");
    if (pipe.status === "completed") {
        statIntegrity.innerHTML = '<span class="text-green">100% PASS</span>';
        statIntegritySub.innerText = "Zero Bitrot / Zero Loss";
    } else if (pipe.status === "corrupted") {
        statIntegrity.innerHTML = '<span class="text-red">FAIL: BITROT</span>';
        statIntegritySub.innerText = "1-Bit Tamper Caught by SHA-256";
    } else {
        statIntegrity.innerText = "Ready";
        statIntegritySub.innerText = "SHA-256 & MD5 ETag";
    }

    // Cutover KPI
    const statCutoverPhase = document.getElementById("statCutoverPhase");
    const statCutoverSub = document.getElementById("statCutoverSub");
    const statDnsCaption = document.getElementById("statDnsCaption");
    if (cutover.phase === "cloud_active") {
        statCutoverPhase.innerHTML = '<span class="text-green">AWS Cloud Live</span>';
        statCutoverSub.innerText = "cloud-alb.aws.internal";
        statDnsCaption.innerText = "Route 53: CNAME (100% Live)";
    } else if (cutover.phase === "delta_sync") {
        statCutoverPhase.innerHTML = '<span class="text-orange">Delta CDC Sync</span>';
        statCutoverSub.innerText = "Streaming live writes";
        statDnsCaption.innerText = "Flushing in-flight buffers...";
    } else if (cutover.phase === "dns_cutover") {
        statCutoverPhase.innerHTML = '<span class="text-purple">DNS Switching</span>';
        statCutoverSub.innerText = "Switching TTL 5s";
        statDnsCaption.innerText = "Propagating DNS records...";
    } else if (cutover.phase === "rolled_back") {
        statCutoverPhase.innerHTML = '<span class="text-red">Rolled Back</span>';
        statCutoverSub.innerText = "192.168.1.50 (Safety)";
        statDnsCaption.innerText = "Route 53: A Record Restored";
    } else {
        statCutoverPhase.innerText = "On-Premises";
        statCutoverSub.innerText = "192.168.1.50";
        statDnsCaption.innerText = "Route 53: A Record (TTL 60s)";
    }

    // Progress Box
    document.getElementById("pipelineStepText").innerText = pipe.current_step;
    document.getElementById("pipelinePctText").innerText = `${pipe.progress_pct}%`;
    document.getElementById("progressBarFill").style.width = `${pipe.progress_pct}%`;

    // Disable start buttons while running
    const isRunning = (pipe.status === "running");
    document.getElementById("btnStartMigration").disabled = isRunning;
    document.getElementById("btnTamperMigration").disabled = isRunning;

    // Render Sub-Components
    renderOnPremAssets(data.onprem_assets);
    renderCloudStorage(data.cloud_s3_storage, data.target_bucket);
    renderAuditLedger(data.audit_records);
    renderBitrotDissector(data.tamper_details);
    renderCutoverStatus(cutover, pipe.status);
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
                <span class="pill-chip" style="font-size: 0.68rem; padding: 2px 8px;">${asset.status}</span>
            </div>
            <div class="asset-meta">
                <span>Type: <strong>${asset.asset_type}</strong></span>
                <span>Size: <strong>${formatBytes(asset.size_bytes)}</strong> (${asset.record_count} records)</span>
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
                No objects in <code>s3://${bucketName}</code> yet.<br>Click "Start Cloud Migration" to begin ingestion.
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
                <span class="badge badge-s3">${obj.storage_class}</span>
            </div>
            <div class="asset-meta">
                <span>Size: <strong>${formatBytes(obj.size_bytes)}</strong></span>
                <span>ETag: <code>"${obj.etag.substring(0, 16)}..."</code></span>
            </div>
            <div class="hash-preview" title="Cloud S3 Object SHA-256 Checksum">
                SHA-256: ${obj.s3_sha256}
            </div>
            <div class="asset-meta" style="margin-top: 4px; font-size: 0.68rem; color: #a5b4fc;">
                Tags: Origin=On-Prem · Encryption=AES-256 · Retention=7Y
            </div>
        `;
        container.appendChild(card);
    });
}

function renderBitrotDissector(tamper) {
    const section = document.getElementById("bitrotSection");
    if (!tamper) {
        section.style.display = "none";
        return;
    }

    section.style.display = "flex";
    document.getElementById("dissectorAsset").innerText = tamper.asset_key;
    document.getElementById("dissectorOffset").innerText = tamper.byte_offset;
    document.getElementById("dissectorAvalanche").innerText = `${tamper.avalanche_flipped_bits} flipped!`;
    document.getElementById("dissectorCleanSnippet").innerText = tamper.original_snippet;
    document.getElementById("dissectorCorruptSnippet").innerText = tamper.corrupted_snippet;
    document.getElementById("dissectorSourceSha").innerText = tamper.source_sha256;
    document.getElementById("dissectorBadSha").innerText = tamper.target_sha256;
}

function renderAuditLedger(records) {
    const tbody = document.getElementById("auditTableBody");
    if (!records || records.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-muted text-center" style="padding: 16px;">
                    Awaiting migration execution to generate cryptographic audit report.
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

function renderCutoverStatus(cutover, pipelineStatus) {
    const dnsDisplay = document.getElementById("cutoverDnsDisplay");
    const dnsStatus = document.getElementById("cutoverDnsStatus");
    const endpointDisplay = document.getElementById("cutoverEndpointDisplay");
    const deltaCount = document.getElementById("cutoverDeltaCount");
    const slaBadge = document.getElementById("cutoverSlaBadge");
    const btnCutover = document.getElementById("btnCutover");
    const btnRollback = document.getElementById("btnRollback");

    dnsDisplay.innerText = cutover.dns_record || "erp.enterprise.internal -> A 192.168.1.50 (TTL 60s)";
    dnsStatus.innerText = `Active Traffic Route: ${cutover.live_traffic_target || '100% On-Premises Core'}`;
    endpointDisplay.innerText = cutover.active_endpoint || "192.168.1.50 (On-Premises Data Center)";
    deltaCount.innerText = `Delta CDC In-Flight Transactions: ${cutover.delta_tx_synced || 0}`;

    if (cutover.can_rollback) {
        slaBadge.className = "sla-badge";
        slaBadge.style.background = "#ecfdf5";
        slaBadge.style.color = "#059669";
        slaBadge.innerText = "✓ Production Live in Cloud · Rollback Armed";
        btnRollback.disabled = false;
        btnCutover.disabled = true;
    } else {
        btnRollback.disabled = true;
        btnCutover.disabled = (pipelineStatus !== "completed");
    }
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

async function triggerAutoHeal() {
    try {
        const res = await fetch("/api/heal-chunk", { method: "POST" });
        const data = await res.json();
        fetchStatus();
    } catch (err) {
        alert("Failed to execute auto-heal: " + err);
    }
}

async function triggerCutover() {
    try {
        const res = await fetch("/api/cutover", { method: "POST" });
        const data = await res.json();
        if (!data.success) {
            alert(data.message);
        }
        fetchStatus();
    } catch (err) {
        alert("Failed to trigger cutover: " + err);
    }
}

async function triggerRollback() {
    try {
        const res = await fetch("/api/rollback", { method: "POST" });
        const data = await res.json();
        if (!data.success) {
            alert(data.message);
        }
        fetchStatus();
    } catch (err) {
        alert("Failed to trigger rollback: " + err);
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

async function updateTco() {
    const dataSize = document.getElementById("tcoDataSize").value;
    const servers = document.getElementById("tcoServers").value;

    try {
        const res = await fetch(`/api/tco?data_size_tb=${dataSize}&servers_count=${servers}`);
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById("tcoOnpremVal").innerText = `$${data.onprem_total.toLocaleString()}`;
        document.getElementById("tcoCloudVal").innerText = `$${data.cloud_total.toLocaleString()}`;
        document.getElementById("tcoSavingsDollar").innerText = `$${data.savings_dollar.toLocaleString()}`;
        document.getElementById("tcoSavingsPct").innerText = `${data.savings_pct}%`;
        document.getElementById("tcoCarbonPct").innerText = `${data.carbon_reduction_pct}%`;
        document.getElementById("tcoCarbonTons").innerText = `${(data.onprem_carbon_tons - data.cloud_carbon_tons).toFixed(1)} tons CO2e saved`;
    } catch (err) {
        console.error("Failed to update TCO:", err);
    }
}

function formatBytes(bytes) {
    if (!bytes || bytes === 0) return "0 B";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}
