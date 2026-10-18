# Báo cáo tiến độ Tuần 1–2 và mốc tích hợp phục vụ Tuần 3

**Nguyễn Tiến Sơn — MSSV 24110054 · Trần Thị Ngọc Quyên — MSSV 24110051**

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS (Domain Apps).
**Học phần:** Điện toán đám mây, lớp 261CLCO332779_05.
**GVHD:** ThS. Huỳnh Xuân Phụng. **Mốc cập nhật:** 18/10/2026, UTC+7.

Repository: [https://github.com/JasonTM17/WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm) · Hồ sơ Tuần 1: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_1) · Hồ sơ Tuần 2: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_2) · Hồ sơ Tuần 3: [https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3](https://github.com/JasonTM17/WeatherAWS_FinalTerm/tree/main/tuan_3).

## 1. Kết quả và phạm vi báo cáo

Chúng em đã xây dựng luồng thu thập dữ liệu Open-Meteo theo lịch EventBridge, xử lý bằng Lambda, lưu raw phân vùng ngày trên S3 và truy vấn bằng Glue/Athena. SNS giữ kênh cảnh báo email; CloudWatch lưu log/metric và Dashboard. Dữ liệu thời tiết/chất lượng không khí là dữ liệu mô hình, không phải phép đo trực tiếp tại trạm.

Tuần 1 tập trung kiến trúc, nền tảng lưu trữ/cấu hình và bộ dữ liệu 156 bản ghi. Tuần 2 hoàn thiện thu thập, truy vấn/phân tích, triển khai mã và kiểm chứng cảnh báo. Mốc chuẩn bị ngày 18/10 bổ sung thử nghiệm Projection/Parquet, Dashboard/Metric Filters, đánh giá dự báo và CI/CD. Kỳ Tuần 3 theo lịch là 19–25/10; mốc này chưa đại diện cho toàn kỳ đó.

## 2. Dữ liệu mới và chất lượng

Sau khi cập nhật phiên Lab, snapshot đọc được **246 bản ghi của sinh viên Tiến Sơn** và **285 bản ghi của sinh viên Ngọc Quyên**. Timestamp cuối lần lượt là 18/10 08:15:46 và 08:51:05 UTC. Bảy nhóm kiểm tra chất lượng đã khai báo không phát hiện lỗi. Cả hai Lambda khớp gói đã được triển khai và kiểm chứng.

[Raw sinh viên Tiến Sơn](tuan_3/results/refresh_2026_10_18/snapshot/default/raw_all.csv) · [Raw sinh viên Ngọc Quyên](tuan_3/results/refresh_2026_10_18/snapshot/quyen/raw_all.csv) · [Nguồn, cửa sổ và giới hạn snapshot](tuan_3/results/refresh_2026_10_18/README.md).

Raw được giữ nguyên từng lượt. Phân tích theo đô thị–giờ lấy trung bình các lượt cùng giờ để tránh cho giờ có nhiều lượt thu trọng số cao hơn. Các tỷ lệ bản ghi không được diễn giải thành tỷ lệ thời gian của toàn tuần; tương quan không được dùng để kết luận quan hệ nhân quả.

## 3. Thống kê mô tả và liên hệ giữa các chỉ số

Đã lưu 96 dòng thống kê cho tám biến, ba đô thị, hai sinh viên và hai phạm vi raw/theo giờ; gồm trung bình, trung vị, độ lệch chuẩn mẫu, min/max và P25/P75/P90/P95. CSV tương quan có 120 dòng Pearson/Spearman, xử lý giá trị đồng hạng bằng hạng trung bình.

[Thống kê đầy đủ](tuan_3/results/refresh_2026_10_18/analysis/descriptive.csv) · [Tương quan đầy đủ](tuan_3/results/refresh_2026_10_18/analysis/correlations.csv) · [Bảng và diễn giải chi tiết](tuan_3/docs/FINAL_REPORT.md#2-đầu-vào-dữ-liệu-raw-và-chất-lượng).

![AQI theo đô thị–giờ](tuan_3/results/refresh_2026_10_18/analysis/city_hour_aqi.png)

![Liên hệ mô tả với PM2.5](tuan_3/results/refresh_2026_10_18/analysis/hourly_correlations.png)

## 4. Athena Projection và Parquet

Thử nghiệm đã chạy 18 truy vấn: ba lần đo cho mỗi cấu hình trong mỗi môi trường, tắt sử dụng lại kết quả. Ba cấu hình gồm NDJSON có phân vùng đăng ký, NDJSON với Projection và Parquet Snappy với Projection. Dữ liệu Parquet được tạo bằng PyArrow, không dùng CTAS. Thử nghiệm dùng bộ raw ban đầu 237/273 đã đóng băng; snapshot mới không thay đầu vào của các truy vấn lịch sử.

Parquet giảm byte quét khoảng 80,59% và 96,50% trong từng môi trường. Tuy nhiên, Parquet không luôn nhanh hơn NDJSON Projection: với sinh viên Ngọc Quyên, engine trung vị 515 ms so với 431 ms. Không quy giảm byte quét thành mức tiết kiệm tiền. Byte/thời gian đo thuộc toàn truy vấn trả ba đô thị, không phân bổ thành số đo riêng của mỗi đô thị.

[18 lượt đo và query ID](tuan_3/results/integration_2026_10_18/benchmark/) · [Bảng chi tiết và kết quả từng đô thị](tuan_3/docs/FINAL_REPORT.md#3-partition-projection-và-parquet).

## 5. Dự báo và đối chiếu dữ liệu tải về sau

Phép đánh giá ban đầu dùng 149 giờ huấn luyện và 24 giờ giữ lại cho mỗi đô thị/chỉ số, so sánh giá trị cuối, lặp 24 giờ trước và MA 24 giờ. Đợt cập nhật bổ sung MA 3 giờ đệ quy, có mã tính và CSV riêng. Đây là phân tích bổ sung sau khi đã xem tập giữ lại, không phải một phép đánh giá độc lập mới để lựa chọn mô hình.

[Mã phân tích bổ sung](tuan_3/scripts/reconcile_analysis.py) · [24 bộ sai số MAE/RMSE/Bias](tuan_3/results/refresh_2026_10_18/analysis/ma_comparison_metrics.csv) · [576 dòng giá trị đích/dự báo](tuan_3/results/refresh_2026_10_18/analysis/ma_comparison_predictions.csv).

![So sánh các phương pháp trên cùng tập giữ lại](tuan_3/results/refresh_2026_10_18/analysis/holdout_ma_comparison.png)

Đã đối chiếu được hai giờ đích 07:00 và 08:00 UTC của bản dự báo phát hành lúc khoảng 06:24 UTC với giá trị CAMS tải về sau: **12/144 dòng**. Các giá trị này không phải số đo trạm và có thể chịu cập nhật mô hình. Chưa đủ 24 giờ đích nên chưa kết luận độ chính xác của toàn kỳ dự báo.

[Bản dự báo đã phát hành](tuan_3/results/forecast_issued_2026_10_18/forecast_24h.csv) · [Đối chiếu mới từng giá trị](tuan_3/results/refresh_2026_10_18/analysis/later_model/comparison.csv) · [Nguồn tải về sau](tuan_3/results/refresh_2026_10_18/analysis/later_model/provenance.json).

## 6. Triển khai, lịch chạy và email

Hai môi trường đã có CD thành công, gói tải lại từ AWS khớp artifact và cấu hình được giữ nguyên. Hai Metric Filters trong mỗi môi trường đã có kiểm tra mẫu/đọc lại; các lượt thật đã tạo điểm metric log mới. Lượt 13:51 của sinh viên Ngọc Quyên sau sửa định dạng cấu hình có đủ ba bản ghi và 0 cảnh báo phù hợp với mẫu dưới ngưỡng.

[Hồ sơ CD](tuan_3/results/cd_2026_10_18/) · [Lượt sau sửa cấu hình](tuan_3/results/post_repair_2026_10_18/README.md) · [Email đã được người nhận xác nhận ngày 16/10](docs/scheduled-run-verification.md).

Metric native có cửa sổ Errors cao hơn Invocations, chưa xác định nguyên nhân. Dashboard bỏ các điểm thiếu/không nhất quán thay vì chuyển thành 0. Kết quả lượt đơn lẻ không chứng minh vận hành liên tục nhiều ngày; xác nhận nhận email cũ không thay cho xác nhận thư mới.

## 7. Mã nguồn và commit minh chứng

- [36c9b39 — mã Lambda và sửa xử lý thời gian](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/36c9b3966a8b6f645dc6bb1491ad6e2b40a78765).
- [4a72d02 — đối chiếu triển khai, raw/truy vấn và email](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/4a72d0260ce7fbe5ff681e8ec73d17c03ab8859b).
- [3d6dfee — minh chứng các lượt chạy tự động](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/3d6dfeed922fa9d63d4659419bb75be675429c9a).
- [db6844d — ghi nhận an toàn hai nhánh lỗi triển khai](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/db6844d4b1f94c9ec959ff770840dc993c5a657c).

Các commit được dẫn theo nội dung thực sự thay đổi. Minh chứng runtime và kiểm tra giả lập được ghi riêng trong [hướng dẫn vận hành](tuan_3/docs/operation.md).

## 8. Phân công và tổng giờ sinh viên công bố

| Giai đoạn | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên | Tổng | Căn cứ |
| --- | --- | --- | --- | --- |
| Tuần 1 | 9,5 giờ | 9,0 giờ | 18,5 giờ | Tổng theo tuần đã xác nhận |
| Tuần 2 | 10,0 giờ | 9,5 giờ | 19,5 giờ | Tổng theo tuần đã xác nhận |
| Tuần 3 — công việc tích hợp | 10,0 giờ | 10,0 giờ | 20,0 giờ | Tổng do sinh viên công bố, không phân bổ ngày |
| **Cộng dồn** | **29,5 giờ** | **28,5 giờ** | **58,0 giờ** | Không suy số giờ từ thời gian hệ thống chạy |

Sinh viên Tiến Sơn phụ trách thu thập, cấu hình, triển khai và giám sát/cảnh báo; sinh viên Ngọc Quyên phụ trách Glue/Athena, thống kê và dự báo. Hai sinh viên cùng rà soát tài liệu và số liệu.

[Nhật ký kỹ thuật và tổng giờ Tuần 3](tuan_3/docs/WORKLOG.md) · [CSV Tuần 3](tuan_3/worklog.csv) · [38 giờ Tuần 1–2](worklog.csv). Tổng 20 giờ bổ sung được ghi theo thông tin sinh viên công bố; không tự gán ngày làm hoặc chia thành giờ thực tế của từng đầu việc.

## 9. Kiểm tra, kết luận và phần tiếp tục

Kiểm tra tệp đã lưu: `python tuan_2/scripts/repository_audit.py --check`, `python tuan_3/scripts/verify_results.py`. Bộ hồi quy: `python -m unittest discover -s tuan_3/tests -v`. Các lệnh này không chứng minh dịch vụ AWS hiện tại; [workflow CI](.github/workflows/verify-repository.yml) và [các lượt Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions) ghi kết quả riêng cho từng commit.

Mốc cập nhật có raw mới, thống kê và biểu đồ truy vết được, thử nghiệm dự báo bổ sung và kết quả đối chiếu một phần với dữ liệu mô hình tải về sau. Cần tiếp tục ghi dữ liệu trong kỳ 19–25/10, đối chiếu các giờ đích còn lại và làm rõ metric native. Các kết quả hiện có chưa được dùng để khẳng định độ phủ cả tuần, hiệu quả dự báo tổng quát hoặc mức tiết kiệm chi phí sản xuất.
