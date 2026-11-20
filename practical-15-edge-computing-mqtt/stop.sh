#!/usr/bin/env bash
# ==============================================================================
# Practical 15: Edge Computing: IoT Telemetry & Mosquitto MQTT Broker
# Unified Teardown Script
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PRAC_TITLE="Practical 15: Edge Computing: IoT Telemetry & Mosquitto MQTT Broker"

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
RESET="\033[0m"

echo -e "${BOLD}${CYAN}==========================================================================${RESET}"
echo -e "${BOLD} 🛑 Stopping $PRAC_TITLE${RESET}"
echo -e "${BOLD}${CYAN}==========================================================================${RESET}"

echo -e "${YELLOW}Tearing down Docker Compose services and networks...${RESET}"
docker compose down -v --remove-orphans

# Clean up dynamically spawned containers if applicable
docker rm -f app-3 app-4 app-5 2>/dev/null || true

echo -e "${BOLD}${GREEN}✅ $PRAC_TITLE stopped successfully. Port 8080 is released.${RESET}"
