# Cài đặt và vận hành

[Kết quả triển khai và kiểm chứng thực tế](deployment-verification.md) ghi phiên bản Lambda, dữ liệu mới, cảnh báo và trạng thái lịch sau khi triển khai.

[Minh chứng chạy tự động](scheduled-run-verification.md) đối chiếu metric của rule với log Lambda, S3, Athena và SNS, giữ riêng với các lượt gọi trực tiếp khi triển khai.

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

Lambda lưu dữ liệu theo ngày UTC trên S3 nhưng chưa tự đăng ký phân vùng Glue. Khi có ngày mới, cần cập nhật catalog trước khi dùng Athena đọc ngày đó. Điểm vào `python tuan_2/scripts/aws_project.py setup-catalog --region us-east-1` có bước `MSCK REPAIR TABLE`; chọn đúng profile AWS của môi trường cần cập nhật. Sau đó chạy SELECT lọc theo ngày và đối chiếu record_id với đối tượng S3, không dùng số dòng của báo cáo cũ làm kết quả kiểm chứng mới.

Khi cập nhật Lambda đã tồn tại, `deploy-lambda` đặt lại runtime Python 3.12, handler `lambda_function.lambda_handler`, bộ nhớ 256 MB và timeout 60 giây. Các biến môi trường riêng được giữ, còn tên bucket, secret và topic được cập nhật theo dự án.

## Thu hồi tài nguyên

Để kết thúc một buổi thực hành, dùng [checklist xuất minh chứng và tạm dừng/khôi phục lịch](../tuan_4/docs/SESSION_CHECKLIST.md). Chức năng thu hồi toàn dự án bên dưới dành cho khi đã kết thúc sử dụng các tài nguyên và đã xác định phạm vi xóa; không dùng làm thao tác mặc định cuối mỗi buổi.

```powershell
python tuan_2/scripts/aws_project.py cleanup --confirm-account ACCOUNT_ID
python tuan_2/scripts/aws_project.py cleanup --confirm-account ACCOUNT_ID --delete-data
```

Thay `ACCOUNT_ID` bằng account của phiên đăng nhập. Xác nhận account được kiểm tra trước thao tác xóa. Dữ liệu S3 được giữ nếu không chọn `--delete-data`; khi chọn xóa, tag Project của bucket phải khớp dự án. Secret sử dụng cửa sổ phục hồi 7 ngày. Quyền hạn Learner Lab có thể giới hạn một số thao tác; lỗi dịch vụ được trả về thay vì báo thành công giả.

## Đọc minh chứng cho repository

[collect_repository_evidence.py](../tuan_2/scripts/collect_repository_evidence.py) đọc cấu hình Lambda, hash module đang triển khai, lịch/target/policy, S3, Glue, SNS và CloudWatch. Chương trình chạy bảy SELECT đã lưu cho mỗi profile `default` và `quyen`, ghi raw, thống kê và QueryExecutionId vào một thư mục mới. Không truy xuất giá trị Secret, đổi cấu hình hoặc gọi thử Lambda.

```powershell
python -X utf8 tuan_2/scripts/collect_repository_evidence.py --output output/review-moi
python tuan_2/scripts/repository_audit.py --check
```

Đích phải chưa tồn tại. SELECT tạo kết quả thông thường trong S3; không ghi đè CSV lịch sử. Phản hồi SDK được chọn trường trước khi lưu: không đưa email, token hoặc URL tải gói có chữ ký vào repo. `service_checks.csv` ghi API đọc được hay không, không đánh giá hệ thống đã vận hành ổn định. [Đợt đọc ngày 16/10](../tuan_2/results/review_2026_10_16/README.md) cho biết giới hạn thực tế.

Danh mục [csv_catalog.csv](csv_catalog.csv) được tạo từ các CSV công khai. Sau khi bổ sung dữ liệu có chủ đích, chạy `python tuan_2/scripts/repository_audit.py --write`, kiểm tra diff rồi chạy lại `--check`. `.gitattributes` giữ nguyên bytes CSV giữa các nền tảng để hash không đổi do xuống dòng.

## Các kiểm tra chức năng nền tảng

Bộ kiểm tra chức năng bao phủ Lambda, CSV, biểu đồ và SDK. Các ca kiểm tra ghép chuỗi khác thứ tự, thu thập lỗi toàn bộ hoặc một phần, khối phản hồi API bị thiếu, thời gian chờ khi API chậm, phân trang có trang đầu chỉ chứa header và chọn cùng cơ sở dữ liệu trong ngữ cảnh lẫn năm truy vấn xuất CSV. Các hồi quy kiểm tra cấu hình Lambda khi cập nhật, bảo toàn CSV cũ khi kết quả sai cấu trúc, CSV rỗng dữ liệu có header và việc import chương trình biểu đồ. Hai ca bổ sung xác nhận `collected_at` của dữ liệu lịch sử là thời điểm thu thập thực tế và timestamp có offset được chuyển về UTC trước khi xác định ngày phân vùng. Kết quả này không phải bằng chứng của một lần triển khai phiên bản mới trên AWS.

Kiểm tra hồ sơ bổ sung trong [test_repository_evidence.py](../tuan_2/tests/test_repository_evidence.py) bao phủ raw/thống kê, cấu trúc CSV, tiếng Việt/xuống dòng, không ghi đè snapshot và không công bố chi tiết lỗi khi phiên AWS hết hạn. CI [Verify repository](../.github/workflows/verify-repository.yml) chạy catalog/worklog, các ca chức năng/hồ sơ và 18 ca phân tích trên Python 3.12; trạng thái từng lần chạy xem tại GitHub Actions.

Các kiểm tra Lambda bao gồm ba hồi quy về số không hữu hạn trong chuẩn hóa và phân loại AQI. Bộ phân tích có thêm 18 ca kiểm tra phạm vi mẫu, cặp quan trắc khi thiếu dữ liệu, phép làm tròn và các giá trị dùng để vẽ. Xem [hướng dẫn đọc mã nguồn](source-guide.md).
