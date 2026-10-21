# GitHub Deployments — Tuần 4

Ngày 21/10/2026, GitHub được bổ sung hai deployment record cho các stack CloudFormation đã triển khai và kiểm chứng ngày **20/10/2026**. Hai record có trạng thái `success`, gắn với commit chứa source và minh chứng: [`58fdf22 — feat(week4): verify live stacks and three historical backtest windows`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/58fdf22da9b048e457aa88e823606cf424ec5caf).

| Sinh viên | GitHub environment | Stack AWS | Deployment ID |
| --- | --- | --- | --- |
| Sinh viên Tiến Sơn | [week4-tien-son](https://github.com/JasonTM17/WeatherAWS_FinalTerm/deployments/week4-tien-son) | `weather-w4-son` | `7215849195` |
| Sinh viên Ngọc Quyên | [week4-ngoc-quyen](https://github.com/JasonTM17/WeatherAWS_FinalTerm/deployments/week4-ngoc-quyen) | `weather-w4-quyen` | `7215850093` |

## Căn cứ ghi nhận

- [Events, hash source/artifact/template và kết quả sinh viên Tiến Sơn](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/58fdf22da9b048e457aa88e823606cf424ec5caf/tuan_4/results/advanced_live_2026_10_20/stacks/default).
- [Events, hash source/artifact/template và kết quả sinh viên Ngọc Quyên](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/58fdf22da9b048e457aa88e823606cf424ec5caf/tuan_4/results/advanced_live_2026_10_20/stacks/quyen).
- Hai stack `CREATE_COMPLETE`; mỗi collector có ba bản ghi, raw và SELECT đúng database/workgroup; truy vấn kiểm chứng không tái sử dụng kết quả.
- Hash source và template tại commit tham chiếu khớp hồ sơ triển khai. Bộ xác minh ngoại tuyến Tuần 4 đã chạy lại thành công trước khi tạo record.
- [Thông tin đăng ký và trạng thái đọc lại từ GitHub](registration.json).

**Ngày tạo record GitHub là 21/10; ngày triển khai và kiểm chứng AWS là 20/10.** Đây là bổ sung lịch sử triển khai đã có minh chứng. Không thực hiện lại CreateStack, cập nhật Lambda, gọi AWS hoặc chạy CD trong lần ghi nhận này. Trạng thái `success` mô tả kết quả triển khai đã lưu; việc xác nhận dịch vụ đang hoạt động ở thời điểm mới cần kiểm chứng AWS riêng.

Các deployment Tuần 3 được giữ nguyên. Mỗi record Tuần 4 liên kết tới hồ sơ cố định theo commit để đối chiếu với phiên bản đã ghi nhận.

[Trang Tuần 4](../../README.md) · [Hồ sơ triển khai AWS ngày 20/10](../advanced_live_2026_10_20/README.md) · [GitHub Deployments](https://github.com/JasonTM17/WeatherAWS_FinalTerm/deployments)
