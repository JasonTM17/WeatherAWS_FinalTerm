# Checklist đầu và cuối phiên AWS Learner Lab

## Trước khi thực hành

1. Start Lab, đợi phiên hoạt động và kiểm tra vùng `us-east-1`.
2. Cập nhật khóa phiên vào profile đúng trên máy; giữ tệp đăng nhập ngoài repository.
3. Kiểm tra source triển khai, rule, target, bucket và đầu ra hiện có bằng `verify_environment.py`.
4. Nếu phiên trước đã tạm dừng bằng công cụ bên dưới, khôi phục từ **đúng state file của phiên đó**. Không tự bật lịch phụ `WeatherCollectionHourlyRule`.
5. Ghi ngày, công việc và sản phẩm thực tế vào nhật ký. Số giờ do từng sinh viên xác nhận.

## Cuối phiên — thứ tự thực hiện

| Bước | Thao tác | Minh chứng cần giữ |
| --- | --- | --- |
| 1 | Chờ lượt Lambda/SELECT đang thực hiện kết thúc; kiểm tra lịch sử thực thi | Trạng thái kết thúc, request/query ID đã xử lý thông tin riêng tư |
| 2 | Xuất raw, danh mục object/hash, log và metric trong cùng cửa sổ | CSV/JSON và manifest trong thư mục đầu ra mới |
| 3 | Xuất Cost Explorer đúng kỳ, service/record type và Estimated | Giữ giá trị gốc; mức dự kiến đặt riêng với số AWS trả về |
| 4 | Xem trước và tạm dừng lịch thu thập của đúng môi trường | State file riêng trong `output/`, đọc lại trạng thái DISABLED |
| 5 | Kiểm tra các thử nghiệm riêng còn hoạt động | Dừng SELECT chưa cần, tắt rule thử nghiệm; chỉ xem xét xóa stack riêng sau khi đã lưu sản phẩm |
| 6 | End Lab trên trang Learner Lab | Kết thúc phiên theo hướng dẫn lớp; phiên sau kiểm tra lại tài nguyên trước khi bật lịch |

Tạm dừng lịch ngăn sự kiện mới từ rule đó; không hủy lượt Lambda đã bắt đầu, sự kiện retry đã xếp hàng hoặc các cách gọi khác. S3, Secret và log còn lưu vẫn có thể phát sinh chi phí lưu trữ. **End Lab không thay cho kiểm tra tài nguyên và xuất minh chứng.**

## Công cụ tạm dừng và khôi phục

Trước khi dùng, đóng các thao tác chỉnh sửa rule ở phiên Console khác. Công cụ kiểm tra account, tên hàm, một target và lịch một giờ; lưu dấu vân tay cấu hình để tránh khôi phục sang môi trường khác. Chương trình không có thao tác xóa tài nguyên.

```powershell
python tuan_4/scripts/session_control.py preview --profile default
python tuan_4/scripts/session_control.py pause --profile default --state-file output/week4_session_control/son-phien-01.json
```

Lệnh thứ hai **chỉ xem trước**, chưa đổi lịch. Khi kết thúc phiên và đã lưu dữ liệu:

```powershell
python tuan_4/scripts/session_control.py pause --profile default --state-file output/week4_session_control/son-phien-01.json --apply
```

Đầu phiên kế tiếp:

```powershell
python tuan_4/scripts/session_control.py restore --profile default --state-file output/week4_session_control/son-phien-01.json
python tuan_4/scripts/session_control.py restore --profile default --state-file output/week4_session_control/son-phien-01.json --apply
```

Sinh viên Ngọc Quyên dùng `--profile quyen` và state file khác. Lịch vốn DISABLED sẽ không bị tự bật khi restore. Không dùng lại state file đã RESTORED; mỗi lần pause có một tệp mới. Nếu SDK mất phản hồi, kiểm tra trạng thái rule trước khi thử lại; state PREPARED vẫn dùng được để khôi phục sau khi xác nhận rule đang DISABLED và binding không đổi.

Công cụ này dành cho `WeatherCollectionSchedule` hiện hữu. Với stack CloudFormation mới, dùng rule `weather-w4-<môi trường>-hourly` và quy trình Console trong [hướng dẫn hạ tầng](INFRASTRUCTURE.md). Các API EventBridge không có khóa phiên bản để ngăn hoàn toàn chỉnh sửa đồng thời; không để hai người sửa cùng rule trong lúc pause/restore.

## Xem xét xóa thử nghiệm sau cùng

- Chỉ chọn stack/đầu ra thử nghiệm có tên, tag và người sở hữu đã xác định; xem lại **Resources** trước khi xóa.
- Giữ bucket raw, Secret và log theo chính sách Retain của template; kiểm kê chúng riêng sau khi xóa stack.
- Giữ nguồn và minh chứng nộp thầy. Không dùng chức năng thu hồi toàn dự án làm thao tác cuối mỗi buổi.
- Đối với dữ liệu/bucket muốn xóa vĩnh viễn, lập danh sách đối tượng cụ thể và xác nhận phạm vi trước khi thực hiện.

[Hồ sơ Tuần 4](../README.md) · [Video demo](DEMO_GUIDE.md)
