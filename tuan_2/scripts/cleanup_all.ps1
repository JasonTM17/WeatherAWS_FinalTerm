# Entry point for the Python SDK implementation.
param(
    [string]$Region = "us-east-1",
    [string]$Python = "python",
    [Parameter(Mandatory=$true)][string]$ConfirmAccount,
    [switch]$DeleteData
)
$ErrorActionPreference = "Stop"
$sdkScript = Join-Path $PSScriptRoot "aws_project.py"
$sdkArgs = @($sdkScript, "cleanup", "--region", $Region)
$sdkArgs += @("--confirm-account", $ConfirmAccount)
if ($DeleteData) { $sdkArgs += "--delete-data" }
& $Python @sdkArgs
if ($LASTEXITCODE -ne 0) { throw "Python SDK operation failed with exit code $LASTEXITCODE" }
