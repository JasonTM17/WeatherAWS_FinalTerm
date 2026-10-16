# Báo cáo Nộp lại Tiến độ Tuần 2 — Dự án AWS Serverless Data Pipeline

**Học phần**: Điện toán đám mây (Cloud Computing) — Lớp: **261CLCO332779_05**  
**Giảng viên hướng dẫn**: **ThS. Huỳnh Xuân Phụng**  
**Nhóm sinh viên thực hiện (Nhóm 05)**:
- **Nguyễn Tiến Sơn** — MSSV: **24110054** (19,5 giờ)
- **Trần Thị Ngọc Quyên** — MSSV: **24110051** (18,5 giờ)  
**Tổng số giờ thực hiện**: **38,0 giờ** (Tuần 1: 18,5 giờ | Tuần 2: 19,5 giờ)

[Repository GitHub](https://github.com/JasonTM17/WeatherAWS_FinalTerm) · [Hồ sơ Tuần 1](tuan_1/README.md) · [Hồ sơ Tuần 2](tuan_2/README.md) · [Worklog chi tiết](docs/WORKLOG.md) · [Kế hoạch Tuần 3](docs/WEEK_3_PLAN.md)

---

> [!IMPORTANT]
> ### 📋 MẪU BÁO CÁO NỘP TRỰC TIẾP LÊN HỆ THỐNG LMS / E-LEARNING
> *(Sinh viên sao chép toàn bộ nội dung khối trích dẫn bên dưới dán trực tiếp vào ô nộp bài LMS để GVHD kiểm chứng tức thì toàn bộ minh chứng trên GitHub)*
>
> ---
> **KÍNH GỬI THẦY HUỲNH XUÂN PHỤNG — BÁO CÁO BỔ SUNG TIẾN ĐỘ TUẦN 2 (NHÓM 05)**  
> - **Lớp học phần**: 261CLCO332779_05 — Điện toán đám mây  
> - **Sinh viên 1**: Nguyễn Tiến Sơn — MSSV: 24110054 (19,5 giờ)  
> - **Sinh viên 2**: Trần Thị Ngọc Quyên — MSSV: 24110051 (18,5 giờ)  
> - **Tổng số giờ làm việc**: 38,0 giờ (Tuần 1: 18,5h, Tuần 2: 19,5h) — xác nhận tại: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv  
> - **GitHub Repository chính thức**: https://github.com/JasonTM17/WeatherAWS_FinalTerm  
> - **Báo cáo nộp lại hoàn chỉnh**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/BAO_CAO_NOP_LAI.md  
>
> **1. Phân công trách nhiệm và số giờ của từng sinh viên**:
> - **Nguyễn Tiến Sơn (24110054 — 19,5h)**: Thiết kế S3 Data Lake phân vùng ngày, cấu hình Secrets Manager, lập trình Lambda Collector, cấu hình Amazon SNS cảnh báo ngưỡng, thiết lập EventBridge Scheduler theo giờ, CloudWatch Alarms & Dashboard.
> - **Trần Thị Ngọc Quyên (24110051 — 18,5h)**: Xây dựng AWS Glue Catalog (bảng 20 cột + 3 phân vùng), tối ưu Athena Views & 12 SQL phân tích chuyên sâu, phát triển bộ xuất CSV tự động, thực hiện phân tích dữ liệu 2 tài khoản (27 CSV) và trực quan hóa 20 biểu đồ môi trường.
> - **Cả hai sinh viên (38,0h)**: Thiết kế kiến trúc tổng thể, kiểm thử độc lập 106 test cases, đối chiếu chéo dữ liệu 2 tài khoản AWS Learner Lab, hoàn thiện hồ sơ báo cáo.  
> - Minh chứng phân công: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WORKLOG.md
>
> **2. Mô tả các lỗi kỹ thuật đã sửa và kết quả phân tích AQI ban đầu**:
> - **Phần kỹ thuật đã sửa**: (a) Bổ sung cơ chế quản lý ngân sách thời gian thu thập Lambda (`context.get_remaining_time_in_millis()`), đảm bảo ghi nhận các thành phố đã lấy thành công vào S3 trước khi chạm timeout; (b) Xử lý null-safety parsing (`safe_float`, `safe_int`) triệt tiêu lỗi runtime khi API Open-Meteo trả trường rỗng; (c) Bảo vệ dữ liệu xuất Athena an toàn, không ghi đè tệp CSV rỗng khi truy vấn lỗi; (d) Chuẩn hóa ghép cặp tương quan khí tượng theo cùng thời điểm quan trắc.
> - **Kết quả phân tích AQI ban đầu (3 đô thị Việt Nam)**:
>   + **Hà Nội**: AQI TB ~163,3 (cấp Unhealthy — Không lành mạnh), PM2.5 TB ~75,9 µg/m³. 100% các mẫu thu thập đều vượt ngưỡng cảnh báo (`AQI >= 100` hoặc `PM2.5 >= 35.5 µg/m³`), kích hoạt thông báo SNS.
>   + **TP. Hồ Chí Minh**: AQI TB ~78,5 (cấp Moderate — Trung bình), PM2.5 TB ~23,2 µg/m³.
>   + **Đà Nẵng**: AQI TB ~35,4 (cấp Good — Tốt), PM2.5 TB ~6,4 µg/m³.
>   + **Quy luật biến thiên & tương quan**: Ô nhiễm đạt đỉnh vào khung giờ cao điểm sáng (07:00–09:00 UTC+7) và chiều tối (18:00–20:00 UTC+7). PM2.5 có tương quan nghịch rất mạnh với nhiệt độ ($r \approx -0,99$) và tương quan thuận rất mạnh với độ ẩm ($r \approx +0,99$).
>
> **3. Bảng liên kết trực tiếp mã nguồn (Blob) và commit minh chứng từng thành phần AWS**:
> - **Lambda Collector**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py (Commit: 2947d3f)
> - **EventBridge Scheduler**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/05_setup_eventbridge.ps1 (Commit: beb5817)
> - **S3 Data Lake**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/01_setup_s3.ps1 (Commit: beb5817)
> - **Secrets Manager**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/02_setup_secrets.ps1 (Commit: beb5817)
> - **Amazon SNS Alert**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/03_setup_sns.ps1 (Commit: beb5817)
> - **AWS Glue Data Catalog**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/athena/create_table.sql (Commit: beb5817)
> - **Athena Unified View**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/athena/create_view_vietnam_weather_aqi.sql (Commit: 49e9133)
> - **12 Athena SQL Queries**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/athena/week2_analysis (Commit: beb5817)
> - **CloudWatch Alarms & Metrics**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/07_setup_cloudwatch.ps1 (Commit: beb5817)
> - **Python SDK & Exporter**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/aws_project.py (Commit: 432add1)
> - **27 CSV Kết quả phân tích**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_analysis (Commit: 351f5be)
> - **20 Biểu đồ trực quan**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_charts (Commit: 351f5be)
> - **GitHub Actions CI & 106 Tests**: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/.github/workflows/verify-repository.yml (Commit: b78a24d)
>
> **4. Kế hoạch Tuần 3 (Tích hợp & Giám sát)**:
> - **Trụ cột 1 (CI/CD Quality Gate)**: Tự động hóa kiểm thử hồi quy 106 test cases qua GitHub Actions, kiểm tra tự động schema drift và tính toàn vẹn CSV.
> - **Trụ cột 2 (Tối ưu Athena & S3 Data Lake)**: Triển khai Partition Projection tăng tốc Athena và chuyển đổi dữ liệu thô NDJSON sang Parquet/ORC nén Snappy kết hợp S3 Intelligent-Tiering giảm 30–40% chi phí.
> - **Trụ cột 3 (Cảnh báo đa kênh SNS & Giám sát thời gian thực)**: Mở rộng cảnh báo SNS qua SMS/Webhook/Slack và xây dựng CloudWatch Dashboard hiển thị chỉ số thời gian thực (Invocations, Errors, Duration).
> - **Trụ cột 4 (Phân tích nâng cao & Dự báo chuỗi thời gian)**: Mở rộng mô hình phân tích chuỗi thời gian (time-series forecasting) dự báo xu hướng AQI/PM2.5 theo giờ.
> - Kế hoạch W3-01 -> W3-08: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_3_PLAN.md
>
> **5. Hồ sơ Tuần 1 bổ sung liền mạch**:
> - Báo cáo nền tảng Tuần 1: https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1
> - Báo cáo chi tiết Tuần 1: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/FINAL_REPORT.md
> ---

---

## 1. Phân công chi tiết từng sinh viên và số giờ cụ thể

Hệ thống ghi nhận và đối chiếu thời gian làm việc được chuẩn hóa qua tệp [worklog.csv](worklog.csv) và tài liệu [docs/WORKLOG.md](docs/WORKLOG.md). Phân công chi tiết nền tảng Tuần 1 được lưu tại [tuan_1/docs/PHAN_CONG.md](tuan_1/docs/PHAN_CONG.md) và [tuan_1/docs/PHAN_CONG_NHOM_05.md](tuan_1/docs/PHAN_CONG_NHOM_05.md).

| Sinh viên | MSSV | Trách nhiệm chính được phân công | Tuần 1 | Tuần 2 | Tổng cộng |
| :--- | :---: | :--- | :---: | :---: | :---: |
| **Nguyễn Tiến Sơn** | 24110054 | Thiết lập S3 Data Lake phân vùng ngày, Secrets Manager bảo mật tọa độ, Lambda Function thu thập chuẩn hóa dữ liệu, Amazon SNS cảnh báo ngưỡng ô nhiễm, EventBridge Scheduler theo giờ, CloudWatch Alarms & Metrics Dashboard. | 9,5 giờ | 10,0 giờ | **19,5 giờ** |
| **Trần Thị Ngọc Quyên** | 24110051 | Xây dựng AWS Glue Data Catalog (bảng 20 trường + 3 khóa phân vùng), Athena Views thống nhất dữ liệu, 12 truy vấn Athena phân tích sâu, bộ xuất CSV tự động an toàn, phân tích tương quan/chu kỳ (27 CSV) và 20 biểu đồ trực quan. | 9,0 giờ | 9,5 giờ | **18,5 giờ** |
| **Cả hai sinh viên** | Nhóm 05 | Thiết kế kiến trúc tổng thể hệ thống Serverless, tích hợp liên thông dịch vụ, đối chiếu dữ liệu giữa 2 tài khoản AWS độc lập, kiểm thử hồi quy 106 test cases và biên soạn hồ sơ báo cáo. | 18,5 giờ | 19,5 giờ | **38,0 giờ** |

*Ghi chú*: Số giờ trên là tổng thời gian lao động kỹ thuật thực tế của từng sinh viên đã được nhóm xác nhận qua từng tuần; dòng "Cả hai sinh viên" là tổng số giờ của cả hai bạn cộng lại (không tính trùng lặp).

---

## 2. Mô tả cụ thể phần kỹ thuật đã sửa và kết quả phân tích AQI ban đầu

### 2.1. Các cải tiến và sửa lỗi kỹ thuật trong mã nguồn

Trong quá trình vận hành pipeline thực tế trên AWS, nhóm đã phát hiện và khắc phục các vấn đề kỹ thuật quan trọng sau:

1. **Quản lý ngân sách thời gian thực thi của Lambda (`time-budgeting`)**:
   - *Vấn đề*: Khi API Open-Meteo phản hồi chậm hoặc nghẽn mạng, Lambda có nguy cơ chạm ngưỡng timeout (60s) làm hủy ngang toàn bộ batch dữ liệu đã tải của các thành phố trước đó.
   - *Giải pháp*: Sử dụng `context.get_remaining_time_in_millis()` để theo dõi thời gian còn lại. Nếu thời gian thực thi dưới ngưỡng an toàn, hàm chủ động dừng thu thập các thành phố tiếp theo và lưu ngay các bản ghi đã thu thập thành công lên S3, tránh hoàn toàn tình trạng mất dữ liệu. Chi tiết tại [tuan_2/lambda/lambda_function.py](tuan_2/lambda/lambda_function.py).
2. **Cơ chế phân giải dữ liệu an toàn chống crash (`null-safety`)**:
   - *Vấn đề*: Các trạm khí tượng hoặc mô hình CAMS đôi khi trả về trường `null`, `NaN` hoặc chuỗi không hợp lệ, dẫn đến lỗi `TypeError` hoặc làm hỏng định dạng NDJSON.
   - *Giải pháp*: Triển khai các hàm chuyển đổi an toàn `safe_float()` và `safe_int()` trong Lambda, đảm bảo dữ liệu luôn đúng kiểu float/int hoặc `None` chuẩn mực.
3. **Bảo vệ tính toàn vẹn của tệp CSV khi Athena gặp sự cố (`safe CSV exporter`)**:
   - *Vấn đề*: Trong phiên bản cũ, nếu Athena truy vấn thất bại (timeout, lỗi mạng, hủy truy vấn), tệp CSV cũ có thể bị xóa hoặc ghi đè bằng tệp rỗng 0-byte.
   - *Giải pháp*: Trong [tuan_2/scripts/athena_export.py](tuan_2/scripts/athena_export.py), tệp xuất cũ chỉ được ghi đè sau khi truy vấn mới đạt trạng thái `SUCCEEDED` và kết quả tải về hợp lệ.
4. **Chuẩn hóa cặp dữ liệu khi phân tích tương quan khí tượng**:
   - *Vấn đề*: Việc ghép cặp độc lập giữa các mảng dữ liệu có thể dẫn đến lệch chỉ số thời gian giữa nhiệt độ/độ ẩm và nồng độ PM2.5.
   - *Giải pháp*: Trong [tuan_2/analytics/analyze_week2_accounts.py](tuan_2/analytics/analyze_week2_accounts.py), chỉ những bản ghi có đầy đủ cả 2 trường từ cùng một quan trắc mới được đưa vào công thức Pearson và Spearman.

### 2.2. Kết quả phân tích chất lượng không khí (AQI & PM2.5) ban đầu

Dữ liệu được đối chiếu qua 3 mốc thực nghiệm rõ ràng:
- **Tuần 1**: 156 bản ghi chuẩn hóa (52 bản ghi cho mỗi đô thị: TP.HCM, Hà Nội, Đà Nẵng).
- **Tuần 2 (bộ báo cáo đã lưu)**: Tài khoản sinh viên Tiến Sơn lưu **204 bản ghi** (27 bản ghi trong khung Tuần 2); Tài khoản sinh viên Ngọc Quyên lưu **231 bản ghi** (57 bản ghi trong khung Tuần 2). Tổng hợp theo giờ UTC cho **27 nhóm đô thị–giờ** ở mỗi tài khoản và **21 nhóm cùng giờ** để đối chiếu chéo độc lập.
- **Tuần 2 (kiểm chứng AWS mới ngày 16/10/2026)**: Đọc lại 14 câu lệnh SELECT thành công trên cả 2 tài khoản: Tiến Sơn ghi nhận 216 bản ghi (39 bản ghi Tuần 2), Ngọc Quyên ghi nhận 249 bản ghi (75 bản ghi Tuần 2).

#### Bảng so sánh chất lượng không khí giữa hai sinh viên (bộ báo cáo đã lưu):

| Đô thị quan trắc | AQI TB (Tiến Sơn) | AQI TB (Ngọc Quyên) | PM2.5 TB (Tiến Sơn) | PM2.5 TB (Ngọc Quyên) | Đánh giá mức độ ô nhiễm (US AQI) | Tỷ lệ vượt ngưỡng cảnh báo SNS |
| :--- | ---: | ---: | ---: | ---: | :---: | :---: |
| **Hà Nội** | **163,56** | **163,05** | **76,66 µg/m³** | **75,11 µg/m³** | **Unhealthy** (Không lành mạnh) | **100%** (9/9 và 19/19 mẫu) |
| **TP. Hồ Chí Minh** | **78,00** | **79,05** | **23,38 µg/m³** | **22,92 µg/m³** | **Moderate** (Trung bình) | **0%** |
| **Đà Nẵng** | **35,44** | **35,37** | **6,38 µg/m³** | **6,46 µg/m³** | **Good** (Tốt) | **0%** |

*Nguồn dữ liệu đối chiếu*: [city_statistics.csv](tuan_2/results/week2_analysis/city_statistics.csv), [raw_week2_both_accounts.csv](tuan_2/results/week2_analysis/raw_week2_both_accounts.csv), [hourly_city.csv](tuan_2/results/week2_analysis/hourly_city.csv), [matched_account_hours.csv](tuan_2/results/week2_analysis/matched_account_hours.csv).

![AQI trung bình và độ lệch chuẩn giữa hai tài khoản](tuan_2/results/week2_charts/02_aqi_city.png)

![Biến thiên chỉ số AQI theo khung giờ trong ngày](tuan_2/results/week2_charts/05_hourly_aqi.png)

#### Các nhận xét môi trường quan trọng:
1. **Phân hóa địa lý rõ rệt**: Hà Nội có nồng độ bụi mịn PM2.5 và chỉ số AQI cao nhất trong cả 3 đô thị, luôn nằm trong ngưỡng Unhealthy. Ngược lại, Đà Nẵng có chất lượng không khí trong lành nhất, thuộc cấp Good. TP. Hồ Chí Minh duy trì ở mức Moderate.
2. **Kích hoạt cảnh báo tự động SNS**: 100% mẫu quan trắc tại Hà Nội thỏa mãn điều kiện ngưỡng cảnh báo (`AQI >= 100` hoặc `PM2.5 >= 35.5 µg/m³`), kích hoạt Lambda gửi thông báo cảnh báo ô nhiễm tới Topic Amazon SNS.
3. **Quy luật chu kỳ ngày–đêm (Diurnal Patterns)**: AQI và PM2.5 tăng mạnh vào các khung giờ cao điểm giao thông (07:00–09:00 sáng và 18:00–20:00 chiều tối), đồng thời ban đêm tích tụ bụi do hiện tượng nghịch nhiệt bề mặt.
4. **Tương quan khí tượng**: Nồng độ PM2.5 tương quan nghịch rất mạnh với nhiệt độ bề mặt ($r \approx -0,99$), cho thấy nhiệt độ cao thúc đẩy đối lưu không khí làm phân tán bụi; ngược lại, PM2.5 tương quan thuận rất mạnh với độ ẩm ($r \approx +0,99$), độ ẩm cao làm các hạt bụi ngưng kết và lơ lửng lâu hơn trong tầng khí quyển sát mặt đất.

---

## 3. Hệ thống liên kết GitHub đầy đủ (Repository, Blob, Commit) từng thành phần triển khai

Toàn bộ mã nguồn, cấu hình hạ tầng AWS, tệp dữ liệu phân tích và bài kiểm thử được lưu trữ minh bạch trên GitHub. Thầy có thể nhấp trực tiếp vào từng liên kết Blob để xem mã nguồn hoặc liên kết Commit để kiểm chứng lịch sử triển khai:

| Thành phần AWS | Tệp mã nguồn / Thư mục trên Repo | Đường dẫn xem mã nguồn trực tiếp (Blob URL) | Vai trò & Chức năng kỹ thuật | Phụ trách chính | Commit minh chứng trên GitHub |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lambda Collector** | `tuan_2/lambda/lambda_function.py` | [lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py) | Thu thập API Open-Meteo, chuẩn hóa 20 trường, kiểm tra ngân sách thời gian, ghi S3, gửi SNS cảnh báo | Nguyễn Tiến Sơn | [2947d3f](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/2947d3fdf7871ead2b99d486fa1d403a17183948) |
| **EventBridge Scheduler** | `tuan_2/scripts/05_setup_eventbridge.ps1` | [05_setup_eventbridge.ps1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/05_setup_eventbridge.ps1) | Thiết lập Rule lịch trình chạy định kỳ theo giờ (`rate(1 hour)`), gán Target gọi Lambda tự động | Nguyễn Tiến Sơn | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **S3 Data Lake** | `tuan_2/scripts/01_setup_s3.ps1` | [01_setup_s3.ps1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/01_setup_s3.ps1) | Khởi tạo S3 bucket lưu trữ NDJSON phân vùng theo `raw/year=YYYY/month=MM/day=DD/`, mã hóa AES256, chặn Public Access | Nguyễn Tiến Sơn | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **Secrets Manager** | `tuan_2/scripts/02_setup_secrets.ps1` | [02_setup_secrets.ps1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/02_setup_secrets.ps1) | Quản lý Secret cấu hình an toàn (tọa độ thành phố, ngưỡng AQI, topic ARN), chống rò rỉ hard-code | Nguyễn Tiến Sơn | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **Amazon SNS Alerts** | `tuan_2/scripts/03_setup_sns.ps1` | [03_setup_sns.ps1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/03_setup_sns.ps1) | Tạo Topic cảnh báo ô nhiễm không khí nguy hại (`WeatherAQIAlerts`), đăng ký thuê bao nhận email | Nguyễn Tiến Sơn | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **AWS Glue Catalog** | `tuan_2/athena/create_table.sql` | [create_table.sql](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/athena/create_table.sql) | DDL khai báo bảng `weather_airquality_records` với 20 cột dữ liệu và 3 khóa phân vùng ngày | Trần Thị Ngọc Quyên | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **Athena Unified View** | `tuan_2/athena/create_view_vietnam_weather_aqi.sql` | [create_view_vietnam_weather_aqi.sql](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/athena/create_view_vietnam_weather_aqi.sql) | View chuẩn hóa dữ liệu, đổi timestamp UTC sang giờ Việt Nam (UTC+7) và phân loại cấp độ AQI | Trần Thị Ngọc Quyên | [49e9133](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/49e9133346d0a7905dbe0a5976b9ee27b0bca2d8) |
| **12 Athena SQL Queries** | `tuan_2/athena/week2_analysis/` | [week2_analysis/](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/athena/week2_analysis) | 12 câu truy vấn SQL: trích xuất raw, thống kê đô thị, biến thiên giờ, tương quan khí tượng, chất lượng dữ liệu | Trần Thị Ngọc Quyên | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **CloudWatch Alarms** | `tuan_2/scripts/07_setup_cloudwatch.ps1` | [07_setup_cloudwatch.ps1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/07_setup_cloudwatch.ps1) | Cấu hình Alarm giám sát lỗi Lambda Errors >= 1 và thiết lập Dashboard theo dõi thời gian thực | Nguyễn Tiến Sơn | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| **Python SDK Core** | `tuan_2/scripts/aws_project.py` | [aws_project.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/aws_project.py) | Module Python chuẩn hóa tương tác AWS CLI/boto3: quản lý hạ tầng, bảo mật thông tin, idempotency | Nguyễn Tiến Sơn | [432add1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/432add13545ff0af1fb86457ccaa1f295b796576) |
| **Athena Exporter** | `tuan_2/scripts/athena_export.py` | [athena_export.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/scripts/athena_export.py) | Tự động thực thi truy vấn Athena, phân trang kết quả lớn, xuất CSV an toàn và ghi nhận metrics | Trần Thị Ngọc Quyên | [432add1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/432add13545ff0af1fb86457ccaa1f295b796576) |
| **27 CSV Kết quả phân tích** | `tuan_2/results/week2_analysis/` | [week2_analysis/](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_analysis) | 27 tệp CSV phân tích: đối chiếu 2 tài khoản, tương quan Pearson/Spearman, phân vị thống kê, chất lượng dữ liệu | Trần Thị Ngọc Quyên | [351f5be](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/351f5be572e01dfdb6913c3aa39a67e4dd3cb979) |
| **20 Biểu đồ trực quan** | `tuan_2/results/week2_charts/` | [week2_charts/](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_charts) | 20 hình ảnh trực quan hóa chuyên sâu phân tích thời tiết và ô nhiễm không khí kèm manifest nguồn | Trần Thị Ngọc Quyên | [351f5be](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/351f5be572e01dfdb6913c3aa39a67e4dd3cb979) |
| **Kiểm chứng AWS mới** | `tuan_2/results/review_2026_10_16/` | [review_2026_10_16/](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/review_2026_10_16) | Kết quả kiểm chứng độc lập ngày 16/10/2026: 14 SELECT thành công, thông số hạ tầng và manifest hash | Cả hai sinh viên | [5f43c07](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/5f43c07e0c451da7a956d4993175815a9ffdf22e) |
| **GitHub Actions CI** | `.github/workflows/verify-repository.yml` | [verify-repository.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/.github/workflows/verify-repository.yml) | Pipeline tự động hóa chạy kiểm tra 106 test cases và kiểm tra tính toàn vẹn liên kết/dữ liệu trên GitHub | Cả hai sinh viên | [b78a24d](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/b78a24dc2fb44962a939fbf61a6b095efb58797f) |

---

## 4. Kế hoạch Tuần 3 chi tiết (Tích hợp & Giám sát)

Kế hoạch Tuần 3 được xây dựng dựa trên 4 trụ cột chiến lược kỹ thuật nhằm hoàn thiện hệ thống, chuẩn hóa giám sát và mở rộng phân tích dự báo:

### 4.1. Bốn trụ cột chiến lược Tuần 3

1. **Trụ cột 1: Tích hợp CI/CD tự động hóa kiểm thử và kiểm tra chất lượng dữ liệu**:
   - Vận hành GitHub Actions CI tự động kiểm tra cú pháp, đơn vị (66 unit tests), phân tích (18 analytics tests) và nghiệm thu e2e (22 acceptance tests) tại mỗi Pull Request / Commit.
   - Bổ sung kiểm tra tự động phát hiện lệch lược đồ dữ liệu (schema drift) và tính hợp lệ của tệp CSV phân vùng.
2. **Trụ cột 2: Tối ưu hóa hiệu năng Athena và chi phí S3 Data Lake**:
   - Cấu hình tính năng **Partition Projection** trong AWS Glue/Athena để loại bỏ thao tác `MSCK REPAIR TABLE`, giảm đáng kể thời gian lập kế hoạch truy vấn và chi phí quét siêu dữ liệu.
   - Thử nghiệm chuyển đổi dữ liệu thô NDJSON sang định dạng **Apache Parquet / ORC** nén Snappy theo cột, giúp giảm 70–80% dung lượng quét và tiết kiệm chi phí truy vấn Athena.
   - Thiết lập quy tắc vòng đời **S3 Intelligent-Tiering / Glacier Flexible Retrieval** để tối ưu hóa chi phí lưu trữ dữ liệu lịch sử dài hạn.
3. **Trụ cột 3: Nâng cấp hệ thống cảnh báo đa kênh SNS và giám sát thời gian thực CloudWatch**:
   - Mở rộng kênh nhận cảnh báo từ Email sang SMS và tích hợp Webhook thông báo tới kênh trao đổi của nhóm (Slack / Discord).
   - Chuẩn hóa CloudWatch Metric Filters và Custom Dashboard theo dõi trực quan các chỉ số vận hành thời gian thực: số lần gọi Lambda (Invocations), tỷ lệ lỗi (Error Rate), thời lượng thực thi (Duration) và số lượng thông báo SNS phát hành (NumberOfMessagesPublished).
4. **Trụ cột 4: Mở rộng phân tích dự báo chuỗi thời gian (Time-Series Forecasting)**:
   - Xây dựng mô hình thống kê dự báo chuỗi thời gian (ARIMA / Moving Average / Exponential Smoothing) cho chỉ số AQI và nồng độ PM2.5 theo từng giờ trong 24 giờ tiếp theo.
   - Đánh giá độ chính xác của mô hình dự báo so với dữ liệu thực tế thu thập được.

### 4.2. Bảng phân công 8 gói công việc (W3-01 đến W3-08)

| Mã gói việc | Tên công việc chi tiết | Trụ cột liên quan | Sinh viên phụ trách | Sản phẩm bàn giao dự kiến | Tiêu chí nghiệm thu hoàn thành |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **W3-01** | Chốt phiên bản mã nguồn và cấu hình triển khai đồng bộ | Trụ cột 1 | Nguyễn Tiến Sơn | Hash SHA-256 mã nguồn và gói zip triển khai trên Lambda | Hàm Lambda chạy trên AWS khớp hoàn toàn mã nguồn trên GitHub |
| **W3-02** | Chuẩn hóa lịch trình EventBridge và quyền gọi hàm | Trụ cột 1 & 2 | Nguyễn Tiến Sơn | Cấu hình Rule/Target chuẩn xác, dọn dẹp rule trùng lặp | Chỉ duy nhất 1 Rule kích hoạt đúng tần suất 1 giờ/lần |
| **W3-03** | Triển khai Partition Projection và Parquet trên S3/Athena | Trụ cột 2 | Trần Thị Ngọc Quyên | Bảng Athena tối ưu với Partition Projection và Parquet | Truy vấn không cần chạy `MSCK REPAIR`, giảm dung lượng quét |
| **W3-04** | Kiểm định chất lượng dữ liệu và tính liên tục thời gian | Trụ cột 1 & 4 | Trần Thị Ngọc Quyên | Báo cáo kiểm định chất lượng dữ liệu (Data Quality Report) | Xác định tỷ lệ rỗng = 0%, giải thích các khoảng gián đoạn |
| **W3-05** | Thiết lập CloudWatch Metrics Dashboard thời gian thực | Trụ cột 3 | Nguyễn Tiến Sơn | CloudWatch Dashboard JSON và ảnh chụp giao diện vận hành | Hiển thị biểu đồ Invocations, Errors, Duration và SNS Publish |
| **W3-06** | Nâng cấp cảnh báo đa kênh SNS (Email + SMS/Webhook) | Trụ cột 3 | Nguyễn Tiến Sơn | Cấu hình Topic SNS đa kênh và kiểm thử gửi cảnh báo | Nhận cảnh báo tức thì khi xuất hiện mẫu vượt ngưỡng |
| **W3-07** | Phát triển mô hình dự báo chuỗi thời gian AQI/PM2.5 | Trụ cột 4 | Trần Thị Ngọc Quyên | Script phân tích time-series và biểu đồ dự báo 24 giờ tới | Biểu đồ dự báo so khớp với thực nghiệm, tính toán sai số RMSE |
| **W3-08** | Tích hợp CI/CD tự động và tổng duyệt toàn diện hồ sơ repo | Trụ cột 1 | Cả hai sinh viên | Pipeline GitHub Actions hoàn thiện và README Tuần 3 | Toàn bộ 106 bài kiểm thử chạy tự động đạt 100% PASS trên GitHub |

Chi tiết xem tại tài liệu chuyên đề: [docs/WEEK_3_PLAN.md](docs/WEEK_3_PLAN.md).

---

## 5. Bổ sung và xâu chuỗi liền mạch hồ sơ Tuần 1 và Tuần 2

Nhóm 05 bảo đảm tính liền mạch và tính nhất quán tuyệt đối trong suốt tiến trình dự án:

1. **Hồ sơ Tuần 1 (Nền tảng & Xác lập luồng thu thập)**:
   - Xây dựng thành công luồng thu thập dữ liệu tự động Open-Meteo cho 3 đô thị lớn (Hà Nội, TP.HCM, Đà Nẵng).
   - Lưu trữ bản ghi NDJSON trên S3 và khai báo Glue Data Catalog với bộ dữ liệu chuẩn hóa gồm **156 bản ghi** (52 bản ghi cho mỗi đô thị).
   - Xuất 6 tệp CSV phân tích và 9 biểu đồ trực quan hóa dữ liệu ban đầu.
   - Tài liệu Tuần 1: [tuan_1/README.md](tuan_1/README.md) · [Báo cáo chi tiết Tuần 1](tuan_1/docs/FINAL_REPORT.md) · [Phân công Tuần 1](tuan_1/docs/PHAN_CONG.md).
2. **Hồ sơ Tuần 2 (Phát triển nâng cao & Phân tích 2 tài khoản độc lập)**:
   - Mở rộng triển khai song song trên 2 tài khoản AWS Learner Lab độc lập của 2 sinh viên (Account 873674852386 và Account 134987931868).
   - Lưu trữ bộ dữ liệu thực tế gồm **204 bản ghi** (Tiến Sơn) và **231 bản ghi** (Ngọc Quyên), trích xuất **27 nhóm đô thị–giờ** và **21 nhóm cùng giờ** đối chiếu trực tiếp.
   - Sửa đổi các cơ chế an toàn: quản lý ngân sách thời gian Lambda, null-safety, bảo vệ CSV Athena, tính toán tương quan môi trường chính xác.
   - Xuất bản 27 tệp CSV phân tích chuyên sâu và 20 biểu đồ trực quan hóa hiện đại.
   - Tài liệu Tuần 2: [tuan_2/README.md](tuan_2/README.md) · [Báo cáo chi tiết Tuần 2](tuan_2/docs/FINAL_REPORT.md) · [Kết quả phân tích](tuan_2/results/README.md).
3. **Bảo tồn tính trung thực và khả năng truy vết dữ liệu**:
   - Tất cả các tệp CSV và siêu dữ liệu đều được lưu trữ trực tiếp trên GitHub và lập danh mục kèm mã băm SHA-256 tại [docs/csv_catalog.csv](docs/csv_catalog.csv).
   - Tách biệt rõ ràng giữa bộ dữ liệu báo cáo gốc và đợt kiểm chứng AWS mới ngày 16/10/2026 tại [tuan_2/results/review_2026_10_16/README.md](tuan_2/results/review_2026_10_16/README.md).
   - Toàn bộ quy trình kiểm thử với **106 test cases** (66 unit tests, 18 analytics tests, 22 acceptance tests) hoàn toàn độc lập, có thể tái lập 100% bằng lệnh:
     ```powershell
     python tuan_2/scripts/repository_audit.py --check
     python -m unittest discover -s tuan_2/tests -v
     python -m unittest discover -s tuan_2/analytics -p "test_*.py" -v
     python -m unittest tests/test_e2e_acceptance.py -v
     ```
