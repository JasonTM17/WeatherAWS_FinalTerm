# MINH CHỨNG THỰC THI AWS CLI THỰC TẾ (CLI EXECUTION EVIDENCE)

> **Môn học:** Cloud - Đợt 1 - 2026-2027 | **GVHD:** ThS. Huỳnh Xuân Phụng  
> **Sinh viên:** Trần Minh Jason - MSSV: `24110054`  
> **AWS Account ID:** `134987931868` | **Region:** `us-east-1`  
> **Thời gian thực thi:** 07/10/2026 (UTC+7)  

---

## 1. XÁC THỰC DANH TÍNH TÀI KHOẢN (CALLER IDENTITY)
```bash
$ aws sts get-caller-identity
{
    "UserId": "AROAR63PIMDONYKCGJT7O:user5434332=24110051@student.hcmute.edu.vn",
    "Account": "134987931868",
    "Arn": "arn:aws:sts::134987931868:assumed-role/voclabs/user5434332=24110051@student.hcmute.edu.vn"
}
```

---

## 2. KHỞI TẠO VÀ GẮN TAG AMAZON S3 BUCKET
```bash
$ aws s3api create-bucket --bucket weather-aqi-134987931868 --region us-east-1
{
    "Location": "/weather-aqi-134987931868",
    "BucketArn": "arn:aws:s3:::weather-aqi-134987931868"
}

$ aws s3api get-bucket-tagging --bucket weather-aqi-134987931868
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
    --secret-string '{"api_provider":"open-meteo","api_key":"sec_demo_weather_api_key_134987931868","aqi_threshold_pm25":35.5,"locations":[{"city":"HoChiMinh","lat":10.8231,"lon":106.6297},{"city":"HaNoi","lat":21.0285,"lon":105.8542},{"city":"DaNang","lat":16.0544,"lon":108.2022}],"aqi_threshold_pm10":50.0,"aqi_threshold_us_aqi":100}' \
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm

{
    "ARN": "arn:aws:secretsmanager:us-east-1:134987931868:secret:weather/api_config-E8lYcr",
    "Name": "weather/api_config",
    "VersionId": "8b851c2f-bdc9-4a81-85c2-1f401c01546b"
}
```

---

## 4. KHỞI TẠO AMAZON SNS TOPIC & SUBSCRIPTION
```bash
$ aws sns create-topic --name weather-airquality-alerts \
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm
{
    "TopicArn": "arn:aws:sns:us-east-1:134987931868:weather-airquality-alerts"
}

$ aws sns subscribe --topic-arn "arn:aws:sns:us-east-1:134987931868:weather-airquality-alerts" \
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
    --role "arn:aws:iam::134987931868:role/LabRole" \
    --handler "lambda_function.lambda_handler" \
    --zip-file "fileb://d:/AWS_Final_Term/lambda_package.zip" \
    --timeout 60 --memory-size 256 \
    --environment "Variables={S3_BUCKET_NAME=weather-aqi-134987931868,SECRET_NAME=weather/api_config,SNS_TOPIC_ARN=arn:aws:sns:us-east-1:134987931868:weather-airquality-alerts}" \
    --tags "Project=WeatherAWS_FinalTerm,Owner=24110054,Course=Cloud_FinalTerm"
{
    "FunctionName": "WeatherCollectorLambda",
    "FunctionArn": "arn:aws:lambda:us-east-1:134987931868:function:WeatherCollectorLambda",
    "Runtime": "python3.12",
    "Role": "arn:aws:iam::134987931868:role/LabRole",
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
        {"s3_key": "raw/year=2026/month=10/day=07/data_20261007_4f8a69eb.json", "count": 3}
    ],
    "bucket": "weather-aqi-134987931868"
}
```

---

## 6. THIẾT LẬP AMAZON EVENTBRIDGE SCHEDULER
```bash
$ aws events put-rule --name "WeatherCollectionHourlyRule" \
    --schedule-expression "rate(1 hour)" --state "ENABLED" \
    --description "Triggers WeatherCollectorLambda periodically to fetch weather and AQI data" \
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm
{
    "RuleArn": "arn:aws:events:us-east-1:134987931868:rule/WeatherCollectionHourlyRule"
}

$ aws events put-targets --rule "WeatherCollectionHourlyRule" \
    --targets "Id=1,Arn=arn:aws:lambda:us-east-1:134987931868:function:WeatherCollectorLambda"
{
    "FailedEntryCount": 0,
    "FailedEntries": []
}

$ aws lambda add-permission --function-name "WeatherCollectorLambda" \
    --statement-id "EventBridgeInvokePermission_WeatherCollectionHourlyRule" \
    --action "lambda:InvokeFunction" \
    --principal "events.amazonaws.com" \
    --source-arn "arn:aws:events:us-east-1:134987931868:rule/WeatherCollectionHourlyRule"
{
    "Statement": "{\"Sid\":\"EventBridgeInvokePermission_WeatherCollectionHourlyRule\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"events.amazonaws.com\"},\"Action\":\"lambda:InvokeFunction\",\"Resource\":\"arn:aws:lambda:us-east-1:134987931868:function:WeatherCollectorLambda\"}"
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
$ pwsh -File scripts/export_csv_via_cli.ps1 -Region "us-east-1"

[INFO] Running query: avg_aqi_by_city (Thống kê chỉ số ô nhiễm và thời tiết trung bình theo từng thành phố)...
  -> QueryExecutionId: 57e9d139-1a73-422d-adb4-e0b006f740c6
  -> Execution Time: 983 ms | Data Scanned: 87250 bytes
  -> Downloaded CSV: D:\AWS_Final_Term\results\aws_cli_exports\avg_aqi_by_city.csv

[INFO] Running query: peak_pollution_hours (Phân tích khung giờ ô nhiễm trong ngày)...
  -> QueryExecutionId: f77e7656-bb51-4cb1-9ba8-117bce879d57
  -> Execution Time: 1171 ms | Data Scanned: 87250 bytes
  -> Downloaded CSV: D:\AWS_Final_Term\results\aws_cli_exports\peak_pollution_hours.csv

[INFO] Running query: aqi_category_distribution (Phân bố cấp độ chất lượng không khí)...
  -> QueryExecutionId: f1e2d2a8-dc47-4afb-98e6-30f4de8b096f
  -> Execution Time: 773 ms | Data Scanned: 87250 bytes
  -> Downloaded CSV: D:\AWS_Final_Term\results\aws_cli_exports\aqi_category_distribution.csv

[INFO] Running query: weather_correlation (Tương quan giữa Nhiệt độ, Độ ẩm và Bụi mịn PM2.5)...
  -> QueryExecutionId: 25272532-19a7-405f-b803-91244e1c946a
  -> Execution Time: 791 ms | Data Scanned: 87250 bytes
  -> Downloaded CSV: D:\AWS_Final_Term\results\aws_cli_exports\weather_correlation.csv

[INFO] Running query: raw_weather_aqi_records (Toàn bộ 156 bản ghi dữ liệu thô)...
  -> QueryExecutionId: c98f6f44-d9f2-4621-9c17-59578c4c730e
  -> Execution Time: 742 ms | Data Scanned: 87250 bytes
  -> Downloaded CSV: D:\AWS_Final_Term\results\aws_cli_exports\raw_weather_aqi_records.csv
```

---

## 9. GIÁM SÁT CLOUDWATCH ALARM & DASHBOARD
```bash
$ aws cloudwatch put-metric-alarm --alarm-name "WeatherCollector-Errors-Alarm" \
    --alarm-description "Triggers alarm if WeatherCollectorLambda has execution errors" \
    --metric-name "Errors" --namespace "AWS/Lambda" --statistic "Sum" --period 300 --threshold 1 \
    --comparison-operator "GreaterThanOrEqualToThreshold" \
    --dimensions Name=FunctionName,Value=WeatherCollectorLambda --evaluation-periods 1 \
    --alarm-actions "arn:aws:sns:us-east-1:134987931868:weather-airquality-alerts"

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
[OK] AWS CLI xac thuc thanh cong!
     Account ID: 134987931868
     User ARN  : arn:aws:sts::134987931868:assumed-role/voclabs/user5434332=24110051@student.hcmute.edu.vn
[INFO] Su dung Database: weather_aqi_db | Table: vietnam_weather_aqi

>>> [Truy van 1/5] avg_aqi_by_city...
    Mo ta: Thong ke chi so o nhiem va thoi tiet trung binh theo tung thanh pho
    [1/3] aws athena start-query-execution...
          QueryExecutionId = 57e9d139-1a73-422d-adb4-e0b006f740c6
    [2/3] aws athena get-query-execution (Dang doi ket qua)...
          Trang thai = SUCCEEDED | Thoi gian = 983 ms | Da quet = 87250 bytes
    [3/3] aws s3 cp ket qua CSV tu S3 ve may cuc bo...
          [S3 CP OK] Da tai tu s3://weather-aqi-134987931868/athena-results/57e9d139-1a73-422d-adb4-e0b006f740c6.csv -> D:\AWS_Final_Term\results\aws_cli_exports\avg_aqi_by_city.csv
    [XAC THUC] Tep: avg_aqi_by_city.csv | Dong du lieu: 3 | Kich thuoc: 299 bytes

>>> [Truy van 2/5] peak_pollution_hours...
    Mo ta: Phan tich khung gio cao diem o nhiem trong ngay
    [1/3] aws athena start-query-execution...
          QueryExecutionId = f77e7656-bb51-4cb1-9ba8-117bce879d57
    [2/3] aws athena get-query-execution (Dang doi ket qua)...
          Trang thai = SUCCEEDED | Thoi gian = 1171 ms | Da quet = 87250 bytes
    [3/3] aws s3 cp ket qua CSV tu S3 ve may cuc bo...
          [S3 CP OK] Da tai tu s3://weather-aqi-134987931868/athena-results/f77e7656-bb51-4cb1-9ba8-117bce879d57.csv -> D:\AWS_Final_Term\results\aws_cli_exports\peak_pollution_hours.csv
    [XAC THUC] Tep: peak_pollution_hours.csv | Dong du lieu: 24 | Kich thuoc: 828 bytes

>>> [Truy van 3/5] aqi_category_distribution...
    Mo ta: Phan bo cap do chat luong khong khi US EPA
    [1/3] aws athena start-query-execution...
          QueryExecutionId = f1e2d2a8-dc47-4afb-98e6-30f4de8b096f
    [2/3] aws athena get-query-execution (Dang doi ket qua)...
          Trang thai = SUCCEEDED | Thoi gian = 773 ms | Da quet = 87250 bytes
    [3/3] aws s3 cp ket qua CSV tu S3 ve may cuc bo...
          [S3 CP OK] Da tai tu s3://weather-aqi-134987931868/athena-results/f1e2d2a8-dc47-4afb-98e6-30f4de8b096f.csv -> D:\AWS_Final_Term\results\aws_cli_exports\aqi_category_distribution.csv
    [XAC THUC] Tep: aqi_category_distribution.csv | Dong du lieu: 8 | Kich thuoc: 354 bytes

>>> [Truy van 4/5] weather_correlation...
    Mo ta: Tuong quan giua Nhiet do, Do am va Bui min PM2.5
    [1/3] aws athena start-query-execution...
          QueryExecutionId = 25272532-19a7-405f-b803-91244e1c946a
    [2/3] aws athena get-query-execution (Dang doi ket qua)...
          Trang thai = SUCCEEDED | Thoi gian = 791 ms | Da quet = 87250 bytes
    [3/3] aws s3 cp ket qua CSV tu S3 ve may cuc bo...
          [S3 CP OK] Da tai tu s3://weather-aqi-134987931868/athena-results/25272532-19a7-405f-b803-91244e1c946a.csv -> D:\AWS_Final_Term\results\aws_cli_exports\weather_correlation.csv
    [XAC THUC] Tep: weather_correlation.csv | Dong du lieu: 3 | Kich thuoc: 177 bytes

>>> [Truy van 5/5] raw_weather_aqi_records...
    Mo ta: Toan bo 156 ban ghi du lieu tho (23 thuoc tinh do dac thuc te)
    [1/3] aws athena start-query-execution...
          QueryExecutionId = c98f6f44-d9f2-4621-9c17-59578c4c730e
    [2/3] aws athena get-query-execution (Dang doi ket qua)...
          Trang thai = SUCCEEDED | Thoi gian = 742 ms | Da quet = 87250 bytes
    [3/3] aws s3 cp ket qua CSV tu S3 ve may cuc bo...
          [S3 CP OK] Da tai tu s3://weather-aqi-134987931868/athena-results/c98f6f44-d9f2-4621-9c17-59578c4c730e.csv -> D:\AWS_Final_Term\results\aws_cli_exports\raw_weather_aqi_records.csv
    [XAC THUC] Tep: raw_weather_aqi_records.csv | Dong du lieu: 156 | Kich thuoc: 38716 bytes

>>> [XUAT METRICS] Da tao tep query_metrics.csv thanh cong tai D:\AWS_Final_Term\results\aws_cli_exports\query_metrics.csv!
>>> [XUAT JSON] Da tao tep summary_metrics.json thanh cong!
>>> [TAI LIEU HOA] Da tao tai lieu README.md tai D:\AWS_Final_Term\results\aws_cli_exports\README.md!

>>> [DONG GOI] Cap nhat tep nen nop bai docs/Bao_cao_tuan_1_CSV_Nhom_05.zip...
Packaged 4 saved Athena results, query metrics, and README: D:\AWS_Final_Term\docs\Bao_cao_tuan_1_CSV_Nhom_05.zip

========================================================================
  HOAN THANH XUAT TOAN BO FILE CSV TU AWS CLI TRONG 55,5 GIAY!
  - Thu muc xuat chinh : D:\AWS_Final_Term\results\aws_cli_exports
  - Thu muc dong bo    : D:\AWS_Final_Term\results\athena_queries
  - Tong so tep CSV    : 6 (4 bang phan tich + 1 bang raw 156 dong + 1 tep metrics)
========================================================================
```

### Kiểm tra tính toàn vẹn và số dòng các tệp CSV xuất ra:
```bash
$ Get-ChildItem results/aws_cli_exports/*.csv | Select-Object Name, Length

Name                         Length
----                         ------
aqi_category_distribution.csv   354
avg_aqi_by_city.csv             299
peak_pollution_hours.csv        828
query_metrics.csv               678
raw_weather_aqi_records.csv   38716
weather_correlation.csv         177
```

### Kết quả chạy bộ 28 Unit Tests toàn dự án:
```bash
$ py -3.13 -m unittest discover -s tests -v
Ran 28 tests in 57.41s
OK
```
