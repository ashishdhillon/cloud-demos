#!/usr/bin/env bash
# ==============================================================================
# Cloud Systems Engineering Labs - Interactive Master Launcher & Switcher
# Compatible with Bash 3.2+ (macOS default), Bash 4+, and Linux/WSL.
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Colors for terminal styling
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
MAGENTA="\033[0;35m"
DIM="\033[2m"
RESET="\033[0m"

# Indexed arrays (compatible with Bash 3.2 on macOS)
LAB_DIRS=()
LAB_TITLES=()

LAB_DIRS[1]="practical-01-service-models";          LAB_TITLES[1]="NIST Cloud Service Models (IaaS / PaaS / SaaS)"
LAB_DIRS[2]="practical-02-vm-lifecycle";            LAB_TITLES[2]="Virtual Machine Lifecycle & Hypervisor Provisioning"
LAB_DIRS[3]="practical-03-containerization-docker";  LAB_TITLES[3]="Docker Containerization & Cgroups Resource Isolation"
LAB_DIRS[4]="practical-04-k8s-orchestration";        LAB_TITLES[4]="Kubernetes Pod Orchestration & Self-Healing Control Plane"
LAB_DIRS[5]="practical-05-cloud-networking-vpc";    LAB_TITLES[5]="Cloud Networking: Dual-Tier VPC, Routing & SGs"
LAB_DIRS[6]="practical-06-object-storage-s3";        LAB_TITLES[6]="Cloud Object Storage: S3 API Mock & Presigned URLs"
LAB_DIRS[7]="practical-07-iam-access-control";      LAB_TITLES[7]="Cloud Identity & Access Management (IAM & RBAC)"
LAB_DIRS[8]="practical-08-cloud-security";          LAB_TITLES[8]="Cloud Security: WAF, DDoS Mitigation & KMS Encryption"
LAB_DIRS[9]="practical-09-openstack-private-cloud";  LAB_TITLES[9]="OpenStack Private Cloud Architecture & Resource Quotas"
LAB_DIRS[10]="practical-10-cloud-autoscaling";      LAB_TITLES[10]="Horizontal Pod & Container Auto-Scaling Engine"
LAB_DIRS[11]="practical-11-cloud-migration";        LAB_TITLES[11]="Cloud Data Migration: 6-Rs Strategy & Cryptographic Parity"
LAB_DIRS[12]="practical-12-serverless-lambda";      LAB_TITLES[12]="Serverless Computing: FaaS Cold Starts & Micro-Billing"
LAB_DIRS[13]="practical-13-bigdata-analytics";      LAB_TITLES[13]="Cloud Big Data Analytics: MapReduce vs Vectorized"
LAB_DIRS[14]="practical-14-multicloud-terraform";   LAB_TITLES[14]="Multi-Cloud Infrastructure as Code (Terraform Engine)"
LAB_DIRS[15]="practical-15-edge-computing-mqtt";    LAB_TITLES[15]="Edge Computing: IoT Telemetry & Mosquitto Broker"

get_active_project() {
  local running_projects
  running_projects=$(docker compose ls --format json 2>/dev/null | grep -o '"Name":"practical-[^"]*"' | cut -d'"' -f4 || true)
  if [ -z "$running_projects" ]; then
    running_projects=$(docker compose ls --format json 2>/dev/null | grep -o '"Name":"[^"]*autoscale[^"]*"' | cut -d'"' -f4 || true)
  fi
  echo "$running_projects"
}

stop_all() {
  echo -e "${BOLD}${CYAN}==========================================================================${RESET}"
  echo -e "${BOLD} 🛑 Stopping All Active Cloud Labs${RESET}"
  echo -e "${BOLD}${CYAN}==========================================================================${RESET}"

  local count=0
  for proj in $(docker compose ls -q 2>/dev/null || true); do
    if [[ "$proj" == practical-* || "$proj" == *autoscale* ]]; then
      echo -e "${YELLOW}   Tearing down project: $proj...${RESET}"
      docker compose -p "$proj" down -v >/dev/null 2>&1 || true
      count=$((count + 1))
    fi
  done

  # Clean up dynamic containers
  docker rm -f app-3 app-4 app-5 2>/dev/null || true

  # Free any process on port 8080
  local port_holders
  port_holders=$(docker ps --filter "publish=8080" -q)
  if [ -n "$port_holders" ]; then
    echo -e "${YELLOW}   Stopping remaining container(s) on port 8080...${RESET}"
    docker stop $port_holders >/dev/null 2>&1 || true
    count=$((count + 1))
  fi

  if [ "$count" -gt 0 ]; then
    echo -e "${BOLD}${GREEN}✅ All practical projects stopped. Port 8080 is free.${RESET}"
  else
    echo -e "${GREEN}No active practicals were running. Port 8080 is already free.${RESET}"
  fi
  echo ""
}

show_status() {
  local active
  active=$(get_active_project)
  echo -e "${BOLD}${CYAN}==========================================================================${RESET}"
  echo -e "${BOLD} 📊 Cloud Labs Status${RESET}"
  echo -e "${BOLD}${CYAN}==========================================================================${RESET}"
  if [ -n "$active" ]; then
    echo -e " Active Practical Stack : ${BOLD}${GREEN}$active${RESET}"
    echo -e " URL                     : ${BOLD}${CYAN}http://localhost:8080${RESET}"
    echo -e " Containers              :"
    docker ps --filter "name=practical" --filter "name=autoscale" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
  else
    echo -e " ${YELLOW}No practical lab is currently running.${RESET}"
    echo -e " Port 8080 is ${GREEN}free and ready${RESET} for any lab."
  fi
  echo -e "${BOLD}${CYAN}==========================================================================${RESET}"
  echo ""
}

launch_lab() {
  local num="$1"
  # Strip leading zero if present for index calculation
  local idx=$((10#$num))
  local dir="${LAB_DIRS[$idx]:-}"
  local title="${LAB_TITLES[$idx]:-}"

  if [ -z "$dir" ] || [ ! -d "$ROOT_DIR/$dir" ]; then
    echo -e "${RED}❌ Error: Practical $num not found.${RESET}"
    exit 1
  fi

  echo -e "${BOLD}${GREEN}▶ Launching Practical $num: $title...${RESET}"
  "$ROOT_DIR/$dir/start.sh"
}

print_menu() {
  local active
  active=$(get_active_project)

  echo -e "${BOLD}${CYAN}==========================================================================${RESET}"
  echo -e "${BOLD}       🌐 CLOUD SYSTEMS ENGINEERING LABS & INTERACTIVE DEMOS             ${RESET}"
  echo -e "${BOLD}${CYAN}==========================================================================${RESET}"

  for i in $(seq 1 15); do
    local d="${LAB_DIRS[$i]}"
    local t="${LAB_TITLES[$i]}"
    local pad=""
    if [ "$i" -lt 10 ]; then pad=" "; fi

    local badge=""
    if [[ "$active" == *"$d"* ]] || ([[ "$d" == *"autoscaling"* ]] && [[ "$active" == *"autoscale"* ]]); then
      badge=" ${BOLD}${GREEN}🟢 [ACTIVE on :8080]${RESET}"
    fi

    echo -e "  ${BOLD}${CYAN}[$pad$i]${RESET} Practical $(printf "%02d" $i) - $t$badge"
  done

  echo -e "${DIM}--------------------------------------------------------------------------${RESET}"
  echo -e "  ${BOLD}${YELLOW}[ 0]${RESET} Stop All Running Practicals (Free Port 8080)"
  echo -e "  ${BOLD}${BLUE}[ s]${RESET} Check Status & Container Metrics"
  echo -e "  ${BOLD}${RED}[ q]${RESET} Quit"
  echo -e "${BOLD}${CYAN}==========================================================================${RESET}"
}

# --- CLI Argument Handling ---
if [ $# -gt 0 ]; then
  case "$1" in
    stop|down|0)
      stop_all
      exit 0
      ;;
    status|ps)
      show_status
      exit 0
      ;;
    help|-h|--help)
      echo "Usage: ./run.sh [1-15 | stop | status | help]"
      echo "  ./run.sh        - Open interactive lab launcher"
      echo "  ./run.sh 4      - Launch Practical 04 directly"
      echo "  ./run.sh 10     - Launch Practical 10 directly"
      echo "  ./run.sh stop   - Stop any currently running practical"
      echo "  ./run.sh status - View running lab and containers"
      exit 0
      ;;
    [1-9]|1[0-5]|0[1-9])
      launch_lab "$1"
      exit 0
      ;;
    *)
      echo -e "${RED}Invalid command: $1${RESET}"
      echo "Run './run.sh help' for usage instructions."
      exit 1
      ;;
  esac
fi

# --- Interactive Menu Loop ---
while true; do
  print_menu
  read -r -p "Select a practical to launch [0-15, s, q]: " CHOICE || true
  echo ""

  case "$CHOICE" in
    q|Q|exit)
      echo -e "${GREEN}Goodbye!${RESET}"
      exit 0
      ;;
    s|S|status)
      show_status
      ;;
    0|stop)
      stop_all
      ;;
    [1-9]|1[0-5]|0[1-9])
      launch_lab "$CHOICE"
      echo ""
      read -r -p "Press Enter to return to main menu or 'q' to exit: " POST_CHOICE || true
      if [[ "$POST_CHOICE" =~ ^[Qq]$ ]]; then
        exit 0
      fi
      ;;
    *)
      echo -e "${RED}Invalid selection. Please enter a number between 1 and 15, '0' to stop, or 'q' to quit.${RESET}"
      sleep 1
      ;;
  esac
done
