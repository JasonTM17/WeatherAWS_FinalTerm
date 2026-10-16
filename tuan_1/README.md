# Tuần 1 Nền tảng và kết quả phân tích dữ liệu

Nguyễn Tiến Sơn (24110054), Trần Thị Ngọc Quyên (24110051), lớp 261CLCO332779_05. GVHD ThS. Huỳnh Xuân Phụng.

[Báo cáo Nộp lại](../BAO_CAO_NOP_LAI.md) · [Tổng quan dự án](../README.md) · [Hồ sơ Tuần 2](../tuan_2/README.md) · [Mã nguồn và commit](../docs/components.md)

## Mục tiêu và phần đã thực hiện

Tuần 1 xác định luồng thu thập thời tiết/chất lượng không khí ở ba đô thị, cách lưu theo ngày và các truy vấn AQI ban đầu. Chúng em tổ chức dữ liệu Open-Meteo thành bản ghi NDJSON trên S3, khai báo lược đồ Glue và tổng hợp bằng Athena. Kiến trúc sử dụng EventBridge, Lambda, Secrets Manager, S3, Glue, Athena, SNS và CloudWatch.

Hai script nền tảng [S3](scripts/01_setup_s3.ps1) và [cấu hình](scripts/02_setup_secrets.ps1) gọi bộ SDK dùng chung. [Giải thích kiến trúc và dịch vụ](../docs/architecture.md). Mã nguồn hiện tại tiếp tục được sửa ở Tuần 2; không coi mọi dòng mã hiện tại là phiên bản đã triển khai trong Tuần 1.

## Phân công và thời gian

| Sinh viên | Phần chính | Phần chung | Giờ Tuần 1 |
| --- | --- | --- | ---: |
| Sinh viên Tiến Sơn | S3, Secrets Manager, Lambda và SNS | Kiến trúc, tích hợp, đối chiếu và hồ sơ | 9,5 |
| Sinh viên Ngọc Quyên | Glue, Athena, biểu đồ và đối chiếu dữ liệu | Kiến trúc, tích hợp, đối chiếu và hồ sơ | 9,0 |

Tổng **18,5 giờ** đã được sinh viên xác nhận theo tuần. [Nhật ký và đầu việc](docs/WORKLOG.md) · [CSV](worklog.csv) · [Phân công](docs/PHAN_CONG.md).

## Dữ liệu đầu vào và kết quả ban đầu

Bộ đã nộp có **156 bản ghi**, **52/đô thị**, gồm dữ liệu hiện tại và phần lịch sử nạp bổ sung; đây không phải 156 lượt chạy Lambda. Raw có 23 cột kể cả ba khóa phân vùng ngày. Các phép thống kê dùng AQI, PM2.5, PM10, nhiệt độ và độ ẩm.

| Đô thị | Số mẫu | AQI TB | AQI min–max | PM2.5 TB (µg/m³) | PM10 TB (µg/m³) |
| --- | ---: | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 52 | 107,79 | 95–172 | 37,03 | 37,35 |
| Hà Nội | 52 | 67,56 | 56–80 | 15,36 | 16,11 |
| Đà Nẵng | 52 | 74,67 | 36–155 | 14,23 | 17,28 |

Nguồn: [avg_aqi_by_city.csv](docs/Bao_cao_tuan_1_CSV_24110054_24110051/avg_aqi_by_city.csv). TP. Hồ Chí Minh có AQI trung bình cao nhất trong tập mẫu này. Hà Nội có toàn bộ 52 bản ghi ở cấp Moderate; TP. Hồ Chí Minh và Đà Nẵng có nhiều cấp khác nhau. [Số lượng và tỷ lệ theo cấp](docs/Bao_cao_tuan_1_CSV_24110054_24110051/aqi_category_distribution.csv).

![AQI trung bình Tuần 1](../tuan_2/results/charts/01_aqi_city_comparison.png)

![Biến thiên theo 24 nhóm giờ UTC](../tuan_2/results/charts/02_peak_pollution_hours.png)

Năm truy vấn đã lưu đều SUCCEEDED; mỗi truy vấn quét 87.250 byte, gồm bốn phép tổng hợp và một phép xuất raw. [Mã thực thi và metrics](docs/Bao_cao_tuan_1_CSV_24110054_24110051/query_metrics.csv). 24 nhóm giờ là phân nhóm theo giờ trong ngày, không đồng nghĩa mọi giờ của cả tuần đều có dữ liệu.

## CSV và biểu đồ đầy đủ

| Tệp | Nội dung |
| --- | --- |
| [raw_weather_aqi_records.csv](docs/Bao_cao_tuan_1_CSV_24110054_24110051/raw_weather_aqi_records.csv) | Đủ 156 bản ghi và các trường nguồn |
| [avg_aqi_by_city.csv](docs/Bao_cao_tuan_1_CSV_24110054_24110051/avg_aqi_by_city.csv) | Ba dòng thống kê đô thị |
| [peak_pollution_hours.csv](docs/Bao_cao_tuan_1_CSV_24110054_24110051/peak_pollution_hours.csv) | 24 nhóm giờ UTC |
| [aqi_category_distribution.csv](docs/Bao_cao_tuan_1_CSV_24110054_24110051/aqi_category_distribution.csv) | Tám nhóm đô thị–cấp AQI |
| [weather_correlation.csv](docs/Bao_cao_tuan_1_CSV_24110054_24110051/weather_correlation.csv) | Tương quan PM2.5 và khí tượng |
| [query_metrics.csv](docs/Bao_cao_tuan_1_CSV_24110054_24110051/query_metrics.csv) | Năm mã truy vấn, thời gian và bytes quét |

[Chín biểu đồ và bảng nguồn bổ sung](../tuan_2/results/charts/) gồm so sánh AQI, giờ ô nhiễm, cấp AQI, tương quan, bụi, khí tượng, phân bố, scatter và hiệu năng truy vấn. Các hình dùng cùng bộ CSV trên.

## Kết luận và bước tiếp theo

Tuần 1 đã hình thành luồng dữ liệu và bộ phân tích ban đầu có thể đối chiếu từ raw tới bảng và hình. Kết quả mô tả tập mẫu đã lưu, không chứng minh xu hướng toàn tuần hoặc nguyên nhân biến động môi trường. [Minh chứng dịch vụ theo mốc](../docs/saved-evidence.md) phân biệt kết quả Publish và email thực nhận.

[Tuần 2](../tuan_2/README.md) mở rộng phân tích hai bộ báo cáo dữ liệu, so sánh với bộ Tuần 1 và kiểm tra vận hành. [Kế hoạch Tuần 3](../docs/WEEK_3_PLAN.md) tiếp tục tích hợp và giám sát.

## Các bản lưu bổ sung

[Báo cáo chi tiết trên GitHub](docs/FINAL_REPORT.md) · [PDF](docs/Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.pdf) · [Word](docs/Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.docx) · [Excel số liệu và biểu đồ](docs/Bao_cao_tuan_1_Du_lieu_Athena_24110054_24110051.xlsx)
