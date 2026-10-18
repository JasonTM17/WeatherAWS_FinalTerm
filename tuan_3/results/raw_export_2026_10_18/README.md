# Dữ liệu raw sử dụng trong hồ sơ Tuần 3 — bản xuất ngày 18/10/2026

Đã trực tiếp tải dữ liệu từ Amazon S3 của cả hai sinh viên bằng SDK. Bộ hồ sơ có **534 bản ghi, đủ 23 trường**, được giữ ở cả định dạng JSON gốc theo dòng (NDJSON) và CSV. Đây là dữ liệu đầu vào dùng cho công việc tích hợp Tuần 3 đã thực hiện.

| Chỉ tiêu | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Số bản ghi raw | 246 | 288 |
| Tệp JSON gốc từ S3 | 36 | 47 |
| Nhóm đô thị–giờ | 234 | 231 |
| Timestamp cuối UTC | 2026-10-18 08:15:46 | 2026-10-18 09:51:05 |
| Bản ghi đã có được bảo toàn | 246 | 285 |
| Bản ghi bổ sung | 0 | 3 |
| Thời điểm hoàn tất bản xuất (UTC+7) | 18/10/2026 17:01:39 | 18/10/2026 17:02:04 |

## Mở dữ liệu đầy đủ

- **Sinh viên Tiến Sơn:** [CSV toàn bộ](snapshot/default/raw_all.csv) · [JSON nguyên bản](snapshot/default/objects/raw/) · [Danh mục object và SHA-256](snapshot/default/object_inventory.csv) · [Chất lượng](snapshot/default/quality.csv) · [Tổng hợp theo giờ](snapshot/default/hourly_city.csv) · [Thời điểm, lịch và hash Lambda](snapshot/default/snapshot.json).
- **Sinh viên Ngọc Quyên:** [CSV toàn bộ](snapshot/quyen/raw_all.csv) · [JSON nguyên bản](snapshot/quyen/objects/raw/) · [Danh mục object và SHA-256](snapshot/quyen/object_inventory.csv) · [Chất lượng](snapshot/quyen/quality.csv) · [Tổng hợp theo giờ](snapshot/quyen/hourly_city.csv) · [Thời điểm, lịch và hash Lambda](snapshot/quyen/snapshot.json).

## Một bản ghi mới nhất của mỗi đô thị

| Sinh viên | Đô thị | Timestamp UTC | AQI | PM2.5 (µg/m³) | Nhiệt độ (°C) | Độ ẩm (%) |
| --- | --- | --- | --- | --- | --- | --- |
| Sinh viên Tiến Sơn | TP. Hồ Chí Minh | 2026-10-18 08:15:45 | 65 | 11.7 | 28.0 | 83.0 |
| Sinh viên Tiến Sơn | Hà Nội | 2026-10-18 08:15:45 | 87 | 26.1 | 31.5 | 58.0 |
| Sinh viên Tiến Sơn | Đà Nẵng | 2026-10-18 08:15:46 | 51 | 8.2 | 28.5 | 80.0 |
| Sinh viên Ngọc Quyên | TP. Hồ Chí Minh | 2026-10-18 09:51:03 | 65 | 11.8 | 27.8 | 85.0 |
| Sinh viên Ngọc Quyên | Hà Nội | 2026-10-18 09:51:04 | 95 | 27.4 | 30.4 | 64.0 |
| Sinh viên Ngọc Quyên | Đà Nẵng | 2026-10-18 09:51:05 | 50 | 7.0 | 28.0 | 82.0 |

Bảng trên trích nguyên giá trị từ CSV, không làm tròn hay hiệu chỉnh các chỉ số. CSV chứa tất cả bản ghi; JSON giữ nguyên byte từ S3. Các lượt cùng đô thị–giờ vẫn được giữ trong raw và chỉ tổng hợp ở `hourly_city.csv`.

## Phương pháp đối chiếu và phạm vi thời gian

- Bảy nhóm kiểm tra lược đồ, khóa, số, múi giờ, phân vùng và thời gian thu thập không phát hiện lỗi trong hai bộ xuất này.
- Đối chiếu mỗi JSON với hash/kích thước/số bản ghi trong inventory và đối chiếu toàn bộ trường sau chuyển sang CSV. Cả 531 bản ghi ở snapshot trước được bảo toàn; ba bản ghi mới thuộc sinh viên Ngọc Quyên. Không cộng các snapshot chồng nhau thành quan sát mới.
- Cả hai Lambda đang Active/Successful và hash gói khớp bản CD đã kiểm chứng. Lần xuất này chỉ đọc AWS, không gọi Lambda hoặc thay lịch/ngưỡng để tạo dữ liệu.
- Các bản ghi giữ đúng timestamp UTC/UTC+7 gốc. Ngày 18/10 là mốc hoàn thành công việc tích hợp; khoảng lịch báo cáo 19–25/10 được theo dõi theo timestamp riêng. Bộ raw dùng cho hồ sơ Tuần 3 không được diễn giải thành độ phủ liên tục cả bảy ngày.
- Các bảng thống kê và biểu đồ đã công bố dùng snapshot 246/285 dòng; 18 lượt Athena dùng snapshot 237/273 dòng. Bản xuất 246/288 dòng này là mốc riêng và không thay đầu vào của các kết quả đã đóng băng.
- S3 được liệt kê một lượt và từng object được GET với ETag tương ứng. Đây không phải giao dịch nguyên tử trên toàn bucket.

[Thông tin bản xuất](export.json) · [Manifest](manifest.json) · [Chương trình xuất](../../scripts/snapshot.py) · [Kiểm tra tái lập ngoại tuyến](../../scripts/verify_results.py) · [Báo cáo Tuần 3](../../docs/FINAL_REPORT.md).
