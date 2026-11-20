const API = "/api";
const PROXY = "/proxy/";

let trafficRate = 0;
let trafficTimer = null;
let inFlight = 0;
const VM_MONTHLY_COST = 36.0;
const STATIC_VM_COUNT = 5;
const STATIC_MONTHLY_COST = STATIC_VM_COUNT * VM_MONTHLY_COST; // $180.00

const els = {
  activeInstances: document.getElementById("active-instances"),
  minMaxSub: document.getElementById("min-max-sub"),
  avgUtil: document.getElementById("avg-util"),
  utilSub: document.getElementById("util-sub"),
  utilMeter: document.getElementById("util-meter"),
  incomingRpm: document.getElementById("incoming-rpm"),
  totalCapacityCaption: document.getElementById("total-capacity-caption"),
  scalingStatus: document.getElementById("scaling-status"),
  cooldownCaption: document.getElementById("cooldown-caption"),
  costSavedPct: document.getElementById("cost-saved-pct"),
  costSavedDollars: document.getElementById("cost-saved-dollars"),
  instances: document.getElementById("instances"),
  fleetCountTag: document.getElementById("fleet-count-tag"),
  eventLog: document.getElementById("event-log"),
  rateSlider: document.getElementById("request-rate"),
  rateDisplay: document.getElementById("rate-display"),
  cfgMin: document.getElementById("cfg-min"),
  cfgMax: document.getElementById("cfg-max"),
  calcInstances: document.getElementById("calc-instances"),
  calcDynamicCost: document.getElementById("calc-dynamic-cost"),
  calcSavingsText: document.getElementById("calc-savings-text"),
  costProgressBar: document.getElementById("cost-progress-bar"),
  mathCurrent: document.getElementById("math-current"),
  mathUtil: document.getElementById("math-util"),
  mathDesired: document.getElementById("math-desired"),
  verdictText: document.getElementById("verdict-text"),
  guardStatusBadge: document.getElementById("guard-status-badge"),
  cooldownMeterBar: document.getElementById("cooldown-meter-bar"),
};

function setRate(rps) {
  trafficRate = Math.max(0, Math.min(50, rps));
  els.rateSlider.value = trafficRate;
  els.rateDisplay.textContent = `${trafficRate} req/s`;
  restartTraffic();
  updateStepHighlight();
}

function restartTraffic() {
  if (trafficTimer) {
    clearInterval(trafficTimer);
    trafficTimer = null;
  }
  if (trafficRate <= 0) return;
  const intervalMs = Math.max(20, Math.floor(1000 / trafficRate));
  trafficTimer = setInterval(sendBurst, intervalMs);
}

function sendBurst() {
  const batch = trafficRate >= 20 ? 3 : (trafficRate >= 10 ? 2 : 1);
  for (let i = 0; i < batch; i++) {
    if (inFlight > 200) return;
    inFlight += 1;
    fetch(PROXY, { cache: "no-store" })
      .catch(() => null)
      .finally(() => {
        inFlight -= 1;
      });
  }
}

function updateStepHighlight() {
  const steps = [1, 2, 3, 4];
  steps.forEach(s => {
    const el = document.getElementById(`step-card-${s}`);
    if (el) el.classList.remove("active");
  });

  if (trafficRate >= 25) {
    const el = document.getElementById("step-card-2");
    if (el) el.classList.add("active");
  } else if (trafficRate === 0) {
    const el = document.getElementById("step-card-4");
    if (el) el.classList.add("active");
  } else {
    const el = document.getElementById("step-card-1");
    if (el) el.classList.add("active");
  }
}

function appendLogLine(text) {
  const div = document.createElement("div");
  div.className = "line";
  
  if (text.includes("HIGH LOAD DETECTED") || text.includes("Creating new instance")) {
    div.classList.add("log-surge");
  } else if (text.includes("Scaled out successfully")) {
    div.classList.add("log-scaleout");
  } else if (text.includes("Scaled in successfully") || text.includes("Terminating scaled instance")) {
    div.classList.add("log-scalein");
  } else if (text.includes("error") || text.includes("failed")) {
    div.classList.add("log-error");
  }
  
  div.textContent = text;
  els.eventLog.appendChild(div);
  while (els.eventLog.children.length > 300) {
    els.eventLog.removeChild(els.eventLog.firstChild);
  }
  els.eventLog.scrollTop = els.eventLog.scrollHeight;
}

function connectEvents() {
  const source = new EventSource(`${API}/events`);
  source.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data);
      if (data.message) appendLogLine(data.message);
    } catch (_) {
      appendLogLine(ev.data);
    }
  };
  source.onerror = () => {
    source.close();
    setTimeout(connectEvents, 3000);
  };
}

function renderInstances(list, minInstances) {
  els.instances.innerHTML = "";
  if (!list.length) {
    els.instances.innerHTML = "<p style='color: var(--text-muted);'>No instances reported.</p>";
    return;
  }
  
  list.forEach((inst, index) => {
    const card = document.createElement("article");
    card.className = "instance-card";
    const util = Number(inst.utilization_percent) || 0;
    const isBase = index < minInstances;
    const badgeText = isBase ? "Base Replica" : "Autoscaled Worker";
    const badgeClass = isBase ? "base" : "scaled";
    
    let meterColor = "var(--accent)";
    if (util >= 80) meterColor = "var(--danger)";
    else if (util >= 60) meterColor = "var(--warn)";

    card.innerHTML = `
      <div class="inst-header">
        <span class="inst-name">${escapeHtml(inst.container_name || inst.instance_name)}</span>
        <span class="inst-badge ${badgeClass}">${badgeText}</span>
      </div>
      <dl class="inst-details">
        <dt>Container ID</dt><dd>${escapeHtml(inst.container_id || "—")}</dd>
        <dt>Upstream Host</dt><dd>${escapeHtml(inst.container_name || inst.instance_name)}:5000</dd>
        <dt>Requests (60s)</dt><dd>${inst.requests_last_60s ?? 0} / ${inst.capacity ?? 20}</dd>
        <dt>Health Status</dt><dd><span class="text-success">● 200 OK</span></dd>
      </dl>
      <div class="inst-meter-row">
        <div class="inst-meter-label">
          <span>Utilization</span>
          <strong>${util}%</strong>
        </div>
        <div class="meter-bar">
          <div class="meter-fill" style="width: ${Math.min(100, util)}%; background-color: ${meterColor};"></div>
        </div>
      </div>
    `;
    els.instances.appendChild(card);
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function updateFormulaAndVerdict(status) {
  const current = status.active_instances || 2;
  const util = status.average_utilization || 0;
  const targetUtil = 70.0;
  const minInst = status.min_instances || 2;
  const maxInst = status.max_instances || 5;

  let desired = Math.ceil(current * (util / targetUtil));
  if (desired < minInst) desired = minInst;
  if (desired > maxInst) desired = maxInst;

  els.mathCurrent.textContent = current;
  els.mathUtil.textContent = `${util}%`;
  els.mathDesired.textContent = desired;

  const cdRem = status.cooldown_remaining || 0;
  if (cdRem > 0) {
    els.verdictText.textContent = `Decision: Cooldown Active (${cdRem}s remaining). Flapping protection engaged.`;
    const step3 = document.getElementById("step-card-3");
    if (step3) step3.classList.add("active");
  } else if (util > status.scale_out_threshold) {
    els.verdictText.textContent = `Decision: HIGH LOAD (${util}% > ${status.scale_out_threshold}%). Triggering Horizontal Scale-Out.`;
  } else if (util < status.scale_in_threshold && current > minInst) {
    els.verdictText.textContent = `Decision: LOW LOAD (${util}% < ${status.scale_in_threshold}%). Eligible for graceful Scale-In.`;
  } else {
    els.verdictText.textContent = "Decision: Fleet capacity is optimal. Load comfortably handled.";
  }
}

function updateEconomics(activeCount) {
  const count = Math.max(1, activeCount || 2);
  const dynamicCost = count * VM_MONTHLY_COST;
  const savings = Math.max(0, STATIC_MONTHLY_COST - dynamicCost);
  const savingsPct = Math.round((savings / STATIC_MONTHLY_COST) * 100);

  els.calcInstances.textContent = count;
  els.calcDynamicCost.textContent = `$${dynamicCost.toFixed(2)} / mo`;
  els.calcSavingsText.textContent = `$${savings.toFixed(2)}/mo (${savingsPct}% saved)`;
  els.costSavedPct.textContent = `${savingsPct}%`;
  els.costSavedDollars.textContent = `-$${savings.toFixed(0)} / mo`;

  const dynamicPct = (dynamicCost / STATIC_MONTHLY_COST) * 100;
  els.costProgressBar.style.width = `${Math.min(100, dynamicPct)}%`;
}

function updateCooldownUI(cdRemaining, maxCooldown) {
  if (cdRemaining > 0) {
    els.guardStatusBadge.textContent = `Cooldown Active (${cdRemaining}s)`;
    els.guardStatusBadge.style.color = "var(--warn)";
    els.cooldownCaption.textContent = `Cooldown: Active (${cdRemaining}s)`;
    const pct = (cdRemaining / (maxCooldown || 10)) * 100;
    els.cooldownMeterBar.style.width = `${pct}%`;
  } else {
    els.guardStatusBadge.textContent = "Ready (Cooldown Inactive)";
    els.guardStatusBadge.style.color = "var(--success)";
    els.cooldownCaption.textContent = "Cooldown: Inactive (Ready)";
    els.cooldownMeterBar.style.width = "0%";
  }
}

async function refresh() {
  try {
    const [statusRes, instRes] = await Promise.all([
      fetch(`${API}/status`),
      fetch(`${API}/instances`),
    ]);
    if (!statusRes.ok || !instRes.ok) return;
    const status = await statusRes.json();
    const { instances } = await instRes.json();

    const activeCount = status.active_instances || instances.length;
    els.activeInstances.textContent = activeCount;
    els.minMaxSub.textContent = `min ${status.min_instances} / max ${status.max_instances}`;
    els.totalCapacityCaption.textContent = `Total Capacity: ${status.total_capacity || (activeCount * 20)} req/min`;
    els.incomingRpm.textContent = status.incoming_rpm || 0;
    
    const util = Number(status.average_utilization) || 0;
    els.avgUtil.textContent = `${util}%`;
    els.utilMeter.style.width = `${Math.min(100, util)}%`;
    if (util >= 80) {
      els.utilMeter.className = "meter-fill danger";
    } else if (util >= 60) {
      els.utilMeter.className = "meter-fill warning";
    } else {
      els.utilMeter.className = "meter-fill";
    }

    const stateKey = (status.scaling_status || "steady").toLowerCase();
    els.scalingStatus.textContent = stateKey.replace(/_/g, " ");
    els.scalingStatus.className = `status-pill ${stateKey}`;

    els.cfgMin.value = status.min_instances;
    els.cfgMax.value = status.max_instances;
    els.fleetCountTag.textContent = `${activeCount} Containers Online`;

    updateCooldownUI(status.cooldown_remaining || 0, status.scaling_cooldown || 10);
    updateFormulaAndVerdict(status);
    updateEconomics(activeCount);
    renderInstances(instances, status.min_instances || 2);
  } catch (_) {
  }
}

// Preset Handlers
document.getElementById("preset-flash").addEventListener("click", () => setRate(30));
document.getElementById("preset-rush").addEventListener("click", () => setRate(12));
document.getElementById("preset-baseline").addEventListener("click", () => setRate(4));
document.getElementById("preset-midnight").addEventListener("click", () => setRate(0));

// Manual Slider & Buttons
document.getElementById("btn-increase").addEventListener("click", () => setRate(trafficRate + 5));
document.getElementById("btn-decrease").addEventListener("click", () => setRate(trafficRate - 5));
document.getElementById("btn-stop").addEventListener("click", () => setRate(0));
els.rateSlider.addEventListener("input", () => setRate(Number(els.rateSlider.value)));

// Clear Log
document.getElementById("btn-clear-log").addEventListener("click", () => {
  els.eventLog.innerHTML = "";
});

// Config Apply
document.getElementById("btn-apply-config").addEventListener("click", async () => {
  const min = Number(els.cfgMin.value);
  const max = Number(els.cfgMax.value);
  try {
    await fetch(`${API}/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ min_instances: min, max_instances: max }),
    });
    await refresh();
  } catch (_) {
  }
});

connectEvents();
refresh();
setInterval(refresh, 2000);
