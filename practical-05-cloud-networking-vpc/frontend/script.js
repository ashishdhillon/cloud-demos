// Practical 05: Cloud Networking & VPC Simulator Frontend Controller

document.addEventListener("DOMContentLoaded", () => {
    fetchTopology();

    document.getElementById("btn-trace-packet").addEventListener("click", simulatePacket);

    document.querySelectorAll(".btn-scenario").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const b = e.target;
            document.getElementById("pkt-src").value = b.getAttribute("data-src");
            document.getElementById("pkt-dst").value = b.getAttribute("data-dst");
            document.getElementById("pkt-port").value = b.getAttribute("data-port");
            document.getElementById("pkt-proto").value = b.getAttribute("data-proto");
            simulatePacket();
        });
    });
});

async function fetchTopology() {
    try {
        const res = await fetch("/api/topology");
        if (!res.ok) return;
        const data = await res.json();

        // Populate Security Groups
        const webSg = data.security_groups.find(g => g.group_id === "sg-web-public");
        const dbSg = data.security_groups.find(g => g.group_id === "sg-db-private");

        if (webSg) renderSecurityRules("web-sg-rules", webSg);
        if (dbSg) renderSecurityRules("db-sg-rules", dbSg);

    } catch (err) {
        console.error("Failed to fetch topology:", err);
    }
}

function renderSecurityRules(containerId, sg) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    sg.ingress_rules.forEach(rule => {
        const div = document.createElement("div");
        div.className = "rule-item";

        div.innerHTML = `
            <div class="rule-info">
                <span class="rule-headline">${rule.protocol} Port ${rule.port} &larr; ${rule.source}</span>
                <span class="rule-desc">${rule.description}</span>
            </div>
            <button class="rule-toggle-btn ${rule.enabled ? 'rule-active' : 'rule-disabled'}" data-group="${sg.group_id}" data-rule="${rule.id}">
                ${rule.enabled ? '✓ Enabled' : '✕ Denied'}
            </button>
        `;

        div.querySelector("button").addEventListener("click", async (e) => {
            const btn = e.target;
            const groupId = btn.getAttribute("data-group");
            const ruleId = btn.getAttribute("data-rule");
            await toggleRule(groupId, ruleId);
        });

        container.appendChild(div);
    });
}

async function toggleRule(groupId, ruleId) {
    try {
        const res = await fetch("/api/security-groups/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ group_id: groupId, rule_id: ruleId })
        });
        if (res.ok) {
            fetchTopology();
            // Re-simulate current packet to reflect immediate firewall impact
            simulatePacket();
        }
    } catch (err) {
        console.error("Failed to toggle rule:", err);
    }
}

async function simulatePacket() {
    const src = document.getElementById("pkt-src").value.trim();
    const dst = document.getElementById("pkt-dst").value.trim();
    const port = parseInt(document.getElementById("pkt-port").value.trim(), 10);
    const proto = document.getElementById("pkt-proto").value;

    const verdictPill = document.getElementById("trace-verdict-pill");
    const timeline = document.getElementById("trace-timeline");

    verdictPill.textContent = "Routing...";
    verdictPill.className = "pill pill-gray";

    try {
        const res = await fetch("/api/packet/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ source_ip: src, dest_ip: dst, port, protocol: proto })
        });

        const data = await res.json();
        if (!res.ok) {
            alert(`Packet Simulation Error: ${data.error}`);
            return;
        }

        // Render Verdict
        if (data.verdict === "ALLOWED") {
            verdictPill.textContent = `✓ ${data.verdict} (HTTP ${data.status_code})`;
            verdictPill.className = "pill pill-green";
        } else {
            verdictPill.textContent = `✕ ${data.verdict} (${data.status_code})`;
            verdictPill.className = "pill pill-warning";
            verdictPill.style.background = "#fee2e2";
            verdictPill.style.color = "#991b1b";
        }

        // Render Timeline Hops
        timeline.innerHTML = "";
        data.hops.forEach(h => {
            const card = document.createElement("div");
            card.className = `hop-card ${h.status === 'PASS' ? 'hop-pass' : 'hop-drop'}`;

            card.innerHTML = `
                <div class="hop-top">
                    <span>Hop ${h.hop}: ${h.component}</span>
                    <span style="color: ${h.status === 'PASS' ? '#166534' : '#991b1b'};">${h.status}</span>
                </div>
                <div class="hop-action">${h.action}</div>
            `;
            timeline.appendChild(card);
        });

    } catch (err) {
        alert("Failed to simulate packet: " + err.message);
    }
}
