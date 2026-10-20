# Rà soát bảo mật hệ thống

**Ngày cập nhật: 20/10/2026.** Phạm vi gồm cấu hình hệ thống hiện hữu được lưu ngày 19/10 và hai stack CloudFormation mới được tạo, đọc lại và chạy ngày 20/10. Đây là bộ kiểm tra trong phạm vi đồ án, không phải chứng nhận tuân thủ toàn bộ một tiêu chuẩn bảo mật.

## 1. Nguồn và cách đọc

- [Cấu hình hiện hữu ngày 19/10](../results/verification_2026_10_19/environment/).
- [Cấu hình/runtime stack mới của sinh viên Tiến Sơn](../results/advanced_live_2026_10_20/stacks/default/).
- [Cấu hình/runtime stack mới của sinh viên Ngọc Quyên](../results/advanced_live_2026_10_20/stacks/quyen/).
- [Template chính](../infrastructure/weather-stack.json) và [policy collector tham khảo](../infrastructure/collector-policy.example.json).

Tách cấu hình quan sát, kiểm tra tĩnh template và thiết kế quyền đề xuất. CSV [security_controls_audit.csv](../results/security/security_controls_audit.csv) là bảng dẫn xuất từ snapshot ngày 19/10; giữ nguyên ngày và phạm vi đó. Kết quả của stack mới nằm trong configuration.json/runtime_controls.json ngày 20/10.

## 2. Ma trận kiểm tra

| Mã | Kiểm tra | Kết quả và phạm vi |
| --- | --- | --- |
| S01 | Bốn S3 Block Public Access | Cả hai bucket hiện hữu ngày 19/10 và hai bucket mới ngày 20/10 đều bật đủ bốn cờ |
| S02 | Public ACL | Không có quyền public qua ACL trong các lần đọc đã lưu |
| S03 | Public policy | Không ghi nhận policy public trong các lần đọc đã lưu |
| S04 | Mã hóa mặc định | AES256 trên các bucket được kiểm tra |
| S05 | Versioning | Bucket hiện hữu ngày 19/10 ghi NOT_ENABLED; hai bucket mới ngày 20/10 ghi Enabled |
| S06 | HTTPS-only | Policy của từng bucket mới được đọc lại, có Deny khi aws:SecureTransport=false cho bucket và object |
| S07 | Ownership | Hai bucket mới đọc lại BucketOwnerEnforced |
| S08 | Phạm vi IAM | Giữ LabRole học phần; quyền đọc policy bị từ chối trong snapshot ngày 19/10. Không suy ra effective permissions đã tối thiểu |
| S09 | EventBridge → Lambda | Permission của hai collector mới ràng buộc ARN rule và SourceAccount; rule mới đúng một target, giữ DISABLED |
| S10 | CloudWatch → SNS | Template giới hạn Publish bằng ARN alarm và tài khoản; đã kiểm tra cấu trúc. Không coi đây là thử nghiệm xâm nhập từ mọi nguồn khác |
| S11 | Bí mật và minh chứng | Email là tham số NoEcho, không công bố SecretString, credentials, URL có chữ ký hoặc state phục hồi riêng; kiểm tra các tệp được công bố trước phát hành |

## 3. Giải thích cấu hình

**BPA, ACL và policy.** Bốn BPA cùng trạng thái không public bảo vệ bucket khỏi cách cấp truy cập công khai thường gặp. Kiểm tra này không thay việc đánh giá tất cả principal IAM có thể truy cập dữ liệu.

**Mã hóa, HTTPS và ownership.** AES256 bảo vệ dữ liệu lưu trữ; policy HTTPS-only kiểm soát truyền tải; BucketOwnerEnforced vô hiệu hóa ACL ở các bucket mới. Kết quả dựa trên API đọc lại đúng bucket, không chỉ dựa vào template.

**Versioning và Retain.** Versioning giữ phiên bản object khi có ghi đè; đây không phải Object Lock/WORM hoặc bản sao lưu độc lập. Retain áp dụng cho tài nguyên được chỉ định trong template để giữ dữ liệu khi xóa/thay stack. Phiên bản cũ và tài nguyên giữ lại vẫn cần được theo dõi chi phí.

**LabRole.** API từ chối đọc policy không đủ để kết luận nguyên nhân cụ thể do SCP, permissions boundary hay policy nào. Giữ role có sẵn. Mẫu collector giới hạn PutObject raw/*, đọc một Secret, Publish một topic và ghi một log group; gắn thêm policy hẹp không loại bỏ quyền rộng từ policy khác.

**Artifact và ranh giới triển khai.** Công cụ kiểm tra tên tài nguyên trước tạo stack; không coi AccessDenied là tài nguyên chưa tồn tại. ZIP theo hash, version cụ thể và tải lại đối chiếu. Function, bucket, Secret, database/workgroup phải thuộc Outputs đúng môi trường; không dùng kết quả của hệ thống cũ thay cho stack mới.

**Log và minh chứng.** Tệp công khai chọn trường kỹ thuật cần thiết, dùng hash request và không giữ phản hồi lỗi chứa thông tin riêng. Rà soát tệp không có nghĩa đã chứng minh mọi log tương lai không thể chứa dữ liệu nhạy cảm.

## 4. Tái lập kiểm tra

```powershell
python tuan_4/scripts/security_report.py --check
python tuan_4/scripts/verify_results.py
python -m unittest discover -s tuan_4/tests -v
```

Lệnh đầu kiểm tra CSV dẫn xuất ngày 19/10; lệnh thứ hai kiểm tra manifest và cấu hình đã lưu của cả bộ cũ và mới. Đây là xác minh offline. [verify_stack.py](../scripts/verify_stack.py) dùng cho đọc lại dịch vụ trong phiên Lab hợp lệ; cờ --invoke thực hiện một lượt thu thập có ghi S3.

[Báo cáo Tuần 4](FINAL_REPORT.md) · [Hướng dẫn hạ tầng](INFRASTRUCTURE.md) · [Phạm vi quyền runtime](SECURITY_REVIEW.md).
