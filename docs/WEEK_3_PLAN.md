# Kế hoạch Tuần 3 Tích hợp và giám sát

## Mục tiêu và đầu vào

Hoàn thiện và kiểm chứng luồng EventBridge → Lambda → S3 → Glue/Athena → biểu đồ, đồng thời theo dõi lỗi và cảnh báo SNS. Kế hoạch tiếp nối [Tuần 2](../tuan_2/README.md) và [đợt đọc AWS ngày 16/10](../tuan_2/results/review_2026_10_16/README.md).

Đã có hai Lambda Active, dữ liệu theo phân vùng ngày và CSV truy vấn thành công. Những phần còn cần kiểm chứng gồm mã đang chạy khác mã nguồn hiện tại, hai lịch đang bật ở môi trường sinh viên Ngọc Quyên, Alarm `INSUFFICIENT_DATA` và Errors lớn hơn Invocations. Metadata giữ nguyên những trạng thái này; chúng chưa được coi là đã xử lý.

## Phân công và thứ tự thực hiện

| Mã | Công việc | Phụ trách chính | Sản phẩm dự kiến | Tiêu chí hoàn thành |
| --- | --- | --- | --- | --- |
| W3-01 | Chốt phiên bản mã và cấu hình triển khai | Sinh viên Tiến Sơn | Commit, hash gói/hàm trước và sau triển khai | Xác định được phiên bản thực chạy, có cách khôi phục gói cũ, không công bố thông tin đăng nhập |
| W3-02 | Tích hợp lịch với Lambda | Sinh viên Tiến Sơn | Bảng rule/target/policy và các lượt thực thi liên tiếp | Xác nhận lịch được chọn cho từng môi trường; giải thích và xử lý lịch thừa trước khi đánh giá mật độ mẫu |
| W3-03 | Đối chiếu dữ liệu từ lượt thu thập tới phân vùng | Sinh viên Ngọc Quyên | Raw, danh sách đối tượng, phân vùng và CSV số dòng theo ngày/đô thị | Lần theo được dữ liệu từ thời điểm thu thập đến S3/Athena; giải thích các khoảng không có dữ liệu |
| W3-04 | Kiểm tra chất lượng và thời gian quan trắc | Sinh viên Ngọc Quyên | CSV chất lượng và thống kê theo đô thị–giờ | Phân biệt khóa record_id, UTC/UTC+7, NULL và các lượt cùng giờ; giữ raw đầy đủ |
| W3-05 | Chuẩn hóa giám sát Lambda | Sinh viên Tiến Sơn | CSV CloudWatch và log tổng hợp đã loại thông tin riêng tư | Invocations/Errors dùng cùng namespace, dimensions, khoảng thời gian, period và statistic; giải thích bất nhất trước khi tính tỷ lệ lỗi |
| W3-06 | Kiểm chứng đường cảnh báo SNS | Sinh viên Tiến Sơn | Kết quả ngưỡng, Publish, trạng thái đăng ký và xác nhận nhận thư | Tách rõ vượt ngưỡng, SNS nhận Publish và người nhận đã nhận thư; thử có kiểm soát trong Lab với người nhận đồng ý |
| W3-07 | Cập nhật bảng và biểu đồ giám sát | Sinh viên Ngọc Quyên | CSV mới, biểu đồ có màu và liên kết nguồn | Nhãn cỡ mẫu, đơn vị, mốc quan sát và ngưỡng rõ ràng; đồ thị khớp CSV; không suy ra cả tuần từ mẫu ngắn |
| W3-08 | Rà soát tích hợp và hồ sơ GitHub | Cả hai sinh viên | README Tuần 3, worklog, commit và kết quả kiểm tra | Mở được mã, dữ liệu và commit từng phần; kết quả CI/cục bộ và AWS được ghi riêng |

Hai sinh viên phối hợp đối chiếu ở tất cả đầu việc. W3-01 và W3-02 đi trước W3-03; W3-03 cung cấp đầu vào cho W3-04/W3-07. W3-05 và W3-06 theo dõi cùng phiên bản triển khai. W3-08 tổng hợp sau khi các kết quả được đối chiếu.

## Điều kiện và hồ sơ kết thúc

- Thực hiện trong phiên AWS Learner Lab còn hiệu lực. Lịch bật không chứng minh hệ thống chạy liên tục khi Lab ngừng hoạt động.
- Lưu dữ liệu mới vào thư mục riêng theo mốc; giữ nguyên CSV Tuần 1 và Tuần 2 đã dùng trong báo cáo.
- Trước khi cập nhật hạ tầng, lưu phiên bản/cấu hình cũ để khôi phục. Ghi mọi lần triển khai, đổi lịch và thử thông báo vào nhật ký thực tế.
- Chạy kiểm tra theo [hướng dẫn mã nguồn](source-guide.md), sau đó kiểm tra riêng luồng trên AWS. Kiểm tra giả lập không thay thế dịch vụ thật.
- Chưa ghi giờ hoàn thành Tuần 3. Khi thực hiện, bổ sung số giờ thực tế, commit, CSV, hình giám sát và những việc chưa giải quyết.

Hồ sơ kết thúc ghi kết quả W3-01 đến W3-08, phân công/số giờ, raw và CSV tổng hợp, cấu hình đã loại thông tin riêng tư, commit triển khai và các giới hạn còn lại. Chỉ đánh dấu hoàn thành khi có minh chứng tương ứng.

[Nhật ký hai tuần](WORKLOG.md) · [Mã nguồn theo thành phần](components.md) · [Vận hành](operation.md)
