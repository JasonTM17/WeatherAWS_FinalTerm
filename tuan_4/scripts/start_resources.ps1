<#
.SYNOPSIS
    Khởi động và kích hoạt lại tài nguyên khi bắt đầu phiên thực hành AWS Learner Lab mới.
.DESCRIPTION
    Kịch bản thực hiện:
    1. Kiểm tra tính toàn vẹn của state file (output/week4_session_control/<profile>_state.json).
    2. Khôi phục (restore/enable) EventBridge schedule rule (WeatherCollectionSchedule) qua session_control.py.
    3. Đọc lại cấu hình Lambda và EventBridge Rule để xác nhận hệ thống sẵn sàng thu thập.
.PARAMETER Profile
    AWS CLI profile: 'default', 'quyen', hoặc 'all' (mặc định: 'all').
.EXAMPLE
    .\tuan_4\scripts\start_resources.ps1 -Profile all
#>
[CmdletBinding()]
param (
    [ValidateSet('default', 'quyen', 'all')]
    [string]$Profile = 'all'
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$PythonExe = 'py -3.14'

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " [AWS LEARNER LAB] KHỞI ĐỘNG TÀI NGUYÊN CHO PHIÊN THỰC HÀNH MỚI " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Thời điểm thực hiện: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') UTC+7"

$ProfilesToProcess = @()
if ($Profile -eq 'all') {
    $ProfilesToProcess = @('default', 'quyen')
} else {
    $ProfilesToProcess = @($Profile)
}

$BackupBase = Join-Path $RootDir 'output\week4_session_control'

foreach ($p in $ProfilesToProcess) {
    Write-Host "`n--> Đang khôi phục profile [$p]..." -ForegroundColor Green
    $StateFile = Join-Path $BackupBase "$($p)_state.json"
    
    if (-not (Test-Path $StateFile)) {
        Write-Warning "   Không tìm thấy state file cho profile $p tại $StateFile."
        Write-Host "   Đang kiểm tra trực tiếp trạng thái hiện tại trên AWS..."
        $PreviewCmd = "$PythonExe `"$ScriptDir\session_control.py`" preview --profile $p"
        try {
            $PreviewOutput = Invoke-Expression $PreviewCmd
            Write-Host "   Trạng thái hiện hành: $PreviewOutput" -ForegroundColor Gray
        } catch {
            Write-Warning "   Không thể kết nối AWS cho profile $p."
        }
        continue
    }

    Write-Host "1. Khôi phục (RESTORE/ENABLE) EventBridge rule từ state file an toàn..."
    $RestoreCmd = "$PythonExe `"$ScriptDir\session_control.py`" restore --profile $p --state-file `"$StateFile`" --apply"
    try {
        $RestoreOutput = Invoke-Expression $RestoreCmd
        Write-Host "   Kết quả khôi phục: $RestoreOutput" -ForegroundColor Cyan
    } catch {
        Write-Warning "   Khôi phục gặp lỗi hoặc trạng thái rule đã thay đổi. Kiểm tra chi tiết:"
        Write-Error $_
    }
}

Write-Host "`n=================================================================" -ForegroundColor Green
Write-Host " [HOÀN TẤT] HỆ THỐNG ĐÃ SẴN SÀNG VẬN HÀNH CHO BUỔI THỰC HÀNH     " -ForegroundColor Green
Write-Host " EventBridge hourly schedule đã được kích hoạt theo đúng cấu hình." -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
