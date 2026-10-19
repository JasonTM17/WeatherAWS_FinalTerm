# Báo cáo Rà soát An toàn Thông tin — Security Audit (Tuần 4)

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng.  
**Sinh viên thực hiện:** Nguyễn Tiến Sơn (MSSV: 24110054) và Trần Thị Ngọc Quyên (MSSV: 24110051).  
**Mốc thực hiện:** Tuần 4 (26/10/2026 – 01/11/2026) · **Tiêu chuẩn:** AWS Well-Architected Security Pillar.

---

## 1. Bối cảnh và Mục tiêu Rà soát

Theo định hướng nâng cao của Giảng viên hướng dẫn:
> *"Yêu cầu nâng cao (nếu tuần 4 còn thời gian): đề tài khuyến khích tự động hóa/IaC — hai em nên gói toàn bộ stack bằng một CloudFormation template và làm một lượt rà bảo mật ngắn (S3 Block Public Access, quyền tối thiểu cho LabRole). Phần này làm xong thì khi vấn đáp em trả lời tự tin hơn rất nhiều."*

Báo cáo này tiến hành rà soát an toàn thông tin toàn diện trên toàn bộ kiến trúc Serverless đã triển khai, bao gồm:
1. **Kiểm tra ngăn chặn rò rỉ dữ liệu công khai trên S3 (Block Public Access 100%).**
2. **Đánh giá quyền hạn thực thi của IAM LabRole và giải pháp quyền tối thiểu (Least-Privilege).**
3. **Mã hóa dữ liệu khi truyền tải (In-Transit) và khi lưu trữ (At-Rest).**
4. **Vệ sinh bí mật và khóa truy cập trên kho mã nguồn Git (Secrets Hygiene).**
5. **Khử định danh nhật ký và giới hạn hạn mức truy vấn Athena.**

---

## 2. Kết quả Rà soát Theo 5 Trụ cột An toàn

### 2.1. Trụ cột 1: Bảo vệ Lưu trữ S3 Data Lake (S3 Block Public Access 100%)
- **Cấu hình S3 Block Public Access:** Đã bật tuyệt đối cả 4 cờ kiểm soát trên Data Lake Bucket:
  ```json
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
  }
  ```
- **Quyền sở hữu đối tượng:** Áp dụng `BucketOwnerEnforced`, vô hiệu hóa hoàn toàn ACLs cũ, bảo đảm toàn bộ đối tượng tải lên thuộc quyền sở hữu duy nhất của tài khoản AWS quản lý.
- **Tính bất biến & phục hồi:** Kích hoạt `VersioningConfiguration: Status=Enabled` và thiết lập `DeletionPolicy: Retain` trong CloudFormation để bảo vệ toàn bộ dữ liệu lịch sử không bị xóa ngoài ý muốn.

### 2.2. Trụ cột 2: Phân tích Quyền hạn IAM LabRole & Giải pháp Least-Privilege
- **Thực trạng trong AWS Academy Learner Lab:**
  - Môi trường Learner Lab không cho phép sinh viên tự tạo hoặc chỉnh sửa IAM Role/Policy nhằm đảm bảo an toàn sandbox học tập.
  - Mọi Lambda function buộc phải dùng role có sẵn `arn:aws:iam::<account_id>:role/LabRole`.
  - Phân tích tĩnh cho thấy `LabRole` chứa các quyền quản trị rộng (`AdministratorAccess`/`PowerUserAccess`) để hỗ trợ nhiều bài thực hành khác nhau, không đáp ứng nguyên tắc Quyền tối thiểu (Least Privilege) nếu đưa vào môi trường sản xuất thực tế.
- **Giải pháp Quyền tối thiểu Chuẩn Production (`collector-policy.example.json`):**
  Chúng em đã thiết kế một IAM Policy chuyên biệt, chỉ cấp đúng 5 quyền thiết yếu và thu hẹp tài nguyên (Resource ARN) cụ thể:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "WriteRawOnly",
        "Effect": "Allow",
        "Action": ["s3:PutObject"],
        "Resource": "arn:aws:s3:::weather-airquality-datalake-<account>-<env>/raw/*"
      },
      {
        "Sid": "ReadProjectConfig",
        "Effect": "Allow",
        "Action": ["secretsmanager:GetSecretValue"],
        "Resource": "arn:aws:secretsmanager:us-east-1:<account>:secret:weather-aqi-config-*"
      },
      {
        "Sid": "PublishProjectAlert",
        "Effect": "Allow",
        "Action": ["sns:Publish"],
        "Resource": "arn:aws:sns:us-east-1:<account>:weather-aqi-alerts-*"
      },
      {
        "Sid": "WriteExistingCollectorLogs",
        "Effect": "Allow",
        "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
        "Resource": "arn:aws:logs:us-east-1:<account>:log-group:/aws/lambda/WeatherCollectorLambda-*:*"
      }
    ]
  }
  ```
  *Chính sách này ngăn chặn hoàn toàn việc Lambda đọc trộm bucket khác, sửa xóa dữ liệu phân vùng cũ, hoặc phát tán tin nhắn ngoài phạm vi đồ án.*

### 2.3. Trụ cột 3: Mã hóa Dữ liệu (Encryption In-Transit & At-Rest)
- **Mã hóa khi truyền tải (In-Transit):**
  - Áp dụng S3 Bucket Policy từ chối mọi yêu cầu không sử dụng giao thức bảo mật HTTPS/TLS:
    ```yaml
    Statement:
      - Sid: DenyInsecureTransport
        Effect: Deny
        Principal: '*'
        Action: 's3:*'
        Resource:
          - !GetAtt DataBucket.Arn
          - !Sub '${DataBucket.Arn}/*'
        Condition:
          Bool:
            aws:SecureTransport: 'false'
    ```
  - Mọi giao tiếp giữa Lambda, Open-Meteo API, AWS Secrets Manager và S3 đều bắt buộc thông qua TLS 1.2 / TLS 1.3.
- **Mã hóa khi lưu trữ (At-Rest):**
  - S3 Data Lake cấu hình `ServerSideEncryptionByDefault` với thuật toán `AES256` (SSE-S3).
  - Athena Query Workgroup cấu hình `EncryptionOption: SSE_S3` cho toàn bộ kết quả truy vấn xuất ra thư mục `query-results/`.

### 2.4. Trụ cột 4: Vệ sinh Khóa Bí mật trên Kho Mã nguồn (Secrets Hygiene)
- **Kiểm thử tự động:** Được kiểm chứng tự động 100% qua test case `test_security_cleanliness_no_plaintext_credentials` trong [`tests/test_e2e_acceptance.py`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tests/test_e2e_acceptance.py).
- **Nguyên tắc triển khai:**
  - 0 khóa bí mật AWS (Access Key ID, Secret Access Key, Session Token) được lưu trữ trong Git.
  - Tọa độ 3 đô thị và ngưỡng cảnh báo AQI được lưu trong **AWS Secrets Manager**, Lambda đọc tự động qua SDK có ký xác thực AWS Signature V4.
  - File `.gitignore` loại trừ triệt để thư mục credentials, output tạm thời, và state file phục hồi phiên lab (`output/week4_session_control/`).

### 2.5. Trụ cột 5: Khử định danh Nhật ký & Giới hạn Hạn mức (Defense-in-Depth)
- **Khử định danh nhật ký (Log Sanitization):** CloudWatch Logs chỉ ghi nhận mã băm `request_hash` (20 ký tự đầu SHA-256) và các thông số đo đạc môi trường, không ghi log thông tin định danh cá nhân (PII), email người nhận, hoặc nội dung token phiên.
- **Rào chắn Chi phí Truy vấn Athena (Guardrail):** WorkGroup Athena cấu hình `BytesScannedCutoffPerQuery: 10485760` (giới hạn tối đa 10 MB dữ liệu quét cho một câu lệnh SELECT). Nếu một truy vấn viết sai cú pháp hoặc thiếu mệnh đề `WHERE` phân vùng, Athena sẽ tự động hủy truy vấn ngay lập tức, ngăn ngừa hoàn toàn nguy cơ quét cạn dung lượng Data Lake.

---

## 3. Ma trận Đánh giá An toàn Tổng hợp

Trích xuất từ ma trận kiểm toán an toàn [`tuan_4/results/security/security_controls_audit.csv`](../results/security/security_controls_audit.csv):

| Mã kiểm soát | Lĩnh vực | Tên kiểm soát | Yêu cầu kỹ thuật | Trạng thái | Đánh giá | Minh chứng xác thực |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **SEC-01** | Lưu trữ | S3 Block Public Access 100% | Bật đủ 4 cờ: Block/Ignore Public ACLs & Policy | Hoàn tất | **PASS** | `tuan_4/iac/cloudformation_stack.yaml` |
| **SEC-02** | Truyền tải | Enforce HTTPS/TLS trên S3 | Bucket Policy Deny `aws:SecureTransport = false` | Hoàn tất | **PASS** | `tuan_4/tests/test_cloudformation.py` |
| **SEC-03** | Lưu trữ | Mã hóa At-Rest S3 | Thuật toán SSE-S3 AES-256 | Hoàn tất | **PASS** | `tuan_4/iac/cloudformation_stack.yaml` |
| **SEC-04** | Độ bền | S3 Object Versioning | Versioning Status = Enabled | Hoàn tất | **PASS** | `tuan_4/tests/test_cloudformation.py` |
| **SEC-05** | Bí mật | Zero Plaintext Credentials in Git | Quét sạch mã nguồn không lộ Access Key | Hoàn tất | **PASS** | `tests/test_e2e_acceptance.py` |
| **SEC-06** | Cấu hình | Secrets Manager Integration | Lưu trữ tọa độ và ngưỡng AQI trên Secrets Manager | Hoàn tất | **PASS** | `tuan_2/lambda/lambda_function.py` |
| **SEC-07** | Định danh | IAM LabRole Least-Privilege Review | Lập chính sách thu hẹp 5 actions cho production | Hoàn tất | **PASS** | `tuan_4/infrastructure/collector-policy.example.json` |
| **SEC-08** | Tính toán | Lambda Resource Capping | Python 3.12, 256MB RAM, 60s Timeout | Hoàn tất | **PASS** | `tuan_4/tests/test_cloudformation.py` |
| **SEC-09** | Kích hoạt | EventBridge Invoke Authorization | Principal `events.amazonaws.com` bound to Rule ARN | Hoàn tất | **PASS** | `tuan_4/tests/test_cloudformation.py` |
| **SEC-10** | Rào chắn | Athena Query Bytes Cutoff | Giới hạn 10 MB quét tối đa mỗi query | Hoàn tất | **PASS** | `tuan_4/tests/test_cloudformation.py` |
| **SEC-11** | Giám sát | CloudWatch Log Retention & Masking | Giới hạn lưu 14 ngày; khử định danh RequestId | Hoàn tất | **PASS** | `tuan_4/scripts/verify_environment.py` |

---

## 4. Kết luận Đánh giá

Kiến trúc giải pháp tuân thủ xuất sắc các tiêu chuẩn bảo mật đám mây của AWS. Mặc dù chịu ràng buộc bởi chính sách dùng chung `LabRole` của môi trường đào tạo AWS Academy, nhóm sinh viên đã chủ động nhận diện rủi ro, cô lập tài nguyên qua CloudFormation, thực hiện mã hóa 100%, thiết kế chính sách quyền tối thiểu chuẩn mực cho môi trường sản xuất, và cài đặt các rào chắn kỹ thuật bảo vệ hệ thống tuyệt đối an toàn.
