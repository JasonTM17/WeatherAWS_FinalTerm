# Đối chiếu bộ đếm CloudWatch theo từng khoảng thời gian

Đã đọc hai API CloudWatch trên **cùng cửa sổ 07:40–10:40 UTC ngày 18/10/2026**, chu kỳ 300 giây, statistic Sum, namespace AWS/Lambda và đúng FunctionName. Kiểm tra thêm dimension FunctionName + Resource và chu kỳ 60 giây cho kết quả tổng tương ứng. Đây là số liệu của cửa sổ đã lưu, không phải tỷ lệ hoạt động liên tục của cả tuần.

| Chỉ tiêu | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Tổng Invocations có điểm trả về | 2 | 3 |
| Tổng Errors có điểm trả về | 3 | 0 |
| Khoảng thời gian có đủ cặp hợp lệ | 2 | 3 |
| Errors trong các khoảng đủ cặp | 0 | 0 |
| Tỷ lệ trên các khoảng đủ cặp | 0% | 0% |
| Tỷ lệ từ toàn bộ các bộ đếm trong cửa sổ | Không tính: thiếu cặp | 0%, các điểm đã phát đủ cặp |
| Khoảng thiếu Invocations nhưng có Errors | 09:15 UTC: Errors = 3 | Không có trong các điểm đã trả về |
| Request có đủ START/END/REPORT trong log đã đọc | 2 | 3 |

Điểm Errors = 3 của sinh viên Tiến Sơn được giữ nguyên. Cả hai API và hai bộ dimension đều trả cùng điểm này; log không có lifecycle tương ứng ở 09:15 trong cửa sổ đã đọc. Bằng chứng xác định được khoảng thiếu cặp và loại trừ sai khác do xuất CSV, API hoặc cách chọn dimension/chu kỳ ở phép đối chiếu này. Nguyên nhân sâu hơn của điểm native thiếu cặp chưa được xác định; không đổi nó thành 0 hoặc coi 0% của các khoảng đủ cặp là tỷ lệ toàn cửa sổ.

## Mở bằng chứng

- **Sinh viên Tiến Sơn:** [điểm native](default/native_statistics.csv) · [API MetricData](default/native_data.csv) · [dimension Resource](default/resource_statistics.csv) · [chu kỳ 60 giây](default/minute_statistics.csv) · [ghép từng khoảng](default/period_reconciliation.csv) · [lifecycle đã loại thông tin riêng](default/log_lifecycle.csv) · [tổng hợp](default/summary.json).
- **Sinh viên Ngọc Quyên:** [điểm native](quyen/native_statistics.csv) · [API MetricData](quyen/native_data.csv) · [dimension Resource](quyen/resource_statistics.csv) · [chu kỳ 60 giây](quyen/minute_statistics.csv) · [ghép từng khoảng](quyen/period_reconciliation.csv) · [lifecycle đã loại thông tin riêng](quyen/log_lifecycle.csv) · [tổng hợp](quyen/summary.json).
- [Manifest dữ liệu đối chiếu](manifest.json) · [Dashboard cuối sau sửa biểu thức](../monitoring_dashboard_repair_2026_10_18/README.md).

START/END/REPORT được ghép theo request hash. Các dòng Result được đếm riêng vì nội dung log này không có request ID để ghép chắc chắn; không dùng số dòng log thay cho native Invocations. Không có dòng lỗi trong log đã đọc không đủ để phủ nhận điểm Errors native.

## Trạng thái Dashboard

Các tệp `dashboard.json` và PNG trong thư mục này ghi **lần cập nhật đầu**, còn dùng nhiều lớp IF. Sau rà soát metric math, biểu thức đó được thay bằng một IF phẳng; không dùng ảnh của lần đầu làm bằng chứng cho biểu thức cuối. [Cấu hình, phép thử chỉ đọc và ảnh AWS sau sửa](../monitoring_dashboard_repair_2026_10_18/README.md) được lưu riêng để giữ lịch sử đối chiếu.

[Báo cáo](../../docs/FINAL_REPORT.md#43-sửa-ghép-bộ-đếm-và-biểu-thức-dashboard) · [Mã nguồn](../../scripts/monitoring_followup.py).
