# Nội dung nộp báo cáo Tuần 4

**Nguyễn Tiến Sơn — MSSV 24110054; Trần Thị Ngọc Quyên — MSSV 24110051.**

**Báo cáo tổng kết Tuần 4 — Đề tài “Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS”, lĩnh vực Domain Apps.**

Trong Tuần 4, chúng em tập trung kiểm chứng tổng thể hệ thống và hoàn thiện hồ sơ theo góp ý của thầy sau khi báo cáo Tuần 3 được duyệt. Mốc kiểm chứng ngày 19/10/2026 được thực hiện trên môi trường của sinh viên Tiến Sơn và sinh viên Ngọc Quyên. Hồ sơ trình bày mã đang triển khai, dữ liệu raw, truy vấn, cảnh báo, giám sát, chi phí và cấu hình bảo mật; tài liệu được hoàn thiện ngày 20/10/2026.

## 1. Thu thập và đối chiếu dữ liệu đầu-cuối

Mỗi môi trường có một lượt realtime bằng event `{}`, thu đủ ba bản ghi của TP. Hồ Chí Minh, Hà Nội và Đà Nẵng. Chúng em tải lại nguyên object S3, giữ CSV đủ 23 trường và thực hiện SELECT theo đúng record_id. Kết quả truy vấn khớp bản raw về mã bản ghi, đô thị và giá trị dữ liệu. Báo cáo bổ sung bảng raw trực tiếp, giúp theo dõi từ kết quả Lambda tới dữ liệu lưu trữ và Athena.

- **Báo cáo Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md).
- **Raw, CSV, SQL và kết quả truy vấn của sinh viên Tiến Sơn:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/verification_2026_10_19/e2e/default](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/verification_2026_10_19/e2e/default).
- **Raw, CSV, SQL và kết quả truy vấn của sinh viên Ngọc Quyên:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/verification_2026_10_19/e2e/quyen](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/verification_2026_10_19/e2e/quyen).

## 2. Giám sát và cảnh báo email

Trong chu kỳ chứa lượt kiểm chứng, mỗi môi trường ghi nhận một Invocation, không có Error; START/END/REPORT và Result được đối chiếu với đúng request cùng object S3. Việc tính tỷ lệ lỗi áp dụng cho chu kỳ có đủ cặp metric tương ứng.

Điều kiện cảnh báo thực tế là **US AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³**. Trong mỗi lượt đã lưu, Hà Nội có AQI 101 nên phát sinh một yêu cầu cảnh báo; SNS chấp nhận một thông điệp ở mỗi môi trường. Cả sinh viên Tiến Sơn và sinh viên Ngọc Quyên đã xác nhận nhận email mới của đúng đợt kiểm chứng. Các lượt demo sau đó được đánh giá theo dữ liệu và ngưỡng của chính lượt đó.

- **Đối chiếu log–metric–S3:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md).
- **Xác nhận người nhận:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/verification_2026_10_19/recipient_confirmation.json](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/verification_2026_10_19/recipient_confirmation.json).

## 3. Chi phí và quản lý cuối phiên

Cost Explorer được tổng hợp cho kỳ 12–19/10/2026 theo ngày, dịch vụ và loại ghi nhận. Tổng hiển thị đến cent là **0,00 USD của sinh viên Tiến Sơn** và **0,14 USD của sinh viên Ngọc Quyên**. CSV giữ giá trị chính xác, đơn vị và Estimated. Đây là số liệu tài khoản trong kỳ, được trình bày riêng với mức dự kiến của bài thực hành.

Chúng em chuẩn bị checklist xuất raw/log/metric/chi phí trước khi tạm dừng lịch và kết thúc Learner Lab. Công cụ preview/pause/restore kiểm tra đúng môi trường, hàm, rule và target, lưu trạng thái khôi phục trước thao tác áp dụng. Việc kết thúc phiên được thực hiện sau khi lưu đủ minh chứng và hoàn tất sử dụng môi trường.

- **Báo cáo chi phí:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md).
- **Checklist cuối phiên:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SESSION_CHECKLIST.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SESSION_CHECKLIST.md).

## 4. CloudFormation và rà soát bảo mật

Repository giữ một template CloudFormation chính gồm **17 tài nguyên ứng dụng**, sử dụng artifact từ source collector chính. Template đã qua cfn-lint và AWS ValidateTemplate trên cả hai môi trường; lịch mới khởi tạo DISABLED, các tài nguyên chứa dữ liệu được chỉ định giữ theo Retain. Hồ sơ phân biệt bước kiểm tra template với việc tạo và kiểm chứng stack mới.

Kết quả đọc S3 hiện hữu ghi nhận đủ bốn thiết lập Block Public Access, mã hóa AES256 và không ghi nhận public policy/public ACL. Báo cáo tách cấu hình hiện hữu với versioning và chính sách HTTPS của stack mới. LabRole của học phần được giữ nguyên; mẫu quyền runtime giới hạn theo bucket, Secret, topic và log group được cung cấp để đối chiếu.

- **Template chính:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/infrastructure/weather-stack.json](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/infrastructure/weather-stack.json).
- **Hồ sơ kiểm tra template:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/template_validation_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/template_validation_2026_10_19).
- **Rà soát bảo mật:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md).

## 5. Phân công, nhật ký và chuẩn bị trình bày

Sinh viên Tiến Sơn phụ trách hạ tầng, Lambda, S3, lịch, SNS và CloudWatch. Sinh viên Ngọc Quyên phụ trách Glue/Athena, dữ liệu, chi phí và phân tích. Hai sinh viên cùng tích hợp, đối chiếu và hoàn thiện hồ sơ. **Tổng theo tuần đã xác nhận** của Tuần 4 là 10 giờ mỗi sinh viên, tổng 20 giờ; toàn đồ án là **78 giờ**.

Chúng em đã chuẩn bị lời thoại và hướng dẫn thao tác cho video dưới 10 phút, đi từ kiến trúc đến Test Lambda, log, S3, Athena, SNS/email, dashboard, chi phí và bảo mật. Đường dẫn video thực tế được bổ sung sau khi quay và kiểm tra quyền xem.

- **Nhật ký Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/WORKLOG.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/WORKLOG.md).
- **CSV giờ công toàn đồ án:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv).
- **Lời thoại demo:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/VIDEO_DEMO_SCRIPT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/VIDEO_DEMO_SCRIPT.md).
- **Hướng dẫn từng bước bấm:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/DEMO_GUIDE.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/DEMO_GUIDE.md).

## 6. Mã nguồn, phiên bản và tổng kết

Source collector tiếp tục sử dụng tệp chính của dự án. Bản tổng kết toàn đồ án nối kết kết quả Tuần 1–4, giải thích lựa chọn kiến trúc, thực nghiệm Athena, sai số dự báo và phương pháp kiểm chứng. Nội dung cạnh liên kết commit dưới đây giữ nguyên message trong Git:

- **`feat(week4): complete final week verification, consolidate CloudFormation infrastructure, and update catalog` — 96bedec:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093).
- **`fix(evidence): preserve Week 4 snapshot bytes across platforms` — 892861e:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/892861ec5129d59a9c772ef20ed6d2ac053d65f5](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/892861ec5129d59a9c772ef20ed6d2ac053d65f5).
- **`docs(report): add final project synthesis and acceptance mapping` — f6921e7:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/f6921e7dc0e26245ca5d33dd0b7288dc11120f0d](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/f6921e7dc0e26245ca5d33dd0b7288dc11120f0d).

Kết quả Tuần 4 kết nối được source triển khai với lượt thực thi, dữ liệu lưu trữ, truy vấn và email đã nhận. Hồ sơ chi phí, bảo mật, hạ tầng và nhật ký sử dụng cùng các nguồn minh chứng có thể kiểm tra lại. Chúng em kính gửi thầy báo cáo và hệ thống liên kết để đối chiếu kết quả.

- **Source collector:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py).
- **Tổng kết toàn đồ án:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md).
- **Hồ sơ Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4).
- **Quy trình kiểm tra CI:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml).
