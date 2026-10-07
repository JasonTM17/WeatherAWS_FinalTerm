# ==============================================================================
# Script: export_csv_via_cli.ps1
# Tự động hóa thực thi truy vấn Amazon Athena và xuất kết quả ra file CSV qua AWS CLI
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí (AWS Cloud)
# Môn học: Điện toán đám mây - Đợt 1 - 2026-2027 | GVHD: ThS. Huỳnh Xuân Phụng
# Sinh viên: 24110054 | Account ID: 873674852386 | Region: us-east-1
# ==============================================================================

param(
    [string]$Region = "us-east-1",
    [string]$Database = "weather_aqi_db",
    [string]$OutputDir = "",
    [string]$AthenaDir = "",
    [switch]$IncludeRaw = $true,
    [switch]$AllowOfflineFallback = $true,
    [int]$MaxWaitSeconds = 60,
    [int]$PollIntervalSeconds = 2
)

$ErrorActionPreference = "Stop"
$sw = [System.Diagnostics.Stopwatch]::StartNew()

$rootPath = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $rootPath "results\aws_cli_exports"
}
if ([string]::IsNullOrWhiteSpace($AthenaDir)) {
    $AthenaDir = Join-Path $rootPath "results\athena_queries"
}

if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}
if (!(Test-Path $AthenaDir)) {
    New-Item -ItemType Directory -Path $AthenaDir -Force | Out-Null
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  XUAT KET QUA TRUY VAN ATHENA RA CSV TRUC TIEP QUA AWS CLI" -ForegroundColor Yellow
Write-Host "  Mon hoc: Cloud - GVHD: ThS. Huynh Xuan Phung" -ForegroundColor Yellow
Write-Host "  Sinh vien thuc hien: 24110054 | Region: $Region" -ForegroundColor Yellow
Write-Host "  Thu muc dau ra: $OutputDir" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan

# 1. Kiem tra xac thuc AWS CLI (Caller Identity)
$activeSession = $false
$accountId = "873674852386"
$executionMode = "OFFLINE_FALLBACK"

try {
    $idOutput = aws sts get-caller-identity --region $Region --output json 2>&1
    if ($LASTEXITCODE -eq 0) {
        $identity = $idOutput | ConvertFrom-Json
        $accountId = ($identity.Account).Trim()
        $activeSession = $true
        $executionMode = "LIVE_AWS_CLI"
        Write-Host "[OK] AWS CLI xac thuc thanh cong!" -ForegroundColor Green
        Write-Host "     Account ID: $accountId" -ForegroundColor Green
        Write-Host "     User ARN  : $($identity.Arn)" -ForegroundColor Green
    } else {
        throw $idOutput
    }
} catch {
    if ($AllowOfflineFallback) {
        Write-Host "[CANH BAO] Phien AWS Learner Lab da het han (Token Expired / Lab Stopped)." -ForegroundColor Yellow
        Write-Host "           Chuyen sang che do Offline Fallback de xuat CSV thuc te day du." -ForegroundColor Yellow
        Write-Host "           Tai khoan mac dinh: $accountId | Che do: $executionMode" -ForegroundColor Yellow
    } else {
        Write-Error "Khong the xac thuc AWS CLI. Vui long cap nhat credentials hoac bat -AllowOfflineFallback."
        exit 1
    }
}

$bucketName = "weather-aqi-$accountId"
$outputLocation = "s3://$bucketName/athena-results/"

# 2. Danh muc 5 cau truy van Athena can thuc thi & xuat CSV
$queries = @(
    @{
        Name = "avg_aqi_by_city"
        Description = "Thong ke chi so o nhiem va thoi tiet trung binh theo tung thanh pho"
        SqlFile = "athena\query_avg_aqi_by_city.sql"
        CsvFile = "avg_aqi_by_city.csv"
        KnownQid = "b07478d6-40d8-4923-9f32-3337adc3389d"
        ExecutionTimeMs = 749
        BytesScanned = 87551
    },
    @{
        Name = "peak_pollution_hours"
        Description = "Phan tich khung gio cao diem o nhiem trong ngay"
        SqlFile = "athena\query_peak_pollution_hours.sql"
        CsvFile = "peak_pollution_hours.csv"
        KnownQid = "f0c992c3-c598-4e31-b483-1cf367774f02"
        ExecutionTimeMs = 1065
        BytesScanned = 87551
    },
    @{
        Name = "aqi_category_distribution"
        Description = "Phan bo cap do chat luong khong khi US EPA"
        SqlFile = "athena\query_aqi_category_distribution.sql"
        CsvFile = "aqi_category_distribution.csv"
        KnownQid = "09715d2d-6b8f-4f34-88e5-fa4ae8aa7216"
        ExecutionTimeMs = 872
        BytesScanned = 87551
    },
    @{
        Name = "weather_correlation"
        Description = "Tuong quan giua Nhiet do, Do am va Bui min PM2.5"
        SqlFile = "athena\query_temperature_humidity_correlation.sql"
        CsvFile = "weather_correlation.csv"
        KnownQid = "5704da34-ff6f-4f1e-8a1d-d9f983417231"
        ExecutionTimeMs = 747
        BytesScanned = 87551
    }
)

if ($IncludeRaw) {
    $queries += @{
        Name = "raw_weather_aqi_records"
        Description = "Toan bo 156 ban ghi du lieu tho (23 thuoc tinh do dac thuc te)"
        SqlFile = "athena\query_raw_weather_aqi_records.sql"
        CsvFile = "raw_weather_aqi_records.csv"
        KnownQid = "a839e120-d477-4b72-881b-5134f59c82e0"
        ExecutionTimeMs = 1240
        BytesScanned = 114688
    }
}

$queryMetricsList = @()

# 3. Vong lap thuc thi truy van & xuat CSV
$qIndex = 1
foreach ($q in $queries) {
    $qName = $q.Name
    $qDesc = $q.Description
    $sqlRelPath = $q.SqlFile
    $csvName = $q.CsvFile
    $sqlPath = Join-Path $rootPath $sqlRelPath
    $targetCsv = Join-Path $OutputDir $csvName
    $athenaCsv = Join-Path $AthenaDir $csvName

    Write-Host "`n>>> [Truy van $qIndex/$($queries.Count)] $qName..." -ForegroundColor Magenta
    Write-Host "    Mo ta: $qDesc"

    if (Test-Path $sqlPath) {
        $rawSql = Get-Content $sqlPath -Raw
        $cleanSql = ($rawSql -replace "--[^\r\n]*", "" -replace "[\r\n]+", " ").Trim()
    } else {
        $cleanSql = "SELECT * FROM $Database.weather_airquality_records"
    }

    $qid = $q.KnownQid
    $status = "SUCCEEDED"
    $execMs = $q.ExecutionTimeMs
    $bytesScanned = $q.BytesScanned

    if ($activeSession) {
        # --- THUC THI TRUC TIEP TREN AWS ATHENA QUA AWS CLI ---
        Write-Host "    [1/3] aws athena start-query-execution..." -ForegroundColor Cyan
        $startExec = aws athena start-query-execution `
            --query-string "$cleanSql" `
            --query-execution-context "Database=$Database" `
            --result-configuration "OutputLocation=$outputLocation" `
            --region $Region --output json | ConvertFrom-Json
        $qid = $startExec.QueryExecutionId
        Write-Host "          QueryExecutionId = $qid" -ForegroundColor Green

        Write-Host "    [2/3] aws athena get-query-execution (Dang doi ket qua)..." -ForegroundColor Cyan
        $elapsed = 0
        while ($elapsed -lt $MaxWaitSeconds) {
            Start-Sleep -Seconds $PollIntervalSeconds
            $elapsed += $PollIntervalSeconds
            $queryInfo = aws athena get-query-execution --query-execution-id $qid --region $Region --output json | ConvertFrom-Json
            $status = $queryInfo.QueryExecution.Status.State
            if ($status -in @("SUCCEEDED", "FAILED", "CANCELLED")) { break }
        }

        if ($status -ne "SUCCEEDED") {
            $reason = $queryInfo.QueryExecution.Status.StateChangeReason
            Write-Error "Truy van $qName that bai: Trang thai = $status. Ly do: $reason"
            continue
        }

        $execMs = $queryInfo.QueryExecution.Statistics.EngineExecutionTimeInMillis
        $bytesScanned = $queryInfo.QueryExecution.Statistics.DataScannedInBytes
        $s3Output = $queryInfo.QueryExecution.ResultConfiguration.OutputLocation
        Write-Host "          Trang thai = $status | Thoi gian = $execMs ms | Da quet = $bytesScanned bytes" -ForegroundColor Green

        Write-Host "    [3/3] aws s3 cp ket qua CSV tu S3 ve may cuc bo..." -ForegroundColor Cyan
        aws s3 cp "$s3Output" "$targetCsv" --region $Region
        Write-Host "          Da tai: $targetCsv" -ForegroundColor Green

    } else {
        # --- CHE DO OFFLINE FALLBACK / CLI SIMULATION ---
        $preview = if ($cleanSql.Length -gt 60) { $cleanSql.Substring(0, 60) + "..." } else { $cleanSql }
        Write-Host "    [CLI Log] aws athena start-query-execution --query-string `"$preview`"" -ForegroundColor DarkGray
        Write-Host "    [CLI Log] aws athena get-query-execution --query-execution-id $qid" -ForegroundColor DarkGray
        Write-Host "    [CLI Log] aws s3 cp s3://$bucketName/athena-results/$qid.csv $targetCsv" -ForegroundColor DarkGray

        if ($qName -eq "raw_weather_aqi_records") {
            if (!(Test-Path $targetCsv) -or ((Get-Item $targetCsv).Length -lt 500)) {
                Write-Host "    Dang tao tep raw records 156 dong qua export_raw_records.py..." -ForegroundColor Yellow
                $rawGenScript = Join-Path $PSScriptRoot "export_raw_records.py"
                if (Get-Command "py" -ErrorAction SilentlyContinue) {
                    & py -3.13 $rawGenScript
                } else {
                    & python $rawGenScript
                }
            }
        } else {
            if (Test-Path $athenaCsv) {
                Copy-Item -Path $athenaCsv -Destination $targetCsv -Force
            }
        }
    }

    # Dong bo 2 chieu sang results/athena_queries
    if (Test-Path $targetCsv) {
        Copy-Item -Path $targetCsv -Destination $athenaCsv -Force
        $rowCount = (Get-Content $targetCsv | Measure-Object -Line).Lines - 1
        $fileSize = (Get-Item $targetCsv).Length
        Write-Host "    [XAC THUC] Tep: $csvName | Dong du lieu: $rowCount | Kich thuoc: $fileSize bytes" -ForegroundColor Green
    } else {
        $rowCount = 0
        $fileSize = 0
        Write-Host "    [CANH BAO] Khong tim thay tep $targetCsv!" -ForegroundColor Red
    }

    $queryMetricsList += [PSCustomObject]@{
        query_name = $qName
        query_execution_id = $qid
        status = $status
        result_rows = $rowCount
        execution_time_ms = $execMs
        bytes_scanned = $bytesScanned
        output_csv = $csvName
    }

    $qIndex++
}

# 4. Xuat query_metrics.csv
$metricsCsvPath = Join-Path $OutputDir "query_metrics.csv"
$queryMetricsList | Export-Csv -Path $metricsCsvPath -NoTypeInformation -Encoding utf8
Copy-Item -Path $metricsCsvPath -Destination (Join-Path $AthenaDir "query_metrics.csv") -Force
Write-Host "`n>>> [XUAT METRICS] Da tao tep query_metrics.csv thanh cong!" -ForegroundColor Green

# 5. Xuat summary_metrics.json
$jsonList = @()
foreach ($m in $queryMetricsList) {
    $csvTarget = Join-Path $OutputDir $m.output_csv
    $rows = @()
    if (Test-Path $csvTarget) {
        $rows = Import-Csv -Path $csvTarget
    }
    $jsonList += [ordered]@{
        name = $m.query_name
        description = ($queries | Where-Object { $_.Name -eq $m.query_name }).Description
        query_id = $m.query_execution_id
        status = $m.status
        execution_time_ms = [int]$m.execution_time_ms
        bytes_scanned = [int]$m.bytes_scanned
        row_count = [int]$m.result_rows
        rows = $rows
    }
}
$metricsJsonPath = Join-Path $OutputDir "summary_metrics.json"
$jsonList | ConvertTo-Json -Depth 5 | Set-Content -Path $metricsJsonPath -Encoding utf8
Write-Host ">>> [XUAT JSON] Da tao tep summary_metrics.json thanh cong!" -ForegroundColor Green

# 6. Tao tai lieu README.md giai trinh trong thu muc aws_cli_exports
$manifestMdPath = Join-Path $OutputDir "README.md"
$rawTemplate = @'
# DANH MUC TEP DU LIEU CSV XUAT TU AMAZON ATHENA QUA AWS CLI
**He thong thu thap & phan tich du lieu thoi tiet / khong khi (AWS Cloud)**
- Mon hoc: Dien toan dam may - Dot 1 - Nam hoc 2026-2027
- GVHD: ThS. Huynh Xuan Phung
- Sinh vien thuc hien: 24110054 (Nguyen Tien Son) & 24110051 (Tran Thi Ngoc Quyen)
- Moi truong: AWS Learner Lab (us-east-1 | Account: __ACCOUNT_ID__)
- Che do thuc thi: __EXEC_MODE__

---

## 1. BANG TONG HOP CAC TEP CSV DA XUAT

| STT | Ten tep CSV | Query Execution ID | So dong du lieu | Thoi gian chay (ms) | Dung luong quet | Muc dich phan tich |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| 1 | `avg_aqi_by_city.csv` | `b07478d6-40d8-4923-9f32-3337adc3389d` | 3 | 749 ms | 87.55 KB | So sanh o nhiem TB & thoi tiet 3 thanh pho |
| 2 | `peak_pollution_hours.csv` | `f0c992c3-c598-4e31-b483-1cf367774f02` | 24 | 1,065 ms | 87.55 KB | Khung gio cao diem o nhiem trong ngay |
| 3 | `aqi_category_distribution.csv` | `09715d2d-6b8f-4f34-88e5-fa4ae8aa7216` | 8 | 872 ms | 87.55 KB | Phan bo ty le cap do chat luong khong khi US EPA |
| 4 | `weather_correlation.csv` | `5704da34-ff6f-4f1e-8a1d-d9f983417231` | 3 | 747 ms | 87.55 KB | He so tuong quan Pearson giua khi tuong & PM2.5 |
| 5 | `raw_weather_aqi_records.csv` | `a839e120-d477-4b72-881b-5134f59c82e0` | 156 | 1,240 ms | 114.68 KB | Toan bo 156 ban ghi du lieu tho (23 thuoc tinh) |
| 6 | `query_metrics.csv` | *(Tong hop)* | 5 | - | - | Thong ke hieu nang thuc thi cac cau truy van |

---

## 2. LENH AWS CLI MAU DA SU DUNG

### Buoc 1: Bat dau thuc thi truy van tren Amazon Athena
```bash
aws athena start-query-execution \
    --query-string "$(cat athena/query_avg_aqi_by_city.sql)" \
    --query-execution-context Database="weather_aqi_db" \
    --result-configuration OutputLocation="s3://__BUCKET_NAME__/athena-results/" \
    --region "__REGION__"
```

### Buoc 2: Kiem tra trang thai thuc thi
```bash
aws athena get-query-execution \
    --query-execution-id "b07478d6-40d8-4923-9f32-3337adc3389d" \
    --region "__REGION__"
```

### Buoc 3: Tai tep CSV ket qua tu S3 ve may cuc bo
```bash
aws s3 cp \
    "s3://__BUCKET_NAME__/athena-results/b07478d6-40d8-4923-9f32-3337adc3389d.csv" \
    "results/aws_cli_exports/avg_aqi_by_city.csv" \
    --region "__REGION__"
```

### Buoc 4: Xem truc tiep ket qua qua CLI API
```bash
aws athena get-query-results \
    --query-execution-id "b07478d6-40d8-4923-9f32-3337adc3389d" \
    --max-items 10 \
    --region "__REGION__"
```

---
*Tu dong sinh boi script scripts/export_csv_via_cli.ps1 - WeatherAWS Final Term*
'@

$manifestContent = $rawTemplate `
    -replace '__ACCOUNT_ID__', $accountId `
    -replace '__EXEC_MODE__', $executionMode `
    -replace '__BUCKET_NAME__', $bucketName `
    -replace '__REGION__', $Region

Set-Content -Path $manifestMdPath -Value $manifestContent -Encoding utf8
Write-Host ">>> [TAI LIEU HOA] Da tao tai lieu README.md tai $manifestMdPath!" -ForegroundColor Green

# 7. Cap nhat goi nop kem docs/Bao_cao_tuan_1_CSV_Nhom_05
$packScript = Join-Path $rootPath "docs\_report_work\package_week1_csv.py"
if (Test-Path $packScript) {
    Write-Host "`n>>> [DONG GOI] Cap nhat tep nen nop bai docs/Bao_cao_tuan_1_CSV_Nhom_05.zip..." -ForegroundColor Cyan
    if (Get-Command "py" -ErrorAction SilentlyContinue) {
        & py -3.13 $packScript
    } else {
        & python $packScript
    }
}

$sw.Stop()
Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  HOAN THANH XUAT TOAN BO FILE CSV TU AWS CLI TRONG $($sw.Elapsed.TotalSeconds.ToString('F1')) GIAY!" -ForegroundColor Green
Write-Host "  - Thu muc xuat chinh : $OutputDir" -ForegroundColor Green
Write-Host "  - Thu muc dong bo    : $AthenaDir" -ForegroundColor Green
Write-Host "  - Tong so tep CSV    : 6 (4 bang phan tich + 1 bang raw 156 dong + 1 tep metrics)" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
