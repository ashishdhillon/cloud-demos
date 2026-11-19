let currentFault = "none";

// Elements
const elEdgeLatency = document.getElementById("val-edge-latency");
const elCloudLatency = document.getElementById("val-cloud-latency");
const elBandwidthSaved = document.getElementById("val-bandwidth-saved");
const elMitigations = document.getElementById("val-mitigations");
const elFaultStatusBadge = document.getElementById("fault-status-badge");

// Sensors
const elDcTemp = document.getElementById("val-dc-temp");
const elDcHumidity = document.getElementById("val-dc-humidity");
const elDcFan = document.getElementById("val-dc-fan");
const elDcStatusBadge = document.getElementById("dc-status-badge");
const elBarDcTemp = document.getElementById("bar-dc-temp");

const elPowerVoltage = document.getElementById("val-power-voltage");
const elPowerCurrent = document.getElementById("val-power-current");
const elPowerFreq = document.getElementById("val-power-freq");
const elPowerBreakerBadge = document.getElementById("power-breaker-badge");
const elBarPowerVoltage = document.getElementById("bar-power-voltage");

const elMachineryVibration = document.getElementById("val-machinery-vibration");
const elMachineryTemp = document.getElementById("val-machinery-temp");
const elMachineryRpm = document.getElementById("val-machinery-rpm");
const elMachineryStatusBadge = document.getElementById("machinery-status-badge");
const elBarMachineryVibration = document.getElementById("bar-machinery-vibration");

const elNetIngress = document.getElementById("val-net-ingress");
const elNetWan = document.getElementById("val-net-wan");
const elNetCache = document.getElementById("val-net-cache");
const elBarNetIngress = document.getElementById("bar-net-ingress");

const elAlertsContainer = document.getElementById("alerts-container");
const elAlertCountBadge = document.getElementById("alert-count-badge");
const elEventLog = document.getElementById("event-log");

async function fetchSnapshot() {
    try {
        const res = await fetch("/api/snapshot");
        if (!res.ok) return;
        const data = await res.json();
        updateUI(data);
    } catch (err) {
        console.error("Snapshot error:", err);
    }
}

function updateUI(data) {
    const t = data.telemetry;
    const stats = data.stats;
    currentFault = data.active_fault;

    // 1. Stats Banner
    elBandwidthSaved.textContent = `${stats.bandwidth_saved_pct}%`;
    elMitigations.textContent = stats.edge_mitigations;

    // 2. Fault Badges & Buttons
    updateFaultButtons(currentFault);

    // 3. Sensor 1: Datacenter Environment
    elDcTemp.textContent = `${t.datacenter.temp} °C`;
    elDcHumidity.textContent = `${t.datacenter.humidity}%`;
    elDcFan.textContent = `${t.datacenter.fan_rpm} RPM`;
    
    const tempPct = Math.min(100, Math.max(0, (t.datacenter.temp / 100) * 100));
    elBarDcTemp.style.width = `${tempPct}%`;
    
    if (t.datacenter.temp > 80) {
        elDcStatusBadge.className = "badge badge-critical";
        elDcStatusBadge.textContent = "CRITICAL OVERHEAT";
        elBarDcTemp.className = "progress-bar bg-danger";
    } else if (t.datacenter.temp > 70) {
        elDcStatusBadge.className = "badge badge-warning";
        elDcStatusBadge.textContent = "WARNING";
        elBarDcTemp.className = "progress-bar bg-warning";
    } else {
        elDcStatusBadge.className = "badge badge-normal";
        elDcStatusBadge.textContent = "Normal";
        elBarDcTemp.className = "progress-bar bg-success";
    }

    // 4. Sensor 2: Power Grid
    elPowerVoltage.textContent = `${t.power.voltage} V`;
    elPowerCurrent.textContent = `${t.power.current} A`;
    elPowerFreq.textContent = `${t.power.frequency} Hz`;
    
    const voltPct = Math.min(100, Math.max(0, (t.power.voltage / 260) * 100));
    elBarPowerVoltage.style.width = `${voltPct}%`;
    
    if (t.power.breaker.includes("TRIPPED")) {
        elPowerBreakerBadge.className = "badge badge-critical";
        elPowerBreakerBadge.textContent = "BREAKER TRIPPED";
        elBarPowerVoltage.className = "progress-bar bg-danger";
    } else {
        elPowerBreakerBadge.className = "badge badge-normal";
        elPowerBreakerBadge.textContent = "Breaker: CLOSED";
        elBarPowerVoltage.className = "progress-bar bg-primary";
    }

    // 5. Sensor 3: Machinery
    elMachineryVibration.textContent = `${t.machinery.vibration} mm/s`;
    elMachineryTemp.textContent = `${t.machinery.bearing_temp} °C`;
    elMachineryRpm.textContent = `${t.machinery.rpm}`;
    
    const vibPct = Math.min(100, Math.max(0, (t.machinery.vibration / 10) * 100));
    elBarMachineryVibration.style.width = `${vibPct}%`;
    
    if (t.machinery.vibration > 7.0) {
        elMachineryStatusBadge.className = "badge badge-critical";
        elMachineryStatusBadge.textContent = "EXCESSIVE VIBRATION";
        elBarMachineryVibration.className = "progress-bar bg-danger";
    } else {
        elMachineryStatusBadge.className = "badge badge-normal";
        elMachineryStatusBadge.textContent = "Normal";
        elBarMachineryVibration.className = "progress-bar bg-success";
    }

    // 6. Sensor 4: Network
    elNetIngress.textContent = `${t.edge_network.ingress_mbps} Mbps`;
    elNetWan.textContent = `${t.edge_network.wan_uplink_mbps} Mbps`;
    elNetCache.textContent = `${t.edge_network.cache_hit_rate}%`;

    // 7. Edge Alerts Log
    elAlertCountBadge.textContent = `${data.alerts.length} Actions`;
    if (data.alerts.length === 0) {
        elAlertsContainer.innerHTML = `<div class="empty-state">No anomalies detected. Edge monitoring is nominal.</div>`;
    } else {
        elAlertsContainer.innerHTML = data.alerts.map(a => `
            <div class="alert-item">
                <div class="header">
                    <span>⚠️ ${a.subsystem}: ${a.metric} breached (${a.value})</span>
                    <span class="latency">Edge Action in ${a.edge_latency_ms} ms</span>
                </div>
                <div class="action">&rarr; Executed: ${a.action}</div>
            </div>
        `).join("");
    }

    // 8. MQTT Events Log
    elEventLog.innerHTML = data.events.map(ev => `
        <div class="log-row">
            <span class="time">[${ev.timestamp}]</span>
            <span class="source ${ev.category}">${ev.source}</span>
            <span class="msg">${ev.message}</span>
        </div>
    `).join("");
}

function updateFaultButtons(fault) {
    document.querySelectorAll(".btn-fault").forEach(b => b.classList.remove("active"));
    
    if (fault === "temp_spike") {
        document.getElementById("btn-fault-temp").classList.add("active");
        elFaultStatusBadge.className = "badge badge-critical";
        elFaultStatusBadge.textContent = "Active Fault: Facility Overheat";
    } else if (fault === "voltage_drop") {
        document.getElementById("btn-fault-voltage").classList.add("active");
        elFaultStatusBadge.className = "badge badge-critical";
        elFaultStatusBadge.textContent = "Active Fault: Grid Undervoltage";
    } else if (fault === "vibration_spike") {
        document.getElementById("btn-fault-vibration").classList.add("active");
        elFaultStatusBadge.className = "badge badge-critical";
        elFaultStatusBadge.textContent = "Active Fault: Bearing Wear";
    } else {
        elFaultStatusBadge.className = "badge badge-normal";
        elFaultStatusBadge.textContent = "Mode: Normal Operation";
    }
}

async function triggerFault(faultType) {
    try {
        await fetch("/api/fault", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ fault: faultType })
        });
        fetchSnapshot();
    } catch (err) {
        console.error("Fault trigger error:", err);
    }
}

// Start 1 Hz Polling Loop
window.addEventListener("DOMContentLoaded", () => {
    fetchSnapshot();
    setInterval(fetchSnapshot, 1000);
});
