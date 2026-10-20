# Bản xuất Cost Explorer ngày 20/10/2026

Chi phí đang hiển thị trên web theo xác nhận của sinh viên: **Tiến Sơn 0,25 USD; Ngọc Quyên 0,22 USD**. Nguồn hiện tại là [confirmed_cost_summary.json](../cost/confirmed_cost_summary.json).

Thư mục này giữ riêng kết quả truy vấn API để đối chiếu lịch sử. Kỳ yêu cầu: Start inclusive `2026-10-12`, End exclusive `2026-10-21` (UTC); ngày 20/10 chưa kết thúc. Truy vấn lúc 08:34 UTC / 15:34 UTC+7.

- Ngọc Quyên: PASS, 54 nhóm, toàn bộ Estimated=True; profile khớp cấu hình collector hiện hữu.
- Tiến Sơn: BLOCKED_CAPABILITY, AccessDeniedException khi đọc Cost Explorer; cả truy vấn kỳ cũ cũng bị từ chối.

[CSV](learner_lab_cost_breakdown.csv) chỉ chứa nhóm tải thành công. [Tổng API](cost_summary.json), [nguồn và thời điểm](environment/), [SHA-256](manifest.json) giữ đúng kết quả lần tải; không thay bằng số xác nhận mới. [Bản lịch sử trước đó](../cost/cost_summary.json) cũng được giữ nguyên. Các bản API không phân bổ riêng theo đồ án hoặc stack.
