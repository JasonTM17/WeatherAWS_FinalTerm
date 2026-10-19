# Kiểm chứng trực tiếp ngày 19/10/2026

- [Báo cáo và bảng đối chiếu](../../docs/VERIFICATION_REPORT.md).
- [Source, schedule, storage, log/metric và chi phí hai môi trường](environment/summary.json).
- [Một lượt realtime và SELECT chính xác — sinh viên Tiến Sơn](e2e/default/).
- [Một lượt realtime và SELECT chính xác — sinh viên Ngọc Quyên](e2e/quyen/).
- [Chu kỳ kiểm chứng sinh viên Tiến Sơn](controlled/default.json), [sinh viên Ngọc Quyên](controlled/quyen.json): mỗi chu kỳ 1 Invocation, 0 Errors, 3 dòng raw, 1 Publish được SNS chấp nhận.
- [Bản dựng source/template](build.json), [kiểm tra cục bộ](local_checks.json), [manifest SHA-256](manifest.json).

Raw là các byte JSON tải lại từ S3. CSV và SELECT giữ record_id của lượt mới; không dùng dữ liệu cũ làm lượt kiểm chứng mới. Bộ đếm ở chu kỳ khác giữ nguyên trong bảng kỹ thuật. Xác nhận email của lượt mới được lưu riêng khi người nhận xác nhận. Không triển khai stack mới hoặc tạm dừng lịch trong đợt đọc này.
