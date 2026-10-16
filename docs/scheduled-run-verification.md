# Kiểm chứng lượt chạy tự động sau triển khai

## Phạm vi và phương pháp

Ngày 16/10/2026, một lượt chạy thực tế của `WeatherCollectionSchedule` được theo dõi trong từng môi trường của sinh viên Tiến Sơn và sinh viên Ngọc Quyên. Lịch giữ nguyên `rate(1 hour)`; đợt theo dõi này không gọi Lambda trực tiếp, không tạo sự kiện thử và không thay đổi source hoặc ngưỡng cảnh báo.

Mã đang chạy là phiên bản đã triển khai tại commit [`36c9b39`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/36c9b3966a8b6f645dc6bb1491ad6e2b40a78765), được kiểm tra lại bằng hash gói trên AWS. [Minh chứng JSON](../tuan_2/results/scheduled_verification_2026_10_16/verification.json) lưu request_id, metric của rule, log REPORT, các bản ghi mới, hash đối tượng S3, MessageId SNS và kết quả truy vấn Athena.

Nguồn kích hoạt được đối chiếu bằng metric `TriggeredRules` và `Invocations` của đúng rule, target Lambda, log START/REPORT và kết quả xử lý trong cùng cửa sổ thời gian. Các request_id của lượt gọi trực tiếp trước đó được loại khỏi phép đối chiếu. Log ứng dụng chưa lưu nguyên vẹn payload sự kiện EventBridge; đây là minh chứng tương quan giữa các dịch vụ, không phải bản ghi payload sự kiện.

## Thời điểm và kết quả thu thập

Các thời điểm dưới đây dùng giờ Việt Nam (UTC+7).

| Nội dung | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Phút ghi nhận metric rule | 15:15 | 14:50 |
| Lambda START | 15:15:44 | 14:51:02 |
| Lambda kết thúc | 15:15:45 | 14:51:05 |
| TriggeredRules / Invocations của rule | 1 / 1 | 1 / 1 |
| Kết quả thu thập | complete, đủ ba đô thị | complete, đủ ba đô thị |
| Bản ghi / đối tượng S3 | 3 / 1 | 3 / 1 |
| Athena đối chiếu record_id mới | Khớp 3/3 | Khớp 3/3 |
| Thời gian Lambda theo REPORT | 1.911,98 ms | 2.953,22 ms |

Metric được tổng hợp theo phút, còn log có timestamp chi tiết hơn. Vì vậy, phép đối chiếu xét phút chứa START hoặc phút ngay trước đó; không lấy chênh lệch giữa mốc phút và START làm độ trễ giao sự kiện chính xác. [Tài liệu AWS về giám sát EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-monitoring.html) mô tả độ phân giải và tính chất best effort của metric.

Hai đối tượng S3 được đọc lại để kiểm tra số dòng, 23 trường, đủ TP. Hồ Chí Minh/Hà Nội/Đà Nẵng, thời gian UTC/UTC+7, `collected_at`, ngày phân vùng và mã hóa AES256. Hai SELECT chỉ lọc các record_id của lượt tự động, xác nhận đô thị, timestamp, AQI và PM2.5 khớp với S3. Các phân vùng ngày 16/10 đã được đăng ký ở đợt triển khai trước; đợt này không sửa catalog hoặc dữ liệu nguồn.

## Cảnh báo và giám sát

Trong cả hai lượt tự động, các bản ghi TP. Hồ Chí Minh và Hà Nội đi qua nhánh cảnh báo của mã đang triển khai. Mỗi lượt có hai dòng cảnh báo vượt ngưỡng và hai SNS MessageId thành công. Đà Nẵng không phát cảnh báo trong các mẫu này.

| Metric trong cửa sổ của lượt chạy | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | ---: | ---: |
| Lambda Invocations | 1 | 1 |
| Lambda Errors / Throttles | 0 / 0 | 0 / 0 |
| SNS NumberOfMessagesPublished | 2 | 2 |
| SNS NumberOfNotificationsDelivered | 2 | 4 |
| SNS NumberOfNotificationsFailed | 0 | 0 |

Topic của sinh viên Tiến Sơn có một đăng ký đã xác nhận; topic của sinh viên Ngọc Quyên có hai đăng ký, nên số lượt giao thông báo khác nhau. Người nhận đã xác nhận cả hai bên nhận email mới của các lượt tự động khoảng 14:51 và 15:15. Xác nhận này được ghi riêng với metric giao thông báo; không coi metric là bằng chứng email đã được đọc.

`FailedInvocations` của rule không trả về datapoint trong cửa sổ đối chiếu; không diễn giải dữ liệu vắng mặt thành một phép đo bằng 0. Kết luận thành công dựa trên các điểm kích hoạt/gọi target có giá trị dương cùng log Lambda hoàn tất, S3, Athena và SNS. Số 0 ở bảng trên là datapoint thực đọc được của Lambda/SNS.

## Kết luận và phạm vi áp dụng

Đã kiểm chứng một lượt chạy theo lịch sau triển khai trên mỗi môi trường: EventBridge → Lambda → API → S3, dữ liệu truy vấn được bằng Athena, cảnh báo SNS có số liệu giao thông báo và xác nhận từ người nhận. Hai lượt tạo sáu bản ghi mới và bốn thông điệp SNS. Các CSV, biểu đồ và bản báo cáo đã lưu giữ nguyên nguồn số liệu.

Kết quả này bổ sung cho [đợt triển khai và gọi trực tiếp](deployment-verification.md). Nó xác nhận hai lượt thực tế trong các cửa sổ nêu trên; chưa dùng để kết luận hệ thống ổn định nhiều ngày. Khi xuất hiện ngày dữ liệu mới, vẫn cần cập nhật phân vùng Glue theo [hướng dẫn vận hành](operation.md).
