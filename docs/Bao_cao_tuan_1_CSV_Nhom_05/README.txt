BỘ CSV KẾT QUẢ ATHENA – BÁO CÁO TUẦN 1, NHÓM 05

Nguồn: năm kết quả truy vấn Athena và query_metrics.csv đã lưu trong results/athena_queries.
Đây là bản sao nguyên vẹn của các CSV đã lưu, không phải lượt tải AWS mới.
Nếu Excel trên máy mở CSV thành một cột, dùng bản .xlsx trình bày nộp kèm.

QUY CÁCH CSV
Giữ nguyên byte của bản CSV xuất đã lưu: dấu phẩy phân cột, dòng đầu là tên cột.
Các CSV kết quả Athena dùng dấu ngoặc kép và LF; query_metrics dùng UTF-8 BOM và CRLF.
Tên cột, thứ tự cột, thứ tự dòng và giá trị không bị đổi khi đóng gói.
CSV thuần không lưu màu hay kiểu chữ; bản Excel đi kèm có trình bày đen–trắng.

DANH MỤC TỆP
1. avg_aqi_by_city.csv – 3 dòng kết quả; QueryExecutionId: c2fddbda-2bad-424f-b9f9-02773d5b3df4.
2. peak_pollution_hours.csv – 24 dòng kết quả; QueryExecutionId: 8018524b-c34e-47ed-bb89-c05e7db88bd1.
3. aqi_category_distribution.csv – 8 dòng kết quả; QueryExecutionId: ec8641a0-c706-45fb-bc8c-4f1d72d1978a.
4. weather_correlation.csv – 3 dòng kết quả; QueryExecutionId: 14bb410d-4725-45f3-bb5d-59ddf4c962cb.
5. raw_weather_aqi_records.csv – 156 bản ghi, 23 cột; QueryExecutionId: d67cd503-1d5a-487a-98dd-b46a111b2f43.
6. query_metrics.csv – metadata của cả năm truy vấn: trạng thái, thời gian chạy,
   dung lượng quét và tên CSV. result_rows là số dòng dữ liệu của từng CSV.

ĐƠN VỊ VÀ CÁCH ĐỌC
avg_pm2_5, avg_pm10: µg/m³; avg_temp: °C; avg_humidity, percentage: %.
hour: giờ UTC; corr_*: hệ số tương quan Pearson, không có đơn vị.
Tổng total_records theo đô thị và tổng sample_count theo giờ đều là 156.
Bốn CSV tổng hợp đi kèm CSV raw chứa đủ 156 bản ghi quan trắc gốc.
