# NHẬT KÝ CÔNG VIỆC DỰ ÁN - TUẦN 2 (PROJECT WORKLOG WEEK 2)

> **Học phần:** Điện toán đám mây (Cloud Computing) - Mã lớp: `261CLCO332779_05`  
> **Giảng viên hướng dẫn (GVHD):** ThS. Huỳnh Xuân Phụng  
> **Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết & chất lượng không khí đa đô thị trên nền tảng AWS Serverless  
> **Kho lưu trữ GitHub chính thức:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm.git](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)  
> **Nhóm thực hiện (Nhóm 05):**
> - **Sinh viên 1 (Trưởng nhóm):** Nguyễn Tiến Sơn — MSSV: `24110054`
> - **Sinh viên 2 (Thành viên):** Trần Thị Ngọc Quyên — MSSV: `24110051`  
> **Môi trường thực nghiệm:** AWS Academy Learner Lab (`us-east-1` | IAM Role: `LabRole`)  
> - Tài khoản 1 (Sơn): `873674852386` (Profile: `[default]`)  
> - Tài khoản 2 (Quyên): `134987931868` (Profile: `[quyen]`)

---

## 1. BẢNG TỔNG KẾT THỜI GIAN LÀM VIỆC TUẦN 2 (CAM KẾT ĐỊNH MỨC >= 8H / TUẦN / SINH VIÊN)

Tuân thủ quy định của đề cương học phần và hướng dẫn của GVHD ThS. Huỳnh Xuân Phụng: *Mỗi sinh viên dành tối thiểu 8 giờ/tuần cho đồ án (tương đương tối thiểu 16 giờ/tuần đối với nhóm 2 sinh viên).*

| Tuần | Giai đoạn thực hiện theo đề cương | Giờ SV1 (Sơn - 24110054) | Giờ SV2 (Quyên - 24110051) | Tổng giờ nhóm | Trạng thái nghiệm thu |
|:---:|---|:---:|:---:|:---:|:---:|
| **Tuần 1** | Khảo sát dịch vụ, thiết kế kiến trúc, dựng nền tảng S3 & Secrets Manager, gắn tag | 9.5 giờ | 9.0 giờ | 18.5 giờ | Hoàn thành (Đạt) |
| **Tuần 2** | **Triển khai các chức năng lõi trên AWS (Lambda, EventBridge, SNS, Athena DDL, Unit tests)** | **10.0 giờ** | **9.5 giờ** | **19.5 giờ** | **HOÀN THÀNH (ĐẠT)** |
| **Tuần 3** | Tích hợp Glue Catalog tự động, CloudWatch Metric Alarm, Dashboard giám sát | 9.0 giờ | 8.5 giờ | 17.5 giờ | Kế hoạch dự kiến |
| **Tuần 4** | Kiểm thử tổng thể, tối ưu chi phí quét dữ liệu, dọn tài nguyên, báo cáo & demo | 10.5 giờ | 10.0 giờ | 20.5 giờ | Kế hoạch dự kiến |
| **TỔNG** | **Toàn bộ 4 tuần thực hiện đồ án** | **39.0 giờ** | **37.0 giờ** | **76.0 giờ** | **ĐẠT TIÊU CHUẨN** |

---

## 2. NHẬT KÝ CHI TIẾT CÔNG VIỆC TUẦN 2 (22/09/2026 – 28/09/2026)

**Mục tiêu Tuần 2:** Triển khai toàn bộ các chức năng lõi (Core Services) của hệ thống thu thập và phân tích dữ liệu trên AWS Learner Lab: lập trình hàm AWS Lambda thu thập dữ liệu Open-Meteo REST API, cấu hình tự động hóa lịch biểu EventBridge 1 giờ/lần, thiết lập cơ chế cảnh báo ô nhiễm tức thời qua Amazon SNS, xây dựng lược đồ bảng ngoại Glue/Athena với SerDe JSON và phân vùng Hive-style, thực thi 5 truy vấn SQL chuyên sâu, hoàn thành bộ 28 ca kiểm thử đơn vị tự động đạt tỷ lệ 100% PASS và biên soạn báo cáo kỹ thuật Tuần 2.

| Ngày | Sinh viên thực hiện | Nội dung công việc chi tiết | Số giờ | Minh chứng / Sản phẩm bàn giao | Mức độ AI hỗ trợ (AI Disclosure) |
|:---:|---|---|:---:|---|---|
| **22/09/2026** | **Nguyễn Tiến Sơn**<br>(MSSV: `24110054`) | Thiết kế và lập trình mã nguồn hàm AWS Lambda (`lambda_function.py`, 401 dòng): tích hợp đọc cấu hình từ Secrets Manager với cơ chế fallback nội bộ an toàn; kết nối HTTPS tới Open-Meteo Weather & Air Quality API; trích xuất và chuẩn hóa 23 trường thuộc tính dữ liệu; tích hợp thuật toán phân loại chất lượng không khí US EPA AQI (6 cấp độ). | **3.5h** | - Mã nguồn `tuan_2/lambda/lambda_function.py`.<br>- Thuật toán phân cấp AQI và xử lý ngoại lệ an toàn kiểu dữ liệu `safe_float`, `safe_int`. | **Có dùng AI hỗ trợ**<br>(LLM hỗ trợ gợi ý khung xử lý lỗi thư viện chuẩn `urllib.request`). |
| **23/09/2026** | **Trần Thị Ngọc Quyên**<br>(MSSV: `24110051`) | Thiết kế cấu trúc lưu trữ phân vùng Hive-style trên Amazon S3 Data Lake theo cấu trúc `raw/year=YYYY/month=MM/day=DD/`. Xây dựng hàm `save_records_to_s3()` đóng gói các bản ghi thu thập thành định dạng NDJSON (Newline Delimited JSON) tối ưu hóa tốc độ ghi và khả năng quét dữ liệu phân vùng của Athena. | **3.5h** | - Module ghi dữ liệu S3 trong `lambda_function.py`.<br>- Các tệp dữ liệu `data_*.json` mẫu được lưu đúng đường dẫn phân vùng Hive-style trên S3. | **Tự lập trình**<br>(Sinh viên tự phân tích thiết kế cấu trúc thư mục phân vùng và viết logic định dạng NDJSON). |
| **24/09/2026** | **Nguyễn Tiến Sơn**<br>(MSSV: `24110054`) | Khởi tạo Amazon SNS Topic (`weather-airquality-alerts`) trên Region `us-east-1` bằng AWS CLI; thiết lập cơ chế gửi email thông báo cho sinh viên và người dân; xây dựng logic đánh giá ngưỡng ô nhiễm trong Lambda: tự động phát sinh cảnh báo khi US AQI >= 100 hoặc nồng độ bụi mịn PM2.5 >= 35.5 µg/m³. | **3.0h** | - Script `tuan_2/scripts/03_setup_sns.ps1`.<br>- SNS Topic hoạt động và email subscription xác nhận.<br>- Mẫu thông điệp cảnh báo định dạng chuẩn. | **Tự cấu hình qua CLI**<br>(Tự viết script CLI và thiết kế nội dung thông báo cảnh báo qua email). |
| **25/09/2026** | **Trần Thị Ngọc Quyên**<br>(MSSV: `24110051`) | Thiết kế lược đồ bảng ngoại (External Table) trên AWS Glue Data Catalog (`weather_airquality_records`) sử dụng OpenX JSON SerDe với cấu hình `ignore.malformed.json=TRUE`; tạo View phân tích `vietnam_weather_aqi` tự động quy đổi múi giờ UTC sang giờ Việt Nam (UTC+7); cấu hình cơ chế nạp phân vùng dữ liệu qua `MSCK REPAIR TABLE`. | **3.0h** | - File DDL SQL `create_table.sql` và `create_view_vietnam_weather_aqi.sql`.<br>- Script `tuan_2/scripts/06_setup_glue_athena.ps1`.<br>- Database và bảng ngoại hoạt động trên Glue/Athena. | **Có dùng AI hỗ trợ**<br>(LLM hỗ trợ kiểm tra kiểu dữ liệu SerDe và cú pháp hàm thời gian Presto/Athena). |
| **26/09/2026** | **Nguyễn Tiến Sơn**<br>(MSSV: `24110054`) | Cấu hình Amazon EventBridge Rule (`WeatherCollectionSchedule`) kích hoạt định kỳ 1 giờ/lần (`rate(1 hour)`); thiết lập Resource-based policy cho phép EventBridge gọi Lambda; viết script đóng gói mã nguồn và triển khai Lambda Function gán quyền thực thi `LabRole` qua AWS CLI. | **3.5h** | - Script `tuan_2/scripts/04_deploy_lambda.ps1` và `05_setup_eventbridge.ps1`.<br>- EventBridge Rule ENABLED kích hoạt Lambda tự động 24/7 trên us-east-1. | **Tự cấu hình qua CLI**<br>(Tự cấu hình tham số CLI và kiểm tra quyền gọi hàm giữa các dịch vụ). |
| **27/09/2026** | **Trần Thị Ngọc Quyên**<br>(MSSV: `24110051`) | Soạn thảo bộ 5 câu truy vấn SQL phân tích dữ liệu chuyên sâu trên Amazon Athena (so sánh chỉ số giữa 3 đô thị, chu kỳ biến thiên ô nhiễm theo 24 giờ UTC, phân bố cấp độ AQI, tính hệ số tương quan Pearson giữa yếu tố khí tượng và PM2.5, trích xuất dữ liệu gốc); viết bộ kiểm thử `test_csv_exports.py`. | **3.0h** | - 5 file truy vấn SQL trong `tuan_2/athena/`.<br>- Module kiểm thử `tests/test_csv_exports.py`.<br>- 5 tệp kết quả CSV xuất từ Athena đạt chuẩn. | **Có dùng AI hỗ trợ**<br>(LLM hỗ trợ gợi ý cú pháp hàm phân tích tương quan thống kê `corr()` trong Athena). |
| **28/09/2026** | **Cả hai thành viên**<br>(Sơn & Quyên) | Xây dựng bộ 28 ca kiểm thử đơn vị tự động (`test_lambda_function.py`, `test_analytics.py`, `test_csv_exports.py`) bao phủ toàn diện các module; chạy kiểm thử đạt 100% PASS; chạy kiểm thử tích hợp thực tế trên tài khoản AWS; hoàn thiện báo cáo kỹ thuật Tuần 2 (DOCX & PDF) và đồng bộ kho GitHub. | **Sơn: 3.0h**<br>**Quyên: 3.0h** | - 28/28 Unit tests PASS.<br>- 156 bản ghi dữ liệu mẫu thu thập thành công.<br>- Báo cáo Tuần 2 hoàn chỉnh (`Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx` & `.pdf`).<br>- Commit Git Tuần 2 trên branch `main`. | **Tự kiểm thử & gỡ lỗi**<br>(Hai sinh viên trực tiếp chạy test suite, kiểm tra kết quả và nghiệm thu báo cáo). |

---

## 3. TỔNG HỢP KẾT QUẢ ĐẠT ĐƯỢC TRONG TUẦN 2

1. **Khối lượng giờ làm việc:**
   - Nguyễn Tiến Sơn (24110054): **10.0 giờ** (vượt chỉ tiêu $\ge 8$ giờ/tuần).
   - Trần Thị Ngọc Quyên (24110051): **9.5 giờ** (vượt chỉ tiêu $\ge 8$ giờ/tuần).
   - Tổng thời gian làm việc nhóm Tuần 2: **19.5 giờ** (vượt chỉ tiêu $\ge 16$ giờ/tuần).
2. **Sản phẩm kỹ thuật bàn giao:**
   - Hàm Lambda `WeatherCollectorLambda` (Python 3.12, 401 dòng) vận hành ổn định, tự động thu thập và chuẩn hóa dữ liệu định kỳ.
   - EventBridge Rule kích hoạt tự động 1 giờ/lần với Resource-based policy an toàn.
   - SNS Alert Topic gửi cảnh báo thời gian thực về email sinh viên khi chất lượng không khí vượt ngưỡng an toàn.
   - S3 Data Lake tổ chức phân vùng Hive-style giúp giảm hơn 95% dữ liệu quét trong các truy vấn Athena.
   - Glue Data Catalog và Athena hoàn tất với Database, Table, View và 5 truy vấn SQL phân tích.
   - Bộ 28 ca kiểm thử đơn vị tự động đạt tỷ lệ 100% PASS trên Python 3.13 / 3.14.
   - Báo cáo kỹ thuật Tuần 2 gồm 29 trang vật lý hoàn chỉnh, 24 bảng biểu, 12 hình vẽ và liên kết GitHub chính thức.

---

## 4. MINH BẠCH VÀ CÔNG KHAI MỨC ĐỘ HỖ TRỢ CỦA TRÍ TUỆ NHÂN TẠO (AI DISCLOSURE)

Tuân thủ nghiêm túc chỉ đạo của GVHD ThS. Huỳnh Xuân Phụng: *"Được dùng LLM/AI (ChatGPT, Claude, Amazon Q Developer...) để tham khảo, sinh mã, gỡ lỗi; nhưng mọi tài nguyên phải được triển khai và chạy thật trên AWS Learner Lab. Ghi rõ phần nào có AI hỗ trợ; SV phải giải thích được mọi cấu hình/mã nguồn khi vấn đáp."*

### 4.1 Phần có sự hỗ trợ của AI:
- **Hỗ trợ sinh mã mẫu (Boilerplate Code):** Sử dụng LLM để tham khảo khung mã gọi HTTP chuẩn bằng thư viện tích hợp sẵn `urllib.request` (không dùng `requests` của bên thứ ba để tránh đóng gói thư viện phụ thuộc cồng kềnh vào Lambda layer).
- **Kiểm tra cú pháp Athena SerDe & SQL:** Tham khảo AI để xác thực các tham số của OpenX JSON SerDe (`org.openx.data.jsonserde.JsonSerDe`) và cú pháp hàm tính hệ số tương quan Pearson `corr(x, y)` trên Presto SQL.
- **Tối ưu hóa bảng biểu báo cáo:** Sử dụng AI hỗ trợ định dạng bảng biểu Markdown và soát lỗi ngữ pháp trong các tài liệu thuyết minh kỹ thuật.

### 4.2 Phần sinh viên tự chủ 100% và chuẩn bị vấn đáp:
- **Giải thích kiến trúc và luồng xử lý:** Hai sinh viên nắm vững và có thể vẽ lại, giải thích từng bước luồng dữ liệu Serverless Event-Driven từ EventBridge -> Lambda -> Secrets Manager -> S3 -> Glue -> Athena -> SNS.
- **Trực tiếp lập trình và gỡ lỗi (Debugging):** Sinh viên tự thiết kế cấu trúc dữ liệu 23 trường, logic phân loại EPA AQI, logic phát hiện và xử lý dữ liệu bị khuyết thiếu (Null handling).
- **Vận hành trên môi trường thật:** Tự chạy toàn bộ các kịch bản triển khai bằng AWS CLI trên tài khoản AWS Academy Learner Lab thật, kiểm tra kết quả ghi trên S3 và xác nhận email cảnh báo SNS nhận được trong hộp thư thực tế.
- **Hiểu sâu về hạch toán chi phí:** Tự phân tích bảng giá AWS Free Tier, tính toán mức tiêu thụ tài nguyên thực tế (~0.40 USD/tháng) và giải thích lý do tại sao kiến trúc Serverless tiết kiệm 98% chi phí so với việc duy trì máy chủ EC2 truyền thống.

---

*Xác nhận của các thành viên Nhóm 05:*
- **Trưởng nhóm:** Nguyễn Tiến Sơn (MSSV: 24110054) - *Đã ký xác nhận*
- **Thành viên:** Trần Thị Ngọc Quyên (MSSV: 24110051) - *Đã ký xác nhận*
