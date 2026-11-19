const API = "/api";
const PROXY = "/proxy/";

let trafficRate = 0;
let trafficTimer = null;
let inFlight = 0;

const els = {
  activeInstances: document.getElementById("active-instances"),
  minMax: document.getElementById("min-max"),
  totalCapacity: document.getElementById("total-capacity"),
  incomingRpm: document.getElementById("incoming-rpm"),
  avgUtil: document.getElementById("avg-util"),
  scalingStatus: document.getElementById("scaling-status"),
  instances: document.getElementById("instances"),
  eventLog: document.getElementById("event-log"),
  rateSlider: document.getElementById("request-rate"),
  rateDisplay: document.getElementById("rate-display"),
  cfgMin: document.getElementById("cfg-min"),
  cfgMax: document.getElementById("cfg-max"),
};

function setRate(rps) {
  trafficRate = Math.max(0, Math.min(50, rps));
  els.rateSlider.value = trafficRate;
  els.rateDisplay.textContent = `${trafficRate} req/s`;
  restartTraffic();
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
  const batch = trafficRate >= 10 ? 2 : 1;
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

function appendLogLine(text) {
  const div = document.createElement("div");
  div.className = "line";
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

function renderInstances(list) {
  els.instances.innerHTML = "";
  if (!list.length) {
    els.instances.textContent = "No instances reported.";
    return;
  }
  for (const inst of list) {
    const card = document.createElement("article");
    card.className = "instance-card";
    const util = Number(inst.utilization_percent) || 0;
    const status = inst.status || "unknown";
    const badgeClass = status === "running" ? "running" : "other";
    card.innerHTML = `
      <h3>${escapeHtml(inst.container_name || inst.instance_name)}</h3>
      <dl>
        <dt>Container ID</dt><dd>${escapeHtml(inst.container_id || "—")}</dd>
        <dt>Requests (60s)</dt><dd>${inst.requests_last_60s ?? 0}</dd>
        <dt>Capacity</dt><dd>${inst.capacity ?? "—"}</dd>
        <dt>Utilization</dt><dd>${util}%</dd>
        <dt>Status</dt><dd><span class="badge ${badgeClass}">${escapeHtml(status)}</span></dd>
      </dl>
      <div class="util-bar"><div class="util-fill ${util >= 80 ? "high" : ""}" style="width:${Math.min(100, util)}%"></div></div>
    `;
    els.instances.appendChild(card);
  }
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
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
    els.activeInstances.textContent = status.active_instances;
    els.minMax.textContent = `${status.min_instances} / ${status.max_instances}`;
    els.totalCapacity.textContent = status.total_capacity;
    els.incomingRpm.textContent = status.incoming_rpm;
    els.avgUtil.textContent = `${status.average_utilization}%`;
    els.scalingStatus.textContent = status.scaling_status.replace(/_/g, " ");
    els.cfgMin.value = status.min_instances;
    els.cfgMax.value = status.max_instances;
    renderInstances(instances);
  } catch (_) {
  }
}

document.getElementById("btn-increase").addEventListener("click", () => {
  setRate(trafficRate + 5);
});

document.getElementById("btn-decrease").addEventListener("click", () => {
  setRate(trafficRate - 5);
});

document.getElementById("btn-stop").addEventListener("click", () => {
  setRate(0);
});

els.rateSlider.addEventListener("input", () => {
  setRate(Number(els.rateSlider.value));
});

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