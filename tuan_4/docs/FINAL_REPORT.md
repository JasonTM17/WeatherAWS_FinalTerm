# Báo cáo Tuần 4 — Kiểm chứng hệ thống và chuẩn bị bảo vệ

**Nguyễn Tiến Sơn — MSSV 24110054; Trần Thị Ngọc Quyên — MSSV 24110051.**

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng.
**Ngày kiểm chứng:** 19/10/2026. **Phạm vi:** thực hiện các yêu cầu bổ sung sau khi báo cáo Tuần 3 được duyệt, làm đầu vào cho tổng kết Tuần 4.

**Ngày hoàn thiện tài liệu:** 20/10/2026. Số liệu thực thi trong báo cáo giữ mốc kiểm chứng ngày 19/10; việc biên tập tài liệu không tạo thêm lượt chạy AWS.

## Tóm tắt

Tuần 4 tập trung kiểm chứng luồng thu thập, lưu trữ, truy vấn và cảnh báo trên hai môi trường thực hành. Mỗi sinh viên có một lượt realtime thu đủ ba đô thị; raw tải lại từ S3 khớp SELECT theo record_id. Cùng chu kỳ kiểm chứng, mỗi môi trường ghi nhận một Invocation, không có Error và một thông điệp được SNS chấp nhận. Hai người nhận đã xác nhận email mới của đợt này.

Hồ sơ bổ sung Cost Explorer đúng kỳ, rà soát cấu hình S3, một template CloudFormation 17 tài nguyên đã kiểm tra và công cụ quản lý lịch cuối phiên. Các phần sau giải thích dữ liệu raw, điều kiện cảnh báo và phương pháp đối chiếu, đồng thời dẫn tới source, truy vấn, nhật ký và sản phẩm trình bày. [Nội dung nộp Tuần 4 có liên kết đầy đủ](SUBMISSION.md) được chuẩn bị riêng để sao chép vào hệ thống của lớp.

## Mục tiêu và phương pháp

Phép kiểm chứng đi theo một lượt xử lý xác định: source/gói triển khai → request → log → object S3 → CSV → SELECT Athena. Nhánh SNS được kiểm tra bằng dữ liệu và ngưỡng thật, kết quả Publish, sau đó xác nhận người nhận. Các kết luận sử dụng đúng request, cùng môi trường và cùng phạm vi thời gian.

![Kiến trúc thu thập và phân tích dữ liệu](../../docs/architecture.png)

*Hình 1. Kiến trúc ứng dụng được kiểm chứng trong Tuần 4. Sơ đồ thể hiện quan hệ thành phần; bảng kết quả và raw ở mục 3–4 ghi nhận thực thi của đợt ngày 19/10.*

## 1. Các nội dung thực hiện theo góp ý giảng viên

| Yêu cầu | Sản phẩm và bằng chứng |
| --- | --- |
| Message commit cạnh liên kết phải khớp Git | Đã cập nhật [nội dung nộp Tuần 3](../../BAO_CAO.md), [báo cáo kỹ thuật](../../tuan_3/docs/FINAL_REPORT.md) và [chỉ mục commit](../../docs/components.md) |
| Kiểm thử tổng thể | Hai lượt realtime, mỗi lượt 3 bản ghi; đối chiếu nguyên object S3 và một SELECT theo đúng record_id |
| Đối chiếu log–metric–S3 | Ghép request trong START/END/REPORT, Result, số dòng raw; kiểm tra riêng native metric theo cùng chu kỳ |
| Chi phí | Cost Explorer theo ngày/service/record type trong kỳ 12–19/10; giữ Estimated và giá trị chính xác |
| Kết thúc phiên Lab | [Checklist](SESSION_CHECKLIST.md), [công cụ preview/pause/restore](../scripts/session_control.py) với state file riêng và kiểm tra target |
| Một template CloudFormation | 17 tài nguyên, đã kiểm tra bằng cfn-lint và API ValidateTemplate trên hai môi trường; [hướng dẫn tạo stack riêng](INFRASTRUCTURE.md) |
| Rà soát bảo mật | Đọc S3 BPA, mã hóa, ACL/policy status, source và lịch; cung cấp mẫu quyền collector giới hạn theo tài nguyên |
| Video dưới 10 phút | [Kịch bản 9 phút 30 giây](DEMO_GUIDE.md), có nút bấm, kết quả cần quan sát và lời giải thích |

## 2. Phiên bản mã và hạ tầng

Source thu thập tiếp tục là [lambda_function.py](../../tuan_2/lambda/lambda_function.py), không tạo một thuật toán thu thập thứ hai. Module được tải từ cả hai Lambda, xác minh hash của gói và đối chiếu với source trong repository.

| Thuộc tính | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Source trùng repository | Đạt | Đạt |
| Lambda state/update | Active / Successful | Active / Successful |
| Lịch chuẩn | WeatherCollectionSchedule, Enabled | WeatherCollectionSchedule, Enabled |
| Chu kỳ | rate(1 hour) | rate(1 hour) |
| Số lịch đang bật cùng gọi collector | 1 | 1 |
| Target và quyền gọi theo ARN rule | Đạt | Đạt |

SHA-256 module dùng trong kiểm chứng:

```text
ade29ff52bfd14accb7c470f82b923704daade8a740ed16584bf523dc04cc219
```

Các lượt kiểm tra không thay source, ngưỡng, Secret hoặc lịch hiện hữu. [Bản dựng](../results/verification_2026_10_19/build.json), [source sinh viên Tiến Sơn](../results/verification_2026_10_19/environment/default/source.json), [source sinh viên Ngọc Quyên](../results/verification_2026_10_19/environment/quyen/source.json).

### 2.1. Cách source tạo ra kết quả kiểm chứng

| Thành phần trong source | Vai trò | Sản phẩm dùng để kiểm tra |
| --- | --- | --- |
| `fetch_secrets` và biến môi trường | Xác định vị trí, ngưỡng, bucket và topic; có nhánh cấu hình dự phòng khi đọc Secret thất bại | Cấu hình môi trường và log của lượt chạy |
| `fetch_city_data` | Gọi dữ liệu chất lượng không khí và thời tiết, chuẩn hóa thành bản ghi | Tên đô thị, record_id, thời gian và các giá trị raw |
| `lambda_handler` | Chọn realtime khi event `{}`; kiểm tra từng đô thị và ngưỡng cảnh báo | `collection_status`, `failed_cities`, `records_collected`, `alerts_sent` |
| `send_sns_alert` | Publish thông điệp; trả kết quả chấp nhận gửi cho handler | Số Publish được chấp nhận và xác nhận email lưu riêng |
| `save_records_to_s3` | Gom bản ghi theo ngày UTC và ghi NDJSON | `saved_files`, key và số dòng object tải lại |

Điều kiện trong [source chính](../../tuan_2/lambda/lambda_function.py) là:

```python
if rec['pm2_5'] >= threshold_pm25 or rec['us_aqi'] >= threshold_aqi:
    if send_sns_alert(rec, threshold_pm25, threshold_aqi):
        alerts_sent += 1
```

Phép so sánh lấy cả giá trị bằng ngưỡng và dùng điều kiện OR. `alerts_sent` chỉ tăng sau khi hàm gửi trả về thành công. Trạng thái `complete` mô tả thu thập; để đánh giá cảnh báo cần xem thêm dữ liệu, log gửi SNS và xác nhận người nhận. Nhánh backfill chủ động không gửi cảnh báo lịch sử.

## 3. Kiểm thử realtime → S3 → Athena

Mỗi môi trường được gọi một lần với event `{}`. Collector đọc cấu hình, thu thập dữ liệu của ba đô thị và trả trạng thái complete. Các object được tải lại nguyên byte từ S3; bản CSV được giữ cạnh JSON gốc để đối chiếu.

| Kiểm tra | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Bản ghi mới | 3 | 3 |
| Đô thị | 3 | 3 |
| Đô thị thất bại | 0 | 0 |
| Số cảnh báo dự kiến từ dữ liệu và ngưỡng thật | 1 | 1 |
| Số Publish được collector ghi nhận SNS chấp nhận | 1 | 1 |
| SELECT trả đúng ba record_id và giá trị raw | Đạt | Đạt |
| Sử dụng lại kết quả Athena | Không | Không |
| Bytes quét của SELECT đối chiếu | 19.683 | 20.251 |
| Engine execution time | 674 ms | 584 ms |
| Total execution time | 888 ms | 747 ms |

Hai SELECT trên kiểm tra đúng dữ liệu của lượt vừa chạy. Đây là số đo từng truy vấn, không phải trung vị của thử nghiệm NDJSON/Parquet. Dữ liệu ba đô thị giữ nguyên theo nguồn mô hình Open-Meteo; ngưỡng không được thay để tạo email thử.

- [Raw và kết quả sinh viên Tiến Sơn](../results/verification_2026_10_19/e2e/default/): JSON gốc, CSV, SQL và QueryExecutionId.
- [Raw và kết quả sinh viên Ngọc Quyên](../results/verification_2026_10_19/e2e/quyen/).
- [SQL theo đúng record_id của sinh viên Tiến Sơn](../results/verification_2026_10_19/e2e/default/exact_records.sql).
- [SQL theo đúng record_id của sinh viên Ngọc Quyên](../results/verification_2026_10_19/e2e/quyen/exact_records.sql).

### 3.1. Bảng dữ liệu raw của hai lượt realtime

Các giá trị sau được trích trực tiếp từ [CSV raw sinh viên Tiến Sơn](../results/verification_2026_10_19/e2e/default/raw_invocation.csv) và [CSV raw sinh viên Ngọc Quyên](../results/verification_2026_10_19/e2e/quyen/raw_invocation.csv), cùng ngày kiểm chứng 19/10/2026. Mỗi hàng là một bản ghi, không phải trung bình theo ngày.

| Sinh viên | Đô thị | US AQI | PM2.5, µg/m³ | Nhiệt độ, °C | Độ ẩm, % |
| --- | --- | ---: | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | TP. Hồ Chí Minh | 61 | 22,1 | 26,7 | 89,0 |
| Sinh viên Tiến Sơn | Hà Nội | 101 | 29,9 | 27,3 | 81,0 |
| Sinh viên Tiến Sơn | Đà Nẵng | 52 | 7,3 | 25,3 | 92,0 |
| Sinh viên Ngọc Quyên | TP. Hồ Chí Minh | 61 | 22,1 | 26,7 | 89,0 |
| Sinh viên Ngọc Quyên | Hà Nội | 101 | 29,9 | 27,3 | 81,0 |
| Sinh viên Ngọc Quyên | Đà Nẵng | 52 | 7,3 | 25,3 | 92,0 |

CSV nguồn giữ đủ **23 trường**, gồm record_id, tọa độ, thời gian UTC/Việt Nam, khí tượng, chất lượng không khí, cấp AQI và khóa thời gian. Các [JSON sinh viên Tiến Sơn](../results/verification_2026_10_19/e2e/default/objects/) và [JSON sinh viên Ngọc Quyên](../results/verification_2026_10_19/e2e/quyen/objects/) giữ byte gốc tải lại từ S3.

Hai lượt dùng cùng nguồn mô hình và vị trí nên có thể có cùng giá trị môi trường. Mã bản ghi của hai lượt vẫn khác nhau; SELECT kiểm tra đúng các mã đó. Vì vậy, các giá trị bằng nhau ở bảng này không được dùng để coi hai báo cáo là hai phép đo độc lập tại trạm.

### 3.2. Từ dữ liệu đến quyết định cảnh báo

| Đô thị trong mỗi lượt | AQI ≥ 100 | PM2.5 ≥ 35,5 µg/m³ | Kết quả điều kiện OR |
| --- | --- | --- | --- |
| TP. Hồ Chí Minh | Không: 61 | Không: 22,1 | Không phát sinh yêu cầu cảnh báo |
| Hà Nội | Có: 101 | Không: 29,9 | Phát sinh một yêu cầu cảnh báo |
| Đà Nẵng | Không: 52 | Không: 7,3 | Không phát sinh yêu cầu cảnh báo |

Mỗi môi trường vì vậy có một đô thị thỏa điều kiện trong đúng lượt đã lưu. Kết quả `alerts_sent = 1` được đối chiếu với điều kiện trong source và bản raw, sau đó kiểm tra riêng email tới người nhận. Ngưỡng này là cấu hình của đồ án; không diễn giải thành một kết luận y tế.

### 3.3. Cách đọc một lượt demo mới

Một lượt demo sau đó có thể cho dữ liệu và số cảnh báo khác bảng ngày 19/10. Khi `alerts_sent = 0`, trước tiên kiểm tra các giá trị AQI/PM2.5 và log gửi thông báo: nếu không đô thị nào đạt ngưỡng thì không phát cảnh báo là phù hợp; nếu có đô thị đạt ngưỡng thì cần kiểm tra topic và kết quả Publish. Không suy ra nguyên nhân chỉ từ số 0.

Thông báo `Executing function: succeeded` xác nhận lượt gọi kết thúc thành công. Phần `collection_status`, `failed_cities`, số bản ghi và object S3 tiếp tục được đọc để xác nhận kết quả nghiệp vụ. `Duration` là thời gian thực thi; dòng hiển thị dạng “seconds ago” chỉ thời điểm chạy cách hiện tại bao lâu.

## 4. Đối chiếu vận hành và cảnh báo

### 4.1. Chu kỳ chứa lượt kiểm chứng có kiểm soát

| Chỉ tiêu | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Native Invocations | 1 | 1 |
| Native Errors | 0 | 0 |
| Result log của request được kiểm chứng | 1 | 1 |
| START/END/REPORT của request | Đủ | Đủ |
| Dòng S3 của lượt kiểm chứng | 3 | 3 |
| Tỷ lệ lỗi trong chu kỳ kiểm chứng hợp lệ | 0% | 0% |

Request trong log khớp với mã request đã băm của lượt gọi; Result dẫn tới object S3 có số dòng tương ứng. Native metric được ghép theo chu kỳ 300 giây. Bảng này chỉ áp dụng cho chu kỳ chứa lượt kiểm chứng, không suy rộng tỷ lệ 0% cho toàn bộ lịch sử vận hành.

Kết quả chi tiết: [sinh viên Tiến Sơn](../results/verification_2026_10_19/controlled/default.json), [sinh viên Ngọc Quyên](../results/verification_2026_10_19/controlled/quyen.json). Các chu kỳ khác trong cửa sổ quan sát được giữ trong [metric sinh viên Tiến Sơn](../results/verification_2026_10_19/environment/default/metric_reconciliation.json) và [metric sinh viên Ngọc Quyên](../results/verification_2026_10_19/environment/quyen/metric_reconciliation.json); chu kỳ thiếu cặp không dùng để tính tỷ lệ toàn cửa sổ.

### 4.2. Kiểm tra nhánh cảnh báo

Ngưỡng thực tế đọc trước lượt chạy là `AQI >= 100 OR PM2.5 >= 35.5`. Dữ liệu mỗi lượt thỏa điều kiện cảnh báo ở một đô thị; collector ghi nhận một Publish được SNS chấp nhận ở mỗi môi trường. Cả sinh viên Tiến Sơn và sinh viên Ngọc Quyên đã xác nhận nhận email mới của đúng hai lượt kiểm chứng. [Xác nhận người nhận](../results/verification_2026_10_19/recipient_confirmation.json) được lưu riêng để đối chiếu với kết quả Publish.

Các ca biên bằng ngưỡng, dưới ngưỡng và điều kiện OR được kiểm tra trong bộ hồi quy. Ca dữ liệu lịch sử không được dùng để kiểm chứng email realtime.

## 5. Chi phí theo kỳ thực hành

Cost Explorer được gọi theo ngày, nhóm **Service** và **Record type** với metric UnblendedCost, kỳ từ 12/10 đến hết 19/10; API dùng ngày kết thúc không bao gồm là 20/10.

| Sinh viên | Dòng service/record type được trả về | Tổng hiển thị đến cent, USD |
| --- | --- | --- |
| Sinh viên Tiến Sơn | 70 | 0,00 |
| Sinh viên Ngọc Quyên | 47 | 0,14 |

Giá trị chính xác, cờ Estimated và từng nhóm được giữ tại [CSV sinh viên Tiến Sơn](../results/verification_2026_10_19/environment/default/cost_by_service.csv), [CSV sinh viên Ngọc Quyên](../results/verification_2026_10_19/environment/quyen/cost_by_service.csv). Tổng hiển thị được làm tròn đến cent; các lượng rất nhỏ không bị đổi dấu hoặc sửa trong dữ liệu gốc. Kỳ này là chi phí tài khoản theo dịch vụ, không gọi là chi phí được phân bổ riêng cho dự án hoặc toàn bộ Tuần 4.

Với riêng ngày 19/10, lần đọc trước đó chưa có nhóm chi phí được AWS trả về cho sinh viên Tiến Sơn; chương trình ghi `NOT_AVAILABLE`, không tự gán bằng 0. Báo cáo dùng kỳ nhiều ngày có nhóm số liệu được trả về ở cả hai môi trường. Mức dự kiến trong các báo cáo trước giữ vai trò kế hoạch, không thay thế số Cost Explorer.

## 6. CloudFormation và bảo mật

### 6.1. Hạ tầng dưới dạng mã

[Template ứng dụng](../infrastructure/weather-stack.json) có S3/BucketPolicy, Secret, SNS/subscription, Lambda/log group, EventBridge/permission, Glue database/table, Athena workgroup, alarm và dashboard. Nguồn Lambda được đóng gói từ source chính, có artifact SHA-256 và S3 VersionId khi triển khai.

- cfn-lint **1.57.2**: đạt kiểm tra cho vùng us-east-1.
- AWS **ValidateTemplate**: bản 17 tài nguyên đạt trên cả hai profile, xác nhận sáu tham số. [Hồ sơ template hiện tại](../results/template_validation_2026_10_19/README.md).
- Stack mới khởi tạo với lịch **DISABLED**, giữ bucket/Secret/log theo Retain; không sửa LabRole.
- Lần kiểm chứng này xác nhận template và mã đang vận hành; chưa tạo stack CloudFormation mới. [Hướng dẫn triển khai](INFRASTRUCTURE.md) mô tả bước tạo stack và kiểm chứng riêng sau CREATE_COMPLETE.

### 6.2. Kết quả đọc cấu hình hiện hữu

| Kiểm tra | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Đủ bốn S3 Block Public Access | Đạt | Đạt |
| Public bucket policy / public ACL | Không / Không | Không / Không |
| Mã hóa mặc định | AES256 | AES256 |
| Versioning bucket hiện hữu | Chưa bật | Chưa bật |
| Versioning theo template mới | Enabled | Enabled |
| Source và lịch đúng môi trường | Đạt | Đạt |

Quyền đọc IAM policy của LabRole bị môi trường từ chối trong lần kiểm chứng, nên không kết luận effective permissions của role đã tối thiểu. [Mẫu quyền collector](../infrastructure/collector-policy.example.json) giới hạn ghi raw, đọc một Secret, Publish một topic và ghi một log group; đây là đề xuất cho execution role riêng. Không có thao tác sửa role học phần dùng chung. [Phương pháp rà soát](SECURITY_REVIEW.md) nêu rõ cách kiểm tra phạm vi quyền.

## 7. Quản lý cuối phiên và video

[session_control.py](../scripts/session_control.py) mặc định xem trước. Khi xác nhận áp dụng, chương trình lưu trạng thái riêng, kiểm tra đúng account/function/rule/target và đọc lại DISABLED. Khi restore, binding phải trùng bản lưu; lịch vốn tắt không được tự bật. Tệp khôi phục được cập nhật qua tệp tạm và atomic replacement để tránh mất bản gốc khi ghi lỗi.

Trong lần kiểm chứng này, lịch thu thập hiện hữu được giữ nguyên, chưa chạy pause/restore trên AWS. Các tình huống phục hồi đã được kiểm thử cục bộ. [Checklist kết thúc Lab](SESSION_CHECKLIST.md) quy định xuất minh chứng trước, dừng lịch rồi kết thúc phiên; chỉ thu hồi các thử nghiệm đã xác định phạm vi, giữ dữ liệu phục vụ báo cáo.

[Kịch bản video](DEMO_GUIDE.md) dài 9 phút 30 giây, hướng dẫn từ trang GitHub đến rule, Test Lambda, log, S3, Athena, SNS/email, dashboard, chi phí và bảo mật. Nội dung trình bày gắn với ngày và phạm vi dữ liệu thực tế.

## 8. Kiểm tra mã và hướng hoàn thiện theo kế hoạch

34 kiểm thử Tuần 4 đã đạt trên máy Windows, gồm trường hợp billing chính xác, thiếu metric, nhầm lịch, thay target, mất phản hồi, ghi tệp khôi phục lỗi, tái lập báo cáo và truyền tham số PowerShell. Hai điểm phát hiện ở lượt review độc lập đã được sửa và kiểm tra lại. [Manifest](../results/verification_2026_10_19/manifest.json) kiểm tra toàn vẹn các tệp minh chứng của đợt này.

[Báo cáo tổng kết đồ án](../../docs/FINAL_PROJECT_REPORT.md) nối kết kết quả Tuần 1–4, phân tích thực nghiệm Athena, đánh giá dự báo và đối chiếu yêu cầu cuối kỳ. Nhật ký giờ công đã được xác nhận tại mục 9. Video thực tế cần được quay và bổ sung đường dẫn theo kịch bản; các kỳ đánh giá dữ liệu tiếp theo trong [kế hoạch](../../docs/WEEK_4_PLAN.md) được theo dõi riêng với kết quả đã kiểm chứng ngày 19/10.

[Hồ sơ Tuần 4](../README.md) · [Nhật ký sản phẩm](WORKLOG.md) · [Kế hoạch](../../docs/WEEK_4_PLAN.md)

## 9. Phân công và nhật ký theo tuần

Sinh viên Tiến Sơn phụ trách hạ tầng, S3, cấu hình, Lambda, lịch thu thập, SNS và CloudWatch. Sinh viên Ngọc Quyên phụ trách Glue/Athena, chất lượng dữ liệu, phân tích chi phí và đối chiếu báo cáo. Hai sinh viên rà soát chéo minh chứng và chuẩn bị trình bày.

| Tuần | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên | Tổng |
| --- | --- | --- | --- |
| Tuần 1 | 9,5 giờ | 9,0 giờ | 18,5 giờ |
| Tuần 2 | 10,0 giờ | 9,5 giờ | 19,5 giờ |
| Tuần 3 | 10,0 giờ | 10,0 giờ | 20,0 giờ |
| Tuần 4 | 10,0 giờ | 10,0 giờ | 20,0 giờ |
| Tổng | 39,5 giờ | 38,5 giờ | **78,0 giờ** |

Căn cứ: **Tổng theo tuần đã xác nhận**. Giờ công thực tế Tuần 4 đã xác nhận là 10 giờ cho mỗi sinh viên; [bản ghi xác nhận](../results/verification_2026_10_19/worklog_confirmation.json), [CSV Tuần 4](../worklog.csv), [nhật ký](WORKLOG.md). Giờ công ghi nhận công việc thực tế, tách với trạng thái từng phép kiểm chứng dịch vụ.

## 10. Kết luận

Đợt kiểm chứng đã nối được source triển khai, request thực thi, ba bản ghi S3 và truy vấn Athena ở mỗi môi trường. Nhánh cảnh báo được đối chiếu với ngưỡng thật và xác nhận email mới của hai sinh viên. Hồ sơ chi phí, bảo mật và hạ tầng dùng cùng nguồn bằng chứng và có đường dẫn tái lập.

Repository giữ một template chính, các chương trình xuất báo cáo có kiểm tra nguồn và một kịch bản quay khoảng 9 phút. Các bước tạo stack mới, quản lý lịch cuối phiên và các kỳ đánh giá kế tiếp được thực hiện theo checklist tương ứng, ghi nhận theo kết quả thực tế.

Phần tổng kết xuyên suốt về mục tiêu, lựa chọn kiến trúc, phương pháp phân tích và sản phẩm bàn giao được trình bày tại [Báo cáo tổng kết đồ án](../../docs/FINAL_PROJECT_REPORT.md).

## 11. Đối chiếu sản phẩm cuối kỳ và cách kiểm tra lại

| Nội dung | Tài liệu kiểm tra | Kết quả bàn giao |
| --- | --- | --- |
| Source, raw và SELECT của lượt thật | Mục 2–3; [bộ raw và truy vấn](../results/verification_2026_10_19/e2e/) | Hai lượt, sáu bản ghi; SELECT khớp mã và giá trị raw |
| Log, metric và cảnh báo | [Bảng đối chiếu](LOG_METRIC_S3_RECONCILIATION.md); [xác nhận email](../results/verification_2026_10_19/recipient_confirmation.json) | Có số liệu cùng chu kỳ; email đã được hai người nhận xác nhận |
| Chi phí và bảo mật | [Chi phí](COST_REPORT.md); [cấu hình bảo mật](SECURITY_AUDIT.md) | Có kỳ, nguồn và phân biệt cấu hình hiện hữu/thiết kế mới |
| Hạ tầng dưới dạng mã | [Template](../infrastructure/weather-stack.json); [kết quả kiểm tra](../results/template_validation_2026_10_19/README.md) | Một template 17 tài nguyên đã kiểm tra; việc tạo stack mới có quy trình riêng |
| Quản lý sau buổi thực hành | [Checklist](SESSION_CHECKLIST.md) | Có preview/pause/restore và thứ tự xuất minh chứng trước khi kết thúc Lab |
| Phân công và giờ công | [Nhật ký](WORKLOG.md); [CSV](../worklog.csv) | 20 giờ Tuần 4; 78 giờ toàn đồ án đã xác nhận |
| Video trình bày | [Lời thoại](VIDEO_DEMO_SCRIPT.md); [hướng dẫn thao tác](DEMO_GUIDE.md) | Có kịch bản dưới 10 phút; đường dẫn video thực tế bổ sung sau khi quay |
| Nội dung nộp và tổng kết | [Nội dung nộp Tuần 4](SUBMISSION.md); [tổng kết toàn đồ án](../../docs/FINAL_PROJECT_REPORT.md) | Có văn bản và liên kết đầy đủ để sao chép |

Các phép kiểm tra dưới đây đọc hồ sơ đã lưu, không gọi Lambda hoặc thay đổi cấu hình AWS:

```powershell
python tuan_2/scripts/repository_audit.py --check
python tuan_4/scripts/verify_results.py
python tuan_4/scripts/cost_analysis.py --check
python tuan_4/scripts/reconcile_ops.py --check
python tuan_4/scripts/security_report.py --check
```

Kiểm tra mã và cơ chế quản lý phiên: `python -m unittest discover -s tuan_4/tests -v`. Quy trình CI chạy theo từng commit tại [GitHub Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml). Kết quả kiểm tra tệp đã lưu, kiểm thử chương trình và quan sát trực tiếp AWS được trình bày theo từng nguồn bằng chứng tương ứng.

### Phiên bản hoàn thiện hồ sơ Tuần 4

- **`feat(week4): complete final week verification, consolidate CloudFormation infrastructure, and update catalog` — 96bedec:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093).
- **`docs(week4): synchronize final report test count to 34` — e9704bf:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e9704bf645a11bf07a3f360770061c1cc3a8b3a5](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e9704bf645a11bf07a3f360770061c1cc3a8b3a5).
- **`fix(evidence): preserve Week 4 snapshot bytes across platforms` — 892861e:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/892861ec5129d59a9c772ef20ed6d2ac053d65f5](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/892861ec5129d59a9c772ef20ed6d2ac053d65f5).
