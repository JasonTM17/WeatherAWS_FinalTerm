# Báo cáo tiến độ Tuần 3 và hồ sơ đối chiếu Tuần 1–2

**Nguyễn Tiến Sơn — MSSV 24110054 · Trần Thị Ngọc Quyên — MSSV 24110051**

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS (Domain Apps).
**Học phần:** Điện toán đám mây, lớp 261CLCO332779_05.
**GVHD:** ThS. Huỳnh Xuân Phụng. **Mốc cập nhật:** 19/10/2026, UTC+7.

Repository: [https://github.com/JasonTM17/WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm) · Hồ sơ Tuần 1: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1) · Hồ sơ Tuần 2: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2) · Hồ sơ Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3).

## 1. Kết quả và phạm vi báo cáo

Chúng em đã xây dựng luồng thu thập dữ liệu Open-Meteo theo lịch EventBridge, xử lý bằng Lambda, lưu raw phân vùng ngày trên S3 và truy vấn bằng Glue/Athena. SNS giữ kênh cảnh báo email; CloudWatch lưu log/metric và Dashboard. Dữ liệu thời tiết và chất lượng không khí được cung cấp từ mô hình Open-Meteo/CAMS, có ghi nguồn và thời điểm tải.

Tuần 1 tập trung kiến trúc, nền tảng lưu trữ/cấu hình và bộ dữ liệu 156 bản ghi. Tuần 2 hoàn thiện thu thập, truy vấn/phân tích, triển khai mã và kiểm chứng cảnh báo. **Đã hoàn thành kế hoạch công việc tích hợp Tuần 3 tại mốc ngày 18/10/2026.** Các sản phẩm gồm bản xuất raw, thử nghiệm Projection/Parquet, Dashboard/Metric Filters, đánh giá dự báo và CI/CD.

## 2. Dữ liệu mới và chất lượng

**Cập nhật ngày 19/10/2026:** đã dùng phiên AWS của hai sinh viên để thu chuỗi lịch sử bằng Lambda và đọc lại S3. Raw tích lũy hiện có **302 bản ghi của sinh viên Tiến Sơn và 339 của sinh viên Ngọc Quyên**, tổng **641 bản ghi, 95 JSON gốc**. Riêng ngày 19/10 có **45 và 42 bản ghi** đến lúc xuất 14:22–14:23. Thống kê dùng cùng **14 giờ hoàn tất, 00:00–13:00 UTC+7**, tương ứng 42 bản ghi mỗi sinh viên. Ba bản ghi trong giờ đang diễn ra của sinh viên Tiến Sơn được giữ riêng ở raw. Chuỗi backfill là phần thu bổ sung từ mô hình; nguồn và chế độ thu được ghi theo từng bản ghi, riêng với các lượt theo lịch.

Dữ liệu ngày 19/10, CSV/JSON và minh chứng Lambda–S3: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/daily_update_2026_10_19/README.md .

![AQI và PM2.5 ngày 19/10](tuan_3/results/daily_update_2026_10_19/daily_aqi_pm25.png)

**Các mốc ngày 18/10 dưới đây được giữ để truy vết bảng và biểu đồ đã công bố:**

**Raw đã được xuất đầy đủ cho hồ sơ Tuần 3:** [246 dòng của sinh viên Tiến Sơn](tuan_3/results/raw_export_2026_10_18/snapshot/default/raw_all.csv), [288 dòng của sinh viên Ngọc Quyên](tuan_3/results/raw_export_2026_10_18/snapshot/quyen/raw_all.csv), kèm [83 tệp JSON gốc, hash, thời điểm và bảng mẫu](tuan_3/results/raw_export_2026_10_18/README.md). Tổng 534 bản ghi, giữ đủ 23 trường và bảo toàn dữ liệu cũ.

**Snapshot dùng cho các bảng phân tích bên dưới:**

Sau khi cập nhật phiên Lab, snapshot đọc được **246 bản ghi của sinh viên Tiến Sơn** và **285 bản ghi của sinh viên Ngọc Quyên**. Timestamp cuối lần lượt là 18/10 08:15:46 và 08:51:05 UTC. Bảy nhóm kiểm tra chất lượng đã khai báo không phát hiện lỗi. Cả hai Lambda khớp gói đã được triển khai và kiểm chứng.

[Raw sinh viên Tiến Sơn](tuan_3/results/refresh_2026_10_18/snapshot/default/raw_all.csv) · [Raw sinh viên Ngọc Quyên](tuan_3/results/refresh_2026_10_18/snapshot/quyen/raw_all.csv) · [Nguồn và thời điểm chốt dữ liệu](tuan_3/results/refresh_2026_10_18/README.md).

Raw được giữ nguyên từng lượt. Phân tích theo đô thị–giờ lấy trung bình các lượt cùng giờ để tránh cho giờ có nhiều lượt thu trọng số cao hơn. Tỷ lệ được tính trên các bản ghi đã lưu; hệ số tương quan mô tả mức liên hệ giữa các chỉ số trong cùng tập phân tích.

## 3. Thống kê mô tả và liên hệ giữa các chỉ số

Đã lưu 96 dòng thống kê cho tám biến, ba đô thị, hai sinh viên và hai phạm vi raw/theo giờ; gồm trung bình, trung vị, độ lệch chuẩn mẫu, min/max và P25/P75/P90/P95. CSV tương quan có 120 dòng Pearson/Spearman, xử lý giá trị đồng hạng bằng hạng trung bình.

[Thống kê đầy đủ](tuan_3/results/refresh_2026_10_18/analysis/descriptive.csv) · [Tương quan đầy đủ](tuan_3/results/refresh_2026_10_18/analysis/correlations.csv) · [Bảng và diễn giải chi tiết](tuan_3/docs/FINAL_REPORT.md#2-đầu-vào-dữ-liệu-raw-và-chất-lượng).

![AQI theo đô thị–giờ](tuan_3/results/refresh_2026_10_18/analysis/city_hour_aqi.png)

![Liên hệ mô tả với PM2.5](tuan_3/results/refresh_2026_10_18/analysis/hourly_correlations.png)

## 4. Athena Projection và Parquet

Thử nghiệm đã chạy 18 truy vấn: ba lần đo cho mỗi cấu hình trong mỗi môi trường, tắt sử dụng lại kết quả. Ba cấu hình gồm NDJSON có phân vùng đăng ký, NDJSON với Projection và Parquet Snappy với Projection. Dữ liệu Parquet được tạo bằng PyArrow, không dùng CTAS. Thử nghiệm dùng bộ raw ban đầu 237/273 đã đóng băng; snapshot mới không thay đầu vào của các truy vấn lịch sử.

Parquet giảm byte quét khoảng 80,59% và 96,50% trong từng môi trường. Thời gian được đánh giá riêng: ở môi trường sinh viên Ngọc Quyên, engine trung vị của Parquet là 515 ms, NDJSON Projection là 431 ms. Byte và thời gian là số đo của toàn truy vấn trả ba đô thị; chi phí được theo dõi riêng bằng Cost Explorer.

[18 lượt đo và query ID](tuan_3/results/integration_2026_10_18/benchmark/) · [Bảng chi tiết và kết quả từng đô thị](tuan_3/docs/FINAL_REPORT.md#3-partition-projection-và-parquet).

## 5. Dự báo và đối chiếu dữ liệu tải về sau

Phép đánh giá ban đầu dùng 149 giờ huấn luyện và 24 giờ giữ lại cho mỗi đô thị/chỉ số, so sánh giá trị cuối, lặp 24 giờ trước và MA 24 giờ. Đợt cập nhật bổ sung MA 3 giờ đệ quy, có mã tính và CSV riêng. MA 3 giờ được trình bày là phân tích khám phá bổ sung trên cùng tập giữ lại; các kỳ dự báo phát hành trước giờ đích được theo dõi riêng.

[Mã phân tích bổ sung](tuan_3/scripts/reconcile_analysis.py) · [24 bộ sai số MAE/RMSE/Bias](tuan_3/results/refresh_2026_10_18/analysis/ma_comparison_metrics.csv) · [576 dòng giá trị đích/dự báo](tuan_3/results/refresh_2026_10_18/analysis/ma_comparison_predictions.csv).

![So sánh các phương pháp trên cùng tập giữ lại](tuan_3/results/refresh_2026_10_18/analysis/holdout_ma_comparison.png)

Bản cập nhật ngày **19/10**, cutoff **07:00 UTC**, đã đối chiếu đủ **24/24 giờ đích, 144/144 giá trị** với dữ liệu CAMS tải về sau. Giữ nguyên bản dự báo phát hành khoảng 06:24 UTC ngày 18/10. Kỳ đối chiếu từ 18/10 14:00 đến 19/10 13:00 UTC+7, sử dụng giá trị mô hình CAMS tải về sau theo đúng từng giờ đích.

Bản phát hành gốc: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/forecast_issued_2026_10_18/forecast_24h.csv .

144 giá trị đối chiếu, sai số và nguồn: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/forecast_followup_2026_10_19/README.md .

![Đối chiếu đủ kỳ dự báo đã phát hành](tuan_3/results/forecast_followup_2026_10_19/issued_vs_later_model.png)

## 6. Triển khai, lịch chạy và email

Hai môi trường đã có CD thành công, gói tải lại từ AWS khớp artifact và cấu hình được giữ nguyên. Hai Metric Filters trong mỗi môi trường đã có kiểm tra mẫu/đọc lại; các lượt thật đã tạo điểm metric log mới. Lượt 13:51 của sinh viên Ngọc Quyên sau sửa định dạng cấu hình có đủ ba bản ghi và 0 cảnh báo phù hợp với mẫu dưới ngưỡng.

[Hồ sơ CD](tuan_3/results/cd_2026_10_18/) · [Lượt sau sửa cấu hình](tuan_3/results/post_repair_2026_10_18/README.md) · [Email đã được người nhận xác nhận ngày 16/10](docs/scheduled-run-verification.md).

Đã đối chiếu số liệu CloudWatch theo timestamp UTC và kiểm chứng biểu thức Dashboard trên sáu trường hợp trong mỗi môi trường; cấu hình đọc lại khớp. Trong cửa sổ 07:40–10:40 UTC, sinh viên Tiến Sơn có hai khoảng và sinh viên Ngọc Quyên có ba khoảng đủ cặp bộ đếm hợp lệ; tỷ lệ lỗi trên các khoảng này là 0%. Mẫu số của tỷ lệ là các khoảng đủ cặp nêu trên; phương pháp ghép và dữ liệu theo thời gian được lưu trong hồ sơ kỹ thuật. Minh chứng Dashboard: https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_3/results/monitoring_dashboard_repair_2026_10_18/README.md .

## 7. Mã nguồn và commit minh chứng

**Các thay đổi chính phục vụ Tuần 3:**

- [62f1c08 — lấy đúng các giờ đã hoàn tất của ngày hiện tại, dùng cho hai lượt thu bổ sung 19/10](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650). [CI đã đạt](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39215400909).

- [0b26858 — tích hợp snapshot, thử nghiệm Athena, Dashboard và đánh giá dự báo](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e).
- [c28da19 — chuẩn hóa gói Lambda để artifact Windows/Linux khớp byte, dùng cho hai lượt CD](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356).
- [7ec1b32 — xuất CSV và 83 JSON raw nguyên bản, kiểm tra đối chiếu và đồng bộ worklog](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/7ec1b3269388214111c96466a01a7fc9541e58b1).

**Các mốc thu thập, triển khai và hồi quy được kế thừa:**

- [36c9b39 — mã Lambda và sửa xử lý thời gian](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/36c9b3966a8b6f645dc6bb1491ad6e2b40a78765).
- [4a72d02 — đối chiếu triển khai, raw/truy vấn và email](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/4a72d0260ce7fbe5ff681e8ec73d17c03ab8859b).
- [3d6dfee — minh chứng các lượt chạy tự động](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/3d6dfeed922fa9d63d4659419bb75be675429c9a).
- [db6844d — ghi nhận an toàn hai nhánh lỗi triển khai](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/db6844d4b1f94c9ec959ff770840dc993c5a657c).

Các commit được dẫn theo nội dung thực sự thay đổi. Minh chứng runtime và kiểm tra giả lập được ghi riêng trong [hướng dẫn vận hành](tuan_3/docs/operation.md).

## 8. Phân công và tổng giờ đã xác nhận

| Giai đoạn | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên | Tổng | Căn cứ |
| --- | --- | --- | --- | --- |
| Tuần 1 | 9,5 giờ | 9,0 giờ | 18,5 giờ | Tổng theo tuần đã xác nhận |
| Tuần 2 | 10,0 giờ | 9,5 giờ | 19,5 giờ | Tổng theo tuần đã xác nhận |
| Tuần 3 — công việc tích hợp | 10,0 giờ | 10,0 giờ | 20,0 giờ | Tổng theo tuần đã xác nhận |
| **Cộng dồn** | **29,5 giờ** | **28,5 giờ** | **58,0 giờ** | Tổng theo tuần đã xác nhận |

Sinh viên Tiến Sơn phụ trách thu thập, cấu hình, triển khai và giám sát/cảnh báo; sinh viên Ngọc Quyên phụ trách Glue/Athena, thống kê và dự báo. Hai sinh viên cùng rà soát tài liệu và số liệu.

[Nhật ký kỹ thuật và tổng giờ Tuần 3](tuan_3/docs/WORKLOG.md) · [CSV Tuần 3](tuan_3/worklog.csv) · [38 giờ Tuần 1–2](worklog.csv). Tổng 20 giờ Tuần 3 được tổng hợp theo xác nhận của từng sinh viên, kèm các mốc kỹ thuật và sản phẩm trong nhật ký.

## 9. Kiểm tra và kết luận

Kiểm tra hồ sơ cập nhật ngày 19/10 đã đạt **57 trường hợp Tuần 3 và đối chiếu 492 tệp minh chứng trong 14 manifest**, gồm raw ngày 19/10 và đủ 24 giờ đích dự báo. CI theo đúng commit dữ liệu: https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39216764078 .

Kiểm tra tệp đã lưu: `python tuan_2/scripts/repository_audit.py --check`, `python tuan_3/scripts/verify_results.py`. Bộ hồi quy: `python -m unittest discover -s tuan_3/tests -v`. Các lệnh kiểm tra tính nhất quán của mã và hồ sơ đã lưu; minh chứng thực thi AWS được dẫn riêng tại mục 6. [Workflow CI](.github/workflows/verify-repository.yml) và [các lượt Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions) ghi kết quả riêng cho từng commit.

**Đã hoàn thành kế hoạch công việc tích hợp Tuần 3 tại mốc ngày 18/10/2026**, với raw, thử nghiệm Athena, Dashboard/Metric Filters, đánh giá dự báo và CI/CD có liên kết minh chứng trực tiếp. Các tệp đã lưu được kiểm tra tính toàn vẹn và tính lại số liệu. Cập nhật ngày 19/10 bổ sung raw trong ngày, thống kê trên cùng 14 giờ hoàn tất và đối chiếu đủ 24 giờ đích dự báo. Dữ liệu ngày 19/10 được chốt lúc 14:22–14:23 UTC+7, với bảng thống kê 00:00–13:00 và nguồn từng bản ghi. [Bảng đối chiếu hồ sơ trước khi nộp](tuan_3/docs/operation.md#8-đối-chiếu-hồ-sơ-trước-khi-nộp) liên kết kết quả với dữ liệu, chương trình và minh chứng vận hành.

## 10. Kế hoạch Tuần 4

Tuần 4 dự kiến tập trung vận hành theo lịch, đối chiếu giám sát, kiểm chứng email và đánh giá dữ liệu qua nhiều mốc. Kế hoạch có tám đầu việc W4-01–W4-08, người phụ trách, sản phẩm, phụ thuộc và tiêu chí nghiệm thu. Lịch đề xuất 26/10–01/11/2026; mốc nộp theo thông báo của giảng viên.

| Trọng tâm | Phân công | Sản phẩm dự kiến |
| --- | --- | --- |
| Phiên bản, thu thập và CloudWatch | Sinh viên Tiến Sơn | Baseline hai môi trường; raw theo ngày; bảng log–metric–S3 và Dashboard |
| Cảnh báo AQI/PM2.5 qua email | Sinh viên Tiến Sơn; sinh viên Ngọc Quyên rà soát | Kiểm tra dưới/vượt ngưỡng, minh chứng SNS và xác nhận email theo lượt mới |
| Athena và phân tích | Sinh viên Ngọc Quyên | 18 lượt đo trên đầu vào cố định; thống kê và biểu đồ màu khớp CSV |
| Dự báo theo nhiều kỳ | Sinh viên Ngọc Quyên | Mục tiêu ba kỳ phát hành, mỗi kỳ 24 giờ đích; sai số theo từng đô thị/chỉ số |
| Kiểm tra và hồ sơ nộp | Hai sinh viên | CI theo commit; báo cáo, nhật ký, liên kết mã nguồn và kịch bản trình bày |

Kế hoạch chi tiết: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_4_PLAN.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/WEEK_4_PLAN.md). Công việc Tuần 4 được cập nhật theo sản phẩm thực hiện; giờ công được tổng hợp riêng khi hai sinh viên xác nhận.
