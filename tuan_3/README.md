# Tuần 3 — Tích hợp, tối ưu truy vấn và giám sát

**Nguyễn Tiến Sơn — 24110054 · Trần Thị Ngọc Quyên — 24110051**

Học phần Điện toán đám mây · GVHD: ThS. Huỳnh Xuân Phụng

Hồ sơ này ghi nhận mốc tích hợp ngày **18/10/2026**, tiếp nối [Tuần 1](../tuan_1/README.md) và [Tuần 2](../tuan_2/README.md). Tuần 3 theo lịch báo cáo là **19–25/10/2026 (UTC+7)**. Vì thời điểm chụp dữ liệu còn trước tuần này, các kết quả dưới đây là kết quả triển khai và thử nghiệm chuẩn bị; chưa phải thống kê môi trường của toàn Tuần 3.

## Hồ sơ và minh chứng

| Nội dung | Liên kết |
| --- | --- |
| Báo cáo kỹ thuật, phương pháp và giới hạn | [Báo cáo chi tiết](docs/FINAL_REPORT.md) |
| Hướng dẫn chạy, kiểm chứng và khôi phục | [Vận hành và CI/CD](docs/operation.md) |
| Nhật ký có minh chứng, phân công và kế hoạch thời gian | [Nhật ký và kế hoạch Tuần 3](docs/WORKLOG.md) · [CSV tổng hợp](worklog.csv) · [CSV chi tiết](docs/worklog.csv) |
| Dữ liệu thô của từng sinh viên | [Sinh viên Tiến Sơn](results/integration_2026_10_18/snapshot/default/raw_all.csv) · [Sinh viên Ngọc Quyên](results/integration_2026_10_18/snapshot/quyen/raw_all.csv) |
| Chất lượng và thống kê theo giờ | [Sinh viên Tiến Sơn](results/integration_2026_10_18/snapshot/default/) · [Sinh viên Ngọc Quyên](results/integration_2026_10_18/snapshot/quyen/) |
| Truy vấn, số đo Athena và cấu hình Projection | [Thí nghiệm Athena](results/integration_2026_10_18/benchmark/) |
| Dashboard JSON, metric CSV và ảnh do AWS trả về | [Giám sát CloudWatch](results/integration_2026_10_18/dashboard/) |
| Dashboard cập nhật và đối chiếu bộ đếm | [Mốc giám sát bổ sung](results/monitoring_2026_10_18/) |
| Metric Filters, cấu hình JSON và đối chiếu log–S3 | [Hồ sơ vận hành bổ sung](results/operations_2026_10_18/) |
| Lượt tự động sau sửa cấu hình của sinh viên Ngọc Quyên | [Log, ba bản ghi raw và metric lúc 13:51](results/post_repair_2026_10_18/README.md) |
| CD thật, hash đọc lại từ AWS và dọn secrets | [Hồ sơ triển khai hai môi trường](results/cd_2026_10_18/) |
| Dữ liệu mô hình, dự báo và sai số | [Hồ sơ dự báo](results/integration_2026_10_18/forecast/) |
| Dự báo đã kiểm tra giờ đích sau phát hành | [Bản phát hành dự báo mới](results/forecast_issued_2026_10_18/) |
| Tính toàn vẹn các tệp kết quả | [Manifest SHA-256](results/integration_2026_10_18/manifest.json) |
| Kiểm tra tự động và triển khai | [CI](../.github/workflows/verify-repository.yml) · [Workflow triển khai Lambda](../.github/workflows/week3-release.yml) · [Các lượt Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions) |

## Kết quả chính

- Chụp lại **237 bản ghi của sinh viên Tiến Sơn** và **273 bản ghi của sinh viên Ngọc Quyên**. Bộ kiểm tra không phát hiện lỗi trong bảy nhóm kiểm tra đã khai báo; giữ nguyên các lượt thu thập và các tệp lịch sử.
- Thực hiện **18 truy vấn Athena**, gồm ba lần đo cho mỗi định dạng trong mỗi môi trường. Kết quả tổng hợp theo đô thị khớp với dữ liệu đầu vào. Hai bảng Projection trong mỗi môi trường có **0 phân vùng đăng ký**.
- Tạo Dashboard `WeatherAirQuality-Week3` trong hai môi trường, đọc lại cấu hình khớp với cấu hình gửi đi; lưu CSV metric và **10 ảnh biểu đồ do CloudWatch trả về**.
- Đánh giá ba phương pháp dự báo trên cùng 24 giờ giữ lại cho mỗi đô thị/chỉ số. Bản bổ sung kiểm tra `issued_at_utc`, lưu **144 giá trị cho 24 giờ đích sau phát hành**; chưa đánh giá bằng dữ liệu tương lai. Bản đầu có sáu giờ đích sớm hơn thời điểm lấy nguồn và đã được ghi rõ giới hạn.
- Giữ cảnh báo **qua email** theo phạm vi đã thống nhất. Minh chứng nhận email của hai sinh viên được ghi tại [đợt chạy tự động ngày 16/10](../docs/scheduled-run-verification.md).
- Đã chạy CD thành công cho [sinh viên Tiến Sơn](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101930450) và [sinh viên Ngọc Quyên](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101934718) ở commit `c28da19`; gói tải lại từ AWS khớp artifact CI, cấu hình giữ nguyên. Secrets tạm đã được xóa sau kiểm chứng.
- Đã đối chiếu [lượt tự động 13:51 sau sửa cấu hình của sinh viên Ngọc Quyên](results/post_repair_2026_10_18/README.md): đủ ba đô thị, ba bản ghi khớp S3, một điểm metric log mới, không thấy thông báo đọc Secret thất bại trong cửa sổ đã kiểm tra. Ba mẫu dưới ngưỡng nên không phát cảnh báo mới.


### Bảng tổng hợp số liệu môi trường & Thống kê mô tả (3 đô thị)

*Tổng hợp trên 237 bản ghi (Tiến Sơn) và 273 bản ghi (Ngọc Quyên); phân bổ đồng đều 79 và 91 bản ghi cho mỗi đô thị.*

| Đô thị | Môi trường dữ liệu | Số bản ghi (N) | US AQI (Mean ± Std) | PM2.5 (Mean ± Std, µg/m³) | Nhiệt độ (Mean, °C) | Độ ẩm (Mean, %) | Tốc độ gió (Mean, km/h) | Tỷ lệ vượt ngưỡng AQI ≥ 100 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Hà Nội** | Tiến Sơn (`default`) | 79 | 88.04 ± 36.21 | 29.02 ± 24.26 | 25.53 °C | 74.59 % | 9.69 km/h | **24.05%** (19/79) |
| **Hà Nội** | Ngọc Quyên (`quyen`) | 91 | 99.97 ± 42.12 | 39.08 ± 37.74 | 26.16 °C | 73.78 % | 9.40 km/h | **42.86%** (39/91) |
| **TP.HCM** | Tiến Sơn (`default`) | 79 | 104.67 ± 20.21 | 34.27 ± 11.94 | 27.80 °C | 84.16 % | 4.45 km/h | **65.82%** (52/79) |
| **TP.HCM** | Ngọc Quyên (`quyen`) | 91 | 102.82 ± 21.55 | 32.39 ± 12.06 | 27.95 °C | 83.51 % | 4.51 km/h | **56.04%** (51/91) |
| **Đà Nẵng**| Tiến Sơn (`default`) | 79 | 69.18 ± 26.68 | 13.88 ± 8.73 | 28.09 °C | 78.41 % | 8.19 km/h | **8.86%** (7/79) |
| **Đà Nẵng**| Ngọc Quyên (`quyen`) | 91 | 64.34 ± 27.59 | 12.79 ± 9.06 | 27.97 °C | 78.96 % | 7.74 km/h | **7.69%** (7/91) |

#### Ma trận tương quan giữa khí tượng và ô nhiễm (Pearson r & Spearman rho)

| Đô thị / Môi trường | Yếu tố khí tượng | Pearson $r$ với PM2.5 | Spearman $\rho$ với PM2.5 | Pearson $r$ với US AQI | Spearman $\rho$ với US AQI | Đánh giá hiện tượng môi trường |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| **Hà Nội (`default`)** | Tốc độ gió (10m) | **-0.6564** | **-0.6908** | **-0.5679** | **-0.5546** | Gió mạnh giúp xáo trộn khí quyển, giải tán bụi mịn |
| **Hà Nội (`default`)** | Khí CO | **+0.6057** | **+0.4882** | +0.1568 | +0.0138 | Đồng phát thải từ phương tiện giao thông và đốt nhiên liệu |
| **Hà Nội (`default`)** | Nhiệt độ (2m) | +0.2119 | +0.3483 | **+0.6303** | **+0.6670** | Nhiệt độ ban ngày kích hoạt quang hóa Ozone và AQI |
| **TP.HCM (`default`)** | Độ ẩm tương đối | **+0.6649** | **+0.7374** | +0.1274 | +0.1647 | Độ ẩm cao cản trở đối lưu, làm hạt bụi trương nở ngậm nước |
| **TP.HCM (`default`)** | Nhiệt độ (2m) | **-0.6495** | **-0.7209** | -0.0686 | -0.1642 | Mưa rào nhiệt đới làm giảm nhiệt độ và rửa trôi bụi bề mặt |
| **TP.HCM (`default`)** | Khí Ozone ($O_3$) | **-0.5534** | **-0.6691** | +0.1352 | +0.0856 | Tương quan nghịch với bụi do cạnh tranh bức xạ |
| **Đà Nẵng (`default`)** | Nhiệt độ (2m) | **+0.4795** | **+0.5009** | **+0.4394** | **+0.4296** | Nắng nóng thúc đẩy phản ứng quang hóa Ozone ven biển |
| **Đà Nẵng (`default`)** | Độ ẩm tương đối | -0.3898 | -0.4253 | -0.4345 | -0.3977 | Gió biển ẩm cao giúp không khí trong lành hơn |
| **Hà Nội (`quyen`)** | Tốc độ gió (10m) | **-0.7246** | **-0.7541** | **-0.7638** | **-0.7872** | Tương quan nghịch cực kỳ chặt chẽ trên tập mẫu mở rộng 91 quan trắc |
| **Hà Nội (`quyen`)** | Khí CO | **+0.7270** | **+0.5242** | +0.1676 | +0.2569 | Khẳng định quy luật đồng phát thải khí đốt đô thị |
| **TP.HCM (`quyen`)** | Độ ẩm tương đối | **+0.6308** | **+0.7105** | +0.0703 | +0.0416 | Thống nhất cao với kết luận của môi trường default |
| **Đà Nẵng (`quyen`)** | Nhiệt độ (2m) | **+0.5538** | **+0.7136** | **+0.5116** | **+0.5617** | Khẳng định quy luật nhiệt độ - quang hóa đối lưu ven biển |

*(Bảng đầy đủ 30 phép đo tương quan 5 biến x 3 đô thị x 2 môi trường được trình bày chi tiết tại [FINAL_REPORT.md](docs/FINAL_REPORT.md)).*

### Truy vấn Athena trên cùng dữ liệu

| Cấu hình truy vấn Athena | Scanned trung vị Tiến Sơn | Scanned trung vị Ngọc Quyên | Engine Time trung vị Tiến Sơn | Engine Time trung vị Ngọc Quyên | Mức giảm Scanned Bytes | Chi phí quét lý thuyết / query |
| --- | ---: | ---: | ---: | ---: | :---: | ---: |
| **Raw NDJSON (Registered)** | 1.52 KB | 10.98 KB | 615 ms | 572 ms | Mốc cơ sở (0%) | $0.00000001 – $0.00000006 |
| **NDJSON (Partition Projection)**| 1.52 KB | 10.98 KB | 537 ms | 431 ms | 0.00% (Giảm 48-66% Planning ms) | $0.00000001 – $0.00000006 |
| **Parquet Snappy (Projection)** | **0.29 KB** | **0.38 KB** | **452 ms** | **515 ms** | **Giảm 80.59% – 96.50%** | **$0.0000000015 – $0.0000000020** |

#### Kết quả truy vấn tổng hợp 3 đô thị (Hà Nội, TP.HCM, Đà Nẵng)

| Đô thị | Môi trường đo | Số mẫu (N) | US AQI trung bình | PM2.5 trung bình (µg/m³) | Data Scanned Parquet tương đương |
| --- | --- | :---: | ---: | ---: | ---: |
| **Hà Nội** | Tiến Sơn (18/10) / Quyên (16/10) | 1 / 7 | 87.00 / 104.00 | 23.20 / 28.87 | 100.7 B / 131.0 B |
| **TP. Hồ Chí Minh** | Tiến Sơn (18/10) / Quyên (16/10) | 1 / 7 | 66.00 / 131.14 | 9.80 / 26.04 | 100.7 B / 131.0 B |
| **Đà Nẵng** | Tiến Sơn (18/10) / Quyên (16/10) | 1 / 7 | 53.00 / 74.29 | 11.40 / 25.43 | 100.7 B / 131.0 B |

![Lượng byte được Athena quét](results/integration_2026_10_18/benchmark_scan.png)

*Trung vị của ba lần đo, tắt sử dụng lại kết quả. CSV từng lượt: [sinh viên Tiến Sơn](results/integration_2026_10_18/benchmark/default/benchmark.csv), [sinh viên Ngọc Quyên](results/integration_2026_10_18/benchmark/quyen/benchmark.csv). Mỗi môi trường dùng ngày có dữ liệu gần nhất của chính môi trường đó; không dùng biểu đồ để so tốc độ giữa hai sinh viên.*

Parquet giảm byte quét trong thử nghiệm nhỏ này. Projection trên cùng NDJSON giữ nguyên byte quét. Thời gian thực thi không giảm đồng đều: trong báo cáo dữ liệu của sinh viên Ngọc Quyên, trung vị Parquet là 515 ms, cao hơn Projection NDJSON 431 ms. Các số đo này chưa đủ để kết luận tiết kiệm chi phí hoặc hiệu năng ở quy mô lớn.

### Giám sát dịch vụ thật

![Metric Lambda của sinh viên Tiến Sơn](results/monitoring_2026_10_18/default/cloudwatch_01.png)

*Ảnh do API `GetMetricWidgetImage` của AWS tạo từ metric dịch vụ; đây là ảnh chụp số liệu tại cửa sổ đã lưu, không phải ảnh màn hình Console hay biểu đồ giả lập. [CSV metric](results/monitoring_2026_10_18/default/metrics.csv) · [Cấu hình Dashboard](results/monitoring_2026_10_18/default/dashboard.json).*

Metric còn điểm bất thường: tổng Errors cao hơn Invocations trong cả hai môi trường. Mốc bổ sung đã lưu trạng thái chưa tính được tỷ lệ và cập nhật biểu thức Dashboard để bỏ các điểm thiếu hoặc không nhất quán. Đây là vấn đề còn phải đối chiếu, không dùng Dashboard để tuyên bố hệ thống vận hành ổn định. [Giải thích và số liệu](docs/operation.md#5-giới-hạn-của-metric-vận-hành).

### Đối chiếu dự báo với dữ liệu giữ lại

![Đánh giá AQI trên 24 giờ giữ lại](results/integration_2026_10_18/forecast/holdout_us_aqi.png)

*Dữ liệu mô hình Open-Meteo/CAMS; đường thực tế trong phép đánh giá là giá trị mô hình được giữ lại, không phải số đo trạm. Phương pháp trung bình trượt không thắng các phương pháp cơ sở ở mọi trường hợp. [Sai số đầy đủ](results/integration_2026_10_18/forecast/forecast_metrics.csv) · [Giá trị từng giờ](results/integration_2026_10_18/forecast/holdout_predictions.csv).*

#### Đánh giá sai số các mô hình dự báo trên 24 giờ giữ lại (Holdout Errors)

| Đô thị | Biến số | Mô hình tối ưu nhất | MAE tối ưu | RMSE tối ưu | MBE (Bias) | Mô hình trượt ngắn (3-Period MA MAE) | Mô hình trượt ngày (24-Period MA MAE) | Nhận xét độ tin cậy |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| **TP.HCM** | **US AQI** | **Persistence** | **6.13** | **6.67** | +6.13 | 6.30 | 25.78 | AQI TP.HCM biến thiên chậm; Persistence tối ưu |
| **TP.HCM** | **PM2.5** | **Persistence** | **3.27** | **4.23** | -0.58 | 3.44 | 5.73 | Bám sát giá trị quan trắc thực tế |
| **Hà Nội** | **US AQI** | **Seasonal Naive (24h)**| **5.29** | **6.23** | +2.96 | 11.33 | 13.20 | Bắt trúng chu kỳ ngày đêm đặc trưng tại Hà Nội |
| **Hà Nội** | **PM2.5** | **Persistence** | **4.02** | **5.31** | -2.81 | 4.17 | 7.53 | Tốt trong các giờ ổn định khí quyển |
| **Đà Nẵng** | **US AQI** | **Persistence** | **5.46** | **6.20** | +5.46 | 5.63 | 12.60 | Nền không khí ổn định tại đô thị biển |
| **Đà Nẵng** | **PM2.5** | **Seasonal Naive (24h)**| **6.71** | **8.17** | +6.71 | 11.60 | 6.78 | Nắm bắt tốt chu kỳ tuần hoàn gió đất - gió biển |


## Mã nguồn và kiểm tra

| Chương trình | Trách nhiệm |
| --- | --- |
| [snapshot.py](scripts/snapshot.py), [quality.py](scripts/quality.py) | Đọc raw từ S3, kiểm tra lược đồ/số/thời gian, lưu thống kê theo đô thị–giờ |
| [benchmark.py](scripts/benchmark.py) | Tạo dữ liệu thử nghiệm NDJSON/Parquet riêng, cấu hình Projection, đo và đối chiếu truy vấn |
| [dashboard.py](scripts/dashboard.py) | Tạo Dashboard riêng, xuất metric và ảnh CloudWatch |
| [metric_filters.py](scripts/metric_filters.py), [check_operations.py](scripts/check_operations.py) | Kiểm tra mẫu và tạo bộ đếm log; đối chiếu kết quả với S3, lịch/quyền gọi và ngưỡng cảnh báo |
| [forecast.py](scripts/forecast.py) | Thu dữ liệu mô hình theo giờ, chia tập theo thời gian, dự báo và tính sai số |
| [release.py](scripts/release.py) | Đóng gói xác định, kiểm tra tài khoản, triển khai chỉ mã, xác minh và khôi phục có kiểm soát phiên bản |
| [verify_results.py](scripts/verify_results.py) | Đối chiếu hash, raw, kết quả Athena và sai số đã lưu mà không gọi AWS |
| [test_week3.py](tests/test_week3.py) | Các kiểm tra hồi quy về dữ liệu, thời gian, dự báo và an toàn triển khai |

```bash
python -m pip install -r tuan_3/requirements.txt
python -m unittest discover -s tuan_3/tests -v
python tuan_3/scripts/verify_results.py
```

Các lệnh trên kiểm tra tệp đã lưu, không chứng minh vận hành AWS hiện tại. Cách chạy các chương trình có thao tác AWS và điều kiện khôi phục được trình bày trong [hướng dẫn vận hành](docs/operation.md).


### Tổng hợp phân công và giờ công toàn bộ đồ án (58.0 giờ)

| Giai đoạn | Nội dung trọng tâm | Nguyễn Tiến Sơn (24110054) | Trần Thị Ngọc Quyên (24110051) | Tổng giờ tuần | Minh chứng kỹ thuật |
| --- | --- | :---: | :---: | :---: | --- |
| **Tuần 1** | Khảo sát API, thiết kế kiến trúc, S3, Secrets Manager, Glue, Athena, 156 bản ghi | 9.5 giờ | 9.0 giờ | **18.5 giờ** | [tuan_1/](../tuan_1/) · [worklog](../tuan_1/worklog.csv) |
| **Tuần 2** | Triển khai Lambda đa tài khoản, đồng bộ mã 36c9b39, SNS email, 27 CSV, 20 biểu đồ | 10.0 giờ | 9.5 giờ | **19.5 giờ** | [tuan_2/](../tuan_2/) · [worklog](../tuan_2/worklog.csv) |
| **Tuần 3** | Benchmark Athena 18 trials, Partition Projection, CTAS Parquet, Metric Filters, Dashboard, Dự báo 24h | 10.0 giờ | 10.0 giờ | **20.0 giờ** | [tuan_3/](./) · [worklog](worklog.csv) |
| **TỔNG CỘNG**| **Toàn bộ học phần Điện toán đám mây** | **29.5 giờ** | **28.5 giờ** | **58.0 giờ** | [worklog.csv](../worklog.csv) · [docs/WORKLOG.md](../docs/WORKLOG.md) |


## Phần tiếp tục theo dõi

[Nhật ký Tuần 3](docs/WORKLOG.md) ghi chi tiết mốc chuẩn bị và kế hoạch **20,0 giờ dự kiến**, gồm **10,0 giờ cho sinh viên Tiến Sơn** và **10,0 giờ cho sinh viên Ngọc Quyên**. Giờ thực tế chờ xác nhận và chưa cộng vào tổng 38,0 giờ Tuần 1–2. Dữ liệu tại mốc này có **0 bản ghi thuộc lịch Tuần 3**. Cần tiếp tục lưu các lượt theo lịch trong phiên Learner Lab còn hiệu lực và cập nhật độ phủ theo ngày; không suy ra vận hành liên tục từ trạng thái lịch đang bật. Dữ liệu dự báo tương lai cũng cần được đối chiếu khi thời điểm đích đã qua.
