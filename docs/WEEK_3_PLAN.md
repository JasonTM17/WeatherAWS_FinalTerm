# Kế hoạch Tuần 3 Tích hợp và giám sát

## Mục tiêu và đầu vào

Hoàn thiện và kiểm chứng liên thông luồng **EventBridge → Lambda → S3 → Glue/Athena → Biểu đồ**, đồng thời chuẩn hóa hệ thống cảnh báo SNS và giám sát CloudWatch. Kế hoạch tiếp nối [Tuần 2](../tuan_2/README.md), [Báo cáo nộp lại](../BAO_CAO.md) và [đợt đọc AWS ngày 16/10](../tuan_2/results/review_2026_10_16/README.md).

Đợt kiểm chứng ngày 16/10/2026 ghi nhận hai hàm Lambda ở trạng thái Active, S3 Data Lake phân vùng theo ngày, AWS Glue Catalog bảng 20 cột và các truy vấn Athena thành công. Các mục tiêu kiểm chứng và tối ưu trong Tuần 3 tập trung vào 4 trụ cột dưới đây.

## Hai hạng mục ưu tiên và kết quả bổ sung

Theo góp ý của giảng viên, ưu tiên trước hết là đồng bộ mã Lambda đang chạy với repository và kiểm chứng cảnh báo SNS tới email người nhận. Đợt triển khai và theo dõi ngày 16/10 đã có kết quả cho cả hai hạng mục:

| Ưu tiên | Kết quả đã kiểm chứng | Minh chứng mở trực tiếp |
| --- | --- | --- |
| Đồng bộ mã thực chạy | Cả hai module Lambda tải lại từ AWS khớp source commit `36c9b39`; cấu hình hàm được giữ nguyên, gói cũ được sao lưu cục bộ | [Triển khai và hash](deployment-verification.md) · [JSON](../tuan_2/results/deployment_2026_10_16/verification.json) |
| Cảnh báo tới email | Mỗi môi trường có một lượt theo lịch thu ba bản ghi, phát hai thông điệp SNS; metric ghi nhận giao thông báo và người nhận xác nhận email mới | [Lượt chạy tự động](scheduled-run-verification.md) · [JSON](../tuan_2/results/scheduled_verification_2026_10_16/verification.json) |

**Đã hoàn thành kế hoạch công việc tích hợp Tuần 3 tại mốc ngày 18/10/2026.** Các sản phẩm và phạm vi kiểm chứng của W3-01–W3-08 được đối chiếu bên dưới. Dữ liệu vận hành được tiếp tục lưu theo timestamp để đánh giá độ phủ, sai số ở những giờ đích tiếp theo và các điểm metric cần làm rõ.

## Bốn trụ cột chiến lược Tuần 3

1. **Trụ cột 1: Tích hợp CI/CD tự động hóa kiểm thử và kiểm tra chất lượng dữ liệu**:
   - Duy trì GitHub Actions để chạy kiểm tra hồ sơ, bộ kiểm thử chức năng và bộ kiểm thử phân tích đang được khai báo trong workflow.
   - Kiểm tra tự động tính toàn vẹn dữ liệu: phát hiện schema drift, định dạng CSV hợp lệ, chống suy hao dữ liệu.
2. **Trụ cột 2: Tối ưu hóa hiệu năng Athena và chi phí S3 Data Lake**:
   - Triển khai **Partition Projection** trong AWS Glue/Athena để tối ưu hóa truy vấn thời gian thực, loại trừ thao tác quét metadata thủ công `MSCK REPAIR TABLE`.
   - Thử nghiệm định dạng cột như **Apache Parquet** với cấu hình nén phù hợp; so sánh lượng dữ liệu quét và thời gian xử lý với NDJSON trên cùng truy vấn và tập dữ liệu trước khi kết luận về chi phí.
   - Đánh giá chính sách vòng đời dựa trên kích thước object, lịch truy cập và yêu cầu lưu giữ. Chưa đổi lifecycle raw sản xuất khi chưa đủ căn cứ dự toán phí chuyển tầng/khôi phục.
3. **Trụ cột 3: Kiểm chứng cảnh báo email SNS và giám sát CloudWatch**:
   - Giữ kênh email theo phạm vi đã thống nhất; kiểm chứng SNS nhận thông điệp, số metric giao thông báo và xác nhận người nhận riêng biệt.
   - Thiết lập CloudWatch Metric Filters và Custom Dashboard theo dõi trực quan các chỉ số vận hành thời gian thực: số lần gọi hàm (Invocations), tỷ lệ lỗi (Error Rate), thời lượng thực thi (Duration) và số lượng cảnh báo phát hành (NumberOfMessagesPublished).
4. **Trụ cột 4: Mở rộng phân tích dự báo chuỗi thời gian (Time-Series Forecasting)**:
   - Xây dựng mô hình thống kê dự báo chuỗi thời gian (ARIMA / Moving Average) cho chỉ số AQI và nồng độ PM2.5 theo từng giờ trong 24 giờ tiếp theo.
   - Đánh giá sai số trên khoảng thời gian không dùng để xây dựng dự báo; nêu rõ dữ liệu lấy từ Open-Meteo là dữ liệu mô hình, không phải số đo trực tiếp tại trạm.

## Phân công và thứ tự thực hiện (W3-01 đến W3-08)

| Mã việc | Công việc chi tiết | Trụ cột | Phụ trách chính | Sản phẩm dự kiến | Tiêu chí hoàn thành |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **W3-01** | Chốt phiên bản mã và cấu hình triển khai | Trụ cột 1 | Sinh viên Tiến Sơn | Commit, hash gói/hàm trước và sau triển khai | Xác định được phiên bản thực chạy, có cách khôi phục gói cũ, không công bố thông tin đăng nhập |
| **W3-02** | Tích hợp lịch với Lambda và dọn dẹp rule | Trụ cột 1 & 2 | Sinh viên Tiến Sơn | Bảng rule/target/policy và các lượt thực thi liên tiếp | Xác nhận lịch được chọn cho từng môi trường; giải thích và xử lý lịch thừa trước khi đánh giá mật độ mẫu |
| **W3-03** | Thử nghiệm Partition Projection và Parquet trên S3/Athena | Trụ cột 2 | Sinh viên Ngọc Quyên | Cấu hình thử nghiệm, câu truy vấn và bảng so sánh | Truy vấn không cần `MSCK REPAIR`; lượng byte quét và thời gian được đo trên cùng dữ liệu trước khi đánh giá lợi ích |
| **W3-04** | Kiểm tra chất lượng và thời gian quan trắc | Trụ cột 1 & 4 | Sinh viên Ngọc Quyên | CSV chất lượng và thống kê theo đô thị–giờ | Phân biệt khóa record_id, UTC/UTC+7, NULL và các lượt cùng giờ; giữ raw đầy đủ |
| **W3-05** | Chuẩn hóa giám sát CloudWatch Dashboard | Trụ cột 3 | Sinh viên Tiến Sơn | Dashboard JSON, CSV metric và ảnh biểu đồ do AWS trả về | Invocations/Errors dùng cùng namespace, dimensions, cửa sổ và chu kỳ; đọc lại Dashboard khớp cấu hình gửi |
| **W3-06** | Kiểm chứng cảnh báo email SNS | Trụ cột 3 | Sinh viên Tiến Sơn | Minh chứng Publish, giao thông báo và xác nhận nhận email | Tách rõ vượt ngưỡng, SNS nhận Publish và người nhận đã nhận thư; không mở thêm kênh cảnh báo |
| **W3-07** | Đánh giá khả năng dự báo chuỗi thời gian AQI/PM2.5 | Trụ cột 4 | Sinh viên Ngọc Quyên | Script, CSV dự báo và biểu đồ có nguồn dữ liệu | Tính sai số trên khoảng thời gian giữ lại; ghi rõ kích thước mẫu, phương pháp và giới hạn dữ liệu |
| **W3-08** | Tích hợp CI/CD tự động và rà soát hồ sơ repo GitHub | Trụ cột 1 | Cả hai sinh viên | Workflow GitHub Actions và README Tuần 3 | Mã, dữ liệu và commit mở được; các kiểm tra được cấu hình trong workflow đạt PASS trên CI |

Hai sinh viên phối hợp đối chiếu ở tất cả đầu việc. W3-01 và W3-02 đi trước W3-03; W3-03 cung cấp đầu vào cho W3-04/W3-07. W3-05 và W3-06 theo dõi cùng phiên bản triển khai. W3-08 tổng hợp sau khi các kết quả được đối chiếu.

## Tiến độ theo minh chứng đã có

Trạng thái dưới đây đối chiếu tiêu chí của từng mã việc với các hồ sơ ngày 16/10 và mốc chuẩn bị ngày 18/10; không suy ra số giờ làm việc từ commit hoặc thời gian chạy chương trình.

| Mã việc | Trạng thái có thể xác nhận | Minh chứng và phần còn lại |
| --- | --- | --- |
| W3-01 | Đã đạt tại đợt triển khai | [Source, hash module và sao lưu trước cập nhật](deployment-verification.md#phiên-bản-được-triển-khai); tiếp tục đối chiếu nếu mã thay đổi |
| W3-02 | Đã chuẩn hóa lịch và ghi nhận thêm các lượt sau CD | [Lượt ngày 16/10](scheduled-run-verification.md), [lượt sinh viên Tiến Sơn 13:15](../tuan_3/results/operations_2026_10_18/scheduled_followup/collections/default/) và [sinh viên Ngọc Quyên 13:51 sau sửa cấu hình](../tuan_3/results/post_repair_2026_10_18/README.md); chưa đủ kết luận vận hành liên tục nhiều ngày |
| W3-03 | Đã có thử nghiệm riêng ngày 18/10 | [18 truy vấn và kết quả Projection/Parquet](../tuan_3/docs/FINAL_REPORT.md#3-partition-projection-và-parquet); không quy đổi giảm byte quét thành mức tiết kiệm tiền |
| W3-04 | Đã xuất raw và kiểm tra chất lượng | [Bản xuất mới 246/288 dòng và 83 JSON gốc](../tuan_3/results/raw_export_2026_10_18/README.md); bảy nhóm kiểm tra đã khai báo không phát hiện lỗi; snapshot thống kê 246/285 và benchmark 237/273 được giữ riêng |
| W3-05 | Đã cấu hình Dashboard, hai Metric Filters và quan sát log mới ở cả hai môi trường | [Filter và điểm mới sinh viên Tiến Sơn](../tuan_3/results/operations_2026_10_18/), [điểm mới sinh viên Ngọc Quyên](../tuan_3/results/post_repair_2026_10_18/README.md); native metric còn điểm chưa nhất quán, không chuyển thiếu điểm thành 0 |
| W3-06 | Đạt luồng email tại các lượt 16/10 | [Publish → giao thông báo → xác nhận người nhận](scheduled-run-verification.md#cảnh-báo-và-giám-sát); tiếp tục ghi nhận lượt mới, không suy ra đã nhận thư từ metric đơn lẻ |
| W3-07 | Có đánh giá giữ lại và đối chiếu một phần với mô hình tải về sau | [Bốn phương pháp, 24 bộ sai số bổ sung](../tuan_3/docs/FINAL_REPORT.md#5-dự-báo-theo-giờ-và-đánh-giá); mới đối chiếu 2/24 giờ đích của bản phát hành, không phải dữ liệu trạm hoặc kết quả đủ 24 giờ |
| W3-08 | CI và CD hai môi trường đã có lượt thành công | [Kết quả CI/CD, hash AWS và dọn secrets](../tuan_3/docs/operation.md#4-kết-quả-thực-hiện); độ phủ vận hành theo lịch và giờ làm Tuần 3 vẫn ghi riêng |

## Điều kiện và hồ sơ kết thúc

- Thực hiện trong phiên AWS Learner Lab còn hiệu lực. Lịch bật không chứng minh hệ thống chạy liên tục khi Lab ngừng hoạt động.
- Lưu dữ liệu mới vào thư mục riêng theo mốc; giữ nguyên CSV Tuần 1 và Tuần 2 đã dùng trong báo cáo.
- Trước khi cập nhật hạ tầng, lưu phiên bản/cấu hình cũ để khôi phục. Ghi mọi lần triển khai, đổi lịch và thử thông báo vào nhật ký thực tế.
- Chạy kiểm tra theo [hướng dẫn mã nguồn](source-guide.md), sau đó kiểm tra riêng luồng trên AWS. Kiểm tra giả lập không thay thế dịch vụ thật.
- [Nhật ký Tuần 3](../tuan_3/docs/WORKLOG.md) ghi nhận đầy đủ mốc kỹ thuật và tổng 20,0 giờ công của hai sinh viên (10,0 giờ mỗi người), kèm liên kết trực tiếp tới các minh chứng dữ liệu và mã nguồn.

Hồ sơ kết thúc ghi kết quả W3-01 đến W3-08, phân công/số giờ, raw và CSV tổng hợp, cấu hình đã loại thông tin riêng tư, commit triển khai và các giới hạn còn lại. Chỉ đánh dấu hoàn thành khi có minh chứng tương ứng.

[Báo cáo nộp lại](../BAO_CAO.md) · [Nhật ký hai tuần](WORKLOG.md) · [Mã nguồn theo thành phần](components.md) · [Vận hành](operation.md)
