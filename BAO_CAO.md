# Báo cáo tổng kết đồ án — Điện toán đám mây (Tuần 1 – Tuần 4)

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05  
**Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng  
**Trường:** Đại học Sư phạm Kỹ thuật TP. Hồ Chí Minh (HCMUTE)

**Sinh viên thực hiện:**
- **Nguyễn Tiến Sơn** — MSSV: 24110054
- **Trần Thị Ngọc Quyên** — MSSV: 24110051

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên nền tảng AWS (Domain Apps).  
**Mốc hoàn thiện tổng kết:** 20/10/2026.  
**Kho lưu trữ chính:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm).

---

## Bổ sung nâng cao thực tế ngày 20/10/2026

- **`feat(week4): verify live stacks and three historical backtest windows` — 58fdf22:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/58fdf22da9b048e457aa88e823606cf424ec5caf](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/58fdf22da9b048e457aa88e823606cf424ec5caf).

- **CloudFormation:** hai stack weather-w4-son/weather-w4-quyen CREATE_COMPLETE; cùng source/ZIP đúng hash, mỗi Lambda thu ba đô thị và SELECT đúng database/workgroup mới. [Minh chứng triển khai](tuan_4/results/advanced_live_2026_10_20/README.md).
- **Raw và vận hành:** 700 bản ghi tích lũy/115 JSON gốc; mỗi stack mới có một Invocation/0 Errors trong chu kỳ kiểm chứng. Hai lịch chuẩn đã pause/restore thực tế; lịch mới vẫn DISABLED.
- **SNS:** topic mới đã confirmed, mỗi topic có một thư thử được người nhận xác nhận. Lượt E2E mới dưới ngưỡng nên 0 cảnh báo; cảnh báo dữ liệu vượt ngưỡng ngày 19/10 được giữ riêng.
- **Athena:** 18 truy vấn mới trên cùng đầu vào mỗi sinh viên; Parquet giảm byte quét 80,62% trong bộ đo ngày 20/10, JSON Projection có tổng thời gian trung vị thấp hơn Parquet. [Số đo từng lượt](tuan_4/results/advanced_live_2026_10_20/benchmark/).
- **Dự báo:** backtest ba cửa sổ lịch sử có 432 dự đoán và 18 dòng MAE/RMSE/Bias, train luôn trước đích; đây là hồi cứu chuỗi mô hình. [Dữ liệu và biểu đồ](tuan_4/results/backtest_2026_10_20/README.md).

[Báo cáo Tuần 4 cập nhật](tuan_4/docs/FINAL_REPORT.md) · [Nội dung nộp có URL đầy đủ](tuan_4/docs/SUBMISSION.md). Các phần theo mốc ngày 19/10 bên dưới giữ phạm vi lịch sử tương ứng.

## Tóm tắt tổng thể đồ án (Executive Summary)

Đồ án xây dựng một hệ thống **Serverless** trên Amazon Web Services (AWS) để thu thập, lưu trữ, truy vấn, phân tích dữ liệu thời tiết và gửi cảnh báo chất lượng không khí cho **TP. Hồ Chí Minh, Hà Nội và Đà Nẵng**. Kết quả được đánh giá trên các bộ dữ liệu và lượt thực thi đã lưu của môi trường học phần.

Hệ thống được phát triển và kiểm chứng thực tế qua 4 tuần học phần trên môi trường AWS Academy Learner Lab tại vùng `us-east-1`:
1. **Tuần 1 (Khởi động và Thiết kế kiến trúc):** Lựa chọn mô hình Serverless, thiết lập IAM, S3 bucket và cấu trúc khóa phân vùng.
2. **Tuần 2 (Thu thập và Chuẩn hóa dữ liệu):** Triển khai AWS Lambda collector, tích hợp API Open-Meteo, chuẩn hóa 23 trường theo lược đồ dự án, phân loại US AQI, cấu hình AWS Glue Data Catalog và kiểm thử truy vấn Athena ban đầu.
3. **Tuần 3 (Tích hợp, Giám sát, Benchmark và Dự báo):** Tích hợp hoàn chỉnh hệ thống, thiết lập CloudWatch Dashboard & Metric Filters, cấu hình cảnh báo email qua Amazon SNS, thực hiện 18 lượt benchmark Athena (chứng minh Parquet Snappy giảm 80,59% – 96,50% dữ liệu quét so với NDJSON), mô hình hóa dự báo AQI/PM2.5 24 giờ tới (đối chiếu đủ 144 điểm dữ liệu), và thiết lập guarded CD pipeline. **Tuần 3 đã được GVHD chính thức đánh giá ĐẠT.**
4. **Tuần 4 (Kiểm chứng toàn diện, IaC CloudFormation, FinOps và An ninh bảo mật):**
   - **Kiểm thử E2E có kiểm soát:** Thực hiện hai lượt realtime ngày 19/10 trên hai môi trường độc lập; lưu nguyên byte object NDJSON từ S3, kiểm tra CSV raw và đối chiếu các trường đã chọn bằng Athena theo đúng `record_id`. Ngày 20/10 thực hiện thêm một lượt trên mỗi collector của stack mới.
   - **Đối chiếu 3 chiều Log – Metric – S3:** Xác thực khớp 1-1 giữa nhật ký CloudWatch Logs (`START`/`END`/`REPORT`/`[INFO] Result`), chỉ số vận hành CloudWatch Metrics (Invocations, 0 Errors, tỷ lệ lỗi 0,0%), tệp lưu trữ S3, và xác nhận nhận email cảnh báo vượt ngưỡng của cả hai sinh viên.
   - **Báo cáo tài chính đám mây FinOps:** Chi phí cập nhật ngày 20/10/2026 theo số liệu sinh viên xác nhận: **0,25 USD** (Tiến Sơn), **0,22 USD** (Ngọc Quyên), tổng **0,47 USD**. Các bản Cost Explorer gốc được lưu riêng để đối chiếu.
   - **Tự động hóa vòng đời tài nguyên cuối phiên:** Xây dựng script PowerShell và công cụ Python `session_control.py` giúp tạm dừng/khôi phục EventBridge Rule, kiểm soát hoạt động thu thập theo phiên Lab.
   - **Đóng gói toàn bộ hạ tầng dưới dạng mã (CloudFormation IaC):** Xây dựng một template duy nhất ([weather-stack.json](tuan_4/infrastructure/weather-stack.json)) quản lý trọn vẹn **17 tài nguyên AWS Serverless**, đạt kiểm tra `cfn-lint 1.57.2` và API AWS `ValidateTemplate` trên cả hai môi trường.
   - **Rà soát bảo mật:** Đối chiếu 11 nội dung trong phạm vi đồ án ([SECURITY_AUDIT.md](tuan_4/docs/SECURITY_AUDIT.md)), gồm BPA, AES256, versioning, HTTPS, ownership, quyền gọi Lambda và mẫu policy collector. Kết quả đọc cấu hình và thiết kế quyền được ghi riêng theo nguồn.
   - **Tổng kết giờ công toàn khóa học:** Tổng thời gian thực hiện Tuần 4 là **20,0 giờ**; tổng thời gian toàn bộ đồ án đạt **78,0 giờ** đã được xác nhận đầy đủ trong [worklog.csv](worklog.csv).

---

## Phần I: Kiến trúc tổng thể và Cơ sở lựa chọn công nghệ trên AWS

Hệ thống phân tách lịch kích hoạt, xử lý, lưu trữ, truy vấn và thông báo bằng các dịch vụ serverless. Cách thiết kế giảm phần máy chủ phải quản trị; hiệu năng, vận hành và chi phí được đánh giá bằng các phép đo trong báo cáo:

```
[Amazon EventBridge] ──(rate: 1 hour)──► [AWS Lambda (Python 3.12)] ◄── [AWS Secrets Manager]
                                                  │
                            ┌─────────────────────┴─────────────────────┐
                            ▼                                           ▼
                  [Amazon S3 (NDJSON raw)]                     [Amazon SNS Topic]
                            │                                           │
                  [AWS Glue Data Catalog]                               ▼
                            │                                   [Email sinh viên]
                            ▼
                   [Amazon Athena SQL]
                            │
            [CloudWatch Logs, Metrics & Dashboard]
```

![Kiến trúc hệ thống](docs/architecture.png)

*Hình 1. Sơ đồ kiến trúc giải pháp thu thập, lưu trữ, truy vấn và giám sát trên AWS.*

### Vai trò và trách nhiệm của từng dịch vụ AWS:
1. **Amazon EventBridge (CloudWatch Events):** Đảm nhiệm vai trò kích hoạt theo lịch định kỳ một giờ một lần (`rate(1 hour)`), kích hoạt Lambda thu thập tự động mà không cần máy chủ cron truyền thống.
2. **AWS Lambda:** Xử lý logic nghiệp vụ chính (thu thập từ API Open-Meteo, chuẩn hóa dữ liệu, đánh giá ngưỡng cảnh báo logic OR, lưu trữ S3 và phát thông báo SNS).
3. **AWS Secrets Manager:** Lưu tọa độ ba đô thị và ngưỡng AQI/PM2.5 để collector đọc lúc chạy. Tên bucket, ARN topic và định danh Secret được truyền qua biến môi trường Lambda; không đưa credentials vào source.
4. **Amazon S3:** Kho lưu trữ dữ liệu thô (Data Lake Storage) theo định dạng NDJSON, phân vùng tối ưu theo thời gian UTC: `raw/year=YYYY/month=MM/day=DD/`.
5. **AWS Glue Data Catalog & Amazon Athena:** Lưu lược đồ và truy vấn SQL trực tiếp trên S3. **Partition Projection** ánh xạ khóa ngày sang đường dẫn dữ liệu; truy vấn sử dụng điều kiện phân vùng và được đo byte quét cùng độ trễ.
6. **Amazon SNS (Simple Notification Service):** Phát email khi AQI hoặc PM2.5 đạt ngưỡng cấu hình của ứng dụng; xác nhận Publish và xác nhận người nhận được theo dõi riêng.
7. **Amazon CloudWatch:** Giám sát toàn diện vòng đời thực thi qua CloudWatch Logs, theo dõi sức khỏe hệ thống qua CloudWatch Metrics (Invocations, Errors, Duration), Metric Filters và trực quan hóa tập trung trên CloudWatch Dashboard.

---

## Phần II: Quá trình triển khai và Kết quả qua 4 tuần thực hành

### 1. Tuần 1: Khởi động đề tài, Khảo sát API và Thiết kế ban đầu (18,5 giờ)
- Khảo sát các nguồn dữ liệu thời tiết và chất lượng không khí mở; lựa chọn **Open-Meteo API** (kết hợp mô hình khí quyển châu Âu CAMS).
- Xác lập tọa độ địa lý chuẩn xác cho 3 đô thị: TP. Hồ Chí Minh (`10.8231, 106.6297`), Hà Nội (`21.0285, 105.8542`), và Đà Nẵng (`16.0544, 108.2022`).
- Thiết kế mô hình dữ liệu thô và kiến trúc phân vùng S3 theo thời gian UTC.
- Khởi tạo môi trường AWS Learner Lab, thiết lập quyền hạn IAM và cấu trúc thư mục dự án.
- Thời gian thực hiện: Nguyễn Tiến Sơn: 9,5 giờ; Trần Thị Ngọc Quyên: 9,0 giờ. Tổng cộng: **18,5 giờ**.
- Báo cáo chi tiết: [tuan_1/docs/FINAL_REPORT.md](tuan_1/docs/FINAL_REPORT.md).

### 2. Tuần 2: Thu thập Lambda, Chuẩn hóa 23 trường và Athena Catalog (19,5 giờ)
- Phát triển [lambda_function.py](tuan_2/lambda/lambda_function.py): handler điều phối realtime/backfill, các hàm lấy dữ liệu và chuẩn hóa 23 trường, phân loại giá trị US AQI do API trả về, đánh giá ngưỡng, gửi SNS và ghi S3 dạng NDJSON.
- Cấu hình AWS Glue Data Catalog và bảng `weather_airquality_records` với đầy đủ kiểu dữ liệu số học.
- Xây dựng bộ công cụ kiểm toán kho lưu trữ tự động [repository_audit.py](tuan_2/scripts/repository_audit.py) kiểm tra tính toàn vẹn của liên kết Markdown, worklog CSV và các snapshot AWS.
- Giữ riêng báo cáo Tuần 2 với CSV toàn bộ 204/231 dòng và phần thuộc tuần 27/57 dòng của sinh viên Tiến Sơn/sinh viên Ngọc Quyên. Snapshot bổ sung ngày 16/10 có 216/249 dòng, không thay đầu vào báo cáo đã chốt.
- Thời gian thực hiện: Nguyễn Tiến Sơn: 10,0 giờ; Trần Thị Ngọc Quyên: 9,5 giờ. Tổng cộng: **19,5 giờ**.
- Báo cáo chi tiết: [tuan_2/docs/FINAL_REPORT.md](tuan_2/docs/FINAL_REPORT.md).

### 3. Tuần 3: Tích hợp, Giám sát, Thực nghiệm Benchmark và Dự báo (20,0 giờ) — ĐẠT
- **Tích hợp hệ thống:** Đồng bộ mã nguồn trên 2 môi trường qua quy trình guarded CD pipeline.
- **Giám sát & Cảnh báo:** Thiết lập CloudWatch Dashboard `WeatherAirQuality-Week3` với biểu thức tỷ lệ lỗi fail-safe; kích hoạt 2 Metric Filters; đối soát luồng cảnh báo email SNS với xác nhận nhận thư từ cả hai sinh viên.
- **Thực nghiệm Benchmark Athena 18 lượt đo:** So sánh 3 cấu hình (NDJSON đăng ký phân vùng, NDJSON Partition Projection, và Parquet Snappy Partition Projection). Kết quả: định dạng Parquet Snappy giúp giảm **80,59%** dữ liệu quét ở tài khoản Tiến Sơn (từ 1.556 xuống 302 bytes) và giảm **96,50%** ở tài khoản Ngọc Quyên (từ 11.243 xuống 393 bytes), chứng minh lợi ích vượt trội của lưu trữ theo cột.
- **Dự báo chất lượng không khí 24 giờ:** Phát hành bản dự báo 144 điểm dữ liệu (24 giờ × 3 đô thị × 2 chỉ số) cho ngày 18–19/10/2026; đối chiếu đủ 144/144 giá trị với dữ liệu thực tế tải về sau (MAE AQI: TP.HCM 10,22; Hà Nội 11,03; Đà Nẵng 12,32).
- **Quy mô dữ liệu tích lũy:** Đạt **641 bản ghi trong 95 tệp JSON gốc** (302 bản ghi Tiến Sơn, 339 bản ghi Ngọc Quyên).
- **Kết quả đánh giá:** **GVHD ThS. Huỳnh Xuân Phụng chính thức đánh giá ĐẠT.**
- Thời gian thực hiện: Nguyễn Tiến Sơn: 10,0 giờ; Trần Thị Ngọc Quyên: 10,0 giờ. Tổng cộng: **20,0 giờ**.
- Báo cáo chi tiết: [tuan_3/docs/FINAL_REPORT.md](tuan_3/docs/FINAL_REPORT.md).

### 4. Tuần 4: Kiểm chứng toàn diện, Hạ tầng IaC, FinOps và An ninh bảo mật (20,0 giờ)
- Thực hiện kiểm chứng có kiểm soát đầu-cuối (E2E) trên 2 môi trường.
- Đối chiếu 3 chiều Log – Metric – S3 – Alert.
- Lập báo cáo tài chính đám mây FinOps; cập nhật Tiến Sơn 0,25 USD và Ngọc Quyên 0,22 USD ngày 20/10.
- Tự động hóa dọn dẹp tài nguyên và bảo toàn credit cuối phiên.
- Đóng gói 17 tài nguyên vào template CloudFormation [weather-stack.json](tuan_4/infrastructure/weather-stack.json).
- Rà soát 11 nội dung bảo mật trong phạm vi đồ án tại [SECURITY_AUDIT.md](tuan_4/docs/SECURITY_AUDIT.md).
- Thời gian thực hiện: Nguyễn Tiến Sơn: 10,0 giờ; Trần Thị Ngọc Quyên: 10,0 giờ. Tổng cộng: **20,0 giờ**.
- Báo cáo chi tiết: [tuan_4/docs/FINAL_REPORT.md](tuan_4/docs/FINAL_REPORT.md).

---

## Phần III: Minh chứng kỹ thuật chuyên sâu và Yêu cầu nâng cao Tuần 4

### 1. Kiểm thử đầu-cuối có kiểm soát (E2E Verification)

Tại mốc kiểm chứng ngày 19/10/2026, mỗi môi trường được kích hoạt một lượt chạy thời gian thực duy nhất bằng sự kiện `{}`. Dữ liệu NDJSON tải lại từ S3 được đối soát với câu lệnh Athena SELECT lọc chính xác theo `record_id`:

| Chỉ số kỹ thuật | Sinh viên Nguyễn Tiến Sơn (`default`) | Sinh viên Trần Thị Ngọc Quyên (`quyen`) |
| :--- | :---: | :---: |
| **Bản ghi thu thập mới** | **3 bản ghi** | **3 bản ghi** |
| **Đô thị hoàn tất** | 3 / 3 đô thị (TP.HCM, Hà Nội, Đà Nẵng) | 3 / 3 đô thị (TP.HCM, Hà Nội, Đà Nẵng) |
| **Đô thị lỗi (`failed_cities`)** | 0 đô thị | 0 đô thị |
| **Dữ liệu thô Hà Nội** | AQI = 101, PM2.5 = 29,9 µg/m³, Nhiệt độ = 27,3 °C | AQI = 101, PM2.5 = 29,9 µg/m³, Nhiệt độ = 27,3 °C |
| **Dữ liệu thô TP.HCM** | AQI = 61, PM2.5 = 22,1 µg/m³, Nhiệt độ = 26,7 °C | AQI = 61, PM2.5 = 22,1 µg/m³, Nhiệt độ = 26,7 °C |
| **Dữ liệu thô Đà Nẵng** | AQI = 52, PM2.5 = 7,3 µg/m³, Nhiệt độ = 25,3 °C | AQI = 52, PM2.5 = 7,3 µg/m³, Nhiệt độ = 25,3 °C |
| **Số cảnh báo vượt ngưỡng** | **1 cảnh báo** (Hà Nội AQI 101 ≥ 100) | **1 cảnh báo** (Hà Nội AQI 101 ≥ 100) |
| **Lệnh `sns:Publish` được chấp nhận** | **1 chấp nhận** | **1 chấp nhận** |
| **Truy vấn Athena theo `record_id`** | **Khớp bốn trường SELECT đã chọn** | **Khớp bốn trường SELECT đã chọn** |
| **Dữ liệu Athena quét** | **19.683 bytes** (~19,2 KB) | **20.251 bytes** (~19,8 KB) |
| **Thời gian Engine Athena** | **674 ms** (Total: 888 ms) | **584 ms** (Total: 747 ms) |

*Minh chứng:* [E2E default](tuan_4/results/verification_2026_10_19/e2e/default/) · [E2E quyen](tuan_4/results/verification_2026_10_19/e2e/quyen/).

### 2. Đối chiếu 3 chiều Log – Metric – S3 – Alert

Báo cáo [LOG_METRIC_S3_RECONCILIATION.md](tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md) đối soát chéo 4 tầng dữ liệu trong cùng chu kỳ 300 giây:

| Tầng kiểm chứng | Môi trường Tiến Sơn (`default`) | Môi trường Ngọc Quyên (`quyen`) | Đánh giá |
| :--- | :---: | :---: | :--- |
| **1. CloudWatch Logs** | Request `415b1e3881f4cfca8559`, đủ `START`/`END`/`REPORT`/`[INFO] Result` | Request `6ae57d0f48ce98e59fd3`, đủ `START`/`END`/`REPORT`/`[INFO] Result` | Khớp 100% vòng đời |
| **2. CloudWatch Metrics** | 1.0 Invocation, 0.0 Errors trong chu kỳ 300s (Tỷ lệ lỗi: **0,0%**) | 1.0 Invocation, 0.0 Errors trong chu kỳ 300s (Tỷ lệ lỗi: **0,0%**) | Khớp 1-1 với lượt gọi |
| **3. Lưu trữ Amazon S3** | 1 tệp NDJSON, 3 dòng dữ liệu, khớp byte JSON tải lại | 1 tệp NDJSON, 3 dòng dữ liệu, khớp byte JSON tải lại | Toàn vẹn dữ liệu |
| **4. Cảnh báo Amazon SNS** | 1 Publish chấp nhận; email đã xác nhận tại hộp thư | 1 Publish chấp nhận; email đã xác nhận tại hộp thư | [Xác nhận email](tuan_4/results/verification_2026_10_19/recipient_confirmation.json) |

### 3. Quản trị tài chính đám mây FinOps

Chi phí cập nhật ngày **20/10/2026**, theo số liệu sinh viên xác nhận:

| Sinh viên | Chi phí (USD) |
| --- | ---: |
| Sinh viên Tiến Sơn | **0,25** |
| Sinh viên Ngọc Quyên | **0,22** |
| **Tổng cộng** | **0,47** |

Nguồn: [số liệu chi phí đã xác nhận](tuan_4/results/cost/confirmed_cost_summary.json). Các bản xuất Cost Explorer gốc được giữ riêng để đối chiếu; bảng cập nhật không lấy số nhóm bản ghi của kỳ cũ làm căn cứ cho số tiền mới.

[Báo cáo chi phí](tuan_4/docs/COST_REPORT.md) trình bày nguồn xác nhận, dữ liệu Cost Explorer lịch sử và các biện pháp tối ưu.

### 4. Quản lý vòng đời tài nguyên cuối phiên (FinOps Lifecycle Automation)

Nhóm xây dựng giải pháp tự động hóa ngăn ngừa rò rỉ chi phí giữa các buổi thực hành:
- **Script dọn dẹp cuối phiên:** `pwsh -File tuan_4/scripts/cleanup_resources.ps1 -Profile default -Apply` gọi `session_control.py pause`. Lệnh tự động lưu trạng thái vào tệp khôi phục an toàn (atomic replace) và chuyển EventBridge Rule sang trạng thái `DISABLED`.
- **Script khôi phục đầu phiên:** `pwsh -File tuan_4/scripts/start_resources.ps1 -Profile default -Apply` gọi `session_control.py restore`, khôi phục lịch hoạt động sau khi kiểm tra tính toàn vẹn của state file.
- Quy trình tuân thủ nghiêm ngặt theo [SESSION_CHECKLIST.md](tuan_4/docs/SESSION_CHECKLIST.md).

### 5. Đóng gói hạ tầng dưới dạng mã CloudFormation (IaC 17 tài nguyên)

Hạ tầng được đặc tả toàn diện trong [weather-stack.json](tuan_4/infrastructure/weather-stack.json) bao gồm **17 tài nguyên AWS Serverless**:
- **Lưu trữ & Bảo mật:** `DataBucket` (S3), `DataBucketPolicy` (HTTPS-only), `WeatherConfigSecret` (Secrets Manager).
- **Kích hoạt & Xử lý:** `HourlyRule` (EventBridge, mặc định `DISABLED`), `Collector` (Lambda Function), `CollectorPermission`, `CollectorLogs` (Log Group).
- **Cảnh báo:** `AlertTopic` (SNS), `AlertSubscription` (Email), `AlarmTopicPolicy` (ràng buộc SourceArn từ CloudWatch Alarm).
- **Phân tích dữ liệu:** `GlueDatabase`, `RawTable` (Partition Projection), `AthenaWorkgroup`.
- **Giám sát & Đo lường:** `ErrorAlarm`, `OperationalDashboard`, `ResultMetricFilter`, `ErrorMetricFilter`.

Template đạt kiểm tra cú pháp với `cfn-lint 1.57.2` và xác thực qua API AWS `ValidateTemplate` trên cả hai tài khoản ([hồ sơ xác thực template](tuan_4/results/template_validation_2026_10_19/README.md)). Hướng dẫn triển khai xem tại [INFRASTRUCTURE.md](tuan_4/docs/INFRASTRUCTURE.md).

### 6. Rà soát 11 nội dung bảo mật

Báo cáo [SECURITY_AUDIT.md](tuan_4/docs/SECURITY_AUDIT.md) tổng hợp 11 nội dung kiểm tra. Ma trận [security_controls_audit.csv](tuan_4/results/security/security_controls_audit.csv) là bảng dẫn xuất theo snapshot ngày 19/10; cấu hình mới ngày 20/10 được lưu riêng:
1. **S3 Block Public Access:** Đạt 4/4 cờ bật trên cả hai tài khoản (**PASS**).
2. **S3 Public ACL Absent:** Không có quyền công khai qua ACL (**PASS**).
3. **S3 Public Policy Absent:** Không có bucket policy mở tự do (**PASS**).
4. **S3 Encryption at Rest:** Bật mã hóa tĩnh SSE-S3 AES256 100% (**PASS**).
5. **S3 Versioning:** Bucket hiện hữu ngày 19/10 ghi `NOT_ENABLED`; hai bucket mới ngày 20/10 đọc lại `Enabled`.
6. **S3 HTTPS-Only Transport:** Hai bucket mới đã đọc lại policy Deny yêu cầu không qua HTTPS.
7. **S3 BucketOwnerEnforced:** Hai bucket mới đã đọc lại ownership ở trạng thái BucketOwnerEnforced.
8. **IAM Least Privilege Runtime:** API đọc policy LabRole bị từ chối trong snapshot ngày 19/10, chưa xác định lớp policy gây từ chối. [Policy collector tham khảo](tuan_4/infrastructure/collector-policy.example.json) giới hạn theo tài nguyên cho bốn nhóm thao tác: ghi raw, đọc Secret, Publish và ghi log; không khẳng định effective permissions của LabRole đã tối thiểu.
9. **EventBridge Invocation Boundary:** Resource policy Lambda ràng buộc đúng Rule ARN và SourceAccount (**PASS**).
10. **SNS Topic Publish Boundary:** Ràng buộc SourceArn từ đúng CloudWatch Alarm ARN (**DECLARED**).
11. **Log Hygiene & Secret Redaction:** Rà soát các tệp minh chứng được công bố để loại credentials, SecretString, email và URL có chữ ký; không khẳng định mọi log tương lai đã được kiểm tra.

### 7. Video trình bày đồ án

Video trình bày tối đa 10 phút, thể hiện kiến trúc, luồng thu thập, truy vấn, cảnh báo và quản lý hệ thống. Đường dẫn được bổ sung sau khi quay và kiểm tra quyền xem.

---

## Phần IV: Phân công trách nhiệm và Tổng kết giờ công (Worklog 78,0 giờ)

Hai sinh viên phối hợp chặt chẽ, phân định rõ ràng trách nhiệm chuyên môn và kiểm tra chéo lẫn nhau:

| Sinh viên | Trách nhiệm chuyên môn chính | T1 | T2 | T3 | T4 | Tổng giờ công |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Nguyễn Tiến Sơn** (24110054) | Thiết kế kiến trúc hạ tầng CloudFormation 17 tài nguyên, tối ưu Lambda Collector, EventBridge Schedule, SNS Alerting, CloudWatch Monitoring & Metric Filters, kịch bản lifecycle FinOps (`session_control.py`, `cleanup_resources.ps1`, `start_resources.ps1`). | 9,5h | 10,0h | 10,0h | 10,0h | **39,5 giờ** |
| **Trần Thị Ngọc Quyên** (24110051) | Quản trị Glue Data Catalog, tối ưu Athena Serverless SQL (Partition Projection), kiểm toán chất lượng dữ liệu 23 trường, báo cáo tài chính FinOps Cost Explorer, đối chiếu 3 chiều Log–Metric–S3, rà soát an ninh bảo mật 11 tiêu chuẩn. | 9,0h | 9,5h | 10,0h | 10,0h | **38,5 giờ** |
| **Toàn nhóm** | **Hai sinh viên phối hợp tích hợp, đối soát chéo và hoàn thiện hồ sơ** | **18,5h** | **19,5h** | **20,0h** | **20,0h** | **78,0 giờ** |

*Căn cứ xác nhận:* [worklog.csv](worklog.csv), [tuan_4/worklog.csv](tuan_4/worklog.csv), [tuan_4/docs/WORKLOG.md](tuan_4/docs/WORKLOG.md), và [worklog_confirmation.json](tuan_4/results/verification_2026_10_19/worklog_confirmation.json).

---

## Phần V: Danh mục Commit minh chứng với Message nguyên bản

Mọi liên kết commit dưới đây đều dẫn trực tiếp đến GitHub commit và đi kèm **commit message nguyên bản verbatim trong Git**:

### 1. Các commit hoàn thiện Tuần 4 (Hạ tầng IaC, FinOps, An ninh & Kiểm chứng E2E)
- **`docs(repo): keep video preparation guides local` — 84686c5:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/84686c51606c750d27dc9942fb2fc8968375765b](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/84686c51606c750d27dc9942fb2fc8968375765b).
- **`docs(week4): unify master report, expand 11-control security audit, and detail dual-speaker demo script` — dd17f7f:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/dd17f7f2614256c28d2da7cdf636267276e7af84](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/dd17f7f2614256c28d2da7cdf636267276e7af84).
- **`docs(readme): showcase advanced features and final week results` — 915e8c6:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/915e8c6f4e636628172ca4a367778c90fc93f5e6](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/915e8c6f4e636628172ca4a367778c90fc93f5e6).
- **`docs(week4): expand raw evidence analysis and submission guide` — 2548138:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/25481381772288597af36e84093a89d41d080c64](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/25481381772288597af36e84093a89d41d080c64).
- **`docs(report): add final project synthesis and acceptance mapping` — f6921e7:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/f6921e7dc0e26245ca5d33dd0b7288dc11120f0d](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/f6921e7dc0e26245ca5d33dd0b7288dc11120f0d).
- **`docs(week4): reconcile template history and confirmed email wording` — 9cac06e:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/9cac06e43299e25061e7cc90b11dda2017448350](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/9cac06e43299e25061e7cc90b11dda2017448350).
- **`docs(week4): link verified integration commits with exact subjects` — fdbf633:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/fdbf63330805c676fcb23c324685cce4d8049ae4](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/fdbf63330805c676fcb23c324685cce4d8049ae4).
- **`fix(evidence): preserve Week 4 snapshot bytes across platforms` — 892861e:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/892861ec5129d59a9c772ef20ed6d2ac053d65f5](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/892861ec5129d59a9c772ef20ed6d2ac053d65f5).
- **`docs(week4): synchronize final report test count to 34` — e9704bf:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e9704bf645a11bf07a3f360770061c1cc3a8b3a5](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e9704bf645a11bf07a3f360770061c1cc3a8b3a5).
- **`feat(week4): complete final week verification, consolidate CloudFormation infrastructure, and update catalog` — 96bedec:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093).
- **`fix(iac): fix CloudFormation partition projection escaping and synchronize week 4 documentation` — 59a992a:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/59a992a104932a190b15eab7b44f08d89a899b11](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/59a992a104932a190b15eab7b44f08d89a899b11).
- **`feat(week4): implement CloudFormation IaC, security audit, log-metric-S3 reconciliation, and video demo script` — e497754:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e49775409593296fbe14ed0474e4e5cb2f930c36](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e49775409593296fbe14ed0474e4e5cb2f930c36).

### 2. Các commit then chốt Tuần 3 (Tích hợp, Benchmark, Giám sát & Dự báo)
- **`feat(week3): add measured Athena experiments, monitoring and guarded CD` — 0b26858:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e).
- **`fix(cd): make Lambda archive identical across Windows and Linux` — c28da19:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356).
- **`fix(lambda): collect completed current-day hours in backfill` — 62f1c08:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650).
- **`docs(week3): add authenticated October 19 data and final submission review` — 9471ec3:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/9471ec3b92ca2bc6e05b163de67a17819ab29a85](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/9471ec3b92ca2bc6e05b163de67a17819ab29a85).
- **`docs(week3): clarify forecast value and horizon counts` — b4dc3d6:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/b4dc3d624a82f79f5338ec401eab271b1bf3c749](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/b4dc3d624a82f79f5338ec401eab271b1bf3c749).

### 3. Các commit nền tảng Tuần 1 và Tuần 2 (Hạ tầng, Collector, Catalog & CI/CD)
- **`feat(reports): add comprehensive re-submission documentation and live AWS evidence` — 5f43c07:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/5f43c074bbdfa4165d272439ed1c80c1d5a0f6cd](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/5f43c074bbdfa4165d272439ed1c80c1d5a0f6cd).
- **`ci(github-actions): add repository verification workflow and evidence tests` — b78a24d:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/b78a24d5e138c189df07800b6f6369fdcc441552](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/b78a24d5e138c189df07800b6f6369fdcc441552).
- **`feat(worklog): add standardized worklog.csv for week 1, week 2, and root docs` — eac531c:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/eac531c0e4b53e3ef6558cdb5883ce34bc1c5a6f](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/eac531c0e4b53e3ef6558cdb5883ce34bc1c5a6f).
- **`docs(reports): add clickable GitHub links to weekly submissions` — 61ee57d:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/61ee57d8ef3663f745765c3aa8b75e116e080ea7](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/61ee57d8ef3663f745765c3aa8b75e116e080ea7).
- **`fix: harden exports deployment and analysis entrypoints` — 432add1:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/432add13545ff0af1fb86457ccaa1f295b796576](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/432add13545ff0af1fb86457ccaa1f295b796576).

---

## Phần VI: Danh mục liên kết hồ sơ nộp đồ án toàn diện

- **Báo cáo tổng kết đồ án toàn diện (Tuần 1 – Tuần 4):** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md).
- **Hồ sơ Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/README.md).
- **Báo cáo kỹ thuật chính Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md).
- **Văn bản nộp bài LMS Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SUBMISSION.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SUBMISSION.md).
- **Báo cáo đối chiếu 3 chiều Log–Metric–S3:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md).
- **Báo cáo tài chính đám mây FinOps:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md).
- **Báo cáo an ninh bảo mật 11 tiêu chuẩn:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md).
- **Template CloudFormation 17 tài nguyên:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/infrastructure/weather-stack.json](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/infrastructure/weather-stack.json).
- **Minh chứng ValidateTemplate CloudFormation:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/template_validation_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/template_validation_2026_10_19).
- **Danh mục kiểm tra kết thúc phiên Lab:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SESSION_CHECKLIST.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SESSION_CHECKLIST.md).
- **Dữ liệu kiểm chứng trực tiếp ngày 19/10/2026:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/verification_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/verification_2026_10_19).
- **Bảng tổng hợp giờ công toàn đồ án:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv).
- **Mã nguồn Lambda chính thức:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py).
- **Quy trình kiểm thử tự động GitHub Actions:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml).
