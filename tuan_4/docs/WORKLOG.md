# Nhật ký Công việc Tuần 4 — Vận hành, Kiểm thử và Hoàn thiện Hồ sơ

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng.  
**Sinh viên thực hiện:**  
- **Nguyễn Tiến Sơn** — MSSV: 24110054 (Phụ trách: Serverless Architecture, CloudFormation IaC, Lambda, EventBridge, CloudWatch, SNS, Security).  
- **Trần Thị Ngọc Quyên** — MSSV: 24110051 (Phụ trách: S3 Data Lake, Athena Partition Projection, Cost Analysis, CI/CD, Testing, Báo cáo & Demo).  

**Lịch thực hiện:** Tuần 4 (26/10/2026 – 01/11/2026).  
**Căn cứ ghi nhận:** **Tổng số giờ theo tuần đã được sinh viên xác nhận**, không phân bổ thời gian tùy tiện.

---

## 1. Tổng hợp Số giờ Toàn bộ Đồ án (Tuần 1 – Tuần 4)

| Tuần thực hiện | Nguyễn Tiến Sơn (24110054) | Trần Thị Ngọc Quyên (24110051) | Tổng cộng nhóm | Trạng thái nghiệm thu | Căn cứ xác nhận |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Tuần 1** | 9.5 giờ | 9.0 giờ | **18.5 giờ** | Đã nghiệm thu | [Báo cáo Tuần 1](../../tuan_1/docs/FINAL_REPORT.md) · [CSV](../../tuan_1/worklog.csv) |
| **Tuần 2** | 10.0 giờ | 9.5 giờ | **19.5 giờ** | Đã nghiệm thu | [Báo cáo Tuần 2](../../tuan_2/docs/FINAL_REPORT.md) · [CSV](../../tuan_2/worklog.csv) |
| **Tuần 3** | 10.0 giờ | 10.0 giờ | **20.0 giờ** | Đã nghiệm thu (ĐẠT) | [Báo cáo Tuần 3](../../tuan_3/docs/FINAL_REPORT.md) · [CSV](../../tuan_3/worklog.csv) |
| **Tuần 4** (Tuần cuối) | 10.0 giờ | 10.0 giờ | **20.0 giờ** | Hoàn thành xuất sắc | [Báo cáo Tuần 4](FINAL_REPORT.md) · [CSV](worklog.csv) |
| **TOÀN BỘ ĐỒ ÁN** | **39.5 giờ** | **38.5 giờ** | **78.0 GIỜ** | **HOÀN TẤT 100%** | [worklog.csv](../../worklog.csv) |

---

## 2. Chi tiết Phân công và Sản phẩm Đầu ra Tuần 4

### 2.1. Sinh viên Nguyễn Tiến Sơn (MSSV: 24110054) — 10.0 Giờ
- **Trách nhiệm chính:**
  1. Thiết kế và triển khai mẫu hạ tầng tự động hóa **AWS CloudFormation IaC** chuẩn production (`tuan_4/iac/cloudformation_stack.yaml` và `cloudformation_stack.json`) với đầy đủ 16 tài nguyên Serverless.
  2. Thực hiện đối chiếu 3 chiều giữa CloudWatch Logs, CloudWatch Native Metrics, Metric Filters (`ResultLogLines`, `ErrorLogLines`) và S3 Data Lake Objects.
  3. Xây dựng bộ công cụ quản lý vòng đời tài nguyên (`cleanup_resources.ps1` và `start_resources.ps1`) phối hợp cùng `session_control.py` để tạm dừng/khôi phục EventBridge Rule ngoài giờ lab.
  4. Thực hiện rà soát an toàn thông tin (Security Audit) theo 5 trụ cột AWS Well-Architected, đánh giá quyền hạn của IAM `LabRole` và đề xuất chính sách quyền tối thiểu chuẩn mực `collector-policy.example.json`.
  5. Biên soạn phần kịch bản demo cho các dịch vụ Lambda, EventBridge, CloudWatch Dashboard và SNS email alerts.
- **Sản phẩm bàn giao:**
  - `tuan_4/iac/cloudformation_stack.yaml`
  - `tuan_4/iac/cloudformation_stack.json`
  - `tuan_4/scripts/cleanup_resources.ps1`
  - `tuan_4/scripts/start_resources.ps1`
  - `tuan_4/scripts/reconcile_ops.py`
  - `tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md`
  - `tuan_4/docs/SECURITY_AUDIT.md`

### 2.2. Sinh viên Trần Thị Ngọc Quyên (MSSV: 24110051) — 10.0 Giờ
- **Trách nhiệm chính:**
  1. Phân tích chi phí vận hành AWS Cost Explorer cho S3, Lambda, Athena, CloudWatch và Secrets Manager trong môi trường AWS Learner Lab.
  2. Lập các kịch bản mô phỏng chi phí (1 tháng, 3 tháng, 6 tháng, 1 năm, 100 đô thị) và các đề xuất tối ưu hóa FinOps.
  3. Xây dựng bộ kiểm thử tự động toàn diện: `test_cloudformation.py` và `test_week4_operations.py`, bảo đảm 100% test cases pass.
  4. Lập ma trận đánh giá 11 kiểm soát an toàn thông tin (`tuan_4/results/security/security_controls_audit.csv`).
  5. Biên soạn kịch bản video demo chi tiết từng phút (dưới 10 phút) tại `tuan_4/docs/VIDEO_DEMO_SCRIPT.md`.
  6. Rà soát, đồng bộ chính xác từng commit message nguyên bản cạnh link commit trong tất cả tài liệu báo cáo theo đúng nhận xét của Thầy hướng dẫn.
- **Sản phẩm bàn giao:**
  - `tuan_4/docs/COST_REPORT.md`
  - `tuan_4/results/cost/learner_lab_cost_breakdown.csv`
  - `tuan_4/results/cost/projected_cost_scenarios.csv`
  - `tuan_4/results/cost/cost_optimization_recommendations.csv`
  - `tuan_4/tests/test_cloudformation.py`
  - `tuan_4/tests/test_week4_operations.py`
  - `tuan_4/results/security/security_controls_audit.csv`
  - `tuan_4/docs/VIDEO_DEMO_SCRIPT.md`

---

## 3. Nhật ký Công việc Kỹ thuật Theo Kế hoạch Tuần 4 (W4-01 – W4-08)

| Mã đầu việc | Nội dung công việc | Người thực hiện | Sản phẩm minh chứng | Đánh giá nghiệm thu |
| :---: | :--- | :--- | :--- | :---: |
| **W4-01** | Đóng gói hạ tầng IaC CloudFormation | Nguyễn Tiến Sơn | `cloudformation_stack.yaml`, `cloudformation_stack.json` | **ĐẠT (PASS)** |
| **W4-02** | Thu thập S3 Data Lake & Kiểm tra chất lượng | Hai sinh viên | `raw/` partitions, NDJSON schema check | **ĐẠT (PASS)** |
| **W4-03** | Đối chiếu CloudWatch Logs – Metrics – S3 | Nguyễn Tiến Sơn | `LOG_METRIC_S3_RECONCILIATION.md`, `log_metric_s3_reconciliation.csv` | **ĐẠT (PASS)** |
| **W4-04** | Kiểm chứng luồng cảnh báo email SNS | Nguyễn Tiến Sơn | Email alerts received, SNS publish verified | **ĐẠT (PASS)** |
| **W4-05** | Thực nghiệm Athena & Hiệu năng Parquet | Trần Thị Ngọc Quyên | Partition Projection metadata, Parquet scan reduction | **ĐẠT (PASS)** |
| **W4-06** | Phân tích chi phí FinOps & AWS Cost Explorer | Trần Thị Ngọc Quyên | `COST_REPORT.md`, 3 bảng CSV chi phí | **ĐẠT (PASS)** |
| **W4-07** | Rà soát An toàn Thông tin & Quyền tối thiểu | Hai sinh viên | `SECURITY_AUDIT.md`, `security_controls_audit.csv` | **ĐẠT (PASS)** |
| **W4-08** | Kịch bản Video Demo (<10p) & Hoàn thiện Hồ sơ | Hai sinh viên | `VIDEO_DEMO_SCRIPT.md`, `FINAL_REPORT.md`, `README.md` | **ĐẠT (PASS)** |

---

## 4. Xác nhận của Sinh viên

- Chúng em xác nhận toàn bộ số giờ làm việc (78.0 giờ) được ghi nhận trung thực dựa trên công sức nghiên cứu, lập trình, kiểm thử và tài liệu hóa thực tế.
- Mọi liên kết, commit hash, số liệu thống kê và minh chứng đều sẵn sàng để Giảng viên hướng dẫn kiểm tra, tái lập và nghiệm thu.
