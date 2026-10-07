BỘ CSV KẾT QUẢ ATHENA – BÁO CÁO TUẦN 1, NHÓM 05

Nguồn: bốn tệp kết quả và summary_metrics.json đã lưu trong results/athena_queries.
Đây là bản đóng gói từ dữ liệu đã lưu, không phải lượt tải mới từ AWS.
AWS CLI trả kết quả GetQueryResults dạng JSON; các tệp dưới đây là bảng CSV
được chuẩn hóa từ kết quả Athena đã lưu, không phải stdout nguyên gốc của CLI.
Nếu Excel trên máy mở CSV thành một cột, xem bản trình bày .xlsx nộp kèm.

QUY CÁCH CSV
UTF-8 BOM; dấu phẩy phân cột; xuống dòng CRLF; dòng đầu là tên cột.
Tên cột, thứ tự cột, thứ tự dòng và từng giá trị giữ đúng tập kết quả đã lưu.
Số dùng dấu chấm thập phân, không thêm dấu phân nhóm hay đơn vị vào ô dữ liệu.

DANH MỤC TỆP
1. avg_aqi_by_city.csv – 3 dòng kết quả; QueryExecutionId: 57e9d139-1a73-422d-adb4-e0b006f740c6.
2. peak_pollution_hours.csv – 24 dòng kết quả; QueryExecutionId: f77e7656-bb51-4cb1-9ba8-117bce879d57.
3. aqi_category_distribution.csv – 8 dòng kết quả; QueryExecutionId: f1e2d2a8-dc47-4afb-98e6-30f4de8b096f.
4. weather_correlation.csv – 3 dòng kết quả; QueryExecutionId: 25272532-19a7-405f-b803-91244e1c946a.
5. query_metrics.csv – bảng đối chiếu bốn truy vấn với các trường trạng thái,
   thời gian chạy (ms), dung lượng quét (byte) và tên tệp kết quả.
   ResultRows là số dòng kết quả trong CSV, không phải số bản ghi raw.

ĐƠN VỊ VÀ CÁCH ĐỌC
avg_pm2_5, avg_pm10: µg/m³; avg_temp: °C; avg_humidity, percentage: %.
hour: giờ UTC; corr_*: hệ số tương quan Pearson, không có đơn vị.
Tổng total_records theo đô thị và tổng sample_count theo giờ đều là 156.
Bốn CSV là các bảng tổng hợp, không chứa 156 bản ghi quan trắc gốc.
