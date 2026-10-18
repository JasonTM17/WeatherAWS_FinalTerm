# Snapshot và phân tích cập nhật ngày 18/10/2026

Đọc S3/Lambda bằng SDK sau khi cập nhật phiên Lab; không gọi Lambda thủ công, không thay mã/lịch/ngưỡng hoặc kênh email. Đây là snapshot 246/285 dùng cho thống kê và biểu đồ; [bản xuất sau lúc 17:02](../raw_export_2026_10_18/README.md) giữ riêng 246/288 dòng cùng JSON gốc.

| Chỉ tiêu | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Số raw | 246 | 285 |
| Nhóm đô thị–giờ | 234 | 228 |
| Timestamp cuối UTC | 2026-10-18 08:15:46 | 2026-10-18 08:51:05 |
| Mã khớp gói đã kiểm chứng | Có | Có |
| Số nhóm kiểm tra chất lượng phát hiện lỗi | 0/7 | 0/7 |

## Nguồn và cách tổng hợp

- [Raw sinh viên Tiến Sơn](snapshot/default/raw_all.csv) · [Snapshot, hash và thời điểm đọc](snapshot/default/snapshot.json).
- [Raw sinh viên Ngọc Quyên](snapshot/quyen/raw_all.csv) · [Snapshot, hash và thời điểm đọc](snapshot/quyen/snapshot.json).
- [96 dòng thống kê](analysis/descriptive.csv): raw và trung bình từng đô thị–giờ được tổng hợp riêng; độ lệch chuẩn mẫu, phân vị tuyến tính.
- [120 dòng tương quan](analysis/correlations.csv): Pearson và Spearman, xử lý đồng hạng; không kết luận nhân quả.
- [24 bộ sai số của bốn phương pháp](analysis/ma_comparison_metrics.csv) · [576 dòng giữ lại](analysis/ma_comparison_predictions.csv). MA 3 giờ là phân tích bổ sung, không thay mã dự báo đang chạy.
- [Dữ liệu mô hình tải về sau](analysis/later_model/history.csv) · [12 dòng đối chiếu với bản đã phát hành](analysis/later_model/comparison.csv) · [Nguồn/thời gian/cutoff](analysis/later_model/provenance.json). Chỉ hai giờ đích hoàn tất, chưa đủ 24 giờ; không phải dữ liệu trạm.
- [Mã tái lập](../../scripts/reconcile_analysis.py) · [Nguồn các đầu vào và hash](analysis/provenance.json) · [Manifest 26 tệp](manifest.json).

## Biểu đồ từ cùng CSV

![AQI theo giờ](analysis/city_hour_aqi.png)

Thanh sai số là độ lệch chuẩn mẫu, không phải khoảng tin cậy; n là số đô thị–giờ của từng sinh viên.

![Tương quan theo giờ](analysis/hourly_correlations.png)

![So sánh MA 3/24 giờ](analysis/holdout_ma_comparison.png)

## Giới hạn và tính toàn vẹn

Bảy nhóm kiểm tra chất lượng đã khai báo không phát hiện lỗi, không có nghĩa dữ liệu mô hình đúng như số đo thực địa. Snapshot bảo vệ từng đối tượng bằng ETag, không phải giao dịch nguyên tử toàn bucket. Số đo Athena cũ vẫn dùng bộ raw ban đầu 237/273; không gán byte/thời gian của truy vấn cho từng đô thị. Bản dự báo đã phát hành giữ nguyên và chỉ được đối chiếu với giá trị mô hình tải về sau ở những giờ đã hoàn tất.

[Báo cáo kỹ thuật](../../docs/FINAL_REPORT.md) · [Trang Tuần 3](../../README.md) · [Worklog](../../docs/WORKLOG.md)
