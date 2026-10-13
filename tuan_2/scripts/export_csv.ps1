# Export actual Athena CSVs or explicitly copy a saved snapshot.
param(
    [string]$Region = "us-east-1",
    [string]$Database = "weather_aqi_db",
    [string]$Bucket,
    [string]$OutputDir,
    [string]$Python = "python",
    [switch]$Offline
)
$ErrorActionPreference = "Stop"
$sdkArgs = @((Join-Path $PSScriptRoot "athena_export.py"), "--region", $Region, "--database", $Database)
if ($Bucket) { $sdkArgs += @("--bucket", $Bucket) }
if ($OutputDir) { $sdkArgs += @("--output", $OutputDir) }
if ($Offline) { $sdkArgs += "--offline" }
& $Python @sdkArgs
if ($LASTEXITCODE -ne 0) { throw "Data export failed with exit code $LASTEXITCODE" }
