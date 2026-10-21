# BÁO CÁO TỔNG KẾT TUẦN 4

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS.

**Lĩnh vực:** Domain Apps.

**Sinh viên thực hiện:** Nguyễn Tiến Sơn — MSSV 24110054; Trần Thị Ngọc Quyên — MSSV 24110051.

**Học phần:** Điện toán đám mây.

**Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng.

**Ngày cập nhật hồ sơ:** 21/10/2026.

Kính gửi thầy,

Chúng em gửi thầy báo cáo tổng kết Tuần 4 và hồ sơ bàn giao đồ án. Trong tuần cuối, chúng em tập trung kiểm tra hệ thống từ bước thu thập dữ liệu đến lưu trữ, truy vấn, giám sát và gửi cảnh báo. Các nội dung hạ tầng tự động, bảo mật, chi phí và quản lý tài nguyên được hoàn thiện theo góp ý của thầy.

Báo cáo sử dụng kết quả kiểm chứng ngày 19–20/10/2026. Mỗi phần có liên kết đến dữ liệu, mã nguồn hoặc kết quả thực thi để đối chiếu. Video demo được đính kèm cùng hồ sơ.

**Repository:**

[https://github.com/JasonTM17/WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm)

**Video demo — tệp `24110054_24110051.mp4`:**

[https://drive.google.com/drive/folders/1G50ZYK7QFGoftLx3hYglw4SRTwr3TvAR?usp=sharing](https://drive.google.com/drive/folders/1G50ZYK7QFGoftLx3hYglw4SRTwr3TvAR?usp=sharing)

## 1. Triển khai hạ tầng và kiểm tra mã nguồn

Hệ thống thu thập dữ liệu thời tiết và chất lượng không khí cho **TP. Hồ Chí Minh, Hà Nội và Đà Nẵng**. EventBridge gọi Lambda theo lịch; Lambda lấy dữ liệu từ API, chuẩn hóa và lưu bản ghi trên S3. Athena sử dụng Glue Data Catalog để truy vấn dữ liệu. SNS tiếp nhận cảnh báo khi dữ liệu vượt ngưỡng; CloudWatch lưu nhật ký và các chỉ số vận hành.

Chúng em đóng gói hạ tầng ứng dụng bằng **một template CloudFormation gồm 17 tài nguyên**, dùng chung cho hai môi trường. Ngày 20/10/2026, hai stack **`weather-w4-son`** và **`weather-w4-quyen`** đều đạt trạng thái **CREATE_COMPLETE**. Sau khi tạo stack, chúng em kiểm tra lại cấu hình, đối chiếu mã Lambda với collector trong repository bằng SHA-256 và kiểm tra artifact theo Version ID đã sử dụng.

Hai lịch của stack mới được giữ **DISABLED** để tránh thu thập song song với lịch chuẩn của hệ thống hiện hữu. Việc kiểm chứng ứng dụng trên hạ tầng mới được thực hiện bằng các lượt gọi Lambda có kiểm soát.

Minh chứng triển khai được dẫn trực tiếp đến CloudFormation Events, cấu hình và kết quả thực thi của từng stack, tại phiên bản đã lưu trong Git.

- **Báo cáo chi tiết Tuần 4:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md)
- **Template CloudFormation:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/infrastructure/weather-stack.json](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/infrastructure/weather-stack.json)
- **Tài liệu hạ tầng và hướng dẫn triển khai:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/INFRASTRUCTURE.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/INFRASTRUCTURE.md)
- **Hồ sơ kiểm chứng hai stack:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/stacks](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/stacks)
- **Môi trường của sinh viên Tiến Sơn:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/58fdf22da9b048e457aa88e823606cf424ec5caf/tuan_4/results/advanced_live_2026_10_20/stacks/default](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/58fdf22da9b048e457aa88e823606cf424ec5caf/tuan_4/results/advanced_live_2026_10_20/stacks/default)
- **Môi trường của sinh viên Ngọc Quyên:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/58fdf22da9b048e457aa88e823606cf424ec5caf/tuan_4/results/advanced_live_2026_10_20/stacks/quyen](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/58fdf22da9b048e457aa88e823606cf424ec5caf/tuan_4/results/advanced_live_2026_10_20/stacks/quyen)

## 2. Thu thập dữ liệu và đối chiếu kết quả vận hành

Trong đợt kiểm chứng ngày 20/10, mỗi Lambda mới được gọi một lần bằng sự kiện `{}` và thu đủ **ba bản ghi cho ba đô thị**. Chúng em tải object vừa ghi trên S3, xuất CSV đủ **23 trường** và chạy SELECT theo đúng `record_id` trong database/workgroup của từng stack. Bốn trường đối chiếu trực tiếp là `record_id`, `city`, `us_aqi` và `pm2_5`; kết quả truy vấn khớp dữ liệu raw. Chế độ sử dụng lại kết quả Athena được tắt trong các truy vấn kiểm chứng.

Nhật ký **START, END, REPORT và Result** được ghép theo cùng request để nối lượt thực thi với object S3 và kết quả Athena. Trong chu kỳ metric chứa lượt kiểm chứng, mỗi function ghi nhận **một Invocation và 0 Errors**.

Bộ dữ liệu tích lũy ngày 20/10 gồm **700 bản ghi trong 115 tệp JSON gốc**: sinh viên Tiến Sơn có **331 bản ghi/53 tệp**; sinh viên Ngọc Quyên có **369 bản ghi/62 tệp**. Số dòng, dung lượng và SHA-256 của từng object được lưu trong danh mục kiểm kê. Đây là số liệu tích lũy của các lượt thu thập; dữ liệu tổng hợp theo đô thị–giờ được xuất riêng để phân tích.

- **Kết quả kiểm chứng ngày 20/10:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/advanced_live_2026_10_20/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/advanced_live_2026_10_20/README.md)
- **JSON gốc, CSV và danh mục object:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/snapshot](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/snapshot)
- **Đối chiếu log–metric–S3–Athena:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md)

## 3. Kiểm chứng cảnh báo và email người nhận

Hệ thống gửi cảnh báo khi **US AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³**. Trong đợt kiểm chứng ngày 19/10 trên hệ thống hiện hữu, dữ liệu Hà Nội ghi nhận **AQI 101**. Mỗi môi trường có một thông báo được SNS chấp nhận; cả hai người nhận đã xác nhận nhận được email cảnh báo mới.

Lượt thu thập ngày 20/10 trên stack mới có dữ liệu dưới ngưỡng nên kết quả **0 cảnh báo** phù hợp với cấu hình. Chúng em kiểm tra riêng kênh email bằng cách xác nhận subscription của hai topic mới và gửi một thư thử trên mỗi topic. Cả hai thông báo được SNS chấp nhận và cả hai sinh viên xác nhận đã nhận đúng thư.

Hồ sơ lưu riêng cảnh báo từ dữ liệu vượt ngưỡng và thư thử kênh SNS, kèm xác nhận người nhận cho từng đợt kiểm tra.

- **Xác nhận email cảnh báo ngày 19/10:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/verification_2026_10_19/recipient_confirmation.json](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/verification_2026_10_19/recipient_confirmation.json)
- **Kiểm chứng email của hai topic mới:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/email](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/email)

## 4. Thực nghiệm Athena và đánh giá dự báo

### 4.1. So sánh tổ chức dữ liệu trên Athena

Chúng em thực hiện **18 truy vấn**, gồm ba phương án: JSON đăng ký phân vùng, JSON Partition Projection và Parquet Partition Projection. Mỗi phương án được đo ba lần trên mỗi môi trường, tương ứng **3 phương án × 3 lần đo × 2 môi trường**. Các phép đo sử dụng cùng dữ liệu và phép tổng hợp, luân phiên thứ tự chạy và tắt chế độ sử dụng lại kết quả.

Với ngày lọc 20/10 có ba bản ghi, lượng dữ liệu quét trung vị giảm từ **1.558 byte của JSON Projection xuống 302 byte của Parquet Projection**. Tỷ lệ giảm được tính bằng **(1.558 − 302) / 1.558 × 100 ≈ 80,62%**. Các phương án trả kết quả tổng hợp tương đương.

JSON Projection có tổng thời gian trung vị thấp hơn Parquet trong bộ đo này. Vì vậy, báo cáo đánh giá riêng lượng dữ liệu quét và độ trễ; tỷ lệ giảm byte được sử dụng để mô tả bộ thực nghiệm, không quy đổi trực tiếp thành tỷ lệ giảm hóa đơn.

**SQL, kết quả và thống kê của 18 truy vấn:**

[https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/benchmark](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/benchmark)

### 4.2. Đánh giá dự báo trên ba cửa sổ lịch sử

Chúng em sử dụng phương pháp **MA24 đệ quy** để backtest ba cửa sổ lịch sử. Mỗi cửa sổ nhận 24 giờ dữ liệu trước mốc dự báo và dự đoán 24 giờ tiếp theo cho ba đô thị, với hai biến US AQI và PM2.5. Dữ liệu đích của chính cửa sổ đang đánh giá không được đưa vào quá trình dự đoán.

Đầu ra gồm **432 giá trị dự đoán**, tương ứng **3 cửa sổ × 3 đô thị × 2 biến × 24 giờ**, và **18 nhóm chỉ số MAE/RMSE/Bias**. MAE phản ánh độ lệch tuyệt đối trung bình; RMSE nhạy hơn với sai số lớn; Bias cho biết xu hướng dự đoán cao hoặc thấp hơn giá trị đối chiếu.

Đây là đánh giá hồi cứu trên chuỗi dữ liệu mô hình Open-Meteo/CAMS. Dữ liệu đầu vào, dự đoán, sai số và biểu đồ được lưu cùng phương pháp; kỳ dự báo đã phát hành trong Tuần 3 được giữ riêng theo mốc.

- **Phương pháp, dữ liệu và biểu đồ backtest:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/README.md)
- **432 giá trị dự đoán:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/predictions.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/predictions.csv)
- **Kết quả MAE, RMSE và Bias:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/metrics.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/metrics.csv)

## 5. Bảo mật, chi phí và quản lý tài nguyên

### 5.1. Cấu hình bảo mật

Chúng em kiểm tra lại hai bucket của stack mới: cả bốn thiết lập **S3 Block Public Access** đều bật; mã hóa mặc định sử dụng **AES256**; versioning ở trạng thái **Enabled**; Object Ownership là **BucketOwnerEnforced**. Các bucket có policy từ chối kết nối không sử dụng HTTPS và không có public ACL/policy.

Quyền gọi Lambda được ràng buộc với ARN của EventBridge rule và SourceAccount. Hệ thống sử dụng LabRole được cấp trong học phần; policy runtime giới hạn theo tài nguyên được cung cấp làm tài liệu tham khảo cho thiết kế quyền collector.

**Báo cáo rà soát bảo mật:**

[https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md)

### 5.2. Tổng hợp chi phí

Theo số liệu nhóm xác nhận, tổng chi phí thực hiện đồ án là **0,47 USD**, gồm **0,25 USD của sinh viên Tiến Sơn** và **0,22 USD của sinh viên Ngọc Quyên**. Chúng em kết hợp theo dõi chi phí với kiểm soát lịch thu thập, lưu kết quả phân tích để sử dụng lại và kiểm kê tài nguyên cuối phiên. Báo cáo chi phí và dữ liệu đối chiếu được đính kèm trong hồ sơ bàn giao.

- **Báo cáo chi phí:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md)
- **Bản tổng hợp chi phí:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/cost/confirmed_cost_summary.json](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/cost/confirmed_cost_summary.json)
- **Dữ liệu Cost Explorer theo kỳ — JSON tổng hợp:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/cost/cost_summary.json](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/cost/cost_summary.json)
- **Dữ liệu Cost Explorer theo kỳ — CSV chi tiết:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/cost/learner_lab_cost_breakdown.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/cost/learner_lab_cost_breakdown.csv)

### 5.3. Tạm dừng và khôi phục lịch thu thập

Ngày 20/10, chúng em kiểm chứng thao tác tạm dừng và khôi phục lịch chuẩn trên cả hai môi trường theo trình tự **ENABLED → DISABLED → ENABLED**. Trạng thái ban đầu được ghi trước khi thay đổi; sau khi khôi phục, thông tin môi trường và target được đối chiếu, giữ nguyên cấu hình đích và dữ liệu đã lưu.

Hai lịch của stack mới tiếp tục giữ DISABLED để tránh thu thập trùng. Checklist cuối phiên hướng dẫn lưu minh chứng, kiểm tra lịch hoạt động và kiểm kê tài nguyên còn lưu giữ trước khi kết thúc sử dụng.

- **Kết quả tạm dừng và khôi phục:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/session](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/session)
- **Checklist quản lý tài nguyên cuối phiên:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SESSION_CHECKLIST.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SESSION_CHECKLIST.md)

## 6. Phân công và hồ sơ bàn giao

Sinh viên **Nguyễn Tiến Sơn** phụ trách hạ tầng, Lambda, S3, Secrets Manager, SNS, EventBridge và CloudWatch. Sinh viên **Trần Thị Ngọc Quyên** phụ trách Glue/Athena, dữ liệu, phân tích, dự báo và chi phí. Hai sinh viên phối hợp tích hợp hệ thống, đối chiếu kết quả và hoàn thiện báo cáo.

**Tổng theo tuần đã xác nhận:** Tuần 4 là **10 giờ mỗi sinh viên, tổng 20 giờ**; tổng thời gian thực hiện toàn đồ án qua bốn tuần là **78 giờ**.

Hồ sơ bàn giao gồm mã nguồn, template hạ tầng, dữ liệu raw, kết quả truy vấn, biểu đồ, báo cáo, worklog và video demo. Các kiểm thử kiểm tra nhận diện môi trường, gói triển khai, khôi phục lịch và tách dữ liệu đầu vào/đích của dự báo. Bộ xác minh ngoại tuyến đối chiếu manifest, JSON–CSV–SELECT và tính lại dự đoán cùng các chỉ số sai số. GitHub Actions kiểm tra repository theo từng commit.

- **Worklog Tuần 4:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/WORKLOG.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/WORKLOG.md)
- **CSV giờ công toàn đồ án:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv)
- **Báo cáo tổng kết toàn đồ án:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md)
- **Toàn bộ hồ sơ Tuần 4:**

  [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4)
- **Video demo — tệp `24110054_24110051.mp4`:**

  [https://drive.google.com/drive/folders/1G50ZYK7QFGoftLx3hYglw4SRTwr3TvAR?usp=sharing](https://drive.google.com/drive/folders/1G50ZYK7QFGoftLx3hYglw4SRTwr3TvAR?usp=sharing)

## 7. Mã nguồn, commit và hồ sơ đối chiếu

**`feat(week4): verify live stacks and three historical backtest windows` — `58fdf22`:** kiểm chứng hai stack và đánh giá dự báo trên ba cửa sổ lịch sử.

[https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/58fdf22da9b048e457aa88e823606cf424ec5caf](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/58fdf22da9b048e457aa88e823606cf424ec5caf)

**`feat(week4): complete final week verification, consolidate CloudFormation infrastructure, and update catalog` — `96bedec`:** hoàn thiện bộ kiểm chứng, hợp nhất hạ tầng CloudFormation và cập nhật danh mục dữ liệu.

[https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093)

**`fix(week4): verify deployment records and replace inaccessible evidence links` — `1248abe`:** kiểm tra công khai các bản ghi GitHub, bổ sung kiểm thử và thay liên kết minh chứng bằng hồ sơ AWS cố định theo commit.

[https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/1248abe70a07671b2b5fb33e2172a763c1afc27b](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/1248abe70a07671b2b5fb33e2172a763c1afc27b)

**`docs(week4): record verified AWS stacks in GitHub Deployments` — `616f15c`:** bổ sung tài liệu và bản tổng hợp trong repository. Phạm vi commit là tài liệu; kết quả đối chiếu API được lưu riêng trong hồ sơ dưới đây.

[https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/616f15c71c1c6ec9c0f8bf098ecdc2e15d371486](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/616f15c71c1c6ec9c0f8bf098ecdc2e15d371486)

**Hồ sơ đối chiếu bản ghi GitHub ngày 21/10:**

[https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/github_deployment_readback_2026_10_21/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/github_deployment_readback_2026_10_21/README.md)

**Mã nguồn Lambda collector:**

[https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py)

**Workflow kiểm tra repository:**

[https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml)

## 8. Kết luận

Tuần 4 hoàn tất phần kiểm chứng và bàn giao đồ án. Hệ thống đã có kết quả đối chiếu từ mã nguồn và hạ tầng đến lượt thực thi, dữ liệu S3, truy vấn Athena, giám sát và email người nhận. Phần thực nghiệm bổ sung so sánh tổ chức dữ liệu, đánh giá dự báo theo thời gian, rà soát bảo mật và quản lý tài nguyên.

Chúng em kính gửi thầy báo cáo cùng mã nguồn, dữ liệu và video demo tại các liên kết trên. Chúng em cảm ơn thầy đã góp ý và hướng dẫn trong quá trình thực hiện đồ án.
