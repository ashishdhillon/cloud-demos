// Practical 01: Cloud Service Models Frontend Controller

let currentModel = "iaas";
let currentView = "tech"; // "tech" or "pizza"
let layersData = [];
let pizzaLayersData = [];
let matrixData = {};

document.addEventListener("DOMContentLoaded", () => {
    fetchOverview();
    fetchState();

    // Model Buttons
    document.querySelectorAll(".btn-model").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const targetBtn = e.target.closest(".btn-model");
            if (!targetBtn) return;
            document.querySelectorAll(".btn-model").forEach(b => b.classList.remove("active"));
            targetBtn.classList.add("active");
            currentModel = targetBtn.getAttribute("data-model");
            renderMatrix();
            highlightStep(1);
        });
    });

    // View Toggle Buttons (Tech vs Pizza)
    const btnTech = document.getElementById("btn-view-tech");
    const btnPizza = document.getElementById("btn-view-pizza");

    if (btnTech && btnPizza) {
        btnTech.addEventListener("click", () => {
            currentView = "tech";
            btnTech.classList.add("active");
            btnPizza.classList.remove("active");
            renderMatrix();
            highlightStep(1);
        });

        btnPizza.addEventListener("click", () => {
            currentView = "pizza";
            btnPizza.classList.add("active");
            btnTech.classList.remove("active");
            renderMatrix();
            highlightStep(2);
        });
    }

    // Tab Buttons
    document.querySelectorAll(".btn-tab").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".btn-tab").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
            e.target.classList.add("active");
            const targetId = e.target.getAttribute("data-tab");
            document.getElementById(targetId).classList.add("active");
        });
    });

    // Wizard Cards
    document.querySelectorAll(".wizard-card").forEach(card => {
        card.addEventListener("click", () => {
            const modelTarget = card.getAttribute("data-answer");
            if (modelTarget) {
                const btn = document.querySelector(`.btn-model[data-model="${modelTarget}"]`);
                if (btn) btn.click();
            }
        });
    });

    // Workbench Action Listeners
    document.getElementById("btn-provision-iaas").addEventListener("click", provisionIaas);
    document.getElementById("btn-deploy-paas").addEventListener("click", deployPaas);
    document.getElementById("btn-create-saas").addEventListener("click", createSaasTenant);
});

function highlightStep(stepNum) {
    [1, 2, 3, 4].forEach(s => {
        const el = document.getElementById(`step-card-${s}`);
        if (el) el.classList.remove("active");
    });
    const target = document.getElementById(`step-card-${stepNum}`);
    if (target) target.classList.add("active");
}

async function fetchOverview() {
    try {
        const res = await fetch("/api/overview");
        if (!res.ok) return;
        const data = await res.json();
        layersData = data.layers || [];
        pizzaLayersData = data.pizza_layers || [];
        matrixData = data.models_matrix || {};
        renderMatrix();
    } catch (err) {
        console.error("Failed to fetch overview:", err);
    }
}

function renderMatrix() {
    const model = matrixData[currentModel];
    if (!model) return;

    const statSelected = document.getElementById("stat-selected-model");
    if (statSelected) {
        statSelected.textContent = currentModel.toUpperCase().replace("_", "-");
    }

    const analogySub = document.getElementById("stat-analogy-sub");
    if (analogySub) {
        analogySub.textContent = model.analogy_name ? `${model.analogy_name} Analogy` : "Shared Responsibility";
    }

    const summaryEl = document.getElementById("matrix-summary");
    if (currentView === "pizza") {
        summaryEl.innerHTML = `
            <strong>🍕 Pizza Analogy — ${model.analogy_name || model.name}:</strong> ${model.analogy_summary || model.summary}
            ${model.examples ? `<br><span style="font-size: 0.8rem; color: var(--text-secondary);"><strong>Tech Equivalents:</strong> ${model.examples}</span>` : ''}
        `;
    } else {
        summaryEl.innerHTML = `
            <strong>${model.name}:</strong> ${model.summary}
            ${model.examples ? `<br><span style="font-size: 0.8rem; color: var(--text-secondary);"><strong>Industry Examples:</strong> ${model.examples}</span>` : ''}
        `;
    }

    const container = document.getElementById("layers-stack-container");
    container.innerHTML = "";

    if (currentView === "pizza") {
        const providerList = model.pizza_provider || [];
        pizzaLayersData.forEach(layer => {
            const isProvider = providerList.includes(layer.id);
            const div = document.createElement("div");
            div.className = `layer-item ${isProvider ? 'layer-provider' : 'layer-customer'}`;

            div.innerHTML = `
                <div>
                    <span class="layer-category">${layer.category} Layer</span>
                    <div class="layer-name">🍕 ${layer.name}</div>
                </div>
                <span class="layer-tag">
                    ${isProvider ? '🏪 Pizzeria / Restaurant Supplies' : '👤 You Provide at Home'}
                </span>
            `;
            container.appendChild(div);
        });
    } else {
        const providerList = model.provider_managed || [];
        layersData.forEach(layer => {
            const isProvider = providerList.includes(layer.id);
            const div = document.createElement("div");
            div.className = `layer-item ${isProvider ? 'layer-provider' : 'layer-customer'}`;

            div.innerHTML = `
                <div>
                    <span class="layer-category">${layer.category} Layer</span>
                    <div class="layer-name">☁️ ${layer.name}</div>
                </div>
                <span class="layer-tag">
                    ${isProvider ? '☁️ Cloud Provider Managed' : '👤 Customer Managed & Secured'}
                </span>
            `;
            container.appendChild(div);
        });
    }
}

async function fetchState() {
    try {
        const res = await fetch("/api/state");
        if (!res.ok) return;
        const data = await res.json();

        // Top Stats
        const iaasCount = document.getElementById("stat-iaas-count");
        const paasCount = document.getElementById("stat-paas-count");
        const saasCount = document.getElementById("stat-saas-count");

        if (iaasCount) iaasCount.textContent = data.iaas_instances.length;
        if (paasCount) paasCount.textContent = data.paas_deployments.length;
        if (saasCount) saasCount.textContent = data.saas_tenants.length;

        // Render Lists
        renderIaasList(data.iaas_instances);
        renderPaasList(data.paas_deployments);
        renderSaasList(data.saas_tenants);
    } catch (err) {
        console.error("Failed to fetch state:", err);
    }
}

function renderIaasList(instances) {
    const container = document.getElementById("iaas-instances-list");
    container.innerHTML = "";

    if (!instances.length) {
        container.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-muted);">No IaaS virtual machines running.</div>`;
        return;
    }

    instances.forEach(inst => {
        const isPatched = inst.os_patch_status.startsWith("patched");
        const isCritical = inst.cve_vulnerable || inst.os_patch_status.includes("CRITICAL");
        const div = document.createElement("div");
        div.className = "item-card";
        if (isCritical) {
            div.style.borderColor = "var(--danger)";
            div.style.backgroundColor = "rgba(239, 68, 68, 0.05)";
        }

        div.innerHTML = `
            <div class="item-header">
                <span class="item-title">🖥️ ${escapeHtml(inst.instance_id)} (${escapeHtml(inst.os)})</span>
                <span class="pill ${isCritical ? 'pill-danger' : (isPatched ? 'pill-green' : 'pill-warning')}">${inst.status}</span>
            </div>
            <div class="item-details">
                <span>Hardware: <strong>${inst.vcpu} vCPU</strong> · <strong>${inst.ram_gb} GB RAM</strong> · Uptime: ${escapeHtml(inst.uptime)}</span>
                <span>Networking: Private <code>${inst.private_ip}</code> · Public Elastic IP <code>${inst.public_ip}</code></span>
                <span>OS Kernel Patch: <strong style="color: ${isCritical ? 'var(--danger)' : (isPatched ? 'var(--success)' : 'var(--warn)')};">${escapeHtml(inst.os_patch_status)}</strong></span>
            </div>
            <div class="item-actions">
                ${!isPatched ? `<button class="btn-sm btn-patch" data-id="${inst.instance_id}">🔧 Run Security Patch (apt-get upgrade)</button>` : '<span style="font-size: 0.78rem; color: var(--success); font-weight: 600;">✓ Linux Kernel Fully Patched</span>'}
                <button class="btn-sm btn-cve" data-id="${inst.instance_id}">⚠️ Simulate Kernel CVE</button>
                <button class="btn-sm btn-danger btn-term" data-id="${inst.instance_id}">Terminate</button>
            </div>
        `;

        const patchBtn = div.querySelector(".btn-patch");
        if (patchBtn) {
            patchBtn.addEventListener("click", async () => {
                await patchIaas(inst.instance_id);
            });
        }

        const cveBtn = div.querySelector(".btn-cve");
        if (cveBtn) {
            cveBtn.addEventListener("click", async () => {
                await simulateCveIaas(inst.instance_id);
                highlightStep(3);
            });
        }

        div.querySelector(".btn-term").addEventListener("click", async () => {
            await terminateIaas(inst.instance_id);
        });

        container.appendChild(div);
    });
}

function renderPaasList(deployments) {
    const container = document.getElementById("paas-deployments-list");
    container.innerHTML = "";

    if (!deployments.length) {
        container.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-muted);">No PaaS applications deployed.</div>`;
        return;
    }

    deployments.forEach(dep => {
        const div = document.createElement("div");
        div.className = "item-card";

        div.innerHTML = `
            <div class="item-header">
                <span class="item-title">🚀 ${escapeHtml(dep.app_name)} (<code>${escapeHtml(dep.deployment_id)}</code>)</span>
                <span class="pill pill-green">${escapeHtml(dep.health)}</span>
            </div>
            <div class="item-details">
                <span>Runtime: <strong>${escapeHtml(dep.runtime)}</strong></span>
                <span>URL: <a href="${escapeHtml(dep.url)}" target="_blank" style="color: var(--accent);">${escapeHtml(dep.url)}</a></span>
                <span>Horizontal Scale: <strong>${dep.replicas} Active Replicas</strong> (${escapeHtml(dep.auto_scaling_range)})</span>
                <span>Host Maintenance: <strong style="color: var(--success);">${escapeHtml(dep.os_management)}</strong></span>
            </div>
            <div class="item-actions">
                <button class="btn-sm btn-scale-down" data-id="${dep.deployment_id}" data-rep="${dep.replicas - 1}">-1 Replica</button>
                <button class="btn-sm btn-scale-up" data-id="${dep.deployment_id}" data-rep="${dep.replicas + 1}">+1 Replica</button>
                <button class="btn-sm btn-cve-check">🛡️ Vulnerability Immune Check</button>
            </div>
        `;

        div.querySelector(".btn-scale-up").addEventListener("click", async (e) => {
            const rep = parseInt(e.target.getAttribute("data-rep"), 10);
            await scalePaas(dep.deployment_id, rep);
            highlightStep(4);
        });

        div.querySelector(".btn-scale-down").addEventListener("click", async (e) => {
            const rep = parseInt(e.target.getAttribute("data-rep"), 10);
            await scalePaas(dep.deployment_id, rep);
        });

        div.querySelector(".btn-cve-check").addEventListener("click", () => {
            alert("✓ PaaS Platform Security Check Passed!\n\nBecause you are using PaaS, the underlying Linux kernel and hypervisor security patches are managed 100% automatically by the Cloud Provider with zero downtime. Customer action is ZERO.");
        });

        container.appendChild(div);
    });
}

function renderSaasList(tenants) {
    const container = document.getElementById("saas-tenants-list");
    container.innerHTML = "";

    if (!tenants.length) {
        container.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-muted);">No SaaS workspaces active.</div>`;
        return;
    }

    tenants.forEach(t => {
        const div = document.createElement("div");
        div.className = "item-card";

        div.innerHTML = `
            <div class="item-header">
                <span class="item-title">🏢 ${escapeHtml(t.company)} (<code>${escapeHtml(t.tenant_id)}</code>)</span>
                <span class="pill" style="background: var(--saas-dim); color: var(--saas);">${escapeHtml(t.plan)}</span>
            </div>
            <div class="item-details">
                <span>User Accounts: <strong>${t.users} Allocated Seats</strong> · Created: ${escapeHtml(t.created_at)}</span>
                <span>Cloud Storage Allocated: <strong>${t.storage_used_mb} MB</strong></span>
                <span>Tenant Isolation: <strong style="color: var(--saas);">Multi-Tenant Logical DB Partition (0 Infrastructure Overhead)</strong></span>
            </div>
            <div class="item-actions">
                <button class="btn-sm btn-danger btn-del-tenant" data-id="${t.tenant_id}">Decommission Tenant</button>
            </div>
        `;

        div.querySelector(".btn-del-tenant").addEventListener("click", async () => {
            await deleteSaasTenant(t.tenant_id);
        });

        container.appendChild(div);
    });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// Action Callbacks
async function provisionIaas() {
    const os = document.getElementById("iaas-os").value;
    const vcpu = parseInt(document.getElementById("iaas-vcpu").value, 10);
    const ram_gb = parseInt(document.getElementById("iaas-ram").value, 10);

    try {
        await fetch("/api/iaas/provision", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ os, vcpu, ram_gb })
        });
        fetchState();
        highlightStep(3);
    } catch (err) {
        alert("Error provisioning IaaS VM: " + err.message);
    }
}

async function patchIaas(instanceId) {
    try {
        await fetch("/api/iaas/patch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ instance_id: instanceId })
        });
        fetchState();
    } catch (err) {
        alert("Error patching IaaS VM: " + err.message);
    }
}

async function simulateCveIaas(instanceId) {
    try {
        await fetch("/api/iaas/simulate-cve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ instance_id: instanceId })
        });
        fetchState();
    } catch (err) {
        alert("Error simulating CVE: " + err.message);
    }
}

async function terminateIaas(instanceId) {
    try {
        await fetch(`/api/iaas/terminate/${instanceId}`, { method: "DELETE" });
        fetchState();
    } catch (err) {
        alert("Error terminating VM: " + err.message);
    }
}

async function deployPaas() {
    const name = document.getElementById("paas-name").value.trim() || "my-app";
    const runtime = document.getElementById("paas-runtime").value;
    const branch = document.getElementById("paas-branch").value.trim() || "main";

    try {
        await fetch("/api/paas/deploy", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ app_name: name, runtime, branch })
        });
        fetchState();
        highlightStep(4);
    } catch (err) {
        alert("Error deploying PaaS app: " + err.message);
    }
}

async function scalePaas(deploymentId, replicas) {
    try {
        await fetch("/api/paas/scale", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ deployment_id: deploymentId, replicas })
        });
        fetchState();
    } catch (err) {
        alert("Error scaling PaaS app: " + err.message);
    }
}

async function createSaasTenant() {
    const company = document.getElementById("saas-company").value.trim() || "Acme Partner";
    const users = parseInt(document.getElementById("saas-users").value, 10);
    const plan = document.getElementById("saas-plan").value;

    try {
        await fetch("/api/saas/tenant", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ company, users, plan })
        });
        fetchState();
        highlightStep(4);
    } catch (err) {
        alert("Error creating SaaS tenant: " + err.message);
    }
}

async function deleteSaasTenant(tenantId) {
    try {
        await fetch(`/api/saas/tenant/${tenantId}`, { method: "DELETE" });
        fetchState();
    } catch (err) {
        alert("Error deleting SaaS tenant: " + err.message);
    }
}
