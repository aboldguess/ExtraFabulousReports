#!/usr/bin/env bash
# Set up a Python virtual environment and install dependencies for ExtraFabulousReports.

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
printf "Environment ready. Activate with 'source venv/bin/activate'\n"
