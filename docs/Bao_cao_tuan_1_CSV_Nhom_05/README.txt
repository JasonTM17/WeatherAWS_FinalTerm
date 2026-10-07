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
1. avg_aqi_by_city.csv – 3 dòng kết quả; QueryExecutionId: 834239d3-ba12-495f-8ac7-673abb95f025.
2. peak_pollution_hours.csv – 24 dòng kết quả; QueryExecutionId: 96035c95-2d2f-4b62-96b8-aa08db990976.
3. aqi_category_distribution.csv – 8 dòng kết quả; QueryExecutionId: e5b23e62-5259-401c-a6a1-9d691caa1fd5.
4. weather_correlation.csv – 3 dòng kết quả; QueryExecutionId: efae4537-970d-452c-b3fc-665713a9d424.
5. raw_weather_aqi_records.csv – 156 bản ghi, 23 cột; QueryExecutionId: 1e473ab6-4d52-4ec2-9412-5aa66626b05f.
6. query_metrics.csv – metadata của cả năm truy vấn: trạng thái, thời gian chạy,
   dung lượng quét và tên CSV. result_rows là số dòng dữ liệu của từng CSV.

ĐƠN VỊ VÀ CÁCH ĐỌC
avg_pm2_5, avg_pm10: µg/m³; avg_temp: °C; avg_humidity, percentage: %.
hour: giờ UTC; corr_*: hệ số tương quan Pearson, không có đơn vị.
Tổng total_records theo đô thị và tổng sample_count theo giờ đều là 156.
Bốn CSV tổng hợp đi kèm CSV raw chứa đủ 156 bản ghi quan trắc gốc.
