# Báo cáo tiến độ Tuần 3

**Nguyễn Tiến Sơn – MSSV 24110054; Trần Thị Ngọc Quyên – MSSV 24110051.**

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS, thuộc lĩnh vực Domain Apps.

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng.

**Mốc tích hợp:** 18/10/2026 · **Cập nhật dữ liệu và hồ sơ:** 19/10/2026.

## 1. Mục tiêu và phạm vi thực hiện

Trên cơ sở kết quả của hai tuần đầu, Tuần 3 tập trung hoàn thiện việc tích hợp các thành phần của hệ thống, đồng bộ mã nguồn triển khai, bổ sung giám sát CloudWatch và đối chiếu luồng cảnh báo email qua SNS. Song song với phần vận hành, chúng em thực nghiệm Partition Projection/Parquet trên Athena, kiểm tra chất lượng dữ liệu và đánh giá dự báo AQI, PM2.5 theo giờ.

Hệ thống được triển khai trong AWS Learner Lab tại vùng `us-east-1`, phục vụ thu thập dữ liệu của TP. Hồ Chí Minh, Hà Nội và Đà Nẵng. EventBridge kích hoạt Lambda theo lịch; Lambda đọc cấu hình từ Secrets Manager, gọi API Open-Meteo, chuẩn hóa kết quả và lưu dữ liệu gốc trên S3. Glue Data Catalog quản lý lược đồ để Athena truy vấn. Các chương trình Python thực hiện kiểm tra, tổng hợp số liệu và xây dựng biểu đồ; SNS và CloudWatch đảm nhiệm cảnh báo, ghi nhận nhật ký và giám sát.

Các thao tác quản lý tài nguyên, triển khai Lambda, đọc dữ liệu S3 và thực thi truy vấn Athena được thực hiện qua Python SDK Boto3. Các tệp PowerShell là điểm vào gọi chương trình Python tương ứng. Mã nguồn, hướng dẫn vận hành và minh chứng triển khai cùng sử dụng phương thức này.

Hồ sơ tổng quan Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/README.md).

Kiến trúc và vai trò các dịch vụ: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/architecture.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/architecture.md).

## 2. Phân công trách nhiệm và thời gian thực hiện

**Sinh viên Tiến Sơn** phụ trách S3, Secrets Manager, Lambda, EventBridge, SNS và CloudWatch. Công việc trọng tâm gồm kiểm tra phiên bản triển khai, đối chiếu lịch thu thập, cấu hình giám sát và kiểm chứng luồng cảnh báo email.

**Sinh viên Ngọc Quyên** phụ trách Glue, Athena, kiểm tra dữ liệu gốc, xuất CSV, phân tích thống kê, thực nghiệm truy vấn, xây dựng biểu đồ và đánh giá dự báo. Hai sinh viên phối hợp tích hợp hệ thống, đối chiếu kết quả, rà soát minh chứng và hoàn thiện báo cáo.

Thời gian Tuần 3 đã được xác nhận của sinh viên Tiến Sơn là **10,0 giờ**, của sinh viên Ngọc Quyên là **10,0 giờ**, tổng cộng **20,0 giờ**. Nhật ký liên kết các công việc với sản phẩm và ghi tổng giờ theo tuần đã xác nhận.

Nhật ký công việc Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/WORKLOG.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/WORKLOG.md).

CSV tổng hợp thời gian Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/worklog.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/worklog.csv).

## 3. Mã nguồn và commit minh chứng

Mã Lambda được tổ chức theo các chức năng đọc cấu hình, gọi API, chuẩn hóa dữ liệu, phân loại AQI, kiểm tra ngưỡng và ghi S3. Bản ghi giữ thời gian UTC, giờ Việt Nam và thời điểm thu thập để phân biệt thời gian của dữ liệu với lúc chương trình xử lý. S3 sử dụng cấu trúc `raw/year=YYYY/month=MM/day=DD/` theo UTC; khi báo cáo theo ngày Việt Nam, chương trình chuyển ranh giới UTC+7 sang UTC trước khi lọc.

Phần lấy lịch sử ghép hai chuỗi thời tiết và chất lượng không khí theo timestamp, chọn đúng khoảng giờ được yêu cầu và chỉ đưa các giờ đã hoàn tất vào thống kê. Bản cập nhật ngày 19/10 bổ sung đúng dữ liệu của ngày UTC hiện tại. Kết quả xử lý ghi số bản ghi, object đã lưu và trạng thái của các đô thị để đối chiếu Lambda với S3. Cảnh báo SNS áp dụng ở nhánh thời gian thực; chế độ lịch sử lưu dữ liệu với kết quả 0 cảnh báo lịch sử.

Các chương trình Tuần 3 được tổ chức theo nhiệm vụ: xuất dữ liệu và kiểm tra chất lượng, thực nghiệm Athena, cấu hình Dashboard/Metric Filters, dự báo, tổng hợp dữ liệu theo ngày và xác minh hồ sơ. Cách tổ chức này giúp xác định chương trình tạo từng đầu ra, tính lại bảng từ CSV và đối chiếu biểu đồ với dữ liệu nguồn.

Mã nguồn Lambda dùng chung: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py).

Các chương trình Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/scripts](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/scripts).

Ba commit trực tiếp thể hiện các thay đổi chính:

- **0b26858 — `feat(week3): add measured Athena experiments, monitoring and guarded CD`:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e).
- **c28da19 — `fix(cd): make Lambda archive identical across Windows and Linux`:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356).
- **62f1c08 — `fix(lambda): collect completed current-day hours in backfill`:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650).

## 4. Quy mô dữ liệu raw và kiểm tra chất lượng

Bản xuất S3 cập nhật ngày **19/10/2026** lưu **302 bản ghi của sinh viên Tiến Sơn và 339 bản ghi của sinh viên Ngọc Quyên**, tổng cộng **641 bản ghi trong 95 tệp JSON gốc**. Trong đó, sinh viên Tiến Sơn có 43 tệp JSON, sinh viên Ngọc Quyên có 52 tệp. CSV giữ đủ 23 trường, gồm định danh, đô thị, tọa độ, thời gian, các chỉ số khí tượng, chất lượng không khí và khóa phân vùng.

Tính đến lần xuất dữ liệu ngày 19/10, các bản ghi mang ngày này theo UTC+7 gồm **45 bản ghi của sinh viên Tiến Sơn và 42 bản ghi của sinh viên Ngọc Quyên**. Hai lượt Lambda ở chế độ lấy lịch sử đã thu bổ sung các giờ hoàn tất trong ngày, mỗi lượt **14 giờ × 3 đô thị = 42 bản ghi**. Thống kê so sánh dùng cùng 14 giờ hoàn tất của mỗi sinh viên. Ba bản ghi thuộc giờ đang diễn ra của sinh viên Tiến Sơn được giữ riêng trong raw. Nguồn từng bản ghi phân biệt chế độ lấy lịch sử với các lượt thu khác.

Chúng em đối chiếu theo bảy nhóm kiểm tra: mã bản ghi, lược đồ, trường số bị thiếu, giá trị số không hợp lệ, UTC/UTC+7, phân vùng và thứ tự thời gian thu thập so với thời gian dữ liệu. Bản xuất của cả hai sinh viên đều đạt các kiểm tra đã khai báo. Mỗi object có đường dẫn, số dòng, thời điểm và SHA-256; toàn bộ bản ghi của bản xuất trước được bảo toàn.

Bản raw ngày 18/10 được giữ riêng với **534 bản ghi và 83 JSON gốc**. Các bảng, hình và lượt đo lịch sử vẫn liên kết với đúng bộ đầu vào tại mốc thực hiện.

Raw, CSV, JSON và thống kê cập nhật ngày 19/10: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19).

CSV ngày 19/10 của sinh viên Tiến Sơn: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/daily/default/raw_today.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/daily/default/raw_today.csv).

CSV ngày 19/10 của sinh viên Ngọc Quyên: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/daily/quyen/raw_today.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/daily/quyen/raw_today.csv).

## 5. Kết quả thống kê và biểu đồ

Chúng em tổng hợp theo đô thị–giờ để các giờ có cùng trọng số khi đối chiếu. CSV thống kê gồm trung bình, trung vị, độ lệch chuẩn mẫu, min/max và các phân vị; biểu đồ màu dùng trực tiếp bảng nguồn tương ứng. Dữ liệu chất lượng không khí sử dụng nguồn mô hình CAMS qua Open-Meteo, có lưu thời điểm tải.

Trong cùng 14 giờ hoàn tất ngày 19/10, AQI trung bình của TP. Hồ Chí Minh, Hà Nội và Đà Nẵng lần lượt là **55,857; 91,071; 47,143**. PM2.5 trung bình tương ứng là **11,557; 35,914; 13,086 µg/m³**. Các giá trị AQI và PM2.5 trung bình này bằng nhau trong hai bộ báo cáo dữ liệu do cùng nguồn mô hình, tọa độ và tập giờ đã lưu. Hà Nội có giá trị trung bình cao nhất trong ba đô thị ở mốc phân tích này.

Một số bản ghi minh họa ngày **19/10** ghi nhận TP. Hồ Chí Minh có AQI 55, PM2.5 11,3 µg/m³; Hà Nội có AQI 96, PM2.5 23,5 µg/m³; Đà Nẵng có AQI 53, PM2.5 11,4 µg/m³. Đây là giá trị của các bản ghi tại một thời điểm, được trình bày riêng với trung bình 14 giờ ở trên.

Phần phân tích tại mốc ngày 18/10 lưu **96 dòng thống kê mô tả và 120 dòng tương quan Pearson/Spearman**, phân biệt tập bản ghi gốc với tập tổng hợp theo đô thị–giờ. Các kết quả và biểu đồ được giữ theo đúng bộ đầu vào tương ứng.

Bảng thống kê, mẫu raw và biểu đồ ngày 19/10: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/README.md).

Thống kê và tương quan tại mốc 18/10: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/refresh_2026_10_18/analysis](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/refresh_2026_10_18/analysis).

## 6. Thực nghiệm Partition Projection và Parquet trên Athena

Chúng em thực hiện **18 lượt đo**, gồm ba lần cho mỗi cấu hình trong hai môi trường: NDJSON có phân vùng đăng ký, NDJSON dùng Partition Projection và Parquet Snappy dùng Partition Projection. Các cấu hình trong mỗi môi trường được so sánh trên cùng bộ dữ liệu đã chốt. Bảng và vị trí lưu dữ liệu thử nghiệm được tách riêng; chức năng sử dụng lại kết quả được tắt và thứ tự cấu hình được luân phiên giữa các lần đo.

Partition Projection xác định phân vùng từ cấu hình bảng, giảm phụ thuộc thao tác đăng ký metadata. Parquet tổ chức dữ liệu theo cột và nén Snappy để đánh giá lượng byte Athena cần đọc cho các cột được truy vấn. Chương trình đối chiếu kết quả SQL với tổng hợp từ CSV trước khi báo số đo.

Trong môi trường sinh viên Tiến Sơn, trung vị byte quét của NDJSON là **1.556 byte**, Parquet là **302 byte**, giảm **80,59%**; thời gian engine trung vị của NDJSON đăng ký phân vùng, NDJSON Projection và Parquet lần lượt là **615, 537 và 452 ms**. Trong môi trường sinh viên Ngọc Quyên, trung vị byte quét giảm từ **11.243 xuống 393 byte**, tương ứng **96,50%**; engine trung vị lần lượt là **572, 431 và 515 ms**.

Kết quả đánh giá riêng byte quét và thời gian cho từng cấu hình trong cùng môi trường. Với sinh viên Ngọc Quyên, NDJSON Projection có engine trung vị thấp hơn Parquet trong phép đo này. Báo cáo lưu từng lượt, ngày/số dòng được truy vấn, query ID và kết quả tổng hợp ba đô thị để kiểm tra lại.

Truy vấn, 18 lượt đo và kết quả: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/integration_2026_10_18/benchmark](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/integration_2026_10_18/benchmark).

Mã thực nghiệm Athena: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/scripts/benchmark.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/scripts/benchmark.py).

## 7. Giám sát CloudWatch và cảnh báo email SNS

CloudWatch Dashboard tổng hợp số lượt gọi Lambda, lỗi, lượt bị giới hạn thực thi, thời gian xử lý, thông điệp SNS và các chỉ số từ nhật ký. Hai Metric Filters trong mỗi môi trường ghi nhận các dòng kết quả và dòng lỗi khớp mẫu, phục vụ đối chiếu với chỉ số của dịch vụ.

Tỷ lệ lỗi dùng các cặp Errors/Invocations cùng hàm, dimension, timestamp UTC và chu kỳ 300 giây, với Invocations > 0 và Errors ≤ Invocations. Chúng em đã kiểm chứng biểu thức Dashboard qua sáu trường hợp trong mỗi môi trường, đọc lại cấu hình và lưu ảnh metric do AWS trả về. Các lượt thu thập theo lịch được đối chiếu theo request, số đô thị, số bản ghi và object S3.

Nhánh thời gian thực kiểm tra điều kiện **AQI ≥ ngưỡng AQI hoặc PM2.5 ≥ ngưỡng PM2.5**; giá trị mặc định trong mã là 100 và 35,5 µg/m³, ngưỡng thực thi được đọc từ cấu hình môi trường. Trong một lượt tự động ngày **18/10** của sinh viên Ngọc Quyên, Lambda thu đủ ba đô thị, S3 có đủ ba bản ghi và kết quả 0 cảnh báo khớp các mẫu dưới ngưỡng.

Minh chứng email được ghi theo các lượt kiểm chứng ngày **16/10** của sinh viên Tiến Sơn và sinh viên Ngọc Quyên. Mỗi lượt thu ba bản ghi và phát hai thông điệp SNS. Cả hai sinh viên đã xác nhận nhận email mới của các lượt này. Hồ sơ liên kết dữ liệu, log, metric SNS và xác nhận người nhận.

Dashboard và kiểm chứng cấu hình: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/monitoring_dashboard_repair_2026_10_18](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/monitoring_dashboard_repair_2026_10_18).

Lượt tự động ngày 18/10 của sinh viên Ngọc Quyên: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/post_repair_2026_10_18/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/post_repair_2026_10_18/README.md).

Luồng theo lịch và xác nhận email ngày 16/10: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/scheduled-run-verification.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/scheduled-run-verification.md).

## 8. Dự báo AQI, PM2.5 và đối chiếu đủ kỳ

Chúng em đánh giá ba phương pháp cơ sở: giữ giá trị cuối, lặp lại giá trị 24 giờ trước và trung bình trượt 24 giờ. MA 3 giờ được tính bổ sung trên cùng tập giữ lại. Các phương pháp có mã nguồn, bảng dự báo và MAE/RMSE/Bias để so sánh theo từng đô thị, chỉ số. Dự báo trung bình trượt sử dụng kết quả đệ quy cho các bước tiếp theo; giá trị đích được giữ riêng khỏi đầu vào.

Bản dự báo phát hành ngày **18/10** gồm **144 giá trị**, tương ứng **24 giờ đích × 3 đô thị × 2 chỉ số**. Các giờ đích thuộc ngày **18/10 và 19/10**. Đến mốc cập nhật ngày **19/10**, chúng em đã đối chiếu đủ **24/24 giờ đích và 144/144 giá trị** với dữ liệu mô hình CAMS tải về sau. Bản dự báo phát hành được giữ nguyên và kiểm tra bằng SHA-256.

MAE của AQI tại TP. Hồ Chí Minh, Hà Nội và Đà Nẵng lần lượt là **10,221; 11,031; 12,320 điểm**. MAE của PM2.5 tương ứng là **6,178; 6,619; 3,126 µg/m³**. CSV còn lưu RMSE và Bias; Bias được tính bằng trung bình của dự báo trừ giá trị mô hình tải về sau. Báo cáo gắn các sai số với đúng bản phát hành, nguồn dữ liệu và kỳ đích đã đối chiếu.

Bản dự báo phát hành gốc: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/forecast_issued_2026_10_18/forecast_24h.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/forecast_issued_2026_10_18/forecast_24h.csv).

144 giá trị đối chiếu, sai số và biểu đồ: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/forecast_followup_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/forecast_followup_2026_10_19).

## 9. Kiểm tra mã nguồn và quy trình CI/CD

Quy trình CI kiểm tra cấu trúc hồ sơ, CSV, worklog, chức năng thu thập, xử lý dữ liệu, phân tích, dự báo và quy trình phát hành; đồng thời tạo gói Lambda có thể đối chiếu bằng hash. Bộ hồ sơ dữ liệu ngày 19/10 có **57 trường hợp kiểm tra Tuần 3**, cùng đối chiếu **492 tệp minh chứng trong 14 manifest**. Kết quả kiểm tra mã nguồn và tệp dữ liệu được lưu riêng với minh chứng thực thi trên AWS.

Workflow CD Lambda chạy thủ công trên main, yêu cầu chọn và xác nhận môi trường. Hai lượt CD ngày 18/10 thành công trên môi trường sinh viên Tiến Sơn và sinh viên Ngọc Quyên; gói tải lại từ AWS khớp artifact và cấu hình giữ nguyên. Lượt cập nhật qua SDK ngày 19/10 tiếp tục kiểm tra phiên bản, sao lưu và đọc lại hash/cấu hình cho commit 62f1c08. Nhật ký triển khai ghi riêng phương thức và thời điểm của từng lượt.

Workflow CI và các lượt kiểm tra: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml).

Hai lượt CD và minh chứng đọc lại từ AWS: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/cd_2026_10_18](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/cd_2026_10_18).

Hồ sơ cập nhật SDK ngày 19/10: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19/release](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19/release).

## 10. Hoàn thành Tuần 4 và Tổng kết Toàn diện Đồ án

Trong Tuần 4 (tuần cuối cùng của đồ án), hai sinh viên đã bám sát kế hoạch W4-01–W4-08 và hoàn thành xuất sắc toàn bộ mục tiêu đề ra cùng các **yêu cầu nâng cao** theo đúng nhận xét của ThS. Huỳnh Xuân Phụng:

1. **Hạ tầng tự động hóa IaC CloudFormation:** Đóng gói toàn bộ kiến trúc Serverless bằng một mẫu CloudFormation chuẩn hóa ([`tuan_4/iac/cloudformation_stack.yaml`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/iac/cloudformation_stack.yaml)), tự động khởi tạo đồng bộ 16 tài nguyên AWS (S3 Data Lake AES-256, Secrets Manager, SNS, Lambda Python 3.12, EventBridge Schedule, Glue Catalog Database, Athena Table Partition Projection, CloudWatch Metric Filters, Alarms và Dashboard). Đã kiểm thử 100% PASS qua `test_cloudformation.py`.
2. **Rà soát An toàn Thông tin (Security Audit):** Rà soát chuyên sâu 11 kiểm soát bảo mật theo AWS Well-Architected Security ([`tuan_4/docs/SECURITY_AUDIT.md`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md)). Bật 100% S3 Block Public Access, Bucket Policy từ chối non-TLS (`aws:SecureTransport: false`), phân tích quyền hạn của IAM LabRole và thiết lập chính sách quyền tối thiểu chuẩn mực `collector-policy.example.json`.
3. **Đối chiếu 3 chiều Log – Metric – S3:** Kiểm chứng 14 phiên kích hoạt hoàn tất, tỷ lệ khớp đạt 100.0%, 0 tệp S3 mồ côi và 0 lượt gọi ảo ([`tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md)).
4. **Báo cáo Chi phí AWS Cost Explorer & FinOps:** Tính toán chi tiết chi phí từng dịch vụ trong AWS Learner Lab, tổng chi phí thực tế chỉ **$0.4037 USD / tháng** (tiêu tốn chưa tới 2.5% ngân sách $50 của Lab trong cả học kỳ) ([`tuan_4/docs/COST_REPORT.md`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md)).
5. **Kịch bản Vòng đời Tài nguyên:** Phát triển kịch bản `cleanup_resources.ps1` và `start_resources.ps1` phối hợp cùng `session_control.py` để tạm dừng EventBridge Rule ngoài giờ lab nhằm bảo tồn credit.
6. **Kịch bản Video Demo dưới 10 phút:** Xây dựng kịch bản ghi hình chi tiết từng phút (9 phút 45 giây) tại [`tuan_4/docs/VIDEO_DEMO_SCRIPT.md`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/VIDEO_DEMO_SCRIPT.md) với phân công lời thoại và thao tác màn hình cụ thể cho từng sinh viên.
7. **Đồng bộ Commit Message nguyên bản:** Toàn bộ liên kết commit trong báo cáo và repository được ghi kèm message thật theo đúng hướng dẫn của Thầy.
8. **Tổng thời gian thực hiện toàn bộ đồ án:** Đã được hai sinh viên xác nhận chính thức là **78,0 giờ** (Tuần 1: 18,5h; Tuần 2: 19,5h; Tuần 3: 20,0h; Tuần 4: 20,0h).

**Các liên kết tổng hợp của hồ sơ đồ án:**

- **Repository chính thức:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm).
- **Hồ sơ tổng kết Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/README.md).
- **Báo cáo kỹ thuật Tuần 4 đầy đủ:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md).
- **Hạ tầng CloudFormation IaC:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/iac/cloudformation_stack.yaml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/iac/cloudformation_stack.yaml).
- **Báo cáo Rà soát An toàn (Security Audit):** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md).
- **Báo cáo Chi phí AWS Cost Explorer:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md).
- **Đối chiếu Log – Metric – S3 Data Lake:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md).
- **Kịch bản Video Demo (<10 phút):** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/VIDEO_DEMO_SCRIPT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/VIDEO_DEMO_SCRIPT.md).
- **Nhật ký thời gian toàn đồ án (78.0h):** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv).
- **Báo cáo kỹ thuật Tuần 3:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/FINAL_REPORT.md).
- **Commit tổng kết Tuần 4 — `e497754` (`feat(week4): implement CloudFormation IaC, security audit, log-metric-S3 reconciliation, and video demo script`):** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e49775409593296fbe14ed0474e4e5cb2f930c36](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e49775409593296fbe14ed0474e4e5cb2f930c36).
