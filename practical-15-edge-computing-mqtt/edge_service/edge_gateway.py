import json
import os
import random
import threading
import time
from collections import deque
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

MQTT_BROKER = os.environ.get("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))

class EdgeGateway:
    def __init__(self):
        self.lock = threading.Lock()
        self.active_fault = "none"
        self.total_readings = 0
        self.raw_bytes_generated = 0
        self.cloud_bytes_transmitted = 0
        self.edge_mitigations_triggered = 0
        
        self.latest_telemetry = {
            "datacenter": {"temp": 24.5, "humidity": 45.0, "fan_rpm": 2200, "status": "Normal"},
            "power": {"voltage": 230.2, "current": 14.8, "frequency": 50.02, "power_kw": 3.4, "breaker": "CLOSED"},
            "machinery": {"vibration": 1.8, "bearing_temp": 42.0, "rpm": 1450, "status": "Normal"},
            "edge_network": {"ingress_mbps": 85.0, "wan_uplink_mbps": 4.2, "cache_hit_rate": 95.1}
        }
        
        self.recent_events = deque(maxlen=200)
        self.recent_alerts = deque(maxlen=50)
        self.buffer_datacenter = []
        self.buffer_power = []
        self.last_cloud_sync = time.time()
        
        # Setup MQTT Client
        self.client = mqtt.Client(client_id="edge-gateway-daemon", protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.running = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.log_event("MQTT", "Broker connected on port 1883", "SYSTEM", "success")
            self.client.subscribe("edge/#")
            self.client.subscribe("cloud/#")
        else:
            self.log_event("MQTT", f"Connection failed with code {rc}", "SYSTEM", "error")

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode("utf-8"))
            # If control message
            if "edge/control" in topic:
                self.log_event(topic, f"Action: {payload.get('action')}", "CONTROL", "warning")
        except Exception:
            pass

    def log_event(self, source: str, message: str, category: str = "INFO", level: str = "info"):
        event = {
            "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "source": source,
            "message": message,
            "category": category,
            "level": level
        }
        with self.lock:
            self.recent_events.appendleft(event)

    def log_alert(self, subsystem: str, metric: str, value: float, threshold: float, action: str):
        alert = {
            "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "subsystem": subsystem,
            "metric": metric,
            "value": round(value, 2),
            "threshold": threshold,
            "edge_latency_ms": round(random.uniform(0.8, 1.8), 2),
            "action": action
        }
        with self.lock:
            self.recent_alerts.appendleft(alert)
            self.edge_mitigations_triggered += 1

    def set_fault(self, fault_type: str):
        with self.lock:
            self.active_fault = fault_type
            if fault_type == "none":
                self.latest_telemetry["power"]["breaker"] = "CLOSED"
        self.log_event("FaultInjector", f"Active fault mode set to: {fault_type.upper()}", "SIMULATOR", "warning")

    def run_telemetry_loop(self):
        while self.running:
            try:
                now = time.time()
                
                # 1. Generate Datacenter Environment Telemetry
                if self.active_fault == "temp_spike":
                    temp = round(random.uniform(84.0, 93.5), 1)
                    humidity = round(random.uniform(25.0, 32.0), 1)
                    fan_rpm = 4500
                    dc_status = "CRITICAL"
                else:
                    temp = round(random.uniform(22.0, 26.5), 1)
                    humidity = round(random.uniform(42.0, 48.0), 1)
                    fan_rpm = random.randint(2100, 2350)
                    dc_status = "Normal"

                # 2. Generate Power Substation Telemetry
                if self.active_fault == "voltage_drop":
                    voltage = round(random.uniform(188.0, 204.0), 1)
                    current = round(random.uniform(22.0, 28.5), 1)
                    freq = round(random.uniform(48.8, 49.3), 2)
                    breaker = "TRIPPED (SAFETY OVERRIDE)"
                else:
                    voltage = round(random.uniform(228.0, 232.5), 1)
                    current = round(random.uniform(13.5, 15.2), 1)
                    freq = round(random.uniform(49.98, 50.04), 2)
                    breaker = "CLOSED"

                # 3. Generate Machinery Vibration Telemetry
                if self.active_fault == "vibration_spike":
                    vibration = round(random.uniform(7.8, 9.4), 2)
                    bearing_temp = round(random.uniform(78.0, 86.0), 1)
                    machinery_status = "EXCESSIVE WEAR"
                else:
                    vibration = round(random.uniform(1.2, 2.2), 2)
                    bearing_temp = round(random.uniform(40.0, 44.0), 1)
                    machinery_status = "Normal"

                power_kw = round((voltage * current * 0.95) / 1000.0, 2)
                cache_hit = round(random.uniform(94.5, 96.8), 1)

                with self.lock:
                    self.latest_telemetry = {
                        "datacenter": {"temp": temp, "humidity": humidity, "fan_rpm": fan_rpm, "status": dc_status},
                        "power": {"voltage": voltage, "current": current, "frequency": freq, "power_kw": power_kw, "breaker": breaker},
                        "machinery": {"vibration": vibration, "bearing_temp": bearing_temp, "rpm": 1450 if breaker == "CLOSED" else 0, "status": machinery_status},
                        "edge_network": {"ingress_mbps": 95.0, "wan_uplink_mbps": 4.8, "cache_hit_rate": cache_hit}
                    }
                    self.total_readings += 4
                    self.buffer_datacenter.append(temp)
                    self.buffer_power.append(voltage)

                # Local Edge Intelligence: Fast-Path Rule Evaluation (< 2ms)
                if temp > 80.0:
                    self.log_alert("Datacenter", "Temperature", temp, 80.0, "HVAC Fan Boost to 4500 RPM")
                    self.publish_mqtt("edge/control/hvac", {"command": "BOOST", "fan_rpm": 4500, "source": "EdgeRuleEngine"})
                
                if voltage < 210.0 or voltage > 245.0:
                    self.log_alert("Power Grid", "Voltage", voltage, 210.0, "Automated Breaker Trip")
                    self.publish_mqtt("edge/control/breaker", {"command": "TRIP", "reason": "Undervoltage", "source": "EdgeRuleEngine"})

                if vibration > 7.0:
                    self.log_alert("Turbine Pump", "Vibration", vibration, 7.0, "Predictive Maintenance Alert")
                    self.publish_mqtt("edge/control/machinery", {"command": "THROTTLE_LUBE", "source": "EdgeRuleEngine"})

                # Publish High-Frequency Local Edge Telemetry
                dc_payload = json.dumps(self.latest_telemetry["datacenter"])
                power_payload = json.dumps(self.latest_telemetry["power"])
                self.publish_mqtt("edge/sensors/datacenter/temperature", dc_payload)
                self.publish_mqtt("edge/sensors/substation/power", power_payload)

                with self.lock:
                    self.raw_bytes_generated += len(dc_payload) + len(power_payload)

                # Periodic Edge-to-Cloud Aggregation (Every 10 seconds)
                # Instead of sending every 1Hz reading, send aggregated summary to save cloud WAN bandwidth
                if now - self.last_cloud_sync >= 10.0:
                    with self.lock:
                        avg_temp = round(sum(self.buffer_datacenter) / max(len(self.buffer_datacenter), 1), 2)
                        avg_volt = round(sum(self.buffer_power) / max(len(self.buffer_power), 1), 2)
                        sync_payload = json.dumps({
                            "batch_timestamp": int(now),
                            "datacenter_avg_temp": avg_temp,
                            "power_avg_voltage": avg_volt,
                            "active_fault": self.active_fault,
                            "samples_compressed": len(self.buffer_datacenter) + len(self.buffer_power)
                        })
                        self.cloud_bytes_transmitted += len(sync_payload)
                        self.buffer_datacenter.clear()
                        self.buffer_power.clear()
                        self.last_cloud_sync = now

                    self.publish_mqtt("cloud/telemetry/aggregate", sync_payload)
                    self.log_event("CloudSync", f"Aggregated telemetry batch transmitted to cloud ({len(sync_payload)} bytes)", "CLOUD", "success")

            except Exception as e:
                self.log_event("TelemetryLoop", f"Error: {str(e)}", "ERROR", "error")

            time.sleep(1.0)

    def publish_mqtt(self, topic: str, payload: any):
        try:
            str_payload = payload if isinstance(payload, str) else json.dumps(payload)
            self.client.publish(topic, str_payload, qos=0)
        except Exception:
            pass

    def start(self):
        self.running = True
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            self.log_event("MQTT", f"Broker connect pending: {e}", "SYSTEM", "warning")
            # Retry connection in thread
            threading.Thread(target=self._retry_connect, daemon=True).start()

        self.telemetry_thread = threading.Thread(target=self.run_telemetry_loop, daemon=True)
        self.telemetry_thread.start()

    def _retry_connect(self):
        while self.running:
            try:
                self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
                self.client.loop_start()
                break
            except Exception:
                time.sleep(2)

    def stop(self):
        self.running = False
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass

    def get_snapshot(self):
        with self.lock:
            # Calculate bandwidth savings
            raw = max(self.raw_bytes_generated, 1)
            cloud = self.cloud_bytes_transmitted
            saved_pct = round(max(0, (raw - cloud) / raw * 100), 1)

            return {
                "telemetry": self.latest_telemetry,
                "active_fault": self.active_fault,
                "stats": {
                    "total_readings": self.total_readings,
                    "raw_bytes_generated": self.raw_bytes_generated,
                    "cloud_bytes_transmitted": self.cloud_bytes_transmitted,
                    "bandwidth_saved_pct": saved_pct,
                    "edge_mitigations": self.edge_mitigations_triggered,
                    "local_edge_latency_ms": 1.2,
                    "simulated_cloud_wan_latency_ms": 125.0
                },
                "alerts": list(self.recent_alerts),
                "events": list(self.recent_events)
            }
