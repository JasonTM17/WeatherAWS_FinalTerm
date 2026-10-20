# Tuần 4 — Kiểm chứng toàn diện hệ thống, Đóng gói hạ tầng IaC và Chuẩn bị bảo vệ đồ án

**Sinh viên thực hiện:**
- **Nguyễn Tiến Sơn** — MSSV: 24110054
- **Trần Thị Ngọc Quyên** — MSSV: 24110051

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng
**Mốc kiểm chứng kỹ thuật:** 19/10/2026. **Mốc hoàn thiện tài liệu:** 20/10/2026.

---

## 1. Tóm tắt tổng quan (Executive Summary)

Tuần 4 là giai đoạn hoàn thiện tổng kết và kiểm chứng kỹ thuật toàn diện cho toàn bộ đồ án sau khi báo cáo Tuần 3 được GVHD chính thức đánh giá **ĐẠT**.

Trong tuần này, nhóm đã hoàn thành xuất sắc 100% các mục tiêu cốt lõi và nâng cao:
1. **Kiểm thử đầu-cuối có kiểm soát (E2E Testing):** Thực hiện 2 lượt kích hoạt thời gian thực trên hai tài khoản độc lập (`default` của sinh viên Tiến Sơn và `quyen` của sinh viên Ngọc Quyên). Mỗi lượt thu thập đủ 3 bản ghi cho TP.HCM, Hà Nội và Đà Nẵng; đối chiếu khớp 100% giữa tệp NDJSON lưu trên S3 với truy vấn Athena Serverless theo danh sách `record_id`.
2. **Đối chiếu 3 chiều Log – Metric – S3 – Alert:** Khẳng định tính toàn vẹn của hệ thống khi chu kỳ kiểm chứng 300 giây ghi nhận đúng 1 Invocation, 0 Error (tỷ lệ lỗi 0,0%), đầy đủ log vòng đời `START`/`END`/`REPORT`/`[INFO] Result`, 3 bản ghi S3, 1 lệnh gọi `sns:Publish` được chấp nhận (cảnh báo Hà Nội AQI 101), và email cảnh báo đã được xác nhận thực tế tại hộp thư của cả hai sinh viên.
3. **Báo cáo tài chính đám mây FinOps (Cost Explorer):** Phân tích toàn diện 117 nhóm bản ghi chi phí từ Cost Explorer API trong kỳ 12–19/10/2026. Tổng chi phí tài khoản hiển thị làm tròn đạt **0,00 USD** (Tiến Sơn) và **0,14 USD** (Ngọc Quyên) nhờ kiến trúc Serverless và chính sách bù trừ tín dụng Credit của Learner Lab.
4. **Hạ tầng dưới dạng mã CloudFormation (IaC 17 tài nguyên):** Đóng gói trọn vẹn 17 tài nguyên AWS vào một template duy nhất ([weather-stack.json](infrastructure/weather-stack.json)), vượt qua 100% kiểm tra cú pháp với `cfn-lint 1.57.2` và API AWS `ValidateTemplate` trên cả hai tài khoản thực hành.
5. **Rà soát an ninh bảo mật 11 tiêu chuẩn:** Đạt chuẩn 4/4 cờ S3 Block Public Access, mã hóa tĩnh SSE-S3 AES256, thực thi HTTPS bắt buộc, phân tích hạn chế SCP đối với `LabRole`, và cung cấp mẫu IAM Policy tối thiểu cho collector.
6. **Tự động hóa vòng đời tài nguyên cuối phiên:** Xây dựng script `cleanup_resources.ps1` (pause) và `start_resources.ps1` (restore) cùng checklist vận hành giúp tạm dừng EventBridge Rule và bảo toàn ngân sách 100 USD của học phần.
7. **Kịch bản video demo bảo vệ đồ án 09:45:** Kịch bản song thoại chi tiết từng từ cho Nguyễn Tiến Sơn và Trần Thị Ngọc Quyên, kết nối 10 phân đoạn trình bày chuẩn mực dưới 10 phút.
8. **Tổng kết giờ công toàn khóa học:** Hoàn thành **20,0 giờ** Tuần 4 (10,0h mỗi sinh viên); tổng thời gian toàn bộ đồ án đạt **78,0 giờ** đã xác nhận.

---

## 2. Ma trận kết quả chuyển giao (Deliverables Matrix)

| STT | Nội dung chuyển giao | Tệp tài liệu / Minh chứng kỹ thuật | Trạng thái | Lệnh kiểm tra xác thực |
| :---: | :--- | :--- | :---: | :--- |
| **01** | **Báo cáo kỹ thuật chính Tuần 4** | [docs/FINAL_REPORT.md](docs/FINAL_REPORT.md) | **100% HOÀN THÀNH** | Đọc đối soát nội dung |
| **02** | **Văn bản nộp báo cáo LMS** | [docs/SUBMISSION.md](docs/SUBMISSION.md) | **100% HOÀN THÀNH** | Sao chép nộp hệ thống |
| **03** | **Đối chiếu 3 chiều Log–Metric–S3** | [docs/LOG_METRIC_S3_RECONCILIATION.md](docs/LOG_METRIC_S3_RECONCILIATION.md) | **100% HOÀN THÀNH** | `python tuan_4/scripts/reconcile_ops.py --check` |
| **04** | **Báo cáo tài chính FinOps Cost Explorer** | [docs/COST_REPORT.md](docs/COST_REPORT.md) | **100% HOÀN THÀNH** | `python tuan_4/scripts/cost_analysis.py --check` |
| **05** | **Rà soát an ninh bảo mật 11 tiêu chuẩn** | [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md) · [docs/SECURITY_REVIEW.md](docs/SECURITY_REVIEW.md) | **100% HOÀN THÀNH** | `python tuan_4/scripts/security_report.py --check` |
| **06** | **CloudFormation IaC (17 tài nguyên)** | [infrastructure/weather-stack.json](infrastructure/weather-stack.json) · [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) | **100% HOÀN THÀNH** | `cfn-lint infrastructure/weather-stack.json` |
| **07** | **Mẫu IAM Policy tối thiểu** | [infrastructure/collector-policy.example.json](infrastructure/collector-policy.example.json) | **100% HOÀN THÀNH** | Rà soát cấu trúc JSON |
| **08** | **Kịch bản video demo 09:45 song thoại** | [docs/VIDEO_DEMO_SCRIPT.md](docs/VIDEO_DEMO_SCRIPT.md) · [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) | **100% HOÀN THÀNH** | Khớp timeline 9:45 |
| **09** | **Quản lý tài nguyên cuối phiên** | [docs/SESSION_CHECKLIST.md](docs/SESSION_CHECKLIST.md) · [scripts/cleanup_resources.ps1](scripts/cleanup_resources.ps1) | **100% HOÀN THÀNH** | `python tuan_4/scripts/session_control.py pause --help` |
| **10** | **Dữ liệu kiểm chứng trực tiếp** | [results/verification_2026_10_19/README.md](results/verification_2026_10_19/README.md) | **100% HOÀN THÀNH** | `python tuan_4/scripts/verify_results.py` |
| **11** | **Bộ kiểm thử tự động Tuần 4** | [tests/](tests/) (34 test cases) | **PASS 100%** | `python -m unittest discover -s tuan_4/tests -v` |
| **12** | **Nhật ký giờ công Tuần 4 & Tổng thể** | [docs/WORKLOG.md](docs/WORKLOG.md) · [worklog.csv](worklog.csv) | **78,0 giờ ĐÃ XÁC NHẬN** | `python tuan_2/scripts/repository_audit.py --check` |

---

## 3. Chỉ mục điều hướng hồ sơ (Navigation Index)

```
tuan_4/
├── README.md                               # Trang tổng quan Tuần 4 và ma trận chuyển giao
├── worklog.csv                             # Bản ghi thời gian thực hiện Tuần 4 (20.0h)
├── docs/                                   # Tài liệu kỹ thuật chi tiết
│   ├── FINAL_REPORT.md                     # Báo cáo tổng kết toàn diện Tuần 4
│   ├── SUBMISSION.md                       # Văn bản nộp bài có liên kết đầy đủ
│   ├── LOG_METRIC_S3_RECONCILIATION.md     # Báo cáo đối chiếu 3 chiều Log - Metric - S3
│   ├── COST_REPORT.md                      # Báo cáo tài chính đám mây FinOps Cost Explorer
│   ├── SECURITY_AUDIT.md                   # Báo cáo rà soát an ninh bảo mật 11 tiêu chuẩn
│   ├── SECURITY_REVIEW.md                  # Phương pháp đánh giá quyền và an toàn dữ liệu
│   ├── INFRASTRUCTURE.md                   # Hướng dẫn triển khai hạ tầng CloudFormation
│   ├── VIDEO_DEMO_SCRIPT.md                # Kịch bản video demo 09:45 song thoại từng từ
│   ├── DEMO_GUIDE.md                       # Hướng dẫn chi tiết từng bước bấm demo
│   ├── SESSION_CHECKLIST.md                # Danh mục kiểm tra bảo toàn credit cuối phiên
│   ├── VERIFICATION_REPORT.md              # Báo cáo tóm tắt mốc kiểm chứng 19/10
│   └── WORKLOG.md                          # Nhật ký công việc và phân công trách nhiệm
├── infrastructure/                         # Hạ tầng dưới dạng mã (IaC)
│   ├── weather-stack.json                  # Template CloudFormation 17 tài nguyên chuẩn hóa
│   └── collector-policy.example.json       # Mẫu chính sách IAM tối thiểu cho collector
├── scripts/                                # Bộ công cụ tự động hóa vận hành và kiểm toán
│   ├── verify_results.py                   # Xác thực dữ liệu kiểm chứng và template hash
│   ├── cost_analysis.py                    # Phân tích và kiểm toán chi phí Cost Explorer
│   ├── reconcile_ops.py                    # Đối soát 3 chiều Log - Metric - S3
│   ├── security_report.py                  # Tạo ma trận kiểm toán an ninh bảo mật
│   ├── prepare_stack.py                    # Đóng gói artifact và kiểm tra hợp đồng template
│   ├── session_control.py                  # Quản lý trạng thái lịch (preview / pause / restore)
│   ├── cleanup_resources.ps1               # Script PowerShell dọn dẹp tài nguyên cuối phiên
│   ├── start_resources.ps1                 # Script PowerShell khôi phục tài nguyên đầu phiên
│   ├── run_demo_check.py                   # Công cụ kiểm thử trực tiếp luồng Lambda
│   └── verify_environment.py               # Công cụ kiểm tra môi trường AWS
├── results/                                # Kết quả kiểm toán và minh chứng thực thi
│   ├── verification_2026_10_19/            # Dữ liệu kiểm chứng trực tiếp ngày 19/10/2026
│   ├── template_validation_2026_10_19/     # Minh chứng ValidateTemplate API từ AWS
│   ├── cost/                               # Bộ dữ liệu chi phí FinOps (117 bản ghi CSV)
│   ├── monitoring/                         # Bộ dữ liệu đối chiếu 3 chiều CSV & JSON
│   └── security/                           # Ma trận kiểm toán bảo mật 16 dòng CSV
└── tests/                                  # Bộ kiểm thử đơn vị tự động (34 tests)
    ├── test_cloudformation.py              # Kiểm thử cấu trúc CloudFormation
    ├── test_final_week.py                  # Kiểm thử hợp đồng và ranh giới vận hành
    └── test_week4_operations.py            # Kiểm thử tái lập báo cáo fail-closed
```

---

## 4. Hướng dẫn tái lập và kiểm toán ngoại tuyến

Toàn bộ kết quả của Tuần 4 có thể được xác minh hoàn toàn ngoại tuyến mà không cần gọi lại AWS API:

```powershell
# 1. Chạy toàn bộ 34 kiểm thử đơn vị của Tuần 4
python -m unittest discover -s tuan_4/tests -v

# 2. Xác thực tính toàn vẹn của tệp kiểm chứng và template hash
python tuan_4/scripts/verify_results.py

# 3. Kiểm toán báo cáo tài chính FinOps Cost Explorer
python tuan_4/scripts/cost_analysis.py --check

# 4. Kiểm toán dữ liệu đối chiếu 3 chiều Log - Metric - S3
python tuan_4/scripts/reconcile_ops.py --check

# 5. Kiểm toán ma trận an ninh bảo mật 11 tiêu chuẩn
python tuan_4/scripts/security_report.py --check

# 6. Kiểm tra cú pháp template CloudFormation
cfn-lint tuan_4/infrastructure/weather-stack.json --regions us-east-1

# 7. Kiểm toán toàn diện kho lưu trữ (liên kết, worklog, CSV catalog)
python tuan_2/scripts/repository_audit.py --check
```

---

## 5. Liên kết hệ thống

- [Trang chủ Đồ án](../README.md)
- [Báo cáo tổng kết đồ án toàn diện (Tuần 1 – Tuần 4)](../docs/FINAL_PROJECT_REPORT.md)
- [Báo cáo nộp bài tổng kết](../BAO_CAO.md)
- [Hồ sơ Tuần 3](../tuan_3/README.md) · [Hồ sơ Tuần 2](../tuan_2/README.md) · [Hồ sơ Tuần 1](../tuan_1/README.md)
- [Quy trình kiểm thử tự động GitHub Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml)
