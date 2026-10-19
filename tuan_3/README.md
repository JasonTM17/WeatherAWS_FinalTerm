# Tuần 3 — Tích hợp, tối ưu truy vấn và giám sát

**Nguyễn Tiến Sơn — 24110054 · Trần Thị Ngọc Quyên — 24110051**

Học phần Điện toán đám mây · GVHD: ThS. Huỳnh Xuân Phụng

Hồ sơ ghi nhận các công việc tích hợp Tuần 3 hoàn thành tại mốc **18/10/2026**, cập nhật dữ liệu ngày **19/10/2026**, tiếp nối [Tuần 1](../tuan_1/README.md) và [Tuần 2](../tuan_2/README.md). Kết quả gồm dữ liệu raw từ S3, tối ưu Athena, giám sát, dự báo và CI/CD; mỗi bộ dữ liệu giữ thời điểm và đầu vào tương ứng.

## Hồ sơ và minh chứng

| Nội dung | Liên kết |
| --- | --- |
| Báo cáo kỹ thuật, kết quả và phương pháp | [Báo cáo chi tiết](docs/FINAL_REPORT.md) · [Nội dung nộp LMS](../BAO_CAO.md) |
| Dữ liệu ngày 19/10 và raw tích lũy mới | [45/42 dòng trong ngày, 302/339 dòng tích lũy, 95 JSON gốc](results/daily_update_2026_10_19/README.md) |
| Đối chiếu đủ kỳ dự báo | [24/24 giờ đích, 144/144 giá trị và nguồn CAMS tải ngày 19/10](results/forecast_followup_2026_10_19/README.md) |
| Hướng dẫn chạy, kiểm chứng và khôi phục | [Vận hành và CI/CD](docs/operation.md) |
| Nhật ký kỹ thuật, phân công và tổng giờ đã xác nhận | [Nhật ký Tuần 3](docs/WORKLOG.md) · [CSV tổng giờ](worklog.csv) · [Bản CSV trong hồ sơ](docs/worklog.csv) |
| Raw dùng cho thống kê và biểu đồ đã lưu | [Sinh viên Tiến Sơn — 246 dòng](results/refresh_2026_10_18/snapshot/default/raw_all.csv) · [Sinh viên Ngọc Quyên — 285 dòng](results/refresh_2026_10_18/snapshot/quyen/raw_all.csv) |
| Bản xuất raw ngày 18/10: CSV và JSON gốc | [Sinh viên Tiến Sơn — 246 dòng](results/raw_export_2026_10_18/snapshot/default/raw_all.csv) · [Sinh viên Ngọc Quyên — 288 dòng](results/raw_export_2026_10_18/snapshot/quyen/raw_all.csv) · [83 JSON, chất lượng và SHA-256](results/raw_export_2026_10_18/README.md) |
| Raw của mốc tích hợp ban đầu | [Sinh viên Tiến Sơn](results/integration_2026_10_18/snapshot/default/raw_all.csv) · [Sinh viên Ngọc Quyên](results/integration_2026_10_18/snapshot/quyen/raw_all.csv) |
| Chất lượng và thống kê theo giờ của snapshot cập nhật | [Sinh viên Tiến Sơn](results/refresh_2026_10_18/snapshot/default/) · [Sinh viên Ngọc Quyên](results/refresh_2026_10_18/snapshot/quyen/) |
| Truy vấn, số đo Athena và cấu hình Projection | [Thí nghiệm Athena](results/integration_2026_10_18/benchmark/) |
| Dashboard JSON, metric CSV và ảnh do AWS trả về | [Giám sát CloudWatch](results/integration_2026_10_18/dashboard/) |
| Dashboard cập nhật và đối chiếu bộ đếm | [Mốc giám sát bổ sung](results/monitoring_2026_10_18/) |
| Metric Filters, cấu hình JSON và đối chiếu log–S3 | [Hồ sơ vận hành bổ sung](results/operations_2026_10_18/) |
| Lượt tự động sau sửa cấu hình của sinh viên Ngọc Quyên | [Log, ba bản ghi raw và metric lúc 13:51](results/post_repair_2026_10_18/README.md) |
| CD thật, hash đọc lại từ AWS và dọn secrets | [Hồ sơ triển khai hai môi trường](results/cd_2026_10_18/) |
| Dữ liệu mô hình, dự báo và sai số | [Hồ sơ dự báo](results/integration_2026_10_18/forecast/) |
| Dự báo đã kiểm tra giờ đích sau phát hành | [Bản phát hành dự báo mới](results/forecast_issued_2026_10_18/) |
| Tính toàn vẹn các tệp kết quả | [Manifest mốc đầu](results/integration_2026_10_18/manifest.json) · [Manifest snapshot cập nhật](results/refresh_2026_10_18/manifest.json) · [Kiểm tra toàn bộ các mốc](scripts/verify_results.py) |
| Kế hoạch tiếp theo | [Tuần 4: phân công, sản phẩm và tiêu chí nghiệm thu](../docs/WEEK_4_PLAN.md) |
| Kiểm tra tự động và triển khai | [CI](../.github/workflows/verify-repository.yml) · [Workflow triển khai Lambda](../.github/workflows/week3-release.yml) · [Các lượt Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions) |

## Kết quả cập nhật mới nhất

**Đã hoàn thành kế hoạch công việc tích hợp Tuần 3 tại mốc ngày 18/10/2026.**

- **Bản xuất ngày 19/10: 302/339 bản ghi tích lũy, riêng trong ngày 45/42 bản ghi và 95 JSON gốc.** [Raw, nguồn từng bản ghi và thống kê trên cùng 14 giờ hoàn tất](results/daily_update_2026_10_19/README.md).

- Snapshot phân tích đã lưu: **246 bản ghi của sinh viên Tiến Sơn** và **285 bản ghi của sinh viên Ngọc Quyên**; bảy nhóm kiểm tra chất lượng đều bằng 0.
- [Raw, thống kê và ba biểu đồ màu của mốc 18/10](results/refresh_2026_10_18/README.md).
- Mốc raw ngày 18/10 được lưu giữ riêng: [246/288 dòng, 83 JSON gốc và bảng mẫu](results/raw_export_2026_10_18/README.md).
- Đã đối chiếu đủ **24/24 giờ đích, 144/144 giá trị**, giữ nguyên bản dự báo phát hành. [Nguồn, sai số và biểu đồ ngày 19/10](results/forecast_followup_2026_10_19/README.md).
- Đã đối chiếu số liệu theo timestamp và kiểm chứng biểu thức Dashboard; [hai API/dimension/chu kỳ và log](results/monitoring_followup_2026_10_18/README.md) được kiểm tra, [cấu hình Dashboard](results/monitoring_dashboard_repair_2026_10_18/README.md) đã đọc lại khớp trong cả hai môi trường. Tỷ lệ được tính theo các khoảng có đủ cặp Errors/Invocations hợp lệ, có bảng đối chiếu theo thời gian.

## Dữ liệu bổ sung ngày 19/10

Hai lượt Lambda backfill đã thu đủ 14 giờ hoàn tất cho ba đô thị, mỗi lượt 42 bản ghi và 0 cảnh báo lịch sử. Số liệu ngày 19/10 được tách khỏi các snapshot cũ. Thống kê dùng 00:00–13:00 UTC+7; ba bản ghi trong giờ đang diễn ra của sinh viên Tiến Sơn chỉ nằm trong raw.

![AQI và PM2.5 ngày 19/10](results/daily_update_2026_10_19/daily_aqi_pm25.png)

[CSV ngày 19/10 và nguồn từng bản ghi](results/daily_update_2026_10_19/README.md) · [Đối chiếu đủ kỳ dự báo](results/forecast_followup_2026_10_19/README.md).

## Kết quả chính tại mốc tích hợp ban đầu

- Chụp lại **237 bản ghi của sinh viên Tiến Sơn** và **273 bản ghi của sinh viên Ngọc Quyên**. Bộ kiểm tra không phát hiện lỗi trong bảy nhóm kiểm tra đã khai báo; giữ nguyên các lượt thu thập và các tệp lịch sử.
- Thực hiện **18 truy vấn Athena**, gồm ba lần đo cho mỗi định dạng trong mỗi môi trường. Kết quả tổng hợp theo đô thị khớp với dữ liệu đầu vào. Hai bảng Projection trong mỗi môi trường có **0 phân vùng đăng ký**.
- Tạo Dashboard `WeatherAirQuality-Week3` trong hai môi trường, đọc lại cấu hình khớp với cấu hình gửi đi; lưu CSV metric và **10 ảnh biểu đồ do CloudWatch trả về**.
- Đánh giá ba phương pháp dự báo trên cùng 24 giờ giữ lại cho mỗi đô thị/chỉ số. Bản bổ sung kiểm tra `issued_at_utc`, lưu **144 giá trị cho 24 giờ đích sau phát hành**; chưa đánh giá bằng dữ liệu tương lai. Bản đầu có sáu giờ đích sớm hơn thời điểm lấy nguồn và đã được ghi rõ giới hạn.
- Giữ cảnh báo **qua email** theo phạm vi đã thống nhất. Minh chứng nhận email của hai sinh viên được ghi tại [đợt chạy tự động ngày 16/10](../docs/scheduled-run-verification.md).
- Đã chạy CD thành công cho [sinh viên Tiến Sơn](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101930450) và [sinh viên Ngọc Quyên](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101934718) ở commit `c28da19`; gói tải lại từ AWS khớp artifact CI, cấu hình giữ nguyên. Secrets tạm đã được xóa sau kiểm chứng.
- Đã đối chiếu [lượt tự động 13:51 sau sửa cấu hình của sinh viên Ngọc Quyên](results/post_repair_2026_10_18/README.md): đủ ba đô thị, ba bản ghi khớp S3, một điểm metric log mới, không thấy thông báo đọc Secret thất bại trong cửa sổ đã kiểm tra. Ba mẫu dưới ngưỡng nên không phát cảnh báo mới.


### Thống kê snapshot cập nhật theo đô thị–giờ

Mỗi giờ có trọng số bằng nhau sau khi lấy trung bình các lượt thu trong cùng đô thị–giờ. Các giá trị dưới đây dùng snapshot mới 246/285 dòng; bộ đầu vào benchmark cũ được giữ riêng.

| Sinh viên | Đô thị | N giờ | AQI TB | ĐLC mẫu AQI | PM2.5 TB (µg/m³) |
| --- | --- | --- | --- | --- | --- |
| Sinh viên Tiến Sơn | TP. Hồ Chí Minh | 78 | 102,346 | 21,258 | 33,151 |
| Sinh viên Tiến Sơn | Hà Nội | 78 | 88,769 | 36,066 | 28,460 |
| Sinh viên Tiến Sơn | Đà Nẵng | 78 | 68,154 | 27,018 | 13,749 |
| Sinh viên Ngọc Quyên | TP. Hồ Chí Minh | 76 | 103,039 | 21,736 | 33,054 |
| Sinh viên Ngọc Quyên | Hà Nội | 76 | 87,947 | 36,102 | 30,005 |
| Sinh viên Ngọc Quyên | Đà Nẵng | 76 | 67,526 | 27,854 | 13,261 |

[Thống kê đủ tám biến, raw và theo giờ](results/refresh_2026_10_18/analysis/descriptive.csv).

![AQI theo giờ từ raw mới](results/refresh_2026_10_18/analysis/city_hour_aqi.png)

#### Tương quan theo giờ với PM2.5

| Sinh viên | Đô thị | Pearson r: nhiệt độ | Pearson r: độ ẩm | Pearson r: gió |
| --- | --- | --- | --- | --- |
| Sinh viên Tiến Sơn | TP. Hồ Chí Minh | -0,589 | 0,604 | -0,433 |
| Sinh viên Tiến Sơn | Hà Nội | 0,214 | 0,079 | -0,656 |
| Sinh viên Tiến Sơn | Đà Nẵng | 0,465 | -0,371 | -0,141 |
| Sinh viên Ngọc Quyên | TP. Hồ Chí Minh | -0,567 | 0,577 | -0,459 |
| Sinh viên Ngọc Quyên | Hà Nội | 0,140 | 0,121 | -0,672 |
| Sinh viên Ngọc Quyên | Đà Nẵng | 0,510 | -0,406 | -0,086 |

Hệ số Pearson/Spearman mô tả mức liên hệ trong tập phân tích, có số nhóm giờ và cách xử lý đồng hạng đi kèm. [Đủ hai hệ số và hai chỉ số đích](results/refresh_2026_10_18/analysis/correlations.csv).

![Ma trận liên hệ theo giờ](results/refresh_2026_10_18/analysis/hourly_correlations.png)


### Truy vấn Athena trên cùng dữ liệu

| Cấu hình truy vấn Athena | Byte quét trung vị — sinh viên Tiến Sơn | Byte quét trung vị — sinh viên Ngọc Quyên | Engine trung vị — sinh viên Tiến Sơn (ms) | Engine trung vị — sinh viên Ngọc Quyên (ms) |
| --- | ---: | ---: | ---: | ---: |
| NDJSON, phân vùng đăng ký | 1.556 | 11.243 | 615 | 572 |
| NDJSON, Partition Projection | 1.556 | 11.243 | 537 | 431 |
| Parquet Snappy, Partition Projection | 302 | 393 | 452 | 515 |

Dấu chấm trong hai cột byte phân cách hàng nghìn. Parquet giảm byte quét 80,59% trong báo cáo dữ liệu của sinh viên Tiến Sơn và 96,50% trong báo cáo dữ liệu của sinh viên Ngọc Quyên. Các trung vị planning/total và từng lượt được lưu trong [bảng đo gốc](results/integration_2026_10_18/benchmark/); chi phí thực hành được theo dõi riêng bằng Cost Explorer.

#### Kết quả truy vấn tổng hợp ba đô thị

| Sinh viên | Đô thị | Số mẫu của truy vấn | AQI TB | PM2.5 TB |
| --- | --- | --- | --- | --- |
| Sinh viên Tiến Sơn | Đà Nẵng | 1 | 53,000 | 11,400 |
| Sinh viên Tiến Sơn | Hà Nội | 1 | 87,000 | 23,200 |
| Sinh viên Tiến Sơn | TP. Hồ Chí Minh | 1 | 66,000 | 9,800 |
| Sinh viên Ngọc Quyên | Đà Nẵng | 7 | 74,286 | 25,429 |
| Sinh viên Ngọc Quyên | Hà Nội | 7 | 104,000 | 28,871 |
| Sinh viên Ngọc Quyên | TP. Hồ Chí Minh | 7 | 131,143 | 26,043 |

Byte quét, thời gian và planning được đo cho cả truy vấn trả ba đô thị; không chia thành số đo hoặc chi phí riêng của mỗi đô thị. Nguồn: [CSV và query ID](results/integration_2026_10_18/benchmark/).


![Lượng byte được Athena quét](results/integration_2026_10_18/benchmark_scan.png)

*Trung vị của ba lần đo, tắt sử dụng lại kết quả. CSV từng lượt: [sinh viên Tiến Sơn](results/integration_2026_10_18/benchmark/default/benchmark.csv), [sinh viên Ngọc Quyên](results/integration_2026_10_18/benchmark/quyen/benchmark.csv). Mỗi môi trường dùng ngày có dữ liệu gần nhất của chính môi trường đó; không dùng biểu đồ để so tốc độ giữa hai sinh viên.*

Projection trên cùng NDJSON giữ nguyên byte quét; Parquet giảm byte quét theo kết quả trong bảng. Thời gian engine được đánh giá riêng: với sinh viên Ngọc Quyên, trung vị Parquet là 515 ms, so với 431 ms của NDJSON Projection. Mỗi số đo gắn với cấu hình, bộ đầu vào và ba lượt chạy trong môi trường tương ứng.

### Giám sát dịch vụ thật

Dashboard tổng hợp số lần gọi, thời gian thực thi, thông báo SNS và lịch thu thập. Cấu hình của hai môi trường đã được đọc lại khớp; [hồ sơ kiểm chứng và ảnh metric do AWS trả về](results/monitoring_dashboard_repair_2026_10_18/README.md) được lưu để đối chiếu.

Số liệu giám sát được đối chiếu trước khi tính tỷ lệ: hai khoảng hợp lệ của sinh viên Tiến Sơn và ba khoảng của sinh viên Ngọc Quyên, trong cửa sổ 07:40–10:40 UTC ngày 18/10. [Bộ đếm, số request và phương pháp tính](docs/FINAL_REPORT.md#43-kiểm-chứng-số-liệu-giám-sát).

### Đối chiếu dự báo với dữ liệu giữ lại

![Đánh giá AQI trên 24 giờ giữ lại](results/integration_2026_10_18/forecast/holdout_us_aqi.png)

*Dữ liệu mô hình Open-Meteo/CAMS; đường tham chiếu là giá trị mô hình trong 24 giờ giữ lại. Kết quả từng phương pháp được tính riêng theo đô thị/chỉ số. [Sai số đầy đủ](results/integration_2026_10_18/forecast/forecast_metrics.csv) · [Giá trị từng giờ](results/integration_2026_10_18/forecast/holdout_predictions.csv).*

#### Thử nghiệm MA 3 giờ bổ sung trên cùng tập giữ lại

| Đô thị | Chỉ số | MAE nhỏ nhất trong bốn phương pháp | MAE | RMSE của phương pháp đó | MAE MA 3 giờ | MAE MA 24 giờ |
| --- | --- | --- | --- | --- | --- | --- |
| TP. Hồ Chí Minh | US AQI | persistence | 6,125 | 6,674 | 6,296 | 25,781 |
| TP. Hồ Chí Minh | PM2.5 | persistence | 3,271 | 4,233 | 3,442 | 5,734 |
| Hà Nội | US AQI | seasonal_naive_24h | 5,292 | 6,228 | 11,333 | 13,204 |
| Hà Nội | PM2.5 | persistence | 4,025 | 5,306 | 4,168 | 7,535 |
| Đà Nẵng | US AQI | persistence | 5,458 | 6,201 | 5,630 | 12,598 |
| Đà Nẵng | PM2.5 | seasonal_naive_24h | 6,712 | 8,171 | 11,600 | 6,779 |

MA 3 giờ là phân tích khám phá bổ sung sau khi xem kết quả giữ lại, sử dụng cùng tập đánh giá để đối chiếu các cửa sổ trung bình trượt. [24 bộ sai số và nguồn](results/refresh_2026_10_18/analysis/ma_comparison_metrics.csv).

![So sánh MA 3/24 giờ và cơ sở](results/refresh_2026_10_18/analysis/holdout_ma_comparison.png)

**Mốc lịch sử ngày 18/10, cutoff 11:00 UTC:** đã so được 4/24 giờ đích (24/144 giá trị) với dữ liệu CAMS tải về sau. [CSV và nguồn của mốc lịch sử](results/forecast_followup_2026_10_18/README.md).

![Đối chiếu bốn giờ đích](results/forecast_followup_2026_10_18/issued_vs_later_model.png)

**Cập nhật mới nhất ngày 19/10, cutoff 07:00 UTC:** đã đối chiếu đủ **24/24 giờ đích, 144/144 giá trị**, giữ nguyên bản dự báo phát hành ngày 18/10. [CSV, sai số và nguồn của kết quả đủ kỳ](results/forecast_followup_2026_10_19/README.md).

![Đối chiếu đủ kỳ dự báo](results/forecast_followup_2026_10_19/issued_vs_later_model.png)


## Mã nguồn và kiểm tra

| Chương trình | Trách nhiệm |
| --- | --- |
| [snapshot.py](scripts/snapshot.py), [quality.py](scripts/quality.py) | Đọc raw từ S3, kiểm tra lược đồ/số/thời gian, lưu thống kê theo đô thị–giờ |
| [benchmark.py](scripts/benchmark.py) | Tạo dữ liệu thử nghiệm NDJSON/Parquet riêng, cấu hình Projection, đo và đối chiếu truy vấn |
| [dashboard.py](scripts/dashboard.py) | Tạo Dashboard riêng, xuất metric và ảnh CloudWatch |
| [metric_filters.py](scripts/metric_filters.py), [check_operations.py](scripts/check_operations.py) | Kiểm tra mẫu và tạo bộ đếm log; đối chiếu kết quả với S3, lịch/quyền gọi và ngưỡng cảnh báo |
| [monitoring_followup.py](scripts/monitoring_followup.py) | Ghép metric theo khoảng, đối chiếu hai API/dimension/chu kỳ với lifecycle log, kiểm tra biểu thức metric math chỉ đọc và cập nhật Dashboard có sao lưu |
| [forecast_followup.py](scripts/forecast_followup.py) | Giữ nguyên dự báo đã phát hành, tải nguồn mô hình mới và tính sai số trên các giờ đích đã hoàn tất |
| [forecast.py](scripts/forecast.py) | Thu dữ liệu mô hình theo giờ, chia tập theo thời gian, dự báo và tính sai số |
| [release.py](scripts/release.py) | Đóng gói xác định, kiểm tra tài khoản, triển khai chỉ mã, xác minh và khôi phục có kiểm soát phiên bản |
| [daily_snapshot.py](scripts/daily_snapshot.py) | Chọn ngày UTC+7 từ S3 đã xuất, giữ provenance, thống kê theo giờ đã hoàn tất và vẽ biểu đồ |
| [verify_results.py](scripts/verify_results.py) | Đối chiếu hash, raw, kết quả Athena và sai số đã lưu mà không gọi AWS |
| [reconcile_analysis.py](scripts/reconcile_analysis.py) | Tính thống kê raw/theo giờ, tương quan, thử nghiệm MA 3 giờ và đối chiếu bản phát hành với dữ liệu mô hình tải về sau |
| [test_week3.py](tests/test_week3.py) | Các kiểm tra hồi quy về dữ liệu, thời gian, dự báo và an toàn triển khai |

```bash
python -m pip install -r tuan_3/requirements.txt
python -m unittest discover -s tuan_3/tests -v
python tuan_3/scripts/verify_results.py
```

Các lệnh trên kiểm tra mã và tính nhất quán của hồ sơ đã lưu; minh chứng AWS được liên kết theo từng mốc thực thi. Cách chạy các chương trình có thao tác AWS và điều kiện khôi phục được trình bày trong [hướng dẫn vận hành](docs/operation.md).


### Tổng giờ đã xác nhận

| Giai đoạn | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên | Tổng | Căn cứ |
| --- | --- | --- | --- | --- |
| Tuần 1 | 9,5 giờ | 9,0 giờ | 18,5 giờ | Tổng theo tuần đã xác nhận |
| Tuần 2 | 10,0 giờ | 9,5 giờ | 19,5 giờ | Tổng theo tuần đã xác nhận |
| Tuần 3 — công việc tích hợp | 10,0 giờ | 10,0 giờ | 20,0 giờ | Tổng theo tuần đã xác nhận |
| **Cộng dồn** | **29,5 giờ** | **28,5 giờ** | **58,0 giờ** | Tổng theo tuần đã xác nhận |

38,0 giờ thuộc hồ sơ Tuần 1–2; 20,0 giờ Tuần 3 là tổng theo tuần đã xác nhận, không phân bổ ngày. [Hai dòng CSV tổng giờ Tuần 3](worklog.csv) ghi căn cứ này riêng với các mốc kỹ thuật trong nhật ký.

## Kế hoạch Tuần 4

[Kế hoạch W4-01–W4-08](../docs/WEEK_4_PLAN.md) tiếp nối kết quả tích hợp Tuần 3: thu raw theo ngày, đối chiếu CloudWatch/log–S3, kiểm chứng cảnh báo email, đo Athena và đánh giá thêm ba kỳ dự báo có thời điểm phát hành. Sinh viên Tiến Sơn phụ trách vận hành/triển khai/giám sát; sinh viên Ngọc Quyên phụ trách truy vấn/phân tích/dự báo; hai sinh viên cùng rà soát hồ sơ và nhật ký.

Kế hoạch có lịch đề xuất 26/10–01/11/2026, đầu ra, phụ thuộc và tiêu chí nghiệm thu cho từng đầu việc. [Nhật ký Tuần 3](docs/WORKLOG.md) giữ tổng giờ đã xác nhận; sản phẩm và giờ công Tuần 4 sẽ cập nhật theo công việc thực hiện.
