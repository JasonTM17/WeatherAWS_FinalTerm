# Đối chiếu request, log, metric và S3

**Ngày kiểm chứng:** 19/10/2026. Hai môi trường của sinh viên Tiến Sơn và sinh viên Ngọc Quyên được kiểm tra độc lập.

## 1. Kết quả của hai lượt có kiểm soát

| Chỉ tiêu | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Request được đối chiếu | 1 | 1 |
| START/END/REPORT và Result | Đủ | Đủ |
| Bản ghi S3 | 3 | 3 |
| Đô thị | 3 | 3 |
| Native Invocations trong chu kỳ chứa lượt kiểm chứng | 1 | 1 |
| Native Errors trong cùng chu kỳ | 0 | 0 |
| SELECT theo record_id khớp raw | Đạt | Đạt |
| Publish được SNS chấp nhận | 1 | 1 |
| Người nhận xác nhận email mới | Có | Có |

[CSV đối chiếu](../results/monitoring/log_metric_s3_reconciliation.csv), [tóm tắt phạm vi](../results/monitoring/reconciliation_summary.json), [xác nhận email](../results/verification_2026_10_19/recipient_confirmation.json).

## 2. Cách đối chiếu

1. Xác minh hash của snapshot trước khi dùng dữ liệu.
2. Tìm request đã băm trong log lifecycle và Result; đối chiếu key/số dòng với JSON tải lại từ S3.
3. Ghép native Errors/Invocations theo cùng hàm, chu kỳ 300 giây và timestamp UTC.
4. Dùng record_id của đúng lượt chạy để SELECT Athena; đối chiếu đô thị, AQI và PM2.5 với raw.
5. Ghi riêng Publish và xác nhận email tới người nhận.

Metric Filters đếm dòng log theo mẫu; không mặc định bằng số lượt gọi. Đợt này không xuất số đếm Metric Filters cho hai lượt, nên ô đó giữ trống. Tỷ lệ 0% chỉ áp dụng cho hai chu kỳ được kiểm chứng, không suy rộng cho cả cửa sổ có chu kỳ thiếu cặp. Phép kiểm tra không quét toàn bộ bucket để kết luận không còn object mồ côi.

## 3. Tái lập bảng

```powershell
python tuan_4/scripts/reconcile_ops.py --check
python tuan_4/scripts/reconcile_ops.py --output output/week4-reconciliation-moi
```

[Chương trình](../scripts/reconcile_ops.py) lấy request và số liệu từ [snapshot trực tiếp](../results/verification_2026_10_19/README.md); không tạo lịch giờ hoặc S3 key minh họa để coi là lượt chạy thực tế.

[Báo cáo chính](FINAL_REPORT.md) · [Lời thoại demo](VIDEO_DEMO_SCRIPT.md)
