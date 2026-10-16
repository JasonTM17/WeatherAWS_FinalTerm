# Báo cáo tiến độ Tuần 1 và Tuần 2

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết và chất lượng không khí — lĩnh vực Domain Apps.

**Học phần:** Điện toán đám mây, lớp 261CLCO332779_05.

**Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng.

**Sinh viên thực hiện:** Nguyễn Tiến Sơn — MSSV 24110054; Trần Thị Ngọc Quyên — MSSV 24110051.

## Nội dung báo cáo tiến độ

Chúng em báo cáo tiến độ Tuần 1 và Tuần 2 của đề tài “Hệ thống thu thập và phân tích dữ liệu thời tiết và chất lượng không khí”, thuộc lĩnh vực Domain Apps. Đề tài hướng đến thu thập định kỳ dữ liệu từ Open-Meteo cho TP. Hồ Chí Minh, Hà Nội và Đà Nẵng; lưu trữ trên Amazon S3 theo phân vùng ngày; sử dụng AWS Glue và Amazon Athena để truy vấn, tổng hợp số liệu; đồng thời xây dựng chức năng cảnh báo theo ngưỡng bằng Amazon SNS và theo dõi hoạt động bằng Amazon CloudWatch.

Về phân công, sinh viên Tiến Sơn phụ trách S3, Secrets Manager, Lambda và SNS, phối hợp thiết lập lịch thu thập và giám sát. Sinh viên Ngọc Quyên phụ trách Glue, Athena, xuất CSV, phân tích dữ liệu và biểu đồ. Chúng em cùng thực hiện kiến trúc, tích hợp, đối chiếu kết quả và hoàn thiện báo cáo. Thời gian đã xác nhận của sinh viên Tiến Sơn là 9,5 giờ ở Tuần 1 và 10,0 giờ ở Tuần 2; của sinh viên Ngọc Quyên là 9,0 giờ ở Tuần 1 và 9,5 giờ ở Tuần 2. Tổng thời gian hai sinh viên là 18,5 giờ ở Tuần 1, 19,5 giờ ở Tuần 2 và 38,0 giờ cho cả hai tuần; nhật ký được đính kèm trên repository.

Trong Tuần 1, chúng em khảo sát API, thiết kế kiến trúc, chuẩn bị nền tảng lưu trữ và lược đồ dữ liệu, thực hiện truy vấn và xây dựng bộ phân tích ban đầu. Bộ dữ liệu dùng trong báo cáo có 156 bản ghi, tương ứng 52 bản ghi cho mỗi đô thị; gồm 105 bản ghi trong phạm vi Tuần 1 và 51 bản ghi lịch sử được nạp bổ sung trước ranh giới tuần. Hồ sơ có năm truy vấn Athena thành công, sáu tệp CSV và chín biểu đồ. Các tệp báo cáo Word/PDF, dữ liệu gốc và bảng tổng hợp đã được đưa vào thư mục Tuần 1 trên GitHub.

Trong Tuần 2, chúng em phát triển mã thu thập, bổ sung xử lý phản hồi API thiếu hoặc sai cấu trúc, điều chỉnh thời gian chờ theo thời gian Lambda còn lại, bảo vệ CSV đã lưu khi truy vấn xuất dữ liệu thất bại và hoàn thiện phương pháp phân tích. Bộ báo cáo dữ liệu của sinh viên Tiến Sơn có 204 bản ghi toàn bộ, trong đó 27 bản ghi thuộc Tuần 2; bộ của sinh viên Ngọc Quyên có 231 bản ghi toàn bộ, trong đó 57 bản ghi thuộc Tuần 2. Khi tổng hợp theo đô thị và giờ UTC, mỗi sinh viên có 27 nhóm, trong đó 21 nhóm cùng giờ được dùng đối chiếu trực tiếp. Chúng em giữ đầy đủ các bản ghi gốc, đồng thời cung cấp 27 bảng CSV phân tích, 20 biểu đồ và phụ lục 84 bản ghi thuộc Tuần 2 trong báo cáo.

Kết quả từ bộ báo cáo Tuần 2 đã lưu cho thấy Hà Nội có AQI trung bình cao nhất: 163,56 trong báo cáo dữ liệu của sinh viên Tiến Sơn và 163,05 trong báo cáo dữ liệu của sinh viên Ngọc Quyên; PM2.5 trung bình tương ứng là 76,66 và 75,11 µg/m³. Tại TP. Hồ Chí Minh, AQI trung bình lần lượt là 78,00 và 79,05; tại Đà Nẵng là 35,44 và 35,37. Các mẫu Hà Nội đều thỏa ngưỡng cảnh báo cấu hình AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³. Đây là kết quả trên tập mẫu ở hai ngày và chín khung giờ có dữ liệu của mỗi sinh viên; các thống kê và tương quan được sử dụng để mô tả mẫu, chưa đủ để kết luận về toàn tuần hoặc nguyên nhân biến động chất lượng không khí.

Đợt kiểm chứng bổ sung ngày 16/10/2026 ghi nhận 14/14 truy vấn SELECT thành công. Tổng số bản ghi tại lần đọc này là 216 đối với sinh viên Tiến Sơn và 249 đối với sinh viên Ngọc Quyên; số bản ghi thuộc Tuần 2 lần lượt là 39 và 75. Chúng em lưu riêng lần đọc bổ sung để giữ nguyên nguồn số liệu của báo cáo và biểu đồ đã lập. Hai Lambda được ghi nhận ở trạng thái Active; tuy nhiên phiên bản mã đang triển khai khác mã hiện tại trong repository, hai Alarm ở trạng thái INSUFFICIENT_DATA và chưa có minh chứng xác nhận email cảnh báo đã đến người nhận. Vì vậy, các thay đổi mã đã được kiểm tra cục bộ được trình bày riêng với trạng thái vận hành thực tế trên AWS.

Trong Tuần 3, chúng em dự kiến đồng bộ phiên bản triển khai, kiểm tra lịch thu thập, hoàn thiện giám sát và xác nhận luồng cảnh báo. Đồng thời, chúng em sẽ đối chiếu chất lượng dữ liệu, duy trì kiểm tra tự động trên GitHub Actions, thử nghiệm tối ưu truy vấn và đánh giá khả năng phân tích chuỗi thời gian khi dữ liệu đáp ứng yêu cầu. Các công việc, người phụ trách và tiêu chí hoàn thành được trình bày trong kế hoạch Tuần 3; hiệu quả tối ưu chỉ được kết luận sau khi có số đo thực nghiệm.

Chúng em đã bổ sung repository GitHub vào hồ sơ cả hai tuần. Thầy có thể truy cập các liên kết dưới đây để xem báo cáo, mã nguồn, nhật ký công việc, CSV và biểu đồ.

- [Repository GitHub](https://github.com/JasonTM17/WeatherAWS_FinalTerm)
- [Báo cáo tiến độ tổng hợp](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/BAO_CAO.md)
- [Hồ sơ Tuần 1: báo cáo Word/PDF, CSV và biểu đồ](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1)
- [Hồ sơ Tuần 2: báo cáo Word/PDF, CSV và biểu đồ](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2)
- [Nhật ký công việc và số giờ](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WORKLOG.md)
- [CSV tổng hợp số giờ](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv)
- [Mã nguồn và commit theo thành phần](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/components.md)
- [Kế hoạch Tuần 3](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_3_PLAN.md)

## Bảng đối chiếu sản phẩm và minh chứng

| Nội dung | Sản phẩm hoặc nguồn đối chiếu |
| --- | --- |
| Kiến trúc và luồng xử lý | [Kiến trúc hệ thống](docs/architecture.md) |
| Phân công và giờ đã xác nhận | [Worklog](docs/WORKLOG.md) · [CSV](worklog.csv) |
| Lược đồ và truy vấn | [Danh mục SQL](tuan_2/athena/README.md) |
| Mã thu thập, xử lý lỗi và giới hạn thời gian | [Lambda](tuan_2/lambda/lambda_function.py) · [Giải thích mã nguồn](docs/source-guide.md) |
| Cấu hình tài nguyên qua Python SDK | [aws_project.py](tuan_2/scripts/aws_project.py) |
| Xuất CSV và bảo vệ kết quả đã lưu | [Athena exporter](tuan_2/scripts/athena_export.py) |
| Thu thập và phân tích Tuần 1 | [Hồ sơ Tuần 1](tuan_1/README.md) · [CSV đã dùng](tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/) |
| Dữ liệu gốc Tuần 2 của sinh viên Tiến Sơn | [27 bản ghi trong tuần](tuan_2/results/week2_live/default/raw_week2.csv) · [204 bản ghi toàn bộ](tuan_2/results/week2_live/default/raw_all.csv) |
| Dữ liệu gốc Tuần 2 của sinh viên Ngọc Quyên | [57 bản ghi trong tuần](tuan_2/results/week2_live/quyen/raw_week2.csv) · [231 bản ghi toàn bộ](tuan_2/results/week2_live/quyen/raw_all.csv) |
| Trung bình AQI và PM2.5 | [city_statistics.csv](tuan_2/results/week2_analysis/city_statistics.csv) |
| Tỷ lệ thỏa ngưỡng cấu hình | [threshold_exceedance.csv](tuan_2/results/week2_analysis/threshold_exceedance.csv) |
| Tổng hợp và đối chiếu theo giờ | [hourly_city.csv](tuan_2/results/week2_analysis/hourly_city.csv) · [matched_account_hours.csv](tuan_2/results/week2_analysis/matched_account_hours.csv) |
| Tương quan và kích thước mẫu | [correlations.csv](tuan_2/results/week2_analysis/correlations.csv) |
| 20 biểu đồ và nguồn CSV của từng hình | [Thư mục hình](tuan_2/results/week2_charts/) · [Manifest](tuan_2/results/week2_charts/chart_manifest.json) |
| Dữ liệu mới và cấu hình đọc ngày 16/10 | [Kết quả, số dòng và giới hạn kiểm chứng](tuan_2/results/review_2026_10_16/README.md) |
| Tính nhất quán của hồ sơ | [Danh mục CSV](docs/csv_catalog.csv) · [Chương trình đối chiếu](tuan_2/scripts/repository_audit.py) |
| Kiểm tra tự động | [Workflow đang được cấu hình](.github/workflows/verify-repository.yml) · [Các lượt chạy GitHub Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions) |

## Cách đọc kết quả

Số lượt ghi gốc, số nhóm theo giờ và số nhóm giờ chung là ba đại lượng có mục đích khác nhau. Thống kê từng bộ dữ liệu dùng đầy đủ lượt ghi của sinh viên đó; đối chiếu trực tiếp dùng cùng đô thị và giờ UTC, mỗi giờ có cùng trọng số. Không cộng số dòng từ các lần xuất để coi là các quan trắc độc lập, không gộp trung bình hai sinh viên thành một chỉ số chung khi chưa xác định phương pháp tính và trọng số.

Dữ liệu chất lượng không khí lấy qua Open-Meteo là dữ liệu mô hình CAMS, không được trình bày như số đo trực tiếp tại trạm. Các hệ số tương quan được báo kèm đô thị, bộ dữ liệu và số cặp mẫu; chúng không xác định nguyên nhân từ giao thông, độ ẩm hoặc nghịch nhiệt. Tỷ lệ vượt ngưỡng cấu hình không chứng minh SNS đã phát thông báo ở từng lượt hoặc email đã đến hộp thư.

Trong mã hiện tại, xử lý số thiếu/không hợp lệ có chính sách giá trị mặc định; giá trị 0 cần được diễn giải theo quy tắc chuẩn hóa. Cơ chế điều chỉnh timeout hạn chế rủi ro quá thời gian nhưng không bảo đảm mọi yêu cầu HTTP/SDK hoặc ghi S3 đều hoàn thành trước giới hạn Lambda. Chi tiết và các kiểm tra nằm trong [hướng dẫn mã nguồn](docs/source-guide.md).

Chi phí dự kiến sinh viên xác nhận và số liệu Cost Explorer được trình bày riêng trong [phương pháp phân tích](docs/data-analysis.md). Giá trị do AWS trả về được giữ nguyên trong CSV; số hiển thị làm tròn không thay thế số liệu gốc hoặc hóa đơn cuối cùng.

## Kiểm tra và tái lập

Chạy từ gốc repository:

```powershell
python -m pip install -r tuan_2/analytics/requirements.txt
python tuan_2/scripts/repository_audit.py --check
python -m unittest discover -s tuan_2/tests -v
python -m unittest discover -s tuan_2/analytics -p "test_*.py" -v
```

Các lệnh kiểm tra dùng dữ liệu đã lưu và API/SDK giả lập. Kết quả CI được xác nhận theo từng commit; chúng không thay thế việc kiểm tra phiên bản triển khai, lịch chạy, Alarm hay thư thực nhận trên AWS. Đợt đọc ngày 16/10 giữ riêng metadata, mã truy vấn và hash để đối chiếu; dữ liệu báo cáo Tuần 1 và Tuần 2 được bảo toàn.

## Kết luận

Hai tuần đầu đã có bộ dữ liệu gốc, kết quả truy vấn, bảng phân tích, biểu đồ và nhật ký có thể mở trực tiếp trên GitHub. Báo cáo giữ rõ nguồn dữ liệu của từng sinh viên và phạm vi từng lần xuất. Phần tiếp theo tập trung đồng bộ mã triển khai, hoàn thiện tích hợp, giám sát và kiểm chứng cảnh báo theo [kế hoạch Tuần 3](docs/WEEK_3_PLAN.md).
