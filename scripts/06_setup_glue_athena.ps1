# ==============================================================================
# Script 06: Setup AWS Glue Catalog & Amazon Athena Table
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí
# Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
# ==============================================================================

param(
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "==> [06/07] Khởi tạo AWS Glue Database & Athena External Table..." -ForegroundColor Cyan

$accountId = (aws sts get-caller-identity --query "Account" --output text).Trim()
$bucketName = "weather-aqi-$accountId"
$dbName = "weather_aqi_db"
$outputLocation = "s3://$bucketName/athena-results/"

# 1. Tạo Glue Database
$checkDb = aws glue get-database --name $dbName --region $Region 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "    Đang tạo Glue database: $dbName..." -ForegroundColor Yellow
    $dbInput = @{
        Name = $dbName
        Description = "Database for Weather and Air Quality IoT and API Analytics"
    } | ConvertTo-Json -Compress
    aws glue create-database --database-input "$dbInput" --region $Region
} else {
    Write-Host "    Glue database $dbName đã tồn tại." -ForegroundColor Green
}

# 2. Chạy DDL tạo Athena Table
Write-Host "    Đang thực thi DDL Athena External Table..."
$rootPath = Split-Path -Parent $PSScriptRoot
$sqlPath = Join-Path $rootPath "athena\create_table.sql"
$ddlSql = Get-Content $sqlPath -Raw
$ddlSql = $ddlSql -replace "weather-aqi-[0-9a-zA-Z_-]+", $bucketName

$execDdl = aws athena start-query-execution `
    --query-string "$ddlSql" `
    --query-execution-context Database=$dbName `
    --result-configuration OutputLocation=$outputLocation `
    --region $Region | ConvertFrom-Json

$qidDdl = $execDdl.QueryExecutionId
Write-Host "    DDL Query ID: $qidDdl. Đang đợi hoàn tất..."

while ($true) {
    $status = (aws athena get-query-execution --query-execution-id $qidDdl --region $Region --query "QueryExecution.Status.State" --output text).Trim()
    if ($status -in @("SUCCEEDED", "FAILED", "CANCELLED")) { break }
    Start-Sleep -Seconds 1
}

if ($status -ne "SUCCEEDED") {
    Write-Error "    Lỗi thực thi DDL Table: $status"
} else {
    Write-Host "    Bảng weather_airquality_records đã được tạo thành công!" -ForegroundColor Green
}

# 3. Chạy MSCK REPAIR TABLE
Write-Host "    Đang tải phân vùng (MSCK REPAIR TABLE)..."
$repairSql = "MSCK REPAIR TABLE weather_aqi_db.weather_airquality_records;"
$execRepair = aws athena start-query-execution `
    --query-string "$repairSql" `
    --query-execution-context Database=$dbName `
    --result-configuration OutputLocation=$outputLocation `
    --region $Region | ConvertFrom-Json

$qidRepair = $execRepair.QueryExecutionId
while ($true) {
    $status = (aws athena get-query-execution --query-execution-id $qidRepair --region $Region --query "QueryExecution.Status.State" --output text).Trim()
    if ($status -in @("SUCCEEDED", "FAILED", "CANCELLED")) { break }
    Start-Sleep -Seconds 1
}

Write-Host "==> [06/07] Glue & Athena đã sẵn sàng phân tích!" -ForegroundColor Green
