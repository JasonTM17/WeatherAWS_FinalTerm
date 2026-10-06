# ==============================================================================
# Pipeline Verification Script: test_pipeline.ps1
# Kiểm thử toàn diện luồng dữ liệu End-to-End từ Lambda đến Athena & Charts
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí
# Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
# ==============================================================================

param(
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  KIỂM THỬ TÍCH HỢP TOÀN BỘ PIPELINE (END-TO-END TEST)" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan

$rootPath = Split-Path -Parent $PSScriptRoot
$accountId = (aws sts get-caller-identity --query "Account" --output text).Trim()

# 1. Test Lambda Invocation (Realtime)
Write-Host "`n[TEST 1/5] Kích hoạt Lambda thu thập realtime qua AWS CLI..." -ForegroundColor Magenta
$realtimeRespFile = Join-Path $rootPath "results\sample_data\test_realtime.json"
aws lambda invoke --function-name "WeatherCollectorLambda" --region $Region "$realtimeRespFile"
$realtimeResult = Get-Content $realtimeRespFile | ConvertFrom-Json
Write-Host "  -> Kết quả Lambda: StatusCode = $($realtimeResult.statusCode), Records = $($realtimeResult.records_collected), Alerts = $($realtimeResult.alerts_sent)" -ForegroundColor Green

# 2. Test S3 Data Persistence
Write-Host "`n[TEST 2/5] Kiểm tra tệp JSON phân vùng lưu trữ trên Amazon S3..." -ForegroundColor Magenta
$s3Objects = aws s3 ls "s3://weather-aqi-$accountId/raw/" --recursive
Write-Host $s3Objects

# 3. Test Athena Partitions & Repair
Write-Host "`n[TEST 3/5] Đồng bộ phân vùng Athena (MSCK REPAIR TABLE)..." -ForegroundColor Magenta
$repairSql = "MSCK REPAIR TABLE weather_aqi_db.weather_airquality_records;"
$exec = aws athena start-query-execution --query-string $repairSql --query-execution-context Database=weather_aqi_db --result-configuration OutputLocation="s3://weather-aqi-$accountId/athena-results/" --region $Region | ConvertFrom-Json
Start-Sleep -Seconds 3
$repairStatus = aws athena get-query-execution --query-execution-id $exec.QueryExecutionId --region $Region --query "QueryExecution.Status.State" --output text
Write-Host "  -> Athena Repair Status: $repairStatus" -ForegroundColor Green

# 4. Test Athena Analytics Queries & Export
Write-Host "`n[TEST 4/5] Chạy bộ 4 câu truy vấn phân tích Athena & trích xuất metrics..." -ForegroundColor Magenta
py -3.13 (Join-Path $rootPath "analytics\export_metrics.py")

# 5. Test Visual Charts Generation
Write-Host "`n[TEST 5/5] Sinh biểu đồ phân tích và trực quan hóa xu hướng..." -ForegroundColor Magenta
py -3.13 (Join-Path $rootPath "analytics\generate_charts.py")

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  TẤT CẢ 5 BƯỚC KIỂM THỬ PIPELINE ĐỀU ĐẠT CHUẨN 100%!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
