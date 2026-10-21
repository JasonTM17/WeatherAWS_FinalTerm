# Kiểm tra công khai GitHub Deployments — ngày 21/10/2026

## Kết quả đã quan sát

Nguồn: [public_readback.json](public_readback.json). Trường `checked_at_utc` ghi thời điểm kiểm tra; mỗi phản hồi có URL, mã HTTP, ngày phản hồi và GitHub request ID. Chỉ lưu các trường API công khai cần đối chiếu, không lưu token, cookie, thông tin creator hoặc nội dung HTML.

Lần kiểm tra dùng **GET không đăng nhập**. Không tạo deployment, cập nhật status, chạy workflow, gọi AWS hoặc triển khai lại hệ thống.

- Danh sách deployment công khai trả HTTP 200 và chứa cả hai ID Tuần 4.
- Record `7215849195` trả HTTP 200: environment `week4-tien-son`, commit `58fdf22da9b048e457aa88e823606cf424ec5caf`, tạo lúc `2026-10-21T02:09:12Z`.
- Record `7215850093` trả HTTP 200: environment `week4-ngoc-quyen`, cùng commit, tạo lúc `2026-10-21T02:09:16Z`.
- API status của từng record trả HTTP 200; trạng thái mới nhất là `success`, environment và đường dẫn hồ sơ khớp bản tổng hợp. Payload ghi `registration_only=true`, `fresh_aws_verification=false`.
- Hai URL dạng `/deployments/week4-…` trả HTTP 404 khi không đăng nhập. Chúng không còn được dùng làm link minh chứng trong nội dung nộp.

Kết quả kiểm tra: **API record PASS; HTTP truy cập trang môi trường FAIL; tổng hợp PARTIAL**. Không coi API thành công là bằng chứng người đọc mở được trang môi trường. Phiên Chrome đang đăng nhập hiển thị sáu deployments trong lần quan sát riêng; điều đó không thay đổi kết quả HTTP không đăng nhập đã lưu.

Không có log phản hồi nguyên gốc của thao tác tạo record trong commit tài liệu cũ. Phản hồi đọc lại hiện tại xác nhận trạng thái tại thời điểm kiểm tra, không tái tạo điều kiện truy cập của người đánh giá trước đó.

## Liên kết công khai để đối chiếu

- [API record của sinh viên Tiến Sơn](https://api.github.com/repos/JasonTM17/WeatherAWS_FinalTerm/deployments/7215849195).
- [API status của sinh viên Tiến Sơn](https://api.github.com/repos/JasonTM17/WeatherAWS_FinalTerm/deployments/7215849195/statuses).
- [API record của sinh viên Ngọc Quyên](https://api.github.com/repos/JasonTM17/WeatherAWS_FinalTerm/deployments/7215850093).
- [API status của sinh viên Ngọc Quyên](https://api.github.com/repos/JasonTM17/WeatherAWS_FinalTerm/deployments/7215850093/statuses).
- [Hồ sơ triển khai AWS ngày 20/10](../advanced_live_2026_10_20/stacks/) là nguồn kiểm chứng triển khai, tách với bản ghi GitHub bổ sung sau đó.

## Tái kiểm tra

Kiểm tra lại snapshot đã lưu, không gọi mạng:

```text
python tuan_4/scripts/verify_github_deployments.py --check tuan_4/results/github_deployment_readback_2026_10_21/public_readback.json
```

Lấy phản hồi mới vào một thư mục mới, không ghi đè bằng chứng cũ:

```text
python tuan_4/scripts/verify_github_deployments.py --output output/github-public-readback-new
```

Verifier kiểm tra ID, environment, commit, ngày tạo, danh sách chứa record, payload, status mới nhất và các link hồ sơ. HTTP 404, record thiếu, status rỗng hoặc sai identity đều không được coi là API PASS. Trạng thái HTTP của trang môi trường được kiểm tra độc lập. Dữ liệu lưu lại chỉ chứng minh lần kiểm tra đã ghi, không bảo đảm truy cập mãi về sau.

[Tài liệu GitHub REST Deployments](https://docs.github.com/en/rest/deployments/deployments) · [Bản tổng hợp cũ và đính chính](../github_deployments_2026_10_21/README.md) · [Nội dung nộp Tuần 4](../../docs/SUBMISSION.md).
