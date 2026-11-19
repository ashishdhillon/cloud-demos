// Practical 01: Cloud Service Models Frontend Controller

let currentModel = "iaas";
let layersData = [];
let matrixData = {};

document.addEventListener("DOMContentLoaded", () => {
    fetchOverview();
    fetchState();

    // Model Buttons
    document.querySelectorAll(".btn-model").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".btn-model").forEach(b => b.classList.remove("active"));
            e.target.classList.add("active");
            currentModel = e.target.getAttribute("data-model");
            renderMatrix();
        });
    });

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

    // Workbench Action Listeners
    document.getElementById("btn-provision-iaas").addEventListener("click", provisionIaas);
    document.getElementById("btn-deploy-paas").addEventListener("click", deployPaas);
    document.getElementById("btn-create-saas").addEventListener("click", createSaasTenant);
});

async function fetchOverview() {
    try {
        const res = await fetch("/api/overview");
        if (!res.ok) return;
        const data = await res.json();
        layersData = data.layers;
        matrixData = data.models_matrix;
        renderMatrix();
    } catch (err) {
        console.error("Failed to fetch overview:", err);
    }
}

function renderMatrix() {
    const model = matrixData[currentModel];
    if (!model) return;

    document.getElementById("stat-selected-model").textContent = currentModel.toUpperCase().replace("_", "-");
    document.getElementById("matrix-summary").innerHTML = `
        <strong>${model.name}:</strong> ${model.summary}
        ${model.examples ? `<br><span class="text-sm text-muted"><strong>Industry Examples:</strong> ${model.examples}</span>` : ''}
    `;

    const container = document.getElementById("layers-stack-container");
    container.innerHTML = "";

    layersData.forEach(layer => {
        const isProvider = model.provider_managed.includes(layer.id);
        const div = document.createElement("div");
        div.className = `layer-item ${isProvider ? 'layer-provider' : 'layer-customer'}`;

        div.innerHTML = `
            <div>
                <span class="layer-category">${layer.category} Layer</span>
                <div>${layer.name}</div>
            </div>
            <span class="layer-tag">
                ${isProvider ? '☁️ Cloud Provider' : '👤 Customer Managed'}
            </span>
        `;
        container.appendChild(div);
    });
}

async function fetchState() {
    try {
        const res = await fetch("/api/state");
        if (!res.ok) return;
        const data = await res.json();

        // Top Stats
        document.getElementById("stat-iaas-count").textContent = data.iaas_instances.length;
        document.getElementById("stat-paas-count").textContent = data.paas_deployments.length;
        document.getElementById("stat-saas-count").textContent = data.saas_tenants.length;

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
        container.innerHTML = `<div class="text-sm text-muted">No IaaS virtual machines running.</div>`;
        return;
    }

    instances.forEach(inst => {
        const isPatched = inst.os_patch_status.startsWith("patched");
        const div = document.createElement("div");
        div.className = "item-card";

        div.innerHTML = `
            <div class="item-header">
                <span class="item-title">🖥️ ${inst.instance_id} (${inst.os})</span>
                <span class="pill ${isPatched ? 'pill-green' : 'pill-warning'}">${inst.status}</span>
            </div>
            <div class="item-details">
                <span>Compute: ${inst.vcpu} vCPU · ${inst.ram_gb} GB RAM · Uptime: ${inst.uptime}</span>
                <span>Private IP: <code>${inst.private_ip}</code> · Public IP: <code>${inst.public_ip}</code></span>
                <span>OS Patch Status: <strong style="color: ${isPatched ? '#10b981' : '#ea580c'};">${inst.os_patch_status}</strong></span>
            </div>
            <div class="item-actions">
                ${!isPatched ? `<button class="btn btn-sm btn-warning btn-patch" data-id="${inst.instance_id}">🔧 Run OS Security Patch (apt upgrade)</button>` : '<span class="text-sm text-success">✓ OS Secure</span>'}
                <button class="btn btn-sm btn-danger btn-term" data-id="${inst.instance_id}">Terminate</button>
            </div>
        `;

        const patchBtn = div.querySelector(".btn-patch");
        if (patchBtn) {
            patchBtn.addEventListener("click", async () => {
                await patchIaas(inst.instance_id);
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
        container.innerHTML = `<div class="text-sm text-muted">No PaaS applications deployed.</div>`;
        return;
    }

    deployments.forEach(dep => {
        const div = document.createElement("div");
        div.className = "item-card";

        div.innerHTML = `
            <div class="item-header">
                <span class="item-title">🚀 ${dep.app_name} (<code>${dep.deployment_id}</code>)</span>
                <span class="pill pill-green">${dep.health}</span>
            </div>
            <div class="item-details">
                <span>Runtime: <strong>${dep.runtime}</strong></span>
                <span>URL: <a href="${dep.url}" target="_blank" style="color: #0284c7;">${dep.url}</a></span>
                <span>Horizontal Scale: <strong>${dep.replicas} Active Replicas</strong> (${dep.auto_scaling_range})</span>
                <span>Maintenance: <strong style="color: #10b981;">${dep.os_management}</strong></span>
            </div>
            <div class="item-actions">
                <button class="btn btn-sm btn-secondary btn-scale-down" data-id="${dep.deployment_id}" data-rep="${dep.replicas - 1}">-1 Replica</button>
                <button class="btn btn-sm btn-primary btn-scale-up" data-id="${dep.deployment_id}" data-rep="${dep.replicas + 1}">+1 Replica</button>
            </div>
        `;

        div.querySelector(".btn-scale-up").addEventListener("click", async (e) => {
            const rep = parseInt(e.target.getAttribute("data-rep"), 10);
            await scalePaas(dep.deployment_id, rep);
        });

        div.querySelector(".btn-scale-down").addEventListener("click", async (e) => {
            const rep = parseInt(e.target.getAttribute("data-rep"), 10);
            await scalePaas(dep.deployment_id, rep);
        });

        container.appendChild(div);
    });
}

function renderSaasList(tenants) {
    const container = document.getElementById("saas-tenants-list");
    container.innerHTML = "";

    if (!tenants.length) {
        container.innerHTML = `<div class="text-sm text-muted">No SaaS workspaces active.</div>`;
        return;
    }

    tenants.forEach(t => {
        const div = document.createElement("div");
        div.className = "item-card";

        div.innerHTML = `
            <div class="item-header">
                <span class="item-title">🏢 ${t.company} (<code>${t.tenant_id}</code>)</span>
                <span class="pill" style="background: #ede9fe; color: #6d28d9;">${t.plan}</span>
            </div>
            <div class="item-details">
                <span>User Accounts: <strong>${t.users} Allocated Seats</strong> · Created: ${t.created_at}</span>
                <span>Cloud Storage Allocated: <strong>${t.storage_used_mb} MB</strong></span>
                <span>Tenant Isolation: <strong style="color: #7c3aed;">Multi-Tenant Logical DB Partition (0 Infrastructure Overhead)</strong></span>
            </div>
            <div class="item-actions">
                <button class="btn btn-sm btn-danger btn-del-tenant" data-id="${t.tenant_id}">Decommission Tenant</button>
            </div>
        `;

        div.querySelector(".btn-del-tenant").addEventListener("click", async () => {
            await deleteSaasTenant(t.tenant_id);
        });

        container.appendChild(div);
    });
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
