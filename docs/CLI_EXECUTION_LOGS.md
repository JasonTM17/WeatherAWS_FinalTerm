# MINH CHỨNG THỰC THI AWS CLI THỰC TẾ (CLI EXECUTION EVIDENCE)

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
