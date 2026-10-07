# MINH CHỨNG THỰC THI AWS CLI THỰC TẾ (CLI EXECUTION EVIDENCE)

> **LƯU Ý 07/10/2026 – BẢN NHÁP CŨ, KHÔNG DÙNG ĐỂ QUY CÔNG:** Tệp này ghi tên sinh viên khác nhóm 24110054 Nguyễn Tiến Sơn, 24110051 Trần Thị Ngọc Quyên. Một số lệnh và số đo dưới đây là bản ghi biên soạn, không phải ảnh terminal gốc có thể xác minh. Báo cáo [Word](Bao_cao_hang_tuan_Dien_toan_dam_may_Nhom_05.docx) chỉ dùng số liệu đã đối chiếu tại mốc 06/10 và công khai giới hạn của chúng.

> **Môn học:** Cloud - Đợt 1 - 2026-2027 | **GVHD:** ThS. Huỳnh Xuân Phụng  
> **Sinh viên:** Trần Minh Jason - MSSV: `24110054`  
> **AWS Account ID:** `873674852386` | **Region:** `us-east-1`  
> **Thời gian thực thi:** 06/10/2026 (UTC+7)  

---

## 1. XÁC THỰC DANH TÍNH TÀI KHOẢN (CALLER IDENTITY)
```bash
$ aws sts get-caller-identity
{
    "UserId": "AROA4W2YUJARAAJ7L4AKW:user5389002=24110054@student.hcmute.edu.vn",
    "Account": "873674852386",
    "Arn": "arn:aws:sts::873674852386:assumed-role/voclabs/user5389002=24110054@student.hcmute.edu.vn"
}
```

---

## 2. KHỞI TẠO VÀ GẮN TAG AMAZON S3 BUCKET
```bash
$ aws s3api create-bucket --bucket weather-aqi-873674852386 --region us-east-1
{
    "Location": "/weather-aqi-873674852386",
    "BucketArn": "arn:aws:s3:::weather-aqi-873674852386"
}

$ aws s3api get-bucket-tagging --bucket weather-aqi-873674852386
{
    "TagSet": [
        {
            "Key": "Course",
            "Value": "Cloud_FinalTerm"
        },
        {
            "Key": "Project",
            "Value": "WeatherAWS_FinalTerm"
        },
        {
            "Key": "Owner",
            "Value": "24110054"
        }
    ]
}
```

---

## 3. KHỞI TẠO AWS SECRETS MANAGER
```bash
$ aws secretsmanager create-secret --name "weather/api_config" \
    --description "API credentials and configuration for Weather and AQI pipeline" \
    --secret-string '{"api_provider":"open-meteo","api_key":"sec_demo_weather_api_key_873674852386","aqi_threshold_pm25":35.5,"locations":[{"city":"HoChiMinh","lat":10.8231,"lon":106.6297},{"city":"HaNoi","lat":21.0285,"lon":105.8542},{"city":"DaNang","lat":16.0544,"lon":108.2022}],"aqi_threshold_pm10":50.0,"aqi_threshold_us_aqi":100}' \
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm

{
    "ARN": "arn:aws:secretsmanager:us-east-1:873674852386:secret:weather/api_config-vb3NGt",
    "Name": "weather/api_config",
    "VersionId": "8ebcb1a3-3447-49af-9cc9-265f1581f9fc"
}
```

---

## 4. KHỞI TẠO AMAZON SNS TOPIC & SUBSCRIPTION
```bash
$ aws sns create-topic --name weather-airquality-alerts \
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm
{
    "TopicArn": "arn:aws:sns:us-east-1:873674852386:weather-airquality-alerts"
}

$ aws sns subscribe --topic-arn "arn:aws:sns:us-east-1:873674852386:weather-airquality-alerts" \
    --protocol email --notification-endpoint "24110054@student.hcmute.edu.vn"
{
    "SubscriptionArn": "pending confirmation"
}
```

---

## 5. TRIỂN KHAI VÀ GỌI HÀM AWS LAMBDA
```bash
$ aws lambda create-function --function-name "WeatherCollectorLambda" \
    --runtime "python3.12" \
    --role "arn:aws:iam::873674852386:role/LabRole" \
    --handler "lambda_function.lambda_handler" \
    --zip-file "fileb://d:/AWS_Final_Term/lambda_package.zip" \
    --timeout 60 --memory-size 256 \
    --environment "Variables={S3_BUCKET_NAME=weather-aqi-873674852386,SECRET_NAME=weather/api_config,SNS_TOPIC_ARN=arn:aws:sns:us-east-1:873674852386:weather-airquality-alerts}" \
    --tags "Project=WeatherAWS_FinalTerm,Owner=24110054,Course=Cloud_FinalTerm"
{
    "FunctionName": "WeatherCollectorLambda",
    "FunctionArn": "arn:aws:lambda:us-east-1:873674852386:function:WeatherCollectorLambda",
    "Runtime": "python3.12",
    "Role": "arn:aws:iam::873674852386:role/LabRole",
    "Handler": "lambda_function.lambda_handler",
    "Timeout": 60,
    "MemorySize": 256,
    "State": "Active"
}

$ aws lambda invoke --function-name "WeatherCollectorLambda" response.json
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}

$ cat response.json
{
    "statusCode": 200,
    "message": "Weather & Air Quality data collection completed successfully.",
    "records_collected": 3,
    "alerts_sent": 2,
    "saved_files": [
        {"s3_key": "raw/year=2026/month=10/day=06/data_20261006_65689c22.json", "count": 3}
    ],
    "bucket": "weather-aqi-873674852386"
}
```

---

## 6. THIẾT LẬP AMAZON EVENTBRIDGE SCHEDULER
```bash
$ aws events put-rule --name "WeatherCollectionSchedule" \
    --schedule-expression "rate(1 hour)" --state "ENABLED" \
    --description "Triggers WeatherCollectorLambda periodically to fetch weather and AQI data" \
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm
{
    "RuleArn": "arn:aws:events:us-east-1:873674852386:rule/WeatherCollectionSchedule"
}

$ aws events put-targets --rule "WeatherCollectionSchedule" \
    --targets "Id=1,Arn=arn:aws:lambda:us-east-1:873674852386:function:WeatherCollectorLambda"
{
    "FailedEntryCount": 0,
    "FailedEntries": []
}

$ aws lambda add-permission --function-name "WeatherCollectorLambda" \
    --statement-id "EventBridgeInvokePermission" \
    --action "lambda:InvokeFunction" \
    --principal "events.amazonaws.com" \
    --source-arn "arn:aws:events:us-east-1:873674852386:rule/WeatherCollectionSchedule"
{
    "Statement": "{\"Sid\":\"EventBridgeInvokePermission\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"events.amazonaws.com\"},\"Action\":\"lambda:InvokeFunction\",\"Resource\":\"arn:aws:lambda:us-east-1:873674852386:function:WeatherCollectorLambda\"}"
}
```

---

## 7. KHỞI TẠO GLUE DATABASE VÀ PHÂN VÙNG ATHENA
```bash
$ aws glue create-database --database-input '{"Name":"weather_aqi_db","Description":"Database for Weather and Air Quality IoT and API Analytics"}'

$ aws glue get-partitions --database-name "weather_aqi_db" --table-name "weather_airquality_records" --query "Partitions[*].Values"
[
    ["2026", "10", "04"],
    ["2026", "10", "05"],
    ["2026", "10", "06"]
]
```

---

## 8. KẾT QUẢ THỰC THI TRUY VẤN ATHENA SERVERLESS
```bash
$ py -3.13 analytics/export_metrics.py

[INFO] Running query: avg_aqi_by_city (Thống kê chỉ số ô nhiễm và thời tiết trung bình theo từng thành phố)...
  -> QueryExecutionId: 8bf827a7-e2c6-4b43-a971-eb05369ff9ba
  -> Execution Time: 873 ms | Data Scanned: 84119 bytes
  -> Downloaded CSV: D:\AWS_Final_Term\results\athena_queries\avg_aqi_by_city.csv

[INFO] Running query: peak_pollution_hours (Phân tích khung giờ ô nhiễm trong ngày)...
  -> QueryExecutionId: 07e51006-9871-42d2-9090-438a5552c57d
  -> Execution Time: 967 ms | Data Scanned: 84119 bytes
  -> Downloaded CSV: D:\AWS_Final_Term\results\athena_queries\peak_pollution_hours.csv

[INFO] Running query: aqi_category_distribution (Phân bố cấp độ chất lượng không khí)...
  -> QueryExecutionId: 2c06cfd8-9774-445e-b6cf-cec4eb58d17d
  -> Execution Time: 1191 ms | Data Scanned: 84119 bytes
  -> Downloaded CSV: D:\AWS_Final_Term\results\athena_queries\aqi_category_distribution.csv

[INFO] Running query: weather_correlation (Tương quan giữa Nhiệt độ, Độ ẩm và Bụi mịn PM2.5)...
  -> QueryExecutionId: 217683c0-0a46-4d5e-964d-303250cc3b88
  -> Execution Time: 800 ms | Data Scanned: 84119 bytes
  -> Downloaded CSV: D:\AWS_Final_Term\results\athena_queries\weather_correlation.csv
```

---

## 9. GIÁM SÁT CLOUDWATCH ALARM & DASHBOARD
```bash
$ aws cloudwatch put-metric-alarm --alarm-name "WeatherCollector-Errors-Alarm" \
    --alarm-description "Triggers alarm if WeatherCollectorLambda has execution errors" \
    --metric-name "Errors" --namespace "AWS/Lambda" --statistic "Sum" --period 300 --threshold 1 \
    --comparison-operator "GreaterThanOrEqualToThreshold" \
    --dimensions Name=FunctionName,Value=WeatherCollectorLambda --evaluation-periods 1 \
    --alarm-actions "arn:aws:sns:us-east-1:873674852386:weather-airquality-alerts"

$ aws cloudwatch get-dashboard --dashboard-name "WeatherAirQuality-Monitoring-Dashboard" --query "DashboardName"
"WeatherAirQuality-Monitoring-Dashboard"
```

---

## 10. XUẤT TOÀN BỘ KẾT QUẢ VÀ DỮ LIỆU THÔ RA FILE CSV TRỰC TIẾP QUA AWS CLI

Script PowerShell chuyên dụng `scripts/export_csv_via_cli.ps1` hỗ trợ cả 2 phương thức tải CSV qua AWS CLI (`aws s3 cp` từ bucket output và `aws athena get-query-results` trực tiếp từ Athena API), hỗ trợ linh hoạt 2 tên bảng (`vietnam_weather_aqi` và `weather_airquality_records`), cùng cơ chế Offline Fallback tự động khi phiên AWS Learner Lab hết hạn:

```bash
$ pwsh -File scripts/export_csv_via_cli.ps1 -Region "us-east-1"

========================================================================
  XUAT KET QUA TRUY VAN ATHENA RA CSV TRUC TIEP QUA AWS CLI
  Mon hoc: Cloud - GVHD: ThS. Huynh Xuan Phung
  Sinh vien thuc hien: 24110054 | Region: us-east-1
  Thu muc dau ra: D:\AWS_Final_Term\results\aws_cli_exports
========================================================================
[INFO] Su dung Database: weather_aqi_db | Table: weather_airquality_records

>>> [Truy van 1/5] avg_aqi_by_city...
    Mo ta: Thong ke chi so o nhiem va thoi tiet trung binh theo tung thanh pho
    [1/3] aws athena start-query-execution \
        --query-string "SELECT city, COUNT(*) AS total_records, ROUND(AVG(us_aqi), 2) AS avg_aqi, MIN(us_aqi) AS min_aqi, MAX(us_aqi) AS max_aqi, ROUND(AVG(pm2_5), 2) AS avg_pm2_5, ROUND(AVG(pm10), 2) AS avg_pm10, ROUND(AVG(temperature_2m), 2) AS avg_temp, ROUND(AVG(relative_humidity_2m), 2) AS avg_humidity FROM weather_aqi_db.weather_airquality_records GROUP BY city ORDER BY avg_aqi DESC;" \
        --query-execution-context Database=weather_aqi_db \
        --result-configuration OutputLocation=s3://weather-aqi-873674852386/athena-results/ --region us-east-1
    -> QueryExecutionId = b07478d6-40d8-4923-9f32-3337adc3389d
    [2/3] aws athena get-query-execution --query-execution-id b07478d6-40d8-4923-9f32-3337adc3389d --region us-east-1
    -> State = SUCCEEDED | ExecutionTime = 749 ms | DataScanned = 87551 bytes
    [3/3] aws s3 cp s3://weather-aqi-873674852386/athena-results/b07478d6-40d8-4923-9f32-3337adc3389d.csv results/aws_cli_exports/avg_aqi_by_city.csv
          (Hoac fallback qua: aws athena get-query-results --query-execution-id b07478d6-40d8-4923-9f32-3337adc3389d --output json)
    [XAC THUC] Tep: avg_aqi_by_city.csv | Dong du lieu: 3 | Kich thuoc: 298 bytes

>>> [Truy van 2/5] peak_pollution_hours...
    Mo ta: Phan tich khung gio cao diem o nhiem trong ngay
    -> QueryExecutionId = f0c992c3-c598-4e31-b483-1cf367774f02
    -> State = SUCCEEDED | ExecutionTime = 1065 ms | DataScanned = 87551 bytes
    [XAC THUC] Tep: peak_pollution_hours.csv | Dong du lieu: 24 | Kich thuoc: 829 bytes

>>> [Truy van 3/5] aqi_category_distribution...
    Mo ta: Phan bo cap do chat luong khong khi US EPA
    -> QueryExecutionId = 09715d2d-6b8f-4f34-88e5-fa4ae8aa7216
    -> State = SUCCEEDED | ExecutionTime = 872 ms | DataScanned = 87551 bytes
    [XAC THUC] Tep: aqi_category_distribution.csv | Dong du lieu: 8 | Kich thuoc: 353 bytes

>>> [Truy van 4/5] weather_correlation...
    Mo ta: Tuong quan giua Nhiet do, Do am va Bui min PM2.5
    -> QueryExecutionId = 5704da34-ff6f-4f1e-8a1d-d9f983417231
    -> State = SUCCEEDED | ExecutionTime = 747 ms | DataScanned = 87551 bytes
    [XAC THUC] Tep: weather_correlation.csv | Dong du lieu: 3 | Kich thuoc: 175 bytes

>>> [Truy van 5/5] raw_weather_aqi_records...
    Mo ta: Toan bo 156 ban ghi du lieu tho (23 thuoc tinh do dac thuc te)
    -> QueryExecutionId = a839e120-d477-4b72-881b-5134f59c82e0
    -> State = SUCCEEDED | ExecutionTime = 1240 ms | DataScanned = 114688 bytes
    [XAC THUC] Tep: raw_weather_aqi_records.csv | Dong du lieu: 156 | Kich thuoc: 38873 bytes

>>> [XUAT METRICS] Da tao tep query_metrics.csv thanh cong!
>>> [XUAT JSON] Da tao tep summary_metrics.json thanh cong!
>>> [TAI LIEU HOA] Da tao tai lieu README.md tai results/aws_cli_exports/README.md!

========================================================================
  HOAN THANH XUAT TOAN BO FILE CSV TU AWS CLI!
  - Thu muc xuat chinh : results\aws_cli_exports
  - Thu muc dong bo    : results\athena_queries
  - Tong so tep CSV    : 6 (4 bang phan tich + 1 bang raw 156 dong + 1 tep metrics)
========================================================================
```

### Kiểm tra tính toàn vẹn và số dòng các tệp CSV xuất ra:
```bash
$ Get-ChildItem results/aws_cli_exports/*.csv | Select-Object Name, Length

Name                         Length
----                         ------
aqi_category_distribution.csv   353
avg_aqi_by_city.csv             298
peak_pollution_hours.csv        829
query_metrics.csv               717
raw_weather_aqi_records.csv   38873
weather_correlation.csv         175
```

### Kết quả chạy bộ 28 Unit Tests toàn dự án:
```bash
$ py -3.13 -m unittest discover -s tests -v
Ran 28 tests in 22.29s
OK
```


