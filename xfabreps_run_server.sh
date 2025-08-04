#!/usr/bin/env bash
# Start the ExtraFabulousReports server on Linux/Raspberry Pi.
#
# Usage:
#   ./xfabreps_run_server.sh [--port PORT] [--prod] [other-flask-args]
#
# --port PORT  : TCP port to listen on (default: 5000)
# --prod       : Use the production Waitress server if installed
# Any additional arguments are forwarded to the underlying Python app,
# allowing advanced users to specify options like --host.

set -euo pipefail

PORT=5000          # Default port if --port is not provided
USE_PROD=0         # Whether to run the production server
EXTRA_ARGS=()      # Collect any other arguments

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      PORT="$2"
      shift 2
      ;;
    --prod)
      USE_PROD=1
      shift
      ;;
    *)
      EXTRA_ARGS+=("$1")
      shift
      ;;
  esac
done

# Build the Python command dynamically
CMD=(python app.py --port "$PORT")
if [[ "$USE_PROD" -eq 1 ]]; then
  CMD+=("--prod")
fi
CMD+=("${EXTRA_ARGS[@]}")

# Echo the command for debugging so users can see what is executed
printf 'Starting ExtraFabulousReports with command: %s\n' "${CMD[*]}"
"${CMD[@]}"
