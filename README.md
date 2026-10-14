# Hệ thống thu thập và phân tích thời tiết và chất lượng không khí

Học phần **Điện toán đám mây**, lớp **261CLCO332779_05**, Nhóm 05. GVHD **ThS. Huỳnh Xuân Phụng**.

| Sinh viên | MSSV | Phụ trách chính |
| --- | --- | --- |
| Nguyễn Tiến Sơn | 24110054 | S3, Secrets Manager, Lambda và SNS |
| Trần Thị Ngọc Quyên | 24110051 | Glue, Athena, biểu đồ và đối chiếu dữ liệu |

Hai thành viên cùng thiết kế kiến trúc, tích hợp và báo cáo. [Nhật ký nhóm](docs/WORKLOG.md).

## Báo cáo và dữ liệu

| Tuần | Phạm vi | Word | PDF | Excel |
| --- | --- | --- | --- | --- |
| 1 | Bộ dữ liệu đã nộp: 156 bản ghi và bốn biểu đồ | [Word](tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx) | [PDF](tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf) | [Excel](tuan_1/docs/Bao_cao_tuan_1_Du_lieu_Athena_Nhom_05.xlsx) |
| 2 | Phân tích mới từ hai tài khoản, 16 biểu đồ và 24 truy vấn mới | [Word](tuan_2/docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx) | [PDF](tuan_2/docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.pdf) | [Excel](tuan_2/docs/Du_lieu_phan_tich_Tuan_2_Nhom_05.xlsx) |

[Tài liệu dự án](docs/README.md) · [Kiến trúc](docs/architecture.md) · [Phương pháp dữ liệu](docs/data-analysis.md) · [Vận hành](docs/operation.md).

## Kết quả Tuần 2

Đã tải 204 bản ghi raw từ tài khoản Sơn và 231 từ tài khoản Quyên. Sau lọc ranh giới Tuần 2 theo UTC+7, có **27 và 57 dòng nguồn**, tương ứng **9 và 19 mẫu mỗi đô thị**. Hai tài khoản được phân tích riêng; 144 quan trắc lịch sử trùng thành phố/thời gian và cùng giá trị cảm biến được nhận diện.

| Đô thị | AQI TB Sơn | AQI TB Quyên | PM2.5 TB Sơn µg/m³ | PM2.5 TB Quyên µg/m³ |
| --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 78,00 | 79,05 | 23,38 | 22,92 |
| Hà Nội | 163,56 | 163,05 | 76,66 | 75,11 |
| Đà Nẵng | 35,44 | 35,37 | 6,38 | 6,46 |

Mẫu mới bao phủ hai ngày và 9 giờ riêng mỗi tài khoản, chưa đủ toàn bộ tuần. Tương quan mô tả tập mẫu, không chứng minh quan hệ nhân quả. Dữ liệu API chất lượng không khí dựa trên sản phẩm CAMS, không phải phép đo trực tiếp tại trạm.

- [CSV Athena mới theo tài khoản](tuan_2/results/week2_live/)
- [25 CSV phân tích và đối chiếu](tuan_2/results/week2_analysis/)
- [16 biểu đồ và bảng nguồn](tuan_2/results/week2_charts/)
- [Tệp raw và metadata dịch vụ đã đọc](tuan_2/results/week2_evidence/)
- [SQL của 12 phép phân tích](tuan_2/athena/week2_analysis/)

## Kiến trúc và thao tác

![Kiến trúc](docs/architecture.png)

EventBridge gọi Lambda; Lambda đọc cấu hình Secrets Manager, thu thập Open-Meteo, ghi NDJSON vào S3 và gửi SNS. Glue quản lý lược đồ, Athena phân tích dữ liệu và CloudWatch ghi chỉ số/log. Các thao tác quản lý và xuất dữ liệu dùng boto3.

Source Lambda trên máy khác bản đang triển khai ở cả hai tài khoản; hash được lưu trong metadata. Tài khoản Quyên có hai quy tắc lịch đang bật và hai đăng ký email xác nhận, Sơn có một lịch và một đăng ký. Các tổng Errors lớn hơn Invocations được giữ nguyên và tỷ lệ lỗi để trống trong bộ phân tích; không suy diễn trạng thái chạy ổn định từ một Alarm OK.

## Tái lập phân tích

Yêu cầu Python 3.12 trở lên và dependencies trong requirements.txt.

```powershell
python -m pip install -r requirements.txt
python tuan_2/analytics/analyze_week2_accounts.py
python tuan_2/analytics/generate_week2_charts.py
python -m unittest discover -s tuan_2/analytics -p test_week2_analysis.py -v
```

Phân tích dùng tệp đã xuất cùng metadata và không cần thông tin đăng nhập. Để chạy các chức năng quản lý dịch vụ hoặc xuất dữ liệu mới, xem [hướng dẫn vận hành](docs/operation.md). Không đưa credentials vào repository. Bộ 44 kiểm tra chức năng cũ và 7 hồi quy phân tích sâu có phạm vi riêng; kết quả cục bộ không phải một lần triển khai AWS mới.
