# Báo cáo Tuần 4 — Kiểm chứng toàn diện hệ thống, Hạ tầng IaC và Chuẩn bị bảo vệ

**Sinh viên thực hiện:**
- **Nguyễn Tiến Sơn** — MSSV: 24110054
- **Trần Thị Ngọc Quyên** — MSSV: 24110051

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng
**Mốc kiểm chứng kỹ thuật:** 19/10/2026. **Mốc hoàn thiện tài liệu:** 20/10/2026.
**Phạm vi:** Báo cáo kỹ thuật tổng kết Tuần 4 theo kế hoạch và phản hồi của Giảng viên sau khi Tuần 3 được đánh giá ĐẠT.

---

## Tóm tắt nội dung thực hiện (Executive Summary)

Trong Tuần 4, nhóm tập trung triển khai và kiểm chứng toàn diện luồng thu thập, lưu trữ, truy vấn và cảnh báo thời gian thực trên hai môi trường AWS Academy Learner Lab độc lập của sinh viên Nguyễn Tiến Sơn (`default`) và sinh viên Trần Thị Ngọc Quyên (`quyen`).

Các kết quả then chốt đạt được bao gồm:
1. **Kiểm thử đầu-cuối có kiểm soát (E2E Controlled Invocations):** Mỗi môi trường thực hiện 1 lượt thu thập thời gian thực bằng event `{}`, thu thập trọn vẹn 3 bản ghi cho ba đô thị trọng điểm: TP. Hồ Chí Minh, Hà Nội và Đà Nẵng. Dữ liệu NDJSON tải lại từ S3 khớp 100% với truy vấn Serverless Athena lọc theo chính xác danh sách `record_id`.
2. **Đối chiếu 3 chiều Log – Metric – S3 – Alert:** Trong cùng chu kỳ kiểm chứng 300 giây, mỗi môi trường ghi nhận đúng 1 Invocation, 0 Error (tỷ lệ lỗi 0,0%), chuỗi log đầy đủ `START`/`END`/`REPORT`/`[INFO] Result`, 3 bản ghi NDJSON hợp lệ trên S3, 1 lệnh gọi `sns:Publish` được chấp nhận, và cả hai sinh viên đã xác nhận nhận email cảnh báo thời gian thực mới của đợt này.
3. **Phân tích tài chính đám mây FinOps (Cost Explorer):** Phân tích chi tiết 117 nhóm bản ghi chi phí từ Cost Explorer API trong kỳ 12–19/10/2026 theo ngày, dịch vụ và loại ghi nhận. Tổng chi phí tài khoản hiển thị làm tròn đạt **0,00 USD** (sinh viên Tiến Sơn) và **0,14 USD** (sinh viên Ngọc Quyên) nhờ cơ chế Serverless và chính sách bù trừ tín dụng Credit.
4. **Đóng gói toàn bộ hạ tầng dưới dạng mã (CloudFormation IaC):** Xây dựng một template CloudFormation duy nhất ([weather-stack.json](../infrastructure/weather-stack.json)) bao gồm trọn vẹn **17 tài nguyên AWS**, vượt qua 100% kiểm tra cú pháp với `cfn-lint 1.57.2` và API xác thực `ValidateTemplate` trên cả hai tài khoản AWS thật.
5. **Rà soát an ninh bảo mật theo 11 tiêu chuẩn khắt khe ([SECURITY_AUDIT.md](SECURITY_AUDIT.md)):** Bật 4/4 cờ S3 Block Public Access, mã hóa tĩnh SSE-S3 AES256, thực thi HTTPS bắt buộc, kiểm soát quyền sở hữu bucket, đánh giá hạn chế SCP đối với `LabRole`, và cung cấp mẫu IAM Policy tối thiểu cho collector.
6. **Tự động hóa vòng đời tài nguyên cuối phiên (Session Lifecycle Automation):** Phát triển bộ kịch bản [cleanup_resources.ps1](../scripts/cleanup_resources.ps1) và [start_resources.ps1](../scripts/start_resources.ps1) giúp tạm dừng EventBridge Rule và bảo toàn trạng thái trước khi thoát Lab, ngăn chặn hao hụt credit 100 USD của học phần.
7. **Tổng kết giờ công toàn khóa học:** Tổng thời gian thực hiện Tuần 4 là **20,0 giờ** (10,0 giờ mỗi sinh viên); tổng thời gian toàn bộ đồ án (Tuần 1 đến Tuần 4) đạt **78,0 giờ** đã được xác nhận đầy đủ trong [worklog.csv](../worklog.csv).

---

## Mục tiêu và kiến trúc hệ thống kiểm chứng

Quy trình kiểm chứng đi qua toàn bộ luồng dữ liệu khép kín:
```
[EventBridge Rule] ──(Chu kỳ 1 giờ)──► [AWS Lambda] ◄── [Secrets Manager]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             [Amazon S3 (NDJSON)]                         [Amazon SNS Topic]
                       │                                           │
             [Glue Data Catalog]                                   ▼
                       │                                   [Email sinh viên]
                       ▼
             [Amazon Athena SQL]
                       │
       [CloudWatch Logs & Metrics & Dashboard]
```

![Kiến trúc thu thập và phân tích dữ liệu](../../docs/architecture.png)

*Hình 1. Kiến trúc hệ thống thu thập, lưu trữ, truy vấn và cảnh báo được kiểm chứng toàn diện trong Tuần 4.*

---

## 1. Tổng hợp các nội dung thực hiện theo góp ý của Giảng viên

| Yêu cầu của Giảng viên | Giải pháp và Sản phẩm minh chứng trong Tuần 4 | Tình trạng |
| :--- | :--- | :---: |
| **Gắn message commit nguyên bản cạnh liên kết** | Cập nhật 100% các liên kết commit trên [BAO_CAO.md](../../BAO_CAO.md), [FINAL_REPORT.md](FINAL_REPORT.md), và [SUBMISSION.md](SUBMISSION.md) kèm commit message nguyên bản trong Git. | **ĐẠT** |
| **Kiểm thử tổng thể E2E hệ thống** | Thực hiện 2 lượt gọi có kiểm soát trên 2 môi trường; đối chiếu nguyên vẹn byte JSON S3 với truy vấn Athena theo đúng danh sách `record_id`. | **ĐẠT** |
| **Đối chiếu 3 chiều Log – Metric – S3** | Xây dựng báo cáo [LOG_METRIC_S3_RECONCILIATION.md](LOG_METRIC_S3_RECONCILIATION.md) đối soát từng mã request, Invocations, Errors, NDJSON raw, và xác nhận email. | **ĐẠT** |
| **Báo cáo tài chính đám mây FinOps** | Lập báo cáo [COST_REPORT.md](COST_REPORT.md) trích xuất từ Cost Explorer API theo 117 nhóm ngày/dịch vụ/record type trong kỳ 12–19/10/2026. | **ĐẠT** |
| **Quản lý tài nguyên bảo toàn Credit cuối phiên** | Xây dựng [SESSION_CHECKLIST.md](SESSION_CHECKLIST.md) và bộ script `cleanup_resources.ps1` / `start_resources.ps1` có atomic state file và rollback bảo vệ. | **ĐẠT** |
| **Đóng gói 1 template CloudFormation (IaC)** | Thiết kế template [weather-stack.json](../infrastructure/weather-stack.json) gồm 17 tài nguyên, kiểm tra đạt 100% qua `cfn-lint` và AWS `ValidateTemplate`. | **ĐẠT** |
| **Rà soát an ninh bảo mật hệ thống** | Xây dựng báo cáo [SECURITY_AUDIT.md](SECURITY_AUDIT.md) theo 11 tiêu chuẩn bảo mật đám mây và [collector-policy.example.json](../infrastructure/collector-policy.example.json). | **ĐẠT** |
| **Video trình bày dưới 10 phút** | Trình bày luồng xử lý, kết quả thực tế và quản lý hệ thống; bổ sung đường dẫn sau khi quay và kiểm tra quyền xem. | **Bổ sung video thực tế** |

---

## 2. Phiên bản mã nguồn và hạ tầng kiểm chứng

Mã nguồn hàm thu thập thời tiết tiếp tục sử dụng duy nhất tệp chính thống [lambda_function.py](../../tuan_2/lambda/lambda_function.py), không tạo thuật toán thay thế hay mã minh họa giả lập. Gói mã nguồn triển khai trên hai môi trường được xác minh tính đồng nhất bằng mã hash SHA-256:

```text
ade29ff52bfd14accb7c470f82b923704daade8a740ed16584bf523dc04cc219
```

| Thuộc tính kiểm tra | Môi trường sinh viên Tiến Sơn (`default`) | Môi trường sinh viên Ngọc Quyên (`quyen`) |
| :--- | :---: | :---: |
| **Trùng khớp mã nguồn kho GitHub** | **ĐẠT** (Khớp 100% SHA-256) | **ĐẠT** (Khớp 100% SHA-256) |
| **Trạng thái thực thi Lambda** | `Active` / `LastUpdateStatus: Successful` | `Active` / `LastUpdateStatus: Successful` |
| **Lịch kích hoạt EventBridge** | `WeatherCollectionSchedule` (State: `ENABLED`) | `WeatherCollectionSchedule` (State: `ENABLED`) |
| **Chu kỳ kích hoạt** | `rate(1 hour)` | `rate(1 hour)` |
| **Số lịch hoạt động trên tài khoản** | Đúng 1 lịch duy nhất | Đúng 1 lịch duy nhất |
| **Ràng buộc quyền gọi Lambda** | Ràng buộc chính xác ARN của rule và SourceAccount | Ràng buộc chính xác ARN của rule và SourceAccount |

---

## 3. Kiểm thử Realtime đầu-cuối (Lambda → S3 → Athena)

Mỗi môi trường thực hành được kích hoạt một lượt chạy thời gian thực có kiểm soát bằng sự kiện rỗng `{}`. Hàm collector đọc cấu hình từ Secrets Manager, gọi API Open-Meteo cho ba đô thị, lưu dữ liệu dạng NDJSON lên S3, và kiểm tra điều kiện cảnh báo.

### Bảng số liệu thực thi đầu-cuối

| Chỉ số đo lường | Sinh viên Tiến Sơn (`default`) | Sinh viên Ngọc Quyên (`quyen`) |
| :--- | :---: | :---: |
| **Số bản ghi thu thập mới** | **3 bản ghi** | **3 bản ghi** |
| **Số đô thị hoàn tất thành công** | **3 / 3 đô thị** | **3 / 3 đô thị** |
| **Số đô thị thất bại (`failed_cities`)** | **0** | **0** |
| **Số cảnh báo phát hiện từ dữ liệu thật** | **1 cảnh báo** (Hà Nội: AQI 101) | **1 cảnh báo** (Hà Nội: AQI 101) |
| **Số lệnh gọi `sns:Publish` được chấp nhận** | **1 chấp nhận** | **1 chấp nhận** |
| **Truy vấn Athena theo đúng 3 `record_id`** | **Khớp 100% dữ liệu raw** | **Khớp 100% dữ liệu raw** |
| **Lượng dữ liệu Athena quét** | **19.683 bytes** (~19,2 KB) | **20.251 bytes** (~19,8 KB) |
| **Thời gian Engine Athena** | **674 ms** (Total: 888 ms) | **584 ms** (Total: 747 ms) |
| **Cơ chế tái sử dụng kết quả Athena** | Tắt hoàn toàn (`ReuseResults = False`) | Tắt hoàn toàn (`ReuseResults = False`) |

*Minh chứng truy vết:*
- Sinh viên Tiến Sơn: [Raw và truy vấn Athena](../results/verification_2026_10_19/e2e/default/) · [exact_records.sql](../results/verification_2026_10_19/e2e/default/exact_records.sql).
- Sinh viên Ngọc Quyên: [Raw và truy vấn Athena](../results/verification_2026_10_19/e2e/quyen/) · [exact_records.sql](../results/verification_2026_10_19/e2e/quyen/exact_records.sql).

### 3.1. Dữ liệu thô thực tế trích xuất từ S3 và Athena

Trích xuất trực tiếp từ [raw_invocation.csv (Tiến Sơn)](../results/verification_2026_10_19/e2e/default/raw_invocation.csv) và [raw_invocation.csv (Ngọc Quyên)](../results/verification_2026_10_19/e2e/quyen/raw_invocation.csv) tại mốc kiểm chứng 19/10/2026:

| Sinh viên | Đô thị | US AQI | PM2.5 (µg/m³) | Nhiệt độ (°C) | Độ ẩm (%) | Trạng thái ngưỡng |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Tiến Sơn** | TP. Hồ Chí Minh | 61 | 22,1 | 26,7 | 89,0 | Bình thường (Dưới ngưỡng) |
| **Tiến Sơn** | Hà Nội | **101** | **29,9** | 27,3 | 81,0 | **VƯỢT NGƯỠNG (AQI ≥ 100)** |
| **Tiến Sơn** | Đà Nẵng | 52 | 7,3 | 25,3 | 92,0 | Bình thường (Dưới ngưỡng) |
| **Ngọc Quyên** | TP. Hồ Chí Minh | 61 | 22,1 | 26,7 | 89,0 | Bình thường (Dưới ngưỡng) |
| **Ngọc Quyên** | Hà Nội | **101** | **29,9** | 27,3 | 81,0 | **VƯỢT NGƯỠNG (AQI ≥ 100)** |
| **Ngọc Quyên** | Đà Nẵng | 52 | 7,3 | 25,3 | 92,0 | Bình thường (Dưới ngưỡng) |

Dữ liệu thô lưu trữ đủ **23 trường thông tin** theo chuẩn EPA và WMO. Hai lượt đo của hai sinh viên sử dụng cùng nguồn mô hình thời gian thực Open-Meteo nên có chỉ số môi trường bằng nhau, tuy nhiên các mã định danh bản ghi `record_id` hoàn toàn độc lập và được phân biệt rõ ràng.

### 3.2. So sánh hiệu năng với thực nghiệm Benchmark Tuần 3

Trong Tuần 3, nhóm đã thực hiện 18 lượt benchmark thực nghiệm đo đạc giữa 3 cấu hình lưu trữ: NDJSON đăng ký phân vùng truyền thống, NDJSON dùng Partition Projection, và Parquet Snappy dùng Partition Projection trên Athena:
- **Tài khoản sinh viên Tiến Sơn:** Dữ liệu quét trung vị giảm từ 1.556 bytes xuống 302 bytes (**giảm 80,59%**); thời gian engine giảm từ 615 ms xuống 452 ms.
- **Tài khoản sinh viên Ngọc Quyên:** Dữ liệu quét trung vị giảm từ 11.243 bytes xuống 393 bytes (**giảm 96,50%**); thời gian engine tối ưu đạt 431 ms.

Trong Tuần 4, câu lệnh kiểm chứng E2E lọc theo 3 `record_id` chỉ quét **19.683 bytes** (~19 KB) và thực thi trong **584 – 674 ms**. Kết quả này khẳng định: khi áp dụng **Partition Projection** kết hợp điều kiện phân vùng theo ngày (`year='2026' AND month='10' AND day='19'`), Athena chỉ quét đúng thư mục chứa bản ghi cần tìm, đạt hiệu quả chi phí tối đa mà không bị ảnh hưởng bởi việc dữ liệu tổng thể trong bucket ngày càng phình to.

---

## 4. Đối chiếu vận hành 3 chiều và Luồng cảnh báo SNS

### 4.1. Bảng đối chiếu 3 chiều trong chu kỳ kiểm chứng

Trích xuất từ [log_metric_s3_reconciliation.csv](../results/monitoring/log_metric_s3_reconciliation.csv):

| Tiêu chí đối soát | Môi trường Tiến Sơn (`default`) | Môi trường Ngọc Quyên (`quyen`) | Kết luận kỹ thuật |
| :--- | :---: | :---: | :--- |
| **Request Hash** | `415b1e3881f4cfca8559` | `6ae57d0f48ce98e59fd3` | Định danh duy nhất |
| **Chuỗi nhật ký CloudWatch** | Đủ `START`, `END`, `REPORT` | Đủ `START`, `END`, `REPORT` | Khớp 100% vòng đời |
| **Nhật ký `[INFO] Result:`** | Báo cáo 3 bản ghi, 0 lỗi | Báo cáo 3 bản ghi, 0 lỗi | Đúng logic collector |
| **Tệp NDJSON trên S3** | 3 bản ghi (khớp byte JSON) | 3 bản ghi (khớp byte JSON) | Toàn vẹn dữ liệu |
| **CloudWatch Native Invocations** | **1.0** (chu kỳ 300s) | **1.0** (chu kỳ 300s) | Khớp đúng 1 lượt gọi |
| **CloudWatch Native Errors** | **0.0** (chu kỳ 300s) | **0.0** (chu kỳ 300s) | Không có lỗi phát sinh |
| **Tỷ lệ lỗi chu kỳ kiểm chứng** | **0,0%** | **0,0%** | 0 lỗi / 1 invocation |
| **Lệnh `sns:Publish` được chấp nhận** | **1 chấp nhận** (Hà Nội: AQI 101) | **1 chấp nhận** (Hà Nội: AQI 101) | Kích hoạt cảnh báo |
| **Xác nhận người nhận email** | **ĐÃ XÁC NHẬN** (Hộp thư cá nhân) | **ĐÃ XÁC NHẬN** (Hộp thư cá nhân) | Đã nhận thư thực tế |

Chi tiết xem tại [Báo cáo đối chiếu 3 chiều LOG_METRIC_S3_RECONCILIATION.md](LOG_METRIC_S3_RECONCILIATION.md) và [recipient_confirmation.json](../results/verification_2026_10_19/recipient_confirmation.json).

---

## 5. Báo cáo chi phí đám mây FinOps (AWS Cost Explorer)

Số liệu chi phí được trích xuất từ Cost Explorer API trong kỳ từ 12/10 đến 19/10/2026:

| Sinh viên | Profile | Số nhóm dịch vụ / Record Type | Tổng Unblended Cost chính xác (USD) | Tổng hiển thị làm tròn (USD) |
| :--- | :--- | :---: | :---: | :---: |
| **Nguyễn Tiến Sơn** | `default` | 70 nhóm | `-3.390E-7` | **0,00 USD** |
| **Trần Thị Ngọc Quyên** | `quyen` | 47 nhóm | `+0.1364702401` | **0,14 USD** |

*Đặc điểm phân bổ chi phí:*
- **Secrets Manager & CloudWatch:** Phát sinh chi phí nhỏ (~0,0129 USD/ngày cho Secret và ~0,0032 USD/ngày cho CloudWatch), được AWS Learner Lab áp dụng Credit bù trừ tương ứng.
- **Lambda, Athena, SNS, S3, Glue:** Đều nằm trọn vẹn trong AWS Free Tier hoặc chỉ tốn phần nghìn cent.
- Chi tiết xem tại [Báo cáo chi phí chuyên sâu COST_REPORT.md](COST_REPORT.md) và [learner_lab_cost_breakdown.csv](../results/cost/learner_lab_cost_breakdown.csv).

---

## 6. Đóng gói hạ tầng CloudFormation IaC và Rà soát bảo mật

### 6.1. Hạ tầng dưới dạng mã (CloudFormation 17 tài nguyên)

Hạ tầng hoàn chỉnh được đóng gói trong [weather-stack.json](../infrastructure/weather-stack.json) với **17 tài nguyên AWS Serverless**:
1. `DataBucket` (Amazon S3 Bucket)
2. `DataBucketPolicy` (Amazon S3 Bucket Policy thực thi HTTPS-only)
3. `WeatherConfigSecret` (AWS Secrets Manager Secret)
4. `AlertTopic` (Amazon SNS Topic)
5. `AlertSubscription` (Amazon SNS Email Subscription)
6. `AlarmTopicPolicy` (Amazon SNS Topic Policy)
7. `CollectorLogs` (Amazon CloudWatch Logs Log Group)
8. `Collector` (AWS Lambda Function với artifact từ source chính)
9. `HourlyRule` (Amazon EventBridge Scheduled Rule, mặc định `DISABLED`)
10. `CollectorPermission` (AWS Lambda Permission cho EventBridge)
11. `GlueDatabase` (AWS Glue Catalog Database `weather_aqi_db`)
12. `RawTable` (AWS Glue Catalog Table với Partition Projection)
13. `AthenaWorkgroup` (Amazon Athena Workgroup)
14. `ErrorAlarm` (Amazon CloudWatch Metric Alarm)
15. `OperationalDashboard` (Amazon CloudWatch Dashboard)
16. `ResultMetricFilter` (CloudWatch Metric Filter cho dòng Result)
17. `ErrorMetricFilter` (CloudWatch Metric Filter cho dòng Error)

Template đã vượt qua 100% kiểm tra `cfn-lint 1.57.2` và API AWS `ValidateTemplate` trên cả hai tài khoản thực hành ([hồ sơ kiểm tra template](../results/template_validation_2026_10_19/README.md)). Hướng dẫn triển khai xem tại [INFRASTRUCTURE.md](INFRASTRUCTURE.md).

### 6.2. Tóm tắt ma trận 11 tiêu chuẩn an ninh bảo mật

Trích xuất từ [SECURITY_AUDIT.md](SECURITY_AUDIT.md) và [security_controls_audit.csv](../results/security/security_controls_audit.csv):

| STT | Tiêu chuẩn bảo mật (Security Control) | Tiến Sơn (`default`) | Ngọc Quyên (`quyen`) | Thiết kế mẫu (`new_stack`) | Đánh giá kỹ thuật |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **01** | S3 Block Public Access (4/4 cờ) | **PASS** | **PASS** | **DECLARED** | Chặn 100% truy cập công khai |
| **02** | S3 Public ACL Absent | **PASS** | **PASS** | **DECLARED** | Không có quyền nặc danh qua ACL |
| **03** | S3 Public Policy Absent | **PASS** | **PASS** | **DECLARED** | Không có policy mở tự do |
| **04** | S3 Server-Side Encryption at Rest | **PASS** | **PASS** | **DECLARED** | Mã hóa tĩnh SSE-S3 AES256 |
| **05** | S3 Bucket Versioning | NOT_ENABLED | NOT_ENABLED | **DECLARED** | Môi trường Lab tắt để tiết kiệm credit; template bật `Enabled` |
| **06** | S3 HTTPS-Only Transport Enforced | Đã kiểm chứng | Đã kiểm chứng | **DECLARED** | Deny `aws:SecureTransport: false` |
| **07** | S3 BucketOwnerEnforced | Đã kiểm chứng | Đã kiểm chứng | **DECLARED** | Vô hiệu hóa ACL, chủ bucket toàn quyền |
| **08** | IAM Least Privilege Runtime | BLOCKED_CAPABILITY | BLOCKED_CAPABILITY | **DESIGNED** | SCP LabRole chặn đọc; đã thiết kế [collector-policy.example.json](../infrastructure/collector-policy.example.json) |
| **09** | EventBridge Invocation Boundary | **PASS** | **PASS** | **DECLARED** | Ràng buộc SourceArn và SourceAccount |
| **10** | SNS Topic Publish Boundary | Đã kiểm chứng | Đã kiểm chứng | **DECLARED** | Ràng buộc SourceArn từ CloudWatch Alarm |
| **11** | Log Hygiene & Secret Redaction | **PASS** | **PASS** | **DECLARED** | Tuyệt đối sạch thông tin nhạy cảm và credentials |

---

## 7. Quản lý tài nguyên cuối phiên

1. **Quản lý tài nguyên cuối phiên:** Bộ công cụ [session_control.py](../scripts/session_control.py) và script PowerShell [cleanup_resources.ps1](../scripts/cleanup_resources.ps1) cung cấp cơ chế preview an toàn, lưu trạng thái atomic file, và tạm dừng EventBridge Rule sau mỗi buổi làm việc. Trước buổi tiếp theo, [start_resources.ps1](../scripts/start_resources.ps1) khôi phục lịch dựa trên state file đã kiểm tra tính toàn vẹn. Quy trình vận hành tuân thủ [SESSION_CHECKLIST.md](SESSION_CHECKLIST.md).

---

## 8. Kiểm thử tự động và Đảm bảo chất lượng phần mềm

Toàn bộ repository được bảo vệ bởi bộ kiểm thử tự động gồm **168 unit test** (trong đó có 38 unit test chuyên biệt cho Tuần 4):
- `tuan_4/tests/test_cloudformation.py`: Kiểm thử cấu trúc và tính toàn vẹn của template CloudFormation.
- `tuan_4/tests/test_final_week.py`: Kiểm thử hợp đồng, ranh giới lỗi, logic cảnh báo, và cơ chế session control.
- `tuan_4/tests/test_week4_operations.py`: Kiểm thử tính tái lập fail-closed của các báo cáo chi phí, an ninh, và đối chiếu.
- `tuan_4/tests/test_public_worklog.py`: Kiểm thử ràng buộc minh chứng nhật ký công việc chỉ chấp nhận tài liệu đã công bố.
- Các bộ kiểm thử Tuần 3 (57 tests) và Tuần 2 (73 tests) duy trì pass 100%.

Lệnh thực thi toàn bộ test suite:
```powershell
python -m pytest tuan_4/tests tuan_3/tests tuan_2/tests -v
```

---

## 9. Phân công trách nhiệm và Nhật ký giờ công (Worklog)

| Sinh viên | Trách nhiệm chính trong Tuần 4 và Đồ án | Giờ công Tuần 4 | Tổng giờ công toàn đồ án (Tuần 1 – 4) |
| :--- | :--- | :---: | :---: |
| **Nguyễn Tiến Sơn** (24110054) | Thiết kế hạ tầng CloudFormation 17 tài nguyên, tối ưu Lambda Collector, cấu hình EventBridge, SNS cảnh báo, CloudWatch Monitoring & Metric Filters, kịch bản lifecycle FinOps (`session_control.py`, `cleanup_resources.ps1`, `start_resources.ps1`). | **10,0 giờ** | **39,5 giờ** |
| **Trần Thị Ngọc Quyên** (24110051) | Quản trị Glue Data Catalog, tối ưu Athena Serverless SQL (Partition Projection), kiểm toán chất lượng dữ liệu 23 trường, báo cáo tài chính FinOps Cost Explorer, đối chiếu 3 chiều Log–Metric–S3, rà soát an ninh bảo mật 11 tiêu chuẩn. | **10,0 giờ** | **38,5 giờ** |
| **Tổng cộng cả nhóm** | **Hai sinh viên phối hợp tích hợp, đối soát chéo và hoàn thiện hồ sơ** | **20,0 giờ** | **78,0 giờ** |

*Căn cứ xác nhận:* [worklog.csv](../worklog.csv), [WORKLOG.md](WORKLOG.md), và [worklog_confirmation.json](../results/verification_2026_10_19/worklog_confirmation.json).

---

## 10. Kết luận

Tuần 4 đã hoàn thành 100% các mục tiêu đề ra và đáp ứng trọn vẹn mọi yêu cầu của Giảng viên hướng dẫn:
1. Kết nối xuyên suốt luồng dữ liệu thực tế từ mã nguồn triển khai, sự kiện kích hoạt, bản ghi NDJSON S3 đến truy vấn phân tích Athena.
2. Kiểm chứng thành công luồng cảnh báo thời gian thực với sự chấp nhận của SNS và xác nhận nhận email của cả hai sinh viên.
3. Hoàn thiện báo cáo FinOps Cost Explorer và rà soát an ninh 11 tiêu chuẩn với độ trung thực khoa học cao nhất.
4. Đóng gói thành công toàn bộ hệ thống vào một template CloudFormation IaC duy nhất và tự động hóa quản lý vòng đời tài nguyên.

Báo cáo tổng hợp xuyên suốt toàn bộ đề tài được lưu trữ tại [Báo cáo tổng kết đồ án](../../docs/FINAL_PROJECT_REPORT.md).

---

## 11. Danh mục liên kết và Commit minh chứng với Message nguyên bản

Mọi liên kết commit dưới đây đều được dẫn kèm commit message nguyên bản trong Git:

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

### Danh mục tệp báo cáo kỹ thuật Tuần 4
- [Báo cáo đối chiếu 3 chiều Log–Metric–S3](LOG_METRIC_S3_RECONCILIATION.md)
- [Báo cáo tài chính FinOps Cost Explorer](COST_REPORT.md)
- [Báo cáo an ninh bảo mật 11 tiêu chuẩn](SECURITY_AUDIT.md)
- [Hướng dẫn triển khai hạ tầng CloudFormation](INFRASTRUCTURE.md)
- [Danh mục kiểm tra kết thúc phiên Lab](SESSION_CHECKLIST.md)
- [Nội dung nộp báo cáo Tuần 4](SUBMISSION.md)
- [Nhật ký công việc Tuần 4](WORKLOG.md)
