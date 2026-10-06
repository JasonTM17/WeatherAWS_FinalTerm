# ==============================================================================
# Script 01: Setup Amazon S3 Storage Bucket
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí
# Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
# ==============================================================================

param(
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "==> [01/07] Khởi tạo Amazon S3 Bucket..." -ForegroundColor Cyan

$accountId = (aws sts get-caller-identity --query "Account" --output text).Trim()
$bucketName = "weather-aqi-$accountId"

Write-Host "    Account ID : $accountId"
Write-Host "    Bucket Name: $bucketName"
Write-Host "    Region     : $Region"

# Tạo Bucket (Region us-east-1 không cần LocationConstraint, các region khác như us-west-2 cần LocationConstraint)
$exists = aws s3api head-bucket --bucket $bucketName 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "    Đang tạo bucket $bucketName tại $Region..." -ForegroundColor Yellow
    if ($Region -eq "us-east-1") {
        aws s3api create-bucket --bucket $bucketName --region $Region
    } else {
        aws s3api create-bucket --bucket $bucketName --region $Region --create-bucket-configuration LocationConstraint=$Region
    }
} else {
    Write-Host "    Bucket $bucketName đã tồn tại." -ForegroundColor Green
}

# Gắn Tags tuân thủ quy định GVHD
Write-Host "    Đang gắn tags tài nguyên..."
aws s3api put-bucket-tagging --bucket $bucketName --tagging "TagSet=[{Key=Project,Value=WeatherAWS_FinalTerm},{Key=Owner,Value=24110054},{Key=Course,Value=Cloud_FinalTerm}]"

Write-Host "==> [01/07] S3 Bucket $bucketName đã sẵn sàng!" -ForegroundColor Green
