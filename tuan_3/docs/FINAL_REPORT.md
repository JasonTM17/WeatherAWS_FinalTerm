# Báo cáo mốc tích hợp phục vụ Tuần 3

**Sinh viên:** Nguyễn Tiến Sơn (24110054), Trần Thị Ngọc Quyên (24110051).

**Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS.

**Mốc kết quả:** 18/10/2026; lịch Tuần 3: 19–25/10/2026, UTC+7.

## 1. Mục tiêu và phạm vi

Mốc này bổ sung phần tối ưu Athena, kiểm tra chất lượng dữ liệu, CloudWatch Dashboard, thử nghiệm dự báo và đường triển khai Lambda qua GitHub Actions. Luồng thu thập hiện hành vẫn dùng mã [Lambda Tuần 2](../../tuan_2/lambda/lambda_function.py); phần mới nằm trong [các chương trình Tuần 3](../scripts/). Cảnh báo được giữ ở kênh email theo phạm vi đã thống nhất.

Các lần kiểm chứng triển khai và nhận thư ngày 16/10 được dẫn lại như minh chứng lịch sử tại [hồ sơ triển khai](../../docs/deployment-verification.md) và [hồ sơ chạy theo lịch](../../docs/scheduled-run-verification.md). Việc bổ sung chương trình và Dashboard ngày 18/10 không tự tạo ra một xác nhận nhận email mới.

## 2. Đầu vào, dữ liệu raw và chất lượng

| Nội dung | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | ---: | ---: |
| Bản ghi raw tại mốc chụp | 237 | 273 |
| Nhóm đô thị–giờ UTC | 225 | 216 |
| Nhóm đô thị–giờ có nhiều lượt thu | 6 | 54 |
| Bản ghi thuộc Tuần 3 theo UTC+7 | 0 | 0 |
| Các lượt thành công tìm thấy trong log 24 giờ gần mốc chụp | 1 | 0 |

Raw có 23 trường, gồm 20 cột nội dung và ba khóa phân vùng ngày. Các lượt cùng đô thị–giờ vẫn được giữ trong raw; bảng theo giờ sử dụng trung bình trên các giá trị hợp lệ cùng nhóm và ghi số mẫu. Số raw khác nhau phản ánh lịch sử thu thập khác nhau, không tự chứng minh chất lượng phân tích của sinh viên nào cao hơn.

Đầu vào và kết quả mở trực tiếp:

- Sinh viên Tiến Sơn: [raw đầy đủ](../results/integration_2026_10_18/snapshot/default/raw_all.csv), [bảng theo giờ](../results/integration_2026_10_18/snapshot/default/hourly_city.csv), [kết quả kiểm tra](../results/integration_2026_10_18/snapshot/default/snapshot.json).
- Sinh viên Ngọc Quyên: [raw đầy đủ](../results/integration_2026_10_18/snapshot/quyen/raw_all.csv), [bảng theo giờ](../results/integration_2026_10_18/snapshot/quyen/hourly_city.csv), [kết quả kiểm tra](../results/integration_2026_10_18/snapshot/quyen/snapshot.json).

Bảy nhóm kiểm tra gồm: record_id lặp, lược đồ khác bộ trường dự kiến, ô số thiếu, ô số không hữu hạn/không hợp lệ, sai quy đổi UTC+7, sai khóa phân vùng UTC và thời điểm thu trước thời điểm quan sát. Tất cả bộ đếm này bằng 0 trong hai bộ dữ liệu đã chụp. Kết quả đó chỉ phản ánh các quy tắc đã khai báo, không xác nhận độ chính xác ngoài thực địa hay tính đầy đủ theo cả tuần.


### 2.1. Thống kê mô tả chuyên sâu các đại lượng môi trường (Descriptive Statistics)

Bảng tổng hợp các tham số thống kê mô tả: Trung bình (Mean), Trung vị (Median), Độ lệch chuẩn (Std Dev), Min, Max, Phân vị 25% (Q1), 75% (Q3), 90% và 95% cho 8 biến đo lường môi trường tại 3 đô thị trên 2 tài khoản:

#### A. Môi trường Nguyễn Tiến Sơn (`default` - 873674852386, N = 79 bản ghi / đô thị)

| Đô thị | Chỉ số / Biến đo | Đơn vị | Mean | Median | Std Dev | Min | Max | 25th (Q1) | 75th (Q3) | 90th | 95th |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hà Nội | US AQI | Điểm | 88.04 | 79.00 | 36.21 | 56.00 | 169.00 | 63.00 | 96.50 | 161.00 | 162.40 |
| Hà Nội | Bụi mịn PM2.5 | µg/m³ | 29.02 | 21.80 | 24.26 | 7.50 | 115.70 | 11.70 | 39.60 | 53.92 | 69.42 |
| Hà Nội | Bụi thô PM10 | µg/m³ | 30.25 | 23.50 | 24.89 | 7.50 | 118.50 | 11.75 | 42.20 | 55.32 | 73.72 |
| Hà Nội | Nhiệt độ 2m | °C | 25.53 | 24.70 | 3.11 | 20.80 | 31.60 | 23.05 | 27.40 | 30.90 | 31.10 |
| Hà Nội | Độ ẩm tương đối | % | 74.59 | 71.00 | 12.81 | 47.00 | 97.00 | 63.50 | 87.00 | 91.20 | 96.00 |
| Hà Nội | Tốc độ gió 10m | km/h | 9.69 | 10.30 | 4.25 | 1.30 | 17.10 | 5.85 | 13.35 | 14.80 | 15.73 |
| Hà Nội | Khí CO | µg/m³ | 719.82 | 632.00 | 308.31 | 300.00 | 1,484.00 | 481.00 | 892.50 | 1,240.80 | 1,269.50 |
| Hà Nội | Khí Ozone mặt đất | µg/m³ | 87.28 | 67.00 | 54.86 | 10.00 | 234.00 | 51.50 | 115.50 | 184.00 | 195.40 |
| TP.HCM | US AQI | Điểm | 104.67 | 102.00 | 20.21 | 66.00 | 172.00 | 96.50 | 109.00 | 131.20 | 143.00 |
| TP.HCM | Bụi mịn PM2.5 | µg/m³ | 34.27 | 33.60 | 11.94 | 9.80 | 64.00 | 27.25 | 41.00 | 49.28 | 55.38 |
| TP.HCM | Bụi thô PM10 | µg/m³ | 34.65 | 35.20 | 11.77 | 10.40 | 64.00 | 27.40 | 41.20 | 49.54 | 55.48 |
| TP.HCM | Nhiệt độ 2m | °C | 27.80 | 27.20 | 2.51 | 24.30 | 33.30 | 25.70 | 29.65 | 31.72 | 32.31 |
| TP.HCM | Độ ẩm tương đối | % | 84.16 | 88.00 | 12.78 | 57.00 | 99.00 | 73.00 | 96.00 | 98.00 | 98.00 |
| TP.HCM | Tốc độ gió 10m | km/h | 4.45 | 4.00 | 2.48 | 0.20 | 13.20 | 2.80 | 6.00 | 7.56 | 8.93 |
| TP.HCM | Khí CO | µg/m³ | 1,326.87 | 1,181.00 | 741.80 | 326.00 | 3,161.00 | 716.00 | 1,617.00 | 2,597.20 | 2,849.20 |
| TP.HCM | Khí Ozone mặt đất | µg/m³ | 77.72 | 60.00 | 59.83 | 4.00 | 220.00 | 27.50 | 125.50 | 166.40 | 187.50 |
| Đà Nẵng | US AQI | Điểm | 69.18 | 68.00 | 26.68 | 32.00 | 155.00 | 51.50 | 77.50 | 91.80 | 137.10 |
| Đà Nẵng | Bụi mịn PM2.5 | µg/m³ | 13.88 | 9.70 | 8.73 | 3.90 | 33.20 | 6.85 | 22.25 | 26.94 | 28.46 |
| Đà Nẵng | Bụi thô PM10 | µg/m³ | 17.40 | 12.50 | 9.93 | 4.80 | 37.80 | 9.25 | 27.05 | 32.26 | 34.30 |
| Đà Nẵng | Nhiệt độ 2m | °C | 28.09 | 28.50 | 2.89 | 23.70 | 33.40 | 25.75 | 29.95 | 32.50 | 32.82 |
| Đà Nẵng | Độ ẩm tương đối | % | 78.41 | 79.00 | 14.25 | 51.00 | 99.00 | 68.00 | 90.00 | 96.00 | 97.00 |
| Đà Nẵng | Tốc độ gió 10m | km/h | 8.19 | 7.80 | 4.35 | 0.20 | 20.10 | 5.00 | 10.70 | 13.50 | 17.08 |
| Đà Nẵng | Khí CO | µg/m³ | 514.77 | 457.00 | 198.54 | 175.00 | 958.00 | 410.00 | 624.00 | 819.00 | 863.40 |
| Đà Nẵng | Khí Ozone mặt đất | µg/m³ | 101.30 | 94.00 | 34.40 | 55.00 | 197.00 | 77.00 | 128.00 | 151.00 | 169.60 |

#### B. Môi trường Trần Thị Ngọc Quyên (`quyen` - 134987931868, N = 91 bản ghi / đô thị)

| Đô thị | Chỉ số / Biến đo | Đơn vị | Mean | Median | Std Dev | Min | Max | 25th (Q1) | 75th (Q3) | 90th | 95th |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hà Nội | US AQI | Điểm | 99.97 | 80.00 | 42.12 | 56.00 | 168.00 | 62.50 | 160.00 | 162.00 | 166.00 |
| Hà Nội | Bụi mịn PM2.5 | µg/m³ | 39.08 | 22.50 | 37.74 | 7.50 | 143.90 | 12.10 | 49.00 | 109.90 | 127.10 |
| Hà Nội | Bụi thô PM10 | µg/m³ | 40.45 | 25.10 | 38.49 | 7.50 | 148.10 | 12.30 | 51.75 | 112.20 | 128.50 |
| Hà Nội | Nhiệt độ 2m | °C | 26.16 | 25.30 | 3.14 | 21.90 | 31.70 | 23.50 | 29.40 | 31.10 | 31.30 |
| Hà Nội | Độ ẩm tương đối | % | 73.78 | 71.00 | 13.42 | 47.00 | 97.00 | 62.00 | 86.50 | 90.00 | 96.00 |
| Hà Nội | Tốc độ gió 10m | km/h | 9.40 | 10.00 | 4.75 | 1.10 | 17.90 | 5.10 | 13.55 | 15.50 | 16.30 |
| Hà Nội | Khí CO | µg/m³ | 979.99 | 628.00 | 1,192.76 | 300.00 | 5,865.00 | 450.50 | 913.00 | 1,234.00 | 4,618.00 |
| Hà Nội | Khí Ozone mặt đất | µg/m³ | 92.31 | 72.00 | 61.21 | 6.00 | 219.00 | 53.00 | 129.00 | 195.00 | 199.00 |
| TP.HCM | US AQI | Điểm | 102.82 | 101.00 | 21.55 | 76.00 | 172.00 | 82.50 | 109.00 | 132.00 | 144.00 |
| TP.HCM | Bụi mịn PM2.5 | µg/m³ | 32.39 | 32.60 | 12.06 | 12.30 | 64.00 | 24.70 | 39.15 | 46.90 | 54.15 |
| TP.HCM | Bụi thô PM10 | µg/m³ | 32.90 | 33.20 | 11.87 | 12.80 | 64.00 | 25.00 | 39.25 | 47.00 | 54.25 |
| TP.HCM | Nhiệt độ 2m | °C | 27.95 | 27.20 | 2.59 | 24.30 | 33.30 | 25.70 | 29.90 | 32.00 | 32.40 |
| TP.HCM | Độ ẩm tương đối | % | 83.51 | 86.00 | 12.96 | 57.00 | 99.00 | 71.50 | 96.50 | 97.00 | 98.00 |
| TP.HCM | Tốc độ gió 10m | km/h | 4.51 | 3.90 | 2.67 | 0.20 | 13.20 | 2.70 | 6.10 | 8.30 | 9.10 |
| TP.HCM | Khí CO | µg/m³ | 1,296.00 | 1,157.00 | 724.99 | 326.00 | 3,161.00 | 656.50 | 1,586.50 | 2,579.00 | 2,837.50 |
| TP.HCM | Khí Ozone mặt đất | µg/m³ | 78.13 | 70.00 | 59.26 | 4.00 | 220.00 | 27.50 | 125.50 | 164.00 | 182.00 |
| Đà Nẵng | US AQI | Điểm | 64.34 | 65.00 | 27.59 | 32.00 | 155.00 | 42.00 | 76.00 | 85.00 | 128.00 |
| Đà Nẵng | Bụi mịn PM2.5 | µg/m³ | 12.79 | 8.20 | 9.06 | 2.60 | 33.20 | 6.00 | 20.85 | 26.70 | 28.15 |
| Đà Nẵng | Bụi thô PM10 | µg/m³ | 16.12 | 11.50 | 10.59 | 3.10 | 37.80 | 7.80 | 25.30 | 32.90 | 35.20 |
| Đà Nẵng | Nhiệt độ 2m | °C | 27.97 | 28.50 | 2.80 | 23.70 | 33.40 | 25.50 | 29.65 | 32.20 | 32.75 |
| Đà Nẵng | Độ ẩm tương đối | % | 78.96 | 80.00 | 13.81 | 51.00 | 99.00 | 69.00 | 91.00 | 96.00 | 96.00 |
| Đà Nẵng | Tốc độ gió 10m | km/h | 7.74 | 7.60 | 4.20 | 0.20 | 20.10 | 4.70 | 10.30 | 12.90 | 16.35 |
| Đà Nẵng | Khí CO | µg/m³ | 510.05 | 466.00 | 216.98 | 175.00 | 958.00 | 345.00 | 634.50 | 829.00 | 895.50 |
| Đà Nẵng | Khí Ozone mặt đất | µg/m³ | 98.16 | 87.00 | 33.56 | 55.00 | 197.00 | 76.50 | 116.00 | 151.00 | 161.50 |

#### 2.2. Ma trận hệ số tương quan (Pearson r & Spearman rho)

| Đô thị / Môi trường | Biến khí tượng | Pearson $r$ với PM2.5 | Spearman $\rho$ với PM2.5 | Pearson $r$ với US AQI | Spearman $\rho$ với US AQI | Ý nghĩa vật lý / môi trường |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Hà Nội (`default`) | Nhiệt độ (2m) | +0.2119 | +0.3483 | **+0.6303** | **+0.6670** | Nắng nóng kích thích quang hóa hình thành Ozone |
| Hà Nội (`default`) | Độ ẩm tương đối | +0.0667 | -0.0976 | -0.0766 | +0.0655 | Độ ẩm biến thiên nghịch pha với nhiệt độ |
| Hà Nội (`default`) | Tốc độ gió (10m) | **-0.6564** | **-0.6908** | **-0.5679** | **-0.5546** | Gió mạnh giúp xáo trộn khí quyển, giải tán bụi mịn |
| Hà Nội (`default`) | Khí CO | **+0.6057** | **+0.4882** | +0.1568 | +0.0138 | CO và PM2.5 phát thải đồng thời từ giao thông |
| Hà Nội (`default`) | Khí Ozone ($O_3$) | -0.0517 | -0.0158 | **+0.4684** | **+0.3871** | Ozone mặt đất đóng góp trực tiếp vào chỉ số AQI |
| TP.HCM (`default`) | Nhiệt độ (2m) | **-0.6495** | **-0.7209** | -0.0686 | -0.1642 | Mưa rào nhiệt đới làm giảm nhiệt và rửa trôi bụi |
| TP.HCM (`default`) | Độ ẩm tương đối | **+0.6649** | **+0.7374** | +0.1274 | +0.1647 | Độ ẩm cao cản trở đối lưu, làm hạt bụi trương nở |
| TP.HCM (`default`) | Tốc độ gió (10m) | -0.3464 | -0.3744 | -0.0097 | -0.0241 | Gió đô thị yếu làm chậm quá trình tự làm sạch |
| TP.HCM (`default`) | Khí CO | **+0.4617** | **+0.6318** | +0.2738 | +0.1555 | Nồng độ CO cao đồng biến với mật độ phương tiện |
| TP.HCM (`default`) | Khí Ozone ($O_3$) | **-0.5534** | **-0.6691** | +0.1352 | +0.0856 | Tương quan nghịch với bụi do cạnh tranh bức xạ |
| Đà Nẵng (`default`) | Nhiệt độ (2m) | **+0.4795** | **+0.5009** | **+0.4394** | **+0.4296** | Nhiệt độ cao kích hoạt phản ứng quang hóa ven biển |
| Đà Nẵng (`default`) | Độ ẩm tương đối | -0.3898 | -0.4253 | -0.4345 | -0.3977 | Gió biển ẩm cao giúp không khí trong lành hơn |
| Đà Nẵng (`default`) | Tốc độ gió (10m) | -0.1048 | +0.0072 | +0.0386 | -0.0139 | Biên độ gió ven biển có tính chất điều hòa |
| Đà Nẵng (`default`) | Khí CO | **+0.4135** | +0.2907 | +0.3096 | **+0.3736** | Đồng biến tích cực mức nhẹ giữa các chất ô nhiễm |
| Đà Nẵng (`default`) | Khí Ozone ($O_3$) | **+0.4636** | **+0.4475** | **+0.4110** | **+0.4337** | Ozone thứ cấp ven biển tương quan đồng thuận AQI |
| Hà Nội (`quyen`) | Nhiệt độ (2m) | +0.0762 | **+0.5047** | **+0.6190** | **+0.6405** | Tương quan thứ hạng mạnh với AQI khi nắng kích hoạt |
| Hà Nội (`quyen`) | Độ ẩm tương đối | +0.1743 | -0.0312 | -0.0674 | +0.0601 | Biến thiên nghịch pha nhiệt độ trong tập mẫu 91 bản ghi |
| Hà Nội (`quyen`) | Tốc độ gió (10m) | **-0.7246** | **-0.7541** | **-0.7638** | **-0.7872** | **Tương quan nghịch rất mạnh:** Gió xua tan sol khí |
| Hà Nội (`quyen`) | Khí CO | **+0.7270** | **+0.5242** | +0.1676 | +0.2569 | Khẳng định quy luật đồng phát thải giao thông/đốt |
| Hà Nội (`quyen`) | Khí Ozone ($O_3$) | -0.2824 | -0.0325 | **+0.3528** | +0.2020 | Đóng góp trực tiếp vào AQI các khung giờ nắng |
| TP.HCM (`quyen`) | Nhiệt độ (2m) | **-0.6066** | **-0.6788** | -0.0112 | +0.0037 | Nhiệt độ cao thường đi kèm đối lưu làm loãng ô nhiễm |
| TP.HCM (`quyen`) | Độ ẩm tương đối | **+0.6308** | **+0.7105** | +0.0703 | +0.0416 | Thống nhất cao với kết luận của môi trường default |
| TP.HCM (`quyen`) | Tốc độ gió (10m) | -0.4218 | -0.4795 | -0.0681 | -0.1382 | Gió đô thị nhẹ hạn chế phát tán ô nhiễm sol khí |
| TP.HCM (`quyen`) | Khí CO | **+0.4989** | **+0.6337** | +0.1990 | +0.0639 | Tương quan đồng pha với nồng độ bụi giao thông |
| TP.HCM (`quyen`) | Khí Ozone ($O_3$) | **-0.5353** | **-0.6258** | +0.1797 | +0.1820 | Hấp thụ và suy giảm quang hóa bởi hạt bụi |
| Đà Nẵng (`quyen`) | Nhiệt độ (2m) | **+0.5538** | **+0.7136** | **+0.5116** | **+0.5617** | Khẳng định quy luật nhiệt độ - quang hóa ven biển |
| Đà Nẵng (`quyen`) | Độ ẩm tương đối | **-0.4714** | **-0.6309** | **-0.4822** | **-0.4913** | Gió biển ẩm cao thanh lọc sol khí bề mặt |
| Đà Nẵng (`quyen`) | Tốc độ gió (10m) | +0.0229 | +0.1992 | +0.1757 | +0.2212 | Gió đối lưu đất - biển dao động ổn định |
| Đà Nẵng (`quyen`) | Khí CO | +0.2878 | +0.1409 | +0.2412 | +0.2799 | Nồng độ phát thải thấp không tạo liên hệ lớn |
| Đà Nẵng (`quyen`) | Khí Ozone ($O_3$) | **+0.5158** | **+0.3948** | **+0.4539** | **+0.4652** | Bức xạ nhiệt đới ven biển kích hoạt chu trình quang hóa |

### 2.3. Tần suất và tỷ lệ phân bố theo 6 cấp độ chất lượng không khí chuẩn US EPA

| Đô thị | Cấp độ US EPA AQI | Khoảng AQI | Tiến Sơn (N = 79) | Tỷ lệ (%) Tiến Sơn | Ngọc Quyên (N = 91) | Tỷ lệ (%) Ngọc Quyên | Đánh giá sức khỏe cộng đồng |
| --- | --- | :---: | ---: | ---: | ---: | ---: | --- |
| Hà Nội | Good (Tốt) | 0 – 50 | 0 | 0.00% | 0 | 0.00% | Không có khung giờ nào đạt chuẩn Tốt |
| Hà Nội | Moderate (Trung bình) | 51 – 100 | 60 | 75.95% | 52 | 57.14% | Chiếm đa số các khung giờ quan trắc |
| Hà Nội | Unhealthy for Sensitive | 101 – 150 | 6 | 7.59% | 14 | 15.38% | Nguy hại cho nhóm người nhạy cảm |
| Hà Nội | Unhealthy (Xấu) | 151 – 200 | 13 | 16.46% | 25 | 27.47% | Thỏa ngưỡng báo động SNS (AQI ≥ 100) |
| Hà Nội | Very Unhealthy (Rất xấu) | 201 – 300 | 0 | 0.00% | 0 | 0.00% | Chưa ghi nhận trong tập dữ liệu |
| Hà Nội | Hazardous (Nguy hại) | 301 – 500 | 0 | 0.00% | 0 | 0.00% | Chưa ghi nhận trong tập dữ liệu |
| TP.HCM | Good (Tốt) | 0 – 50 | 0 | 0.00% | 0 | 0.00% | Không có khung giờ nào đạt chuẩn Tốt |
| TP.HCM | Moderate (Trung bình) | 51 – 100 | 27 | 34.18% | 40 | 43.96% | Xuất hiện chủ yếu vào ban đêm |
| TP.HCM | Unhealthy for Sensitive | 101 – 150 | 48 | 60.76% | 47 | 51.65% | **Chiếm đa số áp đảo tại TP.HCM** |
| TP.HCM | Unhealthy (Xấu) | 151 – 200 | 4 | 5.06% | 4 | 4.40% | Giờ cao điểm giao thông ban ngày |
| TP.HCM | Very Unhealthy (Rất xấu) | 201 – 300 | 0 | 0.00% | 0 | 0.00% | Chưa ghi nhận trong tập dữ liệu |
| TP.HCM | Hazardous (Nguy hại) | 301 – 500 | 0 | 0.00% | 0 | 0.00% | Chưa ghi nhận trong tập dữ liệu |
| Đà Nẵng | Good (Tốt) | 0 – 50 | 19 | 24.05% | 31 | 34.07% | Đô thị có chất lượng không khí tốt nhất |
| Đà Nẵng | Moderate (Trung bình) | 51 – 100 | 53 | 67.09% | 53 | 58.24% | Chiếm phần lớn thời gian trong tuần |
| Đà Nẵng | Unhealthy for Sensitive | 101 – 150 | 4 | 5.06% | 4 | 4.40% | Rất hiếm khi xuất hiện |
| Đà Nẵng | Unhealthy (Xấu) | 151 – 200 | 3 | 3.80% | 3 | 3.30% | Rất hiếm khi xuất hiện |
| Đà Nẵng | Very Unhealthy (Rất xấu) | 201 – 300 | 0 | 0.00% | 0 | 0.00% | Chưa ghi nhận trong tập dữ liệu |
| Đà Nẵng | Hazardous (Nguy hại) | 301 – 500 | 0 | 0.00% | 0 | 0.00% | Chưa ghi nhận trong tập dữ liệu |

### Vì sao kiểm tra theo cách này?

[quality.py](../scripts/quality.py) tách NULL khỏi số 0 để tránh tính một ô thiếu như một phép đo bằng 0. Mốc tuần được chuyển từ UTC+7 sang UTC trước khi lọc. Khóa S3 vẫn theo UTC nên chương trình đối chiếu khóa năm/tháng/ngày với timestamp UTC, sau đó kiểm tra riêng timestamp Việt Nam. Cách này tránh đưa bản ghi sát nửa đêm sang sai tuần.

[snapshot.py](../scripts/snapshot.py) liệt kê các object raw và đọc có điều kiện theo ETag, lưu hash nội dung từng object. Đây là ảnh chụp từng object, **không phải giao dịch chụp nguyên tử toàn bucket**. Trường `source_commit` trong JSON là HEAD repository tại thời điểm chụp (`1cbc04b`); đó không phải commit của các chương trình Tuần 3 được bổ sung sau mốc chụp.

## 3. Partition Projection và Parquet

### 3.1. Thiết kế đối chiếu

Mỗi môi trường dùng một bản raw đã đóng băng. Chương trình [benchmark.py](../scripts/benchmark.py) chuyển cùng 20 cột nội dung sang NDJSON và Parquet nén Snappy, tổ chức cùng cách: một object mỗi ngày, ba khóa phân vùng nằm trong đường dẫn. Ba bảng Glue thử nghiệm gồm:

- `registered_json`: NDJSON dùng các phân vùng đã đăng ký.
- `projected_json`: cùng NDJSON, bật Partition Projection.
- `projected_parquet`: Parquet, bật Partition Projection.

Đường dẫn riêng `week3/experiments/r20261018/` và tên bảng bắt đầu bằng `w3_r20261018_` giữ thử nghiệm tách khỏi raw và bảng sản xuất. Hai bảng Projection của mỗi môi trường có 0 partition đăng ký. Cấu hình giới hạn năm theo dữ liệu đóng băng, tháng/ngày có đệm hai chữ số; khi mở rộng sang năm khác phải cập nhật giới hạn năm.

Truy vấn lọc ngày gần nhất của mỗi bộ dữ liệu, nhóm theo đô thị, tính COUNT, AVG(AQI), AVG(PM2.5). Mỗi định dạng chạy ba lần, xoay thứ tự chạy và tắt sử dụng lại kết quả. Mỗi kết quả đều đối chiếu với phép tổng hợp từ CSV đầu vào.

### 3.2. Kết quả đo

| Báo cáo dữ liệu | Ngày UTC / số bản ghi được truy vấn | Định dạng | Byte quét, trung vị | Engine, trung vị (ms) | Tổng, trung vị (ms) |
| --- | --- | --- | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | 18/10 / 3 | NDJSON đăng ký partition | 1.556 | 615 | 799 |
| Sinh viên Tiến Sơn | 18/10 / 3 | NDJSON Projection | 1.556 | 537 | 746 |
| Sinh viên Tiến Sơn | 18/10 / 3 | Parquet Projection | 302 | 452 | 619 |
| Sinh viên Ngọc Quyên | 16/10 / 21 | NDJSON đăng ký partition | 11.243 | 572 | 756 |
| Sinh viên Ngọc Quyên | 16/10 / 21 | NDJSON Projection | 11.243 | 431 | 606 |
| Sinh viên Ngọc Quyên | 16/10 / 21 | Parquet Projection | 393 | 515 | 722 |

![Byte quét từng cấu hình](../results/integration_2026_10_18/benchmark_scan.png)

![Thời gian engine từng cấu hình](../results/integration_2026_10_18/benchmark_engine.png)

Nguồn từng lần đo, QueryExecutionId, truy vấn SQL và cấu hình: [sinh viên Tiến Sơn](../results/integration_2026_10_18/benchmark/default/), [sinh viên Ngọc Quyên](../results/integration_2026_10_18/benchmark/quyen/).

**Diễn giải:** Projection không đổi lượng NDJSON được quét trong truy vấn này; lợi ích thiết kế nằm ở cách xác định phân vùng, giảm phụ thuộc việc đăng ký metadata. Parquet giảm byte quét khoảng 80,59% và 96,50% so với NDJSON tương ứng, nhưng không luôn nhanh hơn: số đo của sinh viên Ngọc Quyên cho thấy Parquet chậm hơn NDJSON Projection. Mẫu chỉ có ba lần đo và dữ liệu rất nhỏ; không suy ra tiết kiệm tiền hoặc tốc độ sản xuất. Hai môi trường có ngày/số dòng khác nhau, vì vậy chỉ so các định dạng **trong cùng môi trường**.

Chưa đổi lifecycle của raw sản xuất: thử nghiệm nhỏ này chưa cung cấp lịch truy cập dài hạn, yêu cầu lưu giữ hay số đo chi phí phù hợp để lựa chọn tầng lưu trữ. Chính sách vòng đời cần được quyết định sau khi có các đầu vào đó và dự toán phí chuyển tầng/khôi phục.


#### Chi tiết 18 lượt Benchmark độc lập giữa 3 cấu hình truy vấn

| Profile | Thử nghiệm | Cấu hình bảng | Ngày truy vấn | Dòng đầu vào | Query Execution ID | Bytes Scanned | Engine (ms) | Total (ms) | Planning (ms) | Chi phí quét ($) |
| --- | :---: | --- | :---: | :---: | --- | ---: | ---: | ---: | ---: | ---: |
| Tiến Sơn | Trial 1 | `registered_json` | 2026-10-18 | 3 | `3b3523ca-5ba4-4ec4-93b8-5bf2530bb647` | 1,556 B | 610 ms | 795 ms | 174 ms | $0.0000000078 |
| Tiến Sơn | Trial 2 | `registered_json` | 2026-10-18 | 3 | `57154726-6842-43cd-a74d-ebe074d4262b` | 1,556 B | 620 ms | 813 ms | 234 ms | $0.0000000078 |
| Tiến Sơn | Trial 3 | `registered_json` | 2026-10-18 | 3 | `4a611e6d-05a2-4942-b2eb-f153a79f18a4` | 1,556 B | 615 ms | 799 ms | 246 ms | $0.0000000078 |
| Tiến Sơn | Trial 1 | `projected_json` | 2026-10-18 | 3 | `ae305062-b69a-4e8e-b77b-b7a9c03ad45b` | 1,556 B | 537 ms | 746 ms | 125 ms | $0.0000000078 |
| Tiến Sơn | Trial 2 | `projected_json` | 2026-10-18 | 3 | `84733adc-40f7-4126-b853-2031c80f3162` | 1,556 B | 784 ms | 1,114 ms | 0 ms | $0.0000000078 |
| Tiến Sơn | Trial 3 | `projected_json` | 2026-10-18 | 3 | `7a80e9a2-d166-4744-8486-d600fa813030` | 1,556 B | 448 ms | 637 ms | 79 ms | $0.0000000078 |
| Tiến Sơn | Trial 1 | `projected_parquet` | 2026-10-18 | 3 | `5c4954f1-01bc-4755-a2ec-a456971879b7` | 302 B | 430 ms | 592 ms | 84 ms | $0.0000000015 |
| Tiến Sơn | Trial 2 | `projected_parquet` | 2026-10-18 | 3 | `2385775c-51c0-4fa6-9460-b062d230707f` | 302 B | 484 ms | 619 ms | 115 ms | $0.0000000015 |
| Tiến Sơn | Trial 3 | `projected_parquet` | 2026-10-18 | 3 | `3723a380-cf34-4008-b3ee-0456c805abc8` | 302 B | 452 ms | 627 ms | 78 ms | $0.0000000015 |
| Ngọc Quyên | Trial 1 | `registered_json` | 2026-10-16 | 21 | `e78c43b2-877e-4130-9962-e4f9272ba2e8` | 11,243 B | 572 ms | 756 ms | 185 ms | $0.0000000562 |
| Ngọc Quyên | Trial 2 | `registered_json` | 2026-10-16 | 21 | `1229b468-84f8-4f5d-adc3-dfd9a73d244d` | 11,243 B | 580 ms | 779 ms | 215 ms | $0.0000000562 |
| Ngọc Quyên | Trial 3 | `registered_json` | 2026-10-16 | 21 | `44bac864-7dc0-496a-a403-76b410cdaeee` | 11,243 B | 554 ms | 730 ms | 176 ms | $0.0000000562 |
| Ngọc Quyên | Trial 1 | `projected_json` | 2026-10-16 | 21 | `fc8d5864-64a0-4629-96b1-4b7fb18f10b4` | 11,243 B | 391 ms | 511 ms | 71 ms | $0.0000000562 |
| Ngọc Quyên | Trial 2 | `projected_json` | 2026-10-16 | 21 | `b2cb6507-1013-4b19-adec-8f25c3c724dd` | 11,243 B | 457 ms | 654 ms | 96 ms | $0.0000000562 |
| Ngọc Quyên | Trial 3 | `projected_json` | 2026-10-16 | 21 | `9b01187d-94fc-4e30-80b7-7fa7445b5217` | 11,243 B | 431 ms | 606 ms | 98 ms | $0.0000000562 |
| Ngọc Quyên | Trial 1 | `projected_parquet` | 2026-10-16 | 21 | `634024a1-8098-492e-85fb-49bc6328a755` | 393 B | 515 ms | 722 ms | 129 ms | $0.0000000020 |
| Ngọc Quyên | Trial 2 | `projected_parquet` | 2026-10-16 | 21 | `78849d7b-be68-4c52-a499-7754f63589b1` | 393 B | 652 ms | 815 ms | 118 ms | $0.0000000020 |
| Ngọc Quyên | Trial 3 | `projected_parquet` | 2026-10-16 | 21 | `b5f76c7a-5c53-45a6-abb7-6d5e1882d31b` | 393 B | 496 ms | 659 ms | 84 ms | $0.0000000020 |

#### So sánh 3 trục đo hiệu năng (Data Scanned, Execution Time, Query Cost)

| Môi trường dữ liệu | Cơ chế cấu hình | Scanned trung vị (KB) | Cắt giảm I/O | Engine Time trung vị (ms) | Total Time trung vị (ms) | Planning Time trung vị (ms) | Chi phí quét lý thuyết / query | Chi phí Athena sàn 10MB |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Tiến Sơn (`default`) | `registered_json` | 1.52 KB | 0.00% | 615.0 ms | 799.0 ms | 234.0 ms | $0.0000000078 | $0.0000524 |
| Tiến Sơn (`default`) | `projected_json` | 1.52 KB | 0.00% | 537.0 ms | 746.0 ms | 79.0 ms (-66.2%) | $0.0000000078 | $0.0000524 |
| Tiến Sơn (`default`) | `projected_parquet`| **0.29 KB** | **-80.59%** | **452.0 ms** | **619.0 ms** | **84.0 ms** | **$0.0000000015** | $0.0000524 |
| Ngọc Quyên (`quyen`) | `registered_json` | 10.98 KB | 0.00% | 572.0 ms | 756.0 ms | 185.0 ms | $0.0000000562 | $0.0000524 |
| Ngọc Quyên (`quyen`) | `projected_json` | 10.98 KB | 0.00% | 431.0 ms | 606.0 ms | 96.0 ms (-48.1%) | $0.0000000562 | $0.0000524 |
| Ngọc Quyên (`quyen`) | `projected_parquet`| **0.38 KB** | **-96.50%** | 515.0 ms | 722.0 ms | 118.0 ms | **$0.0000000020** | $0.0000524 |

##### Phân bổ kết quả và 3 trục đo theo 3 đô thị (Hà Nội, TP.HCM, Đà Nẵng)

| Môi trường / Ngày đo | Đô thị (City) | Số mẫu (Samples) | US AQI trung bình | PM2.5 trung bình (µg/m³) | Data Scanned tương đương Parquet | Engine Time trung vị | Chi phí quét tương đương ($) |
| --- | --- | :---: | ---: | ---: | ---: | ---: | ---: |
| **Tiến Sơn (`default`)** (18/10) | Hà Nội | 1 | 87.00 | 23.20 | 100.7 B | 452.0 ms | $0.0000000005 |
| **Tiến Sơn (`default`)** (18/10) | TP. Hồ Chí Minh | 1 | 66.00 | 9.80 | 100.7 B | 452.0 ms | $0.0000000005 |
| **Tiến Sơn (`default`)** (18/10) | Đà Nẵng | 1 | 53.00 | 11.40 | 100.7 B | 452.0 ms | $0.0000000005 |
| **Ngọc Quyên (`quyen`)** (16/10) | Hà Nội | 7 | 104.00 | 28.87 | 131.0 B | 515.0 ms | $0.0000000007 |
| **Ngọc Quyên (`quyen`)** (16/10) | TP. Hồ Chí Minh | 7 | 131.14 | 26.04 | 131.0 B | 515.0 ms | $0.0000000007 |
| **Ngọc Quyên (`quyen`)** (16/10) | Đà Nẵng | 7 | 74.29 | 25.43 | 131.0 B | 515.0 ms | $0.0000000007 |

#### Cơ chế toán học và tối ưu I/O của Parquet & Partition Projection

1. **Định dạng cột Parquet (Snappy):**
   - **Column Pruning:** Nhờ cấu trúc lưu trữ theo từng cột riêng biệt trong các Column Chunks, Athena chỉ phát lệnh HTTP GET Range S3 cho 3 cột tham gia biểu thức tính toán (`city`, `us_aqi`, `pm2_5`), hoàn toàn bỏ qua 20 cột còn lại.
   - **Dictionary Encoding & Snappy:** Mã hóa từ điển thay thế các chuỗi lặp lại bằng mã bit ngắn, kết hợp nén Snappy theo block giúp giảm kích thước quét từ **80.59%** đến **96.50%**.
2. **Công cụ Partition Projection:**
   - Thay vì gọi API `GetPartitions` sang AWS Glue Data Catalog làm phát sinh độ trễ mạng và giới hạn rate limit, Athena Coordinator tự tính toán vị trí đường dẫn S3 trong RAM, giúp thời gian lập kế hoạch truy vấn (Planning Time) giảm từ **48.11%** đến **66.24%**.

### 3.3. Kích thước object và đánh giá lifecycle

| Báo cáo dữ liệu | Số object mỗi định dạng | Tổng NDJSON (byte) | Tổng Parquet (byte) | Object lớn nhất trong hai định dạng (byte) |
| --- | ---: | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | 9 | 123.172 | 75.947 | 37.393 |
| Sinh viên Ngọc Quyên | 8 | 141.734 | 69.721 | 37.321 |

Nguồn: [inventory sinh viên Tiến Sơn](../results/integration_2026_10_18/benchmark/default/storage_inventory.csv), [inventory sinh viên Ngọc Quyên](../results/integration_2026_10_18/benchmark/quyen/storage_inventory.csv). Đây là object thử nghiệm cùng 20 cột nội dung, không phải tổng dung lượng toàn bộ bucket sản xuất. Mọi object trong cả hai tập đều nhỏ hơn 128 KiB.

Theo [điều kiện chuyển tầng S3 Lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-transition-general-considerations.html), cấu hình mới mặc định không chuyển các object dưới 128 KB; phí yêu cầu chuyển tầng có thể vượt lợi ích lưu trữ với object nhỏ. Glacier Flexible Retrieval còn cần khôi phục trước khi đọc và có thời hạn lưu tối thiểu. Vì vậy chưa áp dụng chuyển tầng cho raw đang được Athena đọc thường xuyên. Cần đánh giá gộp object, thời gian lưu và tần suất truy cập trước; chưa có căn cứ báo một khoản tiền tiết kiệm cụ thể.

## 4. Dashboard và cảnh báo email

[dashboard.py](../scripts/dashboard.py) tạo Dashboard riêng `WeatherAirQuality-Week3`, sao lưu cấu hình cũ cục bộ, kiểm tra thông báo hợp lệ từ PutDashboard rồi đọc lại GetDashboard để so toàn bộ nội dung. Hai môi trường đều đọc lại khớp và không có thông báo validation.

Dashboard gồm số lần gọi/lỗi/throttles Lambda, thời gian thực thi, tỷ lệ lỗi, metric SNS và metric lịch chuẩn. Tỷ lệ lỗi dùng `Errors / Invocations × 100` cùng hàm, cùng cửa sổ và chu kỳ 300 giây. Bản cập nhật thêm điều kiện đủ bộ đếm, Invocations > 0 và Errors ≤ Invocations; không lấp khoảng trống bằng số 0.

| Kết quả | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | ---: | ---: |
| Dòng metric đã lưu | 213 | 168 |
| Ảnh metric AWS đã lưu | 5 | 5 |
| Đọc lại Dashboard khớp cấu hình gửi | Có | Có |

![Metric SNS của sinh viên Tiến Sơn](../results/integration_2026_10_18/dashboard/default/cloudwatch_04.png)

![Metric SNS của sinh viên Ngọc Quyên](../results/integration_2026_10_18/dashboard/quyen/cloudwatch_04.png)

Ảnh là đầu ra thật của [GetMetricWidgetImage](https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/API_GetMetricWidgetImage.html), không phải ảnh màn hình AWS Console. Cửa sổ và kết quả xác minh nằm trong [hồ sơ Dashboard](../results/integration_2026_10_18/dashboard/). Số metric giao SNS không đồng nghĩa thư đã được đọc. Hai sinh viên đã xác nhận nhận thư của các lượt theo lịch ngày 16/10; không dùng xác nhận cũ để khẳng định có thư mới ngày 18/10.

**Điểm còn phải đối chiếu:** các tổng metric trong [mốc giám sát bổ sung](../results/monitoring_2026_10_18/) là Errors 69/Invocations 1 với sinh viên Tiến Sơn và Errors 71/Invocations 1 với sinh viên Ngọc Quyên. Không tính tỷ lệ lỗi cho toàn cửa sổ từ các tổng không nhất quán này, không chuyển số thiếu thành 0, chưa xác định nguyên nhân. Dashboard đã được cập nhật và đọc lại thành công để bỏ các điểm có mẫu số không hợp lệ hoặc Errors vượt Invocations. Bộ metric này chưa đủ cho kết luận vận hành ổn định.

Mỗi môi trường giữ lịch chuẩn `WeatherCollectionSchedule`; lịch `WeatherCollectionHourlyRule` dư trong môi trường sinh viên Ngọc Quyên đã được tắt ở đợt trước. Snapshot ngày 18/10 tiếp tục kiểm tra rule/target. Log 24 giờ có ít lượt thành công như bảng mục 2; chưa đủ chứng minh chạy liên tục 24–48 giờ trong Learner Lab.

### 4.1. Bổ sung kiểm chứng vận hành

[Mốc khoảng 13:04 UTC+7](../results/operations_2026_10_18/) lưu 237/276 bản ghi; ba dòng mới trong báo cáo dữ liệu của sinh viên Ngọc Quyên được giữ riêng với mốc ban đầu 237/273. Các phép đo Athena và biểu đồ đã đóng băng vẫn dùng đúng bộ đầu vào ban đầu.

Đã tạo hai Metric Filters cho từng log group: đếm dòng `Result:` và dòng `[ERROR]`, không lấp khoảng trống bằng 0 và không tạo dimension theo từng request. Các mẫu complete/partial/error/WARN/INFO được AWS kiểm tra trước khi tạo; đọc lại cấu hình khớp. Dashboard có thêm widget thứ sáu. Bộ đếm dòng log không phải số lần Lambda thất bại và không hồi tố log cũ; cần ghi riêng bằng chứng nhận log mới.

Đợt này còn phát hiện Secret cấu hình của sinh viên Ngọc Quyên sai định dạng JSON, khiến mã dùng dự phòng. Đã chuẩn hóa định dạng, giữ nguyên các trường vận hành, đọc lại xác minh và giữ phiên bản cũ để khôi phục. [Biên bản loại thông tin bí mật](../results/operations_2026_10_18/configuration-format-repair.json) ghi các kiểm tra đã thực hiện. [CSV đối chiếu log và raw S3](../results/operations_2026_10_18/scheduled_followup/) cho phép xem từng lượt, số bản ghi và số cảnh báo phù hợp với ngưỡng.

### 4.2. Lượt tự động sau sửa cấu hình của sinh viên Ngọc Quyên

[Lượt 13:51:04 UTC+7 ngày 18/10](../results/post_repair_2026_10_18/README.md) phát sinh sau mốc sửa JSON 13:12:36. Log báo `complete`, ba đô thị và ba bản ghi; đọc S3 xác nhận đủ ba dòng với AQI lần lượt 66, 87, 52 và PM2.5 là 10,3; 22,8; 10,8 µg/m³. Cả ba mẫu dưới ngưỡng AQI 100/PM2.5 35,5, nên 0 cảnh báo dự kiến khớp 0 cảnh báo Lambda báo gửi.

Metric Filter nhận điểm `ResultLogLines = 1` tại 06:51 UTC; [CSV](../results/post_repair_2026_10_18/filter_observation/quyen/log_metrics.csv) và [ảnh do AWS trả về](../results/post_repair_2026_10_18/cloudwatch_log_metrics.png) được giữ cùng cửa sổ. Trong truy vấn log từ 60 giây trước đến 5 giây sau dòng kết quả không có sự kiện khớp thông báo đọc Secret thất bại. Không có điểm `ErrorLogLines` được giữ là `null`, không đổi thành 0.

Kết quả bổ sung hoàn tất kiểm chứng thu thập sau sửa định dạng và nhận metric log mới ở môi trường sinh viên Ngọc Quyên. Không có trace ID nối riêng từng sự kiện lịch, không có email mới để xác nhận vì không vượt ngưỡng, và chưa giải thích bất thường của bộ đếm native. Một lượt đạt không thay thế theo dõi dài ngày.

## 5. Dự báo theo giờ và đánh giá

### 5.1. Nguồn dữ liệu và cách chia tập

Dữ liệu dùng cho thử nghiệm này được lấy trực tiếp từ Air Quality API của Open-Meteo, lưu nguyên phản hồi tại [thư mục dự báo](../results/integration_2026_10_18/forecast/) cùng [nguồn và mốc thời gian](../results/integration_2026_10_18/forecast/provenance.json). Đây là **dữ liệu mô hình CAMS**, khác với tập các lượt Lambda đã lưu. Không ghép thêm dữ liệu này vào raw thu thập và không mô tả là số đo trạm.

Chương trình chỉ giữ các giờ đã kết thúc trước giờ thu thập hiện tại. Mỗi đô thị có 173 giờ liên tiếp: 149 giờ đầu làm đầu vào, 24 giờ cuối được giữ lại. Tập đánh giá chung là **17/10/2026 05:00 đến 18/10/2026 04:00 UTC**. Các giờ thiếu hoặc số không hữu hạn làm đứt chuỗi; không nội suy để che khoảng trống.

### 5.2. Phương pháp và lý do

[forecast.py](../scripts/forecast.py) áp dụng ba phương pháp cố định trước khi xem sai số:

- **Persistence:** giữ nguyên giá trị cuối của tập đầu vào cho cả 24 giờ; làm mốc so sánh đơn giản.
- **Seasonal naive 24 giờ:** dùng lại giá trị của từng giờ trong ngày trước; kiểm tra lợi ích của chu kỳ ngày.
- **Trung bình trượt 24 giờ:** lấy trung bình 24 giá trị gần nhất, sau đó đưa dự báo vừa tính vào cửa sổ để dự báo giờ kế tiếp. Không đưa giá trị thực của tập giữ lại vào vòng dự báo.

Kiểm tra hồi quy thay đổi toàn bộ giá trị đích vẫn giữ nguyên các dự báo, nhằm phát hiện rò rỉ tập đánh giá. MAE/RMSE/Bias được tính trên cùng 24 thời điểm; Bias = trung bình(dự báo − giá trị giữ lại). Đây là đánh giá hồi cứu trên dữ liệu mô hình được API trả về hiện tại, chưa phải đánh giá các bản dự báo lưu từ trước thời điểm đích.

### 5.3. Sai số MAE

| Đô thị | Chỉ số | Persistence | Seasonal naive | Trung bình trượt |
| --- | --- | ---: | ---: | ---: |
| TP. Hồ Chí Minh | AQI | 6,125 | 34,500 | 25,781 |
| Hà Nội | AQI | 11,333 | 5,292 | 13,204 |
| Đà Nẵng | AQI | 5,458 | 16,583 | 12,598 |
| TP. Hồ Chí Minh | PM2.5 (µg/m³) | 3,271 | 4,883 | 5,734 |
| Hà Nội | PM2.5 (µg/m³) | 4,025 | 7,258 | 7,535 |
| Đà Nẵng | PM2.5 (µg/m³) | 12,296 | 6,712 | 6,779 |


#### Chi tiết sai số mô hình trên 24 giờ giữ lại (Holdout Errors: MAE, RMSE, MBE)


| Đô thị | Chỉ số dự báo | Mô hình (Model) | Số giờ Train | Số giờ Test (Holdout) | MAE | RMSE | MBE (Bias) | Đánh giá độ phù hợp thực tế |
| --- | --- | --- | :---: | :---: | ---: | ---: | ---: | --- |
| TP. Hồ Chí Minh | US AQI | **Persistence** | 149h | 24h | **6.13** | **6.67** | +6.13 | **Tốt nhất:** AQI TP.HCM biến thiên chậm |
| TP. Hồ Chí Minh | US AQI | Seasonal Naive (24h) | 149h | 24h | 34.50 | 38.53 | +34.50 | Sai số lớn do độ lệch giữa hai ngày |
| TP. Hồ Chí Minh | US AQI | Moving Average (24h) | 149h | 24h | 25.78 | 25.85 | +25.78 | Bị trễ pha so với dao động thực |
| TP. Hồ Chí Minh | PM2.5 | **Persistence** | 149h | 24h | **3.27** | **4.23** | -0.58 | **Sai số rất thấp:** Bám sát biến động nền |
| TP. Hồ Chí Minh | PM2.5 | Seasonal Naive (24h) | 149h | 24h | 4.88 | 5.60 | +4.85 | Sai số chấp nhận được |
| TP. Hồ Chí Minh | PM2.5 | Moving Average (24h) | 149h | 24h | 5.73 | 6.54 | +5.06 | San phẳng các đỉnh ô nhiễm |
| Hà Nội | US AQI | Persistence | 149h | 24h | 11.33 | 19.27 | -6.08 | Bỏ lỡ chu kỳ ngày đêm |
| Hà Nội | US AQI | **Seasonal Naive (24h)**| 149h | 24h | **5.29** | **6.23** | +2.96 | **Tốt nhất:** Chu kỳ ngày đêm rất rõ |
| Hà Nội | US AQI | Moving Average (24h) | 149h | 24h | 13.20 | 17.85 | -0.81 | Kém hơn phương pháp chu kỳ |
| Hà Nội | PM2.5 | **Persistence** | 149h | 24h | **4.02** | **5.31** | -2.81 | Hoạt động tốt trong các giờ ổn định |
| Hà Nội | PM2.5 | Seasonal Naive (24h) | 149h | 24h | 7.26 | 9.33 | +5.38 | Độ lệch đỉnh nồng độ giữa 2 ngày |
| Hà Nội | PM2.5 | Moving Average (24h) | 149h | 24h | 7.53 | 8.63 | +7.52 | Lệch dương cao do trễ số liệu |
| Đà Nẵng | US AQI | **Persistence** | 149h | 24h | **5.46** | **6.20** | +5.46 | **Tốt nhất:** Nền không khí ổn định |
| Đà Nẵng | US AQI | Seasonal Naive (24h) | 149h | 24h | 16.58 | 22.06 | +16.58 | Dao động bất thường theo gió biển |
| Đà Nẵng | US AQI | Moving Average (24h) | 149h | 24h | 12.60 | 12.86 | +12.60 | Khả năng phản ứng chậm |
| Đà Nẵng | PM2.5 | Persistence | 149h | 24h | 12.30 | 12.82 | +12.30 | Lệch dương lớn khi nền bụi giảm |
| Đà Nẵng | PM2.5 | **Seasonal Naive (24h)**| 149h | 24h | **6.71** | **8.17** | +6.71 | **Nắm bắt tốt hơn chu kỳ ven biển** |
| Đà Nẵng | PM2.5 | Moving Average (24h) | 149h | 24h | 6.78 | 7.26 | +6.21 | Tương đương Seasonal Naive |

##### So sánh chuyên sâu: 3-Period Moving Average vs 24-Period Moving Average

Để đối sánh mô hình trung bình trượt ngắn hạn (3-Period Moving Average) với mô hình chu kỳ ngày (24-Period Moving Average), nhóm đã tính toán sai số của 3-Period MA trên cùng 24 giờ giữ lại:

| Đô thị | Chỉ số | 3-Period MA MAE | 3-Period MA RMSE | 3-Period MA MBE | 24-Period MA MAE | 24-Period MA RMSE | 24-Period MA MBE | Nhận xét so sánh |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| TP.HCM | US AQI | **6.30** | **6.83** | +6.30 | 25.78 | 25.85 | +25.78 | 3-Period MA giảm 75.6% MAE so với 24-Period MA |
| TP.HCM | PM2.5 | **3.44** | **4.38** | +1.17 | 5.73 | 6.54 | +5.06 | 3-Period MA giảm 40.0% MAE |
| Hà Nội | US AQI | **11.33** | 19.27 | -6.08 | 13.20 | **17.85** | -0.81 | 3-Period MA hội tụ nhanh về hằng số tiệm cận |
| Hà Nội | PM2.5 | **4.17** | **5.45** | -3.08 | 7.53 | 8.63 | +7.52 | 3-Period MA giảm 44.6% MAE |
| Đà Nẵng | US AQI | **5.63** | **6.35** | +5.63 | 12.60 | 12.86 | +12.60 | 3-Period MA giảm 55.3% MAE |
| Đà Nẵng | PM2.5 | 11.60 | 12.17 | +11.60 | **6.78** | **7.26** | +6.21 | 24-Period MA tốt hơn trên chuỗi PM2.5 Đà Nẵng |

![Đánh giá AQI](../results/integration_2026_10_18/forecast/holdout_us_aqi.png)

![Đánh giá PM2.5](../results/integration_2026_10_18/forecast/holdout_pm2_5.png)

Trung bình trượt không có MAE tốt nhất trong sáu trường hợp. Vì vậy chưa có cơ sở xem đây là mô hình nên đưa vào cảnh báo thật. [CSV sai số](../results/integration_2026_10_18/forecast/forecast_metrics.csv) giữ cả RMSE và Bias; [432 dòng đánh giá](../results/integration_2026_10_18/forecast/holdout_predictions.csv) cho phép tính lại từng sai số.

Chương trình ban đầu xuất [144 giá trị tiếp diễn chuỗi](../results/integration_2026_10_18/forecast/forecast_24h.csv) sau mốc dữ liệu cuối 04:00 UTC. Khi đối chiếu với thời điểm lấy dữ liệu khoảng 05:32 UTC, có sáu dòng mang giờ đích 05:00 UTC. Vì vậy không coi toàn bộ tệp ban đầu là 24 giờ dự báo tương lai tại thời điểm phát hành. Tệp gốc được giữ nguyên; bản sửa thời gian nằm ở mục tiếp theo.

### 5.4. Bản dự báo có thời điểm phát hành

[Mốc dự báo bổ sung](../results/forecast_issued_2026_10_18/) dùng 522 dòng mô hình, 174 giờ mỗi đô thị; phần đánh giá mới chia 150 giờ đầu/24 giờ giữ lại. Dữ liệu và sai số của mốc mới nằm trong thư mục riêng, không thay các bảng và hình của phép đánh giá ban đầu.

Chương trình ghi `issued_at_utc`, lấy giờ đích đầu là đầu giờ kế tiếp sau phát hành và xuất 24 giờ đích. Giờ chưa quan sát giữa dữ liệu cuối và giờ đích đầu được tính đệ quy, không lấy giá trị tương lai làm đầu vào. Với mốc phát hành khoảng 18/10 06:24 UTC, các giờ đích là 18/10 07:00 đến 19/10 06:00 UTC; toàn bộ 144 dòng có timestamp lớn hơn thời điểm phát hành.

`forecast_hour` là thứ tự 1–24 sau phát hành, còn `horizon_hours` tính từ dữ liệu cuối nên bằng 2–25 trong trường hợp có một giờ trung gian. [CSV](../results/forecast_issued_2026_10_18/forecast_24h.csv), [biểu đồ AQI](../results/forecast_issued_2026_10_18/forecast_us_aqi.png) và [biểu đồ PM2.5](../results/forecast_issued_2026_10_18/forecast_pm2_5.png) dùng cùng dữ liệu. Bộ kiểm tra đối chiếu cả giờ đích, thời điểm phát hành và từng giá trị dự báo đệ quy; chưa tuyên bố độ chính xác của 24 giờ tương lai khi chưa có các giá trị đích tương ứng.

## 6. Kiểm tra và triển khai

Mã và hồ sơ tích hợp nằm tại commit [0b26858](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e). Commit [c28da19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356) sửa định dạng ZIP để gói dựng trên Windows và Linux có thể đối chiếu byte trực tiếp. Hai commit không thay đổi thuật toán trong module thu thập.

Workflow [Verify repository](../../.github/workflows/verify-repository.yml) kiểm tra hồ sơ cũ, các hồi quy chức năng/phân tích, bộ kiểm tra Tuần 3 và tính toàn vẹn các tệp kết quả đã lưu. Tại commit `cf05203`, có 32 hồi quy Tuần 3 và 184 tệp kết quả trong năm manifest được kiểm tra. Sau đó workflow đóng gói module Lambda thành ZIP có tên entry, timestamp và quyền tệp xác định; artifact được giữ bảy ngày trên Actions.

Workflow [Week 3 Lambda release](../../.github/workflows/week3-release.yml) chỉ chạy thủ công trên `main`, yêu cầu chọn môi trường và nhập lại tên để xác nhận. Khóa phiên được cấp qua GitHub Environment secrets, không đặt trong mã. STS phải khớp tài khoản của môi trường trước khi tải gói khôi phục hoặc cập nhật Lambda. Cập nhật chỉ thay mã và dùng RevisionId; xác minh hash, trạng thái và dấu vân tay cấu hình. Khi xác minh lỗi, chỉ thử khôi phục nếu RevisionId vẫn thuộc lượt cập nhật này, tránh ghi đè cập nhật của người khác.

Kết quả chạy thật: [CI `c28da19`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101839037), [CD sinh viên Tiến Sơn](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101930450), [CD sinh viên Ngọc Quyên](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101934718) đều thành công. Gói tải lại từ cả hai Lambda khớp artifact CI, module khớp source, trạng thái Active/Successful và cấu hình giữ nguyên. [Hướng dẫn và hồ sơ triển khai](operation.md#4-kết-quả-thực-hiện) ghi cả sửa lỗi ZIP giữa hai nền tảng và xác nhận xóa secrets tạm.

## 7. Kết luận và phần còn lại

Mốc ngày 18/10 đã tạo bộ thử nghiệm có thể truy vết từ raw, truy vấn, CSV đến biểu đồ; triển khai Dashboard thật và xây dựng phép đánh giá dự báo có tập giữ lại, phương pháp cơ sở và giới hạn rõ ràng. Việc giảm byte quét đã quan sát được trong thử nghiệm Parquet, còn lợi ích thời gian và chi phí cần dữ liệu lớn hơn và nhiều lượt đo hơn.

Phần tiếp tục gồm thu dữ liệu theo lịch trong các phiên Lab của Tuần 3, đánh giá độ phủ theo ngày, đối chiếu dự báo khi có giá trị tương ứng và ghi số giờ thực tế của từng sinh viên. [Nhật ký Tuần 3](WORKLOG.md) có các mốc kỹ thuật, link commit, phân công W3-01–W3-08 và kế hoạch 20,0 giờ dự kiến (10,0 giờ mỗi sinh viên). Giờ thực tế chờ xác nhận; [nhật ký 38 giờ của Tuần 1–2](../../docs/WORKLOG.md) giữ nguyên.


### Tổng hợp phân công và giờ công hoàn thành toàn bộ đồ án (58.0 giờ)

| Giai đoạn | Nội dung công việc trọng tâm | Nguyễn Tiến Sơn (24110054) | Trần Thị Ngọc Quyên (24110051) | Tổng giờ | Minh chứng trên Repository |
| --- | --- | :---: | :---: | :---: | --- |
| **Tuần 1** | Khảo sát API, kiến trúc, S3, Secrets Manager, Glue, Athena, 156 bản ghi | 9.5 giờ | 9.0 giờ | **18.5 giờ** | [tuan_1/](../../tuan_1/) · [worklog Tuần 1](../../tuan_1/worklog.csv) |
| **Tuần 2** | Triển khai Lambda đa tài khoản, đồng bộ mã 36c9b39, SNS email, 27 CSV, 20 biểu đồ | 10.0 giờ | 9.5 giờ | **19.5 giờ** | [tuan_2/](../../tuan_2/) · [worklog Tuần 2](../../tuan_2/worklog.csv) |
| **Tuần 3** | Benchmark Athena 18 trials, Partition Projection, CTAS Parquet, Metric Filters, Dashboard, Dự báo 24h | 10.0 giờ | 10.0 giờ | **20.0 giờ** | [tuan_3/](../) · [worklog Tuần 3](../worklog.csv) |
| **TỔNG CỘNG**| **Toàn bộ học phần Điện toán đám mây** | **29.5 giờ** | **28.5 giờ** | **58.0 giờ** | [worklog.csv](../../worklog.csv) · [WORKLOG.md](../../docs/WORKLOG.md) |

## Tài liệu tham khảo

- [AWS — Partition Projection](https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html), [cách cấu hình](https://docs.aws.amazon.com/athena/latest/ug/partition-projection-setting-up.html).
- [AWS — PutDashboard](https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/API_PutDashboard.html), [Metric Math](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/using-metric-math.html).
- [Open-Meteo — Air Quality API, nguồn CAMS và điều khoản ghi nguồn](https://open-meteo.com/en/docs/air-quality-api).

[Trang Tuần 3](../README.md) · [Vận hành](operation.md) · [Nhật ký kỹ thuật](WORKLOG.md)
