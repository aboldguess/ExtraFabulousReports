#!/usr/bin/env bash
# Convenience script to launch the ExtraFabulousReports server with network access.
# Additional arguments such as --port or --prod are forwarded to the Flask CLI.

python -m flask --app app.py run-server "$@"
