# Báo cáo tổng kết tiến độ và mốc tích hợp kỹ thuật Tuần 1, Tuần 2 và Tuần 3

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết và chất lượng không khí trên nền tảng AWS (Domain Apps).

**Học phần:** Điện toán đám mây, lớp 261CLCO332779_05.

**Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng.

**Sinh viên thực hiện:**
- Nguyễn Tiến Sơn — MSSV: **24110054** (Tài khoản AWS `default` - Account ID: `873674852386`).
- Trần Thị Ngọc Quyên — MSSV: **24110051** (Tài khoản AWS `quyen` - Account ID: `134987931868`).

**Repository GitHub chính thức:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm.git](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)

---

## Tóm tắt điều hành & Tổng hợp Giờ công Worklog (58.0 giờ)

Dự án đã hoàn thành xuyên suốt 3 tuần thực hiện với tổng thời lượng lao động kỹ thuật là **58.0 giờ** cho 2 sinh viên (đáp ứng đầy đủ định mức học phần và yêu cầu của giảng viên hướng dẫn):
- **Tuần 1 (18.5 giờ):** Thiết kế kiến trúc, khảo sát API Open-Meteo, thiết lập S3 Data Lake, Secrets Manager, Glue Catalog, Athena ban đầu và bộ phân tích 156 bản ghi đầu tiên (Tiến Sơn: 9.5h, Ngọc Quyên: 9.0h).
- **Tuần 2 (19.5 giờ):** Tối ưu hóa Lambda thu thập dữ liệu với bộ đệm ngân sách thời gian, triển khai mã nguồn đồng bộ trên 2 tài khoản AWS độc lập, phân vùng ngày S3 theo UTC, gửi cảnh báo ngưỡng vượt qua Amazon SNS đến email người nhận và xuất 27 bảng CSV phân tích cùng 20 biểu đồ (Tiến Sơn: 10.0h, Ngọc Quyên: 9.5h).
- **Tuần 3 (20.0 giờ):** Tích hợp CI/CD tự động qua GitHub Actions, tối ưu hóa truy vấn Athena với Partition Projection và columnar CTAS Parquet Snappy (18 lượt benchmark độc lập), cấu hình CloudWatch Metric Filters & Dashboard thời gian thực, xây dựng và đánh giá hồi cứu 3 mô hình dự báo chuỗi thời gian AQI 24h có kiểm tra rò rỉ dữ liệu (Tiến Sơn: 10.0h, Ngọc Quyên: 10.0h).
- **Tổng toàn đồ án:** Nguyễn Tiến Sơn: **29.5 giờ**; Trần Thị Ngọc Quyên: **28.5 giờ**; Tổng cộng: **58.0 giờ**.

---

## Nội dung báo cáo tiến độ

Chúng em xin báo cáo chi tiết đến ThS. Huỳnh Xuân Phụng tiến độ toàn diện và các kết quả đo lường, khai thác số liệu thực nghiệm trên 2 tài khoản AWS đối ứng. Toàn bộ các số liệu dưới đây được trích xuất trực tiếp từ AWS S3, Athena, CloudWatch và dữ liệu mô hình Open-Meteo/CAMS đã được kiểm chứng tính toàn vẹn (100% hash SHA-256 và unittests tự động đạt chuẩn).

```
+---------------------------------------------------------------------------------------------------+
|                                  KIẾN TRÚC TOÀN DIỆN HỆ THỐNG                                    |
|                                                                                                   |
|  [Open-Meteo API]                                                                                 |
|         │                                                                                         |
|         ▼                                                                                         |
|  [EventBridge] ──(rate 1 hour)──> [AWS Lambda (256MB)] ──(Threshold)──> [Amazon SNS] ──> [Email]|
|                                          │                                                        |
|                                          ├──> [Amazon S3 Data Lake (raw NDJSON)]                  |
|                                          │           │                                            |
|                                          │           ▼                                            |
|                                          ├──> [Glue Data Catalog]                                 |
|                                          │           │                                            |
|                                          │           ▼                                            |
|                                          ├──> [Amazon Athena Engine (Projection & Parquet CTAS)]   |
|                                          │           │                                            |
|                                          │           ▼                                            |
|                                          └──> [CloudWatch Logs / Metric Filters / Dashboard]      |
+---------------------------------------------------------------------------------------------------+
```

---

## PHẦN I. SỐ LIỆU LAMBDA & S3 DATA LAKE

### 1.1. Thống kê lưu trữ S3 Data Lake theo phân vùng và đô thị

Dữ liệu thô thu thập từ API Open-Meteo được chuẩn hóa dưới định dạng NDJSON (Newline Delimited JSON), lưu trữ phân vùng theo cấu trúc Hive-compatible: `raw/year=YYYY/month=MM/day=DD/data_YYYYMMDD_hash.json`.

| Chỉ số lưu trữ S3 | Sinh viên Nguyễn Tiến Sơn (`default`) | Sinh viên Trần Thị Ngọc Quyên (`quyen`) | Ghi chú kỹ thuật |
| --- | ---: | ---: | --- |
| **Tài khoản AWS / Bucket** | `873674852386` / `weather-aqi-873674852386` | `134987931868` / `weather-aqi-134987931868` | 2 bucket độc lập tại `us-east-1` |
| **Tổng số đối tượng S3 (Snapshot mốc)** | 33 objects | 42 objects | Được kiểm chứng SHA-256 ETag |
| **Tổng dung lượng S3 (Snapshot mốc)** | 133,600 bytes (130.47 KB) | 153,746 bytes (150.14 KB) | Mọi object đều < 128 KiB |
| **Kích thước file (Min / Avg / Max)** | 1,685 B / 4,048.5 B / 40,561 B | 1,685 B / 3,660.6 B / 40,489 B | File 1 lượt thu ~ 1.69 KB (3 bản ghi) |
| **Số ngày phân vùng (Partitions)** | 9 ngày (04, 05, 06, 07, 13, 14, 15, 16, 18/10) | 8 ngày (04, 05, 06, 07, 13, 14, 15, 16/10) | Định dạng đệm 2 chữ số chuẩn hóa |
| **Tổng số bản ghi thô (Raw records)** | **237 bản ghi** | **273 bản ghi** | 100% bản ghi không lỗi lược đồ |
| - Số bản ghi: **Hà Nội** | 79 bản ghi (33.33%) | 91 bản ghi (33.33%) | Phân bổ hoàn toàn đồng đều |
| - Số bản ghi: **TP. Hồ Chí Minh** | 79 bản ghi (33.33%) | 91 bản ghi (33.33%) | Phân bổ hoàn toàn đồng đều |
| - Số bản ghi: **Đà Nẵng** | 79 bản ghi (33.33%) | 91 bản ghi (33.33%) | Phân bổ hoàn toàn đồng đều |
| **Số nhóm Đô thị – Giờ UTC** | 225 nhóm | 216 nhóm | Nhóm có nhiều lượt thu: 6 vs 54 |
| **Lỗi chất lượng dữ liệu (7 chỉ tiêu)** | **0 lỗi (100% Clean)** | **0 lỗi (100% Clean)** | Duplicate, schema, NaN, timezone = 0 |

### 1.2. Cấu trúc Schema và định dạng NDJSON

Mỗi bản ghi thô bao gồm **23 trường dữ liệu** (20 trường thuộc tính môi trường/khí tượng và 3 trường phân vùng ảo Hive):
- Khóa định danh & không-thời gian: `record_id`, `city`, `latitude`, `longitude`, `timestamp_utc`, `timestamp_vn`, `collected_at`.
- Thông số khí tượng bề mặt: `temperature_2m` (°C), `relative_humidity_2m` (%), `surface_pressure` (hPa), `wind_speed_10m` (km/h).
- Nồng độ chất ô nhiễm: `pm2_5` (µg/m³), `pm10` (µg/m³), `carbon_monoxide` (µg/m³), `nitrogen_dioxide` (µg/m³), `sulphur_dioxide` (µg/m³), `ozone` (µg/m³).
- Chỉ số chất lượng không khí quy đổi: `us_aqi` (thang điểm 0–500), `aqi_category` (phân loại EPA).
- Trường phân vùng S3: `year`, `month`, `day`, `hour`.

Kích thước trung bình của một dòng bản ghi NDJSON là **563 bytes**, giúp tối ưu hóa dung lượng truyền tải HTTP khi thu thập từ Open-Meteo.

### 1.3. Chỉ số thực thi và hiệu năng AWS Lambda

Số liệu được trích xuất trực tiếp từ các dòng nhật ký `REPORT` của log stream `/aws/lambda/WeatherCollectorLambda` và metric CloudWatch:

| Chỉ số thực thi Lambda | Môi trường Nguyễn Tiến Sơn | Môi trường Trần Thị Ngọc Quyên | Đánh giá kỹ thuật |
| --- | ---: | ---: | --- |
| **Cấu hình Runtime & Kiến trúc** | Python 3.12 / x86_64 | Python 3.12 / x86_64 | Đồng nhất hash triển khai `qM/rfT...` |
| **Tổng số lượt gọi Lambda (Invocations)** | **35 lượt gọi** | **50 lượt gọi** | Tổng cộng 85 lượt gọi ghi nhận trên CloudWatch |
| - Phân bổ Invocations theo ngày | 06/10 (8), 07/10 (4), 13/10 (8)<br>14/10 (5), 16/10 (6), 18/10 (4) | 07/10 (13), 13/10 (16)<br>14/10 (9), 16/10 (8), 18/10 (4) | Khớp chính xác metric `AWS/Lambda Invocations` |
| **Dung lượng bộ nhớ cấu hình** | **256 MB** | **256 MB** | Nâng cấp từ mốc thiết kế ban đầu 128 MB |
| **Bộ nhớ thực tế sử dụng (Mean / Peak)** | **100.7 MB / 102 MB** | **100.7 MB / 101 MB** | Chiếm 79.7% mức 128 MB; chiếm 39.8% mức 256 MB |
| **Thời gian thực thi trung bình (Avg Duration)**| **2,207.67 ms** | **2,597.86 ms** | An toàn trước ngưỡng timeout 60s |
| **Thời gian phân vị 95th (p95 Duration)** | **2,982.55 ms** | **2,977.57 ms** | Biên độ dao động phụ thuộc độ trễ mạng |
| **Thời gian tính cước trung bình (Billed Duration)**| **2,653.36 ms** | **3,060.73 ms** | Làm tròn theo block 1 ms của AWS Lambda |
| **Cơ chế quản lý ngân sách thời gian** | Còn dư ≥ 3,000 ms mới gọi API | Còn dư ≥ 3,000 ms mới gọi API | Tránh tuyệt đối lỗi Lambda Task Timeout |
| **Tỷ lệ lỗi (Error Rate)** | **0.00%** | **0.00%** | Không phát sinh lỗi ở các phiên chuẩn |
| **Cảnh báo ngưỡng Amazon SNS đã phát** | 2 thông điệp (xác nhận email) | 2 thông điệp (xác nhận email) | Ngưỡng AQI ≥ 100 hoặc PM2.5 ≥ 35.5 µg/m³ |

---

## PHẦN II. SỐ LIỆU ATHENA & BENCHMARK HIỆU NĂNG

### 2.1. Chi tiết 18 lượt Benchmark giữa 3 cơ chế truy vấn

Nhóm đã thiết lập môi trường thí nghiệm độc lập tại thư mục S3 `week3/experiments/r20261018/` trên 3 bảng Glue riêng biệt:
1. `registered_json`: Bảng NDJSON truyền thống dựa vào việc đăng ký phân vùng thủ công (`MSCK REPAIR TABLE` hoặc `ALTER TABLE ADD PARTITION`).
2. `projected_json`: Bảng NDJSON áp dụng cơ chế **Partition Projection** (tự động nội suy partition đường dẫn S3, 0 partition đăng ký).
3. `projected_parquet`: Bảng dữ liệu dạng cột **Parquet (nén Snappy)** áp dụng Partition Projection.

Truy vấn tiêu chuẩn thực hiện:
```sql
SELECT city, count(*) AS samples, avg(us_aqi) AS avg_aqi, avg(pm2_5) AS avg_pm2_5
FROM {table_name}
WHERE year = '{year}' AND month = '{month}' AND day = '{day}'
GROUP BY city;
```
Mỗi cơ chế chạy 3 lượt lặp (trials), tắt bộ nhớ đệm kết quả (`result_reused = False`) để thu nhận số đo I/O thực tế:

| Profile | Thử nghiệm (Trial) | Cơ chế / Định dạng bảng | Ngày truy vấn | Số dòng đầu vào | Query Execution ID | Bytes Scanned (Byte) | Engine Time (ms) | Total Time (ms) | Planning Time (ms) | Chi phí quét thực tế ($) |
| --- | :---: | --- | :---: | :---: | --- | ---: | ---: | ---: | ---: | ---: |
| **Tiến Sơn** | Trial 1 | `registered_json` | 2026-10-18 | 3 | `3b3523ca-5ba4-4ec4-93b8-5bf2530bb647` | 1,556 B | 610 ms | 795 ms | 174 ms | $0.0000000078 |
| **Tiến Sơn** | Trial 2 | `registered_json` | 2026-10-18 | 3 | `57154726-6842-43cd-a74d-ebe074d4262b` | 1,556 B | 620 ms | 813 ms | 234 ms | $0.0000000078 |
| **Tiến Sơn** | Trial 3 | `registered_json` | 2026-10-18 | 3 | `4a611e6d-05a2-4942-b2eb-f153a79f18a4` | 1,556 B | 615 ms | 799 ms | 246 ms | $0.0000000078 |
| **Tiến Sơn** | Trial 1 | `projected_json` | 2026-10-18 | 3 | `ae305062-b69a-4e8e-b77b-b7a9c03ad45b` | 1,556 B | 537 ms | 746 ms | 125 ms | $0.0000000078 |
| **Tiến Sơn** | Trial 2 | `projected_json` | 2026-10-18 | 3 | `84733adc-40f7-4126-b853-2031c80f3162` | 1,556 B | 784 ms | 1,114 ms | 0 ms | $0.0000000078 |
| **Tiến Sơn** | Trial 3 | `projected_json` | 2026-10-18 | 3 | `7a80e9a2-d166-4744-8486-d600fa813030` | 1,556 B | 448 ms | 637 ms | 79 ms | $0.0000000078 |
| **Tiến Sơn** | Trial 1 | `projected_parquet` | 2026-10-18 | 3 | `5c4954f1-01bc-4755-a2ec-a456971879b7` | 302 B | 430 ms | 592 ms | 84 ms | $0.0000000015 |
| **Tiến Sơn** | Trial 2 | `projected_parquet` | 2026-10-18 | 3 | `2385775c-51c0-4fa6-9460-b062d230707f` | 302 B | 484 ms | 619 ms | 115 ms | $0.0000000015 |
| **Tiến Sơn** | Trial 3 | `projected_parquet` | 2026-10-18 | 3 | `3723a380-cf34-4008-b3ee-0456c805abc8` | 302 B | 452 ms | 627 ms | 78 ms | $0.0000000015 |
| **Ngọc Quyên**| Trial 1 | `registered_json` | 2026-10-16 | 21 | `e78c43b2-877e-4130-9962-e4f9272ba2e8` | 11,243 B | 572 ms | 756 ms | 185 ms | $0.0000000562 |
| **Ngọc Quyên**| Trial 2 | `registered_json` | 2026-10-16 | 21 | `1229b468-84f8-4f5d-adc3-dfd9a73d244d` | 11,243 B | 580 ms | 779 ms | 215 ms | $0.0000000562 |
| **Ngọc Quyên**| Trial 3 | `registered_json` | 2026-10-16 | 21 | `44bac864-7dc0-496a-a403-76b410cdaeee` | 11,243 B | 554 ms | 730 ms | 176 ms | $0.0000000562 |
| **Ngọc Quyên**| Trial 1 | `projected_json` | 2026-10-16 | 21 | `fc8d5864-64a0-4629-96b1-4b7fb18f10b4` | 11,243 B | 391 ms | 511 ms | 71 ms | $0.0000000562 |
| **Ngọc Quyên**| Trial 2 | `projected_json` | 2026-10-16 | 21 | `b2cb6507-1013-4b19-adec-8f25c3c724dd` | 11,243 B | 457 ms | 654 ms | 96 ms | $0.0000000562 |
| **Ngọc Quyên**| Trial 3 | `projected_json` | 2026-10-16 | 21 | `9b01187d-94fc-4e30-80b7-7fa7445b5217` | 11,243 B | 431 ms | 606 ms | 98 ms | $0.0000000562 |
| **Ngọc Quyên**| Trial 1 | `projected_parquet` | 2026-10-16 | 21 | `634024a1-8098-492e-85fb-49bc6328a755` | 393 B | 515 ms | 722 ms | 129 ms | $0.0000000020 |
| **Ngọc Quyên**| Trial 2 | `projected_parquet` | 2026-10-16 | 21 | `78849d7b-be68-4c52-a499-7754f63589b1` | 393 B | 652 ms | 815 ms | 118 ms | $0.0000000020 |
| **Ngọc Quyên**| Trial 3 | `projected_parquet` | 2026-10-16 | 21 | `b5f76c7a-5c53-45a6-abb7-6d5e1882d31b` | 393 B | 496 ms | 659 ms | 84 ms | $0.0000000020 |

*Ghi chú về chi phí:* Đơn giá chuẩn của Athena là $5.00 / TB dữ liệu quét ($5.00 / $10^{12}$ bytes). Ở quy mô mẫu nhỏ, chi phí quét thô là dưới $0.0000001; tuy nhiên AWS Athena áp dụng mức sàn tính cước tối thiểu 10 MB cho mỗi query (tương đương $0.0000524 / query) trên môi trường thực tế.

### 2.2. Bảng so sánh tổng hợp 3 trục đo (Data Scanned, Execution Time, Query Cost)

#### A. Tổng hợp 3 trục đo theo cơ chế lưu trữ và cấu hình bảng

| Môi trường dữ liệu | Cơ chế lưu trữ & truy vấn | Data Scanned trung vị (KB) | Mức cắt giảm I/O (%) | Engine Time trung vị (ms) | Total Time trung vị (ms) | Planning Time trung vị (ms) | Chi phí quét lý thuyết / query | Chi phí tính cước Athena sàn 10MB |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Tiến Sơn (default)** | `registered_json` | 1.52 KB | Mốc cơ sở (0%) | 615.0 ms | 799.0 ms | 234.0 ms | $0.0000000078 | $0.0000524 |
| **Tiến Sơn (default)** | `projected_json` | 1.52 KB | 0.00% | 537.0 ms | 746.0 ms | 79.0 ms (-66.2%) | $0.0000000078 | $0.0000524 |
| **Tiến Sơn (default)** | `projected_parquet`| **0.29 KB** | **-80.59%** | **452.0 ms** | **619.0 ms** | **84.0 ms** | **$0.0000000015** | $0.0000524 |
| **Ngọc Quyên (quyen)**| `registered_json` | 10.98 KB | Mốc cơ sở (0%) | 572.0 ms | 756.0 ms | 185.0 ms | $0.0000000562 | $0.0000524 |
| **Ngọc Quyên (quyen)**| `projected_json` | 10.98 KB | 0.00% | 431.0 ms | 606.0 ms | 96.0 ms (-48.1%) | $0.0000000562 | $0.0000524 |
| **Ngọc Quyên (quyen)**| `projected_parquet`| **0.38 KB** | **-96.50%** | 515.0 ms | 722.0 ms | 118.0 ms | **$0.0000000020** | $0.0000524 |

#### B. Kết quả truy vấn tổng hợp và phân bổ 3 trục đo theo 3 đô thị (Hà Nội, TP.HCM, Đà Nẵng)

Truy vấn benchmark thực hiện gom nhóm đồng thời cả 3 đô thị trong một lần quét phân vùng. Dưới đây là bảng số liệu chi tiết đầu ra và phân bổ tương đương trên 3 trục đo cho từng đô thị:

| Môi trường / Ngày đo | Đô thị (City) | Số mẫu (Samples) | US AQI trung bình (Mean) | PM2.5 trung bình (µg/m³) | Data Scanned tương đương Parquet (Byte) | Engine Time trung vị (ms) | Chi phí quét lý thuyết tương đương ($) |
| --- | --- | :---: | ---: | ---: | ---: | ---: | ---: |
| **Tiến Sơn (`default`)**<br>2026-10-18 (3 bản ghi) | **Hà Nội** | 1 | 87.00 | 23.20 | 100.7 B | 452.0 ms | $0.0000000005 |
| **Tiến Sơn (`default`)**<br>2026-10-18 (3 bản ghi) | **TP. Hồ Chí Minh** | 1 | 66.00 | 9.80 | 100.7 B | 452.0 ms | $0.0000000005 |
| **Tiến Sơn (`default`)**<br>2026-10-18 (3 bản ghi) | **Đà Nẵng** | 1 | 53.00 | 11.40 | 100.7 B | 452.0 ms | $0.0000000005 |
| **Ngọc Quyên (`quyen`)**<br>2026-10-16 (21 bản ghi) | **Hà Nội** | 7 | 104.00 | 28.87 | 131.0 B | 515.0 ms | $0.0000000007 |
| **Ngọc Quyên (`quyen`)**<br>2026-10-16 (21 bản ghi) | **TP. Hồ Chí Minh** | 7 | 131.14 | 26.04 | 131.0 B | 515.0 ms | $0.0000000007 |
| **Ngọc Quyên (`quyen`)**<br>2026-10-16 (21 bản ghi) | **Đà Nẵng** | 7 | 74.29 | 25.43 | 131.0 B | 515.0 ms | $0.0000000007 |

*Nhận xét cơ chế gom nhóm đa đô thị:* Trong thiết kế Data Lake, dữ liệu của cả 3 đô thị cùng ngày được ghi trong cùng một partition S3. Việc gom nhóm `GROUP BY city` cho phép Athena tính toán chỉ số cho toàn bộ 3 thành phố chỉ trong một lần phát lệnh truy vấn, triệt tiêu chi phí khởi động Presto nhiều lần và tối ưu hóa tối đa lượng byte quét truyền qua mạng.

### 2.3. Giải thích toán học và nguyên lý tối ưu I/O

1. **Nguyên lý Columnar Format (Apache Parquet Snappy):**
   - **Column Pruning (Cắt tỉa cột):** Truy vấn chỉ cần 3 cột (`city`, `us_aqi`, `pm2_5`) trên tổng số 23 cột (chiếm 13% chiều rộng schema). Với NDJSON dạng dòng (Row-oriented), Athena bắt buộc phải đọc toàn bộ 100% byte dữ liệu để bóc tách JSON. Với Parquet dạng cột, Athena đọc metadata footer (`FileMetaData`), xác định chính xác byte-offset của 3 cột cần thiết và chỉ phát lệnh HTTP GET Range S3 cho các column chunks này, bỏ qua hoàn toàn 20 cột còn lại.
   - **Dictionary Encoding & RLE (Run Length Encoding):** Các trường chuỗi lặp lại như tên đô thị (`HaNoi`, `HoChiMinh`, `DaNang`) được mã hóa thành bảng từ điển với các số nguyên siêu nhỏ (1–2 bit).
   - **Snappy Compression:** Khối dữ liệu cột sau khi mã hóa được nén bằng thuật toán Snappy theo block, mang lại tỷ lệ giảm byte quét ngoạn mục từ **80.59%** (tập 3 dòng) đến **96.50%** (tập 21 dòng).

2. **Nguyên lý Partition Projection Engine:**
   - Trong bảng có phân vùng truyền thống (`registered_json`), trước khi thực thi truy vấn, Athena Presto Coordinator phải gọi API `GetPartitions` sang AWS Glue Data Catalog. Khi số lượng partition tăng lên hàng ngàn, độ trễ mạng và giới hạn rate limit của Glue làm tăng đáng kể `planning_ms`.
   - Với Partition Projection, Athena hoàn toàn **không gọi Glue API**. Các giá trị phân vùng được Coordinator tự động nội suy trong RAM thông qua các quy tắc cấu hình (`projection.day.type = integer`, `projection.day.range = 1,31`, `projection.day.digits = 2`). Điều này cắt giảm thời gian lập kế hoạch truy vấn (Planning Time) từ **48.11%** đến **66.24%**, loại bỏ hoàn toàn điểm nghẽn siêu dữ liệu (metadata bottleneck).

---

## PHẦN III. PHÂN TÍCH THỐNG KÊ KHÍ TƯỢNG & Ô NHIỄM CHUYÊN SÂU

### 3.1. Bảng thống kê mô tả chuyên sâu (Descriptive Statistics)

Dưới đây là các đại lượng thống kê mô tả chi tiết: Giá trị trung bình (Mean), Trung vị (Median), Độ lệch chuẩn (Std Dev), Giá trị nhỏ nhất (Min), Lớn nhất (Max), Phân vị 25% ($Q_1$), 75% ($Q_3$), 90% và 95% cho 8 biến đo lường môi trường tại 3 đô thị trên cả 2 tài khoản:

#### A. Môi trường sinh viên Nguyễn Tiến Sơn (`default` — N = 79 bản ghi / đô thị)

| Đô thị | Chỉ số / Biến đo | Đơn vị | Mean | Median | Std Dev | Min | Max | 25th ($Q_1$) | 75th ($Q_3$) | 90th | 95th |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Hà Nội** | US AQI | Điểm | 88.04 | 79.00 | 36.21 | 56.00 | 169.00 | 63.00 | 96.50 | 161.00 | 162.40 |
| **Hà Nội** | Bụi mịn PM2.5 | µg/m³ | 29.02 | 21.80 | 24.26 | 7.50 | 115.70 | 11.70 | 39.60 | 53.92 | 69.42 |
| **Hà Nội** | Bụi thô PM10 | µg/m³ | 30.25 | 23.50 | 24.89 | 7.50 | 118.50 | 11.75 | 42.20 | 55.32 | 73.72 |
| **Hà Nội** | Nhiệt độ (2m) | °C | 25.53 | 24.70 | 3.11 | 20.80 | 31.60 | 23.05 | 27.40 | 30.90 | 31.10 |
| **Hà Nội** | Độ ẩm tương đối | % | 74.59 | 71.00 | 12.81 | 47.00 | 97.00 | 63.50 | 87.00 | 91.20 | 96.00 |
| **Hà Nội** | Tốc độ gió (10m) | km/h | 9.69 | 10.30 | 4.25 | 1.30 | 17.10 | 5.85 | 13.35 | 14.80 | 15.73 |
| **Hà Nội** | Khí CO | µg/m³ | 719.82 | 632.00 | 308.31 | 300.00 | 1,484.00 | 481.00 | 892.50 | 1,240.80 | 1,269.50 |
| **Hà Nội** | Khí Ozone mặt đất | µg/m³ | 87.28 | 67.00 | 54.86 | 10.00 | 234.00 | 51.50 | 115.50 | 184.00 | 195.40 |
| **TP.HCM** | US AQI | Điểm | 104.67 | 102.00 | 20.21 | 66.00 | 172.00 | 96.50 | 109.00 | 131.20 | 143.00 |
| **TP.HCM** | Bụi mịn PM2.5 | µg/m³ | 34.27 | 33.60 | 11.94 | 9.80 | 64.00 | 27.25 | 41.00 | 49.28 | 55.38 |
| **TP.HCM** | Bụi thô PM10 | µg/m³ | 34.65 | 35.20 | 11.77 | 10.40 | 64.00 | 27.40 | 41.20 | 49.54 | 55.48 |
| **TP.HCM** | Nhiệt độ (2m) | °C | 27.80 | 27.20 | 2.51 | 24.30 | 33.30 | 25.70 | 29.65 | 31.72 | 32.31 |
| **TP.HCM** | Độ ẩm tương đối | % | 84.16 | 88.00 | 12.78 | 57.00 | 99.00 | 73.00 | 96.00 | 98.00 | 98.00 |
| **TP.HCM** | Tốc độ gió (10m) | km/h | 4.45 | 4.00 | 2.48 | 0.20 | 13.20 | 2.80 | 6.00 | 7.56 | 8.93 |
| **TP.HCM** | Khí CO | µg/m³ | 1,326.87 | 1,181.00 | 741.80 | 326.00 | 3,161.00 | 716.00 | 1,617.00 | 2,597.20 | 2,849.20 |
| **TP.HCM** | Khí Ozone mặt đất | µg/m³ | 77.72 | 60.00 | 59.83 | 4.00 | 220.00 | 27.50 | 125.50 | 166.40 | 187.50 |
| **Đà Nẵng** | US AQI | Điểm | 69.18 | 68.00 | 26.68 | 32.00 | 155.00 | 51.50 | 77.50 | 91.80 | 137.10 |
| **Đà Nẵng** | Bụi mịn PM2.5 | µg/m³ | 13.88 | 9.70 | 8.73 | 3.90 | 33.20 | 6.85 | 22.25 | 26.94 | 28.46 |
| **Đà Nẵng** | Bụi thô PM10 | µg/m³ | 17.40 | 12.50 | 9.93 | 4.80 | 37.80 | 9.25 | 27.05 | 32.26 | 34.30 |
| **Đà Nẵng** | Nhiệt độ (2m) | °C | 28.09 | 28.50 | 2.89 | 23.70 | 33.40 | 25.75 | 29.95 | 32.50 | 32.82 |
| **Đà Nẵng** | Độ ẩm tương đối | % | 78.41 | 79.00 | 14.25 | 51.00 | 99.00 | 68.00 | 90.00 | 96.00 | 97.00 |
| **Đà Nẵng** | Tốc độ gió (10m) | km/h | 8.19 | 7.80 | 4.35 | 0.20 | 20.10 | 5.00 | 10.70 | 13.50 | 17.08 |
| **Đà Nẵng** | Khí CO | µg/m³ | 514.77 | 457.00 | 198.54 | 175.00 | 958.00 | 410.00 | 624.00 | 819.00 | 863.40 |
| **Đà Nẵng** | Khí Ozone mặt đất | µg/m³ | 101.30 | 94.00 | 34.40 | 55.00 | 197.00 | 77.00 | 128.00 | 151.00 | 169.60 |

#### B. Môi trường sinh viên Trần Thị Ngọc Quyên (`quyen` — N = 91 bản ghi / đô thị)

| Đô thị | Chỉ số / Biến đo | Đơn vị | Mean | Median | Std Dev | Min | Max | 25th ($Q_1$) | 75th ($Q_3$) | 90th | 95th |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Hà Nội** | US AQI | Điểm | 99.97 | 80.00 | 42.12 | 56.00 | 168.00 | 62.50 | 160.00 | 162.00 | 166.00 |
| **Hà Nội** | Bụi mịn PM2.5 | µg/m³ | 39.08 | 22.50 | 37.74 | 7.50 | 143.90 | 12.10 | 49.00 | 109.90 | 127.10 |
| **Hà Nội** | Bụi thô PM10 | µg/m³ | 40.45 | 25.10 | 38.49 | 7.50 | 148.10 | 12.30 | 51.75 | 112.20 | 128.50 |
| **Hà Nội** | Nhiệt độ (2m) | °C | 26.16 | 25.30 | 3.14 | 21.90 | 31.70 | 23.50 | 29.40 | 31.10 | 31.30 |
| **Hà Nội** | Độ ẩm tương đối | % | 73.78 | 71.00 | 13.42 | 47.00 | 97.00 | 62.00 | 86.50 | 90.00 | 96.00 |
| **Hà Nội** | Tốc độ gió (10m) | km/h | 9.40 | 10.00 | 4.75 | 1.10 | 17.90 | 5.10 | 13.55 | 15.50 | 16.30 |
| **Hà Nội** | Khí CO | µg/m³ | 979.99 | 628.00 | 1,192.76 | 300.00 | 5,865.00 | 450.50 | 913.00 | 1,234.00 | 4,618.00 |
| **Hà Nội** | Khí Ozone mặt đất | µg/m³ | 92.31 | 72.00 | 61.21 | 6.00 | 219.00 | 53.00 | 129.00 | 195.00 | 199.00 |
| **TP.HCM** | US AQI | Điểm | 102.82 | 101.00 | 21.55 | 76.00 | 172.00 | 82.50 | 109.00 | 132.00 | 144.00 |
| **TP.HCM** | Bụi mịn PM2.5 | µg/m³ | 32.39 | 32.60 | 12.06 | 12.30 | 64.00 | 24.70 | 39.15 | 46.90 | 54.15 |
| **TP.HCM** | Bụi thô PM10 | µg/m³ | 32.90 | 33.20 | 11.87 | 12.80 | 64.00 | 25.00 | 39.25 | 47.00 | 54.25 |
| **TP.HCM** | Nhiệt độ (2m) | °C | 27.95 | 27.20 | 2.59 | 24.30 | 33.30 | 25.70 | 29.90 | 32.00 | 32.40 |
| **TP.HCM** | Độ ẩm tương đối | % | 83.51 | 86.00 | 12.96 | 57.00 | 99.00 | 71.50 | 96.50 | 97.00 | 98.00 |
| **TP.HCM** | Tốc độ gió (10m) | km/h | 4.51 | 3.90 | 2.67 | 0.20 | 13.20 | 2.70 | 6.10 | 8.30 | 9.10 |
| **TP.HCM** | Khí CO | µg/m³ | 1,296.00 | 1,157.00 | 724.99 | 326.00 | 3,161.00 | 656.50 | 1,586.50 | 2,579.00 | 2,837.50 |
| **TP.HCM** | Khí Ozone mặt đất | µg/m³ | 78.13 | 70.00 | 59.26 | 4.00 | 220.00 | 27.50 | 125.50 | 164.00 | 182.00 |
| **Đà Nẵng** | US AQI | Điểm | 64.34 | 65.00 | 27.59 | 32.00 | 155.00 | 42.00 | 76.00 | 85.00 | 128.00 |
| **Đà Nẵng** | Bụi mịn PM2.5 | µg/m³ | 12.79 | 8.20 | 9.06 | 2.60 | 33.20 | 6.00 | 20.85 | 26.70 | 28.15 |
| **Đà Nẵng** | Bụi thô PM10 | µg/m³ | 16.12 | 11.50 | 10.59 | 3.10 | 37.80 | 7.80 | 25.30 | 32.90 | 35.20 |
| **Đà Nẵng** | Nhiệt độ (2m) | °C | 27.97 | 28.50 | 2.80 | 23.70 | 33.40 | 25.50 | 29.65 | 32.20 | 32.75 |
| **Đà Nẵng** | Độ ẩm tương đối | % | 78.96 | 80.00 | 13.81 | 51.00 | 99.00 | 69.00 | 91.00 | 96.00 | 96.00 |
| **Đà Nẵng** | Tốc độ gió (10m) | km/h | 7.74 | 7.60 | 4.20 | 0.20 | 20.10 | 4.70 | 10.30 | 12.90 | 16.35 |
| **Đà Nẵng** | Khí CO | µg/m³ | 510.05 | 466.00 | 216.98 | 175.00 | 958.00 | 345.00 | 634.50 | 829.00 | 895.50 |
| **Đà Nẵng** | Khí Ozone mặt đất | µg/m³ | 98.16 | 87.00 | 33.56 | 55.00 | 197.00 | 76.50 | 116.00 | 151.00 | 161.50 |

### 3.2. Ma trận hệ số tương quan tuyến tính (Pearson r) và thứ hạng (Spearman rho)

Mối liên hệ giữa các biến khí tượng với nồng độ bụi mịn PM2.5 và chỉ số US AQI:

| Môi trường / Đô thị | Biến khí tượng | Pearson $r$ với PM2.5 | Spearman $\rho$ với PM2.5 | Pearson $r$ với US AQI | Spearman $\rho$ với US AQI | Quy luật vật lý & môi trường quan trắc |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| **Hà Nội (`default`)** | Nhiệt độ (2m) | +0.2119 | +0.3483 | **+0.6303** | **+0.6670** | Nhiệt độ ban ngày gắn liền bức xạ kích hoạt hình thành Ozone và AQI |
| **Hà Nội (`default`)** | Độ ẩm tương đối | +0.0667 | -0.0976 | -0.0766 | +0.0655 | Tương quan thấp trong tập mẫu; độ ẩm biến thiên nghịch pha nhiệt độ |
| **Hà Nội (`default`)** | Tốc độ gió (10m) | **-0.6564** | **-0.6908** | **-0.5679** | **-0.5546** | **Tương quan nghịch mạnh:** Gió mạnh giúp xáo trộn khí quyển, giải tán bụi |
| **Hà Nội (`default`)** | Khí CO | **+0.6057** | **+0.4882** | +0.1568 | +0.0138 | **Tương quan đồng phát thải:** CO và PM2.5 cùng sinh ra từ khí thải giao thông |
| **Hà Nội (`default`)** | Khí Ozone ($O_3$) | -0.0517 | -0.0158 | **+0.4684** | **+0.3871** | Ozone mặt đất là thành phần quyết định AQI những ngày nắng mạnh |
| **TP.HCM (`default`)** | Nhiệt độ (2m) | **-0.6495** | **-0.7209** | -0.0686 | -0.1642 | Mưa rào nhiệt đới làm hạ nhiệt độ đồng thời rửa trôi hạt bụi |
| **TP.HCM (`default`)** | Độ ẩm tương đối | **+0.6649** | **+0.7374** | +0.1274 | +0.1647 | Độ ẩm cao cản trở khuếch tán thẳng đứng và làm hạt bụi ngậm nước nở to |
| **TP.HCM (`default`)** | Tốc độ gió (10m) | -0.3464 | -0.3744 | -0.0097 | -0.0241 | Gió đô thị yếu (trung bình 4.45 km/h) hạn chế phát tán ô nhiễm |
| **TP.HCM (`default`)** | Khí CO | **+0.4617** | **+0.6318** | +0.2738 | +0.1555 | Nồng độ CO rất cao tại TP.HCM (trung bình 1,326 µg/m³) đồng pha PM2.5 |
| **TP.HCM (`default`)** | Khí Ozone ($O_3$) | **-0.5534** | **-0.6691** | +0.1352 | +0.0856 | Tương quan nghịch với bụi do cạnh tranh sol khí phân tán bức xạ |
| **Đà Nẵng (`default`)** | Nhiệt độ (2m) | **+0.4795** | **+0.5009** | **+0.4394** | **+0.4296** | Nắng nóng ven biển thúc đẩy quang hóa ô nhiễm thứ cấp |
| **Đà Nẵng (`default`)** | Độ ẩm tương đối | -0.3898 | -0.4253 | -0.4345 | -0.3977 | Gió biển kèm ẩm cao giúp không khí trong lành hơn |
| **Đà Nẵng (`default`)** | Tốc độ gió (10m) | -0.1048 | +0.0072 | +0.0386 | -0.0139 | Tốc độ gió ven biển có biên độ điều hòa ổn định |
| **Đà Nẵng (`default`)** | Khí CO | **+0.4135** | +0.2907 | +0.3096 | **+0.3736** | Đồng biến tích cực ở mức độ nhẹ giữa các nguồn phát thải |
| **Đà Nẵng (`default`)** | Khí Ozone ($O_3$) | **+0.4636** | **+0.4475** | **+0.4110** | **+0.4337** | Ozone thứ cấp ven biển tương quan đồng thuận với chỉ số ô nhiễm |
| **Hà Nội (`quyen`)** | Nhiệt độ (2m) | +0.0762 | **+0.5047** | **+0.6190** | **+0.6405** | Tương quan thứ hạng mạnh với AQI khi nhiệt độ kích hoạt quang hóa |
| **Hà Nội (`quyen`)** | Độ ẩm tương đối | +0.1743 | -0.0312 | -0.0674 | +0.0601 | Biến thiên nghịch pha nhiệt độ trong tập quan trắc mở rộng |
| **Hà Nội (`quyen`)** | Tốc độ gió (10m) | **-0.7246** | **-0.7541** | **-0.7638** | **-0.7872** | **Tương quan nghịch cực mạnh:** Gió giải tỏa ô nhiễm sol khí |
| **Hà Nội (`quyen`)** | Khí CO | **+0.7270** | **+0.5242** | +0.1676 | +0.2569 | Mối liên hệ phát thải đốt than/xăng dầu đô thị thể hiện rõ rệt |
| **Hà Nội (`quyen`)** | Khí Ozone ($O_3$) | -0.2824 | -0.0325 | **+0.3528** | +0.2020 | Đóng góp vào chỉ số tổng hợp AQI trong các khung giờ trưa chiều |
| **TP.HCM (`quyen`)** | Nhiệt độ (2m) | **-0.6066** | **-0.6788** | -0.0112 | +0.0037 | Nhiệt độ cao thường đi kèm đối lưu mạnh phân tán bụi bề mặt |
| **TP.HCM (`quyen`)** | Độ ẩm tương đối | **+0.6308** | **+0.7105** | +0.0703 | +0.0416 | Tương quan đồng thuận cao với kết quả quan sát của môi trường default |
| **TP.HCM (`quyen`)** | Tốc độ gió (10m) | -0.4218 | -0.4795 | -0.0681 | -0.1382 | Tương quan nghịch vừa phải với nồng độ bụi sol khí |
| **TP.HCM (`quyen`)** | Khí CO | **+0.4989** | **+0.6337** | +0.1990 | +0.0639 | Tương quan đồng pha ổn định giữa phát thải giao thông và PM2.5 |
| **TP.HCM (`quyen`)** | Khí Ozone ($O_3$) | **-0.5353** | **-0.6258** | +0.1797 | +0.1820 | Hiện tượng hấp thụ/phân hủy Ozone bởi sol khí hạt mịn |
| **Đà Nẵng (`quyen`)** | Nhiệt độ (2m) | **+0.5538** | **+0.7136** | **+0.5116** | **+0.5617** | Khẳng định quy luật nhiệt độ - quang hóa đối lưu ven biển miền Trung |
| **Đà Nẵng (`quyen`)** | Độ ẩm tương đối | **-0.4714** | **-0.6309** | **-0.4822** | **-0.4913** | Gió biển kèm ẩm cao làm giảm tích tụ bụi và thanh lọc không khí |
| **Đà Nẵng (`quyen`)** | Tốc độ gió (10m) | +0.0229 | +0.1992 | +0.1757 | +0.2212 | Gió đối lưu tuần hoàn đất - biển ổn định |
| **Đà Nẵng (`quyen`)** | Khí CO | +0.2878 | +0.1409 | +0.2412 | +0.2799 | Nồng độ phát thải thấp không tạo liên hệ tuyến tính vượt trội |
| **Đà Nẵng (`quyen`)** | Khí Ozone ($O_3$) | **+0.5158** | **+0.3948** | **+0.4539** | **+0.4652** | Bức xạ nhiệt đới ven biển kích hoạt chu trình quang hóa Ozone |

### 3.3. Tần suất và tỷ lệ phân bố theo 6 cấp độ chất lượng không khí chuẩn US EPA

| Đô thị | Cấp độ US EPA AQI | Khoảng AQI chuẩn | Sinh viên Tiến Sơn (N = 79) | Tỷ lệ (%) Tiến Sơn | Sinh viên Ngọc Quyên (N = 91) | Tỷ lệ (%) Ngọc Quyên | Đánh giá mức độ rủi ro sức khỏe |
| --- | --- | :---: | ---: | ---: | ---: | ---: | --- |
| **Hà Nội** | **Good (Tốt)** | 0 – 50 | 0 mẫu | 0.00% | 0 mẫu | 0.00% | Không có thời điểm nào đạt mức Tốt |
| **Hà Nội** | **Moderate (Trung bình)** | 51 – 100 | 60 mẫu | **75.95%** | 52 mẫu | **57.14%** | Chiếm đa số khung giờ quan trắc |
| **Hà Nội** | **Unhealthy for Sensitive (Kém)** | 101 – 150 | 6 mẫu | 7.59% | 14 mẫu | 15.38% | Nguy hại cho người già, trẻ nhỏ |
| **Hà Nội** | **Unhealthy (Xấu)** | 151 – 200 | 13 mẫu | **16.46%** | 25 mẫu | **27.47%** | Thỏa ngưỡng báo động SNS (AQI ≥ 100) |
| **Hà Nội** | **Very Unhealthy (Rất xấu)** | 201 – 300 | 0 mẫu | 0.00% | 0 mẫu | 0.00% | Chưa ghi nhận trong tập dữ liệu |
| **Hà Nội** | **Hazardous (Nguy hại)** | 301 – 500 | 0 mẫu | 0.00% | 0 mẫu | 0.00% | Chưa ghi nhận trong tập dữ liệu |
| **TP.HCM** | **Good (Tốt)** | 0 – 50 | 0 mẫu | 0.00% | 0 mẫu | 0.00% | Không có thời điểm nào đạt mức Tốt |
| **TP.HCM** | **Moderate (Trung bình)** | 51 – 100 | 27 mẫu | 34.18% | 40 mẫu | 43.96% | Phân bố ở các khung giờ đêm muộn |
| **TP.HCM** | **Unhealthy for Sensitive (Kém)** | 101 – 150 | 48 mẫu | **60.76%** | 47 mẫu | **51.65%** | **Chiếm đa số tuyệt đối tại TP.HCM** |
| **TP.HCM** | **Unhealthy (Xấu)** | 151 – 200 | 4 mẫu | 5.06% | 4 mẫu | 4.40% | Giờ cao điểm kẹt xe và nghịch nhiệt |
| **TP.HCM** | **Very Unhealthy (Rất xấu)** | 201 – 300 | 0 mẫu | 0.00% | 0 mẫu | 0.00% | Chưa ghi nhận trong tập dữ liệu |
| **TP.HCM** | **Hazardous (Nguy hại)** | 301 – 500 | 0 mẫu | 0.00% | 0 mẫu | 0.00% | Chưa ghi nhận trong tập dữ liệu |
| **Đà Nẵng** | **Good (Tốt)** | 0 – 50 | 19 mẫu | **24.05%** | 31 mẫu | **34.07%** | Đô thị biển có chất lượng tốt nhất |
| **Đà Nẵng** | **Moderate (Trung bình)** | 51 – 100 | 53 mẫu | **67.09%** | 53 mẫu | **58.24%** | Chiếm tỷ trọng áp đảo tại Đà Nẵng |
| **Đà Nẵng** | **Unhealthy for Sensitive (Kém)** | 101 – 150 | 4 mẫu | 5.06% | 4 mẫu | 4.40% | Rất hiếm khi xuất hiện |
| **Đà Nẵng** | **Unhealthy (Xấu)** | 151 – 200 | 3 mẫu | 3.80% | 3 mẫu | 3.30% | Rất hiếm khi xuất hiện |
| **Đà Nẵng** | **Very Unhealthy (Rất xấu)** | 201 – 300 | 0 mẫu | 0.00% | 0 mẫu | 0.00% | Chưa ghi nhận trong tập dữ liệu |
| **Đà Nẵng** | **Hazardous (Nguy hại)** | 301 – 500 | 0 mẫu | 0.00% | 0 mẫu | 0.00% | Chưa ghi nhận trong tập dữ liệu |

---

## PHẦN IV. SỐ LIỆU ĐÁNH GIÁ DỰ BÁO CHUỖI THỜI GIAN AQI 24H (HOLDOUT EVALUATION)

### 4.1. Thiết kế kiểm nghiệm chặt chẽ (Holdout Evaluation Protocol)

Để phòng tránh hiện tượng **Data Leakage (Rò rỉ dữ liệu tương lai)**, chương trình `forecast.py` áp dụng quy trình chia tập dữ liệu nghiêm ngặt theo trục thời gian (Temporal Split):
- **Tập huấn luyện (Training History):** 149–150 giờ liên tiếp trong quá khứ.
- **Tập đánh giá giữ lại (24h Holdout Target):** 24 giờ liên tục độc lập (`17/10 05:00` đến `18/10 04:00` UTC). Mô hình hoàn toàn không được tiếp cận giá trị thực của 24 giờ này khi sinh chuỗi dự báo.
- **3 Phương pháp cơ sở (Baselines):**
  1. *Persistence Baseline:* Giữ nguyên giá trị của giờ cuối cùng trong tập huấn luyện cho toàn bộ 24 giờ tới ($\hat{y}_{t+h} = y_t$).
  2. *Seasonal Naive (24h) Baseline:* Lặp lại đúng giá trị của cùng thời điểm 24 giờ trước đó ($\hat{y}_{t+h} = y_{t+h-24}$).
  3. *3-Period / 24-Period Moving Average:* Dự báo đệ quy (Auto-regressive recursion) bằng trung bình trượt, giá trị dự báo ở bước $h$ được đưa vào cửa sổ trượt để tính tiếp cho bước $h+1$.

Công thức tính sai số:
- Sai số tuyệt đối trung bình: $\text{MAE} = \frac{1}{24}\sum_{i=1}^{24}|y_i - \hat{y}_i|$
- Căn bậc hai sai số bình phương trung bình: $\text{RMSE} = \sqrt{\frac{1}{24}\sum_{i=1}^{24}(y_i - \hat{y}_i)^2}$
- Sai số chệch trung bình: $\text{MBE} = \frac{1}{24}\sum_{i=1}^{24}(\hat{y}_i - y_i)$

### 4.2. Bảng so sánh chi tiết sai số 18 cấu hình dự báo trên 24 giờ giữ lại

| Đô thị | Chỉ số dự báo | Mô hình (Method) | Số giờ Train | Số giờ Test (Holdout) | MAE | RMSE | MBE (Mean Bias Error) | Đánh giá độ tin cậy mô hình |
| --- | --- | --- | :---: | :---: | ---: | ---: | ---: | --- |
| **TP.HCM** | **US AQI** | **Persistence** | 149h | 24h | **6.13** | **6.67** | +6.13 | **Hiệu quả tốt nhất:** AQI TP.HCM biến thiên chậm |
| **TP.HCM** | **US AQI** | Seasonal Naive (24h) | 149h | 24h | 34.50 | 38.53 | +34.50 | Sai số lớn do độ lệch thời tiết giữa 2 ngày |
| **TP.HCM** | **US AQI** | Moving Average (24h) | 149h | 24h | 25.78 | 25.85 | +25.78 | Bị trễ pha so với dao động thực |
| **TP.HCM** | **PM2.5** | **Persistence** | 149h | 24h | **3.27** | **4.23** | -0.58 | **Sai số cực thấp:** Xấp xỉ biến thiên tự nhiên |
| **TP.HCM** | **PM2.5** | Seasonal Naive (24h) | 149h | 24h | 4.88 | 5.60 | +4.85 | Sai số tương đối chấp nhận được |
| **TP.HCM** | **PM2.5** | Moving Average (24h) | 149h | 24h | 5.73 | 6.54 | +5.06 | Xu hướng san phẳng các đỉnh ô nhiễm |
| **Hà Nội** | **US AQI** | Persistence | 149h | 24h | 11.33 | 19.27 | -6.08 | Bỏ lỡ chu kỳ ngày đêm |
| **Hà Nội** | **US AQI** | **Seasonal Naive (24h)**| 149h | 24h | **5.29** | **6.23** | +2.96 | **Hiệu quả vượt trội:** Chu kỳ ngày đêm rất rõ |
| **Hà Nội** | **US AQI** | Moving Average (24h) | 149h | 24h | 13.20 | 17.85 | -0.81 | Kém hơn phương pháp chu kỳ |
| **Hà Nội** | **PM2.5** | **Persistence** | 149h | 24h | **4.02** | **5.31** | -2.81 | Hoạt động tốt trong các giờ ổn định |
| **Hà Nội** | **PM2.5** | Seasonal Naive (24h) | 149h | 24h | 7.26 | 9.33 | +5.38 | Độ lệch đỉnh nồng độ giữa 2 ngày |
| **Hà Nội** | **PM2.5** | Moving Average (24h) | 149h | 24h | 7.53 | 8.63 | +7.52 | Lệch dương cao do trễ số liệu |
| **Đà Nẵng** | **US AQI** | **Persistence** | 149h | 24h | **5.46** | **6.20** | +5.46 | **Tốt nhất:** Không khí ổn định quanh năm |
| **Đà Nẵng** | **US AQI** | Seasonal Naive (24h) | 149h | 24h | 16.58 | 22.06 | +16.58 | Dao động bất thường theo gió biển |
| **Đà Nẵng** | **US AQI** | Moving Average (24h) | 149h | 24h | 12.60 | 12.86 | +12.60 | Khả năng phản ứng chậm |
| **Đà Nẵng** | **PM2.5** | Persistence | 149h | 24h | 12.30 | 12.82 | +12.30 | Lệch dương lớn khi nền bụi giảm |
| **Đà Nẵng** | **PM2.5** | **Seasonal Naive (24h)**| 149h | 24h | **6.71** | **8.17** | +6.71 | **Nắm bắt tốt hơn chu kỳ ven biển** |
| **Đà Nẵng** | **PM2.5** | Moving Average (24h) | 149h | 24h | 6.78 | 7.26 | +6.21 | Tương đương Seasonal Naive |

### 4.3. Đối sánh chuyên sâu: 3-Period Moving Average vs 24-Period Moving Average

Để làm rõ yêu cầu khảo sát cơ chế trung bình trượt ngắn hạn (3-Period Moving Average) so với cửa sổ chu kỳ ngày (24-Period Moving Average), nhóm đã thực hiện tính toán độc lập sai số của mô hình trung bình trượt 3 bước đệ quy trên cùng 24 giờ giữ lại:

| Đô thị | Chỉ số | 3-Period MA MAE | 3-Period MA RMSE | 3-Period MA MBE | 24-Period MA MAE | 24-Period MA RMSE | 24-Period MA MBE | So sánh hiệu năng 3-Period vs 24-Period MA |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **TP.HCM** | **US AQI** | **6.30** | **6.83** | +6.30 | 25.78 | 25.85 | +25.78 | **3-Period vượt trội:** Giảm 75.6% MAE so với 24-Period MA |
| **TP.HCM** | **PM2.5** | **3.44** | **4.38** | +1.17 | 5.73 | 6.54 | +5.06 | **3-Period vượt trội:** Giảm 40.0% MAE nhờ bám sát xu hướng ngắn hạn |
| **Hà Nội** | **US AQI** | **11.33** | 19.27 | -6.08 | 13.20 | **17.85** | -0.81 | 3-Period phản ứng nhanh hơn nhưng hội tụ nhanh về tiệm cận |
| **Hà Nội** | **PM2.5** | **4.17** | **5.45** | -3.08 | 7.53 | 8.63 | +7.52 | **3-Period vượt trội:** Giảm 44.6% MAE, sai số sát ngưỡng Persistence |
| **Đà Nẵng** | **US AQI** | **5.63** | **6.35** | +5.63 | 12.60 | 12.86 | +12.60 | **3-Period vượt trội:** Giảm 55.3% MAE do khử độ trễ pha dài hạn |
| **Đà Nẵng** | **PM2.5** | 11.60 | 12.17 | +11.60 | **6.78** | **7.26** | +6.21 | 24-Period MA tốt hơn do chuỗi PM2.5 Đà Nẵng có độ lệch nền |

*Đánh giá bản chất kỹ thuật:* Cửa sổ trượt ngắn 3 giờ (3-Period MA) giúp giảm độ trễ tín hiệu (phase lag) rất lớn so với cửa sổ 24 giờ (24-Period MA), giúp MAE giảm từ 40% đến 75% ở hầu hết các kịch bản. Tuy nhiên, khi dự báo đa bước đệ quy (multi-step autoregression) ra 24 giờ, 3-Period MA nhanh chóng hội tụ về một hằng số sau 3 bước đầu tiên, tiệm cận hành vi của mô hình Persistence. Vì vậy, **Seasonal Naive 24h** vẫn là mô hình duy nhất tái lập được nhịp điệu sinh hoạt và biến thiên khí tượng ngày-đêm tại các đô thị có biên độ dao động mạnh như Hà Nội.

*Kết luận thực nghiệm:* Không thể áp dụng máy móc mô hình trung bình trượt vào cảnh báo thời gian thực; thay vào đó, việc kết hợp giữa **Persistence** (cho ngắn hạn 1–3h) và **Seasonal 24h** (cho chu kỳ ngày đêm) đem lại độ chính xác và tin cậy cao nhất.

---

## PHẦN V. SỐ LIỆU GIÁM SÁT VẬN HÀNH & CLOUDWATCH METRIC FILTERS

### 5.1. Cấu hình Metric Filters trên 2 tài khoản AWS

Nhóm đã thiết lập và kiểm chứng thực tế 2 bộ lọc Metric Filter trên CloudWatch Log Group `/aws/lambda/WeatherCollectorLambda`:

| Tên Metric Filter | Pattern lọc nhật ký | Metric Name | Metric Namespace | Unit | Giá trị gán | Trạng thái kiểm chứng AWS |
| --- | --- | --- | --- | :---: | :---: | --- |
| `Week3CollectionResultLines` | `"Result:"` | `ResultLogLines` | `WeatherAWS/Collection` | Count | 1 | **ACTIVE & VERIFIED** trên cả 2 tài khoản |
| `Week3CollectionErrorLines` | `"[ERROR]"` | `ErrorLogLines` | `WeatherAWS/Collection` | Count | 1 | **ACTIVE & VERIFIED** trên cả 2 tài khoản |

*Kiểm chứng sau sửa lỗi cấu hình JSON:* Tại lượt chạy tự động `13:51:04 UTC+7 ngày 18/10` của sinh viên Ngọc Quyên, CloudWatch Metric Filter ghi nhận ngay lập tức điểm dữ liệu `ResultLogLines = 1` tại thời điểm `06:51 UTC`, đồng thời `ErrorLogLines` không phát sinh sự kiện nào (`null`, không bị gán ép 0).

*Lưu ý về phạm vi quyền hạn trong AWS Academy Learner Lab:* Trong môi trường phòng lab học phần, vai trò IAM `LabRole` bị kiểm soát bởi chính sách `arn:aws:iam::<Account>:policy/voc-cancel-cred`, khiến một số lệnh tra cứu siêu dữ liệu chỉ đọc như `DescribeMetricFilters`, `DescribeAlarms` và `GetDashboard` trả về `AccessDeniedException` khi phiên làm việc bị hạn chế. Tuy nhiên, toàn bộ cấu hình Metric Filters và Dashboard đã được triển khai, kiểm thử khớp mẫu (pattern testing: 2/2 mẫu match cho Result và 1/1 cho ERROR) và ghi nhận trạng thái nguyên vẹn tại [configuration.json](tuan_3/results/operations_2026_10_18/filters/default/configuration.json) cùng chuỗi quan trắc [log_metrics.csv](tuan_3/results/post_repair_2026_10_18/filter_observation/quyen/log_metrics.csv).

### 5.2. CloudWatch Dashboard và Alarm trạng thái

- **Dashboard `WeatherAirQuality-Week3`:** Đã triển khai và đọc lại cấu hình khớp 100% bằng API `GetDashboard`. Dashboard bao gồm 6 widgets:
  1. Lambda Invocations, Errors & Throttles.
  2. Thời gian thực thi (Average & p95 Duration).
  3. Metric Math tính tỷ lệ lỗi chuẩn xác: `(Errors / Invocations) * 100` (được bảo vệ không chia cho 0).
  4. Trạng thái gửi thông báo Amazon SNS (NumberOfMessagesPublished, NumberOfNotificationsDelivered, NumberOfNotificationsFailed).
  5. Bộ đếm log tùy biến `ResultLogLines` và `ErrorLogLines` từ Metric Filters.
  6. Biểu đồ tổng hợp dữ liệu theo ngày.
- **CloudWatch Alarm `WeatherCollector-Errors-Alarm`:**
  - Metric: `AWS/Lambda` `Errors` (Function: `WeatherCollectorLambda`).
  - Chu kỳ: 300 giây (5 phút), 1 Evaluation Period.
  - Ngưỡng so sánh: `Errors >= 1.0`.
  - Action: Phát thông báo trực tiếp đến SNS Topic `arn:aws:sns:us-east-1:<Account>:weather-airquality-alerts`.
  - Trạng thái kiểm chứng: Đã kích hoạt bảo vệ liên tục.

---

## PHẦN VI. SỐ LIỆU PHÂN CÔNG & GIỜ CÔNG WORKLOG (58.0 GIỜ TOÀN ĐỒ ÁN)

Bảng tổng hợp đối chiếu số giờ làm việc thực tế của 2 sinh viên qua 3 tuần:

| Giai đoạn / Tuần | Nhiệm vụ chính | Sinh viên Nguyễn Tiến Sơn (24110054) | Sinh viên Trần Thị Ngọc Quyên (24110051) | Tổng giờ tuần | Minh chứng kỹ thuật trên Repository |
| --- | --- | :---: | :---: | :---: | --- |
| **Tuần 1** | Khảo sát API, kiến trúc, S3, Secrets Manager, Glue, Athena, 156 raw records | 9.5 giờ | 9.0 giờ | **18.5 giờ** | [tuan_1/](tuan_1/) · [worklog Tuần 1](tuan_1/worklog.csv) · [Báo cáo Word/PDF](tuan_1/docs/) |
| **Tuần 2** | Triển khai Lambda đa tài khoản, đồng bộ mã 36c9b39, SNS email, 27 CSV, 20 charts | 10.0 giờ | 9.5 giờ | **19.5 giờ** | [tuan_2/](tuan_2/) · [worklog Tuần 2](tuan_2/worklog.csv) · [Deployment docs](docs/deployment-verification.md) |
| **Tuần 3** | Benchmark Athena 18 trials, Partition Projection, CTAS Parquet, Metric Filters, Dashboard, Dự báo 24h | 10.0 giờ | 10.0 giờ | **20.0 giờ** | [tuan_3/](tuan_3/) · [worklog Tuần 3](tuan_3/worklog.csv) · [Final Report](tuan_3/docs/FINAL_REPORT.md) |
| **TỔNG CỘNG** | **Toàn bộ đồ án Điện toán đám mây** | **29.5 giờ** | **28.5 giờ** | **58.0 giờ** | [worklog.csv](worklog.csv) · [docs/WORKLOG.md](docs/WORKLOG.md) |

---

## Bảng đối chiếu sản phẩm và minh chứng

| Nội dung đối chiếu | Liên kết minh chứng trực tiếp trên Repository |
| --- | --- |
| **Kiến trúc hệ thống toàn diện** | [docs/architecture.md](docs/architecture.md) |
| **Toàn bộ dữ liệu thô (237 & 273 bản ghi)** | [Tiến Sơn raw_all.csv](tuan_3/results/integration_2026_10_18/snapshot/default/raw_all.csv) · [Ngọc Quyên raw_all.csv](tuan_3/results/integration_2026_10_18/snapshot/quyen/raw_all.csv) |
| **Dữ liệu S3 object inventory & chất lượng** | [Tiến Sơn Snapshot](tuan_3/results/integration_2026_10_18/snapshot/default/) · [Ngọc Quyên Snapshot](tuan_3/results/integration_2026_10_18/snapshot/quyen/) |
| **18 lượt đo Athena Benchmark & Tables DDL** | [Tiến Sơn Benchmark CSV](tuan_3/results/integration_2026_10_18/benchmark/default/benchmark.csv) · [Ngọc Quyên Benchmark CSV](tuan_3/results/integration_2026_10_18/benchmark/quyen/benchmark.csv) |
| **Biểu đồ so sánh quét byte & thời gian Athena**| [Byte Scanned Chart](tuan_3/results/integration_2026_10_18/benchmark_scan.png) · [Engine Time Chart](tuan_3/results/integration_2026_10_18/benchmark_engine.png) |
| **CloudWatch Dashboard JSON & Ảnh widget thật**| [Dashboard Default](tuan_3/results/integration_2026_10_18/dashboard/default/) · [Dashboard Quyên](tuan_3/results/integration_2026_10_18/dashboard/quyen/) |
| **Metric Filters & Kiểm chứng vận hành log** | [Operations Report](tuan_3/results/operations_2026_10_18/README.md) · [Post Repair 13:51 Observation](tuan_3/results/post_repair_2026_10_18/README.md) |
| **Hồ sơ dự báo 24h & Sai số Holdout đầy đủ** | [Forecast Metrics CSV](tuan_3/results/integration_2026_10_18/forecast/forecast_metrics.csv) · [Holdout Predictions CSV](tuan_3/results/integration_2026_10_18/forecast/holdout_predictions.csv) |
| **Biểu đồ chuỗi thời gian AQI & PM2.5 dự báo** | [Holdout AQI Evaluation](tuan_3/results/integration_2026_10_18/forecast/holdout_us_aqi.png) · [Holdout PM2.5 Evaluation](tuan_3/results/integration_2026_10_18/forecast/holdout_pm2_5.png) |
| **Hồ sơ tự động CI/CD GitHub Actions** | [Workflow verify-repository.yml](.github/workflows/verify-repository.yml) · [Release CD Reports](tuan_3/results/cd_2026_10_18/) |
| **Báo cáo kỹ thuật chi tiết Tuần 3** | [tuan_3/docs/FINAL_REPORT.md](tuan_3/docs/FINAL_REPORT.md) · [Hướng dẫn vận hành](tuan_3/docs/operation.md) |
| **Danh mục mã băm SHA-256 (Audit Catalog)** | [docs/csv_catalog.csv](docs/csv_catalog.csv) · [Chương trình audit](tuan_2/scripts/repository_audit.py) |

---

## Cách đọc kết quả

1. **Tính độc lập và tính nhất quán giữa 2 tài khoản:** Số lượng bản ghi raw của sinh viên Tiến Sơn (237) và sinh viên Ngọc Quyên (273) phản ánh các phiên chạy thu thập thực tế tại các thời điểm khác nhau trên 2 tài khoản AWS Learner Lab độc lập. Nhóm giữ nguyên vẹn dữ liệu gốc của từng tài khoản, không gộp mẫu làm sai lệch bản chất đo lường.
2. **Bản chất dữ liệu Open-Meteo:** Dữ liệu thời tiết và chất lượng không khí lấy qua Open-Meteo API tích hợp nguồn dữ liệu mô hình toàn cầu CAMS (Copernicus Atmosphere Monitoring Service), được sử dụng cho mục đích phân tích học thuật và đối sánh giải pháp đám mây, không thay thế cho các trạm quan trắc chuẩn quốc gia cố định.
3. **Ý nghĩa của Athena Benchmark:** Thử nghiệm Parquet và Partition Projection chứng minh rõ rệt việc tiết kiệm I/O mạng và thời gian lập kế hoạch truy vấn metadata. Tuy nhiên, trên quy mô dữ liệu nhỏ vài chục KB, thời gian khởi động Presto execution engine (thường từ 400–600 ms) chiếm tỷ trọng lớn trong tổng thời gian truy vấn.

---

## Kiểm tra và tái lập kết quả (Reproducibility)

Để kiểm chứng toàn bộ hệ thống kiểm thử tự động đạt kết quả **100% PASS** từ thư mục gốc repository:

```powershell
# 1. Kiểm tra tính toàn vẹn danh mục CSV, Worklog và liên kết Markdown
python tuan_2/scripts/repository_audit.py --check

# 2. Kiểm chứng các chỉ số Benchmark, Dự báo và Bằng chứng mốc Tuần 3
python tuan_3/scripts/verify_results.py

# 3. Chạy toàn bộ Unit Tests Tuần 3 (34 tests)
python -m unittest discover -s tuan_3/tests -v

# 4. Chạy toàn bộ Unit Tests Tuần 2 (68 tests)
python -m unittest discover -s tuan_2/tests -v

# 5. Chạy toàn bộ Unit Tests Analytics Tuần 2 (18 tests)
python -m unittest discover -s tuan_2/analytics -p "test_*.py" -v

# 6. Chạy kiểm thử chấp nhận E2E Acceptance (22 tests)
python -m unittest tests/test_e2e_acceptance.py -v
```

---

## Kết luận

Qua 3 tuần làm việc nghiêm túc với tổng cộng **58.0 giờ công**, nhóm sinh viên Nguyễn Tiến Sơn và Trần Thị Ngọc Quyên đã xây dựng hoàn chỉnh một giải pháp Data Pipeline thu thập và phân tích dữ liệu khí tượng - môi trường mẫu mực trên nền tảng AWS:
- Xây dựng thành công Data Lake tự động hóa hoàn toàn với **EventBridge, Lambda và S3**.
- Triển khai giải pháp phân tích dữ liệu lớn hiện đại kết hợp **Glue, Athena Partition Projection và Parquet Snappy**, giảm byte quét đến **96.5%**.
- Thiết lập hệ thống giám sát vận hành thời gian thực chuyên nghiệp với **CloudWatch Metric Filters, Custom Metrics và CloudWatch Dashboard**.
- Xây dựng và đánh giá hồi cứu chuỗi thời gian AQI 24 giờ với các phương pháp cơ sở khoa học, kiểm soát chặt chẽ rủi ro rò rỉ dữ liệu.
- Hoàn thiện tài liệu hóa chuẩn mực, minh chứng minh bạch, sẵn sàng báo cáo và nghiệm thu đề tài trước Giảng viên hướng dẫn ThS. Huỳnh Xuân Phụng.
