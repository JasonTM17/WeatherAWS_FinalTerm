# ==============================================================================
# Script 04: Package and Deploy AWS Lambda Function
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí
# Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
# ==============================================================================

param(
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "==> [04/07] Đóng gói và Triển khai AWS Lambda Function..." -ForegroundColor Cyan

$accountId = (aws sts get-caller-identity --query "Account" --output text).Trim()
$bucketName = "weather-aqi-$accountId"
$functionName = "WeatherCollectorLambda"
$roleArn = "arn:aws:iam::$accountId`:role/LabRole"
$snsTopicArn = "arn:aws:sns:$Region`:$accountId`:weather-airquality-alerts"

$rootPath = Split-Path -Parent $PSScriptRoot
$lambdaSrc = Join-Path $rootPath "lambda\lambda_function.py"
$zipPath = Join-Path $rootPath "lambda_package.zip"

Write-Host "    Đang nén file mã nguồn: $lambdaSrc -> $zipPath..."
Compress-Archive -Path $lambdaSrc -DestinationPath $zipPath -Force

$envVars = "Variables={S3_BUCKET_NAME=$bucketName,SECRET_NAME=weather/api_config,SNS_TOPIC_ARN=$snsTopicArn}"

$checkFunc = aws lambda get-function --function-name $functionName --region $Region 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "    Đang tạo mới Lambda function: $functionName..." -ForegroundColor Yellow
    aws lambda create-function `
        --function-name $functionName `
        --runtime "python3.12" `
        --role $roleArn `
        --handler "lambda_function.lambda_handler" `
        --zip-file "fileb://$zipPath" `
        --timeout 60 `
        --memory-size 256 `
        --environment "$envVars" `
        --tags "Project=WeatherAWS_FinalTerm,Owner=24110054,Course=Cloud_FinalTerm" `
        --region $Region
} else {
    Write-Host "    Đang cập nhật code và cấu hình Lambda function: $functionName..." -ForegroundColor Yellow
    aws lambda update-function-code `
        --function-name $functionName `
        --zip-file "fileb://$zipPath" `
        --region $Region

    Start-Sleep -Seconds 3

    aws lambda update-function-configuration `
        --function-name $functionName `
        --timeout 60 `
        --memory-size 256 `
        --environment "$envVars" `
        --region $Region
}

Write-Host "==> [04/07] Lambda Function $functionName triển khai thành công!" -ForegroundColor Green
