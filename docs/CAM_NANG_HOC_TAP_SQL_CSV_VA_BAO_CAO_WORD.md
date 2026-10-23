# CẨM NANG HỌC TẬP VÀ HƯỚNG DẪN BÁO CÁO WORD
## DỰ ÁN WEATHERAWS — SERVERLESS DATA PIPELINE & ANALYTICS

**Học phần:** Điện toán đám mây (Cloud Computing)  
**Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng  
**Nhóm sinh viên thực hiện:**  
- Nguyễn Tiến Sơn — MSSV: 24110054 (Account: `873674852386` - Profile `default`)  
- Trần Thị Ngọc Quyên — MSSV: 24110051 (Account: `134987931868` - Profile `quyen`)  
**Kho lưu trữ mã nguồn:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm.git](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)

---

# MỤC LỤC TỔNG QUAN

1. **PHẦN 1: TỔNG QUÁT DỰ ÁN WEATHERAWS TỪ A ĐẾN Z**
   - 1.1. Mục tiêu học thuật và bài toán dữ liệu
   - 1.2. Kiến trúc giải pháp AWS Serverless 5 tầng
   - 1.3. Bảng phân nhiệm và vai trò của từng dịch vụ AWS
   - 1.4. Vòng đời của một bản ghi dữ liệu (Data Pipeline Flow)
   - 1.5. Tổng kết kết quả triển khai qua 4 tuần

2. **PHẦN 2: NHỮNG ĐIỀU SỐNG CÒN CẦN CHÚ Ý VỀ SQL TRONG AMAZON ATHENA**
   - 2.1. Bản chất kiến trúc của Amazon Athena (Presto/Trino Engine)
   - 2.2. DDL External Table và SerDe JSON: Tại sao và như thế nào?
   - 2.3. Sự phân tách thiết kế giữa External Table và Athena View
   - 2.4. Kỹ thuật Phân vùng (Partitioning) & Partition Pruning tối ưu I/O
   - 2.5. Kỹ thuật nâng cao: Partition Projection (Tự động hóa không cần Crawler)
   - 2.6. Tối ưu hóa Columnar: CTAS và định dạng Parquet Snappy
   - 2.7. 10 Bẫy cú pháp và lưu ý quan trọng khi viết SQL trên Athena
   - 2.8. Chi tiết các câu truy vấn phân tích cốt lõi trong dự án

3. **PHẦN 3: HƯỚNG DẪN CHI TIẾT CÁCH TRÍCH XUẤT CÁC BẢN CSV**
   - 3.1. Phương pháp 1: Trích xuất CSV tự động qua AWS CLI
   - 3.2. Phương pháp 2: Trích xuất CSV qua Python Boto3 SDK
   - 3.3. Phân loại và cấu trúc của toàn bộ 384 tệp CSV trong đồ án
   - 3.4. Cơ chế sao lưu và tái lập ngoại tuyến (Offline Mode)

4. **PHẦN 4: ĐỀ CƯƠNG VÀ CÂU HỎI VẤN ĐÁP MẪU DÀNH CHO BÁO CÁO WORD**
   - 4.1. Đề cương các mục nên đưa vào Báo cáo Word (DOCX)
   - 4.2. Bộ 15 câu hỏi phản biện thường gặp của Giảng viên và câu trả lời chuẩn

---

# PHẦN 1: TỔNG QUÁT DỰ ÁN WEATHERAWS TỪ A ĐẾN Z

## 1.1. Mục tiêu học thuật và bài toán dữ liệu
Dự án **WeatherAWS** giải quyết bài toán xây dựng một đường ống dữ liệu (Data Pipeline) hoàn chỉnh trên nền tảng điện toán đám mây AWS nhằm tự động hóa quá trình:
- Thu thập dữ liệu khí tượng (nhiệt độ, độ ẩm, áp suất, tốc độ gió) và chất lượng không khí (US AQI, bụi mịn PM2.5, PM10, CO, NO2, SO2, O3) theo thời gian thực từ API toàn cầu Open-Meteo.
- Địa bàn giám sát: 3 đô thị trọng điểm tại Việt Nam gồm **TP. Hồ Chí Minh**, **Hà Nội**, và **Đà Nẵng**.
- Xây dựng kho lưu trữ dữ liệu dạng hồ (**S3 Data Lake**) phân vùng theo thời gian, đảm bảo an toàn, bất biến và mã hóa.
- Tự động hóa việc phân tích dữ liệu lớn bằng SQL Serverless (**Amazon Athena & AWS Glue Data Catalog**), so sánh hiệu năng giữa định dạng hàng (Row-based NDJSON) và định dạng cột (Columnar Parquet Snappy).
- Thiết lập hệ thống giám sát sức khỏe vận hành (**CloudWatch Metrics & Logs**) và phát tín hiệu cảnh báo khẩn cấp khi AQI vượt ngưỡng nguy hại qua email (**Amazon SNS**).
- Đóng gói toàn bộ kiến trúc thành mã hạ tầng (**AWS CloudFormation IaC**) và kiểm toán an ninh (**Security Audit**), quản trị tài chính đám mây (**AWS Cost Explorer FinOps**).

## 1.2. Kiến trúc giải pháp AWS Serverless 5 tầng

```
               [ Amazon EventBridge ] (Hourly Rule: rate(1 hour))
                         │
                         ▼
             [ AWS Lambda Collector ] ◄── [ AWS Secrets Manager ]
             (Python 3.12, LabRole)       (API Endpoint & Config)
              │                   │
   (PutObject raw NDJSON)   (High AQI Publish)
              │                   │
              ▼                   ▼
    [ Amazon S3 Data Lake ]   [ Amazon SNS Alert Topic ]
    (year=YYYY/month=MM/day=DD)   │
              │                   ▼
              │            [ Email Subscribers ] (2 Sinh viên)
              ▼
    [ AWS Glue Data Catalog ]
    (Database: weather_aqi_db)
              │
              ▼
       [ Amazon Athena ] ◄── (Interactive Serverless SQL / Presto)
              │
       ┌──────┴─────────────────────────┐
       ▼                                ▼
[ Analytical CSV Queries ]   [ CTAS Parquet Snappy Benchmark ]
       │                                │
       └──────────────┬─────────────────┘
                      ▼
        [ CloudWatch Dashboard & Alarms ]
```

Kiến trúc tuân thủ triệt để mô hình **Serverless Event-Driven Architecture (EDA)**, chia thành 5 tầng chức năng:
1. **Tầng Kích hoạt (Scheduling Tier):** Amazon EventBridge phát tín hiệu định kỳ mỗi 1 giờ (`rate(1 hour)` hoặc cron).
2. **Tầng Xử lý (Compute Tier):** AWS Lambda Function (`WeatherCollectorLambda`) viết bằng Python 3.12, cấu hình 256 MB RAM, timeout 60 giây, kế thừa quyền qua IAM `LabRole`.
3. **Tầng Lưu trữ Hồ dữ liệu (Storage / Data Lake Tier):** Amazon S3 Bucket được khóa chặt 100% truy cập công khai (Block Public Access 4/4), mã hóa mặc định AES256 (SSE-S3), phân vùng thư mục chuẩn Hive `raw/year=YYYY/month=MM/day=DD/`.
4. **Tầng Phân tích & Trích xuất (Analytics & Query Tier):** AWS Glue Data Catalog quản lý metadata bảng `weather_airquality_records` và Amazon Athena thực thi các câu truy vấn SQL chuẩn Presto/Trino, trích xuất dữ liệu ra CSV.
5. **Tầng Giám sát, Cảnh báo & Quản trị (Governance & Ops Tier):** 
   - Amazon CloudWatch theo dõi Log Stream, Metric Filters (`ResultLogLines`, `ErrorLogLines`), Dashboard thời gian thực và Alarm kích hoạt khi có lỗi.
   - Amazon SNS gửi email cảnh báo tự động khi nồng độ ô nhiễm vượt ngưỡng an toàn (US AQI > 150 hoặc PM2.5 > 55.4 µg/m³).
   - AWS CloudFormation tự động hóa triển khai hạ tầng với 17 tài nguyên.
   - AWS Cost Explorer phân rã chi phí chi tiết theo FinOps.

## 1.3. Bảng phân nhiệm và vai trò của từng dịch vụ AWS

| Dịch vụ AWS | Loại dịch vụ | Vai trò cụ thể trong đồ án WeatherAWS |
| :--- | :--- | :--- |
| **Amazon EventBridge** | Serverless Scheduler | Đóng vai trò "đồng hồ báo thức", kích hoạt Lambda Collector chính xác mỗi giờ một lần mà không cần máy chủ cron chạy liên tục. |
| **AWS Lambda** | Serverless Compute | Bộ não thu thập dữ liệu: gọi HTTP tới Open-Meteo, chuẩn hóa 23 trường dữ liệu, kiểm tra ngưỡng ô nhiễm, ghi dữ liệu vào S3 và phát SNS. |
| **AWS Secrets Manager** | Security & Secret Mgmt | Lưu trữ an toàn URL API và cấu hình Open-Meteo, tách biệt hoàn toàn giữa mã nguồn và thông tin cấu hình nhạy cảm. |
| **Amazon S3** | Object Storage Data Lake | Lưu trữ vĩnh viễn các tệp JSON thô (raw NDJSON) và lưu trữ kết quả đầu ra của các câu truy vấn Athena, artifact ZIP của Lambda. |
| **Amazon SNS** | Pub/Sub Messaging | Kênh phân phối thông báo đẩy: khi chỉ số ô nhiễm vượt ngưỡng hoặc hệ thống gặp sự cố, SNS gửi email trực tiếp tới hộp thư 2 sinh viên. |
| **AWS Glue Data Catalog** | Metadata Repository | Lưu lược đồ (schema: 20 cột dữ liệu + 3 cột phân vùng), kiểu dữ liệu và vị trí S3 của bảng `weather_airquality_records`. |
| **Amazon Athena** | Serverless Interactive SQL | Công cụ phân tích SQL phân tán: quét trực tiếp dữ liệu thô trên S3, tính toán thống kê, tương quan, lọc phân vùng và xuất file CSV. |
| **Amazon CloudWatch** | Monitoring & Observability | Lưu trữ toàn bộ log thực thi của Lambda, đo lường các metric (Invocations, Duration, Errors), vẽ Dashboard và thiết lập Alarm. |
| **AWS CloudFormation** | Infrastructure as Code (IaC) | Quản lý vòng đời hạ tầng dưới dạng tệp khai báo JSON duy nhất (17 tài nguyên), giúp tái lập toàn bộ hệ sinh thái chỉ bằng 1 lệnh. |
| **AWS Cost Explorer** | Cloud Financial Mgmt (FinOps) | Theo dõi chi phí thực tế từng ngày theo từng dịch vụ AWS trong môi trường AWS Academy Learner Lab. |

## 1.4. Vòng đời của một bản ghi dữ liệu (Data Pipeline Flow)

1. **Kích hoạt:** EventBridge Rule gửi sự kiện theo lịch tới Lambda.
2. **Lấy cấu hình:** Lambda gọi Secrets Manager (`GetSecretValue`) đọc cấu hình `weather/api_config`.
3. **Gọi API nguồn:** Lambda gửi đồng thời 2 request HTTP tới Open-Meteo cho mỗi đô thị (1 request thời tiết + 1 request chất lượng không khí).
4. **Chuẩn hóa & Gán định danh:** Lambda trích xuất 23 trường chỉ số, gán `record_id` (UUIDv4 duy nhất), tạo cặp mốc thời gian `timestamp_utc` và `timestamp_vn` (UTC+7).
5. **Ghi vào S3 Data Lake:** Lambda gom các bản ghi thành định dạng Newline Delimited JSON (NDJSON) và ghi vào đường dẫn:
   `s3://weather-aqi-<account_id>/raw/year=YYYY/month=MM/day=DD/data_YYYYMMDD_HHmmss.json`
6. **Kiểm tra cảnh báo:** Nếu `us_aqi >= 150` hoặc `pm2_5 >= 55.4`, Lambda gọi `sns:Publish` gửi cảnh báo khẩn cấp qua email kèm thông số chi tiết của đô thị đó.
7. **Ghi Log:** Lambda xuất dòng log chuẩn cấu trúc `[INFO] Result: city=..., aqi=..., pm2_5=...` để CloudWatch Metric Filters bắt tín hiệu.
8. **Truy vấn phân tích:** Người dùng hoặc tiến trình tự động chạy câu lệnh SQL trên Amazon Athena qua AWS CLI / Python để lấy kết quả phân tích thống kê và xuất CSV.

## 1.5. Tổng kết kết quả triển khai qua 4 tuần

- **Tuần 1 (Thiết kế & Nền tảng):** Tìm hiểu dịch vụ, thiết kế kiến trúc 5 tầng, khởi tạo S3 Bucket với Block Public Access, mã hóa AES256, phân quyền IAM LabRole, cấu hình Secrets Manager. Bộ 156 bản ghi mẫu đầu tiên.
- **Tuần 2 (Triển khai chức năng lõi):** Lập trình hàm Lambda Python thu thập dữ liệu Open-Meteo, thiết lập EventBridge Rule chạy 1 giờ/lần, tạo SNS Topic email alert, tạo bảng Glue & Athena DDL/Views, xuất 27 bảng CSV phân tích thực nghiệm và 4 biểu đồ khí tượng.
- **Tuần 3 (Tích hợp, Giám sát & Dự báo):** Xây dựng quy trình CI/CD bảo vệ bằng GitHub Actions, thiết lập CloudWatch Dashboard & Alarms, thực nghiệm 18 lượt Benchmark Athena tối ưu I/O (Partition Projection vs Raw JSON), triển khai mô hình chuỗi thời gian Moving Average dự báo AQI 24 giờ tới và đánh giá sai số Holdout (MAE, RMSE, Bias).
- **Tuần 4 (Kiểm chứng E2E, IaC CloudFormation, Security & FinOps):**
  * Đóng gói toàn bộ hệ thống bằng 1 CloudFormation template duy nhất quản lý **17 tài nguyên** serverless (`weather-stack.json`). Triển khai thành công 2 stack thực tế trên AWS (`CREATE_COMPLETE`).
  * Thực hiện đối chiếu 3 chiều **Log – Metric – S3** khớp 100% (1 Invocation $\rightarrow$ đủ START/END/REPORT $\rightarrow$ 1 object S3 $\rightarrow$ SELECT Athena trả đúng `record_id`).
  * Thực hiện kiểm toán an ninh bảo mật 11 tiêu chí (**Security Audit**).
  * Lập báo cáo tài chính **AWS Cost Explorer (FinOps)** phân rã 117 dòng chi tiết từ API GetCostAndUsage.
  * Xây dựng script quản lý vòng đời tài nguyên cuối phiên (`session_control.py`, `cleanup_resources.ps1`, `start_resources.ps1`) bảo toàn credit cho sinh viên.
  * Kịch bản video demo dưới 10 phút và hoàn thiện bộ hồ sơ báo cáo.

---

# PHẦN 2: NHỮNG ĐIỀU SỐNG CÒN CẦN CHÚ Ý VỀ SQL TRONG AMAZON ATHENA

Đây là phần trọng tâm nhất để bạn học tập, nắm vững nguyên lý và tự tin trả lời vấn đáp khi Giảng viên hỏi về cơ chế truy vấn dữ liệu.

## 2.1. Bản chất kiến trúc của Amazon Athena (Presto/Trino Engine)

- **Athena KHÔNG PHẢI là một hệ quản trị cơ sở dữ liệu quan hệ truyền thống (RDBMS)** như MySQL, SQL Server hay PostgreSQL. Trong Athena, **không có máy chủ cơ sở dữ liệu nào chạy thường trực** và **không có đĩa cứng riêng để lưu trữ dữ liệu**.
- **Cơ chế hoạt động:** Athena là một **Interactive Serverless Query Engine** dựa trên nền tảng nguồn mở **Presto / Trino**.
- **Nguyên lý Schema-on-Read (Áp lược đồ khi đọc):**
  * Trong RDBMS truyền thống (Schema-on-Write), bạn phải định nghĩa bảng trước, khi nạp dữ liệu vào thì dữ liệu bị biến đổi và kiểm tra theo đúng cấu trúc của bảng.
  * Trong Athena, dữ liệu thực tế nằm nguyên bản dưới dạng file (JSON, CSV, Parquet) trên Amazon S3. Bảng trong Athena chỉ là một **bản ánh xạ siêu dữ liệu (Metadata mapping)** lưu trong AWS Glue Data Catalog. Khi bạn chạy câu lệnh `SELECT`, Athena mới dùng các Worker node phân tán để đọc các file thô trên S3, phân tích cú pháp (parse) theo SerDe, lọc dữ liệu và trả về kết quả.

## 2.2. DDL External Table và SerDe JSON: Tại sao và như thế nào?

Hãy phân tích cặn kẽ câu lệnh DDL cốt lõi của dự án trong file `tuan_2/athena/create_table.sql`:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS weather_aqi_db.weather_airquality_records (
    record_id STRING,
    city STRING,
    latitude DOUBLE,
    longitude DOUBLE,
    timestamp_utc STRING,
    timestamp_vn STRING,
    temperature_2m DOUBLE,
    relative_humidity_2m DOUBLE,
    surface_pressure DOUBLE,
    wind_speed_10m DOUBLE,
    pm2_5 DOUBLE,
    pm10 DOUBLE,
    carbon_monoxide DOUBLE,
    nitrogen_dioxide DOUBLE,
    sulphur_dioxide DOUBLE,
    ozone DOUBLE,
    us_aqi INT,
    aqi_category STRING,
    hour INT,
    collected_at STRING
)
PARTITIONED BY (
    year STRING,
    month STRING,
    day STRING
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
    'ignore.malformed.json' = 'true'
)
LOCATION 's3://weather-aqi-ACCOUNT_ID/raw/'
TBLPROPERTIES ('has_encrypted_data'='false');
```

### Những điểm chú ý sống còn về mặt kỹ thuật:

1. **Từ khóa `EXTERNAL`:**
   - Bắt buộc phải có `EXTERNAL` trong Athena. Nó xác nhận đây là bảng ngoại.
   - **Hệ quả cực kỳ quan trọng:** Nếu bạn chạy lệnh `DROP TABLE weather_airquality_records;`, Athena **chỉ xóa metadata trong Glue Catalog**, toàn bộ dữ liệu file JSON gốc trên S3 **hoàn toàn nguyên vẹn**, không bị mất!
2. **`ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'`:**
   - **SerDe** viết tắt của **Serializer / Deserializer**.
   - `org.openx.data.jsonserde.JsonSerDe` là bộ thư viện mã nguồn mở chuyên dụng giúp Athena đọc từng dòng văn bản (NDJSON) trên S3 và chuyển thành các cột dữ liệu tương ứng.
   - SerDe này ánh xạ tên key trong file JSON (ví dụ `"city": "Ho Chi Minh"`) với tên cột `city STRING` trong bảng.
3. **Cấu hình `'ignore.malformed.json' = 'true'`:**
   - Đây là cơ chế phòng vệ (Defensive data engineering): Nếu chẳng may có một dòng JSON bị lỗi định dạng (bị ngắt giữa chừng, hỏng byte), SerDe sẽ bỏ qua dòng hỏng đó hoặc trả về NULL thay vì làm dừng toàn bộ câu truy vấn với lỗi `Corrupt JSON exception`.
4. **`LOCATION 's3://.../raw/'`:**
   - Đường dẫn này trỏ tới thư mục gốc chứa dữ liệu trên S3. Athena sẽ quét đệ quy các thư mục con bên dưới đường dẫn này.

## 2.3. Sự phân tách thiết kế giữa External Table và Athena View

Trong đồ án, nhóm tạo 2 đối tượng:
1. External Table: `weather_airquality_records`
2. View: `vietnam_weather_aqi`

```sql
CREATE OR REPLACE VIEW weather_aqi_db.vietnam_weather_aqi AS
SELECT 
    record_id, city, latitude, longitude,
    timestamp_utc, timestamp_vn,
    temperature_2m, relative_humidity_2m, surface_pressure, wind_speed_10m,
    pm2_5, pm10, carbon_monoxide, nitrogen_dioxide, sulphur_dioxide, ozone,
    us_aqi, aqi_category, hour, collected_at,
    year, month, day
FROM weather_aqi_db.weather_airquality_records;
```

**Tại sao phải làm như vậy? (Câu hỏi vấn đáp rất hay gặp):**
- **Nguyên lý đóng gói và bảo mật tầng dữ liệu (Data Layer Abstraction):** External Table là tầng lưu trữ vật lý gắn chặt với SerDe và vị trí S3. Người dùng phân tích (Data Analyst) hoặc ứng dụng bên ngoài không nên truy cập trực tiếp vào bảng vật lý.
- Khi người dùng truy vấn qua View `vietnam_weather_aqi`:
  * Nếu sau này cấu trúc vật lý thay đổi (ví dụ chuyển từ JSON sang Parquet, đổi tên thư mục S3, hoặc đổi SerDe), ta chỉ cần cập nhật View mà **toàn bộ mã nguồn truy vấn của người dùng không hề bị gãy!**
  * View cho phép ẩn đi các trường dữ liệu nhạy cảm hoặc định dạng lại kiểu dữ liệu trước khi cung cấp cho người dùng.

## 2.4. Kỹ thuật Phân vùng (Partitioning) & Partition Pruning tối ưu I/O

Đây là kỹ thuật quan trọng nhất quyết định hiệu năng và chi phí của hệ thống Data Lake trên AWS.

### Nguyên lý cấu trúc thư mục Hive:
Lambda lưu trữ các tệp trên S3 theo quy ước phân vùng Hive:
```
s3://weather-aqi-<account_id>/raw/
   ├── year=2026/
   │   ├── month=10/
   │   │   ├── day=18/
   │   │   │   ├── data_20261018_010000.json
   │   │   │   └── data_20261018_020000.json
   │   │   └── day=19/
   │   │       ├── data_20261019_010000.json
   │   │       └── ...
```

### Partition Pruning (Cắt tỉa phân vùng) là gì?
Hãy so sánh 2 câu truy vấn sau:

**Câu lệnh A (KHÔNG dùng phân vùng):**
```sql
SELECT city, AVG(pm2_5) 
FROM weather_airquality_records 
WHERE city = 'Ho Chi Minh';
```
- **Cách Athena xử lý:** Vì `city` là một cột dữ liệu nằm BÊN TRONG nội dung file JSON, Athena bắt buộc phải **quét 100% tất cả các file JSON có trong toàn bộ S3 bucket** từ trước đến nay, tải toàn bộ dữ liệu về bộ nhớ rồi mới lọc ra những dòng có `city = 'Ho Chi Minh'`.
- **Hậu quả:** Tốn nhiều dung lượng quét I/O, thời gian thực thi lâu, chi phí tăng cao theo thời gian.

**Câu lệnh B (CÓ dùng Partition Pruning):**
```sql
SELECT city, AVG(pm2_5) 
FROM weather_airquality_records 
WHERE year = '2026' AND month = '10' AND day = '19'
  AND city = 'Ho Chi Minh';
```
- **Cách Athena xử lý:** Do `year`, `month`, `day` là các **cột phân vùng (Partition Columns)**, Athena nhận diện ngay điều kiện lọc nằm ở cấp độ đường dẫn S3 (S3 prefix). Athena **chỉ liệt kê và đọc duy nhất các file nằm trong thư mục `year=2026/month=10/day=19/`**, toàn bộ các ngày/tháng/năm khác bị loại bỏ ngay lập tức trước khi đọc dữ liệu!
- **Kết quả đo đạc thực tế trong đồ án:** Partition Pruning giúp **cắt giảm từ 75,28% đến 86,76% lượng dữ liệu quét (Data Scanned)** so với truy vấn toàn bảng!

## 2.5. Kỹ thuật nâng cao: Partition Projection (Tự động hóa không cần Crawler)

### Vấn đề của phân vùng truyền thống:
Trong kiến trúc truyền thống, khi Lambda ghi một file mới vào thư mục mới (ví dụ sang ngày mới `day=20`), Athena sẽ **chưa biết** thư mục đó tồn tại. Người quản trị bắt buộc phải:
1. Chạy lệnh `MSCK REPAIR TABLE weather_airquality_records;` thủ công, HOẶC
2. Lập lịch cho **AWS Glue Crawler** quét S3 định kỳ để cập nhật metadata phân vùng vào Glue Catalog.
- **Hạn chế:** Lệnh `MSCK REPAIR TABLE` chạy rất lâu khi dữ liệu lớn (quét toàn bộ metadata S3), Glue Crawler thì tốn chi phí (0.44 USD/DPU-Hour) và có độ trễ cao.

### Giải pháp Partition Projection trong Tuần 3 & Tuần 4:
Nhóm cấu hình **Partition Projection** trực tiếp trong thuộc tính bảng (`TBLPROPERTIES`):

```sql
TBLPROPERTIES (
    'projection.enabled' = 'true',
    'projection.year.type' = 'integer',
    'projection.year.range' = '2026,2030',
    'projection.month.type' = 'integer',
    'projection.month.range' = '1,12',
    'projection.month.digits' = '2',
    'projection.day.type' = 'integer',
    'projection.day.range' = '1,31',
    'projection.day.digits' = '2',
    'storage.location.template' = 's3://weather-aqi-ACCOUNT_ID/raw/year=${year}/month=${month}/day=${day}/'
);
```

**Cách Partition Projection hoạt động:**
- Thay vì tra cứu danh sách phân vùng trong Glue Data Catalog, Athena sử dụng các quy tắc toán học (phạm vi từ 2026 đến 2030, tháng 01-12, ngày 01-31) để **tự tính toán và ánh xạ trực tiếp đường dẫn S3 template**.
- **Lợi ích vượt trội:** Dữ liệu vừa được Lambda ghi vào S3 là Athena có thể truy vấn được **ngay lập tức trong mili-giây** (Zero-latency data availability), không cần chạy `MSCK REPAIR TABLE`, không cần Glue Crawler, loại bỏ hoàn toàn chi phí quét metadata!

## 2.6. Tối ưu hóa Columnar: CTAS và định dạng Parquet Snappy

Trong Tuần 3 và Tuần 4, nhóm đã thực hiện benchmark nâng cao so sánh 3 phương pháp lưu trữ bằng kỹ thuật **CTAS (Create Table As Select)**:

```sql
CREATE TABLE weather_aqi_db.vietnam_weather_parquet
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY',
    external_location = 's3://weather-aqi-ACCOUNT_ID/optimized/parquet/'
) AS 
SELECT * FROM weather_aqi_db.weather_airquality_records;
```

### Tại sao Parquet Snappy lại tối ưu vượt trội so với JSON?
1. **Lưu trữ dạng cột (Columnar Storage):**
   - File JSON lưu theo từng dòng: muốn lấy 1 cột `pm2_5`, Athena vẫn phải đọc cả dòng gồm 23 cột.
   - File Parquet tách riêng từng cột thành các khối dữ liệu độc lập. Khi câu lệnh chỉ `SELECT city, pm2_5`, Athena **chỉ tải đúng 2 cột đó từ S3 về**, 21 cột còn lại hoàn toàn không bị tải qua mạng (Column Pruning)!
2. **Nén khối với thuật toán Snappy:**
   - Snappy là thuật toán nén cân bằng hoàn hảo giữa tỷ lệ nén và tốc độ giải nén cực nhanh của Google. Giúp dung lượng file trên S3 giảm từ 60% đến 80% so với plain JSON.
3. **Thống kê Min/Max tại Footer:**
   - Parquet lưu sẵn giá trị lớn nhất và nhỏ nhất của từng khối trong phần Footer. Khi bạn truy vấn `WHERE pm2_5 > 150`, Athena đọc Footer trước, nếu khối dữ liệu có `max_pm2_5 = 80`, Athena bỏ qua luôn toàn bộ khối đó mà không cần giải nén!

### Bảng kết quả 18 lượt Benchmark thực tế trên AWS:
| Cơ chế lưu trữ & truy vấn | Byte quét trung bình (Data Scanned) | Tốc độ thực thi (Execution Time) | Chi phí ước tính |
| :--- | :---: | :---: | :---: |
| **1. Raw NDJSON (Không phân vùng)** | ~ 152 KB | 1.150 ms | Tiêu chuẩn |
| **2. Partition Projection (NDJSON)** | ~ 24 KB (Giảm **84,2%**) | 680 ms (Nhanh hơn **40,8%**) | Giảm **84,2%** |
| **3. CTAS Parquet Snappy (Tối ưu)** | ~ 4.2 KB (Giảm **97,2%**) | 420 ms (Nhanh hơn **63,5%**) | Giảm **97,2%** |

---

## 2.7. 10 Bẫy cú pháp và lưu ý quan trọng khi viết SQL trên Athena

Khi học và trả lời vấn đáp, bạn cần nắm rõ 10 lưu ý kỹ thuật này:

1. **Phân biệt dấu nháy đơn (`'`) và dấu backtick (`` ` ``):**
   - Dấu nháy đơn `'` dùng cho **chuỗi giá trị văn bản (String literal)**: `WHERE city = 'Ho Chi Minh'`.
   - Dấu backtick `` ` `` hoặc nháy kép `"` dùng cho **tên định danh cột hoặc bảng đặc biệt**: ví dụ cột trùng từ khóa `` `timestamp` ``. Không bao giờ dùng nháy kép cho giá trị chuỗi!
2. **Trích xuất trường trong đối tượng JSON lồng nhau (Nested Struct):**
   - Nếu dữ liệu thô có cấu trúc lồng nhau dạng `struct<temperature:double, humidity:double>`, cú pháp truy vấn trong Athena là dùng dấu chấm:
     `SELECT weather.temperature, air_quality.pm2_5 FROM ...`
3. **Ép kiểu an toàn bằng `TRY_CAST` thay vì `CAST`:**
   - Nếu dữ liệu thô bị lẫn một chuỗi không hợp lệ (ví dụ `"pm2_5": "N/A"`), lệnh `CAST(pm2_5 AS DOUBLE)` sẽ quăng lỗi và dừng toàn bộ query!
   - Sử dụng `TRY_CAST(pm2_5 AS DOUBLE)`: nếu không ép kiểu được, hàm sẽ trả về `NULL` một cách an toàn mà query vẫn chạy hoàn tất.
4. **Xử lý ngày giờ với `from_iso8601_timestamp`:**
   - Trường `collected_at` lưu chuỗi ISO 8601 (ví dụ `2026-10-19T08:00:00Z`).
   - Để chuyển sang kiểu Timestamp và đổi sang giờ Việt Nam (UTC+7):
     ```sql
     from_iso8601_timestamp(collected_at) AT TIME ZONE 'Asia/Ho_Chi_Minh'
     ```
5. **Cảnh giác với phép chia số nguyên (Integer Division):**
   - Trong SQL Presto/Trino, `COUNT(*) / 100` nếu cả 2 là số nguyên thì kết quả sẽ bị làm tròn thành 0!
   - Luôn nhân với số thực: `COUNT(*) * 100.0 / total`.
6. **Hàm tương quan Pearson `corr()`:**
   - Athena hỗ trợ sẵn hàm `corr(y, x)` để tính hệ số tương quan tuyến tính Pearson giữa 2 biến liên tục. Giá trị trả về nằm trong khoảng `[-1.0, 1.0]`.
7. **Hàm phân vị gần đúng `approx_percentile()`:**
   - Khi tính toán trên dữ liệu lớn, thay vì sắp xếp chính xác toàn bộ tập dữ liệu (tốn RAM và I/O), Athena cung cấp `approx_percentile(pm2_5, 0.5)` để tìm trung vị (Median) và `approx_percentile(pm2_5, 0.95)` để tìm bách phân vị thứ 95 với độ chính xác xấp xỉ cực cao.
8. **Window Functions kết hợp Aggregation:**
   - Câu lệnh tính tỷ lệ phần trăm phân bố cấp độ AQI của từng thành phố:
     ```sql
     ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city), 1) AS percentage
     ```
   - Trong đó: `COUNT(*)` đếm số bản ghi của cấp AQI đó trong thành phố; `SUM(COUNT(*)) OVER (PARTITION BY city)` tính tổng số bản ghi của toàn thành phố đó.
9. **Lọc bản ghi mới nhất bằng `ROW_NUMBER()`:**
   - Để lấy duy nhất 1 bản ghi mới nhất của mỗi đô thị:
     ```sql
     WITH ranked AS (
         SELECT *, ROW_NUMBER() OVER (PARTITION BY city ORDER BY timestamp_utc DESC) AS rn
         FROM vietnam_weather_aqi
     )
     SELECT * FROM ranked WHERE rn = 1;
     ```
10. **Chính sách tính phí của Athena:**
    - Giá niêm yết: **5.00 USD cho mỗi 1 TB dữ liệu quét**.
    - **Lưu ý tối thiểu:** Mỗi câu truy vấn Athena luôn bị tính tối thiểu **10 MB dữ liệu quét**, kể cả khi câu lệnh của bạn chỉ đọc 5 KB! Do đó, việc gộp các truy vấn thông minh là nguyên tắc tiết kiệm chi phí trong FinOps.

---

## 2.8. Chi tiết các câu truy vấn phân tích cốt lõi trong dự án

### Query 1: So sánh tổng hợp khí tượng và ô nhiễm theo thành phố
File: `tuan_2/athena/query_avg_aqi_by_city.sql`
```sql
SELECT 
    city,
    COUNT(*) AS total_records,
    ROUND(AVG(us_aqi), 2) AS avg_aqi,
    MIN(us_aqi) AS min_aqi,
    MAX(us_aqi) AS max_aqi,
    ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
    ROUND(AVG(pm10), 2) AS avg_pm10,
    ROUND(AVG(temperature_2m), 2) AS avg_temp,
    ROUND(AVG(relative_humidity_2m), 2) AS avg_humidity
FROM weather_aqi_db.weather_airquality_records
GROUP BY city
ORDER BY avg_aqi DESC;
```
*Ý nghĩa:* Giúp so sánh mức độ ô nhiễm trung bình giữa 3 thành phố, tìm ra thành phố có chỉ số AQI cao nhất và khoảng dao động min-max.

### Query 2: Khung giờ cao điểm ô nhiễm trong ngày
File: `tuan_2/athena/query_peak_pollution_hours.sql`
```sql
SELECT 
    hour,
    ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
    ROUND(AVG(pm10), 2) AS avg_pm10,
    ROUND(AVG(us_aqi), 2) AS avg_aqi,
    COUNT(*) AS sample_count
FROM weather_aqi_db.weather_airquality_records
GROUP BY hour
ORDER BY hour ASC;
```
*Ý nghĩa:* Nhóm dữ liệu theo 24 giờ trong ngày để phát hiện quy luật ô nhiễm (thường đạt đỉnh vào khung giờ cao điểm giao thông buổi sáng từ 7h - 9h và chiều từ 17h - 19h).

### Query 3: Phân tích tương quan giữa Thời tiết và Bụi mịn PM2.5
File: `tuan_2/athena/query_temperature_humidity_correlation.sql`
```sql
SELECT 
    city,
    ROUND(corr(temperature_2m, pm2_5), 4) AS corr_temp_pm25,
    ROUND(corr(relative_humidity_2m, pm2_5), 4) AS corr_humidity_pm25,
    ROUND(corr(wind_speed_10m, pm2_5), 4) AS corr_wind_pm25
FROM weather_aqi_db.weather_airquality_records
GROUP BY city;
```
*Ý nghĩa:* Đánh giá ảnh hưởng của các yếu tố khí tượng đến sự khuếch tán bụi mịn. Ví dụ: gió mạnh có hệ số tương quan âm (gió giúp thổi bay bụi), độ ẩm cao có hệ số tương quan dương (ẩm giữ bụi lơ lửng).

---

# PHẦN 3: HƯỚNG DẪN CHI TIẾT CÁCH TRÍCH XUẤT CÁC BẢN CSV

Trong đồ án này, dữ liệu CSV được tạo ra bằng 2 phương pháp chính: **Qua AWS CLI** và **Qua Python Boto3 SDK**. Dưới đây là các bước thực hiện chi tiết:

## 3.1. Phương pháp 1: Trích xuất CSV tự động qua AWS CLI

Đây là phương pháp dùng khi thao tác trực tiếp trên giao diện dòng lệnh PowerShell/Bash:

### Bước 1: Khởi tạo câu truy vấn trên Athena bằng AWS CLI
```powershell
$QueryString = "SELECT city, ROUND(AVG(us_aqi),2) AS avg_aqi, ROUND(AVG(pm2_5),2) AS avg_pm25 FROM weather_aqi_db.weather_airquality_records GROUP BY city ORDER BY avg_aqi DESC;"
$S3Output = "s3://weather-aqi-873674852386/athena-query-results/"

$StartResult = aws athena start-query-execution `
    --query-string "$QueryString" `
    --query-execution-context Database="weather_aqi_db" `
    --result-configuration OutputLocation="$S3Output" `
    --region us-east-1 `
    --output json | ConvertFrom-Json

$QueryExecutionId = $StartResult.QueryExecutionId
Write-Host "Query ID vừa tạo: $QueryExecutionId"
```
*Lưu ý:* Lệnh `start-query-execution` là một lệnh bất đồng bộ (Asynchronous). Nó trả về ngay lập tức một mã định danh `QueryExecutionId` mà chưa có dữ liệu kết quả ngay.

### Bước 2: Thăm dò (Polling) trạng thái thực thi của truy vấn
```powershell
do {
    Start-Sleep -Seconds 2
    $StatusResult = aws athena get-query-execution `
        --query-execution-id $QueryExecutionId `
        --region us-east-1 `
        --output json | ConvertFrom-Json
        
    $State = $StatusResult.QueryExecution.Status.State
    Write-Host "Trạng thái truy vấn: $State..."
} while ($State -in @("QUEUED", "RUNNING"))

if ($State -ne "SUCCEEDED") {
    throw "Truy vấn thất bại với trạng thái: $State"
}
```

### Bước 3: Tải trực tiếp file CSV kết quả từ S3 về máy cục bộ
Khi Athena hoàn thành, nó tự động lưu kết quả dưới dạng file CSV trên đường dẫn S3 được chỉ định:
`s3://weather-aqi-873674852386/athena-query-results/<QueryExecutionId>.csv`

Ta chỉ cần dùng lệnh `aws s3 cp` để tải về:
```powershell
$S3CsvUri = "$S3Output$QueryExecutionId.csv"
aws s3 cp $S3CsvUri "./avg_aqi_by_city.csv" --region us-east-1
Write-Host "Đã xuất kết quả thành công ra file avg_aqi_by_city.csv!"
```

*(Cách thay thế: Dùng lệnh `aws athena get-query-results --query-execution-id $QueryExecutionId` để đọc kết quả dạng JSON rồi parse ra CSV).*

---

## 3.2. Phương pháp 2: Trích xuất CSV qua Python Boto3 SDK

Trong mã nguồn của đồ án, module `tuan_2/scripts/athena_export.py` và `tuan_2/scripts/export_raw_records.py` thực hiện việc xuất dữ liệu hoàn toàn tự động và an toàn:

### Quy trình của script Python:
1. Đọc nội dung tệp SQL mẫu từ thư mục `tuan_2/athena/*.sql`.
2. Khởi tạo boto3 client:
   ```python
   athena_client = boto3.client('athena', region_name='us-east-1')
   s3_client = boto3.client('s3', region_name='us-east-1')
   ```
3. Gọi `start_query_execution()`, chờ `SUCCEEDED`.
4. Đọc `ResultConfiguration.OutputLocation`, tải luồng byte qua `s3_client.get_object()`.
5. Kiểm tra tính toàn vẹn của CSV (đảm bảo encoding UTF-8, có header hợp lệ, không có giá trị rỗng bất thường).
6. Ghi file CSV ra thư mục đích và tính mã băm SHA-256 để đưa vào `manifest.json`.

---

## 3.3. Phân loại và cấu trúc của toàn bộ 384 tệp CSV trong đồ án

Toàn bộ hệ thống kiểm toán tự động (`repository_audit.py`) theo dõi chính xác **384 tệp CSV** được chia thành 4 nhóm nghiệp vụ:

1. **Nhóm CSV Dữ liệu Thô (Raw Datasets):**
   - `tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/raw_weather_aqi_records.csv`: 156 bản ghi Tuần 1.
   - `tuan_2/results/week2_analysis/raw_records.csv`: 84 bản ghi Tuần 2 (27 dòng Tiến Sơn, 57 dòng Ngọc Quyên).
   - `tuan_4/results/advanced_live_2026_10_20/snapshot/`: 700 bản ghi tích lũy Tuần 4.
2. **Nhóm CSV Báo cáo Phân tích Khí tượng & Ô nhiễm (Analytical CSVs):**
   - `avg_aqi_by_city.csv`: Chỉ số trung bình, min, max theo thành phố.
   - `peak_pollution_hours.csv`: Nồng độ ô nhiễm theo 24 khung giờ.
   - `category_distribution.csv`: Tỷ lệ phần trăm 6 cấp độ chất lượng không khí.
   - `correlation_matrix.csv`: Ma trận tương quan Pearson giữa nhiệt độ, độ ẩm, gió và PM2.5.
   - `descriptive_statistics.csv`: Thống kê mô tả đầy đủ (Mean, Median, StdDev, P25, P75, P90, P95).
3. **Nhóm CSV Đối soát Tài chính FinOps (Cost Explorer CSVs):**
   - `learner_lab_cost_breakdown.csv`: **117 dòng chi tiết** đối soát chi phí AWS Cost Explorer (70 nhóm cho Tiến Sơn, 47 nhóm cho Ngọc Quyên).
4. **Nhóm CSV Dự báo Chuỗi thời gian (Forecasting & Backtest CSVs):**
   - `predictions.csv`: 432 điểm dự đoán chuỗi thời gian qua 3 cửa sổ lịch sử.
   - `metrics.csv`: 18 dòng chỉ số đánh giá sai số mô hình (MAE, RMSE, Mean Bias Error).

---

## 3.4. Cơ chế sao lưu và tái lập ngoại tuyến (Offline Mode)

**Tại sao cần cơ chế Offline Mode? (Điểm cộng rất lớn với Giảng viên):**
- Trong môi trường học phần, tài khoản AWS Academy Learner Lab có thời hạn phiên (thường 4 tiếng) và số credit có hạn ($100). Khi bảo vệ đồ án hoặc khi Giảng viên chấm bài offline, phiên AWS có thể đã hết hạn hoặc tài nguyên đã tạm tắt.
- Do đó, các script trong dự án được thiết kế với cờ `--offline`:
  ```powershell
  python tuan_2/scripts/export_raw_records.py --offline
  python tuan_4/scripts/cost_analysis.py --check
  python tuan_4/scripts/verify_results.py
  ```
- **Nguyên lý:** Khi có cờ `--offline`, script sẽ không gọi ra internet hoặc AWS API mà đọc trực tiếp từ bộ snapshot bằng chứng đã lưu có chữ ký SHA-256 nguyên bản. Nhờ đó, bất kỳ ai tải repository về đều có thể tái lập và xác minh 100% kết quả tính toán mà không cần tài khoản AWS!

---

# PHẦN 4: ĐỀ CƯƠNG VÀ CÂU HỎI VẤN ĐÁP MẪU DÀNH CHO BÁO CÁO WORD

## 4.1. Đề cương các mục nên đưa vào Báo cáo Word (DOCX)

Khi bạn viết bài báo cáo Word, hãy chia theo bố cục chuẩn sau:

- **Trang bìa:** Theo mẫu chuẩn HCMUTE, ghi rõ môn học Điện toán đám mây, GVHD ThS. Huỳnh Xuân Phụng, tên 2 sinh viên kèm MSSV, liên kết GitHub Repository nổi bật.
- **Mục lục, Danh mục Bảng, Danh mục Hình vẽ**
- **Chương 1: Giới thiệu đề tài & Kiến trúc tổng thể:** Trình bày bài toán, sơ đồ kiến trúc 5 tầng, vai trò từng dịch vụ AWS.
- **Chương 2: Thiết kế & Triển khai tầng Thu thập Dữ liệu (Lambda, Secrets Manager, S3):** Cấu hình hàm Lambda, lưu trữ NDJSON trên S3 theo phân vùng Hive, mã hóa AES256, Block Public Access.
- **Chương 3: Phân tích Dữ liệu Lớn với Amazon Athena & Glue:** Phân tích DDL External Table, kỹ thuật Partition Pruning, Partition Projection và tối ưu hóa Columnar Parquet Snappy kèm số liệu benchmark.
- **Chương 4: Giám sát, Cảnh báo & Vận hành (CloudWatch, SNS):** Metric Filters, Alarm, Dashboard thời gian thực, quy trình kiểm chứng đối chiếu 3 chiều Log – Metric – S3.
- **Chương 5: Đóng gói Hạ tầng IaC (CloudFormation) & Rà soát Bảo mật:** 17 tài nguyên serverless, kết quả triển khai stack thật, 11 tiêu chuẩn an toàn bảo mật.
- **Chương 6: Quản trị Tài chính Đám mây FinOps (Cost Explorer):** Phân tích chi phí 117 dòng thực tế từ AWS, các giải pháp tiết kiệm credit cuối phiên.
- **Chương 7: Kết quả Thực nghiệm & Đánh giá Dự báo:** Bảng biểu thống kê mô tả khí tượng, ma trận tương quan, biểu đồ trực quan và kết quả kiểm thử sai số mô hình (MAE, RMSE).
- **Chương 8: Kết luận & Hướng phát triển:** Tổng kết đồ án, bảng phân công giờ công chi tiết (78 giờ công đã xác nhận).

---

## 4.2. Bộ 15 câu hỏi phản biện thường gặp của Giảng viên và câu trả lời chuẩn

### Câu 1: Tại sao nhóm không lưu dữ liệu vào cơ sở dữ liệu quan hệ như RDS MySQL mà lại lưu vào Amazon S3?
**Trả lời:**
- *Về mặt kiến trúc:* Dữ liệu thời tiết và chất lượng không khí là dữ liệu chuỗi thời gian (time-series data) phát sinh liên tục theo giờ. Việc lưu vào S3 xây dựng **Data Lake** giúp lưu trữ không giới hạn dung lượng với chi phí cực rẻ (khoảng 0.023 USD/GB/tháng so với hàng chục USD/tháng để duy trì một RDS instance chạy 24/7).
- *Về mặt mở rộng:* Dữ liệu thô (raw data) trên S3 là bất biến (immutable), cho phép nhiều công cụ phân tích khác nhau (Athena, EMR, Redshift Spectrum, SageMaker) cùng khai thác mà không làm ảnh hưởng đến hiệu năng của hệ thống thu thập.

### Câu 2: Sự khác nhau giữa External Table trong Athena và Table thông thường trong SQL là gì?
**Trả lời:**
- Athena Table là **External Table** (Bảng ngoại). Athena chỉ quản lý metadata (lược đồ bảng, kiểu dữ liệu, đường dẫn thư mục S3) thông qua AWS Glue Data Catalog. Dữ liệu thực tế hoàn toàn nằm trên Amazon S3 do người dùng sở hữu.
- Do đó, khi ta thực hiện lệnh `DROP TABLE`, Athena chỉ xóa phần định nghĩa metadata trong Glue, còn toàn bộ dữ liệu gốc trên S3 vẫn được bảo toàn nguyên vẹn, không bị mất mát.

### Câu 3: Kỹ thuật Partition Pruning hoạt động như thế nào và tại sao nó lại giảm được chi phí?
**Trả lời:**
- Partition Pruning là cơ chế cắt tỉa phân vùng ở tầng siêu dữ liệu S3 trước khi đọc nội dung file. Khi bảng được phân vùng theo `year/month/day` và câu truy vấn có mệnh đề `WHERE year = '2026' AND month = '10' AND day = '19'`, Athena chỉ liệt kê các object nằm đúng trong prefix S3 tương ứng để đọc.
- Vì Athena tính tiền dựa trên **số lượng byte dữ liệu quét từ S3** (5 USD / 1 TB), việc chỉ quét đúng ngày cần phân tích thay vì quét toàn bộ hồ dữ liệu giúp giảm từ 75% đến 86% dung lượng đọc, qua đó giảm trực tiếp chi phí truy vấn tương ứng.

### Câu 4: Partition Projection khác gì so với phân vùng truyền thống dùng MSCK REPAIR TABLE?
**Trả lời:**
- Phân vùng truyền thống yêu cầu danh sách các phân vùng phải được đăng ký sẵn trong AWS Glue Catalog. Khi có dữ liệu mới ghi vào ngày mới, nếu không chạy `MSCK REPAIR TABLE` hoặc Glue Crawler thì Athena sẽ không thấy dữ liệu đó.
- **Partition Projection** cho phép Athena tự động nội suy và tính toán danh sách phân vùng dựa trên cấu hình phạm vi số học (Range: 2026-2030, tháng 01-12, ngày 01-31). Do đó, ngay khi Lambda ghi dữ liệu vào S3, Athena có thể truy vấn được ngay lập tức (Zero-latency) mà không cần chờ Crawler hay chạy lệnh quét metadata.

### Câu 5: Tại sao định dạng Parquet Snappy lại nhanh và tốn ít byte quét hơn file JSON?
**Trả lời:**
- Parquet là định dạng lưu trữ dạng cột (Columnar Storage). Trong khi JSON lưu theo dòng (muốn đọc 1 cột phải tải cả dòng), Parquet cho phép Athena chỉ tải đúng các cột có mặt trong mệnh đề `SELECT` (Column Pruning).
- Parquet tích hợp thuật toán nén khối Snappy giúp giảm dung lượng vật lý từ 60-80%. Ngoài ra, phần Footer của file Parquet lưu trữ sẵn thống kê Min/Max của từng khối, giúp Athena bỏ qua các khối dữ liệu không thỏa mãn điều kiện `WHERE` mà không cần giải nén.

### Câu 6: Làm thế nào để nhóm xuất được kết quả truy vấn Athena ra file CSV?
**Trả lời:**
- *Cách 1 (AWS CLI):* Gọi lệnh `aws athena start-query-execution` để bắt đầu truy vấn. Khi Athena chạy xong (trạng thái `SUCCEEDED`), kết quả CSV tự động được lưu tại S3 Query Output Location (`s3://.../<QueryId>.csv`). Ta dùng lệnh `aws s3 cp` để tải về máy.
- *Cách 2 (Python Boto3):* Sử dụng SDK Boto3 tự động kích hoạt truy vấn, thăm dò trạng thái và tải luồng dữ liệu byte về ghi ra file CSV, đồng thời kiểm tra tính hợp lệ của tiêu đề cột và tính mã băm SHA-256 để lưu vào manifest.

### Câu 7: Tại sao cần tạo Athena View `vietnam_weather_aqi` mà không để người dùng truy vấn thẳng vào External Table?
**Trả lời:**
- Đây là nguyên tắc phân tách tầng dữ liệu vật lý và tầng logic (Data Abstraction). External Table gắn liền với cấu hình SerDe, vị trí S3 và định dạng file thô.
- Khi cung cấp View cho người dùng hoặc ứng dụng BI, nếu sau này nhóm tối ưu đổi định dạng file từ JSON sang Parquet hoặc đổi thư mục S3, nhóm chỉ cần cập nhật định nghĩa View, toàn bộ ứng dụng của người dùng tiếp tục hoạt động bình thường mà không bị gián đoạn.

### Câu 8: Nhóm đã xử lý bài toán lệch múi giờ giữa UTC và giờ Việt Nam (UTC+7) như thế nào trong SQL?
**Trả lời:**
- API Open-Meteo trả về mốc thời gian dạng ISO 8601 theo chuẩn UTC (ví dụ `2026-10-19T08:00:00Z`).
- Trong mã nguồn Lambda, nhóm lưu trữ song song cả 2 trường `timestamp_utc` và `timestamp_vn` (cộng 7 tiếng).
- Trong SQL Athena, nhóm sử dụng hàm `from_iso8601_timestamp(collected_at) AT TIME ZONE 'Asia/Ho_Chi_Minh'` để chuyển đổi chính xác mốc thời gian sang giờ địa phương Việt Nam trước khi gom nhóm theo giờ (`hour`).

### Câu 9: Trong câu lệnh SQL, hàm `corr()` được dùng để làm gì và ý nghĩa kết quả thực nghiệm ra sao?
**Trả lời:**
- Hàm `corr(y, x)` trong Athena tính toán hệ số tương quan tuyến tính Pearson giữa 2 biến liên tục.
- Kết quả thực nghiệm trong đồ án cho thấy:
  * Tốc độ gió (`wind_speed_10m`) có hệ số tương quan âm với nồng độ bụi PM2.5 (gió càng mạnh thì bụi mịn càng dễ bị phân tán, chất lượng không khí tốt hơn).
  * Độ ẩm (`relative_humidity_2m`) có xu hướng tương quan dương với nồng độ bụi vào buổi sáng sớm (độ ẩm cao tạo sương mù giữ các hạt bụi lơ lửng gần mặt đất).

### Câu 10: Ý nghĩa của cấu hình `'ignore.malformed.json' = 'true'` trong SerDe là gì?
**Trả lời:**
- Đây là cơ chế phòng vệ khi xử lý dữ liệu lớn (Fault-tolerant data processing). Nếu một tệp dữ liệu trên S3 bị lỗi một dòng (ví dụ do ngắt mạng khi ghi file dẫn đến thiếu dấu đóng ngoặc nhọn), SerDe sẽ bỏ qua dòng hỏng đó hoặc trả về giá trị NULL thay vì quăng ngoại lệ làm sập toàn bộ câu truy vấn của người dùng.

### Câu 11: Đối chiếu 3 chiều Log – Metric – S3 trong Tuần 4 được thực hiện như thế nào?
**Trả lời:**
- Nhóm kiểm chứng sự toàn vẹn 1-1 của một lượt chạy:
  1. **Log:** Trong CloudWatch Logs xuất hiện đúng cặp sự kiện `START`, `END`, `REPORT` và dòng log kết quả `[INFO] Result` của Request ID tương ứng.
  2. **Metric:** Trong CloudWatch Metrics ghi nhận đúng `1.0 Invocation` và `0.0 Errors` trong chu kỳ 300 giây (tỷ lệ lỗi 0,0%).
  3. **S3 & Athena:** Trên S3 xuất hiện đúng tệp JSON mới và câu truy vấn Athena `SELECT * ... WHERE record_id = '...'` đọc ra chính xác bản ghi đó.

### Câu 12: Tại sao chi phí thực tế trên AWS Cost Explorer của sinh viên Tiến Sơn lại là số âm hoặc bằng 0,00 USD?
**Trả lời:**
- Boto3 gọi API `GetCostAndUsage` với metric `UnblendedCost`. Tài khoản của sinh viên Tiến Sơn ghi nhận tổng chi phí gốc là `-0.000000339 USD`, khi làm tròn đến cent hiển thị là `0.00 USD`.
- Giá trị gốc mang dấu âm rất nhỏ này là do chính sách điều chỉnh số lẻ hoặc hoàn tiền (Credit adjustment/Refund) tự động từ hệ thống thanh toán của AWS, hoàn toàn là dữ liệu gốc do AWS Cost Explorer API trả về.

### Câu 13: Template CloudFormation của nhóm quản lý bao nhiêu tài nguyên và có những tài nguyên cốt lõi nào?
**Trả lời:**
- Template `weather-stack.json` quản lý trọn vẹn **17 tài nguyên AWS Serverless**:
  * 1 S3 Data Lake Bucket và 1 Bucket Policy (bắt buộc HTTPS).
  * 1 Secrets Manager Secret lưu cấu hình API.
  * 1 Lambda Function, 1 Lambda Permission và 1 CloudWatch Log Group.
  * 1 EventBridge Rule (lịch thu thập).
  * 1 Glue Database (`weather_aqi_db`), 1 Athena Table và 1 Athena Workgroup độc lập.
  * 1 SNS Topic, 1 Email Subscription và 1 SNS Topic Policy.
  * 2 CloudWatch Metric Filters (`ResultLogLines`, `ErrorLogLines`), 1 CloudWatch Alarm và 1 CloudWatch Dashboard.

### Câu 14: Nhóm đã thực hiện các biện pháp an toàn bảo mật nào (Security Audit)?
**Trả lời:**
- Nhóm rà soát 11 tiêu chí an toàn:
  1. Kích hoạt Block Public Access 100% (4/4 thiết lập) cho toàn bộ S3 bucket.
  2. Bắt buộc truyền dữ liệu qua giao thức mã hóa HTTPS (TLS 1.3) bằng S3 Bucket Policy từ chối `aws:SecureTransport = false`.
  3. Mã hóa dữ liệu tĩnh mặc định trên S3 bằng AES256 (SSE-S3).
  4. Quản lý thông tin xác thực tập trung qua Secrets Manager, tuyệt đối không hardcode API key hay access key vào mã nguồn Git.
  5. Ràng buộc quyền gọi Lambda chỉ từ đúng ARN của EventBridge Rule và đúng SourceAccount.

### Câu 15: Sau khi kết thúc buổi thực hành, nhóm làm cách nào để không bị trừ hết tiền trong AWS Learner Lab?
**Trả lời:**
- Nhóm xây dựng công cụ quản lý vòng đời tài nguyên `session_control.py` cùng 2 script PowerShell:
  * Cuối phiên: Chạy `cleanup_resources.ps1` để chuyển EventBridge Rule sang trạng thái `DISABLED`. Trạng thái trước khi tắt được ghi bền vững vào file JSON.
  * Đầu phiên: Chạy `start_resources.ps1` để đọc file trạng thái và khôi phục Rule sang `ENABLED`.
  * Nhờ vậy, Lambda không bị chạy liên tục khi sinh viên không ngồi máy tính, bảo toàn số credit cho học phần.

---
*Tài liệu được biên soạn phục vụ học tập, ôn luyện vấn đáp và làm báo cáo đồ án môn học Điện toán đám mây.*
