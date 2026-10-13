# Kiến trúc hệ thống

![Luồng xử lý](architecture.png)

| Thành phần | Trách nhiệm | Đầu ra |
| --- | --- | --- |
| EventBridge | Kích hoạt theo biểu thức rate(1 hour) | Sự kiện tới Lambda |
| Secrets Manager | Quản lý vị trí và ngưỡng | Cấu hình xử lý |
| Lambda | Gọi hai API cho mỗi đô thị; chuẩn hóa và phân loại AQI | Bản ghi 23 trường |
| S3 | Lưu NDJSON theo phân vùng thời gian | Tệp trong raw/year=YYYY/month=MM/day=DD/ |
| SNS | Tiếp nhận thông báo khi AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³ | Thông điệp cảnh báo |
| Glue và Athena | Lược đồ, phân vùng và truy vấn | CSV tổng hợp và CSV raw |
| CloudWatch | Theo dõi Invocations, Errors và Duration | Metric, alarm và dashboard |

Các ngưỡng cảnh báo là cấu hình của dự án. SNS chấp nhận thông điệp không đồng nghĩa email đã được nhận; người dùng cần xác nhận subscription. Kết quả SDK kiểm tra cục bộ được phân biệt với dữ liệu của một lần vận hành trên AWS.

## Cấu hình triển khai

`S3_BUCKET_NAME`, `SECRET_NAME` và `SNS_TOPIC_ARN` được truyền vào Lambda qua môi trường. Chương trình quản lý dùng account của phiên đăng nhập để dựng tên bucket và ARN. Một lịch chính `WeatherCollectionSchedule` được tạo cho hàm; tên cũ được xử lý trong chức năng thu hồi tài nguyên.

## Xử lý lỗi

Lambda có cấu hình dự phòng và ghi log khi đọc secret thất bại. Chương trình Athena có giới hạn thời gian chờ, dừng truy vấn khi timeout và giữ lại tệp cũ nếu truy vấn mới thất bại. Phân trang kết quả giữ vị trí cột và giá trị rỗng của SQL NULL.

Chuỗi khí tượng lịch sử được ghép với quan trắc AQI theo timestamp. Lambda phát sinh lỗi nếu không thu được bản ghi; nếu chỉ một số đô thị thất bại, kết quả ghi `collection_status=partial` và `failed_cities`. Cách này phân biệt lỗi thu thập với một lượt hoàn tất.
