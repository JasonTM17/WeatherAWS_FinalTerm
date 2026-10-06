# ==============================================================================
# Resource Cleanup Script: cleanup_all.ps1
# Dọn dẹp và xóa sạch tài nguyên sau mỗi buổi thực hành theo yêu cầu của GVHD:
# "dừng/xóa tài nguyên sau mỗi buổi; báo cáo chi phí sử dụng cuối kỳ"
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí
# Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
# ==============================================================================

param(
    [string]$Region = "us-east-1",
    [switch]$Force
)

Write-Host "========================================================================" -ForegroundColor Yellow
Write-Host "  DỌN DẸP VÀ XÓA TÀI NGUYÊN AWS LEARNER LAB (TỐI ƯU CHI PHÍ)" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Yellow

$accountId = (aws sts get-caller-identity --query "Account" --output text).Trim()
$bucketName = "weather-aqi-$accountId"
$functionName = "WeatherCollectorLambda"
$ruleName = "WeatherCollectionSchedule"
$topicArn = "arn:aws:sns:$Region`:$accountId`:weather-airquality-alerts"
$secretName = "weather/api_config"
$dbName = "weather_aqi_db"
$alarmName = "WeatherCollector-Errors-Alarm"
$dashboardName = "WeatherAirQuality-Monitoring-Dashboard"

# 1. Xóa EventBridge Rule & Targets
Write-Host "`n[1/8] Xóa EventBridge Rule: $ruleName..." -ForegroundColor Cyan
aws events remove-targets --rule $ruleName --ids "1" --region $Region 2>$null
aws events delete-rule --name $ruleName --region $Region 2>$null
Write-Host "  -> EventBridge Rule đã bị xóa." -ForegroundColor Green

# 2. Xóa CloudWatch Dashboard & Alarm
Write-Host "`n[2/8] Xóa CloudWatch Monitoring (Dashboard & Alarm)..." -ForegroundColor Cyan
aws cloudwatch delete-dashboards --dashboard-names $dashboardName --region $Region 2>$null
aws cloudwatch delete-alarms --alarm-names $alarmName --region $Region 2>$null
Write-Host "  -> CloudWatch Dashboard & Alarm đã bị xóa." -ForegroundColor Green

# 3. Xóa AWS Lambda Function
Write-Host "`n[3/8] Xóa AWS Lambda Function: $functionName..." -ForegroundColor Cyan
aws lambda delete-function --function-name $functionName --region $Region 2>$null
Write-Host "  -> Lambda Function đã bị xóa." -ForegroundColor Green

# 4. Xóa Amazon SNS Topic
Write-Host "`n[4/8] Xóa Amazon SNS Topic: $topicArn..." -ForegroundColor Cyan
aws sns delete-topic --topic-arn $topicArn --region $Region 2>$null
Write-Host "  -> SNS Topic đã bị xóa." -ForegroundColor Green

# 5. Xóa Glue Database & Athena Tables
Write-Host "`n[5/8] Xóa AWS Glue Database: $dbName..." -ForegroundColor Cyan
aws glue delete-table --database-name $dbName --name "weather_airquality_records" --region $Region 2>$null
aws glue delete-database --name $dbName --region $Region 2>$null
Write-Host "  -> Glue Database & Athena Tables đã bị xóa." -ForegroundColor Green

# 6. Xóa AWS Secrets Manager Secret
Write-Host "`n[6/8] Xóa AWS Secrets Manager: $secretName..." -ForegroundColor Cyan
aws secretsmanager delete-secret --secret-id $secretName --force-delete-without-recovery --region $Region 2>$null
Write-Host "  -> Secret đã bị xóa hoàn toàn." -ForegroundColor Green

# 7. Xóa dữ liệu và Amazon S3 Bucket
Write-Host "`n[7/8] Xóa dữ liệu và Amazon S3 Bucket: $bucketName..." -ForegroundColor Cyan
aws s3 rm "s3://$bucketName" --recursive 2>$null
aws s3api delete-bucket --bucket $bucketName --region $Region 2>$null
Write-Host "  -> S3 Bucket và toàn bộ dữ liệu đã được giải phóng." -ForegroundColor Green

# 8. Dọn dẹp CloudWatch Log Groups
Write-Host "`n[8/8] Xóa CloudWatch Log Group: /aws/lambda/$functionName..." -ForegroundColor Cyan
aws logs delete-log-group --log-group-name "/aws/lambda/$functionName" --region $Region 2>$null
Write-Host "  -> Log Group đã bị xóa." -ForegroundColor Green

Write-Host "`n========================================================================" -ForegroundColor Green
Write-Host "  HOÀN TẤT DỌN DẸP TOÀN BỘ TÀI NGUYÊN! CHI PHÍ LAB ĐÃ ĐƯỢC BẢO TOÀN 100%." -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
