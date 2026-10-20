# Nội dung nộp báo cáo Tuần 4

**Nguyễn Tiến Sơn — MSSV 24110054; Trần Thị Ngọc Quyên — MSSV 24110051.**

**Báo cáo tổng kết Tuần 4 — Đề tài “Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS”, lĩnh vực Domain Apps.**

Kính gửi thầy, chúng em gửi báo cáo tổng kết Tuần 4, cập nhật ngày 20/10/2026, tiếp nối hồ sơ các tuần đã được duyệt và bổ sung kiểm chứng nâng cao thực tế.

## 1. Tổng kết và triển khai hạ tầng

Trong Tuần 4, chúng em hoàn thiện kiểm chứng hệ thống thời tiết và chất lượng không khí cho TP. Hồ Chí Minh, Hà Nội và Đà Nẵng, đồng thời triển khai hai stack ứng dụng độc lập bằng một template CloudFormation gồm 17 tài nguyên. Ngày 20/10/2026, `weather-w4-son` và `weather-w4-quyen` đều đạt CREATE_COMPLETE. Gói Lambda của hai stack khớp source collector trong repository qua SHA-256; artifact được lấy theo Version ID cụ thể. Lịch mới giữ DISABLED để tránh thu thập tự động song song với lịch chuẩn.

- **Báo cáo Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md).
- **CloudFormation và hướng dẫn triển khai:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/INFRASTRUCTURE.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/INFRASTRUCTURE.md).
- **Events, cấu hình và kiểm chứng stack mới:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/stacks](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/stacks).

## 2. Thu thập, dữ liệu raw và giám sát

Mỗi Lambda mới được gọi một lần có kiểm soát bằng event `{}`, thu đủ ba bản ghi cho ba đô thị. Chúng em tải nguyên object S3, xuất CSV đủ 23 trường và SELECT theo chính xác record_id trong database/workgroup của từng stack. Bốn trường record_id, city, us_aqi và pm2_5 trong truy vấn khớp raw; không dùng lại kết quả Athena. START/END/REPORT và Result được ghép theo đúng request; mỗi function có một Invocation và 0 Errors trong chu kỳ 300 giây chứa lượt kiểm chứng.

Snapshot tích lũy ngày 20/10 gồm **700 bản ghi và 115 JSON gốc**: sinh viên Tiến Sơn có 331 bản ghi/53 tệp; sinh viên Ngọc Quyên có 369 bản ghi/62 tệp. Mỗi object có số dòng, dung lượng và SHA-256; raw giữ các lượt lấy lặp, bảng đô thị–giờ được xuất riêng cho phân tích.

- **Bộ kiểm chứng AWS ngày 20/10:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/advanced_live_2026_10_20/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/advanced_live_2026_10_20/README.md).
- **JSON gốc, CSV và inventory:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/snapshot](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/snapshot).
- **Đối chiếu vận hành:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md).

## 3. Kiểm chứng cảnh báo và kênh email

Quy tắc cảnh báo là **US AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³**. Đợt ngày 19/10 trên hệ thống hiện hữu ghi nhận Hà Nội AQI 101; mỗi môi trường có một Publish được SNS chấp nhận và người nhận xác nhận email mới.

Trong lượt thu thập ngày 20/10 trên stack mới, dữ liệu dưới ngưỡng nên kết quả 0 cảnh báo đúng với cấu hình. Sau khi xác nhận subscription của hai topic mới, chúng em gửi riêng một thư thử kênh SNS trên mỗi topic; AWS chấp nhận cả hai và cả hai sinh viên xác nhận đã nhận đúng thư. Thư thử ghi rõ mục đích kiểm chứng, được phân biệt với cảnh báo vượt ngưỡng.

- **Xác nhận cảnh báo dữ liệu ngày 19/10:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/verification_2026_10_19/recipient_confirmation.json](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/verification_2026_10_19/recipient_confirmation.json).
- **Publish và xác nhận email của topic mới:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/email](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/email).

## 4. Thực nghiệm Athena và đánh giá dự báo

Chúng em thực hiện **18 truy vấn Athena mới**, gồm JSON đăng ký phân vùng, JSON Partition Projection và Parquet Partition Projection, mỗi phương án đo ba lần trên mỗi môi trường. Các phương án dùng cùng snapshot và phép tổng hợp, tắt result reuse, luân phiên thứ tự chạy. Kết quả tổng hợp tương đương; với ngày lọc 20/10 có ba bản ghi, Parquet giảm median byte quét từ 1.558 xuống 302 byte, khoảng **80,62%**. JSON Projection có tổng thời gian trung vị thấp hơn Parquet trong bộ đo này; báo cáo trình bày byte quét và độ trễ riêng.

Phần dự báo sử dụng phương án **backtest ba cửa sổ lịch sử**, mỗi cửa sổ đích 24 giờ cho ba đô thị và hai biến. MA24 đệ quy được cố định trước đánh giá, chỉ nhận 24 giờ trước từng gốc; đầu ra có **432 dự đoán và 18 dòng MAE/RMSE/Bias**. Dữ liệu mô hình, dự đoán, sai số và biểu đồ đều được lưu. Đây là backtest hồi cứu trên chuỗi mô hình Open-Meteo/CAMS; kỳ dự báo đã phát hành của Tuần 3 vẫn giữ riêng theo mốc.

- **18 truy vấn và Statistics:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/benchmark](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/benchmark).
- **Backtest: phương pháp, dữ liệu và hình:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/README.md).
- **432 dự đoán:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/predictions.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/predictions.csv).
- **MAE/RMSE/Bias:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/metrics.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/results/backtest_2026_10_20/metrics.csv).

## 5. Bảo mật, chi phí và quản lý phiên

Hai bucket mới được đọc lại cấu hình: bốn thiết lập Block Public Access đều bật, AES256, versioning Enabled, BucketOwnerEnforced, không public ACL/policy và policy từ chối kết nối không qua HTTPS. Permission gọi Lambda gắn với ARN rule và SourceAccount. LabRole học phần được giữ nguyên, policy runtime giới hạn theo tài nguyên được cung cấp để tham khảo.

Cost Explorer kỳ 12–19/10 có 117 nhóm ngày/dịch vụ/loại ghi nhận; tổng hiển thị đến cent là **0,00 USD của sinh viên Tiến Sơn** và **0,14 USD của sinh viên Ngọc Quyên**. CSV giữ giá trị gốc và Estimated; số liệu thuộc kỳ chi phí đã chọn.

Ngày 20/10, công cụ quản lý phiên đã tạm dừng rồi khôi phục lịch chuẩn trên cả hai môi trường qua ENABLED → DISABLED → ENABLED, đối chiếu fingerprint môi trường/target không đổi và không xóa dữ liệu. Trạng thái phục hồi riêng được ghi trước thao tác.

- **Rà soát bảo mật:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SECURITY_AUDIT.md).
- **Báo cáo chi phí:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/COST_REPORT.md).
- **Minh chứng pause/restore thực tế:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/session](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20/session).
- **Checklist cuối Lab:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SESSION_CHECKLIST.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SESSION_CHECKLIST.md).

## 6. Phân công, kiểm tra và bàn giao

Sinh viên Tiến Sơn phụ trách hạ tầng, Lambda, S3, Secrets Manager, SNS, EventBridge và CloudWatch. Sinh viên Ngọc Quyên phụ trách Glue/Athena, dữ liệu, phân tích, dự báo và chi phí; hai sinh viên cùng tích hợp và rà soát hồ sơ. **Tổng theo tuần đã xác nhận:** Tuần 4 là 10 giờ mỗi sinh viên, tổng 20 giờ; toàn đồ án **78 giờ**.

Repository có kiểm thử các ranh giới triển khai, môi trường, artifact, phục hồi lịch và tách dữ liệu huấn luyện/đích. Bộ xác minh offline kiểm tra manifest, JSON–CSV–SELECT và tính lại dự đoán/sai số. GitHub Actions kiểm tra theo đúng commit. Video trình bày dưới 10 phút được bổ sung bằng đường dẫn sau khi quay và kiểm tra quyền xem.

- **Worklog Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/WORKLOG.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/WORKLOG.md).
- **CSV giờ công toàn đồ án:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/worklog.csv).
- **Báo cáo tổng kết Tuần 1–4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md).

## 7. Mã nguồn và commit minh chứng

Các commit dưới đây giữ đúng message nguyên bản; mỗi liên kết dẫn đến thay đổi tương ứng trong Git:

- **`feat(week4): add verify_stack script for isolated stack output verification` — 62673c4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62673c4824ce9a9b333bd762c266a91794f020e3](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62673c4824ce9a9b333bd762c266a91794f020e3).
- **`docs(week4): synchronize verbatim commit history, add deploy_stack test suite, and finalize master report` — cb72600:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/cb72600708d2f674c2f50be8a33dbeeab8b15966](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/cb72600708d2f674c2f50be8a33dbeeab8b15966).
- **`fix(worklog): require published evidence and exclude local demo guides` — 97cc67b:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/97cc67bda994cf3e6c04dfe3049d3a680b807470](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/97cc67bda994cf3e6c04dfe3049d3a680b807470).
- **`feat(week4): complete final week verification, consolidate CloudFormation infrastructure, and update catalog` — 96bedec:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96bedec19f4c208a179581039b5ebc42a526b093).

- **Source collector:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py).
- **Hồ sơ Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4).

- **Kiểm tra CI:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml).

Chúng em kính gửi thầy báo cáo cùng dữ liệu và các liên kết minh chứng để đối chiếu kết quả.
