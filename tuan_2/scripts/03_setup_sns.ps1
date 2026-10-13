# Entry point for the Python SDK implementation.
param(
    [string]$Region = "us-east-1",
    [string]$Python = "python",
    [string]$AlertEmail
)
$ErrorActionPreference = "Stop"
$sdkScript = Join-Path $PSScriptRoot "aws_project.py"
$sdkArgs = @($sdkScript, "setup-sns", "--region", $Region)
if ($AlertEmail) { $sdkArgs += @("--email", $AlertEmail) }
& $Python @sdkArgs
if ($LASTEXITCODE -ne 0) { throw "Python SDK operation failed with exit code $LASTEXITCODE" }
