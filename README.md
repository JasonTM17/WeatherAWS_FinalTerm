# Thu thập và phân tích dữ liệu thời tiết và chất lượng không khí trên AWS

Dự án thu thập dữ liệu Open-Meteo cho TP. Hồ Chí Minh, Hà Nội và Đà Nẵng bằng AWS Serverless. EventBridge gọi Lambda; dữ liệu được chuẩn hóa, lưu trên S3 theo ngày và phân tích bằng Glue/Athena. SNS phục vụ cảnh báo theo ngưỡng cấu hình, CloudWatch phục vụ giám sát.

Học phần **Điện toán đám mây**, lớp **261CLCO332779_05**. GVHD **ThS. Huỳnh Xuân Phụng**. Sinh viên **Nguyễn Tiến Sơn (24110054)** và **Trần Thị Ngọc Quyên (24110051)**.

[Repository GitHub](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git) · [Báo cáo nộp lại](BAO_CAO_NOP_LAI.md) · [Hồ sơ Tuần 1](tuan_1/README.md) · [Hồ sơ Tuần 2](tuan_2/README.md)

## Hồ sơ tiến độ trên GitHub

| Nội dung | Đường dẫn xem trực tiếp |
| --- | --- |
| Tổng hợp bổ sung theo nhận xét GVHD | [Phân công, kết quả, minh chứng và kế hoạch](BAO_CAO_NOP_LAI.md) |
| Tuần 1 | [Mục tiêu, nền tảng, 156 bản ghi và chín biểu đồ](tuan_1/README.md) |
| Tuần 2 | [Phần đã thực hiện, kết quả AQI và dữ liệu hai sinh viên](tuan_2/README.md) |
| Phân công và số giờ | [Worklog](docs/WORKLOG.md) · [CSV tổng hợp](worklog.csv) |
| Mã nguồn và commit từng thành phần | [Chỉ mục mã nguồn](docs/components.md) |
| Kiểm chứng AWS bằng phiên mới | [Đợt ngày 16/10/2026](tuan_2/results/review_2026_10_16/README.md) |
| Kế hoạch Tuần 3 | [Tích hợp và giám sát](docs/WEEK_3_PLAN.md) |
| Danh mục tệp dữ liệu | [CSV có số dòng, số cột và SHA-256](docs/csv_catalog.csv) |

Repo chứa nội dung tiến độ, mã nguồn và dữ liệu để đọc trực tiếp. Word/PDF/Excel là các bản lưu bổ sung, có đường dẫn trong từng tuần.

## Phân công

| Sinh viên | MSSV | Phụ trách chính | Tuần 1 | Tuần 2 |
| --- | --- | --- | ---: | ---: |
| Nguyễn Tiến Sơn | 24110054 | S3, Secrets Manager, Lambda và SNS; phối hợp lịch và giám sát | 9,5 giờ | 10,0 giờ |
| Trần Thị Ngọc Quyên | 24110051 | Glue, Athena, xuất CSV, biểu đồ và đối chiếu dữ liệu | 9,0 giờ | 9,5 giờ |
| Tổng | | Cả hai cùng làm kiến trúc, tích hợp và hồ sơ | 18,5 giờ | 19,5 giờ |

Các tổng giờ đã được sinh viên xác nhận theo tuần; không suy ra giờ từng ngày từ lịch sử commit. [Nhật ký và minh chứng từng đầu việc](docs/WORKLOG.md).

## Kiến trúc và dữ liệu đầu vào

![Kiến trúc hệ thống](docs/architecture.png)

Open-Meteo cung cấp dữ liệu thời tiết và chất lượng không khí qua API. Bản ghi có 20 trường nội dung và ba khóa phân vùng `year/month/day`, gồm thành phố, tọa độ, thời gian UTC/UTC+7, khí tượng, bụi, khí ô nhiễm, US AQI và thời điểm thu thập. Dữ liệu chất lượng không khí dựa trên mô hình CAMS; không phải phép đo trực tiếp tại trạm.

[Kiến trúc chi tiết](docs/architecture.md) · [Mô hình và phương pháp phân tích](docs/data-analysis.md) · [Lược đồ và SQL](tuan_2/athena/README.md)

## Kết quả AQI trong bộ báo cáo Tuần 2 đã lưu

| Đô thị | AQI TB sinh viên Tiến Sơn | AQI TB sinh viên Ngọc Quyên | PM2.5 TB sinh viên Tiến Sơn (µg/m³) | PM2.5 TB sinh viên Ngọc Quyên (µg/m³) |
| --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 78,00 | 79,05 | 23,38 | 22,92 |
| Hà Nội | 163,56 | 163,05 | 76,66 | 75,11 |
| Đà Nẵng | 35,44 | 35,37 | 6,38 | 6,46 |

Bảng lấy từ [city_statistics.csv](tuan_2/results/week2_analysis/city_statistics.csv), dùng **27/57 lượt ghi gốc** trong phạm vi Tuần 2 của hai sinh viên. Khi tổng hợp theo đô thị–giờ, mỗi sinh viên có 27 nhóm; 21 nhóm cùng giờ dùng cho đối chiếu trực tiếp. Các lượt trong cùng giờ được giữ trong raw và giải thích trong [phương pháp](docs/data-analysis.md). Mẫu của mỗi sinh viên chỉ bao phủ hai ngày và chín giờ có dữ liệu; kết luận giới hạn trong tập mẫu.

![AQI theo đô thị trong bộ báo cáo đã lưu](tuan_2/results/week2_charts/02_aqi_city.png)

## Phân biệt các mốc dữ liệu

| Bộ dữ liệu | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên | Mục đích |
| --- | ---: | ---: | --- |
| Tuần 1 đã nộp | 156 bản ghi chung, 52/đô thị | Cùng bộ Tuần 1 | [Sáu CSV](tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/) và chín hình |
| Tuần 2 đã lưu | 204 toàn bộ; 27 thuộc Tuần 2 | 231 toàn bộ; 57 thuộc Tuần 2 | [24 truy vấn](tuan_2/results/week2_live/), [27 bảng](tuan_2/results/week2_analysis/), [20 hình](tuan_2/results/week2_charts/) |
| Đọc lại AWS ngày 16/10 | 216 toàn bộ; 39 thuộc Tuần 2 | 249 toàn bộ; 75 thuộc Tuần 2 | [14 SELECT mới, raw, metadata và hash](tuan_2/results/review_2026_10_16/README.md) |

Không cộng các mốc này thành các quan trắc độc lập. Truy vấn mới ghi vào thư mục riêng, giữ nguyên số liệu đã dùng trong báo cáo và biểu đồ cũ.

## Trạng thái kiểm chứng AWS mới

Hai Lambda đều Active, Python 3.12, 256 MB và timeout 60 giây. Hai S3 bật mã hóa AES256 và đủ bốn tùy chọn chặn truy cập công khai. Mỗi môi trường có sáu phân vùng Glue. Sinh viên Tiến Sơn có một lịch bật và một đăng ký email đã xác nhận; sinh viên Ngọc Quyên có hai lịch bật và hai đăng ký.

Hai Alarm hiện `INSUFFICIENT_DATA`; tổng Errors lớn hơn Invocations trong cửa sổ metric đã đọc, nên chưa tính tỷ lệ lỗi. Mã Lambda đang triển khai khác mã nguồn hiện tại trong repo. Đợt này chỉ đọc cấu hình và chạy SELECT, chưa triển khai hoặc gọi thử Lambda. [Metadata, mã truy vấn và giới hạn xác nhận](tuan_2/results/review_2026_10_16/README.md).

## Cấu trúc mã nguồn

| Thư mục | Vai trò |
| --- | --- |
| [docs/](docs/README.md) | Kiến trúc, phương pháp, worklog, chỉ mục commit và kế hoạch |
| [tuan_1/](tuan_1/README.md) | Hồ sơ nền tảng, phân công, CSV và báo cáo Tuần 1 |
| [tuan_2/lambda/](tuan_2/lambda/) | Hàm thu thập chuẩn |
| [tuan_2/scripts/](tuan_2/scripts/) | Python SDK quản lý dịch vụ, xuất CSV, đọc minh chứng và kiểm tra repo |
| [tuan_2/athena/](tuan_2/athena/README.md) | Một bảng gốc, một view và SQL phân tích |
| [tuan_2/analytics/](tuan_2/analytics/) | Phân tích CSV và dựng biểu đồ |
| [tuan_2/results/](tuan_2/results/README.md) | Các bộ raw, CSV, hình và metadata theo mốc |
| [tuan_2/tests/](tuan_2/tests/) | Kiểm tra chức năng và tính nhất quán của hồ sơ |

[Sơ đồ mã nguồn](docs/repository-layout.md) · [Giải thích code](docs/source-guide.md) · [Vận hành bằng Python SDK](docs/operation.md)

## Kiểm tra và tái lập

Python 3.12 trở lên. Các kiểm tra dưới đây dùng dữ liệu đã lưu, không cần credentials:

```powershell
python -m pip install -r tuan_2/analytics/requirements.txt
python tuan_2/scripts/repository_audit.py --check
python -m unittest discover -s tuan_2/tests -v
python -m unittest discover -s tuan_2/analytics -p "test_*.py" -v
```

Để tính lại bảng và dựng hình, xem [hướng dẫn tái lập](docs/source-guide.md). Để xuất một mốc kiểm chứng AWS khác, xem [hướng dẫn bộ thu thập](docs/operation.md). Không lưu credentials, token, giá trị Secret hoặc địa chỉ người nhận vào repo. Kiểm tra cục bộ/CI và minh chứng AWS có phạm vi xác nhận riêng.
