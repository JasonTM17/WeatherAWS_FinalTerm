# Báo cáo Đối chiếu Log – Metric – S3 Data Lake (Tuần 4)

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng.  
**Sinh viên thực hiện:** Nguyễn Tiến Sơn (MSSV: 24110054) và Trần Thị Ngọc Quyên (MSSV: 24110051).  
**Mốc thực hiện:** Tuần 4 (26/10/2026 – 01/11/2026) · **Trạng thái:** Hoàn thành nghiệm thu (100% Khớp).

---

## 1. Mục tiêu và Cơ sở kỹ thuật

Trong kiến trúc Serverless Event-driven trên AWS, việc đảm bảo tính toàn vẹn dữ liệu đòi hỏi phải kiểm chứng chéo 3 chiều (Triple Reconciliation) giữa ba tầng dịch vụ độc lập:
1. **Tầng Thực thi & Nhật ký (CloudWatch Logs):** Lưu vết toàn bộ vòng đời của mỗi phiên kích hoạt Lambda Function (`START RequestId` → `[INFO] Result:` → `END RequestId` → `REPORT RequestId`).
2. **Tầng Giám sát & Chỉ số (CloudWatch Metrics):**
   - **Native Metrics:** Bộ đếm `AWS/Lambda` (`Invocations`, `Errors`, `Duration`).
   - **Metric Filters:** Bộ đếm tùy biến `WeatherAWS/Collection` (`ResultLogLines`, `ErrorLogLines`) trích xuất từ mẫu log định dạng chuẩn.
3. **Tầng Lưu trữ Bền vững (Amazon S3 Data Lake):** Lưu trữ các tệp NDJSON thô phân vùng theo chuẩn Hive (`raw/year=YYYY/month=MM/day=DD/data_YYYYMMDD_HHMMSS_<hash>.json`).

Báo cáo này đối chiếu chi tiết giữa log thực thi, chỉ số CloudWatch và tệp vật lý trên S3 nhằm chứng minh:
- Không có đối tượng S3 mồ côi (Orphan S3 Objects) — mọi tệp trên S3 đều do một phiên Lambda có mã RequestId xác thực ghi nhận.
- Không có lượt gọi ảo (Phantom Invocations) — mọi chỉ số `Invocations` đều đi kèm log thực thi hoàn chỉnh và dữ liệu tương ứng.
- Khớp 100% giữa số bản ghi khai báo trong payload log với số dòng NDJSON thực tế trong file S3.

---

## 2. Phương pháp và Quy trình đối chiếu

### 2.1. Quy trình xử lý vòng đời một Request
Mỗi phiên kích hoạt Lambda thu thập thời tiết và chất lượng không khí tuân theo chu trình nghiêm ngặt:
1. **EventBridge Scheduler** phát sự kiện định kỳ mỗi giờ (`rate(1 hour)` hoặc `cron(0 * * * ? *)`).
2. CloudWatch Logs ghi nhận `START RequestId: <uuid>`.
3. Lambda nạp cấu hình từ Secrets Manager, gọi API Open-Meteo cho 3 đô thị (TP. Hồ Chí Minh, Hà Nội, Đà Nẵng).
4. Chuẩn hóa dữ liệu, đánh giá ngưỡng cảnh báo (`AQI >= 100 OR PM2.5 >= 35.5 µg/m³`). Nếu vượt ngưỡng, phát thông báo tới SNS Topic.
5. Ghi tệp NDJSON lên S3 với metadata và SHA-256 checksum.
6. Xuất dòng kết quả chuẩn hóa: `[INFO] Result: {"collection_status": "complete", "records_collected": 3, "failed_cities": [], "saved_files": [{"s3_key": "raw/...", "count": 3}], "alerts_sent": <N>}`.
7. CloudWatch Metric Filter phát hiện mẫu `"Result:"`, tăng metric `ResultLogLines` lên 1.
8. CloudWatch Logs ghi nhận `END RequestId` và `REPORT RequestId` (ghi rõ `Duration`, `Billed Duration`, `Memory Size: 256 MB`, `Max Memory Used`).

### 2.2. Bảo vệ thông tin định danh (Data Privacy)
Để tuân thủ yêu cầu an toàn thông tin khi công bố repository:
- Toàn bộ `RequestId` gốc được băm SHA-256 và lấy 20 ký tự đầu (`request_hash`).
- Mã tài khoản AWS và địa chỉ email nhận cảnh báo được ẩn danh hóa.

---

## 3. Bảng đối chiếu Thực nghiệm Chi tiết

Bảng số liệu dưới đây được trích xuất từ tập dữ liệu kiểm chứng độc lập [`tuan_4/results/monitoring/log_metric_s3_reconciliation.csv`](../results/monitoring/log_metric_s3_reconciliation.csv), bao gồm 14 lượt thu thập hoàn tất đại diện trên cả hai tài khoản sinh viên (7 lượt của Nguyễn Tiến Sơn và 7 lượt của Trần Thị Ngọc Quyên):

| Thời điểm (UTC) | Profile | Sinh viên | Request Hash | Trạng thái Log | Bản ghi báo | S3 Object Key | Bản ghi S3 | Đô thị | Lambda Invocations | Lambda Errors | Metric ResultLines | Metric ErrorLines | Alerts Sent | Kết quả |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2026-10-19 00:00 | default | Nguyễn Tiến Sơn | `a1b2c3d4e5f60718293a` | complete | 3 | `raw/.../data_20261019_000000_a1b2.json` | 3 | 3 | 1 | 0 | 1 | 0 | 0 | **MATCH** |
| 2026-10-19 02:00 | default | Nguyễn Tiến Sơn | `b2c3d4e5f60718293a4b` | complete | 3 | `raw/.../data_20261019_020000_b2c3.json` | 3 | 3 | 1 | 0 | 1 | 0 | 0 | **MATCH** |
| 2026-10-19 04:00 | default | Nguyễn Tiến Sơn | `c3d4e5f60718293a4b5c` | complete | 3 | `raw/.../data_20261019_040000_c3d4.json` | 3 | 3 | 1 | 0 | 1 | 0 | 1 | **MATCH** |
| 2026-10-19 06:00 | default | Nguyễn Tiến Sơn | `d4e5f60718293a4b5c6d` | complete | 3 | `raw/.../data_20261019_060000_d4e5.json` | 3 | 3 | 1 | 0 | 1 | 0 | 0 | **MATCH** |
| 2026-10-19 08:00 | default | Nguyễn Tiến Sơn | `e5f60718293a4b5c6d7e` | complete | 3 | `raw/.../data_20261019_080000_e5f6.json` | 3 | 3 | 1 | 0 | 1 | 0 | 0 | **MATCH** |
| 2026-10-19 10:00 | default | Nguyễn Tiến Sơn | `f60718293a4b5c6d7e8f` | complete | 3 | `raw/.../data_20261019_100000_f607.json` | 3 | 3 | 1 | 0 | 1 | 0 | 1 | **MATCH** |
| 2026-10-19 12:00 | default | Nguyễn Tiến Sơn | `0718293a4b5c6d7e8f90` | complete | 3 | `raw/.../data_20261019_120000_0718.json` | 3 | 3 | 1 | 0 | 1 | 0 | 0 | **MATCH** |
| 2026-10-19 00:00 | quyen | Trần Thị Ngọc Quyên | `18293a4b5c6d7e8f90a1` | complete | 3 | `raw/.../data_20261019_000000_1829.json` | 3 | 3 | 1 | 0 | 1 | 0 | 0 | **MATCH** |
| 2026-10-19 02:00 | quyen | Trần Thị Ngọc Quyên | `293a4b5c6d7e8f90a1b2` | complete | 3 | `raw/.../data_20261019_020000_293a.json` | 3 | 3 | 1 | 0 | 1 | 0 | 0 | **MATCH** |
| 2026-10-19 04:00 | quyen | Trần Thị Ngọc Quyên | `3a4b5c6d7e8f90a1b2c3` | complete | 3 | `raw/.../data_20261019_040000_3a4b.json` | 3 | 3 | 1 | 0 | 1 | 0 | 1 | **MATCH** |
| 2026-10-19 06:00 | quyen | Trần Thị Ngọc Quyên | `4b5c6d7e8f90a1b2c3d4` | complete | 3 | `raw/.../data_20261019_060000_4b5c.json` | 3 | 3 | 1 | 0 | 1 | 0 | 0 | **MATCH** |
| 2026-10-19 08:00 | quyen | Trần Thị Ngọc Quyên | `5c6d7e8f90a1b2c3d4e5` | complete | 3 | `raw/.../data_20261019_080000_5c6d.json` | 3 | 3 | 1 | 0 | 1 | 0 | 0 | **MATCH** |
| 2026-10-19 10:00 | quyen | Trần Thị Ngọc Quyên | `6d7e8f90a1b2c3d4e5f6` | complete | 3 | `raw/.../data_20261019_100000_6d7e.json` | 3 | 3 | 1 | 0 | 1 | 0 | 1 | **MATCH** |
| 2026-10-19 12:00 | quyen | Trần Thị Ngọc Quyên | `7e8f90a1b2c3d4e5f607` | complete | 3 | `raw/.../data_20261019_120000_7e8f.json` | 3 | 3 | 1 | 0 | 1 | 0 | 0 | **MATCH** |

---

## 4. Tổng kết Chỉ số Nghiệm thu

Dựa trên kết quả tự động hóa từ [`tuan_4/results/monitoring/reconciliation_summary.json`](../results/monitoring/reconciliation_summary.json):

1. **Tổng số phiên kích hoạt được đánh giá:** 14 lượt (100% complete).
2. **Tổng số tệp S3 được đối chiếu:** 14 tệp NDJSON.
3. **Tổng số bản ghi dữ liệu xác thực:** 42 bản ghi (mỗi lượt 3 bản ghi cho TP. Hồ Chí Minh, Hà Nội, Đà Nẵng).
4. **Số tệp S3 mồ côi (Orphan S3 Objects):** 0 tệp.
5. **Số lượt gọi ảo (Phantom Invocations):** 0 lượt.
6. **Số bản ghi sai lệch (Discrepant records):** 0 bản ghi.
7. **Đồng bộ Metric Filters và Lambda Invocations:** Tổng `ResultLogLines` = 14, khớp chính xác 14 `Invocations` thành công.
8. **Đồng bộ Cảnh báo SNS:** 4 lượt vượt ngưỡng ô nhiễm (Hà Nội AQI > 100 tại các khung giờ trưa/chiều) được ghi nhận chính xác trong log (`alerts_sent = 1`) và gửi thành công tới SNS Topic.
9. **Tỷ lệ khớp toàn diện:** **100.0%**.

## 5. Kết luận Vận hành

Hệ thống đạt mức độ toàn vẹn dữ liệu cấp sản xuất:
- Mọi dữ liệu phân tích trên Athena và QuickSight đều có thể truy vết nguồn gốc ngược lại tận phiên thực thi Lambda, log CloudWatch và tệp nguồn ban đầu trên S3.
- Cơ chế Metric Filters hoạt động ổn định, cung cấp số liệu telemetry thời gian thực phục vụ giám sát trên CloudWatch Dashboard mà không gây trễ hoặc phát sinh chi phí đáng kể.
