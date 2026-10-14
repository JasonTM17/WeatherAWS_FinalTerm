# Dữ liệu và phương pháp phân tích

## Bộ báo cáo Tuần 1

[CSV của báo cáo Tuần 1](../tuan_2/results/athena_queries/) gồm 156 bản ghi/52 mẫu mỗi đô thị, bốn bảng tổng hợp và chỉ số truy vấn. Bộ này giữ nguyên các giá trị trong báo cáo và Excel Tuần 1. Mỗi đô thị có 52 mốc giờ liên tiếp, được gom thành 24 nhóm giờ trong ngày. Có 51 dòng lịch sử nạp bổ sung trước ranh giới Tuần 1 và 105 dòng trong ranh giới tuần theo UTC+7; bộ 156 dòng là phạm vi của lần xuất dùng làm báo cáo.

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

[25 CSV phân tích](../tuan_2/results/week2_analysis/) có bảng phân bố, giờ/ngày, cấp AQI, vượt ngưỡng, tương quan, so sánh ghép giờ, chất lượng, vận hành, query metrics, chi phí và đối chiếu với báo cáo Tuần 1. [Manifest hình](../tuan_2/results/week2_charts/chart_manifest.json) chỉ rõ CSV nguồn của cả 16 hình. Word và Excel nhúng cùng các ảnh, bên cạnh dữ liệu và các công thức tổng hợp trong Excel.

## Hai phạm vi đối chiếu tuần

- [submitted_week1_comparison.csv](../tuan_2/results/week2_analysis/submitted_week1_comparison.csv) giữ bộ 156 dòng của báo cáo Tuần 1 làm mốc (52 mẫu/đô thị), so với mẫu Tuần 2 riêng từng nguồn (9/19). Bảng 3.10 và 3.11 trong báo cáo dùng phép này cho AQI và PM2.5. Chênh lệch tính từ trung bình chưa làm tròn; tệp manifest lưu hash của bộ mốc.
- [weekly_comparison.csv](../tuan_2/results/week2_analysis/weekly_comparison.csv) lọc hai tuần từ cùng lần xuất mới, nên có 42/41 mẫu Tuần 1 và 9/19 mẫu Tuần 2 mỗi đô thị. Bảng 3.12 và Hình 3.12 dùng riêng phạm vi này. Sheet So_sanh_tuan trong Excel giữ cả hai bảng nguồn.
- Các bộ có thời gian và độ phủ khác nhau; không xem chênh lệch trung bình mẫu là xu hướng của toàn bộ bảy ngày hoặc so sánh cùng thời điểm. Trong lần xuất mới, 144/156 dòng theo thành phố và timestamp trùng bộ cũ ở nguồn Sơn, 156/156 ở nguồn Quyên; các trường cảm biến ở phần trùng đều giống nhau.

Dữ liệu chất lượng không khí được cung cấp qua [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), dựa trên CAMS. Bộ API đã lưu không được coi là phép đo trực tiếp tại một trạm.
