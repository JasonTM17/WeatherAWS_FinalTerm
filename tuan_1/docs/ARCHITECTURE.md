# Kiến trúc Tuần 1

![Kiến trúc và luồng dữ liệu](../../docs/architecture.png)

EventBridge kích hoạt Lambda theo giờ. Lambda đọc cấu hình vị trí và ngưỡng từ Secrets Manager, gọi API Open-Meteo và ghi NDJSON vào S3 theo phân vùng thời gian. SNS tiếp nhận thông báo khi vượt ngưỡng; Glue quản lý lược đồ, Athena truy vấn S3 và CloudWatch theo dõi thực thi.

- [Mô tả kiến trúc và cấu hình mã nguồn](../../docs/architecture.md)
- [Mô hình dữ liệu và số liệu](../../docs/data-analysis.md)
- [Báo cáo Tuần 1](FINAL_REPORT.md)
- [Hướng dẫn vận hành Python SDK](../../docs/operation.md)

Bộ số liệu báo cáo gồm 156 bản ghi đã lưu, 52 mẫu cho mỗi đô thị. Bảng số liệu và biểu đồ mô tả tập mẫu này; cấu hình thiết kế không được dùng thay cho số liệu vận hành.
