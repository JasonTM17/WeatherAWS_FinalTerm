# Báo cáo Tiến độ — Đề tài: Hệ thống thu thập và phân tích dữ liệu thời tiết/không khí (Nhóm: Domain Apps)

**Học phần**: Điện toán đám mây (Cloud - Đợt 1 - 2026-2027) — Lớp: **261CLCO332779_05**  
**Giảng viên hướng dẫn (GVHD)**: **ThS. Huỳnh Xuân Phụng**  
**Nhóm sinh viên thực hiện (Nhóm 05)**:
- **Nguyễn Tiến Sơn** — MSSV: **24110054** (19,5 giờ)
- **Trần Thị Ngọc Quyên** — MSSV: **24110051** (18,5 giờ)  
**Tổng số giờ thực hiện cả 2 tuần**: **38,0 giờ** (Tuần 1: 18,5 giờ | Tuần 2: 19,5 giờ — đạt định mức $\ge 16$h/tuần/nhóm)

[Repository GitHub](https://github.com/JasonTM17/WeatherAWS_FinalTerm) · [Hồ sơ Tuần 1](tuan_1/README.md) · [Hồ sơ Tuần 2](tuan_2/README.md) · [Worklog chi tiết](docs/WORKLOG.md) · [Mã nguồn & Commit](docs/components.md) · [Kế hoạch Tuần 3](docs/WEEK_3_PLAN.md)

---

> [!IMPORTANT]
> ### 📋 MẪU NỘI DUNG NỘP TRỰC TIẾP LÊN HỆ THỐNG LMS / E-LEARNING
> *(Sinh viên sao chép toàn bộ nội dung khối trích dẫn bên dưới dán trực tiếp vào ô nộp bài LMS theo đúng cấu trúc chuẩn của học phần)*
>
> ---
>
> **NỘI DUNG BÁO CÁO**
>
> Nguyễn Tiến Sơn – MSSV 24110054, Trần Thị Ngọc Quyên – MSSV 24110051 (Nhóm 05, Lớp 261CLCO332779_05) Báo cáo tiến độ Tuần 1 và Tuần 2 – Đề tài “Hệ thống thu thập và phân tích dữ liệu thời tiết/không khí (Nhóm: Domain Apps)”.
>
> Mục tiêu đề tài: Định kỳ thu thập dữ liệu thời tiết và chất lượng không khí từ API công khai (Open-Meteo) cho TP. Hồ Chí Minh, Hà Nội và Đà Nẵng, lưu trữ trên Amazon S3 Data Lake theo phân vùng ngày, tổng hợp phân tích xu hướng bằng Glue/Athena, đồng thời phát hành cảnh báo tức thì qua Amazon SNS khi chỉ số US AQI hoặc nồng độ bụi PM2.5 vượt ngưỡng nguy hại.
>
> Phân công trách nhiệm và khối lượng thời gian làm việc (đối chiếu chuẩn hóa tại worklog.csv): Tuân thủ chặt chẽ định mức học phần (mỗi SV ≥ 8 giờ/tuần; nhóm 2 SV ≥ 16 giờ/tuần), nhóm xác nhận tổng thời gian làm việc kỹ thuật thực tế qua 2 tuần là 38,0 giờ. Cụ thể: Nguyễn Tiến Sơn phụ trách thiết kế S3 Data Lake, cấu hình Secrets Manager, lập trình hàm Lambda Collector, thiết lập EventBridge Scheduler theo giờ, cấu hình Amazon SNS và CloudWatch Alarms/Dashboard (Tuần 1: 9,5h; Tuần 2: 10,0h; Tổng: 19,5h). Trần Thị Ngọc Quyên phụ trách xây dựng AWS Glue Data Catalog, tối ưu hóa Athena Views, phát triển 12 truy vấn SQL phân tích chuyên sâu, xây dựng module xuất CSV an toàn, đối chiếu số liệu 2 tài khoản và trực quan hóa biểu đồ (Tuần 1: 9,0h; Tuần 2: 9,5h; Tổng: 18,5h). Cả hai thành viên cùng phối hợp thiết kế kiến trúc Serverless, đối chiếu dữ liệu độc lập và kiểm thử hồi quy 106 test cases.
>
> Tiến độ triển khai thực tế trên AWS Learner Lab tại Region us-east-1 (sử dụng IAM LabRole có sẵn, gắn tag Project/Owner đầy đủ):
> 1. Tuần 1 (Nền tảng & Xác lập luồng thu thập): Khảo sát API Open-Meteo, thiết kế sơ đồ kiến trúc hệ thống; khởi tạo S3 Data Lake riêng tư với mã hóa SSE-S3 AES256, bật Block Public Access, tổ chức lưu trữ NDJSON phân vùng theo raw/year=YYYY/month=MM/day=DD/; lưu trữ tọa độ và ngưỡng an toàn trong Secrets Manager; khai báo AWS Glue Data Catalog database weather_aqi_db và bảng ngoài weather_airquality_records (20 trường + 3 khóa phân vùng ngày). Đã thu thập và chuẩn hóa bộ mẫu Tuần 1 gồm 156 bản ghi (52 bản ghi/đô thị), thực thi 5/5 truy vấn Athena SUCCEEDED (mỗi truy vấn quét 87.250 bytes) và kết xuất 6 tệp CSV cùng 9 biểu đồ trực quan hóa ban đầu.
> 2. Tuần 2 (Triển khai chức năng lõi, sửa lỗi vận hành & Phân tích 2 tài khoản độc lập):
>    - Triển khai EventBridge Scheduler với Rule kích hoạt định kỳ 1 giờ/lần (rate(1 hour)), gán Target gọi Lambda tự động.
>    - Phát triển hàm Lambda Collector (lambda_function.py, runtime Python 3.12, 256MB, timeout 60s), khắc phục triệt để các lỗi kỹ thuật quan trọng: (a) bổ sung cơ chế quản lý ngân sách thời gian thực thi time-budgeting (context.get_remaining_time_in_millis()) để chủ động ghi dữ liệu các thành phố đã tải lên S3 trước khi chạm timeout; (b) xử lý null-safety (safe_float, safe_int) triệt tiêu lỗi runtime khi API Open-Meteo trả trường rỗng; (c) xây dựng cơ chế bảo vệ file CSV Athena (safe exporter), không ghi đè file rỗng 0-byte khi truy vấn thất bại; (d) chuẩn hóa ghép cặp tương quan khí tượng cùng thời điểm.
>    - Cấu hình Topic Amazon SNS (WeatherAQIAlerts) tự động gửi email cảnh báo khi AQI >= 100 hoặc PM2.5 >= 35.5 µg/m³.
>    - Thiết lập CloudWatch Alarms giám sát lỗi Lambda Errors >= 1 và xây dựng Dashboard hiển thị chỉ số thời gian thực.
>    - Thu thập và đối chiếu thực nghiệm trên 2 tài khoản AWS Learner Lab độc lập của 2 sinh viên (Tiến Sơn: Account 873674852386; Ngọc Quyên: Account 134987931868): lưu trữ tổng cộng 435 bản ghi (204 và 231 bản ghi), tổng hợp thành 27 nhóm đô thị–giờ ở mỗi tài khoản và 21 nhóm cùng giờ đối chiếu độc lập; đợt kiểm chứng mới ngày 16/10 ghi nhận 14/14 câu lệnh SELECT thành công (tăng lên 216 và 249 bản ghi).
> 3. Kết quả phân tích môi trường và ô nhiễm không khí ban đầu: Chất lượng không khí phân hóa rõ nét giữa 3 miền: Hà Nội có AQI trung bình cao nhất đạt 163,3 (cấp Unhealthy — Không lành mạnh), nồng độ bụi mịn PM2.5 trung bình đạt 75,9 µg/m³ với 100% mẫu quan trắc vượt ngưỡng nguy hại, liên tục kích hoạt thông báo cảnh báo qua SNS; TP. Hồ Chí Minh có AQI trung bình 78,5 (cấp Moderate — Trung bình) và PM2.5 trung bình 23,2 µg/m³; Đà Nẵng có chất lượng không khí trong lành nhất với AQI trung bình 35,4 (cấp Good — Tốt) và PM2.5 trung bình 6,4 µg/m³. Quy luật biến thiên theo giờ cho thấy ô nhiễm đạt đỉnh vào 2 khung giờ cao điểm giao thông (07:00–09:00 sáng và 18:00–20:00 tối) kết hợp hiện tượng nghịch nhiệt bề mặt ban đêm. Nồng độ PM2.5 tương quan nghịch rất mạnh với nhiệt độ (r ≈ -0,99) do nhiệt độ cao thúc đẩy đối lưu phân tán bụi, và tương quan thuận rất mạnh với độ ẩm (r ≈ +0,99) do độ ẩm cao khiến các hạt bụi ngưng kết lơ lửng gần mặt đất.
> 4. Kế hoạch Tuần 3 (Tích hợp & Giám sát toàn diện): Tập trung vào 4 trụ cột chiến lược và 8 gói công việc (W3-01 đến W3-08): (1) Vận hành CI/CD Quality Gate tự động hóa 106 bài kiểm thử qua GitHub Actions, kiểm tra tự động schema drift và tính toàn vẹn CSV; (2) Triển khai tính năng Partition Projection trong Athena để loại bỏ lệnh MSCK REPAIR TABLE, đồng thời thử nghiệm chuyển đổi NDJSON sang Apache Parquet nén Snappy kết hợp S3 Intelligent-Tiering giúp giảm 70–80% chi phí quét dữ liệu; (3) Nâng cấp hệ thống cảnh báo đa kênh SNS qua SMS/Webhook (Slack/Discord) và thiết lập CloudWatch Metrics Dashboard thời gian thực theo dõi Invocations, Duration, Errors; (4) Xây dựng mô hình phân tích chuỗi thời gian (time-series forecasting) dự báo xu hướng AQI/PM2.5 theo từng giờ trong 24 giờ tiếp theo.
>
> Cập nhật các link repo:
> - Repo GitHub: https://github.com/JasonTM17/WeatherAWS_FinalTerm
> - Báo cáo nộp lại hoàn chỉnh trên Repo: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/BAO_CAO.md
> - Bảng chấm công chuẩn hóa (worklog.csv): https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv
> - Hồ sơ chi tiết Tuần 1: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/README.md
> - Hồ sơ chi tiết Tuần 2: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/README.md
> - Mã nguồn và commit từng thành phần: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/components.md
> - Kế hoạch Tuần 3 chi tiết: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_3_PLAN.md
> - Nguồn dữ liệu Open-Meteo API: https://open-meteo.com/en/docs/air-quality-api
>
> ---
>
> **AI HỖ TRỢ**
>
> - Công cụ AI sử dụng: ChatGPT, Claude, GitHub Copilot.
> - Mục đích và phạm vi hỗ trợ:
>   + Tham khảo gợi ý thiết kế kiến trúc Serverless Event-driven và cấu trúc luồng dữ liệu trên AWS.
>   + Hỗ trợ cấu trúc boilerplate mã nguồn Python SDK tương tác boto3, PowerShell wrapper scripts và GitHub Actions CI workflow.
>   + Rà soát cú pháp câu lệnh SQL Athena DDL/Views và công thức tính toán thống kê Pearson/Spearman trong xử lý dữ liệu.
>   + Hỗ trợ kiểm tra phát hiện lỗi logic tiềm ẩn (null handling, Lambda remaining execution time budgeting).
> - Cam kết của nhóm sinh viên:
>   + Toàn bộ hạ tầng đám mây và quy trình xử lý dữ liệu đã được nhóm tự cấu hình, kiểm thử và chạy thật 100% trên AWS Learner Lab của 2 sinh viên (Region us-east-1, Account 873674852386 và Account 134987931868).
>   + Cả 2 sinh viên nắm vững toàn bộ mã nguồn, cấu hình IAM LabRole, cơ chế phân vùng S3, câu truy vấn Athena và sẵn sàng giải thích chi tiết khi GVHD vấn đáp đánh giá.
>
> ---

---

## 1. Mục tiêu đề tài và yêu cầu học phần

Đề tài thuộc nhóm **Domain Apps** của học phần **Điện toán đám mây** (Cloud - Đợt 1 - 2026-2027), lớp **261CLCO332779_05**, GVHD **ThS. Huỳnh Xuân Phụng**.

- **Mục tiêu chính**: Định kỳ thu thập dữ liệu thời tiết và chất lượng không khí từ API công khai, lưu trữ, phân tích xu hướng và cảnh báo AQI cao.
- **Sản phẩm dự kiến**: Lambda theo lịch (EventBridge) gọi API công khai → S3 (JSON phân vùng); Glue + Athena phân tích; SNS cảnh báo; biểu đồ xu hướng.
- **Dịch vụ AWS sử dụng**: AWS Lambda, Amazon EventBridge, Amazon S3, AWS Secrets Manager, Amazon SNS, AWS Glue Data Catalog, Amazon Athena, Amazon CloudWatch.
- **Quy chuẩn hạ tầng**: Triển khai trên AWS Learner Lab tại Region `us-east-1`, sử dụng `LabRole` có sẵn, gắn tag `Project=WeatherAWS_FinalTerm` và `Owner=Nhom05`.

---

## 2. Phân công trách nhiệm và số giờ làm việc

Phân công nhiệm vụ và số giờ làm việc thực tế của 2 sinh viên được chuẩn hóa minh bạch tại [worklog.csv](worklog.csv) và tài liệu [docs/WORKLOG.md](docs/WORKLOG.md). Phân công chi tiết Tuần 1 được lưu tại [tuan_1/docs/PHAN_CONG.md](tuan_1/docs/PHAN_CONG.md).

| Sinh viên | MSSV | Trách nhiệm chính được phân công | Tuần 1 | Tuần 2 | Tổng cộng |
| :--- | :---: | :--- | :---: | :---: | :---: |
| **Nguyễn Tiến Sơn** | 24110054 | Thiết kế S3 Data Lake phân vùng ngày, cấu hình Secrets Manager, lập trình hàm Lambda Collector, thiết lập EventBridge Scheduler theo giờ, Amazon SNS cảnh báo ngưỡng ô nhiễm, CloudWatch Alarms & Metrics Dashboard. | 9,5 giờ | 10,0 giờ | **19,5 giờ** |
| **Trần Thị Ngọc Quyên** | 24110051 | Xây dựng AWS Glue Catalog (bảng 20 trường + 3 khóa phân vùng), Athena Unified Views, 12 câu truy vấn SQL phân tích chuyên sâu, phát triển bộ xuất CSV tự động an toàn, phân tích đối chiếu 2 tài khoản (27 CSV) và 20 biểu đồ trực quan. | 9,0 giờ | 9,5 giờ | **18,5 giờ** |
| **Cả hai sinh viên** | Nhóm 05 | Thiết kế kiến trúc tổng thể, kiểm thử hồi quy 106 test cases, đối chiếu chéo dữ liệu 2 tài khoản AWS Learner Lab độc lập, viết báo cáo và hoàn thiện hồ sơ repo. | 18,5 giờ | 19,5 giờ | **38,0 giờ** |

*Định mức học phần*: Mỗi sinh viên $\ge 8,0\text{ giờ/tuần}$; nhóm 2 sinh viên $\ge 16,0\text{ giờ/tuần}$. Nhóm đạt 18,5 giờ (Tuần 1) và 19,5 giờ (Tuần 2), vượt định mức tối thiểu.

---

## 3. Các cải tiến kỹ thuật đã sửa và kết quả phân tích AQI ban đầu

### 3.1. Các sửa lỗi kỹ thuật cốt lõi trong mã nguồn

1. **Quản lý ngân sách thời gian thực thi của Lambda (`time-budgeting`)**:
   - Sử dụng `context.get_remaining_time_in_millis()` trong [tuan_2/lambda/lambda_function.py](tuan_2/lambda/lambda_function.py) để theo dõi thời gian thực thi còn lại. Nếu thời gian dưới ngưỡng an toàn, hàm chủ động dừng thu thập các thành phố tiếp theo và lưu ngay các bản ghi đã lấy thành công lên S3, triệt tiêu nguy cơ Lambda timeout hủy ngang toàn bộ batch dữ liệu.
2. **Cơ chế phân giải dữ liệu an toàn (`null-safety`)**:
   - Triển khai các hàm chuyển đổi `safe_float()` và `safe_int()` trong Lambda, bảo đảm dữ liệu rỗng hoặc sai định dạng từ trạm khí tượng không gây crash `TypeError` hoặc làm hỏng cấu trúc NDJSON.
3. **Bảo vệ tính toàn vẹn của tệp CSV khi Athena gặp sự cố (`safe CSV exporter`)**:
   - Trong [tuan_2/scripts/athena_export.py](tuan_2/scripts/athena_export.py), tệp xuất cũ chỉ được ghi đè sau khi truy vấn mới đạt trạng thái `SUCCEEDED` và kết quả tải về hợp lệ, chống hoàn toàn hiện tượng tạo file rỗng 0-byte khi truy vấn lỗi.
4. **Chuẩn hóa ghép cặp khi phân tích tương quan khí tượng**:
   - Trong [tuan_2/analytics/analyze_week2_accounts.py](tuan_2/analytics/analyze_week2_accounts.py), chỉ những bản ghi có đầy đủ cả 2 chỉ số môi trường từ cùng một quan trắc mới được đưa vào công thức Pearson và Spearman, tránh lệch thời gian quan trắc.

### 3.2. Kết quả phân tích chất lượng không khí (AQI & PM2.5) ban đầu

Dữ liệu thực nghiệm được đối chiếu minh bạch qua các mốc:
- **Tuần 1**: 156 bản ghi chuẩn hóa (52 bản ghi cho mỗi đô thị: TP.HCM, Hà Nội, Đà Nẵng).
- **Tuần 2 (bộ báo cáo đã lưu)**: Tài khoản sinh viên Tiến Sơn lưu **204 bản ghi** (27 bản ghi trong khung Tuần 2); Tài khoản sinh viên Ngọc Quyên lưu **231 bản ghi** (57 bản ghi trong khung Tuần 2). Tổng hợp theo giờ UTC cho **27 nhóm đô thị–giờ** ở mỗi tài khoản và **21 nhóm cùng giờ** để đối chiếu chéo độc lập.
- **Tuần 2 (kiểm chứng AWS mới ngày 16/10/2026)**: 14 câu lệnh SELECT thành công trên cả 2 tài khoản: Tiến Sơn ghi nhận 216 bản ghi (39 bản ghi Tuần 2), Ngọc Quyên ghi nhận 249 bản ghi (75 bản ghi Tuần 2).

#### Bảng so sánh chất lượng không khí giữa hai sinh viên (bộ báo cáo đã lưu):

| Đô thị quan trắc | AQI TB (Tiến Sơn) | AQI TB (Ngọc Quyên) | PM2.5 TB (Tiến Sơn) | PM2.5 TB (Ngọc Quyên) | Đánh giá mức độ ô nhiễm (US AQI) | Tỷ lệ vượt ngưỡng cảnh báo SNS |
| :--- | ---: | ---: | ---: | ---: | ---: | :---: |
| **Hà Nội** | **163,56** | **163,05** | **76,66 µg/m³** | **75,11 µg/m³** | **Unhealthy** (Không lành mạnh) | **100%** (9/9 và 19/19 mẫu) |
| **TP. Hồ Chí Minh** | **78,00** | **79,05** | **23,38 µg/m³** | **22,92 µg/m³** | **Moderate** (Trung bình) | **0%** |
| **Đà Nẵng** | **35,44** | **35,37** | **6,38 µg/m³** | **6,46 µg/m³** | **Good** (Tốt) | **0%** |

*Nguồn dữ liệu đối chiếu*: [city_statistics.csv](tuan_2/results/week2_analysis/city_statistics.csv), [raw_week2_both_accounts.csv](tuan_2/results/week2_analysis/raw_week2_both_accounts.csv), [hourly_city.csv](tuan_2/results/week2_analysis/hourly_city.csv).

![AQI trung bình và độ lệch chuẩn](tuan_2/results/week2_charts/02_aqi_city.png)
![Biến thiên AQI theo giờ](tuan_2/results/week2_charts/05_hourly_aqi.png)

#### Các nhận xét môi trường quan trọng:
1. **Phân hóa không gian**: Hà Nội có mức ô nhiễm bụi mịn PM2.5 nghiêm trọng nhất, liên tục nằm trong ngưỡng Unhealthy; TP.HCM duy trì ở mức trung bình Moderate; Đà Nẵng có chất lượng không khí tốt nhất (Good).
2. **Kích hoạt cảnh báo SNS**: 100% mẫu quan trắc tại Hà Nội vượt ngưỡng (`AQI >= 100` hoặc `PM2.5 >= 35.5 µg/m³`), kích hoạt Lambda công bố thông báo tới Topic Amazon SNS.
3. **Quy luật chu kỳ ngày–đêm (Diurnal Patterns)**: AQI và PM2.5 tăng mạnh vào các khung giờ cao điểm giao thông (07:00–09:00 sáng và 18:00–20:00 chiều tối), đồng thời ban đêm tích tụ bụi do hiện tượng nghịch nhiệt bề mặt.
4. **Tương quan khí tượng**: Nồng độ PM2.5 tương quan nghịch rất mạnh với nhiệt độ ($r \approx -0,99$) và tương quan thuận rất mạnh với độ ẩm ($r \approx +0,99$).

---

## 4. Hệ thống liên kết GitHub (Blob URL & Commit) từng thành phần triển khai

Toàn bộ mã nguồn, script cấu hình, dữ liệu và kiểm thử được lưu trữ minh bạch trên GitHub:

| Thành phần AWS | Tệp mã nguồn trên Repo | Đường dẫn xem trực tiếp (Blob URL) | Vai trò & Chức năng kỹ thuật | Phụ trách | Commit minh chứng |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lambda Collector** | `tuan_2/lambda/lambda_function.py` | [lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py) | Thu thập API Open-Meteo, chuẩn hóa 20 trường, time-budgeting, ghi S3, gửi SNS cảnh báo | Nguyễn Tiến Sơn | [2947d3f](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/2947d3fdf7871ead2b99d486fa1d403a17183948) |
| **EventBridge Scheduler** | `tuan_2/scripts/05_setup_eventbridge.ps1` | [05_setup_eventbridge.ps1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/05_setup_eventbridge.ps1) | Rule lịch trình định kỳ theo giờ (`rate(1 hour)`), gán Target gọi Lambda tự động | Nguyễn Tiến Sơn | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **S3 Data Lake** | `tuan_2/scripts/01_setup_s3.ps1` | [01_setup_s3.ps1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/01_setup_s3.ps1) | Khởi tạo bucket, bật SSE-S3 AES256, chặn Public Access, phân vùng `raw/year=YYYY/month=MM/day=DD/` | Nguyễn Tiến Sơn | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **Secrets Manager** | `tuan_2/scripts/02_setup_secrets.ps1` | [02_setup_secrets.ps1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/02_setup_secrets.ps1) | Lưu trữ an toàn tọa độ 3 thành phố, ngưỡng cảnh báo, chống lộ thông tin hard-code | Nguyễn Tiến Sơn | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **Amazon SNS Alerts** | `tuan_2/scripts/03_setup_sns.ps1` | [03_setup_sns.ps1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/03_setup_sns.ps1) | Topic cảnh báo ô nhiễm nguy hại `WeatherAQIAlerts`, đăng ký nhận email cảnh báo | Nguyễn Tiến Sơn | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **AWS Glue Catalog** | `tuan_2/athena/create_table.sql` | [create_table.sql](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/athena/create_table.sql) | DDL khai báo bảng `weather_airquality_records` với 20 cột và 3 khóa phân vùng ngày | Trần Thị Ngọc Quyên | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **Athena Unified View** | `tuan_2/athena/create_view_vietnam_weather_aqi.sql` | [create_view_vietnam_weather_aqi.sql](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/athena/create_view_vietnam_weather_aqi.sql) | View chuẩn hóa dữ liệu, đổi timestamp sang giờ VN (UTC+7) và phân loại cấp AQI | Trần Thị Ngọc Quyên | [49e9133](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/49e9133346d0a7905dbe0a5976b9ee27b0bca2d8) |
| **12 Athena SQL Queries** | `tuan_2/athena/week2_analysis/` | [week2_analysis/](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/athena/week2_analysis) | 12 câu truy vấn SQL: trích xuất raw, thống kê đô thị, biến thiên giờ, tương quan, chất lượng | Trần Thị Ngọc Quyên | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **CloudWatch Alarms** | `tuan_2/scripts/07_setup_cloudwatch.ps1` | [07_setup_cloudwatch.ps1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/07_setup_cloudwatch.ps1) | Alarm giám sát lỗi Lambda Errors >= 1 và Dashboard theo dõi chỉ số thời gian thực | Nguyễn Tiến Sơn | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **Python SDK Core** | `tuan_2/scripts/aws_project.py` | [aws_project.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/aws_project.py) | Module Python chuẩn hóa tương tác AWS CLI/boto3: quản lý hạ tầng, bảo mật, idempotency | Nguyễn Tiến Sơn | [432add1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/432add13545ff0af1fb86457ccaa1f295b796576) |
| **Athena Exporter** | `tuan_2/scripts/athena_export.py` | [athena_export.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/athena_export.py) | Thực thi truy vấn Athena, phân trang kết quả lớn, xuất CSV an toàn và ghi nhận metrics | Trần Thị Ngọc Quyên | [432add1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/432add13545ff0af1fb86457ccaa1f295b796576) |
| **27 CSV Kết quả phân tích** | `tuan_2/results/week2_analysis/` | [week2_analysis/](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_analysis) | 27 tệp CSV: đối chiếu 2 tài khoản, tương quan Pearson/Spearman, phân vị thống kê | Trần Thị Ngọc Quyên | [351f5be](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/351f5be572e01dfdb6913c3aa39a67e4dd3cb979) |
| **20 Biểu đồ trực quan** | `tuan_2/results/week2_charts/` | [week2_charts/](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_charts) | 20 hình ảnh biểu đồ phân tích thời tiết và ô nhiễm không khí kèm manifest nguồn | Trần Thị Ngọc Quyên | [351f5be](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/351f5be572e01dfdb6913c3aa39a67e4dd3cb979) |
| **Kiểm chứng AWS mới** | `tuan_2/results/review_2026_10_16/` | [review_2026_10_16/](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/review_2026_10_16) | Kết quả kiểm chứng độc lập 16/10: 14 SELECT thành công, cấu hình hạ tầng và SHA-256 | Cả hai sinh viên | [5f43c07](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/5f43c07e0c451da7a956d4993175815a9ffdf22e) |
| **GitHub Actions CI** | `.github/workflows/verify-repository.yml` | [verify-repository.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/.github/workflows/verify-repository.yml) | Pipeline CI tự động hóa chạy kiểm thử 106 test cases và kiểm tra toàn vẹn liên kết/CSV | Cả hai sinh viên | [b78a24d](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/b78a24dc2fb44962a939fbf61a6b095efb58797f) |

Chi tiết thêm xem tại: [docs/components.md](docs/components.md).

---

## 5. Kế hoạch Tuần 3 chi tiết (Tích hợp & Giám sát)

Kế hoạch Tuần 3 bám sát đề cương học phần và được chia thành **4 trụ cột chiến lược** với **8 gói công việc** cụ thể:

### 5.1. Bốn trụ cột chiến lược Tuần 3
1. **Trụ cột 1: Tự động hóa CI/CD Quality Gate**: Vận hành GitHub Actions CI tự động kiểm tra 106 test cases, kiểm tra tự động phát hiện schema drift và tính toàn vẹn CSV.
2. **Trụ cột 2: Tối ưu Athena & S3 Data Lake**: Cấu hình Partition Projection loại bỏ `MSCK REPAIR TABLE`, chuyển đổi dữ liệu NDJSON sang Parquet/ORC nén Snappy kết hợp S3 Intelligent-Tiering giảm 30–40% chi phí.
3. **Trụ cột 3: Nâng cấp cảnh báo đa kênh SNS & Giám sát thời gian thực CloudWatch**: Mở rộng kênh nhận cảnh báo từ Email sang SMS/Webhook (Slack/Discord) và xây dựng CloudWatch Dashboard hiển thị chỉ số thời gian thực.
4. **Trụ cột 4: Mở rộng phân tích dự báo chuỗi thời gian (Time-Series Forecasting)**: Xây dựng mô hình thống kê dự báo xu hướng AQI và PM2.5 theo từng giờ cho 24 giờ tiếp theo.

### 5.2. Bảng phân công 8 gói công việc (W3-01 đến W3-08)
| Mã gói việc | Tên công việc chi tiết | Trụ cột | Sinh viên phụ trách | Sản phẩm bàn giao dự kiến |
| :---: | :--- | :---: | :---: | :--- |
| **W3-01** | Chốt phiên bản mã nguồn và cấu hình triển khai đồng bộ | Trụ cột 1 | Nguyễn Tiến Sơn | Hash SHA-256 mã nguồn và gói zip triển khai trên Lambda |
| **W3-02** | Chuẩn hóa lịch trình EventBridge và quyền gọi hàm | Trụ cột 1 & 2 | Nguyễn Tiến Sơn | Cấu hình Rule/Target chuẩn xác, dọn dẹp rule trùng lặp |
| **W3-03** | Triển khai Partition Projection và Parquet trên S3/Athena | Trụ cột 2 | Trần Thị Ngọc Quyên | Bảng Athena tối ưu với Partition Projection và Parquet |
| **W3-04** | Kiểm định chất lượng dữ liệu và tính liên tục thời gian | Trụ cột 1 & 4 | Trần Thị Ngọc Quyên | Báo cáo kiểm định chất lượng dữ liệu (Data Quality Report) |
| **W3-05** | Thiết lập CloudWatch Metrics Dashboard thời gian thực | Trụ cột 3 | Nguyễn Tiến Sơn | CloudWatch Dashboard JSON và ảnh chụp giao diện vận hành |
| **W3-06** | Nâng cấp cảnh báo đa kênh SNS (Email + SMS/Webhook) | Trụ cột 3 | Nguyễn Tiến Sơn | Cấu hình Topic SNS đa kênh và kiểm thử gửi cảnh báo |
| **W3-07** | Phát triển mô hình dự báo chuỗi thời gian AQI/PM2.5 | Trụ cột 4 | Trần Thị Ngọc Quyên | Script phân tích time-series và biểu đồ dự báo 24 giờ tới |
| **W3-08** | Tích hợp CI/CD tự động và tổng duyệt toàn diện hồ sơ repo | Trụ cột 1 | Cả hai sinh viên | Pipeline GitHub Actions hoàn thiện và README Tuần 3 |

Chi tiết kế hoạch: [docs/WEEK_3_PLAN.md](docs/WEEK_3_PLAN.md).

---

## 6. Hồ sơ Tuần 1 bổ sung liền mạch

- Báo cáo Tuần 1: [tuan_1/README.md](tuan_1/README.md) · [Báo cáo chi tiết Tuần 1](tuan_1/docs/FINAL_REPORT.md) · [Phân công Tuần 1](tuan_1/docs/PHAN_CONG.md)
- Dữ liệu Tuần 1: 156 bản ghi chuẩn hóa, 6 CSV, 9 biểu đồ trực quan tại [tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/](tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/).

---

## 7. Quy trình tái lập và kiểm thử tự động (106 tests PASS)

Toàn bộ hệ thống kiểm tra độc lập gồm **106 test cases** (66 unit tests, 18 analytics tests, 22 acceptance tests) có thể tái lập 100% bằng lệnh:

```powershell
python tuan_2/scripts/repository_audit.py --check
python -m unittest discover -s tuan_2/tests -v
python -m unittest discover -s tuan_2/analytics -p "test_*.py" -v
python -m unittest tests/test_e2e_acceptance.py -v
```
