# Dữ liệu và phương pháp phân tích

## Bộ báo cáo Tuần 1

[CSV đã nộp](../tuan_2/results/athena_queries/) gồm 156 bản ghi/52 mẫu mỗi đô thị, bốn bảng tổng hợp và chỉ số truy vấn. Bộ này được giữ nguyên cùng báo cáo và Excel Tuần 1.

## Bộ dữ liệu mới Tuần 2

[Kết quả Athena](../tuan_2/results/week2_live/) được xuất riêng theo hai tài khoản. Tổng raw là 204/231, mẫu thuộc Tuần 2 là 27/57. Tuần được lọc theo UTC+7, timestamp môi trường dạng không có múi giờ được hiểu là UTC; các thời điểm dịch vụ có múi giờ được đổi về UTC trước khi lọc.

[Tệp raw và metadata nguồn](../tuan_2/results/week2_evidence/) giữ đủ tệp raw có thể đọc được, danh sách/hash đối tượng, trạng thái tài nguyên, điểm CloudWatch, dòng REPORT đã trích, lịch sử truy vấn và chi phí theo dịch vụ. Credentials, nội dung secret, endpoint email, URL tải có chữ ký và log thô được loại khỏi bộ công khai.

## Phép tính

- Phân tích riêng từng tài khoản; không cộng 144 cặp lịch sử trùng nhau thành quan trắc độc lập.
- Trung bình và SD tính trên các bản ghi trong cùng đô thị/tài khoản; SD dùng n−1.
- Q1, trung vị, Q3 và P95 dùng nội suy tuyến tính. Không gọi SD là khoảng tin cậy.
- Các tỷ lệ dùng số mẫu cùng đô thị/tài khoản làm mẫu số; không diễn giải thành tỷ lệ thời gian toàn tuần.
- Đối chiếu ghép trung bình của cùng thành phố/giờ, 21 nhóm (7 giờ mỗi đô thị), với trọng số mỗi giờ bằng nhau.
- Pearson và Spearman giữ kèm n; Spearman dùng hạng trung bình cho giá trị trùng. Mẫu chuỗi ngắn không chứng minh nhân quả.
- Giá trị NULL/không hữu hạn được kiểm tra riêng; số 0 giữ nguyên và đếm riêng.
- Errors > Invocations khiến tỷ lệ lỗi không xác định. Không thay dữ liệu bằng 0 hoặc tạo phần trăm vượt 100%.
- Cost Explorer giữ số tiền gốc, đơn vị và cờ Estimated; số liệu theo tài khoản không được gọi là chi phí riêng dự án.

## Tệp kết quả

[24 CSV phân tích](../tuan_2/results/week2_analysis/) có bảng phân bố, giờ/ngày, cấp AQI, vượt ngưỡng, tương quan, so sánh ghép giờ, chất lượng, vận hành, query metrics và chi phí. [Manifest hình](../tuan_2/results/week2_charts/chart_manifest.json) chỉ rõ CSV nguồn của cả 16 hình. Word và Excel nhúng cùng các ảnh, bên cạnh dữ liệu và các công thức tổng hợp trong Excel.

Dữ liệu chất lượng không khí được cung cấp qua [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), dựa trên CAMS. Bộ API đã lưu không được coi là phép đo trực tiếp tại một trạm.
