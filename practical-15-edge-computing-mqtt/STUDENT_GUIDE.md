# 🎓 Student Lab Guide: Practical 15 — Edge Computing & IoT Telemetry Broker (MQTT)

---

## 📌 1. What is this practical about? (The Real-World Problem)

Imagine an offshore oil rig or a modern manufacturing plant with 10,000 industrial sensors:
- Each sensor reports temperature, pressure, and vibration every 10 milliseconds.
- If you stream all raw data directly to a cloud data center over satellite or 4G:
  - **Bandwidth Cost:** Terabytes of redundant data sent over the WAN every day costing tens of thousands of dollars.
  - **Latency Danger:** If a turbine bearing begins overheating, sending the data to the cloud, waiting for a cloud function to compute, and sending a shutdown signal takes **~250 milliseconds**. In 250ms, the turbine can explode.

### The Cloud Solution: **Edge Computing & Fast-Path Rule Engines**
Deploy a small edge computer (like an IoT gateway running Eclipse Mosquitto MQTT and a lightweight rule engine) physically close to the machines:
1. **Sub-2ms Emergency Action:** The edge computer evaluates safety rules locally. If vibration spikes, it triggers an emergency shutdown instantly without waiting for the internet.
2. **WAN Bandwidth Compression:** It filters out 95% of normal, boring data, only uploading hourly summaries or anomalies to the central cloud.

---

## 🛠️ 2. Prerequisites
- Docker & Docker Compose installed.
- No hardware sensors needed (the project includes an automated industrial telemetry emulator).

---

## 🚀 3. Step-by-Step Lab Execution Plan

### Step 1: Open Terminal & Start the Lab
```bash
cd practical-15-edge-computing-mqtt
cp .env.example .env
docker compose up --build -d
```

### Step 2: Open the Interactive Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 4. Interactive Lab Exercises (Tasks to Perform)

### 🔹 Task 1: Observe Real-Time MQTT Telemetry Streams
1. Watch the top stat cards:
   - **MQTT Telemetry Rate:** ~10-20 messages/second arriving via WebSocket MQTT.
   - **WAN Bandwidth Compression:** Notice that **~94% to 96%** of bandwidth is saved at the edge!
2. Look at the live gauges for **Turbine Bearing Temperature (°C)**, **RPM Vibration (mm/s)**, and **Coolant Pressure (PSI)**.

### 🔹 Task 2: Inject an Industrial Fault (Emergency Decision)
1. In the **"Live Industrial Fault Injection Console"**, click **"🔥 Over-Temperature Spike (95°C)"**.
2. Observe the edge rule engine reaction:
   - **Local Edge Decision Time:** `< 2.0 ms`!
   - A critical alert is raised immediately, and the emergency coolant valve is tripped locally at the edge.
3. Compare this with the simulated **Cloud Round-Trip Latency (~240 ms)** displayed on screen. In a physical industrial setting, edge decision speed prevents catastrophic machine failure.

### 🔹 Task 3: Compare Edge Filtering vs. Raw Cloud Upload
1. Toggle the **"Edge Filtering Engine"** switch to **OFF (Stream 100% Raw Data)**:
   - Watch the WAN egress meter surge from ~2 KB/s up to ~50 KB/s.
2. Toggle it back to **ON (Smart Edge Aggregation)**:
   - Notice how only compressed mathematical rollups (min, max, avg) are sent over the WAN, proving the economic power of edge computing.

---

## 💻 5. Terminal CLI Verification

You can subscribe to live MQTT topics using the terminal (if `mosquitto_sub` or `curl` is available):

```bash
# 1. Fetch current edge broker health and metrics
curl -s http://localhost:8080/api/edge/metrics | python3 -m json.tool

# 2. Trigger an edge fault simulation via API
curl -s -X POST http://localhost:8080/api/edge/fault \
  -H "Content-Type: application/json" \
  -d '{"fault_type": "vibration_spike", "sensor_id": "turbine-01"}'
```

---

## 🧠 6. Viva & Interview Questions

1. **Why is MQTT preferred over HTTP for IoT and Edge computing?**
   - MQTT is an ultra-lightweight publish/subscribe protocol with tiny 2-byte header overhead (compared to hundreds of bytes in HTTP headers), persistent keep-alives, and built-in Quality of Service (QoS) levels.
2. **What is the difference between Fog Computing and Edge Computing?**
   - *Edge Computing:* Processing happening directly on or right beside the physical sensor/device (e.g. smart camera, router, microcontroller).
   - *Fog Computing:* An intermediary layer of servers (e.g. localized micro-datacenter in a factory) between the edge and the centralized cloud.
3. **What is "Store and Forward" in edge IoT gateways?**
   - If internet connectivity to the central cloud drops, the edge gateway stores telemetry locally in a database or disk queue, and automatically forwards it once WAN connection is restored, ensuring zero data loss.

---

## 🧹 7. Teardown / Reclaiming Memory
```bash
docker compose down
```
