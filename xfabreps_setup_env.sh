#!/usr/bin/env bash
# Prepare a Python virtual environment for ExtraFabulousReports on Linux/Raspberry Pi.
#
# This script creates a "venv" directory, activates it and installs all
# required dependencies. Run it once during initial setup.

set -euo pipefail

python3 -m venv venv                          # Create the virtual environment
source venv/bin/activate                      # Activate the environment
pip install -r requirements.txt               # Install dependencies
printf "Environment ready. Activate with 'source venv/bin/activate'\n"
