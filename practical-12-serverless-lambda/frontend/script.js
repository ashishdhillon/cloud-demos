let functions = {};
let selectedFunctionId = "image-thumbnailer";

// DOM Elements
const elStatTotal = document.getElementById("stat-total");
const elStatCold = document.getElementById("stat-cold");
const elStatWarm = document.getElementById("stat-warm");
const elStatWarmRatio = document.getElementById("stat-warm-ratio");
const elStatCost = document.getElementById("stat-cost");

const elFunctionList = document.getElementById("function-list");
const elBtnInvoke = document.getElementById("btn-invoke");
const elBtnInvokeBurst = document.getElementById("btn-invoke-burst");
const elSandboxPool = document.getElementById("sandbox-pool");
const elSandboxCountBadge = document.getElementById("sandbox-count-badge");

const elExecutionTypeBadge = document.getElementById("execution-type-badge");
const elValTotalDuration = document.getElementById("val-total-duration");
const elValInitDuration = document.getElementById("val-init-duration");
const elValExecDuration = document.getElementById("val-exec-duration");
const elValCallCost = document.getElementById("val-call-cost");
const elBarInit = document.getElementById("bar-init");
const elBarExec = document.getElementById("bar-exec");
const elLatencyRatioLabel = document.getElementById("latency-ratio-label");

const elValReqId = document.getElementById("val-req-id");
const elValSandboxId = document.getElementById("val-sandbox-id");
const elValMemAlloc = document.getElementById("val-mem-alloc");
const elValMemUsed = document.getElementById("val-mem-used");
const elHistoryTableBody = document.getElementById("history-table-body");

async function loadFunctions() {
    try {
        const res = await fetch("/api/functions");
        if (!res.ok) return;
        const data = await res.json();
        functions = data.functions;
        renderFunctionList();
    } catch (err) {
        console.error("Failed to load functions:", err);
    }
}

function renderFunctionList() {
    elFunctionList.innerHTML = "";
    Object.keys(functions).forEach(id => {
        const f = functions[id];
        const div = document.createElement("div");
        div.className = `func-card ${id === selectedFunctionId ? 'active' : ''}`;
        div.innerHTML = `
            <div class="func-header">
                <strong>${f.name}</strong>
                <span class="badge badge-normal">${f.memory_mb} MB</span>
            </div>
            <p>${f.description}</p>
        `;
        div.onclick = () => selectFunction(id);
        elFunctionList.appendChild(div);
    });
}

function selectFunction(id) {
    selectedFunctionId = id;
    document.querySelectorAll(".func-card").forEach(c => {
        c.classList.toggle("active", c.innerHTML.includes(functions[id].name));
    });
}

async function invokeFunction() {
    elBtnInvoke.disabled = true;
    elBtnInvoke.textContent = "Invoking Handler...";
    try {
        const res = await fetch("/api/invoke", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ function_id: selectedFunctionId })
        });
        if (res.ok) {
            const record = await res.json();
            renderExecutionTrace(record);
            await loadStats();
            await loadSandboxes();
            await loadHistory();
        }
    } catch (err) {
        console.error("Invoke error:", err);
    } finally {
        elBtnInvoke.disabled = false;
        elBtnInvoke.textContent = "⚡ Invoke Function";
    }
}

async function invokeBurst() {
    elBtnInvokeBurst.disabled = true;
    elBtnInvokeBurst.textContent = "Dispatching 6x Parallel Invocations...";
    try {
        const res = await fetch("/api/invoke-burst", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ function_id: selectedFunctionId, count: 6 })
        });
        if (res.ok) {
            const data = await res.json();
            if (data.results && data.results.length > 0) {
                renderExecutionTrace(data.results[0]);
            }
            await loadStats();
            await loadSandboxes();
            await loadHistory();
        }
    } catch (err) {
        console.error("Burst error:", err);
    } finally {
        elBtnInvokeBurst.disabled = false;
        elBtnInvokeBurst.textContent = "🚀 Invoke Burst (6x Concurrent Fan-Out)";
    }
}

function renderExecutionTrace(r) {
    if (r.is_cold_start) {
        elExecutionTypeBadge.className = "badge badge-cold";
        elExecutionTypeBadge.textContent = "❄️ COLD START (~280 ms)";
    } else {
        elExecutionTypeBadge.className = "badge badge-warm";
        elExecutionTypeBadge.textContent = "⚡ WARM CONTAINER REUSE (~15 ms)";
    }

    elValTotalDuration.textContent = `${r.total_duration_ms} ms`;
    elValInitDuration.textContent = `${r.init_duration_ms} ms`;
    elValExecDuration.textContent = `${r.execution_duration_ms} ms`;
    elValCallCost.textContent = r.cost_usd;

    // Latency Bar percentages
    const total = Math.max(r.total_duration_ms, 1.0);
    const initPct = Math.round((r.init_duration_ms / total) * 100);
    const execPct = 100 - initPct;

    elBarInit.style.width = `${initPct}%`;
    elBarExec.style.width = `${execPct}%`;
    elLatencyRatioLabel.textContent = `${initPct}% Init / ${execPct}% Exec`;

    elValReqId.textContent = r.request_id;
    elValSandboxId.textContent = r.sandbox_id;
    elValMemAlloc.textContent = `${r.memory_allocated_mb} MB`;
    elValMemUsed.textContent = `${r.max_memory_used_mb} MB`;
}

async function loadStats() {
    try {
        const res = await fetch("/api/stats");
        if (!res.ok) return;
        const s = await res.json();
        elStatTotal.textContent = s.total_invocations;
        elStatCold.textContent = s.total_cold_starts;
        elStatWarm.textContent = s.total_warm_reuses;
        elStatWarmRatio.textContent = `${s.warm_reuse_ratio_pct}%`;
        elStatCost.textContent = s.total_billed_cost_usd;
    } catch (err) {
        console.error("Stats error:", err);
    }
}

async function loadSandboxes() {
    try {
        const res = await fetch("/api/sandboxes");
        if (!res.ok) return;
        const data = await res.json();
        const sandboxes = data.sandboxes || [];

        elSandboxCountBadge.textContent = `${sandboxes.length} Active`;
        if (sandboxes.length === 0) {
            elSandboxPool.innerHTML = `<div class="empty-state">No active warm sandboxes. Trigger an invocation to provision a worker.</div>`;
            return;
        }

        elSandboxPool.innerHTML = sandboxes.map(s => `
            <div class="sandbox-item">
                <div class="sandbox-info">
                    <code>${s.sandbox_id} (${s.memory_mb} MB)</code>
                    <span class="sandbox-meta">${s.function_id} &bull; ${s.reuse_count} reuses</span>
                </div>
                <div class="sandbox-ttl">
                    Idle TTL: ${s.ttl_remaining_s}s
                </div>
            </div>
        `).join("");
    } catch (err) {
        console.error("Sandbox error:", err);
    }
}

async function loadHistory() {
    try {
        const res = await fetch("/api/history");
        if (!res.ok) return;
        const data = await res.json();
        const history = data.history || [];

        if (history.length === 0) {
            elHistoryTableBody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">No invocations recorded yet.</td></tr>`;
            return;
        }

        elHistoryTableBody.innerHTML = history.map(h => `
            <tr>
                <td><strong>${h.function_name}</strong></td>
                <td>
                    <span class="badge ${h.is_cold_start ? 'badge-cold' : 'badge-warm'}">
                        ${h.is_cold_start ? 'Cold Start' : 'Warm Reuse'}
                    </span>
                </td>
                <td><strong>${h.total_duration_ms} ms</strong></td>
                <td>${h.init_duration_ms} ms</td>
                <td><code>${h.cost_usd}</code></td>
                <td style="color: #64748b;">${h.timestamp}</td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("History error:", err);
    }
}

elBtnInvoke.onclick = invokeFunction;
elBtnInvokeBurst.onclick = invokeBurst;
document.getElementById("btn-refresh-history").onclick = loadHistory;

// Initialize
window.addEventListener("DOMContentLoaded", () => {
    loadFunctions();
    loadStats();
    loadSandboxes();
    loadHistory();
    // Poll active sandbox TTL every 1s
    setInterval(() => {
        loadSandboxes();
        loadStats();
    }, 1000);
});
