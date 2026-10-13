# TUẦN 1: TÌM HIỂU DỊCH VỤ, THIẾT KẾ KIẾN TRÚC & DỰNG NỀN TẢNG ĐÁM MÂY (AWS)
### Week 1: Service Exploration, Architecture Design & Cloud Foundation Setup

> **Môn học:** Điện toán đám mây (Cloud Computing) — Lớp: `261CLCO332779_05`  
> **Giảng viên hướng dẫn (GVHD):** ThS. Huỳnh Xuân Phụng  
> **Sinh viên thực hiện:**  
> 1. Nguyễn Tiến Sơn — MSSV: `24110054` (Trưởng nhóm)  
> 2. Trần Thị Ngọc Quyên — MSSV: `24110051` (Thành viên)  
> **Môi trường:** AWS Academy Learner Lab (`us-east-1`, IAM Role: `LabRole`)  
> **Repository:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm.git](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)  

---

## 📌 1. MỤC TIÊU VÀ PHẠM VI TUẦN 1

Tuần 1 tập trung vào giai đoạn khảo sát, thiết kế và thiết lập hạ tầng nền tảng cho hệ thống thu thập và phân tích dữ liệu thời tiết / chất lượng không khí:
1. **Tìm hiểu dịch vụ AWS & Ràng buộc Learner Lab:** Khảo sát các dịch vụ đám mây AWS (S3, Secrets Manager, IAM LabRole, CloudWatch) trong phạm vi tài khoản AWS Learner Lab với ngân sách $100 và quyền hạn hạn chế của `LabRole`.
2. **Khảo sát Nguồn Dữ liệu:** Đánh giá cấu trúc Open-Meteo Air Quality & Weather API, xác định 23 chỉ số đo lường (bụi mịn PM2.5, PM10, khí độc hại CO, NO2, SO2, O3, nhiệt độ, độ ẩm, tốc độ gió, US AQI theo chuẩn EPA).
3. **Thiết kế Kiến trúc Hệ thống:** Xây dựng mô hình Serverless Event-Driven, luồng dữ liệu tự động từ EventBridge Scheduler -> AWS Lambda -> Amazon S3 Data Lake (Hive-partitioning) -> Amazon Athena -> Amazon SNS Alerting.
4. **Khởi tạo Nền tảng Lưu trữ & Bảo mật:** Viết các script tự động hóa PowerShell / AWS CLI khởi tạo S3 Bucket có cấu trúc phân vùng thời gian và Secrets Manager lưu trữ thông số cấu hình an toàn.
5. **Hồ sơ Báo cáo Tuần 1:** Hoàn thiện bộ báo cáo tiến độ chuẩn mẫu HCMUTE gồm bản DOCX, bản PDF 20 trang với mục lục siêu liên kết (hyperlinked TOC), sổ tính Excel minh chứng và gói dữ liệu CSV.

---

## 🏛️ 2. SƠ ĐỒ KIẾN TRÚC HỆ THỐNG

![Kiến trúc hệ thống và luồng dữ liệu](docs/architecture_report.png)

Kiến trúc tuần 1 xác lập 4 phân vùng chức năng:
- **Tầng Thu thập (Ingestion Layer):** Kích hoạt định kỳ theo giờ, gọi Open-Meteo REST API cho 3 thành phố: TP.HCM, Hà Nội, Đà Nẵng.
- **Tầng Lưu trữ (Storage / Data Lake Layer):** Amazon S3 Bucket lưu trữ NDJSON theo phân vùng Hive-style: `raw/year=YYYY/month=MM/day=DD/`.
- **Tầng Bảo mật & Cấu hình (Security & Configuration Layer):** AWS Secrets Manager (`weather/api_config`) quản lý tọa độ địa lý, tham số cảm biến và ngưỡng cảnh báo an toàn.
- **Tầng Báo động & Truy vấn (Alerting & Analytics Layer):** Amazon SNS Topic phát cảnh báo chất lượng không khí và Amazon Athena truy vấn dữ liệu phân vùng.

---

## 📁 3. CẤU TRÚC THƯ MỤC TUẦN 1 (`tuan_1/`)

```
tuan_1/
├── README.md                                          # Tài liệu hướng dẫn và tổng kết Tuần 1
├── scripts/                                           # Kịch bản khởi tạo hạ tầng nền tảng
│   ├── 01_setup_s3.ps1                                # Khởi tạo S3 Bucket & gắn thẻ Tags bắt buộc
│   └── 02_setup_secrets.ps1                           # Khởi tạo AWS Secrets Manager lưu cấu hình
└── docs/                                              # Tài liệu thiết kế và hồ sơ báo cáo Tuần 1
    ├── ARCHITECTURE.md                                # Đặc tả chi tiết kiến trúc Serverless Event-Driven
    ├── architecture_diagram.svg                       # Sơ đồ kiến trúc dạng vector SVG
    ├── architecture_report.png                        # Sơ đồ kiến trúc chất lượng cao dùng trong báo cáo
    ├── Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx  # Báo cáo tiến độ Tuần 1 (Bản Word có mục lục native)
    ├── Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf   # Báo cáo tiến độ Tuần 1 (Bản PDF 20 trang chuẩn in)
    ├── Bao_cao_tuan_1_Du_lieu_Athena_Nhom_05.xlsx     # Sổ tính Excel 6 sheet trình bày số liệu truy vấn
    ├── Bao_cao_tuan_1_CSV_Nhom_05/                    # Thư mục 6 tệp CSV dữ liệu trích xuất ban đầu
    ├── Bao_cao_tuan_1_CSV_Nhom_05.zip                 # Gói nén ZIP nộp kèm dữ liệu CSV Tuần 1
    ├── WORKLOG_NHOM_05_CAN_XAC_NHAN.md                # Nhật ký công việc và phân công nhiệm vụ Tuần 1
    └── WORKLOG.md                                     # Nhật ký công việc tham khảo nội bộ
```

---

## 🚀 4. HƯỚNG DẪN THỰC THI HẠ TẦNG NỀN TẢNG TUẦN 1

### 4.1. Khởi tạo Amazon S3 Bucket & Gắn thẻ Tags
Script `01_setup_s3.ps1` tự động truy vấn AWS Account ID hiện tại và tạo bucket với định dạng duy nhất toàn cầu:
```powershell
pwsh -File .\scripts\01_setup_s3.ps1 -Region "us-east-1"
```
*Tài nguyên khởi tạo:*
- Bucket Name: `weather-aqi-<AccountId>`
- Thẻ Tags: `Project=WeatherAWS_FinalTerm`, `Owner=24110054`, `Course=Cloud_FinalTerm`

### 4.2. Khởi tạo AWS Secrets Manager
Script `02_setup_secrets.ps1` tạo secret `weather/api_config` chứa thông số 3 đô thị và ngưỡng kích hoạt:
```powershell
pwsh -File .\scripts\02_setup_secrets.ps1 -Region "us-east-1"
```
*Thông số cấu hình:*
- Tọa độ: TP.HCM (`lat=10.8231, lon=106.6297`), Hà Nội (`lat=21.0285, lon=105.8542`), Đà Nẵng (`lat=16.0544, lon=108.2022`).
- Ngưỡng cảnh báo US EPA: `alert_aqi_threshold = 100`, `alert_pm25_threshold = 35.5 µg/m³`.

---

## 📑 5. HỒ SƠ VÀ BÁO CÁO TUẦN 1
- **Bản DOCX & PDF:** [Báo cáo Tuần 1 DOCX](docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx) · [Báo cáo Tuần 1 PDF](docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf)
  - Đúng chuẩn 20 trang vật lý in ấn HCMUTE.
  - Chứa liên kết GitHub repository chính thức: `https://github.com/JasonTM17/WeatherAWS_FinalTerm.git`.
  - Mục lục 28 mục có bookmark và siêu liên kết trỏ chính xác đến từng trang in.
- **Sổ tính & Dữ liệu:** [Sổ tính Excel Athena](docs/Bao_cao_tuan_1_Du_lieu_Athena_Nhom_05.xlsx) · [Gói dữ liệu CSV](docs/Bao_cao_tuan_1_CSV_Nhom_05.zip).
