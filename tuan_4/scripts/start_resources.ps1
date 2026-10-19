<# Preview or restore one schedule from the exact private state of its previous pause. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidateSet('default','quyen')][string]$Profile,
    [Parameter(Mandatory=$true)][string]$StateFile,
    [string]$Python = 'python',
    [switch]$Apply
)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not [IO.Path]::IsPathRooted($StateFile)) {
    $StateFile = Join-Path $ProjectRoot $StateFile
}
$CommandArguments = @((Join-Path $PSScriptRoot 'session_control.py'), 'restore', '--profile', $Profile, '--state-file', $StateFile)
if ($Apply) { $CommandArguments += '--apply' }
& $Python @CommandArguments
exit $LASTEXITCODE
