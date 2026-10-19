# Tuần 2: Thu thập và phân tích hai bộ dữ liệu — Hệ thống thu thập và phân tích dữ liệu thời tiết/không khí (Domain Apps)

Nguyễn Tiến Sơn (24110054), Trần Thị Ngọc Quyên (24110051), lớp 261CLCO332779_05. GVHD ThS. Huỳnh Xuân Phụng.

[Báo cáo Nộp lại](../BAO_CAO.md) · [Repository](../README.md) · [Hồ sơ Tuần 1](../tuan_1/README.md) · [Phân công và worklog](docs/WORKLOG.md) · [CSV worklog](worklog.csv) · [Mã nguồn và commit](../docs/components.md) · [Kế hoạch Tuần 3](../docs/WEEK_3_PLAN.md)

## Mục tiêu và phần đã thực hiện

Chúng em hoàn thiện luồng thu thập, phân tích AQI và kiểm tra dữ liệu của sinh viên Tiến Sơn và sinh viên Ngọc Quyên. Nội dung được giữ trực tiếp trên GitHub để đối chiếu từng phần từ mã nguồn tới CSV và biểu đồ.

| Phần việc | Sản phẩm | Cách kiểm chứng |
| --- | --- | --- |
| Thu thập và lưu dữ liệu | [Lambda](lambda/lambda_function.py), NDJSON theo ngày | [Raw và metadata của từng sinh viên](results/week2_evidence/) |
| Lịch, cấu hình và cảnh báo | [SDK quản lý dịch vụ](scripts/aws_project.py) | [Rule, target, policy, cấu hình hàm và SNS mới đọc](results/review_2026_10_16/README.md) |
| Lược đồ và truy vấn | [Bảng, view](athena/README.md) và [12 SELECT](athena/week2_analysis/) | [24 kết quả truy vấn trong bộ đã lưu](results/week2_live/) |
| Phân tích và đối chiếu | [Chương trình phân tích](analytics/analyze_week2_accounts.py) | [27 CSV](results/week2_analysis/) |
| Trực quan hóa | [Chương trình dựng hình](analytics/generate_week2_charts.py) | [20 hình và manifest nguồn](results/week2_charts/) |

Mã hiện tại bổ sung kiểm tra phản hồi API, timeout theo thời gian Lambda còn lại, bảo vệ tệp CSV cũ khi xuất lỗi, ghép cặp hợp lệ khi tính tương quan và tránh tạo hình khi import module. [Giải thích code và lý do thiết lập](../docs/source-guide.md). Mã tại commit [36c9b39](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/36c9b3966a8b6f645dc6bb1491ad6e2b40a78765) đã được triển khai lên cả hai Lambda; module tải lại từ AWS khớp source. [Minh chứng thu thập, Athena và cảnh báo](../docs/deployment-verification.md) được giữ riêng với bộ dữ liệu đã dùng lập báo cáo.

## Phân công và số giờ

| Sinh viên | Phụ trách chính | Giờ Tuần 2 |
| --- | --- | ---: |
| Sinh viên Tiến Sơn | S3, Secrets Manager, Lambda và SNS; phối hợp lịch và giám sát | 10,0 |
| Sinh viên Ngọc Quyên | Glue, Athena, xuất CSV, biểu đồ và đối chiếu dữ liệu | 9,5 |

Cả hai phối hợp kiến trúc, tích hợp và hồ sơ. Tổng **19,5 giờ** đã xác nhận theo tuần. [Nhật ký đầu việc](docs/WORKLOG.md) ghi liên kết sản phẩm; chưa chia giờ theo ngày khi chưa có nhật ký buổi làm.

## Đầu vào và phạm vi thống kê

Open-Meteo cung cấp thời tiết và chất lượng không khí cho ba đô thị. Lược đồ gồm 20 trường nội dung và ba khóa phân vùng; raw có thành phố, tọa độ, thời gian UTC/UTC+7, 11 chỉ số môi trường dạng số, cấp AQI và thời điểm thu thập.

| Mốc | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên | Nguồn |
| --- | ---: | ---: | --- |
| Bộ báo cáo đã lưu | 204 toàn bộ; 27 thuộc Tuần 2 | 231 toàn bộ; 57 thuộc Tuần 2 | [Raw Athena](results/week2_live/) |
| Kiểm chứng AWS ngày 16/10 | 216 toàn bộ; 39 thuộc Tuần 2 | 249 toàn bộ; 75 thuộc Tuần 2 | [Raw, 14 SELECT mới và metadata](results/review_2026_10_16/README.md) |

Phần kết quả và 20 hình dưới đây dùng **bộ đã lưu 27/57**. Hai mốc không được trộn. Bộ lọc Tuần 2 là từ 12/10 00:00 đến trước 19/10 00:00 UTC+7; truy vấn dùng ranh giới UTC tương ứng. Mẫu thực có hai ngày và chín giờ ở mỗi sinh viên trong bộ đã lưu.

## Kết quả AQI ban đầu trong bộ đã lưu

| Đô thị | AQI TB sinh viên Tiến Sơn | AQI TB sinh viên Ngọc Quyên | PM2.5 TB sinh viên Tiến Sơn (µg/m³) | PM2.5 TB sinh viên Ngọc Quyên (µg/m³) |
| --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 78,00 | 79,05 | 23,38 | 22,92 |
| Hà Nội | 163,56 | 163,05 | 76,66 | 75,11 |
| Đà Nẵng | 35,44 | 35,37 | 6,38 | 6,46 |

Nguồn: [city_statistics.csv](results/week2_analysis/city_statistics.csv). Hà Nội có AQI trung bình cao nhất trong mẫu; các mẫu tại đây thuộc cấp Unhealthy. TP. Hồ Chí Minh thuộc Moderate và Đà Nẵng thuộc Good. [Số mẫu và tỷ lệ](results/week2_analysis/category_distribution.csv).

![AQI trung bình và độ lệch chuẩn](results/week2_charts/02_aqi_city.png)

![Biến thiên AQI theo giờ](results/week2_charts/05_hourly_aqi.png)

### Cách đối chiếu hai bộ báo cáo dữ liệu

Gom theo đô thị và giờ UTC cho **27 nhóm ở mỗi sinh viên**, trong đó **21 nhóm cùng giờ** được dùng đối chiếu trực tiếp. Bộ của sinh viên Ngọc Quyên có nhiều lượt ghi trong một giờ; raw giữ đầy đủ, thống kê theo lượt ghi và theo giờ được trình bày riêng. [hourly_city.csv](results/week2_analysis/hourly_city.csv) · [matched_account_hours.csv](results/week2_analysis/matched_account_hours.csv).

Mẫu Hà Nội có 9/9 và 19/19 lượt thỏa ngưỡng cấu hình `AQI >= 100` hoặc `PM2.5 >= 35.5`. Đây là tỷ lệ trong mẫu, không chứng minh ô nhiễm cả tuần hoặc email đã được gửi/nhận ở từng lượt. Các hệ số tương quan mô tả mẫu ngắn, không xác định quan hệ nhân quả.

### Đối chiếu Tuần 1

[submitted_week1_comparison.csv](results/week2_analysis/submitted_week1_comparison.csv) dùng đúng bộ 156 dòng Tuần 1, 52/đô thị. [weekly_comparison.csv](results/week2_analysis/weekly_comparison.csv) lọc lại hai tuần từ lần xuất mới và có cỡ mẫu khác; hai phép so sánh được trình bày riêng. [Chi tiết](../docs/data-analysis.md).

![Đối chiếu AQI với bộ Tuần 1 đã nộp](results/week2_charts/17_submitted_week1_aqi.png)

## Kiểm chứng vận hành mới

Đợt ngày 16/10 đọc được 13 nhóm thông tin dịch vụ ở mỗi môi trường và 14/14 SELECT thành công. CSV mới xác nhận mẫu Tuần 2 tăng lên 39/75 lượt ghi. [Manifest và bảng kết quả](results/review_2026_10_16/README.md) nêu mã truy vấn, thời gian tải, SHA-256, cấu hình, số đối tượng và phân vùng.

Tại snapshot trước triển khai, hai hàm Active nhưng mã chưa đồng bộ, hai Alarm thiếu dữ liệu và sinh viên Ngọc Quyên có hai lịch bật. Đợt đọc đó chỉ kiểm tra trạng thái. Trong [đợt triển khai tiếp theo](../docs/deployment-verification.md), source được đồng bộ; mỗi môi trường thu sáu bản ghi qua hai lượt gọi, Athena đối chiếu khớp và SNS phát hai thông điệp. Người nhận xác nhận cả hai bên nhận email mới. Lịch dư được tắt theo xác nhận; mỗi môi trường giữ một lịch một giờ. Alarm ở trạng thái OK tại lần đọc cuối. Commit [4a72d02](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/4a72d0260ce7fbe5ff681e8ec73d17c03ab8859b) lưu hồ sơ và JSON kiểm chứng của đợt này.

## Kết luận và hồ sơ đầy đủ

Tuần 2 đã có mã cho luồng thu thập/phân tích, các kết quả truy vấn truy được về raw, bảng thống kê và hình dùng cùng nguồn. Sau đợt triển khai, [hai lượt chạy theo lịch](../docs/scheduled-run-verification.md) được đối chiếu với metric EventBridge, log Lambda, sáu bản ghi mới và bốn thông điệp SNS; người nhận xác nhận email mới. Commit [3d6dfee](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/3d6dfeed922fa9d63d4659419bb75be675429c9a) lưu minh chứng của hai lượt tự động. Kết quả thống kê vẫn mô tả đúng các bộ mẫu đã lưu; hai lượt kiểm chứng chưa chứng minh vận hành ổn định nhiều ngày. [Tiến độ Tuần 3](../docs/WEEK_3_PLAN.md#tiến-độ-theo-minh-chứng-đã-có) phân biệt hai ưu tiên đã có kết quả với các phần mở rộng còn lại.

[Báo cáo chi tiết trên GitHub](docs/FINAL_REPORT.md) · [CSV Athena đã lưu](results/week2_live/) · [27 CSV phân tích](results/week2_analysis/) · [20 biểu đồ](results/week2_charts/) · [Raw và metadata đã lưu](results/week2_evidence/)

Các bản lưu bổ sung: [PDF](docs/Bao_cao_Tuan_2_24110054_24110051.pdf) · [Word](docs/Bao_cao_Tuan_2_24110054_24110051.docx) · [Excel](docs/Du_lieu_phan_tich_Tuan_2_24110054_24110051.xlsx).

## Liên kết minh chứng để sao chép

- **Báo cáo đầy đủ Tuần 2:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/FINAL_REPORT.md).

- **Raw và metadata: 27/57 bản ghi thuộc Tuần 2:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_evidence](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_evidence).

- **24 CSV kết quả Athena của hai sinh viên:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_live](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_live).

- **27 CSV phân tích và đối chiếu theo giờ:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_analysis](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_analysis).

- **20 biểu đồ và dữ liệu dùng để dựng hình:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_charts](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_charts).

- **Mã nguồn Lambda hiện tại dùng chung:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py).

- **Nhật ký và phân công Tuần 2: 19,5 giờ:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/WORKLOG.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/WORKLOG.md).

- **Các lượt theo lịch và xác nhận email ngày 16/10:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/scheduled-run-verification.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/scheduled-run-verification.md).

Danh mục Tuần 1–3, commit trực tiếp và cách đối chiếu: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/EVIDENCE_INDEX.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/EVIDENCE_INDEX.md).
