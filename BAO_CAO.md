# Báo cáo tiến độ Tuần 3

**Nguyễn Tiến Sơn – MSSV 24110054; Trần Thị Ngọc Quyên – MSSV 24110051.**

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS, thuộc lĩnh vực Domain Apps.

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng.

**Mốc tích hợp:** 18/10/2026 · **Cập nhật dữ liệu và hồ sơ:** 19/10/2026, múi giờ Việt Nam (UTC+7).

## 1. Mục tiêu và phạm vi thực hiện

Trong Tuần 3, chúng em tập trung hoàn thiện luồng tích hợp, giám sát vận hành bằng CloudWatch, kiểm chứng cảnh báo email SNS và đồng bộ mã Lambda triển khai với repository. Đồng thời, chúng em thực nghiệm Partition Projection/Parquet trên Athena, bổ sung kiểm tra chất lượng dữ liệu và đánh giá dự báo AQI, PM2.5 theo giờ.

Hệ thống tiếp tục thu thập dữ liệu của TP. Hồ Chí Minh, Hà Nội và Đà Nẵng trong AWS Learner Lab tại vùng us-east-1. EventBridge kích hoạt Lambda theo lịch; Lambda đọc cấu hình từ Secrets Manager, gọi Open-Meteo, chuẩn hóa bản ghi và lưu trên S3. Glue Data Catalog cung cấp lược đồ để Athena truy vấn; các chương trình Python tạo bảng phân tích và biểu đồ. SNS xử lý cảnh báo theo ngưỡng, còn CloudWatch lưu log, metric và Dashboard phục vụ đối chiếu vận hành.

Hồ sơ tổng quan Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/README.md).

Kiến trúc và vai trò các dịch vụ: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/architecture.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/architecture.md).

## 2. Phân công trách nhiệm và thời gian thực hiện

**Sinh viên Tiến Sơn** phụ trách S3, Secrets Manager, Lambda, EventBridge, SNS và CloudWatch; tập trung đối chiếu phiên bản triển khai, lịch thu thập, cấu hình giám sát và luồng cảnh báo email. **Sinh viên Ngọc Quyên** phụ trách Glue/Athena, kiểm tra raw, xuất CSV, thống kê, thực nghiệm truy vấn, biểu đồ và dự báo. Hai sinh viên cùng tích hợp hệ thống, rà soát số liệu, kiểm tra liên kết minh chứng và hoàn thiện báo cáo.

Thời gian Tuần 3 đã được xác nhận của sinh viên Tiến Sơn là **10,0 giờ**, của sinh viên Ngọc Quyên là **10,0 giờ**, tổng cộng **20,0 giờ**. Nhật ký liên kết các công việc với sản phẩm và ghi tổng giờ theo tuần đã xác nhận.

Nhật ký công việc Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/WORKLOG.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/WORKLOG.md).

CSV tổng hợp thời gian Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/worklog.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/worklog.csv).

## 3. Mã nguồn và commit minh chứng

Mã Lambda được tổ chức theo các chức năng đọc cấu hình, gọi API, chuẩn hóa dữ liệu, phân loại AQI, kiểm tra ngưỡng và ghi S3. Bản ghi giữ thời gian UTC, giờ Việt Nam và thời điểm thu thập để phân biệt thời gian của dữ liệu với lúc chương trình xử lý. S3 sử dụng cấu trúc `raw/year=YYYY/month=MM/day=DD/` theo UTC; khi báo cáo theo ngày Việt Nam, chương trình chuyển ranh giới UTC+7 sang UTC trước khi lọc.

Phần lấy lịch sử ghép hai chuỗi thời tiết và chất lượng không khí theo timestamp, chọn đúng khoảng giờ được yêu cầu và chỉ đưa các giờ đã hoàn tất vào thống kê. Bản cập nhật ngày 19/10 bổ sung đúng dữ liệu của ngày UTC hiện tại. Kết quả xử lý ghi số bản ghi, object đã lưu và trạng thái của các đô thị để đối chiếu Lambda với S3. Cảnh báo SNS áp dụng ở nhánh thời gian thực; chế độ lịch sử lưu dữ liệu với kết quả 0 cảnh báo lịch sử.

Các chương trình Tuần 3 được tách theo nhiệm vụ: snapshot và chất lượng, benchmark Athena, Dashboard/Metric Filters, dự báo, tổng hợp dữ liệu theo ngày và kiểm tra minh chứng. Cách tổ chức này cho phép tính lại bảng từ CSV và truy từ biểu đồ về dữ liệu nguồn.

Mã nguồn Lambda dùng chung: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py).

Các chương trình Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/scripts](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/scripts).

Ba commit trực tiếp thể hiện các thay đổi chính:

- **0b26858 – tích hợp snapshot, thực nghiệm Athena, Dashboard và dự báo:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e).
- **c28da19 – chuẩn hóa gói Lambda giữa Windows/Linux, phục vụ triển khai:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356).
- **62f1c08 – cập nhật cách lấy các giờ lịch sử đã hoàn tất của ngày hiện tại:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650).

## 4. Quy mô dữ liệu raw và kiểm tra chất lượng

Bản xuất S3 ngày **19/10/2026**, chốt lúc **14:22–14:23 UTC+7**, lưu **302 bản ghi của sinh viên Tiến Sơn và 339 bản ghi của sinh viên Ngọc Quyên**, tổng cộng **641 bản ghi trong 95 tệp JSON gốc**. Trong đó, sinh viên Tiến Sơn có 43 tệp JSON, sinh viên Ngọc Quyên có 52 tệp. CSV giữ đủ 23 trường, gồm định danh, đô thị, tọa độ, thời gian, các chỉ số khí tượng/chất lượng không khí và khóa phân vùng.

Riêng dữ liệu mang ngày 19/10 theo UTC+7 có **45 bản ghi của sinh viên Tiến Sơn và 42 bản ghi của sinh viên Ngọc Quyên**. Hai lượt Lambda ở chế độ lấy lịch sử đã thu bổ sung chuỗi mô hình từ **00:00 đến 13:00**, mỗi lượt **14 giờ × 3 đô thị = 42 bản ghi**. Thống kê so sánh dùng cùng 14 giờ hoàn tất của mỗi sinh viên. Ba bản ghi trong giờ 14 của sinh viên Tiến Sơn được giữ riêng trong raw. Nguồn từng bản ghi phân biệt chế độ lấy lịch sử với các lượt thu khác.

Chúng em đối chiếu theo bảy nhóm kiểm tra: mã bản ghi, lược đồ, trường số bị thiếu, giá trị số không hợp lệ, UTC/UTC+7, phân vùng và thứ tự thời gian thu thập so với thời gian dữ liệu. Bản xuất của cả hai sinh viên đều đạt các kiểm tra đã khai báo. Mỗi object có đường dẫn, số dòng, thời điểm và SHA-256; toàn bộ bản ghi của bản xuất trước được bảo toàn.

Bản raw ngày 18/10 được giữ riêng với **534 bản ghi và 83 JSON gốc**. Các bảng, hình và lượt đo lịch sử vẫn liên kết với đúng bộ đầu vào tại mốc thực hiện.

Raw, CSV, JSON và thống kê cập nhật ngày 19/10: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19).

CSV ngày 19/10 của sinh viên Tiến Sơn: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/daily/default/raw_today.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/daily/default/raw_today.csv).

CSV ngày 19/10 của sinh viên Ngọc Quyên: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/daily/quyen/raw_today.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/daily/quyen/raw_today.csv).

## 5. Kết quả thống kê và biểu đồ

Chúng em tổng hợp theo đô thị–giờ để các giờ có cùng trọng số khi đối chiếu. CSV thống kê gồm trung bình, trung vị, độ lệch chuẩn mẫu, min/max và các phân vị; biểu đồ màu dùng trực tiếp bảng nguồn tương ứng. Dữ liệu chất lượng không khí sử dụng nguồn mô hình CAMS qua Open-Meteo, có lưu thời điểm tải.

Trong cùng 14 giờ hoàn tất ngày 19/10, AQI trung bình của TP. Hồ Chí Minh, Hà Nội và Đà Nẵng lần lượt là **55,857; 91,071; 47,143**. PM2.5 trung bình tương ứng là **11,557; 35,914; 13,086 µg/m³**. Các giá trị AQI và PM2.5 trung bình này bằng nhau trong hai bộ báo cáo dữ liệu do cùng nguồn mô hình, tọa độ và tập giờ đã lưu. Hà Nội có giá trị trung bình cao nhất trong ba đô thị ở mốc phân tích này.

Ví dụ tại **13:00 ngày 19/10**, raw của TP. Hồ Chí Minh ghi AQI 55, PM2.5 11,3 µg/m³; Hà Nội ghi AQI 96, PM2.5 23,5 µg/m³; Đà Nẵng ghi AQI 53, PM2.5 11,4 µg/m³. Đây là giá trị từng bản ghi tại một giờ, được trình bày riêng với trung bình 14 giờ ở trên.

Phần phân tích mốc 18/10 còn lưu **96 dòng thống kê mô tả và 120 dòng tương quan Pearson/Spearman**, có quy định rõ tập raw và tập đô thị–giờ. Các mốc dữ liệu được lưu riêng, phục vụ đối chiếu kết quả theo thời điểm.

Bảng thống kê, mẫu raw và biểu đồ ngày 19/10: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/README.md).

Thống kê và tương quan tại mốc 18/10: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/refresh_2026_10_18/analysis](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/refresh_2026_10_18/analysis).

## 6. Thực nghiệm Partition Projection và Parquet trên Athena

Chúng em thực hiện **18 lượt đo**, gồm ba lần cho mỗi cấu hình trong hai môi trường: NDJSON có phân vùng đăng ký, NDJSON dùng Partition Projection và Parquet Snappy dùng Partition Projection. Mỗi môi trường sử dụng cùng bộ raw đã chốt để tạo các định dạng thử nghiệm. Các bảng/prefix thử nghiệm được tách riêng; chức năng sử dụng lại kết quả bị tắt và thứ tự cấu hình được luân phiên giữa các lần đo.

Partition Projection xác định phân vùng từ cấu hình bảng, giảm phụ thuộc thao tác đăng ký metadata. Parquet tổ chức dữ liệu theo cột và nén Snappy để đánh giá lượng byte Athena cần đọc cho các cột được truy vấn. Chương trình đối chiếu kết quả SQL với tổng hợp từ CSV trước khi báo số đo.

Trong môi trường sinh viên Tiến Sơn, trung vị byte quét của NDJSON là **1.556 byte**, Parquet là **302 byte**, giảm **80,59%**; thời gian engine trung vị của NDJSON đăng ký phân vùng, NDJSON Projection và Parquet lần lượt là **615, 537 và 452 ms**. Trong môi trường sinh viên Ngọc Quyên, trung vị byte quét giảm từ **11.243 xuống 393 byte**, tương ứng **96,50%**; engine trung vị lần lượt là **572, 431 và 515 ms**.

Kết quả đánh giá riêng byte quét và thời gian cho từng cấu hình trong cùng môi trường. Với sinh viên Ngọc Quyên, NDJSON Projection có engine trung vị thấp hơn Parquet trong phép đo này. Báo cáo lưu từng lượt, ngày/số dòng được truy vấn, query ID và kết quả tổng hợp ba đô thị để kiểm tra lại.

Truy vấn, 18 lượt đo và kết quả: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/integration_2026_10_18/benchmark](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/integration_2026_10_18/benchmark).

Mã thực nghiệm Athena: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/scripts/benchmark.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/scripts/benchmark.py).

## 7. Giám sát CloudWatch và cảnh báo email SNS

Dashboard tổng hợp các chỉ số Lambda, SNS và lịch thu thập: số lượt gọi, Errors, Throttles, thời gian thực thi, số thông điệp và kết quả từ log. Hai Metric Filters trong mỗi môi trường đếm các dòng kết quả và dòng lỗi khớp mẫu; các chỉ số log được lưu riêng với native metric của dịch vụ.

Tỷ lệ lỗi dùng các cặp Errors/Invocations cùng hàm, dimension, timestamp UTC và chu kỳ 300 giây, với Invocations > 0 và Errors ≤ Invocations. Chúng em đã kiểm chứng biểu thức Dashboard qua sáu trường hợp trong mỗi môi trường, đọc lại cấu hình và lưu ảnh metric do AWS trả về. Các lượt thu thập theo lịch được đối chiếu theo request, số đô thị, số bản ghi và object S3.

Nhánh thời gian thực kiểm tra điều kiện **AQI ≥ ngưỡng AQI hoặc PM2.5 ≥ ngưỡng PM2.5**; giá trị mặc định trong mã là 100 và 35,5 µg/m³, ngưỡng thực thi được đọc từ cấu hình môi trường. Trong lượt tự động **13:51 UTC+7 ngày 18/10** của sinh viên Ngọc Quyên, Lambda thu đủ ba đô thị, S3 có đủ ba bản ghi và kết quả 0 cảnh báo khớp các mẫu dưới ngưỡng.

Minh chứng email được ghi đúng mốc kiểm chứng: các lượt theo lịch ngày **16/10**, khoảng **14:51 đối với sinh viên Ngọc Quyên và 15:15 đối với sinh viên Tiến Sơn**, mỗi lượt thu ba bản ghi và phát hai thông điệp SNS. Cả hai sinh viên đã xác nhận nhận email mới của các lượt này. Hồ sơ liên kết dữ liệu, log, metric SNS và xác nhận người nhận.

Dashboard và kiểm chứng cấu hình: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/monitoring_dashboard_repair_2026_10_18](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/monitoring_dashboard_repair_2026_10_18).

Lượt tự động ngày 18/10 của sinh viên Ngọc Quyên: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/post_repair_2026_10_18/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/post_repair_2026_10_18/README.md).

Luồng theo lịch và xác nhận email ngày 16/10: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/scheduled-run-verification.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/scheduled-run-verification.md).

## 8. Dự báo AQI, PM2.5 và đối chiếu đủ kỳ

Chúng em đánh giá ba phương pháp cơ sở: giữ giá trị cuối, lặp lại giá trị 24 giờ trước và trung bình trượt 24 giờ. MA 3 giờ được tính bổ sung trên cùng tập giữ lại. Các phương pháp có mã nguồn, bảng dự báo và MAE/RMSE/Bias để so sánh theo từng đô thị, chỉ số. Dự báo trung bình trượt sử dụng kết quả đệ quy cho các bước tiếp theo; giá trị đích được giữ riêng khỏi đầu vào.

Bản dự báo phát hành khoảng **06:24 UTC ngày 18/10** lưu **24 giờ đích × 3 đô thị × 2 chỉ số = 144 giá trị**. Kỳ đích từ **18/10 14:00 đến 19/10 13:00 UTC+7**. Đến mốc tải ngày 19/10, chúng em đã đối chiếu đủ **24/24 giờ đích và 144/144 giá trị** với nguồn mô hình CAMS tải về sau; bản dự báo phát hành được giữ nguyên cùng SHA-256.

MAE của AQI tại TP. Hồ Chí Minh, Hà Nội và Đà Nẵng lần lượt là **10,221; 11,031; 12,320 điểm**. MAE của PM2.5 tương ứng là **6,178; 6,619; 3,126 µg/m³**. CSV còn lưu RMSE và Bias; Bias được tính bằng trung bình của dự báo trừ giá trị mô hình tải về sau. Báo cáo gắn các sai số với đúng bản phát hành, nguồn dữ liệu và kỳ đích đã đối chiếu.

Bản dự báo phát hành gốc: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/forecast_issued_2026_10_18/forecast_24h.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/forecast_issued_2026_10_18/forecast_24h.csv).

144 giá trị đối chiếu, sai số và biểu đồ: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/forecast_followup_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/forecast_followup_2026_10_19).

## 9. Kiểm tra mã nguồn và quy trình CI/CD

Workflow CI tự động kiểm tra cấu trúc hồ sơ, CSV/worklog, chức năng thu thập, xử lý dữ liệu, phân tích, dự báo và quy trình phát hành; đồng thời tạo gói Lambda có thể đối chiếu bằng hash. Bộ hồ sơ dữ liệu ngày 19/10 có **57 trường hợp kiểm tra Tuần 3**, cùng đối chiếu **492 tệp minh chứng trong 14 manifest**. Các kiểm tra mã/tệp được lưu riêng với minh chứng thực thi AWS.

Workflow CD Lambda chạy thủ công trên main, yêu cầu chọn và xác nhận môi trường. Hai lượt CD ngày 18/10 thành công trên môi trường sinh viên Tiến Sơn và sinh viên Ngọc Quyên; gói tải lại từ AWS khớp artifact và cấu hình giữ nguyên. Lượt cập nhật qua SDK ngày 19/10 tiếp tục kiểm tra phiên bản, sao lưu và đọc lại hash/cấu hình cho commit 62f1c08. Nhật ký triển khai ghi riêng phương thức và thời điểm của từng lượt.

Workflow CI và các lượt kiểm tra: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml).

Hai lượt CD và minh chứng đọc lại từ AWS: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/cd_2026_10_18](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/cd_2026_10_18).

Hồ sơ cập nhật SDK ngày 19/10: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19/release](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19/release).

## 10. Kế hoạch Tuần 4 và kết luận

Tuần 4 tiếp tục theo dõi thu thập theo lịch trong các phiên Learner Lab, xuất raw theo ngày và đối chiếu log–metric–S3. Sinh viên Tiến Sơn phụ trách phiên bản triển khai, thu thập, CloudWatch và kiểm chứng cảnh báo email. Sinh viên Ngọc Quyên phụ trách chất lượng dữ liệu, Athena, thống kê, biểu đồ và các kỳ dự báo tiếp theo. Hai sinh viên cùng kiểm tra mã, nhật ký, liên kết và nội dung nộp.

Kế hoạch gồm tám đầu việc W4-01–W4-08, có phụ thuộc, sản phẩm và tiêu chí nghiệm thu. Mục tiêu phân tích gồm 18 lượt đo Athena trên bộ đầu vào mới và ba kỳ dự báo có thời điểm phát hành, mỗi kỳ 24 giờ đích. Lịch đề xuất **26/10–01/11/2026**; tiến độ, sản phẩm và giờ công được cập nhật theo công việc thực hiện và thông báo của giảng viên.

Kế hoạch Tuần 4: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_4_PLAN.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_4_PLAN.md).

**Chúng em đã hoàn thành kế hoạch công việc tích hợp Tuần 3 và bổ sung dữ liệu ngày 19/10.** Kết quả gồm raw/CSV có nguồn, thực nghiệm Athena, Dashboard và cảnh báo email theo mốc kiểm chứng, bản dự báo đã đối chiếu đủ kỳ, cùng hồ sơ CI/CD. Phân công và tổng 20,0 giờ được ghi trong worklog; các kết quả có liên kết tới mã nguồn, commit và tệp minh chứng để giảng viên thuận tiện kiểm tra.

**Các liên kết tổng hợp của hồ sơ:**

- **Repository:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm).
- **Báo cáo kỹ thuật Tuần 3 đầy đủ:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/FINAL_REPORT.md).
- **Mã nguồn và commit theo thành phần:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/components.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/components.md).
- **Danh mục minh chứng trực tiếp:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/EVIDENCE_INDEX.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/EVIDENCE_INDEX.md).
