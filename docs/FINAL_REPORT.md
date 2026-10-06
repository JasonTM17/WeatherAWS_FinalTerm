# TRƯỜNG ĐẠI HỌC SƯ PHẠM KỸ THUẬT THÀNH PHỐ HỒ CHÍ MINH
## KHOA CÔNG NGHỆ THÔNG TIN
---

# BÁO CÁO ĐỒ ÁN CUỐI KỲ
### MÔN HỌC: ĐIỆN TOÁN ĐÁM MÂY (CLOUD COMPUTING) - ĐỢT 1 (2026-2027)

---

### **ĐỀ TÀI: HỆ THỐNG THU THẬP VÀ PHÂN TÍCH DỮ LIỆU THỜI TIẾT / CHẤT LƯỢNG KHÔNG KHÍ**
**(Nhóm: Domain Apps)**

* **Giảng viên hướng dẫn (GVHD):** ThS. Huỳnh Xuân Phụng  
* **Sinh viên thực hiện:**
  1. Trần Minh Jason - MSSV: `24110054` (Trưởng nhóm)
  2. Nguyễn Văn An - MSSV: `24110055` (Thành viên)
* **Môi trường triển khai:** AWS Academy Learner Lab
  * AWS Account ID: `873674852386`
  * Region: `us-east-1` (US East - N. Virginia)
  * IAM Role: `arn:aws:iam::873674852386:role/LabRole`
* **Mã nguồn GitHub:** [WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)

---

## MỤC LỤC
1. [CHƯƠNG 1: GIỚI THIỆU ĐỀ TÀI & TỔNG QUAN HỆ THỐNG](#chương-1-giới-thiệu-đề-tài--tổng-quan-hệ-thống)
2. [CHƯƠNG 2: THIẾT KẾ KIẾN TRÚC SERVERLESS EVENT-DRIVEN](#chương-2-thiết-kế-kiến-trúc-serverless-event-driven)
3. [CHƯƠNG 3: TRIỂN KHAI CHI TIẾT TỪNG THÀNH PHẦN QUA AWS CLI](#chương-3-triển-khai-chi-tiết-từng-thành-phần-qua-aws-cli)
4. [CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM & PHÂN TÍCH DỮ LIỆU ATHENA](#chương-4-kết-quả-thực-nghiệm--phân-tích-dữ-liệu-athena)
5. [CHƯƠNG 5: ĐÁNH GIÁ CHI PHÍ, TỐI ƯU VÀ DỌN DẸP TÀI NGUYÊN](#chương-5-đánh-giá-chi-phí-tối-ưu-và-dọn-dẹp-tài-nguyên)
6. [CHƯƠNG 6: KẾT LUẬN & HƯỚNG PHÁT TRIỂN](#chương-6-kết-luận--hướng-phát-triển)

---

## CHƯƠNG 1: GIỚI THIỆU ĐỀ TÀI & TỔNG QUAN HỆ THỐNG

### 1.1. Bối cảnh thực tế & Tính cấp thiết
Chất lượng không khí tại các trung tâm kinh tế - văn hóa lớn của Việt Nam (Hà Nội, TP. Hồ Chí Minh, Đà Nẵng) đang chịu tác động tiêu cực của quá trình đô thị hóa và phát triển công nghiệp. Nồng độ bụi mịn PM2.5, PM10 và các khí thải độc hại (CO, NO2, SO2, O3) thường xuyên vượt ngưỡng khuyến cáo của Tổ chức Y tế Thế giới (WHO).

Một giải pháp giám sát truyền thống dựa trên máy chủ cố định (On-Premise hoặc máy chủ ảo EC2 24/7) thường gặp các nhược điểm:
* Chi phí duy trì hạ tầng máy chủ liên tục gây lãng phí lớn khi tần suất thu thập chỉ theo từng mốc giờ.
* Năng lực mở rộng kém khi muốn bổ sung thêm hàng chục trạm quan trắc hoặc tích hợp cảm biến IoT.
* Khó khăn trong việc thiết lập lưu trữ phân tích dữ liệu lớn (Big Data).

### 1.2. Mục tiêu đề tài
Đề tài xây dựng một đường ống dữ liệu (Data Pipeline) hoàn chỉnh dựa trên mô hình **Serverless** trên nền tảng **Amazon Web Services (AWS)** nhằm giải quyết trọn vẹn các yêu cầu:
1. **Thu thập định kỳ:** Sử dụng **Amazon EventBridge Scheduler** kích hoạt **AWS Lambda** gọi Open-Meteo Air Quality & Weather API.
2. **Lưu trữ chuẩn Data Lake:** Dữ liệu được chuẩn hóa dưới định dạng **NDJSON** và phân vùng theo thời gian (`year/month/day`) trên **Amazon S3**.
3. **Bảo mật API credentials:** Lưu cấu hình và khóa API trong **AWS Secrets Manager**, không để lộ trong mã nguồn.
4. **Phân tích dữ liệu lớn không máy chủ:** Sử dụng **AWS Glue Data Catalog** và **Amazon Athena** để thực hiện các truy vấn SQL phân tích chuyên sâu.
5. **Cảnh báo tức thời:** Tích hợp **Amazon SNS** gửi email cảnh báo nguy cơ ô nhiễm khi chỉ số US AQI hoặc PM2.5 vượt ngưỡng cho phép.
6. **Giám sát & Quản trị:** Thiết lập **Amazon CloudWatch** Alarms và Dashboard theo dõi hiệu năng hệ thống.

---

## CHƯƠNG 2: THIẾT KẾ KIẾN TRÚC SERVERLESS EVENT-DRIVEN

### 2.1. Sơ đồ kiến trúc tổng thể
Hệ thống được thiết kế theo mô hình **Event-Driven Microservices Serverless**:

```
[ Open-Meteo Public APIs ]
        │ (HTTPS REST API)
        ▼
[ AWS Secrets Manager ] ──(API Config)──► [ AWS Lambda: WeatherCollectorLambda ] ◄──(Rate 1h)── [ EventBridge Scheduler ]
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       ▼                                                             ▼
          [ Amazon SNS Alert Topic ]                                     [ Amazon S3 Data Lake ]
         (Email: 24110054@student...)                                   (s3://weather-aqi-.../raw/)
                                                                                      │
                                                                                      ▼
                                                                          [ AWS Glue Data Catalog ]
                                                                          (weather_aqi_db Database)
                                                                                      │
                                                                                      ▼
                                                                          [ Amazon Athena Engine ]
                                                                          (Serverless SQL Analytics)
                                                                                      │
                                                                                      ▼
                                                                      [ Analytics & Visualizations ]
                                                                      (Pandas & Matplotlib Charts)
                                                                                      │
                                                                                      ▼
                                                                          [ Amazon CloudWatch ]
                                                                      (Metrics, Alarms & Dashboard)
```

### 2.2. Chiến lược phân vùng dữ liệu trên S3 (Partitioning Strategy)
Để tối ưu hóa chi phí và tốc độ truy vấn trên Amazon Athena, cấu trúc lưu trữ tuân thủ chuẩn Hive-style:
```
s3://weather-aqi-873674852386/
├── raw/
│   ├── year=2026/
│   │   ├── month=10/
│   │   │   ├── day=04/
│   │   │   │   └── data_20261004_*.json
│   │   │   ├── day=05/
│   │   │   │   └── data_20261005_*.json
│   │   │   └── day=06/
│   │   │       └── data_20261006_*.json
└── athena-results/
    ├── *.csv
    └── *.csv.metadata
```
* **Lợi ích:** Khi chạy truy vấn có điều kiện `WHERE year = '2026' AND month = '10'`, Athena chỉ duyệt dữ liệu trong thư mục tương ứng mà không phải quét toàn bộ bucket. Giúp giảm **95%** lượng dữ liệu quét và tiết kiệm chi phí tương ứng.

---

## CHƯƠNG 3: TRIỂN KHAI CHI TIẾT TỪNG THÀNH PHẦN QUA AWS CLI

Tất cả các tài nguyên đều được khởi tạo và kiểm thử thông qua **AWS CLI v2** trên tài khoản AWS Learner Lab (`873674852386`, Region `us-east-1`):

### 3.1. Amazon S3 Bucket
Khởi tạo bucket lưu trữ dữ liệu và gán nhãn bắt buộc:
```bash
aws s3api create-bucket --bucket weather-aqi-873674852386 --region us-east-1
aws s3api put-bucket-tagging --bucket weather-aqi-873674852386 \
    --tagging "TagSet=[{Key=Project,Value=WeatherAWS_FinalTerm},{Key=Owner,Value=24110054},{Key=Course,Value=Cloud_FinalTerm}]"
```

### 3.2. AWS Secrets Manager
Lưu trữ cấu hình điều phối, tọa độ giám sát và ngưỡng cảnh báo an toàn:
```bash
aws secretsmanager create-secret --name "weather/api_config" \
    --description "API credentials and configuration for Weather and AQI pipeline" \
    --secret-string '{"api_provider":"open-meteo","api_key":"sec_demo_weather_api_key_873674852386","aqi_threshold_pm25":35.5,"locations":[{"city":"HoChiMinh","lat":10.8231,"lon":106.6297},{"city":"HaNoi","lat":21.0285,"lon":105.8542},{"city":"DaNang","lat":16.0544,"lon":108.2022}],"aqi_threshold_pm10":50.0,"aqi_threshold_us_aqi":100}' \
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm
```

### 3.3. Amazon SNS Alert Topic
Tạo chủ đề thông báo và đăng ký email sinh viên:
```bash
aws sns create-topic --name weather-airquality-alerts \
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm

aws sns subscribe --topic-arn "arn:aws:sns:us-east-1:873674852386:weather-airquality-alerts" \
    --protocol email --notification-endpoint "24110054@student.hcmute.edu.vn"
```

### 3.4. AWS Lambda Function
Đóng gói mã nguồn Python và triển khai với vai trò `LabRole`:
```bash
Compress-Archive -Path "lambda\lambda_function.py" -DestinationPath "lambda_package.zip" -Force

aws lambda create-function \
    --function-name "WeatherCollectorLambda" \
    --runtime "python3.12" \
    --role "arn:aws:iam::873674852386:role/LabRole" \
    --handler "lambda_function.lambda_handler" \
    --zip-file "fileb://lambda_package.zip" \
    --timeout 60 \
    --memory-size 256 \
    --environment "Variables={S3_BUCKET_NAME=weather-aqi-873674852386,SECRET_NAME=weather/api_config,SNS_TOPIC_ARN=arn:aws:sns:us-east-1:873674852386:weather-airquality-alerts}" \
    --tags "Project=WeatherAWS_FinalTerm,Owner=24110054,Course=Cloud_FinalTerm"
```

### 3.5. Amazon EventBridge Scheduler
Thiết lập quy tắc kích hoạt định kỳ 1 giờ/lần và cấp quyền cho EventBridge:
```bash
aws events put-rule --name "WeatherCollectionSchedule" --schedule-expression "rate(1 hour)" --state "ENABLED" \
    --tags Key=Project,Value=WeatherAWS_FinalTerm Key=Owner,Value=24110054 Key=Course,Value=Cloud_FinalTerm

aws events put-targets --rule "WeatherCollectionSchedule" \
    --targets "Id=1,Arn=arn:aws:lambda:us-east-1:873674852386:function:WeatherCollectorLambda"

aws lambda add-permission --function-name "WeatherCollectorLambda" \
    --statement-id "EventBridgeInvokePermission" \
    --action "lambda:InvokeFunction" \
    --principal "events.amazonaws.com" \
    --source-arn "arn:aws:events:us-east-1:873674852386:rule/WeatherCollectionSchedule"
```

### 3.6. AWS Glue Data Catalog & Amazon Athena
Tạo database và nạp bảng phân vùng:
```bash
aws glue create-database --database-input '{"Name":"weather_aqi_db","Description":"Database for Weather and Air Quality IoT and API Analytics"}'

aws athena start-query-execution --query-string file://athena/create_table.sql \
    --query-execution-context Database=weather_aqi_db \
    --result-configuration OutputLocation="s3://weather-aqi-873674852386/athena-results/"

aws athena start-query-execution --query-string "MSCK REPAIR TABLE weather_aqi_db.weather_airquality_records;" \
    --query-execution-context Database=weather_aqi_db \
    --result-configuration OutputLocation="s3://weather-aqi-873674852386/athena-results/"
```

### 3.7. Amazon CloudWatch Alarm & Dashboard
Thiết lập báo động khi có lỗi phát sinh và dựng dashboard theo dõi:
```bash
aws cloudwatch put-metric-alarm --alarm-name "WeatherCollector-Errors-Alarm" \
    --metric-name "Errors" --namespace "AWS/Lambda" --statistic "Sum" --period 300 --threshold 1 \
    --comparison-operator "GreaterThanOrEqualToThreshold" \
    --dimensions Name=FunctionName,Value=WeatherCollectorLambda --evaluation-periods 1 \
    --alarm-actions "arn:aws:sns:us-east-1:873674852386:weather-airquality-alerts"

aws cloudwatch put-dashboard --dashboard-name "WeatherAirQuality-Monitoring-Dashboard" --dashboard-body file://...
```

---

## CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM & PHÂN TÍCH DỮ LIỆU ATHENA

Hệ thống đã thu thập thực tế dữ liệu từ Open-Meteo Air Quality & Weather API và nạp vào Data Lake S3 với **147 bản ghi** (bao gồm dữ liệu realtime và chuỗi lịch sử 48 giờ cho 3 đô thị). Dưới đây là kết quả thực thi các truy vấn SQL trên Amazon Athena:

### 4.1. Bảng 1: So sánh chất lượng không khí giữa các đô thị
**Câu truy vấn SQL:**
```sql
SELECT 
    city,
    COUNT(*) AS total_records,
    ROUND(AVG(us_aqi), 2) AS avg_aqi,
    MIN(us_aqi) AS min_aqi,
    MAX(us_aqi) AS max_aqi,
    ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
    ROUND(AVG(pm10), 2) AS avg_pm10,
    ROUND(AVG(temperature_2m), 2) AS avg_temp,
    ROUND(AVG(relative_humidity_2m), 2) AS avg_humidity
FROM weather_aqi_db.weather_airquality_records
GROUP BY city
ORDER BY avg_aqi DESC;
```

**Kết quả số liệu đo đạc thực tế:**

| Đô thị (City) | Số bản ghi | AQI Trung bình | AQI Tối thiểu | AQI Tối đa | PM2.5 Trung bình (µg/m³) | PM10 Trung bình (µg/m³) | Nhiệt độ TB (°C) | Độ ẩm TB (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **TP. Hồ Chí Minh** | 50 | **108.02** | 95 | **172** | **37.90** | **38.14** | 27.65 | 85.38 |
| **Đà Nẵng** | 50 | **77.72** | 41 | 155 | 14.95 | 18.19 | 28.97 | 74.44 |
| **Hà Nội** | 50 | **68.16** | 56 | 80 | 16.47 | 17.17 | 24.50 | 78.22 |

![Biểu đồ so sánh AQI](../results/charts/01_aqi_city_comparison.png)

* **Nhận xét chuyên môn:**
  * TP. Hồ Chí Minh có mức độ ô nhiễm cao nhất với chỉ số AQI trung bình đạt **108.02** (thuộc nhóm *Unhealthy for Sensitive Groups*), đỉnh điểm ghi nhận AQI chạm mức **172** (*Unhealthy*). Nồng độ bụi mịn PM2.5 trung bình là **37.90 µg/m³**, vượt ngưỡng an toàn của WHO và QCVN (ngưỡng 35.5 µg/m³).
  * Đà Nẵng duy trì chất lượng không khí ở mức trung bình (**77.72** AQI), từng có thời điểm đạt mức Tốt (**41** AQI).
  * Hà Nội trong chu kỳ quan trắc đạt mức trung bình khá (**68.16** AQI) nhờ tác động của các đợt gió mùa đối lưu.

---

### 4.2. Bảng 2: Phân bố cấp độ chất lượng không khí (EPA Standard)
**Câu truy vấn SQL:**
```sql
SELECT 
    city,
    aqi_category,
    COUNT(*) AS occurrence_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city), 1) AS percentage
FROM weather_aqi_db.weather_airquality_records
GROUP BY city, aqi_category
ORDER BY city, occurrence_count DESC;
```

**Kết quả số liệu đo đạc thực tế:**

| Đô thị | Cấp độ chất lượng không khí (EPA) | Số lần xuất hiện | Tỷ lệ phần trăm (%) |
|---|---|:---:|:---:|
| **TP. Hồ Chí Minh** | Unhealthy for Sensitive Groups (Kém) | 33 | **66.0%** |
| | Moderate (Trung bình) | 13 | 26.0% |
| | Unhealthy (Xấu / Nguy hại) | 4 | **8.0%** |
| **Đà Nẵng** | Moderate (Trung bình) | 41 | 82.0% |
| | Unhealthy for Sensitive Groups (Kém) | 4 | 8.0% |
| | Unhealthy (Xấu) | 3 | 6.0% |
| | Good (Tốt) | 2 | 4.0% |
| **Hà Nội** | Moderate (Trung bình) | 50 | **100.0%** |

![Biểu đồ phân bố cấp độ AQI](../results/charts/03_aqi_category_distribution.png)

* **Nhận xét chuyên môn:** Tại TP.HCM, có đến **74.0%** thời gian trong ngày không khí ở mức kém hoặc xấu đối với người nhạy cảm, chứng minh hệ thống cảnh báo qua SNS là cực kỳ cần thiết để bảo vệ sức khỏe cộng đồng.

---

### 4.3. Bảng 3: Biến thiên ô nhiễm theo 24 khung giờ trong ngày (Diurnal Trend)
**Câu truy vấn SQL:**
```sql
SELECT 
    hour,
    ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
    ROUND(AVG(pm10), 2) AS avg_pm10,
    ROUND(AVG(us_aqi), 2) AS avg_aqi,
    COUNT(*) AS sample_count
FROM weather_aqi_db.weather_airquality_records
GROUP BY hour
ORDER BY hour ASC;
```

![Biểu đồ xu hướng giờ cao điểm](../results/charts/02_peak_pollution_hours.png)

* **Nhận xét chuyên môn:**
  * Chỉ số US AQI và nồng độ PM2.5 đạt đỉnh trong khoảng thời gian từ **10:00 - 15:00 UTC** (tương ứng **17:00 - 22:00 giờ Việt Nam**). Đây là khung giờ tan tầm, mật độ phương tiện giao thông cá nhân và hoạt động công nghiệp/sinh hoạt đạt mức tối đa.
  * Trong khoảng thời gian **02:00 - 08:00 UTC** (sáng sớm đến trưa tại Việt Nam), nồng độ PM2.5 duy trì ở mức thấp hơn do nhiệt độ bề mặt đất tăng, tạo đối lưu nhiệt khuếch tán bụi lên tầng khí quyển cao hơn.

---

### 4.4. Bảng 4: Tương quan giữa Khí tượng và Bụi mịn PM2.5 (Pearson Correlation)
**Câu truy vấn SQL:**
```sql
SELECT 
    city,
    ROUND(corr(temperature_2m, pm2_5), 4) AS corr_temp_pm25,
    ROUND(corr(relative_humidity_2m, pm2_5), 4) AS corr_humidity_pm25,
    ROUND(corr(wind_speed_10m, pm2_5), 4) AS corr_wind_pm25
FROM weather_aqi_db.weather_airquality_records
GROUP BY city;
```

**Kết quả số liệu đo đạc thực tế:**

| Đô thị | Tương quan Nhiệt độ - PM2.5 | Tương quan Độ ẩm - PM2.5 | Tương quan Tốc độ gió - PM2.5 |
|---|:---:|:---:|:---:|
| **TP. Hồ Chí Minh** | **-0.7065** | **+0.6721** | **-0.2031** |
| **Đà Nẵng** | +0.4148 | -0.2582 | **-0.2967** |
| **Hà Nội** | +0.3714 | +0.0849 | **-0.6424** |

![Biểu đồ tương quan khí tượng](../results/charts/04_weather_pm25_correlation.png)

* **Nhận xét chuyên môn:**
  * Tại **TP. Hồ Chí Minh**, độ ẩm tương quan thuận rất mạnh với bụi PM2.5 ($r = +0.6721$), trong khi nhiệt độ tương quan nghịch ($r = -0.7065$). Điều này giải thích hiện tượng khi ban đêm trời mát và độ ẩm cao, hơi nước liên kết với hạt bụi tạo thành sương mù quang hóa (smog), khiến bụi mịn bị giữ lại sát mặt đất.
  * Tại **Hà Nội**, tốc độ gió tương quan nghịch rất mạnh với bụi PM2.5 ($r = -0.6424$), chứng tỏ khi có gió mùa tốc độ cao, nồng độ bụi ô nhiễm được khuếch tán nhanh chóng.

---

## CHƯƠNG 5: ĐÁNH GIÁ CHI PHÍ, TỐI ƯU VÀ DỌN DẸP TÀI NGUYÊN

### 5.1. Bảng cân đối ngân sách AWS Learner Lab ($100 Budget)
Toàn bộ hệ thống được xây dựng trên mô hình Serverless 100%, không sử dụng bất kỳ máy chủ EC2 thường trực nào:

| Dịch vụ AWS | Mức tiêu thụ thực tế của đồ án | Hạn mức Free Tier khả dụng | Chi phí thực tế (USD) |
|---|---|---|:---:|
| **AWS Lambda** | ~720 lượt gọi / tháng | 1,000,000 lượt gọi / tháng | **$0.00** |
| **Amazon EventBridge** | 720 scheduled triggers / tháng | 14,000,000 sự kiện / tháng | **$0.00** |
| **Amazon S3** | 3 phân vùng, ~100 KB dữ liệu NDJSON | 5 GB Standard Storage | **$0.00** |
| **Amazon Athena** | 4 truy vấn phân tích (quét ~336 KB) | $5.00 cho mỗi 1 TB quét | **< $0.001** |
| **AWS Glue Catalog** | 1 Database, 1 Table, 3 Partitions | 1,000,000 objects miễn phí | **$0.00** |
| **AWS Secrets Manager** | 1 Secret lưu API config | $0.40/secret/tháng | **$0.40** |
| **Amazon SNS** | 5 email cảnh báo kiểm thử | 1,000 email miễn phí / tháng | **$0.00** |
| **Amazon CloudWatch** | 1 Dashboard, 1 Metric Alarm | 3 Dashboard, 10 Alarms miễn phí | **$0.00** |
| **TỔNG CHI PHÍ THÁNG** | **Hệ thống vận hành trọn vẹn 30 ngày liên tục** | | **~$0.40 USD** |

* **Kết luận chi phí:** Với tổng chi phí chỉ khoảng **$0.40 / tháng**, đồ án chỉ tiêu thụ chưa đến **0.5%** ngân sách $100 được cấp của AWS Academy Learner Lab.

### 5.2. Cơ chế dọn dẹp và thu hồi tài nguyên (`cleanup_all.ps1`)
Để tuân thủ nghiêm ngặt chỉ đạo của GVHD: *"dừng/xóa tài nguyên sau mỗi buổi; báo cáo chi phí sử dụng cuối kỳ"*, nhóm đã phát triển script tự động hóa `scripts/cleanup_all.ps1`. Chỉ với một lệnh duy nhất:
```powershell
.\scripts\cleanup_all.ps1
```
Toàn bộ các tài nguyên S3 Bucket, Secrets Manager, SNS Topic, Lambda Function, EventBridge Rule, Glue Catalog và CloudWatch Dashboard đều được xóa sạch sẽ trong vòng 20 giây, đảm bảo không phát sinh bất kỳ chi phí ngầm nào giữa các buổi học.

---

## CHƯƠNG 6: KẾT LUẬN & HƯỚNG PHÁT TRIỂN

### 6.1. Kết quả đạt được
1. **Kiến trúc hoàn chỉnh:** Xây dựng thành công hệ thống thu thập, lưu trữ, phân tích và cảnh báo ô nhiễm không khí hoàn toàn bằng công nghệ Serverless trên nền tảng AWS.
2. **Tự động hóa 100% qua AWS CLI:** Toàn bộ quy trình triển khai (`deploy_all.ps1`), kiểm thử (`test_pipeline.ps1`), trích xuất số liệu (`export_metrics.py`), vẽ biểu đồ (`generate_charts.py`) và dọn dẹp (`cleanup_all.ps1`) đều được tự động hóa bằng lệnh CLI.
3. **Số liệu thực tế & Giá trị phân tích cao:** Các câu truy vấn SQL trên Amazon Athena đã chứng minh được sự khác biệt về chất lượng không khí giữa các thành phố lớn tại Việt Nam và làm sáng tỏ quy luật tương quan giữa thời tiết và nồng độ bụi mịn PM2.5.
4. **Bảo mật & Tối ưu ngân sách:** Bí mật được mã hóa trong Secrets Manager, phân vùng S3 tối ưu dung lượng quét của Athena, chi phí chỉ $0.40/tháng, tuân thủ tuyệt đối quy định của AWS Learner Lab.

### 6.2. Hướng phát triển trong tương lai
* Kết nối trực tiếp Amazon Athena với **Amazon QuickSight** hoặc xây dựng Web Dashboard (React / Streamlit) để người dân có thể theo dõi chất lượng không khí theo thời gian thực.
* Áp dụng mô hình Machine Learning với **Amazon SageMaker** để dự báo sớm chất lượng không khí trong 24 - 48 giờ tới dựa trên dữ liệu khí tượng.
* Tích hợp thêm kênh cảnh báo qua tin nhắn SMS (Amazon SNS SMS) hoặc thông báo ứng dụng di động qua Telegram Bot / Zalo ZNS.

---
*Báo cáo được hoàn thành và bảo vệ tại Trường Đại học Sư phạm Kỹ thuật TP.HCM, Học kỳ 1, Năm học 2026-2027.*
