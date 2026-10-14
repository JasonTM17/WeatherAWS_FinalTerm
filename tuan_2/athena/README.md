# Lược đồ và truy vấn Athena

## Bảng và view

| Tệp | Đối tượng | Vai trò |
| --- | --- | --- |
| [create_table.sql](create_table.sql) | `weather_aqi_db.weather_airquality_records` | Bảng ngoài đọc NDJSON trên S3: 20 cột và ba khóa phân vùng UTC `year/month/day` |
| [create_view_vietnam_weather_aqi.sql](create_view_vietnam_weather_aqi.sql) | `weather_aqi_db.vietnam_weather_aqi` | View chọn các cột từ bảng gốc |

Chương trình [aws_project.py](../scripts/aws_project.py), thao tác `setup-catalog`, tạo database nếu cần, tạo bảng gốc, chạy `MSCK REPAIR TABLE`, rồi tạo view. Hai tên đối tượng có vai trò riêng; tên `vietnam_weather_aqi` dành cho view. `ACCOUNT_ID` trong vị trí S3 là mẫu được SDK thay bằng bucket của phiên đăng nhập.

Nếu catalog đã có một bảng ngoài cũ mang tên `vietnam_weather_aqi`, SDK giữ đối tượng hiện có; cần xem loại đối tượng trước khi chuyển đổi. Source này không tự xóa bảng cũ để tạo view.

## Các truy vấn đọc dữ liệu

- Năm tệp `query_*.sql` là các SELECT dùng cho [bộ xuất CSV](../scripts/athena_export.py): dữ liệu raw, trung bình theo đô thị, thống kê theo giờ, phân bố AQI và tương quan thời tiết.
- [week2_analysis/](week2_analysis/) chứa 12 SELECT dùng trong hồ sơ Tuần 2 của mỗi sinh viên. Các điều kiện thời gian/phân vùng thuộc phạm vi dữ liệu đã lưu của tuần này.
- Kết quả, đơn vị và ranh giới thời gian được giải thích trong [phương pháp dữ liệu](../../docs/data-analysis.md) và [danh mục dữ liệu](../results/README.md).

Lược đồ và SQL được quản lý tại đây. Các script PowerShell gọi cùng SDK, không duy trì một bản triển khai SQL khác.
