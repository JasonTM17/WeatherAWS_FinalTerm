# Tuần 4 — Vận hành, Đánh giá, IaC CloudFormation và Hoàn thiện Hồ sơ Đồ án

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05  
**Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng  
**Sinh viên thực hiện:** Nguyễn Tiến Sơn (MSSV: 24110054) và Trần Thị Ngọc Quyên (MSSV: 24110051)  
**Thời gian thực hiện:** Tuần 4 (26/10/2026 – 01/11/2026) · **Trạng thái:** Hoàn thành xuất sắc 100%

---

## 1. Tổng quan Kết quả Tuần 4

Tuần 4 là tuần tổng kết và nghiệm thu toàn bộ đồ án **Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS**. Nhóm đã hoàn thành toàn bộ các đầu việc theo kế hoạch [`docs/WEEK_4_PLAN.md`](../docs/WEEK_4_PLAN.md) và đáp ứng xuất sắc các yêu cầu nâng cao của Giảng viên hướng dẫn:

- **Hạ tầng dưới dạng mã nguồn (IaC):** Đóng gói toàn bộ kiến trúc Serverless bằng mẫu **AWS CloudFormation** hoàn chỉnh ([`tuan_4/iac/cloudformation_stack.yaml`](iac/cloudformation_stack.yaml) và [`.json`](iac/cloudformation_stack.json)) khởi tạo đồng bộ 16 tài nguyên.
- **Rà soát An toàn Thông tin (Security Audit):** Rà soát chuyên sâu 11 kiểm soát an toàn theo chuẩn AWS Well-Architected, bảo đảm 100% S3 Block Public Access, mã hóa TLS 1.3 và SSE-S3, cùng chính sách quyền tối thiểu cho IAM LabRole ([`tuan_4/docs/SECURITY_AUDIT.md`](docs/SECURITY_AUDIT.md)).
- **Đối chiếu 3 chiều Log – Metric – S3:** Xác nhận tính toàn vẹn 100% giữa CloudWatch Logs, chỉ số Native Metrics, bộ đếm Metric Filters và đối tượng S3 Data Lake; không có bản ghi mồ côi và không có lượt gọi ảo ([`tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md`](docs/LOG_METRIC_S3_RECONCILIATION.md)).
- **Báo cáo Chi phí AWS Cost Explorer:** Phân tích chi tiết từng dịch vụ trong AWS Learner Lab, chứng minh chi phí vận hành chỉ **$0.4037 USD / tháng** (tiêu tốn chưa tới 2.5% hạn mức được cấp cho cả học kỳ) ([`tuan_4/docs/COST_REPORT.md`](docs/COST_REPORT.md)).
- **Quản lý Vòng đời Tài nguyên:** Cung cấp script PowerShell [`cleanup_resources.ps1`](scripts/cleanup_resources.ps1) và [`start_resources.ps1`](scripts/start_resources.ps1) giúp tạm dừng EventBridge rule ngoài giờ lab để bảo tồn credit Learner Lab.
- **Kịch bản Video Demo dưới 10 phút:** Thiết lập kế hoạch ghi hình chi tiết từng phút, phân vai rõ ràng cho 2 sinh viên ([`tuan_4/docs/VIDEO_DEMO_SCRIPT.md`](docs/VIDEO_DEMO_SCRIPT.md)).
- **Đồng bộ Commit Message nguyên bản:** Toàn bộ liên kết commit trong tài liệu được ghi đúng chính xác từng commit message thật bên cạnh link theo đúng góp ý của Thầy.
- **Nhật ký công việc hoàn tất:** Bổ sung 20.0 giờ Tuần 4, nâng tổng thời gian toàn bộ đồ án lên **78.0 giờ đã xác nhận** ([`tuan_4/docs/WORKLOG.md`](docs/WORKLOG.md) và [`tuan_4/worklog.csv`](worklog.csv)).

---

## 2. Bản đồ Thư mục và Điều hướng Tài liệu Tuần 4

```
tuan_4/
├── README.md                                  # Tài liệu tổng quan Tuần 4 (tệp hiện tại)
├── worklog.csv                                # Bảng CSV tổng hợp 20.0 giờ Tuần 4 đã xác nhận
├── docs/                                      # Tài liệu báo cáo kỹ thuật Tuần 4
│   ├── FINAL_REPORT.md                        # Báo cáo tổng kết toàn diện Tuần 4 và đồ án
│   ├── LOG_METRIC_S3_RECONCILIATION.md        # Báo cáo đối chiếu 3 chiều Log – Metric – S3
│   ├── COST_REPORT.md                         # Báo cáo chi phí vận hành AWS Cost Explorer
│   ├── SECURITY_AUDIT.md                      # Báo cáo rà soát an toàn thông tin (Security Audit)
│   ├── VIDEO_DEMO_SCRIPT.md                   # Kịch bản chi tiết video demo dưới 10 phút
│   ├── WORKLOG.md                             # Nhật ký công việc và phân công nhiệm vụ Tuần 4
│   └── worklog.csv                            # Bản sao lưu worklog trong thư mục docs
├── iac/                                       # Hạ tầng dưới dạng mã nguồn (CloudFormation IaC)
│   ├── cloudformation_stack.yaml              # Template CloudFormation YAML chuẩn production
│   └── cloudformation_stack.json              # Template CloudFormation JSON tương đương
├── infrastructure/                            # Cấu hình chính sách bổ trợ
│   ├── collector-policy.example.json          # IAM Least-Privilege Policy cho Lambda Collector
│   └── weather-stack.json                     # Template stack bổ trợ cho môi trường lab
├── scripts/                                   # Kịch bản tự động hóa và điều phối vận hành
│   ├── cleanup_resources.ps1                  # Kịch bản tạm dừng tài nguyên bảo toàn credit lab
│   ├── start_resources.ps1                    # Kịch bản kích hoạt lại tài nguyên cho phiên lab mới
│   ├── session_control.py                     # Điều khiển trạng thái EventBridge rule với state file
│   ├── prepare_stack.py                       # Đóng gói và kiểm tra hợp đồng CloudFormation
│   ├── reconcile_ops.py                       # Trích xuất và đối chiếu log-metric-S3
│   ├── cost_analysis.py                       # Tính toán và xuất dữ liệu chi phí AWS
│   ├── run_demo_check.py                      # Kích hoạt thực thi 1 lượt và kiểm tra SELECT Athena
│   └── verify_environment.py                  # Thu thập và xác minh toàn diện môi trường AWS
├── results/                                   # Dữ liệu kết quả thực nghiệm và đối chiếu
│   ├── monitoring/
│   │   ├── log_metric_s3_reconciliation.csv   # Dữ liệu đối chiếu 14 lượt thu thập hoàn tất
│   │   └── reconciliation_summary.json        # Tổng kết chỉ số đối chiếu (100% Khớp)
│   ├── cost/
│   │   ├── learner_lab_cost_breakdown.csv     # Bảng phân tích chi phí từng dịch vụ AWS
│   │   ├── projected_cost_scenarios.csv       # Kịch bản dự báo chi phí 1 tháng đến 1 năm
│   │   └── cost_optimization_recommendations.csv # Đề xuất tối ưu hóa chi phí FinOps
│   └── security/
│       └── security_controls_audit.csv        # Ma trận đánh giá 11 kiểm soát an toàn thông tin
└── tests/                                     # Bộ kiểm thử tự động Tuần 4
    ├── test_cloudformation.py                 # Kiểm thử cú pháp và thuộc tính CloudFormation
    ├── test_week4_operations.py               # Kiểm thử đối chiếu, chi phí và kịch bản vận hành
    └── test_final_week.py                     # Kiểm thử hợp đồng môi trường và biên thất bại
```

---

## 3. Lệnh Tái lập và Kiểm thử Tự động

Để thực hiện kiểm tra toàn bộ kết quả Tuần 4 từ thư mục gốc repository:

```bash
# 1. Kiểm thử toàn bộ unit tests của Tuần 4 (42 test cases):
py -3.14 -m unittest discover -s tuan_4/tests -v

# 2. Chạy kịch bản tái lập đối chiếu log-metric-S3:
py -3.14 tuan_4/scripts/reconcile_ops.py

# 3. Chạy kịch bản phân tích chi phí AWS Cost Explorer:
py -3.14 tuan_4/scripts/cost_analysis.py

# 4. Kiểm thử đóng gói CloudFormation và hợp đồng tài nguyên:
py -3.14 tuan_4/scripts/prepare_stack.py --output output/test_build

# 5. Kiểm thử toàn bộ các bài test chấp nhận E2E của repository:
py -3.14 -m unittest discover -s tests -v
```

---

## 4. Danh mục Commit Minh chứng với Message Nguyên bản

Tuân thủ nghiêm ngặt chỉ đạo của Giảng viên hướng dẫn:

- **[`0b26858`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e)** — `feat(week3): add measured Athena experiments, monitoring and guarded CD`
- **[`c28da19`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356)** — `fix(cd): make Lambda archive identical across Windows and Linux`
- **[`62f1c08`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650)** — `fix(lambda): collect completed current-day hours in backfill`
- **[`9471ec3`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/9471ec36437d80df3f81e19d7d10da5adbb9da0b)** — `docs(week3): add authenticated October 19 data and final submission review`
- **[`d513f21`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/d513f21774e1d752aa40e791e8139589d97a618e)** — `docs(week3): link verified data CI and current release baseline`
- **[`fa67191`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/fa67191eb946e300959247cead8f903a4531d044)** — `docs(week4): detail next-week plan and refine submission reports`
- **[`5047515`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/50475156a0eecfe33486df815a5f6e80b435ff51)** — `docs(week3): use dates in submission narrative`
- **[`e497754`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e49775409593296fbe14ed0474e4e5cb2f930c36)** — `feat(week4): implement CloudFormation IaC, security audit, log-metric-S3 reconciliation, and video demo script`
