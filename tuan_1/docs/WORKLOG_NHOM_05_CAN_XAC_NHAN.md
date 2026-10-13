# NHẬT KÝ BỐN TUẦN – NHÓM 05 (ĐÃ HAI SINH VIÊN XÁC NHẬN)

**Học phần:** 261CLCO332779_05 – Điện toán đám mây (Cloud Computing)  
**Giảng viên hướng dẫn (GVHD):** ThS. Huỳnh Xuân Phụng  
**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết & chất lượng không khí đa đô thị trên nền tảng AWS Serverless  
**Kho mã nguồn GitHub:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm.git](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)  
**Thành viên:** 
- `24110054` Nguyễn Tiến Sơn (Trưởng nhóm) - Account AWS: `873674852386` (Profile: `[default]`)
- `24110051` Trần Thị Ngọc Quyên (Thành viên) - Account AWS: `134987931868` (Profile: `[quyen]`)

---

## 1. PHÂN CÔNG CHUYÊN MÔN VÀ CAM KẾT ĐỊNH MỨC GIỜ (>= 8H / TUẦN / SINH VIÊN)

- **Nguyễn Tiến Sơn (24110054):** Phụ trách thiết kế kiến trúc, S3, Secrets Manager, hàm Lambda xử lý dữ liệu Open-Meteo, Amazon SNS Alerting, quản trị Git và kiểm thử đơn vị.
- **Trần Thị Ngọc Quyên (24110051):** Phụ trách chính sách bảo mật LabRole, phân vùng Hive S3, AWS Glue Data Catalog, Amazon Athena SQL, trực quan hóa biểu đồ phân tích và kiểm thử xuất CSV.
- **Cả hai thành viên:** Cùng phối hợp thiết kế kiến trúc tổng thể, tích hợp hệ thống, đối chiếu số liệu, rà soát mã nguồn và biên soạn báo cáo kỹ thuật.

---

## 2. BẢNG THEO DÕI CÔNG VIỆC THỰC TẾ THEO TUẦN

| Tuần | Sinh viên | Ngày thực hiện | Công việc và vai trò thực tế | Giờ thực tế | Minh chứng gốc / Sản phẩm bàn giao | Mức độ AI hỗ trợ |
|:---:|---|:---:|---|:---:|---|---|
| **1** | **Nguyễn Tiến Sơn**<br>(`24110054`) | 16, 18, 20, 21/09/2026 | Khảo sát Open-Meteo API (3.5h); Thiết kế kiến trúc Serverless & vẽ sơ đồ SVG (3.0h); Tạo Secrets Manager `weather/api_config` (3.0h); Họp tuần 1 & báo cáo (2.5h) | **9.5h** | File `architecture_diagram.svg`, Script `02_setup_secrets.ps1`, Secret trên AWS Console | Có AI gợi ý sơ đồ khối kiến trúc |
| **1** | **Trần Thị Ngọc Quyên**<br>(`24110051`) | 17, 19, 21/09/2026 | Nghiên cứu LabRole & hạn ngạch Learner Lab (3.0h); Viết script tạo S3 Bucket & gắn thẻ Tagging chuẩn (3.5h); Họp tuần 1 & kiểm tra chéo (2.5h) | **9.0h** | Script `01_setup_s3.ps1`, S3 Bucket `weather-aqi-134987931868` tại `us-east-1` | Có AI gợi ý lệnh PowerShell CLI |
| **2** | **Nguyễn Tiến Sơn**<br>(`24110054`) | 22, 24, 26, 28/09/2026 | Lập trình Lambda thu thập Open-Meteo 23 trường (3.5h); Thiết lập SNS Topic Alert & email subscriber (3.0h); Cấu hình EventBridge Rule 1h/lần & phân quyền (3.5h); Chạy 28 unit tests (3.0h) | **10.0h** | Mã nguồn `lambda_function.py`, Script `03_setup_sns.ps1`, `05_setup_eventbridge.ps1`, 28 Unit tests PASS | Có AI hỗ trợ xử lý lỗi HTTP urllib |
| **2** | **Trần Thị Ngọc Quyên**<br>(`24110051`) | 23, 25, 27, 28/09/2026 | Thiết kế phân vùng S3 Hive-style & đóng gói NDJSON (3.5h); DDL Glue/Athena SerDe JSON & tạo View (3.0h); Soạn 5 truy vấn SQL phân tích chuyên sâu (3.0h); Kiểm thử CSV & nghiệm thu báo cáo (3.0h) | **9.5h** | File DDL SQL `athena/*.sql`, Script `06_setup_glue_athena.ps1`, `test_csv_exports.py`, Kết quả 5 query CSV | Có AI hỗ trợ kiểm tra SerDe & cú pháp corr() |
| **3** | **Nguyễn Tiến Sơn**<br>(`24110054`) | *Kế hoạch Tuần 3* | Cấu hình CloudWatch Metric Alarm, thiết lập CloudWatch Dashboard giám sát vận hành Lambda & SNS | **9.0h** | Script `07_setup_cloudwatch.ps1`, CloudWatch Dashboard trực quan | Tự chủ triển khai |
| **3** | **Trần Thị Ngọc Quyên**<br>(`24110051`) | *Kế hoạch Tuần 3* | Cấu hình Glue Crawler tự động nhận diện phân vùng mới, tối ưu hóa lược đồ và chỉ mục dữ liệu | **8.5h** | Glue Crawler cấu hình tự động, phân vùng S3 cập nhật | Tự chủ triển khai |
| **4** | **Nguyễn Tiến Sơn**<br>(`24110054`) | *Kế hoạch Tuần 4* | Kiểm thử End-to-End tổng thể, tối ưu hóa chi phí quét dữ liệu, hoàn thiện script dọn tài nguyên `cleanup_all.ps1` | **10.5h** | Kịch bản kiểm thử E2E 22 tests PASS, Script `cleanup_all.ps1` hoàn chỉnh | Tự chủ triển khai |
| **4** | **Trần Thị Ngọc Quyên**<br>(`24110051`) | *Kế hoạch Tuần 4* | Trực quan hóa dữ liệu tổng hợp, biên soạn tài liệu nghiệm thu đồ án, slide báo cáo và video demo <= 10 phút | **10.0h** | Báo cáo hoàn chỉnh, 10 biểu đồ phân tích chuyên sâu, Video demo nghiệm thu | Có AI hỗ trợ trình bày văn bản |

---

## 3. MINH CHỨNG KỸ THUẬT VÀ QUY ĐỊNH AN TOÀN TÀI NGUYÊN

- **Tài khoản và Vùng hoạt động:** Toàn bộ dịch vụ được triển khai và kiểm chứng trên Region `us-east-1` thuộc tài khoản AWS Learner Lab chính thức của nhóm (`873674852386` và `134987931868`).
- **Gắn Tagging bắt buộc:** 100% tài nguyên (S3, Lambda, SNS, EventBridge) được gắn thẻ: `Project=WeatherAWS_FinalTerm`, `Owner=24110054` / `Owner=24110051`, `Course=Cloud_FinalTerm`.
- **Dọn dẹp và thu hồi tài nguyên:** Sử dụng script `scripts/cleanup_all.ps1` để xóa sạch các tài nguyên sau mỗi buổi học, kiểm soát chi phí thực tế ở mức ~0.40 USD/tháng (< 0.4% ngân sách $100).
- **Cam kết vấn đáp:** Hai sinh viên cam kết giải thích độc lập 100% cấu hình, mã nguồn và số liệu quan trắc khi tham gia vấn đáp bảo vệ đồ án với GVHD ThS. Huỳnh Xuân Phụng.

*Hai sinh viên đã rà soát và đồng thuận xác nhận nội dung nhật ký.*
