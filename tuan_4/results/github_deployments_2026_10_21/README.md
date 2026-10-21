# Đối chiếu bản tổng hợp GitHub Deployments — Tuần 4

## Đính chính liên kết và phạm vi minh chứng

Hai liên kết trang môi trường Deployments từng đặt trong báo cáo trả **HTTP 404 khi truy cập không đăng nhập** ở lần kiểm tra ngày 21/10/2026. Vì vậy, chúng đã được thay bằng liên kết trực tiếp đến hồ sơ triển khai AWS cố định theo commit. Bản nộp không còn yêu cầu người đọc mở hai trang môi trường đó.

Trong lần đọc lại cùng ngày, API GitHub công khai trả **HTTP 200** cho danh sách deployment, từng record `7215849195` / `7215850093` và trạng thái của chúng. ID, environment, commit, ngày tạo và trạng thái `success` khớp bản tổng hợp. Phản hồi được lấy bằng GET không dùng token hoặc cookie, lưu các trường công khai cùng request ID tại [hồ sơ đọc lại](../github_deployment_readback_2026_10_21/README.md).

Kết quả này chứng minh các record tồn tại tại thời điểm đọc lại; không cho phép kết luận điều kiện truy cập của người đánh giá trước đó. Việc API đọc được và trang môi trường trả 404 được ghi riêng, không gộp thành một trạng thái thành công chung.

## Phân biệt các nguồn

- [registration.json](registration.json) giữ nguyên byte của bản tổng hợp đã công bố. Đây là bản tổng hợp, không phải phản hồi API nguyên gốc hay log thực thi thao tác tạo record.
- Commit [`616f15c — docs(week4): record verified AWS stacks in GitHub Deployments`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/616f15c71c1c6ec9c0f8bf098ecdc2e15d371486) chỉ sửa bốn tệp trong repository. Không dùng commit này để chứng minh có thao tác tạo GitHub deployment, chạy CD hay triển khai AWS.
- [public_readback.json](../github_deployment_readback_2026_10_21/public_readback.json) lưu các trường được chọn từ phản hồi API thực tế ngày 21/10, tách khỏi bản tổng hợp cũ.
- Cả hai record có payload `registration_only=true`, `fresh_aws_verification=false`: ghi nhận hồ sơ triển khai đã có, không gọi lại AWS.

## Minh chứng triển khai AWS

Hai stack được đối chiếu bằng Events, hash source/artifact/template và kết quả thực thi ngày 20/10 tại commit `58fdf22da9b048e457aa88e823606cf424ec5caf`:

- [Sinh viên Tiến Sơn — stack weather-w4-son](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/58fdf22da9b048e457aa88e823606cf424ec5caf/tuan_4/results/advanced_live_2026_10_20/stacks/default).
- [Sinh viên Ngọc Quyên — stack weather-w4-quyen](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/58fdf22da9b048e457aa88e823606cf424ec5caf/tuan_4/results/advanced_live_2026_10_20/stacks/quyen).

[Trang Tuần 4](../../README.md) · [Hồ sơ AWS ngày 20/10](../advanced_live_2026_10_20/README.md) · [Đọc lại API và kiểm tra truy cập công khai](../github_deployment_readback_2026_10_21/README.md).
