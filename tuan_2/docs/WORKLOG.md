# Nhật ký công việc Tuần 2

Lớp 261CLCO332779_05 — Điện toán đám mây.

| Thành viên | Phụ trách chính | Phần phối hợp | Tổng giờ Tuần 2 |
| --- | --- | --- | ---: |
| Nguyễn Tiến Sơn — 24110054 | S3, Secrets Manager, Lambda và SNS | Kiến trúc, tích hợp, đối chiếu và báo cáo | 10,0 |
| Trần Thị Ngọc Quyên — 24110051 | Glue, Athena, biểu đồ và đối chiếu dữ liệu | Kiến trúc, tích hợp, đối chiếu và báo cáo | 9,5 |

**Tổng thời gian của nhóm: 19,5 giờ.** Số giờ và phân công do nhóm xác nhận. Mục 1.2 của báo cáo Tuần 2 sử dụng cùng số liệu này.

## Sản phẩm và nguồn đối chiếu

- [Báo cáo Word](Bao_cao_Tuan_2_24110054_24110051.docx) và [PDF](Bao_cao_Tuan_2_24110054_24110051.pdf): chức năng, cấu hình, bảng số liệu và phân tích.
- [Nhật ký CSV Tuần 2](../worklog.csv): tổng giờ theo sinh viên, kèm phân công và đường dẫn sản phẩm; chưa phân bổ giờ theo ngày hoặc từng đầu việc.
- [Mã nguồn Lambda](../lambda/lambda_function.py) và [chương trình quản lý dịch vụ](../scripts/aws_project.py): thu thập, chuẩn hóa, lưu trữ, lịch và cảnh báo.
- [Lược đồ và truy vấn](../athena/): mô hình dữ liệu và phép tổng hợp.
- [Kết quả Athena mới](../results/week2_live/) và [20 biểu đồ](../results/week2_charts/): hai bộ báo cáo dữ liệu được trình bày riêng, 27/57 bản ghi thuộc Tuần 2.
- [Excel Tuần 2](Du_lieu_phan_tich_Tuan_2_24110054_24110051.xlsx): bảng nguồn, kết quả và các biểu đồ cùng dữ liệu với báo cáo.
- [Hồ sơ vận hành đã lưu](../../docs/saved-evidence.md): phản hồi Lambda 3 bản ghi, 2 cảnh báo và năm mã truy vấn khớp CSV.

Hồ sơ vận hành đã lưu được phân biệt với các lần sửa mã nguồn sau đó. CSV, Excel và biểu đồ dùng cùng bộ kết quả; chúng không tự xác nhận một lượt chạy mới của phiên bản hiện tại.

Đợt phân tích bổ sung tải đủ 435 dòng nguồn, xác nhận 84 dòng thuộc Tuần 2 qua 24 truy vấn mới. Tệp raw, trạng thái tài nguyên và hash mã đang triển khai được giữ tại [hồ sơ nguồn](../results/week2_evidence/). Số giờ đã xác nhận vẫn là 10,0 và 9,5 giờ; không tự tăng theo thời gian hỗ trợ phân tích bổ sung.

## Các đầu việc và kết quả

| Đầu việc | Người phụ trách | Sản phẩm và phạm vi xác nhận |
| --- | --- | --- |
| Thu thập, chuẩn hóa và lưu S3 | Sinh viên Tiến Sơn | [Lambda](../lambda/lambda_function.py); [hồ sơ nguồn](../results/week2_evidence/) giữ metadata của phiên bản đã chạy |
| Lịch EventBridge và cảnh báo SNS | Sinh viên Tiến Sơn | [SDK](../scripts/aws_project.py); [metadata mới](../results/review_2026_10_16/README.md) xác nhận lịch, target, policy và đăng ký; chưa xác nhận thư đã được nhận |
| Lược đồ, view và phân tích theo tuần | Sinh viên Ngọc Quyên | [12 truy vấn](../athena/week2_analysis/) và [CSV Athena đã lưu](../results/week2_live/) |
| Xuất CSV, thống kê và đối chiếu raw | Sinh viên Ngọc Quyên | [Exporter](../scripts/athena_export.py), [phân tích](../analytics/analyze_week2_accounts.py), [27 bảng](../results/week2_analysis/) |
| Dựng và đối chiếu biểu đồ | Sinh viên Ngọc Quyên, cả hai đối chiếu | [20 hình và manifest](../results/week2_charts/); mỗi hình có CSV nguồn |
| Tích hợp và hồ sơ tiến độ | Cả hai sinh viên | [Tuần 2](../README.md), [chỉ mục commit](../../docs/components.md), [kế hoạch tiếp theo](../../docs/WEEK_3_PLAN.md) |

Đợt kiểm chứng ngày 16/10 đọc lại AWS bằng phiên mới và chạy thêm 14 SELECT, cho 39/75 lượt ghi thuộc Tuần 2. Đây là bộ bổ sung riêng; hồ sơ 27/57 vẫn giữ nguyên. Công việc và số giờ thực tế của Tuần 3 sẽ được ghi khi thực hiện.
