# Dữ liệu ngày 19/10/2026 và bản xuất S3 cập nhật

## Nguồn và thời điểm

Đã dùng phiên AWS của hai sinh viên để triển khai bản sửa giới hạn giờ backfill, gọi Lambda ở chế độ lấy lịch sử và đọc lại các object S3. Mỗi lượt backfill thu **42 bản ghi: 14 giờ × 3 đô thị**, không gửi SNS cho dữ liệu lịch sử. Đây là chuỗi mô hình được thu bổ sung lúc 14:22 ngày 19/10, không phải minh chứng các lượt tự động đã chạy trong 14 giờ trước đó. [Source đã triển khai](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650) · [CI đã đạt của source](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39215400909).

Ngày báo cáo dùng UTC+7: từ 19/10 00:00 đến trước 20/10 00:00, tương ứng `[18/10 17:00, 19/10 17:00)` UTC. Bản xuất được chốt giữa ngày, không đại diện đủ 24 giờ ngày 19/10.

| Nội dung | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | ---: | ---: |
| Hoàn tất xuất (UTC+7) | 19/10 14:22:37 | 19/10 14:23:28 |
| Raw tích lũy trong S3 | 302 | 339 |
| Object JSON nguyên bản | 43 | 52 |
| Raw mang ngày 19/10 theo UTC+7 | 45 | 42 |
| Bản ghi thuộc giờ đã hoàn tất trước 14:00 | 42 | 42 |
| Bản ghi trong giờ đang diễn ra, giữ riêng ở raw | 3 | 0 |
| Giờ dùng thống kê của mỗi đô thị | 14 | 14 |
| Bản ghi của mốc 18/10 được bảo toàn | 246 | 288 |

Tổng bản xuất: **641 bản ghi, 95 JSON gốc**. Riêng ngày 19/10: **87 bản ghi**, gồm 84 bản ghi của hai lượt backfill và ba bản ghi khác trong giờ đang diễn ra của sinh viên Tiến Sơn. Thống kê và hình dưới dùng cùng khung **00:00–13:00 UTC+7**, không đưa giờ 14 chưa kết thúc vào so sánh. Raw vẫn giữ đủ 23 trường và toàn bộ bản ghi, không cân số dòng bằng cách xóa hay thêm dữ liệu.

## Tệp để đối chiếu

| Hồ sơ | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Raw riêng ngày 19/10 | [45 dòng](daily/default/raw_today.csv) | [42 dòng](daily/quyen/raw_today.csv) |
| Raw tích lũy | [302 dòng](snapshot/default/raw_all.csv) | [339 dòng](snapshot/quyen/raw_all.csv) |
| JSON gốc S3 | [43 object](snapshot/default/objects/raw/) | [52 object](snapshot/quyen/objects/raw/) |
| Theo đô thị–giờ đã hoàn tất | [42 nhóm](daily/default/hourly_city.csv) | [42 nhóm](daily/quyen/hourly_city.csv) |
| Thống kê đầy đủ | [48 dòng](daily/default/descriptive.csv) | [48 dòng](daily/quyen/descriptive.csv) |
| Nguồn của từng record_id | [Bản đồ nguồn](daily/default/record_sources.csv) | [Bản đồ nguồn](daily/quyen/record_sources.csv) |
| Kết quả Lambda và object đã ghi | [Lượt backfill](collection/default.json) | [Lượt backfill](collection/quyen.json) |
| Hash gói và đọc lại sau triển khai | [Tiến Sơn](release/tien-son.json) | [Ngọc Quyên](release/ngoc-quyen.json) |

[Tổng hợp và thời điểm từng bộ](summary.json) · [Manifest 123 tệp](manifest.json). Mọi object được đọc có điều kiện ETag và lưu đúng byte gốc. Snapshot không phải giao dịch nguyên tử trên toàn bucket. Các tệp không chứa khóa phiên, nội dung Secret hay gói sao lưu triển khai riêng tư.

**Trích raw cùng giờ 13:00 ngày 19/10 (UTC+7):**

| Sinh viên | Đô thị | Timestamp Việt Nam | US AQI | PM2.5 (µg/m³) | Nhiệt độ (°C) | Độ ẩm (%) |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | TP. Hồ Chí Minh | 2026-10-19 13:00:00 | 55 | 11,3 | 27,2 | 83,0 |
| Sinh viên Tiến Sơn | Hà Nội | 2026-10-19 13:00:00 | 96 | 23,5 | 31,7 | 61,0 |
| Sinh viên Tiến Sơn | Đà Nẵng | 2026-10-19 13:00:00 | 53 | 11,4 | 29,5 | 74,0 |
| Sinh viên Ngọc Quyên | TP. Hồ Chí Minh | 2026-10-19 13:00:00 | 55 | 11,3 | 27,2 | 83,0 |
| Sinh viên Ngọc Quyên | Hà Nội | 2026-10-19 13:00:00 | 96 | 23,5 | 31,7 | 61,0 |
| Sinh viên Ngọc Quyên | Đà Nẵng | 2026-10-19 13:00:00 | 53 | 11,4 | 29,5 | 74,0 |

Đây là một phần các trường raw để minh họa, không phải giá trị trung bình. CSV nguồn giữ đủ 23 trường, bao gồm `record_id`, `timestamp_utc` và `collected_at`; dấu thời gian của mô hình được giữ riêng với lúc Lambda thu bổ sung.

## Thống kê theo giờ đã hoàn tất

| Sinh viên | Đô thị | Giờ hoàn tất | AQI TB | PM2.5 TB (µg/m³) | Nhiệt độ TB (°C) | Độ ẩm TB (%) | Gió TB (km/h) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | TP. Hồ Chí Minh | 14 | 55,857 | 11,557 | 27,307 | 83,857 | 7,193 |
| Sinh viên Tiến Sơn | Hà Nội | 14 | 91,071 | 35,914 | 27,293 | 82,929 | 4,450 |
| Sinh viên Tiến Sơn | Đà Nẵng | 14 | 47,143 | 13,086 | 26,914 | 86,571 | 4,921 |
| Sinh viên Ngọc Quyên | TP. Hồ Chí Minh | 14 | 55,857 | 11,557 | 27,307 | 83,857 | 7,650 |
| Sinh viên Ngọc Quyên | Hà Nội | 14 | 91,071 | 35,914 | 27,293 | 82,929 | 4,171 |
| Sinh viên Ngọc Quyên | Đà Nẵng | 14 | 47,143 | 13,086 | 26,914 | 86,571 | 5,107 |

Độ lệch chuẩn mẫu, trung vị và các phân vị có trong CSV thống kê, tách phạm vi raw và đô thị–giờ. Hai môi trường dùng cùng tọa độ và nguồn Open-Meteo nên có thể cho cùng AQI/PM2.5 ở cùng giờ; không xem hai bộ là hai nguồn đo độc lập. Dữ liệu tải lại có thể được mô hình cập nhật hồi cứu.

![AQI và PM2.5 ngày 19/10](daily_aqi_pm25.png)

## Tái lập từ bản xuất đã lưu

```bash
python tuan_3/scripts/daily_snapshot.py --snapshot tuan_3/results/daily_update_2026_10_19/snapshot --collection tuan_3/results/daily_update_2026_10_19/collection --release tuan_3/results/daily_update_2026_10_19/release --date 2026-10-19 --output output/recompute-day19-new
python tuan_3/scripts/verify_results.py
```

Lệnh đầu chỉ đọc các tệp đã lưu và tạo đầu ra riêng. Không gọi AWS, triển khai lại hay gọi Lambda. Các kiểm tra đối chiếu JSON–CSV, ngày UTC+7, provenance từng bản ghi, phạm vi giờ hoàn tất, thống kê và hash gói. [Báo cáo](../../docs/FINAL_REPORT.md) · [Nhật ký](../../docs/WORKLOG.md).
