let personas = {};
let activePersonaId = "junior-developer";

// Elements
const elPersonaTabs = document.getElementById("persona-tabs");
const elPersonaName = document.getElementById("active-persona-name");
const elPersonaArn = document.getElementById("active-persona-arn");
const elPersonaDesc = document.getElementById("active-persona-desc");
const elPolicyJsonCode = document.getElementById("policy-json-code");
const elPolicyJsonContainer = document.getElementById("policy-json-container");
const elBtnToggleJson = document.getElementById("btn-toggle-json");
const elToggleMfa = document.getElementById("toggle-mfa");

const elVerdictBanner = document.getElementById("verdict-banner");
const elVerdictIcon = document.getElementById("verdict-icon");
const elVerdictText = document.getElementById("verdict-text");
const elVerdictSubtext = document.getElementById("verdict-subtext");
const elEvalSpeed = document.getElementById("eval-speed");
const elPipelineSteps = document.getElementById("pipeline-steps");
const elMatchedStmtBox = document.getElementById("matched-stmt-box");
const elMatchedSid = document.getElementById("matched-sid");
const elMatchedStmtCode = document.getElementById("matched-stmt-code");
const elAuditTableBody = document.getElementById("audit-table-body");

const elCustomAction = document.getElementById("custom-action");
const elCustomResource = document.getElementById("custom-resource");
const elBtnEvalCustom = document.getElementById("btn-eval-custom");

async function loadPersonas() {
    try {
        const res = await fetch("/api/personas");
        if (!res.ok) return;
        const data = await res.json();
        personas = data.personas;
        renderPersonaTabs();
        selectPersona(activePersonaId);
    } catch (err) {
        console.error("Failed to load personas:", err);
    }
}

function renderPersonaTabs() {
    elPersonaTabs.innerHTML = "";
    Object.keys(personas).forEach(id => {
        const p = personas[id];
        const btn = document.createElement("button");
        btn.className = `persona-tab ${id === activePersonaId ? 'active' : ''}`;
        btn.textContent = p.name;
        btn.onclick = () => selectPersona(id);
        elPersonaTabs.appendChild(btn);
    });
}

function selectPersona(id) {
    activePersonaId = id;
    const p = personas[id];
    if (!p) return;

    document.querySelectorAll(".persona-tab").forEach(tab => {
        tab.classList.toggle("active", tab.textContent.includes(p.name));
    });

    elPersonaName.textContent = p.name;
    elPersonaArn.textContent = p.role_arn;
    elPersonaDesc.textContent = p.description;
    elPolicyJsonCode.textContent = JSON.stringify(p.policy, null, 2);
}

elBtnToggleJson.onclick = () => {
    elPolicyJsonContainer.classList.toggle("hidden");
    elBtnToggleJson.textContent = elPolicyJsonContainer.classList.contains("hidden") 
        ? "View Attached Policy JSON ▾" 
        : "Hide Attached Policy JSON ▴";
};

async function simulateAction(action, resource) {
    const isMfa = elToggleMfa.checked;
    const context = {
        "aws:MultiFactorAuthPresent": isMfa ? "true" : "false"
    };

    try {
        const res = await fetch("/api/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                persona: activePersonaId,
                action: action,
                resource: resource,
                context: context
            })
        });

        if (!res.ok) return;
        const data = await res.json();
        renderEvaluationResult(data);
        loadAudit();
    } catch (err) {
        console.error("Evaluation error:", err);
    }
}

function renderEvaluationResult(data) {
    elEvalSpeed.textContent = `Latency: ${data.eval_time_ms} ms`;
    elVerdictBanner.className = "verdict-banner";

    if (data.decision_type === "EXPLICIT_ALLOW") {
        elVerdictBanner.classList.add("allow");
        elVerdictIcon.textContent = "✅";
        elVerdictText.textContent = "ACCESS GRANTED (200 OK)";
        elVerdictSubtext.textContent = `Action '${data.action}' permitted by Statement '${data.matched_statement_sid}'.`;
    } else if (data.decision_type === "EXPLICIT_DENY") {
        elVerdictBanner.classList.add("explicit-deny");
        elVerdictIcon.textContent = "🚫";
        elVerdictText.textContent = "EXPLICIT DENY (403 FORBIDDEN)";
        elVerdictSubtext.textContent = `Action blocked by explicit deny rule '${data.matched_statement_sid}'. Deny overrides all allows.`;
    } else {
        elVerdictBanner.classList.add("implicit-deny");
        elVerdictIcon.textContent = "⚠️";
        elVerdictText.textContent = "IMPLICIT DENY (403 FORBIDDEN)";
        elVerdictSubtext.textContent = `No matching Allow statement found. Default deny baseline applied.`;
    }

    // Render Steps
    elPipelineSteps.innerHTML = "";
    data.trace.forEach(step => {
        const div = document.createElement("div");
        let stepClass = "";
        if (step.status === "ALLOW") stepClass = "step-allow";
        if (step.status.includes("DENY")) stepClass = "step-deny";

        div.className = `pipeline-step ${stepClass}`;
        div.innerHTML = `
            <div class="step-num">${step.step}</div>
            <div class="step-body">
                <strong>${step.rule} &rarr; <span class="badge badge-${step.status.toLowerCase().replace('_', '-')}">${step.status}</span></strong>
                <p>${step.detail}</p>
            </div>
        `;
        elPipelineSteps.appendChild(div);

        if (step.statement) {
            elMatchedStmtBox.classList.remove("hidden");
            elMatchedSid.textContent = step.statement.Sid || "Matched";
            elMatchedStmtCode.textContent = JSON.stringify(step.statement, null, 2);
        }
    });

    if (!data.matched_statement_sid) {
        elMatchedStmtBox.classList.add("hidden");
    }
}

async function loadAudit() {
    try {
        const res = await fetch("/api/audit");
        if (!res.ok) return;
        const data = await res.json();
        renderAuditTable(data.history || []);
    } catch (err) {
        console.error("Failed to load audit history:", err);
    }
}

function renderAuditTable(history) {
    elAuditTableBody.innerHTML = "";
    if (history.length === 0) {
        elAuditTableBody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No simulation history yet.</td></tr>`;
        return;
    }

    history.forEach(item => {
        const tr = document.createElement("tr");
        let badgeClass = "badge-implicit-deny";
        if (item.decision_type === "EXPLICIT_ALLOW") badgeClass = "badge-allow";
        if (item.decision_type === "EXPLICIT_DENY") badgeClass = "badge-explicit-deny";

        tr.innerHTML = `
            <td><strong>${item.persona}</strong></td>
            <td><code>${item.action}</code></td>
            <td style="max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${item.resource}"><code>${item.resource}</code></td>
            <td><span class="badge ${badgeClass}">${item.decision_type}</span></td>
            <td>${item.eval_time_ms} ms</td>
        `;
        elAuditTableBody.appendChild(tr);
    });
}

elBtnEvalCustom.onclick = () => {
    const act = elCustomAction.value.trim();
    const res = elCustomResource.value.trim();
    if (act && res) simulateAction(act, res);
};

document.getElementById("btn-refresh-audit").onclick = loadAudit;

// Initialize
window.addEventListener("DOMContentLoaded", () => {
    loadPersonas();
    loadAudit();
});
