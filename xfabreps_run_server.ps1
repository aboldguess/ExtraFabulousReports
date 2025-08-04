<#
Start the ExtraFabulousReports server on Windows.

Usage:
  .\xfabreps_run_server.ps1 [-Port 8000] [-Prod] [-Host 0.0.0.0]

-Port : TCP port to listen on (default 5000)
-Prod : Use the production Waitress server if available
-Host : Interface to bind to (default 0.0.0.0)
#>
param(
    [int]$Port = 5000,
    [switch]$Prod,
    [string]$Host = "0.0.0.0"
)

$cmd = @("python", "app.py", "--host", $Host, "--port", $Port)
if ($Prod) { $cmd += "--prod" }
Write-Host "Starting ExtraFabulousReports with command: $($cmd -join ' ')"
& $cmd
