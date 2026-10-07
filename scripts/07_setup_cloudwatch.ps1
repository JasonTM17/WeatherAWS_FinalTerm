# ==============================================================================
# Script 07: Setup Amazon CloudWatch Alarms & Monitoring Dashboard
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí
# Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
# ==============================================================================

param(
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "==> [07/07] Khởi tạo CloudWatch Metric Alarms & Dashboard..." -ForegroundColor Cyan

$accountId = (aws sts get-caller-identity --query "Account" --output text).Trim()
$functionName = "WeatherCollectorLambda"
$snsTopicArn = "arn:aws:sns:$Region`:$accountId`:weather-airquality-alerts"
$alarmName = "WeatherCollector-Errors-Alarm"
$dashboardName = "WeatherAirQuality-Monitoring-Dashboard"

# 1. Tạo Alarm giám sát lỗi Lambda
Write-Host "    Đang tạo CloudWatch Alarm: $alarmName..."
aws cloudwatch put-metric-alarm `
    --alarm-name $alarmName `
    --alarm-description "Triggers alarm if WeatherCollectorLambda has execution errors" `
    --metric-name "Errors" `
    --namespace "AWS/Lambda" `
    --statistic "Sum" `
    --period 300 `
    --threshold 1 `
    --comparison-operator "GreaterThanOrEqualToThreshold" `
    --dimensions "Name=FunctionName,Value=$functionName" `
    --evaluation-periods 1 `
    --alarm-actions $snsTopicArn `
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm `
    --region $Region

# 2. Tạo Dashboard giám sát hệ thống
Write-Host "    Đang tạo CloudWatch Dashboard: $dashboardName..."
$dashboardBody = @{
    widgets = @(
        @{
            type = "metric"
            x = 0; y = 0; width = 12; height = 6
            properties = @{
                metrics = @(
                    @("AWS/Lambda", "Invocations", "FunctionName", $functionName, @{ stat = "Sum"; label = "Invocations" }),
                    @("AWS/Lambda", "Errors", "FunctionName", $functionName, @{ stat = "Sum"; label = "Errors"; color = "#d62728" })
                )
                view = "timeSeries"
                stacked = $false
                region = $Region
                title = "Lambda Execution & Error Rate"
                period = 300
            }
        },
        @{
            type = "metric"
            x = 12; y = 0; width = 12; height = 6
            properties = @{
                metrics = @(
                    @("AWS/Lambda", "Duration", "FunctionName", $functionName, @{ stat = "Average"; label = "Avg Duration (ms)" }),
                    @("AWS/Lambda", "Duration", "FunctionName", $functionName, @{ stat = "Maximum"; label = "Max Duration (ms)" })
                )
                view = "timeSeries"
                stacked = $false
                region = $Region
                title = "Lambda Execution Duration"
                period = 300
            }
        },
        @{
            type = "text"
            x = 0; y = 6; width = 24; height = 3
            properties = @{
                markdown = "# He thong thu thap va phan tich du lieu thoi tiet / khong khi`n**Mon hoc:** Cloud - Dot 1 - 2026-2027 | **GVHD:** Huynh Xuan Phung | **SV:** 24110054`n**Account ID:** $accountId | **Region:** $Region | **Pipeline:** EventBridge -> Lambda -> S3 -> Glue/Athena -> SNS"
            }
        }
    )
} | ConvertTo-Json -Depth 10

$tempDashboardFile = [System.IO.Path]::GetTempFileName()
try {
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($tempDashboardFile, $dashboardBody, $utf8NoBom)
    aws cloudwatch put-dashboard --dashboard-name $dashboardName --dashboard-body "file://$tempDashboardFile" --region $Region
} finally {
    if (Test-Path $tempDashboardFile) {
        Remove-Item $tempDashboardFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "==> [07/07] CloudWatch Monitoring hoàn tất!" -ForegroundColor Green
