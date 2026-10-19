# Báo cáo Tuần 4 — Kiểm chứng hệ thống và chuẩn bị bảo vệ

**Nguyễn Tiến Sơn — MSSV 24110054; Trần Thị Ngọc Quyên — MSSV 24110051.**

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng.
**Ngày kiểm chứng:** 19/10/2026. **Phạm vi:** thực hiện các yêu cầu bổ sung sau khi báo cáo Tuần 3 được duyệt, làm đầu vào cho tổng kết Tuần 4.

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

### Phiên bản hoàn thiện hồ sơ Tuần 4

- **`feat(week4): complete final week verification, consolidate CloudFormation infrastructure, and update catalog` — 96bedec:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093).
- **`docs(week4): synchronize final report test count to 34` — e9704bf:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e9704bf645a11bf07a3f360770061c1cc3a8b3a5](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/e9704bf645a11bf07a3f360770061c1cc3a8b3a5).
- **`fix(evidence): preserve Week 4 snapshot bytes across platforms` — 892861e:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/892861ec5129d59a9c772ef20ed6d2ac053d65f5](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/892861ec5129d59a9c772ef20ed6d2ac053d65f5).
