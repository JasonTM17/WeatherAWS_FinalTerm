# ==============================================================================
# Script 05: Setup Amazon EventBridge Scheduler Rule
# Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí
# Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
# ==============================================================================

param(
    [string]$Region = "us-east-1",
    [string]$ScheduleRate = "rate(1 hour)"
)

$ErrorActionPreference = "Stop"

Write-Host "==> [05/07] Khởi tạo Amazon EventBridge Schedule ($ScheduleRate)..." -ForegroundColor Cyan

$accountId = (aws sts get-caller-identity --query "Account" --output text).Trim()
$ruleNames = @("WeatherCollectionHourlyRule", "WeatherCollectionSchedule")
$functionName = "WeatherCollectorLambda"
$functionArn = "arn:aws:lambda:$Region`:$accountId`:function:$functionName"

foreach ($ruleName in $ruleNames) {
    Write-Host "    Thiết lập EventBridge Rule: $ruleName ($ScheduleRate)..." -ForegroundColor Yellow
    $ruleArn = (aws events put-rule `
        --name $ruleName `
        --schedule-expression "$ScheduleRate" `
        --state "ENABLED" `
        --description "Triggers WeatherCollectorLambda periodically to fetch weather and AQI data" `
        --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm `
        --region $Region --query "RuleArn" --output text).Trim()

    Write-Host "    Rule ARN: $ruleArn"

    # Gán Target
    aws events put-targets `
        --rule $ruleName `
        --targets "Id=1,Arn=$functionArn" `
        --region $Region

    # Phân quyền cho EventBridge gọi Lambda
    $statementId = "EventBridgeInvokePermission_$ruleName"
    $permCheck = aws lambda get-policy --function-name $functionName --region $Region 2>&1
    if ($permCheck -notmatch $statementId) {
        Write-Host "    Cấp quyền EventBridge gọi Lambda cho $ruleName..." -ForegroundColor Yellow
        aws lambda add-permission `
            --function-name $functionName `
            --statement-id $statementId `
            --action "lambda:InvokeFunction" `
            --principal "events.amazonaws.com" `
            --source-arn $ruleArn `
            --region $Region
    }
}

Write-Host "==> [05/07] EventBridge Schedules ($($ruleNames -join ', ')) đã sẵn sàng!" -ForegroundColor Green
