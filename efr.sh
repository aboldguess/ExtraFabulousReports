#!/usr/bin/env bash
# efr.sh - Helper script to run ExtraFabulousReports on a Raspberry Pi.
# This script creates/activates a Python virtual environment, installs
# dependencies and starts the Flask server.

set -e  # Exit immediately on error.

PORT=5000       # Default port for the web server.
DEBUG=true      # Debug mode is enabled by default for development.

# ---------------------------------------------------------------------------
# Parse command-line arguments
#   -p or --port <port>: choose a custom port
#   -P or --prod:       run in production mode (disables debug)
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--port)
      PORT="$2"
      shift 2
      ;;
    -P|--prod)
      DEBUG=false
      shift
      ;;
    *)
      echo "Usage: $0 [-p PORT] [--prod]"
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Set up the virtual environment if it does not already exist. The venv
# directory is created once and reused on subsequent runs.
# ---------------------------------------------------------------------------
if [[ ! -d venv ]]; then
  python3 -m venv venv
fi

# Activate the virtual environment so that Python and pip use the isolated
# environment. shellcheck disable=SC1091 tells linting tools the source path is
# dynamic and should not raise an error.
# shellcheck source=/dev/null
source venv/bin/activate

# Install required dependencies inside the virtual environment. This is safe to
# run multiple times because pip skips packages that are already installed.
pip install -r requirements.txt

# ---------------------------------------------------------------------------
# Launch the Flask development server. In production mode we omit the --debug
# flag to disable the reloader and debugger.
# ---------------------------------------------------------------------------
if [[ "$DEBUG" == true ]]; then
  python -m flask --app app run --host 0.0.0.0 --port "$PORT" --debug
else
  python -m flask --app app run --host 0.0.0.0 --port "$PORT"
fi
