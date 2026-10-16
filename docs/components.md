# Mã nguồn và lịch sử theo thành phần

Các đường dẫn mở trực tiếp mã nguồn và mốc commit liên quan. Commit là lịch sử cập nhật trên GitHub; trạng thái triển khai AWS được đối chiếu riêng trong [hồ sơ kiểm chứng](../tuan_2/results/review_2026_10_16/README.md).

| Thành phần | Tệp và vai trò | Phụ trách chính | Commit hoặc lịch sử |
| --- | --- | --- | --- |
| Lambda | [lambda_function.py](../tuan_2/lambda/lambda_function.py): thu thập hiện tại/lịch sử, phân loại AQI, ghi S3, gửi SNS | Sinh viên Tiến Sơn | [2947d3f](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/2947d3fdf7871ead2b99d486fa1d403a17183948) |
| S3 và cấu hình | [aws_project.py](../tuan_2/scripts/aws_project.py): bucket, mã hóa, chặn công khai, Secrets Manager | Sinh viên Tiến Sơn | [432add1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/432add13545ff0af1fb86457ccaa1f295b796576) |
| EventBridge, SNS, CloudWatch | [SDK](../tuan_2/scripts/aws_project.py) và [điểm vào PowerShell](../tuan_2/scripts/): lịch, target, quyền gọi hàm, đăng ký, Alarm | Sinh viên Tiến Sơn | [Lịch sử SDK](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commits/main/tuan_2/scripts/aws_project.py) |
| Glue | [create_table.sql](../tuan_2/athena/create_table.sql): 20 cột nội dung và ba khóa phân vùng ngày, JSON SerDe | Sinh viên Ngọc Quyên | [beb5817](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/beb5817079939be06121c9d02f8c1088a973c7d3) |
| View Athena | [create_view_vietnam_weather_aqi.sql](../tuan_2/athena/create_view_vietnam_weather_aqi.sql): thống nhất các trường bảng gốc | Sinh viên Ngọc Quyên | [Lịch sử view](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commits/main/tuan_2/athena/create_view_vietnam_weather_aqi.sql) |
| Truy vấn tuần | [12 SELECT](../tuan_2/athena/week2_analysis/): raw, đô thị, giờ, phân loại, tương quan, chất lượng và dung lượng quét | Sinh viên Ngọc Quyên | [Lịch sử SQL](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commits/main/tuan_2/athena/week2_analysis) |
| Xuất CSV | [athena_export.py](../tuan_2/scripts/athena_export.py): thực thi, phân trang, kiểm tra CSV, giữ tệp cũ khi lỗi | Sinh viên Ngọc Quyên | [432add1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/432add13545ff0af1fb86457ccaa1f295b796576) |
| Phân tích | [analyze_week2_accounts.py](../tuan_2/analytics/analyze_week2_accounts.py): lọc tuần, thống kê, tương quan, đối chiếu theo giờ | Sinh viên Ngọc Quyên | [432add1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/432add13545ff0af1fb86457ccaa1f295b796576) |
| Biểu đồ | [generate_week2_charts.py](../tuan_2/analytics/generate_week2_charts.py) và [phần bổ sung](../tuan_2/analytics/report_chart_extensions.py): đọc CSV và lưu manifest | Sinh viên Ngọc Quyên | [Lịch sử hình](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commits/main/tuan_2/analytics) |
| Minh chứng repo | [collect_repository_evidence.py](../tuan_2/scripts/collect_repository_evidence.py): đọc cấu hình và chạy SELECT, không lấy giá trị Secret | Cả hai đối chiếu | [Lịch sử bộ thu thập](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commits/main/tuan_2/scripts/collect_repository_evidence.py) |
| Kiểm tra hồ sơ | [repository_audit.py](../tuan_2/scripts/repository_audit.py): cột/dòng/hash CSV, giờ worklog, link và raw so với thống kê | Cả hai đối chiếu | [Lịch sử kiểm tra](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commits/main/tuan_2/scripts/repository_audit.py) |

## Vì sao tổ chức như vậy

EventBridge tách lịch khỏi xử lý; Lambda chuẩn hóa bản ghi theo cùng lược đồ. S3 giữ raw NDJSON theo `year/month/day`; Glue khai báo kiểu và phân vùng để Athena đọc bằng SQL. View dùng lại bảng gốc, tránh hai lược đồ độc lập. Exporter giữ CSV và mã truy vấn để kết quả truy về đầu vào. Biểu đồ đọc CSV thay vì nhập lại số liệu.

Mã SDK dùng chung nằm trong `tuan_2/`; hai script nền tảng Tuần 1 gọi module này. Đường dẫn hiện tại không đồng nghĩa toàn bộ nội dung tệp đã tồn tại từ Tuần 1. Hồ sơ lịch sử và mốc truy vấn được giữ riêng.

Chi tiết hàm, NULL và timeout nằm trong [hướng dẫn mã nguồn](source-guide.md); thao tác triển khai nằm trong [vận hành](operation.md).
