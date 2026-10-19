# Hướng dẫn quay demo — Từng thao tác trong tối đa 10 phút

**Mục tiêu:** giải thích được luồng EventBridge → Lambda → S3 → Athena và nhánh SNS/email, theo dõi bằng CloudWatch; trình bày thêm chi phí, bảo mật và cách kết thúc phiên thực hành.

**Thời lượng mục tiêu: 9 phút 30 giây.** Diễn tập trước một lần; mở sẵn tab để không mất thời gian tìm dịch vụ. Có thể chia lời trình bày cho hai sinh viên, dùng một môi trường làm demo chính và mở bảng kiểm chứng môi trường còn lại.

## Cách bắt đầu quay trên Windows 11

1. Mở sẵn cửa sổ trình duyệt sẽ demo và đóng các cửa sổ có khóa đăng nhập.
2. Bấm **Start**, tìm **Snipping Tool**, mở ứng dụng → chọn biểu tượng **Record/Video** → **New**. Hoặc nhấn **Windows + Shift + R**.
3. Kéo chọn vùng chứa cửa sổ trình duyệt. Giữ cửa sổ ở vị trí này suốt buổi quay; không chọn phần có thông tin riêng tư ở ngoài vùng demo.
4. Kiểm tra biểu tượng micro trên thanh quay của phiên bản đang dùng; cho phép quyền micro và bật thu giọng nói. Quay thử khoảng 10 giây, mở lại nghe trước khi quay bản chính.
5. Bấm **Start**, trình bày theo thứ tự bên dưới. Khi xong chọn **Stop**, xem lại rồi **Save** bản video. Đặt tên `Demo_WeatherAWS_24110054_24110051.mp4` nếu lưu ở định dạng MP4.
6. Xem lại âm thanh, độ rõ chữ, thời lượng và vùng hình trước khi nộp. Có thể dùng **Edit in Clipchamp** để cắt thời gian chờ và che thông tin riêng tư, giữ nguyên các kết quả thực thi.

Các nút quay và phím tắt được đối chiếu theo [hướng dẫn Snipping Tool của Microsoft](https://support.microsoft.com/en-us/windows/apps/use-snipping-tool-to-capture-screenshots). Nếu máy không có chế độ Video, mở Snipping Tool từ Start để kiểm tra phiên bản hỗ trợ trước khi quay.

## 1. Chuẩn bị trước khi bấm quay

1. Start Lab, đợi phiên hoạt động. Trong AWS Console chọn **N. Virginia — us-east-1**. Đây là vùng chứa `WeatherCollectorLambda`.
2. Mở một cửa sổ trình duyệt riêng. Đóng tab chứa credentials, trang AWS Details và Secret value; tắt thông báo. Kiểm tra lại vùng cửa sổ được ghi hình trước khi quay.
3. Mở sẵn các tab sau theo thứ tự:

| Tab | Địa chỉ / nội dung |
| --- | --- |
| 1 | [Repository và hồ sơ Tuần 4](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4) |
| 2 | [EventBridge Rules](https://us-east-1.console.aws.amazon.com/events/home?region=us-east-1#/rules), chọn bus `default` |
| 3 | [Lambda WeatherCollectorLambda](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions/WeatherCollectorLambda) |
| 4 | [CloudWatch Logs](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups), log group `/aws/lambda/WeatherCollectorLambda` |
| 5 | [S3 Console](https://s3.console.aws.amazon.com/s3/buckets?region=us-east-1), bucket raw `weather-aqi-…` của môi trường đang đăng nhập |
| 6 | [Athena Query editor](https://us-east-1.console.aws.amazon.com/athena/home?region=us-east-1#/query-editor), database `weather_aqi_db` |
| 7 | [SNS Topics](https://us-east-1.console.aws.amazon.com/sns/v3/home?region=us-east-1#/topics) và hộp thư nhận cảnh báo |
| 8 | [CloudWatch Dashboards](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:), mở `WeatherAirQuality-Week3` |
| 9 | [Cost Explorer](https://console.aws.amazon.com/costmanagement/home#/cost-explorer) hoặc CSV chi phí đã xuất; template CloudFormation trong GitHub |

Các đường dẫn Console cần đăng nhập bằng phiên Lab. Nếu Console chuyển về trang chủ, tìm dịch vụ bằng ô tìm kiếm phía trên rồi mở tài nguyên theo tên. Với stack CloudFormation mới, dùng tên trong **Outputs** thay cho các tên của hệ thống hiện hữu.

4. Trong Lambda, chuẩn bị test event **`demo-week4`** với JSON **`{}`**. Chưa bấm Test ở bước chuẩn bị nếu muốn ghi hình đúng một lượt mới.
5. Đảm bảo SNS subscription đã Confirmed. Chuẩn bị cách che địa chỉ email khi quay; chỉ hiển thị subject, ngày và nội dung cảnh báo cần đối chiếu.
6. Mở trước [báo cáo kiểm chứng](VERIFICATION_REPORT.md) và [checklist cuối phiên](SESSION_CHECKLIST.md). Không đổi ngưỡng thật để làm cho dữ liệu trông đẹp hơn.

## 2. Kịch bản 9 phút 30 giây

| Thời lượng | Màn hình và việc làm | Ý chính cần nói |
| --- | --- | --- |
| 00:00–00:40 | GitHub: tên đề tài, sinh viên, sơ đồ | Ba đô thị, nguồn Open-Meteo, luồng thu thập và nhánh cảnh báo |
| 00:40–01:20 | EventBridge: rule, state, schedule, target | Một lịch một giờ gọi đúng Lambda |
| 01:20–02:20 | Lambda: event `{}` → Test → kết quả | Lượt mới, ba bản ghi, ba đô thị và số cảnh báo thực tế |
| 02:20–03:20 | CloudWatch Logs → S3 object | Ghép kết quả thực thi với đúng dữ liệu được lưu |
| 03:20–04:30 | Athena: chạy SELECT → kết quả | Đọc được dữ liệu raw qua Glue và truy vấn theo phân vùng |
| 04:30–05:20 | SNS subscription và email | Phân biệt gửi tới SNS, giao thông báo và người nhận |
| 05:20–06:20 | Dashboard và bảng log–metric–S3 | Native metric có cửa sổ; không coi điểm thiếu là 0 |
| 06:20–07:00 | Chi phí | Kỳ đo, đơn vị, Estimated và phạm vi tài khoản |
| 07:00–08:30 | S3 Permissions + template + policy | BPA, mã hóa, một stack, quyền theo tài nguyên |
| 08:30–09:30 | Checklist, CI, commit và kết luận | Kết thúc Lab có kiểm soát; minh chứng truy được về source |

## 3. Hướng dẫn bấm và lời trình bày

### Bước A — Giới thiệu trên GitHub

**Bấm:** repository → `tuan_4` → mở sơ đồ và bảng tài liệu; có thể mở `tuan_3` để chỉ ra phần đã được giảng viên duyệt.

**Nói:** “Em là Nguyễn Tiến Sơn, MSSV 24110054, cùng sinh viên Trần Thị Ngọc Quyên, MSSV 24110051. Đề tài thu thập dữ liệu thời tiết và chất lượng không khí của TP. Hồ Chí Minh, Hà Nội và Đà Nẵng. Em sẽ trình bày một lượt chạy thực tế, đối chiếu dữ liệu và các bước quản lý hệ thống.”

### Bước B — Chứng minh lịch thu thập

**Bấm:** EventBridge → **Rules** (mục bus/rule, không phải Scheduler) → Event bus `default` → tìm `WeatherCollectionSchedule` → mở rule → xem **Schedule** và **Targets**.

**Cần thấy:** State `Enabled`; `rate(1 hour)`; target `WeatherCollectorLambda`. Ở môi trường sinh viên Ngọc Quyên, lịch phụ `WeatherCollectionHourlyRule` phải tiếp tục Disabled.

**Nói:** “Rule này phát sự kiện một giờ một lần và gọi đúng hàm thu thập. Hệ thống giữ một lịch đang chạy cho collector để tránh thu thập và gửi cảnh báo hai lần do hai lịch cùng hoạt động.”

### Bước C — Chạy Lambda đúng một lần

**Bấm:** Lambda → `WeatherCollectorLambda` → tab **Test**. Nếu chưa có event, chọn **Create new event**, đặt tên `demo-week4`, thay nội dung bằng `{}`, chọn **Save**. Chọn event đó rồi bấm **Test** **một lần**, đợi thực thi xong, mở **Details/Execution result**.

**Cần thấy:** `collection_status: complete`, `records_collected: 3`, `failed_cities: []`, `saved_files` và `alerts_sent`. Kiểm tra kết quả thật, không đọc thuộc một số cảnh báo cố định.

**Nói:** “Event rỗng chạy nhánh realtime. Hàm đọc vị trí và ngưỡng, gọi API cho ba đô thị, lưu bản ghi theo ngày UTC lên S3. Cảnh báo được xét khi AQI từ 100 hoặc PM2.5 từ 35,5. Số cảnh báo trên màn hình là kết quả của lượt chạy này.”

**Chú ý:** Không dùng `backfill_hours` cho phần demo cảnh báo: nhánh lịch sử chủ động không gửi email lịch sử. Nếu nút Test mất phản hồi, mở log trước khi chạy lại để tránh tạo hai lượt.

### Bước D — Từ log sang đúng object S3

**Bấm:** trong Lambda chọn **Monitor → View CloudWatch logs**, hoặc dùng tab CloudWatch đã mở → `/aws/lambda/WeatherCollectorLambda` → stream mới nhất → tìm `[INFO] Result:`. Xem START/END/REPORT và Result của cùng lượt.

Ghi lại key ở `saved_files`. Chuyển tab S3 → bucket raw → mở đúng đường dẫn `raw/year=…/month=…/day=…/` theo key đó → chọn object → **Download** để mở JSON trên máy nếu cần. Chỉ mở tệp dữ liệu, không chuyển sang tab Notepad chứa khóa.

**Cần thấy:** số dòng bằng `count` trong `saved_files`, có đủ ba đô thị. Mỗi dòng chứa `record_id`, timestamp, AQI, PM2.5 và các trường thời tiết.

**Nói:** “Em đối chiếu key S3 và số dòng từ kết quả Lambda. Dữ liệu có cả thời gian mô hình và thời điểm thu thập; partition dùng UTC, còn phần trình bày dùng ngày Việt Nam.”

### Bước E — Truy vấn Athena

**Bấm:** Athena → **Query editor** → chọn workgroup đang dùng, data source `AwsDataCatalog`, database `weather_aqi_db`.

Ưu tiên mở `exact_records.sql` do [run_demo_check.py](../scripts/run_demo_check.py) tạo từ lần diễn tập, chạy **Run** và giải thích đây là truy vấn đúng record_id của lượt diễn tập đã lưu. Muốn đối chiếu đúng lượt vừa quay, lấy ba record_id trong JSON ở bước D và thay trong câu truy vấn trước khi bấm Run.

Cách xem nhanh dữ liệu của ngày đang demo:

```sql
SELECT city, timestamp_vn, collected_at, us_aqi, pm2_5
FROM weather_aqi_db.weather_airquality_records
WHERE year = '2026' AND month = '10' AND day = '19'
ORDER BY collected_at DESC, city
LIMIT 9;
```

**Thay ngày trong WHERE bằng ngày UTC trong key S3 của lượt quay.** Truy vấn này lấy tối đa 9 dòng trong ngày, không mặc nhiên là riêng ba dòng của lần bấm Test. Nếu dùng stack CloudFormation mới, chọn database/workgroup từ Outputs.

**Cần thấy:** query `Succeeded`, các trường dữ liệu và số byte quét. Với truy vấn exact-records, phải ra đúng ba record_id và giá trị giống raw. Nếu ngày mới chưa được đăng ký trong catalog hiện hữu, cập nhật catalog trước buổi quay và chạy lại kiểm tra; không đổi ngày truy vấn để giả là dữ liệu mới.

**Nói:** “Glue lưu lược đồ và thông tin phân vùng, Athena đọc dữ liệu từ S3. Em lọc phân vùng để giới hạn lượng dữ liệu quét; các giá trị AQI/PM2.5 đối chiếu được với JSON nguồn.”

### Bước F — SNS và email

**Bấm:** SNS → **Topics** → topic có tên `weather-airquality-alerts` → **Subscriptions** → kiểm tra Confirmed. Chuyển sang hộp thư, tìm subject `[AWS ALERT]`, mở đúng thư mới nếu lượt ở bước C đã phát cảnh báo.

**Nói:** “Điều kiện cảnh báo nằm trong collector. `alerts_sent` ghi số lần SNS chấp nhận Publish. Subscription phải được xác nhận; em kiểm tra thêm thư đến để xác nhận tới người nhận.”

Nếu `alerts_sent = 0`, nói dữ liệu lượt này chưa vượt ngưỡng. Có thể mở thư cảnh báo đã lưu trước đó và nêu đúng ngày kiểm chứng. Không gọi thư cũ là thư của lượt mới và không hạ ngưỡng trong lúc quay.

### Bước G — CloudWatch và đối chiếu vận hành

**Bấm:** CloudWatch → **Dashboards → WeatherAirQuality-Week3** → chọn cửa sổ có lượt chạy, ví dụ **3h** → **Refresh**. Xem Invocations/Errors/Duration, SNS và phần counter gaps. Mở thêm bảng `collection_s3.csv`/`metric_reconciliation.json` của lượt kiểm chứng Tuần 4.

**Nói:** “Em dùng cùng hàm, cùng cửa sổ UTC và chu kỳ 300 giây. Log START/END/REPORT đối chiếu request; Result đối chiếu key và số dòng S3. Metric là phép tổng hợp khác: chỉ tính tỷ lệ lỗi ở chu kỳ có cả Errors và Invocations hợp lệ. Bộ đếm giao SNS không thay cho xác nhận người nhận.”

Metric có thể cập nhật sau log; không bấm Test nhiều lần để ép biểu đồ hiện ngay. Có thể dùng bảng kiểm chứng đã chốt và nêu ngày của bảng.

### Bước H — Chi phí

**Bấm:** Cost Explorer → **Cost and usage** → chọn kỳ thực hành → **Daily** → nhóm theo **Service**. Mở thêm CSV theo service/record type trong hồ sơ Tuần 4.

**Nói:** “Chi phí được lấy từ Cost Explorer theo kỳ và đơn vị USD, có cờ Estimated. Đây là số liệu phạm vi tài khoản theo dịch vụ; mức dự kiến của bài thực hành được trình bày riêng. Dữ liệu ngày đang chạy có thể chưa được AWS tổng hợp.”

Nếu chưa có nhóm chi phí trong ngày hoặc tài khoản không cho mở Cost Explorer, mở báo cáo/CSV kỳ đã xuất đúng ngày và ghi đúng trạng thái. Không thay số thực đo bằng 0,05 USD dự kiến.

### Bước I — Bảo mật và hạ tầng

**Bấm:** S3 → bucket → **Permissions → Block public access**: kiểm tra bốn mục bật. Chuyển **Properties → Default encryption** để xem AES256. Không chọn Edit trong phần quay này.

Chuyển GitHub → `tuan_4/infrastructure/weather-stack.json`; lần lượt tìm `DataBucket`, `Collector`, `HourlyRule`, `SchedulePermission`, `RawTable`. Nếu đã tạo stack thật, mở CloudFormation → stack → **Resources/Outputs**; nếu chỉ đang trình bày mã template, gọi đúng là cấu hình IaC đã kiểm tra.

**Nói:** “Một template khai báo 15 tài nguyên ứng dụng. Bucket riêng tư và mã hóa; source Lambda được đóng gói theo hash và version artifact. Stack mới khởi tạo với lịch tắt, bật sau kiểm thử. LabRole là role do môi trường học phần cung cấp; em không sửa role dùng chung và đã tách mẫu quyền runtime giới hạn theo bucket, Secret, topic và log group.”

### Bước J — Kết thúc và bàn giao

**Bấm:** GitHub → **Actions** → mở lần Verify repository thành công của commit đang trình bày. Mở commit và đọc đúng **message gốc** cạnh link trong báo cáo. Chuyển checklist cuối phiên.

**Nói:** “Sau thực hành, em chờ các lượt đang chạy kết thúc, xuất raw/log/metric/chi phí và hash, tạm dừng rule đã kiểm tra target, rồi kết thúc Learner Lab. Dữ liệu phục vụ báo cáo được giữ lại; các thử nghiệm riêng được kiểm kê trước khi thu hồi.”

Nếu buổi quay cũng là kết thúc phiên Lab: sau khi lưu hết minh chứng, vào rule → **Disable** → xác nhận → kiểm tra state `Disabled`; chỉ thao tác trên đúng môi trường và không có người đang cần lịch đó. Ưu tiên công cụ [pause/restore](SESSION_CHECKLIST.md) để lưu trạng thái khôi phục trước. End Lab thực hiện sau khi quay hoặc ở đoạn cuối.

## 4. Câu hỏi vấn đáp cần hiểu

| Câu hỏi | Cách giải thích |
| --- | --- |
| Vì sao S3 có nhiều hơn ba bản ghi? | Mỗi lượt tạo bản ghi mới, dữ liệu tích lũy gồm nhiều lượt/giờ; ba dòng là phạm vi một lượt realtime |
| Vì sao hai sinh viên có AQI giống nhau? | Cùng nguồn mô hình, tọa độ và giờ đích có thể trả cùng giá trị; so sánh dùng cùng tập giờ, không sửa dữ liệu để tạo khác biệt |
| Dữ liệu có phải trạm đo tại chỗ? | Là dữ liệu mô hình từ Open-Meteo/CAMS; kết luận theo nguồn và khung giờ của bộ dữ liệu |
| Vì sao có log nhưng metric chưa hiện? | Hai luồng ghi nhận và tổng hợp riêng; kiểm tra cửa sổ, dimension, chu kỳ và thời gian cập nhật |
| Vì sao dùng Secret khi API miễn phí? | Quản lý tập trung vị trí/ngưỡng, tránh gắn cấu hình theo tài khoản vào source; không cần nhúng API key |
| LabRole đã tối thiểu chưa? | Template không sửa role học phần; kiểm tra scope thực tế và cung cấp mẫu policy hẹp cho execution role riêng |
| Disable rule có xóa dữ liệu hoặc hết phí ngay không? | Không. Nó ngừng lịch đó phát sự kiện mới; dữ liệu và các dịch vụ lưu trữ vẫn cần quản lý |

## 5. Checklist trước khi nộp video

- [ ] Video dưới 10 phút, đọc rõ, cursor dễ theo dõi và không mất thời gian chờ/tìm tab.
- [ ] Thể hiện ít nhất một lượt thật và liên hệ được Result → log → S3 → Athena.
- [ ] Phân biệt trạng thái SNS với email nhận; không dùng lại ngày cũ như lượt mới.
- [ ] Có chi phí, BPA/mã hóa, template, CI và kết thúc Lab.
- [ ] Không có khóa, Secret value hoặc trang đăng nhập riêng tư trong khung hình.
- [ ] Link video có quyền xem phù hợp với lớp; các link GitHub mở đúng trang công khai.

[Hồ sơ Tuần 4](../README.md) · [Báo cáo kiểm chứng](VERIFICATION_REPORT.md)
