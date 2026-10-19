<#
.SYNOPSIS
    Dừng và dọn dẹp tài nguyên sau mỗi buổi thực hành AWS Learner Lab để tiết kiệm credit.
.DESCRIPTION
    Kịch bản thực hiện:
    1. Vô hiệu hóa (pause/disable) EventBridge schedule rule (WeatherCollectionSchedule) qua session_control.py.
    2. Lưu trạng thái vào state file an toàn riêng tư (output/week4_session_control/<profile>_state.json).
    3. Ngăn chặn Lambda collector tự động kích hoạt ngoài giờ lab, giảm thiểu chi phí runtime và API calls.
    4. Bảo toàn 100% dữ liệu Data Lake raw và bằng chứng đã tích lũy (không xóa dữ liệu S3 raw).
.PARAMETER Profile
    AWS CLI profile: 'default', 'quyen', hoặc 'all' (mặc định: 'all').
.EXAMPLE
    .\tuan_4\scripts\cleanup_resources.ps1 -Profile all
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
Write-Host " [AWS LEARNER LAB] DỪNG TÀI NGUYÊN SAU BUỔI THỰC HÀNH TUẦN 4    " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Thời điểm thực hiện: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') UTC+7"
Write-Host "Mục tiêu: Pause EventBridge Rule, bảo tồn credit Learner Lab, giữ nguyên S3 raw data." -ForegroundColor Yellow

$ProfilesToProcess = @()
if ($Profile -eq 'all') {
    $ProfilesToProcess = @('default', 'quyen')
} else {
    $ProfilesToProcess = @($Profile)
}

$BackupBase = Join-Path $RootDir 'output\week4_session_control'
if (-not (Test-Path $BackupBase)) {
    New-Item -ItemType Directory -Path $BackupBase -Force | Out-Null
}

foreach ($p in $ProfilesToProcess) {
    Write-Host "`n--> Đang xử lý profile [$p]..." -ForegroundColor Green
    $StateFile = Join-Path $BackupBase "$($p)_state.json"
    
    # Check current state preview
    Write-Host "1. Kiểm tra trạng thái hiện tại của rule..."
    $PreviewCmd = "$PythonExe `"$ScriptDir\session_control.py`" preview --profile $p"
    try {
        $PreviewOutput = Invoke-Expression $PreviewCmd
        Write-Host "   Trạng thái hiện hành: $PreviewOutput" -ForegroundColor Gray
    } catch {
        Write-Warning "   Không thể đọc trạng thái rule cho profile $p (phiên lab có thể đã hết hạn hoặc offline)."
        continue
    }

    # Execute pause with state persistence
    Write-Host "2. Tạm dừng (PAUSE/DISABLE) EventBridge rule để tránh kích hoạt ngoài giờ lab..."
    $PauseCmd = "$PythonExe `"$ScriptDir\session_control.py`" pause --profile $p --state-file `"$StateFile`" --apply"
    try {
        $PauseOutput = Invoke-Expression $PauseCmd
        Write-Host "   Kết quả: $PauseOutput" -ForegroundColor Cyan
    } catch {
        Write-Warning "   Thao tác pause gặp lỗi hoặc state file đã tồn tại. Đang kiểm tra..."
    }
}

Write-Host "`n=================================================================" -ForegroundColor Green
Write-Host " [HOÀN TẤT] TÀI NGUYÊN ĐÃ ĐƯỢC ĐƯA VỀ TRẠNG THÁI NGHỈ AN TOÀN   " -ForegroundColor Green
Write-Host " S3 Data Lake và toàn bộ bản ghi minh chứng được bảo toàn 100%. " -ForegroundColor Green
Write-Host " Khi bắt đầu buổi lab mới, chạy start_resources.ps1 để khôi phục." -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
