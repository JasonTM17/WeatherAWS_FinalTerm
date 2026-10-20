# Danh mục minh chứng trực tiếp trên GitHub

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS.

**Sinh viên:** Nguyễn Tiến Sơn (24110054) và Trần Thị Ngọc Quyên (24110051).

**Cập nhật danh mục:** 20/10/2026, UTC+7.

Danh mục liên kết báo cáo với raw, truy vấn, bảng phân tích, biểu đồ, mã nguồn và nhật ký theo từng tuần. Địa chỉ được hiển thị đầy đủ để giảng viên có thể bấm mở hoặc sao chép. Liên kết tệp dùng `blob/main`, thư mục dùng `tree/main`, commit dẫn tới đúng mốc thay đổi.

**Tổng kết toàn đồ án và phân tích chuyên sâu:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md).

**Nội dung nộp Tuần 4 có liên kết đầy đủ:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SUBMISSION.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/SUBMISSION.md).

## 1. Các bộ dữ liệu dùng trong báo cáo

| Bộ hồ sơ | Bản ghi | Tệp JSON gốc | Phạm vi đối chiếu |
| --- | --- | --- | --- |
| Tuần 1 | 156, gồm 52 bản ghi mỗi đô thị | Theo hồ sơ raw Tuần 1 | Sáu CSV, năm truy vấn Athena và chín biểu đồ |
| Tuần 2 | Sinh viên Tiến Sơn: 27; sinh viên Ngọc Quyên: 57 | Theo metadata từng sinh viên | Mỗi sinh viên có 27 nhóm đô thị–giờ; 21 nhóm chung để đối chiếu |
| Raw Tuần 3 xuất ngày 18/10 | 246/288; tổng 534 | 36 + 47 = **83** | Mốc lịch sử phục vụ đối chiếu các bản xuất |
| Raw Tuần 3 xuất ngày 19/10 | 302/339; tổng 641 | 43 + 52 = **95** | Raw tích lũy mới, chốt lúc 14:22–14:23 UTC+7 |
| Riêng dữ liệu ngày 19/10 | 45/42; tổng 87 | Nằm trong bản xuất ngày 19/10 | Thống kê chung 00:00–13:00: 42 bản ghi mỗi sinh viên |
| Dự báo phát hành ngày 18/10, đối chiếu đủ kỳ ngày 19/10 | 24 giờ × 3 đô thị × 2 chỉ số = 144 giá trị | Phản hồi API lưu cùng hồ sơ dự báo | Từ 18/10 14:00 đến 19/10 13:00 UTC+7, nguồn CAMS tải về sau |

Thứ tự số liệu hai sinh viên trong bảng là **sinh viên Tiến Sơn / sinh viên Ngọc Quyên**. Số **95 JSON** thuộc bản xuất `daily_update_2026_10_19`; bản `raw_export_2026_10_18` có **83 JSON**. Danh mục từng object và SHA-256 ở mục 4 cho phép đối chiếu trực tiếp.

## 2. Minh chứng Tuần 1

- **Bản Word Tuần 1:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.docx](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.docx).

- **Bản PDF Tuần 1:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.pdf](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.pdf).

- **Báo cáo đầy đủ và hồ sơ Tuần 1:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/FINAL_REPORT.md).

- **CSV raw Tuần 1: 156 bản ghi, 23 trường:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/raw_weather_aqi_records.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/raw_weather_aqi_records.csv).

- **Sáu CSV truy vấn và bảng đo Athena:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051).

- **Chín biểu đồ Tuần 1 và bảng nguồn:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/charts](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/charts).

- **Nhật ký và phân công Tuần 1: 18,5 giờ:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/WORKLOG.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_1/docs/WORKLOG.md).

- **Mã nguồn nền tảng S3 và cấu hình:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1/scripts](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1/scripts).

- **Commit nền tảng Tuần 1 — 425b24a:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/425b24a747965783c019b8fe2fd62a47611fb03a](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/425b24a747965783c019b8fe2fd62a47611fb03a).

- **Commit bổ sung biểu đồ trong hồ sơ hai tuần — 351f5be:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/351f5be44737843a123e7f8586ba849f3a4f9cc0](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/351f5be44737843a123e7f8586ba849f3a4f9cc0).

- **Commit đối chiếu giờ công và minh chứng — 0d0df38:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0d0df38148d0b702cbfc1635c39c7338ca0871d3](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0d0df38148d0b702cbfc1635c39c7338ca0871d3).

## 3. Minh chứng Tuần 2

- **Bản Word Tuần 2:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/Bao_cao_Tuan_2_24110054_24110051.docx](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/Bao_cao_Tuan_2_24110054_24110051.docx).

- **Bản PDF Tuần 2:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/Bao_cao_Tuan_2_24110054_24110051.pdf](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/Bao_cao_Tuan_2_24110054_24110051.pdf).

- **Báo cáo đầy đủ Tuần 2:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/FINAL_REPORT.md).

- **Raw và metadata: 27/57 bản ghi thuộc Tuần 2:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_evidence](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_evidence).

- **24 CSV kết quả Athena của hai sinh viên:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_live](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_live).

- **27 CSV phân tích và đối chiếu theo giờ:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_analysis](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_analysis).

- **20 biểu đồ và dữ liệu dùng để dựng hình:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_charts](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2/results/week2_charts).

- **Mã nguồn Lambda hiện tại dùng chung:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py).

- **Nhật ký và phân công Tuần 2: 19,5 giờ:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/WORKLOG.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/docs/WORKLOG.md).

- **Các lượt theo lịch và xác nhận email ngày 16/10:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/scheduled-run-verification.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/scheduled-run-verification.md).

- **Commit khởi tạo triển khai Tuần 2 — 0166b40:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0166b402afbde753378718f2f847160b83c74a1a](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0166b402afbde753378718f2f847160b83c74a1a).

- **Commit báo cáo và phân tích hai bộ dữ liệu — 96ce0a3:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96ce0a34e4f7d1a253c387a5ffd1d7a53170dc6a](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/96ce0a34e4f7d1a253c387a5ffd1d7a53170dc6a).

- **Commit chuẩn hóa thời gian thu thập/phân vùng — 36c9b39:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/36c9b3966a8b6f645dc6bb1491ad6e2b40a78765](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/36c9b3966a8b6f645dc6bb1491ad6e2b40a78765).

## 4. Minh chứng Tuần 3

- **Báo cáo kỹ thuật Tuần 3:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/FINAL_REPORT.md).

- **Raw cập nhật 19/10: 641 bản ghi, 95 JSON gốc:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/daily_update_2026_10_19).

- **Danh mục 43 JSON của sinh viên Tiến Sơn và SHA-256:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/snapshot/default/object_inventory.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/snapshot/default/object_inventory.csv).

- **Danh mục 52 JSON của sinh viên Ngọc Quyên và SHA-256:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/snapshot/quyen/object_inventory.csv](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/snapshot/quyen/object_inventory.csv).

- **Mốc raw 18/10: 534 bản ghi, 83 JSON gốc:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/raw_export_2026_10_18](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/raw_export_2026_10_18).

- **CSV và biểu đồ ngày 19/10: 14 giờ hoàn tất:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/README.md).

- **Dự báo: đủ 24/24 giờ đích, 144 giá trị đối chiếu:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/forecast_followup_2026_10_19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/forecast_followup_2026_10_19).

- **Athena: 18 lượt đo và query ID của mốc tích hợp:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/integration_2026_10_18/benchmark](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/integration_2026_10_18/benchmark).

- **Dashboard và cấu hình đọc lại từ AWS:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/monitoring_dashboard_repair_2026_10_18](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3/results/monitoring_dashboard_repair_2026_10_18).

- **Triển khai SDK, hash và kết quả thu bổ sung ngày 19/10:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/README.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/README.md).

- **Nhật ký và tổng giờ Tuần 3: 20,0 giờ:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/WORKLOG.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/docs/WORKLOG.md).

- **Mã Lambda hiện tại:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_2/lambda/lambda_function.py).

- **Commit tích hợp Athena, Dashboard và dự báo — 0b26858:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e).

- **Commit artifact và phát hành Lambda — c28da19:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356).

- **Commit sửa giờ backfill đã triển khai — 62f1c08:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650).

## 5. Kiểm tra, quy trình phát hành và kế hoạch tiếp theo

- **Chỉ mục thành phần và commit:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/components.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/components.md).

- **Workflow CI kiểm tra repository:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/.github/workflows/verify-repository.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/.github/workflows/verify-repository.yml).

- **Workflow CD Lambda chạy thủ công:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/.github/workflows/week3-release.yml](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/.github/workflows/week3-release.yml).

- **Các lượt GitHub Actions:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions).

- **Kế hoạch Tuần 4 và tiêu chí nghiệm thu:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_4_PLAN.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_4_PLAN.md).

- **CI của bộ hồ sơ đầu vào tại commit fa67191:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39218181522](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39218181522).

CI kiểm tra source, dữ liệu đã lưu và artifact; hồ sơ triển khai ghi riêng thao tác thực hiện trên AWS. Workflow CI chạy theo push/PR; workflow CD Lambda chạy thủ công với xác nhận môi trường. Kế hoạch Tuần 4 được trình bày là công việc dự kiến, có sản phẩm và tiêu chí nghiệm thu.

## 6. Cách đối chiếu một kết quả

1. Mở báo cáo của tuần, xác định bảng hoặc hình, đô thị, đơn vị và mốc dữ liệu.
2. Mở CSV nguồn hoặc bản ghi JSON; dùng danh mục object/hash để kiểm tra nguồn và tính toàn vẹn.
3. Mở chương trình hoặc truy vấn tính kết quả; xem commit trực tiếp để xác định phần đã thay đổi.
4. Đối với thu thập/cảnh báo, mở hồ sơ request–log–S3–SNS và xác nhận email theo đúng lượt kiểm chứng.
5. Đối chiếu người phụ trách và tổng giờ theo tuần trong worklog.

Các đường dẫn nhánh `main` mở nội dung hiện tại; liên kết commit giữ mốc thay đổi cụ thể. Bản ghi mô hình, thời điểm Lambda thu và ngày xuất được ghi riêng trong từng bộ hồ sơ.

[Báo cáo nộp LMS](../BAO_CAO.md) · [Tài liệu dự án](README.md) · [Tổng quan repository](../README.md)

## Bổ sung kiểm chứng nâng cao ngày 20/10

- **Hai stack, raw, 18 truy vấn, metric, email và quản lý phiên:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/advanced_live_2026_10_20).
- **Backtest ba cửa sổ lịch sử và 432 dự đoán:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/backtest_2026_10_20](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_4/results/backtest_2026_10_20).
