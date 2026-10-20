# Rà soát bảo mật phạm vi đồ án

## 1. Các điểm kiểm tra

| Thành phần | Cách kiểm tra | Tiêu chí |
| --- | --- | --- |
| Danh tính môi trường | STS và ARN Lambda, bucket trong biến môi trường | Hàm và bucket thuộc đúng môi trường đang kiểm chứng |
| Source | Tải gói Lambda qua URL tạm thời trong bộ nhớ, kiểm tra hash và module | Module trùng source đã chốt; không lưu URL có chữ ký |
| S3 | Bốn thiết lập Block Public Access, policy status, ACL, mã hóa và versioning | Không có public policy/public ACL; bật đủ BPA và mã hóa. Versioning được báo riêng |
| EventBridge → Lambda | Rule, danh sách target và resource policy | Một target đúng function; quyền gọi ràng buộc ARN của rule; không có hai lịch đang cùng chạy |
| LabRole | Trust policy, inline policy và managed policy hiện hành | Tin cậy dịch vụ Lambda; thống kê các Allow có wildcard để quản trị viên xem phạm vi |
| Artifact | ZIP xác định, SHA-256, key theo hash và VersionId | Truy được mã nguồn của gói; không dùng version `null` |
| Minh chứng công khai | Chọn trường trước khi xuất | Không có token, SecretString, email cá nhân hoặc URL tải gói có chữ ký; tên tài nguyên phục vụ đối chiếu được giữ theo phạm vi hồ sơ |

`verify_environment.py` chỉ đọc các cấu hình trên. Chương trình không sửa S3 BPA, Secret hoặc IAM policy. Native metric và log được tách khỏi xác nhận email; thiếu điểm metric không chuyển thành số 0.

## 2. Quyền tối thiểu cho mã thu thập

| Thao tác runtime | Phạm vi tài nguyên đề xuất | Lý do |
| --- | --- | --- |
| `s3:PutObject` | `raw/*` trong đúng bucket | Collector chỉ cần ghi dữ liệu; không cần xóa hoặc đọc toàn bộ bucket |
| `secretsmanager:GetSecretValue` | Một Secret cấu hình | Đọc tọa độ và ngưỡng; không cần quyền quản trị Secret |
| `sns:Publish` | Một topic cảnh báo | Gửi cảnh báo; không cần tạo/xóa subscription |
| `logs:CreateLogStream`, `logs:PutLogEvents` | Một log group đã có | Ghi log thực thi; CloudFormation tạo log group trước |

[Policy tham khảo](../infrastructure/collector-policy.example.json) là mẫu cho execution role riêng. Các placeholder phải được thay bằng tài nguyên của stack. Nếu chuyển sang khóa KMS do khách hàng quản lý, đánh giá thêm quyền KMS và key policy cho đúng luồng.

## 3. Đọc kết quả IAM đúng phạm vi

Kiểm tra tĩnh đếm Allow dùng `Resource: "*"`, action `*`/`service:*` hoặc `NotAction`/`NotResource`. Những statement đó cần xem xét scope. Kết quả không tự đánh giá toàn bộ Condition, permissions boundary hay SCP; không được dùng số đếm này để kết luận effective permissions đã tối thiểu.

LabRole thuộc môi trường học phần và có thể dùng chung cho nhiều hoạt động. Gắn thêm policy hẹp không loại bỏ quyền rộng từ policy khác. Repository cung cấp bằng chứng đọc và mẫu policy giới hạn cho collector; **không chỉnh role dùng chung**. Khi triển khai với role riêng ngoài Lab, quản trị viên có thể áp dụng quyền hẹp và kiểm tra lại các đường ghi S3/đọc Secret/Publish/log.

## 4. Bảo vệ khi trình bày

- Không mở trang AWS Details, tệp credentials hoặc nút lấy Secret value trong video.
- Chỉ mở tab ứng dụng cần demo. Dùng cửa sổ trình duyệt riêng; ẩn thông báo và che email/thông tin tài khoản trước khi nộp video.
- Trình bày ARN bằng tên tài nguyên trong báo cáo công khai; giá trị đầy đủ dùng riêng cho cấu hình trên máy.
- Giữ dữ liệu thô, hash và giá trị chi phí do AWS cung cấp; phân loại mức dự kiến riêng với số đo.

Nguồn: [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html), [Lambda execution role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html).

[Báo cáo kiểm chứng](VERIFICATION_REPORT.md) · [Hồ sơ Tuần 4](../README.md)
