#!/usr/bin/env bash
# ==============================================================================
# Cloud Labs Web Portal - Root Launcher Shortcut
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT_DIR/portal/start.sh" "$@"
