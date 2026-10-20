# Báo cáo rà soát an ninh và bảo mật hệ thống (11-Control Security Audit)

**Sinh viên thực hiện:**
- Nguyễn Tiến Sơn — MSSV: 24110054
- Trần Thị Ngọc Quyên — MSSV: 24110051

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng
**Mốc kiểm toán:** 19/10/2026. **Phạm vi:** Đối soát thực tế trên hai tài khoản AWS Learner Lab (`default` và `quyen`) kết hợp thẩm định thiết kế mẫu hạ tầng IaC CloudFormation 17 tài nguyên.

---

## 1. Mục tiêu và phương pháp kiểm toán

Báo cáo an ninh này đánh giá hệ thống dựa trên **11 tiêu chuẩn an toàn thông tin đám mây cốt lõi (11 Security Controls)** theo chuẩn kiến trúc AWS Well-Architected Framework (Security Pillar). 

Quy trình đánh giá tuân thủ nguyên tắc **phân định rạch ròi** giữa:
1. **Cấu hình quan sát thực tế (Observed Environment):** Trạng thái an ninh được đọc trực tiếp từ API AWS của hai tài khoản học phần (sinh viên Tiến Sơn và sinh viên Ngọc Quyên).
2. **Thiết kế hạ tầng chuẩn hóa (Declared Template):** Các tiêu chuẩn an ninh tiên tiến được đặc tả trong CloudFormation template chính ([weather-stack.json](../infrastructure/weather-stack.json)).
3. **Giới hạn môi trường học phần (Learner Lab Boundaries):** Nhận diện trung thực các hạn chế quyền hạn nội tại của AWS Academy Learner Lab (ví dụ không thể đọc hoặc chỉnh sửa IAM Role học phần `LabRole`).

---

## 2. Bảng ma trận 11 tiêu chí bảo mật (Security Controls Matrix)

| STT | Tiêu chuẩn bảo mật (Security Control) | Phạm vi đánh giá | Trạng thái sinh viên Tiến Sơn (`default`) | Trạng thái sinh viên Ngọc Quyên (`quyen`) | Trạng thái thiết kế mẫu (`new_stack`) | Bằng chứng kiểm toán |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **01** | **S3 Block Public Access (BPA)** | Observed Environment | **PASS** (4/4 cờ bật) | **PASS** (4/4 cờ bật) | **DECLARED** (Bật toàn diện) | [storage.json (default)](../results/verification_2026_10_19/environment/default/storage.json) · [storage.json (quyen)](../results/verification_2026_10_19/environment/quyen/storage.json) |
| **02** | **S3 Public ACL Absent** | Observed Environment | **PASS** (Không có public ACL) | **PASS** (Không có public ACL) | **DECLARED** (Vô hiệu hóa ACL) | `public_acl: false` trong cả 2 hồ sơ storage |
| **03** | **S3 Public Policy Absent** | Observed Environment | **PASS** (Không có public policy) | **PASS** (Không có public policy) | **DECLARED** (Policy HTTPS-only) | `public_policy: false` trong cả 2 hồ sơ storage |
| **04** | **S3 Default Encryption at Rest** | Observed Environment | **PASS** (SSE-S3 AES256) | **PASS** (SSE-S3 AES256) | **DECLARED** (AES256 bắt buộc) | `encryption_algorithms: ["AES256"]` |
| **05** | **S3 Bucket Versioning** | Observed / Declared | **NOT_ENABLED** (Chưa bật) | **NOT_ENABLED** (Chưa bật) | **DECLARED** (Bật `Enabled`) | Tránh tích lũy chi phí Lab; stack chuẩn bật sẵn |
| **06** | **S3 HTTPS-Only Transport Enforced** | Declared Template | Đã kiểm chứng mẫu policy | Đã kiểm chứng mẫu policy | **DECLARED** (Deny insecure traffic) | `Resources.DataBucketPolicy` trong `weather-stack.json` |
| **07** | **S3 BucketOwnerEnforced (Ownership)** | Declared Template | Mặc định bucket owner | Mặc định bucket owner | **DECLARED** (`BucketOwnerEnforced`) | `OwnershipControls` trong `weather-stack.json` |
| **08** | **IAM Least Privilege Runtime** | Observed / Proposed | **BLOCKED_CAPABILITY** (API Denied) | **BLOCKED_CAPABILITY** (API Denied) | **DESIGNED** (Mẫu quyền tối thiểu) | [role.json](../results/verification_2026_10_19/environment/default/role.json) · [collector-policy.example.json](../infrastructure/collector-policy.example.json) |
| **09** | **EventBridge Invocation Boundary** | Observed Environment | **PASS** (Ràng buộc đúng Rule ARN) | **PASS** (Ràng buộc đúng Rule ARN) | **DECLARED** (Ràng buộc SourceArn) | Resource policy Lambda: `lambda:InvokeFunction` từ Rule |
| **10** | **SNS Alert Topic Publish Boundary** | Declared Template | Đã kích hoạt cho Lambda | Đã kích hoạt cho Lambda | **DECLARED** (Ràng buộc Alarm ARN) | `Resources.AlarmTopicPolicy` trong `weather-stack.json` |
| **11** | **Log Hygiene & Secret Redaction** | Observed Environment | **PASS** (100% sạch dữ liệu nhạy cảm) | **PASS** (100% sạch dữ liệu nhạy cảm) | **DECLARED** (Giữ an toàn mã nguồn) | Rà soát toàn bộ log thực thi và minh chứng GitHub |

---

## 3. Phân tích chuyên sâu 11 tiêu chí bảo mật

### Tiêu chuẩn 1, 2, 3: Bảo vệ lưu trữ S3 chống truy cập công khai
- Cả hai bucket thực hành của sinh viên Tiến Sơn và sinh viên Ngọc Quyên đều bật **đủ cả 4 thiết lập S3 Block Public Access**:
  1. `BlockPublicAcls = True`: Ngăn chặn tạo các ACL công khai mới.
  2. `IgnorePublicAcls = True`: Bỏ qua toàn bộ quyền công khai từ ACL hiện có.
  3. `BlockPublicPolicy = True`: Từ chối các chính sách bucket có nội dung công khai.
  4. `RestrictPublicBuckets = True`: Giới hạn quyền truy cập chỉ cho người dùng được ủy quyền.
- Bucket không có bất kỳ quyền truy cập nặc danh nào qua ACL (`public_acl: false`) hoặc bucket policy (`public_policy: false`). Dữ liệu thô thời tiết và chất lượng không khí được bảo vệ an toàn.

### Tiêu chuẩn 4: Mã hóa dữ liệu tĩnh (Data Encryption at Rest)
- Cấu hình mã hóa mặc định Server-Side Encryption SSE-S3 bằng thuật toán **AES256** được bật 100% trên cả hai môi trường. Mọi tệp dữ liệu NDJSON và kết quả truy vấn Athena lưu trên S3 đều tự động được mã hóa ở tầng vật lý trước khi ghi xuống đĩa.

### Tiêu chuẩn 5: Quản lý phiên bản lưu trữ (S3 Bucket Versioning)
- **Trên môi trường Learner Lab hiện hữu:** Cấu hình được ghi nhận trung thực là `NOT_ENABLED`. Trong môi trường học phần có hạn mức credit 100 USD, việc chưa bật versioning là quyết định có chủ đích nhằm tránh việc tích lũy các phiên bản tệp ghi đè gây lãng phí dung lượng lưu trữ không cần thiết.
- **Trong template CloudFormation chuẩn hóa:** Tài nguyên `DataBucket` được khai báo `VersioningConfiguration.Status: Enabled` để đảm bảo tính bất biến của dữ liệu (data immutability) và khả năng khôi phục sau thảm họa khi triển khai trên môi trường sản xuất thực thụ.

### Tiêu chuẩn 6: Bắt buộc truyền thông mã hóa (HTTPS-Only Transport)
- Trong template [weather-stack.json](../infrastructure/weather-stack.json), tài nguyên `DataBucketPolicy` thiết lập một lệnh `Deny` rõ ràng cho mọi hành động trên bucket nếu yêu cầu không sử dụng giao thức HTTPS bảo mật:
  ```json
  "Condition": {
    "Bool": { "aws:SecureTransport": "false" }
  }
  ```
- Chính sách này bảo đảm dữ liệu truyền tải trên đường truyền (Data in Transit) luôn được mã hóa qua TLS.

### Tiêu chuẩn 7: Kiểm soát quyền sở hữu đối tượng (Object Ownership)
- Template chuẩn hóa kích hoạt thuộc tính `OwnershipControls` với quy tắc `BucketOwnerEnforced`. Thiết lập này vô hiệu hóa hoàn toàn cơ chế ACL truyền thống (vốn tiềm ẩn nguy cơ cấu hình sai) và chuyển toàn bộ quyền quản lý quyền hạn về các chính sách IAM và Bucket Policy tập trung của chủ sở hữu bucket.

### Tiêu chuẩn 8: Nguyên tắc đặc quyền tối thiểu (Least Privilege IAM Role)
- **Thực tế tại AWS Academy Learner Lab:** Do môi trường học phần dùng chung một IAM Role định sẵn là `LabRole`, AWS áp dụng chính sách SCP (Service Control Policy) chặn các lệnh gọi `iam:GetRole`, `iam:GetRolePolicy`, `iam:ListAttachedRolePolicies`. Hệ thống kiểm toán ghi nhận trung thực mã lỗi `AccessDenied` với trạng thái `BLOCKED_CAPABILITY`, không khẳng định sai sự thật rằng LabRole đã được tối thiểu hóa.
- **Giải pháp thiết kế mẫu an toàn:** Nhóm cung cấp tệp chính sách tham khảo hoàn chỉnh [collector-policy.example.json](../infrastructure/collector-policy.example.json). Khi triển khai với vai trò thực thi độc lập (Dedicated Execution Role), chính sách này chỉ cấp 4 quyền tối thiểu tuyệt đối:
  1. `s3:PutObject` trên tiền tố `raw/*` của đúng bucket dự án (không cấp quyền xóa hoặc đọc toàn bộ bucket).
  2. `secretsmanager:GetSecretValue` trên đúng ARN của Secret cấu hình thời tiết (không cấp quyền sửa/xóa Secret).
  3. `sns:Publish` trên đúng ARN của Topic cảnh báo `weather-airquality-alerts`.
  4. `logs:CreateLogStream` và `logs:PutLogEvents` trên Log Group định sẵn của Lambda.

### Tiêu chuẩn 9: Ranh giới kích hoạt EventBridge → Lambda
- Để ngăn chặn việc các rule lạ hoặc tài khoản khác kích hoạt ngoài ý muốn hàm `WeatherCollectorLambda`, chính sách tài nguyên (Resource-based Policy) của Lambda được cấu hình với điều kiện nghiêm ngặt:
  - Hành động: `lambda:InvokeFunction`
  - Principal: `events.amazonaws.com`
  - `SourceArn`: Ràng buộc chính xác ARN của rule `WeatherCollectionSchedule`.
  - `SourceAccount`: Ràng buộc ID tài khoản hiện hành.

### Tiêu chuẩn 10: Ranh giới phát thông điệp cảnh báo SNS (Alarm Topic Boundary)
- Trong template CloudFormation, tài nguyên `AlarmTopicPolicy` cấp quyền cho dịch vụ CloudWatch phát thông báo cảnh báo đến SNS topic, nhưng có ràng buộc điều kiện bắt buộc:
  ```json
  "Condition": {
    "ArnEquals": {
      "aws:SourceArn": { "Fn::GetAtt": ["ErrorAlarm", "Arn"] }
    }
  }
  ```
- Ràng buộc này ngăn ngừa các alarm hoặc dịch vụ khác trong tài khoản phát thông báo rác vào kênh cảnh báo của hệ thống.

### Tiêu chuẩn 11: Vệ sinh nhật ký và che giấu dữ liệu nhạy cảm (Log Hygiene & Redaction)
- Toàn bộ nhật ký thực thi của Lambda trên CloudWatch Logs được kiểm tra kỹ lưỡng:
  - Mã nguồn sử dụng cấu trúc log JSON có cấu trúc `[INFO] Result: ...`, không bao giờ in giá trị chuỗi Secret (tọa độ API key nếu có), thông tin phiên đăng nhập AWS hoặc địa chỉ email cá nhân ra log.
  - Các tệp minh chứng công khai lưu trong repository được tự động lọc bỏ các mã định danh tài khoản nhạy cảm, token xác thực phiên, và URL S3 có chữ ký tạm thời (Presigned URLs).

---

## 4. Tái lập và kiểm toán độc lập

Toàn bộ ma trận kiểm toán an ninh có thể được tái lập và xác minh tính nhất quán thông qua bộ công cụ mã nguồn mở của dự án:

```powershell
# Kiểm tra đối soát ma trận bảo mật đã lưu
python tuan_4/scripts/security_report.py --check

# Xuất lại báo cáo bảo mật ra thư mục kiểm toán độc lập
python tuan_4/scripts/security_report.py --output output/week4-security-audit
```

**Đầu ra đối soát:**
- [Ma trận kiểm toán an ninh bảo mật 16 dòng CSV](../results/security/security_controls_audit.csv)
- Kiểm thử đơn vị tự động đảm bảo các quyền bị từ chối trong LabRole không bao giờ bị dán nhãn sai thành `PASS`: `python -m unittest tuan_4/tests/test_week4_operations.py`.

---

## 5. Tài liệu liên quan

- [Phương pháp rà soát an ninh chi tiết](SECURITY_REVIEW.md)
- [Mẫu chính sách IAM tối thiểu cho Collector](../infrastructure/collector-policy.example.json)
- [Template CloudFormation 17 tài nguyên](../infrastructure/weather-stack.json)
- [Báo cáo tổng kết Tuần 4](FINAL_REPORT.md)
