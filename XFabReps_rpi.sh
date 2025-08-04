#!/usr/bin/env bash
# Launch ExtraFabulousReports on Raspberry Pi or other Linux systems.
# Supports optional port selection and production mode.

set -euo pipefail

PORT=5000
PRODUCTION=0

show_help() {
    echo "Usage: ./XFabReps_rpi.sh [-p PORT] [--production]"
    exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--port)
      PORT="$2"
      shift 2
      ;;
    --production)
      PRODUCTION=1
      shift
      ;;
    -h|--help)
      show_help
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      ;;
  esac
done

MODE="development"
if [[ $PRODUCTION -eq 1 ]]; then
  MODE="production"
fi

echo "Starting ExtraFabulousReports on port $PORT in $MODE mode"

if [[ $PRODUCTION -eq 1 ]]; then
  python3 app.py --port "$PORT" --production
else
  python3 app.py --port "$PORT"
fi
