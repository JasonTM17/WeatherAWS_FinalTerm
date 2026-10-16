# Nhật ký công việc Tuần 1

Lớp 261CLCO332779_05 — Điện toán đám mây.

| Thành viên | Phụ trách chính | Phần phối hợp | Tổng giờ Tuần 1 |
| --- | --- | --- | ---: |
| Nguyễn Tiến Sơn — 24110054 | S3, Secrets Manager, Lambda và SNS | Kiến trúc, tích hợp, đối chiếu và báo cáo | 9,5 |
| Trần Thị Ngọc Quyên — 24110051 | Glue, Athena, biểu đồ và đối chiếu dữ liệu | Kiến trúc, tích hợp, đối chiếu và báo cáo | 9,0 |

**Tổng thời gian của nhóm: 18,5 giờ.** Số giờ và phân công do nhóm xác nhận; Bảng 2.1 và mục 2.1 trong báo cáo dùng cùng thông tin này.

## Sản phẩm và nguồn đối chiếu

- [Báo cáo Word](Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.docx) và [PDF](Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.pdf): kiến trúc, nền tảng và số liệu phân tích Tuần 1.
- [Nhật ký CSV Tuần 1](../worklog.csv): tổng giờ theo sinh viên, kèm phân công và đường dẫn sản phẩm; chưa phân bổ giờ theo ngày hoặc từng đầu việc.
- [Kiến trúc hệ thống](../../docs/architecture.md): luồng dữ liệu và vai trò dịch vụ.
- [CSV Athena đã lưu](../../tuan_2/results/athena_queries/): 156 bản ghi, 52 mẫu mỗi đô thị; các phép tổng hợp và chỉ số truy vấn.
- [Hồ sơ vận hành đã lưu](../../docs/saved-evidence.md): kết quả dịch vụ và mã truy vấn dùng đối chiếu.

## Các đầu việc đã ghi nhận

| Đầu việc | Người phụ trách | Sản phẩm kiểm chứng |
| --- | --- | --- |
| Thiết kế luồng và cách lưu dữ liệu ba đô thị | Cả hai sinh viên | [Kiến trúc](../../docs/architecture.md) |
| Nền tảng S3 và cấu hình Secrets Manager | Sinh viên Tiến Sơn | [S3](../scripts/01_setup_s3.ps1) · [Cấu hình](../scripts/02_setup_secrets.ps1) |
| Lược đồ Glue và truy vấn Athena | Sinh viên Ngọc Quyên | [DDL](../../tuan_2/athena/create_table.sql) · [SQL](../../tuan_2/athena/README.md) |
| Phân tích 156 bản ghi và biểu đồ | Sinh viên Ngọc Quyên, cả hai đối chiếu | [Sáu CSV](Bao_cao_tuan_1_CSV_24110054_24110051/) · [Chín hình](../../tuan_2/results/charts/) |
| Tổng hợp kết quả Tuần 1 | Cả hai sinh viên | [Báo cáo trên GitHub](FINAL_REPORT.md) |

Mã triển khai dùng chung ở `tuan_2/` có thể đã được chỉnh sửa sau Tuần 1; số liệu Tuần 1 tiếp tục lấy từ bộ CSV đã lưu. Số giờ là tổng theo tuần đã xác nhận, không tự chia thành các buổi làm khi chưa có nhật ký buổi.
