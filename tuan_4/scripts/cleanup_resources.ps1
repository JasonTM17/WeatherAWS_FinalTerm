<# Preview or pause one canonical collection schedule through the Python SDK.
Default is preview. Keep the printed state-file path for the next session.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidateSet('default','quyen')][string]$Profile,
    [string]$StateFile,
    [string]$Python = 'python',
    [switch]$Apply
)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not $StateFile) {
    $StateFile = Join-Path $ProjectRoot ('output/week4_session_control/' + $Profile + '_' + [guid]::NewGuid().ToString('N') + '.json')
} elseif (-not [IO.Path]::IsPathRooted($StateFile)) {
    $StateFile = Join-Path $ProjectRoot $StateFile
}
$CommandArguments = @((Join-Path $PSScriptRoot 'session_control.py'), 'pause', '--profile', $Profile, '--state-file', $StateFile)
if ($Apply) { $CommandArguments += '--apply' }
Write-Host ('State file: ' + $StateFile)
& $Python @CommandArguments
exit $LASTEXITCODE
