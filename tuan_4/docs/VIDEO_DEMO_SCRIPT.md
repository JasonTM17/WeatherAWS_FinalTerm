# Lời thoại demo WeatherAWS — khoảng 9 phút

Chỉ đọc phần **Lời thoại**. Phần **Bấm** là hướng dẫn thao tác, không đọc thành tiếng. Các mốc dưới đây gồm cả thời gian chuyển tab và chờ kết quả; diễn tập trước một lượt.

## Trước khi quay

- Start Lab, đợi phiên hoạt động, chọn vùng N. Virginia/us-east-1.
- Mở sẵn GitHub, EventBridge, Lambda, CloudWatch Logs, S3, Athena, SNS, hộp thư và Dashboard. Chi phí/template mở sẵn ở tab riêng.
- Chuẩn bị test event Private tên `demo-week4`, nội dung `{}`; không dùng backfill cho phần demo cảnh báo.
- Mở cửa sổ trình duyệt riêng, không để credentials hoặc Secret value trong vùng ghi hình.
- Windows 11: Windows + Shift + R → kéo vùng quay → kiểm tra micro → Start. Quay thử 10 giây và nghe lại trước bản chính.

## 1. Giới thiệu — 00:00–00:40

**Bấm:** mở repository `https://github.com/JasonTM17/WeatherAWS_FinalTerm`, dừng ở tên đề tài và sơ đồ kiến trúc.

**Lời thoại:**

> Kính chào thầy. Em là Nguyễn Tiến Sơn, mã số sinh viên 24110054, thực hiện đề tài cùng sinh viên Trần Thị Ngọc Quyên, mã số sinh viên 24110051.
>
> Đề tài của chúng em là hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS cho Thành phố Hồ Chí Minh, Hà Nội và Đà Nẵng. Trong video này, em trình bày một lượt thu thập thực tế, kiểm tra dữ liệu lưu trữ, truy vấn, cảnh báo và cách quản lý hệ thống.

## 2. Lịch EventBridge — 00:40–01:15

**Bấm:** EventBridge → Rules → bus `default` → `WeatherCollectionSchedule` → xem trạng thái, Schedule và Targets.

**Lời thoại:**

> Đầu tiên là lịch thu thập trên EventBridge. Rule này có chu kỳ một giờ và gọi hàm WeatherCollectorLambda.
>
> Em kiểm tra lịch đang bật và target trỏ đúng hàm thu thập. Mỗi môi trường sử dụng một lịch đang hoạt động cho collector, giúp kiểm soát số lượt chạy và tránh gửi cảnh báo hai lần do hai lịch cùng gọi một hàm.

**Đối chiếu trước khi đọc:** chỉ nói lịch đang bật nếu state là Enabled và chu kỳ đúng `rate(1 hour)`.

## 3. Chạy Lambda — 01:15–02:20

**Bấm:** Lambda → `WeatherCollectorLambda` → Test → chọn `demo-week4`, JSON `{}` → Test một lần. Khi xong mở Execution result → Details.

Nếu đang ở trình soạn thảo Code của Lambda, có thể bấm **Create new test event** trong TEST EVENTS ở cạnh trái, đặt tên `demo-week4`, nhập `{}`, chọn Private và lưu; nút **Test** nằm dưới **Deploy**. CloudWatch Logs là trang xem nhật ký, không có tab Test của Lambda. Nếu chỉ kiểm tra mã đang triển khai, không cần bấm Deploy.

**Lời thoại lúc bấm Test:**

> Tiếp theo, em chạy một lượt kiểm tra trực tiếp bằng event rỗng. Đây là nhánh thu thập dữ liệu hiện tại.
>
> Hàm đọc vị trí và ngưỡng từ Secrets Manager, gọi API Open-Meteo cho ba đô thị, sau đó lưu kết quả lên S3. Điều kiện cảnh báo là AQI từ 100 hoặc PM2.5 từ 35,5 microgam trên mét khối.

**Khi thấy complete, 3 bản ghi và failed_cities rỗng, đọc tiếp:**

> Kết quả trả về cho thấy lượt thu thập hoàn tất, có ba bản ghi và không có đô thị thất bại. Phần saved_files cho biết object S3 vừa được tạo; phần alerts_sent thể hiện số lần gửi cảnh báo được hàm ghi nhận thành công.

**Không bấm Test liên tiếp khi đang chờ. Nếu kết quả khác, mô tả kết quả thật và kiểm tra log.**

## 4. Từ log đến S3 — 02:20–03:30

**Bấm:** Lambda → Monitor → View CloudWatch logs → stream của lượt vừa chạy → tìm `[INFO] Result:`. Chỉ ra START, END, REPORT và key S3 trong Result. Chuyển tab S3, mở đúng bucket/key → Download và mở JSON.

**Lời thoại:**

> Để kiểm tra lượt chạy, em mở CloudWatch Logs. Các dòng START, END và REPORT ghi nhận vòng đời thực thi; dòng Result ghi trạng thái thu thập, số bản ghi và đường dẫn dữ liệu.
>
> Từ đường dẫn này, em mở đúng object trên S3. Dữ liệu được lưu theo ngày UTC và mỗi dòng là một bản ghi JSON.
>
> Em kiểm tra số dòng, tên ba đô thị, mã bản ghi và các trường AQI, PM2.5, nhiệt độ. Như vậy, kết quả Lambda được đối chiếu với dữ liệu thực sự lưu trên S3.

**Giữ lại ba record_id trong JSON để dùng bước tiếp theo.**

## 5. Athena — 03:30–04:45

**Bấm:** Athena → Query editor → data source `AwsDataCatalog` → database `weather_aqi_db`. Dán câu SQL bên dưới, thay ngày theo partition S3 và thay ba ID bằng record_id trong JSON vừa mở → Run.

```sql
SELECT record_id, city, timestamp_vn, us_aqi, pm2_5
FROM weather_aqi_db.weather_airquality_records
WHERE year = '2026' AND month = '10' AND day = '19'
  AND record_id IN (
    'DAN_RECORD_ID_TP_HCM',
    'DAN_RECORD_ID_HA_NOI',
    'DAN_RECORD_ID_DA_NANG'
  )
ORDER BY city;
```

**Ba chuỗi DAN_RECORD_ID... là chỗ cần thay, không phải dữ liệu để chạy nguyên văn.** Chuẩn bị sẵn khung SQL trước buổi quay để chỉ phải dán ba ID.

**Lời thoại lúc chạy:**

> Tiếp theo, em dùng Athena để truy vấn dữ liệu trên S3 thông qua lược đồ trong Glue Data Catalog. Câu truy vấn lọc theo ngày và ba mã bản ghi của lượt vừa chạy, vì vậy kết quả có thể đối chiếu trực tiếp với JSON nguồn.

**Khi query Succeeded và trả đúng ba bản ghi, đọc:**

> Truy vấn đã thành công và trả về đúng ba bản ghi của ba đô thị. Em đối chiếu mã bản ghi cùng giá trị AQI và PM2.5 với dữ liệu raw. Phần thống kê của Athena cho biết thời gian thực thi và lượng dữ liệu đã quét.

## 6. SNS và email — 04:45–05:30

**Bấm:** SNS → Topics → `weather-airquality-alerts` → Subscriptions. Sau đó mở hộp thư và tìm `[AWS ALERT]`.

**Lời thoại chung:**

> Nhánh cảnh báo sử dụng Amazon SNS. Em kiểm tra đăng ký email đã được xác nhận. Khi dữ liệu thỏa điều kiện ngưỡng, Lambda Publish thông báo lên topic này để gửi đến người nhận.

**Nếu lượt vừa chạy có cảnh báo và thư mới đã đến, đọc:**

> Đây là email của lượt kiểm tra vừa thực hiện. Em đối chiếu đô thị, chỉ số và ngưỡng cảnh báo với dữ liệu đã thu thập. Bước này kiểm tra thêm việc thư tới hộp thư người nhận, bên cạnh kết quả Publish của Lambda.

**Nếu alerts_sent bằng 0:** đối chiếu raw và log trước khi kết luận nguyên nhân. Khi không có đô thị nào đạt ngưỡng, thay đoạn trên bằng:

> Lượt hiện tại không phát cảnh báo. Để minh họa nội dung thư, em mở email của đợt kiểm chứng đã lưu trước đó; ngày kiểm chứng được thể hiện trong hồ sơ.

Nếu raw có đô thị đạt ngưỡng nhưng số chấp nhận gửi vẫn bằng 0, kiểm tra cấu hình topic và log Publish; không nói dữ liệu chưa vượt ngưỡng. Một dòng succeeded xác nhận lượt gọi kết thúc thành công, còn trạng thái thu thập và gửi cảnh báo được đọc riêng.

**Nếu có Publish nhưng thư đang chờ:** nói “SNS đã tiếp nhận thông báo; em tiếp tục kiểm tra hộp thư để xác nhận bước giao email.” Không gọi thư cũ là thư mới.

## 7. CloudWatch Dashboard — 05:30–06:15

**Bấm:** CloudWatch → Dashboards → `WeatherAirQuality-Week3` → chọn cửa sổ có lượt chạy, ví dụ 3h → Refresh. Chỉ vào Invocations, Errors, Duration và SNS.

**Lời thoại:**

> Dashboard tổng hợp số lượt gọi, số lỗi, thời gian thực thi và các chỉ số SNS. Khi đối chiếu, em sử dụng cùng hàm, cùng khoảng quan sát và chu kỳ 300 giây.
>
> Log giúp xác định request và đường dẫn S3; metric giúp theo dõi hoạt động theo từng chu kỳ. Tỷ lệ lỗi chỉ được tính khi có đủ cặp Errors và Invocations hợp lệ. Email nhận được được xác nhận riêng với các bộ đếm trên Dashboard.

**Nếu metric chưa cập nhật:** mở bảng kiểm chứng đã lưu và nêu đúng ngày, không gọi đó là metric tức thời của lượt mới.

## 8. Chi phí — 06:15–06:50

**Bấm:** Cost Explorer → Cost and usage → chọn kỳ của báo cáo, Daily, nhóm Service. Nếu không mở được Console, dùng CSV Cost Explorer đã xuất đúng kỳ.

**Lời thoại:**

> Phần chi phí được tổng hợp từ Cost Explorer theo ngày và dịch vụ, đơn vị là đô la Mỹ. Báo cáo giữ thông tin Estimated để phân biệt số liệu đang được AWS tổng hợp.
>
> Em tách số liệu chi phí do AWS trả về với mức dự kiến của bài thực hành. Kỳ và phạm vi thống kê được ghi rõ để người đọc có thể đối chiếu lại dữ liệu nguồn.

## 9. Bảo mật và CloudFormation — 06:50–08:05

**Bấm:** S3 → bucket → Permissions → Block public access → xem bốn mục bật. Chuyển Properties → Default encryption. Sau đó mở template chính của dự án tại `tuan_4/infrastructure/weather-stack.json`.

**Lời thoại:**

> Về lưu trữ, bucket đã bật các thiết lập Block Public Access và mã hóa mặc định. Em kiểm tra cấu hình này để bảo vệ dữ liệu và kiểm soát quyền truy cập.
>
> Về tự động hóa hạ tầng, chúng em chuẩn bị template CloudFormation mô tả các thành phần của ứng dụng, gồm lưu trữ, cấu hình, Lambda, lịch thu thập, cảnh báo, catalog, truy vấn và giám sát.
>
> Cấu hình stack mới khởi tạo với lịch tắt để kiểm thử trước khi bật tự động. Dữ liệu phục vụ báo cáo được giữ lại theo chính sách lưu giữ.
>
> Trong Learner Lab, hệ thống dùng LabRole do môi trường học phần cấp. Mẫu quyền runtime trong repository giới hạn theo bucket, Secret, topic và log group của ứng dụng, phục vụ đối chiếu khi sử dụng execution role riêng.

**Nếu chỉ đang mở template:** nói “template đã chuẩn bị/kiểm tra”, không nói đã triển khai stack. Chỉ mở Resources/Outputs và nói đã tạo stack khi có CREATE_COMPLETE thật.

## 10. CI, kết thúc phiên và kết luận — 08:05–09:00

**Bấm:** GitHub → Actions → mở lần kiểm tra thành công của đúng phiên bản đang trình bày → xem commit với message gốc. Mở checklist cuối phiên.

**Lời thoại:**

> Mã nguồn và các kiểm tra của dự án được quản lý trên GitHub. Mỗi phiên bản có commit cụ thể; nội dung báo cáo dẫn tới source và minh chứng tương ứng.
>
> Sau buổi thực hành, chúng em chờ các lượt đang chạy kết thúc, xuất dữ liệu và kết quả kiểm chứng, rồi tạm dừng lịch thu thập trước khi kết thúc Learner Lab. Việc thu hồi tài nguyên thử nghiệm được thực hiện sau khi đã xác định phạm vi và lưu sản phẩm cần giữ.
>
> Qua phần demo, em đã trình bày luồng thu thập, lưu trữ, truy vấn, cảnh báo và theo dõi hệ thống. Toàn bộ mã nguồn cùng dữ liệu đối chiếu được tổ chức trong repository để thầy kiểm tra. Em cảm ơn thầy đã theo dõi.

**Kết thúc:** Stop → xem lại → Save. Chỉ Disable rule/End Lab khi cả hai sinh viên đã kết thúc sử dụng môi trường; không cần thực hiện thay đổi đó ngay giữa video.

## Mẹo giữ video dưới 10 phút

- Chỉ đọc phần lời thoại; không đọc tên menu, SQL, JSON hoặc toàn bộ bảng.
- Chọn một môi trường làm demo chính; không lặp lại toàn bộ thao tác ở tài khoản thứ hai.
- Mở tab và chuẩn bị SQL trước. Không cài đặt hoặc tạo stack trong lúc quay.
- Nếu bị chờ dịch vụ, cắt đoạn chờ trước khi nộp và giữ nguyên kết quả thực thi.
- Mục tiêu khoảng 9 phút để có một phút dự phòng; diễn tập một lần bằng đồng hồ trước bản chính.

Tài liệu thao tác đối chiếu: [AWS Lambda Test](https://docs.aws.amazon.com/lambda/latest/dg/testing-functions.html), [Athena query results](https://docs.aws.amazon.com/athena/latest/ug/querying.html), [Microsoft Snipping Tool](https://support.microsoft.com/en-us/windows/apps/use-snipping-tool-to-capture-screenshots).

[Báo cáo chính](FINAL_REPORT.md) · [Checklist cuối phiên](SESSION_CHECKLIST.md)
