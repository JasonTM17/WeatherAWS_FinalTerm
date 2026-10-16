# Thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS

Dự án sử dụng AWS Serverless để thu thập dữ liệu Open-Meteo cho TP. Hồ Chí Minh, Hà Nội và Đà Nẵng. Lambda xử lý dữ liệu theo lịch, lưu bản ghi trên S3 theo phân vùng ngày và gửi thông báo qua SNS khi thỏa ngưỡng cấu hình. Athena tổng hợp US AQI, PM2.5, PM10 và các yếu tố khí tượng để tạo bảng số liệu, biểu đồ và báo cáo theo tuần.

Học phần **Điện toán đám mây**, lớp **261CLCO332779_05**. GVHD **ThS. Huỳnh Xuân Phụng**.

[Repository GitHub](https://github.com/JasonTM17/WeatherAWS_FinalTerm) · [Hồ sơ Tuần 1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1) · [Hồ sơ Tuần 2](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2)

| Sinh viên | MSSV | Phụ trách chính |
| --- | --- | --- |
| Nguyễn Tiến Sơn | 24110054 | S3, Secrets Manager, Lambda và SNS |
| Trần Thị Ngọc Quyên | 24110051 | Glue, Athena, biểu đồ và đối chiếu dữ liệu |

Hai thành viên cùng thiết kế kiến trúc, tích hợp và báo cáo. [Nhật ký nhóm](docs/WORKLOG.md).

## Báo cáo và dữ liệu

| Tuần | Phạm vi | Word | PDF | Excel |
| --- | --- | --- | --- | --- |
| 1 | Bộ dữ liệu đã nộp: 156 bản ghi và chín biểu đồ | [Word](tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.docx) | [PDF](tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.pdf) | [Excel](tuan_1/docs/Bao_cao_tuan_1_Du_lieu_Athena_24110054_24110051.xlsx) |
| 2 | Hai bộ báo cáo dữ liệu của sinh viên Tiến Sơn và sinh viên Ngọc Quyên; 27 nhóm đô thị–giờ mỗi sinh viên, 20 biểu đồ, 24 truy vấn mới và phụ lục đủ 84 lượt ghi gốc | [Word](tuan_2/docs/Bao_cao_Tuan_2_24110054_24110051.docx) | [PDF](tuan_2/docs/Bao_cao_Tuan_2_24110054_24110051.pdf) | [Excel](tuan_2/docs/Du_lieu_phan_tich_Tuan_2_24110054_24110051.xlsx) |

[Tài liệu dự án](docs/README.md) · [Kiến trúc](docs/architecture.md) · [Phương pháp dữ liệu](docs/data-analysis.md) · [Vận hành](docs/operation.md) · [Hướng dẫn đọc mã nguồn](docs/source-guide.md).

## Cấu trúc dự án

| Thư mục | Vai trò | Điểm bắt đầu |
| --- | --- | --- |
| `docs/` | Tài liệu chung, kiến trúc, phương pháp và nhật ký | [Mục lục tài liệu](docs/README.md) |
| `tuan_1/` | Báo cáo, dữ liệu đã nộp và script nền tảng của Tuần 1 | [Tuần 1](tuan_1/README.md) |
| `tuan_2/lambda/` | Chương trình thu thập chính | [lambda_function.py](tuan_2/lambda/lambda_function.py) |
| `tuan_2/scripts/` | Quản lý dịch vụ và xuất CSV bằng Python SDK; PowerShell chuyển tham số | [Hướng dẫn vận hành](docs/operation.md) |
| `tuan_2/athena/` | Một bảng dữ liệu, một view và các truy vấn phân tích | [Thứ tự dùng SQL](tuan_2/athena/README.md) |
| `tuan_2/analytics/` | Phân tích CSV và dựng biểu đồ của từng tuần | [Hướng dẫn đọc mã nguồn](docs/source-guide.md) |
| `tuan_2/results/` | Các tập dữ liệu đã lưu, metadata và hình từ dữ liệu | [Danh mục dữ liệu](tuan_2/results/README.md) |
| `tuan_2/tests/` | Kiểm tra Lambda, SDK, CSV và biểu đồ của dự án | [Kiểm tra chức năng](tuan_2/tests/) |

Mã triển khai dùng chung nằm tại `tuan_2/`; các chương trình thiết lập nền tảng của Tuần 1 gọi lại bộ mã này. [Sơ đồ mã nguồn](docs/repository-layout.md) giải thích các tệp chính, dữ liệu đầu vào và cách dùng lại chương trình giữa hai tuần.

## Kết quả Tuần 2

Hai bộ dữ liệu đã lưu gồm 204 bản ghi của sinh viên Tiến Sơn và 231 bản ghi của sinh viên Ngọc Quyên. Sau khi lọc theo ranh giới Tuần 2 ở múi giờ UTC+7, có **27 và 57 lượt ghi gốc** tương ứng. Bộ của sinh viên Ngọc Quyên có hai hoặc ba lượt ghi trong cùng đô thị và giờ UTC với các chỉ số môi trường bằng nhau.

[Bảng theo giờ](tuan_2/results/week2_analysis/hourly_city.csv) tổng hợp các lượt ghi thành **27 nhóm đô thị–giờ cho mỗi sinh viên**; **21 nhóm có dữ liệu của cả hai sinh viên** được dùng để đối chiếu trực tiếp. Các bản ghi gốc được giữ riêng theo sinh viên và trình bày đầy đủ trong phụ lục. Khi đối chiếu dữ liệu lịch sử, có 144 quan trắc cùng đô thị và thời điểm xuất hiện trong cả hai bộ với các giá trị môi trường tương ứng bằng nhau.

| Đô thị | AQI TB<br>Sinh viên Tiến Sơn | AQI TB<br>Sinh viên Ngọc Quyên | PM2.5 TB (µg/m³)<br>Sinh viên Tiến Sơn | PM2.5 TB (µg/m³)<br>Sinh viên Ngọc Quyên |
| --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 78,00 | 79,05 | 23,38 | 22,92 |
| Hà Nội | 163,56 | 163,05 | 76,66 | 75,11 |
| Đà Nẵng | 35,44 | 35,37 | 6,38 | 6,46 |

Mẫu Tuần 2 của mỗi sinh viên bao phủ hai ngày, gồm chín giờ có dữ liệu. Các thống kê mô tả phạm vi mẫu đã thu thập; hệ số tương quan không chứng minh quan hệ nhân quả. Dữ liệu chất lượng không khí từ Open-Meteo dựa trên mô hình CAMS, không phải phép đo trực tiếp tại trạm.

- [CSV Athena trong hai báo cáo dữ liệu](tuan_2/results/week2_live/)
- [27 CSV phân tích và đối chiếu](tuan_2/results/week2_analysis/)
- [20 biểu đồ và bảng nguồn](tuan_2/results/week2_charts/)
- [Tệp raw và metadata dịch vụ đã đọc](tuan_2/results/week2_evidence/)
- [SQL của 12 phép phân tích](tuan_2/athena/week2_analysis/)

## Kiến trúc hệ thống

![Kiến trúc](docs/architecture.png)

EventBridge gọi Lambda; Lambda đọc cấu hình Secrets Manager, thu thập Open-Meteo, ghi NDJSON vào S3 và gửi SNS. Glue quản lý lược đồ, Athena phân tích dữ liệu và CloudWatch ghi chỉ số/log. Các thao tác quản lý và xuất dữ liệu dùng boto3.

Theo hồ sơ Tuần 2 đã lưu, môi trường AWS của sinh viên Ngọc Quyên có hai quy tắc lịch đang bật và hai đăng ký email đã xác nhận; sinh viên Tiến Sơn có một lịch và một đăng ký. Tổng Errors lớn hơn Invocations trong bộ chỉ số đã xuất, nên tỷ lệ lỗi được để trống trong kết quả phân tích. Trạng thái Alarm OK tại lần đọc được trình bày riêng với các chỉ số tích lũy.

## Tái lập phân tích

Yêu cầu Python 3.12 trở lên và các thư viện trong [tuan_2/analytics/requirements.txt](tuan_2/analytics/requirements.txt).

```powershell
python -m pip install -r tuan_2/analytics/requirements.txt
python tuan_2/analytics/analyze_week2_accounts.py
python tuan_2/analytics/generate_week1_supplement.py
python tuan_2/analytics/generate_week2_charts.py
python -m unittest discover -s tuan_2/analytics -p "test_*.py" -v
```

Phân tích dùng tệp đã xuất cùng metadata và không cần thông tin đăng nhập. Để chạy các chức năng quản lý dịch vụ hoặc xuất dữ liệu mới, xem [hướng dẫn vận hành](docs/operation.md). Không đưa credentials vào repository. Bộ kiểm tra gồm 56 ca chức năng và 18 ca phân tích dữ liệu; kết quả cục bộ không phải một lần triển khai AWS mới.
