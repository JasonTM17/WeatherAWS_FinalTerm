# Nhật ký công việc Tuần 2 — Nhóm 05

Lớp 261CLCO332779_05 — Điện toán đám mây.

| Thành viên | Phụ trách chính | Phần phối hợp | Tổng giờ Tuần 2 |
| --- | --- | --- | ---: |
| Nguyễn Tiến Sơn — 24110054 | S3, Secrets Manager, Lambda và SNS | Kiến trúc, tích hợp, đối chiếu và báo cáo | 10,0 |
| Trần Thị Ngọc Quyên — 24110051 | Glue, Athena, biểu đồ và đối chiếu dữ liệu | Kiến trúc, tích hợp, đối chiếu và báo cáo | 9,5 |

**Tổng thời gian của nhóm: 19,5 giờ.** Số giờ và phân công do nhóm xác nhận. Chương 1 và Chương 7 của báo cáo Tuần 2 sử dụng cùng số liệu này.

## Sản phẩm và nguồn đối chiếu

- [Báo cáo Word](Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx) và [PDF](Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.pdf): chức năng, cấu hình, bảng số liệu và phân tích.
- [Mã nguồn Lambda](../lambda/lambda_function.py) và [chương trình quản lý dịch vụ](../scripts/aws_project.py): thu thập, chuẩn hóa, lưu trữ, lịch và cảnh báo.
- [Lược đồ và truy vấn](../athena/): mô hình dữ liệu và phép tổng hợp.
- [Kết quả Athena mới](../results/week2_live/) và [16 biểu đồ](../results/week2_charts/): hai tài khoản được phân tích riêng, 27/57 bản ghi thuộc Tuần 2.
- [Excel Tuần 2](Du_lieu_phan_tich_Tuan_2_Nhom_05.xlsx): bảng nguồn, kết quả và các biểu đồ cùng dữ liệu với báo cáo.
- [Hồ sơ vận hành đã lưu](../../docs/saved-evidence.md): phản hồi Lambda 3 bản ghi, 2 cảnh báo và năm mã truy vấn khớp CSV.

Hồ sơ vận hành đã lưu được phân biệt với các lần sửa mã nguồn sau đó. CSV, Excel và biểu đồ dùng cùng bộ kết quả; chúng không tự xác nhận một lượt chạy mới của phiên bản hiện tại.

Đợt phân tích bổ sung tải đủ 435 dòng nguồn, xác nhận 84 dòng thuộc Tuần 2 qua 24 truy vấn mới. Tệp raw, trạng thái tài nguyên và hash mã đang triển khai được giữ tại [hồ sơ nguồn](../results/week2_evidence/). Số giờ đã xác nhận vẫn là 10,0 và 9,5 giờ; không tự tăng theo thời gian hỗ trợ phân tích bổ sung.
