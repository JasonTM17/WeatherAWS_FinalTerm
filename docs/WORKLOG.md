# Nhật ký thực hiện

| Tuần | Nhật ký | Số giờ đã được nhóm xác nhận |
| --- | --- | --- |
| 1 | [Nhật ký Tuần 1](../tuan_1/docs/WORKLOG.md) · [CSV](../tuan_1/worklog.csv) | Nguyễn Tiến Sơn: 9,5 giờ; Trần Thị Ngọc Quyên: 9,0 giờ; tổng 18,5 giờ |
| 2 | [Nhật ký Tuần 2](../tuan_2/docs/WORKLOG.md) · [CSV](../tuan_2/worklog.csv) | Nguyễn Tiến Sơn: 10,0 giờ; Trần Thị Ngọc Quyên: 9,5 giờ; tổng 19,5 giờ |
| Toàn bộ | [CSV tổng hợp](../worklog.csv) | Tổng cộng 38,0 giờ (Tiến Sơn: 19,5 giờ; Ngọc Quyên: 18,5 giờ) |

Phân công và số giờ được nhóm xác nhận và ghi nhất quán trong từng báo cáo. Tổng thời gian hai tuần là 38,0 giờ. Tuần 1 giữ nguyên bộ CSV 156 bản ghi đã nộp. Phân tích bổ sung Tuần 2 dùng hai bộ báo cáo dữ liệu của sinh viên Tiến Sơn và sinh viên Ngọc Quyên: 204/231 bản ghi toàn bộ, trong đó 27/57 thuộc Tuần 2. Các quan trắc cùng đô thị và thời điểm được đối chiếu; thống kê giữ riêng theo bộ dữ liệu của từng sinh viên.

[Minh chứng vận hành đã lưu](saved-evidence.md) tổng hợp phản hồi Lambda và năm mã truy vấn đã đối chiếu với CSV.

## Cách ghi thời gian

Số giờ là tổng theo tuần đã được hai sinh viên xác nhận. CSV giữ một dòng cho mỗi sinh viên trong mỗi tuần, dùng dấu chấm cho phần thập phân và UTF-8 để giữ đúng tiếng Việt. Chưa có nhật ký thời điểm bắt đầu/kết thúc từng buổi, nên các tổng này không được chia thành ngày hoặc đầu việc có số giờ giả định. Đợt đối chiếu bổ sung không tự làm tăng giờ đã xác nhận.

## Trách nhiệm và minh chứng

| Sinh viên | Công việc chính | Sản phẩm kiểm chứng |
| --- | --- | --- |
| Sinh viên Tiến Sơn | S3, Secrets Manager, Lambda và SNS; phối hợp lịch và giám sát | [Lambda](../tuan_2/lambda/lambda_function.py) · [SDK quản lý dịch vụ](../tuan_2/scripts/aws_project.py) · [Hồ sơ AWS](../tuan_2/results/week2_evidence/) |
| Sinh viên Ngọc Quyên | Glue, Athena, xuất CSV, phân tích AQI, biểu đồ và đối chiếu dữ liệu | [SQL](../tuan_2/athena/README.md) · [Exporter](../tuan_2/scripts/athena_export.py) · [Phân tích](../tuan_2/analytics/analyze_week2_accounts.py) · [Kết quả](../tuan_2/results/week2_analysis/) |
| Cả hai sinh viên | Kiến trúc, tích hợp, giải thích số liệu và hoàn thiện hồ sơ | [Kiến trúc](architecture.md) · [Tuần 1](../tuan_1/README.md) · [Tuần 2](../tuan_2/README.md) |

Lịch sử Git ghi nhận các lần cập nhật sản phẩm; tên người commit không thay thế phân công hoặc nhật ký thời gian của từng sinh viên.

[Đợt kiểm chứng mới](../tuan_2/results/review_2026_10_16/README.md) giữ riêng số liệu được tải lại. Không cộng hai lần những quan trắc đã có trong bộ cũ.

[Mã nguồn và commit](components.md) · [Kế hoạch Tuần 3](WEEK_3_PLAN.md) · [Danh mục CSV](csv_catalog.csv)
