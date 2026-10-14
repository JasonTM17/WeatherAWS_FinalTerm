# Hệ thống thu thập và phân tích thời tiết và chất lượng không khí

Học phần **Điện toán đám mây**, lớp **261CLCO332779_05**, Nhóm 05. GVHD **ThS. Huỳnh Xuân Phụng**.

[Repository GitHub](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)

| Sinh viên | MSSV | Phụ trách chính |
| --- | --- | --- |
| Nguyễn Tiến Sơn | 24110054 | S3, Secrets Manager, Lambda và SNS |
| Trần Thị Ngọc Quyên | 24110051 | Glue, Athena, biểu đồ và đối chiếu dữ liệu |

Hai thành viên cùng thiết kế kiến trúc, tích hợp và báo cáo. [Nhật ký nhóm](docs/WORKLOG.md).

## Báo cáo và dữ liệu

| Tuần | Phạm vi | Word | PDF | Excel |
| --- | --- | --- | --- | --- |
| 1 | Bộ dữ liệu đã nộp: 156 bản ghi và bốn biểu đồ | [Word](tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx) | [PDF](tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf) | [Excel](tuan_1/docs/Bao_cao_tuan_1_Du_lieu_Athena_Nhom_05.xlsx) |
| 2 | Hai bộ báo cáo dữ liệu của sinh viên Tiến Sơn và sinh viên Ngọc Quyên, 18 biểu đồ và 24 truy vấn mới | [Word](tuan_2/docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx) | [PDF](tuan_2/docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.pdf) | [Excel](tuan_2/docs/Du_lieu_phan_tich_Tuan_2_Nhom_05.xlsx) |

[Tài liệu dự án](docs/README.md) · [Kiến trúc](docs/architecture.md) · [Phương pháp dữ liệu](docs/data-analysis.md) · [Vận hành](docs/operation.md) · [Hướng dẫn đọc source](docs/source-guide.md) · [Kiểm tra source](TEST_READY.md).

## Cấu trúc repository

| Thư mục | Vai trò | Điểm bắt đầu |
| --- | --- | --- |
| `docs/` | Tài liệu chung, kiến trúc, phương pháp và nhật ký | [Mục lục tài liệu](docs/README.md) |
| `tuan_1/` | Báo cáo, dữ liệu đã nộp và script nền tảng của Tuần 1 | [Tuần 1](tuan_1/README.md) |
| `tuan_2/lambda/` | Chương trình thu thập chính | [lambda_function.py](tuan_2/lambda/lambda_function.py) |
| `tuan_2/scripts/` | Quản lý dịch vụ và xuất CSV bằng Python SDK; PowerShell chuyển tham số | [Hướng dẫn vận hành](docs/operation.md) |
| `tuan_2/athena/` | Một bảng dữ liệu, một view và các truy vấn phân tích | [Thứ tự dùng SQL](tuan_2/athena/README.md) |
| `tuan_2/analytics/` | Phân tích CSV và dựng biểu đồ của từng tuần | [Hướng dẫn đọc source](docs/source-guide.md) |
| `tuan_2/results/` | Các tập dữ liệu đã lưu, metadata và hình từ dữ liệu | [Danh mục dữ liệu](tuan_2/results/README.md) |
| `tests/`, `tuan_2/tests/` | Kiểm tra cấu trúc/tài liệu ở gốc và kiểm tra chức năng chuẩn | [Các lệnh kiểm tra](TEST_READY.md) |

Hai tuần dùng chung một bộ triển khai tại `tuan_2/`; các script nền tảng Tuần 1 gọi bộ này. Chi tiết tệp chuẩn, bản sao dữ liệu và các điểm vào tương thích nằm trong [sơ đồ source](docs/repository-layout.md).

## Kết quả Tuần 2

Báo cáo dữ liệu của sinh viên Tiến Sơn có 204 bản ghi raw, báo cáo của sinh viên Ngọc Quyên có 231 bản ghi raw. Sau lọc ranh giới Tuần 2 theo UTC+7, có **27 và 57 dòng nguồn**, tương ứng **9 và 19 mẫu mỗi đô thị**. Hai bộ báo cáo dữ liệu được trình bày riêng; 144 quan trắc lịch sử cùng đô thị và thời điểm có giá trị cảm biến tương ứng bằng nhau được nhận diện khi đối chiếu.

| Đô thị | AQI TB Tiến Sơn | AQI TB Ngọc Quyên | PM2.5 TB Tiến Sơn µg/m³ | PM2.5 TB Ngọc Quyên µg/m³ |
| --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 78,00 | 79,05 | 23,38 | 22,92 |
| Hà Nội | 163,56 | 163,05 | 76,66 | 75,11 |
| Đà Nẵng | 35,44 | 35,37 | 6,38 | 6,46 |

Mẫu mới bao phủ hai ngày và 9 giờ riêng trong bộ dữ liệu của mỗi sinh viên, chưa đủ toàn bộ tuần. Tương quan mô tả tập mẫu, không chứng minh quan hệ nhân quả. Dữ liệu API chất lượng không khí dựa trên sản phẩm CAMS, không phải phép đo trực tiếp tại trạm.

- [CSV Athena trong hai báo cáo dữ liệu](tuan_2/results/week2_live/)
- [25 CSV phân tích và đối chiếu](tuan_2/results/week2_analysis/)
- [18 biểu đồ và bảng nguồn](tuan_2/results/week2_charts/)
- [Tệp raw và metadata dịch vụ đã đọc](tuan_2/results/week2_evidence/)
- [SQL của 12 phép phân tích](tuan_2/athena/week2_analysis/)

## Kiến trúc và thao tác

![Kiến trúc](docs/architecture.png)

EventBridge gọi Lambda; Lambda đọc cấu hình Secrets Manager, thu thập Open-Meteo, ghi NDJSON vào S3 và gửi SNS. Glue quản lý lược đồ, Athena phân tích dữ liệu và CloudWatch ghi chỉ số/log. Các thao tác quản lý và xuất dữ liệu dùng boto3.

Môi trường AWS của sinh viên Ngọc Quyên có hai quy tắc lịch đang bật và hai đăng ký email xác nhận, sinh viên Tiến Sơn có một lịch và một đăng ký. Các tổng Errors lớn hơn Invocations được giữ nguyên và tỷ lệ lỗi để trống trong bộ phân tích; không suy diễn trạng thái chạy ổn định từ một Alarm OK.

## Tái lập phân tích

Yêu cầu Python 3.12 trở lên và dependencies trong requirements.txt.

```powershell
python -m pip install -r requirements.txt
python tuan_2/analytics/analyze_week2_accounts.py
python tuan_2/analytics/generate_week2_charts.py
python -m unittest discover -s tuan_2/analytics -p "test_*.py" -v
```

Phân tích dùng tệp đã xuất cùng metadata và không cần thông tin đăng nhập. Để chạy các chức năng quản lý dịch vụ hoặc xuất dữ liệu mới, xem [hướng dẫn vận hành](docs/operation.md). Không đưa credentials vào repository. Bộ 52 kiểm tra chức năng và các hồi quy phân tích dữ liệu có phạm vi riêng; kết quả cục bộ không phải một lần triển khai AWS mới.
