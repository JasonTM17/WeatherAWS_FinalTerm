# Kiểm tra source và tài liệu

Lệnh kiểm tra: `python -m unittest discover -s tuan_2/tests -v`.

52 ca kiểm tra cục bộ gồm Lambda, CSV, biểu đồ và SDK. Các ca kiểm tra không yêu cầu một lượt triển khai AWS mới. Word/PDF được kiểm tra riêng về bảng số liệu, hình, mục lục và bố cục sau khi xuất. Các hồi quy bổ sung kiểm tra phản hồi API thiếu khối current/hourly, API chậm và thời gian thu thập còn lại của Lambda ở cả chế độ hiện tại và lịch sử.

Kiểm tra phân tích: `python -m unittest discover -s tuan_2/analytics -p "test_*.py" -v`, gồm 13 ca về ranh giới thời gian, thống kê, nguồn đối chiếu và giá trị cột của hai biểu đồ so sánh trực tiếp. Hướng dẫn đọc từng module nằm trong [source-guide](docs/source-guide.md).

Kiểm tra hồ sơ và cấu trúc: `python tests/test_e2e_acceptance.py`. Cài `requirements.txt` trong cùng môi trường Python để đọc PDF và Word. Bộ này kiểm tra tệp, liên kết trong báo cáo, số liệu đã lưu và gọi lại bộ chức năng giả lập; tên tệp không có nghĩa là chạy trên dịch vụ AWS thật. Mục đọc lịch sử/remote Git được bỏ qua khi chạy bản source ZIP không có `.git`; kết quả hiển thị số mục bỏ qua.

Kiểm tra DDL xác nhận `weather_airquality_records` là bảng gốc, `vietnam_weather_aqi` là view đọc bảng này và không có DDL tạo bảng cùng tên view. [Sơ đồ source](docs/repository-layout.md) và [danh mục SQL](tuan_2/athena/README.md) giải thích các đường dẫn chuẩn.
