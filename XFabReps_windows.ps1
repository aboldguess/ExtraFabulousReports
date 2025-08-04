<#
.SYNOPSIS
    Launch ExtraFabulousReports on Windows.
.DESCRIPTION
    Starts the web server with optional port and production parameters.
    Use -Help to display usage information.
#>

param(
    [int]$Port = 5000,
    [switch]$Production,
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\XFabReps_windows.ps1 [-Port <number>] [-Production]" -ForegroundColor Yellow
    exit 0
}

$mode = if ($Production) { "production" } else { "development" }
Write-Host "Starting ExtraFabulousReports on port $Port in $mode mode"

if ($Production) {
    python app.py --port $Port --production
} else {
    python app.py --port $Port
}
