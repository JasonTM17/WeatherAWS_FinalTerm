# ==============================================================================
# Script 03: Setup Amazon SNS Alerting Topic
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí
# Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
# ==============================================================================

param(
    [string]$Region = "us-east-1",
    [string]$AlertEmail = "24110054@student.hcmute.edu.vn"
)

$ErrorActionPreference = "Stop"

Write-Host "==> [03/07] Khởi tạo Amazon SNS Topic và Email Subscription..." -ForegroundColor Cyan

$topicName = "weather-airquality-alerts"

$topicArn = (aws sns create-topic --name $topicName `
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm `
    --region $Region --query "TopicArn" --output text).Trim()

Write-Host "    Topic ARN: $topicArn"

if ($AlertEmail) {
    Write-Host "    Đăng ký nhận cảnh báo email: $AlertEmail..." -ForegroundColor Yellow
    aws sns subscribe --topic-arn $topicArn --protocol email --notification-endpoint $AlertEmail --region $Region
}

Write-Host "==> [03/07] SNS Topic đã sẵn sàng!" -ForegroundColor Green
