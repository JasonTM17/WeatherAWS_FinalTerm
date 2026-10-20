# Báo cáo chi phí AWS theo kỳ thực hành (FinOps Cloud Report)

**Sinh viên thực hiện:**
- Nguyễn Tiến Sơn — MSSV: 24110054
- Trần Thị Ngọc Quyên — MSSV: 24110051

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng
**Mốc xuất báo cáo:** 19/10/2026. **Kỳ số liệu đối soát:** 12/10/2026 – 19/10/2026 (ngày kết thúc không bao gồm trong API là 20/10/2026).

---

## 1. Nguyên tắc FinOps và bối cảnh AWS Learner Lab

Trong môi trường AWS Academy Learner Lab, mỗi tài khoản được cấp một hạn mức tín dụng cố định **100 USD** cho toàn bộ học phần. Khi hạn mức này cạn kiệt, tài khoản bị tạm ngưng và toàn bộ tài nguyên có nguy cơ bị xóa bỏ. Do đó, việc áp dụng nguyên tắc **FinOps (Cloud Financial Management)** là yêu cầu cốt lõi nhằm:
1. **Kiểm soát chi phí theo thời gian thực:** Nắm rõ từng cent chi tiêu của từng dịch vụ, phân tách rõ ràng giữa chi phí sử dụng (*Usage*) và khoản bù trừ tín dụng (*Credit*).
2. **Tối ưu hóa tài nguyên Serverless:** Thiết kế kiến trúc hoàn toàn không dùng máy chủ (Serverless — EventBridge, Lambda, S3, Glue Data Catalog, Athena, SNS, Secrets Manager), đảm bảo không phát sinh chi phí nhàn rỗi (idle compute cost).
3. **Bảo toàn tín dụng cuối phiên:** Tự động hóa việc tắt/bật lịch kích hoạt bằng script và checklist để tránh lãng phí credit giữa các buổi thực hành.

---

## 2. Nguồn dữ liệu và phạm vi đối soát

Số liệu chi phí được truy vấn trực tiếp từ **AWS Cost Explorer API** thông qua phương thức `GetCostAndUsage` với các tham số kỹ thuật chuẩn:
- **Metric:** `UnblendedCost`
- **Granularity:** `DAILY` (theo ngày UTC)
- **GroupBy:** `SERVICE` và `RECORD_TYPE` (phân định rõ giữa `Usage` và `Credit`)
- **TimePeriod:** `Start: '2026-10-12'`, `End: '2026-10-20'` (bao gồm trọn vẹn 8 ngày từ 12/10 đến hết 19/10/2026 UTC).

Số liệu thô được bảo toàn nguyên vẹn tại [CSV gốc sinh viên Tiến Sơn](../results/verification_2026_10_19/environment/default/cost_by_service.csv) và [CSV gốc sinh viên Ngọc Quyên](../results/verification_2026_10_19/environment/quyen/cost_by_service.csv), bao gồm độ chính xác số học cao (Decimal) và cờ `Estimated = True` do AWS đánh dấu cho các bản ghi đang tổng hợp.

### Bảng tổng hợp chi phí 2 tài khoản thực hành

| Sinh viên thực hiện | Profile | Số nhóm ghi nhận (Service / Record Type) | Tổng Unblended Cost chính xác (USD) | Tổng hiển thị làm tròn (USD) | Trạng thái đối soát |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Nguyễn Tiến Sơn** | `default` | 70 nhóm | `-3.390E-7` | **0,00 USD** | Khớp 100% dữ liệu API |
| **Trần Thị Ngọc Quyên** | `quyen` | 47 nhóm | `+0.1364702401` | **0,14 USD** | Khớp 100% dữ liệu API |

*Ghi chú quan trọng:*
- Đây là chi phí thực tế toàn bộ tài khoản học phần trong kỳ 12–19/10/2026, không phải chi phí riêng của một nhóm tài nguyên hay dự toán hàng tháng.
- Ở tài khoản của sinh viên Tiến Sơn, tổng chi phí unblended âm nhẹ (`-3.390E-7 USD`) do các khoản Credit của Learner Lab bù trừ cho các dịch vụ vượt nhẹ mức sử dụng micro-cents.
- Ở tài khoản của sinh viên Ngọc Quyên, chi phí ròng đạt `0,14 USD` chủ yếu do các truy vấn phân tích chuyên sâu và kiểm thử tải dữ liệu lịch sử trong Tuần 3 và Tuần 4.

---

## 3. Phân tích chi tiết chi phí theo từng dịch vụ AWS

Từ [117 dòng số liệu gốc tổng hợp](../results/cost/learner_lab_cost_breakdown.csv), chi phí của các dịch vụ trong hệ thống được phân rã như sau:

| Dịch vụ AWS | Vai trò trong hệ thống | Cơ chế tính phí & Tác động chi phí | Tối ưu hóa FinOps đã áp dụng |
| :--- | :--- | :--- | :--- |
| **AWS Secrets Manager** | Lưu trữ tọa độ 3 thành phố và ngưỡng cảnh báo an toàn | 0,40 USD/secret/tháng + 0,05 USD/10.000 API calls. Mức phát sinh trung bình ~0,0129 USD/ngày, được Credit bù trừ tương ứng. | Lưu trữ duy nhất 1 Secret cấu hình chung cho cả 3 thành phố; Lambda đọc cấu hình theo đợt gọi. |
| **AmazonCloudWatch** | Thu thập Logs (START/END/REPORT, Result), Metrics, Alarms và Dashboard | Phí thu thập log (0,50 USD/GB), lưu trữ log, và Dashboard (3,00 USD/dashboard/tháng ngoài Free Tier). Ghi nhận ~0,0032 – 0,0037 USD/ngày. | Giới hạn log retention, thiết kế 1 Dashboard duy nhất (`WeatherAirQuality-Week3`), dùng Metric Filters để giám sát không tốn thêm compute. |
| **Amazon S3** | Lưu trữ hồ sơ NDJSON phân vùng theo ngày UTC (`raw/year=YYYY/...`) | Lưu trữ Standard (0,023 USD/GB/tháng) + PUT requests (0,005 USD/1.000 reqs). Mức phát sinh rất nhỏ (~0,0005 USD/ngày). | Gom dữ liệu 3 thành phố vào một tệp NDJSON cho mỗi lượt gọi thay vì tạo nhiều tệp rời; nén dữ liệu và cấu trúc partition rõ ràng. |
| **AWS Lambda** | Thu thập thời tiết từ Open-Meteo API và điều phối cảnh báo | Tính theo số lượt gọi (0,20 USD/1M reqs) và compute duration (GB-giây). Nằm hoàn toàn trong AWS Free Tier (1M reqs và 400.000 GB-giây miễn phí). | Tối ưu thời gian chạy (~700ms - 1500ms), cấu hình bộ nhớ phù hợp (128 MB), xử lý bất đồng bộ. Chi phí = **0,00 USD**. |
| **Amazon Athena** | Truy vấn Serverless SQL trên dữ liệu S3 thông qua Glue Catalog | 5,00 USD/TB dữ liệu được quét. Các truy vấn có kiểm soát trong Tuần 4 quét 19.683 – 20.251 bytes (~19 KB), chi phí chỉ ~0,0001 USD/lượt. | Áp dụng **Partition Projection** và điều kiện `WHERE year=... AND month=... AND day=...` kết hợp nén Snappy Parquet ở Tuần 3 giúp giảm **80,59% – 96,50%** lượng byte quét. |
| **Amazon SNS** | Gửi cảnh báo chất lượng không khí vượt ngưỡng qua Email | 1.000 email thông báo đầu tiên mỗi tháng hoàn toàn miễn phí; sau đó 2,00 USD/100.000 email. | Chỉ phát thông báo khi AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³; không gửi cảnh báo trùng lặp ở nhánh backfill dữ liệu lịch sử. Chi phí = **0,00 USD**. |
| **AWS Glue** | Lưu trữ Data Catalog metadata (Database và Table definition) | Lưu trữ 1 triệu đối tượng miễn phí; truy vấn catalog miễn phí. | Chỉ khai báo 1 catalog database và 1 bảng chính, không chạy Glue Crawler định kỳ tốn phí. Chi phí = **0,00 USD**. |
| **AWS Cost Explorer** | Phân tích và truy vấn dữ liệu chi phí | 0,01 USD cho mỗi yêu cầu API `GetCostAndUsage` có phân nhóm. Đã được Credit bù trừ. | Chỉ gọi khi cần kiểm toán; lưu lại bản sao CSV có chữ ký SHA-256 để phân tích ngoại tuyến mà không cần gọi API lặp lại. |

---

## 4. Chiến lược quản lý chi phí (FinOps Action Plan)

Để bảo đảm tài khoản không bao giờ vượt ngưỡng 100 USD của Learner Lab, nhóm đã ban hành và tuân thủ nghiêm ngặt các quy trình vận hành:

1. **Quản lý vòng đời tài nguyên sau mỗi phiên Lab (Session Lifecycle Management):**
   - Sử dụng script tự động hóa [cleanup_resources.ps1](../scripts/cleanup_resources.ps1) gọi `session_control.py pause` để tạm dừng lịch EventBridge ngay khi kết thúc buổi thực hành.
   - Khi tạm dừng lịch, Lambda không còn bị kích hoạt ngầm mỗi giờ, ngăn chặn hoàn toàn việc tích lũy chi phí API ngoài ý muốn.
   - Trước buổi thực hành tiếp theo, dùng [start_resources.ps1](../scripts/start_resources.ps1) khôi phục lịch một cách an toàn dựa trên state file đã kiểm tra tính toàn vẹn.

2. **Tuân thủ danh mục kiểm tra kết thúc phiên ([SESSION_CHECKLIST.md](SESSION_CHECKLIST.md)):**
   - Bước 1: Chờ tất cả request đang chạy hoàn tất.
   - Bước 2: Xuất toàn bộ dữ liệu raw, log, metric và chi phí ra thư mục minh chứng.
   - Bước 3: Tạm dừng EventBridge rule.
   - Bước 4: Kiểm tra trạng thái `DISABLED` trên AWS Console hoặc qua CLI.
   - Bước 5: Bấm **End Lab** trên giao diện AWS Academy.

3. **Tối ưu hóa chi phí truy vấn phân tích:**
   - Luôn sử dụng Partition Projection trong Glue/Athena để khoanh vùng ngày truy vấn.
   - Tránh tuyệt đối các câu lệnh `SELECT *` không có điều kiện `WHERE` trên toàn bộ bucket.
   - Trong Tuần 3, nhóm đã chứng minh việc chuyển đổi định dạng từ NDJSON sang Parquet Snappy giảm dữ liệu quét từ 11.243 bytes xuống 393 bytes (giảm 96,50%), mang lại hiệu quả kinh tế rõ rệt khi quy mô dữ liệu mở rộng.

---

## 5. Quy trình tái lập và kiểm toán độc lập

Mọi số liệu trong báo cáo này có thể được tái lập và xác minh hoàn toàn ngoại tuyến mà không cần gọi lại AWS API, bảo đảm tính minh bạch và toàn vẹn dữ liệu:

```powershell
# Kiểm tra đối soát dữ liệu chi phí đã lưu
python tuan_4/scripts/cost_analysis.py --check

# Xuất lại báo cáo chi phí vào một thư mục mới độc lập
python tuan_4/scripts/cost_analysis.py --output output/week4-cost-audit
```

**Kết quả xác thực:**
- [Bảng phân tích chi phí 117 dòng](../results/cost/learner_lab_cost_breakdown.csv)
- [Tệp tóm tắt số học JSON](../results/cost/cost_summary.json)
- Các tệp đầu ra được kiểm tra tính khớp bằng kiểu dữ liệu số học độ chính xác cao `Decimal` của Python.

---

## 6. Tài liệu tham khảo và liên kết

- [Tài liệu chính thức AWS Cost Explorer API](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_GetCostAndUsage.html)
- [Báo cáo tổng kết Tuần 4](FINAL_REPORT.md)
- [Danh mục kiểm tra kết thúc phiên thực hành](SESSION_CHECKLIST.md)
- [Báo cáo tổng kết toàn đồ án](../../docs/FINAL_PROJECT_REPORT.md)
