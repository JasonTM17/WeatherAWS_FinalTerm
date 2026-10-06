# ==============================================================================
# Master Deployment Script: deploy_all.ps1
# Tự động hóa triển khai toàn bộ hệ thống qua AWS CLI
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí (Nhóm: Domain Apps)
# Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng
# Sinh viên thực hiện: 24110054
# ==============================================================================

param(
    [string]$Region = "us-east-1",
    [string]$AlertEmail = "24110054@student.hcmute.edu.vn"
)

$ErrorActionPreference = "Stop"
$sw = [System.Diagnostics.Stopwatch]::StartNew()

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  HỆ THỐNG THU THẬP VÀ PHÂN TÍCH DỮ LIỆU THỜI TIẾT / KHÔNG KHÍ (AWS)" -ForegroundColor Yellow
Write-Host "  Môn học: Cloud - GVHD: ThS. Huỳnh Xuân Phụng" -ForegroundColor Yellow
Write-Host "  Sinh viên: 24110054 | Region: $Region" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan

# Kiểm tra caller identity
try {
    $identity = aws sts get-caller-identity | ConvertFrom-Json
    Write-Host "[OK] Xác thực AWS thành công: User ARN = $($identity.Arn)" -ForegroundColor Green
    Write-Host "[OK] Account ID: $($identity.Account)" -ForegroundColor Green
} catch {
    Write-Error "Không thể xác thực AWS CLI. Hãy kiểm tra credentials hoặc lab session."
    exit 1
}

$scripts = @(
    "01_setup_s3.ps1",
    "02_setup_secrets.ps1",
    "03_setup_sns.ps1",
    "04_deploy_lambda.ps1",
    "05_setup_eventbridge.ps1",
    "06_setup_glue_athena.ps1",
    "07_setup_cloudwatch.ps1"
)

foreach ($s in $scripts) {
    $path = Join-Path $PSScriptRoot $s
    Write-Host "`n>>> Thực thi script: $s..." -ForegroundColor Magenta
    if ($s -eq "03_setup_sns.ps1") {
        & $path -Region $Region -AlertEmail $AlertEmail
    } else {
        & $path -Region $Region
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Script $s thất bại với mã lỗi $LASTEXITCODE!"
        exit 1
    }
}

$sw.Stop()
Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  TRIỂN KHAI TOÀN BỘ HỆ THỐNG THÀNH CÔNG TRONG $($sw.Elapsed.TotalSeconds.ToString('F1')) GIÂY!" -ForegroundColor Green
Write-Host "  Tài nguyên đã sẵn sàng trên AWS Learner Lab ($Region):" -ForegroundColor Green
Write-Host "  1. S3 Bucket       : weather-aqi-$($identity.Account)"
Write-Host "  2. Secrets Manager : weather/api_config"
Write-Host "  3. SNS Topic       : weather-airquality-alerts"
Write-Host "  4. Lambda Function : WeatherCollectorLambda"
Write-Host "  5. EventBridge Rule: WeatherCollectionSchedule (rate 1 hour)"
Write-Host "  6. Glue & Athena   : weather_aqi_db.weather_airquality_records"
Write-Host "  7. CloudWatch      : WeatherAirQuality-Monitoring-Dashboard"
Write-Host "========================================================================" -ForegroundColor Cyan
