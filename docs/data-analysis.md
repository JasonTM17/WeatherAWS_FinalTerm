# Mô hình dữ liệu và phân tích

## Bộ dữ liệu đã lưu

156 mã bản ghi khác nhau, 52 mẫu cho mỗi đô thị TP. Hồ Chí Minh, Hà Nội và Đà Nẵng. Mỗi bản ghi có 23 trường, gồm nhận diện, tọa độ, thời gian UTC/VN, khí tượng, các nồng độ ô nhiễm, AQI và ba khóa phân vùng. Xem [CSV gốc](../tuan_2/results/athena_queries/raw_weather_aqi_records.csv) và [lược đồ Athena](../tuan_2/athena/create_table.sql).

Dữ liệu chất lượng không khí được cung cấp qua [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), dựa trên sản phẩm mô hình khí quyển CAMS. Bộ số liệu API đã lưu không được coi là phép đo trực tiếp tại một trạm.

| Kết quả | Cách nhóm | Số dòng |
| --- | --- | ---: |
| avg_aqi_by_city.csv | Thành phố | 3 |
| peak_pollution_hours.csv | Giờ UTC | 24 |
| aqi_category_distribution.csv | Thành phố và cấp AQI | 8 |
| weather_correlation.csv | Thành phố | 3 |
| raw_weather_aqi_records.csv | Bản ghi | 156 |

Tổng mẫu theo đô thị, nhóm giờ và cấp AQI đều là 156. Bốn nhóm giờ có 9 mẫu và hai mươi nhóm giờ có 6 mẫu. Tỷ lệ AQI được tính trên số mẫu của từng đô thị; không diễn giải thành tỷ lệ thời gian vận hành.

## Đọc kết quả

AQI trung bình của TP. Hồ Chí Minh là 107,79, Đà Nẵng 74,67 và Hà Nội 67,56. AQI theo giờ cao nhất ở 11 UTC (103,83); PM2.5 theo giờ cao nhất ở 19 UTC (25,53 µg/m³). Những giá trị này mô tả tập dữ liệu đã lưu; chúng không đủ để kết luận nguyên nhân phát thải hoặc chu kỳ điển hình.

Hệ số Pearson tính riêng cho từng đô thị. Ví dụ, nhiệt độ–PM2.5 tại TP. Hồ Chí Minh có r = −0,6977, độ ẩm–PM2.5 có r = 0,6627. Tương quan không chứng minh quan hệ nhân quả.

## Xuất và kiểm tra

Xuất trực tiếp lưu CSV do Athena trả về. Nếu đọc qua API phân trang, chương trình giữ header một lần và bảo toàn ô rỗng. Chế độ ngoại tuyến chỉ sao chép bản đã lưu; manifest ghi `saved-snapshot`. Số liệu `query_metrics.csv` là dữ liệu lịch sử của các lượt truy vấn trong bộ kết quả, không phải kết quả mới của một lần sao chép ngoại tuyến.
