# Đề xuất cải tiến kiến trúc và tối ưu hóa hệ thống AWS

**Học phần:** Điện toán đám mây  
**Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng  
**Sinh viên thực hiện:** Nguyễn Tiến Sơn (24110054) · Trần Thị Ngọc Quyên (24110051)  
**Ngày lập đề xuất:** 03/11/2026  

---

## 1. Đặt vấn đề và Mục tiêu cải tiến

Sau khi hoàn thành đợt kiểm chứng Tuần 4 và tiến hành rà soát thực tế qua AWS CLI và Cost Explorer API vào ngày **03/11/2026**, hệ thống đã ghi nhận các chỉ số vận hành và chi phí sau 1 tháng hoạt động:
- **Chi phí thực tế tích lũy (Actual Usage Cost):** 3,16 USD (Tài khoản Tiến Sơn: 2,46 USD; Tài khoản Ngọc Quyên: 0,70 USD).
- **Quy ước kế toán:** Toàn bộ số liệu là chi phí thực tế tiêu dùng (Actual Usage Cost, tuyệt đối không ghi số âm).
- **Nguyên nhân chính phát sinh chi phí thô:** Dịch vụ Amazon CloudWatch (2,02 USD, chiếm 63,8%) và AWS Secrets Manager (1,03 USD, chiếm 32,7%). Chi phí tính toán Lambda và truy vấn Athena chỉ chiếm dưới 1,0% tổng chi phí.

Mục tiêu của tài liệu này là xây dựng phương án cải tiến kiến trúc toàn diện theo tiêu chuẩn AWS Well-Architected Framework, tối ưu chi phí (FinOps), nâng cao độ tin cậy (Reliability), tối ưu hóa dữ liệu (Performance Efficiency) và hoàn thiện bảo mật đặc quyền tối thiểu (Security).

---

## 2. Tối ưu hóa chi phí (Cost Optimization & FinOps)

### 2.1. Chuyển dịch cấu hình từ AWS Secrets Manager sang AWS Systems Manager Parameter Store

#### Thực trạng
- AWS Secrets Manager áp dụng biểu phí **0,40 USD/secret/tháng** (tính theo tỷ lệ ngày lưu trữ) cộng với 0,05 USD cho mỗi 10.000 API call.
- Mỗi tài khoản đang lưu trữ đồng thời 2 secret (`weather/api_config` thủ công và `ApiConfig-...` do CloudFormation sinh ra), tạo chi phí cố định khoảng 0,80 USD/tháng cho mỗi tài khoản dù hệ thống không kích hoạt thu thập.
- Cấu hình hiện tại chỉ chứa URL Open-Meteo, tọa độ 3 thành phố và các ngưỡng AQI (không chứa API key bí mật trả phí).

#### Giải pháp
- Thay thế Secrets Manager bằng **AWS Systems Manager (SSM) Parameter Store** với loại tham số `String` hoặc `SecureString`.
- Trong hạn mức Standard tier, SSM Parameter Store **hoàn toàn miễn phí** lưu trữ và miễn phí các lượt truy vấn API chuẩn.

```
+-----------------------------------------------------------------------------------------+
| Mô hình cũ: Secrets Manager                                                              |
| Lambda ---> secretsmanager:GetSecretValue ---> Trả JSON cấu hình ($0,40/secret/tháng)   |
+-----------------------------------------------------------------------------------------+
| Mô hình đề xuất: SSM Parameter Store                                                    |
| Lambda ---> ssm:GetParameter(/weather/config) ---> Trả JSON cấu hình ($0,00/tháng)       |
+-----------------------------------------------------------------------------------------+
```

Đoạn mã truy xuất cấu hình trong Lambda:
```python
import boto3
import json

def get_pipeline_config(parameter_name: str) -> dict:
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return json.loads(response['Parameter']['Value'])
```

### 2.2. Thiết lập chính sách lưu trữ nhật ký CloudWatch Logs (Log Retention Policy)

#### Thực trạng
- Các nhóm nhật ký `/aws/lambda/WeatherCollectorLambda` và các hàm bổ trợ được tạo tự động với thời gian lưu trữ mặc định là `Never expire`.
- Dung lượng nhật ký tích lũy theo thời gian khiến chi phí lưu trữ CloudWatch Logs tăng dần đều (0,03 USD/GB/tháng tại us-east-1).

#### Giải pháp
- Áp dụng thời hạn lưu trữ tự động `RetentionInDays: 7` hoặc `14` cho toàn bộ các Log Group trong CloudFormation template:
```json
"CollectorLogs": {
  "Type": "AWS::Logs::LogGroup",
  "Properties": {
    "LogGroupName": { "Fn::Sub": "/aws/lambda/weather-collector" },
    "RetentionInDays": 14
  }
}
```

### 2.3. Hợp nhất cảnh báo CloudWatch Alarms và dọn dẹp tài nguyên thừa

#### Thực trạng
- Mỗi tài khoản tồn tại 2 CloudWatch Alarms: một cảnh báo từ đợt thực hành Tuần 1-2 (`WeatherCollector-Errors-Alarm`) và một cảnh báo từ stack Tuần 4 (`weather-w4-*-errors`).
- CloudWatch Alarm tiêu chuẩn có mức phí **0,10 USD/alarm/tháng**.

#### Giải pháp
- Thu hồi cảnh báo cũ không còn quản lý qua CloudFormation.
- Cấu hình Composite Alarm hoặc chỉ duy trì một cảnh báo lỗi duy nhất theo dõi chỉ số `Errors` và `Throttles` của Lambda.

### 2.4. Bảng phân tích hiệu quả kinh tế (Cost Benefit Analysis)

Bảng tính dự phóng chi phí cho 1 năm vận hành hệ thống:

| Hạng mục chi phí | Cấu hình hiện tại (Ước tính/tháng) | Cấu hình tối ưu (Ước tính/tháng) | Mức tiết kiệm |
| :--- | :---: | :---: | :---: |
| AWS Secrets Manager (4 secrets / 2 TK) | 1,60 USD | 0,00 USD (Chuyển sang SSM) | -100% |
| CloudWatch Alarms (4 alarms / 2 TK) | 0,40 USD | 0,20 USD (Giữ 2 alarms) | -50% |
| CloudWatch Logs Storage | 0,15 USD | 0,02 USD (Hạn lưu 14 ngày) | -86,7% |
| AWS Lambda (Tần suất 1 giờ/lượt) | 0,00 USD (Free Tier) | 0,00 USD (Free Tier) | 0% |
| Amazon S3 Storage & Athena SQL | 0,02 USD | 0,01 USD (Lifecycle S3) | -50% |
| **Tổng chi phí duy trì hàng tháng** | **2,17 USD** | **0,23 USD** | **-89,4%** |
| **Tổng chi phí 1 năm (12 tháng)** | **26,04 USD** | **2,76 USD** | **-23,28 USD** |

---

## 3. Nâng cao độ tin cậy và khả năng chịu lỗi (Reliability & Resilience)

### 3.1. Tích hợp Dead-Letter Queue (SQS DLQ) cho Lambda Collector

#### Thực trạng
- Khi EventBridge kích hoạt Lambda thu thập theo chu kỳ, nếu API Open-Meteo gặp sự cố gián đoạn hoặc timeout vượt quá 60 giây, EventBridge sẽ thử lại tối đa 2 lần rồi hủy bỏ sự kiện.
- Dữ liệu lượt thu thập đó bị mất và không thể đối chiếu nguyên nhân lỗi nếu không đọc nhật ký thô.

#### Giải pháp
- Bổ sung Amazon SQS Dead-Letter Queue (`AWS::SQS::Queue`) làm đích đến cho các lượt thực thi thất bại của Lambda.
- Cấu hình `DeadLetterConfig` trên hàm Lambda:
```json
"CollectorDeadLetterQueue": {
  "Type": "AWS::SQS::Queue",
  "Properties": {
    "QueueName": { "Fn::Sub": "weather-collector-dlq-${AWS::AccountId}" },
    "MessageRetentionPeriod": 1209600
  }
},
"Collector": {
  "Type": "AWS::Lambda::Function",
  "Properties": {
    "DeadLetterConfig": {
      "TargetArn": { "Fn::GetAtt": ["CollectorDeadLetterQueue", "Arn"] }
    }
  }
}
```
- Khi phát sinh lỗi, thông tin ngữ cảnh lỗi được lưu lại an toàn trên SQS, cho phép script khôi phục (`reconcile_ops.py`) đọc và backfill dữ liệu tự động.

### 3.2. Tinh chỉnh tài nguyên bộ nhớ Lambda (Lambda Power Tuning)

#### Thực trạng
- Hàm Lambda `WeatherCollectorLambda` hiện được cấp phát `MemorySize: 256 MB`.
- Nhật ký vận hành thực tế cho thấy hàm tiêu thụ trung bình từ **68 MB đến 84 MB RAM**, thời gian chạy trung bình 1.800 ms. Phần lớn thời gian là chờ phản hồi I/O qua mạng từ API bên ngoài.

#### Giải pháp
- Điều chỉnh `MemorySize` về mức **128 MB**.
- Với tác vụ thuần I/O, thời gian thực thi không thay đổi đáng kể, nhưng chỉ số GB-giây (Gigabyte-seconds) tính phí sẽ giảm **50%**, tối ưu ngân sách khi chạy ở quy mô lớn.

---

## 4. Quản lý vòng đời dữ liệu Data Lake (S3 & Athena Optimization)

### 4.1. Thiết lập S3 Lifecycle Rules cho kết quả truy vấn Athena

#### Thực trạng
- Mỗi câu lệnh truy vấn qua Amazon Athena sinh ra tệp kết quả `.csv` và tệp metadata `.csv.metadata` trong đường dẫn lưu trữ tạm của S3 bucket (`athena-query-results/`).
- Các tệp này không tự động xóa, làm tăng số lượng object và dung lượng lưu trữ tĩnh.

#### Giải pháp
- Thêm quy tắc vòng đời (`LifecycleConfiguration`) trên S3 Bucket để tự động xóa các đối tượng trong tiền tố `athena-query-results/` sau **7 ngày**:
```json
"LifecycleConfiguration": {
  "Rules": [
    {
      "Id": "CleanupAthenaStaging",
      "Prefix": "athena-query-results/",
      "Status": "Enabled",
      "ExpirationInDays": 7
    }
  ]
}
```

### 4.2. Duy trì định dạng nén Parquet và Partition Projection

- Tiếp tục duy trì chuẩn nén **Parquet với thuật toán Snappy** đã chứng minh hiệu quả ở Tuần 3: giảm từ **80,59% đến 96,50%** khối lượng dữ liệu quét so với định dạng NDJSON thô.
- Giữ nguyên cơ chế **Partition Projection** cho Glue Data Catalog để loại bỏ bước chạy `MSCK REPAIR TABLE` tốn thời gian và chi phí quét metadata.

---

## 5. Thiết kế bảo mật theo mô hình doanh nghiệp (Enterprise Security)

### 5.1. Mô hình phân quyền đặc quyền tối thiểu (IAM Least Privilege Production Model)

Trong môi trường học tập AWS Learner Lab, sinh viên sử dụng role chia sẻ `LabRole`. Trong môi trường thực tế (Production), vai trò thực thi của Lambda cần được thu hẹp nghiêm ngặt theo chính sách sau:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowLogging",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:*:log-group:/aws/lambda/weather-w4-*"
    },
    {
      "Sid": "AllowS3DataLakeWrite",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::weather-w4-*/*"
    },
    {
      "Sid": "AllowSSMParameterRead",
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter"
      ],
      "Resource": "arn:aws:ssm:us-east-1:*:parameter/weather/*"
    },
    {
      "Sid": "AllowSNSPublishAlerts",
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:us-east-1:*:weather-w4-*-alerts"
    },
    {
      "Sid": "AllowSQSDLQSend",
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage"
      ],
      "Resource": "arn:aws:sqs:us-east-1:*:weather-collector-dlq-*"
    }
  ]
}
```

### 5.2. Chính sách bảo vệ dữ liệu trên S3
- Duy trì 4 cờ khóa truy cập công khai (`BlockPublicAccessBlockConfiguration` = True).
- Thực thi chính sách bắt buộc mã hóa đường truyền HTTPS (`aws:SecureTransport` = False thì Deny).
- Mã hóa dữ liệu tĩnh qua chuẩn `AES256` hoặc `aws:kms`.

---

## 6. Ma trận đối chiếu Hiện trạng và Cấu hình Tối ưu

| Tiêu chí | Cấu hình Hiện tại (Tuần 4) | Cấu hình Đề xuất Tối ưu | Lợi ích đạt được |
| :--- | :--- | :--- | :--- |
| **Quản lý cấu hình/Secret** | AWS Secrets Manager (4 secrets) | AWS Systems Manager Parameter Store | Tiết kiệm 100% chi phí lưu trữ secret (~1,60 USD/tháng) |
| **Lưu trữ CloudWatch Log** | Không giới hạn thời gian (Never expire) | Tự động xoay vòng sau 14 ngày | Tránh phình dung lượng lưu trữ log không cần thiết |
| **Khả năng chịu lỗi Lambda** | Thử lại 2 lần rồi bỏ rơi sự kiện | Tích hợp Amazon SQS Dead-Letter Queue | Bảo toàn 100% bản tin lỗi để truy vết và tái xử lý |
| **Bộ nhớ cấp phát Lambda** | 256 MB RAM | 128 MB RAM | Giảm 50% chỉ số GB-giây tính toán của hàm thu thập |
| **Dọn dẹp kết quả Athena S3** | Lưu vĩnh viễn trên S3 staging | Tự động hủy sau 7 ngày qua S3 Lifecycle | Tối ưu dung lượng bucket và chi phí lưu trữ đối tượng |
| **Cảnh báo lỗi vận hành** | 2 Alarms độc lập / tài khoản | 1 Composite Alarm hoặc 1 Metric Alarm chuẩn hóa | Tiết kiệm 50% chi phí alarm tĩnh hàng tháng |
| **Mô hình bảo mật IAM** | Sử dụng LabRole (Toàn quyền) | Tách Custom Role đặc quyền tối thiểu | Đạt chuẩn an toàn thông tin doanh nghiệp (Principle of Least Privilege) |

---

## 7. Lộ trình triển khai (Implementation Roadmap)

1. **Giai đoạn 1 — Tối ưu chi phí ngay lập tức (Immediate FinOps Quick-wins):**
   - Áp dụng cấu hình `RetentionInDays: 14` cho log groups.
   - Xóa bỏ các cảnh báo và secret thủ công không còn liên kết với CloudFormation stack.
2. **Giai đoạn 2 — Nâng cấp hạ tầng dưới dạng mã (IaC Upgrade):**
   - Đóng gói template mẫu tối ưu hóa: [weather-stack-optimized.json](../tuan_4/infrastructure/weather-stack-optimized.json) bổ sung SQS DLQ, S3 Lifecycle và tham số SSM.
3. **Giai đoạn 3 — Hoàn thiện tài liệu nghiệm thu:**
   - Cập nhật số liệu kiểm toán chi phí vào `BAO_CAO.md`, `README.md` và `FINAL_PROJECT_REPORT.md`.
   - Bổ sung tài liệu đề xuất cải tiến này vào danh mục hồ sơ đồ án phục vụ bảo vệ trước Hội đồng chấm thi.
