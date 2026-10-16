# Bổ sung hồ sơ tiến độ Tuần 2

Học phần Điện toán đám mây, lớp 261CLCO332779_05. GVHD ThS. Huỳnh Xuân Phụng. Sinh viên Nguyễn Tiến Sơn (24110054) và Trần Thị Ngọc Quyên (24110051).

Chúng em bổ sung hồ sơ trực tiếp trong repo để thầy đối chiếu phân công, sản phẩm, dữ liệu và kế hoạch tiếp theo. [Repository](https://github.com/JasonTM17/WeatherAWS_FinalTerm) · [Tuần 1](tuan_1/README.md) · [Tuần 2](tuan_2/README.md).

## 1 Phân công và số giờ

| Sinh viên | Trách nhiệm chính | Tuần 1 | Tuần 2 | Tổng |
| --- | --- | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | S3, Secrets Manager, Lambda và SNS; phối hợp lịch và giám sát | 9,5 giờ | 10,0 giờ | 19,5 giờ |
| Sinh viên Ngọc Quyên | Glue, Athena, xuất CSV, biểu đồ và đối chiếu dữ liệu | 9,0 giờ | 9,5 giờ | 18,5 giờ |
| Cả hai | Kiến trúc, tích hợp, đối chiếu và tài liệu | 18,5 giờ | 19,5 giờ | 38,0 giờ |

Các số trên là tổng theo tuần đã được sinh viên xác nhận; dòng Cả hai là tổng thời gian của hai sinh viên, không phải thời gian cộng thêm. [Worklog](docs/WORKLOG.md) và [CSV](worklog.csv) liên kết các sản phẩm của từng phần việc. Không phân bổ thêm giờ theo ngày hoặc đầu việc khi chưa có nhật ký buổi làm.

## 2 Phần đã thực hiện và kết quả phân tích ban đầu

Chúng em đã tổ chức luồng Open-Meteo → Lambda → S3 → Glue/Athena, có lịch EventBridge và cấu hình ngưỡng SNS. S3 lưu NDJSON theo ngày; bảng Glue có 20 cột nội dung và ba khóa phân vùng. Bộ SQL xuất raw, thống kê đô thị/giờ/cấp AQI, tương quan và chất lượng dữ liệu. [Đầu vào và kết quả Tuần 2](tuan_2/README.md).

Các sửa đổi mã nguồn bổ sung kiểm tra phản hồi API, timeout theo thời gian còn lại, bảo vệ CSV khi truy vấn lỗi và ghép đúng cặp dữ liệu tương quan. Kết quả kiểm tra cục bộ được xác nhận riêng; metadata mới cho thấy mã đang triển khai chưa trùng mã hiện tại trong repo. [Giải thích code](docs/source-guide.md) · [Kiểm chứng AWS](tuan_2/results/review_2026_10_16/README.md).

| Đô thị | AQI TB sinh viên Tiến Sơn | AQI TB sinh viên Ngọc Quyên | PM2.5 TB sinh viên Tiến Sơn (µg/m³) | PM2.5 TB sinh viên Ngọc Quyên (µg/m³) |
| --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 78,00 | 79,05 | 23,38 | 22,92 |
| Hà Nội | 163,56 | 163,05 | 76,66 | 75,11 |
| Đà Nẵng | 35,44 | 35,37 | 6,38 | 6,46 |

Bảng dùng bộ báo cáo đã lưu gồm **27/57 lượt ghi Tuần 2**, lần lượt 9/19 mẫu mỗi đô thị. Nguồn: [city_statistics.csv](tuan_2/results/week2_analysis/city_statistics.csv); [raw đủ trường](tuan_2/results/week2_analysis/raw_week2_both_accounts.csv). Có 27 nhóm đô thị–giờ ở mỗi sinh viên và 21 nhóm cùng giờ dùng đối chiếu. Mẫu chỉ bao phủ hai ngày và chín giờ ở mỗi sinh viên.

Hà Nội có AQI trung bình cao nhất trong tập mẫu và các mẫu thuộc Unhealthy. TP. Hồ Chí Minh thuộc Moderate, Đà Nẵng thuộc Good. Mẫu Hà Nội thỏa ngưỡng cấu hình AQI/PM2.5; kết quả này không tự xác nhận SNS đã gửi hoặc người nhận đã nhận email ở từng quan trắc. Tương quan không chứng minh nguyên nhân ô nhiễm.

![AQI trung bình của bộ báo cáo đã lưu](tuan_2/results/week2_charts/02_aqi_city.png)

[27 CSV phân tích](tuan_2/results/week2_analysis/) · [20 hình và manifest nguồn](tuan_2/results/week2_charts/) · [SQL](tuan_2/athena/week2_analysis/) · [Danh mục CSV và hash](docs/csv_catalog.csv)

### Đối chiếu bằng phiên AWS mới

Ngày 16/10/2026, chúng em đọc lại cấu hình và chạy **14 SELECT** thành công, giữ riêng kết quả trong [thư mục kiểm chứng](tuan_2/results/review_2026_10_16/README.md). Bộ mới có 216/249 bản ghi toàn bộ, trong đó 39/75 thuộc Tuần 2. CSV cũ và 20 hình trên giữ nguyên mốc 27/57.

Hai Lambda Active; S3 bật mã hóa/chặn công khai; mỗi môi trường có sáu phân vùng Glue. Metadata có lịch, target, policy và số đăng ký SNS. Hai Alarm hiện thiếu dữ liệu; Errors lớn hơn Invocations nên chưa tính tỷ lệ lỗi. Đợt kiểm chứng không triển khai, đổi lịch hoặc gọi Lambda.

## 3 Mã nguồn và commit từng thành phần

[Chỉ mục thành phần](docs/components.md) cung cấp tệp và commit/lịch sử cho Lambda, EventBridge, S3, Secrets Manager, SNS, Glue, Athena, CloudWatch, exporter và phân tích/biểu đồ. Người đọc có thể mở code ngay trên GitHub và kiểm tra lịch sử thay đổi.

- [Lambda](tuan_2/lambda/lambda_function.py) · [commit sửa bộ thu thập](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/2947d3fdf7871ead2b99d486fa1d403a17183948)
- [SDK dịch vụ](tuan_2/scripts/aws_project.py) và [exporter](tuan_2/scripts/athena_export.py) · [commit sửa triển khai, xuất và phân tích](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/432add13545ff0af1fb86457ccaa1f295b796576)
- [DDL bảng](tuan_2/athena/create_table.sql), [view](tuan_2/athena/create_view_vietnam_weather_aqi.sql) và [SELECT Tuần 2](tuan_2/athena/week2_analysis/)
- [Hồ sơ AWS đã lưu](tuan_2/results/week2_evidence/) và [hồ sơ mới](tuan_2/results/review_2026_10_16/README.md) phân biệt mã hiện tại với phiên bản thực chạy.

## 4 Kế hoạch Tuần 3

[Kế hoạch tích hợp và giám sát](docs/WEEK_3_PLAN.md) gồm tám đầu việc W3-01 đến W3-08, có người phụ trách, thứ tự, sản phẩm dự kiến và tiêu chí hoàn thành. Trọng tâm là chốt phiên bản triển khai, kiểm chứng lịch/target, đối chiếu raw với phân vùng, xử lý giám sát và xác minh đường cảnh báo, sau đó cập nhật bảng/hình.

Đây là công việc dự kiến; chưa ghi giờ hoàn thành Tuần 3 hoặc coi các vấn đề giám sát là đã giải quyết.

## 5 Hồ sơ Tuần 1 và tiến độ liền mạch

[Hồ sơ Tuần 1](tuan_1/README.md) có mục tiêu, phần đã làm, phân công 18,5 giờ, bảng AQI ban đầu, sáu CSV, chín biểu đồ, SQL và kết luận. Bộ Tuần 1 có 156 bản ghi, 52/đô thị, gồm phần lịch sử nạp bổ sung. Tuần 2 đối chiếu với đúng bộ này và trình bày riêng phép lọc lại hai tuần từ lần xuất mới.

[Báo cáo chi tiết Tuần 1](tuan_1/docs/FINAL_REPORT.md) · [Báo cáo chi tiết Tuần 2](tuan_2/docs/FINAL_REPORT.md) · [Worklog tổng hợp](docs/WORKLOG.md)

## Nội dung ngắn khi dẫn repo trên hệ thống lớp

Chúng em bổ sung hồ sơ Tuần 2 trên GitHub gồm phân công và số giờ từng sinh viên, mô tả đầu vào và kết quả AQI, CSV/raw, mã nguồn và commit theo thành phần, cùng kế hoạch Tuần 3 về tích hợp và giám sát. Hồ sơ Tuần 1 được liên kết để theo dõi tiến độ. Đợt đọc AWS mới được lưu riêng với mã truy vấn và SHA-256; các giới hạn vận hành được trình bày tại từng mốc.

[Mở repository](https://github.com/JasonTM17/WeatherAWS_FinalTerm) · [Mở Tuần 1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1) · [Mở Tuần 2](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2)
