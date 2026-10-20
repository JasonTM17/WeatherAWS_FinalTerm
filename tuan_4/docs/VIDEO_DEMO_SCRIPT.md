# Kịch bản lời thoại và thao tác video demo bảo vệ đồ án (Thời lượng chuẩn: 09:45)

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS
**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng
**Sinh viên trình bày (Song thoại - Dual-Speaker):**
- **Nguyễn Tiến Sơn** — MSSV: 24110054 (Speaker 1)
- **Trần Thị Ngọc Quyên** — MSSV: 24110051 (Speaker 2)

**Mục tiêu thời lượng:** **Đúng 9 phút 45 giây (09:45)**. Có phân vai song thoại rõ ràng, hướng dẫn thao tác chi tiết từng giây trên trình duyệt/AWS Console, và lời thoại đọc từng từ (word-for-word).

---

## Chuẩn bị trước khi quay (Checklist tiền kỳ)

1. **Khởi động phiên Lab:** Start Lab trên AWS Academy, đợi trạng thái chuyển sang màu xanh (Active), chọn đúng vùng **US East (N. Virginia) `us-east-1`**.
2. **Sắp xếp thứ tự các Tab trình duyệt (từ trái sang phải):**
   - Tab 1: [GitHub Repository](https://github.com/JasonTM17/WeatherAWS_FinalTerm) (mở sẵn trang chủ `README.md` và sơ đồ kiến trúc).
   - Tab 2: [Amazon EventBridge Rules](https://us-east-1.console.aws.amazon.com/events/home?region=us-east-1#/rules) (chọn bus `default`, mở sẵn rule `WeatherCollectionSchedule`).
   - Tab 3: [AWS Lambda Functions](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions/WeatherCollectorLambda) (hàm `WeatherCollectorLambda`, tạo sẵn Test Event `demo-week4` với JSON `{}`).
   - Tab 4: [CloudWatch Logs](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups) (log group `/aws/lambda/WeatherCollectorLambda`).
   - Tab 5: [Amazon S3 Console](https://s3.console.aws.amazon.com/s3/buckets?region=us-east-1) (bucket `weather-aqi-...`, mở sẵn thư mục `raw/`).
   - Tab 6: [Amazon Athena Query Editor](https://us-east-1.console.aws.amazon.com/athena/home?region=us-east-1#/query-editor) (database `weather_aqi_db`, dán sẵn khung SQL).
   - Tab 7: [Amazon SNS Topics](https://us-east-1.console.aws.amazon.com/sns/v3/home?region=us-east-1#/topics) & Hộp thư sinh viên (mở sẵn cửa sổ email).
   - Tab 8: [CloudWatch Dashboard](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:) (Dashboard `WeatherAirQuality-Week3`).
   - Tab 9: [AWS Cost Explorer](https://console.aws.amazon.com/costmanagement/home#/cost-explorer) & Báo cáo FinOps Tuần 4.
   - Tab 10: [CloudFormation Template](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/infrastructure/weather-stack.json) & Báo cáo an ninh `SECURITY_AUDIT.md`.
3. **Phần mềm quay màn hình:** Dùng Windows Snipping Tool (`Windows + Shift + R`), chọn quay màn hình có thu âm micro của cả hai sinh viên.

---

## Kịch bản chi tiết từng phân đoạn (Timeline 00:00 – 09:45)

### Phân đoạn 1: Giới thiệu đề tài, thành viên & Kiến trúc tổng quan (00:00 – 00:45 | 45 giây)

**Thao tác thực hiện (Bấm):**
- Mở Tab 1 (GitHub Repository), cuộn chuột chậm rãi qua tiêu đề đề tài, thông tin hai sinh viên, và dừng lại ở hình ảnh sơ đồ kiến trúc hệ thống (`architecture.png`).

**Lời thoại:**

> **[Nguyễn Tiến Sơn (00:00 – 00:22)]:**
> "Kính chào Thầy và các bạn. Em là Nguyễn Tiến Sơn, mã số sinh viên 24110054, đại diện nhóm cùng bạn Trần Thị Ngọc Quyên, mã số sinh viên 24110051. Hôm nay nhóm em xin trình bày video báo cáo bảo vệ đồ án kết thúc học phần Điện toán đám mây với đề tài: 'Xây dựng hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên nền tảng AWS'."

> **[Trần Thị Ngọc Quyên (00:22 – 00:45)]:**
> "Hệ thống của nhóm em được thiết kế hoàn toàn theo mô hình Serverless trên AWS, bao gồm EventBridge kích hoạt lịch, Lambda xử lý dữ liệu, Secrets Manager bảo mật cấu hình, S3 lưu trữ hồ sơ, Glue và Athena phục vụ phân tích dữ liệu lớn, SNS gửi cảnh báo qua email, và CloudWatch giám sát toàn diện. Trong video này, hai chúng em sẽ chứng minh toàn bộ luồng vận hành thực tế từ thu thập đến phân tích và bảo mật."

---

### Phân đoạn 2: Quản lý lịch kích hoạt EventBridge & Bảo toàn Credits (00:45 – 01:30 | 45 giây)

**Thao tác thực hiện (Bấm):**
- Chuyển sang Tab 2 (Amazon EventBridge Console).
- Mở chi tiết rule `WeatherCollectionSchedule`.
- Rê chuột vào phần **Event schedule** hiển thị `rate(1 hour)`, trạng thái **Enabled**, và tab **Targets** trỏ chính xác đến hàm `WeatherCollectorLambda`.

**Lời thoại:**

> **[Nguyễn Tiến Sơn (00:45 – 01:30)]:**
> "Bước đầu tiên là cơ chế kích hoạt tự động. Trên màn hình là EventBridge Rule mang tên `WeatherCollectionSchedule`. Lịch được thiết lập với chu kỳ đều đặn một giờ một lần (`rate(1 hour)`), trạng thái hiện tại là Enabled.
>
> Tại tab Targets, rule trỏ trực tiếp đến Lambda Function `WeatherCollectorLambda`. Để kiểm soát chặt chẽ ngân sách tín dụng 100 USD của AWS Learner Lab và tránh gửi cảnh báo trùng lặp, mỗi tài khoản thực hành chỉ duy trì duy nhất một lịch hoạt động. Khi kết thúc phiên làm việc, nhóm luôn chủ động tạm dừng rule này bằng kịch bản tự động hóa mà nhóm em sẽ demo ở cuối video."

---

### Phân đoạn 3: Thực thi Lambda Collector thời gian thực & Cấu hình Secrets Manager (01:30 – 02:45 | 75 giây)

**Thao tác thực hiện (Bấm):**
- Chuyển sang Tab 3 (AWS Lambda Console -> `WeatherCollectorLambda`).
- Mở tab **Configuration** -> **Environment variables** (chỉ rõ bucket name và secret name).
- Chuyển sang tab **Code** -> chọn tab con **Test**.
- Chọn Test Event có tên `demo-week4` (JSON `{}`).
- Bấm nút **Test** một lần duy nhất.
- Chờ 1-2 giây cho Lambda thực thi xong, bung mở mục **Execution result -> Details**.

**Lời thoại:**

> **[Nguyễn Tiến Sơn (01:30 – 02:45)]:**
> "Bây giờ em chuyển sang dịch vụ AWS Lambda với hàm xử lý chính `WeatherCollectorLambda`. Trong phần cấu hình, toàn bộ tọa độ ba thành phố gồm Thành phố Hồ Chí Minh, Hà Nội, Đà Nẵng cùng các ngưỡng cảnh báo an toàn được tách rời và bảo vệ an toàn trong AWS Secrets Manager.
>
> Em tiến hành chạy thử nghiệm một lượt thu thập thời gian thực bằng event rỗng `{}`. Em bấm Test một lần.
>
> *(Khi kết quả Execution result hiện màu xanh)*
> Kết quả thực thi trả về mã thành công: `collection_status: complete`, thời gian thực thi chỉ hơn 800 mili-giây, bộ nhớ sử dụng tối ưu. Hàm đã thu thập trọn vẹn 3 bản ghi cho cả ba thành phố mà không có bất kỳ đô thị nào bị lỗi (`failed_cities: []`).
>
> Mục `saved_files` hiển thị đường dẫn tệp JSON vừa được đẩy lên Amazon S3, và mục `alerts_sent: 1` ghi nhận đã có một cảnh báo vượt ngưỡng được phát hiện và gửi đi thành công. Tiếp theo, bạn Quyên sẽ đối chiếu dữ liệu này trên CloudWatch Logs và S3."

---

### Phân đoạn 4: Kiểm tra CloudWatch Logs vòng đời & Tải đối chiếu S3 NDJSON raw (02:45 – 03:50 | 65 giây)

**Thao tác thực hiện (Bấm):**
- Chuyển sang Tab 4 (CloudWatch Logs -> log group `/aws/lambda/WeatherCollectorLambda`).
- Bấm vào Log stream mới nhất vừa sinh ra từ lượt chạy Test ở bước 3.
- Chỉ vào chuỗi sự kiện `START`, dòng log `[INFO] Result: ...`, và sự kiện `REPORT` (chỉ ra RequestId, Duration, Memory Used).
- Chuyển sang Tab 5 (Amazon S3 Console), mở đúng đường dẫn `raw/year=2026/month=10/day=19/...`.
- Tải tệp `.json` về máy, mở nhanh trên màn hình để thấy 3 dòng NDJSON.

**Lời thoại:**

> **[Trần Thị Ngọc Quyên (02:45 – 03:50)]:**
> "Em xin tiếp tục phần trình bày với việc kiểm tra tính toàn vẹn trên CloudWatch Logs. Tại log stream mới nhất, Thầy có thể thấy đầy đủ vòng đời thực thi gồm dòng `START`, các dòng nhật ký gọi API Open-Meteo, dòng log có cấu trúc `[INFO] Result:` ghi nhận chính xác 3 bản ghi, và dòng `REPORT` chốt thời gian thực thi cùng lượng RAM tiêu thụ.
>
> Từ đường dẫn S3 được ghi trong log, em chuyển sang Amazon S3 Console. Dữ liệu được tổ chức theo cấu trúc phân vùng chuẩn hóa `raw/year=YYYY/month=MM/day=DD/`.
>
> Tải tệp dữ liệu về và mở ra, đây là định dạng NDJSON với đúng 3 dòng tương ứng với TP. Hồ Chí Minh, Hà Nội và Đà Nẵng. Mỗi bản ghi chứa trọn vẹn 23 trường thông tin: từ mã định danh duy nhất `record_id`, tọa độ địa lý, nhiệt độ, độ ẩm, cho đến chỉ số bụi mịn PM2.5 và chất lượng không khí US AQI. Dữ liệu thực sự đã nằm trên S3 và sẵn sàng cho tầng truy vấn."

---

### Phân đoạn 5: Truy vấn Serverless Athena theo record_id chính xác & Partition Projection (03:50 – 05:00 | 70 giây)

**Thao tác thực hiện (Bấm):**
- Chuyển sang Tab 6 (Amazon Athena Query Editor).
- Chọn Database `weather_aqi_db`.
- Dán 3 mã `record_id` vừa lấy từ tệp NDJSON ở bước 4 vào câu lệnh SQL chuẩn bị sẵn:
  ```sql
  SELECT record_id, city, timestamp_vn, us_aqi, pm2_5, temperature_c
  FROM weather_aqi_db.weather_airquality_records
  WHERE year = '2026' AND month = '10' AND day = '19'
    AND record_id IN ('HoChiMinh_...', 'HaNoi_...', 'DaNang_...')
  ORDER BY city;
  ```
- Bấm nút **Run**.
- Khi trạng thái chuyển sang **Succeeded**, chỉ vào kết quả 3 dòng và số liệu thống kê: **Data scanned: ~19 KB**, **Engine time: ~600 ms**.

**Lời thoại:**

> **[Trần Thị Ngọc Quyên (03:50 – 05:00)]:**
> "Tiếp theo là tầng phân tích dữ liệu lớn không dùng máy chủ bằng Amazon Athena thông qua AWS Glue Data Catalog. Em sử dụng câu truy vấn SQL lọc chính xác theo ngày phân vùng và ba mã `record_id` vừa thu thập được từ S3. Em bấm Run.
>
> Truy vấn đã hoàn tất chỉ trong 600 mili-giây và lượng dữ liệu quét cực kỳ khiêm tốn: chỉ xấp xỉ 19 Kilobytes.
>
> Kết quả trả về đúng ba dòng dữ liệu của ba thành phố, giá trị AQI và PM2.5 khớp 100% với dữ liệu thô trên S3. Sở dĩ truy vấn quét ít dữ liệu và đạt tốc độ cao như vậy là nhờ cơ chế **Partition Projection** mà nhóm em đã cấu hình từ Tuần 3, giúp Athena tính toán trực tiếp vị trí dữ liệu trên S3 mà không tốn chi phí quét metadata của Glue. Tiếp theo, bạn Sơn sẽ trình bày về luồng cảnh báo thời gian thực."

---

### Phân đoạn 6: Kiểm chứng luồng cảnh báo thời gian thực Amazon SNS & Xác nhận email (05:00 – 05:55 | 55 giây)

**Thao tác thực hiện (Bấm):**
- Chuyển sang Tab 7 (Amazon SNS Console -> Topics -> `weather-airquality-alerts`).
- Cho thấy topic đang hoạt động và danh sách **Subscriptions** có địa chỉ email ở trạng thái **Confirmed**.
- Chuyển sang cửa sổ Hộp thư Email sinh viên, bấm vào email cảnh báo mới nhất vừa nhận được từ AWS Notifications mang tiêu đề `[AWS ALERT] Canh bao chat luong khong khi - HaNoi`.
- Cuộn xem nội dung: đô thị Hà Nội, giá trị AQI = 101, PM2.5, thời gian phát hiện.

**Lời thoại:**

> **[Nguyễn Tiến Sơn (05:00 – 05:55)]:**
> "Về cơ chế cảnh báo tự động, hệ thống sử dụng Amazon SNS Topic mang tên `weather-airquality-alerts`. Đăng ký nhận thông báo qua email của hai thành viên nhóm đều đã ở trạng thái Confirmed.
>
> Ngưỡng cảnh báo trong hệ thống được định nghĩa chặt chẽ theo điều kiện logic OR: `AQI >= 100 HOẶC PM2.5 >= 35.5 µg/m³`.
>
> Trong lượt chạy vừa rồi, trạm đo Hà Nội ghi nhận chỉ số US AQI là 101, vượt ngưỡng an toàn 100, do đó Lambda đã kích hoạt lệnh gửi cảnh báo tới SNS.
>
> Ngay lập tức trên màn hình hộp thư của em, email cảnh báo từ AWS đã được chuyển phát thành công với tiêu đề cảnh báo chất lượng không khí Hà Nội, hiển thị đầy đủ thời gian, giá trị AQI 101 và các khuyến cáo phòng hộ sức khỏe. Điều này khẳng định nhánh cảnh báo thời gian thực hoạt động chính xác từ logic xử lý đến người nhận cuối."

---

### Phân đoạn 7: Giám sát CloudWatch Dashboard & Metric Filters (05:55 – 06:45 | 50 giây)

**Thao tác thực hiện (Bấm):**
- Chuyển sang Tab 8 (CloudWatch Dashboard `WeatherAirQuality-Week3`).
- Bấm **Refresh**, chọn cửa sổ quan sát thời gian gần nhất (1 giờ hoặc 3 giờ).
- Rê chuột qua các widget đồ thị:
  - Widget Lambda Invocations & Errors (cho thấy 1 Invocation, 0 Error, tỷ lệ lỗi 0%).
  - Widget Duration (thời gian chạy trung bình ~800ms).
  - Widget SNS Notifications (cho thấy thông điệp đã phát).

**Lời thoại:**

> **[Nguyễn Tiến Sơn (05:55 – 06:45)]:**
> "Để vận hành và theo dõi toàn diện hệ thống, nhóm em đã thiết lập CloudWatch Dashboard tập trung mang tên `WeatherAirQuality-Week3`.
>
> Tại biểu đồ Lambda Invocations và Errors, hệ thống ghi nhận đúng một lượt gọi tương ứng với test vừa chạy và số lỗi là 0, tỷ lệ lỗi đạt 0% trong chu kỳ kiểm chứng. Biểu đồ Duration thể hiện thời gian xử lý ổn định dưới 1 giây. Biểu đồ SNS hiển thị thông điệp gửi đi thành công.
>
> Bên cạnh các chỉ số gốc, nhóm còn thiết lập hai **Metric Filters** trên log group để theo dõi số lượng dòng `Result` và dòng `Error` theo thời gian thực, tạo cơ sở cho việc đối chiếu ba chiều giữa nhật ký, chỉ số và dữ liệu lưu trữ."

---

### Phân đoạn 8: Quản trị tài chính đám mây FinOps & Chi phí Cost Explorer (06:45 – 07:45 | 60 giây)

**Thao tác thực hiện (Bấm):**
- Chuyển sang Tab 9 (Báo cáo FinOps và AWS Cost Explorer).
- Mở bảng chi phí tổng hợp `learner_lab_cost_breakdown.csv` và `cost_summary.json`.
- Chỉ vào số liệu chi phí thực tế của 2 tài khoản: Tiến Sơn (70 nhóm, 0.00 USD), Ngọc Quyên (47 nhóm, 0.14 USD).
- Rê chuột qua danh sách dịch vụ: Secrets Manager, CloudWatch, S3, Lambda, Athena, SNS.

**Lời thoại:**

> **[Trần Thị Ngọc Quyên (06:45 – 07:45)]:**
> "Một đóng góp nâng cao quan trọng trong Tuần 4 là công tác quản trị tài chính đám mây **FinOps** trên AWS Learner Lab. Nhóm em đã trích xuất dữ liệu chi phí chính thức từ AWS Cost Explorer API trong kỳ đối soát từ ngày 12 đến ngày 19 tháng 10.
>
> Kết quả kiểm toán cho thấy: tài khoản của bạn Tiến Sơn ghi nhận 70 nhóm chi phí với tổng làm tròn là **0,00 USD** nhờ chính sách bù trừ tín dụng Credit của AWS; tài khoản của em ghi nhận 47 nhóm chi phí với tổng chỉ **0,14 USD** phát sinh từ các đợt benchmark phân tích dữ liệu lớn.
>
> Các dịch vụ Serverless như Lambda, Athena, SNS và S3 đều nằm trọn vẹn trong Free Tier hoặc tiêu tốn phần nghìn cent. Điều này chứng minh kiến trúc Serverless của đồ án đạt hiệu quả kinh tế tối ưu và bảo toàn an toàn ngân sách 100 USD của học phần."

---

### Phân đoạn 9: Đóng gói hạ tầng CloudFormation 17 tài nguyên & An ninh bảo mật (07:45 – 08:50 | 65 giây)

**Thao tác thực hiện (Bấm):**
- Chuyển sang Tab 10.
- Cuộn mở tệp `tuan_4/infrastructure/weather-stack.json`, làm nổi bật cấu trúc 17 tài nguyên AWS được đóng gói bằng IaC.
- Mở tiếp tệp `tuan_4/docs/SECURITY_AUDIT.md`, chỉ vào bảng **11 tiêu chuẩn an ninh bảo mật** (S3 Block Public Access đạt 4/4 cờ, mã hóa AES256, HTTPS enforcement, Least Privilege).

**Lời thoại:**

> **[Nguyễn Tiến Sơn (07:45 – 08:20)]:**
> "Về khía cạnh tự động hóa hạ tầng dưới dạng mã (IaC), nhóm em đã đóng gói toàn bộ 17 tài nguyên của hệ thống vào một template AWS CloudFormation duy nhất mang tên `weather-stack.json`.
>
> Template này đã vượt qua 100% các bài kiểm tra cú pháp với `cfn-lint` và API xác thực `ValidateTemplate` trên cả hai tài khoản AWS thật. Template tự động thiết lập toàn bộ từ S3, Secrets Manager, Lambda, EventBridge, SNS, Glue, Athena cho đến CloudWatch Alarms và Dashboard."

> **[Trần Thị Ngọc Quyên (08:20 – 08:50)]:**
> "Đồng thời, nhóm em đã thực hiện một cuộc rà soát an ninh bảo mật toàn diện theo **11 tiêu chuẩn khắt khe**.
>
> Cả hai môi trường S3 đều đã kích hoạt 100% bốn lớp **S3 Block Public Access**, bật mã hóa tĩnh **AES256**, chính sách bucket bắt buộc truyền thông an toàn qua **HTTPS**, và quyền thực thi được thiết kế theo nguyên tắc đặc quyền tối thiểu (Least Privilege). Mọi dữ liệu nhạy cảm, token xác thực đều được vệ sinh sạch sẽ khỏi nhật ký và kho mã nguồn."

---

### Phân đoạn 10: Tự động hóa dọn dẹp tài nguyên cuối phiên, CI/CD & Kết luận (08:50 – 09:45 | 55 giây)

**Thao tác thực hiện (Bấm):**
- Mở cửa sổ Terminal PowerShell trên máy, chạy lệnh kiểm tra kịch bản dọn dẹp:
  ```powershell
  python tuan_4/scripts/session_control.py pause --help
  ```
- Mở nhanh trang **GitHub Actions** cho thấy workflow `verify-repository.yml` đang có dấu tích xanh (All checks passed).
- Quay lại trang chủ GitHub Repository để chào kết thúc.

**Lời thoại:**

> **[Nguyễn Tiến Sơn (08:50 – 09:20)]:**
> "Để đảm bảo an toàn sau mỗi buổi thực hành trong phòng Lab, nhóm em đã xây dựng kịch bản PowerShell `cleanup_resources.ps1` và `start_resources.ps1`. Trước khi kết thúc phiên, lệnh `session_control.py pause` sẽ lưu trạng thái an toàn vào file khôi phục và tạm dừng EventBridge Rule, ngăn ngừa mọi chi phí phát sinh ngầm khi sinh viên rời máy.
>
> Trên GitHub Actions, quy trình CI/CD tự động kiểm thử 100% mã nguồn với hơn 160 unit test, bảo đảm chất lượng phần mềm không bao giờ bị suy thoái."

> **[Trần Thị Ngọc Quyên (09:20 – 09:45)]:**
> "Tổng kết lại qua bốn tuần thực hiện với tổng thời gian 78 giờ công đã được xác nhận, nhóm chúng em đã xây dựng thành công một giải pháp Điện toán đám mây hoàn chỉnh, ổn định, tiết kiệm chi phí và đạt chuẩn an ninh trên AWS.
>
> Hai chúng em xin chân thành cảm ơn Thầy Huỳnh Xuân Phụng đã luôn tận tình hướng dẫn và đóng góp những ý kiến quý báu giúp chúng em hoàn thiện đồ án này. Nhóm em xin trân trọng cảm ơn Thầy đã theo dõi video!"

---

## Bảng tổng kết thời gian và phân công lời thoại (Timing Verification)

| Phân đoạn | Nội dung trình bày | Người nói chính | Thời lượng (giây) | Mốc thời gian |
| :---: | :--- | :---: | :---: | :---: |
| **01** | Giới thiệu đề tài & Kiến trúc tổng quan | Sơn & Quyên | 45s | 00:00 – 00:45 |
| **02** | Quản lý lịch EventBridge & Tiết kiệm Credits | Tiến Sơn | 45s | 00:45 – 01:30 |
| **03** | Thực thi Lambda Collector & Secrets Manager | Tiến Sơn | 75s | 01:30 – 02:45 |
| **04** | Đối chiếu CloudWatch Logs & Tải tệp S3 NDJSON | Ngọc Quyên | 65s | 02:45 – 03:50 |
| **05** | Truy vấn Serverless Athena & Partition Projection | Ngọc Quyên | 70s | 03:50 – 05:00 |
| **06** | Kiểm chứng cảnh báo Amazon SNS & Email | Tiến Sơn | 55s | 05:00 – 05:55 |
| **07** | Giám sát CloudWatch Dashboard & Metric Filters | Tiến Sơn | 50s | 05:55 – 06:45 |
| **08** | Quản trị tài chính đám mây FinOps & Cost Explorer | Ngọc Quyên | 60s | 06:45 – 07:45 |
| **09** | CloudFormation IaC 17 tài nguyên & An ninh bảo mật | Sơn & Quyên | 65s | 07:45 – 08:50 |
| **10** | Quản lý tài nguyên cuối phiên, CI/CD & Kết luận | Sơn & Quyên | 55s | 08:50 – 09:45 |
| **TỔNG** | **Toàn bộ video demo bảo vệ đồ án** | **Cả hai SV** | **585 giây** | **Đúng 09:45** |

---

## Hướng dẫn xử lý tình huống phát sinh trong lúc quay (Contingency Notes)

1. **Trường hợp Lambda trả về `alerts_sent = 0` (Thời tiết thực tế không vượt ngưỡng):**
   - Đọc số liệu thực tế trên kết quả Lambda: *"Trong lượt test này, chỉ số AQI và PM2.5 của cả ba thành phố đều nằm trong vùng an toàn dưới ngưỡng, do đó hàm không phát sinh cảnh báo là hoàn toàn chính xác theo logic OR. Để minh chứng email cảnh báo đã hoạt động, em xin mở email của đợt kiểm chứng ngày 19/10 đã được lưu trữ trong hồ sơ xác nhận."*
2. **Trường hợp email thông báo SNS đến trễ vài giây do độ trễ mạng:**
   - Bình tĩnh nói: *"SNS đã chấp nhận thông điệp phát đi từ Lambda. Trong lúc đợi hộp thư mạng cập nhật, em xin mở email kiểm chứng của đợt đo trước để Thầy quan sát cấu trúc thông điệp chuẩn."*
3. **Trường hợp Athena Query mất hơn 1 giây:**
   - Không bấm Run liên tục nhiều lần. Giữ nguyên màn hình cho đến khi query chuyển sang Succeeded.
4. **Không để lộ thông tin bảo mật:**
   - Tuyệt đối không bấm nút mở giá trị Plaintext Secret trong Secrets Manager.
   - Không mở tab AWS Details chứa Session Token / Access Keys.
