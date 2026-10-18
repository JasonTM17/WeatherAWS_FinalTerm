# Truy nguyên điểm Errors = 3 của sinh viên Tiến Sơn

## 1. Phạm vi và dữ liệu nguồn

Đợt đọc AWS bắt đầu **11:31:58 UTC ngày 18/10/2026** (18:31:58 Việt Nam), dùng SDK trong vùng `us-east-1`, hàm `WeatherCollectorLambda`. Cửa sổ metric/log là **07:40 ≤ t < 11:00 UTC**. CloudTrail LookupEvents lọc cùng mốc đầu/cuối theo ngữ nghĩa API của dịch vụ. Đây là điều tra chỉ đọc; không gọi Lambda, ghi metric/log, gửi email thử hay sửa IAM/Lambda/lịch.

- [probe.json](probe.json): các trường AWS đã chọn và loại thông tin riêng; trạng thái từng phép đọc, metric phút, lifecycle log, cấu hình hiện tại và lịch sử quản trị.
- [findings.json](findings.json): trích lại các phút bất thường, giữ `null` cho điểm không được trả về.
- [manifest.json](manifest.json): kích thước và SHA-256 của hai JSON.
- [Chương trình tái hiện](../../scripts/investigate_native_errors.py): gọi API chỉ đọc, không lưu ARN, tài khoản, người gọi, IP, nội dung lỗi đầy đủ hoặc log ứng dụng nguyên văn. Mỗi lần chạy dùng đầu ra mới; dữ liệu AWS có thể được bổ sung sau snapshot này.
- [Đối chiếu hai API/dimension/chu kỳ trước đó](../monitoring_followup_2026_10_18/README.md): giữ nguyên, không thay dữ liệu lịch sử.

## 2. Vì sao tổng năm phút bằng 3?

Các chuỗi sau thuộc `AWS/Lambda`, dimension `FunctionName=WeatherCollectorLambda`, period 60 giây. Errors, Invocations, Throttles, AsyncEventsReceived/Dropped dùng Sum; AsyncEventAge dùng Maximum, đơn vị ms. Duration dùng SampleCount để tìm dấu vết mẫu thời lượng, không dùng giá trị thời lượng để đếm lỗi.

| Phút UTC / Việt Nam | Errors | Invocations | Duration SampleCount | Throttles | AsyncEventsReceived | AsyncEventsDropped | AsyncEventAge max (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 09:15 / 16:15 | 1 | — | — | 0 | 1 | — | 72 |
| 09:16 / 16:16 | 1 | — | — | 0 | — | — | 60.364 |
| 09:18 / 16:18 | 1 | — | — | 0 | — | 1 | 167.598 |

**Dấu “—” là không có điểm trả về, không phải 0.** Ba điểm Errors cộng thành 3 trong khoảng 09:15–09:20 UTC. Như vậy, giá trị 3 không xuất phát từ việc nhân một lỗi trong chương trình tổng hợp.

Các mốc thời gian, tuổi sự kiện tăng và một điểm bỏ sự kiện **phù hợp với nhịp thử lại bất đồng bộ rồi bỏ sự kiện**. AWS mô tả cơ chế mặc định thử lại lỗi hàm thêm hai lần. Tuy nhiên, chuỗi metric tổng hợp không có ID sự kiện/request để nối từng điểm; không dùng sự phù hợp này làm bằng chứng chắc chắn rằng ba lỗi đều thuộc một sự kiện, hoặc tự điền Invocations = 3. [AWS — xử lý lỗi bất đồng bộ](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-error-handling.html), [định nghĩa metric](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics-types.html).

## 3. Log, cấu hình và lịch sử quyền

| Kiểm tra | Quan sát | Giới hạn kết luận |
| --- | --- | --- |
| Đọc trực tiếp log stream | Sáu stream có tiền tố ngày; 16 sự kiện trong cửa sổ. Hai request có START/END/REPORT, hai Result complete ở 08:15 và 10:15; không thấy lifecycle/INIT_REPORT hoặc chữ ký lỗi đã dò ở 09:15–09:18 | Không chứng minh hàm không hề chạy; thông điệp lỗi có thể chưa được ghi/không nằm trong phần quan sát |
| STS AssumeRole | Có bản ghi thành công nhắm đúng execution role và phiên có tên hàm ở 09:15:43, 09:16:43, 09:18:30 UTC | Chỉ chứng minh thao tác nhận vai trò được ghi thành công; không chứng minh mọi quyền runtime, số lần chạy hay kết quả handler |
| Lambda hiện tại | Active, LastUpdateStatus Successful; LastModified 05:50:53 UTC, runtime Python 3.12, timeout 60 s, memory 256 MB; hash gói khớp gói CD đã lưu | Không tìm được ngoại lệ gây lỗi; trạng thái hiện tại không thay thế lịch sử |
| Lịch sử Lambda/EventBridge | LookupEvents trả 10/8 sự kiện tương ứng, tất cả chỉ đọc trong cửa sổ | Không quan sát thấy thao tác cập nhật mã/cấu hình hoặc đổi lịch trong lịch sử đã truy vấn; không khẳng định mọi thay đổi ngoài phạm vi đều bị loại trừ |
| IAM lúc 09:06 | Có CreatePolicyVersion/AttachRolePolicy; policy mới có Deny và điều kiện PrincipalArn/TokenIssueTime | Policy không nằm trong các policy hiện gắn vào execution role; thao tác gắn không nêu execution role. Chưa đủ để quy lỗi Lambda cho thay đổi này |
| AccessDenied lúc 09:23:36 và 09:24:59 | Hai lệnh GetFunctionConfiguration bị từ chối; session issuer khác execution role | Đây là lỗi người gọi API kiểm tra, không phải bằng chứng Lambda runtime bị từ chối quyền |
| Đọc policy hiện tại | Đọc được 4/7 tài liệu policy; 3 tài liệu nhận AccessDenied | Giữ trạng thái không đọc được, không suy các policy này là rỗng hoặc không có Deny |
| Cấu hình bất đồng bộ hiện tại | GetFunctionEventInvokeConfig trả ResourceNotFoundException; không có cấu hình riêng được API này trả về. Function không có DeadLetterConfig; target lịch không có DLQ riêng | Không có failure payload trong hồ sơ này. Không suy cấu hình hiện tại chắc chắn giống thời điểm lỗi |
| CloudTrail | DescribeTrails và ListEventDataStores trả 0 đối tượng nhìn thấy trong phạm vi đọc | LookupEvents chỉ cung cấp lịch sử management events, không thay cho Invoke data events; không chứng minh mọi tài khoản/vùng đều không có trail |

Không quan sát thấy throttling tại ba phút lỗi. Những lần thành công hai bên khoảng lỗi và hash mã hiện tại hỗ trợ nhận định đây là một gián đoạn trong mẫu quan sát; chưa xác định được lỗi nằm ở khởi tạo, runtime, quyền ở bước khác hay việc phát metric/log. [AWS — CloudTrail cho Lambda](https://docs.aws.amazon.com/lambda/latest/dg/logging-using-cloudtrail.html).

## 4. Kết luận và hướng xử lý

**Đã truy được cách hình thành Errors = 3 và dấu vết bỏ sự kiện; nguyên nhân sâu hơn làm thiếu Invocations vẫn chưa đủ bằng chứng để kết luận.** Không có căn cứ thay mã thu thập, mở rộng quyền LabRole, khởi động lại hoặc triển khai lại để sửa một lỗi lịch sử chưa xác định. Không sửa số gốc, không coi khoảng trống là thành công và không tính tỷ lệ lỗi toàn cửa sổ.

Dashboard đã có [bộ kiểm tra cặp và IF phẳng được kiểm chứng trước đó](../monitoring_dashboard_repair_2026_10_18/README.md); đợt này giữ cấu hình đó. Để phân giải ngoại lệ cụ thể nếu tái diễn, cần failure payload hoặc log khởi tạo/runtime, cùng lịch sử quyền đúng execution role tại thời điểm lỗi. Bật OnFailure destination/DLQ cho sự kiện sau này cần cấu hình bổ sung; không thể truy hồi payload đã bỏ chỉ bằng việc bật mới. Có thể chuyển mốc thời gian và dữ liệu native cho quản trị Learner Lab/AWS để kiểm tra phía dịch vụ.

## 5. Tái hiện và kiểm chứng

```bash
python tuan_3/scripts/investigate_native_errors.py --profile default --output output/native-error-new/probe.json
python -m unittest discover -s tuan_3/tests -p test_native_investigation.py -v
python tuan_3/scripts/verify_results.py
```

Bộ kiểm tra tính lại bảng ba phút từ probe đã lưu, đối chiếu manifest, tổng Errors, lifecycle, các sự kiện quản trị và giới hạn kết luận. Đây là kiểm chứng hồ sơ, không tái tạo lỗi trên AWS. Các ARN chỉ được so sánh trong bộ nhớ, không xuất ra hồ sơ công khai.

[Báo cáo kỹ thuật](../../docs/FINAL_REPORT.md) · [Vận hành](../../docs/operation.md)
