# Đối chiếu bản dự báo đã phát hành — cập nhật cutoff 11:00 UTC ngày 18/10/2026

Đã tải lại dữ liệu Open-Meteo/CAMS và đối chiếu **4/24 giờ đích, tương ứng 24/144 giá trị**. Các giờ đã hoàn tất là 07:00–10:00 UTC ngày 18/10, tức 14:00–17:00 UTC+7. Chỉ dùng thời điểm trước cutoff 11:00 UTC. Bản dự báo phát hành lúc khoảng 06:24 UTC và tất cả giá trị dự báo được giữ nguyên; không huấn luyện hoặc phát hành lại để khớp kết quả tải về sau.

## Dữ liệu và nguồn

- [24 giá trị đối chiếu](comparison.csv) · [Sáu bộ sai số](comparison_metrics.csv).
- [537 dòng lịch sử mô hình tải về](history.csv) · [Ba phản hồi API đã lưu](model_source/) · [URL, thời điểm tải, cutoff và SHA-256 bản dự báo gốc](provenance.json).
- [Bản dự báo 144 giá trị đã phát hành](../forecast_issued_2026_10_18/forecast_24h.csv) · [Mốc đối chiếu cũ 2/24 giờ](../refresh_2026_10_18/analysis/later_model/comparison.csv) · [Manifest](manifest.json).

## Sai số trên các giờ đã có dữ liệu

| Đô thị | Chỉ số | Giờ đã đối chiếu | MAE | RMSE | Bias |
| --- | --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | US AQI | 4/24 | 6,727 | 6,734 | 6,727 |
| TP. Hồ Chí Minh | PM2.5 (µg/m³) | 4/24 | 8,960 | 9,063 | 8,960 |
| Hà Nội | US AQI | 4/24 | 15,061 | 16,285 | 5,167 |
| Hà Nội | PM2.5 (µg/m³) | 4/24 | 2,079 | 2,312 | 1,347 |
| Đà Nẵng | US AQI | 4/24 | 12,032 | 12,140 | 12,032 |
| Đà Nẵng | PM2.5 (µg/m³) | 4/24 | 2,235 | 2,335 | 2,235 |

Bias = dự báo trừ giá trị mô hình tải về sau. MAE/RMSE/Bias chỉ mô tả bốn giờ này, không phải độ chính xác của cả 24 giờ hay dữ liệu đo tại trạm. Mô hình CAMS có thể cập nhật hồi cứu; số liệu ở bản tải mới không được ghi đè vào snapshot cũ.

![Dự báo đã phát hành và dữ liệu CAMS tải về sau](issued_vs_later_model.png)

Màu phân biệt ba đô thị; nét liền là dữ liệu mô hình tải về sau, nét đứt là bản dự báo đã phát hành. PNG và bảng sai số đều lấy từ `comparison.csv`.

## Tái lập

Chạy `python tuan_3/scripts/forecast_followup.py --output output/forecast-followup-new` tại gốc repository để tải một mốc mới, không ghi đè thư mục đã có. Chương trình chỉ ghép giờ đích đã hoàn tất, lưu nguồn và không thay tệp dự báo đã phát hành. `python tuan_3/scripts/verify_results.py` kiểm tra lại các giá trị với phản hồi API đã lưu mà không gọi mạng.

[Báo cáo Tuần 3](../../docs/FINAL_REPORT.md#57-cập-nhật-đối-chiếu-giờ-đích-đã-hoàn-tất) · [Vận hành](../../docs/operation.md).
