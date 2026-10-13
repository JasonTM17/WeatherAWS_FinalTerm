# Hệ thống thu thập và phân tích dữ liệu thời tiết và chất lượng không khí

Đồ án học phần **Điện toán đám mây**, lớp **261CLCO332779_05**, Nhóm 05.
Giảng viên hướng dẫn: **ThS. Huỳnh Xuân Phụng**.

[Kho mã nguồn GitHub](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)

| Sinh viên | MSSV | Phụ trách chính |
| --- | --- | --- |
| Nguyễn Tiến Sơn | 24110054 | S3, Secrets Manager, Lambda và SNS |
| Trần Thị Ngọc Quyên | 24110051 | Glue, Athena, biểu đồ và đối chiếu dữ liệu |

Hai thành viên cùng thực hiện kiến trúc, tích hợp và báo cáo.

## Báo cáo và tài liệu

| Tuần | Nội dung | Word | PDF |
| --- | --- | --- | --- |
| 1 | Kiến trúc, cấu hình nền tảng và phân tích bộ dữ liệu | [Tải Word](tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx) | [Tải PDF](tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf) |
| 2 | Chức năng xử lý, lịch thu thập, cảnh báo và đối chiếu kết quả | [Tải Word](tuan_2/docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx) | [Tải PDF](tuan_2/docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.pdf) |

[Tài liệu dự án](docs/README.md) · [Kiến trúc](docs/architecture.md) · [Mô hình dữ liệu và phân tích](docs/data-analysis.md) · [Hướng dẫn vận hành](docs/operation.md)

## Kiến trúc

![Kiến trúc và luồng dữ liệu](docs/architecture.png)

EventBridge kích hoạt Lambda theo giờ. Lambda đọc cấu hình từ Secrets Manager, gọi API thời tiết và chất lượng không khí của Open-Meteo, chuẩn hóa bản ghi rồi lưu NDJSON vào S3 theo phân vùng năm/tháng/ngày. SNS tiếp nhận thông báo vượt ngưỡng. Glue quản lý lược đồ; Athena truy vấn dữ liệu S3; CloudWatch theo dõi lượt gọi, lỗi và thời gian xử lý.

## Số liệu dùng trong báo cáo

Bộ CSV đã lưu gồm **156 bản ghi**, 52 mẫu cho mỗi đô thị. Hai báo cáo dùng cùng bộ dữ liệu để đối chiếu; báo cáo Tuần 2 mô tả thêm phần chức năng và mã nguồn, không coi bộ CSV này là một lượt thu thập mới.

| Đô thị | Mẫu | AQI trung bình | PM2.5 trung bình µg/m³ | PM10 trung bình µg/m³ |
| --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 52 | 107,79 | 37,03 | 37,35 |
| Đà Nẵng | 52 | 74,67 | 14,23 | 17,28 |
| Hà Nội | 52 | 67,56 | 15,36 | 16,11 |

[Dữ liệu và kết quả Athena](tuan_2/results/athena_queries/) gồm so sánh đô thị, 24 nhóm giờ UTC, phân bố cấp AQI, tương quan khí tượng và bản ghi gốc. Thống kê mô tả tập mẫu; tương quan không chứng minh quan hệ nhân quả.

## Source và cách chạy

Yêu cầu Python 3.12 trở lên. Từ thư mục gốc:

```powershell
python -m pip install -r requirements.txt
python tuan_2/scripts/athena_export.py --offline --output output/csv
python tuan_2/analytics/generate_charts.py
python -m unittest discover -s tuan_2/tests -v
```

Chế độ `--offline` sao chép CSV đã lưu và tạo manifest ghi rõ nguồn; không tạo mã truy vấn hoặc trạng thái thực thi mới. Bộ kiểm tra cục bộ hiện gồm 40 ca, dùng dữ liệu và đối tượng dịch vụ giả lập.

Các thao tác AWS sử dụng **boto3**, chỉ tạo client khi chạy chức năng tương ứng. Phiên đăng nhập Learner Lab được cung cấp qua biến môi trường hoặc shared credentials của AWS SDK. Không đưa thông tin đăng nhập vào repository. Xem [hướng dẫn vận hành](docs/operation.md) để triển khai, kiểm tra trạng thái và quản lý tài nguyên.

## Cấu trúc

```text
tuan_1/             Báo cáo và chức năng nền tảng Tuần 1
tuan_2/lambda/      Chức năng thu thập và xử lý
tuan_2/athena/      Lược đồ, view và truy vấn
tuan_2/scripts/     Quản lý dịch vụ và xuất CSV bằng Python SDK
tuan_2/analytics/   Sinh biểu đồ từ CSV
tuan_2/tests/       Kiểm tra Lambda, CSV, biểu đồ và SDK
tuan_2/results/     Dữ liệu đã lưu và kết quả phân tích
docs/               Tài liệu dự án
```

Các kiểm tra mã nguồn không chứng minh một lần triển khai mới trên AWS. Trạng thái dịch vụ và kết quả vận hành cần được quan sát trong phiên thực hành tương ứng.
