# Kiểm chứng AWS ngày 16 tháng 10 năm 2026

Đợt này dùng hai phiên AWS của sinh viên Tiến Sơn và sinh viên Ngọc Quyên tại `us-east-1` để đọc metadata và chạy lại SELECT. Thời điểm hoàn tất tải ghi trong [manifest.json](manifest.json) là `2026-10-16T05:17:07Z` (12:17 UTC+7). Bộ lọc Tuần 2 giữ từ 12/10 00:00 đến trước 19/10 00:00 UTC+7; dữ liệu thực tải được chỉ nằm trong hai ngày 13–14/10.

## CSV và phạm vi dữ liệu

| Hạng mục | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | ---: | ---: |
| CSV toàn bộ | [216 bản ghi](default/raw_all.csv) | [249 bản ghi](quyen/raw_all.csv) |
| CSV thuộc Tuần 2 | [39 lượt ghi](default/raw_week2.csv) | [75 lượt ghi](quyen/raw_week2.csv) |
| Mẫu mỗi đô thị | 13 | 25 |
| Nhóm đô thị–giờ trong raw | 39 | 36 |
| Phân vùng Glue đã đăng ký | 6 | 6 |
| SELECT thành công | 7/7 | 7/7 |

Bộ kiểm tra tính lại số dòng, trung bình AQI/PM2.5 và phân bố cấp từ raw, đối chiếu với kết quả SQL. Nó cũng xác nhận raw Tuần 2 là tập con đúng theo bộ lọc của raw toàn bộ, mã bản ghi không lặp trong từng bộ toàn bộ và hash từng CSV khớp metadata. [Chương trình đối chiếu](../../scripts/repository_audit.py).

### AQI và PM2.5 trong lần tải mới

| Đô thị | AQI TB sinh viên Tiến Sơn | AQI TB sinh viên Ngọc Quyên | PM2.5 TB sinh viên Tiến Sơn (µg/m³) | PM2.5 TB sinh viên Ngọc Quyên (µg/m³) |
| --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 78,54 | 79,20 | 20,33 | 20,70 |
| Hà Nội | 162,85 | 162,56 | 70,01 | 70,42 |
| Đà Nẵng | 38,23 | 37,44 | 7,83 | 7,58 |

Nguồn: [city_week2 của sinh viên Tiến Sơn](default/city_week2.csv), [city_week2 của sinh viên Ngọc Quyên](quyen/city_week2.csv). Mỗi trung bình dùng toàn bộ lượt ghi của sinh viên đó, không ép bằng cỡ mẫu. Các lượt cùng đô thị–giờ được giữ nguyên trong raw. Phân loại mẫu lần lượt vẫn là Moderate ở TP. Hồ Chí Minh, Unhealthy ở Hà Nội và Good ở Đà Nẵng; xem [phân bố của sinh viên Tiến Sơn](default/category_week2.csv) và [sinh viên Ngọc Quyên](quyen/category_week2.csv).

Đây là mốc bổ sung cho bộ báo cáo cũ 27/57. Không dùng bảng mới để giải thích các hình đã dựng từ bộ cũ, không cộng các bản ghi chung giữa hai lần tải và không suy ra biến động dài hạn từ mẫu hai ngày.

## Trạng thái dịch vụ đọc được

| Hạng mục | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Lambda | Active, Python 3.12, 256 MB, 60 giây | Active, Python 3.12, 256 MB, 60 giây |
| Mã hàm so với repo | Khác | Khác |
| Rule bật trỏ tới hàm | 1 | 2 |
| Quyền EventBridge gọi Lambda | Có | Có |
| S3 | AES256, bốn tùy chọn chặn công khai bật | AES256, bốn tùy chọn chặn công khai bật |
| SNS | Một topic dự án, một email đã xác nhận | Một topic dự án, hai email đã xác nhận |
| Alarm | INSUFFICIENT_DATA | INSUFFICIENT_DATA |
| Invocations Sum trong cửa sổ đã đọc | 13 | 25 |
| Errors Sum trong cửa sổ đã đọc | 288 | 576 |

[services.json của sinh viên Tiến Sơn](default/services.json) · [services.json của sinh viên Ngọc Quyên](quyen/services.json). `PASS` trong `service_checks.csv` nghĩa là API đọc được phản hồi, không phải hệ thống đã vận hành ổn định.

CloudWatch được hỏi với namespace `AWS/Lambda`, dimension `FunctionName=WeatherCollectorLambda`, statistic `Sum` cho Invocations/Errors, `Average` cho Duration và period 86.400 giây. Khoảng truy vấn bắt đầu từ ranh giới Tuần 2 và kết thúc ở thời điểm đọc từng môi trường. [CSV metric sinh viên Tiến Sơn](default/cloudwatch_metrics.csv) · [CSV metric sinh viên Ngọc Quyên](quyen/cloudwatch_metrics.csv). Các timestamp giữ nguyên offset trong phản hồi SDK; offset được ghi trong chuỗi thời gian. Đây là các điểm theo ngày, không phải số tổng tại thời điểm Alarm.

Errors lớn hơn Invocations ngay cả với truy vấn cùng namespace/dimension/statistic; chưa xác định nguyên nhân và chưa tính tỷ lệ lỗi. Hai lịch trong môi trường sinh viên Ngọc Quyên cần được đối chiếu trước khi kết luận về mật độ lấy mẫu. [Kế hoạch Tuần 3](../../../docs/WEEK_3_PLAN.md) nêu bước kiểm tra tiếp theo.

## Truy vết truy vấn và tệp

- [queries.json sinh viên Tiến Sơn](default/queries.json) và [sinh viên Ngọc Quyên](quyen/queries.json): QueryExecutionId, SQL nguồn, trạng thái, thời gian, bytes quét, số dòng và SHA-256.
- [Bảy SELECT dùng lại](../../athena/week2_analysis/): `raw_all`, `raw_week2`, `city_week2`, `category_week2`, `hour_city_week2`, `partition_all`, `quality_all`.
- [Danh sách đối tượng sinh viên Tiến Sơn](default/s3_objects.csv) và [sinh viên Ngọc Quyên](quyen/s3_objects.csv): key, kích thước, thời gian sửa; không chứa đường dẫn tải có chữ ký.
- [Manifest](manifest.json): commit nền, hash chương trình tại lúc thu thập và hash/bytes của các tệp kết quả. Mã bộ thu thập được sửa riêng phần in Unicode trên Windows và lưu kết quả khi STS lỗi sau lần này; không chạy lại các truy vấn vì thay đổi đó.

## Cách tái lập và giới hạn

Chạy từ gốc repo với hai profile SDK đã cấu hình trên máy:

```powershell
python -X utf8 tuan_2/scripts/collect_repository_evidence.py --output output/review-moi
python tuan_2/scripts/repository_audit.py --check
```

Thư mục đích phải chưa tồn tại để tránh ghi đè. Nếu có API không đọc được hoặc thiếu truy vấn, chương trình giữ manifest và trả mã thoát khác 0. Athena SELECT tạo các đối tượng kết quả thông thường trong S3; chương trình không triển khai, đổi lịch, thay quyền, gọi Lambda, lấy giá trị Secret hoặc gửi SNS. Metadata không công bố token, URL tải gói có chữ ký hay địa chỉ email. Lần đọc này xác nhận tài nguyên và dữ liệu đang đọc được, không chứng minh phiên bản repo vừa được triển khai, thư đã tới người nhận hoặc lịch chạy suốt thời gian Lab ngừng hoạt động.

[Hồ sơ Tuần 2](../../README.md) · [Bộ dữ liệu đã lưu](../README.md) · [Mã thu thập minh chứng](../../scripts/collect_repository_evidence.py)
