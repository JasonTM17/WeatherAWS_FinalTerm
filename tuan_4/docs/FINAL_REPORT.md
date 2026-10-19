# Báo cáo Tổng kết Tuần 4 — Vận hành, Kiểm thử Toàn diện và Hoàn thiện Hồ sơ Đồ án

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05  
**Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng  
**Sinh viên thực hiện:**  
1. **Nguyễn Tiến Sơn** — MSSV: 24110054 (Vai trò: Serverless Architecture, CloudFormation IaC, Lambda, EventBridge, CloudWatch, SNS, Security)  
2. **Trần Thị Ngọc Quyên** — MSSV: 24110051 (Vai trò: S3 Data Lake, Athena Partition Projection, Cost Analysis, CI/CD, Testing, Báo cáo & Demo)  

**Mốc tích hợp:** Tuần 4 (26/10/2026 – 01/11/2026) · **Nền tảng:** AWS Academy Learner Lab (`us-east-1`)  
**Kho mã nguồn GitHub:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm)

---

## 1. Giới thiệu và Mục tiêu Tuần 4

Tuần 4 là tuần kết thúc của đồ án **"Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS"**. Dựa trên nền tảng tích hợp đã đạt đánh giá **ĐẠT** ở Tuần 3 và bám sát các chỉ đạo tại nhận xét của ThS. Huỳnh Xuân Phụng:
1. **Kiểm thử tổng thể và đối chiếu 3 chiều Log – Metric – S3 Data Lake:** Chứng minh tính toàn vẹn dữ liệu, không có bản ghi mồ côi (orphan) và không có lượt gọi ảo (phantom).
2. **Báo cáo chi phí vận hành chi tiết qua AWS Cost Explorer:** Phân tích từng dịch vụ serverless, mô phỏng các kịch bản dài hạn và đề xuất giải pháp FinOps.
3. **Quản lý vòng đời tài nguyên sau buổi lab:** Xây dựng bộ công cụ dừng và kích hoạt tài nguyên an toàn (`cleanup_resources.ps1`, `start_resources.ps1`), bảo toàn 100% credit được cấp trong AWS Learner Lab.
4. **Yêu cầu nâng cao (IaC & Security Audit):**
   - Đóng gói toàn bộ kiến trúc Serverless bằng một mẫu **AWS CloudFormation** hoàn chỉnh (`tuan_4/iac/cloudformation_stack.yaml` và `.json`).
   - Thực hiện đợt rà soát an toàn thông tin chuyên sâu (S3 Block Public Access 100%, phân tích quyền tối thiểu cho IAM LabRole).
5. **Đồng bộ commit message nguyên bản:** Ghi đúng chính xác từng commit message thật bên cạnh link commit theo đúng góp ý của Thầy.
6. **Xây dựng kịch bản video demo dưới 10 phút:** Thiết lập kế hoạch ghi hình chi tiết từng phút cho cả hai sinh viên.

---

## 2. Kiến trúc Hạ tầng Tự động hóa IaC (AWS CloudFormation)

Thực hiện yêu cầu nâng cao, toàn bộ hệ thống được tự động hóa thông qua mẫu CloudFormation chuẩn hóa tại [`tuan_4/iac/cloudformation_stack.yaml`](../iac/cloudformation_stack.yaml) và [`tuan_4/iac/cloudformation_stack.json`](../iac/cloudformation_stack.json), khởi tạo đồng bộ **16 tài nguyên AWS**:

```
[ Amazon EventBridge ] (Schedule Rule: cron(0 * * * ? *))
          │
          ▼ (lambda:InvokeFunction Permission)
[ AWS Lambda Function ] (Python 3.12, 256MB, LabRole)
   ├── Read Config ────► [ AWS Secrets Manager ] (weather-aqi-config)
   ├── Stream Logs ────► [ CloudWatch Logs ] ──► [ Metric Filters: ResultLogLines / ErrorLogLines ]
   │                                                    │
   │                                                    ▼
   │                                             [ CloudWatch Alarm ] ──► [ Amazon SNS ] ──► [ Email Alerts ]
   │                                                    │
   │                                                    ▼
   │                                             [ CloudWatch Dashboard ] (FullStack Telemetry)
   │
   └── Store Raw NDJSON ─► [ Amazon S3 Data Lake ] (AES-256, 100% Block Public Access, TLS 1.3 Deny)
                                  │
                                  ▼
                           [ AWS Glue Catalog ] (Database: weather_aqi_db)
                                  │
                                  ▼
                           [ Amazon Athena Table ] (Partition Projection + Parquet Snappy + 10MB Cutoff)
```

### Các thành phần chính trong Stack:
1. **Lưu trữ S3 Data Lake (`AWS::S3::Bucket`, `AWS::S3::BucketPolicy`):**
   - Bật đầy đủ 4 cờ `PublicAccessBlockConfiguration` (BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, RestrictPublicBuckets).
   - Mã hóa mặc định `SSEAlgorithm: AES256`. Bật `VersioningConfiguration: Status=Enabled`.
   - Bucket Policy ép buộc TLS: Từ chối (`Deny`) mọi truy cập có `aws:SecureTransport: false`.
2. **Cấu hình Bí mật (`AWS::SecretsManager::Secret`):**
   - Quản lý tập trung tọa độ 3 đô thị (TP. Hồ Chí Minh, Hà Nội, Đà Nẵng) và ngưỡng ô nhiễm (`PM2.5 >= 35.5`, `US AQI >= 100`).
3. **Cảnh báo (`AWS::SNS::Topic`, `AWS::SNS::Subscription`):**
   - Phân phối thông báo ô nhiễm tức thời tới email người nhận.
4. **Xử lý Tính toán (`AWS::Lambda::Function`):**
   - Runtime Python 3.12, IAM LabRole, timeout 60s, RAM 256MB, tích hợp biến môi trường trỏ tới S3, Secrets Manager và SNS.
5. **Kích hoạt Lịch trình (`AWS::Events::Rule`, `AWS::Lambda::Permission`):**
   - EventBridge Scheduler kích hoạt mỗi giờ; cấp quyền gọi hàm có điều kiện ràng buộc SourceArn và SourceAccount.
6. **Danh mục Dữ liệu & Phân tích (`AWS::Glue::Database`, `AWS::Glue::Table`, `AWS::Athena::WorkGroup`):**
   - Bảng phân tích với **Partition Projection** cho các khóa `year`, `month`, `day`.
   - WorkGroup Athena kích hoạt mã hóa `SSE_S3` và rào chắn chi phí `BytesScannedCutoffPerQuery: 10485760` (10 MB).
7. **Giám sát & Telemetry (`AWS::Logs::LogGroup`, `AWS::Logs::MetricFilter`, `AWS::CloudWatch::Alarm`, `AWS::CloudWatch::Dashboard`):**
   - Lưu trữ log 14 ngày.
   - Hai Metric Filters: `ResultLogLines` (bắt mẫu `"Result:"`) và `ErrorLogLines` (bắt mẫu `"[ERROR]"`).
   - CloudWatch Alarm kích hoạt SNS khi phát hiện lỗi; Dashboard giám sát thời gian thực.

Mẫu CloudFormation đã được kiểm thử tự động đạt 100% PASS qua [`tuan_4/tests/test_cloudformation.py`](../tests/test_cloudformation.py).

---

## 3. Đối chiếu Ba Chiều: Log – Metric – S3 Data Lake

Báo cáo đối chiếu chi tiết tại [`tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md`](LOG_METRIC_S3_RECONCILIATION.md) và tập dữ liệu [`tuan_4/results/monitoring/log_metric_s3_reconciliation.csv`](../results/monitoring/log_metric_s3_reconciliation.csv) chứng minh:
- **14/14 phiên kích hoạt hoàn tất:** Khớp chính xác giữa CloudWatch Logs (`START RequestId` -> `[INFO] Result:` -> `REPORT RequestId`), chỉ số hạ tầng `AWS/Lambda Invocations = 1`, bộ đếm log filter `ResultLogLines = 1` và đối tượng vật lý trên S3.
- **Không có đối tượng S3 mồ côi (0 Orphan S3 Objects):** Mọi file NDJSON trên S3 đều truy vết được về đúng 1 request ID xác định.
- **Không có lượt gọi ảo (0 Phantom Invocations):** Toàn bộ các lần đếm metric đều đi kèm log thực thi và dữ liệu S3 hợp lệ.
- **Độ chính xác dữ liệu 100%:** Mỗi tệp S3 lưu trữ chính xác 3 bản ghi cho 3 đô thị với đầy đủ 23 trường lược đồ.
- **Tỷ lệ khớp toàn diện:** **100.0%**.

---

## 4. Báo cáo Chi phí AWS Cost Explorer & FinOps

Báo cáo chi phí chi tiết tại [`tuan_4/docs/COST_REPORT.md`](COST_REPORT.md) và các bảng dữ liệu [`tuan_4/results/cost/`](../results/cost/) ghi nhận:
- **Chi phí thực tế hàng tháng:** **$0.4037 USD / tháng**.
  - **AWS Secrets Manager ($0.4036/tháng):** Chiếm 99.97% tổng hóa đơn (phí cố định $0.40 cho 1 secret lưu trữ).
  - **Amazon Athena ($0.0001/tháng):** Nhờ Partition Projection và nén Parquet Snappy, dung lượng quét mỗi truy vấn giảm từ 11.2 KB xuống còn 393 byte (giảm 96.5%), giữ chi phí Athena ở mức siêu nhỏ.
  - **AWS Lambda, Amazon S3, Amazon CloudWatch, Amazon SNS ($0.0000/tháng):** Toàn bộ lưu lượng và thời gian tính toán được bao phủ 100% bởi AWS Always-Free Tier.
- **Đánh giá ngân sách Learner Lab:**
  - Hoạt động trọn vẹn cả học kỳ (3 tháng) chỉ tiêu tốn **$1.21 USD** (tương đương **2.42%** hạn mức $50 được cấp), đảm bảo tài khoản sinh viên không bao giờ bị khóa vì lý do chi phí.
- **Khuyến nghị FinOps:**
  - Có thể chuyển Secrets Manager sang **AWS Systems Manager Parameter Store** (Standard Parameter) để đạt chi phí **$0.00/tháng (tiết kiệm 99.1%)**.

---

## 5. Quản lý Vòng đời Tài nguyên (Resource Lifecycle Scripts)

Nhằm bảo tồn tối đa credit trong AWS Learner Lab khi sinh viên không trong phiên thực hành, nhóm đã phát triển hai kịch bản PowerShell:
- [`tuan_4/scripts/cleanup_resources.ps1`](../scripts/cleanup_resources.ps1): Tạm dừng (`PAUSE/DISABLE`) EventBridge Rule thu thập định kỳ thông qua `session_control.py`, lưu trữ trạng thái vào state file an toàn riêng tư, bảo toàn 100% dữ liệu đã thu thập trên S3 Data Lake.
- [`tuan_4/scripts/start_resources.ps1`](../scripts/start_resources.ps1): Khôi phục (`RESTORE/ENABLE`) EventBridge Rule từ state file đã kiểm chứng khi sinh viên bắt đầu phiên thực hành mới.

---

## 6. Rà soát An toàn Thông tin (Security Audit)

Báo cáo an toàn thông tin chuyên sâu tại [`tuan_4/docs/SECURITY_AUDIT.md`](SECURITY_AUDIT.md) và ma trận kiểm soát [`tuan_4/results/security/security_controls_audit.csv`](../results/security/security_controls_audit.csv) đánh giá **11/11 tiêu chí đạt PASS**:
1. **S3 Block Public Access:** Đạt 100% trên cả 4 thiết lập bảo vệ chống rò rỉ dữ liệu công khai.
2. **Mã hóa Truyền tải (TLS 1.3):** Bucket Policy từ chối mọi yêu cầu không bảo mật (`aws:SecureTransport: false`).
3. **Mã hóa Lưu trữ (At-Rest):** Mã hóa tự động bằng SSE-S3 AES-256 trên S3 và SSE_S3 trên Athena WorkGroup.
4. **Phân tích Quyền hạn IAM LabRole & Giải pháp Least-Privilege:** Nhận diện LabRole của Learner Lab có quyền rộng, nhóm đã thiết kế chính sách quyền tối thiểu chuẩn mực tại [`tuan_4/infrastructure/collector-policy.example.json`](../infrastructure/collector-policy.example.json) chỉ cấp đúng 5 quyền tối thiểu trên các ARN tài nguyên xác định.
5. **Vệ sinh Khóa bí mật (Secrets Hygiene):** Quét sạch 100% kho mã nguồn, không commit bất kỳ thông tin nhạy cảm hay API keys nào lên Git (xác thực qua test case `test_security_cleanliness_no_plaintext_credentials`).
6. **Khử định danh Nhật ký:** Làm sạch Request ID và các thông tin định danh trong CloudWatch Logs.
7. **Rào chắn Chi phí Athena:** Giới hạn 10 MB quét tối đa mỗi câu lệnh SELECT nhằm ngăn ngừa tấn công hoặc lỗi quét cạn dung lượng.

---

## 7. Đồng bộ Commit Message Nguyên bản Theo Chỉ đạo của GVHD

Thực hiện đúng yêu cầu của Giảng viên hướng dẫn: *"Tuần sau em ghi luôn message thật của commit cạnh link, đọc là hiểu và thầy cũng kiểm tra nhanh hơn"*, nhóm đã đối chiếu và cập nhật chính xác từng thông điệp commit nguyên bản:

| Commit Hash | Thông điệp Commit Thật (Exact Real Commit Message) | Liên kết GitHub Trực tiếp |
| :---: | :--- | :--- |
| **`0b26858`** | `feat(week3): add measured Athena experiments, monitoring and guarded CD` | [Commit 0b26858](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e) |
| **`c28da19`** | `fix(cd): make Lambda archive identical across Windows and Linux` | [Commit c28da19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356) |
| **`62f1c08`** | `fix(lambda): collect completed current-day hours in backfill` | [Commit 62f1c08](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650) |
| **`9471ec3`** | `docs(week3): add authenticated October 19 data and final submission review` | [Commit 9471ec3](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/9471ec36437d80df3f81e19d7d10da5adbb9da0b) |
| **`d513f21`** | `docs(week3): link verified data CI and current release baseline` | [Commit d513f21](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/d513f21774e1d752aa40e791e8139589d97a618e) |
| **`fa67191`** | `docs(week4): detail next-week plan and refine submission reports` | [Commit fa67191](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/fa67191eb946e300959247cead8f903a4531d044) |
| **`5047515`** | `docs(week3): use dates in submission narrative` | [Commit 5047515](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/50475156a0eecfe33486df815a5f6e80b435ff51) |
| **`e497754`** | `feat(week4): implement CloudFormation IaC, security audit, log-metric-S3 reconciliation, and video demo script` | [Commit e497754](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e49775409593296fbe14ed0474e4e5cb2f930c36) |

---

## 8. Kịch bản Video Demo (Dưới 10 Phút)

Kịch bản chi tiết từng phút được trình bày tại [`tuan_4/docs/VIDEO_DEMO_SCRIPT.md`](VIDEO_DEMO_SCRIPT.md), phân chia vai trò rõ ràng giữa hai sinh viên:
- **00:00 – 01:30:** Giới thiệu nhóm và tổng quan kiến trúc Serverless 5 phân tầng (Slide).
- **01:30 – 03:30:** Demo Amazon S3 Data Lake và Athena Partition Projection, minh chứng giảm 96.5% byte quét của Parquet.
- **03:30 – 05:30:** Demo Lambda Function, EventBridge Scheduler và thực thi thu thập thời gian thực, xem log CloudWatch.
- **05:30 – 07:00:** Demo CloudWatch Dashboard (Invocations, Duration, Metric Filters) và kiểm chứng email cảnh báo từ Amazon SNS.
- **07:00 – 08:30:** Demo yêu cầu nâng cao: CloudFormation IaC Stack 16 tài nguyên và Báo cáo Rà soát An toàn Thông tin.
- **08:30 – 10:00:** Demo kho mã nguồn GitHub, kết quả CI/CD Actions, chạy bộ test tự động 100% PASS trên terminal, và tổng kết chi phí AWS.

---

## 9. Phân công Công việc và Nhật ký Hoạt động (78.0 Giờ)

Tổng thời gian làm việc toàn bộ đồ án đã được xác nhận là **78.0 giờ**:
- **Nguyễn Tiến Sơn (24110054):** 39.5 giờ (Tuần 1: 9.5h, Tuần 2: 10.0h, Tuần 3: 10.0h, Tuần 4: 10.0h).
- **Trần Thị Ngọc Quyên (24110051):** 38.5 giờ (Tuần 1: 9.0h, Tuần 2: 9.5h, Tuần 3: 10.0h, Tuần 4: 10.0h).
- Chi tiết nhật ký công việc được lưu tại [`tuan_4/docs/WORKLOG.md`](WORKLOG.md), [`tuan_4/worklog.csv`](../worklog.csv) và [`worklog.csv`](../../worklog.csv).

---

## 10. Kết luận Toàn diện Đồ án

1. **Hoàn thành 100% mục tiêu môn học:** Xây dựng thành công hệ thống thu thập và phân tích dữ liệu lớn thời tiết & chất lượng không khí trên AWS hoàn toàn tự động, bền vững và có tính ứng dụng cao.
2. **Đáp ứng xuất sắc các yêu cầu nâng cao:**
   - Đóng gói toàn bộ hệ thống bằng mẫu **AWS CloudFormation IaC** chuẩn mực.
   - Rà soát an toàn thông tin theo chuẩn **AWS Well-Architected Security**, đạt 100% Block Public Access và thiết kế chính sách quyền tối thiểu chặt chẽ.
3. **Tối ưu hóa FinOps vượt bậc:** Vận hành toàn bộ hệ thống với chi phí chưa tới $1.22 USD cho cả học kỳ, bảo toàn tuyệt đối ngân sách AWS Academy Learner Lab.
4. **Chất lượng kỹ thuật cấp sản xuất:** Toàn bộ mã nguồn có cấu trúc rõ ràng, kiểm thử tự động hơn 120 test cases đạt 100% PASS, tài liệu hóa minh chứng đầy đủ và đồng bộ commit message nguyên bản.
