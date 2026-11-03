# Tổng hợp chi phí và quản lý tài nguyên AWS

**Nguyễn Tiến Sơn (24110054) · Trần Thị Ngọc Quyên (24110051).**

## 1. Chi phí tổng hợp đã xác nhận

Chi phí tổng hợp toàn đồ án được hai sinh viên xác nhận ngày **21/10/2026**: **sinh viên Tiến Sơn 0,25 USD**, **sinh viên Ngọc Quyên 0,22 USD**, **tổng cộng 0,47 USD**. Nguồn số liệu được lưu tại [bản tổng hợp chi phí đã xác nhận](../results/cost/confirmed_cost_summary.json).

Số liệu trên được dùng thống nhất trong README, báo cáo tổng kết và nội dung nộp Tuần 4. Đây là tổng chi phí theo xác nhận của sinh viên cho phần tổng hợp toàn đồ án; không phân bổ ngược thành chi phí từng tuần, từng dịch vụ hoặc từng stack.

## 2. Nguồn Cost Explorer lưu theo kỳ

Các bản xuất Cost Explorer kỳ **12–19/10/2026** được lưu riêng tại [JSON tổng hợp API](../results/cost/cost_summary.json) và [CSV chi tiết theo ngày, dịch vụ và loại ghi nhận](../results/cost/learner_lab_cost_breakdown.csv). Các bản xuất lưu nguyên giá trị UnblendedCost, đơn vị và cờ Estimated để đối chiếu theo kỳ. Báo cáo tổng hợp hiện tại sử dụng số liệu do hai sinh viên xác nhận tại nguồn riêng nêu trên.

Bản xuất lịch sử truy vấn Start inclusive 12/10, End exclusive 20/10/2026. Boto3 gọi GetCostAndUsage, Granularity DAILY, Metric UnblendedCost, GroupBy SERVICE và RECORD_TYPE. CSV gồm 117 nhóm, giữ ngày UTC, dịch vụ, loại ghi nhận, số gốc USD và Estimated. Phép cộng sử dụng Decimal để bảo toàn độ chính xác; nguồn nằm trong [snapshot môi trường](../results/verification_2026_10_19/environment/).

Hai nguồn được quản lý độc lập: `confirmed_cost_summary.json` ghi số sinh viên xác nhận; `cost_summary.json` và `learner_lab_cost_breakdown.csv` tái tạo kết quả API đã lưu. Không cộng hai nguồn hoặc dùng số nhóm của bản xuất cũ để giải thích số tiền cập nhật.

## 3. Quản lý và tối ưu tài nguyên

Hiệu quả Athena được đánh giá qua [18 truy vấn ngày 20/10](../results/advanced_live_2026_10_20/benchmark/), theo byte quét và độ trễ. Mức giảm byte quét được trình bày như kết quả kỹ thuật của bộ thực nghiệm, không quy đổi trực tiếp thành tỷ lệ giảm hóa đơn.

Hai lịch của stack mới giữ DISABLED để tránh thu thập trùng. Lịch chuẩn được quản lý theo [checklist cuối phiên](SESSION_CHECKLIST.md); phép thử tạm dừng–khôi phục ngày 20/10 giữ nguyên target và dữ liệu. CSV, manifest và kết quả phân tích được lưu để có thể kiểm tra offline.

Trước khi kết thúc sử dụng, cần kiểm kê tài nguyên có Retain, các phiên bản object, artifact, Secret và log. Việc tạm dừng lịch chỉ ngừng lượt thu thập tiếp theo; dữ liệu và các tài nguyên còn lưu giữ được quản lý riêng.

## 4. Đối chiếu số liệu

Lệnh `python tuan_4/scripts/cost_analysis.py --check` tính lại tổng của nguồn Cost Explorer lịch sử và kiểm tra byte các bảng dẫn xuất, không gọi AWS. Chi phí đã xác nhận được đọc riêng từ JSON nguồn tại mục 1 và kiểm tra tổng bằng Decimal: **0,25 + 0,22 = 0,47 USD**.

## 5. Cập nhật đối soát chi phí thực tế qua AWS CLI / Boto3 (Kỳ kiểm toán 03/11/2026)

Ngày **03/11/2026**, hệ thống được truy vấn trực tiếp qua AWS CLI / Cost Explorer API (`GetCostAndUsage`) trên cả hai profile để kiểm toán chi phí thực tế tiêu dùng lũy kế toàn bộ chu kỳ từ ngày 01/10 đến 03/11/2026. Toàn bộ số liệu ghi nhận dưới đây là chi phí thực tế phát sinh (Actual Usage Cost), tuyệt đối không ghi số âm:

| Dịch vụ AWS | Profile `default` (Nguyễn Tiến Sơn - 24110054) | Profile `quyen` (Trần Thị Ngọc Quyên - 24110051) | Tổng chi phí thực tế toàn đồ án |
| :--- | :---: | :---: | :---: |
| **Amazon CloudWatch** | **1,8902 USD** | **0,1273 USD** | **2,0175 USD** |
| **AWS Secrets Manager** | **0,5211 USD** | **0,5122 USD** | **1,0332 USD** |
| **AWS Cost Explorer API** | **0,0400 USD** | **0,0500 USD** | **0,0900 USD** |
| **Amazon Athena** | **0,0038 USD** | **0,0064 USD** | **0,0102 USD** |
| **Amazon Simple Storage Service (S3)** | **0,0042 USD** | **0,0056 USD** | **0,0098 USD** |
| **AWS Key Management Service (KMS)** | **0,000003 USD** | **0,0000 USD** | **0,000003 USD** |
| **AWS Lambda** | **0,0000 USD** | **0,0000 USD** | **0,0000 USD** |
| **AWS Glue** | **0,0000 USD** | **0,0000 USD** | **0,0000 USD** |
| **Amazon Simple Notification Service (SNS)** | **0,0000 USD** | **0,0000 USD** | **0,0000 USD** |
| **AWS CloudFormation** | **0,0000 USD** | **0,0000 USD** | **0,0000 USD** |
| **TỔNG CHI PHÍ THỰC TẾ (USD)** | **2,4592 USD** | **0,7015 USD** | **3,1607 USD** |
| **LÀM TRÒN BÁO CÁO (USD)** | **2,46 USD** | **0,70 USD** | **3,16 USD** |

### Đánh giá nguyên nhân phát sinh chi phí thực tế:
- **Amazon CloudWatch (2,02 USD):** Chiếm tỷ trọng lớn nhất (63,8%) do duy trì 2 CloudWatch Alarms (0,10 USD/alarm/tháng) và nạp log từ các hàm Lambda.
- **AWS Secrets Manager (1,03 USD):** Chiếm 32,7% do tồn tại đồng thời 2 secret trên mỗi tài khoản (0,40 USD/secret/tháng pro-rated).
- **AWS Cost Explorer API (0,09 USD):** Chiếm 2,8% từ 9 lượt truy vấn qua API phục vụ kiểm toán chi phí (0,01 USD/request).
- **Amazon Athena & S3 (0,02 USD):** Chiếm dưới 1,0% nhờ tối ưu hóa định dạng Parquet Snappy và Partition Projection.
- **Trạng thái tài nguyên:** Toàn bộ lịch kích hoạt EventBridge (`WeatherCollectionSchedule`, `weather-w4-*-hourly`) trên cả hai tài khoản đều ở trạng thái `DISABLED`, đảm bảo không phát sinh chi phí thu thập ngoài ý muốn.

Chi tiết đối soát từng ngày và từng dịch vụ được lưu trữ tại:
- [JSON tổng hợp kiểm toán 03/11/2026](../results/cost/live_cost_update_2026_11_03.json)
- [CSV phân rã chi tiết từng ngày 01/10 - 03/11/2026](../results/cost/live_cost_breakdown_2026_11_03.csv)

[Báo cáo Tuần 4](FINAL_REPORT.md) · [Dữ liệu chi phí](../results/cost/) · [Minh chứng ngày 20/10](../results/advanced_live_2026_10_20/README.md).