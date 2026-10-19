# Rà soát cấu hình bảo mật

**Mốc đối chiếu:** 19/10/2026. Phân biệt cấu hình đọc từ môi trường hiện hữu và thiết kế của stack mới.

| Kiểm tra hiện hữu | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Đủ bốn S3 Block Public Access | Đạt | Đạt |
| Public ACL / public policy | Không / Không | Không / Không |
| Mã hóa mặc định | AES256 | AES256 |
| Versioning | Chưa bật | Chưa bật |
| Quyền đọc IAM policy LabRole | API bị từ chối | API bị từ chối |

Bảng được lập từ [storage và role của sinh viên Tiến Sơn](../results/verification_2026_10_19/environment/default/) và [sinh viên Ngọc Quyên](../results/verification_2026_10_19/environment/quyen/). Không kết luận effective permissions của LabRole đã tối thiểu khi chưa đọc được policy.

## Thiết kế stack mới

[Template chính](../infrastructure/weather-stack.json) bật BPA, AES256, versioning và BucketOwnerEnforced; giữ bucket, Secret và log theo Retain. BucketPolicy từ chối yêu cầu không dùng HTTPS; điều kiện `aws:SecureTransport` không khẳng định riêng phiên bản TLS 1.3. Alarm được cấp quyền Publish tới đúng topic, ràng buộc đúng ARN alarm và tài khoản. Quyền gọi Lambda ràng buộc rule và SourceAccount.

[Policy tham khảo cho collector](../infrastructure/collector-policy.example.json) giới hạn ghi `raw/*`, đọc một Secret, Publish một topic và ghi một log group có sẵn. Template không tạo hoặc sửa IAM role của Learner Lab. Thiết kế này không được ghi như cấu hình đã triển khai trên bucket hiện hữu.

## Tái lập ma trận

```powershell
python tuan_4/scripts/security_report.py --check
python tuan_4/scripts/security_report.py --output output/week4-security-moi
```

[Ma trận](../results/security/security_controls_audit.csv) có cột scope/evidence và giữ trạng thái `NOT_ENABLED`, `BLOCKED_CAPABILITY`, `DECLARED` riêng với PASS. Không gán đồng loạt mọi tiêu chí là đã đạt trên dịch vụ.

[Phương pháp đánh giá quyền](SECURITY_REVIEW.md) · [Hướng dẫn hạ tầng](INFRASTRUCTURE.md) · [Báo cáo chính](FINAL_REPORT.md)
