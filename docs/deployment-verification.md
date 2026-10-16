# Triển khai Lambda và kiểm chứng luồng dữ liệu

## Phạm vi thực hiện

Ngày 16/10/2026, mã thu thập tại commit [`36c9b39`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/36c9b3966a8b6f645dc6bb1491ad6e2b40a78765) được triển khai lên `WeatherCollectorLambda` trong hai môi trường thực hành của sinh viên Tiến Sơn và sinh viên Ngọc Quyên, vùng `us-east-1`. Đợt này cập nhật mã hàm, chạy thu thập thực tế và kiểm chứng cảnh báo qua SNS. Các CSV, biểu đồ và bản báo cáo đã lưu của Tuần 1–2 giữ nguyên số liệu.

[Minh chứng có cấu trúc](../tuan_2/results/deployment_2026_10_16/verification.json) lưu hash module, trạng thái triển khai, mã thực thi, số dòng, hash đối tượng S3, kết quả Athena và số liệu giám sát. Gói Lambda cũ được sao lưu cục bộ trước khi cập nhật; gói sao lưu, thông tin đăng nhập, địa chỉ email và URL tải mã có chữ ký không đưa vào repository.

## Phiên bản được triển khai

| Nội dung | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Mã nguồn | Commit `36c9b39` | Commit `36c9b39` |
| Module tải lại từ AWS | Khớp source của commit | Khớp source của commit |
| State / LastUpdateStatus | Active / Successful | Active / Successful |
| Runtime, bộ nhớ, timeout | Python 3.12, 256 MB, 60 giây | Python 3.12, 256 MB, 60 giây |
| Cấu hình hàm sau cập nhật mã | Giữ nguyên | Giữ nguyên |

SHA-256 của `lambda_function.py` được tải lại từ cả hai Lambda là `d9d0ad2584feef121234d634bf26bdc43097bb9b8798123cfd767023397ed3cf`. Việc đối chiếu thực hiện trên nội dung module giải nén, bên cạnh hash gói triển khai. Kết quả xác nhận mã trên AWS đã đồng bộ với phiên bản source nêu trên.

## Thu thập, lưu trữ và truy vấn

Mỗi môi trường được gọi trực tiếp một lần ở chế độ hiện tại và một lần với `backfill_hours=1`. Dữ liệu lấy từ API thực tế; không chèn chỉ số ô nhiễm giả hoặc thay ngưỡng để tạo cảnh báo.

| Lượt kiểm chứng | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Thu thập hiện tại | 3 bản ghi, đủ ba đô thị, complete | 3 bản ghi, đủ ba đô thị, complete |
| Nạp một giờ lịch sử | 3 bản ghi, đủ ba đô thị, complete | 3 bản ghi, đủ ba đô thị, complete |
| Đối tượng S3 của hai lượt | 2 đối tượng, 6 bản ghi | 2 đối tượng, 6 bản ghi |
| Athena đối chiếu các record_id mới | SUCCEEDED, khớp 6/6 dòng | SUCCEEDED, khớp 6/6 dòng |

Từng đối tượng S3 được đọc lại để kiểm tra số dòng, 23 trường dữ liệu, đủ ba đô thị, quan hệ UTC/UTC+7 và ngày/giờ phân vùng. Ở lượt lịch sử, thời điểm dữ liệu thuộc ngày 15/10 còn `collected_at` ghi thời điểm thu thập thực tế ngày 16/10. Điều này kiểm chứng việc tách thời điểm quan trắc và thu thập trong mã mới. Kiểm tra thời gian dùng mốc ghi do S3 trả về vì đồng hồ máy gọi và AWS có chênh lệch vài giây.

Hai phân vùng ngày 15/10 và 16/10 chưa có trong Glue được bổ sung theo đúng đường dẫn S3 hiện hữu của từng môi trường. Sau đó, hai SELECT chỉ lọc các record_id vừa tạo xác nhận dữ liệu Athena khớp S3 về đô thị, thời gian, AQI và PM2.5. Không thay lược đồ hoặc sửa dữ liệu gốc. Lambda chưa tự đăng ký phân vùng Glue; khi xuất hiện ngày mới, cần cập nhật catalog trước khi truy vấn ngày đó, theo [hướng dẫn vận hành](operation.md).

## Cảnh báo và email

Trong lượt thu thập hiện tại, các bản ghi TP. Hồ Chí Minh và Hà Nội thỏa ngưỡng cấu hình. Mỗi Lambda ghi nhận hai lần SNS Publish thành công cùng MessageId. Lượt nạp lịch sử không gửi cảnh báo theo thiết kế hiện tại.

| Chỉ số trong cửa sổ kiểm chứng | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | ---: | ---: |
| Lambda Invocations | 2 | 2 |
| Lambda Errors / Throttles | 0 / 0 | 0 / 0 |
| SNS NumberOfMessagesPublished | 2 | 2 |
| SNS NumberOfNotificationsDelivered | 2 | 4 |
| SNS NumberOfNotificationsFailed | 0 | 0 |
| Đăng ký đã xác nhận của topic | 1 | 2 |
| CloudWatch Errors Alarm tại lần đọc cuối | OK | OK |

Số lần giao thông báo khác nhau vì topic của sinh viên Ngọc Quyên có hai đăng ký đã xác nhận. Metric `Delivered` là số lượt giao theo dịch vụ, không phải số email được đọc. Người nhận đã xác nhận qua trao đổi rằng cả hai bên nhận được email mới có tiêu đề `[AWS ALERT]`; đây là xác nhận từ người nhận, không phải kiểm tra trực tiếp hộp thư bởi chương trình. Log REPORT được tìm thấy cho cả bốn lượt gọi; thời gian chạy khoảng 1,6–2,9 giây và bộ nhớ sử dụng tối đa 101–102 MB trong các lượt này.

## Lịch thu thập và giới hạn kết luận

Sinh viên Tiến Sơn có một lịch `WeatherCollectionSchedule` đang bật với `rate(1 hour)`. Môi trường sinh viên Ngọc Quyên ban đầu có hai lịch một giờ cùng gọi một Lambda; sau khi được xác nhận, lịch `WeatherCollectionHourlyRule` được tắt, giữ `WeatherCollectionSchedule` đang bật. Target và quyền gọi hàm của các lịch được giữ nguyên. Mỗi môi trường còn một lịch hoạt động phù hợp với thiết kế.

Đợt triển khai ban đầu xác nhận bốn lượt gọi trực tiếp, API → Lambda → S3 → Athena và cảnh báo SNS kèm xác nhận nhận thư. Các metric và Alarm nêu trên thuộc cửa sổ kiểm chứng này, không chứng minh hệ thống vận hành ổn định nhiều ngày. [Snapshot trước triển khai](../tuan_2/results/review_2026_10_16/README.md) được giữ nguyên để phân biệt hai mốc.

Trong đợt theo dõi tiếp theo, đã đối chiếu được một lượt tự động sau triển khai ở mỗi môi trường, tạo thêm ba bản ghi và hai thông điệp SNS mỗi lượt. Người nhận xác nhận email mới của các lượt theo lịch. Thời điểm rule, request_id Lambda, S3, Athena và metric riêng của các lượt này nằm trong [minh chứng chạy tự động](scheduled-run-verification.md).
