# CloudFormation — Stack ứng dụng thời tiết và chất lượng không khí

## Trạng thái triển khai ngày 20/10/2026

Hai stack `weather-w4-son` và `weather-w4-quyen` đã CREATE_COMPLETE. Mỗi Lambda mới thu ba đô thị, raw được tải lại và SELECT đối chiếu trong database/workgroup mới. Artifact đúng version/hash; hai lịch mới vẫn DISABLED. [Minh chứng triển khai thực tế](../results/advanced_live_2026_10_20/README.md) gồm Events, cấu hình, raw, truy vấn và metric.

Công cụ [deploy_stack.py](../scripts/deploy_stack.py) kiểm tra chín tên tài nguyên, không nhận AccessDenied là chưa tồn tại, không tự nhận quản lý stack đã có. Nhật ký riêng phải đặt dưới output/ bị ignore; công cụ không cập nhật lại stack đã tạo. [verify_stack.py](../scripts/verify_stack.py) đọc Outputs đúng môi trường; cờ --invoke thực hiện một invocation, lưu raw và SELECT. Không dùng các tên collector/database cũ để xác minh stack mới.

## 1. Thành phần và cách thiết kế

[weather-stack.json](../infrastructure/weather-stack.json) khai báo **17 tài nguyên** trong một template. Các tài nguyên mới có tên bắt đầu bằng `weather-w4-`; không nhập hoặc thay thế bucket, Lambda và lịch đang vận hành của Tuần 1–3.

| Thành phần | Cấu hình và lý do |
| --- | --- |
| S3 + BucketPolicy | Bốn thiết lập Block Public Access, BucketOwnerEnforced, AES256, versioning; từ chối kết nối không dùng TLS. Bucket được Retain khi xóa hoặc thay thế stack để bảo toàn raw |
| Secrets Manager | Tọa độ ba đô thị và ngưỡng AQI/PM2.5; Lambda đọc theo ARN được truyền vào môi trường. Secret được giữ lại khi xóa stack |
| SNS + đăng ký email có điều kiện | Một topic của stack; email là tham số NoEcho, phải xác nhận đăng ký trước khi nhận thư. Bỏ trống email thì không tạo subscription |
| Lambda + LogGroup | Cùng source `lambda_function.py`, Python 3.12, 256 MB, 60 giây; log group có trước Lambda và giữ log 14 ngày |
| EventBridge + Lambda Permission | Chu kỳ một giờ, ban đầu DISABLED; quyền gọi gắn đúng ARN rule và tài khoản. Chỉ bật sau bước kiểm chứng trực tiếp |
| Glue Database + RawTable | 20 cột nội dung và 3 cột phân vùng; Partition Projection xác định đường dẫn `raw/year=.../month=.../day=.../`. JSON hỏng không bị âm thầm bỏ qua |
| Athena WorkGroup | S3 đầu ra riêng, SSE_S3, giới hạn quét 10 MiB mỗi truy vấn; cấu hình workgroup được cưỡng chế |
| Metric Filters + Alarm + TopicPolicy + Dashboard | Hai Metric Filters đếm dòng Result/Error trong namespace riêng theo môi trường. Theo dõi Errors, Invocations và SNS; TopicPolicy chỉ cho CloudWatch Publish từ ARN alarm của stack và đúng tài khoản; alarm giữ trạng thái thiếu dữ liệu khi chưa có metric. Không coi thiếu điểm là số lỗi bằng 0 |

Các giá trị ngưỡng vẫn là `AQI >= 100 OR PM2.5 >= 35.5`. Kênh cảnh báo sử dụng email. Hệ thống không cần khóa API Open-Meteo trong template.

## 2. Chuẩn bị gói nguồn

```powershell
python tuan_4/scripts/prepare_stack.py --output output/week4-stack-moi
```

Đầu ra gồm `collector.zip`, bản sao template và `build.json` có SHA-256 của source, artifact và template. Nội dung ZIP là chính source đang dùng trong repository; cách đóng gói xác định được dùng lại từ Tuần 3.

Trên **S3 Console**:

1. Chọn bucket lưu artifact riêng tư ở `us-east-1`, mở **Properties → Bucket Versioning** và kiểm tra đã bật versioning.
2. Trong **Objects**, tải `collector.zip` lên key `artifacts/week4/<artifact_sha256>/collector.zip`; thay `<artifact_sha256>` bằng giá trị trong `build.json`.
3. Mở object, ghi lại **Version ID** và key. Dùng một version cụ thể; không dùng version `null`.

Bucket artifact là đầu vào triển khai. Bucket raw của ứng dụng được tạo trong stack. Không tải credentials hoặc bản sao gói khôi phục riêng lên repo.

## 3. Tạo stack trên Console

1. Chọn vùng **N. Virginia / us-east-1**.
2. Mở **CloudFormation → Stacks → Create stack → With new resources (standard)**.
3. Chọn **Upload a template file**, tải `weather-stack.json`, chọn **Next**.
4. Đặt tên stack `weather-w4-son` hoặc `weather-w4-quyen`.
5. Nhập tham số:

| Tham số | Cách điền |
| --- | --- |
| `EnvironmentName` | `son` hoặc `quyen`, khớp môi trường thực hiện |
| `LabRoleArn` | ARN của LabRole trong **chính tài khoản đang đăng nhập**; sao chép từ IAM/Lambda Permissions, không lấy ARN của môi trường còn lại |
| `ArtifactBucket`, `ArtifactKey` | Bucket/key ZIP vừa tải lên, cùng vùng với Lambda |
| `ArtifactVersion` | Version ID của chính ZIP đó |
| `AlertEmail` | Địa chỉ thật của người nhận hoặc để trống; không quay/đăng công khai giá trị riêng tư |

6. Giữ nguyên các tùy chọn khác phù hợp với Lab. Kiểm tra danh sách tài nguyên trước khi chọn **Submit/Create stack**. Template không tạo IAM role hoặc sửa LabRole.
7. Chờ trạng thái **CREATE_COMPLETE**; mở **Events** nếu có bước thất bại, không chạy tạo stack lặp lại khi chưa đọc nguyên nhân.
8. Mở **Outputs**, dùng đúng tên bucket, function, database, workgroup và dashboard được trả về. Stack mới dùng tên riêng, không dùng lại `WeatherCollectorLambda`.
9. Xác nhận email SNS nếu đã đăng ký. Chạy Lambda một lần với `{}`, kiểm tra đủ ba đô thị và raw, rồi dùng Athena workgroup mới để truy vấn. Projection tự suy ra phân vùng từ ngày.
10. Sau kiểm chứng, nếu cần thu thập tự động cho phiên Lab, mở rule `weather-w4-<môi trường>-hourly`, kiểm tra target là function của stack rồi **Enable**. Cuối phiên **Disable** trước khi End Lab.

CloudFormation template hợp lệ chưa chứng minh tài khoản có toàn bộ quyền tạo dịch vụ hoặc LabRole có quyền với các ARN mới. Kiểm chứng triển khai cần trạng thái stack, kết quả chạy và đọc lại cấu hình của **stack mới**. Trạng thái những bước này được ghi trong [báo cáo](VERIFICATION_REPORT.md).

## 4. Quản lý quyền và dữ liệu

[collector-policy.example.json](../infrastructure/collector-policy.example.json) mô tả các quyền runtime tối thiểu: ghi `raw/*`, đọc đúng Secret, Publish đúng topic và ghi đúng log group đã tạo sẵn. Thay các placeholder bằng ARN từ Outputs trước khi quản trị viên xem xét.

Không gắn policy tham khảo rồi kết luận LabRole đã đạt least privilege: các policy rộng đang gắn trên role vẫn có hiệu lực. Trong Learner Lab, giữ role do lớp cấp; ghi nhận phạm vi quyền qua [rà soát bảo mật](SECURITY_REVIEW.md). Khi triển khai ngoài Lab, dùng execution role riêng và policy được giới hạn cho stack.

Khi kết thúc thử nghiệm: xuất dữ liệu và checksum trước, dừng lịch, sau đó xem danh sách tài nguyên của **đúng stack mới**. Xóa stack sẽ giữ lại DataBucket, ApiConfig và CollectorLogs theo Retain; các tài nguyên này vẫn cần được quản lý lưu trữ/chi phí. Không xóa bucket raw hoặc log đang làm minh chứng cho báo cáo.

## 5. Tài liệu AWS đối chiếu

- [Lambda Function và gói triển khai trong CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-lambda-function.html).
- [Glue Table trong CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-glue-table.html).
- [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html).
- [Execution role và least privilege cho Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html).

[Hồ sơ Tuần 4](../README.md) · [Báo cáo kiểm chứng](FINAL_REPORT.md)

Tham khảo quyền gửi alarm: [CloudWatch alarm → SNS](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Notify_Users_Alarm_Changes.html).

[Minh chứng ValidateTemplate của bản 17 tài nguyên](../results/template_validation_2026_10_19/README.md).
