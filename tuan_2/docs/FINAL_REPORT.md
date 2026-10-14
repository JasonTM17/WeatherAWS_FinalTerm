# Báo cáo Tuần 2 từ hai bộ báo cáo dữ liệu của nhóm

## TÓM TẮT

Báo cáo Tuần 2 tổng hợp hai bộ báo cáo dữ liệu do sinh viên Tiến Sơn và sinh viên Ngọc Quyên cung cấp về thời tiết, chất lượng không khí và kết quả vận hành hệ thống AWS Learner Lab. Chúng em sử dụng các tệp raw trên S3, kết quả truy vấn Athena và chỉ số dịch vụ để trình bày số liệu theo từng nguồn.

Hai bộ báo cáo dữ liệu gồm 435 bản ghi: 204 trong bộ của sinh viên Tiến Sơn và 231 trong bộ của sinh viên Ngọc Quyên. Theo ranh giới tuần ở Việt Nam quy đổi sang UTC, mẫu Tuần 2 có 27 và 57 bản ghi, tương ứng 9 và 19 mẫu mỗi đô thị. Các thống kê được trình bày riêng theo từng sinh viên.

Hà Nội có AQI trung bình Tuần 2 đạt 163,56 và 163,05; TP. Hồ Chí Minh đạt 78,00 và 79,05; Đà Nẵng đạt 35,44 và 35,37. Báo cáo trình bày 20 biểu đồ từ dữ liệu thực tế, 24 truy vấn Athena mới thành công, phân bố mẫu, biến thiên theo giờ, ngưỡng cảnh báo, tương quan khí tượng và mức sử dụng tài nguyên. Các kết luận giới hạn trong mẫu đã thu thập.

## LỜI MỞ ĐẦU

Học phần Điện toán đám mây giúp chúng em vận dụng các dịch vụ quản lý trên AWS vào một luồng dữ liệu cụ thể. Bài toán thời tiết và chất lượng không khí cho phép theo dõi quá trình từ thu thập qua API, chuẩn hóa bản ghi, lưu trữ đến truy vấn và trình bày kết quả.

Báo cáo trình bày chức năng hệ thống, dữ liệu và kết quả phân tích Tuần 2 từ hai bộ báo cáo dữ liệu của sinh viên Tiến Sơn và sinh viên Ngọc Quyên. Word, PDF, bảng và biểu đồ Excel sử dụng cùng các tệp CSV đã đối chiếu. Kho dự án: https://github.com/JasonTM17/WeatherAWS_FinalTerm.git

Đề tài được thực hiện bởi nhóm sinh viên:

- Nguyễn Tiến Sơn — MSSV 24110054: S3, Secrets Manager, Lambda và SNS.

- Trần Thị Ngọc Quyên — MSSV 24110051: Glue, Athena, biểu đồ và đối chiếu dữ liệu.

Báo cáo gồm sáu chương: phạm vi hệ thống và phân công; nguồn dữ liệu và phương pháp phân tích; dữ liệu môi trường; vận hành Lambda và SNS; truy vấn và sử dụng tài nguyên; tổng hợp kết quả Tuần 2.

## Chương 1 Phạm vi và hệ thống thực hành Tuần 2

### 1.1 Mục tiêu và phạm vi số liệu

Chúng em tiếp tục phân tích luồng thu thập thời tiết và chất lượng không khí cho TP. Hồ Chí Minh, Hà Nội và Đà Nẵng. Tuần 2 tập trung vào hoạt động của các dịch vụ, dữ liệu mới theo thời gian quan trắc và các phép phân tích có thể tái lập từ tệp xuất. Dữ liệu Open-Meteo là dữ liệu API mô hình, không được coi là phép đo trực tiếp của một trạm.

Hai bộ báo cáo dữ liệu được thu thập trên hệ thống AWS tại us-east-1 của từng sinh viên. Mỗi bộ gồm các tệp raw của dự án và kết quả của 12 truy vấn SELECT. Bộ dữ liệu Tuần 1 đã lưu được giữ nguyên; số liệu Tuần 2 lấy từ lần đọc dịch vụ và truy vấn mới. Thời điểm xuất và mã truy vấn được lưu cùng dữ liệu để đối chiếu.

### 1.2 Phân công và thời gian thực hiện

Bảng 1.1 Phân công và số giờ đã được nhóm xác nhận

| Thành viên | Phụ trách chính | Phối hợp | Giờ |
| --- | --- | --- | --- |
| Nguyễn Tiến Sơn<br>24110054 | S3, Secrets Manager, Lambda và SNS. | Kiến trúc, tích hợp, phân tích và báo cáo. | 10,0 |
| Trần Thị Ngọc Quyên<br>24110051 | Glue, Athena, biểu đồ và đối chiếu dữ liệu. | Kiến trúc, tích hợp, phân tích và báo cáo. | 9,5 |

Tổng thời gian nhóm đã xác nhận cho Tuần 2 là 19,5 giờ. Hai thành viên cùng đối chiếu nguồn dữ liệu, cách tính thống kê và các sản phẩm báo cáo. Phân công này thống nhất với nhật ký công việc của nhóm.

### 1.3 Kiến trúc và luồng xử lý

![Kiến trúc hệ thống](../../docs/architecture.png)

Hình 1.1 Kiến trúc và luồng dữ liệu của hệ thống

EventBridge kích hoạt Lambda. Hàm đọc cấu hình, gọi hai nguồn Open-Meteo, chuẩn hóa các trường và ghi NDJSON vào S3 theo phân vùng. SNS tiếp nhận thông báo khi thỏa ngưỡng cấu hình. Glue quản lý lược đồ và phân vùng; Athena đọc S3 để tạo các bảng phân tích. CloudWatch lưu chỉ số và log thời gian thực thi.

### 1.4 Trạng thái dịch vụ trong dữ liệu Tuần 2

Bảng 1.2 Cấu hình và trạng thái hệ thống trong hai báo cáo dữ liệu

| Nội dung | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Lambda | Active; Python 3.12; 256 MB; 60 giây. | Active; Python 3.12; 256 MB; 60 giây. |
| Lịch mỗi giờ | 1 quy tắc ENABLED. | 2 quy tắc ENABLED. |
| Đăng ký email SNS | 1 đăng ký đã xác nhận. | 2 đăng ký đã xác nhận. |
| CloudWatch Alarm | OK tại thời điểm đọc. | OK tại thời điểm đọc. |
| Glue Catalog | 6 phân vùng trong bảng raw. | 6 phân vùng trong bảng raw. |

Báo cáo dữ liệu của sinh viên Ngọc Quyên ghi nhận WeatherCollectionHourlyRule và WeatherCollectionSchedule cùng bật với chu kỳ rate(1 hour); báo cáo của sinh viên Tiến Sơn ghi nhận WeatherCollectionSchedule. Trạng thái bật chỉ mô tả cấu hình tại lần đọc. Danh sách lịch và số mẫu được dùng để giải thích mật độ thu thập của từng bộ dữ liệu.

## Chương 2 Nguồn dữ liệu và phương pháp phân tích

### 2.1 Toàn bộ dữ liệu và mẫu thuộc Tuần 2

Bảng 2.1 Quy mô nguồn dữ liệu đã tải

| Sinh viên | Tệp raw | Byte raw | Tổng dòng | Dòng Tuần 2 | Giờ có mẫu |
| --- | --- | --- | --- | --- | --- |
| Tiến Sơn | 22 | 114.736 | 204 | 27 | 9 |
| Ngọc Quyên | 28 | 129.715 | 231 | 57 | 9 |

![Quy mô dữ liệu tải về và phạm vi Tuần 2](../results/week2_charts/01_data_scope.png)

Hình 2.1 Quy mô dữ liệu tải về và phạm vi Tuần 2

Hai bộ báo cáo dữ liệu có tổng 435 dòng nguồn, bao gồm phần dữ liệu lịch sử. Sau khi chọn phạm vi Tuần 2, bộ của sinh viên Tiến Sơn có 27 dòng và bộ của sinh viên Ngọc Quyên có 57 dòng. Các bảng thống kê giữ riêng từng bộ cùng mã bản ghi và thời gian quan trắc; tổng số dòng nguồn không được dùng làm cỡ mẫu độc lập của một tập gộp.

Ranh giới tuần được xác định theo UTC+7, sau đó đổi sang UTC để lọc timestamp_utc. Các thời điểm AWS có múi giờ được chuẩn hóa về UTC trước khi so sánh. Phân vùng S3 dùng ngày UTC, nên điều kiện trên phân vùng được kết hợp với điều kiện timestamp để giữ đúng phạm vi.

### 2.2 Cấu trúc và chất lượng bản ghi

Dữ liệu xuất từ Athena gồm 23 cột, tương ứng 20 cột thường và ba khóa phân vùng year, month, day. Các cột mô tả nhận diện, tọa độ, thời gian UTC và Việt Nam, yếu tố khí tượng, nồng độ ô nhiễm, chỉ số AQI và cấp AQI. CSV giữ một dòng cho một bản ghi; không thêm tiêu đề trang trí hoặc thay đổi giá trị raw.

Bảng 2.2 Đối chiếu chất lượng trong tập Tuần 2

| Sinh viên | Bản ghi | Trường số | NULL hoặc không hữu hạn | Giá trị 0 |
| --- | --- | --- | --- | --- |
| Tiến Sơn | 27 | 11 | 0 | 0 |
| Ngọc Quyên | 57 | 11 | 0 | 0 |

Trong 11 trường số kiểm tra của mẫu Tuần 2, không có NULL, giá trị không hữu hạn hoặc số 0. Kết quả này mô tả giá trị đã lưu; nó không chứng minh nguồn API chưa từng thiếu dữ liệu, vì mã nguồn có nhánh chuyển đầu vào không hợp lệ sang giá trị mặc định. Không ghi đè bản ghi gốc trong quá trình phân tích.

### 2.3 Hai bộ báo cáo dữ liệu của nhóm

Chúng em trình bày hai bộ báo cáo dữ liệu do sinh viên Tiến Sơn và sinh viên Ngọc Quyên cung cấp. Mỗi bộ giữ riêng mã bản ghi, đô thị, thời gian quan trắc và các chỉ số môi trường. Có 144 quan trắc lịch sử cùng đô thị và thời điểm xuất hiện trong cả hai bộ, với giá trị cảm biến tương ứng bằng nhau; các thống kê được tính riêng cho từng bộ dữ liệu.

Đối chiếu số liệu Tuần 2 dựa trên các nhóm cùng đô thị và giờ UTC trong hai báo cáo dữ liệu. Có 21 nhóm đối chiếu, tương ứng 7 giờ chung cho mỗi đô thị. Chênh lệch được tính bằng giá trị của sinh viên Ngọc Quyên trừ giá trị của sinh viên Tiến Sơn, với trọng số mỗi giờ như nhau. Các thống kê theo từng sinh viên vẫn sử dụng toàn bộ mẫu thuộc bộ dữ liệu tương ứng.

### 2.4 Các đại lượng và cách diễn giải

Bảng 2.3 Cách tính các nhóm chỉ số

| Chỉ số | Cách tính và phạm vi |
| --- | --- |
| Trung bình, cực trị | Tính riêng từng bộ dữ liệu và đô thị trên mẫu Tuần 2. |
| Độ lệch chuẩn | Độ lệch chuẩn mẫu với mẫu số n−1; không phải khoảng tin cậy. |
| Trung vị, Q1, Q3, P95 | Nội suy tuyến tính trên các giá trị đã sắp xếp. |
| Tỷ lệ cấp và vượt ngưỡng | Số mẫu thỏa điều kiện chia tổng mẫu của cùng đô thị và bộ dữ liệu. |
| Pearson và Spearman | Liên hệ tuyến tính và liên hệ thứ hạng; không suy ra quan hệ nhân quả. |
| Chi phí và chỉ số dịch vụ | Giữ đúng nguồn AWS, phạm vi thời gian, đơn vị và trạng thái Estimated. |

### 2.5 Thiết kế chức năng thu thập bằng Lambda

Mã nguồn Lambda được tổ chức thành các nhóm chức năng: đọc cấu hình, chuyển đổi kiểu, gọi API, phân loại AQI, thu thập hiện tại hoặc lịch sử, kiểm tra ngưỡng, gửi SNS và ghi S3. Mỗi đô thị có hai lượt gọi API: chất lượng không khí và thời tiết. Các biến môi trường chỉ định bucket, tên secret và topic; LabRole cung cấp quyền thực thi trong Learner Lab.

Cấu hình weather/api_config quản lý tọa độ ba đô thị và ngưỡng cảnh báo. Khi đọc cấu hình thất bại, mã nguồn có nhánh dự phòng và ghi log. Các hàm chuyển đổi dùng mặc định khi dữ liệu không hợp lệ; vì thế việc đánh giá chất lượng CSV phân biệt số 0 với dữ liệu thiếu. Các khoảng phân loại AQI được xác định trong mã nguồn; nhãn cấp AQI đi cùng chỉ số trong bản ghi.

Mã nguồn ghép chuỗi lịch sử khí tượng và AQI theo timestamp, kiểm tra độ dài mảng trước khi đọc, phát sinh lỗi khi không thu được bản ghi và ghi rõ trạng thái thu thập một phần khi chỉ một số đô thị thất bại.

Bảng 2.4 Đầu vào và đầu ra của các nhóm xử lý

| Nhóm chức năng | Đầu vào | Đầu ra |
| --- | --- | --- |
| Cấu hình | Secret và biến môi trường. | Vị trí, ngưỡng và đích lưu/gửi. |
| Thu thập hiện tại | Hai API cho từng đô thị. | Giá trị AQI, khí tượng và nồng độ khí. |
| Chuỗi lịch sử | Các mảng có timestamp của hai API. | Bản ghi ghép theo thời điểm. |
| Cảnh báo | AQI ≥ 100 hoặc PM2.5 ≥ 35,5. | Phản hồi gửi thông điệp SNS. |
| Lưu trữ | Bản ghi 23 trường. | NDJSON trong phân vùng ngày UTC. |

### 2.6 Lược đồ bản ghi và truy vấn dữ liệu

Bảng 2.5 Lược đồ 23 trường của bản ghi

| Trường | Kiểu | Đơn vị | Ý nghĩa |
| --- | --- | --- | --- |
| record_id | string | — | Mã bản ghi |
| city | string | — | Thành phố |
| latitude | double | ° | Vĩ độ |
| longitude | double | ° | Kinh độ |
| timestamp_utc | string | UTC | Thời điểm quan trắc |
| timestamp_vn | string | UTC+7 | Thời điểm ở Việt Nam |
| temperature_2m | double | °C | Nhiệt độ |
| relative_humidity_2m | double | % | Độ ẩm tương đối |
| surface_pressure | double | hPa | Áp suất bề mặt |
| wind_speed_10m | double | km/h | Tốc độ gió |
| pm2_5 | double | µg/m³ | Bụi PM2.5 |
| pm10 | double | µg/m³ | Bụi PM10 |
| carbon_monoxide | double | µg/m³ | CO |
| nitrogen_dioxide | double | µg/m³ | NO₂ |
| sulphur_dioxide | double | µg/m³ | SO₂ |
| ozone | double | µg/m³ | O₃ |
| us_aqi | int | AQI | Chỉ số chất lượng không khí |
| aqi_category | string | — | Nhãn phân loại AQI |
| hour | int | 0–23 | Giờ UTC |
| collected_at | string | ISO 8601 | Mốc ghi nhận |
| year | string | — | Phân vùng năm |
| month | string | — | Phân vùng tháng |
| day | string | — | Phân vùng ngày |

Athena dùng bảng ngoài weather_airquality_records và view vietnam_weather_aqi trong weather_aqi_db. Lược đồ khai báo 20 cột thường và 3 khóa phân vùng; Glue giữ metadata, còn các bản ghi nằm trên S3. Truy vấn hiện tại đọc các phân vùng đã có và kết hợp điều kiện timestamp để lọc đúng ranh giới tuần.

### 2.7 Quyền kích hoạt và điều kiện gửi thông báo

Quy tắc EventBridge trỏ đến WeatherCollectorLambda; chính sách tài nguyên cho phép events.amazonaws.com gọi lambda:InvokeFunction với giới hạn ARN nguồn. Báo cáo dữ liệu của sinh viên Tiến Sơn ghi nhận một lịch đang bật, báo cáo của sinh viên Ngọc Quyên ghi nhận hai lịch. Các cấu hình này được giữ theo trạng thái thực tế tại lần đọc.

SNS topic weather-airquality-alerts nhận thông điệp có đô thị, thời điểm, AQI, cấp phân loại, PM2.5, PM10 và yếu tố khí tượng. Đăng ký email cần được người nhận xác nhận. Hai báo cáo dữ liệu ghi nhận lần lượt một và hai đăng ký đã xác nhận trong môi trường AWS của sinh viên Tiến Sơn và sinh viên Ngọc Quyên. Delivered mô tả giao tới đích dịch vụ, không xác nhận người nhận đã đọc thư.

## Chương 3 Phân tích dữ liệu môi trường Tuần 2

### 3.1 So sánh AQI theo đô thị

Bảng 3.1 AQI trung bình và độ phân tán

| Đô thị | Sinh viên | n | TB | SD | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | Tiến Sơn | 9 | 78,00 | 2,45 | 75 | 82 |
| TP. Hồ Chí Minh | Ngọc Quyên | 19 | 79,05 | 2,34 | 76 | 83 |
| Hà Nội | Tiến Sơn | 9 | 163,56 | 3,84 | 160 | 169 |
| Hà Nội | Ngọc Quyên | 19 | 163,05 | 3,14 | 160 | 168 |
| Đà Nẵng | Tiến Sơn | 9 | 35,44 | 3,54 | 32 | 42 |
| Đà Nẵng | Ngọc Quyên | 19 | 35,37 | 3,61 | 32 | 42 |

![AQI trung bình và độ lệch chuẩn của mẫu Tuần 2](../results/week2_charts/02_aqi_city.png)

Hình 3.1 AQI trung bình và độ lệch chuẩn của mẫu Tuần 2

Hà Nội có AQI trung bình cao nhất: 163,56 ở bộ dữ liệu của sinh viên Tiến Sơn và 163,05 ở bộ dữ liệu của sinh viên Ngọc Quyên; Đà Nẵng thấp nhất. Thanh sai số biểu diễn SD của mẫu. Mỗi đô thị có 9 và 19 bản ghi, nhưng mỗi nguồn chỉ gồm 9 nhóm giờ; các dòng gần nhau có thể phản ánh cùng trạng thái API, nên không mặc nhiên xem là mẫu độc lập.

### 3.2 Nồng độ PM2.5 và PM10

Bảng 3.2 Bụi và khí tượng trung bình

| Đô thị | Sinh viên | PM2.5 | PM10 | Nhiệt độ °C | Độ ẩm % |
| --- | --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | Tiến Sơn | 23,38 | 24,69 | 26,71 | 87,89 |
| TP. Hồ Chí Minh | Ngọc Quyên | 22,92 | 24,09 | 26,92 | 86,68 |
| Hà Nội | Tiến Sơn | 76,66 | 78,52 | 28,06 | 74,22 |
| Hà Nội | Ngọc Quyên | 75,11 | 76,95 | 28,35 | 72,89 |
| Đà Nẵng | Tiến Sơn | 6,38 | 8,56 | 25,50 | 90,56 |
| Đà Nẵng | Ngọc Quyên | 6,46 | 8,66 | 25,86 | 88,53 |

![PM2.5 và PM10 trung bình theo đô thị và nguồn dữ liệu](../results/week2_charts/03_particulates.png)

Hình 3.2 PM2.5 và PM10 trung bình theo đô thị và nguồn dữ liệu

PM2.5 trung bình tại Hà Nội là 76,66 và 75,11 µg/m³, trong khi TP. Hồ Chí Minh khoảng 23 µg/m³ và Đà Nẵng khoảng 6,4 µg/m³. PM10 cao hơn PM2.5 trong cả sáu nhóm. Các đơn vị nồng độ được giữ riêng với chỉ số AQI; không so sánh chiều cao cột của hai đại lượng khác đơn vị trên cùng trục.

### 3.3 Trung vị tứ phân vị và P95

Bảng 3.3 Các phân vị AQI trong từng tập mẫu

| Đô thị | Sinh viên | Q1 | Trung vị | Q3 | P95 | IQR |
| --- | --- | --- | --- | --- | --- | --- |
| Đà Nẵng | Tiến Sơn | 32,00 | 35,00 | 38,00 | 40,40 | 6,00 |
| Hà Nội | Tiến Sơn | 160,00 | 161,00 | 167,00 | 168,60 | 7,00 |
| TP. Hồ Chí Minh | Tiến Sơn | 76,00 | 77,00 | 80,00 | 81,60 | 4,00 |
| Đà Nẵng | Ngọc Quyên | 32,00 | 34,00 | 37,50 | 42,00 | 5,50 |
| Hà Nội | Ngọc Quyên | 160,50 | 161,00 | 166,00 | 168,00 | 5,50 |
| TP. Hồ Chí Minh | Ngọc Quyên | 77,00 | 78,00 | 81,00 | 83,00 | 4,00 |

![Trung vị khoảng tứ phân vị và độ phân tán AQI](../results/week2_charts/04_aqi_distribution.png)

Hình 3.3 Trung vị khoảng tứ phân vị và độ phân tán AQI

Biểu đồ hộp thể hiện trung vị, khoảng tứ phân vị và cực trị của mẫu. P95 được tính bằng nội suy tuyến tính giữa các giá trị quan trắc. Với cỡ mẫu nhỏ và chuỗi lấy mẫu ngắn, P95 mô tả tập mẫu hiện có, chưa đại diện cho phân vị dài hạn của đô thị.

### 3.4 Diễn biến tại các giờ có quan trắc

![Biến thiên AQI tại các giờ thực sự có dữ liệu](../results/week2_charts/05_hourly_aqi.png)

Hình 3.4 Biến thiên AQI tại các giờ thực sự có dữ liệu

Chuỗi thời gian thể hiện các giờ có dữ liệu và ngắt đường tại khoảng thiếu giờ. Báo cáo dữ liệu của sinh viên Tiến Sơn có 9 giờ quan trắc, mỗi giờ một mẫu cho mỗi đô thị. Báo cáo của sinh viên Ngọc Quyên có 9 giờ, phần lớn hai mẫu mỗi đô thị trong giờ và một giờ ba mẫu.

Bảng 3.4 Giờ có AQI trung bình lớn nhất trong bộ dữ liệu của từng sinh viên

| Đô thị | Sinh viên | Giờ UTC | AQI TB | Mẫu trong giờ |
| --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | Tiến Sơn | 07 | 82,00 | 1 |
| TP. Hồ Chí Minh | Ngọc Quyên | 06 | 83,00 | 2 |
| Hà Nội | Tiến Sơn | 19 | 169,00 | 1 |
| Hà Nội | Ngọc Quyên | 18 | 168,00 | 2 |
| Đà Nẵng | Tiến Sơn | 02 | 42,00 | 1 |
| Đà Nẵng | Ngọc Quyên | 02 | 42,00 | 3 |

Giờ UTC được trình bày để đối chiếu cùng trường hour trong dữ liệu. Bảng chọn cực đại trong các giờ đã quan trắc, không xác nhận một khung giờ cao điểm ô nhiễm điển hình trong ngày.

### 3.5 Độ phủ và mật độ lấy mẫu

![Mật độ lấy mẫu theo đô thị, sinh viên và giờ](../results/week2_charts/06_sampling_coverage.png)

Hình 3.5 Mật độ lấy mẫu theo đô thị, sinh viên và giờ

Các ô có số thể hiện lượng mẫu của từng đô thị trong một giờ; ô trắng là giờ chưa có mẫu trong phạm vi hình. Hai báo cáo dữ liệu có 7 giờ quan trắc chung và mỗi bộ có thêm 2 giờ riêng. Tổng 27 và 57 dòng phản ánh mật độ lấy mẫu của từng sinh viên trên cùng ba đô thị.

Bộ Tuần 2 mới chỉ có dữ liệu ở hai ngày trong tuần và không đủ 24 nhóm giờ cho từng nguồn. Chúng em giữ các giờ thiếu dưới dạng thiếu dữ liệu, không điền số 0 và không lấy trung bình từ một chuỗi ngày giả định đầy đủ.

### 3.6 Phân bố các cấp chất lượng không khí

Bảng 3.5 Cấp AQI xuất hiện và tỷ lệ mẫu

| Đô thị | Sinh viên | Cấp AQI | Số mẫu | Tỷ lệ % |
| --- | --- | --- | --- | --- |
| Đà Nẵng | Tiến Sơn | Good | 9 | 100,0 |
| Hà Nội | Tiến Sơn | Unhealthy | 9 | 100,0 |
| TP. Hồ Chí Minh | Tiến Sơn | Moderate | 9 | 100,0 |
| Đà Nẵng | Ngọc Quyên | Good | 19 | 100,0 |
| Hà Nội | Ngọc Quyên | Unhealthy | 19 | 100,0 |
| TP. Hồ Chí Minh | Ngọc Quyên | Moderate | 19 | 100,0 |

![Cấp AQI xuất hiện trong mẫu Tuần 2 của mỗi đô thị](../results/week2_charts/07_categories.png)

Hình 3.6 Cấp AQI xuất hiện trong mẫu Tuần 2 của mỗi đô thị

Toàn bộ mẫu Đà Nẵng thuộc Good, TP. Hồ Chí Minh thuộc Moderate và Hà Nội thuộc Unhealthy trên cả hai nguồn. Đây là tỷ lệ bản ghi trong tập mẫu. Không diễn giải 100% mẫu thành 100% thời gian trong tuần, vì còn các giờ chưa có dữ liệu.

### 3.7 Tần suất vượt ngưỡng cấu hình cảnh báo

![Tỷ lệ mẫu vượt các ngưỡng cấu hình cảnh báo](../results/week2_charts/08_exceedance.png)

Hình 3.7 Tỷ lệ mẫu vượt các ngưỡng cấu hình cảnh báo

Bảng 3.6 Mẫu thỏa ít nhất một điều kiện cảnh báo

| Đô thị | Sinh viên | Tổng mẫu | Mẫu vượt | Tỷ lệ % |
| --- | --- | --- | --- | --- |
| Đà Nẵng | Tiến Sơn | 9 | 0 | 0,0 |
| Hà Nội | Tiến Sơn | 9 | 9 | 100,0 |
| TP. Hồ Chí Minh | Tiến Sơn | 9 | 0 | 0,0 |
| Đà Nẵng | Ngọc Quyên | 19 | 0 | 0,0 |
| Hà Nội | Ngọc Quyên | 19 | 19 | 100,0 |
| TP. Hồ Chí Minh | Ngọc Quyên | 19 | 0 | 0,0 |

Điều kiện cấu hình là AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³. Cả 9 và 19 mẫu Hà Nội đồng thời vượt hai ngưỡng; hai đô thị còn lại không có mẫu vượt trong tập Tuần 2. Các ngưỡng là tham số cảnh báo của dự án, không được gọi là giới hạn an toàn của một quy chuẩn y tế.

Số mẫu vượt điều kiện và số thông điệp SNS là hai đại lượng khác nhau: một lần gọi có thể tạo nhiều thông báo, số mẫu phân tích còn phụ thuộc phạm vi thời gian và tệp lưu. Báo cáo không dùng số bản ghi vượt để suy ra số email đã nhận hoặc đã đọc.

### 3.8 Đối chiếu hai báo cáo dữ liệu theo đô thị và giờ

![AQI và PM2.5 trung bình tại các giờ quan trắc chung](../results/week2_charts/09_matched_account_difference.png)

Hình 3.8 AQI và PM2.5 trung bình tại các giờ quan trắc chung

Bảng 3.7 Giá trị trung bình và chênh lệch tại bảy giờ quan trắc chung

| Đô thị | Giờ chung | AQI TB hai báo cáo | PM2.5 TB hai báo cáo | Δ nhiệt độ °C | Δ độ ẩm điểm % |
| --- | --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | 7 | 78,71 | 23,17 | -0,19 | +0,57 |
| Hà Nội | 7 | 163,29 | 73,66 | -0,19 | +1,29 |
| Đà Nẵng | 7 | 35,43 | 6,34 | 0,00 | -0,57 |

Hai bộ báo cáo có bảy giờ quan trắc chung cho mỗi đô thị, tổng cộng 21 nhóm đối chiếu. Tại từng nhóm, AQI, PM2.5 và PM10 bằng nhau trước khi làm tròn; vì vậy chênh lệch của các chỉ số ô nhiễm bằng 0. Hình 3.8 trình bày giá trị thực để thể hiện mức ô nhiễm trong phạm vi giờ chung. Các giá trị này khác trung bình toàn bộ mẫu Tuần 2 vì phạm vi tính chỉ gồm bảy giờ chung.

Nhiệt độ và độ ẩm vẫn có khác biệt. Chênh lệch được tính bằng giá trị của sinh viên Ngọc Quyên trừ sinh viên Tiến Sơn, sau khi lấy trung bình riêng trong từng giờ và cho mỗi giờ cùng trọng số. Δ độ ẩm dùng điểm phần trăm; số gần 0 được hiển thị 0,00 ở độ chính xác hai chữ số thập phân. Số liệu gốc và số mẫu của từng giờ được giữ trong CSV đối chiếu.

### 3.9 Tương quan Pearson và Spearman

Bảng 3.8 Pearson giữa PM2.5 và khí tượng

| Đô thị | Sinh viên | n | Nhiệt độ | Độ ẩm | Gió |
| --- | --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | Tiến Sơn | 9 | -0,7893 | 0,7744 | -0,4588 |
| TP. Hồ Chí Minh | Ngọc Quyên | 19 | -0,7462 | 0,7263 | -0,6262 |
| Hà Nội | Tiến Sơn | 9 | -0,9918 | 0,9857 | -0,5904 |
| Hà Nội | Ngọc Quyên | 19 | -0,9685 | 0,9601 | -0,4373 |
| Đà Nẵng | Tiến Sơn | 9 | 0,8074 | -0,7121 | 0,1220 |
| Đà Nẵng | Ngọc Quyên | 19 | 0,8227 | -0,6787 | 0,2080 |

![Tương quan PM2.5 với khí tượng trong tập mẫu Tuần 2](../results/week2_charts/10_correlations.png)

Hình 3.9 Tương quan PM2.5 với khí tượng trong tập mẫu Tuần 2

Tại Hà Nội, Pearson PM2.5 với nhiệt độ lần lượt là −0,9918 và −0,9685; với độ ẩm là 0,9857 và 0,9601. Đà Nẵng có chiều liên hệ nhiệt độ dương trong cả hai bộ dữ liệu. Spearman được tính trên thứ hạng, dùng hạng trung bình khi nhiều giá trị quan trắc bằng nhau.

Chuỗi ngắn, mẫu gần nhau theo thời gian và các biến cùng đổi theo giờ có thể tạo hệ số lớn. Chúng em không dùng các hệ số này để chứng minh cơ chế khí quyển, kiểm định nhân quả hoặc khả năng dự báo. CSV giữ cả Pearson, Spearman và n để người đọc đối chiếu.

### 3.10 Quan sát trực tiếp quan hệ nhiệt độ và PM2.5

![Quan hệ giữa nhiệt độ và PM2.5 trên các bản ghi thực tế](../results/week2_charts/11_pm25_temperature.png)

Hình 3.10 Quan hệ giữa nhiệt độ và PM2.5 trên các bản ghi thực tế

Biểu đồ phân tán sử dụng từng bản ghi gốc và tách ba đô thị bằng ba khung. Vị trí điểm giúp nhìn thấy độ phủ nhiệt độ nhỏ của mẫu và các điểm gần nhau trong bộ dữ liệu của sinh viên Ngọc Quyên. Trục PM2.5 của các khung được ghi rõ; các khung dùng thang riêng để giữ khả năng đọc từng đô thị.

Biểu đồ phân tán bổ sung góc nhìn về khoảng biến thiên của các chỉ số trong từng bộ báo cáo dữ liệu. Nhiều điểm gần nhau có thể phản ánh các trạng thái môi trường tương tự; vì vậy cần xem cả số giờ quan trắc và độ phủ dữ liệu khi diễn giải cỡ mẫu.

### 3.11 Các khí ô nhiễm còn lại

Bảng 3.9 Nồng độ khí trung bình µg/m³

| Đô thị | Sinh viên | CO | NO₂ | SO₂ | O₃ |
| --- | --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | Tiến Sơn | 1.292,22 | 37,74 | 27,18 | 49,89 |
| TP. Hồ Chí Minh | Ngọc Quyên | 1.248,37 | 35,31 | 27,64 | 56,53 |
| Hà Nội | Tiến Sơn | 936,44 | 51,20 | 51,16 | 99,78 |
| Hà Nội | Ngọc Quyên | 927,16 | 47,71 | 51,44 | 107,21 |
| Đà Nẵng | Tiến Sơn | 432,22 | 6,08 | 3,66 | 71,11 |
| Đà Nẵng | Ngọc Quyên | 461,42 | 5,56 | 3,45 | 74,00 |

![CO NO₂ và O₃ trung bình theo đô thị và nguồn dữ liệu](../results/week2_charts/12_gaseous_pollutants.png)

Hình 3.11 CO NO₂ và O₃ trung bình theo đô thị và nguồn dữ liệu

CO, NO₂, SO₂ và O₃ được lưu với đơn vị µg/m³. Bảng trình bày đủ bốn khí; hình thể hiện CO, NO₂ và O₃ trên các khung riêng. CSV thống kê giữ độ lệch chuẩn, trung vị, tứ phân vị và cực trị của từng khí theo đô thị và sinh viên.

### 3.12 Đối chiếu với báo cáo Tuần 1

a) Đối chiếu trực tiếp với bộ báo cáo Tuần 1 đã lưu

Bộ báo cáo Tuần 1 có 156 bản ghi, 52 mẫu mỗi đô thị, bao gồm dữ liệu lịch sử nạp bổ sung. Mẫu Tuần 2 có 9 mẫu mỗi đô thị của sinh viên Tiến Sơn và 19 mẫu của sinh viên Ngọc Quyên. Hai bảng dưới dùng đúng bộ 156 dòng làm mốc đối chiếu; Δ là trung bình Tuần 2 trừ trung bình trong bộ báo cáo Tuần 1, tính từ giá trị gốc trước khi làm tròn.

Bảng 3.10 Đối chiếu AQI trung bình với bộ báo cáo Tuần 1

| Đô thị | Bộ Tuần 1<br>(n=52) | Tiến Sơn<br>Tuần 2 (n=9) | Ngọc Quyên<br>Tuần 2 (n=19) | Δ Tiến Sơn | Δ Ngọc Quyên |
| --- | --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | 107,79 | 78,00 | 79,05 | -29,79 | -28,74 |
| Hà Nội | 67,56 | 163,56 | 163,05 | 96,00 | 95,49 |
| Đà Nẵng | 74,67 | 35,44 | 35,37 | -39,23 | -39,30 |

Bảng 3.11 Đối chiếu PM2.5 trung bình (µg/m³) với bộ báo cáo Tuần 1

| Đô thị | Bộ Tuần 1<br>(n=52) | Tiến Sơn<br>Tuần 2 (n=9) | Ngọc Quyên<br>Tuần 2 (n=19) | Δ Tiến Sơn | Δ Ngọc Quyên |
| --- | --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | 37,03 | 23,38 | 22,92 | -13,65 | -14,11 |
| Hà Nội | 15,36 | 76,66 | 75,11 | 61,29 | 59,74 |
| Đà Nẵng | 14,23 | 6,38 | 6,46 | -7,85 | -7,77 |

So với bộ báo cáo Tuần 1, AQI trung bình mẫu Hà Nội cao hơn 96,00 điểm trong bộ dữ liệu của sinh viên Tiến Sơn và 95,49 điểm trong bộ dữ liệu của sinh viên Ngọc Quyên; PM2.5 cao hơn 61,29 và 59,74 µg/m³. TP. Hồ Chí Minh và Đà Nẵng có trung bình AQI, PM2.5 thấp hơn trong mẫu Tuần 2. Thứ tự AQI trung bình đổi từ TP. Hồ Chí Minh – Đà Nẵng – Hà Nội sang Hà Nội – TP. Hồ Chí Minh – Đà Nẵng. Đây là khác biệt giữa các tập mẫu có độ phủ không bằng nhau, chưa đủ kết luận xu hướng của toàn bộ hai tuần.

![AQI trung bình: bộ báo cáo Tuần 1 và mẫu Tuần 2](../results/week2_charts/17_submitted_week1_aqi.png)

Hình 3.12 AQI trung bình: bộ báo cáo Tuần 1 và mẫu Tuần 2

![PM2.5 trung bình: bộ báo cáo Tuần 1 và mẫu Tuần 2](../results/week2_charts/18_submitted_week1_pm25.png)

Hình 3.13 PM2.5 trung bình: bộ báo cáo Tuần 1 và mẫu Tuần 2

Hình 3.12 và Hình 3.13 sử dụng bộ 156 bản ghi của báo cáo Tuần 1 (52 mẫu mỗi đô thị) làm mốc chung. Mẫu Tuần 2 có 9 mẫu của sinh viên Tiến Sơn và 19 mẫu của sinh viên Ngọc Quyên cho mỗi đô thị. Hai nguồn được trình bày riêng; chênh lệch giữa các tập mẫu không đại diện cho xu hướng toàn bộ tuần.

![Hình 3.14 Phân bố cấp AQI trong báo cáo Tuần 1 và mẫu Tuần 2](../results/week2_charts/19_week1_category_comparison.png)

Hình 3.14 Phân bố cấp AQI trong báo cáo Tuần 1 và mẫu Tuần 2

Bộ báo cáo Tuần 1 của TP. Hồ Chí Minh có 25,0% mẫu mức trung bình, 67,3% mức không tốt cho nhóm nhạy cảm và 7,7% mức không tốt. Trong mẫu Tuần 2, toàn bộ mẫu TP. Hồ Chí Minh ở mức trung bình; Hà Nội ở mức không tốt và Đà Nẵng ở mức tốt. Mẫu số là 52 cho Tuần 1, 9 cho sinh viên Tiến Sơn và 19 cho sinh viên Ngọc Quyên ở Tuần 2. Các tỷ lệ mô tả từng tập mẫu đã lưu.

![Hình 3.15 Tương quan PM2.5 với khí tượng trong hai phạm vi tuần](../results/week2_charts/20_week1_weather_correlation_comparison.png)

Hình 3.15 Tương quan PM2.5 với khí tượng trong hai phạm vi tuần

Hình giữ cùng cách tính Pearson cho nhiệt độ, độ ẩm và tốc độ gió với PM2.5 trong từng đô thị. Bộ Tuần 1 dùng 52 cặp mỗi đô thị; hai bộ Tuần 2 lần lượt dùng 9 và 19 cặp. Các hệ số được đọc cùng cỡ mẫu và phạm vi thời gian; sự thay đổi dấu hoặc độ lớn của r chưa đủ kết luận một cơ chế tác động hay xu hướng dài hạn.

b) Đối chiếu theo ranh giới tuần trong cùng lần xuất mới

Phép đối chiếu tiếp theo lọc hai tuần từ cùng lần xuất mới trong bộ dữ liệu của từng sinh viên. Mẫu Tuần 1 có 42 dòng mỗi đô thị trong bộ của sinh viên Tiến Sơn và 41 trong bộ của sinh viên Ngọc Quyên. Phạm vi này khác mốc 52 mẫu trong hai bảng trên; Hình 3.16 minh họa riêng phép lọc này.

Bảng 3.12 AQI theo ranh giới tuần trong lần xuất mới

| Đô thị | Sinh viên | n Tuần 1 | n Tuần 2 | AQI Tuần 1 | AQI Tuần 2 |
| --- | --- | --- | --- | --- | --- |
| Đà Nẵng | Tiến Sơn | 42 | 9 | 65,60 | 35,44 |
| Hà Nội | Tiến Sơn | 42 | 9 | 65,74 | 163,56 |
| TP. Hồ Chí Minh | Tiến Sơn | 42 | 9 | 111,17 | 78,00 |
| Đà Nẵng | Ngọc Quyên | 41 | 19 | 63,95 | 35,37 |
| Hà Nội | Ngọc Quyên | 41 | 19 | 69,10 | 163,05 |
| TP. Hồ Chí Minh | Ngọc Quyên | 41 | 19 | 112,27 | 79,05 |

![So sánh các mẫu thuộc Tuần 1 và Tuần 2 trong dữ liệu vừa tải](../results/week2_charts/16_week_comparison.png)

Hình 3.16 So sánh các mẫu thuộc Tuần 1 và Tuần 2 trong dữ liệu vừa tải

Các mẫu thuộc Tuần 1 trong dữ liệu vừa tải có 42 mẫu mỗi đô thị ở bộ dữ liệu của sinh viên Tiến Sơn và 41 ở bộ dữ liệu của sinh viên Ngọc Quyên; Tuần 2 có 9 và 19. Mẫu Hà Nội tăng AQI trung bình, còn TP. Hồ Chí Minh và Đà Nẵng giảm trong cả hai nguồn. Đây là so sánh mô tả hai tập mẫu với độ phủ khác nhau, chưa xác lập xu hướng dài hạn.

Bảng 3.12 và Hình 3.16 dùng mẫu lọc theo ranh giới tuần trong lần xuất mới. Bảng 3.10 và Bảng 3.11 dùng bộ báo cáo Tuần 1 đã lưu, bao gồm phần lịch sử nạp bổ sung. Hai phạm vi được giữ riêng để giải thích rõ sự khác biệt về số mẫu và giá trị trung bình.

## Chương 4 Phân tích vận hành Lambda và SNS

### 4.1 Thời gian thực thi và bộ nhớ Lambda

Bảng 4.1 Thống kê các dòng REPORT thuộc Tuần 2

| Sinh viên | Lượt | Duration TB ms | P95 ms | Max ms | RAM max MB |
| --- | --- | --- | --- | --- | --- |
| Tiến Sơn | 9 | 2.638,08 | 3.073,78 | 3.077,11 | 101 |
| Ngọc Quyên | 19 | 2.703,82 | 3.111,73 | 3.132,36 | 101 |

![Phân bố thời gian Lambda từ các dòng REPORT thuộc Tuần 2](../results/week2_charts/13_lambda_runtime.png)

Hình 4.1 Phân bố thời gian Lambda từ các dòng REPORT thuộc Tuần 2

Các dòng REPORT đã đọc gồm 9 lượt trong báo cáo dữ liệu của sinh viên Tiến Sơn và 19 lượt trong báo cáo của sinh viên Ngọc Quyên thuộc Tuần 2. Duration trung bình là 2.638,08 ms và 2.703,82 ms; P95 là 3.073,78 ms và 3.111,73 ms. Max Memory Used lớn nhất là 101 MB trên cấu hình 256 MB, tương ứng 39,45% dung lượng được cấp trong các lượt có log.

Billed Duration được phân tích riêng và không thay thế Duration. Log REPORT mô tả các lượt đã đọc, không chứng minh tất cả các khoảng thời gian của tuần đều có một lượt xử lý. Không nhân số giờ dự kiến với thời gian trung bình để tạo ra chi phí tháng giả định.

### 4.2 Lịch thu thập và thông báo SNS

Bảng 4.2 Số liệu SNS và đăng ký nhận thông báo

| Sinh viên | Đăng ký đã xác nhận | Published | Delivered | Failed |
| --- | --- | --- | --- | --- |
| Tiến Sơn | 1 | 59 | 59 | 0 |
| Ngọc Quyên | 2 | 68 | 136 | 0 |

CloudWatch trả về Published là 59 và 68, Delivered là 59 và 136 trong phạm vi Tuần 2. Báo cáo dữ liệu của sinh viên Ngọc Quyên ghi nhận hai đăng ký email đã xác nhận, nên một thông điệp có thể được giao tới nhiều đích. Delivered là số lượt giao tới đích dịch vụ, không xác nhận người nhận đã đọc thư.

Các tổng chỉ số được giữ nguyên theo phản hồi AWS. Chúng không được dùng để suy ra số mẫu môi trường, vì phạm vi ghi nhận dịch vụ và thời điểm API thu thập không đồng nhất với từng tệp dữ liệu.

### 4.3 Đối chiếu sự nhất quán của chỉ số vận hành

Bảng 4.3 Invocations và Errors trong dữ liệu trả về

| Sinh viên | Invocations | Errors | Throttles | Tỷ lệ lỗi |
| --- | --- | --- | --- | --- |
| Tiến Sơn | 9 | 150 | 0 | Không tính: Errors > Invocations |
| Ngọc Quyên | 19 | 294 | 0 | Không tính: Errors > Invocations |

AWS trả về Errors bằng 150 và 294, lớn hơn Invocations bằng 9 và 19 trong cùng phạm vi chọn. Các tổng này không thỏa điều kiện để diễn giải Errors/Invocations thành tỷ lệ lỗi của hàm. Báo cáo ghi rõ mâu thuẫn và để tỷ lệ lỗi không xác định, thay vì đưa một phần trăm vượt 100% hoặc tự thay Errors bằng 0.

Trạng thái Alarm được ghi nhận là OK trong dữ liệu Tuần 2, trong khi chuỗi Errors có vấn đề nhất quán. Trạng thái tại một thời điểm và tổng chỉ số qua nhiều giờ là hai nguồn riêng; không dùng một trong hai để suy diễn hệ thống vận hành không có lỗi. CSV giữ tất cả các điểm chỉ số, thống kê, thời gian UTC và tên metric để kiểm tra tiếp.

## Chương 5 Phân tích truy vấn và sử dụng tài nguyên

### 5.1 Đối chứng hiệu quả lọc phân vùng

Bảng 5.1 Dung lượng quét với cùng tập kết quả

| Sinh viên | Bản ghi | Chỉ lọc thời gian byte | Thêm phân vùng byte | Giảm quét % |
| --- | --- | --- | --- | --- |
| Tiến Sơn | 27 | 114.736 | 15.193 | 86,76 |
| Ngọc Quyên | 57 | 129.715 | 32.067 | 75,28 |

![Đối chứng dung lượng quét với cùng số bản ghi Tuần 2](../results/week2_charts/14_partition_scan.png)

Hình 5.1 Đối chứng dung lượng quét với cùng số bản ghi Tuần 2

Hai truy vấn đối chứng trả cùng số bản ghi Tuần 2 trong từng bộ báo cáo dữ liệu. Bộ của sinh viên Tiến Sơn giảm byte quét từ 114.736 xuống 15.193, tương ứng 86,76%; bộ của sinh viên Ngọc Quyên giảm từ 129.715 xuống 32.067, tương ứng 75,28%. Hai truy vấn dùng cùng điều kiện thời gian và khác điều kiện khóa phân vùng.

Thời gian engine của truy vấn có thêm phân vùng trong lần đo này là 1.402 ms và 1.194 ms, dài hơn truy vấn chỉ lọc thời gian 1.213 ms và 755 ms. Vì vậy giảm byte quét không đồng nghĩa giảm thời gian ở mọi lượt chạy; đây là một cặp đo trên tập dữ liệu nhỏ.

### 5.2 Hai mươi bốn truy vấn phân tích mới

Bảng 5.2 Kết quả thực thi 12 loại truy vấn trong bộ dữ liệu của từng sinh viên

| Truy vấn | Dòng Tiến Sơn | Dòng Ngọc Quyên | ms Tiến Sơn | ms Ngọc Quyên |
| --- | --- | --- | --- | --- |
| raw all | 204 | 231 | 953 | 1297 |
| raw week2 | 27 | 57 | 1458 | 1304 |
| city week2 | 3 | 3 | 1127 | 1196 |
| hour city week2 | 27 | 27 | 1513 | 1226 |
| day city week2 | 6 | 6 | 1709 | 1504 |
| category week2 | 3 | 3 | 1113 | 1380 |
| correlation week2 | 3 | 3 | 1326 | 1339 |
| partition all | 6 | 6 | 866 | 800 |
| quality all | 1 | 1 | 908 | 966 |
| scan all count | 1 | 1 | 777 | 898 |
| scan week2 time only | 1 | 1 | 1213 | 755 |
| scan week2 partition | 1 | 1 | 1402 | 1194 |

![Thời gian thực thi 24 truy vấn trong hai báo cáo dữ liệu](../results/week2_charts/15_query_time.png)

Hình 5.2 Thời gian thực thi 24 truy vấn trong hai báo cáo dữ liệu

Tất cả 24 truy vấn mới đều SUCCEEDED. Mỗi báo cáo dữ liệu có 12 truy vấn về raw toàn bộ, raw Tuần 2, đô thị, giờ, ngày, cấp AQI, tương quan, phân vùng, chất lượng và ba phép đối chứng dung lượng quét. Mã thực thi và hash CSV được lưu theo từng bộ dữ liệu để đối chiếu.

### 5.3 Lịch sử truy vấn và phạm vi lỗi

Bảng 5.3 Lịch sử truy vấn của dự án trước đợt phân tích mới

| Sinh viên | Tổng lượt | SUCCEEDED | FAILED |
| --- | --- | --- | --- |
| Tiến Sơn | 52 | 31 | 21 |
| Ngọc Quyên | 92 | 91 | 1 |

Lịch sử ghi nhận 52 lượt truy vấn trong báo cáo dữ liệu của sinh viên Tiến Sơn và 92 lượt trong báo cáo của sinh viên Ngọc Quyên, trước đợt 24 truy vấn mới. Số lượt FAILED tương ứng là 21 và 1. Lịch sử có cả truy vấn cấu hình và phân tích; các số này được trình bày riêng với kết quả của đợt truy vấn vừa xuất.

### 5.4 Chi phí từ Cost Explorer

Bảng 5.4 Chi phí ghi nhận trong phạm vi Tuần 2 làm tròn đến cent

| Sinh viên | Hiển thị đến cent | Đơn vị | Estimated |
| --- | --- | --- | --- |
| Tiến Sơn | 0,00 | USD | Có |
| Ngọc Quyên | 0,03 | USD | Có |

Trong phạm vi Tuần 2, UnblendedCost được trình bày đến cent là 0,00 USD trong báo cáo dữ liệu của sinh viên Tiến Sơn và 0,03 USD trong báo cáo dữ liệu của sinh viên Ngọc Quyên. Tổng giá trị trước khi làm tròn của sinh viên Tiến Sơn có độ lớn dưới 0,000001 USD, nên được hiển thị 0,00 USD ở độ chính xác này. Mức hiển thị 0,00 USD không đồng nghĩa với kết luận dự án hoàn toàn miễn phí.

Chi phí dự kiến: 0,05 USD cho phần thực hành của sinh viên Tiến Sơn trong Tuần 2. Đây là mức dự kiến do nhóm đề xuất; số liệu ghi nhận từ Cost Explorer được trình bày riêng trong Bảng 5.4.

Cả hai kết quả đều có cờ Estimated. Đây là số liệu ước tính tại thời điểm trích xuất Cost Explorer, được tổng hợp theo dịch vụ và ngày trong môi trường AWS của từng sinh viên; chưa phải hóa đơn cuối cùng hoặc chi phí riêng của dự án được phân bổ bằng tag. Các tệp CSV lưu nguyên giá trị trước khi làm tròn, đơn vị và trạng thái ước tính để đối chiếu.

## Chương 6 Tổng hợp kết quả Tuần 2

### 6.1 Sản phẩm dữ liệu và phân tích

Bảng 6.1 Sản phẩm đi kèm và phạm vi

| Sản phẩm | Nội dung |
| --- | --- |
| Dữ liệu nguồn | 435 bản ghi raw trong hai báo cáo dữ liệu; CSV và tệp NDJSON được lưu riêng theo sinh viên. |
| Mẫu Tuần 2 | 84 dòng nguồn: 27 của sinh viên Tiến Sơn và 57 của sinh viên Ngọc Quyên; phân tích riêng từng bộ dữ liệu. |
| Kết quả truy vấn | 24 truy vấn mới thành công; CSV gốc, mã thực thi và metadata theo nguồn. |
| Phân tích | 27 CSV tổng hợp và đối chiếu về môi trường, chất lượng, dịch vụ, truy vấn và chi phí. |
| Trực quan hóa | 20 biểu đồ được dựng từ các CSV tương ứng; cùng dữ liệu trong Excel và báo cáo. |
| Báo cáo | Word có mục lục liên kết và bản PDF đã kiểm tra bố cục. |

### 6.2 Kết luận trong phạm vi mẫu đã thu thập

Hai báo cáo dữ liệu Tuần 2 của sinh viên Tiến Sơn và sinh viên Ngọc Quyên cùng ghi nhận Hà Nội có AQI và PM2.5 cao nhất trong ba đô thị; các mẫu Hà Nội đều thỏa ngưỡng cảnh báo của dự án. Đà Nẵng có AQI thấp nhất, TP. Hồ Chí Minh nằm giữa. Phân bố mẫu, trung vị, diễn biến theo giờ và đối chiếu cùng giờ được trình bày riêng để giải thích kết quả của từng bộ dữ liệu.

Mỗi bộ báo cáo dữ liệu hiện bao phủ hai ngày và 9 giờ quan trắc, nên các kết luận giới hạn trong mẫu đã có của Tuần 2. Các hệ số tương quan lớn không chứng minh quan hệ nhân quả. Phép đối chứng lọc phân vùng ghi nhận giảm byte quét; thời gian engine được diễn giải theo từng lượt cụ thể.

Chúng em đã đối chiếu số liệu môi trường với S3 và Athena, đọc trạng thái lịch, SNS, Lambda và các chỉ số vận hành. Các mâu thuẫn giữa Errors và Invocations được giữ rõ trong báo cáo. Phân công và thời gian 19,5 giờ của nhóm được ghi thống nhất trong nhật ký và báo cáo.
