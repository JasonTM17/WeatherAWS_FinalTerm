# Báo cáo đối chiếu 3 chiều: Request, Log, Metric và S3 (Reconciliation Report)

**Sinh viên thực hiện:**
- Nguyễn Tiến Sơn — MSSV: 24110054
- Trần Thị Ngọc Quyên — MSSV: 24110051

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng
**Mốc kiểm chứng độc lập:** 19/10/2026. **Phạm vi đối chiếu:** Hai môi trường thực hành của sinh viên Nguyễn Tiến Sơn (`default`) và sinh viên Trần Thị Ngọc Quyên (`quyen`).

---

## 1. Phương pháp và mô hình đối chiếu 3 chiều (3-Way Reconciliation Framework)

Trong các hệ thống phân tán Serverless, một yêu cầu xử lý trải qua nhiều tầng dịch vụ độc lập. Để khẳng định hệ thống vận hành chuẩn xác và không có dữ liệu ảo, nhóm áp dụng mô hình đối soát chéo 3 chiều kết hợp tầng xác nhận thông báo:

```
[Kích hoạt Lambda] ────► [Tầng 1: CloudWatch Logs] ── (START/END/REPORT & [INFO] Result)
                               │
                               ├────► [Tầng 2: CloudWatch Metrics] ── (Native Invocations & Errors)
                               │
                               ├────► [Tầng 3: Amazon S3 & Athena] ── (NDJSON raw storage & exact SQL)
                               │
                               └────► [Tầng 4: Amazon SNS & Email] ── (Publish acceptance & Inbox receipt)
```

1. **Chiều 1 — Vòng đời thực thi & Nhật ký ứng dụng (CloudWatch Logs):**
   - Xác định mã `RequestId` đã được băm an toàn trong các sự kiện chuẩn của Lambda: `START`, `END`, và `REPORT`.
   - Đọc dòng nhật ký có cấu trúc `[INFO] Result:` ghi nhận số bản ghi thu thập, các đô thị thành công, đường dẫn tệp S3 và số cảnh báo đã gửi.
2. **Chiều 2 — Chỉ số vận hành gốc (CloudWatch Native Metrics):**
   - Truy vấn các metric chuẩn của AWS/Lambda gồm `Invocations` và `Errors` theo chu kỳ 300 giây (5 phút) tại thời điểm UTC tương ứng với lượt chạy.
   - Đối chiếu số lượt gọi trên metric với số lượng dòng `START/END` trong log.
3. **Chiều 3 — Dữ liệu gốc S3 & Truy vấn kiểm toán Athena (S3 Storage & Athena SQL):**
   - Tải lại nguyên bản tệp NDJSON lưu trên S3 tại đường dẫn được báo cáo trong log.
   - Kiểm tra số dòng (3 dòng tương ứng 3 đô thị) và 23 trường thuộc tính của từng bản ghi.
   - Thực thi câu lệnh Athena SQL lọc chính xác theo danh sách `record_id` của lượt chạy để chứng minh dữ liệu lưu trên S3 có thể truy vấn ngay lập tức qua Glue Data Catalog mà không cần quét lại dữ liệu cũ.
4. **Chiều 4 — Cảnh báo thời gian thực & Xác nhận hộp thư (SNS & Email Recipient):**
   - Đối chiếu quyết định cảnh báo từ dữ liệu thời tiết thực tế (AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³) với số lệnh gọi `sns:Publish` được chấp nhận, và xác nhận nhận thư thực tế từ cả hai sinh viên.

---

## 2. Kết quả đối chiếu chi tiết của hai lượt có kiểm soát

Dưới đây là bảng đối soát chi tiết trích xuất từ dữ liệu kiểm toán độc lập được lưu trữ tại [log_metric_s3_reconciliation.csv](../results/monitoring/log_metric_s3_reconciliation.csv) và [reconciliation_summary.json](../results/monitoring/reconciliation_summary.json):

| Tiêu chí đối chiếu | Sinh viên Nguyễn Tiến Sơn (`default`) | Sinh viên Trần Thị Ngọc Quyên (`quyen`) | Đánh giá kỹ thuật |
| :--- | :---: | :---: | :--- |
| **Request Hash định danh** | `415b1e3881f4cfca8559` | `6ae57d0f48ce98e59fd3` | Mã hash duy nhất cho mỗi lượt chạy |
| **Thời điểm kích hoạt (UTC)** | `2026-10-19T12:38:09.620000+00:00` | `2026-10-19T12:38:19.123000+00:00` | Ghi nhận chính xác microsecond |
| **Chuỗi vòng đời Lambda** | Đủ `START`, `END`, `REPORT` | Đủ `START`, `END`, `REPORT` | Thực thi bình thường, không crash |
| **Số bản ghi Lambda báo cáo** | **3 bản ghi** | **3 bản ghi** | TP.HCM, Hà Nội, Đà Nẵng |
| **Số đô thị thất bại** | **0** | **0** | Thu thập 100% thành công |
| **Tệp S3 được tạo** | 1 tệp NDJSON phân vùng theo ngày | 1 tệp NDJSON phân vùng theo ngày | Cấu trúc `raw/year=2026/month=10/day=19/...` |
| **Số bản ghi xác minh trên S3** | **3 bản ghi** (khớp byte JSON) | **3 bản ghi** (khớp byte JSON) | Đọc trực tiếp từ S3 object |
| **Native Invocations (CloudWatch)** | **1.0** (chu kỳ 300s tương ứng) | **1.0** (chu kỳ 300s tương ứng) | Khớp 1-1 với lượt gọi thực tế |
| **Native Errors (CloudWatch)** | **0.0** (chu kỳ 300s tương ứng) | **0.0** (chu kỳ 300s tương ứng) | Không phát sinh ngoại lệ runtime |
| **Tỷ lệ lỗi chu kỳ kiểm chứng** | **0,0%** | **0,0%** | 0 lỗi / 1 invocation |
| **Truy vấn Athena theo record_id** | Trả đúng 3 bản ghi, 0 lỗi | Trả đúng 3 bản ghi, 0 lỗi | Lọc chính xác 3 `record_id` |
| **Lượng dữ liệu Athena quét** | **19.683 bytes** (~19,2 KB) | **20.251 bytes** (~19,8 KB) | Tối ưu nhờ Partition Projection |
| **Thời gian Engine Athena** | **674 ms** (Total: 888 ms) | **584 ms** (Total: 747 ms) | Serverless query dưới 1 giây |
| **Lệnh Publish SNS chấp nhận** | **1 chấp nhận** (cho Hà Nội: AQI 101) | **1 chấp nhận** (cho Hà Nội: AQI 101) | Khớp điều kiện `AQI >= 100 OR PM2.5 >= 35.5` |
| **Xác nhận người nhận email** | **ĐÃ XÁC NHẬN** (Hộp thư sinh viên) | **ĐÃ XÁC NHẬN** (Hộp thư sinh viên) | [recipient_confirmation.json](../results/verification_2026_10_19/recipient_confirmation.json) |
| **Kết luận đối soát** | **MATCH (Khớp 100%)** | **MATCH (Khớp 100%)** | Toàn bộ 4 chiều dữ liệu khớp hoàn hảo |

---

## 3. Phân tích dữ liệu raw và điều kiện kích hoạt cảnh báo

Từ tệp dữ liệu raw được tải lại từ S3 và bảng kết quả truy vấn Athena:
- **TP. Hồ Chí Minh:** US AQI = `61`, PM2.5 = `22,1 µg/m³`, Nhiệt độ = `26,7 °C`, Độ ẩm = `89,0%`. Không thỏa điều kiện ngưỡng.
- **Hà Nội:** US AQI = `101`, PM2.5 = `29,9 µg/m³`, Nhiệt độ = `27,3 °C`, Độ ẩm = `81,0%`. **Thỏa mãn điều kiện ngưỡng do AQI ≥ 100**. Kích hoạt gửi 1 thông điệp cảnh báo SNS.
- **Đà Nẵng:** US AQI = `52`, PM2.5 = `7,3 µg/m³`, Nhiệt độ = `25,3 °C`, Độ ẩm = `92,0%`. Không thỏa điều kiện ngưỡng.

Kết quả thực nghiệm cho thấy hàm collector xử lý chính xác toán tử logic `OR`:
```python
if rec['pm2_5'] >= threshold_pm25 or rec['us_aqi'] >= threshold_aqi:
    if send_sns_alert(rec, threshold_pm25, threshold_aqi):
        alerts_sent += 1
```
Dù PM2.5 của Hà Nội chưa vượt ngưỡng 35,5 µg/m³, nhưng chỉ số US AQI đạt 101 đã kích hoạt thành công cảnh báo.

---

## 4. Phân tích ranh giới kỹ thuật và tính toán học

Báo cáo duy trì sự trung thực và chặt chẽ về mặt khoa học:
1. **Phạm vi tỷ lệ lỗi 0%:** Tỷ lệ lỗi 0,0% chỉ được khẳng định trong phạm vi hai chu kỳ 300 giây chứa hai lượt kiểm chứng có kiểm soát. Nhóm không suy diễn tỷ lệ 0% này cho toàn bộ lịch sử vận hành nhiều ngày của tài khoản khi có những chu kỳ thiếu cặp metric.
2. **Không quét đối tượng mồ côi toàn bucket:** Phép kiểm toán xác nhận các tệp S3 được tạo bởi hai lượt chạy có kiểm soát; không quét toàn bộ bucket hàng triệu đối tượng để tuyên bố tuyệt đối không có object mồ côi từ các bài thực hành khác.
3. **Phân biệt Metric Filters và Native Metrics:** Metric Filters ghi nhận các dòng log khớp mẫu, trong khi Native Invocations đếm số lần container Lambda được kích hoạt. Nhóm giữ riêng hai chỉ số này, không đồng nhất chúng.

---

## 5. Tái lập và kiểm toán độc lập

Toàn bộ quá trình đối chiếu 3 chiều có thể được tái lập hoàn toàn ngoại tuyến:

```powershell
# Kiểm tra đối soát tệp tổng hợp dữ liệu
python tuan_4/scripts/reconcile_ops.py --check

# Xuất lại báo cáo đối soát sang thư mục mới
python tuan_4/scripts/reconcile_ops.py --output output/week4-reconciliation-audit
```

**Bằng chứng và mã nguồn liên kết:**
- [CSV tổng hợp đối chiếu](../results/monitoring/log_metric_s3_reconciliation.csv)
- [Tệp tóm tắt phạm vi JSON](../results/monitoring/reconciliation_summary.json)
- [Hồ sơ xác nhận email người nhận](../results/verification_2026_10_19/recipient_confirmation.json)
- [Chương trình đối soát Python](../scripts/reconcile_ops.py)
- [Báo cáo tổng kết Tuần 4](FINAL_REPORT.md) · [Lời thoại demo](VIDEO_DEMO_SCRIPT.md)
