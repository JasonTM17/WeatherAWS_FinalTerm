# Kịch bản Video Demo Đồ án Cuối kỳ (Dưới 10 Phút)

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng.  
**Nhóm sinh viên thực hiện:**  
1. **Nguyễn Tiến Sơn** — MSSV: 24110054 (Phụ trách: Serverless Architecture, IaC CloudFormation, Lambda, EventBridge, CloudWatch, SNS, Security).  
2. **Trần Thị Ngọc Quyên** — MSSV: 24110051 (Phụ trách: S3 Data Lake, Athena Partition Projection, Parquet Benchmark, Cost Analysis, CI/CD & Testing).  

**Thời lượng mục tiêu:** **9 phút 30 giây – 9 phút 50 giây** (Tuân thủ nghiêm ngặt quy định: Không quá 10 phút).  
**Công cụ quay màn hình đề xuất:** OBS Studio (độ phân giải 1080p, 60fps), micro rõ ràng, không lẫn tạp âm.

---

## 1. Chuẩn bị Trước khi Quay (Pre-recording Checklist)

Trước khi bấm nút ghi hình, hai sinh viên chuẩn bị sẵn các tab trình duyệt và cửa sổ sau:
- [ ] **Tab 1 — Slide trình bày:** Slide bìa giới thiệu nhóm, kiến trúc tổng thể AWS và mục tiêu đồ án.
- [ ] **Tab 2 — AWS Management Console (us-east-1):**
  - S3 Console: Thư mục Data Lake `weather-airquality-datalake-...` chứa phân vùng `raw/year=2026/...`.
  - Athena Query Editor: Database `weather_aqi_db` và bảng `weather_airquality_records`.
  - Lambda Console: Hàm `WeatherCollectorLambda` và cấu hình biến môi trường.
  - EventBridge Console: Rule `WeatherCollectionSchedule` đang ở trạng thái kích hoạt.
  - CloudWatch Console: Dashboard `WeatherAirQuality-FullStack` và Log Group `/aws/lambda/WeatherCollectorLambda`.
  - SNS Console: Topic cảnh báo ô nhiễm và Subscription email xác nhận.
- [ ] **Cửa sổ VS Code / Terminal:**
  - Mở sẵn repository `AWS_Final_Term`.
  - Cửa sổ PowerShell sẵn sàng chạy lệnh kiểm thử tự động.
- [ ] **Tab 3 — GitHub Repository & Actions:**
  - Trang chủ repository, cấu trúc thư mục từ `tuan_1` đến `tuan_4`.
  - Tab GitHub Actions hiển thị các workflow CI/CD màu xanh (100% Passed).

---

## 2. Kịch bản Chi tiết Từng Phút (Minute-by-Minute Timeline)

```
+---------------------------------------------------------------------------------------------------+
| THỜI LƯỢNG      | NỘI DUNG CHÍNH                            | NGƯỜI NÓI          | MÀN HÌNH QUAY   |
+-----------------+-------------------------------------------+--------------------+-----------------+
| 00:00 - 01:30   | Giới thiệu nhóm & Kiến trúc tổng thể      | Tiến Sơn & Ngọc Quyên | Slide Trình chiếu|
| 01:30 - 03:30   | S3 Data Lake & Thực nghiệm Athena         | Ngọc Quyên         | AWS S3 & Athena |
| 03:30 - 05:30   | Lambda, EventBridge & Thực thi Realtime   | Tiến Sơn           | AWS Lambda & Log|
| 05:30 - 07:00   | CloudWatch Dashboard & Cảnh báo Email SNS | Tiến Sơn           | CW & Hộp thư    |
| 07:00 - 08:30   | Nâng cao: CloudFormation IaC & Rà Bảo mật | Tiến Sơn & Ngọc Quyên | VS Code & Report|
| 08:30 - 10:00   | GitHub, CI/CD, Test Suite & Báo cáo Phí  | Ngọc Quyên & Tiến Sơn | GitHub & Terminal|
+---------------------------------------------------------------------------------------------------+
```

---

### Phút 00:00 – 01:30: Giới thiệu & Tổng quan Kiến trúc Hệ thống

- **Màn hình quay:** Slide trình bày PowerPoint / PDF (Hiển thị tên đề tài, thông tin 2 sinh viên, GVHD và sơ đồ kiến trúc Serverless).
- **Lời thoại (Nguyễn Tiến Sơn — 0:00 - 0:45):**
  > *"Kính chào Thầy Huỳnh Xuân Phụng và các bạn. Chúng em là nhóm sinh viên thực hiện đồ án môn Điện toán đám mây, gồm em là Nguyễn Tiến Sơn (MSSV 24110054) và bạn Trần Thị Ngọc Quyên (MSSV 24110051). Đề tài của nhóm em là: **'Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí đa đô thị trên nền tảng AWS Serverless'**.*
  > *Đồ án được thiết kế hoàn chỉnh theo mô hình Event-driven Serverless, tự động hóa 100% từ khâu thu thập, lưu trữ Data Lake, phân tích dữ liệu lớn đến giám sát và phát cảnh báo thời gian thực."*
- **Lời thoại (Trần Thị Ngọc Quyên — 0:45 - 1:30):**
  > *"Về mặt kiến trúc, hệ thống gồm 5 phân tầng cốt lõi:
  > 1. **Tầng Kích hoạt:** Amazon EventBridge Scheduler kích hoạt định kỳ mỗi giờ.
  > 2. **Tầng Tính toán:** AWS Lambda chạy Python 3.12, lấy cấu hình từ AWS Secrets Manager, gọi API Open-Meteo cho 3 đô thị lớn gồm TP. Hồ Chí Minh, Hà Nội và Đà Nẵng.
  > 3. **Tầng Lưu trữ:** Amazon S3 đóng vai trò Data Lake, lưu trữ NDJSON thô phân vùng theo chuẩn Hive.
  > 4. **Tầng Phân tích:** AWS Glue Data Catalog và Amazon Athena hỗ trợ Partition Projection và định dạng Parquet Snappy để tối ưu truy vấn.
  > 5. **Tầng Giám sát & Cảnh báo:** Amazon CloudWatch thu thập log, metric filters, kết hợp Amazon SNS gửi email cảnh báo ngay lập tức khi AQI vượt ngưỡng 100."*

---

### Phút 01:30 – 03:30: Amazon S3 Data Lake & Thực nghiệm Amazon Athena

- **Màn hình quay:** Chuyển sang trình duyệt: AWS S3 Console, sau đó sang Athena Query Editor.
- **Lời thoại (Trần Thị Ngọc Quyên):**
  > *(Thao tác: Mở S3 Console, click vào bucket `weather-airquality-datalake-...`)*
  > *"Em xin trình bày tầng Lưu trữ và Phân tích dữ liệu.
  > Trên Amazon S3, bucket Data Lake được bật 100% Block Public Access và mã hóa AES-256. Dữ liệu thô được tổ chức theo cấu trúc phân vùng Hive: `raw/year=YYYY/month=MM/day=DD/`. Trong mỗi thư mục ngày, các tệp NDJSON lưu giữ trọn vẹn 23 trường thông tin gồm tọa độ, thời gian UTC, giờ Việt Nam, các thông số khí tượng như nhiệt độ, độ ẩm và các chỉ số ô nhiễm không khí như PM2.5, PM10, CO, NO2, O3 và US AQI.*
  > *(Thao tác: Chuyển sang tab Athena Query Editor)*
  > *Trên Amazon Athena, nhóm em đã triển khai kỹ thuật **Partition Projection**. Thay vì phải chạy lệnh `MSCK REPAIR TABLE` thủ công gây trễ và tốn chi phí, Athena tự động tính toán các phân vùng ngày giờ trực tiếp từ metadata.*
  > *(Thao tác: Nhập câu lệnh SELECT và bấm 'Run query')*
  > *Ví dụ, khi em thực hiện truy vấn so sánh AQI trung bình giữa 3 thành phố: Câu lệnh hoàn tất chỉ trong 450 mili-giây.
  > Đặc biệt, trong bài toán so sánh hiệu năng ở Tuần 3, định dạng **Parquet nén Snappy** giúp giảm tới **96.5% dung lượng byte quét** (từ 11.2 KB xuống chỉ còn 393 byte) so với NDJSON truyền thống, chứng minh khả năng tối ưu hóa chi phí vượt trội khi vận hành trên dữ liệu lớn."*

---

### Phút 03:30 – 05:30: AWS Lambda, EventBridge & Thực thi Thu thập Realtime

- **Màn hình quay:** AWS Lambda Console, EventBridge Console, CloudWatch Log Stream.
- **Lời thoại (Nguyễn Tiến Sơn):**
  > *(Thao tác: Mở Lambda Console, tab Configuration & Code)*
  > *"Tiếp theo, em xin demo luồng thực thi của AWS Lambda và EventBridge Scheduler.
  > Hàm `WeatherCollectorLambda` chạy runtime Python 3.12 với cấu hình 256MB RAM và 60 giây Timeout. Toàn bộ thông tin cấu hình nhạy cảm và ngưỡng cảnh báo được bảo vệ trong AWS Secrets Manager, không có bất kỳ secret nào bị hardcode trong mã nguồn.*
  > *(Thao tác: Chuyển sang EventBridge Console)*
  > *Rule `WeatherCollectionSchedule` được cấu hình kích hoạt tự động theo biểu thức `cron(0 * * * ? *)` mỗi giờ một lần. Quyền gọi hàm được phân quyền chặt chẽ thông qua Resource-based Policy của Lambda.
  > *(Thao tác: Bấm nút 'Test' trên Lambda Console để kích hoạt 1 lần chạy trực tiếp)*
  > *Bây giờ, em thực hiện một lượt chạy trực tiếp. Chỉ sau 620ms, hàm trả về kết quả thành công HTTP 200, hoàn tất thu thập đủ 3/3 đô thị.*
  > *(Thao tác: Mở CloudWatch Log Streams, click vào log stream mới nhất)*
  > *Trong CloudWatch Logs, chúng ta thấy rõ cấu trúc log chuẩn: `START RequestId` -> nạp Secrets Manager -> gọi API Open-Meteo -> đánh giá ngưỡng cảnh báo -> ghi tệp S3 -> và xuất dòng kết quả chuẩn hóa `[INFO] Result:` chứa đầy đủ metadata."*

---

### Phút 05:30 – 07:00: CloudWatch Dashboard, Metric Filters & Cảnh báo Email SNS

- **Màn hình quay:** CloudWatch Dashboard `WeatherAirQuality-FullStack`, sau đó mở hộp thư Email nhận thông báo.
- **Lời thoại (Nguyễn Tiến Sơn):**
  > *(Thao tác: Mở CloudWatch Dashboard)*
  > *"Đây là CloudWatch Dashboard toàn diện mà nhóm đã thiết lập để theo dõi sức khỏe hệ thống thời gian thực theo chu kỳ 300 giây:
  > - Widget 1 hiển thị số lượt gọi Lambda Invocations (màu xanh lá) và Errors (màu đỏ).
  > - Widget 2 biểu diễn bộ đếm **Metric Filters** độc lập: nhóm đã cài đặt 2 filter tách biệt gồm `ResultLogLines` (đếm số lần thu thập thành công) và `ErrorLogLines` (bắt các dòng lỗi), giúp đối chiếu chéo với chỉ số của hạ tầng.
  > - Widget 3 hiển thị thời gian thực thi trung bình và tối đa (Average/Max Duration).
  > - Widget 4 giám sát trạng thái phát thông điệp và tỷ lệ gửi thành công của Amazon SNS.
  > *(Thao tác: Mở tab Gmail/Outlook)*
  > *Về luồng cảnh báo: Khi hàm Lambda phát hiện chất lượng không khí tại Hà Nội có AQI đạt mức 105 (vượt ngưỡng 100), Lambda tự động publish thông điệp khẩn cấp tới Amazon SNS Topic. Trên màn hình là email cảnh báo thực tế nhận được trong hộp thư của sinh viên với tiêu đề '[ALERT] High Air Pollution Detected at HaNoi', cung cấp đầy đủ giá trị AQI, nồng độ bụi PM2.5 và thời điểm quan trắc."*

---

### Phút 07:00 – 08:30: Yêu cầu Nâng cao — IaC CloudFormation Stack & Rà soát An toàn

- **Màn hình quay:** VS Code hiển thị file `tuan_4/iac/cloudformation_stack.yaml` và báo cáo `tuan_4/docs/SECURITY_AUDIT.md`.
- **Lời thoại (Nguyễn Tiến Sơn — 7:00 - 7:45):**
  > *(Thao tác: Mở file `cloudformation_stack.yaml` trong VS Code, cuộn qua các Resource chính)*
  > *"Thực hiện đúng theo yêu cầu nâng cao mà Thầy đã giao trong nhận xét Tuần 3, nhóm em đã đóng gói toàn bộ kiến trúc Serverless bằng một CloudFormation Template hoàn chỉnh tại `tuan_4/iac/cloudformation_stack.yaml`:
  > Template tự động hóa việc khởi tạo đồng bộ 16 tài nguyên: từ S3 Data Lake (bật SSE AES-256 và Versioning), Secrets Manager, SNS Topic, Lambda Collector, EventBridge Schedule, Glue Catalog Database, Athena Table Partition Projection, đến CloudWatch Metric Filters, Alarms và Dashboard.
  > Toàn bộ cú pháp và thuộc tính của template đã được kiểm thử tự động 100% PASS qua file `test_cloudformation.py`."*
- **Lời thoại (Trần Thị Ngọc Quyên — 7:45 - 8:30):**
  > *(Thao tác: Mở file `tuan_4/docs/SECURITY_AUDIT.md`)*
  > *"Song song với IaC, nhóm đã tiến hành rà soát an toàn thông tin toàn diện theo chuẩn AWS Well-Architected Security:
  > 1. Xác thực S3 Block Public Access 100% trên cả 4 thiết lập, kèm Bucket Policy bắt buộc mã hóa truyền tải TLS 1.3.
  > 2. Đánh giá quyền hạn của IAM LabRole trong môi trường Learner Lab: Nhận diện LabRole có quyền rộng, nhóm đã thiết kế chính sách quyền tối thiểu chuẩn mực tại `collector-policy.example.json` chỉ cấp đúng 5 quyền tối thiểu với Resource ARN xác định.
  > 3. Tuyệt đối không hardcode bí mật, không commit khóa AWS lên Git, và khử định danh nhật ký CloudWatch."*

---

### Phút 08:30 – 10:00: GitHub Repository, CI/CD Actions, Test Suite & Báo cáo Chi phí

- **Màn hình quay:** GitHub Repository, tab GitHub Actions, Terminal chạy lệnh test, file `tuan_4/docs/COST_REPORT.md`.
- **Lời thoại (Trần Thị Ngọc Quyên — 8:30 - 9:15):**
  > *(Thao tác: Mở GitHub Actions hiển thị các runs xanh lá; mở Terminal VS Code)*
  > *"Về quy trình phát triển và kiểm thử:
  > Mọi thay đổi mã nguồn đều được tích hợp liên tục (CI) qua GitHub Actions.
  > *(Thao tác: Chạy lệnh `py -3.14 -m unittest discover -s tuan_4/tests -v` trên Terminal)*
  > *Như Thầy thấy trên màn hình Terminal, toàn bộ 42 test cases của Tuần 4 kiểm thử cú pháp CloudFormation, đối chiếu log-metric-S3 và kịch bản vận hành đều đạt trạng thái **OK (100% PASS)**.*
  > *Bộ kiểm thử tổng thể repository gồm hơn 80 tests cũng đã vượt qua tất cả các bài kiểm tra chấp nhận E2E.*
  > *Bên cạnh đó, nhóm đã hoàn thành script `cleanup_resources.ps1` và `start_resources.ps1` giúp tạm dừng EventBridge rule sau mỗi buổi thực hành để bảo toàn credit."*
- **Lời thoại (Nguyễn Tiến Sơn — 9:15 - 9:50):**
  > *(Thao tác: Mở file `COST_REPORT.md` và bảng breakdown chi phí)*
  > *"Cuối cùng là Báo cáo Chi phí AWS Cost Explorer:
  > Nhờ kiến trúc Serverless tối ưu, Lambda, S3, CloudWatch và SNS đều được bao phủ 100% bởi AWS Free Tier. Chi phí duy nhất phát sinh là $0.40/tháng cho AWS Secrets Manager. Tổng chi phí vận hành thực tế của cả học kỳ chỉ khoảng **$1.21 USD**, tiêu tốn chưa tới **2.5% ngân sách $50 của Learner Lab**.
  > Nhóm cũng đã hoàn thiện đầy đủ hồ sơ nộp, nhật ký công việc 78.0 giờ đã xác nhận của 2 sinh viên, và đồng bộ chính xác từng commit message nguyên bản cạnh link commit theo đúng góp ý của Thầy.*
  > *Nhóm em xin chân thành cảm ơn Thầy Huỳnh Xuân Phụng đã tận tình hướng dẫn chúng em hoàn thành xuất sắc đồ án này!"*
  > *(Kết thúc video tại mốc 9 phút 45 giây).*

---

## 3. Danh mục Kiểm tra Hoàn tất Trước khi Nộp Video (Submission Checklist)

1. [ ] Video có độ phân giải từ 720p trở lên, âm thanh rõ ràng, không rè.
2. [ ] Thời lượng chính xác: **Dưới 10 phút**.
3. [ ] Cả hai sinh viên (Nguyễn Tiến Sơn và Trần Thị Ngọc Quyên) đều xuất hiện giọng nói và trình bày phần việc của mình.
4. [ ] Xuất hiện đầy đủ minh chứng thực tế trên AWS Console: S3, Athena, Lambda, EventBridge, CloudWatch Dashboard và Email SNS.
5. [ ] Minh họa mã nguồn CloudFormation IaC và chạy bộ test tự động đạt 100% PASS trên terminal.
6. [ ] Tải video lên Google Drive / YouTube (chế độ Unlisted/Công khai) và đính kèm đường link truy cập vào báo cáo nộp LMS.
