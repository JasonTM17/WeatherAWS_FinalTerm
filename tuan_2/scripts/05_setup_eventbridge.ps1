# Entry point for the Python SDK implementation.
param(
    [string]$Region = "us-east-1",
    [string]$Python = "python",
    [string]$ScheduleRate = "rate(1 hour)"
)
$ErrorActionPreference = "Stop"
$sdkScript = Join-Path $PSScriptRoot "aws_project.py"
$sdkArgs = @($sdkScript, "setup-eventbridge", "--region", $Region)
$sdkArgs += @("--rate", $ScheduleRate)
& $Python @sdkArgs
if ($LASTEXITCODE -ne 0) { throw "Python SDK operation failed with exit code $LASTEXITCODE" }
