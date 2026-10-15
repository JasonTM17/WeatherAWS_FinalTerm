# Cài đặt và vận hành

Chạy từ thư mục gốc repository với Python 3.12 trở lên.

[tuan_2/analytics/requirements.txt](../tuan_2/analytics/requirements.txt) cài boto3, NumPy và Matplotlib cho SDK, phân tích và biểu đồ. Tệp phụ thuộc trong `tuan_2/lambda/` mô tả phạm vi phát triển Lambda. Xem [sơ đồ mã nguồn](repository-layout.md).

```powershell
python -m pip install -r tuan_2/analytics/requirements.txt
python tuan_2/scripts/athena_export.py --offline --output output/csv
python tuan_2/analytics/generate_charts.py
python -m unittest discover -s tuan_2/tests -v
```

## Phiên AWS

Boto3 dùng thông tin đăng nhập từ biến môi trường `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` hoặc shared credentials. Phiên Learner Lab phải còn hiệu lực. Không ghi khóa vào mã nguồn, commit hoặc báo cáo. Vùng mặc định là `us-east-1`; các lệnh dưới dùng `--region` để thay đổi khi cần.

## Triển khai và kiểm tra trạng thái

```powershell
python tuan_2/scripts/aws_project.py deploy --region us-east-1
python tuan_2/scripts/aws_project.py verify --region us-east-1
python tuan_2/scripts/athena_export.py --region us-east-1 --output output/athena
```

Tùy chọn `--email` của `deploy` hoặc `setup-sns` đăng ký địa chỉ nhận thông báo; người nhận cần xác nhận. Các chương trình PowerShell trong `tuan_1/scripts` và `tuan_2/scripts` chuyển tham số tới chương trình Python; tùy chọn `-Python` chọn đường dẫn Python khi máy có nhiều phiên bản.

Thư mục `output/` được Git bỏ qua để lưu các lượt xuất tùy chọn. Luôn chỉ định `--output` khi cần giữ riêng kết quả mới; các mặc định tương thích vẫn trỏ tới thư mục kết quả trong `tuan_2/`. Không dùng thư mục dữ liệu đã nộp làm đích xuất mới.

`verify` đọc trạng thái Lambda, lịch, S3 và bảng Glue; không tự kích hoạt thu thập. Chức năng Lambda xử lý hiện tại theo sự kiện mặc định; sự kiện có `backfill_hours` yêu cầu nạp bù lịch sử.

Khi cập nhật Lambda đã tồn tại, `deploy-lambda` đặt lại runtime Python 3.12, handler `lambda_function.lambda_handler`, bộ nhớ 256 MB và timeout 60 giây. Các biến môi trường riêng được giữ, còn tên bucket, secret và topic được cập nhật theo dự án.

## Thu hồi tài nguyên

```powershell
python tuan_2/scripts/aws_project.py cleanup --confirm-account ACCOUNT_ID
python tuan_2/scripts/aws_project.py cleanup --confirm-account ACCOUNT_ID --delete-data
```

Thay `ACCOUNT_ID` bằng account của phiên đăng nhập. Xác nhận account được kiểm tra trước thao tác xóa. Dữ liệu S3 được giữ nếu không chọn `--delete-data`; khi chọn xóa, tag Project của bucket phải khớp dự án. Secret sử dụng cửa sổ phục hồi 7 ngày. Quyền hạn Learner Lab có thể giới hạn một số thao tác; lỗi dịch vụ được trả về thay vì báo thành công giả.

## Kiểm tra đã thực hiện

Bộ kiểm tra cục bộ gồm 56 ca: Lambda 22, CSV 12, biểu đồ 5 và SDK 17. Các ca kiểm tra ghép chuỗi khác thứ tự, thu thập lỗi toàn bộ hoặc một phần, khối phản hồi API bị thiếu, thời gian chờ khi API chậm, phân trang có trang đầu chỉ chứa header và chọn cùng cơ sở dữ liệu trong ngữ cảnh lẫn năm truy vấn xuất CSV. Các hồi quy mới kiểm tra cấu hình Lambda khi cập nhật, bảo toàn CSV cũ khi kết quả sai cấu trúc, CSV rỗng dữ liệu có header và việc import chương trình biểu đồ. Kết quả này không phải bằng chứng của một lần triển khai phiên bản mới trên AWS.

Các kiểm tra Lambda bao gồm ba hồi quy về số không hữu hạn trong chuẩn hóa và phân loại AQI. Bộ phân tích có thêm 18 ca kiểm tra phạm vi mẫu, cặp quan trắc khi thiếu dữ liệu, phép làm tròn và các giá trị dùng để vẽ. Xem [hướng dẫn đọc mã nguồn](source-guide.md).
