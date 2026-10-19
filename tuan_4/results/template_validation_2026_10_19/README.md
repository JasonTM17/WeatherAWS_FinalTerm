# Kiểm tra template chính ngày 19/10/2026

Template chính gồm 17 tài nguyên và dùng source Lambda thật qua artifact có hash/VersionId.

- [Template đã kiểm tra](template.json).
- [Bản dựng và hash](build.json).
- [AWS ValidateTemplate — sinh viên Tiến Sơn](default.json).
- [AWS ValidateTemplate — sinh viên Ngọc Quyên](quyen.json).
- [Manifest](manifest.json).

Cả hai API trả thành công. Hồ sơ này kiểm tra cấu hình template; không tạo stack mới hoặc sửa tài nguyên hiện hữu. Bản template 15 tài nguyên trong snapshot raw trước đó được giữ nguyên theo mốc chụp.

[Hướng dẫn triển khai](../../docs/INFRASTRUCTURE.md) · [Báo cáo chính](../../docs/FINAL_REPORT.md).
