# Báo cáo tiến độ Tuần 3

**Nguyễn Tiến Sơn – MSSV 24110054; Trần Thị Ngọc Quyên – MSSV 24110051.**

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS (Domain Apps).

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng.

**Mốc tích hợp:** 18/10/2026 · **Cập nhật dữ liệu:** 19/10/2026, UTC+7.

## 1. Nội dung và kết quả thực hiện

Trong Tuần 3, chúng em đã hoàn thành các công việc tích hợp hệ thống, giám sát CloudWatch, kiểm chứng triển khai Lambda, thử nghiệm tối ưu truy vấn Athena và đánh giá dự báo theo giờ. Kết quả được tổ chức trên GitHub theo từng mốc dữ liệu, có liên kết từ báo cáo đến mã nguồn, raw, kết quả truy vấn, biểu đồ và nhật ký.

### Tích hợp, triển khai và cảnh báo

Luồng xử lý sử dụng EventBridge gọi Lambda theo lịch, thu thập dữ liệu Open-Meteo cho TP. Hồ Chí Minh, Hà Nội và Đà Nẵng, lưu raw trên S3, khai báo lược đồ bằng Glue và truy vấn bằng Athena. Nhánh thời gian thực phát cảnh báo qua SNS khi AQI hoặc PM2.5 thỏa ngưỡng cấu hình.

Chúng em đã chuẩn hóa gói triển khai Lambda và kiểm chứng hai lượt CD qua GitHub Actions ngày 18/10. Bản cập nhật cách lấy lịch sử ngày 19/10 được triển khai qua SDK trên hai môi trường, có sao lưu phiên bản trước, kiểm tra RevisionId và đọc lại hash, cấu hình sau cập nhật. Mã Lambda cập nhật ngày 19/10 khớp commit 62f1c08 tại mục 3; cấu hình ngưỡng và lịch được giữ nguyên trong lượt cập nhật mã này.

Dashboard và hai Metric Filters trong mỗi môi trường đã được kiểm tra mẫu, đọc lại cấu hình và đối chiếu với các điểm metric mới. Các lượt thu thập theo lịch được liên kết với log và bản ghi S3 theo cùng thời điểm. Hồ sơ cảnh báo ghi riêng điều kiện vượt ngưỡng, kết quả Publish, giao thông báo và xác nhận người nhận; hai sinh viên đã xác nhận email của các lượt theo lịch ngày 16/10.

### Dữ liệu raw và kiểm tra chất lượng

Bản xuất S3 chốt lúc **14:22–14:23 UTC+7 ngày 19/10/2026** có **302 bản ghi của sinh viên Tiến Sơn và 339 bản ghi của sinh viên Ngọc Quyên**, tổng cộng **641 bản ghi trong 95 tệp JSON gốc**. Riêng dữ liệu mang ngày 19/10 có lần lượt **45 và 42 bản ghi**.

Hai lượt Lambda ở chế độ lấy lịch sử đã thu bổ sung chuỗi mô hình **00:00–13:00 UTC+7**, mỗi lượt 42 bản ghi cho ba đô thị. Thống kê đối chiếu dùng cùng **14 giờ hoàn tất** cho mỗi sinh viên. Ba bản ghi trong giờ 14 của sinh viên Tiến Sơn được giữ trong raw, riêng với tập giờ hoàn tất. Chế độ lấy lịch sử được ghi trong nguồn từng bản ghi và có kết quả 0 cảnh báo lịch sử.

Hồ sơ lưu CSV đủ **23 trường**, JSON nguyên bản, thời điểm thu/xuất, danh mục object và SHA-256. Các kiểm tra cấu trúc, giá trị số, UTC/UTC+7, phân vùng và mã bản ghi đều đạt theo bảy nhóm kiểm tra đã khai báo. Dữ liệu lấy từ Open-Meteo; phần chất lượng không khí sử dụng nguồn mô hình CAMS.

### Truy vấn Athena và phân tích dữ liệu

Chúng em đã thực hiện **18 lượt đo**, gồm ba lần cho mỗi cấu hình trong mỗi môi trường: NDJSON có phân vùng đăng ký, NDJSON sử dụng Partition Projection và Parquet Snappy sử dụng Partition Projection. Các cấu hình được so sánh trên cùng bộ đầu vào đã chốt của từng môi trường. Chức năng sử dụng lại kết quả được tắt trong các lượt đo.

Trong phép đo này, Parquet giảm byte quét khoảng **80,59% đối với sinh viên Tiến Sơn và 96,50% đối với sinh viên Ngọc Quyên**. Thời gian engine và tổng thời gian được ghi riêng cho từng lượt, kèm SQL và query ID. Kích thước object cũng được tổng hợp để đánh giá cách lưu phục vụ Athena. Phần phân tích có thống kê mô tả, tương quan Pearson/Spearman và biểu đồ màu gắn với CSV nguồn.

### Dự báo và đối chiếu giá trị theo giờ

Chúng em đã đánh giá các phương pháp giá trị cuối, lặp 24 giờ trước và trung bình trượt 24 giờ; MA 3 giờ là phân tích bổ sung trên cùng tập giữ lại. Bản dự báo có thời điểm phát hành được lưu riêng; các giá trị đã phát hành được giữ nguyên khi đối chiếu với dữ liệu tải về sau.

Mốc cập nhật ngày 19/10 đã đối chiếu đủ **24/24 giờ đích, tương ứng 144/144 giá trị**, cho ba đô thị và hai chỉ số AQI, PM2.5. Kỳ đích từ **18/10 14:00 đến 19/10 13:00 UTC+7**; nguồn đối chiếu là giá trị mô hình CAMS tải về sau. MAE, RMSE và Bias được tính theo từng đô thị, chỉ số, kèm CSV, phản hồi nguồn và biểu đồ.

## 2. Phân công và thời gian thực hiện

- **Sinh viên Tiến Sơn: 10,0 giờ**, phụ trách thu thập, lưu trữ, cấu hình, triển khai Lambda, CloudWatch và cảnh báo SNS.
- **Sinh viên Ngọc Quyên: 10,0 giờ**, phụ trách Glue/Athena, xuất CSV, kiểm tra dữ liệu, thống kê, biểu đồ và dự báo.
- Hai sinh viên cùng tích hợp, đối chiếu minh chứng và hoàn thiện báo cáo. **Tổng thời gian Tuần 3 đã xác nhận: 20,0 giờ.**

Nhật ký Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/WORKLOG.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/WORKLOG.md).

## 3. Mã nguồn và commit minh chứng

- **Tích hợp dữ liệu, thử nghiệm Athena, Dashboard và dự báo – commit 0b26858:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e).

- **Chuẩn hóa gói Lambda giữa Windows/Linux, phục vụ triển khai – commit c28da19:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356).

- **Sửa cách lấy các giờ lịch sử đã hoàn tất của ngày hiện tại – commit 62f1c08:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650).

## 4. Liên kết báo cáo và minh chứng trực tiếp

- **Repository:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm).

- **Hồ sơ Tuần 3:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3).

- **Báo cáo Tuần 3 đầy đủ:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/FINAL_REPORT.md).

- **Raw, danh mục 95 JSON, CSV và biểu đồ cập nhật ngày 19/10:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19).

- **Kết quả thực nghiệm Athena và query ID:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/integration_2026_10_18/benchmark](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/integration_2026_10_18/benchmark).

- **Dashboard và kiểm chứng cấu hình CloudWatch:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/monitoring_dashboard_repair_2026_10_18](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/monitoring_dashboard_repair_2026_10_18).

- **Minh chứng chạy theo lịch và xác nhận email:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/scheduled-run-verification.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/scheduled-run-verification.md).

- **Kết quả đối chiếu đủ 24 giờ dự báo:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/forecast_followup_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/forecast_followup_2026_10_19).

- **Mã nguồn Lambda dùng chung:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py).

- **Workflow CI và các lượt kiểm tra:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml).

- **Hai lượt CD Lambda ngày 18/10 và kết quả đọc lại từ AWS:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/cd_2026_10_18](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/cd_2026_10_18).

## 5. Kế hoạch Tuần 4 và kết luận

Tuần 4, chúng em dự kiến tiếp tục theo dõi thu thập theo lịch, xuất dữ liệu theo ngày, đối chiếu log–metric–S3, kiểm chứng thêm cảnh báo email, đo Athena trên bộ dữ liệu mới và đánh giá thêm ba kỳ dự báo có thời điểm phát hành. Kế hoạch gồm tám đầu việc, có người phụ trách, sản phẩm dự kiến, thứ tự thực hiện và tiêu chí nghiệm thu.

Kế hoạch chi tiết: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_4_PLAN.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_4_PLAN.md).

**Chúng em đã hoàn thành kế hoạch công việc tích hợp Tuần 3 và bổ sung dữ liệu ngày 19/10. Hồ sơ liên kết trực tiếp kết quả với dữ liệu nguồn, chương trình xử lý, commit và nhật ký để giảng viên thuận tiện kiểm tra, đối chiếu.**
