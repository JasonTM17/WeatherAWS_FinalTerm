# Nhật ký thực hiện

| Tuần | Nhật ký | Số giờ đã được nhóm xác nhận |
| --- | --- | --- |
| 1 | [Nhật ký Tuần 1](../tuan_1/docs/WORKLOG.md) · [CSV](../tuan_1/worklog.csv) | Nguyễn Tiến Sơn: 9,5 giờ; Trần Thị Ngọc Quyên: 9,0 giờ; tổng 18,5 giờ |
| 2 | [Nhật ký Tuần 2](../tuan_2/docs/WORKLOG.md) · [CSV](../tuan_2/worklog.csv) | Nguyễn Tiến Sơn: 10,0 giờ; Trần Thị Ngọc Quyên: 9,5 giờ; tổng 19,5 giờ |
| 3 | [Nhật ký Tuần 3](../tuan_3/docs/WORKLOG.md) · [CSV](../tuan_3/worklog.csv) | Nguyễn Tiến Sơn: 10,0 giờ; Trần Thị Ngọc Quyên: 10,0 giờ; tổng 20,0 giờ |
| 4 | [Nhật ký Tuần 4](../tuan_4/docs/WORKLOG.md) · [CSV](../tuan_4/worklog.csv) | Nguyễn Tiến Sơn: 10,0 giờ; Trần Thị Ngọc Quyên: 10,0 giờ; tổng 20,0 giờ |
| Toàn bộ | [CSV tổng hợp](../worklog.csv) | Tổng cộng 78,0 giờ (Tiến Sơn: 39,5 giờ; Ngọc Quyên: 38,5 giờ) |

Phân công và số giờ được nhóm xác nhận và ghi nhất quán trong từng báo cáo. Tổng thời gian toàn bộ đồ án bốn tuần là 78,0 giờ. Tuần 1 giữ nguyên bộ CSV 156 bản ghi đã nộp. Phân tích bổ sung Tuần 2 dùng hai bộ báo cáo dữ liệu của sinh viên Tiến Sơn và sinh viên Ngọc Quyên. Tuần 3 tích hợp đầy đủ hệ thống, Athena, Dashboard và dự báo. Tuần 4 có bộ hạ tầng CloudFormation, công cụ kiểm thử và mốc đối chiếu trực tiếp ngày 19/10; hồ sơ chi phí, bảo mật và báo cáo tổng kết dẫn tới sản phẩm tương ứng.

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

## Minh chứng bổ sung cho hai hạng mục ưu tiên Tuần 3

| Mốc sản phẩm | Kết quả ghi nhận | Liên kết |
| --- | --- | --- |
| Mã thu thập đã hoàn thiện | Sửa thời điểm thu thập lịch sử và chuyển múi giờ trước phân vùng | [Commit mã 36c9b39](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/36c9b3966a8b6f645dc6bb1491ad6e2b40a78765) |
| Triển khai và gọi trực tiếp | Module của hai Lambda khớp source; bốn lượt gọi thu 12 bản ghi, dữ liệu đối chiếu được bằng Athena; có SNS và xác nhận email | [Kết quả triển khai](deployment-verification.md) |
| Theo dõi lịch tự động | Một lượt mỗi môi trường, tổng sáu bản ghi và bốn thông điệp SNS; người nhận xác nhận email mới | [Kết quả theo lịch](scheduled-run-verification.md) |

Các mốc trên bổ sung minh chứng kỹ thuật; không tự cộng vào 38,0 giờ Tuần 1–2 đã xác nhận. Tổng thời gian Tuần 3 đã xác nhận là 20,0 giờ, gồm 10,0 giờ của sinh viên Tiến Sơn và 10,0 giờ của sinh viên Ngọc Quyên; chi tiết ở mục bên dưới. [Bảng tiến độ W3-01–W3-08](WEEK_3_PLAN.md#tiến-độ-theo-minh-chứng-đã-có) nêu rõ phần đã đạt và phần còn lại.


## Bổ sung tổng giờ Tuần 3

**Đã hoàn thành kế hoạch công việc tích hợp Tuần 3 tại mốc ngày 18/10/2026.** [Bảng sản phẩm W3-01–W3-08 và raw](../tuan_3/docs/WORKLOG.md#5-kết-quả-hoàn-thành-kế-hoạch-công-việc-tích-hợp-tuần-3).

Tổng theo tuần đã xác nhận: 10,0 giờ cho sinh viên Tiến Sơn và 10,0 giờ cho sinh viên Ngọc Quyên, không ghi ngày hoặc phân bổ từng đầu việc. [Nhật ký và căn cứ Tuần 3](../tuan_3/docs/WORKLOG.md), [CSV tổng giờ](../tuan_3/worklog.csv). Các bảng Tuần 1–2 phía trên giữ nguyên tổng 38,0 giờ; cộng thêm 20,0 giờ đã xác nhận của Tuần 3 thành 58,0 giờ.

## Bổ sung giờ công Tuần 4

**Tổng theo tuần đã xác nhận: 20,0 giờ thực tế Tuần 4.** [Bảng sản phẩm W4-01–W4-08 và hồ sơ](../tuan_4/docs/WORKLOG.md).

Tổng theo tuần đã xác nhận Tuần 4: **10,0 giờ cho sinh viên Nguyễn Tiến Sơn** và **10,0 giờ cho sinh viên Trần Thị Ngọc Quyên**.
- [Nhật ký và căn cứ Tuần 4](../tuan_4/docs/WORKLOG.md)
- [CSV tổng giờ Tuần 4](../tuan_4/worklog.csv)
- [Hồ sơ tổng kết Tuần 4](../tuan_4/README.md)
- [Báo cáo chi phí](../tuan_4/docs/COST_REPORT.md)
- [Báo cáo an toàn thông tin](../tuan_4/docs/SECURITY_AUDIT.md)

**Tổng thời gian thực hiện toàn bộ đồ án 4 tuần:** **78,0 giờ** (Tiến Sơn: 39,5 giờ; Ngọc Quyên: 38,5 giờ). [CSV tổng hợp toàn đồ án](../worklog.csv).
