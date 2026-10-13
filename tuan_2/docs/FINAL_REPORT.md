# Báo cáo tiến độ Tuần 2

## TÓM TẮT

Báo cáo Tuần 2 trình bày việc hoàn thiện các chức năng thu thập, lưu trữ, cảnh báo và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS Learner Lab. Chúng em tiếp tục sử dụng mô hình không máy chủ đã thiết kế ở Tuần 1 và tổ chức mã nguồn theo từng nhóm chức năng.

Hệ thống thu thập dữ liệu Open-Meteo cho TP. Hồ Chí Minh, Hà Nội và Đà Nẵng, chuẩn hóa bản ghi gồm 23 trường và lưu theo phân vùng thời gian trên Amazon S3. EventBridge kích hoạt Lambda định kỳ; Secrets Manager quản lý cấu hình; SNS tiếp nhận thông báo vượt ngưỡng; Glue và Athena cung cấp lược đồ và truy vấn phân tích.

Báo cáo Tuần 2 dùng bộ CSV Athena đã lưu, gồm 156 bản ghi và 52 mẫu mỗi đô thị. Năm kết quả truy vấn và bốn biểu đồ mô tả AQI, nồng độ bụi, biến thiên theo giờ và tương quan khí tượng. Hồ sơ vận hành đã lưu ghi nhận một lượt Lambda thu thập 3 bản ghi và gửi 2 cảnh báo; năm mã truy vấn trong hồ sơ khớp các CSV đang sử dụng. Báo cáo phân biệt kết quả vận hành tại mốc đã lưu với phần hoàn thiện mã nguồn và kiểm tra cục bộ sau đó.

## LỜI MỞ ĐẦU

Học phần Điện toán đám mây giúp chúng em vận dụng các dịch vụ quản lý trên AWS vào một luồng dữ liệu cụ thể. Bài toán thời tiết và chất lượng không khí cho phép theo dõi quá trình từ thu thập qua API, chuẩn hóa bản ghi, lưu trữ đến truy vấn và trình bày kết quả.

Báo cáo tập trung vào cấu hình, trình tự xử lý và số liệu đối chiếu của Tuần 2. Bộ source đi kèm gồm chức năng Lambda, lược đồ Athena, chương trình quản lý dịch vụ và chương trình xuất dữ liệu bằng Python SDK. Kho dự án: https://github.com/JasonTM17/WeatherAWS_FinalTerm.git

Đề tài được thực hiện bởi nhóm sinh viên:

- Nguyễn Tiến Sơn — MSSV 24110054: S3, Secrets Manager, Lambda và SNS.

- Trần Thị Ngọc Quyên — MSSV 24110051: Glue, Athena, biểu đồ và đối chiếu dữ liệu.

Các chương lần lượt trình bày mục tiêu và kiến trúc, chức năng Lambda, lịch thu thập và cảnh báo, mô hình dữ liệu và phân tích, kiểm tra kết quả, sử dụng tài nguyên và tổng hợp công việc của nhóm.

## Chương 1 Tổng quan nhiệm vụ và kiến trúc Tuần 2

### 1.1 Mục tiêu và phạm vi Tuần 2

Thu thập dữ liệu môi trường định kỳ là bài toán phù hợp để nghiên cứu cách kết hợp lịch sự kiện, xử lý không máy chủ và lưu trữ trên đám mây. Trong phạm vi học phần, nhóm sử dụng dữ liệu công khai để xây dựng luồng thu thập và phân tích cho ba đô thị.

Mục tiêu Tuần 2 là kết nối các dịch vụ nền tảng thành luồng xử lý có cấu hình rõ ràng, thống nhất lược đồ bản ghi và xuất được các kết quả truy vấn phục vụ báo cáo. Các thống kê chỉ mô tả bộ dữ liệu đã lưu, không đại diện cho chất lượng không khí dài hạn.

### 1.2 Phân công thực hiện

Chúng em phân công hai nhóm chức năng và cùng thực hiện kiến trúc, tích hợp, rà soát số liệu và báo cáo. Theo nhật ký nhóm xác nhận, Nguyễn Tiến Sơn thực hiện 10,0 giờ và Trần Thị Ngọc Quyên thực hiện 9,5 giờ trong Tuần 2, tổng cộng 19,5 giờ. Phần việc và thời gian được trình bày tại Bảng 1.1.

Bảng 1.1 Phân công thực hiện Tuần 2

| Thành viên | Phụ trách chính | Phối hợp | Giờ |
| --- | --- | --- | --- |
| Nguyễn Tiến Sơn<br>24110054 | S3, Secrets Manager, Lambda và SNS. | Kiến trúc, tích hợp và báo cáo. | 10,0 |
| Trần Thị Ngọc Quyên<br>24110051 | Glue, Athena, biểu đồ và đối chiếu dữ liệu. | Kiến trúc, tích hợp và báo cáo. | 9,5 |

### 1.3 Kiến trúc tổng thể

Luồng xử lý kết nối lịch sự kiện, hàm thu thập, lưu trữ, cảnh báo và truy vấn. Mỗi dịch vụ đảm nhiệm một chức năng; các tham số dùng chung được quản lý qua cấu hình triển khai.

- Amazon EventBridge: quy tắc lịch kích hoạt Lambda mỗi giờ với biểu thức rate(1 hour).

- AWS Secrets Manager: quản lý vị trí thu thập, tọa độ và ngưỡng cảnh báo của dự án.

- AWS Lambda: nhận sự kiện, gọi API, chuẩn hóa bản ghi, xác định cấp AQI và ghi dữ liệu.

- Amazon SNS: tiếp nhận thông báo cảnh báo từ Lambda khi điều kiện cấu hình được thỏa mãn.

- Amazon S3 Data Lake: Hồ dữ liệu lưu trữ các tệp NDJSON có cấu trúc phân vùng theo thời gian (year/month/day).

- AWS Glue Data Catalog & Amazon Athena: Cơ sở dữ liệu metadata và công cụ truy vấn SQL không máy chủ cho phép phân tích dữ liệu lớn trực tiếp trên S3.

- Matplotlib: tạo bốn biểu đồ từ CSV Athena để so sánh đô thị, theo dõi biến thiên theo giờ, phân bố cấp AQI và tương quan khí tượng.

- Amazon CloudWatch: Giám sát chỉ số tài nguyên, phát hiện lỗi phát sinh và hiển thị Dashboard điều hành thời gian thực.

![Hình phân tích](../../docs/architecture.png)

Hình 1.1 Kiến trúc và luồng dữ liệu của hệ thống

### 1.4 Danh mục dịch vụ và cấu hình

Môi trường mục tiêu là AWS Academy Learner Lab tại us-east-1, sử dụng LabRole. Trong bộ source, account được xác định từ phiên đăng nhập; tên bucket và ARN được tạo theo account, thay vì cố định theo một tài khoản cụ thể.

Bảng 1.2 Danh mục dịch vụ và cấu hình trong bộ source Tuần 2

| Dịch vụ | Tài nguyên hoặc cấu hình | Vai trò |
| --- | --- | --- |
| Lambda | WeatherCollectorLambda; Python 3.12; 256 MB; 60 giây; LabRole. | Thu thập, chuẩn hóa và ghi dữ liệu. |
| EventBridge | WeatherCollectionSchedule; rate(1 hour). | Kích hoạt xử lý định kỳ. |
| Secrets Manager | weather/api_config. | Quản lý vị trí và ngưỡng cấu hình. |
| SNS | weather-airquality-alerts; giao thức email. | Tiếp nhận thông báo từ Lambda. |
| S3 | Bucket dự án theo account; vùng raw và athena-results. | Lưu dữ liệu và kết quả truy vấn. |
| Glue | weather_aqi_db; weather_airquality_records. | Quản lý lược đồ và phân vùng. |
| Athena | Năm truy vấn phân tích dữ liệu S3. | Tính thống kê và xuất CSV. |
| CloudWatch | WeatherCollector-Errors-Alarm và dashboard của dự án. | Theo dõi lỗi, lượt gọi và thời gian xử lý. |

## Chương 2 Thiết kế chức năng thu thập bằng Lambda

### 2.1 Tổ chức chức năng xử lý

Hàm Lambda được tổ chức thành các nhóm xử lý: đọc cấu hình, gọi API, chuyển đổi kiểu dữ liệu, phân loại AQI, thu thập chuỗi lịch sử, xuất thông báo và ghi S3. Các biến môi trường xác định bucket, secret và SNS topic; hàm nhận sự kiện để lựa chọn chế độ thu thập.

### 2.2 Quản lý cấu hình bằng Secrets Manager

Cấu hình weather/api_config chứa ba vị trí thu thập và các ngưỡng cảnh báo. Hàm đọc cấu hình từ Secrets Manager; nếu không đọc được, cấu hình dự phòng được sử dụng và lỗi được ghi vào log. API công khai được sử dụng trong dự án không yêu cầu khóa API.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Tên cấu hình | weather/api_config |
| Nội dung | Ba vị trí thu thập; các ngưỡng AQI và nồng độ bụi. |
| Dự phòng | Dùng cấu hình nội bộ và ghi log khi đọc secret thất bại. |

Cấu hình dự phòng giúp hàm tiếp tục xử lý trong một số tình huống lỗi. Việc dùng cấu hình dự phòng vẫn cần được nhận biết qua log; nó không chứng minh kết nối Secrets Manager đã hoạt động bình thường.

### 2.3 Thu thập và chuẩn hóa dữ liệu

Mỗi đô thị cần hai lượt gọi API: một lượt lấy chất lượng không khí, một lượt lấy nhiệt độ, độ ẩm, áp suất và tốc độ gió. Mã hiện tại thực hiện các lượt gọi tuần tự, sau đó đưa kết quả vào cùng một bản ghi.

Mỗi bản ghi dữ liệu sau khi thu thập được chuẩn hóa theo schema 23 trường thuộc tính chặt chẽ:

Bảng 2.1: Danh mục chuẩn hóa 23 trường thuộc tính dữ liệu môi trường của hệ thống

| Tên trường | Kiểu | Đơn vị | Ý nghĩa |
| --- | --- | --- | --- |
| record_id | string | — | Mã nhận diện bản ghi. |
| city | string | — | Tên thành phố. |
| latitude | double | ° | Vĩ độ vị trí thu thập. |
| longitude | double | ° | Kinh độ vị trí thu thập. |
| timestamp_utc | string | UTC | Thời điểm của bản ghi theo UTC. |
| timestamp_vn | string | UTC+7 | Thời điểm quy đổi sang giờ Việt Nam. |
| temperature_2m | double | °C | Nhiệt độ không khí ở độ cao 2 m. |
| relative_humidity_2m | double | % | Độ ẩm tương đối ở độ cao 2 m. |
| surface_pressure | double | hPa | Áp suất tại bề mặt. |
| wind_speed_10m | double | km/h | Tốc độ gió ở độ cao 10 m. |
| pm2_5 | double | µg/m³ | Nồng độ bụi PM2.5. |
| pm10 | double | µg/m³ | Nồng độ bụi PM10. |
| carbon_monoxide | double | µg/m³ | Nồng độ CO. |
| nitrogen_dioxide | double | µg/m³ | Nồng độ NO2. |
| sulphur_dioxide | double | µg/m³ | Nồng độ SO2. |
| ozone | double | µg/m³ | Nồng độ O3. |
| us_aqi | int | AQI | Chỉ số chất lượng không khí. |
| aqi_category | string | — | Nhãn phân loại AQI trong hệ thống. |
| hour | int | 0–23 | Giờ UTC dùng để nhóm dữ liệu. |
| collected_at | string | ISO 8601 | Mốc ghi nhận có thông tin múi giờ. |
| year | string | — | Khóa phân vùng năm. |
| month | string | — | Khóa phân vùng tháng. |
| day | string | — | Khóa phân vùng ngày. |

### 2.4 Phân loại chỉ số AQI

Hàm Lambda cài đặt giải thuật phân loại 6 cấp độ chất lượng không khí dựa trên chỉ số tổng hợp us_aqi theo đúng tiêu chuẩn United States Environmental Protection Agency (US EPA):

Bảng 2.2: Bảng tiêu chuẩn phân loại 6 cấp độ chất lượng không khí US EPA AQI

| Khoảng AQI | Nhãn trong dữ liệu | Diễn giải |
| --- | --- | --- |
| 0–50 | Good | Tốt |
| 51–100 | Moderate | Trung bình |
| 101–150 | Unhealthy for Sensitive Groups | Không tốt cho nhóm nhạy cảm |
| 151–200 | Unhealthy | Không tốt |
| 201–300 | Very Unhealthy | Rất không tốt |
| Trên 300 | Hazardous | Nguy hại |

### 2.5 Lưu trữ theo phân vùng trên S3

Dữ liệu được lưu dạng NDJSON, mỗi dòng là một đối tượng JSON. Các bản ghi được gom theo năm, tháng và ngày; tệp được ghi vào phân vùng thời gian tương ứng trong vùng raw của bucket dự án.

Lợi thế của định dạng NDJSON kết hợp phân vùng Hive-style:

- Phân vùng thời gian giúp truy vấn lựa chọn các ngày cần phân tích khi có điều kiện lọc trên khóa phân vùng.

- NDJSON cho phép lưu nhiều bản ghi trong một tệp và sử dụng lược đồ Glue để truy vấn bằng Athena.

- Mỗi tệp có tên riêng để bổ sung dữ liệu mà không ghi đè một tệp đã lưu.

### 2.6 Thu thập hiện tại và nạp bù lịch sử

Hai chế độ thu thập sử dụng chung lược đồ dữ liệu và cách ghi S3:

- Thu thập hiện tại: sự kiện không có yêu cầu nạp bù; mỗi đô thị tạo một bản ghi nếu hai lượt gọi API thành công.

- Nạp bù lịch sử: sự kiện có trường backfill_hours; hàm đọc chuỗi giờ được API trả về và chọn số giờ theo yêu cầu.

Trong xử lý chuỗi lịch sử, các cảm biến ô nhiễm được đọc theo thời gian của mảng AQI; dữ liệu khí tượng được ghép theo timestamp tương ứng. Cách ghép này giữ đúng quan trắc khi hai API trả mốc giờ khác thứ tự. Số bản ghi phụ thuộc độ dài chuỗi API và số đô thị thu thập thành công.

## Chương 3 Lịch thu thập và cảnh báo

### 3.1 Cấu hình lịch thu thập EventBridge

Quy tắc WeatherCollectionSchedule sử dụng biểu thức rate(1 hour) và trỏ tới WeatherCollectorLambda. Bộ source quản lý một lịch thu thập chính để tránh tạo hai lượt kích hoạt đồng thời cho cùng chức năng.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Quy tắc | WeatherCollectionSchedule |
| Chu kỳ | rate(1 hour) |
| Đích xử lý | WeatherCollectorLambda |

### 3.2 Quyền gọi Lambda từ EventBridge

Chính sách của Lambda cho phép dịch vụ EventBridge gọi hàm và ràng buộc nguồn gọi theo ARN của quy tắc lịch. Cấu hình này tách quyền gọi hàm khỏi quyền mà LabRole sử dụng bên trong quá trình xử lý.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Dịch vụ gọi | events.amazonaws.com |
| Hành động được phép | lambda:InvokeFunction |
| Giới hạn nguồn | ARN của WeatherCollectionSchedule |

### 3.3 Topic SNS và đăng ký email

SNS topic weather-airquality-alerts là đích nhận thông báo. Khi đăng ký một địa chỉ email, người nhận cần xác nhận đăng ký trước khi subscription có thể gửi email; việc tạo topic tự nó chưa xác nhận email đã được nhận.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Topic | weather-airquality-alerts |
| Giao thức | Email |
| Điều kiện hoạt động | Subscription được người nhận xác nhận. |

### 3.4 Điều kiện và nội dung thông báo

Hàm Lambda đối chiếu chỉ số đo được với các ngưỡng cảnh báo cấu hình của dự án: us_aqi ≥ 100 hoặc pm2_5 ≥ 35,5 µg/m³. Khi thỏa một trong hai điều kiện, hàm gửi thông báo tới SNS topic đã cấu hình.

Thông điệp chứa thành phố, thời điểm, AQI, cấp phân loại, các nồng độ bụi và điều kiện khí tượng. Kết quả publish được dùng để đếm số thông báo gửi tới SNS; đây là số lần dịch vụ chấp nhận thông điệp, không phải số email người nhận đã đọc.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Nhận diện | Thành phố; thời gian UTC và Việt Nam. |
| Chất lượng không khí | AQI, cấp phân loại, PM2.5, PM10 và ngưỡng cấu hình. |
| Khí tượng | Nhiệt độ, độ ẩm, gió và áp suất. |

## Chương 4 Mô hình dữ liệu và kết quả phân tích

### 4.1 Database và bảng dữ liệu

Để cho phép truy vấn không máy chủ trên hồ dữ liệu S3, nhóm khởi tạo cơ sở dữ liệu weather_aqi_db trên AWS Glue Data Catalog và khai báo bảng ngoại weather_airquality_records sử dụng OpenX JSON SerDe (org.openx.data.jsonserde.JsonSerDe). Lược đồ bảng gồm 20 cột thuộc tính dữ liệu và 3 cột khóa phân vùng:

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Database và bảng | weather_aqi_db.weather_airquality_records |
| Lược đồ | 20 cột dữ liệu và 3 khóa phân vùng năm, tháng, ngày. |
| Định dạng | NDJSON với OpenX JSON SerDe. |

### 4.2 View dữ liệu

View vietnam_weather_aqi cung cấp cách truy cập thống nhất tới bảng dữ liệu. Lược đồ và trường thời gian được giữ rõ ràng để các truy vấn tổng hợp có thể đối chiếu với bản ghi gốc.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Đối tượng | vietnam_weather_aqi |
| Nguồn | weather_airquality_records |
| Vai trò | Cung cấp lớp truy cập thống nhất tới các bản ghi. |

### 4.3 Nạp phân vùng vào Catalog

Các phân vùng được nạp vào Glue Data Catalog để Athena nhận biết vị trí dữ liệu theo ngày. Bộ dữ liệu đang dùng có ba phân vùng thời gian; truy vấn phân tích lấy dữ liệu từ bảng weather_airquality_records.

### 4.4 Năm truy vấn phân tích

#### Truy vấn 1 Thống kê và so sánh chất lượng không khí giữa các đô thị

Truy vấn theo thành phố tính số mẫu, AQI trung bình và cực trị, cùng các đại lượng bụi và khí tượng trung bình. Bảng 4.1 và Bảng 4.2 trình bày toàn bộ các giá trị này.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Nhóm | Thành phố |
| Đại lượng | Số mẫu, AQI trung bình và cực trị, các giá trị bụi và khí tượng trung bình. |

Bảng 4.1 AQI và PM2.5 theo thành phố

| Thành phố | Mẫu | AQI TB | AQI min | AQI max | PM2.5 TB |
| --- | --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | 52 | 107,79 | 95 | 172 | 37,03 |
| Đà Nẵng | 52 | 74,67 | 36 | 155 | 14,23 |
| Hà Nội | 52 | 67,56 | 56 | 80 | 15,36 |

Bảng 4.2 PM10 và khí tượng trung bình theo thành phố

| Thành phố | PM10 µg/m³ | Nhiệt độ °C | Độ ẩm % |
| --- | --- | --- | --- |
| TP. Hồ Chí Minh | 37,35 | 27,79 | 84,71 |
| Đà Nẵng | 17,28 | 28,85 | 74,87 |
| Hà Nội | 16,11 | 24,54 | 76,65 |

![Hình phân tích](../../tuan_2/results/charts/01_aqi_city_comparison.png)

Hình 4.1 AQI trung bình và cực trị của ba đô thị

TP. Hồ Chí Minh có AQI trung bình 107,79, nhỏ nhất 95 và lớn nhất 172; PM2.5 trung bình 37,03 µg/m³. Đà Nẵng có AQI trung bình 74,67 và Hà Nội 67,56. Các giá trị này mô tả 52 mẫu mỗi đô thị; ngưỡng cảnh báo là tham số của hệ thống.

#### Truy vấn 2 Biến thiên ô nhiễm theo 24 khung giờ UTC trong ngày

Truy vấn theo giờ tạo 24 nhóm từ 00 đến 23 UTC. Mỗi nhóm chứa giá trị trung bình AQI, PM2.5, PM10 và số mẫu; số mẫu giữa các giờ không đồng đều.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Nhóm | 24 khung giờ UTC |
| Đại lượng | AQI, PM2.5, PM10 trung bình và số mẫu của mỗi giờ. |

![Hình phân tích](../../tuan_2/results/charts/02_peak_pollution_hours.png)

Hình 4.2 AQI PM2.5 và PM10 trung bình theo giờ UTC

AQI trung bình cao nhất tại giờ 11 UTC với 103,83 và thấp nhất tại giờ 23 với 75,83. PM2.5 cao nhất tại giờ 19 với 25,53 µg/m³ và thấp nhất tại giờ 03 với 18,03 µg/m³. Có 20 nhóm sáu mẫu và bốn nhóm chín mẫu. Dữ liệu này chưa đủ để kết luận nguyên nhân biến động hoặc chu kỳ ô nhiễm điển hình.

Bảng 4.3 AQI PM2.5 và PM10 trung bình theo 24 giờ UTC

| Giờ UTC | AQI TB | PM2.5 µg/m³ | PM10 µg/m³ | Số mẫu |
| --- | --- | --- | --- | --- |
| 00 | 77,00 | 22,81 | 24,06 | 9 |
| 01 | 76,78 | 22,09 | 23,66 | 9 |
| 02 | 76,67 | 18,87 | 20,77 | 9 |
| 03 | 76,67 | 18,03 | 20,04 | 9 |
| 04 | 80,17 | 20,30 | 22,32 | 6 |
| 05 | 80,00 | 20,45 | 22,15 | 6 |
| 06 | 79,67 | 21,17 | 22,77 | 6 |
| 07 | 81,67 | 21,18 | 22,70 | 6 |
| 08 | 86,17 | 21,15 | 22,85 | 6 |
| 09 | 93,50 | 20,55 | 22,05 | 6 |
| 10 | 101,00 | 22,33 | 23,72 | 6 |
| 11 | 103,83 | 25,22 | 26,48 | 6 |
| 12 | 103,67 | 21,67 | 22,92 | 6 |
| 13 | 99,67 | 22,38 | 23,53 | 6 |
| 14 | 93,17 | 22,15 | 23,32 | 6 |
| 15 | 84,00 | 22,60 | 23,78 | 6 |
| 16 | 78,50 | 23,72 | 24,88 | 6 |
| 17 | 78,00 | 24,28 | 25,35 | 6 |
| 18 | 78,00 | 24,38 | 25,48 | 6 |
| 19 | 77,50 | 25,53 | 26,52 | 6 |
| 20 | 77,67 | 25,32 | 26,32 | 6 |
| 21 | 77,33 | 23,77 | 24,68 | 6 |
| 22 | 76,83 | 23,07 | 23,98 | 6 |
| 23 | 75,83 | 23,52 | 24,48 | 6 |

#### Truy vấn 3 Phân bố cấp độ chất lượng không khí theo tiêu chuẩn US EPA

Truy vấn phân bố đếm mẫu của từng cấp AQI trong mỗi đô thị và tính tỷ lệ trên tổng 52 mẫu của đô thị đó. Tổng số mẫu của các cấp được đối chiếu với truy vấn trung bình theo thành phố.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Nhóm | Thành phố và cấp AQI |
| Tỷ lệ | Số mẫu của cấp chia cho tổng số mẫu trong cùng thành phố. |

Bảng 4.4 Phân bố các cấp AQI theo thành phố

| Thành phố | Cấp AQI | Số mẫu | Tỷ lệ % |
| --- | --- | --- | --- |
| Đà Nẵng | Moderate | 39 | 75,0 |
| Đà Nẵng | Good | 6 | 11,5 |
| Đà Nẵng | Unhealthy for Sensitive Groups | 4 | 7,7 |
| Đà Nẵng | Unhealthy | 3 | 5,8 |
| Hà Nội | Moderate | 52 | 100,0 |
| TP. Hồ Chí Minh | Unhealthy for Sensitive Groups | 35 | 67,3 |
| TP. Hồ Chí Minh | Moderate | 13 | 25,0 |
| TP. Hồ Chí Minh | Unhealthy | 4 | 7,7 |

![Hình phân tích](../../tuan_2/results/charts/03_aqi_category_distribution.png)

Hình 4.3 Tỷ lệ mẫu của các cấp AQI theo thành phố

TP. Hồ Chí Minh có 35 mẫu ở cấp không tốt cho nhóm nhạy cảm (67,3%), 13 mẫu trung bình (25,0%) và 4 mẫu không tốt (7,7%). Đà Nẵng có 39 mẫu trung bình (75,0%), 6 mẫu tốt (11,5%), 4 mẫu nhóm nhạy cảm (7,7%) và 3 mẫu không tốt (5,8%). Hà Nội có 52 mẫu trung bình. Đây là tỷ lệ mẫu, không phải tỷ lệ thời gian vận hành.

#### Truy vấn 4 Tương quan Pearson giữa yếu tố Khí tượng và Bụi mịn PM2.5

Hệ số Pearson r được tính riêng cho từng thành phố giữa PM2.5 và nhiệt độ, độ ẩm hoặc tốc độ gió. Dấu của hệ số mô tả chiều liên hệ tuyến tính trong tập mẫu; độ lớn nằm trong khoảng từ −1 đến 1.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Nhóm | Thành phố |
| Đại lượng | Tương quan Pearson giữa PM2.5 và nhiệt độ, độ ẩm hoặc tốc độ gió. |

Bảng 4.5 Hệ số tương quan Pearson với PM2.5

| Thành phố | Nhiệt độ | Độ ẩm | Tốc độ gió |
| --- | --- | --- | --- |
| Hà Nội | 0,6462 | 0,2486 | -0,4846 |
| Đà Nẵng | 0,4798 | -0,3183 | -0,2291 |
| TP. Hồ Chí Minh | -0,6977 | 0,6627 | -0,1536 |

![Hình phân tích](../../tuan_2/results/charts/04_weather_pm25_correlation.png)

Hình 4.4 Tương quan PM2.5 với ba yếu tố khí tượng

Tại TP. Hồ Chí Minh, nhiệt độ có r = −0,6977 và độ ẩm có r = 0,6627 với PM2.5. Tại Hà Nội, tốc độ gió có r = −0,4846. Các hệ số mô tả bộ mẫu hiện có; chúng không chứng minh quan hệ nhân quả hay một cơ chế khí quyển cụ thể.

#### Truy vấn 5 Trích xuất 156 bản ghi dữ liệu gốc

Truy vấn query_raw_weather_aqi_records.sql trích xuất toàn bộ 156 bản ghi gốc lưu ra tệp CSV để phục vụ kiểm định toàn vẹn schema, đối chiếu số liệu và nộp kèm hồ sơ nghiệm thu.

### 4.5 Số liệu thực thi truy vấn Athena

Các chỉ số thực thi được lấy từ tệp query_metrics.csv đã lưu. Thời gian và dung lượng quét phản ánh từng lượt truy vấn cụ thể, không phải cam kết hiệu năng cho mọi khối lượng dữ liệu.

Bảng 4.6 Thời gian thực thi và dung lượng quét của năm truy vấn

| Truy vấn | Dòng | Thời gian ms | Quét byte |
| --- | --- | --- | --- |
| avg aqi by city | 3 | 744 | 87.250 |
| peak pollution hours | 24 | 936 | 87.250 |
| aqi category distribution | 8 | 776 | 87.250 |
| weather correlation | 3 | 930 | 87.250 |
| raw weather aqi records | 156 | 1192 | 87.250 |

Năm lượt truy vấn đều ghi nhận 87.250 byte quét. Thời gian thực thi nằm trong khoảng 744–1.192 ms. Bộ số liệu chưa có thử nghiệm đối chứng không phân vùng, nên không dùng để tính tỷ lệ tiết kiệm dữ liệu quét.

## Chương 5 Đối chiếu dữ liệu và kiểm tra chức năng

### 5.1 Cấu trúc và số lượng bản ghi

Tệp raw_weather_aqi_records.csv chứa 156 dòng, 156 mã bản ghi khác nhau và 23 trường; mỗi đô thị có 52 mẫu. Các phép tổng hợp theo thành phố, giờ và cấp AQI đều có tổng số mẫu 156, giúp phát hiện thiếu hoặc đếm trùng khi đối chiếu. Dữ liệu chất lượng không khí từ Open-Meteo Air Quality API dựa trên sản phẩm mô hình khí quyển CAMS, không phải phép đo trực tiếp tại một trạm. Nguồn dữ liệu: https://open-meteo.com/en/docs/air-quality-api.

### 5.2 Kiểm tra chức năng và tính toàn vẹn dữ liệu

Bộ kiểm tra cục bộ gồm 44 ca cho Lambda, dữ liệu CSV, biểu đồ và chương trình quản lý dịch vụ. Các ca dùng dữ liệu đã lưu và đối tượng AWS giả lập để kiểm tra logic; kết quả không thay thế việc quan sát một lần chạy thật trên AWS.

Bảng 5.1 Phạm vi kiểm tra bộ source hiện tại

| Nhóm kiểm tra | Số ca | Nội dung chính | Kết quả cục bộ |
| --- | --- | --- | --- |
| Lambda | 15 | Chuyển đổi kiểu, phân loại AQI, ghép lịch sử, thu thập, ghi S3 và thông báo. | Đạt |
| Dữ liệu CSV | 12 | Schema, số mẫu, đồng nhất bản sao và xuất dữ liệu đã lưu. | Đạt |
| Biểu đồ | 4 | Sinh bốn hình từ các tệp CSV. | Đạt |
| Python SDK | 13 | Lỗi truy vấn, timeout, phân trang, nguồn ngoại tuyến và điều kiện thu hồi. | Đạt |

### 5.3 Xử lý lỗi và giá trị thiếu

Ba nhóm xử lý lỗi chính trong mã hiện tại gồm:

- Chuyển đổi kiểu: các hàm chuyển đổi dùng giá trị mặc định khi đầu vào không hợp lệ. Mặc định số 0 cần được phân biệt với phép đo thật bằng 0 khi đánh giá dữ liệu thiếu.

- Chuỗi lịch sử: ghép khí tượng theo timestamp của quan trắc AQI và kiểm tra độ dài mảng cảm biến trước khi đọc. Nếu không có bản ghi, hàm phát sinh lỗi; nếu chỉ một số đô thị thất bại, kết quả ghi rõ trạng thái thu thập một phần và danh sách đô thị bị lỗi.

- Cấu hình và xuất dữ liệu: có cấu hình dự phòng cho Lambda; chương trình xuất Athena dừng khi truy vấn lỗi hoặc hết thời gian chờ. Chế độ ngoại tuyến chỉ sao chép CSV đã lưu và ghi rõ nguồn.

### 5.4 Theo dõi bằng CloudWatch

Cấu hình giám sát theo dõi các chỉ số do dịch vụ Lambda cung cấp:

- CloudWatch Metric Alarm (WeatherCollector-Errors-Alarm): Cấu hình phát hiện khi hàm Lambda phát sinh Errors >= 1 trong chu kỳ 300 giây và tự động phát cảnh báo qua SNS Topic.

- CloudWatch Dashboard hiển thị số lượt gọi, số lỗi và thời gian thực thi. Các giá trị chỉ xuất hiện khi có dữ liệu dịch vụ được ghi nhận; hình cấu hình không được dùng như bằng chứng của một lượt chạy.

Invocations đếm số lượt hàm được gọi, Errors đếm lượt kết thúc với lỗi và Duration đo thời gian thực thi. Dashboard hiển thị tổng lượt gọi, tổng lỗi, thời gian trung bình và lớn nhất trong từng chu kỳ 300 giây. Chỉ số Errors không tự xác nhận chất lượng bản ghi; việc đối chiếu CSV được thực hiện riêng.

### 5.5 Kết quả vận hành từ hồ sơ đã lưu

Hồ sơ vận hành của dự án ghi nhận cấu hình Lambda, phản hồi thu thập và năm lượt truy vấn Athena. Mã thực thi, trạng thái, số dòng, thời gian và byte quét được đối chiếu với query_metrics.csv. Các kết quả dưới đây thuộc mốc vận hành đã lưu.

Bảng 5.2 Kết quả xử lý và truy vấn trong hồ sơ vận hành

| Hạng mục | Kết quả đã lưu | Nguồn đối chiếu |
| --- | --- | --- |
| Lambda | WeatherCollectorLambda; Active; Python 3.12; 256 MB; 60 giây. | Cấu hình hàm trong hồ sơ. |
| Phản hồi | Mã 200; thu thập 3 bản ghi. | Phản hồi xử lý đã lưu. |
| Cảnh báo | Hàm ghi nhận 2 cảnh báo gửi tới SNS. | Trường alerts_sent. |
| Athena | 5 truy vấn SUCCEEDED; 87.250 byte quét/lượt; 744–1.192 ms. | Hồ sơ và query_metrics.csv. |

Ba bản ghi của một lượt thu thập và 156 bản ghi của tập phân tích tích lũy là hai đại lượng khác nhau. Hồ sơ đăng ký email ghi pending confirmation, nên số cảnh báo không được diễn giải thành số email đã nhận. Bộ source hiện tại đã được chỉnh sửa sau mốc vận hành này; hồ sơ đã lưu không tự xác nhận một lần triển khai mới.

## Chương 6 Đánh giá kết quả và sử dụng tài nguyên Tuần 2

### 6.1 Các đại lượng theo dõi sử dụng tài nguyên

Để quản lý tài nguyên trong Learner Lab, nhóm theo dõi dung lượng lưu trữ, số lượt xử lý, thời gian thực thi và dung lượng quét của truy vấn. Các đại lượng này được trình bày theo đúng nguồn quan sát, thay vì quy đổi thành chi phí tháng khi chưa có báo cáo thanh toán tương ứng.

Bảng 6.1 Đại lượng sử dụng tài nguyên và nguồn theo dõi

| Thành phần | Đại lượng theo dõi | Nguồn đối chiếu |
| --- | --- | --- |
| Amazon S3 | Số tệp và dung lượng vùng raw. | Trạng thái bucket trong phiên thực hành. |
| AWS Lambda | Invocations, Errors và Duration. | CloudWatch metrics của hàm. |
| Amazon Athena | 87.250 byte quét cho mỗi lượt trong bộ kết quả đã lưu. | query_metrics.csv |
| Amazon SNS | Số thông báo được dịch vụ chấp nhận. | Phản hồi publish và metric SNS. |
| Secrets Manager và Glue | Secret, database, bảng và phân vùng được sử dụng. | Cấu hình tài nguyên. |

Quản lý chi phí dựa trên dữ liệu sử dụng và báo cáo thanh toán của tài khoản tại thời điểm quan sát. Ngân sách Learner Lab không đồng nghĩa với số tiền đã dùng; báo cáo này không suy diễn chi phí thực tế từ đơn giá hoặc mô hình tải giả định.

### 6.2 Tổng hợp các kết quả phân tích

Bốn nhóm kết quả cho thấy sự khác nhau giữa các đô thị, biến thiên của các chỉ số theo giờ, tỷ lệ mẫu theo cấp AQI và liên hệ thống kê với khí tượng. Mỗi hình trong báo cáo được dựng từ tệp CSV tương ứng và có bảng số liệu để đối chiếu.

### 6.3 Quản lý vòng đời tài nguyên

Chương trình thu hồi tài nguyên yêu cầu xác nhận account trước khi xóa. Việc xóa dữ liệu S3 là lựa chọn riêng và chỉ được thực hiện khi bucket có tag dự án phù hợp.

| Thành phần | Cấu hình hoặc cách xử lý |
| --- | --- |
| Xác nhận | Account đăng nhập phải khớp account được xác nhận. |
| Xóa dữ liệu | Lựa chọn riêng; kiểm tra tag dự án trước khi xóa bucket. |

Quy trình thu hồi gồm gỡ lịch và đích kích hoạt, xóa các cấu hình giám sát, hàm xử lý và metadata liên quan. Secret sử dụng thời gian phục hồi; dữ liệu được giữ lại nếu chưa chọn xóa. Thời gian hoàn tất phụ thuộc trạng thái và quyền của dịch vụ.

### 6.4 Đối chiếu sản phẩm Tuần 2

Đối chiếu với các yêu cầu kỹ thuật của đề tài trong đề cương môn học:

Bảng 6.2 Đối chiếu sản phẩm Tuần 2

| Sản phẩm | Nội dung hoàn thiện | Nguồn đối chiếu |
| --- | --- | --- |
| Thu thập | Lambda nhận sự kiện và tạo bản ghi theo lược đồ. | lambda_function.py |
| Lịch và cảnh báo | Cấu hình lịch định kỳ, quyền gọi và SNS topic. | Chương trình quản lý dịch vụ. |
| Dữ liệu | Bảng, view, phân vùng và năm truy vấn. | Tệp SQL và CSV. |
| Phân tích | Bảng thống kê và bốn biểu đồ. | Bốn CSV tổng hợp. |
| Kiểm tra | 44 ca kiểm tra cục bộ. | Bộ kiểm tra Lambda, CSV, biểu đồ và SDK. |

### 6.5 Kết luận Tuần 2

Tuần 2 hoàn thiện bộ chức năng Lambda, lịch thu thập, cảnh báo, mô hình dữ liệu và các truy vấn phân tích. Bộ source tổ chức thao tác AWS qua Python SDK, giữ rõ lỗi dịch vụ và nguồn dữ liệu khi xuất kết quả.

Bộ kết quả dùng trong báo cáo gồm 156 bản ghi và năm tệp truy vấn. Các bảng và biểu đồ cùng sử dụng các giá trị này; diễn giải được giới hạn trong tập mẫu đang có.

Chúng em cùng rà soát luồng dữ liệu và phân công theo các nhóm chức năng. Các kết quả kiểm tra cục bộ giúp xác minh logic xử lý và tính nhất quán dữ liệu.

## Chương 7 Phân công và tổng hợp công việc Tuần 2

### 7.1 Phân công theo nhóm chức năng

Hai thành viên phụ trách các nhóm chức năng khác nhau và cùng thực hiện kiến trúc, tích hợp và báo cáo. Nhật ký Tuần 2 ghi nhận 10,0 giờ của Nguyễn Tiến Sơn và 9,5 giờ của Trần Thị Ngọc Quyên; tổng thời gian là 19,5 giờ. Phần việc bám theo các sản phẩm kỹ thuật đã trình bày trong những chương trước.

Bảng 7.1 Phân công và sản phẩm của từng thành viên

| Thành viên | Sản phẩm phụ trách | Phần thực hiện chung | Giờ |
| --- | --- | --- | --- |
| Nguyễn Tiến Sơn<br>24110054 | Lưu trữ S3, cấu hình secret, Lambda và SNS. | Kiến trúc, tích hợp, đối chiếu và báo cáo. | 10,0 |
| Trần Thị Ngọc Quyên<br>24110051 | Glue, Athena, kết quả truy vấn và biểu đồ. | Kiến trúc, tích hợp, đối chiếu và báo cáo. | 9,5 |

### 7.2 Tổng hợp các sản phẩm đã thực hiện

Các sản phẩm được nhóm rà soát theo luồng từ thu thập đến phân tích; mỗi phần có đầu vào, đầu ra và vai trò cụ thể trong hệ thống.

Bảng 7.2 Tổng hợp sản phẩm Tuần 2

| Nhóm công việc | Sản phẩm | Cách đối chiếu |
| --- | --- | --- |
| Thu thập và chuẩn hóa | Bản ghi 23 trường. | Schema và CSV raw. |
| Lưu trữ và truy vấn | Phân vùng, lược đồ và truy vấn. | Metadata và kết quả CSV. |
| Cảnh báo và lịch | Quy tắc kích hoạt, điều kiện cảnh báo. | Cấu hình dịch vụ và logic xử lý. |
| Phân tích và báo cáo | Bảng số liệu, bốn biểu đồ, Word/PDF. | Giá trị và cách nhóm thống nhất với CSV. |
