#!/usr/bin/env bash
# ==============================================================================
# Practical 03: Docker Containerization & Cgroups Resource Isolation
# Unified Launcher Script
# ==============================================================================
set -euo pipefail

# Ensure script runs from its directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PRAC_NAME="practical-03-containerization-docker"
PRAC_TITLE="Practical 03: Docker Containerization & Cgroups Resource Isolation"
PORT="${HOST_PORT:-8080}"

# Colors for terminal output
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}${CYAN}==========================================================================${RESET}"
echo -e "${BOLD} 🚀 Starting $PRAC_TITLE${RESET}"
echo -e "${BOLD}${CYAN}==========================================================================${RESET}"

# 1. Verify Docker daemon is running
if ! docker info >/dev/null 2>&1; then
  echo -e "${RED}❌ Error: Docker daemon is not running.${RESET}"
  echo -e "   Please start Docker Desktop or the Docker daemon first."
  exit 1
fi

# 2. Check and stop any conflicting cloud-demos containers
echo -e "${BLUE}🔍 Checking for port $PORT conflicts and existing practicals...${RESET}"

for proj in $(docker compose ls -q 2>/dev/null || true); do
  if [[ "$proj" == practical-* || "$proj" == *autoscale* ]] && [[ "$proj" != "$PRAC_NAME" ]]; then
    echo -e "   ${YELLOW}Stopping previous active project: $proj...${RESET}"
    docker compose -p "$proj" down -v >/dev/null 2>&1 || true
  fi
done

# Clean up dynamically spawned containers if any
docker rm -f app-3 app-4 app-5 2>/dev/null || true

# Check if port 8080 is still occupied by any container
OCCUPYING=$(docker ps --filter "publish=$PORT" -q)
if [ -n "$OCCUPYING" ]; then
  OCC_NAME=$(docker ps --filter "publish=$PORT" --format '{{.Names}}' | tr '\n' ' ')
  echo -e "   ${YELLOW}Freeing port $PORT from container(s): $OCC_NAME...${RESET}"
  docker stop $OCCUPYING >/dev/null 2>&1 || true
fi

# 3. Ensure .env exists
if [ ! -f .env ] && [ -f .env.example ]; then
  echo -e "${BLUE}📄 Creating .env from .env.example...${RESET}"
  cp .env.example .env
fi

# 4. Build and start containers
echo -e "${BLUE}📦 Building and launching container stack...${RESET}"
docker compose up --build -d

# 5. Wait for readiness probe
echo -e "${BLUE}⏳ Probing health on http://localhost:$PORT...${RESET}"
READY=0
for i in {1..35}; do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" || true)
  if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
    READY=1
    break
  fi
  sleep 1
done

if [ "$READY" -eq 1 ]; then
  echo ""
  echo -e "${BOLD}${GREEN}==========================================================================${RESET}"
  echo -e "${BOLD}${GREEN} ✅ $PRAC_TITLE IS LIVE!${RESET}"
  echo -e "${BOLD}${GREEN}==========================================================================${RESET}"
  echo -e " 🌐 Dashboard URL : ${BOLD}${CYAN}http://localhost:$PORT${RESET}"
  echo -e " 📋 Live Logs     : ${YELLOW}docker compose logs -f${RESET}"
  echo -e " 🛑 Stop Demo     : ${YELLOW}./stop.sh${RESET}"
  echo -e "${BOLD}${GREEN}==========================================================================${RESET}"
  echo ""

  # Prompt to open in browser if interactive terminal on macOS
  if [[ "${OSTYPE:-}" == "darwin"* ]] && [ -t 0 ] && [ -t 1 ]; then
    read -t 5 -r -p "👉 Open dashboard in browser now? [y/N] " OPEN_BR || true
    if [[ "${OPEN_BR:-}" =~ ^[Yy]$ ]]; then
      open "http://localhost:$PORT"
    fi
  fi
else
  echo ""
  echo -e "${YELLOW}⚠️  Containers launched, but readiness probe timed out.${RESET}"
  echo -e "   Check container logs: ${CYAN}docker compose logs${RESET}"
  echo -e "   Dashboard URL: ${CYAN}http://localhost:$PORT${RESET}"
fi
