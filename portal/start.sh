#!/usr/bin/env bash
# ==============================================================================
# Cloud Labs Web Portal - Startup Script
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-3000}"

BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
RESET="\033[0m"

echo -e "${BOLD}${CYAN}==========================================================================${RESET}"
echo -e "${BOLD} 🚀 Launching Cloud Systems Engineering Web Portal${RESET}"
echo -e "${BOLD}${CYAN}==========================================================================${RESET}"

# Verify Python 3
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Error: python3 is required to run the web portal."
  exit 1
fi

echo -e " 🌐 Portal URL  : ${BOLD}${GREEN}http://localhost:$PORT${RESET}"
echo -e " ⚡ Labs Engine : ${CYAN}http://localhost:8080${RESET}"
echo -e " 🛑 Stop Server : ${YELLOW}Ctrl+C${RESET}"
echo -e "${BOLD}${CYAN}==========================================================================${RESET}"

# Attempt to open browser on macOS
if [[ "${OSTYPE:-}" == "darwin"* ]] && [ -t 1 ]; then
  (sleep 1 && open "http://localhost:$PORT") &
fi

exec python3 "$SCRIPT_DIR/server.py"
