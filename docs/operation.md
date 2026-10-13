# Cài đặt và vận hành

Chạy từ thư mục gốc repository với Python 3.12 trở lên.

```powershell
python -m pip install -r requirements.txt
python tuan_2/scripts/athena_export.py --offline --output output/csv
python tuan_2/analytics/generate_charts.py
python -m unittest discover -s tuan_2/tests -v
```

## Phiên AWS

Boto3 dùng thông tin đăng nhập từ biến môi trường `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` hoặc shared credentials. Phiên Learner Lab phải còn hiệu lực. Không ghi khóa vào source, commit hoặc báo cáo. Vùng mặc định là `us-east-1`; các lệnh dưới dùng `--region` để thay đổi khi cần.

## Triển khai và kiểm tra trạng thái

```powershell
python tuan_2/scripts/aws_project.py deploy --region us-east-1
python tuan_2/scripts/aws_project.py verify --region us-east-1
python tuan_2/scripts/athena_export.py --region us-east-1 --output output/athena
```

Tùy chọn `--email` của `deploy` hoặc `setup-sns` đăng ký địa chỉ nhận thông báo; người nhận cần xác nhận. Các entry point PowerShell trong `tuan_1/scripts` và `tuan_2/scripts` chuyển tham số tới chương trình Python; tùy chọn `-Python` chọn đường dẫn Python khi máy có nhiều phiên bản.

`verify` đọc trạng thái Lambda, lịch, S3 và bảng Glue; không tự kích hoạt thu thập. Chức năng Lambda xử lý hiện tại theo sự kiện mặc định; sự kiện có `backfill_hours` yêu cầu nạp bù lịch sử.

## Thu hồi tài nguyên

```powershell
python tuan_2/scripts/aws_project.py cleanup --confirm-account ACCOUNT_ID
python tuan_2/scripts/aws_project.py cleanup --confirm-account ACCOUNT_ID --delete-data
```

Thay `ACCOUNT_ID` bằng account của phiên đăng nhập. Xác nhận account được kiểm tra trước thao tác xóa. Dữ liệu S3 được giữ nếu không chọn `--delete-data`; khi chọn xóa, tag Project của bucket phải khớp dự án. Secret sử dụng cửa sổ phục hồi 7 ngày. Quyền hạn Learner Lab có thể giới hạn một số thao tác; lỗi dịch vụ được trả về thay vì báo thành công giả.

## Kiểm tra đã thực hiện

Bộ kiểm tra cục bộ gồm 40 ca: Lambda 12, CSV 12, biểu đồ 4 và SDK 12. Các ca SDK kiểm tra truy vấn lỗi, timeout/cancel, phân trang, giữ CSV nguyên trạng, nguồn ngoại tuyến và điều kiện thu hồi. Kết quả này không phải bằng chứng của một lần triển khai live phiên bản mới.
