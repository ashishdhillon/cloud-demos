// Practical 08: Cloud Security & Envelope Encryption Frontend Controller

let storedEnvelopes = [];

document.addEventListener("DOMContentLoaded", () => {
    fetchStatus();
    fetchCertificate();

    document.getElementById("btn-encrypt").addEventListener("click", encryptPayload);
});

async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById("stat-kms-key").textContent = data.kms_key_id.split("/").pop();
        document.getElementById("stat-compliance").textContent = `${data.compliance_score_pct}%`;
        document.getElementById("compliance-pill").textContent = `${data.compliance_score_pct}% Score`;
        document.getElementById("stat-envelopes").textContent = data.total_envelopes_stored;

        renderPostureChecks(data.posture_checks);
    } catch (err) {
        console.error("Failed to fetch status:", err);
    }
}

async function fetchCertificate() {
    try {
        const res = await fetch("/api/certificate");
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById("cert-cn").textContent = `CN: ${data.common_name} (O: ${data.organization})`;
        document.getElementById("cert-san").textContent = data.san_domains.join(", ");
        document.getElementById("cert-fingerprint").textContent = data.sha256_fingerprint;
        document.getElementById("cert-validity").textContent = `${data.valid_from} &rarr; ${data.valid_until}`;
    } catch (err) {
        console.error("Failed to fetch certificate:", err);
    }
}

function renderPostureChecks(checks) {
    const container = document.getElementById("posture-checks-list");
    container.innerHTML = "";

    checks.forEach(check => {
        const div = document.createElement("div");
        div.className = "check-item";

        div.innerHTML = `
            <div class="check-info">
                <span class="check-title">${check.title}</span>
                <span class="check-desc">${check.description}</span>
            </div>
            <button class="check-toggle-btn ${check.enabled ? 'check-pass' : 'check-fail'}" data-id="${check.id}">
                ${check.enabled ? '✓ Compliant' : '✕ Non-Compliant'}
            </button>
        `;

        div.querySelector("button").addEventListener("click", async (e) => {
            const checkId = e.target.getAttribute("data-id");
            await togglePostureCheck(checkId);
        });

        container.appendChild(div);
    });
}

async function togglePostureCheck(checkId) {
    try {
        const res = await fetch("/api/posture/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ check_id: checkId })
        });
        if (res.ok) {
            fetchStatus();
        }
    } catch (err) {
        console.error("Failed to toggle check:", err);
    }
}

async function encryptPayload() {
    const plaintext = document.getElementById("plaintext-input").value.trim();
    const label = document.getElementById("payload-label").value.trim() || "Confidential Record";
    const statusPill = document.getElementById("trace-status-pill");

    if (!plaintext) {
        alert("Please enter a plaintext payload to encrypt.");
        return;
    }

    statusPill.textContent = "Encrypting...";
    statusPill.className = "pill pill-gray";

    try {
        const res = await fetch("/api/envelope/encrypt", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ plaintext, label })
        });
        const data = await res.json();

        if (!res.ok) {
            alert(`Encryption Error: ${data.error}`);
            return;
        }

        statusPill.textContent = "✓ Envelope Encrypted";
        statusPill.className = "pill pill-green";

        renderTrace(data.trace);
        storedEnvelopes.unshift(data.envelope);
        renderEnvelopes();
        fetchStatus();

    } catch (err) {
        alert("Failed to encrypt: " + err.message);
    }
}

function renderTrace(steps) {
    const container = document.getElementById("envelope-trace");
    container.innerHTML = "";

    steps.forEach(step => {
        const div = document.createElement("div");
        div.className = "trace-card";

        div.innerHTML = `
            <div class="trace-top">
                <span>Step ${step.step}: ${step.component}</span>
                <span style="color: #166534;">✓ Success</span>
            </div>
            <div class="trace-action"><strong>${step.action}</strong></div>
            <div class="trace-details">${step.details}</div>
        `;
        container.appendChild(div);
    });
}

function renderEnvelopes() {
    const container = document.getElementById("envelopes-list");
    if (!storedEnvelopes.length) {
        container.innerHTML = `<div class="text-sm text-muted">No envelopes created yet.</div>`;
        return;
    }

    container.innerHTML = "";
    storedEnvelopes.forEach(env => {
        const div = document.createElement("div");
        div.className = "envelope-card";

        div.innerHTML = `
            <div class="envelope-header">
                <span class="envelope-title">${env.label} (<code>${env.envelope_id}</code>)</span>
                <span class="pill pill-gray">${env.algorithm}</span>
            </div>
            <div class="envelope-meta">
                KMS Key: <code>${env.kms_key_id.split('/').pop()}</code> · Encrypted DEK: <code>${env.encrypted_dek_b64.substring(0, 24)}...</code>
            </div>
            <div class="envelope-payload-preview">
                Ciphertext: ${env.ciphertext_payload_b64.substring(0, 60)}... (${env.ciphertext_bytes_len} bytes)
            </div>
            <button class="btn btn-sm btn-primary btn-decrypt" data-id="${env.envelope_id}">
                🔓 Decrypt with KMS
            </button>
            <div class="decrypted-result mt-8" id="dec-${env.envelope_id}" style="display: none;"></div>
        `;

        div.querySelector(".btn-decrypt").addEventListener("click", async () => {
            await decryptEnvelope(env.envelope_id);
        });

        container.appendChild(div);
    });
}

async function decryptEnvelope(envelopeId) {
    const resultBox = document.getElementById(`dec-${envelopeId}`);
    resultBox.style.display = "block";
    resultBox.innerHTML = `<span class="text-sm text-muted">Contacting KMS & verifying authentication tag...</span>`;

    try {
        const res = await fetch("/api/envelope/decrypt", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ envelope_id: envelopeId })
        });
        const data = await res.json();

        if (!res.ok) {
            resultBox.innerHTML = `<span class="text-danger text-sm">Decryption Failed: ${data.error}</span>`;
            return;
        }

        resultBox.innerHTML = `
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 10px; border-radius: 6px;">
                <strong style="color: #166534; font-size: 0.8rem;">Decrypted Plaintext (Zero Data Loss):</strong>
                <p style="font-family: var(--font-mono); font-size: 0.825rem; color: #0f172a; margin-top: 4px;">${data.decrypted_plaintext}</p>
            </div>
        `;
    } catch (err) {
        resultBox.innerHTML = `<span class="text-danger text-sm">Error: ${err.message}</span>`;
    }
}
