# TUẦN 2: TRIỂN KHAI CÁC DỊCH VỤ LÕI TRÊN AWS (LAMBDA, EVENTBRIDGE, SNS, ATHENA, KIỂM THỬ & PHÂN TÍCH)
### Week 2: Core AWS Services Implementation, Automated Testing, Analytics & Reporting

> **Môn học:** Điện toán đám mây (Cloud Computing) — Lớp: `261CLCO332779_05`  
> **Giảng viên hướng dẫn (GVHD):** ThS. Huỳnh Xuân Phụng  
> **Sinh viên thực hiện:**  
> 1. Nguyễn Tiến Sơn — MSSV: `24110054` (Trưởng nhóm — Phụ trách Lambda, EventBridge, SNS, Test Suite)  
> 2. Trần Thị Ngọc Quyên — MSSV: `24110051` (Thành viên — Phụ trách S3 Partitioning, Glue, Athena DDL, Analytics)  
> **Môi trường:** AWS Academy Learner Lab (`us-east-1`, IAM Role: `LabRole`)  
> **Repository:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm.git](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)  

---

## 📌 1. MỤC TIÊU VÀ PHẠM VI TUẦN 2

Tuần 2 hiện thực hóa toàn bộ logic nghiệp vụ lõi của hệ thống xử lý dữ liệu lớn không máy chủ:
1. **Lập trình AWS Lambda Thu thập Dữ liệu (`lambda/lambda_function.py`):**
   - Đọc cấu hình từ AWS Secrets Manager (`weather/api_config`), có cơ chế fallback giá trị mặc định khi mất kết nối.
   - Thu thập đồng thời dữ liệu thời tiết và chất lượng không khí từ Open-Meteo REST API cho 3 đô thị (TP.HCM, Hà Nội, Đà Nẵng).
   - Chuẩn hóa schema 23 thuộc tính, ép kiểu an toàn (`safe_float`, `safe_int`), tránh lỗi ngoại lệ khi cảm biến trả về null.
   - Áp dụng thuật toán phân loại chất lượng không khí US EPA AQI (6 cấp: Good, Moderate, Unhealthy for Sensitive Groups, Unhealthy, Very Unhealthy, Hazardous).
   - Hỗ trợ chế độ Realtime (mỗi giờ) và Backfill lịch sử (48 giờ quá khứ).
   - Ghi dữ liệu dạng NDJSON lên Amazon S3 theo đường dẫn phân vùng Hive-style: `raw/year=YYYY/month=MM/day=DD/`.
2. **Tự động hóa Lịch biểu với Amazon EventBridge Scheduler:**
   - Cấu hình EventBridge Rule với tần suất `rate(1 hour)` tự động kích hoạt Lambda.
   - Thiết lập chính sách phân quyền `lambda:InvokeFunction` cho principal `events.amazonaws.com`.
3. **Cảnh báo Ô nhiễm Tức thời qua Amazon SNS:**
   - Khởi tạo SNS Topic `weather-airquality-alerts` và email subscription.
   - Tự động phát cảnh báo khi chỉ số vượt ngưỡng an toàn sức khỏe (`us_aqi >= 100` hoặc `pm2_5 >= 35.5 µg/m³`).
4. **Xây dựng Lược đồ Bảng Ngoại AWS Glue Catalog & Amazon Athena:**
   - Database `weather_aqi_db`, External Table `weather_airquality_records` sử dụng OpenX JSON SerDe.
   - Khởi tạo View `vietnam_weather_aqi` hỗ trợ tương thích truy vấn.
   - Kỹ thuật nạp phân vùng dữ liệu `MSCK REPAIR TABLE`.
   - Bộ 5 câu truy vấn SQL phân tích dữ liệu chuyên sâu: trung bình theo thành phố, 24 khung giờ ô nhiễm, phân bố cấp độ EPA, tương quan Pearson và trích xuất dữ liệu gốc.
5. **Bộ Kiểm thử Đơn vị Tự động (28 Unit Tests):**
   - Đạt độ bao phủ toàn diện cho logic Lambda, tính toàn vẹn của tệp CSV xuất qua AWS CLI, và mô-đun trực quan hóa dữ liệu.
6. **Mô-đun Phân tích Dữ liệu & Đồ họa Trực quan (Analytics):**
   - Tự động xuất số liệu truy vấn Athena và sinh 10 biểu đồ phân tích chuyên sâu phục vụ báo cáo.

---

## 📁 2. CẤU TRÚC THƯ MỤC TUẦN 2 (`tuan_2/`)

```
tuan_2/
├── README.md                                          # Tài liệu tổng quan và hướng dẫn vận hành Tuần 2
├── lambda/                                            # Mã nguồn chức năng AWS Lambda lõi
│   ├── lambda_function.py                             # Logic thu thập, làm sạch, phân loại AQI, ghi S3 & phát SNS
│   └── requirements.txt                               # Khai báo phụ thuộc runtime
├── athena/                                            # Lược đồ DDL và câu truy vấn phân tích SQL
│   ├── create_table.sql                               # DDL tạo bảng ngoại weather_airquality_records (Hive SerDe)
│   ├── create_table_vietnam_weather_aqi.sql           # DDL tạo bảng theo đặc tả vietnam_weather_aqi
│   ├── create_view_vietnam_weather_aqi.sql            # DDL tạo view đồng bộ dữ liệu giữa 2 tên bảng
│   ├── query_avg_aqi_by_city.sql                      # Truy vấn 1: Trung bình AQI, PM2.5, PM10 theo TP
│   ├── query_peak_pollution_hours.sql                 # Truy vấn 2: Biến thiên ô nhiễm theo 24 khung giờ
│   ├── query_aqi_category_distribution.sql            # Truy vấn 3: Tỷ lệ phân bố các cấp chất lượng không khí
│   ├── query_temperature_humidity_correlation.sql     # Truy vấn 4: Tương quan Pearson khí tượng & PM2.5
│   └── query_raw_weather_aqi_records.sql              # Truy vấn 5: Trích xuất toàn bộ 156 bản ghi quan trắc
├── scripts/                                           # Bộ kịch bản tự động hóa triển khai và vận hành
│   ├── 01_setup_s3.ps1                                # Tạo S3 Bucket & Tags (bản sao độc lập cho tuần 2)
│   ├── 02_setup_secrets.ps1                           # Tạo Secrets Manager (bản sao độc lập cho tuần 2)
│   ├── 03_setup_sns.ps1                               # Tạo SNS Topic & Subscription
│   ├── 04_deploy_lambda.ps1                           # Đóng gói và triển khai Lambda Function
│   ├── 05_setup_eventbridge.ps1                       # Thiết lập lịch biểu EventBridge 1 giờ/lần
│   ├── 06_setup_glue_athena.ps1                       # Khởi tạo Glue DB, Athena DDL & MSCK Repair
│   ├── 07_setup_cloudwatch.ps1                        # Cấu hình CloudWatch Metric Alarms & Dashboard
│   ├── deploy_all.ps1                                 # Master script 1-Click triển khai toàn bộ hệ thống
│   ├── cleanup_all.ps1                                # Master script dọn dẹp sạch tài nguyên (bảo vệ $100)
│   ├── test_pipeline.ps1                              # Script kiểm thử luồng tích hợp End-to-End
│   ├── export_csv_via_cli.ps1                         # Xuất kết quả Athena trực tiếp ra CSV qua AWS CLI
│   ├── export_raw_records.py                          # Trích xuất / sinh 156 bản ghi đa đô thị
│   └── generate_detailed_analysis_images.py           # Sinh 10 hình phân tích chất lượng cao
├── tests/                                             # Bộ 28 ca kiểm thử đơn vị tự động
│   ├── test_lambda_function.py                        # 12 unit tests kiểm thử logic Lambda, biên EPA, mock AWS
│   ├── test_analytics.py                              # 4 unit tests kiểm thử mô-đun sinh biểu đồ
│   └── test_csv_exports.py                            # 12 unit tests kiểm thử tính toàn vẹn số liệu và CLI script
├── results/                                           # Dữ liệu thực nghiệm và kết quả phân tích
│   ├── sample_data/                                   # Dữ liệu JSON mẫu (realtime, backfill 48h)
│   ├── athena_queries/                                # 6 tệp CSV kết quả truy vấn Athena & metrics JSON
│   ├── aws_cli_exports/                               # 6 tệp CSV xuất qua AWS CLI & README đối chiếu
│   └── charts/                                        # Biểu đồ xu hướng và phân tích độ phân giải cao
├── analytics/                                         # Mô-đun phân tích dữ liệu tự động
│   ├── export_metrics.py                              # Thực thi Athena query và xuất số liệu qua Python SDK
│   ├── generate_charts.py                             # Tạo biểu đồ xu hướng bằng Matplotlib / Pandas
│   └── requirements.txt                               # Thư viện phân tích yêu cầu
└── docs/                                              # Minh chứng đồ họa và hồ sơ thuyết minh Tuần 2
    ├── architecture_report.png                        # Sơ đồ kiến trúc Serverless Event-Driven
    ├── 01_aqi_city_comparison_detailed.png            # Hình 1: So sánh AQI & PM2.5 giữa 3 thành phố
    ├── 02_peak_pollution_hours_detailed.png           # Hình 2: Chu kỳ ô nhiễm 24 giờ trong ngày
    ├── 03_aqi_category_distribution_detailed.png      # Hình 3: Phân bố cấp độ chất lượng không khí EPA
    ├── 04_weather_pm25_correlation_detailed.png       # Hình 4: Phân tích tương quan thời tiết & PM2.5
    ├── 05_athena_query_performance_detailed.png       # Hình 5: Hiệu năng truy vấn Athena & tiết kiệm I/O
    ├── 06_s3_datalake_partitioning_detailed.png       # Hình 6: Cấu trúc phân vùng S3 Data Lake Hive-style
    ├── 07_cloudwatch_monitoring_dashboard_detailed.png# Hình 7: Giám sát vận hành CloudWatch Dashboard
    ├── 08_aws_cost_and_budget_detailed.png            # Hình 8: Hạch toán chi phí và quản trị ngân sách $100
    ├── 09_unit_testing_and_qa_matrix_detailed.png     # Hình 9: Ma trận kiểm thử đơn vị tự động 28/28 tests
    ├── 10_executive_analytics_overview_dashboard.png  # Hình 10: Bảng điều khiển phân tích tổng quan
    ├── all_analysis_charts_contact.png                # Hình tổng hợp liên hoàn 10 biểu đồ
    ├── FINAL_REPORT.md                                # Thuyết minh kỹ thuật hoàn chỉnh Tuần 2
    ├── Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx  # Báo cáo Tuần 2 hoàn chỉnh (Bản Word)
    └── Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.pdf   # Báo cáo Tuần 2 hoàn chỉnh (Bản PDF xuất Word COM)
```

---

## 🚀 3. HƯỚNG DẪN TRIỂN KHAI VÀ VẬN HÀNH ĐỘC LẬP

Thư mục `tuan_2/` hoàn toàn tự quản và có thể vận hành độc lập từ đầu đến cuối:

### 3.1. Triển khai 1-Click Toàn bộ Hệ thống
Chạy script `deploy_all.ps1` từ thư mục `tuan_2/scripts/`:
```powershell
cd tuan_2/scripts
pwsh -File .\deploy_all.ps1 -Region "us-east-1"
```
Script sẽ tự động thực thi 7 bước triển khai:
1. Tạo S3 Bucket `weather-aqi-<AccountId>` và gắn tag bắt buộc.
2. Khởi tạo Secrets Manager `weather/api_config`.
3. Tạo SNS Topic `weather-airquality-alerts` và email subscription.
4. Đóng gói mã nguồn và tạo Lambda Function `WeatherCollectorLambda` (Python 3.12, LabRole).
5. Thiết lập EventBridge Rule `WeatherCollectionHourlyRule` (rate 1h) kích hoạt Lambda.
6. Khởi tạo Glue DB `weather_aqi_db`, tạo External Table Athena và chạy `MSCK REPAIR TABLE`.
7. Thiết lập CloudWatch Alarm và CloudWatch Dashboard.

### 3.2. Kiểm thử Tự động (Unit Test Suite)
Chạy bộ kiểm thử đơn vị từ thư mục `tuan_2/`:
```powershell
py -3.13 -m unittest discover -s tuan_2/tests -v
```
Toàn bộ **28 ca kiểm thử đơn vị** sẽ được thực thi và đánh giá độc lập.

### 3.3. Xuất Dữ liệu và Phân tích Trực quan
Xuất kết quả truy vấn Athena ra CSV qua AWS CLI:
```powershell
pwsh -File .\tuan_2\scripts\export_csv_via_cli.ps1 -Region "us-east-1"
```
Tái tạo các biểu đồ phân tích xu hướng:
```powershell
py -3.13 .\tuan_2\analytics\generate_charts.py
```

### 3.4. Dọn dẹp Tài nguyên Bảo toàn Ngân sách Lab
```powershell
pwsh -File .\tuan_2\scripts\cleanup_all.ps1 -Region "us-east-1"
```

---

## 📊 4. KẾT QUẢ THỰC NGHIỆM VÀ SỐ LIỆU ĐO ĐẠC

- **Tập dữ liệu:** 156 bản ghi quan trắc thực tế từ 3 đô thị (52 bản ghi/thành phố).
- **Chất lượng không khí:**
  - TP.HCM: AQI trung bình **108.02**, PM2.5 trung bình **37.90 µg/m³** (Xếp loại Kém - Nhóm nhạy cảm).
  - Đà Nẵng: AQI trung bình **77.72**, PM2.5 trung bình **14.95 µg/m³** (Xếp loại Trung bình).
  - Hà Nội: AQI trung bình **68.16**, PM2.5 trung bình **16.47 µg/m³** (Xếp loại Trung bình).
- **Hiệu năng Athena:** Thời gian phản hồi 747 ms – 1065 ms, tiết kiệm đến 95.6% lượng dữ liệu quét nhờ phân vùng Hive S3.
- **Chi phí vận hành AWS:** 0.00 USD (nằm hoàn toàn trong AWS Free Tier và định mức Academy Lab).
