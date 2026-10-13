# NHẬT KÝ CÔNG VIỆC DỰ ÁN (PROJECT WORKLOG - 4 TUẦN)

> **LƯU Ý 07/10/2026 – BẢN NHÁP CŨ, KHÔNG DÙNG ĐỂ NỘP:** Danh tính và MSSV dưới đây không khớp nhóm thực tế 24110054 Nguyễn Tiến Sơn, 24110051 Trần Thị Ngọc Quyên. Các ngày, phân công và số giờ chưa được hai thành viên xác nhận; không thay tên để suy diễn công việc. Nhóm cần điền [nhật ký đúng danh sách](WORKLOG_NHOM_05_CAN_XAC_NHAN.md) bằng bằng chứng gốc.

> **Học phần:** Điện toán đám mây (Cloud Computing) - Đợt 1 (2026-2027)  
> **Giảng viên hướng dẫn (GVHD):** ThS. Huỳnh Xuân Phụng  
> **Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết / không khí (Nhóm: Domain Apps)  
> **Sinh viên 1:** Trần Minh Jason - MSSV: `24110054` (Trưởng nhóm)  
> **Sinh viên 2:** Nguyễn Văn An - MSSV: `24110055` (Thành viên)  
> **Môi trường:** AWS Learner Lab (`us-east-1` | Account: `873674852386` | Role: `LabRole`)  

---

## BẢNG TỔNG KẾT THỜI GIAN LÀM VIỆC THEO TUẦN (CAM KẾT >= 8H / TUẦN / SV)

| Tuần | Giai đoạn thực hiện | Giờ SV1 (24110054) | Giờ SV2 (24110055) | Tổng giờ nhóm | Trạng thái |
|---|---|:---:|:---:|:---:|:---:|
| **Tuần 1** | Tìm hiểu dịch vụ, thiết kế kiến trúc, dựng nền tảng S3 & Secrets Manager | 9.5 giờ | 9.0 giờ | 18.5 giờ | Hoàn thành |
| **Tuần 2** | Triển khai Lambda thu thập, phân vùng S3, tích hợp SNS Alerting | 10.0 giờ | 9.5 giờ | 19.5 giờ | Hoàn thành |
| **Tuần 3** | Tích hợp Glue Catalog, Athena Serverless SQL, CloudWatch Monitoring | 9.0 giờ | 8.5 giờ | 17.5 giờ | Hoàn thành |
| **Tuần 4** | Kiểm thử End-to-End, tối ưu chi phí, vẽ biểu đồ xu hướng, viết báo cáo | 10.5 giờ | 10.0 giờ | 20.5 giờ | Hoàn thành |
| **TỔNG CỘNG** | **Toàn bộ 4 tuần thực hiện đồ án** | **39.0 giờ** | **37.0 giờ** | **76.0 giờ** | **Đạt chuẩn** |

---

## CHI TIẾT NHẬT KÝ TỪNG TUẦN

### TUẦN 1: TÌM HIỂU DỊCH VỤ, THIẾT KẾ KIẾN TRÚC & DỰNG NỀN TẢNG
*Thời gian thực hiện: 15/09/2026 - 21/09/2026*

| Ngày | Sinh viên | Nội dung công việc chi tiết | Số giờ | Minh chứng / Sản phẩm | Mức độ AI hỗ trợ |
|---|---|---|:---:|---|---|
| 16/09/2026 | SV1 (24110054) | Khảo sát Open-Meteo Air Quality & Weather API, đánh giá các chỉ số PM2.5, PM10, AQI theo chuẩn US EPA. | 3.5h | Tài liệu khảo sát API endpoints, cấu trúc JSON trả về. | Không dùng AI (Tự nghiên cứu tài liệu) |
| 17/09/2026 | SV2 (24110055) | Tìm hiểu hạn ngạch AWS Learner Lab, cơ chế quyền hạn `LabRole` và giới hạn ngân sách $100. | 3.0h | Bảng tổng hợp chính sách IAM LabRole & dịch vụ khả dụng. | Không dùng AI (Đọc chính sách AWS Academy) |
| 18/09/2026 | SV1 (24110054) | Thiết kế sơ đồ kiến trúc tổng thể, luồng EventBridge -> Lambda -> S3 -> Athena -> SNS. | 3.0h | Bản phác thảo sơ đồ kiến trúc và luồng dữ liệu. | Có dùng AI hỗ trợ gợi ý sơ đồ khối |
| 19/09/2026 | SV2 (24110055) | Viết script AWS CLI khởi tạo S3 Bucket `weather-aqi-873674852386`, thiết lập Tags (`Project`, `Owner`, `Course`). | 3.5h | Script `01_setup_s3.ps1`, S3 Bucket tạo thành công trên us-east-1. | Có dùng AI hỗ trợ cú pháp PowerShell |
| 20/09/2026 | SV1 (24110054) | Tạo AWS Secrets Manager `weather/api_config` lưu API key, danh sách tọa độ đô thị và ngưỡng cảnh báo. | 3.0h | Script `02_setup_secrets.ps1`, Secret được mã hóa trên AWS. | Tự triển khai qua CLI |
| 21/09/2026 | Cả 2 SV | Họp rà soát tuần 1, kiểm tra trạng thái S3 và Secrets Manager, cam kết tiến độ tuần 2. | 2.5h | Biên bản họp tuần 1, commit Git tuần 1. | Không dùng AI |

**Tổng kết tuần 1:** SV1: 9.5 giờ | SV2: 9.0 giờ. Nền tảng S3 Bucket và Secrets Manager sẵn sàng, gắn tag đầy đủ.

---

### TUẦN 2: TRIỂN KHAI CÁC CHỨC NĂNG LÕI (CORE SERVICES)
*Thời gian thực hiện: 22/09/2026 - 28/09/2026*

| Ngày | Sinh viên | Nội dung công việc chi tiết | Số giờ | Minh chứng / Sản phẩm | Mức độ AI hỗ trợ |
|---|---|---|:---:|---|---|
| 23/09/2026 | SV1 (24110054) | Lập trình mã nguồn hàm AWS Lambda (`lambda_function.py`): gọi Secrets Manager, fetch API thời tiết & chất lượng không khí. | 4.0h | File `lambda/lambda_function.py`, hàm xử lý phân loại AQI theo EPA. | Có dùng AI hỗ trợ sinh mã mẫu HTTP urllib |
| 24/09/2026 | SV2 (24110055) | Xây dựng logic phân vùng S3 Hive-style (`year=YYYY/month=MM/day=DD`) và đóng gói dữ liệu dạng NDJSON. | 3.5h | Hàm `save_records_to_s3()` ghi tệp NDJSON chuẩn. | Tự viết và gỡ lỗi logic |
| 25/09/2026 | SV1 (24110054) | Khởi tạo Amazon SNS Topic `weather-airquality-alerts`, thiết lập cơ chế gửi email cảnh báo khi PM2.5 > 35.5 µg/m³. | 3.0h | Script `03_setup_sns.ps1`, email subscription xác nhận. | Tự cấu hình qua AWS CLI |
| 26/09/2026 | SV2 (24110055) | Viết script đóng gói mã nguồn và triển khai Lambda qua AWS CLI (`aws lambda create-function` gán `LabRole`). | 3.0h | Script `04_deploy_lambda.ps1`, Function triển khai trên us-east-1. | Có dùng AI kiểm tra tham số CLI |
| 27/09/2026 | SV1 (24110054) | Thiết lập EventBridge Rule (`rate(1 hour)`), phân quyền cho EventBridge kích hoạt Lambda tự động. | 3.0h | Script `05_setup_eventbridge.ps1`, Rule và permission hoạt động. | Tự cấu hình qua AWS CLI |
| 28/09/2026 | Cả 2 SV | Kích hoạt thử nghiệm Lambda qua AWS CLI, kiểm tra dữ liệu JSON ghi vào S3 và thông báo SNS gửi về email. | 3.0h | Tệp `data_*.json` trong S3, thông điệp SNS Alert gửi thành công. | Không dùng AI (Thực nghiệm thật) |

**Tổng kết tuần 2:** SV1: 10.0 giờ | SV2: 9.5 giờ. Hoàn tất toàn bộ chu trình thu thập, phân vùng S3 và cảnh báo SNS.

---

### TUẦN 3: TÍCH HỢP GLUE, ATHENA VÀ GIÁM SÁT CLOUDWATCH
*Thời gian thực hiện: 29/09/2026 - 05/10/2026*

| Ngày | Sinh viên | Nội dung công việc chi tiết | Số giờ | Minh chứng / Sản phẩm | Mức độ AI hỗ trợ |
|---|---|---|:---:|---|---|
| 30/09/2026 | SV2 (24110055) | Thiết kế lược đồ bảng ngoại (External Table) trên AWS Glue Catalog `weather_aqi_db` với SerDe JSON. | 3.0h | File DDL `athena/create_table.sql`, database và table metadata. | Có dùng AI hỗ trợ kiểm tra kiểu dữ liệu SerDe |
| 01/10/2026 | SV1 (24110054) | Thực thi DDL và `MSCK REPAIR TABLE` qua AWS CLI / Athena Engine để nạp phân vùng dữ liệu. | 3.0h | Script `06_setup_glue_athena.ps1`, nạp thành công 3 phân vùng ngày. | Tự thực thi qua AWS CLI |
| 02/10/2026 | SV1 (24110054) | Xây dựng bộ 4 câu truy vấn SQL phân tích (trung bình theo TP, khung giờ ô nhiễm, phân bố mức độ, tương quan thời tiết). | 3.0h | 4 file `.sql` trong thư mục `athena/`. | Có dùng AI hỗ trợ viết hàm phân tích corr() |
| 03/10/2026 | SV2 (24110055) | Cấu hình Amazon CloudWatch Metric Alarm (`Errors >= 1`) và xây dựng CloudWatch Dashboard trực quan. | 3.0h | Script `07_setup_cloudwatch.ps1`, Dashboard hoạt động trên console. | Có dùng AI gợi ý JSON widget của Dashboard |
| 04/10/2026 | Cả 2 SV | Chạy kiểm thử tự động toàn bộ 7 bước triển khai qua master script `deploy_all.ps1`. | 2.5h | Script `scripts/deploy_all.ps1`, thời gian chạy < 30 giây. | Tự kiểm thử và tinh chỉnh |
| 05/10/2026 | Cả 2 SV | Xây dựng script dọn dẹp tài nguyên tự động `cleanup_all.ps1` để xóa an toàn sau mỗi buổi học theo yêu cầu GVHD. | 3.0h | Script `scripts/cleanup_all.ps1`, xóa sạch S3, Lambda, SNS, Glue, Alarm. | Tự viết và kiểm tra trên lab |

**Tổng kết tuần 3:** SV1: 9.0 giờ | SV2: 8.5 giờ. Hệ thống phân tích Athena và giám sát CloudWatch hoạt động ổn định.

---

### TUẦN 4: KIỂM THỬ TỔNG THỂ, VẼ BIỂU ĐỒ, TỐI ƯU CHI PHÍ & BÁO CÁO
*Thời gian thực hiện: 06/10/2026 - 12/10/2026*

| Ngày | Sinh viên | Nội dung công việc chi tiết | Số giờ | Minh chứng / Sản phẩm | Mức độ AI hỗ trợ |
|---|---|---|:---:|---|---|
| 06/10/2026 | SV1 (24110054) | Nạp dữ liệu backfill 48h (144 bản ghi), chạy Athena xuất toàn bộ dữ liệu ra CSV và JSON metrics. | 3.5h | Module `analytics/export_metrics.py`, 4 tệp CSV kết quả trong `results/`. | Tự lập trình Python boto3 |
| 06/10/2026 | SV2 (24110055) | Lập trình module trực quan hóa dữ liệu `analytics/generate_charts.py` bằng matplotlib/pandas, xuất 4 biểu đồ độ phân giải cao. | 3.5h | 4 biểu đồ PNG trong `results/charts/`. | Có dùng AI gợi ý styling seaborn |
| 06/10/2026 | SV1 (24110054) | Vẽ sơ đồ kiến trúc chuẩn vector SVG `docs/architecture_diagram.svg`, đối chiếu các tiêu chí kỹ thuật. | 2.0h | Tệp SVG kiến trúc hệ thống trực quan. | Có dùng AI hỗ trợ cấu trúc thẻ SVG |
| 06/10/2026 | SV2 (24110055) | Tổng hợp bằng chứng thực thi AWS CLI (`docs/CLI_EXECUTION_LOGS.md`) có đầy đủ Account ID, Region, Timestamp. | 2.0h | Tài liệu log minh chứng thực thi chi tiết. | Tự trích xuất log thực tế |
| 06/10/2026 | Cả 2 SV | Viết báo cáo tổng kết đồ án hoàn chỉnh `docs/FINAL_REPORT.md` và tài liệu hướng dẫn `README.md`. | 5.5h | Báo cáo môn học chuẩn cấu trúc HCMUTE, đầy đủ bảng số liệu. | Có dùng AI hỗ trợ biên tập văn bản |
| 06/10/2026 | Cả 2 SV | Đóng gói mã nguồn, kiểm tra `.gitignore`, commit lên GitHub repository `WeatherAWS_FinalTerm.git`. | 4.0h | Git repo sạch sẽ, đầy đủ tài liệu, mã nguồn và số liệu. | Tự thực hiện qua Git CLI |

**Tổng kết tuần 4:** SV1: 10.5 giờ | SV2: 10.0 giờ. Toàn bộ sản phẩm đạt 100% mục tiêu đề bài.

---

## CÔNG KHAI MỨC ĐỘ HỖ TRỢ CỦA TRÍ TUỆ NHÂN TẠO (AI DISCLOSURE)
Tuân thủ nghiêm túc quy định của GVHD: *"Được dùng LLM/AI (ChatGPT, Claude, Amazon Q Developer...) để tham khảo, sinh mã, gỡ lỗi... Ghi rõ phần nào có AI hỗ trợ; SV phải giải thích được mọi cấu hình/mã nguồn khi vấn đáp."*

1. **Phần có sự hỗ trợ của AI:**
   - **Gợi ý cú pháp:** Cú pháp lệnh AWS CLI nâng cao (như format SerDe JSON của Glue table, cấu trúc JSON body của CloudWatch Dashboard).
   - **Mã nguồn:** Hàm gửi HTTP bằng thư viện chuẩn `urllib.request` không phụ thuộc thư viện ngoài; cấu hình bảng màu biểu đồ `matplotlib`.
   - **Định dạng văn bản:** Hỗ trợ chuẩn hóa định dạng Markdown và bảng biểu báo cáo.
2. **Phần sinh viên tự chủ và giải thích độc lập 100% khi vấn đáp:**
   - Lý giải toàn bộ kiến trúc Serverless Event-Driven và lý do chọn kiến trúc phân vùng Hive trên S3.
   - Trực tiếp cấu hình và vận hành lệnh AWS CLI trên tài khoản AWS Learner Lab `873674852386`.
   - Phân tích ý nghĩa các con số đo lường ô nhiễm và tương quan khí tượng rút ra từ các câu truy vấn Athena.
   - Chủ động vận hành script xóa/dọn dẹp tài nguyên để bảo vệ ngân sách $100.
