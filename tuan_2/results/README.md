# Danh mục dữ liệu và biểu đồ

| Thư mục | Vai trò | Chương trình sử dụng |
| --- | --- | --- |
| [athena_queries/](athena_queries/) | Bộ CSV Tuần 1 và metadata của năm truy vấn, dùng để dựng bốn hình; raw có 156 bản ghi | [generate_charts.py](../analytics/generate_charts.py), chế độ sao chép ngoại tuyến của exporter |
| [data_exports/](data_exports/) | Bản sao để kiểm tra xuất dữ liệu và đối chiếu với `athena_queries/` | [Kiểm tra CSV](../tests/test_csv_exports.py); đích xuất mặc định tương thích |
| [charts/](charts/) | Chín hình Tuần 1 từ bộ CSV đã lưu, thống kê bổ sung và manifest | [Báo cáo Tuần 1](../../tuan_1/README.md) |
| [sample_data/](sample_data/) | Ba phản hồi Lambda lịch sử đã lưu; dùng để đọc ví dụ cấu trúc phản hồi | Minh họa hồ sơ trước Tuần 2; tên `backfill` không xác nhận đủ chuỗi lịch sử |
| [week2_live/](week2_live/) | CSV Athena và metadata đã lưu của hai sinh viên, tách `default/` (Tiến Sơn) và `quyen/` (Ngọc Quyên) | [analyze_week2_accounts.py](../analytics/analyze_week2_accounts.py) |
| [week2_evidence/](week2_evidence/) | Raw NDJSON, metadata tài nguyên, truy vấn và chỉ số đã lưu của mỗi sinh viên | Bộ phân tích Tuần 2 đối chiếu nguồn CSV và phạm vi vận hành |
| [week2_analysis/](week2_analysis/) | 27 CSV gồm 25 bảng nền tảng và hai bảng đối chiếu bổ sung; manifest nhận diện đầu vào nền tảng | Excel/báo cáo Tuần 2 và chương trình dựng hình |
| [week2_charts/](week2_charts/) | 20 PNG và manifest liên kết mỗi hình với CSV nguồn | [generate_week2_charts.py](../analytics/generate_week2_charts.py) |

## Bộ nộp Tuần 1

Bản CSV đi cùng báo cáo nằm tại [tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/](../../tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/). Sáu CSV có cùng cột, thứ tự dòng và giá trị với bộ dùng đối chiếu ở đây. Năm tệp giống hoàn toàn về bytes; CSV raw chỉ khác kiểu xuống dòng LF/CRLF. Giữ nguyên định dạng từng bản đã lưu. Các vị trí này giúp báo cáo đã nộp và chương trình đọc dữ liệu có đường dẫn rõ ràng; chúng không phải những quan trắc độc lập.

## Phạm vi Tuần 2

CSV raw của sinh viên Tiến Sơn có 204 dòng và sinh viên Ngọc Quyên có 231 dòng. Sau lọc Tuần 2 còn 27/57 lượt ghi gốc. [hourly_city.csv](week2_analysis/hourly_city.csv) gom theo đô thị và giờ UTC, cho 27 nhóm ở mỗi sinh viên; [matched_account_hours.csv](week2_analysis/matched_account_hours.csv) giữ 21 nhóm có dữ liệu của cả hai. Sinh viên Ngọc Quyên có 24 nhóm gồm hai lượt và ba nhóm gồm ba lượt, nhưng các chỉ số môi trường trong cùng nhóm bằng nhau. Các tệp raw không bị lược dòng. `default` và `quyen` là mã nguồn dữ liệu trong các tệp; nhãn trình bày dùng “sinh viên Tiến Sơn” và “sinh viên Ngọc Quyên”.

Các tệp đã lưu là đầu vào của báo cáo. Để xuất thêm dữ liệu mà giữ riêng bộ này, dùng `--output output/athena` như [hướng dẫn vận hành](../../docs/operation.md). Dữ liệu phân tích và hình có thể được tái tạo từ những đầu vào đã lưu; timestamp tạo tệp trong manifest không phải thời điểm quan trắc mới.
