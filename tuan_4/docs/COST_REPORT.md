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

[Báo cáo Tuần 4](FINAL_REPORT.md) · [Dữ liệu chi phí](../results/cost/) · [Minh chứng ngày 20/10](../results/advanced_live_2026_10_20/README.md).
