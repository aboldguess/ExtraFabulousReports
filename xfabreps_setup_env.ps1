<#
Setup a Python virtual environment for ExtraFabulousReports on Windows.
Run from a PowerShell prompt.
#>

Write-Host "Creating virtual environment..."
py -3 -m venv venv

Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host "Environment ready. Activate later with '.\\venv\\Scripts\\Activate.ps1'"
