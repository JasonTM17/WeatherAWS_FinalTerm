# ==============================================================================
# Script 02: Setup AWS Secrets Manager
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí
# Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
# ==============================================================================

param(
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "==> [02/07] Khởi tạo AWS Secrets Manager cho API Key & Cấu hình..." -ForegroundColor Cyan

$accountId = (aws sts get-caller-identity --query "Account" --output text).Trim()
$secretName = "weather/api_config"

$configPayload = @{
    api_provider = "open-meteo"
    api_key = "sec_demo_weather_api_key_$accountId"
    aqi_threshold_pm25 = 35.5
    aqi_threshold_pm10 = 50.0
    aqi_threshold_us_aqi = 100
    locations = @(
        @{ city = "HoChiMinh"; lat = 10.8231; lon = 106.6297 },
        @{ city = "HaNoi"; lat = 21.0285; lon = 105.8542 },
        @{ city = "DaNang"; lat = 16.0544; lon = 108.2022 }
    )
} | ConvertTo-Json -Depth 5 -Compress

# Kiểm tra xem Secret đã tồn tại chưa
$check = aws secretsmanager describe-secret --secret-id $secretName --region $Region 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "    Đang tạo Secret mới: $secretName..." -ForegroundColor Yellow
    aws secretsmanager create-secret --name $secretName `
        --description "API credentials and configuration for Weather and AQI pipeline" `
        --secret-string "$configPayload" `
        --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm `
        --region $Region
} else {
    Write-Host "    Cập nhật giá trị Secret: $secretName..." -ForegroundColor Yellow
    aws secretsmanager put-secret-value --secret-id $secretName --secret-string "$configPayload" --region $Region
}

Write-Host "==> [02/07] Secrets Manager $secretName đã được thiết lập!" -ForegroundColor Green
