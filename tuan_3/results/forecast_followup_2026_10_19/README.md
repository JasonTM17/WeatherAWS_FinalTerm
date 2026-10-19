# Đối chiếu đủ 24 giờ đích, cập nhật ngày 19/10/2026

Nguồn CAMS tải ngày 19/10, cutoff **07:00 UTC (14:00 UTC+7)**. Đã đối chiếu đủ **24/24 giờ đích và 144/144 giá trị**, từ 18/10 07:00 đến 19/10 06:00 UTC. Đây là toàn bộ kỳ dự báo phát hành khoảng 06:24 UTC ngày 18/10, không phải 24 giờ trọn ngày 19/10.

Bản phát hành gốc được giữ nguyên SHA-256 `9ebfd3aca39d6b71c816f42e366d4b7c505c48530df8ce6fdd7096f5e68e159a`. Không dùng các giá trị tải về sau để huấn luyện lại hoặc thay dự báo đã phát hành. Đối chiếu là với dữ liệu mô hình có thể cập nhật hồi cứu, không phải số đo trực tiếp tại trạm.

| Đô thị | Chỉ số | Giờ đối chiếu | MAE | RMSE | Bias |
| --- | --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | US AQI | 24/24 | 10,221 | 10,617 | 10,221 |
| TP. Hồ Chí Minh | PM2.5 (µg/m³) | 24/24 | 6,178 | 6,730 | 6,178 |
| Hà Nội | US AQI | 24/24 | 11,031 | 14,995 | -0,417 |
| Hà Nội | PM2.5 (µg/m³) | 24/24 | 6,619 | 9,906 | -5,163 |
| Đà Nẵng | US AQI | 24/24 | 12,320 | 12,833 | 12,320 |
| Đà Nẵng | PM2.5 (µg/m³) | 24/24 | 3,126 | 3,699 | -1,369 |

MAE/RMSE cùng đơn vị với chỉ số. Bias = trung bình(dự báo − giá trị mô hình tải về sau). Kết quả chỉ mô tả kỳ dự báo này, không xác lập độ chính xác cho các ngày khác.

![Dự báo đã phát hành và dữ liệu tải về sau](issued_vs_later_model.png)

- [144 giá trị đối chiếu](comparison.csv) · [6 bộ sai số](comparison_metrics.csv).
- [Lịch sử mô hình](history.csv) · [Ba phản hồi API nguyên gốc](model_source/) · [Nguồn/cutoff/hash](provenance.json) · [Manifest 8 tệp](manifest.json).
- [Mốc 4/24 giờ ngày 18/10](../forecast_followup_2026_10_18/README.md) được giữ riêng; số của mốc cũ không bị ghi đè.

Tạo lần cập nhật khác: `python tuan_3/scripts/forecast_followup.py --output output/forecast-followup-new`. Dữ liệu mô hình giữa hai lần tải có thể thay đổi, nên kết quả mới có provenance riêng.

[Báo cáo](../../docs/FINAL_REPORT.md) · [Vận hành](../../docs/operation.md).
