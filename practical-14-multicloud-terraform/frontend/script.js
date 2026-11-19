// Practical 14: Multi-Cloud Terraform Frontend Controller

document.addEventListener("DOMContentLoaded", () => {
    fetchStatus();

    document.getElementById("btn-init").addEventListener("click", () => runCommand("/api/init"));
    document.getElementById("btn-plan").addEventListener("click", () => runCommand("/api/plan"));
    document.getElementById("btn-apply").addEventListener("click", () => runCommand("/api/apply"));
    document.getElementById("btn-refresh").addEventListener("click", () => runCommand("/api/refresh"));
    document.getElementById("btn-destroy").addEventListener("click", () => runCommand("/api/destroy"));

    document.getElementById("btn-trigger-drift").addEventListener("click", triggerDrift);
    document.getElementById("btn-save-hcl").addEventListener("click", saveHcl);
});

async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();

        // Top Stats
        document.getElementById("stat-resources").textContent = data.resource_count;
        document.getElementById("stat-serial").textContent = `v${data.serial}`;

        const driftStat = document.getElementById("stat-drift");
        if (data.drift_detected) {
            driftStat.textContent = "⚠️ Drift Detected!";
            driftStat.className = "value text-warning";
            driftStat.style.color = "#ea580c";
        } else {
            driftStat.textContent = "In-Sync (Clean)";
            driftStat.className = "value text-success";
        }

        // HCL Editor
        const editor = document.getElementById("hcl-editor");
        if (!editor.value) {
            editor.value = data.hcl_code;
        }

        // State Viewer
        document.getElementById("state-viewer").textContent = JSON.stringify(data.tfstate, null, 2);
        document.getElementById("state-serial-pill").textContent = `Serial: ${data.serial}`;

        // Active Resources
        renderActiveResources(data.active_resources);

    } catch (err) {
        console.error("Failed to fetch status:", err);
    }
}

function renderActiveResources(resources) {
    const container = document.getElementById("active-resources-list");
    container.innerHTML = "";

    const keys = Object.keys(resources);
    if (!keys.length) {
        container.innerHTML = `<div class="text-sm text-muted">No cloud resources active (0 provisioned). Run "terraform apply" to deploy.</div>`;
        return;
    }

    keys.forEach(k => {
        const attrs = resources[k];
        let providerClass = "provider-aws";
        let providerBadge = "AWS";

        if (k.startsWith("google")) {
            providerClass = "provider-google";
            providerBadge = "Google Cloud";
        } else if (k.startsWith("docker")) {
            providerClass = "provider-docker";
            providerBadge = "Docker Edge";
        }

        const div = document.createElement("div");
        div.className = `resource-card ${providerClass}`;

        div.innerHTML = `
            <div class="resource-header">
                <span class="resource-name">${k}</span>
                <span class="pill pill-gray">${providerBadge}</span>
            </div>
            <div class="resource-attrs">
                ${Object.entries(attrs).map(([attrKey, attrVal]) => `
                    <span><strong>${attrKey}:</strong> ${typeof attrVal === 'object' ? JSON.stringify(attrVal) : attrVal}</span>
                `).join(" · ")}
            </div>
        `;
        container.appendChild(div);
    });
}

async function runCommand(endpoint) {
    const term = document.getElementById("terminal-output");
    term.textContent = `Running ${endpoint.replace('/api/', 'terraform ')}...`;

    try {
        const res = await fetch(endpoint, { method: "POST" });
        const data = await res.json();

        term.textContent = data.output;
        fetchStatus();

    } catch (err) {
        term.textContent = `Error executing command: ${err.message}`;
    }
}

async function triggerDrift() {
    const term = document.getElementById("terminal-output");
    term.textContent = "Simulating out-of-band ClickOps modification in AWS S3...";

    try {
        const res = await fetch("/api/drift", { method: "POST" });
        const data = await res.json();

        if (data.drift_detected) {
            term.textContent = `[!] Out-of-band Drift injected into ${data.target}!\n\nAn engineer logged into the AWS Web Console manually and deleted the "Environment=Production" tag.\n\nNow click "terraform plan" above to see Terraform detect the drift and plan the reconciliation!`;
        } else {
            term.textContent = `Error triggering drift: ${data.error}`;
        }
        fetchStatus();

    } catch (err) {
        term.textContent = `Failed to trigger drift: ${err.message}`;
    }
}

async function saveHcl() {
    const hcl_code = document.getElementById("hcl-editor").value;
    try {
        await fetch("/api/hcl", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ hcl_code })
        });
        alert("Configuration saved. Click 'terraform plan' to evaluate changes.");
        fetchStatus();
    } catch (err) {
        alert("Failed to save HCL: " + err.message);
    }
}
