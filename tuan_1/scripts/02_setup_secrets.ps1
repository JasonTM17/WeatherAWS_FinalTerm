# Entry point for the Python SDK implementation.
param(
    [string]$Region = "us-east-1",
    [string]$Python = "python"
)
$ErrorActionPreference = "Stop"
$sdkScript = Join-Path $PSScriptRoot "../../tuan_2/scripts/aws_project.py"
$sdkArgs = @($sdkScript, "setup-secrets", "--region", $Region)

& $Python @sdkArgs
if ($LASTEXITCODE -ne 0) { throw "Python SDK operation failed with exit code $LASTEXITCODE" }
