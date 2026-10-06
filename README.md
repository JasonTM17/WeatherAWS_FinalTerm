# HỆ THỐNG THU THẬP VÀ PHÂN TÍCH DỮ LIỆU THỜI TIẾT / CHẤT LƯỢNG KHÔNG KHÍ (AWS CLOUD)
### Weather & Air Quality Data Pipeline with AWS Serverless Architecture
**(Nhóm đề tài: Domain Apps - Học kỳ 1, Năm học 2026-2027)**

[![AWS](https://img.shields.io/badge/AWS-Serverless-orange.svg)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![University](https://img.shields.io/badge/HCMUTE-Cloud%20Computing-red.svg)](https://hcmute.edu.vn/)

---

> **Môn học:** Điện toán đám mây (Cloud Computing)  
> **Giảng viên hướng dẫn (GVHD):** ThS. Huỳnh Xuân Phụng  
> **Sinh viên thực hiện:**  
> 1. Trần Minh Jason - MSSV: `24110054` (Trưởng nhóm)  
> 2. Nguyễn Văn An - MSSV: `24110055` (Thành viên)  
> **Môi trường:** AWS Learner Lab (`us-east-1` | Account ID: `873674852386` | Role: `LabRole`)  
> **Repository:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm.git](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)

---

## 📌 1. TỔNG QUAN DỰ ÁN

Dự án xây dựng một đường ống dữ liệu (Data Pipeline) theo mô hình **Serverless Event-Driven** trên nền tảng Amazon Web Services (AWS) để tự động hóa hoàn toàn chu trình:
1. **Thu thập định kỳ:** Gọi Open-Meteo Air Quality & Weather API thu thập dữ liệu bụi mịn (PM2.5, PM10), khí độc hại (CO, NO2, SO2, O3), chỉ số US AQI và thời tiết (nhiệt độ, độ ẩm, tốc độ gió) tại 3 thành phố lớn: **TP. Hồ Chí Minh, Hà Nội, Đà Nẵng**.
2. **Lưu trữ chuẩn Data Lake:** Định dạng **NDJSON** phân vùng theo thời gian (`year=YYYY/month=MM/day=DD`) trên **Amazon S3**.
3. **Quản lý khóa an toàn:** Lưu trữ API key và cấu hình điều phối trong **AWS Secrets Manager**.
4. **Cảnh báo tức thời:** Gửi email cảnh báo nguy cơ ô nhiễm sức khỏe qua **Amazon SNS** khi AQI > 100 hoặc PM2.5 > 35.5 µg/m³.
5. **Phân tích dữ liệu lớn không máy chủ:** Sử dụng **AWS Glue Data Catalog** và **Amazon Athena** truy vấn SQL phân tích xu hướng, khung giờ cao điểm và tương quan khí tượng.
6. **Trực quan hóa xu hướng:** Tự động xuất biểu đồ phân tích chuyên sâu (`matplotlib` / `pandas`).
7. **Giám sát & Quản trị:** Theo dõi qua **Amazon CloudWatch** Alarms và Dashboard.

---

## 🏛️ 2. SƠ ĐỒ KIẾN TRÚC HỆ THỐNG

![Kiến trúc hệ thống](docs/architecture_diagram.svg)

---

## 🚀 3. HƯỚNG DẪN CÀI ĐẶT & TRIỂN KHAI (QUICK START)

### 3.1. Yêu cầu môi trường
* Windows PowerShell 5.1+ hoặc PowerShell Core 7+
* [AWS CLI v2](https://aws.amazon.com/cli/) đã cấu hình credentials của AWS Learner Lab (`~/.aws/credentials`).
* Python 3.12+ (với `boto3`, `pandas`, `matplotlib`).

### 3.2. Triển khai toàn bộ hệ thống (1-Click Deployment)
Chỉ cần chạy lệnh sau trong PowerShell để tự động tạo toàn bộ S3, Secrets Manager, SNS, Lambda, EventBridge, Glue, Athena và CloudWatch:
```powershell
.\scripts\deploy_all.ps1 -Region "us-east-1"
```

### 3.3. Kiểm thử luồng dữ liệu End-to-End
Chạy script kiểm thử để kích hoạt Lambda, đồng bộ phân vùng Athena, trích xuất dữ liệu ra CSV và vẽ biểu đồ:
```powershell
.\scripts\test_pipeline.ps1 -Region "us-east-1"
```

### 3.4. Dọn dẹp tài nguyên sau buổi thực hành (Bảo toàn $100 Lab)
Theo đúng chỉ đạo của GVHD: *"dừng/xóa tài nguyên sau mỗi buổi; báo cáo chi phí sử dụng cuối kỳ"*:
```powershell
.\scripts\cleanup_all.ps1 -Region "us-east-1"
```

---

## 📊 4. KẾT QUẢ PHÂN TÍCH SỐ LIỆU ĐO ĐẠC THỰC TẾ (ATHENA & CHARTS)

### 4.1. So sánh chất lượng không khí giữa các thành phố
| Đô thị | AQI Trung bình | PM2.5 TB (µg/m³) | PM10 TB (µg/m³) | Nhiệt độ TB (°C) | Độ ẩm TB (%) | Đánh giá EPA |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **TP. Hồ Chí Minh** | **108.02** | **37.90** | 38.14 | 27.65 | 85.38 | Kém (Nhóm nhạy cảm) |
| **Đà Nẵng** | **77.72** | 14.95 | 18.19 | 28.97 | 74.44 | Trung bình |
| **Hà Nội** | **68.16** | 16.47 | 17.17 | 24.50 | 78.22 | Trung bình |

<p align="center">
  <img src="results/charts/01_aqi_city_comparison.png" width="48%" />
  <img src="results/charts/03_aqi_category_distribution.png" width="48%" />
</p>

### 4.2. Chu kỳ biến thiên theo giờ và Tương quan khí tượng
<p align="center">
  <img src="results/charts/02_peak_pollution_hours.png" width="48%" />
  <img src="results/charts/04_weather_pm25_correlation.png" width="48%" />
</p>

---

## 📁 5. CẤU TRÚC THƯ MỤC DỰ ÁN

```
d:/AWS_Final_Term/
├── .gitignore                          # Cấu hình bỏ qua tệp tạm và thông tin nhạy cảm
├── README.md                           # Tài liệu tổng quan dự án
├── lambda/
│   ├── lambda_function.py              # Mã nguồn AWS Lambda xử lý thu thập, phân vùng S3 & SNS
│   └── requirements.txt                # Thư viện yêu cầu
├── scripts/
│   ├── 01_setup_s3.ps1                 # Khởi tạo S3 bucket & gắn tags
│   ├── 02_setup_secrets.ps1            # Khởi tạo AWS Secrets Manager
│   ├── 03_setup_sns.ps1                # Khởi tạo Amazon SNS Topic & Email Subscription
│   ├── 04_deploy_lambda.ps1            # Đóng gói & triển khai Lambda function
│   ├── 05_setup_eventbridge.ps1        # Cấu hình EventBridge Scheduler (rate 1h)
│   ├── 06_setup_glue_athena.ps1        # Khởi tạo Glue DB, Athena DDL & sửa chữa phân vùng
│   ├── 07_setup_cloudwatch.ps1         # Thiết lập CloudWatch Alarm & Dashboard
│   ├── deploy_all.ps1                  # Master script triển khai tự động toàn bộ
│   ├── test_pipeline.ps1               # Master script kiểm thử luồng End-to-End
│   └── cleanup_all.ps1                 # Script dọn dẹp sạch tài nguyên (bảo vệ $100 Lab)
├── athena/
│   ├── create_table.sql                # DDL tạo External Table phân vùng Hive-style
│   ├── query_avg_aqi_by_city.sql       # Query 1: So sánh AQI, PM2.5 trung bình theo TP
│   ├── query_peak_pollution_hours.sql  # Query 2: Xác định khung giờ ô nhiễm cao nhất
│   ├── query_aqi_category_distribution.sql # Query 3: Phân bố tỷ lệ cấp độ ô nhiễm
│   └── query_temperature_humidity_correlation.sql # Query 4: Phân tích tương quan khí tượng
├── analytics/
│   ├── export_metrics.py               # Chạy Athena qua Python SDK, xuất CSV & JSON metrics
│   ├── generate_charts.py              # Vẽ 4 biểu đồ xu hướng chuyên sâu (Matplotlib/Pandas)
│   └── requirements.txt                # Thư viện phân tích dữ liệu
├── docs/
│   ├── ARCHITECTURE.md                 # Tài liệu thiết kế kiến trúc chi tiết
│   ├── WORKLOG.md                      # Nhật ký công việc 4 tuần chi tiết (mỗi SV >= 8h/tuần)
│   ├── CLI_EXECUTION_LOGS.md           # Minh chứng thực thi lệnh AWS CLI có Account ID
│   ├── FINAL_REPORT.md                 # Báo cáo tổng kết đồ án hoàn chỉnh chuẩn HCMUTE
│   └── architecture_diagram.svg        # Sơ đồ kiến trúc vector SVG
└── results/
    ├── athena_queries/                 # Kết quả CSV và JSON trích xuất từ Athena
    ├── charts/                         # 4 hình ảnh biểu đồ độ phân giải cao
    └── sample_data/                    # Dữ liệu JSON mẫu từ Lambda
```

---

## 📑 6. TÀI LIỆU CHI TIẾT
* [Báo cáo tổng kết đồ án hoàn chỉnh (Final Report)](docs/FINAL_REPORT.md)
* [Tài liệu thiết kế kiến trúc (Architecture Details)](docs/ARCHITECTURE.md)
* [Nhật ký công việc 4 tuần chi tiết (Worklog)](docs/WORKLOG.md)
* [Minh chứng thực thi lệnh AWS CLI (Execution Logs)](docs/CLI_EXECUTION_LOGS.md)

---
*Đồ án môn học Điện toán đám mây - Khoa Công nghệ Thông tin - Trường ĐH Sư phạm Kỹ thuật TP.HCM (HCMUTE)*
