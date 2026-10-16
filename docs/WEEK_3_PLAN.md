# Kế hoạch Tuần 3 Tích hợp và giám sát

## Mục tiêu và đầu vào

Hoàn thiện và kiểm chứng liên thông luồng **EventBridge → Lambda → S3 → Glue/Athena → Biểu đồ**, đồng thời chuẩn hóa hệ thống cảnh báo SNS và giám sát CloudWatch. Kế hoạch tiếp nối [Tuần 2](../tuan_2/README.md), [Báo cáo nộp lại](../BAO_CAO_NOP_LAI.md) và [đợt đọc AWS ngày 16/10](../tuan_2/results/review_2026_10_16/README.md).

Hiện tại hệ thống đã có hai hàm Lambda Active, S3 Data Lake phân vùng theo ngày, AWS Glue Catalog bảng 20 cột và bộ SQL Athena truy vấn thành công. Các mục tiêu kiểm chứng và tối ưu trong Tuần 3 tập trung vào 4 trụ cột chiến lược dưới đây.

## Bốn trụ cột chiến lược Tuần 3

1. **Trụ cột 1: Tích hợp CI/CD tự động hóa kiểm thử và kiểm tra chất lượng dữ liệu**:
   - Vận hành GitHub Actions CI tự động hóa kiểm thử 106 test cases (unit tests, analytics tests, e2e acceptance tests).
   - Kiểm tra tự động tính toàn vẹn dữ liệu: phát hiện schema drift, định dạng CSV hợp lệ, chống suy hao dữ liệu.
2. **Trụ cột 2: Tối ưu hóa hiệu năng Athena và chi phí S3 Data Lake**:
   - Triển khai **Partition Projection** trong AWS Glue/Athena để tối ưu hóa truy vấn thời gian thực, loại trừ thao tác quét metadata thủ công `MSCK REPAIR TABLE`.
   - Chuyển đổi dữ liệu thô NDJSON sang định dạng **Apache Parquet / ORC** nén Snappy theo cột giúp giảm 70–80% chi phí quét dữ liệu Athena.
   - Cấu hình chính sách vòng đời **S3 Intelligent-Tiering / Glacier Flexible Retrieval** tối ưu hóa chi phí lưu trữ dài hạn trong S3 Data Lake.
3. **Trụ cột 3: Nâng cấp cảnh báo đa kênh SNS và giám sát thời gian thực CloudWatch**:
   - Nâng cấp kênh cảnh báo Amazon SNS từ Email sang SMS và tích hợp Webhook tới kênh trao đổi nhóm (Slack / Discord).
   - Thiết lập CloudWatch Metric Filters và Custom Dashboard theo dõi trực quan các chỉ số vận hành thời gian thực: số lần gọi hàm (Invocations), tỷ lệ lỗi (Error Rate), thời lượng thực thi (Duration) và số lượng cảnh báo phát hành (NumberOfMessagesPublished).
4. **Trụ cột 4: Mở rộng phân tích dự báo chuỗi thời gian (Time-Series Forecasting)**:
   - Xây dựng mô hình thống kê dự báo chuỗi thời gian (ARIMA / Moving Average) cho chỉ số AQI và nồng độ PM2.5 theo từng giờ trong 24 giờ tiếp theo.
   - Đối chiếu sai số RMSE giữa dự báo và dữ liệu thực tế thu thập từ trạm.

## Phân công và thứ tự thực hiện (W3-01 đến W3-08)

| Mã việc | Công việc chi tiết | Trụ cột | Phụ trách chính | Sản phẩm dự kiến | Tiêu chí hoàn thành |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **W3-01** | Chốt phiên bản mã và cấu hình triển khai | Trụ cột 1 | Sinh viên Tiến Sơn | Commit, hash gói/hàm trước và sau triển khai | Xác định được phiên bản thực chạy, có cách khôi phục gói cũ, không công bố thông tin đăng nhập |
| **W3-02** | Tích hợp lịch với Lambda và dọn dẹp rule | Trụ cột 1 & 2 | Sinh viên Tiến Sơn | Bảng rule/target/policy và các lượt thực thi liên tiếp | Xác nhận lịch được chọn cho từng môi trường; giải thích và xử lý lịch thừa trước khi đánh giá mật độ mẫu |
| **W3-03** | Triển khai Partition Projection và Parquet trên S3/Athena | Trụ cột 2 | Sinh viên Ngọc Quyên | Bảng Glue Partition Projection, định dạng Parquet nén Snappy | Athena truy vấn không cần `MSCK REPAIR`, giảm 70-80% byte quét so với NDJSON |
| **W3-04** | Kiểm tra chất lượng và thời gian quan trắc | Trụ cột 1 & 4 | Sinh viên Ngọc Quyên | CSV chất lượng và thống kê theo đô thị–giờ | Phân biệt khóa record_id, UTC/UTC+7, NULL và các lượt cùng giờ; giữ raw đầy đủ |
| **W3-05** | Chuẩn hóa giám sát CloudWatch Dashboard thời gian thực | Trụ cột 3 | Sinh viên Tiến Sơn | CloudWatch Dashboard JSON, CSV metrics và ảnh chụp giao diện | Invocations/Errors dùng cùng namespace, dimensions, khoảng thời gian; hiển thị biểu đồ thời gian thực |
| **W3-06** | Kiểm chứng cảnh báo đa kênh SNS (Email + SMS/Webhook) | Trụ cột 3 | Sinh viên Tiến Sơn | Cấu hình Topic đa kênh, kết quả gửi thông báo thử nghiệm | Tách rõ vượt ngưỡng, SNS nhận Publish và người nhận đã nhận thư/tin nhắn; thử có kiểm soát trong Lab |
| **W3-07** | Mở rộng mô hình dự báo chuỗi thời gian AQI/PM2.5 | Trụ cột 4 | Sinh viên Ngọc Quyên | Script dự báo time-series, CSV dự báo và 4 biểu đồ so khớp | Biểu đồ dự báo so khớp với thực nghiệm, tính toán sai số RMSE cho 24 giờ tiếp theo |
| **W3-08** | Tích hợp CI/CD tự động và rà soát hồ sơ repo GitHub | Trụ cột 1 | Cả hai sinh viên | Pipeline GitHub Actions hoàn thiện và README Tuần 3 | Mở được mã, dữ liệu và commit từng phần; 106 bài kiểm thử chạy tự động đạt 100% PASS trên CI |

Hai sinh viên phối hợp đối chiếu ở tất cả đầu việc. W3-01 và W3-02 đi trước W3-03; W3-03 cung cấp đầu vào cho W3-04/W3-07. W3-05 và W3-06 theo dõi cùng phiên bản triển khai. W3-08 tổng hợp sau khi các kết quả được đối chiếu.

## Điều kiện và hồ sơ kết thúc

- Thực hiện trong phiên AWS Learner Lab còn hiệu lực. Lịch bật không chứng minh hệ thống chạy liên tục khi Lab ngừng hoạt động.
- Lưu dữ liệu mới vào thư mục riêng theo mốc; giữ nguyên CSV Tuần 1 và Tuần 2 đã dùng trong báo cáo.
- Trước khi cập nhật hạ tầng, lưu phiên bản/cấu hình cũ để khôi phục. Ghi mọi lần triển khai, đổi lịch và thử thông báo vào nhật ký thực tế.
- Chạy kiểm tra theo [hướng dẫn mã nguồn](source-guide.md), sau đó kiểm tra riêng luồng trên AWS. Kiểm tra giả lập không thay thế dịch vụ thật.
- Chưa ghi giờ hoàn thành Tuần 3. Khi thực hiện, bổ sung số giờ thực tế, commit, CSV, hình giám sát và những việc chưa giải quyết.

Hồ sơ kết thúc ghi kết quả W3-01 đến W3-08, phân công/số giờ, raw và CSV tổng hợp, cấu hình đã loại thông tin riêng tư, commit triển khai và các giới hạn còn lại. Chỉ đánh dấu hoàn thành khi có minh chứng tương ứng.

[Báo cáo nộp lại](../BAO_CAO_NOP_LAI.md) · [Nhật ký hai tuần](WORKLOG.md) · [Mã nguồn theo thành phần](components.md) · [Vận hành](operation.md)
